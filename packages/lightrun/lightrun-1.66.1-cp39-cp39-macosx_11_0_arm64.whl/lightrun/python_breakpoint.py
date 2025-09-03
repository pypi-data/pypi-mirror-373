# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Handles a single Python breakpoint."""

import os
import sys
import time
import types

from datetime import datetime, timedelta
from threading import Lock

from . import capture_collector, imphook, lightrun_config, log_collector, messages, module_explorer, module_search, module_utils, utils
from .lightrun_native import native

# Status messages for different breakpoint events (except of "hit").
_BREAKPOINT_EVENT_STATUS = dict(
    [
        (native.BREAKPOINT_EVENT_ERROR, {"isError": True, "description": messages.toJson(messages.ERROR_UNSPECIFIED_INTERNAL_ERROR)}),
        (
            native.BREAKPOINT_EVENT_GLOBAL_CONDITION_QUOTA_EXCEEDED,
            {"isError": True, "refersTo": "BREAKPOINT_CONDITION", "description": messages.toJson(messages.ERROR_CONDITION_BREAKPOINT_QUOTA_EXCEEDED_0)},
        ),
        (
            native.BREAKPOINT_EVENT_BREAKPOINT_CONDITION_QUOTA_EXCEEDED,
            {"isError": True, "refersTo": "BREAKPOINT_CONDITION", "description": messages.toJson(messages.ERROR_CONDITION_BREAKPOINT_QUOTA_EXCEEDED_0)},
        ),
        (
            native.BREAKPOINT_EVENT_CONDITION_EXPRESSION_MUTABLE,
            {"isError": True, "refersTo": "BREAKPOINT_CONDITION", "description": messages.toJson(messages.ERROR_CONDITION_MUTABLE_0)},
        ),
        (
            native.BREAKPOINT_EVENT_CONDITION_EXPRESSION_EVALUATION_FAILED,
            {"isError": True, "refersTo": "BREAKPOINT_CONDITION", "description": messages.toJson(messages.ERROR_CONDITION_INVALID_0)},
        ),
    ]
)

# The implementation of datetime.strptime imports an undocumented module called
# _strptime. If it happens at the wrong time, we can get an exception about
# trying to import while another thread holds the import lock. This dummy call
# to strptime ensures that the module is loaded at startup.
# See http://bugs.python.org/issue7980 for discussion of the Python bug.
datetime.strptime("2017-01-01", "%Y-%m-%d")


def _IsRootInitPy(path):
    return path.lstrip(os.sep) == "__init__.py"


def _NormalizePath(path):
    """Removes surrounding whitespace, leading separator and normalize."""

    # normalize separators between Linux and Windows
    path = path.replace("\\" if os.sep == "/" else "/", os.sep)

    # TODO(google): Calling os.path.normpath "may change the meaning of a
    # path that contains symbolic links" (e.g., "A/foo/../B" != "A/B" if foo is a
    # symlink). This might cause trouble when matching against loaded module
    # paths. We should try to avoid using it.
    # Example:
    #  > import symlink.a
    #  > symlink.a.__file__
    #  symlink/a.py
    #  > import target.a
    #  > starget.a.__file__
    #  target/a.py
    # Python interpreter treats these as two separate modules. So, we also need to
    # handle them the same way.
    path_strip = path.strip().lstrip(os.sep)
    return os.sep.join(path_strip.replace("\\", "/").split("/"))


class PythonBreakpoint(object):
    """
    Handles a single Python breakpoint.

    Taking care of a breakpoint starts with setting one and evaluating
    condition. When a breakpoint we need to evaluate all the watched expressions
    and take an action. The action can be either to collect all the data or
    to log a statement.
    """

    def __init__(self, definition, hub_client, breakpoints_manager, piping_manager, data_visibility_manager):
        """
        Class constructor.

        Tries to set the breakpoint. If the source location is invalid, the
        breakpoint is completed with an error message. If the source location is
        valid, but the module hasn't been loaded yet, the breakpoint is deferred.

        Args:
          definition: breakpoint definition as it came from the backend.
          hub_client: asynchronously sends breakpoint updates to the backend.
          breakpoints_manager: Object to manage active breakpoints.
          piping_manager: Object to manage piping output from breakpoints to backend.
          data_visibility_manager: Object to manage data visibility policy of captured data of the breakpoint.
        """
        self.definition = definition

        # Breakpoint expiration time.
        if self.definition.get("expirationSeconds"):
            expiration_period = timedelta(seconds=self.definition.get("expirationSeconds"))
        else:
            expiration_period = timedelta(seconds=int(lightrun_config.config["breakpoint_expiration_sec"]))
        if self.definition.get("createTime"):
            fmt = "%Y-%m-%dT%H:%M:%S%Z" if "." not in self.definition["createTime"] else "%Y-%m-%dT%H:%M:%S.%f%Z"
            create_datetime = datetime.strptime(self.definition["createTime"].replace("Z", "UTC"), fmt)
        else:
            create_datetime = datetime.utcnow()
        self.expiration_datetime = create_datetime + expiration_period

        if self.definition.get("location").get("path"):
            self.definition["location"]["path"] = _NormalizePath(self.definition["location"]["path"])

        self._hub_client = hub_client
        self._breakpoints_manager = breakpoints_manager
        self._piping_manager = piping_manager
        self._data_visibility_manager = data_visibility_manager
        self._line = self.definition["location"]["line"]
        self._cookie = None
        self._module = None
        self._original_code_object = None
        self._import_hook_cleanup = None
        self._ignore_quota = self.definition.get("ignoreQuota", False)
        self._hit_count = 0

        self._lock = Lock()
        self._completed = False

        if self._GetActionType() == "LOG":
            self._collector = log_collector.LogCollector(self.definition, self._piping_manager, self._data_visibility_manager, self._ignore_quota)
        elif self._IsCaptureAction():
            pass  # A capture collector will be initialized upon each hit

    def _IsCaptureAction(self):
        return self._GetActionType() == "CAPTURE"

    def ActivateBreakpoint(self):
        if self._GetActionType() not in ["LOG", "CAPTURE"]:
            self._CompleteBreakpoint(
                {"status": {"isError": True, "refersTo": "BREAKPOINT_ACTION_TYPE", "description": messages.toJson(messages.ERROR_UNKNOWN_ACTION_TYPE)}}
            )
            return
        original_path = self.definition["location"]["path"]
        path = _NormalizePath(original_path)

        # Only accept .py extension.
        if os.path.splitext(path)[1] != ".py":
            self._CompleteBreakpoint(
                {
                    "status": {
                        "isError": True,
                        "refersTo": "BREAKPOINT_SOURCE_LOCATION",
                        "description": messages.toJson(messages.ERROR_LOCATION_FILE_EXTENSION_0),
                    }
                }
            )
            return

        # A flat init file is too generic; path must include package name.
        if path == "__init__.py":
            err = messages.ERROR_LOCATION_MULTIPLE_MODULES
            self._CompleteBreakpoint(
                {
                    "status": {
                        "isError": True,
                        "refersTo": "BREAKPOINT_SOURCE_LOCATION",
                        "description": {"id": err.id, "format": err.value.replace(""), "parameters": [path]},
                    }
                }
            )
            return

        possible_paths = module_search.Search(path)

        if possible_paths is None or len(possible_paths) == 0:
            # No possible absolute file path found for the searched file
            self._CompleteBreakpoint(
                {
                    "status": {
                        "isError": True,
                        "refersTo": "BREAKPOINT_SOURCE_LOCATION",
                        "description": messages.toJson(messages.ERROR_LOCATION_MODULE_NOT_FOUND_0),
                    }
                }
            )
            return

        base_dir = os.path.join(os.sep, _NormalizePath(lightrun_config.config["base_dir"]))
        base_dir_possible_paths = [p for p in possible_paths if p.startswith(base_dir)]

        if len(possible_paths) > 1:
            # More than one possible path.
            # In case one of the possible paths is an exact match to the searched path, we use it.
            # Otherwise, the agent tries to solve the path ambiguity by taking an option
            # with the shortest unmatched part.
            # If the paths have equal length, the agent can't define which of the paths is the correct one,
            # so we ask the user to set the action with a more specific path.
            if original_path in possible_paths:
                possible_paths = [original_path]
            elif os.path.join(base_dir, original_path) in possible_paths:
                possible_paths = [os.path.join(base_dir, original_path)]
            elif len(base_dir_possible_paths) == 1:
                possible_paths = base_dir_possible_paths
            else:
                native.LogInfo('Picking a match for "%s" with a shortest path' % original_path)
                native.LogInfo("The candidates are %s" % possible_paths)
                shortest_path = module_search.FindShortestPath(original_path, possible_paths)
                native.LogInfo("%s file is selected for adding a breakpoint" % (shortest_path or "No"))
                if shortest_path is not None:
                    possible_paths = [shortest_path]
                else:
                    err_id, err_fmt, err_params = messages.multiple_modules_found_error(path, possible_paths)
                    self._CompleteBreakpoint(
                        {
                            "status": {
                                "isError": True,
                                "refersTo": "BREAKPOINT_SOURCE_LOCATION",
                                "description": {"id": err_id, "format": err_fmt, "parameters": err_params},
                            }
                        }
                    )
                    return

        visible, reason = self._data_visibility_manager.IsFileVisible(utils.NormalizePath(possible_paths[0]))
        if not visible:
            self._CompleteBreakpoint(
                {"status": {"isError": True, "refersTo": "BREAKPOINT_SOURCE_LOCATION", "description": messages.toJson(messages.ERROR_BLACKLISTED_FILE)}}
            )
            return

        # pipingStatus should be set before actually activating the breakpoint.
        # Otherwise, the global piping status can be applied for a short time, which is wrong
        piping_status = self.definition.get("pipingStatus")
        if piping_status and not self._IsCaptureAction():
            self._piping_manager.SetActionPiping(self.GetBreakpointId(), piping_status)

        new_module = module_utils.GetLoadedModuleBySuffix(possible_paths[0])

        if new_module:
            self._ActivateBreakpointInternal(new_module)
        else:
            native.LogInfo("Registering an import hook for breakpoint %s" % self.GetBreakpointId())
            self._import_hook_cleanup = imphook.AddImportCallbackBySuffix(possible_paths[0], self._ActivateBreakpointInternal)

    def Clear(self):
        """
        Clears the breakpoint and releases all breakpoint resources.

        This function is assumed to be called by BreakpointsManager. Therefore we
        don't call CompleteBreakpoint from here.
        """
        self._RemoveImportHook()
        self._completed = True  # Never again send updates for this breakpoint.
        if self._cookie is None:
            return

        native.LogInfo("Clearing breakpoint %s" % self.GetBreakpointId())
        new_co_code = native.ClearConditionalBreakpoint(self._cookie)

        if sys.hexversion >= 0x030B0000:
            status, code_object_node = module_explorer.GetCodeObjectAtLine(self._module, self._line)
            if not status:
                # in some cases the code object exists but can't be found after adding of an action due to
                # https://lightrun.atlassian.net/browse/LGT-11143
                status, code_object_node = module_explorer.GetCodeObjectAtFirstLineNo(self._module, self._original_code_object.co_firstlineno)
                if not status:
                    return  # The code object can no longer be found in the module, so there is nothing to clear
            new_co_consts = self._get_up_to_date_co_consts(code_object_node.obj, self._original_code_object)
            new_code_object = self._original_code_object.replace(
                co_code=new_co_code,
                co_consts=new_co_consts,
                co_linetable=self._original_code_object.co_linetable,
                co_exceptiontable=self._original_code_object.co_exceptiontable,
            )
            self._set_code_object(code_object_node, new_code_object)

        self._cookie = None

    def GetBreakpointId(self):
        return self.definition["id"]

    def GetExpirationTime(self):
        """Computes the timestamp at which this breakpoint will expire."""
        return self.expiration_datetime

    def ExpireBreakpoint(self):
        """Expires this breakpoint."""
        # Let only one thread capture the data and complete the breakpoint.
        if not self._SetCompleted():
            return
        native.LogInfo("Completing breakpoint as expired - ID %s" % (self.GetBreakpointId()))
        self._CompleteBreakpoint({"status": None})

    def _GetActionType(self):
        return self.definition.get("action")

    def _ActivateBreakpointInternal(self, module):
        """Sets the breakpoint in the loaded module, or complete with error."""
        self._module = module
        # First remove the import hook (if installed).
        self._RemoveImportHook()

        # Find the code object in which the breakpoint is being set.
        status, code_object_node = module_explorer.GetCodeObjectAtLine(self._module, self._line)
        if not status:
            # First two parameters are common: the line of the breakpoint and the
            # module we are trying to insert the breakpoint in.
            # TODO(google): Do not display the entire path of the file. Either
            # strip some prefix, or display the path in the breakpoint.

            params = [str(self._line), os.path.splitext(module.__file__)[0] + ".py"]

            # The next 0, 1, or 2 parameters are the alternative lines to set the
            # breakpoint at, displayed for the user's convenience.
            alt_lines = (str(l) for l in code_object_node if l is not None)
            params += alt_lines

            if len(params) == 4:
                fmt = messages.ERROR_LOCATION_NO_CODE_FOUND_AT_LINE_4
            elif len(params) == 3:
                fmt = messages.ERROR_LOCATION_NO_CODE_FOUND_AT_LINE_3
            else:
                fmt = messages.ERROR_LOCATION_NO_CODE_FOUND_AT_LINE_2

            self._CompleteBreakpoint(
                {
                    "status": {
                        "isError": True,
                        "refersTo": "BREAKPOINT_SOURCE_LOCATION",
                        "description": {"id": fmt.id, "format": fmt.value, "parameters": params},
                    }
                }
            )
            return

        # Compile the breakpoint condition.
        condition = None
        if self.definition.get("condition"):
            try:
                condition = compile(self.definition.get("condition"), "<condition_expression>", "eval")
            except (TypeError, ValueError) as e:
                err = messages.ERROR_INVALID_EXPRESSION
                # condition string contains null bytes.
                self._CompleteBreakpoint(
                    {
                        "status": {
                            "isError": True,
                            "refersTo": "BREAKPOINT_CONDITION",
                            "description": {"id": err.id, "format": err.value, "parameters": [str(e)]},
                        }
                    }
                )
                return

            except SyntaxError as e:
                err = messages.ERROR_EXPRESSION_COMPILATION_ERROR
                self._CompleteBreakpoint(
                    {"status": {"isError": True, "refersTo": "BREAKPOINT_CONDITION", "description": {"id": err.id, "format": err.value, "parameters": [e.msg]}}}
                )
                return

        code_obj = code_object_node.obj
        native.LogInfo("Creating new Python breakpoint %s in %s, line %d" % (self.GetBreakpointId(), code_obj, self._line))

        try:
            self._cookie, new_co_code = native.SetConditionalBreakpoint(code_obj, self._line, condition, self._BreakpointEvent, self._ignore_quota)
        except Exception as e:
            self._CompleteBreakpoint({"status": {"isError": True, "refersTo": "UNSPECIFIED", "description": {"format": str(e)}}})
            return

        if sys.hexversion >= 0x030B0000:  # Python 3.11
            new_co_consts = self._get_up_to_date_co_consts(code_object_node.obj, code_obj)
            new_code_object = code_obj.replace(
                co_code=new_co_code, co_consts=new_co_consts, co_linetable=code_obj.co_linetable, co_exceptiontable=code_obj.co_exceptiontable
            )
            self._set_code_object(code_object_node, new_code_object)
            self._original_code_object = code_obj

        if self._cookie != -1:
            self._ReportBreakpointAccepted()

    def _RemoveImportHook(self):
        """Removes the import hook if one was installed."""
        if self._import_hook_cleanup:
            self._import_hook_cleanup()
            self._import_hook_cleanup = None

    def _ReportBreakpointAccepted(self):
        """Updates the breakpoint status in the backend to Accepted"""
        data = dict(self.definition)
        data["isFinalState"] = False
        data["status"] = {
            "isError": False,
            "isAccepted": True,
            "refersTo": "UNSPECIFIED",
        }
        self._hub_client.EnqueueBreakpointUpdate(data)

    def _CompleteBreakpoint(self, data):
        """Deactivates the breakpoint and also sends breakpoint update upon error."""

        if data and data.get("status") and data["status"].get("isError"):
            data = dict(self.definition, **data)
            native.LogError("Completing breakpoint with error - ID %s, status %s" % (self.GetBreakpointId(), data))
            self._UpdateBreakpoint(data)

        self._breakpoints_manager.CompleteBreakpoint(self.GetBreakpointId())
        self.Clear()

    def _UpdateBreakpoint(self, data):
        """Sends breakpoint update."""

        data["isFinalState"] = True
        self._hub_client.EnqueueBreakpointUpdate(data)

    def _SetCompleted(self):
        """Atomically marks the breakpoint as completed.

        Returns:
          True if the breakpoint wasn't marked already completed or False if the
          breakpoint was already completed.
        """
        with self._lock:
            if self._completed:
                return False
            self._completed = True
            return True

    def _BreakpointEvent(self, event, frame):
        """Callback invoked by cdbg_native when breakpoint hits.

        Args:
          event: breakpoint event (see kIntegerConstants in native_module.cc).
          frame: Python stack frame of breakpoint hit or None for other events.
        """
        self._hit_count += 1

        error_status = None

        if event != native.BREAKPOINT_EVENT_HIT:
            error_status = _BREAKPOINT_EVENT_STATUS[event]
        elif self._GetActionType() == "LOG":
            error_status = self._collector.Log(frame)
        elif self._IsCaptureAction():
            # TODO(yaniv): This is a temporary try/except. All exceptions should be
            # caught inside Collect and converted into breakpoint error messages.
            try:
                # A new collector object should be initialized upon each capture hit
                self._collector = capture_collector.CaptureCollector(self.definition, self._data_visibility_manager)
                self._collector.Collect(frame)
            except BaseException as e:  # pylint: disable=broad-except
                native.LogInfo("Internal error during data capture: %s" % repr(e))
                error_status = {"isError": True, "description": {"format": ("Internal error while capturing data: %s" % repr(e))}}
            except:  # pylint: disable=bare-except # noqa: E722
                native.LogInfo("Unknown exception raised")
                error_status = {"isError": True, "description": {"format": "Unknown internal error"}}
            else:
                capture_time = time.time()
                data = dict(self._collector.breakpoint, **{"createTime": {"seconds": int(capture_time), "nanos": capture_time % 1}})
                self._UpdateBreakpoint(data)

        if not self._IsCaptureAction() or self._hit_count < self.definition.get("maxHitCount", 1):
            if not error_status:
                return

        # Let only one thread capture the data and complete the breakpoint.
        if not self._SetCompleted():
            return

        self.Clear()

        self._CompleteBreakpoint({"status": error_status})

    @staticmethod
    def _set_code_object(code_object_node, code_object):
        if hasattr(code_object_node.parent, "__code__"):
            code_object_node.parent.__code__ = code_object
        elif isinstance(code_object_node.parent, tuple):
            # The code object was referenced by the co_consts table of another code object
            previous_co_consts = list(code_object_node.parent)
            index = previous_co_consts.index(code_object_node.obj)
            new_co_consts = list(code_object_node.grandparent.co_consts)
            new_co_consts[index] = code_object
            native.UpdateCoConsts(code_object_node.grandparent, tuple(new_co_consts))
        else:
            native.LogError("Unexpected parent of code object. Action will not take effect.")

    def _get_up_to_date_co_consts(self, up_to_date_code_object, native_updated_code_object):
        """
        When removing a breakpoint, the native code builds the new co_consts based on the code_object from the time
        the breakpoint was inserted. It was assumed that this code object will always be the "active" code object of
        the function, but this no longer holds in our implementation for python 3.11.
        To compensate for this we construct a "correct" co_consts tuple from two parts - the consts of the original
        method taken from an up-to-date version of the code_object, and lightrun related consts taken from the output
        of our code_object manipulation.
        """
        original_co_const_size = len(up_to_date_code_object.co_consts) - self._get_breakpoint_count_on_code_object(up_to_date_code_object)
        non_lightrun_co_consts = up_to_date_code_object.co_consts[:original_co_const_size]
        lightrun_co_consts = native_updated_code_object.co_consts[original_co_const_size:]
        return tuple(non_lightrun_co_consts + lightrun_co_consts)

    def _get_breakpoint_count_on_code_object(self, code_object):
        count = 0
        for obj in reversed(code_object.co_consts):
            if self._is_lightrun_callback(obj):
                count += 1
            else:
                break
        return count

    @staticmethod
    def _is_lightrun_callback(obj):
        try:
            return isinstance(obj, types.BuiltinFunctionType) and obj.__name__ == "Callback" and obj.__module__.__name__ == "lightrun.cdbg_native"
        except AttributeError:
            return False

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

"""Captures application state on a breakpoint hit."""

import copy
import datetime
import inspect
import itertools
import math
import re
import types

from . import lightrun_config, messages, utils

_PRIMITIVE_TYPES = (type(None), float, complex, bool, slice, bytearray, bytes, int, str)
_DATE_TYPES = (datetime.date, datetime.time, datetime.timedelta)
_VECTOR_TYPES = (tuple, list, set)


class _CaptureLimits(object):
    """
    Limits for variable capture.

    Args:
      max_value_len: Maximum number of character to allow for a single string
        value.  Longer strings are truncated.
      max_list_items: Maximum number of items in a list to capture.
      max_depth: Maximum depth of dictionaries to capture.
    """

    def __init__(self, max_value_len=256, max_list_items=25, max_depth=5, max_object_members=100):
        self.max_value_len = max_value_len
        self.max_list_items = max_list_items
        self.max_depth = max_depth
        self.max_object_members = max_object_members


class CaptureCollector(object):
    """
    Captures application state snapshot.

    Captures call stack, local variables and referenced objects. Then formats the
    result to be sent back to the user.

    The performance of this class is important. Once the breakpoint hits, the
    completion of the user request will be delayed until the collection is over.
    It might make sense to implement this logic in C++.

    Attributes:
      breakpoint: breakpoint definition augmented with captured call stack,
          local variables, arguments and referenced objects.
    """

    # Additional type-specific printers. Each pretty printer is a callable
    # that returns None if it doesn't recognize the object or returns a tuple
    # with iterable enumerating object fields (name-value tuple) and object type
    # string.
    pretty_printers = []

    def __init__(self, definition, data_visibility_manager):
        """Class constructor.

        Args:
          definition: breakpoint definition that this class will augment with
              captured data.
          data_visibility_manager: An instance of DataVisibilityManager, used to determine the visibiliy
              of captured variables.
        """
        self._data_visibility_manager = data_visibility_manager

        self.breakpoint = copy.deepcopy(definition)

        self.breakpoint["stackFrames"] = []
        self.breakpoint["evaluatedExpressions"] = []
        self.breakpoint["variableTable"] = [
            {"status": {"isError": True, "refersTo": "VARIABLE_VALUE", "description": {"format": "Buffer full. Use an expression to see more data"}}}
        ]

        # Shortcut to variables table in the breakpoint message.
        self._var_table = self.breakpoint["variableTable"]

        # Maps object ID to its index in variables table.
        self._var_table_index = {}

        # Total size of data collected so far. Limited by max_size.
        self._total_size = 0

        # Maximum number of stack frame to capture. The limit is aimed to reduce
        # the overall collection time.
        self.max_frames = 20

        # Only collect locals and arguments on the few top frames. For the rest of
        # the frames we only collect the source location.
        self.max_expand_frames = lightrun_config.GetMaxFramesWithVars()

        # Maximum amount of data to capture. The application will usually have a
        # lot of objects and we need to stop somewhere to keep the delay
        # reasonable.
        # This constant only counts the collected payload. Overhead due to key
        # names is not counted.
        self.max_size = lightrun_config.GetMaxSnapshotBufferSize()

        self.default_capture_limits = _CaptureLimits(
            max_value_len=lightrun_config.GetMaxVariableSize(),
            max_list_items=lightrun_config.GetMaxCollectionSize(),
            max_object_members=lightrun_config.GetMaxObjectMembers(),
        )

        # When the user provides an expression, they've indicated that they're
        # interested in some specific data. Use higher per-object capture limits
        # for expressions. We don't want to globally increase capture limits,
        # because in the case where the user has not indicated a preference, we
        # don't want a single large object on the stack to use the entire max_size
        # quota and hide the rest of the data.
        self.expression_capture_limits = _CaptureLimits(
            max_value_len=lightrun_config.GetMaxWatchExpressionSize(),
            max_list_items=lightrun_config.GetMaxWatchlistCollectionSize(),
            max_object_members=lightrun_config.GetMaxObjectMembers(),
        )

    def Collect(self, top_frame):
        """Collects call stack, local variables and objects.

        Starts collection from the specified frame. We don't start from the top
        frame to exclude the frames due to debugger. Updates the content of
        self.breakpoint.

        Args:
          top_frame: top frame to start data collection.
        """
        frame = top_frame
        top_line = self.breakpoint["location"]["line"]
        breakpoint_frames = self.breakpoint["stackFrames"]
        try:
            # Evaluate watched expressions.
            if "expressions" in self.breakpoint:
                self.breakpoint["evaluatedExpressions"] = [
                    self._CaptureExpression(top_frame, expression, len(self.breakpoint["expressions"])) for expression in self.breakpoint["expressions"]
                ]

            while frame and (len(breakpoint_frames) < self.max_frames):
                line = top_line if frame == top_frame else frame.f_lineno
                code = frame.f_code
                if len(breakpoint_frames) < self.max_expand_frames:
                    frame_arguments, frame_locals = self.CaptureFrameLocals(frame)
                else:
                    frame_arguments = []
                    frame_locals = []

                breakpoint_frames.append(
                    {
                        "function": _GetFrameCodeObjectName(frame),
                        "location": {"path": utils.NormalizePath(code.co_filename), "line": line},
                        "arguments": frame_arguments,
                        "locals": frame_locals,
                    }
                )

                frame = frame.f_back

        except BaseException as e:  # pylint: disable=broad-except
            # The variable table will get serialized even though there was a failure.
            # The results can be useful for diagnosing the internal error.
            self.breakpoint["status"] = {
                "isError": True,
                "description": {
                    "format": ("INTERNAL ERROR: Failed while capturing locals of frame $0: $1"),
                    "parameters": [str(len(breakpoint_frames)), str(e)],
                },
            }

        # Number of entries in _var_table. Starts at 1 (index 0 is the 'buffer full'
        # status value).
        num_vars = 1

        # Explore variables table in BFS fashion. The variables table will grow
        # inside CaptureVariable as we encounter new references.
        while (num_vars < len(self._var_table)) and (self._total_size < self.max_size):
            variable = self.CaptureVariable(self._var_table[num_vars], 0, self.default_capture_limits, 0, can_enqueue=False)
            if self._total_size < self.max_size:
                self._var_table[num_vars] = variable
                # Move on to the next entry in the variable table.
                num_vars += 1

        # Trim variables table and change make all references to variables that
        # didn't make it point to var_index of 0 ("buffer full")
        self.TrimVariableTable(num_vars)

    def CaptureFrameLocals(self, frame):
        """Captures local variables and arguments of the specified frame.

        Args:
          frame: frame to capture locals and arguments.

        Returns:
          (arguments, locals) tuple.
        """
        if not self._data_visibility_manager.IsFileVisible(utils.NormalizePath(frame.f_code.co_filename))[0]:
            return [], []

        # Capture all local variables (including method arguments).
        variables = {n: self.CaptureNamedVariable(n, v, 1, self.default_capture_limits, 0) for n, v in frame.f_locals.items()}

        # Split between locals and arguments (keeping arguments in the right order).
        nargs = frame.f_code.co_argcount
        if frame.f_code.co_flags & inspect.CO_VARARGS:
            nargs += 1
        if frame.f_code.co_flags & inspect.CO_VARKEYWORDS:
            nargs += 1

        frame_arguments = []
        for argname in frame.f_code.co_varnames[:nargs]:
            if argname in variables:
                frame_arguments.append(variables.pop(argname))

        return (frame_arguments, list(variables.values()))

    def CaptureNamedVariable(self, name, value, depth, limits, expressionsCount):
        """Appends name to the product of CaptureVariable.

        Args:
          name: name of the variable.
          value: data to capture
          depth: nested depth of dictionaries and vectors so far.
          limits: Per-object limits for capturing variable data.

        Returns:
          Formatted captured data as per Variable proto with name.
        """
        if not hasattr(name, "__dict__"):
            name = str(name)
        else:  # TODO(google): call str(name) with immutability verifier here.
            name = str(id(name))
        self._total_size += len(name)

        v = self.CheckDataVisibility(value) or self.CaptureVariable(value, depth, limits, expressionsCount)
        v["name"] = name
        return v

    def CheckDataVisibility(self, value):
        """Returns a status object if the given name is not visible.

        Args:
          value: The value to check.  The actual value here is not important but the
          value's metadata (e.g. package and type) will be checked.

        Returns:
          None if the value is visible.  A variable structure with an error status
          if the value should not be visible.
        """
        visible, reason = self._data_visibility_manager.IsDataVisible(utils.DetermineType(value))

        if visible:
            return None

        return {"status": {"isError": True, "refersTo": "VARIABLE_NAME", "description": {"format": reason}}}

    def CaptureVariablesList(self, items, depth, empty_message, limits, object_members=False):
        """Captures list of named items.

        Args:
          items: iterable of (name, value) tuples.
          depth: nested depth of dictionaries and vectors for items.
          empty_message: info status message to set if items is empty.
          limits: Per-object limits for capturing variable data.
          object_members: Whether items are object members or not.

        Returns:
          List of formatted variable objects.
        """
        max_items = limits.max_list_items
        if object_members:
            max_items = limits.max_object_members
        v = []
        for name, value in items:
            if (self._total_size >= self.max_size) or (len(v) >= max_items):
                v.append(
                    {
                        "status": {
                            "refersTo": "VARIABLE_VALUE",
                            "description": {
                                "format": ("Only first $0 items were captured. Use in an expression to see all items."),
                                "parameters": [str(len(v))],
                            },
                        }
                    }
                )
                break
            v.append(self.CaptureNamedVariable(name, value, depth, limits, 0))

        if not v:
            return [{"status": {"refersTo": "VARIABLE_NAME", "description": {"format": empty_message}}}]

        return v

    def CaptureVariable(self, value, depth, limits, expressionsCount, can_enqueue=True):
        """Try-Except wrapped version of CaptureVariableInternal."""
        try:
            return self.CaptureVariableInternal(value, depth, limits, expressionsCount, can_enqueue)
        except BaseException as e:  # pylint: disable=broad-except
            return {
                "status": {"isError": True, "refersTo": "VARIABLE_VALUE", "description": {"format": ("Failed to capture variable: $0"), "parameters": [str(e)]}}
            }

    def CaptureVariableInternal(self, value, depth, limits, expressionsCount=0, can_enqueue=True):
        """Captures a single nameless object into Variable message.

        TODO(google): safely evaluate iterable types.
        TODO(google): safely call str(value)

        Args:
          value: data to capture
          depth: nested depth of dictionaries and vectors so far.
          limits: Per-object limits for capturing variable data.
          can_enqueue: allows referencing the object in variables table.

        Returns:
          Formatted captured data as per Variable proto.
        """
        if depth == limits.max_depth:
            return {"varTableIndex": 0}  # Buffer full.

        if value is None:
            self._total_size += 4
            return {"value": "None"}

        if isinstance(value, _PRIMITIVE_TYPES):
            value_len = len(repr(value))
            remaining_buffer_size = self.max_size - self._total_size
            max_value_len, expression_limit = self._GetDynamicLimit(expressionsCount, limits)

            status_err = None
            params = []
            if expression_limit >= value_len >= min(max_value_len, remaining_buffer_size):
                # that means that the value size is too big for regular snapshot, but we can suggest
                # the user to use a watch expression in the snapshot
                status_err = messages.ERROR_EXPRESSION_IS_BIGGER_THAN_MAX_OBJECT_SIZE
                params = [max_value_len]
            elif value_len > expression_limit:
                # that means that the value size is too big even for a watch expression, but we can suggest
                # the user to adjust the value size in the agent configuration
                status_err = messages.ERROR_EXPRESSION_IS_BIGGER_THAN_MAX_WATCH_EXPRESSION_SIZE
                params = [expression_limit]

            status = {}
            if status_err:
                status = {
                    "status": {
                        "isError": True,
                        "refersTo": "VARIABLE_VALUE",
                        "description": messages.toJson(status_err, params),
                    }
                }

            r = utils.TrimString(
                repr(value),  # Primitive type, always immutable.
                min(max_value_len, self.max_size - self._total_size),
            )
            self._total_size += len(r)
            return {"value": r, "type": type(value).__name__, **status}

        if isinstance(value, _DATE_TYPES):
            r = str(value)  # Safe to call str().
            self._total_size += len(r)
            return {"value": r, "type": "datetime." + type(value).__name__}

        if isinstance(value, dict):
            # Do not use iteritems() here. If GC happens during iteration (which it
            # often can for dictionaries containing large variables), you will get a
            # RunTimeError exception.
            items = [(repr(k), v) for (k, v) in value.items()]
            return {"members": self.CaptureVariablesList(items, depth + 1, messages.EMPTY_DICTIONARY, limits), "type": "dict"}

        if isinstance(value, _VECTOR_TYPES):
            fields = self.CaptureVariablesList((("[%d]" % i, x) for i, x in enumerate(value)), depth + 1, messages.EMPTY_COLLECTION, limits)
            return {"members": fields, "type": type(value).__name__}

        if isinstance(value, types.FunctionType):
            self._total_size += len(value.__name__)
            # TODO(google): set value to func_name and type to 'function'
            return {"value": "function " + value.__name__}

        if isinstance(value, Exception):
            fields = self.CaptureVariablesList((("[%d]" % i, x) for i, x in enumerate(value.args)), depth + 1, messages.EMPTY_COLLECTION, limits)
            return {"members": fields, "type": type(value).__name__}

        if can_enqueue:
            index = self._var_table_index.get(id(value))
            if index is None:
                index = len(self._var_table)
                self._var_table_index[id(value)] = index
                self._var_table.append(value)
            self._total_size += 4  # number of characters to accommodate a number.
            return {"varTableIndex": index}

        for pretty_printer in CaptureCollector.pretty_printers:
            pretty_value = pretty_printer(value)
            if not pretty_value:
                continue

            fields, object_type = pretty_value
            return {"members": self.CaptureVariablesList(fields, depth + 1, messages.OBJECT_HAS_NO_FIELDS, limits), "type": object_type}

        if not hasattr(value, "__dict__"):
            # TODO(google): keep "value" empty and populate the "type" field instead.
            r = str(type(value))
            self._total_size += len(r)
            return {"value": r}

        evaluated_expressions_indexes = set((evaluated_expression.get("varTableIndex") for evaluated_expression in self.breakpoint["evaluatedExpressions"]))
        evaluated_expressions_values = [self._var_table[index] for index in evaluated_expressions_indexes if index is not None]
        if inspect.ismodule(value) and value not in evaluated_expressions_values:
            v = {"value": value.__name__}
        else:
            # Add an additional depth for the object itself
            items = value.__dict__.items()
            # Make a list of the iterator, to avoid 'dict changed size
            # during iteration' errors from GC happening in the middle.
            # Only limits.max_object_members + 1 items are copied, anything past that will
            # get ignored by CaptureVariablesList().
            items = list(itertools.islice(items, limits.max_object_members + 1))
            members = self.CaptureVariablesList(items, depth + 2, messages.OBJECT_HAS_NO_FIELDS, limits, object_members=True)
            v = {"members": members}

        type_string = utils.DetermineType(value)
        if type_string:
            v["type"] = type_string

        return v

    def _GetDynamicLimit(self, expressionsCount, limits):
        if expressionsCount == 0:
            return limits.max_value_len, lightrun_config.GetMaxWatchExpressionSize()
        max_value_len = math.floor(limits.max_value_len / expressionsCount)
        expression_limit = max_value_len if max_value_len > lightrun_config.GetMaxVariableSize() else lightrun_config.GetMaxWatchExpressionSize()
        return expression_limit, expression_limit

    def _CaptureExpression(self, frame, expression, expressionsCount):
        """Evalutes the expression and captures it into a Variable object.

        Args:
          frame: evaluation context.
          expression: watched expression to compile and evaluate.

        Returns:
          Variable object (which will have error status if the expression fails
          to evaluate).
        """
        eval_success, value = utils.EvaluateExpression(frame, expression)
        if not eval_success:
            return {"name": expression, "status": value}

        return self.CaptureNamedVariable(expression, value, 0, self.expression_capture_limits, expressionsCount)

    def TrimVariableTable(self, new_size):
        """Trims the variable table in the formatted breakpoint message.

        Removes trailing entries in variables table. Then scans the entire
        breakpoint message and replaces references to the trimmed variables to
        point to var_index of 0 ("buffer full").

        Args:
          new_size: desired size of variables table.
        """

        def ProcessBufferFull(variables):
            for variable in variables:
                var_index = variable.get("varTableIndex")
                if var_index is not None and (var_index >= new_size):
                    variable["varTableIndex"] = 0  # Buffer full.
                members = variable.get("members")
                if members is not None:
                    ProcessBufferFull(members)

        del self._var_table[new_size:]
        ProcessBufferFull(self.breakpoint["evaluatedExpressions"])
        for stack_frame in self.breakpoint["stackFrames"]:
            ProcessBufferFull(stack_frame["arguments"])
            ProcessBufferFull(stack_frame["locals"])
        ProcessBufferFull(self._var_table)

    def _StoreLabel(self, name, value):
        """Stores the specified label in the breakpoint's labels.

        In the event of a duplicate label, favour the pre-existing labels. This
        generally should not be an issue as the pre-existing client label names are
        chosen with care and there should be no conflicts.

        Args:
          name: The name of the label to be stored.
          value: The value of the label to be stored.
        """
        if name not in self.breakpoint["labels"]:
            self.breakpoint["labels"][name] = value


def _GetFrameCodeObjectName(frame):
    """Gets the code object name for the frame.

    Args:
      frame: the frame to get the name from

    Returns:
      The function name if the code is a static function or the class name with
      the method name if it is an member function.
    """
    # This functions under the assumption that member functions will name their
    # first parameter argument 'self' but has some edge-cases.
    if frame.f_code.co_argcount >= 1 and "self" == frame.f_code.co_varnames[0]:
        return frame.f_locals["self"].__class__.__name__ + "." + frame.f_code.co_name
    else:
        return frame.f_code.co_name


def _FormatMessage(template, parameters):
    """Formats the message. Unescapes '$$' with '$'.

    Args:
      template: message template (e.g. 'a = $0, b = $1').
      parameters: substitution parameters for the format.

    Returns:
      Formatted message with parameters embedded in template placeholders.
    """

    def GetParameter(m):
        try:
            return parameters[int(m.group(0)[1:])]
        except IndexError:
            return messages.INVALID_EXPRESSION_INDEX

    parts = template.split("$$")
    return "$".join(re.sub(r"\$\d+", GetParameter, part) for part in parts)

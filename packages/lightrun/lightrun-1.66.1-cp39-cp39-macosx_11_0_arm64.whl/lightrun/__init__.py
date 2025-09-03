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

"""Main module for Python Cloud Debugger.

The debugger is enabled in a very similar way to enabling pdb.

The debugger becomes the main module. It eats up its arguments until it gets
to argument '--' that serves as a separator between debugger arguments and
the application command line. It then attaches the debugger and runs the
actual app.
"""

import atexit
import os
import signal
import sys
import threading

from . import (
    appengine_pretty_printers,
    breakpoints_manager,
    capture_collector,
    data_visibility_manager,
    hub_client,
    lightrun_config,
    log_collector,
    module_search,
    piping_manager,
    utils,
    version_retriever,
)
from .lightrun_native import native

MAIN_PROCESS_NAME = "main"
FORK_PROCESS_NAME = "fork"

SUCCESS_INIT_PROCESS_STATUS = True
FAILED_INIT_PROCESS_STATUS = False
STOPPED_PROCESS_STATUS = False

_flags = {}
_main_pid = None
_is_main_process_initialized = False
_is_forked_process_initialized = False
_piping_manager = None
_hub_client = None
_breakpoints_manager = None
_main_lock = threading.Lock()
_fork_lock = threading.Lock()

original_sigterm_handler = signal.getsignal(signal.SIGTERM)
if not utils.is_windows():
    original_sigquit_handler = signal.getsignal(signal.SIGQUIT)


def init_debugger(debugger, pid):
    try:
        disable_lightrun_agent = os.environ.get("DISABLE_LIGHTRUN_AGENT", "0")
        if disable_lightrun_agent.lower() in ["true", "1"]:
            print("Env variable DISABLE_LIGHTRUN_AGENT is set to '%s'. Lightrun agent is disabled." % disable_lightrun_agent)
            return
        if debugger.is_enabled():
            raise RuntimeError("Current pid: %d | Debugger already attached" % (pid))
        debugger.init()
        debugger.update_process_status(SUCCESS_INIT_PROCESS_STATUS)
        print("Current pid: %d | Successfully finished Lightrun enable process" % (pid))
    except Exception as e:
        debugger.update_process_status(FAILED_INIT_PROCESS_STATUS)
        raise RuntimeError("Current pid: %d | Lightrun enable process failed: Exception: %s" % (pid, e))


def enable(**kwargs):
    """
    Starts the debugger for already running application.
    This function should only be called once.

    Args:
      **kwargs: debugger configuration flags.

    Raises:
      RuntimeError: if called more than once.
      ValueError: if flags is not a valid dictionary.
    """
    global _flags

    pid = os.getpid()

    print("Current pid: %d | Starting Lightrun enable process" % (pid))

    _flags = kwargs
    identify_process()

    print("Current pid: %d | Process type: %s" % (pid, _flags["process_type"]))

    with GoogleCloudDebuggerInitializer(_flags["process_type"], _main_lock, _fork_lock) as debugger:
        init_debugger(debugger, pid)


def disable():
    pid = os.getpid()

    print("Current pid: %d | Starting Lightrun disable process" % (pid))

    identify_process()

    print("Current pid: %d | Process type: %s" % (pid, _flags["process_type"]))

    with GoogleCloudDebuggerInitializer(_flags["process_type"], _main_lock, _fork_lock) as debugger:
        try:
            if not debugger.is_enabled():
                print("Current pid: %d | Lightrun is not enabled so no need to disable" % (pid))
                return
            debugger.close()
            debugger.update_process_status(STOPPED_PROCESS_STATUS)
            print("Current pid: %d | Successfully finished Lightrun disable process" % (pid))
        except Exception as e:
            raise RuntimeError("Current pid: %d | Lightrun disable process failed: Exception: %s" % (pid, e))


def identify_process():
    global _main_pid

    # Using the pid we will know if we are the main or fork process
    if _main_pid is None:
        _main_pid = os.getpid()

    pid = os.getpid()

    # That means there is already a main parent process running with lightrun enabled, and we are the child forked process
    if _main_pid != pid:
        native.LogWarning(
            "The current pid: %d does not match the original pid: %d, meaning you are trying to enable Lightrun from a different proccess that is forked from or related to the original process"
            % (pid, _main_pid)
        )
        _flags["process_type"] = FORK_PROCESS_NAME
    # That means we are the main parent process
    else:
        _flags["process_type"] = MAIN_PROCESS_NAME


def signal_handler(sig, frame):
    _hub_client._DeregisterDebuggee()
    signal.signal(signal.SIGTERM, original_sigterm_handler)
    # We need to throw it again (in case the actual program is registered to it):
    os.kill(os.getpid(), sig)


def exit_handler():
    _hub_client._DeregisterDebuggee()


def addLogHandler(handler):
    log_collector.lightrun_logger.addHandler(handler)


class GoogleCloudDebuggerInitializer:
    """
    Handles the initalization process for the Google Cloud Debugger
    Also contains a locking mechanism that makes sure the debugger does not get initialized more than once
    Arguments:
        process_type: The type of the process, currently either main or fork. Default is main
        main_lock: (Optional) If you wish to make the main process thread safe pass a lock
        fork_lock: (Optional) If you wish to make the fork process thread safe pass a lock
    """

    def __init__(self, process_type=MAIN_PROCESS_NAME, main_lock=None, fork_lock=None):
        self.process_type = process_type
        # Handles locking for the main process
        self.main_lock = main_lock
        # Handles locking for each forked process
        self.fork_lock = fork_lock

    def __enter__(self):
        if self.main_lock is not None and self.process_type == MAIN_PROCESS_NAME:
            self.main_lock.acquire()
        elif self.fork_lock is not None and self.process_type == FORK_PROCESS_NAME:
            self.fork_lock.acquire()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.main_lock is not None and self.process_type == MAIN_PROCESS_NAME:
            self.main_lock.release()
        elif self.fork_lock is not None and self.process_type == FORK_PROCESS_NAME:
            self.fork_lock.release()

    """
    Updates the relevant process status depending on the received status
    """

    def update_process_status(self, process_status):
        global _is_main_process_initialized
        global _is_forked_process_initialized

        if self.process_type == MAIN_PROCESS_NAME:
            _is_main_process_initialized = process_status

        if self.process_type == FORK_PROCESS_NAME:
            _is_forked_process_initialized = process_status

    """
    Checks if the Lightrun agent (Google Cloud Debugger) was already enabled on the current process.
    The Lightrun agent can't be enabled twice in the same process.
    """

    def is_enabled(self):
        if self.process_type == MAIN_PROCESS_NAME:
            return _is_main_process_initialized

        if self.process_type == FORK_PROCESS_NAME:
            # We give the option to disable forked agents
            if not _flags["should_allow_forked_agents"]:
                return True

            return _is_forked_process_initialized

    """Configures and starts the debugger"""

    def init(self):
        global _hub_client
        global _piping_manager
        global _breakpoints_manager

        pid = os.getpid()

        # Initialize configuration
        lightrun_config.InitializeConfig(_flags.get("agent_config"), _flags)

        # Initialize native module
        native.InitializeModule(lightrun_config.config)
        native.LogInfo("Current pid: %d | Initializing Cloud Debugger Python agent version: %s" % (pid, version_retriever.get_version_full()))

        # Create the agent components and inject dependencies to one another
        _piping_manager = piping_manager.LogPipingManager()
        native.LogInfo("Current pid: %d | LogPipingManager Initialized" % (pid))
        _data_visibility_manager = data_visibility_manager.DataVisibilityManager()
        native.LogInfo("Current pid: %d | DataVisibilityManager Initialized" % (pid))
        _hub_client = hub_client.HubClient(_piping_manager, _data_visibility_manager)
        native.LogInfo("Current pid: %d | HubClient Initialized" % (pid))
        _breakpoints_manager = breakpoints_manager.BreakpointsManager(_hub_client, _piping_manager, _data_visibility_manager)
        native.LogInfo("Current pid: %d | BreakpointsManager Initialized" % (pid))
        # Init file search module
        module_search.InitSearch()
        native.LogInfo("Current pid: %d | Search Module Initialized" % (pid))

        # Init logger
        log_collector.InitLogger()
        native.LogInfo("Current pid: %d | Logger Initialized" % (pid))

        capture_collector.CaptureCollector.pretty_printers.append(appengine_pretty_printers.PrettyPrinter)

        _hub_client.on_active_breakpoints_changed = _breakpoints_manager.SetActiveBreakpoints
        _hub_client.on_idle = _breakpoints_manager.CheckBreakpointsExpiration
        _hub_client.InitializeDebuggeeMetadata()
        native.LogInfo("Current pid: %d | InitializeDebuggeeMetadata Initialized" % (pid))

        if self.process_type == FORK_PROCESS_NAME:
            native.LogInfo("Current pid: %d | Detected forked process, stopping Hub Client" % (pid))
            _hub_client.Stop()

        native.LogInfo("Current pid: %d | Starting Hub Client" % (pid))
        _hub_client.Start()
        _hub_client.WaitForBreakpointFetchIfNeeded()

        # Before exit
        atexit.register(exit_handler)

        # Singal register
        if not lightrun_config.config["is_serverless"]:
            # We register signals only on non serverless platforms
            signal.signal(signal.SIGTERM, signal_handler)
            if not utils.is_windows():
                # We register SIGQUIT on non windows platforms
                signal.signal(signal.SIGQUIT, signal_handler)

    def close(self):
        _hub_client.Stop()


def _DebuggerMain():
    """Starts the debugger and runs the application with debugger attached."""
    global _flags

    # The first argument is cdbg module, which we don't care.
    del sys.argv[0]

    # Parse debugger flags until we encounter '--'.
    _flags = {}
    while sys.argv[0]:
        arg = sys.argv[0]
        del sys.argv[0]

        if arg == "--":
            break

        if arg == "--version":
            print(version_retriever.get_version_full())
            return

        (name, value) = arg.strip("-").split("=", 2)
        _flags[name] = value

    pid = os.getpid()

    with GoogleCloudDebuggerInitializer(MAIN_PROCESS_NAME, _main_lock, _fork_lock) as debugger:
        init_debugger(debugger, pid)

    # Run the app. The following code was mostly copied from pdb.py.
    app_path = sys.argv[0]

    sys.path[0] = os.path.dirname(app_path)

    import __main__  # pylint: disable=g-import-not-at-top

    __main__.__dict__.clear()
    __main__.__dict__.update({"__name__": "__main__", "__file__": app_path, "__builtins__": __builtins__})
    locals = globals = __main__.__dict__  # pylint: disable=redefined-builtin  # noqa: A001

    sys.modules["__main__"] = __main__

    with open(app_path) as f:
        code = compile(f.read(), app_path, "exec")
        exec(code, globals, locals)  # pylint: disable=exec-used # noqa: S102

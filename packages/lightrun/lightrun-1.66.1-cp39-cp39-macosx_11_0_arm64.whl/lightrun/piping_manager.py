import threading
import time

from enum import Enum

from .lightrun_native import native


class PipingStatus(Enum):
    APP_ONLY = 1
    PLUGIN_ONLY = 2
    BOTH = 3
    NOT_SET = 4


def getStatus(status):
    if status == "APP_ONLY" or status == PipingStatus.APP_ONLY:
        return PipingStatus.APP_ONLY
    elif status == "PLUGIN_ONLY" or status == PipingStatus.PLUGIN_ONLY:
        return PipingStatus.PLUGIN_ONLY
    elif status == "BOTH" or status == PipingStatus.BOTH:
        return PipingStatus.BOTH
    else:
        return PipingStatus.NOT_SET


class LogPipingManager(object):
    """
    Manager class for the log piping feature.

    Responsible for storing and retrieving the logs that are piped into it.
    """

    def __init__(self):
        self._global_piping_status = PipingStatus.APP_ONLY
        self._breakpoint_id_to_piping = dict()
        self._breakpoint_id_to_logs = dict()
        self._lock = threading.RLock()
        self._order_counter = 0
        # Set of actionIds which hits were reported to the server at least once.
        # Used to track first breakpoint hit even if piping is set to APP_ONLY
        self._actions_reported_to_server = set()
        # Pending actionIds having APP_ONLY status that were not reported to the server yet.
        self._pending_app_only_actions = set()

    def GetLogs(self, breakpoint_id=None):
        """
        Get the pending logs string for a specific breakpoint, or for all breakpoints.
        When logs are returned from this method, they are cleared from the pending logs map.

        Returns:
            A list of logs pending for a specific breakpoint.
            If the breakpoint id isn't specified, all of the agent' pending logs are sent.
            If the breakpoint id doesn't have any pending logs, an empty list is returned.
        """
        with self._lock:
            if breakpoint_id is None:
                # Return all of the agent's piped logs
                logs = dict(self._breakpoint_id_to_logs)
                self._breakpoint_id_to_logs.clear()
                return logs
            elif self._breakpoint_id_to_logs.get(breakpoint_id):
                # Return the logs for the specific breakpoint
                return {breakpoint_id: self._breakpoint_id_to_logs.pop(breakpoint_id)}
            else:
                # No logs available for the specific breakpoint
                return {}

    def AddAppOnlyFirstBreakpointHits(self, breakpoint_ids):
        for breakpoint_id in breakpoint_ids:
            self._pending_app_only_actions.add(breakpoint_id)

    def GetAppOnlyFirstBreakpointHits(self):
        result = []
        for breakpoint_id in self._pending_app_only_actions:
            result.append(breakpoint_id)
        # clear the set when pending logs are collected for sending
        self._pending_app_only_actions.clear()
        return result

    def RemoveBreakpoint(self, breakpoint_id):
        """
        Remove a specific breakpoint piping status.
        """
        with self._lock:
            self._breakpoint_id_to_piping.pop(breakpoint_id, None)
            if breakpoint_id in self._actions_reported_to_server:
                self._actions_reported_to_server.remove(breakpoint_id)
            # In case there are existing piped logs for the removed breakpoint, they are not discarded. Instead, they
            # will be sent to the backend in the next call to GetLogs, and only then they'll be removed.

    def AddLogs(self, logs_dict):
        """
        Shove an entire log data dictionary into the piping storage.
        Each entry key in the log dictionary should be a breakpoint id, and each value should be a list of log data
        objects, where each object is a dictionary with the keys - 'data', 'timestamp', 'level', 'order', 'actionId'.

        This should be used mainly to re-insert log data entries that were retrieved from the piping manager
        back into the local storage (for example, in case of failure to transmit the entries to the backend).
        """
        with self._lock:
            for breakpoint_id, logs in logs_dict:
                if self._breakpoint_id_to_piping.get(breakpoint_id) in [PipingStatus.PLUGIN_ONLY, PipingStatus.BOTH]:
                    if self._breakpoint_id_to_logs[breakpoint_id]:
                        self._breakpoint_id_to_logs[breakpoint_id] += logs
                    else:
                        self._breakpoint_id_to_logs[breakpoint_id] = list(logs)

    def AddLog(self, breakpoint_id, log_data, level, watch_results_data=None):
        """
        Store a single log line that belongs to a specific breakpoint id.
        """
        with self._lock:
            action_piping = self.GetActionPiping(breakpoint_id)
            if action_piping in [PipingStatus.PLUGIN_ONLY, PipingStatus.BOTH]:
                if not self._breakpoint_id_to_logs.get(breakpoint_id):
                    # This is the first pending log for the given breakpoint id
                    self._breakpoint_id_to_logs[breakpoint_id] = list()
                self._breakpoint_id_to_logs[breakpoint_id].append(
                    {
                        "data": log_data,
                        "timestamp": int(time.time() * 1000),  # ts in millis
                        "level": level,
                        "order": self._order_counter,
                        "actionId": breakpoint_id,
                        "watchResultsJsonArray": watch_results_data,
                    }
                )
                self._order_counter += 1
                self._actions_reported_to_server.add(breakpoint_id)
            elif breakpoint_id not in self._actions_reported_to_server:
                self._pending_app_only_actions.add(breakpoint_id)
                self._actions_reported_to_server.add(breakpoint_id)

    def GetActionPiping(self, breakpoint_id):
        """
        Get the piping status of a given breakpoint id.
        If no valid piping status is defined for a breakpoint, the global piping status of the agent is returned.
        """
        if self._breakpoint_id_to_piping.get(breakpoint_id) and self._breakpoint_id_to_piping.get(breakpoint_id) != PipingStatus.NOT_SET:
            return self._breakpoint_id_to_piping.get(breakpoint_id)
        else:
            return self._global_piping_status

    def SetActionPiping(self, breakpoint_id, piping_status):
        """
        Sets the piping status of a specific breakpoint id.
        """
        if getStatus(piping_status) in [PipingStatus.APP_ONLY, PipingStatus.PLUGIN_ONLY, PipingStatus.BOTH]:
            self._breakpoint_id_to_piping[breakpoint_id] = getStatus(piping_status)
        else:
            native.LogWarning("Can't set piping status value %s for breakpoint %s" % (str(piping_status), breakpoint_id))

    def SetGlobalPiping(self, piping_status):
        """
        Sets the global piping status of the agent, which is used for breakpoints without a specific
        piping status defined.
        """
        if getStatus(piping_status) in [PipingStatus.APP_ONLY, PipingStatus.PLUGIN_ONLY, PipingStatus.BOTH, PipingStatus.NOT_SET]:
            self._global_piping_status = getStatus(piping_status)
        else:
            native.LogWarning("Can't set global piping status value %s" % (str(piping_status)))

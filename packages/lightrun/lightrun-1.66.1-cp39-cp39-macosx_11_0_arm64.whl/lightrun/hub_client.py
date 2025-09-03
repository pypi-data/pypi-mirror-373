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

"""Communicates with Cloud Debugger backend over HTTP."""

import base64
import copy
import gzip
import itertools
import json
import os
import socket
import sys
import threading
import time
import traceback

from collections import deque
from io import BytesIO

from . import backoff, connection_manager, environment_metadata, lightrun_config, piping_manager, utils, version_retriever
from .connection_manager import HTTPException
from .lightrun_native import native

# This module catches all exception. This is safe because it runs in
# a daemon thread (so we are not blocking Ctrl+C). We need to catch all
# the exception because HTTP client is unpredictable as far as every
# exception it can throw.
# pylint: disable=broad-except


class HubClient(object):
    """
    Controller API client.

    Registers the debuggee, queries the active breakpoints and sends breakpoint updates to the backend.

    HubClient creates a worker thread that communicates with the backend. The thread can be stopped
    with a Stop function, but it is optional since the worker thread is marked as daemon.
    """

    _DEFAULT_RETRANSMISSION_TIMEOUT_SEC = 10
    _COLLECT_LOG_WAIT_SEC = 1

    def __init__(self, piping_manager, data_visibility_manager):
        self._piping_manager = piping_manager
        self._data_visibility_manager = data_visibility_manager
        self.on_active_breakpoints_changed = lambda x: None
        self.on_idle = lambda: []
        self._metadata = {}
        self._service_account_auth = False
        self._debuggee_id = None
        self._breakpoints = []
        self._main_thread = None
        self._transmission_thread = None
        self._transmission_thread_startup_lock = threading.Lock()
        self._transmission_queue = deque(maxlen=100)
        self._new_updates = threading.Event()
        self._log_collector_thread = None
        self._collect_log_request_id = None
        self._collect_log_event = threading.Event()
        self._first_breakpoint_fetch_event = None
        self._pid = os.getpid()
        self._environment_metadata = environment_metadata.EnvironmentMetadata()

        if lightrun_config.config.get("transmission_bulk_max_size"):
            self._bulk_max_size = int(lightrun_config.config["transmission_bulk_max_size"])
        else:
            self._bulk_max_size = 10  # Default value

        server_url = lightrun_config.GetServerURL()
        self._lightrun_connection_manager = connection_manager.ConnectionManager(utils.GetBaseURL(server_url) + "debuggees")

        # Delay before retrying failed request.
        self.register_backoff = backoff.Backoff()  # Register debuggee.
        self.list_backoff = backoff.Backoff()  # Query active breakpoints.
        self.update_backoff = backoff.Backoff()  # Update breakpoint.

        # Maximum number of times that the message is re-transmitted before it
        # is assumed to be poisonous and discarded
        self.max_transmit_attempts = 10

        if lightrun_config.GetBooleanConfigValue("lightrun_wait_for_init"):
            self._first_breakpoint_fetch_event = threading.Event()

    def InitializeDebuggeeMetadata(self):
        """
        Initialize debuggee metadata from agent configuration and flags.
        Specific keys in the configuration take precedence over the metadata file in the configuration,
        and the commandline flags (which are passed by the caller of this method) take precedence over
        everything else.
        """
        self._metadata = {"registration": {}}

        # All metadata configuration keys / flags should begin with this prefix
        metadata_config_prefix = "metadata_registration_"

        if lightrun_config.config.get("agent_regmetadata_file"):
            metadata_file_path = os.path.join(
                os.path.dirname(lightrun_config.config.get("agent_config") or "."), lightrun_config.config["agent_regmetadata_file"]
            )
            with open(metadata_file_path, "rb") as f:
                self._metadata = json.load(f)
        else:
            for name, value in lightrun_config.config.items():
                if name.startswith(metadata_config_prefix):
                    if name.endswith("tags"):
                        # Special case for tags
                        self._metadata["registration"][name[len(metadata_config_prefix) :]] = json.loads(value)
                    else:
                        self._metadata["registration"][name[len(metadata_config_prefix) :]] = value

    def WaitForBreakpointFetchIfNeeded(self):
        if self._first_breakpoint_fetch_event is None:
            return
        wait_timeout = lightrun_config.config.get("lightrun_init_wait_time_seconds")
        if wait_timeout is None or not isinstance(wait_timeout, int):
            wait_timeout = 2
        event_set = self._first_breakpoint_fetch_event.wait(wait_timeout)
        if not event_set:
            native.LogWarning("Failed to fetch breakpoints before init timeout")

    def Start(self):
        """Starts the worker thread."""
        self._shutdown = False

        self._main_thread = threading.Thread(target=self._MainThreadProc)
        self._main_thread.name = "Cloud Debugger main worker thread"
        self._main_thread.daemon = True
        self._main_thread.start()

        self._log_collector_thread = threading.Thread(target=self._LogCollectionThreadProc)
        self._log_collector_thread.name = "Cloud Debugger log collector thread"
        self._log_collector_thread.daemon = True
        self._log_collector_thread.start()

    def is_shutdown(self):
        # used by test
        return self._shutdown

    def _mark_shutdown(self):
        # Signals the worker threads to shut down
        self._shutdown = True
        self._new_updates.set()  # Wake up the transmission thread to save timeout interval wait

    def _detach(self):
        # We do not need nor want to block on worker threads, and so we will not `join()` worker threads
        self._mark_shutdown()

    def Stop(self):
        self._DeregisterDebuggee()
        # mark shut down
        self._mark_shutdown()

        # and wait for worker threads to exit.
        if self._main_thread is not None:
            self._main_thread.join()
            self._main_thread = None

        if self._transmission_thread is not None:
            self._transmission_thread.join()
            self._transmission_thread = None

        if self._log_collector_thread is not None:
            self._log_collector_thread.join()
            self._log_collector_thread = None

    @staticmethod
    def get_json_size(breakpoint_):
        try:
            return len(json.dumps(breakpoint_).encode("utf-8"))
        except Exception as e:
            native.LogError(f"breakpointId: {breakpoint_.get('id')} failed to calculate breakpoint size: {e}")

    def EnqueueBreakpointUpdate(self, breakpoint_):
        """
        Asynchronously updates the specified breakpoint on the backend.

        This function returns immediately. The worker thread is actually doing
        all the work. The worker thread is responsible to retry the transmission
        in case of transient errors.

        Args:
          breakpoint_: breakpoint in either final or non-final state.
        """
        with self._transmission_thread_startup_lock:
            if self._transmission_thread is None:
                self._transmission_thread = threading.Thread(target=self._TransmissionThreadProc)
                self._transmission_thread.name = "Debugger transmission thread"
                self._transmission_thread.daemon = True
                self._transmission_thread.start()

        breakpoint_size = HubClient.get_json_size(breakpoint_)
        if breakpoint_size is None:
            return
        limit = lightrun_config.GetTransmissionHardMaxNetworkSizeLimitInBytes()
        if breakpoint_size >= limit:
            native.LogWarning(f"breakpointId: {breakpoint_.get('id')} size is {breakpoint_size} which is > maxLimit: {limit}")
            return

        self._transmission_queue.append((breakpoint_, 0))
        self._new_updates.set()  # Wake up the worker thread to send immediately.

    def _registrationFlow(self, registration_required, set_event_on_first_breakpoint_fetch):
        """Registration check and start"""
        delay = 0

        if registration_required:
            registration_required, delay = self._RegisterDebuggee()
            if not registration_required:
                retrieved_blacklist = self._FetchAndSetDataVisibilityAndRedaction()
                if not retrieved_blacklist:
                    native.LogInfo("could not retrieve blacklist, agent registering again")
                    registration_required = True

        fetch_breakpoints_response = None
        if not registration_required:
            fetch_breakpoints_response, delay, should_reregister = self._fetch_active_breakpoints()
            registration_required = fetch_breakpoints_response is None and should_reregister
            if set_event_on_first_breakpoint_fetch:
                self._first_breakpoint_fetch_event.set()
                set_event_on_first_breakpoint_fetch = False

        expired_breakpoints_ids = []
        if self.on_idle is not None:
            expired_breakpoints_ids = self.on_idle()

        if fetch_breakpoints_response is not None:
            self._update_active_breakpoints(fetch_breakpoints_response, expired_breakpoints_ids)
        return registration_required, delay, set_event_on_first_breakpoint_fetch

    def _MainThreadProc(self):
        """Entry point for the worker thread."""
        registration_required = True
        set_event_on_first_breakpoint_fetch = self._first_breakpoint_fetch_event is not None
        while not self._shutdown:
            registration_required, delay, set_event_on_first_breakpoint_fetch = self._registrationFlow(
                registration_required, set_event_on_first_breakpoint_fetch
            )

            if not self._shutdown:
                time.sleep(delay)

    def _TransmissionThreadProc(self):
        """Entry point for the transmission worker thread."""
        # TODO(yaniv): Use this unused reconnect value or remove it
        reconnect = True

        while not self._shutdown:
            self._new_updates.clear()

            reconnect, delay = self._TransmitBreakpointUpdates()

            self._SendPendingLogs()
            self._SendPendingAppOnlyLogHits()

            # Wait until there is an update to be sent to the server or until the timeout occurs
            # Notice - the event is not signaled when there are pending logs for transmission. This
            # is done to avoid connection spamming to the backend on each separate log.
            timeout = delay if delay is not None else HubClient._DEFAULT_RETRANSMISSION_TIMEOUT_SEC
            self._new_updates.wait(timeout)

    def _LogCollectionThreadProc(self):
        """Entry point for the agent log collection worker thread."""
        collect_log_cooldown = int(lightrun_config.config["collect_log_cooldown_ms"]) / 1000
        agent_log_max_file_size_mb = int(lightrun_config.config["agent_log_max_file_size_mb"])
        log_path = native.GetLogFilePath()

        last_collect_log_time = 0
        while not self._shutdown:
            if self._collect_log_event.wait(HubClient._COLLECT_LOG_WAIT_SEC):
                self._collect_log_event.clear()
                remaining_cooldown_time = last_collect_log_time + collect_log_cooldown - time.time()
                if remaining_cooldown_time > 0:
                    native.LogInfo(
                        "Request to collect and send logs to backend before cooldown reached:: remaining [%sms]" % int(remaining_cooldown_time * 1000)
                    )
                    continue
                self._CollectAndSendLog(self._collect_log_request_id, log_path, agent_log_max_file_size_mb)
                last_collect_log_time = time.time()

    def _CollectAndSendLog(self, request_id, file_path, agent_log_max_file_size_mb):
        native.LogInfo("Collect and send log requestId=[%s] filepath=[%s] with maxBytes [%s]" % (request_id, file_path, agent_log_max_file_size_mb))
        try:
            compressed_log = BytesIO()
            with open(file_path, "rb") as log_file, gzip.GzipFile(fileobj=compressed_log, mode="w") as gzip_stream:
                gzip_stream.writelines(log_file)

            self._lightrun_connection_manager.SendHttpRequestByteArray(
                "PUT", self._GetDebuggeeEndpointPath("/compressedLogFileV2/%s" % request_id), compressed_log.getvalue(), "application/octet-stream"
            )
        except IOError:
            native.LogWarning("Failed to send Log file [%s]" % os.path.basename(file_path))

    def _RegisterDebuggee(self):
        """
        Single attempt to register the debuggee.

        If the debuggee succeeds in fully registering or joining the read-only-debuggee
        queue of the backend, sets self._debuggee_id to the registered debuggee ID.

        Returns:
        (registration_required, delay) tuple
        """
        try:
            native.LogInfo("Current pid: %d | Registering Debuggee" % (self._pid))
            request = {"debuggee": self._GetDebuggee()}

            try:
                try:
                    native.LogInfo("Current pid: %d | Sending register debugee request to Lightrun Server" % (self._pid))
                    code, response = self._lightrun_connection_manager.SendHttpRequest("POST", "/register", request)
                except connection_manager.HTTPException as e:
                    if e.response_code == connection_manager.HTTPResponseCodes.HTTP_UPGRADE_REQUIRED:
                        register_response = json.loads(e.error_response)
                        native.LogWarning(register_response.get("message"))
                        self._SetDebuggeeId(register_response)
                        return True, self.register_backoff.Failed()
                    native.LogError("Current pid: %d | Failed to send request Lightrun Server | Exception: %s" % (self._pid, e))
                    raise e

                register_response = json.loads(response)
                self._set_connection_timeout_from(register_response)
                self._SetDebuggeeId(register_response)
                is_disabled = self._get_is_disabled(register_response)
                if is_disabled:
                    self._detach()
                    backoff_interval = self.register_backoff.Failed()
                    native.LogInfo("Current pid: %d | Debuggee is disabled, id: %s" % (self._pid, self._debuggee_id))
                else:
                    # Proceed immediately to list active breakpoints.
                    backoff_interval = 0
                    native.LogInfo("Current pid: %d | Debuggee registered successfully, id: %s" % (self._pid, self._debuggee_id))
                    self.register_backoff.Succeeded()

                return is_disabled, backoff_interval
            except BaseException as e:
                native.LogError("Current pid: %d | Failed to register debuggee: request: %s, exception: %s" % (self._pid, request, e))
        except BaseException as e:
            native.LogWarning("Current pid: %d | Debuggee information not available. Exception: %s" % (self._pid, e))

        return True, self.register_backoff.Failed()

    def _fetch_active_breakpoints(self):
        """
        Single attempt to query the list of active breakpoints.
        Must not be called before the debuggee has been registered.
        If the request fails, the delay before the next request will be increased.

        :return: (response, delay) tuple
        response - a response with the list of active breakpoints or None in a case of an error
        delay - a backoff delay before the next request
        """
        try:
            endpoint_path = self._GetDebuggeeEndpointPath("/breakpoints?successOnTimeout=true")
            response_status, response = self._lightrun_connection_manager.SendHttpRequest("GET", endpoint_path)
        except HTTPException as http_exception:
            if http_exception.response_code == 404:
                native.LogWarning("Agent is not registered, returning registration required")
                return None, self.list_backoff.Failed(), True
            else:
                return None, self.list_backoff.Failed(), False
        except BaseException:
            native.LogInfo("Failed to query active breakpoints: " + traceback.format_exc())
            return None, self.list_backoff.Failed(), False
        self.list_backoff.Succeeded()
        return response, 0, False

    def _update_active_breakpoints(self, response, expired_ids):
        """
        Updates the list of agent's breakpoints using data from the server's response.
        The breakpoints marked as expired by the agent after the response was got will be ignored.

        :param response: Server's response with the list of active breakpoints
        :param expired_ids: List of expired breakpoints' ids to exclude from the server's response
        """
        response = json.loads(response)

        self._SetLogLevel(response.get("agentLogLevel"))

        if not response.get("waitExpired"):
            # Update breakpoints
            breakpoints = response.get("breakpoints") or []
            breakpoints = [b for b in breakpoints if b.get("id") not in expired_ids]
            if self._breakpoints != breakpoints:
                self._breakpoints = breakpoints
                native.LogInfo("Breakpoints list changed, activating breakpoint")
                self.on_active_breakpoints_changed(copy.deepcopy(self._breakpoints))
                native.LogInfo("Breakpoint activation successful, %d active breakpoints" % len(self._breakpoints))

            # Update global piping status
            if response.get("pipeLogs"):
                piping_status = piping_manager.getStatus(response.get("pipeLogs"))
                self._piping_manager.SetGlobalPiping(piping_status)

            # TODO(yaniv): When implementing TicToc & counter, handle global piping settings here

            if response.get("collectAndSendLog") and response.get("collectLogRequestId") != self._collect_log_request_id:
                self._collect_log_request_id = response.get("collectLogRequestId")
                self._collect_log_event.set()

    def _TransmitBreakpointUpdates(self):
        """
        Tries to send pending breakpoint updates to the backend.

        Sends all the pending breakpoint updates. In case of transient failures,
        the breakpoint is inserted back to the top of the queue. Application
        failures are not retried (for example updating breakpoint in a final
        state).

        Each pending breakpoint maintains a retry counter. After repeated transient
        failures the breakpoint is discarded and dropped from the queue.

        Returns:
          (reconnect, timeout) tuple. The first element ("reconnect") is set to
          true on unexpected HTTP responses. The caller should discard the HTTP
          connection and create a new one. The second element ("timeout") is
          set to None if all pending breakpoints were sent successfully. Otherwise
          returns time interval in seconds to stall before retrying.
        """
        reconnect = False
        retry_list = []

        # There is only one consumer, so two step pop is safe.
        while self._transmission_queue:
            breakpoints = self._GetBreakpointBulk()
            breakpoint_ids = [bp["id"] for (bp, retry_count) in breakpoints]

            try:
                self._lightrun_connection_manager.SendHttpRequest(
                    "PUT", self._GetDebuggeeEndpointPath("/breakpoints"), [bp for (bp, retry_count) in breakpoints]
                )
                native.LogInfo("Update for breakpoints %s transmitted successfully" % breakpoint_ids)
            except connection_manager.HTTPException as err:
                # Treat 400 error codes (except timeout) as application error that will
                # not be retried. All other errors are assumed to be transient.
                status = err.response_code
                is_transient = (status >= 500) or (status == 408)
                if is_transient:
                    native.LogInfo("Failed to send breakpoints update for breakpoints: %s\nError: %s" % (breakpoint_ids, err))
                    for bp, retry_count in breakpoints:
                        if retry_count < self.max_transmit_attempts - 1:
                            retry_list.append((bp, retry_count + 1))
                        else:
                            native.LogWarning("Breakpoint %s retry count exceeded maximum" % bp["id"])
                else:
                    # There is no point in retrying the transmission (It will fail)
                    native.LogInfo("Failed to transmit breakpoint update, dismissing breakpoints %s.\n Error: %s" % (breakpoint_ids, err))
            except socket.error as err:
                native.LogWarning("Socket error %d while sending breakpoints %s update\n%s" % (err.errno, breakpoint_ids, traceback.format_exc()))
                for bp, retry_count in breakpoints:
                    if retry_count < self.max_transmit_attempts - 1:
                        retry_list.append((bp, retry_count + 1))
                    else:
                        native.LogWarning("Breakpoint %s retry count exceeded maximum" % bp["id"])
                        reconnect = True  # Socket errors shouldn't persist like this; reconnect.
            except BaseException:
                native.LogWarning("Fatal error sending breakpoints %s update: %s" % (breakpoint_ids, traceback.format_exc()))
                reconnect = True

        self._transmission_queue.extend(retry_list)

        if not self._transmission_queue:
            self.update_backoff.Succeeded()
            # Nothing to send, wait until next breakpoint update.
            return reconnect, None
        else:
            return reconnect, self.update_backoff.Failed()

    def _SendPendingLogs(self):
        """
        Sends pending piped logs to the backend.
        In case of failure, the logs are re-inserted into the local storage to be sent later.
        """
        logs_dict = self._piping_manager.GetLogs()
        if len(logs_dict) > 0:
            try:
                logs = list(itertools.chain(*logs_dict.values()))
                self._lightrun_connection_manager.SendHttpRequest("POST", self._GetDebuggeeEndpointPath("/log"), logs)
            except (connection_manager.HTTPException, IOError):
                self._piping_manager.AddLogs(logs_dict)

    def _SendPendingAppOnlyLogHits(self):
        breakpoint_ids = self._piping_manager.GetAppOnlyFirstBreakpointHits()
        if len(breakpoint_ids) > 0:
            try:
                self._lightrun_connection_manager.SendHttpRequest("POST", self._GetDebuggeeEndpointPath("/appOnlyActionHits"), breakpoint_ids)
            except (connection_manager.HTTPException, IOError):
                # if exception occurs, fill back the set of pending app-only logs to retry sending them later
                self._piping_manager.AddAppOnlyFirstBreakpointHits(breakpoint_ids)

    def _DeregisterDebuggee(self):
        """
        Ask the server to detach the agent before Shutdown
        """
        try:
            if self._lightrun_connection_manager is not None and self._debuggee_id is not None:
                self._lightrun_connection_manager.SendHttpRequest("POST", self._GetDebuggeeEndpointPath("/deregister"))
        except (connection_manager.HTTPException, IOError):
            native.LogInfo("Failed to deregister the agent")

    def _FetchAndSetDataVisibilityAndRedaction(self):
        """
        Fetches the data visibility policy and data redaction patterns from the server,
        and configures the data visibility manager accordingly.
        """
        blacklist_endpoint_path = self._GetDebuggeeEndpointPath("/blacklist?successOnTimeout=true")
        code, response = self._lightrun_connection_manager.SendHttpRequest("GET", blacklist_endpoint_path)
        if code != 200:
            return False
        if len(response) > 0:
            native.LogInfo("Setting data visibility policy: %s" % response)
            self._data_visibility_manager.SetDataVisibilityPolicy(response)

        if lightrun_config.GetBooleanConfigValue("enable_pii_redaction"):
            redaction_endpoint_path = self._GetDebuggeeEndpointPath("/redaction?successOnTimeout=true")
            code, response = self._lightrun_connection_manager.SendHttpRequest("GET", redaction_endpoint_path)
            if len(response) > 0:
                native.LogInfo("Setting data redaction patterns: %s" % response)
                self._data_visibility_manager.SetDataRedactionPatterns(response)

        return True

    def _GetDebuggee(self):
        """Builds the debuggee structure."""
        debuggee = {
            "id": self._debuggee_id,
            "labels": {"metadataV2": base64.b64encode(bytes(json.dumps(self._metadata), "utf-8")).decode("utf-8")},
            "agentVersion": version_retriever.get_version_full(),
        }
        debuggee.update(self._environment_metadata.get_props())

        source_context = HubClient._ReadAppJsonFile("source-context.json")
        if source_context:
            debuggee["sourceContexts"] = [source_context]

        return debuggee

    def _GetDebuggeeEndpointPath(self, partial_endpoint_path):
        return "/" + self._debuggee_id + partial_endpoint_path

    def _get_is_disabled(self, register_response):
        is_disabled = (register_response.get("debuggee") or {}).get("isDisabled")
        return bool(is_disabled)

    def _set_connection_timeout_from(self, register_response):
        if "clientConnectionTimeoutInSeconds" not in register_response:
            native.LogWarning(
                "Current pid: {} | Server didn't return a value for the connection timeout. Using existing timeout of {} seconds".format(
                    self._pid, self._lightrun_connection_manager.connection_timeout / 1000
                )
            )
            return
        timeout = register_response.get("clientConnectionTimeoutInSeconds")
        try:
            self._lightrun_connection_manager.connection_timeout = timeout * 1000
        except ValueError:
            native.LogWarning(
                "Current pid: {} | Server returned an invalid value for the connection timeout: {}. Using existing timeout of {} seconds".format(
                    self._pid, timeout, self._lightrun_connection_manager.connection_timeout / 1000
                )
            )
        native.LogInfo("Current pid: {} | Connection timeout was successfully updated from the server to {} seconds".format(self._pid, timeout))

    def _SetDebuggeeId(self, register_response):
        """
        Parses the backend response and sets the local debuggee id.

        Args:
          server_response: A string response received from the backend register API.
        """
        self._debuggee_id = register_response.get("debuggee", {}).get("id")

    def _GetBreakpointBulk(self):
        """
        Collects breakpoints out of the transmission queue into a bulk that is going to be sent to the backend.
        Returns:
          A list of (breakpoint, retry_count) tuples, with a maximal bulk-size length.
        """
        breakpoints = []
        network_size_aggregated = 0
        limit = lightrun_config.GetTransmissionBulkMaxNetworkSizeInBytes()
        while self._transmission_queue and len(breakpoints) < self._bulk_max_size:
            breakpoint_and_retries = self._transmission_queue[0]
            breakpoint_ = breakpoint_and_retries[0]
            breakpoint_size = HubClient.get_json_size(breakpoint_)
            if breakpoint_size is None:
                self._transmission_queue.popleft()
                continue
            if network_size_aggregated + breakpoint_size <= limit:
                breakpoints.append(breakpoint_and_retries)
                network_size_aggregated += breakpoint_size
                self._transmission_queue.popleft()
            elif breakpoint_size > limit and len(breakpoints) == 0:
                native.LogInfo(f"breakpoint {breakpoint_.get('id')} size : {breakpoint_size} > max network size : {limit}, sending only one")
                breakpoints.append(breakpoint_and_retries)
                self._transmission_queue.popleft()
                break
            else:
                break

        return breakpoints

    @staticmethod
    def _ReadAppJsonFile(relative_path):
        """
        Reads JSON file from an application directory.

        Args:
          relative_path: file name relative to application root directory.

        Returns:
          Parsed JSON data or None if the file does not exist, can't be read or
          not a valid JSON file.
        """
        try:
            with open(os.path.join(sys.path[0], relative_path), "r") as f:
                return json.load(f)
        except (IOError, ValueError):
            return None

    def _SetLogLevel(self, agent_log_level):
        # the Python agent has no debug logs ¯\_(ツ)_/¯
        pass

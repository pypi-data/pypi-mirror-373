"""Captures application state on a breakpoint hit."""

import datetime
import inspect
import json
import logging
import logging.handlers
import os
import re
import sys
import time
import types

from . import lightrun_config, log_colored_format, messages, piping_manager, utils
from .data_visibility_manager import REDACTED
from .lightrun_native import native

# Externally defined functions to actually log a message. If these variables
# are not initialized, the log action for breakpoints is invalid.
log_info_message = None
log_warning_message = None
log_error_message = None
log_debug_message = None
lightrun_logger = None

_PRIMITIVE_TYPES = (type(None), float, complex, bool, slice, bytearray, bytes, int, str)
_DATE_TYPES = (datetime.date, datetime.time, datetime.timedelta)
_VECTOR_TYPES = (tuple, list, set)


class LogCollector(object):
    """
    Captures minimal application snapshot and logs it to application log.

    This is similar to CaptureCollector, but we don't need to capture local
    variables, arguments and the objects tree. All we need to do is to format a
    log message. We still need to evaluate watched expressions.

    The actual log functions are defined globally outside of this module.
    """

    def __init__(self, definition, piping_manager, data_visibility_manager, ignore_quota):
        """Class constructor.

        Args:
          definition: breakpoint definition indicating log level, message, etc.
          piping_manager: A dependency for the log piping manager.
          data_visibility_manager: Object to manage data visibility policy of captured data of the breakpoint.
          ignore_quota: A boolean flag that represents whether or not the breakpoint should ignore all quotas.
        """
        self._definition = definition
        self._piping_manager = piping_manager
        self._data_visibility_manager = data_visibility_manager
        self._ignore_quota = ignore_quota

        # Maximum number of character to allow for a single value. Longer strings
        # are truncated.
        self.max_value_len = 256

        # Maximum recursion depth.
        self.max_depth = 2

        # Maximum number of items in a list to capture at the top level.
        self.max_list_items = 10

        # When capturing recursively, limit on the size of sublists.
        self.max_sublist_items = 5

        # Time to pause after dynamic log quota has run out.
        self.quota_recovery_ms = 500

        # The time when we first entered the quota period
        self._quota_recovery_start_time = None

        # Select log function.
        level = self._definition.get("logLevel")
        if not level or level == "INFO":
            self._log_message = log_info_message
        elif level == "WARN":
            self._log_message = log_warning_message
        elif level == "ERROR":
            self._log_message = log_error_message
        elif level == "DEBUG":
            self._log_message = log_debug_message
        else:
            self._log_message = None

    def Log(self, frame):
        """
        Captures the minimal application states, formats it and logs the message.

        Args:
          frame: Python stack frame of breakpoint hit.

        Returns:
          None on success or status message on error.
        """
        # Return error if log methods were not configured globally.
        if not self._log_message:
            return {"isError": True, "description": messages.toJson(messages.LOG_ACTION_NOT_SUPPORTED)}

        if self._quota_recovery_start_time:
            ms_elapsed = (time.time() - self._quota_recovery_start_time) * 1000
            if ms_elapsed > self.quota_recovery_ms:
                # We are out of the recovery period, clear the time and continue
                self._quota_recovery_start_time = None
            else:
                # We are in the recovery period, exit
                return

        # Evaluate watched expressions
        watch_results = self._EvaluateExpressions(frame)
        log_message_format = self._definition.get("logMessageFormat", "")
        log_message = LogCollector._FormatMessage(log_message_format, watch_results)

        # Redact sensitive data in the message and concat it to prefix
        log_message = self._data_visibility_manager.ReplaceRedactedData(log_message)

        # Check whether we should log it to stdout
        action_piping = self._piping_manager.GetActionPiping(self._definition.get("id"))
        log_to_stdout = action_piping in [piping_manager.PipingStatus.APP_ONLY, piping_manager.PipingStatus.BOTH]

        if self._ignore_quota or native.ApplyDynamicLogsQuota(len(log_message)):
            log_line = "LOGPOINT: " + log_message
            if self._data_visibility_manager.redactionIsActive:
                # if redaction's been done on the agent side, send final log message to the server
                log_data = log_line
                watch_results_data = []
            else:
                # ..otherwise send message format + watch results
                log_data = "LOGPOINT: " + log_message_format
                watch_results_data = watch_results
        else:
            self._quota_recovery_start_time = time.time()
            log_line = messages.DYNAMIC_LOG_OUT_OF_QUOTA
            log_data = log_line
            watch_results_data = []

        if log_to_stdout:
            self._log_message(log_line)
        self._piping_manager.AddLog(self._definition.get("id"), log_data, self._definition.get("logLevel"), watch_results_data)

        return None

    def _EvaluateExpressions(self, frame):
        """Evaluates watched expressions into a string form.

        If expression evaluation fails, the error message is used as evaluated
        expression string.

        Args:
          frame: Python stack frame of breakpoint hit.

        Returns:
          Array of strings where each string corresponds to the breakpoint
          expression with the same index.
        """
        return [self._FormatExpression(frame, expression) for expression in self._definition.get("expressions") or []]

    def _FormatExpression(self, frame, expression):
        """Evaluates a single watched expression and formats it into a string form.

        If expression evaluation fails, returns error message string.

        Args:
          frame: Python stack frame in which the expression is evaluated.
          expression: string expression to evaluate.

        Returns:
          Formatted expression value that can be used in the log message.
        """
        rc, value = utils.EvaluateExpression(frame, expression)
        if not rc:
            message = LogCollector._FormatMessage(value["description"]["format"], value["description"].get("parameters"))
            return '"<' + message + '>"'

        if not self._data_visibility_manager.IsDataVisible(utils.DetermineType(value))[0]:
            return '"<' + messages.ERROR_BLACKLISTED_EXPRESSION + '>"'

        return self._FormatValue(value)

    def _FormatValue(self, value, level=0):
        """Pretty-prints an object for a logger.

        This function is very similar to the standard pprint. The main difference
        is that it enforces limits to make sure we never produce an extremely long
        string or take too much time.

        Args:
          value: Python object to print.
          level: current recursion level.

        Returns:
          Formatted string.
        """

        def FormatDictItem(key_value):
            """Formats single dictionary item."""
            key, value = key_value
            if self._data_visibility_manager.ShouldRedactByName(key):
                return self._FormatValue(key, level + 1) + ": " + REDACTED
            else:
                return self._FormatValue(key, level + 1) + ": " + self._FormatValue(value, level + 1)

        def LimitedEnumerate(items, formatter, level=0):
            """Returns items in the specified enumerable enforcing threshold."""
            count = 0
            limit = self.max_sublist_items if level > 0 else self.max_list_items
            for item in items:
                if count == limit:
                    yield "..."
                    break

                yield formatter(item)
                count += 1

        def FormatList(items, formatter, level=0):
            """Formats a list using a custom item formatter enforcing threshold."""
            return ", ".join(LimitedEnumerate(items, formatter, level=level))

        if isinstance(value, _PRIMITIVE_TYPES):
            # Primitive type, always immutable.
            return utils.TrimString(json.dumps(value, ensure_ascii=False), self.max_value_len)

        if isinstance(value, _DATE_TYPES):
            return str(value)

        if level > self.max_depth:
            return str(type(value))

        if isinstance(value, dict):
            return "{" + FormatList(value.items(), FormatDictItem) + "}"

        if isinstance(value, _VECTOR_TYPES):
            return _ListTypeFormatString(value).format(FormatList(value, lambda item: self._FormatValue(item, level + 1), level=level))

        if isinstance(value, types.FunctionType):
            return "function " + value.__name__

        if hasattr(value, "__dict__") and value.__dict__:
            return self._FormatValue(value.__dict__, level)

        return str(type(value))

    @staticmethod
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
                return parameters[int(m.group(0)[1:])].strip('"')  # remove quotes from top-level string watch results
            except IndexError:
                return messages.INVALID_EXPRESSION_INDEX

        parts = template.split("$$")
        return "$".join(re.sub(r"\$\d+", GetParameter, part) for part in parts)


def _ListTypeFormatString(value):
    """Returns the appropriate format string for formatting a list object."""

    if isinstance(value, tuple):
        return "({0})"
    if isinstance(value, set):
        return "{{{0}}}"
    return "[{0}]"


class LineNoFilter(logging.Filter):
    """Enables overriding the path and line number in a logging record.

    The "extra" parameter in logging cannot override existing fields in log
    record, so we can't use it to directly set pathname and lineno. Instead,
    we add this filter to the default logger, and it looks for "cdbg_pathname"
    and "cdbg_lineno", moving them to the pathname and lineno fields accordingly.
    """

    def filter(self, record):
        # This method gets invoked for user-generated logging, so verify that this
        # particular invocation came from our logging code.
        if record.pathname != inspect.currentframe().f_code.co_filename:
            return True
        pathname, lineno, func_name = GetLoggingLocation()
        if pathname:
            record.pathname = pathname
            record.filename = os.path.basename(pathname)
            record.lineno = lineno
            record.funcName = func_name
        return True


def GetLoggingLocation():
    """Search for and return the file and line number from the log collector.

    Returns:
      (pathname, lineno, func_name) The full path, line number, and function name
      for the logpoint location.
    """
    frame = inspect.currentframe()
    this_file = frame.f_code.co_filename
    frame = frame.f_back
    while frame:
        if this_file == frame.f_code.co_filename:
            if "cdbg_logging_location" in frame.f_locals:
                ret = frame.f_locals["cdbg_logging_location"]
                if len(ret) != 3:
                    return (None, None, None)
                return ret
        frame = frame.f_back
    return (None, None, None)


def InitLogger():
    """Sets and configures the logger object to use for all logpoint actions."""
    global log_info_message
    global log_warning_message
    global log_error_message
    global log_debug_message
    global lightrun_logger

    # Initialize and configure the logger object (and underlying handlers & formatters)
    # that will be used in future logpoint actions
    logger = logging.Logger("lightrun")

    # We want to be able to register to this logger later.
    lightrun_logger = logger

    # Define the console handler
    console_handler = logging.StreamHandler(sys.stdout)
    # console_output_format = lightrun_config.config.get('dynamic_log_console_handler_format')
    console_handler.setFormatter(log_colored_format.ColoredDynamicConsoleFormatter())
    logger.addHandler(console_handler)

    # Define the file handler
    if lightrun_config.config.get("dynamic_log_file_handler_file_pattern"):
        file_handler = logging.handlers.RotatingFileHandler(
            lightrun_config.config["dynamic_log_file_handler_file_pattern"],
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=20,
        )
        file_output_format = lightrun_config.config.get("dynamic_log_file_handler_format")
        file_handler.setFormatter(logging.Formatter(file_output_format))
        logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)

    # Set the global
    log_info_message = logger.info
    log_warning_message = logger.warning
    log_error_message = logger.error
    log_debug_message = logger.debug
    logger.addFilter(LineNoFilter())

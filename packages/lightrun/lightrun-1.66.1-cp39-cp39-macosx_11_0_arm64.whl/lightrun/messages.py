from collections import namedtuple

Messages = namedtuple("Messages", ["id", "value"])

#
# Breakpoint module messages
#
# Use the following schema to define breakpoint error message constant:
# ERROR_<Single word from Status.Reference>_<short error name>_<num params>
ERROR_LOCATION_FILE_EXTENSION_0 = Messages(1, "Only files with .py extension are supported")
ERROR_LOCATION_MODULE_NOT_FOUND_0 = Messages(2, "Python module couldn't be found.")
ERROR_LOCATION_MULTIPLE_MODULES_MAX_ARG_NUM = 9
ERROR_LOCATION_MULTIPLE_MODULES = Messages(
    3, "More than one possible match was found for the requested filename $0{}. Provide an absolute or distinguished path"
)
ERROR_LOCATION_NO_CODE_FOUND_AT_LINE_2 = Messages(4, "No executable code was found at $0 in $1")
ERROR_LOCATION_NO_CODE_FOUND_AT_LINE_3 = Messages(5, "No executable code was found at $0 in $1. Try line $2.")
ERROR_LOCATION_NO_CODE_FOUND_AT_LINE_4 = Messages(6, "No executable code was found at $0 in $1. Try lines $2 or $3.")
ERROR_CONDITION_BREAKPOINT_QUOTA_EXCEEDED_0 = Messages(7, "Couldn't evaluate the given condition as it might affect app performance.")
ERROR_CONDITION_MUTABLE_0 = Messages(8, "Only immutable expressions can be used in conditions")
ERROR_CONDITION_INVALID_0 = Messages(9, "The condition evaluation failed")
ERROR_UNKNOWN_ACTION_TYPE = Messages(10, "Action type not supported")
ERROR_BLACKLISTED_FILE = Messages(11, "The file is blacklisted by config")
ERROR_BLACKLISTED_EXPRESSION = "The expression is blacklisted by config"
ERROR_UNSPECIFIED_INTERNAL_ERROR = Messages(12, "Internal error occurred")
ERROR_EXPRESSION_IS_BIGGER_THAN_MAX_OBJECT_SIZE = Messages(53, "Object length is limited to the first $0 characters. Add as a watch expression to view more.")
ERROR_EXPRESSION_IS_BIGGER_THAN_MAX_WATCH_EXPRESSION_SIZE = Messages(
    54, "Expression length is limited to the first $0 characters. To increase this limit, adjust the agent settings — see the documentation."
)
ERROR_INVALID_EXPRESSION = Messages(13, "Invalid expression")
ERROR_EXPRESSION_COMPILATION_ERROR = Messages(14, "Expression could not be compiled: $0")

#
# Collector module messages
#
EMPTY_DICTIONARY = "Empty dictionary"
EMPTY_COLLECTION = "Empty collection"
OBJECT_HAS_NO_FIELDS = "Object has no fields"
LOG_ACTION_NOT_SUPPORTED = Messages(15, "Log action on a breakpoint not supported")
INVALID_EXPRESSION_INDEX = "<N/A>"
DYNAMIC_LOG_OUT_OF_QUOTA = "LOGPOINT: This action is temporarily paused due to high log rate until log quota is restored"


def multiple_modules_found_error(path, candidates):
    """
    Generates an error message to be used when multiple matches are found.

    Args:
      path: The breakpoint location path that the user provided.
      candidates: List of paths that match the user provided path. Must
          contain at least 2 entries (throws AssertionError otherwise).

    Returns:
      A (format, parameters) tuple that should be used in the description
      field of the breakpoint error status.
    """
    if len(candidates) <= 1:
        raise AssertionError("Require candidates")
    params = [path] + candidates[: ERROR_LOCATION_MULTIPLE_MODULES_MAX_ARG_NUM - 1]
    fmt = " ("
    fmt += ", ".join("${}".format(n) for n in range(1, len(params)))
    if len(candidates) > ERROR_LOCATION_MULTIPLE_MODULES_MAX_ARG_NUM - 1:
        fmt += " and ${} more".format(ERROR_LOCATION_MULTIPLE_MODULES_MAX_ARG_NUM)
        params.append(str(len(candidates) - ERROR_LOCATION_MULTIPLE_MODULES_MAX_ARG_NUM + 1))
    fmt += ")"
    return ERROR_LOCATION_MULTIPLE_MODULES.id, ERROR_LOCATION_MULTIPLE_MODULES.value.format(fmt), params


def toJson(err, params=None):
    result = {"format": err.value, "errorId": err.id}
    if params:
        result["parameters"] = [str(p) for p in params]
    return result

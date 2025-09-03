import os
import sys

from urllib.parse import urlparse

from .lightrun_native import native


def is_windows():
    # all windows versions can be identified like this
    return sys.platform == "win32"


def GetBaseURL(url):
    """
    Extract the base url out of the full url path.
    For example - "https://localhost:8080/company/defaultCompany" -> "https://localhost:8080/"

    :param url: A string containing a valid url.
    :return: Returns the base url, If the given url is full and valid. Else, None is returned.
    """
    parsed_url = urlparse(url.replace("\\", ""))
    if len(parsed_url.scheme) > 0 and len(parsed_url.netloc) > 0:
        return parsed_url.scheme + "://" + parsed_url.netloc + "/"
    else:
        return None


def EvaluateExpression(frame, expression):
    """
    Compiles and evaluates watched expression.

    :param frame: evaluation context.
    :param expression: watched expression to compile and evaluate.

    :return: (False, status) on error or (True, value) on success.
    """
    try:
        code = compile(expression, "<watched_expression>", "eval")
    except (TypeError, ValueError) as e:
        # expression string contains null bytes.
        return (False, {"isError": True, "refersTo": "VARIABLE_NAME", "description": {"format": "Invalid expression", "parameters": [str(e)]}})
    except SyntaxError as e:
        return (False, {"isError": True, "refersTo": "VARIABLE_NAME", "description": {"format": "Expression could not be compiled: $0", "parameters": [e.msg]}})

    try:
        return (True, native.CallImmutable(frame, code))
    except BaseException as e:  # pylint: disable=broad-except
        return (False, {"isError": True, "refersTo": "VARIABLE_VALUE", "description": {"format": "Exception occurred: $0", "parameters": [str(e)]}})


def TrimString(s, max_len):
    """
    Trims the string s if it exceeds max_len.
    """
    if len(s) <= max_len:
        return s
    return s[: max_len + 1] + "..."


def DetermineType(value):
    """Determines the type of val, returning a "full path" string.

    For example:
      DetermineType(5) -> __builtin__.int
      DetermineType(Foo()) -> com.bar.Foo

    Args:
      value: Any value, the value is irrelevant as only the type metadata
      is checked

    Returns:
      Type path string.  None if type cannot be determined.
    """

    object_type = type(value)
    if not hasattr(object_type, "__name__"):
        return None

    type_string = getattr(object_type, "__module__", "")
    if type_string:
        type_string += "."

    type_string += object_type.__name__
    return type_string


def NormalizePath(path):
    """Removes any Python system path prefix from the given path.

    Python keeps almost all paths absolute. This is not what we actually
    want to return. This loops through system paths (directories in which
    Python will load modules). If "path" is relative to one of them, the
    directory prefix is removed.

    Args:
      path: absolute path to normalize (relative paths will not be altered)

    Returns:
      Relative path if "path" is within one of the sys.path directories or
      the input otherwise.
    """
    path = os.path.normpath(path)

    for sys_path in sys.path:
        if sys_path in ["", ".", ".."]:
            sys_path = os.path.abspath(sys_path)  # noqa: PLW2901

        if not sys_path:
            continue

        # Append '/' at the end of the path if it's not there already.
        sys_path = os.path.join(sys_path, "")  # noqa: PLW2901

        if path.startswith(sys_path):
            return path[len(sys_path) :]

    return path

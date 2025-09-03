import fnmatch
import json
import os
import sys

import yaml

from .lightrun_native import native

# Possible visibility responses
RESPONSES = {
    "UNKNOWN_TYPE": "Could not determine type",
    "BLACKLISTED": "Blacklisted by config",
    "VISIBLE": "Visible",
}

REDACTED = "REDACTED"


class DataVisibilityManager(object):
    # true if redaction is enabled in agent.config and agent is able to perform a redaction
    redactionIsActive = False

    """
    Manager class for the data visibility. This class handles both the data visibility policy (AKA blacklisting)
    and data redaction policies.
    This class is injected as a dependency to the other manager classes.
    """

    def __init__(self):
        try:
            native.LogInfo("Trying to import re2 to enable pii redaction")
            global re2
            import re2

            native.LogInfo("Successfully imported re2 lib, it is possible to use pii redaction")
        except ImportError:
            native.LogWarning(f"Can't import re2 lib, pii is not supported. Current version {sys.version}")

        self._data_visibility_parse_error = None
        self._blacklist_patterns = GlobPatternList([])
        self._blacklist_exception_patterns = GlobPatternList([])
        self._data_redaction_patterns_by_value = []
        self._data_redaction_patterns_by_name = []

    def SetDataVisibilityPolicy(self, data_visibility_policy_str):
        """
        Parses and sets the visibility policy, which is used to determine the visibility of captured variables
        and files. If the data visibility policy fails to parse, an error is set and returned to the user each time
        the policy is checked.

        Args:
          data_visibility_policy_str: A yaml string containing the policy that was fetched from the backend.
        """
        try:
            # TODO(yaniv): Convert the blacklist format to be a json and not a legacy yaml
            # TODO(yaniv): (Do this in all agents and backend).
            policy_dict = yaml.safe_load(data_visibility_policy_str)
            if policy_dict is not None:
                self._blacklist_patterns = GlobPatternList(policy_dict.get("blacklist", []))
                self._blacklist_exception_patterns = GlobPatternList(policy_dict.get("blacklist_exception", []))
        except IOError as err:
            self._data_visibility_parse_error = "Could not process blacklist config: %s" % err
            native.LogWarning(self._data_visibility_parse_error)

    def SetDataRedactionPatterns(self, data_redaction_patterns_str):
        """
        Parses and sets the redaction policy, which is used to redact sensitive patterns from dynamic logs.
        If the data visibility policy fails to parse, an error is set and returned to the user each time
        the policy is checked.

        Args:
          data_redaction_patterns_str: A json string containing a list of {'name': '', 'pattern': ''} dicts,
            each representing a redaction pattern.
        """
        try:
            DataVisibilityManager.redactionIsActive = True
            redaction_patterns = json.loads(data_redaction_patterns_str)
            if redaction_patterns is not None:
                self._data_redaction_patterns_by_value = []
                self._data_redaction_patterns_by_name = []
                for pattern in redaction_patterns:
                    # example of pattern dto
                    # {'name': 'a', 'pattern': 'a', 'type': 'BY_NAME', 'caseInsensitive': False}
                    if not pattern.get("name") or not pattern.get("pattern"):
                        DataVisibilityManager.redactionIsActive = False
                        native.LogWarning("Invalid redaction pattern structure: %s" % pattern)
                        continue

                    try:
                        complete_pattern = "(?i)%s" % pattern.get("pattern") if pattern.get("caseInsensitive") else pattern.get("pattern")
                        compiled_pattern = re2.compile(complete_pattern)
                        if (pattern.get("type")) == "BY_VALUE":
                            self._data_redaction_patterns_by_value.append(compiled_pattern)
                        elif (pattern.get("type")) == "BY_NAME":
                            self._data_redaction_patterns_by_name.append(compiled_pattern)
                    except re2.error:
                        DataVisibilityManager.redactionIsActive = False
                        native.LogWarning("Failure to compile redaction pattern %s" % pattern)
                        continue
        except RuntimeError as err:
            DataVisibilityManager.redactionIsActive = False
            self._data_visibility_parse_error = "Could not process redaction config: %s" % err
            self._data_redaction_patterns_by_value = []
            self._data_redaction_patterns_by_name = []
            native.LogWarning(self._data_visibility_parse_error)

    def IsDataVisible(self, path):
        """
        Returns a tuple (visible, reason) stating if the data should be visible.

        Args:
          path: A dot separated path that represents a package, class, method or
          variable.  The format is identical to pythons "import" statement.

        Returns:
          (visible, reason) where visible is a boolean that is True if the data
          should be visible.  Reason is a string reason that can be displayed
          to the user and indicates why data is visible or not visible.
        """
        if self._data_visibility_parse_error:
            return False, self._data_visibility_parse_error

        if self._blacklist_patterns.IsEmpty():
            return True, RESPONSES["VISIBLE"]

        if path is None:
            return False, RESPONSES["UNKNOWN_TYPE"]

        if self._blacklist_patterns.Matches(path):
            if not self._blacklist_exception_patterns.Matches(path):
                return False, RESPONSES["BLACKLISTED"]

        return True, RESPONSES["VISIBLE"]

    def IsFileVisible(self, path):
        """Returns a tuple (visible, reason) stating if the file should be visible.

        Args:
          path: A slash-separated path that represents a file path.
        """
        if self._data_visibility_parse_error:
            return False, self._data_visibility_parse_error

        if self._blacklist_patterns.IsEmpty():
            return True, RESPONSES["VISIBLE"]

        # Match the path to the format expected by the IsDataVisible method
        path = os.path.splitext(path)[0]
        path = path.replace(os.sep, ".")

        return self.IsDataVisible(path)

    def ReplaceRedactedData(self, data):
        """
        Replaces defined BY_VALUE patterns in the data with a placeholder string.
        """
        new_data = data
        for pattern in self._data_redaction_patterns_by_value:
            new_data = re2.sub(pattern, REDACTED, new_data)
        return new_data

    def ShouldRedactByName(self, fieldName):
        """
        Finds any match in the given data using BY_NAME patterns
        """
        for pattern in self._data_redaction_patterns_by_name:
            match = re2.search(pattern, fieldName)
            if match:
                return True


class GlobPatternList(object):
    """
    Represents a list of pattern in glob format (i.e. - not regex).
    Each pattern might start with a '!', which indicates it's a reverse match pattern.
    """

    def __init__(self, patterns):
        self._patterns = [p for p in patterns if not p.startswith("!")]
        self._inverse_patterns = [p[1:] for p in patterns if p.startswith("!")]

    def IsEmpty(self):
        return len(self._patterns) == 0 and len(self._inverse_patterns) == 0

    def Matches(self, path):
        """
        Returns true if path matches any pattern found in the pattern list, or if no inverse patterns (more than 0)
        match the
        Returns false if the path matches any pattern found the inverse pattern list, or if no paths in any of the list
        match.
        The patterns are checked as the prefix or suffix of the path.
        The prefix check is performed to handle cases in which the pattern is a package / directory name.
        For example -
            pattern = 'shop.creditcards'
            path (file) = 'shop.creditcards.info'
        The suffix check is performed to handle cases in which the pattern which is passed isn't the full package path.
        For example -
            pattern = 'Foo'
            path (object) = '__main__.Foo'

        Args:
          path: A dot separated path to a package, class, method, variable or file.

        Returns:
          True if path matches any pattern according to the checks written above.
        """
        # If the path matches any of the non-inverse patterns, return True
        for pattern in self._patterns:
            if fnmatch.fnmatchcase(path, pattern + "*") or fnmatch.fnmatchcase(path, "*" + pattern):
                return True

        # If there are any inverse patterns, and a path matches one of them, return False
        if len(self._inverse_patterns) > 0:
            for pattern in self._inverse_patterns:
                if fnmatch.fnmatchcase(path, pattern + "*") or fnmatch.fnmatchcase(path, "*" + pattern):
                    return False
            # If there are inverse patterns, but the path doesn't match any of them, return True
            return True

        return False

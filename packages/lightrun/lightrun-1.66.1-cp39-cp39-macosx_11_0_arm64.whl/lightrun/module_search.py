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

"""Inclusive search for module files."""

import os
import sys
import tempfile
import zipfile

from . import lightrun_config
from .lightrun_native import native

# The global file index. Built during the module initialization via _BuildIndex method.
file_index = {}


def InitSearch():
    """
    Initialize the search module and build the file index.
    """
    # A list of handles to the inflated .egg/.whl/.zip temporary folders.
    # This list makes sure the temporary directories will remain until the file index is built.
    zipped_files = []
    delimiter = lightrun_config.config.get("lightrun_extra_class_path_delimiter") or ":"

    if lightrun_config.config.get("lightrun_class_path"):
        paths = lightrun_config.config["lightrun_class_path"].split(delimiter)
    else:
        lightrun_extra_class_path = lightrun_config.config.get("lightrun_extra_class_path")
        paths = lightrun_extra_class_path.split(delimiter) if lightrun_extra_class_path else []
        paths += sys.path

    for idx, path in enumerate(paths):
        if not os.path.isabs(path):
            paths[idx] = os.path.abspath(path)

    # Zip files that are part of the path are inflated temporarily to
    # be treated as normal directories in the module search process
    for i in range(len(paths)):
        if zipfile.is_zipfile(paths[i]):
            try:
                tmp_zip_dir = tempfile.TemporaryDirectory(prefix="lrn-temp", suffix=".tmp")
                with zipfile.ZipFile(paths[i]) as archive:
                    archive.extractall(tmp_zip_dir.name)
                zipped_files.append(tmp_zip_dir)  # To keep the temp dir open as long as the debuggee is running
                paths[i] = tmp_zip_dir.name  # Replace the zip in the paths with the new temporary dir
            except Exception as e:
                native.LogWarning("Failed to extract files from zip: %s (Error: %s)" % (paths[i], e))

    # Build the file index dictionary
    _BuildIndex(paths)


def Search(path):
    """
    Search the file index to find a source file that matches a given path.

    The provided input path may have an unknown number of irrelevant outer directories
    (e.g., /garbage1/garbage2/real1/real2/x.py'). This function does multiple search iterations
    until an actual Python module file that matches the input path is found. At each iteration,
    it strips one leading directory from the path and searches the pre-built file index.

    Example:

      File index:
        { 'a/b/a': ['/a/b/a.py'], 'b/a': ['/a/b/a.py'], 'a': ['/a/b/a.py', '/a/c/a.py'],
          'a/c/a': ['/a/c/a.py'], 'c/a': ['/a/c/a.py'] }

      1) Search('a/b/a.py')
           Returns ['/a/b/a.py']
      2) Search('q/w/a/b/a.py')
           Returns ['/a/b/a.py']
      3) Search('q/w/a.py')
           Returns ['/a/b/a.py', '/a/c/a.py']
      4) Search('c.py')
           Returns None

    Args:
      path: Path that describes a source file.
            Must contain .py file extension. Must not contain any leading os.sep character.

    Returns:
      A list of all possible absolute paths to the matched source file, if any matches are found.
      Otherwise, None is returned.

    Raises:
      AssertionError: if the provided path is an absolute path, or if it does not have a .py extension.
    """
    # Verify that the os.sep is already stripped from the input.
    if path.startswith(os.sep):
        raise AssertionError("Path must not start with a '/'")

    # Strip the file extension, it will not be needed.
    path_root, path_ext = os.path.splitext(path)
    if path_ext != ".py":
        raise AssertionError("File path must have .py file extension")

    # Search longer suffixes first. Move to shorter suffixes only if longer suffixes do not result in any matches.
    for partial_path in _GenerateSubPaths(path_root):
        if partial_path in file_index:
            # Can be a single match or multiple possible matches. In case there are multiple matches,
            # there is no point to continue searching the shorter partial paths in the file index, as they
            # will certainly have a number of file matches which is larger or equal to the number of file
            # matches for the current partial path.
            return file_index[partial_path]

    # A matching file was not found in the file index
    return None


def FindShortestPath(original_path, candidate_paths):
    """
    The function returns the shortest path from the list.
    If there are two shortest paths of equal length, the function returns None.

    This is a heuristic that solves the path ambiguity by taking a path with the shortest unmatched part.
    When the requested path is /c/d.py and the options are a/b/c/d.py b/c/d.py,
    the second option is taken to avoid ambiguity error.

    The reason behind this heuristic is that the other options are third-party libraries,
    which usually reside in longer paths.
    """
    if not original_path or not candidate_paths:
        return None
    lengths = [len(v) for v in candidate_paths]
    shortest_val = min(lengths)
    indices = [i for i in range(len(lengths)) if shortest_val == lengths[i]]
    return candidate_paths[indices[0]] if len(indices) == 1 else None


def _BuildIndex(searchable_paths):
    """
    Searches for python files in the searchable directories and indexes them inside the file index dictionary.
    Each python (.py / .pyc / .pyo) file found in a recursive scan of the searchable paths is
    saved in the index multiple times - once for each of it's sub path.

    For example, the file "/a/b/a.py" will be saved multiple times, under the keys -
        'a/b/a', 'b/a', and 'a'.

    This is done to allow the user to specify for longer paths when adding actions, and to give the user
    a full list of all possible paths when there is a name collision.

    For example, if there are two name-colliding files under 'a/b/a.py' and 'a/c/a.py', then the built index would be -
        { 'a/b/a': ['/a/b/a.py'], 'b/a': ['/a/b/a.py'], 'a': ['/a/b/a.py', '/a/c/a.py'],
          'a/c/a': ['/a/c/a.py'], 'c/a': ['/a/c/a.py']}
    """
    for searchable_path in searchable_paths:
        # Walk until a python file is found
        for root, _, files in os.walk(searchable_path):
            for file in files:
                suffix_match = file.endswith(".py") or file.endswith(".pyo")
                if not lightrun_config.ShouldIgnorePyc():
                    suffix_match = suffix_match or file.endswith(".pyc")
                if suffix_match:
                    absolute_file_path = os.path.join(root, file)

                    # Save the full location in the file index for each possible sub path
                    for partial_file_path in _GenerateSubPaths(os.path.splitext(absolute_file_path)[0]):
                        if partial_file_path not in file_index:
                            file_index[partial_file_path] = []
                        if absolute_file_path not in file_index[partial_file_path]:
                            file_index[partial_file_path].append(absolute_file_path)


def _GenerateSubPaths(p):
    """Generates all candidates for the fuzzy search of p."""
    while p:
        yield p
        (_, _, p) = p.partition(os.sep)

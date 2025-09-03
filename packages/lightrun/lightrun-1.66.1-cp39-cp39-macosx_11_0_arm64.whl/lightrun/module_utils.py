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

"""Provides utility functions for module path processing."""

import os
import sys

from . import utils


def IsPathSuffix(mod_path, path):
    """Checks whether path is a full path suffix of mod_path.

    Args:
      mod_path: Must be an absolute path to a source file. Must not have
                file extension.
      path: A relative path. Must not have file extension.

    Returns:
      True if path is a full path suffix of mod_path. False otherwise.
    """

    if utils.is_windows():
        # In case someone runs the app like: python .\app.py instead of python app.py
        mod_path = mod_path.replace(".\\", "")

    return mod_path.endswith(path) and (len(mod_path) == len(path) or mod_path[: -len(path)].endswith(os.sep))


def GetModulePathFromFilePath(path):
    """
    Sanitize the file path of a given module into a path that matches loaded module paths.
    For example:
        1. ./package/module.py -> package/module
        2. /home/python/package/module.py -> /home/python/package/module
    """
    # Remove the file suffix
    module_path = os.path.splitext(path)[0]

    # In case the path is relative and the string starts with a . (i.e - './my_module/file.py'), remove the prefix
    if module_path.startswith("." + os.sep):
        module_path = os.path.relpath(module_path)

    return module_path


def GetLoadedModuleBySuffix(path):
    """Searches sys.modules to find a module with the given file path.

    Args:
      path: Path to the source file. It can be relative or absolute, as suffix
            match can handle both. If absolute, it must have already been
            sanitized.

    Algorithm:
      The given path must be a full suffix of a loaded module to be a valid match.
      File extensions are ignored when performing suffix match.

    Example:
      path: 'a/b/c.py'
      modules: {'a': 'a.py', 'a.b': 'a/b.py', 'a.b.c': 'a/b/c.pyc']
      returns: module('a.b.c')

    Returns:
      The module that corresponds to path, or None if such module was not
      found.
    """
    root = GetModulePathFromFilePath(path)
    for module in sys.modules.values():
        mod_root = os.path.splitext(getattr(module, "__file__", None) or "")[0]

        if not mod_root:
            continue

        # While mod_root can contain symlinks, we cannot eliminate them. This is
        # because, we must perform exactly the same transformations on mod_root and
        # path, yet path can be relative to an unknown directory which prevents
        # identifying and eliminating symbolic links.
        #
        # Therefore, we only convert relative to absolute path.
        if not os.path.isabs(mod_root):
            mod_root = os.path.join(os.getcwd(), mod_root)

        if IsPathSuffix(mod_root, root):
            return module

    return None

# Copyright 2010 New Relic, Inc.
# Copyright 2025 Atatus.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import types
import warnings
from atatus.packages.isort import stdlibs as isort_stdlibs

try:
    from functools import cache as _cache_package_versions
except ImportError:
    from functools import wraps
    from threading import Lock

    _package_version_cache = {}
    _package_version_cache_lock = Lock()

    def _cache_package_versions(wrapped):
        """
        Threadsafe implementation of caching for _get_package_version.

        Python 2.7 does not have the @functools.cache decorator, and
        must be reimplemented with support for clearing the cache.
        """

        @wraps(wrapped)
        def _wrapper(name):
            if name in _package_version_cache:
                return _package_version_cache[name]

            with _package_version_cache_lock:
                if name in _package_version_cache:
                    return _package_version_cache[name]

                version = _package_version_cache[name] = wrapped(name)
                return version

        def cache_clear():
            """Cache clear function to mimic @functools.cache"""
            with _package_version_cache_lock:
                _package_version_cache.clear()

        _wrapper.cache_clear = cache_clear
        return _wrapper


# Need to account for 4 possible variations of version declaration specified in (rejected) PEP 396
VERSION_ATTRS = ("__version__", "version", "__version_tuple__", "version_tuple")  # nosec
NULL_VERSIONS = frozenset((None, "", "0", "0.0", "0.0.0", "0.0.0.0", (0,), (0, 0), (0, 0, 0), (0, 0, 0, 0)))  # nosec


def get_package_version(name):
    """Gets the version string of the library.
    :param name: The name of library.
    :type name: str
    :return: The version of the library. Returns None if can't determine version.
    :type return: str or None

    Usage::
        >>> get_package_version("botocore")
                "1.1.0"
    """

    version = _get_package_version(name)

    # Coerce iterables into a string
    if isinstance(version, tuple):
        version = ".".join(str(v) for v in version)

    return version


def get_package_version_tuple(name):
    """Gets the version tuple of the library.
    :param name: The name of library.
    :type name: str
    :return: The version of the library. Returns None if can't determine version.
    :type return: tuple or None

    Usage::
        >>> get_package_version_tuple("botocore")
                (1, 1, 0)
    """

    def int_or_str(value):
        try:
            return int(value)
        except Exception:
            return str(value)

    version = _get_package_version(name)

    # Split "." separated strings and cast fields to ints
    if isinstance(version, str):
        version = tuple(int_or_str(v) for v in version.split("."))

    return version


@_cache_package_versions
def _get_package_version(name):
    module = sys.modules.get(name, None)
    version = None

    # importlib was introduced into the standard library starting in Python3.8.
    if "importlib" in sys.modules and hasattr(sys.modules["importlib"], "metadata"):
        try:
            # In Python3.10+ packages_distribution can be checked for as well
            if hasattr(sys.modules["importlib"].metadata, "packages_distributions"):  # pylint: disable=E1101
                distributions = sys.modules["importlib"].metadata.packages_distributions()  # pylint: disable=E1101
                distribution_name = distributions.get(name, name)
                distribution_name = distribution_name[0] if isinstance(distribution_name, list) else distribution_name
            else:
                distribution_name = name

            version = sys.modules["importlib"].metadata.version(distribution_name)  # pylint: disable=E1101
            if version not in NULL_VERSIONS:
                return version
        except Exception:
            pass

    with warnings.catch_warnings(record=True):
        for attr in VERSION_ATTRS:
            try:
                version = getattr(module, attr, None)

                # In certain cases like importlib_metadata.version, version is a callable
                # function.
                if callable(version):
                    continue

                # In certain cases like clickhouse-connect python library, we get the version
                # as a module instead of its version, so ignoring it.
                if isinstance(version, types.ModuleType):
                    continue

                # Cast any version specified as a list into a tuple.
                version = tuple(version) if isinstance(version, list) else version
                if version not in NULL_VERSIONS:
                    return version
            except Exception:
                pass

    if "pkg_resources" in sys.modules:
        try:
            version = sys.modules["pkg_resources"].get_distribution(name).version
            if version not in NULL_VERSIONS:
                return version
        except Exception:
            pass

def get_plugins():
    stdlib_builtin_module_names = _get_stdlib_builtin_module_names()

    plugins = {}

    # Using any iterable to create a snapshot of sys.modules can occassionally
    # fail in a rare case when modules are imported in parallel by different
    # threads.
    #
    # TL;DR: Do NOT use an iterable on the original sys.modules to generate the
    # list
    for name, module in sys.modules.copy().items():
        if "." in name or name.startswith("_"):
            continue

        # If the module isn't actually loaded (such as failed relative imports
        # in Python 2.7), the module will be None and should not be reported.
        try:
            if not module:
                continue
        except Exception:
            # if the application uses generalimport to manage optional depedencies,
            # it's possible that generalimport.MissingOptionalDependency is raised.
            # In this case, we should not report the module as it is not actually loaded and
            # is not a runtime dependency of the application.
            #
            continue

        # Exclude standard library/built-in modules.
        if name in stdlib_builtin_module_names:
            continue

        version = None
        # Attempt to look up version information
        try:
            version = get_package_version(name)
        except Exception:
            pass

        # If it has no version it's likely not a real package so don't report it
        if version:
            plugins[name] = version

    return plugins

def _get_stdlib_builtin_module_names():
    builtins = set(sys.builtin_module_names)
    # Since sys.stdlib_module_names is not available in versions of python below 3.10,
    # use isort's hardcoded stdlibs instead.
    python_version = sys.version_info[0:2]
    if python_version < (3,):
        stdlibs = isort_stdlibs.py27.stdlib
    elif (3, 7) <= python_version < (3, 8):
        stdlibs = isort_stdlibs.py37.stdlib
    elif python_version < (3, 9):
        stdlibs = isort_stdlibs.py38.stdlib
    elif python_version < (3, 10):
        stdlibs = isort_stdlibs.py39.stdlib
    elif python_version >= (3, 10):
        stdlibs = sys.stdlib_module_names
    else:
        _logger.warn("Unsupported Python version. Unable to determine stdlibs.")
        return builtins
    return builtins | stdlibs
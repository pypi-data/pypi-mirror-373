# Copyright Commonwealth of Australia, Bureau of Meteorology 2024.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Archive Utilities.

Allow archives to be autoimported if detected to be on the system in question.
"""

from __future__ import annotations

from pathlib import Path
import os
import re

import importlib
import logging
from typing import Any
import warnings

from pyearthtools.data import archive
from pyearthtools.data.indexes.utilities.fileload import open_static

LOG = logging.getLogger("pyearthtools.data")


class ImportTest:
    """Methods to test whether to import or not"""

    @staticmethod
    def folder(path: str) -> bool:
        """Folder exists"""
        return Path(path).exists() and Path(path).is_dir()

    @staticmethod
    def file(path: str) -> bool:
        """File exists"""
        return Path(path).exists() and Path(path).is_file()

    @staticmethod
    def env(env_to_check: dict[str, Any] | list[str] | str) -> bool:
        """Environment variable either exists, or contains str"""
        if isinstance(env_to_check, list):
            return all([ImportTest.env(key) for key in env_to_check])

        elif isinstance(env_to_check, str):
            return isinstance(os.environ.get(env_to_check, None), str)

        elif isinstance(env_to_check, dict):
            return all([value in os.environ.get(key, "") for key, value in env_to_check.items()])

        raise TypeError(f"Cannot parse config of type {type(env_to_check)}")

    @staticmethod
    def hostname(name: str) -> bool:
        """Check hostname"""
        import socket

        hostname = str(socket.gethostname())
        return name in hostname

    @staticmethod
    def any(config: dict[str, Any]) -> bool:
        """Run any other with an any clause"""
        return any([getattr(ImportTest, key)(value) for key, value in config.items()])


def _strip_name(key: str) -> str:
    """Remove [] from keys"""
    return re.sub(r"\[.*\]", "", key)


def auto_import() -> None:
    """
    Attempt to auto import archives using registered files.
    """
    import_files: list[str] = list(open_static("pyearthtools.data.archive.registered", "register.txt"))

    for import_config_name in import_files:  # Run across all registered
        import_config: dict[str, Any] = open_static("pyearthtools.data.archive.registered", f"{import_config_name}.yaml")  # type: ignore

        import_module: str = import_config.pop("module")
        deprecated: bool = import_config.pop("deprecated", False)

        if deprecated:
            warnings.warn(
                f"{import_module} appears to be deprecated, please assess this use case.",
                DeprecationWarning,
            )

        to_import: bool = True
        test_results = {}

        for method, value in import_config.items():  # Check all conditions
            result = getattr(ImportTest, _strip_name(method))(value)
            test_results[method] = f"{value} = {result}"

            to_import = to_import and result

        if to_import:  # Attempt import
            try:
                importlib.import_module(import_module)
            except (ImportError, ModuleNotFoundError) as e:
                warnings.warn(
                    f"It appears that you are on {import_config_name}, but {import_module} could not be imported.\n{e}",
                    ImportWarning,
                )
        else:
            results_str = "\n".join([f"{key} - {val}" for key, val in test_results.items()])
            LOG.debug(f"Not importing {import_module} as tests failed. See below for results.\n" f"{results_str}")

    post_import()


def post_import():
    """Run post importing of archives"""
    if not hasattr(archive, "ERA5_ARCO"):
        from pyearthtools.data.download import arcoera5

        setattr(archive, "ERA5_ARCO", arcoera5.ARCOERA5)


__all__ = ["auto_import"]

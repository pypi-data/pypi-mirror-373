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


from __future__ import annotations

import warnings
import logging

import pyearthtools.data
from pyearthtools.data import archive
from pyearthtools.data.warnings import pyearthtoolsDataWarning

LOG = logging.getLogger("pyearthtools.data")


def config_root():
    """Setup Root Directories"""
    if hasattr(archive, "ROOT_DIRECTORIES"):
        ROOT_DIRECTORIES: dict = archive.ROOT_DIRECTORIES  # type: ignore
        setattr(archive, "_BACKUP_ROOT_DIRECTORIES", dict(ROOT_DIRECTORIES))
    else:
        LOG.info(
            "`ROOT_DIRECTORIES` not found underneath `pyearthtools.data.archive`, either archives are not installed or misconfigured. Root Directories cannot be changed. ",
            UserWarning,
        )


def set_root(root_dir: dict[str, str | None] | None = None, **kwargs: str | None):
    """
    Change root directory for data sources.

    Can set value of dictionary to None which will result
    in the root directory being reset to the default value.

    Args:
        root_dir (dict[str, str | None] | None, optional):
            Dictionary with root directory replacements. Defaults to None.
        **kwargs (dict[str,str | None]):
            Kwargs version of root_dir
    """
    if root_dir is None:
        root_dir = {}

    root_dir.update(**kwargs)
    if not hasattr(archive, "ROOT_DIRECTORIES"):
        raise UserWarning("ROOT_DIRECTORIES is not set, so cannot be updated by the user.")

    ROOT_DIRECTORIES = pyearthtools.data.archive.ROOT_DIRECTORIES  # type: ignore
    _BACKUP_ROOT_DIRECTORIES = pyearthtools.data.archive._BACKUP_ROOT_DIRECTORIES  # type: ignore

    for key, value in root_dir.items():
        if key not in ROOT_DIRECTORIES:
            raise KeyError(f"Could not find {key} in ROOT_DIRECTORIES, which contains {list(ROOT_DIRECTORIES.keys())}")

        if value is None:
            value = _BACKUP_ROOT_DIRECTORIES[key]
        else:
            warnings.warn(
                f"Changing Root Directory for {key} from {ROOT_DIRECTORIES[key]} to {value} for this session",
                pyearthtoolsDataWarning,
            )
        ROOT_DIRECTORIES[key] = value


def reset_root():
    """Reset all root directories"""
    if not hasattr(archive, "ROOT_DIRECTORIES"):
        raise UserWarning("ROOT_DIRECTORIES is not set, so cannot be updated by the user.")

    ROOT_DIRECTORIES = pyearthtools.data.archive.ROOT_DIRECTORIES  # type: ignore
    set_root(**{key: None for key in ROOT_DIRECTORIES})  # type: ignore

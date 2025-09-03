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
Extend the functionality of the `archive`.

Using `register_archive` allows a new data index to be added to the archive.

Examples:
    In your library code:

    >>> @pyearthtools.data.archive.register_archive("NewData")
    ... class NewData:
    ...     def __init__(self, initialisation_args):
    ...         pass
    ...
    ...

    Back in an interactive IPython session:

    >>> newdata_index = pyearthtools.data.archive.NewData(
    ...     *initialisation_args
    ... )
    >>> newdata_index(*access_args)  # Get data

"""

from __future__ import annotations

from types import ModuleType
from typing import Callable, Any

import os
import yaml
import warnings

import pyearthtools.data
from pyearthtools.data import archive


def register_archive(name: str, *, sample_kwargs: dict[str, Any] | None = None) -> Callable:
    """
    Register a custom archive underneath `pyearthtools.data.archive`.

    Args:
        name (str):
            Name under which the archive should be registered. A warning is issued
            if this name conflicts with a preexisting archive.
        sample_kwargs (dict[str, Any] | None, optional):
            Keyword arguments to initialise a sample index for demonstration.
            Can be retrieved with `.sample`
    """
    module_location = archive

    def decorator(archive_index: Any):
        """Register `accessor` under `name` on `cls`"""
        if hasattr(module_location, name):
            warnings.warn(
                f"Registration of archive {archive_index!r} under name {name!r} is "
                "overriding a preexisting archive with the same name.",
                pyearthtools.data.AccessorRegistrationWarning,
                stacklevel=2,
            )

        setattr(module_location, name, archive_index)

        if isinstance(archive_index, (ModuleType, Callable)):
            if not hasattr(archive_index, "_pyearthtools_initialisation"):
                setattr(archive_index, "_pyearthtools_initialisation", {})
            getattr(archive_index, "_pyearthtools_initialisation")["class"] = f"pyearthtools.data.archive.{name}"

        if isinstance(archive_index, Callable):

            def sample() -> pyearthtools.data.Index:
                if sample_kwargs is not None:
                    return archive_index(**sample_kwargs)
                raise RuntimeError("Keyword arguments were not given to create a `sample` index.")

            setattr(archive_index, "sample", sample)

        return archive_index

    return decorator


def set_root_directory(key: str, path: str):
    """
    Set / update the path for a specific key in ROOT_DIRECTORIES.

    Args:
        key (str): The key to update (e.g., "ERA5lowres").
        path (str): The new path to set.
    """

    ROOT_DIRECTORIES = pyearthtools.data.archive.ROOT_DIRECTORIES

    if key not in ROOT_DIRECTORIES:
        raise KeyError(f"Invalid key '{key}'. Valid keys are: {list(ROOT_DIRECTORIES.keys())}")
    ROOT_DIRECTORIES[key] = path


def get_root_directories():
    """
    Get the current ROOT_DIRECTORIES.

    Returns:
        dict: The current ROOT_DIRECTORIES.
    """

    return pyearthtools.data.archive.ROOT_DIRECTORIES


def load_root_directories_from_config(config_path: str):
    """
    Load ROOT_DIRECTORIES from a YAML config file.

    Args:
        config_path (str):
            The path to the YAML configuration file containing the root directory mappings.
    """
    if config_path is None:
        raise ValueError("config_path must be provided to load ROOT_DIRECTORIES from a config file.")

    ROOT_DIRECTORIES = pyearthtools.data.archive.ROOT_DIRECTORIES

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        for key in ROOT_DIRECTORIES:
            if key in config:
                ROOT_DIRECTORIES[key] = config[key]

    print("ROOT_DIRECTORIES:", ROOT_DIRECTORIES)

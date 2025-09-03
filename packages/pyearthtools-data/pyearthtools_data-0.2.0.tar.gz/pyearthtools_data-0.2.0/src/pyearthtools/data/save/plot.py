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

from pathlib import Path

from pyearthtools.data.indexes import FileSystemIndex


def save(
    plot,
    callback: FileSystemIndex,
    *args,
    save_kwargs: dict = {},
    **kwargs,
):
    """Save plot objects"""
    path = callback.search(*args, **kwargs)
    if not isinstance(path, (str, Path)):
        raise NotImplementedError(f"Cannot handle saving with paths as {type(path)}")
    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    # suffix = path.suffix  # TODO: why was this here

    if hasattr(plot, "fig"):
        plot = plot.fig
    if not hasattr(plot, "savefig"):
        raise TypeError(f"Unable to determine how to save {type(plot)}")

    plot.savefig(path, **save_kwargs)

    return path

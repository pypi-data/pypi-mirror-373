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
Download Based Data Indexes for `pyearthtools.data`

Implemented:

| Name | Description |
| ---- | ----------- |
| `DownloadIndex`  | Base download index. `download` must be implemented. |
| `cds` | Copernicus Data Store Access |
| `opendata` | ECMWF Opendata |
| `arcoera5` | Analysis-Ready, Cloud Optimized ERA5 by Google |
| `weatherbench` | WeatherBench2 cloud-optimized ground truth and baseline datasets |

"""

from pyearthtools.data.download.templates import DownloadIndex
from pyearthtools.data.download import cds, arcoera5, weatherbench
from pyearthtools.data.download import ecmwf_opendata as opendata

__all__ = ["DownloadIndex", "cds", "arcoera5", "weatherbench", "opendata"]

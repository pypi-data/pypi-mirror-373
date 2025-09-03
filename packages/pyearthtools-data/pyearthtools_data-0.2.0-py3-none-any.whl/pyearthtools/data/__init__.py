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


# ruff: noqa: F401
"""
`pyearthtools.data`

Provide a unified way to index into and retrieve data.

At the moment, data is confined to geospatial netcdf sources.

## Examples
=== "ERA5"
    ```python
    import pyearthtools.data

    ## Date of interest
    doi = '2022-04-01T03:00'

    ## Initialise the Data Loader
    dataloader = pyearthtools.data.archive.ERA5(variables = 'tmax')

    ## Get Data
    dataloader(doi)

    # <xarray.Dataset>
    # Dimensions:               (time: 1, latitude: 361, longitude: 720)
    # Coordinates:
    # * longitude               (longitude) float32 -180.0 -179.5 -179.0 ... 178.5 179.0 179.5
    # * latitude                (latitude) float32 90.0 89.5 89.0 88.5 ... -89.0 -89.5 -90.0
    # * time                    (time) datetime64[ns] 2022-04-01T03:00:00
    # Data variables:
    #     tmax                  (time, latitude, longitude) float32

    ```

=== "Expanded Date Pattern"
    ```python
    import pyearthtools.data

    ## Date of interest
    doi = '2022-04-01T03:00'

    ## Initialise the Data Loader
    dataloader = pyearthtools.data.patterns.ExpandedDate(root_dir = '/data/is/here/', extension = 'nc')

    ## Find Data
    dataloader.search(doi)

    # '/data/is/here/2022/04/01/20229401T0300.nc'
    ```

=== "Geographic Files"
    ```python
    import pyearthtools.data

    ## Initialise the Data Loader
    dataloader = pyearthtools.data.static.geographic()

    ## Find Data
    dataloader('world')

    ## Shapefiles for all countries in the world
    ```
"""

__version__ = "0.2.0"

from pyearthtools.data import logger
from pyearthtools.data import config

from pyearthtools.data.time import Petdt, TimeResolution, TimeDelta, TimeRange
from pyearthtools.data.time import Petdt as datetime

from pyearthtools.data.exceptions import DataNotFoundError, InvalidIndexError
from pyearthtools.data.warnings import (
    IndexWarning,
    pyearthtoolsDataWarning,
    AccessorRegistrationWarning,
)


from pyearthtools.data.collection import Collection, LabelledCollection

# from pyearthtools.data.catalog import Catalog, CatalogEntry

from pyearthtools.data.indexes import (
    Index,
    DataIndex,
    FileSystemIndex,
    TimeIndex,
    AdvancedTimeIndex,
    AdvancedTimeDataIndex,
    BaseTimeIndex,
    DataFileSystemIndex,
    ArchiveIndex,
    ForecastIndex,
    StaticDataIndex,
    CachingIndex,
    CachingForecastIndex,
    IntakeIndex,
    IntakeIndexCache,
)
from pyearthtools.data import indexes
from pyearthtools.data.indexes import register_accessor

from pyearthtools.data import operations as op

from pyearthtools.data import archive, operations, static, transforms, patterns, download, modifications, derived, utils
from pyearthtools.data import transforms as transform
from pyearthtools.data.patterns import PatternIndex

from pyearthtools.data.transforms.transform import (
    Transform,
    TransformCollection,
    FunctionTransform,
)
from pyearthtools.data.transforms.derive import evaluate
from pyearthtools.data import save
from pyearthtools.data.save import ManageFiles, ManageTemp

from pyearthtools.data.load import load

import pyearthtools.utils
import warnings as __python_warnings

from pyearthtools.data.archive.utils import auto_import

"""Auto import archives if available"""

auto_import()

"""Config Root Directories"""
archive.config_root()

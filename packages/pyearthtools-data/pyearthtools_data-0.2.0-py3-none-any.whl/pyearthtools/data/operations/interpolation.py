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
Provide Methods to spatially and temporally interpolate xarray Datasets
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import xarray as xr


import pyearthtools.data
from pyearthtools.data.transforms import interpolation as interp


def SpatialInterpolation(
    *datasets: xr.Dataset,
    reference_dataset: xr.Dataset | None = None,
    merge: bool = True,
    method: str = "linear",
    include_reference: bool = True,
    **kwargs,
) -> list[xr.Dataset] | xr.Dataset:
    """Spatially Interpolate Datasets together
    Uses [pyearthtools.data.transforms.interpolation][pyearthtools.data.transforms.interpolation.InterpolateTransform], thus all kwargs passed there


    Args:
        *datasets: All datasets to be spatially and temporally interpolated
        reference_dataset: Reference Dataset to use as base, if not given use first dataset.
        merge: Whether to merge datasets together.
        method: Spatially interpolation method. Uses [xarray interpolation][xarray.interpolation],
            which itself uses [scipy.interpolate][scipy.interpolate.interpn].
        include_reference: Whether to include reference datasets.
        **kwargs: Extra kwargs passed to [pyearthtools.data.transforms.interpolation][pyearthtools.data.transforms.interpolation.InterpolateTransform.like]

    Returns:
        List of datasets if merge == false, else one merged datasets
    """

    listed_datasets = [*datasets]

    interpolated_datasets = []
    if not reference_dataset:
        interpolated_datasets = [listed_datasets[0]] if include_reference else []
        reference_dataset = listed_datasets.pop(0)

    interp_transform = interp.like(reference_dataset, method=method, **kwargs)  # type: ignore

    for ds in listed_datasets:
        interpolated_datasets.append(interp_transform(ds))

    if merge:
        return xr.merge(interpolated_datasets)
    return interpolated_datasets


def TemporalInterpolation(
    *datasets: xr.Dataset,
    reference_dataset: xr.Dataset | None = None,
    aggregation_function: Callable | str | dict = "mean",
    merge: bool = True,
    include_reference: bool = True,
    **kwargs,
) -> list[xr.Dataset] | xr.Dataset:
    """Temporally Interpolate Datasets together
    Uses [pyearthtools.data.transforms.Aggregation][pyearthtools.data.transforms.aggregation.AggregateTransform.over], thus all kwargs passed there

    !!! Behaviour
        All timesteps will be aggregated to match time dim of reference dataset,
        Will only grab time before the given timestep


    Args:
        *datasets (xr.Dataset):
            All datasets to be spatially and temporally interpolated
        reference_dataset (xr.Dataset, optional):
            Reference Dataset to use as base, if not given use first dataset. Defaults to None.
        aggregation_function (Callable | str, optional):
            Aggregation function to use. Uses [pyearthtools.data.transforms.Aggregation][pyearthtools.data.transforms.aggregation.AggregateTransform.over].
            Defaults to "mean".
        merge (bool, optional):
            Whether to merge datasets together. Defaults to True.
        include_reference (bool, optional):
            Whether to include reference datasets. Defaults to True.

    Raises:
        ValueError:
            If time dim not present in `reference_dataset`

    Returns:
        (list[xr.Dataset] | xr.Dataset):
            List of datasets if merge == false, else one merged datasets
    """

    listed_datasets = [*datasets]

    interpolated_datasets = []
    if not reference_dataset:
        interpolated_datasets = [listed_datasets[0]] if include_reference else []
        reference_dataset = listed_datasets.pop(0)

    if "time" not in reference_dataset:
        raise ValueError("reference dataset contains no dimension 'time'. Cannot interpolate")

    last_index = None
    aggregation = pyearthtools.data.transforms.aggregation.over(aggregation_function, dimension="time", **kwargs)

    for ds in listed_datasets:
        temporal_ds = []
        for time in reference_dataset.time:
            aggregated_ds = aggregation(ds.sel(time=slice(last_index, time)))
            last_index = time
            aggregated_ds = aggregated_ds.expand_dims(time=np.atleast_1d(time), axis=[list(ds.dims).index("time")])
            temporal_ds.append(aggregated_ds)

        interpolated_datasets.append(xr.merge(temporal_ds))

    if merge:
        return xr.merge(interpolated_datasets)

    if len(interpolated_datasets) == 1:
        return interpolated_datasets[0]
    return interpolated_datasets


def FullInterpolation(
    *datasets: xr.Dataset,
    reference_dataset: xr.Dataset | None = None,
    temporal_reference_dataset: xr.Dataset | None = None,
    spatial_method: str = "linear",
    aggregation_function: Callable | str | dict = "mean",
    merge: bool = True,
    include_reference: bool = True,
) -> list[xr.Dataset] | xr.Dataset:
    """Interpolate Datasets both spatially and temporally

    Args:
        *datasets (xr.Dataset):
            All datasets to be spatially and temporally interpolated
        reference_dataset (xr.Dataset, optional):
            Reference Dataset to use as base, if not given use first dataset. Defaults to None.
        temporal_reference_dataset (xr.Dataset, optional):
            Temporal Reference Dataset to use as base, if not given use reference_dataset. Defaults to None.
        spatial_method (str, optional):
            Spatially interpolation method. Defaults to "linear".
        aggregation_function (Callable | str, optional):
            Aggregation function to use. Uses [pyearthtools.data.transforms.Aggregation][pyearthtools.data.transforms.aggregation.AggregateTransform.over].
            Defaults to "mean".
        merge (bool, optional):
            Whether to merge datasets together. Defaults to True.
        include_reference (bool, optional):
            Whether to include reference datasets. Defaults to True.

    Returns:
        (list[xr.Dataset] | xr.Dataset):
            List of datasets if merge == false, else one merged datasets
    """

    datasets = (*datasets, temporal_reference_dataset) if include_reference and temporal_reference_dataset else datasets

    spatial_datasets = SpatialInterpolation(
        *datasets,
        reference_dataset=reference_dataset,
        method=spatial_method,
        merge=False,
        include_reference=include_reference,
        drop_coords=["time", "spatial_ref"],
    )

    return TemporalInterpolation(
        *(spatial_datasets if isinstance(spatial_datasets, (list, tuple)) else (spatial_datasets,)),
        reference_dataset=temporal_reference_dataset or reference_dataset,
        aggregation_function=aggregation_function,
        include_reference=include_reference,
        merge=merge,
    )

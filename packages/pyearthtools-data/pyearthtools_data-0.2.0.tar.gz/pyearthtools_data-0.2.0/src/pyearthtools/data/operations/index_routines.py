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

import logging
from typing import Iterable

import warnings

import numpy as np
import pandas as pd
import xarray as xr

import pyearthtools

import pyearthtools.data
import pyearthtools.utils

from pyearthtools.data.exceptions import DataNotFoundError, InvalidIndexError, InvalidDataError
from pyearthtools.data.time import Petdt, TimeDelta, time_delta_resolution, TimeRange
from pyearthtools.data.transforms.transform import Transform, TransformCollection
from pyearthtools.data.warnings import IndexWarning
from pyearthtools.data.operations.utils import identify_time_dimension

LOG = logging.getLogger("pyearthtools.data")


def series(
    DataFunction: "pyearthtools.data.indexes.AdvancedTimeIndex",
    start: str | Petdt,
    end: str | Petdt,
    interval: tuple[float, str] | TimeDelta,
    *,
    inclusive: bool = False,
    skip_invalid: bool = False,
    transforms: Transform | TransformCollection = TransformCollection(),
    verbose: bool = False,
    force_get: bool = False,
    subset_time: bool = True,
    time_dim: str | None = None,
    tolerance: tuple | pd.Timedelta | None = None,
    **kwargs,
) -> xr.Dataset:
    """
    Index into Provided Data function to create a continuous series of Data

    Args:
        DataFunction (AdvancedTimeIndex):
            Data function, must be AdvancedTimeIndex or child
        start (str | datetime.datetime | Petdt):
            Timestep to begin series at
        end (str | datetime.datetime | Petdt):
            Timestep to end series at
        interval (tuple[float, str]):
            Time interval between samples. Use pandas.to_timedelta notation, (10, 'minute')
        inclusive (bool, optional):
            Whether end time is included in retrieval. Defaults to False.
        skip_invalid (bool, optional):
            Whether to skip invalid data. Defaults to False.
        transforms (Transform | TransformCollection, optional):
            Extra [Transform's][pyearthtools.data.transforms.Transform] to be applied to data. Defaults to TransformCollection().
        verbose (bool, optional):
            Print logging messages. Defaults to False.
        force_get (bool, optional):
            Use series method which loads each dataset using `.get`.
            WARNING: Takes significantly longer, as it does not use dask. Defaults to False.
        subset_time (bool, optional):
            Whether to force subset time dim. Defaults to True.
        tolerance (tuple | pd.Timedelta, optional):
            Tolerance for time subsetting. Defaults to None.

    Returns:
        (xr.Dataset): Loaded xarray dataset
    """

    transforms = TransformCollection(transforms)

    use_single = force_get
    if not hasattr(DataFunction, "search"):
        use_single = True

    # if isinstance(DataFunction, pyearthtools.data.CachingIndex):
    #     use_single = True

    interval = TimeDelta(interval)
    start = Petdt(start)
    end = Petdt(end)

    start = start.at_resolution(max(interval.resolution, start.resolution))
    end = end.at_resolution(max(end.resolution, start.resolution))

    if DataFunction.data_resolution:
        start = start.at_resolution(min(DataFunction.data_resolution, start.resolution))
        end = end.at_resolution(min(DataFunction.data_resolution, start.resolution))

    if inclusive:
        end = end + interval

    function = _mf_series

    if use_single:
        function = _get_series
    # else:
    # transforms += getattr(DataFunction, 'base_transforms', None)

    try:
        data = function(
            DataFunction,
            start,
            end,
            interval,
            skip_invalid=skip_invalid,
            transforms=None,
            verbose=verbose,
            **kwargs,
        )
    except NotImplementedError:
        data = _get_series(
            DataFunction,
            start,
            end,
            interval,
            skip_invalid=skip_invalid,
            transforms=None,
            verbose=verbose,
            **kwargs,
        )

    time_dim = time_dim or identify_time_dimension(data)
    if time_dim in data:
        data = data.sortby(time_dim)

    if not isinstance(data, xr.Dataset):
        return data

    """
    Subsetting on time
    TODO: Improvements
    """

    if subset_time:
        # If resolution of data is greater than the start resolution
        # expand time to include all in 1 step of start and its resolution
        # e.g. hourly data with a daily start and a monthly interval goes from
        # start = 'year-01-01', end = 'year+1', and interval is (1, 'month')
        # ['year-01-01', 'year-02-01'] to
        # ['year-01-01T00', 'year-01-01T01', 'year-01-01T02',..., 'year-02-01T22', 'year-02-01T23']
        timesteps = list(TimeRange(start, end, interval))
        if (
            pyearthtools.utils.config.get("data.experimental")
            and DataFunction.data_resolution
            and DataFunction.data_resolution > start.resolution
        ):
            timesteps = [
                t for time in timesteps for t in pyearthtools.data.TimeRange(time, time + 1, DataFunction.data_interval)
            ]

        time = list(set(map(lambda x: x.datetime64("ns"), timesteps)) & set(data[time_dim].values))

        if not time:
            time = timesteps
        sel_kwargs = {}

        if tolerance:  # and start.resolution < interval.resolution:
            if isinstance(tolerance, tuple):
                tolerance = TimeDelta(tolerance)

            if isinstance(tolerance, TimeDelta):
                tolerance = tolerance._timedelta

            sel_kwargs = getattr(DataFunction, "sel_kwargs", dict(method="bfill", tolerance=tolerance))
            time = list(
                set(
                    map(
                        lambda x: x.datetime64("ns") if x < end else None,
                        timesteps,
                    )
                )
            )
            while None in time:
                time.remove(None)

        time.sort()

        if len(time) == 0 and verbose:
            warnings.warn(
                f"Set of valid time is of length 0. Consider validity and resolution. For request: {start} -> {end} @ {interval}",
                IndexWarning,
            )

        subset_ds = data

        try:
            try:
                subset_ds = data.sel(**{time_dim: time}, **sel_kwargs)
            except KeyError:
                subset_ds = data.sel(**{time_dim: time[:-1]}, **sel_kwargs)
        except KeyError:
            warnings.warn(
                f"Unable to subset on time dimension, returning all timesteps for validation. For request: {start} -> {end} @ {interval}",
                IndexWarning,
            )

        # subset_ds = subset_ds.where(subset_ds.time < end.datetime64(), drop=True)

        try:
            subset_ds = subset_ds.sel(**{time_dim: slice(None, end.datetime64())})
        except TypeError:
            # We may be entering a non-gregorian calendar zone supported by cftime only
            # TODO: see if we can recognise and handle this a bit more gracefull, such as in the __lt__ method of petdatetime
            calendar = subset_ds.time[0].item().calendar
            end = end.to_cftime(calendar=calendar)
            subset_ds = subset_ds.sel(**{time_dim: slice(None, end)})

        if not len(subset_ds[time_dim]) == 0:
            data = subset_ds
        else:
            warnings.warn(
                f"When subsetting no time dimension remained, therefore, skipping the subsetting. For request: {start} -> {end} @ {interval}",
                IndexWarning,
            )

    return transforms(data)


def _mf_series(
    DataFunction: "pyearthtools.data.indexes.AdvancedTimeIndex",
    start: Petdt,
    end: Petdt,
    interval: TimeDelta,
    *,
    skip_invalid: bool = False,
    transforms: Transform | TransformCollection | None = None,
    verbose: bool = True,
    **kwargs,
):
    """
    Retrieve data using [xr.open_mfdataset][xr.open_mfdataset]

    Called by the series method
    """
    dataset_paths = []
    timesteps = []

    warning_count = 0
    warnings_list = []
    warning_threshold = pyearthtools.utils.config.get("data.series.warning_threshold")

    for query_time in TimeRange(start, end, interval, use_tqdm=verbose, desc="Getting data (mf)"):
        timesteps.append(query_time)

        try:
            if skip_invalid and not DataFunction.exists(query_time):
                continue
            files = DataFunction.search(query_time)

            def get_path(file):
                paths = []
                if isinstance(file, dict):
                    paths.extend(get_path(list(file.values())))
                    return paths
                elif isinstance(file, (list, tuple)):
                    for f in file:
                        if isinstance(f, str):
                            paths.append(f)
                        elif isinstance(f, Iterable):
                            paths.extend(get_path(f))
                        else:
                            paths.append(f)
                    return paths
                return file

            paths = get_path(files)
            dataset_paths.extend(paths if isinstance(paths, list) else [paths])
            dataset_paths = list(set(dataset_paths))

        except (DataNotFoundError, InvalidIndexError, InvalidDataError) as e:
            timesteps.remove(query_time)
            warnings_list.append(e)
            if skip_invalid:
                if warning_count < warning_threshold and verbose:
                    warnings.warn(
                        f"An error occured retrieving data at {query_time}, skipping..... \n{str(e)}",
                        IndexWarning,
                    )

                elif warning_count == warning_threshold and verbose:
                    warnings.warn("Warning Threshold reached, quieting warnings.", IndexWarning)

                warning_count += 1
            else:
                raise e

    if warning_count > warning_threshold and verbose:
        warnings.warn(
            f"During .series, {warning_count} data retrieval actions failed.",
            IndexWarning,
        )

    if not dataset_paths:
        if warnings_list:
            raise DataNotFoundError(
                f"Collection of data from {DataFunction.__class__.__name__} was empty. The following errors occured when getting data.\n{warnings_list}"
            )
        raise DataNotFoundError(
            f"Collection of data from {DataFunction.__class__.__name__} was empty, check start, end & interval parameters, or existence of data.\n{start} -> {end} @ {interval}"
        )

    LOG.debug(f"Opening Datasets. {dataset_paths}")

    open_kwargs = pyearthtools.utils.config.get("data.open.xarray")
    open_kwargs.update(pyearthtools.utils.config.get("data.open.xarray_mf"))
    open_kwargs.update(kwargs)

    try:
        full_ds = xr.open_mfdataset(
            list(set(dataset_paths)),
            **open_kwargs,
        )
    except NotImplementedError:
        # Work around a bug/gap in xarray for loading NetCDF4 files and autochunking

        open_kwargs.pop("chunks")

        full_ds = xr.open_mfdataset(
            list(set(dataset_paths)),
            **open_kwargs,
        )

    # full_ds = xr.merge(
    #     [
    #         xr.open_mfdataset( # moving out of preprocess due to issues with transforms needing all data
    #             list(set(value)),
    #             # preprocess=transforms + kwargs.pop("preprocess", None),
    #             chunks=kwargs.pop("chunks", "auto"),
    #             combine_attrs=kwargs.pop("combine_attrs", "override"),
    #             **kwargs,
    #         )
    #         for _, value in dataset_paths.items()
    #     ]
    # )
    if transforms is None:
        return full_ds
    return transforms(full_ds)


def _get_series(
    DataFunction: "pyearthtools.data.indexes.AdvancedTimeIndex",
    start: Petdt,
    end: Petdt,
    interval: TimeDelta,
    *,
    skip_invalid: bool = False,
    transforms: Transform | TransformCollection = TransformCollection(),
    verbose: bool = True,
    **kwargs,
):
    """
    Retrieve data using index `.get`

    """
    opened_datasets = []
    last_ds = None

    warning_count = 0
    warning_threshold = pyearthtools.utils.config.get("data.series.warning_threshold")

    _dim = kwargs.pop("dim", "time")

    timesteps = []

    for query_time in TimeRange(start, end, interval, use_tqdm=verbose, desc="Getting data (.get)"):
        timesteps.append(query_time)

        try:
            dataset = None
            if (
                last_ds is not None
                and "time" in last_ds.coords
                and query_time.datetime64("ns") in np.atleast_1d(last_ds.time)
            ):
                dataset = last_ds
            else:
                if transforms is None:
                    dataset = DataFunction.get(query_time, **kwargs)
                else:
                    dataset = transforms(DataFunction.get(query_time, **kwargs))
                opened_datasets.append(dataset)

            last_ds = dataset

        except (DataNotFoundError, InvalidIndexError, InvalidDataError) as e:
            timesteps.remove(query_time)
            if skip_invalid:
                if warning_count < warning_threshold and verbose:
                    warnings.warn(
                        f"An error occured retrieving data at {query_time}, skipping.....",
                        IndexWarning,
                    )

                elif warning_count == warning_threshold and verbose:
                    warnings.warn("Warning Threshold reached, quieting warnings.", IndexWarning)

                warning_count += 1
            else:
                raise e

    if warning_count > warning_threshold and verbose:
        warnings.warn(
            f"During .series, {warning_count} data retrieval actions failed.",
            IndexWarning,
        )

    if not opened_datasets:
        raise DataNotFoundError(
            f"Collection of data from {DataFunction.__class__.__name__} was empty, check start, end & interval parameters, or existence of data.\n{start} -> {end} @ {interval}"
        )

    dataset = xr.concat(opened_datasets, dim="time")

    return dataset


def safe_series(
    DataFunction: "pyearthtools.data.indexes.AdvancedTimeIndex",
    start: str | Petdt,
    end: str | Petdt,
    interval: TimeDelta,
    **kwargs,
) -> xr.Dataset:
    """Safely index into the provided Data function to create a continuous series of Data.

    Called by the series method

    Uses [series][pyearthtools.data.operations.index_routines.series], but provides an automatic interpolation.

    !!! Warning
        If data is missing or if a resolution higher than the actual data resolution is provided,
        those missing time steps will be interpolated,


    Args:
        DataFunction (AdvancedTimeIndex):
            Data function, must be AdvancedTimeIndex or child
        start (str | Petdt):
            Timestep to begin series at
        end (str | Petdt):
            Timestep to end series at
        interval (TimeDelta):
            Time interval between samples. Use pandas.to_timedelta notation, (10, 'minute')
        **kwargs (dict, optional):
            Any extra keyword arguments to pass to [series][pyearthtools.data.operations.index_routines.series]

    Returns:
        (xr.Dataset):
            Loaded xarray dataset
    """

    kwargs["skip_invalid"] = True

    interval = TimeDelta(interval)
    start = Petdt(start)
    end = Petdt(end)

    if DataFunction.data_resolution and time_delta_resolution(interval) > DataFunction.data_resolution:
        data: xr.Dataset = series(
            DataFunction,
            start.at_resolution(DataFunction.data_resolution) - 1,
            end.at_resolution(DataFunction.data_resolution) + 1,
            DataFunction.data_interval,
            **kwargs,
        )
        data.attrs["WARNING"] = "Data was interpolated to this resolution"
    else:
        data = series(DataFunction, start, end, interval, **kwargs)

    start = start.at_resolution(interval)
    end = end.at_resolution(interval)

    if kwargs.get("inclusive", False):
        end = end + interval

    time_values = [(start + interval * i).datetime64() for i in range(((end - start) // interval))]

    if len(time_values) == 1:
        return data

    if "time" in data and not len(time_values) == len(data.time):
        if not data.time.values[0] == time_values[0] or not data.time.values[-1] == time_values[-1]:
            raise DataNotFoundError(f"Cannot interpolate first or last data point. {time_values} != {data.time.values}")

        return data.compute().interp(time=time_values)
    return data

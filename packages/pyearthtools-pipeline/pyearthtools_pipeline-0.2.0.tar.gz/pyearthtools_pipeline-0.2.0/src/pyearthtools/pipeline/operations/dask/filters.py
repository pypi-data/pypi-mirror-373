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


# type: ignore[reportPrivateImportUsage]

import math
from typing import Literal, Union

import dask.array as da
import numpy as np

from pyearthtools.pipeline.filters import Filter, PipelineFilterException


class daskFilter(Filter):
    """dask Filters"""

    _override_interface = ["Serial"]

    def __init__(self):
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=da.Array,
        )


class DropAnyNan(daskFilter):
    """
    Filter to drop any data with nans when iterating.

    Used to remove any bad data or data that is masked out.
    """

    def __init__(self) -> None:
        """Drop data with any nans"""
        super().__init__()
        self.record_initialisation()

    def filter(self, sample: da.Array):
        """Check if any of the sample is nan

        Args:
            sample (da.Array):
                Sample to check
        Returns:
            (bool):
                If sample contains nan's
        """
        if not bool(da.array(list(da.isnan(sample))).any()):
            raise PipelineFilterException(sample, "Data contained nan's.")


class DropAllNan(daskFilter):
    """
    Filter to drop any data if all nans.

    Used to remove any bad data or data that is masked out.
    """

    def __init__(self) -> None:
        """Drop data with any nans"""
        super().__init__()
        self.record_initialisation()

    def filter(self, sample: da.Array):
        """Check if all of the sample is nan

        Args:
            sample (da.Array):
                Sample to check
        Returns:
            (bool):
                If sample contains nan's
        """
        if not bool(da.array(list(da.isnan(sample))).all()):
            raise PipelineFilterException(sample, "Data contained all nan's.")


class DropValue(daskFilter):
    """
    Filter to drop data containing more than a given percentage of a value.

    Can be used to trim out invalid data
    """

    def __init__(self, value: Union[float, Literal["nan"]], percentage: float) -> None:
        """Drop Data if number of elements equal to value are greater than percentage when iterating.

        Args:
            value (Union[float, Literal["nan"]]):
                Value to search for. Can be nan or 'nan'.
            percentage (float):
                Percentage of `value` of which an exceedance drops data
        """
        super().__init__()
        self.record_initialisation()

        if isinstance(value, str) and value == "nan":
            value = np.nan

        self._value = value
        self._percentage = percentage

    def filter(self, sample: da.Array):
        """Check if all of the sample is nan

        Args:
            sample (da.Array):
                Sample to check
        Returns:
            (bool):
                If sample contains nan's
        """
        if da.isnan(self._value):
            function = (  # noqa
                lambda x: ((da.count_nonzero(da.isnan(x)) / math.prod(x.shape)) * 100) >= self._percentage
            )  # noqa
        else:
            function = (  # noqa
                lambda x: ((da.count_nonzero(x == self._value) / math.prod(x.shape)) * 100) >= self._percentage
            )  # noqa

        if not function(sample):
            raise PipelineFilterException(sample, f"Data contained more than {self._percentage}% of {self._value}.")


class Shape(Filter):
    """
    Filter to drop data of incorrect shape

    Used to ensure that incoming data is of the correct shape for later steps
    """

    def __init__(self, shape: tuple[Union[tuple[int, ...], int], ...], split_tuples: bool = False) -> None:
        """
        Drop Data if shape does not match expected

        Args:
            shape tuple[Union[tuple[int, ...], int]):
                Shape to match, either tuple of shapes for tupled data or direct shape
            split_tuples (bool, optional):
                Whether to split tuples, if `True`, `shape` should not be a tuple of tuples
        """
        super().__init__(split_tuples=split_tuples, recognised_types=da.Array)
        self.record_initialisation()

        self._shape = shape

    def _find_shape(self, data: Union[tuple[da.Array, ...], da.Array]) -> tuple[Union[tuple, int], ...]:
        if isinstance(data, tuple):
            return tuple(map(self._find_shape, data))
        return data.shape

    def check_shape(self, sample: Union[tuple[da.Array, ...], da.Array]):
        if isinstance(sample, (list, tuple)):
            if not isinstance(self._shape, (list, tuple)) and len(self._shape) == len(sample):
                raise RuntimeError(
                    f"If sample is tuple, shape must also be, and of the same length. {self._shape} != {tuple(self._find_shape(i) for i in sample)}"
                )

        if not self._find_shape(sample) == self._shape:
            raise PipelineFilterException(
                sample, f"Shapes were found not to be the same.\n{self._find_shape(sample)} != {self._shape}"
            )

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


from typing import Hashable, TypeVar, Union

import xarray as xr

import pyearthtools.data
from pyearthtools.pipeline.operation import Operation

T = TypeVar("T", xr.Dataset, xr.DataArray)


class Dimensions(Operation):
    """
    Reorder dimensions
    """

    _override_interface = "Serial"

    def __init__(
        self,
        dimensions: Union[str, list[str]],
        append: bool = True,
        preserve_order: bool = False,
    ):
        """
        Operation to reorder Dimensions of an [xarray][xarray] object.

        Not all dims have to be supplied, will automatically add remaining dims,
        or if append == False, prepend extra dims.

        Args:
            dimensions (Union[str, list[str]]):
                Specified order of dimensions to tranpose dataset to
            append (bool, optional):
                Append extra dims, if false, prepend dims. Defaults to True.
            preserve_order (bool, optional):
                Whether to preserve the order of dims or on `undo`, also set to dimensions order.
                Defaults to False.
        """
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=(xr.Dataset, xr.DataArray),
        )
        self.record_initialisation()

        self.dimensions = dimensions if isinstance(dimensions, (list, tuple)) else [dimensions]
        self.append = append
        self.preserve_order = preserve_order

        self._incoming_dims = None

        self.__doc__ = "Reorder Dimensions"

    def apply_func(self, sample: T) -> T:
        dims = sample.dims
        self._incoming_dims = list(dims)

        dims = set(dims).difference(set(self.dimensions))

        if self.append:
            dims = [*self.dimensions, *dims]
        else:
            dims = [*dims, *self.dimensions]

        if self.preserve_order:
            self._incoming_dims = dims

        return sample.transpose(*dims, missing_dims="ignore")

    def undo_func(self, sample: T) -> T:
        if self._incoming_dims:
            return sample.transpose(*self._incoming_dims, missing_dims="ignore")
        return sample


class CoordinateFlatten(Operation):
    """Flatten and Expand on a coordinate"""

    _override_interface = "Serial"

    def __init__(self, coordinate: Union[Hashable, list[Hashable]], *coords: Hashable, skip_missing: bool = False):
        """
        Flatten and expand on coordinate/s

        Args:
            coordinate (Union[Hashable,list[Hashable]]):
                Coordinate to flatten and expand on.
            skip_missing (bool, optional):
                Whether to skip data without the dims. Defaults to False
        """
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=(xr.Dataset, xr.DataArray),
        )
        self.record_initialisation()

        coordinate = [coordinate, *coords] if not isinstance(coordinate, (list, tuple)) else [*coordinate, *coords]
        self.coords = coordinate
        self._skip_missing = skip_missing

    def apply_func(self, ds):
        return pyearthtools.data.transforms.coordinates.Flatten(self.coords, skip_missing=self._skip_missing)(ds)

    def undo_func(self, ds):
        return pyearthtools.data.transforms.coordinates.expand(self.coords)(ds)

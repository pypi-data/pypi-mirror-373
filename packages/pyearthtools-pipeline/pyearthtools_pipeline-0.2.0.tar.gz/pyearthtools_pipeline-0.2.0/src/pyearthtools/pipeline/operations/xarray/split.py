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


from typing import TypeVar, Union, Optional, Any

import xarray as xr

from pyearthtools.pipeline.branching.split import Spliter

T = TypeVar("T", xr.Dataset, xr.DataArray)


class OnVariables(Spliter):
    """Split xarray object's on variables"""

    _override_interface = "Serial"

    def __init__(
        self,
        variables: Optional[Union[tuple[Union[str, tuple[str, ...], list[str]], ...], list[str]]] = None,
        merge_kwargs: Optional[dict[str, Any]] = None,
    ):
        """
        Split on variables

        Args:
            variables (Optional[Union[tuple[Union[str, tuple[str, ...], list[str]], ...], list[str]]], optional):
                Variable split. If tuple or list, will split into those tuples, with the associated list referencing the variables to split out.
                If not given, will split all variables into seperate items. Defaults to None.
            merge_kwargs (Optional[dict[str, Any]], optional):
                Kwargs needed for merge on the `undo`. Defaults to None.
        """
        super().__init__(
            recognised_types=(xr.DataArray, xr.Dataset),
            recursively_split_tuples=True,
        )
        self.record_initialisation()

        self._variables = variables
        self._merge_kwargs = merge_kwargs

    def split(self, sample: xr.Dataset) -> tuple[xr.Dataset, ...]:
        """Split sample"""

        subsets = []
        for var in self._variables or list(sample.data_vars):
            if any(map(lambda x: x not in sample, (var,) if not isinstance(var, (tuple, list)) else var)):
                raise ValueError(
                    f"Could not split on {var}, as it was not found in dataset. Found {list(sample.data_vars)}."
                )
            subsets.append(sample[list(var) if isinstance(var, (tuple, list)) else [var]])
        return tuple(subsets)

    def join(self, sample: tuple[Union[xr.Dataset, xr.DataArray], ...]) -> xr.Dataset:
        """Join sample"""
        return xr.merge(sample, **(self._merge_kwargs or {}))


class OnCoordinate(Spliter):
    """Split xarray object on coordinate"""

    _override_interface = "Serial"

    def __init__(
        self,
        coordinate: str,
        merge_kwargs: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            recursively_split_tuples=True,
            recognised_types=(xr.DataArray, xr.Dataset),
        )
        self.record_initialisation()

        self.coordinate = coordinate
        self._merge_kwargs = merge_kwargs

    def split(self, sample: T) -> tuple[T, ...]:
        return tuple(sample.sel(**{self.coordinate: i}) for i in sample.coords[self.coordinate])

    def undo(self, sample: tuple[T, ...]) -> xr.Dataset:
        return xr.merge(sample, **(self._merge_kwargs or {}))

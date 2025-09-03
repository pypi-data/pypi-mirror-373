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

from typing import Optional

import dask.array as da

from pyearthtools.pipeline.operations.dask.dask import DaskOperation


class Select(DaskOperation):
    """
    Operation to select an element from a given array
    """

    _override_interface = ["Serial"]
    _numpy_counterpart = "select.Select"

    def __init__(
        self,
        array_index: tuple[Optional[int], ...],
        tuple_index: Optional[int] = None,
    ):
        """Select data from a given index

        Args:
            array_index (tuple[Optional[int],...]):
                Tuple of indexes from which to select data. Can use None to specify not to select
            tuple_index (Optional[int], optional):
                Choice of which tuple element to apply selection to, if tuples passed. Defaults to None.

        Examples
            >>> incoming_data = da.zeros((10,5,2))
            >>> select = Select([0])
            >>> select.apply_func(incoming_data).shape
            (5,2)
            >>> select = Select([0, None, 0])
            >>> select.apply_func(incoming_data).shape
            (5)
        """

        super().__init__(
            operation="apply",
            split_tuples=False,
            recognised_types=(da.Array, tuple, list),
        )

        self.record_initialisation()

        self.array_index = array_index
        self.tuple_index = tuple_index

    def _index(self, data, array_index):
        shape = data.shape
        for i, index in enumerate(reversed(array_index)):
            if index is None:
                pass
            selected_data = da.take(data, indices=index, axis=-(i + 1))
            if len(selected_data.shape) < len(shape):
                selected_data = da.expand_dims(selected_data, axis=-(i + 1))
            data = selected_data
        return data

    def apply_func(self, data):
        array_index = self.array_index

        if isinstance(data, tuple):
            data = list(data)
            if self.tuple_index is None:
                return tuple(map(lambda x: self._index(x, array_index), data))

            data[self.tuple_index] = self._index(data[self.tuple_index], array_index)
            data = tuple(data)
            return data

        return self._index(data, array_index)


class Slice(DaskOperation):
    """
    Slice a chunk of a dask array

    Examples:
        >>> Slicer((0,10,2)) # == slice(0,10,2)
        >>> incoming_data = da.zeros((10,5,4))
        >>> Slicer((0,10,2), (1, 3)).apply_func(incoming_data).shape
        (5,2,4)
        >>> Slicer((1, 3)).apply_func(incoming_data).shape
        (2,5,4)
        >>> Slicer((1, 3), reverse_slice = True).apply_func(incoming_data).shape
        (10,5,2)
    """

    _override_interface = ["Serial"]
    _numpy_counterpart = "select.Slice"

    def __init__(self, *slices: tuple[Optional[int], ...], reverse_slice: bool = False):
        """
        Setup slicing operation

        Args:
            slices (tuple[Optional[int], ...]):
                Each tuple is converted into a slice. So must follow slice notation
            reverse_slice (bool, optional):
                Whether to slice offset towards last axis. Defaults to False.
        """
        super().__init__(
            operation="apply",
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=da.Array,
        )

        self.record_initialisation()
        self._slices = tuple(slice(*x) for x in slices)
        self.reverse_slice = reverse_slice

    def apply_func(self, sample: da.Array) -> da.Array:
        if self.reverse_slice:
            base_slices = [slice(None, None, None)] * (len(sample.shape) - len(self._slices))
            base_slices.extend(self._slices)
            return sample[tuple(base_slices)]

        return sample[self._slices]

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


from typing import Union, Optional, Any

import math
import einops
import numpy as np

from pyearthtools.pipeline.operation import Operation


class Rearrange(Operation):
    """
    Operation to rearrange data using einops

    """

    _override_interface = ["Delayed", "Serial"]
    _interface_kwargs = {"Delayed": {"name": "Rearrange"}}

    def __init__(
        self,
        rearrange: str,
        skip: bool = False,
        reverse_rearrange: Optional[str] = None,
        rearrange_kwargs: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """Using Einops rearrange, rearrange data.

        Args:

            rearrange (str):
                String entry to einops.rearrange
            skip (bool, optional):
                Whether to skip data that cannot be rearranged. Defaults to False.
            reverse_rearrange (Optional[str], optional):
                Override for reverse operation, if not given flip rearrange. Defaults to None.
            rearrange_kwargs ( Optional[dict[str, Any]], optional):
                Extra keyword arguments to be passed to the einops.rearrange call. Defaults to {}.
        """
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=(np.ndarray),
        )
        self.record_initialisation()

        self.pattern = rearrange
        self.reverse_pattern = reverse_rearrange

        rearrange_kwargs = rearrange_kwargs or {}
        rearrange_kwargs.update(kwargs)
        self.rearrange_kwargs = rearrange_kwargs

        self.skip = skip

    def _rearrange(self, data: np.ndarray, pattern: str, catch=True):

        try:
            return einops.rearrange(data, pattern, **self.rearrange_kwargs)
        except einops.EinopsError as excep:
            if not catch:
                if self.skip:
                    return data
                raise excep
            pattern = "->".join(["p " + side for side in pattern.split("->")])
            return self._rearrange(data, pattern, catch=False)

    def apply_func(self, data: np.ndarray):
        return self._rearrange(data, self.pattern)

    def undo_func(self, data: np.ndarray):
        if self.reverse_pattern:
            pattern = self.reverse_pattern
        else:
            pattern = self.pattern.split("->")
            pattern.reverse()
            pattern = "->".join(pattern)
        return self._rearrange(data, pattern)


class Squeeze(Operation):
    """
    Operation to Squeeze one-Dimensional axes at 'axis' location

    """

    _override_interface = ["Delayed", "Serial"]
    _interface_kwargs = {"Delayed": {"name": "Squeeze"}}

    def __init__(self, axis: Union[tuple[int, ...], int]) -> None:
        """Squeeze Dimension of Data, removing dimensions of length 1.

        Args:
            axis (Union[tuple[int, ...], int]):
                Axis to squeeze at
        """
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=(np.ndarray),
        )
        self.record_initialisation()

        self.axis = axis

    def apply_func(self, sample: np.ndarray) -> np.ndarray:
        try:
            sample = np.squeeze(sample, self.axis)
        except ValueError as e:
            e.args = (*e.args, f"Shape {sample.shape}")
            raise e
        return sample

    def undo_func(self, sample: np.ndarray) -> np.ndarray:
        return np.expand_dims(sample, self.axis)


class Expand(Operation):
    """
    Operation to Expand One Dimensional axis at 'axis' location

    """

    _override_interface = ["Delayed", "Serial"]
    _interface_kwargs = {"Delayed": {"name": "Expand"}}

    def __init__(self, axis: Union[tuple[int, ...], int]) -> None:
        """Expand Dimension of Data

        Args:
            axis (Union[tuple[int, ...], int]):
                Axis to expand at
        """
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=(np.ndarray),
        )
        self.record_initialisation()

        self.axis = axis

    def apply_func(self, sample: np.ndarray) -> np.ndarray:
        return np.expand_dims(sample, self.axis)

    def undo_func(self, sample: np.ndarray) -> np.ndarray:
        try:
            sample = np.squeeze(sample, self.axis)
        except ValueError as e:
            e.args = (*e.args, f"Shape {sample.shape}")
            raise e
        return sample


class Flattener:
    _unflattenshape = None
    _fillshape = None

    def __init__(
        self,
        flatten_dims: Optional[int] = None,
        shape_attempt: Optional[tuple[Union[str, int], ...]] = None,
    ) -> None:
        self.shape_attempt = shape_attempt

        if isinstance(flatten_dims, int) and flatten_dims < 1:
            raise ValueError("'flatten_dims' cannot be smaller than 1.")
        self.flatten_dims = flatten_dims

    def _prod_shape(self, shape):
        if isinstance(shape, np.ndarray):
            shape = shape.shape
        return math.prod(shape)

    def _configure_shape_attempt(self) -> tuple[Union[str, int], ...]:
        if not self._fillshape or not self.shape_attempt:
            raise RuntimeError("Cannot find shape to unflatten with, try flattening first.")
        if "..." not in self.shape_attempt:
            return self.shape_attempt

        shape_attempt = list(self.shape_attempt)
        if not len(shape_attempt) == len(self._fillshape):
            raise IndexError(f"Shapes must be the same length, not {shape_attempt} and {self._unflattenshape}")

        while "..." in shape_attempt:
            shape_attempt[shape_attempt.index("...")] = self._fillshape[shape_attempt.index("...")]

        return tuple(shape_attempt)

    def apply(self, data: np.ndarray) -> np.ndarray:
        # if self._unflattenshape is None:
        self._unflattenshape = data.shape
        self._fillshape = self._fillshape or data.shape

        self.flatten_dims = self.flatten_dims or len(data.shape)

        self._unflattenshape = self._unflattenshape[-1 * self.flatten_dims :]
        return data.reshape(
            (
                *data.shape[: -1 * self.flatten_dims],
                self._prod_shape(self._unflattenshape),
            )
        )

    def undo(self, data: np.ndarray) -> np.ndarray:
        if self._unflattenshape is None:
            raise RuntimeError("Shape not set, therefore cannot undo")

        def _unflatten(data, shape):
            # while len(data.shape) > len(shape):
            #     shape = (data[-len(shape)], *shape)
            return data.reshape(shape)

        if self.flatten_dims is None:
            raise RuntimeError("`flatten_dims` was not set, and this set hasn't been used. Cannot Unflatten.")

        data_shape = data.shape
        # parsed_shape = data_shape[: -1 * min(1, (self.flatten_dims - 1))] if len(data_shape) > 1 else []
        parsed_shape = data_shape[:-1] if len(data_shape) > 1 else []
        attempts = [
            (*parsed_shape, *self._unflattenshape),
        ]

        if self.shape_attempt:
            shape_attempt = self._configure_shape_attempt()
            if shape_attempt:
                attempts.append((*parsed_shape, *shape_attempt[-1 * self.flatten_dims :]))  # type: ignore

        for attemp in attempts:
            try:
                return _unflatten(data, attemp)
            except ValueError:
                continue
        raise ValueError(f"Unable to unflatten array of shape: {data.shape} with any of {attempts}")


class Flatten(Operation):
    """
    Operation to Flatten parts of data samples into a one dimensional array
    """

    _override_interface = ["Delayed", "Serial"]
    _interface_kwargs = {"Delayed": {"name": "Flatten"}}

    def __init__(
        self,
        flatten_dims: Optional[int] = None,
        *,
        shape_attempt: Optional[tuple[int, ...]] = None,
    ) -> None:
        """Operation to flatten incoming data

        Args:
            flatten_dims: Number of dimensions to flatten, counting from the end. If None, flatten all,
                          with size being stored from first use.
                          Is used for negative indexing, so for last three dims `flatten_dims` == 3, Defaults to None.
            shape_attempt: Reshape value to try if discovered shape fails. Used if data coming to be undone is different.
                           Can have `'...'` as wildcards to get from discovered, Defaults to None.

        Examples:

            >>> incoming_data = np.zeros((5,4,3,2))
            >>> flattener = Flatten(flatten_dims = 2)
            >>> flattener.apply_func(incoming_data).shape
            ... (5, 4, 6)
            >>> flattener = Flatten(flatten_dims = 3)
            >>> flattener.apply_func(incoming_data).shape
            ... (5, 24)
            >>> flattener = Flatten(flatten_dims = None)
            >>> flattener.apply_func(incoming_data).shape
            ... (120)

        .. tip::
            **`shape_attempt` Advanced Use**

            If using a model which does not return a full sample, say an XGBoost model only returning the centre value, set `shape_attempt`.

            If incoming data is of shape `(1, 1, 3, 3)`, and data for undoing is `(1, 1, 1, 1)` aka `(1)`, set `shape_attempt` to `('...','...', 1, 1)`


            >>> title="Spatial Size Change"
            >>> incoming_data = np.zeros((1,1,3,3))
            >>> flattener = Flatten(shape_attempt = (1,1,1,1))
            >>> flattener.apply_func(incoming_data).shape   #(9,)
            >>>
            >>> undo_data = np.zeros((1))
            >>> flattener.undo_func(undo_data).shape        #(1,1,1,1)


            If incoming data is of shape `(8, 1, 3, 3)`, and data for undoing is `(2, 1, 1, 1)` aka `(2)`, set `shape_attempt` to `(2,'...',1,1)`

            >>> title=" Channel or Time Size Change also"
            >>> incoming_data = np.zeros((8,1,3,3))
            >>> flattener = Flatten(shape_attempt = (2,1,1,1))
            >>> flattener.apply_func(incoming_data).shape   #(72,)
            >>>
            >>> undo_data = np.zeros((2))
            >>> flattener.undo_func(undo_data).shape        #(2,1,1,1)

        """
        super().__init__(
            split_tuples=False,
            recognised_types=(np.ndarray),
        )
        self.record_initialisation()

        self.shape_attempt = shape_attempt
        self.flatten_dims = flatten_dims
        self._flatteners = []

    def _get_flatteners(self, number: int) -> tuple[Flattener]:
        """
        Retrieve a set number of Flattener, creating new ones if needed
        """
        return_values = []

        for i in range(number):
            if i < len(self._flatteners):
                return_values.append(self._flatteners[i])
            else:
                self._flatteners.append(Flattener(shape_attempt=self.shape_attempt, flatten_dims=self.flatten_dims))
                return_values.append(self._flatteners[-1])

        return tuple(return_values)

    def apply_func(self, sample: Union[tuple[np.ndarray, ...], np.ndarray]):
        if isinstance(sample, tuple):
            flatteners = self._get_flatteners(len(sample))
            return tuple(flatteners[i].apply(data_item) for i, data_item in enumerate(sample))
        return self._get_flatteners(1)[0].apply(sample)

    def undo_func(self, sample: Union[tuple[np.ndarray, ...], np.ndarray]) -> Union[tuple[np.ndarray, ...], np.ndarray]:
        if isinstance(sample, tuple):
            flatteners = self._get_flatteners(len(sample))
            return tuple(flatteners[i].undo(item) for i, item in enumerate(sample))
        else:
            return self._get_flatteners(1)[0].undo(sample)


class SwapAxis(Operation):
    def __init__(self, axis_1: int, axis_2: int) -> None:
        """Move axis

        Args:
            axis_1 (int):
                Source axis
            axis_2 (int):
                Target axis
        """
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=np.ndarray,
        )
        self.record_initialisation()

        self.axis_1 = axis_1
        self.axis_2 = axis_2

    def apply_func(self, sample: np.ndarray) -> np.ndarray:
        return np.swapaxes(sample, self.axis_1, self.axis_2)

    def undo_func(self, sample: np.ndarray) -> np.ndarray:
        return np.swapaxes(sample, self.axis_2, self.axis_1)

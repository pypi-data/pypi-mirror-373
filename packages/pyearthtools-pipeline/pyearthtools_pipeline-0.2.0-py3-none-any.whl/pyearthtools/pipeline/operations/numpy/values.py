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


from typing import Literal, Union, Optional

import numpy as np

import pyearthtools.data

from pyearthtools.pipeline.operation import Operation


class FillNan(Operation):
    """
    Fill any Nan's with a value
    """

    _override_interface = ["Delayed", "Serial"]
    _interface_kwargs = {"Delayed": {"name": "FillNan"}}

    def __init__(
        self,
        nan: float = 0,
        posinf: Optional[float] = None,
        neginf: Optional[float] = None,
    ) -> None:
        """
        DataOperation to fill Nan's

        Args:
            nan (float, optional):
                Value to fill nan's with.
                If no value is passed then NaN values will not be replaced. Defaults to 0.
            posinf (float, optional):
                Value to be used to fill positive infinity values,
                If no value is passed then positive infinity values will be replaced with a very large number. Defaults to None.
            neginf (float, optional):
                Value to be used to fill negative infinity values,
                If no value is passed then negative infinity values will be replaced with a very small (or negative) number. Defaults to None.
        """

        super().__init__(
            operation="apply",
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=np.ndarray,
        )

        self.record_initialisation()

        self.nan = nan
        self.posinf = posinf
        self.neginf = neginf

    def apply_func(self, sample: np.ndarray):
        return np.nan_to_num(np.array(sample), nan=self.nan, posinf=self.posinf, neginf=self.neginf)


class MaskValue(Operation):
    """
    DataOperation to mask values with a given replacement
    """

    _override_interface = ["Delayed", "Serial"]
    _interface_kwargs = {"Delayed": {"name": "MaskValue"}}

    def __init__(
        self,
        value: Union[float, dict[str, float]],
        operation: Literal["==", ">", "<", ">=", "<="] = "==",
        replacement_value: Union[float, dict[str, float]] = np.nan,
    ):
        """
        Operation to Mask Values

        Args:
            value (Union[float, dict[str, float]]):
                Value to search for.
            operation (Literal['==', '>', '<', '>=','<='], optional):
                Operation to search with. Defaults to '=='.
            replacement_value (Union[float, dict[str, float]], optional):
                Replacement value. Defaults to np.nan.

        Raises:
            KeyError:
                If invalid `operation` passed.
        """
        super().__init__(
            operation="apply",
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=np.ndarray,
        )

        self.record_initialisation()

        if operation not in ["==", ">", "<", ">=", "<="]:
            raise KeyError(f"Invalid operation {operation!r}. Must be one of  ['==', '>', '<', '>=', '<=']")
        self.operation = operation
        self.value = value
        self.replacement_value = replacement_value

        self._mask_transform = pyearthtools.data.transforms.mask.replace_value(value, operation, replacement_value)

    def apply_func(self, sample: np.ndarray) -> np.ndarray:
        """
        Mask Data from initialised configuration

        Args:
            sample (np.ndarray):
                Data to apply mask to

        Returns:
            (np.ndarray):
                Masked Data
        """
        return self._mask_transform(sample)  # type: ignore


class ForceNormalised(Operation):
    """
    Operation to force data within a certain range, by default 0 & 1
    """

    _override_interface = ["Delayed", "Serial"]
    _interface_kwargs = {"Delayed": {"name": "ForceNormalised"}}

    def __init__(
        self,
        min_value: Optional[Union[float, dict[str, float]]] = 0,
        max_value: Optional[Union[float, dict[str, float]]] = 1,
    ):
        """
        Force data into a specified range

        Args:
            min_value (Optional[Union[float, dict[str, float]]], optional):
                Minimum Value. If using a dict, acts per variable given.
                If None, this won't apply a min masking
                Defaults to 0.
            max_value (Optional[Union[float, dict[str, float]]], optional):
                Maximum Value. If using a dict, acts per variable given.
                If None, this won't apply a max masking
                Defaults to 1.
        """
        super().__init__(
            operation="apply",
            split_tuples=True,
            recursively_split_tuples=True,
            recognised_types=np.ndarray,
        )

        self.record_initialisation()

        self._force_min = MaskValue(min_value, "<", min_value) if min_value is not None else None
        self._force_max = MaskValue(max_value, ">", max_value) if max_value is not None else None

    def apply_func(self, sample):
        for func in (func for func in [self._force_min, self._force_max] if func is not None):
            sample = func.apply_func(sample)
        return sample

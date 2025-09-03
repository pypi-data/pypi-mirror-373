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

"""Augment data"""


import dask.array as da
import numpy as np

from pyearthtools.pipeline.operations.dask.dask import DaskOperation


class Rotate(DaskOperation):
    """
    Rotation Augmentation by 90 degrees in the plane specified by axes.
    """

    _override_interface = ["Serial"]
    _numpy_counterpart = "augment.Rotate"

    def __init__(
        self,
        seed: int = 42,
        axis: tuple[int, int] = (-2, -1),
    ):
        """
        Rotation Augmentation by 90 degrees in the plane specified by axes.

        Generates a random number between 0 & 3 inclusive, for number of times to rotate.

        Args:
            seed (int, optional):
                Random Number seed. Defaults to 42.
            axis (tuple[int, int], optional):
                Rotation plane. Axes must be different. Defaults to (-2, -1).
        """
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            operation="apply",
            recognised_types=(da.Array),
        )
        self.record_initialisation()

        self.rng = np.random.default_rng(seed)
        if not isinstance(axis, (list, tuple)):
            raise TypeError("'axis' must be a tuple or list")
        self.axis = axis

    def apply_func(self, sample: da.Array) -> da.Array:
        random_num = self.rng.integers(0, 3, endpoint=True)
        return da.rot90(sample, k=random_num, axes=self.axis)


class Flip(DaskOperation):
    """
    Flip Augmentation on the specified axes.
    """

    _override_interface = ["Serial"]
    _numpy_counterpart = "augment.Flip"

    def __init__(self, seed: int = 42, axis: int = -1):
        """
        Flip Augmentation by 90 degrees in the plane specified by axes.

        Generates a random boolean, if True, flip, otherwise not

        Args:
            seed (int, optional):
                Random Number seed. Defaults to 42.
            axis (tuple[int], optional):
                Axis to flip data in. Defaults to -1.
        """
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            operation="apply",
            recognised_types=(da.Array),
        )
        self.record_initialisation()

        self.rng = np.random.default_rng(seed)
        self.axis = axis

    def apply_func(self, sample: da.Array) -> da.Array:
        random_num = self.rng.integers(0, 1, endpoint=True)
        if random_num > 0:
            return da.flip(sample, axis=self.axis)
        return sample


class FlipAndRotate(DaskOperation):
    """
    Flip & Rotation Augmentation.
    """

    _override_interface = ["Serial"]
    _numpy_counterpart = "augment.FlipAndRotate"

    def __init__(
        self,
        seed: int = 42,
        axis: tuple[int, int] = (-2, -1),
    ):
        """
        Apply both Flip & Rotation Augmentations, will rotate on given axis, and flip on both

        Args:
            seed (int, optional):
                Random Number seed. Defaults to 42.
            axis (tuple[int], optional):
                Rotation plane primarily. Axes must be different. Will also flip on each given axis. Defaults to (-2, -1).
        """
        super().__init__(
            split_tuples=True,
            recursively_split_tuples=True,
            operation="apply",
            recognised_types=(da.Array),
        )
        self.record_initialisation()

        self.transforms: list[DaskOperation] = [Rotate(seed=seed, axis=axis)]

        for i, ax in enumerate(axis):
            self.transforms.append(Flip(seed=seed * i, axis=ax))

    def apply_func(self, sample: da.Array) -> da.Array:
        for trans in self.transforms:
            sample = trans.apply_func(sample)
        return sample

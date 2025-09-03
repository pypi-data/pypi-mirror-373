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

from typing import Any, Optional, Union, Literal
import warnings

from pathlib import Path
from hashlib import sha512
import shutil

import pyearthtools.data
from pyearthtools.data.patterns import PatternIndex

from pyearthtools.pipeline.controller import PipelineIndex
from pyearthtools.pipeline.warnings import PipelineWarning
from pyearthtools.pipeline.exceptions import PipelineRuntimeError

CACHE_HASH_NAME = ".cache_hash"
PIPELINE_SAVE_NAME = "pipeline.yaml"


class Cache(PipelineIndex):
    """
    An `pyearthtools.pipeline` implementation of the `CachingIndex` from `pyearthtools.data`.

    Allows for samples to be cached to disk when using the pipeline.

    Will save according to the `pattern` and `idx` used to retrieve data.

    Examples:
        >>> era_index = pyearthtools.data.archive.ERA5.sample()
        >>> pipeline = pyearthtools.pipeline.Pipeline(
                era_index,
                pyearthtools.pipeline.pipelines.Cache('temp')
            )
        >>> pipeline['2000-01-01T00'] # Data will be cached
    """

    _cache: pyearthtools.data.indexes.FunctionalCacheIndex

    def __init__(
        self,
        cache: Optional[Union[str, Path]] = None,
        pattern: Optional[Union[str, PatternIndex]] = None,
        *,
        pattern_kwargs: dict[str, Any] = {},
        cache_validity: Literal["trust", "delete", "warn", "keep", "override", "deleteF"] = "warn",
        save_kwargs: dict[str, Any] | None = None,
        **kwargs,
    ):
        """
        Pipeline step to cache samples

        Args:
            cache (str | Path, optional):
                Path to cache data to. Defaults to None.
            pattern (str | PatternIndex, optional):
                Pattern to use to cache data, if str use `pattern_kwargs` to initialise. Defaults to None.
            pattern_kwargs (dict[str, Any], optional):
                Kwargs to initalise the pattern with. Defaults to {}.
            cache_validity (Literal['trust','delete','warn','keep','override'], optional):
                Behaviour of cache validity checking.
                | Value | Behaviour |
                | ----- | --------- |
                | 'trust' | Trust the cache even if the hash is different |
                | 'warn'  | Warn if the hash is different |
                | 'keep'  | Keep the cache, and raise an exception if the hash is different |
                | 'override' | Override the cache data when generating data, removes the caching benefit. |
                | 'delete'   | Delete the cache if the hash is different. Will ask for input, include 'F' to force. |
                Defaults to 'warn'.
            save_kwargs (dict[str, Any], optional):
                Keywords arguments to pass to saving function. Defaults to None.
            kwargs (Any, optional):
                All other kwargs passed to `pyearthtools.data.indexes.FunctionalCacheIndex`.
        """
        super().__init__()
        self.record_initialisation()

        self.cache_behaviour = cache_validity
        self._cache = pyearthtools.data.indexes.FunctionalCacheIndex(
            cache,
            pattern,
            function=self._generate,
            pattern_kwargs=pattern_kwargs,
            save_kwargs=save_kwargs,
            **kwargs,
        )
        self.update_initialisation(cache=str(self.cache.cache))

    def _generate(self, idx):
        return self.parent_pipeline()[idx]

    def __getitem__(self, idx):
        """
        Get a sample from the cache, will generate it if it doesn't exist in the cache.
        """
        if self.save_cache_hash():
            self.save_pipeline()

        return self.cache[idx]

    @property
    def cache(self) -> pyearthtools.data.indexes.FunctionalCacheIndex:
        return self._cache

    @property
    def pattern(self) -> pyearthtools.data.patterns.PatternIndex:
        return self.cache.pattern

    @property
    def override(self):
        """Get a context window in which data will be overwritten in the cache"""
        return self.cache.override

    @property
    def global_override(self):
        """Get a context window in which data will be overwritten in all caches"""
        return self.cache.global_override

    @property
    def root_dir(self) -> Path:
        return self.cache.pattern.root_dir

    """
    Hashing and pipeline saving
    """

    @property
    def cache_hash_file(self) -> Path:
        """Get the hash file name"""
        return Path(self.root_dir) / CACHE_HASH_NAME

    @property
    def pipeline_save_file(self) -> Path:
        """Get the pipeline save file name"""
        return Path(self.root_dir) / PIPELINE_SAVE_NAME

    def save_cache_hash(self) -> bool:
        """
        Attempt to make cache hash, if fails do nothing and try again later.

        Will return `bool` indicating if saving hash was successfull.
            True -> Valid hash
            False -> Invalid hash, either unable to write or different
        """
        try:
            return self.cache_validity()
        except Exception as e:
            warnings.warn(f"Cache hash could not be made yet. \n{e}", PipelineWarning)
            return False

    def save_pipeline(self):
        """
        Attempt to make pipeline file, if fails do nothing and try again later.
        """
        try:
            self.as_pipeline().save(self.pipeline_save_file)
        except Exception as e:
            warnings.warn(f"Pipeline file could not be made. \n{e}", PipelineWarning)

    def cache_validity(self) -> bool:
        """
        Check the cache validity according to `cache_validity` passed in `__init__`.
        """
        if not self.cache_hash_file.exists():
            self._save_hash()
            return True

        if not self._get_saved_hash():
            self._save_hash()
            self.save_pipeline()
            return False

        cache_validity = self.hash == self._get_saved_hash()

        if cache_validity or self.root_dir is None:
            return True

        if self.cache_behaviour == "trust":
            self._save_hash()
            return True
        elif self.cache_behaviour == "override":
            self._save_hash()
            return True
        elif self.cache_behaviour == "keep":
            raise PipelineRuntimeError(
                "The saved cache hash is not equal to the current hash.\n"
                "Data may be incorrect. If this data can be trusted, change "
                "'cache_validity' to 'trust' or 'warn', or if it needs to be deleted, "
                "set to 'delete', or 'override'."
                f"\nAt location {str(self.root_dir)!r}"
            )
        elif self.cache_behaviour == "warn":
            warnings.warn(
                "The saved hash and current hash are not the same.\n"
                "Therefore, data loaded from the cache may not be what is expected.\n"
                "If this cache is valid, pass 'cache_validity' = 'trust' once, to trust this cache.\n"
                "If not, pass 'cache_validity' = 'delete' or 'override', to delete the cache "
                "or override it respectively."
                f"\nAt location {str(self.root_dir)!r}",
                PipelineWarning,
            )
            return False

        elif "delete" in self.cache_behaviour:
            if "F" not in self.cache_behaviour:
                if not input("Cache was invalid, Are you sure you want to delete all cached data? (YES/NO): ") == "YES":
                    warnings.warn("Skipping delete.", UserWarning)
                    return False

            warnings.warn(f"Deleting all data underneath '{self.root_dir}'.", UserWarning)
            shutil.rmtree(self.root_dir)
            self._save_hash()
        else:
            raise ValueError(f"Cannot parse 'cache_validity' of {self.cache_behaviour}")
        return True

    def _save_hash(self):
        """Save the hash"""
        if not self.cache_hash_file.parent.exists():
            self.cache_hash_file.parent.mkdir(exist_ok=True, parents=True)

        with open(self.cache_hash_file, "w") as file:
            file.write(self.hash)

    def _get_saved_hash(self):
        """Get the saved hash"""
        with open(self.cache_hash_file, "r") as file:
            return file.read()

    def _get_saved_pipeline(self):
        """Get the saved pipeline as txt"""
        with open(self.pipeline_save_file, "r") as file:
            return file.read()

    @property
    def hash(self) -> str:
        """
        Get sha512 hash of underlying index
        """
        configuration = self.parent_pipeline().save(only_steps=True)  # Hash only parent pipeline
        return sha512(bytes(str(configuration), "utf-8")).hexdigest()


class StaticCache(Cache):
    """
    Static Cache.

    Mainly a convenience wrapper instead of using `IdxOverride` and `Cache` together.

    Will override the index, and cache the result.
    """

    _memory_sample = None

    def __init__(
        self,
        idx: Any,
        cache: Union[str, Path],
        pattern: Optional[Union[str, PatternIndex]] = None,
        *,
        pattern_kwargs: dict[str, Any] = {},
        cache_validity: Literal["trust", "delete", "warn", "keep", "override"] = "warn",
        load_into_memory: bool = False,
        **kwargs,
    ):
        """
        Static Cache

        Args:
            idx (Any):
                Index to override with
            cache (str | Path, optional):
                Path to cache data to. Defaults to None.
            pattern (str | PatternIndex, optional):
                Pattern to use to cache data, if str use `pattern_kwargs` to initialise. Defaults to None.
            pattern_kwargs (dict[str, Any], optional):
                Kwargs to initalise the pattern with. Defaults to {}.
            cache_validity (Literal['trust','delete','warn','keep','override'], optional):
                Behaviour of cache validity checking.
                | Value | Behaviour |
                | ----- | --------- |
                | 'trust' | Trust the cache even if the hash is different |
                | 'warn'  | Warn if the hash is different |
                | 'keep'  | Keep the cache, and raise an exception if the hash is different |
                | 'override' | Override the cache data when generating data, removes the caching benefit. |
                | 'delete'   | Delete the cache if the hash is different. Will ask for input, include 'F' to force. |
                Defaults to 'warn'.
            load_into_memory (bool):
                Load sample into memory if it is a dask or xarray object. Defaults to False.
        """
        super().__init__(cache, pattern, pattern_kwargs=pattern_kwargs, cache_validity=cache_validity, **kwargs)
        self.record_initialisation()
        self._idx = idx
        self._load_into_memory = load_into_memory

    def __getitem__(self, idx):
        if self.save_cache_hash():
            self.save_pipeline()

        if self._load_into_memory and self._memory_sample is not None:
            return self._memory_sample

        sample = self.cache[self._idx]

        if self._load_into_memory:
            if hasattr(sample, "compute"):
                sample = sample.compute()
            self._memory_sample = sample
        return sample


class MemCache(PipelineIndex):
    """
    An `pyearthtools.pipeline` implementation of the `MemCache` from `pyearthtools.data`.

    Allows for samples to be cached to memory when using the pipeline.

    Examples:
        >>> era_index = pyearthtools.data.archive.ERA5.sample()
        >>> pipeline = pyearthtools.pipeline.Pipeline(
                era_index,
                pyearthtools.pipeline.pipelines.MemCache()
            )
        >>> pipeline['2000-01-01T00'] # Data will be cached to memory
    """

    _cache: pyearthtools.data.indexes.FunctionalMemCacheIndex

    def __init__(
        self,
        pattern: Optional[Union[str, PatternIndex]] = None,
        max_size: Optional[str] = None,
        *,
        pattern_kwargs: dict[str, Any] = {},
        **kwargs,
    ):
        """
        Pipeline step to cache samples

        Args:
            pattern (str | PatternIndex, optional):
                Pattern to use to cache data, if str use `pattern_kwargs` to initialise. Defaults to None.
            pattern_kwargs (dict[str, Any], optional):
                Kwargs to initalise the pattern with. Defaults to {}.
            kwargs (Any, optional):
                All other kwargs passed to `pyearthtools.data.indexes.FunctionalMemCacheIndex`.
        """
        super().__init__()
        self.record_initialisation()

        self._cache = pyearthtools.data.indexes.FunctionalMemCacheIndex(
            pattern=pattern,
            function=self._generate,  # type: ignore
            max_size=max_size,
            pattern_kwargs=pattern_kwargs,
            **kwargs,
        )

    def _generate(self, idx):
        return self.parent_pipeline()[idx]

    def __getitem__(self, idx):
        """
        Get a sample from the cache, will generate it if it doesn't exist in the cache.
        """
        return self.cache[idx]

    @property
    def cache(self) -> pyearthtools.data.indexes.FunctionalMemCacheIndex:
        return self._cache

    @property
    def size(self):
        """Size of in memory cache"""
        return self.cache.size

    @property
    def override(self):
        """Get a context window in which data will be overwritten in the cache"""
        return self.cache.override

    @property
    def global_override(self):
        """Get a context window in which data will be overwritten in all caches"""
        return self.cache.global_override

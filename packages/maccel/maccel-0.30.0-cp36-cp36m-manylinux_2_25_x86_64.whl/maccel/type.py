##
# \file
#

from typing import List, Optional, Tuple
from enum import Enum

import numpy as np

import maccel.maccel as _cMaccel

##
# \addtogroup PythonAPI
# @{


class Cluster(Enum):
    """
    @brief Enumerates clusters in the ARIES NPU.

    @note The ARIES NPU consists of two clusters, each containing one global core and
    four local cores, totaling eight local cores. REGULUS has only a single cluster
    (Cluster0) with one local core (Core0).
    """

    Cluster0 = _cMaccel.Cluster.Cluster0
    Cluster1 = _cMaccel.Cluster.Cluster1
    Error = _cMaccel.Cluster.Error


class Core(Enum):
    """
    @brief Enumerates cores within a cluster in the ARIES NPU.

    @note The ARIES NPU consists of two clusters, each containing one global core and
    four local cores, totaling eight local cores. REGULUS has only a single cluster
    (Cluster0) with one local core (Core0).
    """

    Core0 = _cMaccel.Core.Core0
    Core1 = _cMaccel.Core.Core1
    Core2 = _cMaccel.Core.Core2
    Core3 = _cMaccel.Core.Core3
    All = _cMaccel.Core.All
    GlobalCore = _cMaccel.Core.GlobalCore
    Error = _cMaccel.Core.Error


class CoreAllocationPolicy(Enum):
    """@brief Core allocation policy"""

    Auto = _cMaccel.CoreAllocationPolicy.Auto
    Manual = _cMaccel.CoreAllocationPolicy.Manual


class LatencySetPolicy(Enum):
    """@deprecated This enum is deprecated."""

    Auto = _cMaccel.LatencySetPolicy.Auto
    Manual = _cMaccel.LatencySetPolicy.Manual


class MaintenancePolicy(Enum):
    """@deprecated This enum is deprecated."""

    Maintain = _cMaccel.MaintenancePolicy.Maintain
    DropExpired = _cMaccel.MaintenancePolicy.DropExpired
    Undefined = _cMaccel.MaintenancePolicy.Undefined


class SchedulePolicy(Enum):
    """@deprecated This enum is deprecated."""

    FIFO = _cMaccel.SchedulePolicy.FIFO
    LIFO = _cMaccel.SchedulePolicy.LIFO
    ByPriority = _cMaccel.SchedulePolicy.ByPriority
    Undefined = _cMaccel.SchedulePolicy.Undefined


class Scale:
    """@brief Struct for scale values."""

    def __init__(self, scale: float, is_uniform: bool, scale_list: List[float]):
        self._scale = _cMaccel.Scale()
        self._scale.scale = scale
        self._scale.is_uniform = is_uniform
        self._scale.scale_list = scale_list

    @classmethod
    def from_cpp(cls, _scale: _cMaccel.Scale):
        return cls(_scale.scale, _scale.is_uniform, _scale.scale_list)

    @property
    def scale_list(self) -> List[float]:
        return self._scale.scale_list

    @property
    def scale(self) -> float:
        return self._scale.scale

    @property
    def is_uniform(self) -> bool:
        return self._scale.is_uniform

    @scale_list.setter
    def scale_list(self, value: List[float]):
        self._scale.scale_list = value

    @scale.setter
    def scale(self, value: float):
        self._scale.scale = value

    @is_uniform.setter
    def is_uniform(self, value: bool):
        self._scale.is_uniform = value

    def __getitem__(self, i: int) -> float:
        """
        @brief Returns the scale value at the specified index.

        @param[in] i Index.
        @return Scale value.
        """
        return self._scale[i]

    def __repr__(self):
        d = {
            "scale": self.scale,
            "is_uniform": self.is_uniform,
            "scale_list": self.scale_list,
        }
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={}".format(k, v) for k, v in d.items()),
        )


class CoreId:
    """
    @brief Represents a unique identifier for an NPU core.

    A CoreId consists of a Cluster and a Core, identifying a specific core
    within an NPU.
    """

    def __init__(self, cluster: Cluster, core: Core):
        self._core_id = _cMaccel.CoreId()
        self._core_id.cluster = cluster.value
        self._core_id.core = core.value

    @classmethod
    def from_cpp(cls, _core_id: _cMaccel.CoreId):
        return cls(Cluster(_core_id.cluster), Core(_core_id.core))

    @property
    def cluster(self) -> Cluster:
        return Cluster(self._core_id.cluster)

    @property
    def core(self) -> Core:
        return Core(self._core_id.core)

    @cluster.setter
    def cluster(self, value: Cluster):
        self._core_id.cluster = value.value

    @core.setter
    def core(self, value: Core):
        self._core_id.core = value.value

    def __eq__(self, other) -> bool:
        """
        @brief Checks if two CoreId objects are equal.

        @return True if both CoreId objects are identical, False otherwise.
        """
        return self._core_id == other._core_id

    def __lt__(self, other) -> bool:
        """
        @brief Compares two CoreId objects for ordering.

        @return True if this CoreId is less than the given CoreId, False otherwise.
        """
        return self._core_id < other._core_id

    def __repr__(self):
        d = {"cluster": self.cluster, "core": self.core}
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={}".format(k, v) for k, v in d.items()),
        )


class Buffer:
    """
    @brief A simple byte-sized buffer.

    This struct represents a contiguous block of memory for storing byte-sized data.
    """

    def __init__(self, _buffer: Optional[_cMaccel.Buffer] = None):
        self._buffer = _cMaccel.Buffer() if _buffer is None else _buffer

    @property
    def size(self) -> int:
        return self._buffer.size

    @size.setter
    def size(self, value: int):
        self._buffer.size = value

    def set_buffer(self, arr: np.ndarray):
        self._buffer.set_buffer(np.ascontiguousarray(arr))

    def __repr__(self):
        return f"{self.__class__.__name__}(size={self._buffer.size})"


class CoreMode(Enum):
    """
    @brief Defines the core mode for NPU execution.

    Supported core modes include single-core, multi-core, global4-core, and global8-core.
    For detailed explanations of each mode, refer to the following functions:

    - `ModelConfig.set_single_core_mode()`
    - `ModelConfig.set_multi_core_mode()`
    - `ModelConfig.set_global4_core_mode()`
    - `ModelConfig.set_global8_core_mode()`
    """

    Single = _cMaccel.CoreMode.Single
    Multi = _cMaccel.CoreMode.Multi
    Global = _cMaccel.CoreMode.Global
    Global4 = _cMaccel.CoreMode.Global4
    Global8 = _cMaccel.CoreMode.Global8
    Error = _cMaccel.CoreMode.Error


class BufferInfo:
    """@brief Struct representing input/output buffer information."""

    def __init__(
        self,
        original_height: int = 0,
        original_width: int = 0,
        original_channel: int = 0,
        reshaped_height: int = 0,
        reshaped_width: int = 0,
        reshaped_channel: int = 0,
        height: int = 0,
        width: int = 0,
        channel: int = 0,
        max_height: int = 0,
        max_width: int = 0,
        max_channel: int = 0,
        max_cache_size: int = 0,
    ):
        self._buffer_info = _cMaccel.BufferInfo()
        self._buffer_info.original_height = original_height
        self._buffer_info.original_width = original_width
        self._buffer_info.original_channel = original_channel
        self._buffer_info.reshaped_height = reshaped_height
        self._buffer_info.reshaped_width = reshaped_width
        self._buffer_info.reshaped_channel = reshaped_channel
        self._buffer_info.height = height
        self._buffer_info.width = width
        self._buffer_info.channel = channel
        self._buffer_info.max_height = max_height
        self._buffer_info.max_width = max_width
        self._buffer_info.max_channel = max_channel
        self._buffer_info.max_cache_size = max_cache_size

    @classmethod
    def from_cpp(cls, _buffer_info: _cMaccel.BufferInfo):
        return cls(
            _buffer_info.original_height,
            _buffer_info.original_width,
            _buffer_info.original_channel,
            _buffer_info.reshaped_height,
            _buffer_info.reshaped_width,
            _buffer_info.reshaped_channel,
            _buffer_info.height,
            _buffer_info.width,
            _buffer_info.channel,
            _buffer_info.max_height,
            _buffer_info.max_width,
            _buffer_info.max_channel,
            _buffer_info.max_cache_size,
        )

    @property
    def original_height(self) -> int:
        """Height of original input/output"""
        return self._buffer_info.original_height

    @property
    def original_width(self) -> int:
        """Width of original input/output"""
        return self._buffer_info.original_width

    @property
    def original_channel(self) -> int:
        """Channel of original input/output"""
        return self._buffer_info.original_channel

    @property
    def reshaped_height(self) -> int:
        """Height of reshaped input/output"""
        return self._buffer_info.reshaped_height

    @property
    def reshaped_width(self) -> int:
        """Width of reshaped input/output"""
        return self._buffer_info.reshaped_width

    @property
    def reshaped_channel(self) -> int:
        """Channel of reshaped input/output"""
        return self._buffer_info.reshaped_channel

    @property
    def height(self) -> int:
        """Height of NPU input/output"""
        return self._buffer_info.height

    @property
    def width(self) -> int:
        """Width of NPU input/output"""
        return self._buffer_info.width

    @property
    def channel(self) -> int:
        """Channel of NPU input/output"""
        return self._buffer_info.channel

    @property
    def max_height(self) -> int:
        """Maximum height of original input/output if data is sequential."""
        return self._buffer_info.max_height

    @property
    def max_width(self) -> int:
        """Maximum width of original input/output if data is sequential."""
        return self._buffer_info.max_width

    @property
    def max_channel(self) -> int:
        """Maximum channel of original input/output if data is sequential."""
        return self._buffer_info.max_channel

    @property
    def max_cache_size(self) -> int:
        """Maximum KV-cache size, relevant for LLM models using KV cache."""
        return self._buffer_info.max_cache_size

    @original_height.setter
    def original_height(self, value: int):
        self._buffer_info.original_height = value

    @original_width.setter
    def original_width(self, value: int):
        self._buffer_info.original_width = value

    @original_channel.setter
    def original_channel(self, value: int):
        self._buffer_info.original_channel = value

    @reshaped_height.setter
    def reshaped_height(self, value: int):
        self._buffer_info.reshaped_height = value

    @reshaped_width.setter
    def reshaped_width(self, value: int):
        self._buffer_info.reshaped_width = value

    @reshaped_channel.setter
    def reshaped_channel(self, value: int):
        self._buffer_info.reshaped_channel = value

    @height.setter
    def height(self, value: int):
        self._buffer_info.height = value

    @width.setter
    def width(self, value: int):
        self._buffer_info.width = value

    @channel.setter
    def channel(self, value: int):
        self._buffer_info.channel = value

    @max_height.setter
    def max_height(self, value: int):
        self._buffer_info.max_height = value

    @max_width.setter
    def max_width(self, value: int):
        self._buffer_info.max_width = value

    @max_channel.setter
    def max_channel(self, value: int):
        self._buffer_info.max_channel = value

    @max_cache_size.setter
    def max_cache_size(self, value: int):
        self._buffer_info.max_cache_size = value

    def original_size(self) -> int:
        """
        @brief Returns the total size of the original input/output.

        @return The data size.
        """
        return self._buffer_info.original_size()

    def reshaped_size(self) -> int:
        """
        @brief Returns the total size of the reshaped input/output.

        @return The data size.
        """
        return self._buffer_info.reshaped_size()

    def size(self) -> int:
        """
        @brief Returns the total size of the NPU input/output.

        @return The data size.
        """
        return self._buffer_info.size()

    def original_shape(self) -> Tuple[int, int, int]:
        return self._buffer_info.original_shape()

    def original_shape_chw(self) -> Tuple[int, int, int]:
        return self._buffer_info.original_shape_chw()

    def reshaped_shape(self) -> Tuple[int, int, int]:
        return self._buffer_info.reshaped_shape()

    def reshaped_shape_chw(self) -> Tuple[int, int, int]:
        return self._buffer_info.reshaped_shape_chw()

    def shape(self) -> Tuple[int, int, int]:
        return self._buffer_info.shape()

    def shape_chw(self) -> Tuple[int, int, int]:
        return self._buffer_info.shape_chw()

    def __repr__(self):
        d = {
            "original_height": self._buffer_info.original_height,
            "original_width": self._buffer_info.original_width,
            "original_channel": self._buffer_info.original_channel,
            "reshaped_height": self._buffer_info.reshaped_height,
            "reshaped_width": self._buffer_info.reshaped_width,
            "reshaped_channel": self._buffer_info.reshaped_channel,
            "height": self._buffer_info.height,
            "width": self._buffer_info.width,
            "channel": self._buffer_info.channel,
            "max_height": self._buffer_info.max_height,
            "max_width": self._buffer_info.max_width,
            "max_channel": self._buffer_info.max_channel,
            "max_cache_size": self._buffer_info.max_cache_size,
        }
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={}".format(k, v) for k, v in d.items()),
        )


class ModelConfig:
    """
    @brief Configures a core mode and core allocation of a model for NPU inference.
    The `ModelConfig` class provides methods for setting a core mode and allocating
    cores for NPU inference. Supported core modes are single-core, multi-core,
    global4-core, and global8-core. Users can also specify which cores to allocate for
    the model. Additionally, the configuration offers an option to enforce the use of a
    specific NPU bundle.

    @note Deprecated functions are included for backward compatibility, but it is
    recommended to use the newer core mode configuration methods.
    """

    def __init__(self, num_cores: Optional[int] = None):
        """
        @brief Default constructor. This default-constructed object is initially set to
        single-core mode with all NPU local cores included.
        """
        self._model_config = (
            _cMaccel.ModelConfig()
            if num_cores is None
            else _cMaccel.ModelConfig(num_cores)
        )

    def include_all_cores(self) -> bool:
        return self._model_config.include_all_cores()

    def exclude_all_cores(self) -> bool:
        return self._model_config.exclude_all_cores()

    def include(self, cluster: Cluster, core: Optional[Core] = None) -> bool:
        if core is None:
            return self._model_config.include(cluster.value)
        else:
            return self._model_config.include(cluster.value, core.value)

    def exclude(self, cluster: Cluster, core: Optional[Core] = None) -> bool:
        if core is None:
            return self._model_config.exclude(cluster.value)
        else:
            return self._model_config.exclude(cluster.value, core.value)

    def set_single_core_mode(
        self, num_cores: Optional[int] = None, core_ids: Optional[List[CoreId]] = None
    ) -> bool:
        """
        @brief Sets the model to use single-core mode for inference with a specified number
        of local cores.

        In single-core mode, each local core executes model inference independently.
        The number of cores used is specified by the `num_cores` parameter, and the core
        allocation policy is set to `CoreAllocationPolicy.Auto`, meaning the model will be
        automatically allocated to available local cores when the model is launched to the
        NPU, specifically when the `Model.launch()` function is called. Or The user can
        specify a list of CoreIds to determine which cores to use for inference.

        @note Use exactly one of `num_cores` or `core_ids`, not both.

        @param[in] num_cores The number of local cores to use for inference.
        @param[in] core_ids A list of CoreIds to be used for model inference.

        @return True if the mode was successfully set, False otherwise.
        """
        if num_cores is not None and core_ids is None:
            return self._model_config.set_single_core_mode(num_cores)
        elif core_ids is not None and num_cores is None:
            return self._model_config.set_single_core_mode(
                [core_id._core_id for core_id in core_ids]
            )
        raise ValueError(
            "`set_single_core_mode` needs either `num_cores` and `core_ids`."
        )

    def set_global_core_mode(self, clusters: List[Cluster]) -> bool:
        """@deprecated"""
        return self._model_config.set_global_core_mode([c.value for c in clusters])

    def set_global4_core_mode(self, clusters: List[Cluster]) -> bool:
        """
        @brief Sets the model to use global4-core mode for inference with a specified set
        of NPU clusters.

        For Aries NPU, there are two clusters, each consisting of four local cores. In
        global4-core mode, four local cores within the same cluster work together to
        execute the model inference.

        @param[in] clusters A list of clusters to be used for model inference.

        @return True if the mode was successfully set, False otherwise.
        """
        return self._model_config.set_global4_core_mode([c.value for c in clusters])

    def set_global8_core_mode(self) -> bool:
        """
        @brief Sets the model to use global8-core mode for inference.

        For Aries NPU, there are two clusters, each consisting of four local cores. In
        global8-core mode, all eight local cores across the two clusters work together to
        execute the model inference.

        @return True if the mode was successfully set, False otherwise.
        """
        return self._model_config.set_global8_core_mode()

    def get_core_mode(self) -> CoreMode:
        """
        @brief Gets the core mode to be applied to the model.

        This reflects the core mode that will be used when the model is created.

        @return The `CoreMode` to be applied to the model.
        """
        return CoreMode(self._model_config.get_core_mode())

    def set_multi_core_mode(self, clusters: List[Cluster]) -> bool:
        """
        @brief Sets the model to use multi-core mode for batch inference.

        In multi-core mode, on Aries NPU, the four local cores within a cluster work
        together to process batch inference tasks efficiently. This mode is optimized for
        batch processing.

        @param[in] clusters A list of clusters to be used for multi-core batch inference.

        @return True if the mode was successfully set, False otherwise.
        """
        return self._model_config.set_multi_core_mode([c.value for c in clusters])

    def set_auto_mode(self, num_cores: int = 1) -> bool:
        """@deprecated"""
        return self._model_config.set_auto_mode(num_cores)

    def set_manual_mode(self) -> bool:
        """@deprecated"""
        return self._model_config.set_manual_mode()

    def get_core_allocation_policy(self) -> CoreAllocationPolicy:
        """
        @brief Gets the core allocation policy to be applied to the model.

        This reflects the core allocation policy that will be used when the model is
        created.

        @return The `CoreAllocationPolicy` to be applied to the model.
        """
        return CoreAllocationPolicy(self._model_config.get_core_allocation_policy())

    def get_num_cores(self) -> int:
        """
        @brief Gets the number of cores to be allocated for the model.

        This represents the number of cores that will be allocated for inference
        when the model is launched to the NPU.

        @return The number of cores to be allocated for the model.
        """
        return self._model_config.get_num_cores()

    def force_single_npu_bundle(self, npu_bundle_index: int) -> bool:
        """
        @brief Forces the use of a specific NPU bundle.

        This function forces the selection of a specific NPU bundle. If a non-negative
        index is provided, the corresponding NPU bundle is selected and runs without CPU
        offloading. If -1 is provided, all NPU bundles are used with CPU offloading
        enabled.

        @param[in] npu_bundle_index The index of the NPU bundle to force. A non-negative
                                    integer selects a specific NPU bundle (runs without CPU
                                    offloading), or -1 to enable all NPU bundles with CPU
                                    offloading.

        @return True if the index is valid and the NPU bundle is successfully set,
                False if the index is invalid (less than -1).
        """
        return self._model_config.force_single_npu_bundle(npu_bundle_index)

    def get_forced_npu_bundle_index(self) -> bool:
        """
        @brief Retrieves the index of the forced NPU bundle.

        This function returns the index of the NPU bundle that has been forced using the
        `force_single_npu_bundle` function. If no NPU bundle is forced, the returned value
        will be -1.

        @return The index of the forced NPU bundle, or -1 if no bundle is forced.
        """
        return self._model_config.get_forced_npu_bundle_index()

    def set_async_pipeline_enabled(self, enable: bool) -> None:
        """
        @brief Enables or disables the asynchronous pipeline required for asynchronous
            inference.

        Call this function with `enable` set to `True` if you intend to use
        `Model.infer_async()`, as the asynchronous pipeline is necessary for their operation.

        If you are only using synchronous inference, such as `Model.infer()` or
        `Model.infer_to_float()`, it is recommended to keep the asynchronous pipeline disabled
        to avoid unnecessary overhead.

        @param[in] enable Set to `True` to enable the asynchronous pipeline; set to `False`
                        to disable it.
        """
        return self._model_config.set_async_pipeline_enabled(enable)

    def get_async_pipeline_enabled(self) -> bool:
        """
        @brief Returns whether the asynchronous pipeline is enabled in this configuration.

        @return `True` if the asynchronous pipeline is enabled; `False` otherwise.
        """
        return self._model_config.get_async_pipeline_enabled()

    @property
    def schedule_policy(self) -> SchedulePolicy:
        return SchedulePolicy(self._model_config.schedule_policy)

    @property
    def latency_set_policy(self) -> LatencySetPolicy:
        return LatencySetPolicy(self._model_config.latency_set_policy)

    @property
    def maintenance_policy(self) -> MaintenancePolicy:
        return MaintenancePolicy(self._model_config.maintenance_policy)

    @property
    def early_latencies(self) -> List[int]:
        return self._model_config.early_latencies

    @property
    def finish_latencies(self) -> List[int]:
        return self._model_config.finish_latencies

    @schedule_policy.setter
    def schedule_policy(self, policy: SchedulePolicy):
        """@deprecated This setting has no effect."""
        self._model_config.schedule_policy = policy.value

    @latency_set_policy.setter
    def latency_set_policy(self, policy: LatencySetPolicy):
        """@deprecated This setting has no effect."""
        self._model_config.latency_set_policy = policy.value

    @maintenance_policy.setter
    def maintenance_policy(self, policy: MaintenancePolicy):
        """@deprecated This setting has no effect."""
        self._model_config.maintenance_policy = policy.value

    @early_latencies.setter
    def early_latencies(self, latencies: List[int]):
        """@deprecated This setting has no effect."""
        self._model_config.early_latencies = latencies

    @finish_latencies.setter
    def finish_latencies(self, latencies: List[int]):
        """@deprecated This setting has no effect."""
        self._model_config.finish_latencies = latencies

    def get_core_ids(self) -> List[CoreId]:
        """
        @brief Returns the list of NPU CoreIds to be used for model inference.

        This function returns a list of NPU CoreIds that the model will use for
        inference. When `set_single_core_mode(num_cores)` is called and the
        core allocation policy is set to CoreAllocationPolicy.Auto, it will return an
        empty list.

        @return A list of NPU CoreIds.
        """
        return [
            CoreId(Cluster(core_id.cluster), Core(core_id.core))
            for core_id in self._model_config.core_ids
        ]

    def __repr__(self):
        d = {
            "core_mode": self.get_core_mode(),
            "core_allocation_policy": self.get_core_allocation_policy(),
            "core_ids": self.get_core_ids(),
            "num_cores": self.get_num_cores(),
            "forced_npu_bundle_index": self.get_forced_npu_bundle_index(),
        }
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join("{}={}".format(k, v) for k, v in d.items()),
        )


class LogLevel(Enum):
    """@brief LogLevel"""

    DEBUG = _cMaccel.LogLevel.DEBUG
    INFO = _cMaccel.LogLevel.INFO
    WARN = _cMaccel.LogLevel.WARN
    ERR = _cMaccel.LogLevel.ERR
    FATAL = _cMaccel.LogLevel.FATAL
    OFF = _cMaccel.LogLevel.OFF


def set_log_level(level: LogLevel):
    _cMaccel.set_log_level(level.value)


class CacheType(Enum):
    """@brief CacheType"""

    Default = _cMaccel.CacheType.Default
    Batch = _cMaccel.CacheType.Batch
    Error = _cMaccel.CacheType.Error


class CacheInfo:
    """@brief Struct representing KV-cache information."""

    def __init__(
        self,
        cache_type: CacheType = CacheType.Error,
        name: str = "",
        layer_hash: str = "",
        size: int = 0,
        num_batches: int = 0,
    ):
        self._cache_info = _cMaccel.CacheInfo()
        self._cache_info.cache_type = cache_type.value
        self._cache_info.name = name
        self._cache_info.layer_hash = layer_hash
        self._cache_info.size = size
        self._cache_info.num_batches = num_batches

    @classmethod
    def from_cpp(cls, _cache_info: _cMaccel.CacheInfo):
        return cls(
            CacheType(_cache_info.cache_type),
            _cache_info.name,
            _cache_info.layer_hash,
            _cache_info.size,
            _cache_info.num_batches,
        )

    @property
    def cache_type(self) -> CacheType:
        return CacheType(self._cache_info.cache_type)

    @property
    def name(self) -> str:
        return self._cache_info.name

    @property
    def layer_hash(self) -> str:
        return self._cache_info.layer_hash

    @property
    def size(self) -> int:
        return self._cache_info.size

    @property
    def num_batches(self) -> int:
        return self._cache_info.num_batches

    @cache_type.setter
    def cache_type(self, value: CacheType):
        self._cache_info.cache_type = value.value

    @name.setter
    def name(self, value: str):
        self._cache_info.name = value

    @layer_hash.setter
    def layer_hash(self, value: str):
        self._cache_info.layer_hash = value

    @size.setter
    def size(self, value: int):
        self._cache_info.size = value

    @num_batches.setter
    def num_batches(self, value: int):
        self._cache_info.num_batches = value


def start_tracing_events(path: str) -> bool:
    """
    @brief Starts event tracing and prepares to save the trace log to a specified file.

    The trace log is recorded in "Chrome Tracing JSON format," which can be
    viewed at https://ui.perfetto.dev/.

    The trace log is not written immediately; it is saved only when
    stop_tracing_events() is called.

    @param[in] path The file path where the trace log should be stored.
    @return True if tracing starts successfully, False otherwise.
    """
    return _cMaccel.start_tracing_events(path)


def stop_tracing_events():
    """
    @brief Stops event tracing and writes the recorded trace log.

    This function finalizes tracing and saves the collected trace data
    to the file specified when start_tracing_events() was called.
    """
    _cMaccel.stop_tracing_events()


def get_model_summary(mxq_path: str) -> str:
    """
    @brief Generates a structured summary of the specified MXQ model.

    Returns an overview of the model contained in the MXQ file, including:
    - Target NPU hardware
    - Supported core modes and their associated cores
    - The total number of model variants
    - For each variant:
        - Input and output tensor shapes
        - A list of layers with their types, output shapes, and input layer indices

    The summary is returned as a human-readable string in a table and is useful for
    inspecting model compatibility, structure, and input/output shapes.

    @param[in] mxq_path Path to the MXQ model file.
    @return A formatted string containing the model summary.
    """
    return _cMaccel.get_model_summary(mxq_path)


##
# @}

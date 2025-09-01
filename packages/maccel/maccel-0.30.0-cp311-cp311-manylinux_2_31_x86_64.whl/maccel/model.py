##
# \file
#

from typing import List, Optional, Tuple, Union

import numpy as np

import maccel.maccel as _cMaccel
from .accelerator import Accelerator
from .future import *
from .model_variant_handle import *
from .type import *

_Shape = Tuple[int, ...]

__all__ = ["Model", "load"]

##
# \addtogroup PythonAPI
# @{


# input ndarray의 shape이 유효한 shape인지 판별한다.
def _is_valid_shape(input_shape: _Shape, shape: _Shape) -> bool:
    if (len(input_shape) < len(shape)) or (len(input_shape) > len(shape) + 1):
        return False
    # input을 batch일 경우도 고려하여 [h, w, c] 및 [batch, h, w, c] 모두 고려한다
    offset = 1 if len(input_shape) > len(shape) else 0
    for s1, s2 in zip(input_shape[offset:], shape):
        # Dimensions that allow variable lengths are represented by negative values.
        # A variable-length dimension only permits multiples of the original value.
        if s1 % s2 != 0 or (s2 > 0 and s1 != s2):
            return False
    return True


# input ndarray의 shape를 검사하여 HWC인지 CHW인지 판별한다.
def _is_shape_hwc(inputs: List[np.ndarray], shapes: List[_Shape]) -> Optional[bool]:
    if len(inputs) != len(shapes):
        return None

    is_hwc = True
    is_chw = True
    for arr, shape in zip(inputs, shapes):
        shape_hwc = (shape[0], shape[1], shape[2])
        shape_chw = (shape[2], shape[0], shape[1])
        is_hwc = is_hwc and _is_valid_shape(arr.shape, shape_hwc)
        is_chw = is_chw and _is_valid_shape(arr.shape, shape_chw)

    if not is_hwc and not is_chw:
        return None
    # If both `is_hwc` and `is_chw` are `True`, the memory format is assumed to be HWC.
    return is_hwc


# input ndarray에 맞는 model variant index와 shape를 판별한다.
def _find_matching_variant_idx_and_is_hwc(
    model, inputs: List[np.ndarray]
) -> Tuple[int, bool]:
    variant_idx = None
    is_hwc = None
    for i in range(model.get_num_model_variants()):
        is_hwc = _is_shape_hwc(
            inputs, model.get_model_variant_handle(i).get_model_input_shape()
        )
        if is_hwc is not None:
            variant_idx = i
            break

    if is_hwc is None:
        raise ValueError("Input shape is invalid.")
    assert variant_idx is not None
    return variant_idx, is_hwc


# shape에 맞게 numpy ndarray를 생성한다.
def _build_outputs(
    shapes: List[_Shape], is_hwc: bool, dtype: np.dtype
) -> List[np.ndarray]:
    outputs = []
    for shape in shapes:
        if is_hwc:
            shape = (shape[0], shape[1], shape[2])
        else:
            shape = (shape[2], shape[0], shape[1])
        outputs.append(np.empty(shape, dtype=dtype))
    return outputs


# output에 들어있는 numpy ndarray의 shape가 올바른지 검사한다.
def _check_output_shapes(
    outputs: List[np.ndarray], shapes: List[_Shape], is_hwc: bool, dtype: np.dtype
) -> None:
    if len(outputs) != len(shapes):
        raise ValueError("The number of outputs is different.")

    for output, shape in zip(outputs, shapes):
        if output.dtype != dtype:
            raise ValueError("Output dtype mismatch.")

        if is_hwc:
            shape = (shape[0], shape[1], shape[2])
        else:
            shape = (shape[2], shape[0], shape[1])
        if output.shape != shape:
            raise ValueError("Output shape mismatch.")


class Model:
    """
    @brief Represents an AI model loaded from an MXQ file.

    This class loads an AI model from an MXQ file and provides functions to launch it
    on the NPU and perform inference.
    """

    def __init__(self, path: str, model_config: Optional[ModelConfig] = None):
        """
        @brief Creates a Model object from the specified MXQ model file and configuration.

        Parses the MXQ file and constructs a Model object using the provided configuration,
        initializing the model with the given settings.

        @note The created Model object must be launched before performing inference.
              See Model.launch for more details.

        @param[in] path The path to the MXQ model file.
        @param[in] model_config The configuration settings to initialize the Model.
        """
        if model_config is None:
            self._model = _cMaccel.Model(path)
        else:
            self._model = _cMaccel.Model(path, model_config._model_config)

        # 기존 BufferInfo 대신에 ModelShape를 사용한다.
        # Model {input,output} shape는 batch를 포함한 4D이다.
        self._input_shape = self.get_model_input_shape()
        self._output_shape = self.get_model_output_shape()

    def launch(self, acc: Accelerator) -> None:
        """
        @brief Launches the model on the specified Accelerator, which represents
        the actual NPU.

        @param[in] acc The accelerator on which to launch the model.
        """
        self._model.launch(acc._accelerator)
        self._acc = acc

    def dispose(self) -> None:
        """
        @brief Disposes of the model loaded onto the NPU.

        Releases any resources associated with the model on the NPU.
        """
        self._model.dispose()
        self._acc = None

    def is_target(self, core_id: CoreId) -> bool:
        """
        @brief Checks if the NPU core specified by CoreId is the target of the model.
               In other words, whether the model is configured to use the given NPU core.

        @param[in] core_id The CoreId to check.
        @return True if the model is configured to use the specified CoreId, false
        otherwise.
        """
        return self._model.is_target(core_id._core_id)

    def get_core_mode(self) -> CoreMode:
        """
        @brief Retrieves the core mode of the model.

        @return The CoreMode of the model.
        """
        return CoreMode(self._model.get_core_mode())

    def get_target_cores(self) -> List[CoreId]:
        """
        @brief Returns the NPU cores the model is configured to use.

        @return A list of CoreIds representing the target NPU cores.
        """
        return [CoreId.from_cpp(target) for target in self._model.target_cores]

    @property
    def target_cores(self) -> List[CoreId]:
        """@deprecated"""
        return [CoreId.from_cpp(target) for target in self._model.target_cores]

    def infer(
        self,
        inputs: Union[np.ndarray, List[np.ndarray]],
        outputs: Optional[List[np.ndarray]] = None,
        cache_size: int = 0,
    ) -> Optional[List[np.ndarray]]:
        """
        @brief Performs inference.

        Fowllowing types of inference supported.
        1. infer(in:List[numpy]) -> List[numpy]   (float / int)
        2. infer(in:numpy)       -> List[numpy]   (float / int)
        3. infer(in:List[numpy], out:List[numpy]) (float / int)
        4. infer(in:List[numpy], out:List[])      (float / int)
        5. infer(in:numpy, out:List[numpy])       (float / int)
        6. infer(in:numpy, out:List[])            (float / int)

        @param[in] inputs Input data as a single numpy.ndarray or a list
                    of numpy.ndarray's.
        @param[out] outputs Optional pre-allocated list of numpy.ndarray's
                    to store inference results.
        @return Inference results as a list of numpy.ndarray.
        """
        if not isinstance(inputs, list):
            inputs = [inputs]

        variant_idx, is_hwc = _find_matching_variant_idx_and_is_hwc(self, inputs)
        inputs = [np.ascontiguousarray(i) for i in inputs]

        if outputs is None:
            # No Output Parameter
            infer_func = self._model.infer if is_hwc else self._model.infer_chw
            return [np.asarray(o) for o in infer_func(inputs, cache_size)]

        else:
            if outputs:
                _check_output_shapes(
                    outputs,
                    self.get_model_variant_handle(variant_idx).get_model_output_shape(),
                    is_hwc,
                    inputs[0].dtype,
                )
                for oi in range(len(outputs)):
                    outputs[oi] = np.ascontiguousarray(outputs[oi])
            else:
                outputs[:] = _build_outputs(
                    self.get_model_variant_handle(variant_idx).get_model_output_shape(),
                    is_hwc,
                    inputs[0].dtype,
                )

            if is_hwc:
                self._model.infer(inputs, outputs, cache_size)
            else:
                self._model.infer_chw(inputs, outputs, cache_size)

    def infer_to_float(
        self,
        inputs: Union[
            np.ndarray,
            List[np.ndarray],
        ],
        cache_size: int = 0,
    ) -> List[np.ndarray]:
        """
        @brief int8_t-to-float inference
        Performs inference with input and output elements of type `int8_t`

        Using these inference APIs requires manual scaling (quantization)
        of float values to `int8_t` for input.

        @note These APIs are intended for advanced use rather than typical usage.
        """
        if not isinstance(inputs, list):
            inputs = [inputs]

        _, is_hwc = _find_matching_variant_idx_and_is_hwc(self, inputs)
        inputs = [np.ascontiguousarray(i) for i in inputs]

        if is_hwc:
            outputs = self._model.infer_to_float(inputs, cache_size)
        else:
            outputs = self._model.infer_chw_to_float(inputs, cache_size)

        return [np.asarray(o) for o in outputs]

    # For backward compatibility.
    infer_chw = infer
    infer_chw_to_float = infer_to_float

    def infer_buffer(
        self,
        inputs: List[Buffer],
        outputs: List[Buffer],
        shape: List[List[int]] = [],
        cache_size: int = 0,
    ) -> None:
        """
        @brief Buffer-to-Buffer inference

        Performs inference using input and output elements in the NPU’s internal data type.
        The inference operates on buffers allocated via the following APIs:

        - `Model.acquire_input_buffer()`
        - `Model.acquire_output_buffer()`
        - `ModelVariantHandle.acquire_input_buffer()`
        - `ModelVariantHandle.acquire_output_buffer()`

        Additionally, `Model.reposition_inputs()`, `Model.reposition_outputs()`,
        `ModelVariantHandle.reposition_inputs()`, `ModelVariantHandle.reposition_outputs()`
        must be used properly.

        @note These APIs are intended for advanced use rather than typical usage.
        """
        self._model.infer_buffer(
            [i._buffer for i in inputs], [o._buffer for o in outputs], shape, cache_size
        )

    def infer_speedrun(self) -> None:
        """
        @brief Development-only API for measuring pure NPU inference speed.

        Runs NPU inference without uploading inputs and without retrieving outputs.
        """
        self._model.infer_speedrun()

    def infer_async(
        self,
        inputs: Union[np.ndarray, List[np.ndarray]],
    ) -> Future:
        """
        @brief Asynchronous Inference

        Performs inference asynchronously.

        To use asynchronous inference, the model must be created using a `ModelConfig`
        object with the async pipeline configured to be enabled. This is done by calling
        @ref ModelConfig.set_async_pipeline_enabled
        "ModelConfig.set_async_pipeline_enabled(True)" before passing the configuration to
        `Model()`.

        Example:
        @code
        import maccel

        mc = maccel.ModelConfig()
        mc.set_async_pipeline_enabled(True)

        model = maccel.Model(MXQ_PATH, mc)
        acc = maccel.Accelerator()

        model.launch(acc)

        future = model.infer_async(inputs)

        ret = future.get()
        @endcode

        @note Currently, only CNN-based models are supported, as asynchronous execution is
              particularly effective for this type of workload.

        @note Limitations:
               - RNN/LSTM and LLM models are not supported yet.
               - Models requiring CPU offloading are not supported yet.
               - Currently, only single-batch inference is supported (i.e., N = 1).
               - Currently, Buffer inference is not supported. The following types
                 are supported in the synchronous API for advanced use cases, but are not
                 yet available for asynchronous inference:
                  - Buffer to Buffer
                  - Buffer to float
        """
        if not isinstance(inputs, list):
            inputs = [inputs]
        _, is_hwc = _find_matching_variant_idx_and_is_hwc(self, inputs)
        inputs = [np.ascontiguousarray(i) for i in inputs]
        infer_async_func = (
            self._model.infer_async if is_hwc else self._model.infer_async_chw
        )
        return Future.from_cpp(infer_async_func(inputs), inputs)

    def infer_async_to_float(
        self,
        inputs: Union[np.ndarray, List[np.ndarray]],
    ) -> Future:
        """
        @brief This method supports int8_t-to-float asynchronous inference.

        @param[in] inputs Input data as a single numpy.ndarray or a list
                    of numpy.ndarray's.

        @return A future that can be used to retrieve the inference result.
        """
        if not isinstance(inputs, list):
            inputs = [inputs]
        _, is_hwc = _find_matching_variant_idx_and_is_hwc(self, inputs)
        inputs = [np.ascontiguousarray(i) for i in inputs]
        infer_async_func = (
            self._model.infer_async_to_float
            if is_hwc
            else self._model.infer_async_chw_to_float
        )
        return Future.from_cpp(infer_async_func(inputs), inputs)

    def reposition_inputs(
        self,
        inputs: List[np.ndarray],
        input_bufs: List[Buffer],
        seqlens: List[List[int]] = [],
    ) -> None:
        """Reposition input"""
        inputs = [np.ascontiguousarray(i) for i in inputs]
        self._model.reposition_inputs(
            inputs, [buf._buffer for buf in input_bufs], seqlens
        )

    def reposition_outputs(
        self,
        output_bufs: List[Buffer],
        outputs: List[np.ndarray],
        seqlens: List[List[int]] = [],
    ) -> None:
        """Reposition output"""
        if len(outputs) != len(self._output_shape):
            outputs.clear()
            for shape in self._output_shape:
                outputs.append(np.empty(shape=shape, dtype=np.float32))
        else:
            for oi in range(len(outputs)):
                outputs[oi] = np.ascontiguousarray(outputs[oi])
        self._model.reposition_outputs(
            [buf._buffer for buf in output_bufs], outputs, seqlens
        )

    def get_num_model_variants(self) -> int:
        """
        @brief Returns the total number of model variants available in this model.

        The `variant_idx` parameter passed to `Model.get_model_variant_handle()` must be
        in the range [0, return value of this function).

        @return The total number of model variants.
        """
        return self._model.get_num_model_variants()

    def get_model_variant_handle(self, variant_idx) -> ModelVariantHandle:
        """
        @brief Retrieves a handle to the specified model variant.

        Use the returned `ModelVariantHandle` to query details such as input and output
        shapes for the selected variant.

        @param[in] variant_idx Index of the model variant to retrieve.
                               Must be in the range [0, getNumModelVariants()).

        @return A `ModelVariantHandle` object if successful;
                otherwise, raise maccel.MAccelError "Model_InvalidVariantIdx".
        """
        return ModelVariantHandle.from_cpp(
            self._model.get_model_variant_handle(variant_idx)
        )

    def get_model_input_shape(self) -> List[_Shape]:
        """
        @brief Returns the input shape of the model.

        @return A list of input shape of the model.
        """
        return self._model.get_model_input_shape()

    def get_model_output_shape(self) -> List[_Shape]:
        """
        @brief Returns the output shape of the model.

        @return A list of output shape of the model.
        """
        return self._model.get_model_output_shape()

    def get_input_scale(self) -> List[Scale]:
        """
        @brief Returns the input quantization scale(s) of the model.

        @return A list of input scales.
        """
        return [Scale.from_cpp(s) for s in self._model.get_input_scale()]

    def get_output_scale(self) -> List[Scale]:
        """
        @brief Returns the output quantization scale(s) of the model.

        @return A list of output scales.
        """
        return [Scale.from_cpp(s) for s in self._model.get_output_scale()]

    def get_input_buffer_info(self) -> List[BufferInfo]:
        """
        @brief Returns the input buffer information for the model.

        @return A list of input buffer information.
        """
        return [BufferInfo.from_cpp(bi) for bi in self._model.get_input_buffer_info()]

    def get_output_buffer_info(self) -> List[BufferInfo]:
        """
        @brief Returns the output buffer information of the model.

        @return A list of output buffer information.
        """
        return [BufferInfo.from_cpp(bi) for bi in self._model.get_output_buffer_info()]

    def acquire_input_buffer(self, seqlens: List[List[int]] = []) -> List[Buffer]:
        """
        @brief Buffer Management API

        Acquires list of `Buffer` for input.
        These API is required when calling `Model.infer_buffer()`.

        @note These APIs are intended for advanced use rather than typical usage.
        """
        return [Buffer(b) for b in self._model.acquire_input_buffer(seqlens)]

    def acquire_output_buffer(self, seqlens: List[List[int]] = []) -> List[Buffer]:
        """
        @brief Buffer Management API

        Acquires list of `Buffer` for output.
        These API is required when calling `Model.infer_buffer()`.

        @note These APIs are intended for advanced use rather than typical usage.
        """
        return [Buffer(b) for b in self._model.acquire_output_buffer(seqlens)]

    def release_buffer(self, buffer: List[Buffer]) -> None:
        """
        @brief Buffer Management API

        Deallocate acquired Input/Output buffer

        @note These APIs are intended for advanced use rather than typical usage.
        """
        self._model.release_buffer([b._buffer for b in buffer])

    def get_identifier(self) -> int:
        """
        @brief Returns the model's unique identifier.

        This identifier distinguishes multiple models within a single user program.
        It is assigned incrementally, starting from 0 (e.g., 0, 1, 2, 3, ...).

        @return The model identifier.
        """
        return self._model.get_identifier()

    def get_model_path(self) -> str:
        """
        @brief Returns the path to the MXQ model file associated with the Model.

        @return The MXQ file path.
        """
        return self._model.get_model_path()

    def get_cache_infos(self) -> List[CacheInfo]:
        """
        @brief Returns informations of KV-cache of the model.

        @return A list of CacheInfo objects.
        """
        return [CacheInfo.from_cpp(c) for c in self._model.get_cache_infos()]

    def get_schedule_policy(self) -> SchedulePolicy:
        """@deprecated"""
        return SchedulePolicy(self._model.get_schedule_policy())

    def get_latency_set_policy(self) -> LatencySetPolicy:
        """@deprecated"""
        return LatencySetPolicy(self._model.get_latency_set_policy())

    def get_maintenance_policy(self) -> MaintenancePolicy:
        """@deprecated"""
        return MaintenancePolicy(self._model.get_maintenance_policy())

    def get_latency_consumed(self) -> int:
        """@deprecated"""
        return self._model.get_latency_consumed()

    def get_latency_finished(self) -> int:
        """@deprecated"""
        return self._model.get_latency_finished()

    def reset_cache_memory(self) -> None:
        """
        @brief Resets the KV cache memory.

        Clears the stored KV cache, restoring it to its initial state.
        """
        self._model.reset_cache_memory()

    def dump_cache_memory(self) -> List[bytes]:
        """
        @brief Dumps the KV cache memory into buffers.

        Writes the current KV cache data into provided buffers.

        @return A list of bytes containing the KV cache data.
        """
        bufs = self._model.dump_cache_memory()
        return [np.asarray(buf, np.int8).tobytes() for buf in bufs]

    def load_cache_memory(self, bufs: List[bytes]) -> None:
        """
        @brief Loads the KV cache memory from buffers.

        Restores the KV cache from the provided buffers.

        @param[in] bufs A list of bytes containing the KV cache
        """
        self._model.load_cache_memory(
            [np.frombuffer(buf, dtype=np.int8) for buf in bufs]
        )

    def dump_cache_memory_to(self, cache_dir: str) -> None:
        """
        @brief Dumps KV cache memory to files in the specified directory.

        Writes the KV cache data to binary files within the given directory.
        Each file is named using the format: `cache_<layer_hash>.bin`.

        @param[in] cache_dir Path to the directory where KV cache files will be saved.
        """
        self._model.dump_cache_memory(cache_dir)

    def load_cache_memory_from(self, cache_dir: str) -> None:
        """
        @brief Loads the KV cache memory from files in the specified directory.

        Reads KV cache data from files within the given directory and restores them.
        Each file is named using the format: `cache_<layer_hash>.bin`.

        @param[in] cache_dir Path to the directory where KV cache files are saved.
        """
        self._model.load_cache_memory(cache_dir)

    def filter_cache_tail(
        self, cache_size: int, tail_size: int, mask: List[bool]
    ) -> int:
        """
        @brief Filter the tail of the KV cache memory

        Retains the desired caches in the tail of the KV cache memory, excludes the others,
        and shifts the remaining caches forward.

        @param[in] cache_size The number of tokens accumulated in the KV cache so far.
        @param[in] tail_size The tail size of the KV cache to filter (<=32).
        @param[in] mask A mask indicating tokens to retain or exclude at the tail of the KV
                        cache.

        @return New cache size after tail filtering.
        """
        return self._model.filter_cache_tail(cache_size, tail_size, mask)

    def move_cache_tail(self, num_head: int, num_tail: int, cache_size: int) -> int:
        """
        @brief Moves the tail of the KV cache memory to the end of the head.

        Slice the tail of the KV cache memory up to the specified size
        and moves it to the designated cache position.

        @param[in] num_head The size of the KV cache head where the tail is appended.
        @param[in] num_tail The size of the KV cache tail to be moved.
        @param[in] cache_size The total number of tokens accumulated in the KV cache so
                              far.

        @return The updated cache size after moving the tail.
        """
        return self._model.move_cache_tail(num_head, num_tail, cache_size)


def load(path: str, model_config: Optional[ModelConfig] = None) -> Model:
    """
    @brief Single-step inference API. Creates model and uploads the model
    into NPU immediately.

    This operation performs the Accelerator declaration, Model declaration,
    and launch in a single step.
    """
    acc = Accelerator()
    model = Model(path, model_config)
    model.launch(acc)
    return model


##
# @}

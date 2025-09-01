##
# \file
#

from typing import List, Tuple

import maccel.maccel as _cMaccel
from .type import *

_Shape = Tuple[int, ...]

##
# \addtogroup PythonAPI
# @{


class ModelVariantHandle:
    """
    @brief Handle to a specific variant of a loaded model.

    This class provides access to variant-specific information such as input/output
    shapes, buffer information, and quantization scales. It also offers APIs for
    managing inference buffers, consistent with the interface of the `Model` class.

    Objects of this class are obtained via `Model.get_model_variant_handle()`.
    """

    def __init__(self, _model_variant_handle: _cMaccel.ModelVariantHandle):
        self._model_variant_handle = _model_variant_handle
        self._output_shape = self.get_model_output_shape()

    @classmethod
    def from_cpp(cls, _model_variant_handle: _cMaccel.ModelVariantHandle):
        return cls(_model_variant_handle)

    def get_variant_idx(self) -> int:
        """
        @brief Returns the index of this model variant.

        @return Index of the model variant.
        """
        return self._model_variant_handle.get_variant_idx()

    def get_model_input_shape(self) -> List[_Shape]:
        """
        @brief Returns the input shape for this model variant.

        @return model variant's input shape.
        """
        return self._model_variant_handle.get_model_input_shape()

    def get_model_output_shape(self) -> List[_Shape]:
        """
        @brief Returns the output shape for this model variant.

        @return model variant's output shape.
        """
        return self._model_variant_handle.get_model_output_shape()

    def get_input_buffer_info(self) -> List[BufferInfo]:
        """
        @brief Returns the input buffer information for this variant.

        @return A list of input buffer information.
        """
        return [
            BufferInfo.from_cpp(bi)
            for bi in self._model_variant_handle.get_input_buffer_info()
        ]

    def get_output_buffer_info(self) -> List[BufferInfo]:
        """
        @brief Returns the output buffer information for this variant.

        @return A list of output buffer information.
        """
        return [
            BufferInfo.from_cpp(bi)
            for bi in self._model_variant_handle.get_output_buffer_info()
        ]

    def get_input_scale(self) -> List[Scale]:
        """
        @brief Returns the input quantization scale(s) for this variant.

        @return A list of input scales.
        """
        return [Scale.from_cpp(s) for s in self._model_variant_handle.get_input_scale()]

    def get_output_scale(self) -> List[Scale]:
        """
        @brief Returns the output quantization scale(s) for this variant.

        @return A list of output scales.
        """
        return [
            Scale.from_cpp(s) for s in self._model_variant_handle.get_output_scale()
        ]

    def acquire_input_buffer(self, seqlens: List[List[int]] = []) -> List[Buffer]:
        """
        @brief Buffer Management API

        Acquires list of `Buffer` for input.
        These API is required when calling `Model.infer_buffer()`.

        @note These APIs are intended for advanced use and follow the same buffer
              management interface as the `Model` class.
        """
        return [
            Buffer(b) for b in self._model_variant_handle.acquire_input_buffer(seqlens)
        ]

    def acquire_output_buffer(self, seqlens: List[List[int]] = []) -> List[Buffer]:
        """
        @brief Buffer Management API

        Acquires list of `Buffer` for output.
        These API is required when calling `Model.infer_buffer()`.

        @note These APIs are intended for advanced use and follow the same buffer
              management interface as the `Model` class.
        """
        return [
            Buffer(b) for b in self._model_variant_handle.acquire_output_buffer(seqlens)
        ]

    def release_buffer(self, buffer: List[Buffer]) -> None:
        """
        @brief Buffer Management API

        Deallocate acquired Input/Output buffer

        @note These APIs are intended for advanced use and follow the same buffer
              management interface as the `Model` class.
        """
        self._model_variant_handle.release_buffer([b._buffer for b in buffer])

    def reposition_inputs(
        self,
        inputs: List[np.ndarray],
        input_bufs: List[Buffer],
        seqlens: List[List[int]] = [],
    ) -> None:
        """Reposition input"""
        inputs = [np.ascontiguousarray(i) for i in inputs]
        self._model_variant_handle.reposition_inputs(
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
        self._model_variant_handle.reposition_outputs(
            [buf._buffer for buf in output_bufs], outputs, seqlens
        )


##
# @}

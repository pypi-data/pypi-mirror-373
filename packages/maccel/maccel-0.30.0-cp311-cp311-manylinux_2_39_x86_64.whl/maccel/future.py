##
# \file
#

from typing import List, Optional, Union

import numpy as np

import maccel.maccel as _cMaccel

##
# \addtogroup PythonAPI
# @{


class Future:
    """
    @brief Represents a future for retrieving the result of asynchronous inference.

    This class provides a mechanism similar to C++11 std::future, allowing access to
    the result of an asynchronous inference operation initiated via `Model.infer_async()`.
    For details on C++11 std::future, refer to https://en.cppreference.com/w/cpp/thread/future.html .

    The Future object enables the caller to:
    - Wait for the inference to complete (`wait_for`)
    - Block until completion and retrieve the output (`get`)
    """

    def __init__(
        self,
        _future: Optional[Union[_cMaccel.FutureFloat, _cMaccel.FutureInt8]] = None,
        _inputs: Optional[List[np.ndarray]] = None,
    ):
        # If parameters are None, it indicates invalid access.
        # Set FutureFloat by default just to raise error with `get` method.
        self._future = _future if _future is not None else _cMaccel.FutureFloat()
        # self._inputs holds user inputs to prevent them from being garbage collected
        # before asynchronous inference is completed.
        self._inputs = _inputs

    @classmethod
    def from_cpp(
        cls,
        _future: Union[_cMaccel.FutureFloat, _cMaccel.FutureInt8],
        _inputs: List[np.ndarray],
    ):
        return cls(_future, _inputs)

    def wait_for(self, timeout_ms: int) -> bool:
        """
        @brief Waits for asynchronous inference to complete or until the timeout elapses.

        @note This method is safe to call multiple times. Calling it with
              a timeout of zero (i.e., `wait_for(0)`) performs a non-blocking
              check to see whether asynchronous inference has already completed.

        @param[in] timeout_ms Maximum duration to wait, in milliseconds.

        @return True if inference completed before the timeout, false otherwise.
        """
        return self._future.wait_for(timeout_ms)

    def get(self) -> List[np.ndarray]:
        """
        @brief Blocks until asynchronous inference completes and retrieves the output.

        @note This method should be called only once per Future. If called again,
              the return value will be invalid, and it will raise maccel.MAccelError
              "Future_NotValid".

        @return A list of numpy ndarray containing the inference output.
        """
        outputs = self._future.get()
        self._inputs = None
        return [np.asarray(o) for o in outputs]


##
# @}

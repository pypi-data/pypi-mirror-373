##
# \file
#

from typing import List

import maccel.maccel as _cMaccel
from .type import CoreId

__version__: str = _cMaccel.__version__

##
# \addtogroup PythonAPI
# @{


class Accelerator:
    """@brief Represents an accelerator, i.e., an NPU, used for executing models."""

    def __init__(self, dev_no: int = 0):
        """
        @brief Creates an Accelerator object for a specific device number.

        The `dev_no` parameter represents the device number. For example, on Linux,
        if an ARIES NPU is attached as `/dev/aries0`, the device number is `0`.

        @param dev_no The device number to associate with the Accelerator.
        """
        self._accelerator = _cMaccel.Accelerator(dev_no)

    def get_available_cores(self) -> List[CoreId]:
        """
        @brief Retrieves a list of available NPU cores.

        An available core is one that can be allocated for newly created Model objects.

        @note Availability checks are only supported on Linux. On Windows, this function
            returns all NPU cores without checking availability.

        @return A list containing the IDs of available cores.
        """
        return [
            CoreId.from_cpp(core_id)
            for core_id in self._accelerator.get_available_cores()
        ]


##
# @}

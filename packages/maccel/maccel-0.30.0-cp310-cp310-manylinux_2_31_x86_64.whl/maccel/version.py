##
# \file
#

import maccel.maccel as _cMaccel

__all__ = (
    "__version__",
    "__git_version__",
    "__vendor__",
    "__product__",
)

##
# \addtogroup PythonAPI
# @{

__version__: str = _cMaccel.version.__version__
__git_version__: str = _cMaccel.version.__git_version__
__vendor__: str = _cMaccel.version.__vendor__
__product__: str = _cMaccel.version.__product__

##
# @}

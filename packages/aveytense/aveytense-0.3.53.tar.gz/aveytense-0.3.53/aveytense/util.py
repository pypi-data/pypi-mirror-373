"""
**AveyTense Utility Tools** \n
@lifetime >= 0.3.34 \\
© 2025-Present Aveyzan // License: MIT \\
https://aveyzan.xyz/aveytense#aveytense.util    
    
Includes utility tools, including `Final`, `Abstract` and `Frozen` classes, \\
extracted from `aveytense.types_collection`. It formally doesn't use the `aveytense` \\
module.
"""

# standard imports
from __future__ import annotations

from ._ᴧv_collection._util import *
from ._ᴧv_collection._util import __all__, __all_deprecated__

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error
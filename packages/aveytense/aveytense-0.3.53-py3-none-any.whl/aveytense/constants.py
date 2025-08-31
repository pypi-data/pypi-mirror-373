"""
**AveyTense Constants** \n
@lifetime >= 0.3.26rc3 \\
© 2023-Present Aveyzan // License: MIT \\
https://aveyzan.xyz/aveytense#aveytense.constants

Constants wrapper for AveyTense. Extracted from former `tense.tcs` module
"""
from __future__ import annotations
from ._ᴧv_collection._constants import (
    AbroadHexMode as _AbroadHexMode,
    BisectMode as _BisectMode,
    InsortMode as _InsortMode,
    ProbabilityLength as _ProbabilityLength,
    ModeSelection as _ModeSelection
)

#################################### ENUM CONSTANTS ####################################

ABROAD_HEX_INCLUDE = _AbroadHexMode.INCLUDE # 0.3.35
ABROAD_HEX_HASH = _AbroadHexMode.HASH # 0.3.35
ABROAD_HEX_EXCLUDE = _AbroadHexMode.EXCLUDE # 0.3.35

BISECT_LEFT = _BisectMode.LEFT # 0.3.35
BISECT_RIGHT = _BisectMode.RIGHT # 0.3.35

INSORT_LEFT = _InsortMode.LEFT # 0.3.35
INSORT_RIGHT = _InsortMode.RIGHT # 0.3.35

PROBABILITY_MIN = _ProbabilityLength.MIN # 0.3.35
PROBABILITY_MAX = _ProbabilityLength.MAX # 0.3.35
PROBABILITY_COMPUTE = _ProbabilityLength.COMPUTE # 0.3.35
PROBABILITY_DEFAULT = _ProbabilityLength.DEFAULT # 0.3.35

MODE_AND = _ModeSelection.AND # 0.3.36
MODE_OR = _ModeSelection.OR # 0.3.36

STRING_LOWER = "abcdefghijklmnopqrstuvwxyz" # 0.3.36
STRING_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" # 0.3.36
STRING_LETTERS = STRING_LOWER + STRING_UPPER # 0.3.36
STRING_HEXADECIMAL = "0123456789abcdefABCDEF" # 0.3.36
STRING_DIGITS = "0123456789" # 0.3.36
STRING_OCTAL = "01234567" # 0.3.36
STRING_BINARY = "01" # 0.3.36
STRING_SPECIAL = r"""`~!@#$%^&*()-_=+[]{};:'"\|,.<>/?""" # 0.3.36

RGB_MIN = 0 # 0.3.37
RGB_MAX = 2 ** 24 - 1 # 0.3.37

__all__ = [k for k in globals() if not k.startswith("_")]
"""
@lifetime >= 0.3.41
"""
__all_deprecated__ = sorted([n for n in globals() if hasattr(globals()[n], "__deprecated__")])
"""
@lifetime >= 0.3.41

Returns all deprecated declarations within this module.
"""

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error
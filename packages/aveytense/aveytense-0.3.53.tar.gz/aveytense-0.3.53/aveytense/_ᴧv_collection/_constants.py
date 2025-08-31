"""
@lifetime >= 0.3.35 \\
© 2024-Present Aveyzan // License: MIT

Core of `aveytense.constants`; use `aveytense.constants` instead
"""

from __future__ import annotations
from . import _types as __
from platform import architecture as _architecture

class AbroadHexMode(__.Enum):
    "@lifetime >= 0.3.26rc2"
    
    INCLUDE = 0
    HASH = 1
    EXCLUDE = 2

class BisectMode(__.Enum):
    "@lifetime >= 0.3.26rc2"
    
    LEFT = 0
    RIGHT = 1
    
class InsortMode(__.Enum):
    "@lifetime >= 0.3.26rc2"
    
    LEFT = 0
    RIGHT = 1

class ProbabilityLength(__.Enum):
    "@lifetime >= 0.3.26rc2"
    
    COMPUTE = -1
    DEFAULT = 10000
    
    if _architecture()[0] == "64bit":
        MAX = 2 ** 63 - 1 # 9223372036854775807
        
    else:
        MAX = 2 ** 31 - 1 # 2147483647
    
    MIN = 1
    
    
class ModeSelection(__.Enum):
    "@lifetime >= 0.3.36"
    
    AND = 0
    OR = 1
    
if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error
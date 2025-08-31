"""
**AveyTense Operators** \n
@lifetime >= 0.3.27a3 \\
© 2023-Present Aveyzan // License: MIT \\
https://aveyzan.xyz/aveytense#aveytense.operators

Functions handling operations. Extension of standard `operator` library. \\
It does not import anything else, like submodules of AveyTense. Preferred \\
import method: `import aveytense.operators as operators`
"""

from operator import *

# math operations (truediv, floordiv, matmul)
def tdiv(x, y): return x / y
def fdiv(x, y): return x // y
def mmul(x, y): return x @ y

# bitwise
def band(x, y): return x & y
def bor(x, y): return x | y
def bxor(x, y): return x ^ y
def bleft(x, y): return x << y
def bright(x, y): return x >> y

# logical
def isNot(x, y): return x is not y
def isIn(x, y): return x in y # < 0.3.47: in_
def isNotIn(x, y): return x not in y
def land(x, y): return x and y
def lor(x, y): return x or y
def lxor(x, y): return x and not y

# checking
def isNone(x): return x is None
def isNotNone(x): return x is not None
def isEllipsis(x): return x is ...
def isNotEllipsis(x): return x is not ...
def isTrue(x): return x is True
def isFalse(x): return x is False

def setitem(x, y, v): x[y] = v # that's suprisingly something Python missed overall

__all__ = sorted([n for n in globals()])
"\\@since 0.3.27a3. Every declaration in module `aveytense.operators`, including dunder-named ones"

__all_deprecated__ = sorted([n for n in globals() if hasattr(globals()[n], "__deprecated__")])
"""
@since 0.3.41

Returns all deprecated declarations within this module.
"""

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error
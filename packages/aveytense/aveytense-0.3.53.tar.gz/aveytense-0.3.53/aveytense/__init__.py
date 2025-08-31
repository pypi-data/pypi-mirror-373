"""
# AveyTense

@lifetime >= 0.3.24 \\
© 2024-Present Aveyzan // License: MIT \\
https://aveyzan.xyz/aveytense

Multipurpose library with several extensions, including for built-ins.

Submodules:
- `aveytense.exceptions` - exception classes
- `aveytense.types` - types collection
- `aveytense.constants` - constants collection
- `aveytense.operators` - extension of `operator` library
- `aveytense.util` - utility declarations
"""

from __future__ import annotations
import sys as _sys

if hasattr(_sys, "set_int_max_str_digits"): # < 0.3.46: sys.version_info >= (3, 11)
    _sys.set_int_max_str_digits(0) # type: ignore

# 0.3.34: Prevent internal imports and prevent these imported subsequently
import ast as _ast
import bisect as _bisect
import builtins as _builtins
import collections as _collections
import copy as _copy
import dis as _dis
import inspect as _inspect
import io as _io
import itertools as _itertools
import math as _math
import os as _os
import pickle as _pickle
import platform as _platform
import random as _random
import re as _re
import secrets as _secrets
import socket as _socket
import subprocess as _subprocess
import time as _time
import timeit as _timeit
import types as _types
import uuid as _uuid

from ._ᴧv_collection import _abroad as _ab_mod
from ._ᴧv_collection import _constants as _cl
from ._ᴧv_collection._primal import *
from ._ᴧv_collection._util import _InternalHelper, Any as _Any
from ._ᴧv_collection import _version
from . import constants as _cp
from . import exceptions
from . import operators as _op
from . import types # 0.3.41
from . import types as __
from . import util as _util
# from .types_collection import Any as _Any

constants = _cp # 0.3.41
operators = _op # 0.3.41
util = _util # 0.3.41

_E = {
    "string_op_right": "expected a string as a right operand",
    "ls_error": "expected a list or a string",
    "to_list_error": "expected an iterable object or instance of '{}' or '{}'".format(__.ListConvertible.__name__, __.TupleConvertible.__name__)
}

_uni = __.Union
_lit = __.Literal
_opt = __.Optional
_cal = __.AVT_Callable

# local variables (0.3.39)
_MODE_AND = _cp.MODE_AND
_MODE_OR = _cp.MODE_OR
_PROBABILITY_COMPUTE = _cp.PROBABILITY_COMPUTE
_BISECT_LEFT = _cp.BISECT_LEFT
_BISECT_RIGHT = _cp.BISECT_RIGHT
_INSORT_LEFT = _cp.INSORT_LEFT
_INSORT_RIGHT = _cp.INSORT_RIGHT

# public type aliases
if False: # < 0.3.53
    NULL = __.NULL # 0.3.34

# gimmick from enum standard module
Color = RGB = None

# TypeVars, TypeVarTuples, ParamSpecs
_S = __.TypeVar("_S")
_T = __.TypeVar("_T")
_T1 = __.TypeVar("_T1")
_T2 = __.TypeVar("_T2")
_T3 = __.TypeVar("_T3")
_KT = __.TypeVar("_KT")
_KT1 = __.TypeVar("_KT1")
_KT2 = __.TypeVar("_KT2")
_VT = __.TypeVar("_VT")
_VT1 = __.TypeVar("_VT1")
_VT2 = __.TypeVar("_VT2")
_V1 = __.TypeVar("_V1")
_V2 = __.TypeVar("_V2")
_M = __.TypeVar("_M")
_Ts = __.TypeVarTuple("_Ts")
_T_richComparable = __.TypeVar("_T_richComparable", bound = __.RichComparable)
_T_func = __.TypeVar("_T_func", bound = _cal[..., __.Any])
_T_strBytes = __.TypeVar("_T_strBytes", bytes, str) # >= 0.3.42
_T_yield_cov = __.TypeVar("_T_yield_cov", covariant = True) # >= 0.3.53
_T_send_con = __.TypeVar("_T_send_con", contravariant = True, default = None) # >= 0.3.53
_T_return_cov = __.TypeVar("_T_return_cov", covariant = True, default = None) # >= 0.3.53
_T_noneOrEllipsis = __.TypeVar("_T_noneOrEllipsis", None, __.EllipsisType) # >= 0.3.53
_KT_noneOrEllipsis = __.TypeVar("_KT_noneOrEllipsis", None, __.EllipsisType) # >= 0.3.53
_VT_noneOrEllipsis = __.TypeVar("_VT_noneOrEllipsis", None, __.EllipsisType) # >= 0.3.53

# 'types.UnionType' was introduced on Python 3.10.
# For backward-compatibility we need to use 'typing._UnionGenericAlias' before this version.
if _sys.version_info >= (3, 10):
    
    _U = __.TypeVar("_U", bound = __.UnionType)
    _UKT = __.TypeVar("_UKT", bound = __.UnionType)
    _UVT = __.TypeVar("_UVT", bound = __.UnionType)

else:
        
    _U = __.TypeVar("_U", bound = __.TypingUnionType) # type: ignore
    _UKT = __.TypeVar("_UKT", bound = __.TypingUnionType) # type: ignore
    _UVT = __.TypeVar("_UVT", bound = __.TypingUnionType) # type: ignore

# local enums

# class _ColorStyling(_tc.IntegerFlag): ### to 0.3.27
class _ColorStyling(__.Enum):
    """@lifetime >= 0.3.26rc1. Internal class for `%` operator in class `aveytense.Color`."""
    NORMAL = 0
    BOLD = 1
    FAINT = 2
    ITALIC = 3
    UNDERLINE = 4
    SLOW_BLINK = 5
    RAPID_BLINK = 6
    REVERSE = 7
    HIDE = 8
    STRIKE = 9
    # PRIMARY_FONT = 10
    ## 11-19 alternative font
    # GOTHIC = 20
    DOUBLE_UNDERLINE = 21
    # NORMAL_INTENSITY = 22
    # NO_ITALIC = 23
    # NO_UNDERLINE = 24
    # NO_BLINK = 25
    # PROPORTIONAL = 26 # corrected mistake! 0.3.26rc2
    # NO_REVERSE = 27
    # UNHIDE = 28
    # NO_STRIKE = 29
    ## 30-37 foreground color, 3-bit
    # 38 foreground color, 3 4 8 24-bit
    # FOREGROUND_DEFAULT = 39
    ## 40-47 background color, 3-bit
    ## 48 background color, 3 4 8 24-bit
    # BACKGROUND_DEFAULT = 49
    # NO_PROPORTIONAL = 50
    FRAME = 51
    ENCIRCLE = 52
    OVERLINE = 53
    # NO_FRAME = 54 # including "no encircle"
    # NO_OVERLINE = 55
    ## 56 and 57 undefined
    ## 58 underline color, 3 4 8 24-bit
    # UNDERLINE_DEFAULT = 59
    # IDEOGRAM_UNDERLINE = 60
    # IDEOGRAM_DOUBLE_UNDERLINE = 61
    # IDEOGRAM_OVERLINE = 62
    # IDEOGRAM_DOUBLE_OVERLINE = 63
    # IDEOGRAM_STRESS = 64
    # NO_IDEOGRAM = 65
    ## 66-72 undefined
    SUPERSCRIPT = 73
    SUBSCRIPT = 74
    # NO_SUPERSCRIPT = 75 # also counts as no subscript
    ## 76 undefined but recommended value: no subscript
    ## 77-89 undefined
    ## 90-97 bright foreground color, 4-bit
    ## 100-107 bright background color, 4-bit

# class _ColorAdvancedStyling(_tc.IntegerFlag): ### to 0.3.27
class _ColorAdvancedStyling(__.Enum):
    """@lifetime >= 0.3.26rc2. Internal class for `%` operator in class `aveytense.Color`."""
    
    # 2x
    BOLD_ITALIC = 1000
    BOLD_UNDERLINE = 1001
    BOLD_STRIKE = 1002
    BOLD_OVERLINE = 1003
    ITALIC_UNDERLINE = 1004
    ITALIC_STRIKE = 1005
    ITALIC_OVERLINE = 1006
    UNDERLINE_STRIKE = 1007
    UOLINE = 1008
    STRIKE_OVERLINE = 1009
    
    # 3x
    BOLD_ITALIC_UNDERLINE = 1100
    BOLD_ITALIC_STRIKE = 1101
    BOLD_ITALIC_OVERLINE = 1102
    BOLD_UNDERLINE_STRIKE = 1103
    BOLD_UOLINE = 1104
    ITALIC_UNDERLINE_STRIKE = 1105
    ITALIC_UOLINE = 1106
    ITALIC_STRIKE_OVERLINE = 1107
    STRIKE_UOLINE = 1108
    
@__.runtime
class _ClearableAbc(__.Protocol[_T]):
    """
    @since 0.3.42
    
    An internal ABC providing a `clear()` method. Used in `~.Tense.clear()`
    """
    
    def clear() -> _T: ...
    
class AbroadType: 
    """
    @lifetime >= 0.3.52

    Represents type of `abroad()`
    """
    ...

# local type aliases
_Bits = _lit[3, 4, 8, 24]
if _version.VERSION_INFO >= (0, 3, 50) or True:
    _Clearable = _uni[str, Color, _ClearableAbc[_Any], util.MutableString, __.AVT_MutableMapping[_Any, _Any], __.AVT_MutableSequence[_Any], __.AVT_MutableUniqual[_Any], __.IO[_Any], __.FrameType] # 0.3.42
else:
    _Clearable = _uni[str, Color, _ClearableAbc[_Any], util.MutableString, __.AVT_MutableMapping[_Any, _Any], __.AVT_MutableSequence[_Any], __.AVT_MutableUniqual[_Any], __.FrameType] # 0.3.42
_Color = _uni[__.ColorType, RGB]
_Mode = _uni[_cl.ModeSelection, _lit["and", "or"]] # 0.3.36
_Pattern = _uni[_T_strBytes, __.AVT_Pattern[_T_strBytes]] # 0.3.42
_Statement = _uni[_cal[[], object], str]
_Timer = _cal[[], float]
_Target = _uni[str, bytes] # 0.3.42

_AbroadValue1 = _ab_mod.AbroadValue1[_T]
_AbroadValue2 = _ab_mod.AbroadValue2[_T]
_AbroadModifier = _ab_mod.AbroadModifier[_T]
_AbroadPackType = _ab_mod.ReckonType[_T]
_AbroadConvectType = _ab_mod.AbroadConvectType[_T]
_AbroadLiveType = _ab_mod.AbroadLiveType[_T]
AbroadType = _ab_mod.AbroadInitializer # >= 0.3.52
_AbroadVividType = _ab_mod.AbroadVividType[_V1, _V2, _M]
_AbroadEachInitializer = __.AVT_List[_T]
_AbroadMultiInitializer = __.AVT_List[__.AVT_List[int]]

_ColorStylingType = _uni[_ColorStyling, _ColorAdvancedStyling]
_FlagsType = _uni[int, _re.RegexFlag] # reimplement re._FlagsType; 0.3.42
_HasAttrMode = __.Union[_Mode, __.Literal["and-and", "and-or", "or-and", "or-or"]]
_HaveCodeType = _uni[str, bytes, bytearray, __.MethodType, __.FunctionType, __.CodeType, type, __.AnyCallable, None] # from dis.dis()
_ProbabilityLengthType = _uni[int, _lit[_cp.PROBABILITY_COMPUTE]]
        
_ProbabilityType = _uni[
    _T,
    __.AVT_Sequence[_uni[_T, int, __.EllipsisType, None]], # Sequence => _AVT; 0.3.53
    __.AVT_Uniqual[_uni[_T, int, __.EllipsisType, None]], # Uniqual => _AVY; 0.3.53
    __.AVT_Mapping[_T, _uni[int, __.EllipsisType, None]]
] # change 0.3.36, 0.3.46
    
# _ProbabilityTypeTmp = __.Probability__.AVT_Type[_T] # < 0.3.37
# _ProbabilitySeqNoDict = _uni[list, _collections.deque, set, frozenset, tuple] # < 0.3.47
# _ProbabilitySeq = _uni[_ProbabilitySeqNoDict, dict] # 0.3.33; < 0.3.46
_ReckonNGT = _ab_mod.ReckonNGT
_SequenceGeneratorAwaitable = _uni[__.AVT_Sequence[_T], __.AVT_Generator[_T, _Any, _Any], __.AVT_Awaitable[_Any]]

if _sys.version_info >= (3, 10):
    _UnionTypes = (__.TypingUnionType, __.UnionType)
else:
    _UnionTypes = (__.TypingUnionType,)

if _sys.version_info >= (3, 9):
    _GenericTypes = (__.TypingGenericType, __.GenericAlias)
else:
    _GenericTypes = (__.TypingGenericType,)

# This tuple will be used as a type tuple to inspect via isinstance()
# in various functions

# 0.3.35: builtins.type
# 0.3.36: 'types.GenericAlias' and 'types.UnionType'
# 0.3.40: internal class for 'typing.Union' and class 'typing._GenericAlias'
_SupportedTypes = (type, *_GenericTypes, *_UnionTypes)

_Type = type # note for this alias (>= 0.3.35): must be used since it obscures with parameter with exact 'type' built-in name

def _architecture(executable = _sys.executable, bits = "", linkage = ""):
    "@lifetime >= 0.3.26rc2"
    
    return _platform.architecture(executable, bits, linkage)[0]

def _get_all_params(f: _T_func, /):
    
    # if we don't want to use 'inspect' module components, we can use function's __code__ attribute,
    # and access parameters via 'co_varnames' (which also returns tuple of names defined within its body).
    # to return tuple of arguments only, we can use slicing, as co_varnames[:co_argcount + co_kwonlyargcount]
    
    # co_argcount gets amount of non-keyword-only parameters, meanwhile co_kwonlyargcount counts all keyword-only arguments
    # To use in normal code, see ~.util.ParamVar.
    
    # 19.03.2025
    
    return [k for k in f.__code__.co_varnames[:f.__code__.co_argcount + f.__code__.co_kwonlyargcount] if k not in ("self", "return")] # 0.3.42


def _get_all_item_types(i: __.AVT_Iterable[_T], /, distinct = True): # 0.3.51
    
    if not isinstance(i, __.Iterable):
        error = TypeError("expected an iterable")
        raise error
    
    # 0.3.52: Deduce 'typing.Any' from itself and 'StopIteration.value' (type hints 'typing.Any')
    # 0.3.53: The 'distinct' parameter
    
    if distinct:
        return _util.uniquetuple([(
            __.cast(__.AVT_Type[_T], e)
            if type(e) in (__.ProtocolMeta,) else __.cast(__.AVT_Type[_T], _Any)
            if e in (StopIteration.value, _Any) else type(e)
        ) for e in i])
        
    else:
        return tuple([(
            __.cast(__.AVT_Type[_T], e)
            if type(e) in (__.ProtocolMeta,) else __.cast(__.AVT_Type[_T], _Any)
            if e in (StopIteration.value, _Any) else type(e)
        ) for e in i])

##### Functions for Tense.getGeneric() // 0.3.53 #####

# this function may be one day public
def _extract_from_async_iterable(a: __.AVT_AsyncIterable[_T]): # 0.3.53
    
    if not isinstance(a, __.AsyncIterable): 
        error = TypeError("expected an asynchronous iterable")
        raise error
    
    # AsyncIterator and AsyncGenerator have __anext__, but AsyncIterable can access it via __aiter__
    if isinstance(a, __.AsyncIterator): 
        _async_ = a
    else:
        _async_ = a.__aiter__()
    
    import asyncio
    
    # asyncio.run() Py>=3.7
    while True:
        try:
            yield asyncio.run(_async_.__anext__())
        except StopAsyncIteration:
            break
        
# hidden type aliases in _collections_abc.py. these have module name 'builtins' (surprisingly)
def _hidden_collections_abc_def_check(v, t = ""): # 0.3.53
    
    return type(v).__module__ == "builtins" and type(v).__name__ == t

##### END Functions for Tense.getGeneric() #####
    

def _is_hexadecimal(target: str, /):
    _t = target
    
    if target.lower().startswith(("0x", "#")):
        _t = _re.sub(r"^(0[xX]|#)", "", _t)
    
    for c in _t:
        
        if c not in _cp.STRING_HEXADECIMAL:
            return False
        
    return True

def _is_decimal(target: str, /):
    
    for c in target:
        
        if c not in _cp.STRING_DIGITS:
            return False
        
    return True

def _is_octal(target: str, /):
    _t = target
    
    if target.lower().startswith("0o"):
        _t = _re.sub(r"^0[oO]", "", _t)
    
    for c in _t:
        
        if c not in _cp.STRING_OCTAL:
            return False
        
    return True

def _is_binary(target: str, /):
    _t = target
    
    if target.lower().startswith("0b"):
        _t = _re.sub(r"^0[bB]", "", _t)
    
    for c in _t:
        
        if c not in _cp.STRING_BINARY:
            return False
        
    return True

def _is_bool_callback(v: _Any, /) -> __.TypeIs[__.AVT_Callable[[_Any], bool]]:
    
    # Unfortunately, it may not be possible to check if specific function has desired amount of parameters of correct types.
    # Best practice would be checking function annotation and passed types to parameters, so it will work correctly.
    # 02.02.2025
    
    if _version.VERSION_INFO >= (0, 3, 47) or True:
        
        # Fixed on 0.3.51. Perceived emptiness in ~.util.ParamVar.
        # Gimmick on this part is passing empty list and we expect a callable with one parameter only.
        # Verifying the return type is addicted to functions/methods which use this local function.
        # 0.3.53: allow any functions excluding lambda expressions only.
        return callable(v) and v.__code__.co_argcount == 1 and v.__defaults__ is None
    
    else:
        
        return (_inspect.isfunction(v) or callable(v)) and (
            reckon(_inspect.getfullargspec(v).args) == 1 and
            _inspect.getfullargspec(v).varargs is None and
            _inspect.getfullargspec(v).varkw is None and
            reckon(_inspect.getfullargspec(v).kwonlyargs) == 0 and
            _inspect.getfullargspec(v).kwonlydefaults is None and
            reckon(_inspect.getfullargspec(v).annotations) == 0 # yes, we expect a lambda expression
        )

def _int_conversion(target: str, /):
        
    if _is_hexadecimal(target):
        return int(target, 16)
    
    elif _is_decimal(target):
        return int(target, 10)
    
    elif _is_octal(target):
        return int(target, 8)
    
    elif _is_binary(target):
        return int(target, 2)
    
    else:
        return int(target)
    
def _colorize(text: str, bits: _Bits, fg: _uni[int, None], bg: _uni[int, None], /): # 0.3.37 (0.3.37a1)
        
    _s = "\x1b["
    # for e in (self.__fg, self.__bg, self.__un): ### removed 0.3.27
    _msg = {
        3: "for 3-bit colors, expected integer or string value in range 0-7. One of foreground or background values doesn't match this requirement",
        4: "for 4-bit colors, expected integer or string value in range 0-15. One of foreground or background values doesn't match this requirement",
        8: "for 8-bit colors, expected integer or string value in range 0-255. One of foreground or background values doesn't match this requirement",
        24: "for 2-bit colors, expected integer, string, or RGB/CMYK tuple value in range 0-16777215. One of foreground or background values doesn't match this requirement"
    }
    
    for e in (fg, bg):
        
        if e is not None:
            if bits == 3 and e not in abroad(0x8):
                error = ValueError(_msg[3])
                raise error
            
            elif bits == 4 and e not in abroad(0x10):
                error = ValueError(_msg[4])
                raise error
            
            elif bits == 8 and e not in abroad(0x100):
                error = ValueError(_msg[8])
                raise error
        
            elif bits == 24 and e not in abroad(0x1000000):
                error = ValueError(_msg[24])
                raise error
    
    if bits == 3:
        # 2 ** 3 = 8 (0x8 in hex)
        _s += str(30 + fg) + ";" if fg is not None else ""
        _s += str(40 + bg) + ";" if bg is not None else ""
    
    elif bits == 4:
        # 2 ** 4 = 16 (0x10 in hex); WARNING: bright colors notation isn't official
        _s += str(30 + fg) + ";" if fg is not None and fg in abroad(0x8) else ""
        _s += str(40 + bg) + ";" if bg is not None and bg in abroad(0x8) else ""
        _s += str(90 + fg) + ";" if fg is not None and fg in abroad(0x8, 0x10) else ""
        _s += str(100 + bg) + ";" if bg is not None and bg in abroad(0x8, 0x10) else ""
    
    elif bits == 8:
        # 2 ** 8 = 256 (0x100 in hex)
        _s += "38;5;" + str(fg) + ";" if fg is not None else ""
        _s += "48;5;" + str(bg) + ";" if bg is not None else ""
    
    elif bits == 24:
        # 2 ** 24 = 16777216 (0x1000000 in hex)
        # code reconstructed on 0.3.26rc2
        # acknowledgements: equivalent to rgb
        _f = hex(fg) if fg is not None else ""
        _b = hex(bg) if bg is not None else ""
        _f = _re.sub(r"^(0x|#)", "", _f) if reckon(_f) > 0 else ""
        _b = _re.sub(r"^(0x|#)", "", _b) if reckon(_b) > 0 else ""
        _hf, _hb = [None, None]
        for s in (_f, _b):
            
            if reckon(s) == 6:
                if s == _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                # else:
                #    _hu = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2)) ### removed 0.3.27
                
            elif reckon(s) == 5:
                s = "0" + s
                if s == "0" + _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                
            elif reckon(s) == 4:
                s = "00" + s
                if s == "00" + _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                
            elif reckon(s) == 3:
                _tmp = "".join(s[i] * 2 for i in abroad(s)) # aliased according to css hex fff notation
                if s == _f:
                    s = _tmp
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    s = _tmp
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                
            elif reckon(s) == 2:
                s = "0000" + s
                if s == "0000" + _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                
            elif reckon(s) == 1:
                s = "00000" + s
                if s == "00000" + _f:
                    _hf = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
                else:
                    _hb = tuple(int(s[i : i + 2], 16) for i in abroad(0, 5, 2))
        
        _s += "38;2;" + str(_hf[0]) + ";" + str(_hf[1]) + ";" + str(_hf[2]) + ";" if _hf is not None else ""
        _s += "48;2;" + str(_hb[0]) + ";" + str(_hb[1]) + ";" + str(_hb[2]) + ";" if _hb is not None else ""
    else:
        error = ValueError("internal 'bits' variable value is not one from following: 3, 4, 8, 24")
        raise error
    
    if _s != "\033[":
        _s = _re.sub(r";$", "m", _s)
        _s += text + "\033[0m"
    else:
        _s = text
    return _s

# This function can sometimes hint 'typing.Any' as the return annotation, but in reality it will always return
# a boolean value. Keep that on mind!
def _is_sequence_helper(v, /, type = ()): # 0.3.36
    
    # START 0.3.35
    
    _v = list(v) if not isinstance(v, list) else v
    
    if reckon(_v) == 0:
        
        # Since 'typing.Any' cannot be used with isinstance(), as it throws an error (but it should normally return 'True'),
        # the only way to determine if we are dealing with 'typing.Any' is inspecting variable with the 'is' keyword
        if type is _Any:
            return True
        
        return False
    
    # END 0.3.35
    
    # 0.3.53: bit with 'None' and 'Ellipsis'
    if not isinstance(type, (tuple, *_SupportedTypes)) and type not in (None, Ellipsis):
        error = TypeError("passed value to parameter '{}' must be a type, tuple of types, union or generic type".format("type"))
        raise error
        
    _placeholder = True
    
    # 0.3.52: Code revamp
    if isinstance(type, _GenericTypes):
        
        # E.g. begin with '<seqCheckFunc>(v, <generic alias>)' as '<seqCheckFunc>(v, list[int])', then we want 'v'
        # to be duo-dimensional list with internal list being integers only
        for e in _v:
            # Notice if the item isn't iterable, then __args__ isn't used, it is simply considered as inspecting only
            # origin of generic alias instead. Reason of this behavior comes from fact that there are many various ways
            # to retrieve type arguments from a generic alias, especially from concrete attributes
            if _placeholder:
                _placeholder = _placeholder and isinstance(e, type.__origin__)
                if isinstance(e, __.Iterable) and issubclass(type.__origin__, __.Iterable):
                    if _Any in type.__args__:
                        return True
                    for e2 in e:
                        _placeholder = _placeholder and isinstance(e2, type.__args__)
            else:
                break
    
    elif isinstance(type, (_UnionTypes, tuple)):
        
        # Flattening union types within a tuple is currently rethought, you should use either types in
        # a tuple or union type before this solution will be ever implemented
        if isinstance(type, _UnionTypes):
            _unique_ = _util.uniquetuple(type.__args__)
        else:
            if reckon(type) == 0: # behavior for '<seqCheckFunc>(v, ())' from 0.3.35
                return True
            
            _unique_ = _util.uniquetuple(type)
            
            for e in _unique_:
                # 0.3.53: bit with 'None' and 'Ellipsis'
                if not isinstance(e, (_Type, __.NoneType, __.EllipsisType)):
                    error = TypeError("expected only types, 'None' or ellipsis in the tuple") 
                    raise error
            
        _exclude_generics_ = tuple([e for e in _unique_ if not isinstance(e, _GenericTypes) and e not in (None, Ellipsis)])
        _generics_ = tuple([e for e in _unique_ if isinstance(e, _GenericTypes)])
        
        # 0.3.52: 'typing.Any' is not a generic type. once 'typing.Any' is found, always return 'True'
        if _Any in _exclude_generics_: 
            return True
        
        for e in _v:
            if _placeholder:
                # 0.3.53: bit with 'None' and 'Ellipsis'
                if None not in _unique_ and Ellipsis not in _unique_:
                    _placeholder = _placeholder and isinstance(e, _exclude_generics_)
                else:
                    _placeholder = _placeholder and e in (None, Ellipsis)
                # end 0.3.53
                for e2 in _generics_:
                    if isinstance(e, __.Iterable) and issubclass(e2.__origin__, __.Iterable):
                        _placeholder = _placeholder and isinstance(e, e2.__origin__)
                        for e3 in e:
                            _placeholder = _placeholder and isinstance(e3, e2.__args__)
                    else:
                        break
            else:
                break
                
    else:
        
        if type is _Any: # behavior for '<seqCheckFunc>(v, typing.Any)' from 0.3.35
            return True
        
        # Alternatively, it would be 'return all([isinstance(e, type) for e in _v])',
        # but 'for' loop will not stop even if 'False' dropped in at least one iteration
        # from isinstance(). That would decrease performance, and a little greater execution time.
        for e in _v:
            if _placeholder:
                # 0.3.53: bit with 'None' and 'Ellipsis'
                _placeholder = _placeholder and isinstance(e, (_Type(type) if type in (None, Ellipsis) else type))
            else:
                break
        
    return _placeholder

def _inspect_many(*v, type = _Any, mode: _Mode = _MODE_AND): # 0.3.36
    
    if reckon(v) == 0:
        return False
    
    else:
        
        _placeholder = True
        
        for e in v:
            
            try:
                
                if type is not None:
                    
                    if mode in (_MODE_AND, "and"):
                        _placeholder = _placeholder and isinstance(e, type)
                        
                    elif mode in (_MODE_OR, "or"):
                        _placeholder = _placeholder or isinstance(e, type)
                        
                    else:
                        return False
                    
                else:
                    
                    if mode in (_MODE_AND, "and"):
                        _placeholder = _placeholder and e is None
                        
                    elif mode in (_MODE_OR, "or"):
                        _placeholder = _placeholder or e is None
                        
                    else:
                        return False
            
            except:
                
                if mode in (_MODE_AND, "and"):
                    _placeholder = _placeholder and _Type(e) is type
                    
                elif mode in (_MODE_OR, "or"):
                    _placeholder = _placeholder or _Type(e) is type
                    
                else:
                    return False
                    
        return _placeholder
    
    
def _inspect_numerics(*v, mode = "b", lmode: _Mode = _MODE_AND): # 0.3.38
    
    if reckon(v) == 0:
        return False
    
    else:
        
        _placeholder = True
        
        for e in v:
            
            if lmode in (_MODE_AND, "and"):
                
                if mode == "b":
                    _placeholder = _placeholder and (type(e) is str and _is_binary(e))
                    
                elif mode == "o":
                    _placeholder = _placeholder and (type(e) is str and _is_octal(e))
                    
                elif mode == "d":
                    _placeholder = _placeholder and (type(e) is str and _is_decimal(e))
                    
                elif mode == "h":
                    _placeholder = _placeholder and (type(e) is str and _is_hexadecimal(e))
                    
                else:
                    return False
                
            elif lmode in (_MODE_OR, "or"):
                
                if mode == "b":
                    _placeholder = _placeholder or (type(e) is str and _is_binary(e))
                    
                elif mode == "o":
                    _placeholder = _placeholder or (type(e) is str and _is_octal(e))
                    
                elif mode == "d":
                    _placeholder = _placeholder or (type(e) is str and _is_decimal(e))
                    
                elif mode == "h":
                    _placeholder = _placeholder or (type(e) is str and _is_hexadecimal(e))
                    
                else:
                    return False
                
            else:
                return False
            
        return _placeholder

@__.deprecated("Deprecated since 0.3.50 and may be removed in the future")
class TenseOptions(_util.AbstractFinal): # 0.3.27a5
    """
    @lifetime >= 0.3.27a5 \\
    https://aveyzan.xyz/aveytense#aveytense.TenseOptions
    
    Several settings holder class. Cannot be initialized nor subclassed.
    """
    
    if _version.VERSION_INFO < (0, 3, 40) and False:
        
        initializationMessage = False
        """
        @lifetime >= 0.3.27a5; < 0.3.40 \\
        https://aveyzan.xyz/aveytense#aveytense.TenseOptions
        
        Toggle on/off initialization message in the terminal
        """
    
    insertionMessage = False
    """
    @lifetime >= 0.3.27b1 https://aveyzan.xyz/aveytense#aveytense.TenseOptions
    
    Toggle on/off insertion messages (these displayed by `Tense.print()`). \\
    If this option was `False`, invoked is mere `print()` method. This option \\
    has also influence on `Fencord` solutions.
    """
    if False: # < 0.3.49
        
        probabilityExtendedLength = False
        """
        @lifetime >= 0.3.27rc1. Toggle on/off extended length via 2d list technique. Once it is toggled off, \\
        error will be thrown if going above `sys.maxsize`, `(sys.maxsize + 1) ** 2 - 1` otherwise.
        """
    
    if False: # < 0.3.46
        
        disableProbability2LengthLimit = False
        """
        @lifetime >= 0.3.31; < 0.3.46 \\
        https://aveyzan.xyz/aveytense#aveytense.TenseOptions
        
        Switch on/off length limit, which bases on `sys.maxsize`. If that option was enabled, length passed \\
        to `Tense.probability2()` class method will no longer throw an error whether length is greater than \\
        `sys.maxsize`. This also prevents creating a temporary list to generate the result via this method. It will \\
        not work on extended variation of this method, `Tense.probability()`, unless there were exactly 2 \\
        integer values passed. Its default value is `False`.
        
        Deprecated since 0.3.46 and up for removal in version 0.3.48. Reason it is deprecated is because in 0.3.46, \\
        `sys.maxsize` limit has been completely excised.
        """


if _version.VERSION_INFO < (0, 3, 40) and False:
    
    class FencordOptions(_util.AbstractFinal): # 0.3.27b1
        """
        @lifetime >= 0.3.27b1
        
        Several settings holder class. Cannot be initialized nor subclassed.
        """
        
        initializationMessage = False
        "@lifetime >= 0.3.27b1. Toggle on/off initialization message in the terminal"

if False: # 0.3.43
    _util.finalpropertydec(
        _static_ = True,
        none = None,
        constants = _cp,
        operators = _op,
        types_collection = __,
        util = _util,
        version = _cp.VERSION,
        versionInfo = _cp.VERSION_INFO,
        AND = _MODE_AND,
        OR = _MODE_OR,
        PROBABILITY_COMPUTE = _PROBABILITY_COMPUTE,
        BISECT_LEFT = _BISECT_LEFT,
        BISECT_RIGHT = _BISECT_RIGHT,
        INSORT_LEFT = _INSORT_LEFT,
        INSORT_RIGHT = _INSORT_RIGHT,
        ABROAD_HEX_INCLUDE = _cp.ABROAD_HEX_INCLUDE,
        ABROAD_HEX_HASH = _cp.ABROAD_HEX_HASH,
        ABROAD_HEX_EXCLUDE = _cp.ABROAD_HEX_EXCLUDE
    )

class Tense( # 0.3.24
    
    # NennaiAbroads, ### < 0.3.34
    # NennaiStringz, ### < 0.3.27
    # NennaiRandomize, ### < 0.3.34
    Time,
    Math,
    # _tc.Positive[str], ### < 0.3.34
    # _tc.Negative[str], ### < 0.3.34
    # _tc.Invertible[str], ### < 0.3.34
    
):
    """
    @lifetime >= 0.3.24 \\
    @standard-lifetime >= 0.3.24 \\
    https://aveyzan.xyz/aveytense#aveytense.Tense
    
    Root of AveyTense. Subclassing since 0.3.26b3
    """
    
    constants = _cp # 0.3.39
    exceptions = exceptions # 0.3.44
    operators = _op # 0.3.42
    types_collection = __ # 0.3.42
    util = _util # 0.3.42
    
    version = _version.VERSION
    versionInfo = _version.VERSION_INFO
    
    AND = _MODE_AND
    "@lifetime >= 0.3.36"
    
    OR = _MODE_OR
    "@lifetime >= 0.3.36"
    
    PROBABILITY_COMPUTE = _PROBABILITY_COMPUTE
    "@lifetime >= 0.3.26rc2"
    
    BISECT_LEFT = _BISECT_LEFT
    "@lifetime >= 0.3.26rc2"
    
    BISECT_RIGHT = _BISECT_RIGHT
    "@lifetime >= 0.3.26rc2"
    
    INSORT_LEFT = _INSORT_LEFT
    "@lifetime >= 0.3.26rc2"
    
    INSORT_RIGHT = _INSORT_RIGHT
    "@lifetime >= 0.3.26rc2"
    
    if versionInfo < (0, 3, 42) and False:
        
        TIMEIT_TIMER_DEFAULT = _time.perf_counter
        "@lifetime >= 0.3.26rc3"
        
        TIMEIT_NUMBER_DEFAULT = _cp.MATH_MILLION
        "@lifetime >= 0.3.26rc3"
    
    streamLikeC = False
    "@lifetime >= 0.3.27a5. If set to `True`, output becomes `<<` and input - `>>`, vice versa otherwise"
    
    streamInputPrompt = ""
    "@lifetime >= 0.3.27a5. Prompt for `input()` via `>>` and `<<` operators, depending on value of setting `streamLikeC`"
    
    streamInputResult = ""
    "@lifetime >= 0.3.27b1. Result from `>>` or `<<`, depending on which one of them is for input"
    
    
    if versionInfo < (0, 3, 40) and False:
        
        def __init__(self):
            
            if TenseOptions.initializationMessage:
                print("\33[1;90m{}\33[1;36m INITIALIZATION\33[0m Class '{}' was successfully initalized. Line {}".format(
                    super().fencordFormat(), type(self).__name__, self.__frame
                ))
    
    else:
        
        def __init__(self): # 0.3.40
            
            _tmp = _inspect.currentframe().f_back.f_lineno
            self.__frame = _tmp if type(_tmp) is int else -1
            
    def __str__(self): # 0.3.40
        return "<{}.{} object :: Tense()>".format(self.__module__, type(self).__name__)
        
    def __repr__(self): # 0.3.40
        return "<{} defined in line {}>".format(self.__str__(), self.__frame)
    
    def __lshift__(self, other: object):
        "@lifetime >= 0.3.27a5. A C-like I/O printing"
        
        if self.streamLikeC:
            self.print(other)
            
        else:
            if self.isString(other):
                self.streamInputResult = input(self.streamInputPrompt)
                
            else:
                error = TypeError(_E["string_op_right"])
                raise error
            
        return self
    
    def __rshift__(self, other: object):
        "@lifetime >= 0.3.27a5. A C-like I/O printing"
        
        if not self.streamLikeC:
            self.print(other)
            
        else:
            if self.isString(other):
                self.streamInputResult = input(self.streamInputPrompt)
            else:
                error = TypeError(_E["string_op_right"])
                raise error
            
        return self
    
    if versionInfo >= (0, 3, 43) and versionInfo < (0, 3, 45) and False:
        
        none = None
        """@since 0.3.32"""
        
    else:
    
        @_util.finalproperty
        def none(self):
            """
            @lifetime >= 0.3.32
            
            This property is console-specific, and simply returns `None`.
            """
            return None
    
    ABROAD_HEX_INCLUDE = _cp.ABROAD_HEX_INCLUDE
    "@lifetime >= 0.3.26rc2"
    
    ABROAD_HEX_HASH = _cp.ABROAD_HEX_HASH
    "@lifetime >= 0.3.26rc2"
    
    ABROAD_HEX_EXCLUDE = _cp.ABROAD_HEX_EXCLUDE
    "@lifetime >= 0.3.26rc2"
    
    @classmethod
    def toList(self, v: __.Union[__.AVT_Iterable[_T], __.ListConvertible[_T], __.TupleConvertible[_T]], /):
        """
        @lifetime >= 0.3.26rc3
        
        Converts a value to a `list` built-in.
        """
        
        if isinstance(v, __.ListConvertible):
            return v.__tlist__()
        
        elif isinstance(v, __.TupleConvertible):
            return list(v.__ttuple__())
        
        elif isinstance(v, __.Iterable):
            return list(v)
        
        else:
            error = TypeError(_E["to_list_error"])
            raise error
    
    @classmethod
    def toString(self, v: _Any = ..., /):
        """
        @lifetime >= 0.3.26rc3
        
        Alias to `Tense.toStr()`, `str()`

        Converts a value to a `str` built-in.
        """
        return str(v)
    
    @classmethod
    def toStr(self, v: _Any = ..., /):
        """
        @lifetime >= 0.3.26rc3
        
        Converts a value to a `str` built-in.
        """
        return str(v)
    
    @classmethod
    @__.overload
    def isAbroad(self, v: _Any, /) -> __.TypeIs[_ab_mod.AbroadInitializer]: ...
    
    @classmethod
    @__.overload
    def isAbroad(self, v: _Any, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isAbroad(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.50
        
        Determine whether passed object is instance of internal class returned \\
        by function `~.abroad()`.
        """
        
        _many = (v,) + _
        return _inspect_many(*_many, type = _ab_mod.AbroadInitializer, mode = mode)
    
    @classmethod
    @__.overload
    def isNone(self, v: _Any, /) -> __.TypeIs[None]: ...
    
    @classmethod
    @__.overload
    def isNone(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isNone(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26b3 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isNone
        
        Determine whether a value is `None`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = None, mode = mode)
    
    @classmethod
    @__.overload
    def isEllipsis(self, v: _Any, /) -> __.TypeIs[__.EllipsisType]: ...
    
    @classmethod
    @__.overload
    def isEllipsis(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isEllipsis(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isEllipsis
        
        Determine whether a value is `...`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = __.EllipsisType, mode = mode)
    
    @classmethod
    @__.overload
    def isBool(self, v: _Any, /) -> __.TypeIs[bool]: ...
    
    @classmethod
    @__.overload
    def isBool(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isBool(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26b3 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isBoolean
        
        Determine whether a value is of type `bool`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = bool, mode = mode)
    
    @classmethod
    @__.overload
    def isBoolean(self, v: _Any, /) -> __.TypeIs[bool]: ...
    
    @classmethod
    @__.overload
    def isBoolean(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isBoolean(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26rc1 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isBoolean
        
        Alias to `Tense.isBool()`

        Determine whether a value is of type `bool`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = bool, mode = mode)
    
    @classmethod
    @__.overload
    def isInt(self, v: _Any, /) -> __.TypeIs[int]: ...
    
    @classmethod
    @__.overload
    def isInt(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isInt(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26b3 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isInteger
        
        Determine whether a value is of type `int`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = int, mode = mode)
    
    @classmethod
    @__.overload
    def isInteger(self, v: _Any, /) -> __.TypeIs[int]: ...
    
    @classmethod
    @__.overload
    def isInteger(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isInteger(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26rc1 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isInteger
        
        Alias to `Tense.isInt()`

        Determine whether a value is of type `int`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = int, mode = mode)
    
    @classmethod
    @__.overload
    def isFloat(self, v: _Any, /) -> __.TypeIs[float]: ...
    
    @classmethod
    @__.overload
    def isFloat(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isFloat(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26b3 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isFloat
        
        Determine whether a value is of type `float`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = float, mode = mode)
    
    @classmethod
    @__.overload
    def isComplex(self, v: _Any, /) -> __.TypeIs[complex]: ...
    
    @classmethod
    @__.overload
    def isComplex(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isComplex(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26b3 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isComplex
        
        Determine whether a value is of type `complex`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = complex, mode = mode)
    
    @classmethod
    @__.overload
    def isStr(self, v: _Any, /) -> __.TypeIs[str]: ...
    
    @classmethod
    @__.overload
    def isStr(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isStr(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26b3 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isString
        
        Determine whether a value is of type `str`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = str, mode = mode)
    
    @classmethod
    @__.overload
    def isString(self, v: _Any, /) -> __.TypeIs[str]: ...
    
    @classmethod
    @__.overload
    def isString(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isString(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.26rc1 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isString
        
        Alias to `Tense.isStr()`

        Determine whether a value is of type `str`
        
        - 0.3.36: Many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = str, mode = mode)
    
    # CHANGEOVER 0.3.34
    if versionInfo < (0, 3, 34) and False:
        
        @classmethod
        @__.overload
        def isTuple(self, v: _Any, type: __.AVT_Type[_T] = _Any, /) -> __.TypeIs[__.AVT_Tuple[_T, ...]]:
            """
            @lifetime >= 0.3.26rc1
            
            Determine whether a value is a tuple.
            
            - 0.3.34: Added new parameters `type` and `types`
            """
            ...
        
        # this overload is experimental to be finished
        @classmethod
        @__.overload
        @__.deprecated("The overload is experimental, use the other overload, without 'types' parameter (the overload is not actually deprecated)")
        def isTuple(self, v: _Any, type: __.AVT_Type[_T], /, *types: __.Unpack[_Ts]) -> __.TypeIs[__.AVT_Tuple[_T, __.Unpack[_Ts]]]:
            """
            @lifetime >= 0.3.26rc1
            
            Determine whether a value is a tuple. Experimental due to unexpected `False` when passing more than \\
            one type.
            
            - 0.3.34: Added new parameters `type` and `types`
            """
            ...
    
        @classmethod
        def isTuple(self, v, type = _Any, /, *types):
            """
            @lifetime >= 0.3.26rc1
            ```ts
            "class method" in class Tense
            ```
            Determine whether a value is of type `tuple`
            """
            
            if _Type(v) is tuple:
                
                _placeholder = True
                
                if reckon(types) == 0:
                    
                    if reckon(v) == 0:
                        
                        if type is _Any:
                            return True
                        
                        return False
                    
                    if not isinstance(type, _Type):
                        error = TypeError("passed value to parameter '{}' must be a type, not an object".format("type"))
                        raise error
                    
                    if type is _Any:
                        return True
                    
                    for e in v:
                        
                        try:
                            _placeholder = _placeholder and isinstance(e, type)
                            
                        except:
                            _placeholder = _placeholder and _Type(e) is type
                
                    return _placeholder
                
                if reckon(v) != reckon(types) - 1: # minus one due to 'type' parameter
                    return False
                
                if type is _Any:
                    pass
                
                else:
                    
                    try:
                        _placeholder = _placeholder and isinstance(v[0], type)
                        
                    except:
                        _placeholder = _placeholder and _Type(v[0]) is type
                
                _types_any_check = True
                
                for i in abroad(types):
                    _types_any_check = _types_any_check and types[i] is _Any
                    
                if _types_any_check and type is _Any:
                    return True
                
                for i in abroad(1, types):
                    
                    try:
                        _placeholder = _placeholder and isinstance(v[i], types[i - 1])
                        
                    except:
                        _placeholder = _placeholder and _Type(v[i]) is types[i - 1]
                    
                return _placeholder
                
            else:
                return False
            
    else:
        
        @classmethod
        @__.overload
        def isTuple(self, v: _Any, /, type: __.AVT_Type[_T] = _Any) -> __.TypeIs[__.AVT_Tuple[_T, ...]]: ...
        
        @classmethod
        @__.overload
        def isTuple(self, v: _Any, /, type: __.AVT_Tuple[__.AVT_Type[_T], ...]) -> __.TypeIs[__.AVT_Tuple[_T, ...]]: ...
        
        @classmethod
        @__.overload
        def isTuple(self, v: _Any, /, type: _U) -> __.TypeIs[__.AVT_Tuple[_U, ...]]: ...
        
        @classmethod
        def isTuple(self, v, /, type = _Any):
            """
            @lifetime >= 0.3.26rc1 \\
            https://aveyzan.xyz/aveytense#aveytense.Tense.isTuple
            
            Determine whether a value is a tuple built-in.
            
            - 0.3.34: Added new parameter `type`, allowing to restrict the tuple type. Default value is `Any`.
            
            - 0.3.35: Overload; `type` now can be a tuple of types, code will count them as union type to match against. \\
            Hence the experiments concerning `types` parameter are over (parameter isn't included).
            
            - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
            """
            if _Type(v) is tuple:
                return _is_sequence_helper(v, type = type)
            
            else:
                return False
    
    @classmethod
    @__.overload
    def isTuple2(self, v1: __.AVT_Tuple[_Any, ...], v2: __.AVT_Tuple[__.AVT_Type[_T], ...], /) -> __.TypeIs[__.AVT_Tuple[_T, ...]]: ...
    
    @classmethod
    @__.overload
    def isTuple2(self, v1: __.AVT_Tuple[_Any, ...], v2: __.AVT_Tuple[__.AVT_Tuple[__.AVT_Type[_T], ...], ...], /) -> __.TypeIs[__.AVT_Tuple[_T, ...]]: ...
    
    @classmethod
    @__.overload
    def isTuple2(self, v1: __.AVT_Tuple[_Any, ...], v2: __.AVT_Tuple[__.Union[__.AVT_Type[_T], __.AVT_Tuple[__.AVT_Type[_T], ...]], ...], /) -> __.TypeIs[__.AVT_Tuple[_T, ...]]: ...
    
    @classmethod
    @__.overload
    def isTuple2(self, v1: __.AVT_Tuple[_Any, ...], v2: __.AVT_Tuple[_U, ...], /) -> __.TypeIs[__.AVT_Tuple[_U, ...]]: ...
    
    @classmethod
    @__.overload
    def isTuple2(self, v1: __.AVT_Tuple[_Any, ...], v2: __.AVT_Tuple[__.AVT_Tuple[_U, ...], ...], /) -> __.TypeIs[__.AVT_Tuple[_U, ...]]: ...
    
    @classmethod
    @__.overload
    def isTuple2(self, v1: __.AVT_Tuple[_Any, ...], v2: __.AVT_Tuple[__.Union[__.AVT_Type[_T], __.AVT_Tuple[_U, ...]], ...], /) -> __.TypeIs[__.AVT_Tuple[__.Union[_T, _U], ...]]: ...
    
    @classmethod
    @__.overload
    def isTuple2(self, v1: __.AVT_Tuple[_Any, ...], v2: __.AVT_Tuple[__.Union[__.AVT_Tuple[__.AVT_Type[_T], ...], __.AVT_Tuple[_U, ...]], ...], /) -> __.TypeIs[__.AVT_Tuple[__.Union[_T, _U], ...]]: ...
    
    @classmethod
    @__.overload
    def isTuple2(self, v1: __.AVT_Tuple[_Any, ...], v2: __.AVT_Tuple[__.Union[__.AVT_Type[_T], __.AVT_Tuple[__.AVT_Type[_T], ...], __.AVT_Tuple[_U, ...]], ...], /) -> __.TypeIs[__.AVT_Tuple[__.Union[_T, _U], ...]]: ...
    
    @classmethod
    @__.overload
    def isTuple2(self, v1: __.AVT_Tuple[_Any, ...], v2: __.AVT_Tuple[__.Unpack[_Ts]], /) -> __.TypeIs[__.AVT_Tuple[__.Unpack[_Ts]]]: ...
            
    @classmethod
    def isTuple2(self, v1, v2, /):
        """
        @lifetime >= 0.3.43 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isTuple2
        
        Extension of `~.isTuple()` and also `isinstance()`. Usage is following::

            Tense.isTuple2((132, 342), (int,)) # True; same as ~.isTuple((132, 342), int)
            Tense.isTuple2((132, 342), (int, int)) # True (both items are integers)
            Tense.isTuple2((132, 342), (int, int, int)) # throws TypeError
            Tense.isTuple2((132, 342), ((int, str),))) # True; same as ~.isTuple((132, 342), (int, str))
            Tense.isTuple2((132, 342), (int, str)) # False (NOT the same as ~.isTuple((132, 342), (int, str)))
            Tense.isTuple2((132, 342), (str,)) # False
            Tense.isTuple2((132, 342), ((int, str), int)) # True
            Tense.isTuple2((132, 342), ((int, str), str)) # False
            Tense.isTuple2((132, 342), ((int, str), (int, str))) # True
        """
        
        if self.isTuple(v1) and self.isTuple(v2) and reckon(v2) == 0:
            return True
        
        elif self.isTuple(v1) and self.isTuple(v2, (tuple, *_SupportedTypes)):
            
            if reckon(v1) == 0:
                
                if reckon(v2) == 0 or (reckon(v2) == 1 and v2[0] is _Any):
                    return True
                
                return False
            
            _placeholder = True
            
            if reckonIsLeast(v1, v2):
                
                error = TypeError("expected first tuple having same as or bigger amount of items than second tuple")
                raise error
            
            elif reckon(v1) == reckon(v2):
                
                for i in abroad(v1):
                    _placeholder = _placeholder and bool(self.isTuple((v1[i],), v2[i]))
                    
                return _placeholder
            
            else:
                
                for i in abroad(reckon(v2) - 1):
                    _placeholder = _placeholder and bool(self.isTuple((v1[i],), v2[i]))
                    
                for i in abroad(v1[reckon(v2) - 1 :]):
                    _placeholder = _placeholder and bool(self.isTuple((v1[i],), v2[-1]))
                    
                return _placeholder
            
        return False
            
    @classmethod
    @__.overload
    def isList(self, v: _Any, /, type: __.AVT_Type[_T] = _Any) -> __.TypeIs[__.AVT_List[_T]]: ...
    
    @classmethod
    @__.overload
    def isList(self, v: _Any, /, type: __.AVT_Tuple[__.AVT_Type[_T], ...]) -> __.TypeIs[__.AVT_List[_T]]: ...
    
    @classmethod
    @__.overload 
    def isList(self, v: _Any, /, type: _T_noneOrEllipsis) -> __.TypeIs[__.AVT_List[_T_noneOrEllipsis]]: ... # >= 0.3.53
        
    @classmethod
    @__.overload
    def isList(self, v: _Any, /, type: _U) -> __.TypeIs[__.AVT_List[_U]]: ...
                    
    @classmethod
    def isList(self, v, /, type = _Any):
        """
        @lifetime >= 0.3.26rc1 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isList
        
        Determine whether a value is a list built-in.
        
        - 0.3.34: Added new parameter `type`, allowing to restrict the list type. Default value is `Any`
        - 0.3.35: Overload; `type` now can be a tuple of types, code will count them as union type to match against
        - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
        """
        if _Type(v) is list:
            return _is_sequence_helper(v, type = type)
        
        else:
            return False
        
    @classmethod
    @__.overload
    def isDict(
        self,
        v: _Any,
        /,
        ktype: __.Union[__.AVT_Type[_KT], _KT_noneOrEllipsis] = _Any,
        vtype: __.Union[__.AVT_Type[_VT], _VT_noneOrEllipsis] = _Any
    ) -> __.TypeIs[__.AVT_Dict[__.Union[_KT, _KT_noneOrEllipsis], __.Union[_VT, _VT_noneOrEllipsis]]]: ...
    
    @classmethod
    @__.overload
    def isDict(self, v: _Any, /, ktype: __.AVT_Type[_KT], vtype: __.AVT_Tuple[__.AVT_Type[_VT], ...]) -> __.TypeIs[__.AVT_Dict[_KT, _VT]]: ...
    
    @classmethod
    @__.overload
    def isDict(self, v: _Any, /, ktype: __.AVT_Type[_KT], vtype: _UVT) -> __.TypeIs[__.AVT_Dict[_KT, _UVT]]: ...
    
    @classmethod
    @__.overload
    def isDict(self, v: _Any, /, ktype: __.AVT_Tuple[__.AVT_Type[_KT], ...], vtype: type[_VT] = _Any) -> __.TypeIs[__.AVT_Dict[_KT, _VT]]: ...
    
    @classmethod
    @__.overload
    def isDict(self, v: _Any, /, ktype: __.AVT_Tuple[__.AVT_Type[_KT], ...], vtype: __.AVT_Tuple[__.AVT_Type[_VT], ...]) -> __.TypeIs[__.AVT_Dict[_KT, _VT]]: ...
    
    @classmethod
    @__.overload
    def isDict(self, v: _Any, /, ktype: __.AVT_Tuple[__.AVT_Type[_KT], ...], vtype: _UVT) -> __.TypeIs[__.AVT_Dict[_KT, _UVT]]: ...
    
    @classmethod
    @__.overload
    def isDict(self, v: _Any, /, ktype: _UKT, vtype: __.AVT_Type[_VT] = _Any) -> __.TypeIs[__.AVT_Dict[_UKT, _VT]]: ...
    
    @classmethod
    @__.overload
    def isDict(self, v: _Any, /, ktype: _UKT, vtype: __.AVT_Tuple[__.AVT_Type[_VT], ...]) -> __.TypeIs[__.AVT_Dict[_UKT, _VT]]: ...
    
    @classmethod
    @__.overload
    def isDict(self, v: _Any, /, ktype: _UKT, vtype: _UVT) -> __.TypeIs[__.AVT_Dict[_UKT, _UVT]]: ...
    
    @classmethod
    def isDict(self, v, /, ktype = _Any, vtype = _Any):
        """
        @lifetime >= 0.3.31 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isDict
        
        Determine whether a value is a dictionary built-in.
        
        - 0.3.34: Added 2 parameters `ktype` and `vtype`, restricting types for, respectively, keys and values. \\
            Both have default values `Any`.
        - 0.3.35: Overload; `ktype` and `vtype` now can be tuples of types, code will count them as union type to match against, \\
            respectively, keys and values.
        - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
        """
        
        if type(v) is dict:
            
            vk, vv = ([k for k in v], [v[k] for k in v])
            return _is_sequence_helper(vk, type = ktype) and _is_sequence_helper(vv, type = vtype)
            
        else:
            return False
    
    @classmethod
    @__.overload
    def isSet(self, v: _Any, /, type: __.AVT_Type[_T] = _Any) -> __.TypeIs[__.AVT_Set[_T]]: ...
    
    @classmethod
    @__.overload
    def isSet(self, v: _Any, /, type: __.AVT_Tuple[__.AVT_Type[_T], ...]) -> __.TypeIs[__.AVT_Set[_T]]: ...
    
    @classmethod
    @__.overload
    def isSet(self, v: _Any, /, type: _U) -> __.TypeIs[__.AVT_Set[_U]]: ...
            
    @classmethod
    def isSet(self, v, /, type = _Any):
        """
        @lifetime >= 0.3.35 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isSet
        
        Determine whether a value is a set built-in.
        
        Parameter `type` allows to restrict the set type.
        
        - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
        """
        
        if _Type(v) is set:
            
            return _is_sequence_helper(v, type = type)
        
        else:
            
            return False
    
    @classmethod
    @__.overload
    def isFrozenSet(self, v: _Any, /, type: __.AVT_Type[_T] = _Any) -> __.TypeIs[__.AVT_FrozenSet[_T]]: ...
    
    @classmethod
    @__.overload
    def isFrozenSet(self, v: _Any, /, type: __.AVT_Tuple[__.AVT_Type[_T], ...]) -> __.TypeIs[__.AVT_FrozenSet[_T]]: ...
    
    @classmethod
    @__.overload
    def isFrozenSet(self, v: _Any, /, type: _U) -> __.TypeIs[__.AVT_FrozenSet[_U]]: ...
        
    @classmethod
    def isFrozenSet(self, v, /, type = _Any):
        """
        @lifetime >= 0.3.35 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isFrozenSet
        
        Determine whether a value is a frozenset built-in.
        
        Parameter `type` allows to restrict the frozenset type.
        
        - 0.3.36: Generic types are now allowed. Warning: this feature is experimental
        """
        if _Type(v) is frozenset:
            
            return _is_sequence_helper(v, type = type)
        
        else:
            
            return False
        
    
    @classmethod
    @__.overload
    def isDeque(self, v: _Any, /, type: __.AVT_Type[_T] = _Any) -> __.TypeIs[__.AVT_Deque[_T]]: ...
    
    @classmethod
    @__.overload
    def isDeque(self, v: _Any, /, type: __.AVT_Tuple[__.AVT_Type[_T], ...]) -> __.TypeIs[__.AVT_Deque[_T]]: ...
    
    @classmethod
    @__.overload
    def isDeque(self, v: _Any, /, type: _U) -> __.TypeIs[__.AVT_Deque[_U]]: ...
    
    @classmethod
    def isDeque(self, v, /, type = _Any):
        """
        @lifetime >= 0.3.37 (added on 0.3.37a1) \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isDeque
        
        Determine whether a value is a deque.
        
        Parameter `type` allows to restrict the deque type.
        """
        if _Type(v) is _collections.deque:
            
            return _is_sequence_helper(v, type = type)
        
        else:
            
            return False
    
    @classmethod
    @__.overload
    def isBytes(self, v: _Any, /) -> __.TypeIs[bytes]: ...
    
    @classmethod
    @__.overload
    def isBytes(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
        
    @classmethod
    def isBytes(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.35 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isBytes
        
        Determine whether a value is a bytes built-in.
        
        - 0.3.37 (0.3.37a1): many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = bytes, mode = mode)
    
    @classmethod
    @__.overload
    def isArray(self, v: _Any, /) -> __.TypeIs[__.array]: ... # not generic to comply with versions before Python 3.13
    
    @classmethod
    @__.overload
    def isArray(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
        
    @classmethod
    def isArray(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.37 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isArray
        
        Determine whether a value is an array. 
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = __.array, mode = mode)
        
    
    @classmethod
    @__.overload
    def isByteArray(self, v: _Any, /) -> __.TypeIs[bytearray]: ...
    
    @classmethod
    @__.overload
    def isByteArray(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isByteArray(self, v, /, *_, mode = _MODE_AND): # not generic
        """
        @lifetime >= 0.3.35 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isByteArray
        
        Determine whether a value is a bytearray built-in.
        
        - 0.3.37 (0.3.37a1): many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = bytearray, mode = mode)
    
    
    @classmethod
    @__.overload
    def isMemoryView(self, v: _Any, /) -> __.TypeIs[memoryview]: ...
    
    @classmethod
    @__.overload
    def isMemoryView(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
        
    @classmethod
    def isMemoryView(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.35 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isMemoryView
        
        Determine whether a value is a memoryview built-in.
        
        - 0.3.37 (0.3.37a1): many values may be now inspected
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = memoryview, mode = mode)
    
    @classmethod
    @__.overload
    def isClass(self, v: _Any, /) -> __.TypeIs[__.AVT_Type[_Any]]: ... # >= 0.3.43
        
    @classmethod
    @__.overload
    def isClass(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ... # >= 0.3.43
    
    @classmethod
    def isClass(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.35
        
        Equivalent to `inspect.isclass()`. \\
        Determine whether a value is a class.
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = type, mode = mode)
    
    @classmethod
    @__.overload
    def isFunction(self, v: _Any, /) -> __.TypeIs[_types.FunctionType]: ... # >= 0.3.43
        
    @classmethod
    @__.overload
    def isFunction(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ... # >= 0.3.43
    
    @classmethod
    def isFunction(self, v, /, *_, mode = _MODE_AND): # not generic
        """
        @lifetime >= 0.3.35
        
        Equivalent to `inspect.isfunction()`. \\
        Determine whether a value is a function.
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = _types.FunctionType, mode = mode)
    
    
    @classmethod
    @__.overload
    def isBinary(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @__.overload
    def isBinary(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isBinary(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.38
        
        Returns `True`, if value is a number in binary notation in a string. \\
        Many values can be inspected at once as well. Prefix `0b` is ignored.
        """
        _many = (v,) + _
        return _inspect_numerics(*_many, mode = "b", lmode = mode)
    
    
    @classmethod
    @__.overload
    def isOctal(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @__.overload
    def isOctal(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isOctal(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.38
        
        Returns `True`, if value is a number in octal notation in a string. \\
        Many values can be inspected at once as well. Prefix `0o` is ignored.
        """
        _many = (v,) + _
        return _inspect_numerics(*_many, mode = "o", lmode = mode)
    
    
    @classmethod
    @__.overload
    def isNumeric(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @__.overload
    def isNumeric(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isNumeric(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.41
        
        Returns `True`, if value is a number in decimal notation in a string. \\
        Many values can be inspected at once as well. 0.3.43: Renamed from `isDecimal2`
        
        In reality returned is `True` when `re.match(r"\\d", value)` is satisfied.
        """
        _many = (v,) + _
        return _inspect_numerics(*_many, mode = "d", lmode = mode)
    
    
    @classmethod
    @__.overload
    def isHexadecimal(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @__.overload
    def isHexadecimal(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isHexadecimal(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.38
        
        Returns `True`, if value is a number in hexadecimal notation in a string. \\
        Many values can be inspected at once as well. Prefix `0x` is ignored.
        """
        
        _many = (v,) + _
        return _inspect_numerics(*_many, mode = "h", lmode = mode)
    
    
    @classmethod
    @__.overload
    def isFinalVar(self, v: _Any, /) -> __.TypeIs[_util.FinalVarType]: ...
    
    @classmethod
    @__.overload
    def isFinalVar(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isFinalVar(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.38 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isFinalVar
        
        Returns `True`, if value is a final variable (instance of `tense.util.FinalVar`).
        
        Restricting final variable type is currently rethought, for now use:
        `self.isFinalVar(v) and type(v.x) is int`
        """
        
        _many = (v,) + _
        return _inspect_many(*_many, type = _util.FinalVarType, mode = mode)
    
    
    @classmethod
    @__.overload
    def isSlice(self, v: _Any, /) -> __.TypeIs[slice]: ...
    
    @classmethod
    @__.overload
    def isSlice(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isSlice(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.41 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isSlice
        
        Determine whether a value is a slice object.
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = slice, mode = mode)
    
    
    @classmethod
    @__.overload
    def isProperty(self, v: _Any, /) -> __.TypeIs[property]: ...
    
    @classmethod
    @__.overload
    def isProperty(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isProperty(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.41 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isProperty
        
        Determine whether a value is a property in a class. It can be done only, if property is accessed via reference.
        """
        _many = (v,) + _
        return _inspect_many(*_many, type = property, mode = mode)
    
    if versionInfo >= (0, 3, 42) or True:
        
        @classmethod
        @__.overload
        def isFinalProperty(self, v: __.AVT_Tuple[type, str], /) -> bool: ...
        
        @classmethod
        @__.overload
        def isFinalProperty(self, v: __.AVT_Tuple[type, str], /, *_: __.AVT_Tuple[type, str], mode: _Mode = _MODE_AND) -> bool: ...
        
        @classmethod
        @__.overload
        def isFinalProperty(self, v: __.AVT_Tuple[type, str], /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
        
    if versionInfo >= (0, 3, 43) or True:
        
        @classmethod
        @__.overload
        def isFinalProperty(self, v: _Any, /) -> __.TypeIs[_util.finalproperty[__.Any]]: ...
        
    else:
        
        @classmethod
        @__.overload
        def isFinalProperty(self, v: _Any, /) -> bool: ...

    if versionInfo >= (0, 3, 42) or True:
        
        @classmethod
        @__.overload
        def isFinalProperty(self, v: _Any, /, *_: __.AVT_Tuple[type, str], mode: _Mode = _MODE_AND) -> bool: ...
        
        @classmethod
        @__.overload
        def isFinalProperty(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
        
        @classmethod
        def isFinalProperty(self, v, /, *_, mode = _MODE_AND):
            """
            @lifetime >= 0.3.41 \\
            https://aveyzan.xyz/aveytense#aveytense.Tense.isFinalProperty
            
            Returns `True`, if a property is final. It can be done only, if property is accessed via reference.
            
            See `~.util.finalproperty` decorator for more details.
            """
            
            _many = (v,) + _
            _placeholder = True    
            
            for one in _many:
                
                # If we referred to class member from a class instance directly, we would already obtain a value from final property,
                # and this also works for accessing via class reference. That makes it practically impossible to check without the property's
                # parent in separate parameter, hence we need a tuple with the class and its member as a string. This was troublesome before
                # 0.3.43. However, this technique will be kept for backward-compatibility with 0.3.42.
                # 29.03.2025
                
                if self.isTuple(one, (type, str)) and reckon(one) == 2 and isinstance(one[0], type) and isinstance(one[1], str):
                    
                    # Much simplier than 'not ~.isNone(one[0].__dict__.get(one[1], None))'
                    if one[1] in one[0].__dict__:
                        
                        t = one[0].__dict__[one[1]]
                    
                        if mode in (_MODE_AND, "and"):
                            _placeholder = _placeholder and bool(isinstance(t, _util.finalproperty) or (self.isProperty(t) and (t.fset, t.fdel) == (None, None)))
                            
                        elif mode in (_MODE_OR, "or"):
                            _placeholder = _placeholder or bool(isinstance(t, _util.finalproperty) or (self.isProperty(t) and (t.fset, t.fdel) == (None, None)))
                            
                        else:
                            return False
                        
                    else:
                        return False
                
                else:
                    
                    if mode in (_MODE_AND, "and"):
                        _placeholder = _placeholder and bool(isinstance(one, _util.finalproperty) or (self.isProperty(one) and (one.fset, one.fdel) == (None, None)))
                        
                    elif mode in (_MODE_OR, "or"):
                        _placeholder = _placeholder or bool(isinstance(one, _util.finalproperty) or (self.isProperty(one) and (one.fset, one.fdel) == (None, None)))
                        
                    else:
                        return False
                
            return _placeholder
        
    else:
        
        @classmethod
        def isFinalProperty(self, v, /, *_, mode = _MODE_AND):
            """
            @lifetime >= 0.3.41
            
            Returns `True`, if a property is final. It can be done only, if property is accessed via reference.
            
            See `~.util.finalproperty` decorator for more details.
            """
            
            if self.versionInfo >= (0, 3, 42) or True:
                
                def _ins(v):
                    
                    try:
                        v = v
                        
                    except:
                        
                        try:
                            del v
                            
                        except:
                            return True
                        
                    return False
                
                return (type(v) is _util.finalproperty or not self.isNone(_re.match(r"aveytense\.util\.finalproperty", str(type(v))))) or (self.isProperty(v) and (self.isNone(v.fdel, v.fset) or _ins(v)))
                
            else:
                
                # To 0.3.42 there was no formal way checking, how property is final.
                # ~.util.finalproperty is bodyless, restricted to __new__ method only.
            
                se = r"finalproperty\.__new__\.<locals>\._no_se", ("<function finalproperty.__new__.<locals>._no_se", "<function {}.finalproperty.__new__.<locals>._no_se".format(_util.finalproperty.__module__))
                de = r"finalproperty\.__new__\.<locals>\._no_de", ("<function finalproperty.__new__.<locals>._no_de", "<function {}.finalproperty.__new__.<locals>._no_de".format(_util.finalproperty.__module__))
                
                if reckon(_) == 0:
                    
                    return type(v) is property and (
                        (_re.match(se[0], str(v.fset)) is not None and _re.match(de[0], str(v.fdel)) is not None) or
                        (str(v.fset).startswith(se[1]) and str(v.fdel).startswith(de[1]))
                    )
                
                else:
                    
                    _many = (v,) + _
                    
                    if mode in (self.AND, "and"):
                        
                        return all([type(e) is property and (
                            _re.match(se[0], str(e.fset)) is not None and _re.match(de[0], str(e.fdel)) is not None) or
                            (str(e.fset).startswith(se[1]) and str(e.fdel).startswith(de[1])) for e in _many
                        ])
                    
                    elif mode in (self.OR, "or"):
                        
                        return any([type(e) is property and (
                            _re.match(se[0], str(e.fset)) is not None and _re.match(de[0], str(e.fdel)) is not None) or
                            (str(e.fset).startswith(se[1]) and str(e.fdel).startswith(de[1])) for e in _many
                        ])
                    
                    else:
                        
                        return False
            
    @classmethod
    @__.overload
    def isFinalClass(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @__.overload
    def isFinalClass(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isFinalClass(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.41
        
        Returns `True`, if provided class is final (cannot be subclassed).
        
        It is true when class inherits from `~.util.Final`.
        """
        
        def _check_if_final(value):
            
            if self.isClass(value):
                
                # In this attempt, we try to subclass the class - on failure it returns True
                try:
                    class _test(value): ...
                    
                except exceptions.SubclassedError:
                    return True
                
                else:
                    return (
                        (_util.Final in value.__bases__) or
                        ("__final__" in value.__dict__ and value.__final__ is True) or issubclass(value, _util.Final)
                    )
                
            else:
                return False
        
        if reckon(_) == 0:
            
            return _check_if_final(v)
            
        else:
            
            _many = (v,) + _
            
            if mode in (self.AND, "and"):
                
                return all([_check_if_final(e) for e in _many])
            
            elif mode in (self.OR, "or"):
                
                return any([_check_if_final(e) for e in _many])
            
            else:
                
                return False
            
    @classmethod
    def isUnbound(self, f: __.AVT_Callable[..., _Any], v: str, /):
        """
        @lifetime >= 0.3.44 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isUnbound
        
        Returns `True`, if variable `v` in function `f` is unbound. Since 0.3.46 \\
        `True` is returned when a method is unbound.
        
        It is `False` for nondescript variables. To return `True`, concerned \\
        variable must be referenced in the function's code, and defined in a \\
        statement (or more, and not outside) which won't be invoked at runtime. \\
        Other way is referencing the variable before its definition.
        
        This method cannot be invoked in function, which was passed as a parameter \\
        in this method, as this method may not return any value.
        
        It is `True` for the following example::
        
            from aveytense import Tense
            
            def test():
            
                if False:
                    e = 62
                    
                e # if it was lacking, False would be returned
                    
            print(Tense.isUnbound(test, "e")) # True
        """
        
        # 0.3.46
        if _inspect.ismethod(f) and self.test(str(f), r"<unbound method '{}'>".format(f.__qualname__)):
            return True
        
        if not callable(f):
            error = TypeError("first parameter must be a callable") # edit 0.3.46. previous ending: must be parameter-less callable
            raise error
        
        try:
            
            if not self.isString(v):
                error = TypeError("second parameter must be a string")
                raise error
            
        except RecursionError:
            return False
            
        try:
            f()
            
        except RecursionError:
            return False
        
        except TypeError as exc: # >= 0.3.46
            
            if str(exc).startswith("unbound method"):
                return True
            
        # don't permit custom messages
        except UnboundLocalError as exc:
            
            from ._ᴧv_collection import _exceptions
            
            _exception_ = lambda v: [e.format(v) for e in _exceptions._unbound_local_messages]
                
            if str(exc) in _exception_(v):
                return True
            
        return False
    
    @classmethod
    @__.overload
    def isLambda(self, v: _Any, /) -> __.TypeIs[__.FunctionType]: ...
    
    @classmethod
    @__.overload
    def isLambda(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isLambda(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.52
        
        Check if value is a lambda expression
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        return _use_([isinstance(e, __.LambdaType) for e in _all_])
    
    @classmethod
    @__.overload
    def isIterable(self, v: _Any, /) -> __.TypeIs[__.AVT_Iterable[_Any]]: ...
    
    @classmethod
    @__.overload
    def isIterable(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isIterable(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.52
        
        Check if value is an iterable object
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        return _use_([isinstance(e, __.Iterable) for e in _all_])
    
    @classmethod
    @__.overload
    def isIterator(self, v: _Any, /) -> __.TypeIs[__.AVT_Iterator[_Any]]: ...
    
    @classmethod
    @__.overload
    def isIterator(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isIterator(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.52
        
        Check if value is an iterator
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        return _use_([isinstance(e, __.Iterator) for e in _all_])
    
    @classmethod
    @__.overload
    def isAwaitable(self, v: _Any, /) -> __.TypeIs[__.AVT_Awaitable[_Any]]: ...
    
    @classmethod
    @__.overload
    def isAwaitable(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isAwaitable(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.52
        
        Check if value is an awaitable object
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        return _use_([isinstance(e, __.Awaitable) for e in _all_])
    
    @classmethod
    @__.overload
    def isGenerator(self, v: _Any, /) -> __.TypeIs[__.AVT_Generator[_Any, _Any, _Any]]: ...
    
    @classmethod
    @__.overload
    def isGenerator(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isGenerator(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.52
        
        Check if value is an generator
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        return _use_([isinstance(e, __.Generator) for e in _all_])
    
    @classmethod
    @__.overload
    def isGenExpr(self, v: _Any, /) -> __.TypeIs[__.AVT_Generator[_Any, None, None]]: ...
    
    @classmethod
    @__.overload
    def isGenExpr(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isGenExpr(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.52
        
        Check if value is a generator object from generator expression
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        return _use_([isinstance(e, __.GenExprType) for e in _all_])
    
    @classmethod
    @__.overload
    def isCoroutine(self, v: _Any, /) -> __.TypeIs[__.AVT_Coroutine[_Any, _Any, _Any]]: ...
    
    @classmethod
    @__.overload
    def isCoroutine(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isCoroutine(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.52
        
        Check if value is an generator
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        return _use_([isinstance(e, __.Coroutine) for e in _all_])
    
    @classmethod
    @__.overload
    def isAsyncGenerator(self, v: _Any, /) -> __.TypeIs[__.AVT_AsyncGenerator[_Any, _Any]]: ...
    
    @classmethod
    @__.overload
    def isAsyncGenerator(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isAsyncGenerator(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.53
        
        Check if value is an asynchronous generator
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        return _use_([isinstance(e, __.AsyncGenerator) for e in _all_])
    
    @classmethod
    @__.overload
    def isGeneric(self, v: type, /) -> bool: ...
    
    @classmethod
    @__.overload
    def isGeneric(self, v: type, /, *_: type, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isGeneric(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.53 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.isGeneric
        
        Check if value is a generic class, or subscriptable type overall.
        
        This does not include special forms of `typing`, use \\
        `isSpecialForm()` instead
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        def _internals(v):
            
            if isinstance(v, __.TypingGenericType) and _sys.version_info < (3, 9):
                return True
            
            if not isinstance(v, type):
                error = TypeError("expected types(s)")
                raise error
            
            _val_ = issubclass(v, __.Generic)
            
            if _sys.version_info >= (3, 9):
                _val_ = _val_ or hasattr(v, "__class_getitem__")
                
            if not _val_:
            
                try:
                    
                    if _sys.version_info >= (3, 13):
                        exec("{}[__.Any]".format(v.__qualname__), globals = globals())
                    else:
                        exec("{}[__.Any]".format(v.__qualname__), globals())
                    
                except Exception as exc:
                    
                    if isinstance(exc, TypeError) and _sys.version_info < (3, 9):
                        
                        if str(exc).startswith("Too few parameters for"):
                            return True
                        
                    return False
                
            return True
        
        return _use_([_internals(t) for t in _all_])
    
    @classmethod
    @__.overload
    def isSpecialForm(self, v: _Any, /) -> bool: ...
    
    @classmethod
    @__.overload
    def isSpecialForm(self, v: _Any, /, *_: _Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isSpecialForm(self, v, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.53
        
        Special forms/typings on `typing` module
        """
        
        _all_ = (v,) + _
        _use_ = all if mode in ("and", _MODE_AND) else any
        
        return _use_([isinstance(e, __.SpecialForm) for e in _all_])
    
    # OVERLOAD >= 0.3.34; < 0.3.39
    @classmethod
    def any(self, i: __.AVT_Iterable[_T], /, condition: _cal[[_T], bool] = ...):
        """
        @lifetime >= 0.3.26rc2 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.any
        
        Extension of inbuilt function `any()`.
        - 0.3.40: any iterable is now allowed, and replaced `None` with ellipsis
        - 0.3.34: `any()` now returns boolean rather than shallow copy of sequence
        """
        
        if not isinstance(i, __.Iterable):
            error = TypeError("expected an iterable")
            raise error
        
        if not self.isEllipsis(condition) and not _is_bool_callback(condition):
            error = TypeError("expected a callable with parameter without default value or ellipsis in parameter 'condition'")
            raise error
        
        # 0.3.40
        if reckon(i) == 0:
            return False
        
        # 0.3.40; refer to constructor of 'bool'
        _cond = condition if not self.isEllipsis(condition) else lambda x: bool(x)
            
        for e in list(i):
            
            # for better results consider using function/method that returns a boolean value
            if _cond(e):
                return True
            
        return False
    
    # OVERLOAD >= 0.3.34; < 0.3.40
    @classmethod
    def all(self, i: __.AVT_Iterable[_T], /, condition: _cal[[_T], bool] = ...): # slash was after 'condition' parameter before (0.3.34)
        """
        @lifetime >= 0.3.26rc2 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.all
        
        Extension of inbuilt function `all()`
        - 0.3.40: any iterable is now allowed, removed change from 0.3.36. Replace `None` with ellipsis
        - 0.3.36: if condition was a callable, it must return boolean value, otherwise will always return `False`
        - 0.3.34: `all()` now returns boolean rather than shallow copy of sequence
        - 0.3.27a4: removed parameter `default`.
        """
        
        if not isinstance(i, __.Iterable):
            error = TypeError("expected an iterable")
            raise error
        
        if not self.isEllipsis(condition) and not _is_bool_callback(condition):
            error = TypeError("expected a callable with parameter without default value or ellipsis in parameter 'condition'")
            raise error
        
        # 0.3.40
        if reckon(i) == 0:
            return False
        
        # 0.3.40; refer to constructor of 'bool'
        _cond = condition if not self.isEllipsis(condition) else lambda x: bool(x)
        
        for e in list(i):
            
            # for better results consider using function/method that returns a boolean value
            if not _cond(e):
                return False
            
        return True
    
    @classmethod
    @__.overload
    def test(self, target: str, pattern: _Pattern[str], flags: _FlagsType = 0) -> bool: ...
    
    @classmethod
    @__.overload
    def test(self, target: __.ReadableBuffer, pattern: _Pattern[bytes], flags: _FlagsType = 0) -> bool: ...
    
    @classmethod
    def test(self, target, pattern, flags = 0):
        """
        @lifetime >= 0.3.42 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.test
        
        Equivalent to `RegExp.test()` method from JavaScript and `re.match()` in Python; \\
        only difference between this class method and `re.match()` is that `Match` object is \\
        considered `True` (same as `re.match(pattern, target) is not None`).
        
        Target and pattern must be both either `str` or, respectively, `bytes` and buffer. \\
        Pattern can be also instance of `re.Pattern`.
        """
        
        if (
            (self.isString(target) and (self.isString(pattern) or (isinstance(pattern, __.Pattern) and __.get_args(pattern) == (str,))) or
            (isinstance(target, __.Buffer) and (Tense.isBytes(pattern) or (isinstance(pattern, __.Pattern) and __.get_args(pattern) == (bytes,))))) and
            isinstance(flags, (int, _re.RegexFlag))
        ):
            
            return _re.match(pattern, target, flags) is not None
        
        else:
            
            error = TypeError("expected '{}' and '{}' to match one of following type patterns: 'str' + 'str', 'str' + 're.Pattern[str]', 'bytes' + 'collections.abc.Buffer', 'bytes' + 're.Pattern[bytes]', and expected '{}' to be an integer or 're.RegexFlag'".format(*tuple(_get_all_params(self.test))))
            raise error
    
    @classmethod
    @__.overload
    def startsWith(self, target: __.Union[str, __.AVT_Tuple[str, ...]], prefix: __.Union[str, __.AVT_Tuple[str, ...]], /, mode: _Mode = _MODE_OR, start: int = ..., end: int = ...) -> bool: ...
    
    @classmethod
    @__.overload
    def startsWith(self, target: __.Union[bytes, __.AVT_Tuple[bytes, ...]], prefix: __.Union[__.ReadableBuffer, __.AVT_Tuple[__.ReadableBuffer, ...]], /, mode: _Mode = _MODE_OR, start: int = ..., end: int = ...) -> bool: ...
    
    @classmethod
    def startsWith(self, target, prefix, /, mode = _MODE_OR, start = ..., end = ...):
        """
        @lifetime >= 0.3.42 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.startwith
        
        Fusion of `str.startswith()` and `bytes.startswith()`; allows to inspect many strings and bytes at once.
        
        `end` has no effect if `target` is a tuple.
        """
        
        _params = _get_all_params(self.startsWith)
        
        if self.any([target, prefix], lambda x: not self.isString(x) and not self.isBytes(x) and not self.isTuple(x, (str, bytes))):
            
            error = TypeError("expected string or strings in tuple, or 'bytes' object or 'bytes' objects in tuple in parameters '{}' and '{}'".format(*_params[:2]))
            raise error
        
        if self.any([start, end], lambda x: not self.isEllipsis(x) and not self.isInteger(x)):
            
            error = TypeError("expected integer or ellipsis in parameters '{}' and '{}'".format(*_params[3:]))
            raise error
        
        _start = 0 if self.isEllipsis(start) else start
        _end = reckon(target) - 1 if self.isEllipsis(end) else end
        
        if self.isString(target, prefix) or (self.isBytes(target) and isinstance(prefix, __.ReadableBuffer)):
            
            return bool(target.startswith(prefix, _start, _end))
        
        if (self.isString(target) and self.isTuple(prefix, str)) or (self.isBytes(target) and self.isTuple(prefix, __.ReadableBuffer)):
                
            for e in prefix:
                        
                if target.startswith(e, _start, _end):
                    return True
                        
            return False
                    
        elif (self.isTuple(target, str) and (self.isString(prefix) or self.isTuple(prefix, str))) or (self.isTuple(target, bytes) and (isinstance(prefix, __.ReadableBuffer) or self.isTuple(prefix, __.ReadableBuffer))):
            
            _placeholder = True
            
            for e in target:
                    
                if mode in (_MODE_AND, "and"):
                    _placeholder = _placeholder and bool(e.startswith(prefix, _start, reckon(e) - 1))
                        
                elif mode in (_MODE_OR, "or"):
                    _placeholder = _placeholder or bool(e.startswith(prefix, _start, reckon(e) - 1))
                        
                else:
                    return False
                    
            return _placeholder
        
        return False
    
    
    @classmethod
    @__.overload
    def endsWith(self, target: __.Union[str, __.AVT_Tuple[str, ...]], prefix: __.Union[str, __.AVT_Tuple[str, ...]], /, mode: _Mode = _MODE_OR, start: int = ..., end: int = ...) -> bool: ...
    
    @classmethod
    @__.overload
    def endsWith(self, target: __.Union[bytes, __.AVT_Tuple[bytes, ...]], prefix: __.Union[__.ReadableBuffer, __.AVT_Tuple[__.ReadableBuffer, ...]], /, mode: _Mode = _MODE_OR, start: int = ..., end: int = ...) -> bool: ...
    
    @classmethod
    def endsWith(self, target, suffix, /, mode = _MODE_OR, start = ..., end = ...):
        """
        @lifetime >= 0.3.42 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.endswith
        
        Fusion of `str.endswith()` and `bytes.endswith()`; allows to inspect many strings and bytes at once.
        
        `end` has no effect if `target` is a tuple.
        """
        
        _params = _get_all_params(self.endsWith)
        
        if self.any([target, suffix], lambda x: not self.isString(x) and not self.isBytes(x) and not self.isTuple(x, (str, bytes))):
            
            error = TypeError("expected string or strings in tuple, or 'bytes' object or 'bytes' objects in tuple in parameters '{}' and '{}'".format(*_params[:2]))
            raise error
        
        if self.any([start, end], lambda x: not self.isEllipsis(x) and not self.isInteger(x)):
            
            error = TypeError("expected integer or ellipsis in parameters '{}' and '{}'".format(*_params[3:]))
            raise error
        
        _start = 0 if self.isEllipsis(start) else start
        _end = reckon(target) - 1 if self.isEllipsis(end) else end
        
        if self.isString(target, suffix) or (self.isBytes(target) and isinstance(suffix, __.ReadableBuffer)):
            
            return bool(target.endswith(suffix, _start, _end))
        
        if (self.isString(target) and self.isTuple(suffix, str)) or (self.isBytes(target) and self.isTuple(suffix, __.ReadableBuffer)):
                
            for e in suffix:
                        
                if target.endswith(e, _start, _end):
                    return True
                        
            return False
                    
        elif (self.isTuple(target, str) and (self.isString(suffix) or self.isTuple(suffix, str))) or (self.isTuple(target, bytes) and (isinstance(suffix, __.ReadableBuffer) or self.isTuple(suffix, __.ReadableBuffer))):
            
            _placeholder = True
            
            for e in target:
                    
                if mode in (_MODE_AND, "and"):
                    _placeholder = _placeholder and bool(e.endswith(suffix, _start, reckon(e) - 1))
                        
                elif mode in (_MODE_OR, "or"):
                    _placeholder = _placeholder or bool(e.endswith(suffix, _start, reckon(e) - 1))
                        
                else:
                    return False
                    
            return _placeholder
        
        return False   
                        
    if _version.VERSION_INFO >= (0, 3, 78) and False: # >= 18.03.2025
        
        @classmethod
        def replace(self, target: _Target, pattern: _uni[_Pattern, __.AVT_Tuple[str, ...]], value: _uni[_Target, _cal[[_re.Match[_Target]], _Target], __.AVT_Tuple[str, ...]], count = -1, flags: _FlagsType = 0):
            
            if not self.isInteger(count):
                
                error = TypeError("expected 'count' to be an integer")
                raise error
            
            if type(flags) not in (int, _re.RegexFlag):
                
                error = TypeError("expected 'flags' to be an integer or enum member of 're.RegexFlag'")
                raise error
            
            if self.isString(target):
                
                # comply with re.sub()
                _count = 0 if count == -1 else count
                
                if flags in (0, _re.NOFLAG):
                    
                    _new = target
                    
                    if self.isString(pattern):
                        
                        if self.isString(value):
                        
                            return target.replace(pattern, value, count)
                        
                        elif self.isTuple(value, str):
                            
                            for s in value:
                                
                                _new = _new.replace(pattern, s, count)
                                
                            return _new
                    
                    elif self.isTuple(pattern, str):
                        
                        if self.isString(value):
                        
                            for s in pattern:
                                
                                _new = _new.replace(s, value, count)
                                
                            return _new
                        
                        elif self.isTuple(value, str):
                            
                            for s1 in pattern:
                                
                                for s2 in value:
                                    
                                    _new = _new.replace(s1, s2, count)
                                    
                            return _new
                
                if (
                    (self.isString(pattern) or (isinstance(pattern, __.Pattern) and __.get_args(pattern) == (str,))) and
                    (self.isString(value) or (callable(value) and reckon(_get_all_params(value)) == 1))
                ):
                    
                    # typing.Any is deduced
                    a = _re.sub(pattern, value, target, _count, flags)
                    return str(a)
    
    # >= 0.3.45: Annotation in parameter 'm'
    @classmethod
    def expect(self, i: __.AVT_Iterable[_T], m: __.Union[str, range, _ab_mod.AbroadInitializer, __.AVT_Uniqual[int]] = ">= 1", /, condition: __.AVT_Callable[[_T], bool] = ...):
        """
        @lifetime >= 0.3.40 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.expect
        
        Returns `True` whether specific number of items in an iterable satisfied `condition`. \\
        If `m` is `">= 1"` or `"1 <="`, this method will behave the same as `~.any()`.
        
        `m` must be a valid string literal, like `"> 3"`, otherwise `TypeError` is thrown.  \\
        To rebuild `~.any()`, use `">= 1"`. To rebuild `~.all()`, use `"== len"`.
        
        Since 0.3.45 it is allowed to pass a set of positive integers to parameter `m`. This thing \\
        was meant to be provided in version 0.3.48.
        
        See documentation for more details.
        """
        
        if not isinstance(i, __.Iterable):
            error = TypeError("expected an iterable in first positional parameter")
            raise error
        
        if self.versionInfo >= (0, 3, 45) or True:
            
            if not isinstance(m, (str, range, _ab_mod.AbroadInitializer, __.Uniqual)) or (isinstance(m, (range, _ab_mod.AbroadInitializer, __.Uniqual)) and not Math.isPositive(list(m))): # all must satisfy
                error = TypeError("expected a valid string literal, like \"> 3\", or a positive integer set")
                raise error
            
        else:
        
            if not self.isString(m) or (self.isString(m) and not _re.match(r"^(\d+|len) ?(<=|>=|==|!=|<|>)$|^(<=|>=|!=|==|<|>) ?(\d+|len)$", m)):
                error = TypeError("expected a valid string literal, like \"> 3\"")
                raise error
        
        if not (self.isEllipsis(condition) or _is_bool_callback(condition)):
            error = TypeError("expected a callable with parameter without default value or ellipsis in parameter 'condition'")
            raise error
        
        if m in (">= 1", "1 <="):
            return self.any(i, condition)
        
        # just like ~.any(), this method returns False, because 'for' loop is skipped for empty iterables
        # for empty iterable Python any() function would return True
        if reckon(i) == 0:
            return False
        
        # pre-inspection that a callback returns boolean, same behavior as in ~.all()
        if type(condition(i[0])) is not bool:
            error = TypeError("callable in parameter 'condition' must return a boolean value")
            raise error
        
        # gimmick of this part of the code is about creating callable variable
        # and it allows to shorten the code since more 'if' statements would be required
        # when invoked, with both versions it will return boolean
        _cond = condition if not self.isEllipsis(condition) else lambda x: bool(x)
        
        if self.isString(m): # <- 0.3.45
        
            _tmp = str(_re.findall(r"(\d+|len)", m)[0])
            
            if _re.match(r"len", _tmp):
                _tmp = str(reckon(i))
            
            # integer with leading zeros isn't allowed (Python error not everyone can expect)
            if _tmp.startswith("0"):
                error = TypeError("leading zeros in decimal integer literals are not permitted in parameter 'm'")
                raise error
            
            # it is obligatory for integer to be in range [1; len], for zero matches you can use "< 1"
            if not Math.isInRange(int(_tmp), 1, reckon(i)):
                error = TypeError("expected an integer in a string in parameter 'm' in range [1; iterable_length]; for zero matches use \"< 1\"")
                raise error
            
            if _re.match(r"^(\d+|len) ?<=$|^>= ?(\d+|len)$", m):
                return reckon([e for e in i if _cond(e)]) >= int(_tmp)
            
            elif _re.match(r"^(\d+|len) ?>=$|^<= ?(\d+|len)$", m):
                return reckon([e for e in i if _cond(e)]) <= int(_tmp)
            
            elif _re.match(r"^(\d+|len) ?<$|^> ?(\d+|len)$", m):
                return reckon([e for e in i if _cond(e)]) > int(_tmp)
            
            elif _re.match(r"^(\d+|len) ?>$|^< ?(\d+|len)$", m):
                return reckon([e for e in i if _cond(e)]) < int(_tmp)
            
            elif _re.match(r"^(\d+|len) ?!=$|^!= ?(\d+|len)$", m):
                return reckon([e for e in i if _cond(e)]) != int(_tmp)
            
            else:
                return reckon([e for e in i if _cond(e)]) == int(_tmp)
            
        else:
            
            # >= 0.3.45
            return reckon([e for e in i if _cond(e)]) in list(m)
    
    # little typing deviation
    # version tuple-tuple is not ready yet
    if versionInfo >= (0, 3, 49) or True:
        
        @classmethod
        @__.overload
        def hasattr(self, o: __.AVT_Tuple[object, ...], attr: __.Union[str, __.AVT_Tuple[str]], /, mode: _Mode = _MODE_OR) -> bool: ...
        
        @classmethod
        @__.overload
        def hasattr(self, o: object, attr: __.Union[str, __.AVT_Tuple[str]], /) -> bool: ...
        
        @classmethod
        @__.overload
        def hasattr(self, o: object, attr: __.AVT_Tuple[str, __.Unpack[__.AVT_Tuple[str, ...]]], /, mode: _Mode = _MODE_OR) -> bool: ...
    
    else: 
        
        @classmethod
        @__.overload
        def hasattr(self, o: object, attr: str, /) -> bool: ...
        
        @classmethod
        @__.overload
        def hasattr(self, o: object, attr: __.AVT_Tuple[str, ...], /, mode: _Mode = _MODE_OR) -> bool: ...
            
    @classmethod
    def hasattr(self, o, attr, /, mode = _MODE_OR):
        """
        @lifetime >= 0.3.34 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.hasattr
        
        Returns `True` if object has specific attribute. Same as built-in function `hasattr()`, only 2 additional things are provided:
        - If `attr` is a string tuple, then it is deduced as `hasattr(o, attr[0]) or hasattr(o, attr[1]) or ...` \\
        Reference to how `isinstance()` works in case if types tuple is included instead of single type.
        - If `mode` is set to `"and"`, then it will occur as `hasattr(o, attr[0]) and hasattr(o, attr[1]) and ...` \\
        By default has value `"or"`. Note it works only for `attr` being a string tuple.
        """
        
        if self.isString(attr):
            
            if self.isTuple(o, object):
                
                _r = True
                
                for e in o:
                    
                    if mode in (_MODE_AND, "and"):
                        _r = _r or hasattr(e, attr)
                        
                    elif mode in (_MODE_OR, "or"): 
                        _r = _r and hasattr(e, attr)
                        
                return _r
            
            return hasattr(o, attr)
        
        elif self.isTuple(attr, str):
            
            _r = True
            
            for many in attr:
                
                # 0.3.36: ModeSelection
                
                if mode in (_MODE_AND, "and"):
                    _r = _r or hasattr(o, many)
                    
                elif mode in (_MODE_OR, "or"): 
                    _r = _r and hasattr(o, many)
                    
                else:
                    error = ValueError("unknown mode provided, expected \"and\" or \"or\"")
                    raise error
                
            return _r
        
        error = TypeError("expected a string tuple or a string in parameter 'attr'")
        raise error
    
    @classmethod
    def group(self, *statements: _uni[__.AVT_Sequence[bool], __.AVT_Uniqual[bool]], mode = "and-or"):
        """
        @lifetime >= 0.3.34
        
        Returns one boolean value combining all statements into one boolean value. \\
        Parameter `mode` determines about used logical operators inside and outside \\
        provided sequences. Possible values (with `and`, `or`, `nand` = `and not`, `nor` = `or not`):
        
        - `"and-or"` = `(a1 and a2 and ... and aN) or (b1 and b2 and ... and bN) or ...`
        - `"or-and"` = `(a1 or a2 or ... or aN) and (b1 or b2 or ... or bN) and ...`
        - `"and-nor"` = `not (a1 and a2 and ... and aN) or not (b1 and b2 and ... and bN) or not ...`
        - `"nor-and"` = `(not a1 or not a2 or not ... or not aN) and (not b1 or not b2 or not ... or not bN) and ...`
        - `"nand-or"` = `(not a1 and not a2 and not ... and not aN) or (b1 and not b2 and not ... and not bN) or ...`
        - `"or-nand"` = `not (a1 or a2 or ... or aN) and not (b1 or b2 or ... or bN) and not ...`
        - `"nand-nor"` = `not (not a1 and not a2 and not ... and not aN) or not (b1 and not b2 and not ... and not bN) or not ...`
        - `"nor-nand"` = `not (not a1 or not a2 or not ... or not aN) and not (not b1 or not b2 or not ... or not bN) and not ...`
        
        On 0.3.40 added missing modes (and case is now insensitive):
        - `"and-nand"` = `not (a1 and a2 and ... and aN) and not (b1 and b2 and ... and bN) and not ...`
        - `"nand-and"` = `(not a1 and not a2 and not ... and not aN) and (not b1 and not b2 and not ... and not bN) and ...`
        - `"or-nor"` = `not (a1 or a2 or ... or aN) or not (b1 or b2 or ... or bN) or not ...`
        - `"nor-or"` = `(not a1 or not a2 or not ... or not aN) or (not b1 or not b2 or not ... or not bN) or ...`
        
        Note: using modes `"and-and"`, `"or-or"`, `"nand-nand"` and `"nor-nor"` is discouraged, \\
        but will be kept to save some time writing `and`, `or` and `not` operators
        """
        
        if not self.isString(mode):
            
            error = TypeError("expected a string in parameter 'mode'")
            raise error
        
        _mode = mode.lower()
        _modes = ("and-or", "or-and", "and-nor", "nor-and", "nand-or", "or-nand", "nand-nor", "nor-nand", "and-and", "or-or", "nand-nand", "nor-nor", "and-nand", "nand-and", "or-nor", "nor-or")
        
        if _mode not in _modes:
            
            error = ValueError("expected a valid mode from following: {}".format(", ".join(_modes)))
            raise error
        
        for statement in statements:
            
            if not isinstance(statement, (__.Sequence, __.Uniqual)) or (isinstance(statement, (__.Sequence, __.Uniqual)) and not self.isList(list(statement), bool)):
                
                error = ValueError("expected non-empty sequence(s) with single boolean values, like list, tuple, set or frozenset")
                raise error
            
            
        _result = _subresult = True
        
        for statement in statements:
            
            if _mode == "and-and":
                
                for s in statement:
                    _subresult = _subresult and s
                    
                _result = _result and _subresult
                
            elif _mode == "and-nor":
                
                for s in statement:
                    _subresult = _subresult or not s
                    
                _result = _result and _subresult
                
            elif _mode == "and-or":
                
                for s in statement:
                    _subresult = _subresult or s
                    
                _result = _result and _subresult
                
            elif _mode == "nand-nand":
                
                for s in statement:
                    _subresult = _subresult and not s
                    
                _result = _result and not _subresult
                
            elif _mode == "nand-nor":
                
                for s in statement:
                    _subresult = _subresult or not s
                    
                _result = _result and not _subresult
                
            elif _mode == "nand-or":
                
                for s in statement:
                    _subresult = _subresult or s
                    
                _result = _result and not _subresult
                
            elif _mode == "nor-and":
                
                for s in statement:
                    _subresult = _subresult and s
                    
                _result = _result or not _subresult
                
            elif _mode == "nor-nand":
                
                for s in statement:
                    _subresult = _subresult and not s
                    
                _result = _result or not _subresult
                
            elif _mode == "nor-nor":
                
                for s in statement:
                    _subresult = _subresult or not s
                    
                _result = _result or not _subresult
                
            elif _mode == "or-and":
                
                for s in statement:
                    _subresult = _subresult and s
                    
                _result = _result or _subresult
                
            elif _mode == "or-nand":
                
                for s in statement:
                    _subresult = _subresult and not s
                    
                _result = _result or _subresult
                
            elif _mode == "or-or":
                
                for s in statement:
                    _subresult = _subresult or s
                    
                _result = _result or _subresult
                
            elif _mode == "and-nand":
                
                for s in statement:
                    _subresult = _subresult and not s
                    
                _result = _result and _subresult
                
            elif _mode == "nand-and":
                
                for s in statement:
                    _subresult = _subresult and s
                    
                _result = _result and not _subresult
                
            elif _mode == "nor-or":
                
                for s in statement:
                    _subresult = _subresult or s
                    
                _result = _result or not _subresult
                
            else:
                
                for s in statement:
                    _subresult = _subresult or not s
                    
                _result = _result or _subresult
                
            _subresult = True
            
        return _result
    
    @classmethod
    def equal(self, *v: _T):
        """
        @lifetime >= 0.3.41 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.equal
        
        Returns `True` if all values are equal to each other.
        
        Same as::

            v[0] == v[1] and v[1] == v[2] and v[2] == v[3] and ...
            v[0] == v[1] == v[2] == v[3] == ...
            
        For no values and no type accordance returned is `False`.
        """
        
        if reckon(v) == 0:
            return False
        
        _placeholder = True
        _type_all = type(v[0])
        
        for i in abroad(1, v):
            
            if type(v[i - 1]) is not _type_all:
                return False
            
            _placeholder = _placeholder and v[i - 1] == v[i]
            
        return _placeholder
    
    @classmethod
    def inequal(self, *v: _T):
        """
        @lifetime >= 0.3.41 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.inequal
        
        Returns `True` if all values are inequal to each other.
        
        Same as::

            v[0] != v[1] and v[1] != v[2] and v[2] != v[3] and ...
            v[0] != v[1] != v[2] != v[3] != ...
            
        For no values and no type accordance returned is `False`.
        """
        
        if reckon(v) == 0:
            return False
        
        _placeholder = True
        _type_all = type(v[0])
        
        for i in abroad(1, v):
            
            if type(v[i - 1]) is not _type_all:
                return False
            
            _placeholder = _placeholder and v[i - 1] != v[i]
            
        return _placeholder
    
    @classmethod
    def abroadPositive(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        @lifetime >= 0.3.24 \\
        @modified 0.3.25 (moved slash to between `value1` and `value2`), 0.3.29, 0.3.52
        
        Every negative integer is coerced to positive.
        """
        ab = abroad(value1, value2, modifier)
        return type(ab)([abs(e) for e in ab], abs(ab.params[0]), abs(ab.params[1]), ab.params[2])
    
    @classmethod
    def abroadNegative(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        @lifetime >= 0.3.24 \\
        @modified 0.3.25 (moved slash to between `value1` and `value2`), 0.3.29, 0.3.52
        
        Every positive integer is coerced to negative.
        """
        ab = abroad(value1, value2, modifier)
        return type(ab)([-abs(e) for e in ab], -abs(ab.params[0]), -abs(ab.params[1]), ab.params[2])
    
    @classmethod
    def abroadPositiveFlip(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        @lifetime >= 0.3.24 \\
        @modified 0.3.25 (moved slash to between `value1` and `value2`), 0.3.29, 0.3.52
        
        Every negative integer is coerced to positive, then sequence is reversed.
        """
        ab = abroad(value1, value2, modifier)
        return type(ab)([abs(e) for e in ab][::-1], abs(ab.params[1]) - 1, abs(ab.params[0]) - 1, ab.params[2])
    
    @classmethod
    def abroadNegativeFlip(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        @lifetime >= 0.3.24 \\
        @modified 0.3.25 (moved slash to between `value1` and `value2`), 0.3.29, 0.3.52
        
        Every positive integer is coerced to negative, then sequence is reversed.
        """
        ab = abroad(value1, value2, modifier)
        return type(ab)([-abs(e) for e in ab][::-1], -abs(ab.params[1]) + 1, -abs(ab.params[0]) + 1, ab.params[2])
    
    @classmethod
    def abroadPack(self, *values: _AbroadPackType[_T]):
        """
        @lifetime >= 0.3.25 \\
        @modified 0.3.29
        
        This variation of `abroad()` function bases on `zip()` Python function.
        """
        ab = abroad(reckonLeast(*values))
        return type(ab)([e for e in ab], ab.params[0], ab.params[1], ab.params[2])
    
    @classmethod
    def abroadExclude(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, *excludedIntegers: int):
        """
        @lifetime >= 0.3.25 \\
        @modified 0.3.29, 0.3.52
        
        This variation of `abroad()` function is the same as `abroad()` function, \\
        but it also allows to exclude specific integers from the returned list. \\
        If all are excluded, returned is empty integer list. If integers excluded \\
        do not exist in returned sequence normally, this issue is omitted.
        """
        for e in excludedIntegers:
            
            if not self.isInteger(e):
                error = TypeError("every item in parameter 'excludedIntegers' must be an integer")
                raise error
            
        return [e for e in abroad(value1, value2, modifier) if e not in excludedIntegers] # >= 0.3.52, return list
    
    @classmethod
    def abroadPrecede(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, prefix: _opt[str] = None):
        """
        @lifetime >= 0.3.25 \\
        @modified 0.3.29, 0.3.52
        
        This variation of `abroad()` function returns strings in a list. If `prefix` is `None`, \\
        returned are integers in strings, otherwise added is special string prefix before integers.
        """
        if prefix is not None and not isinstance(prefix, str):
            error = TypeError("expected parameter '{}' have string value".format(_get_all_params(self.abroadPrecede)[-1]))
            raise error

        return [("" if prefix is None else prefix) + str(e) for e in abroad(value1, value2, modifier)] # >= 0.3.52; return list
            
    @classmethod
    def abroadSufcede(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, suffix: _opt[str] = None):
        """
        @lifetime >= 0.3.25 \\
        @modified 0.3.29, 0.3.52
        
        This variation of `abroad()` function returns strings in a list. If `prefix` is `None`, \\
        returned are integers in strings, otherwise added is special string suffix after integers.
        """
        if suffix is not None and not isinstance(suffix, str):
            error = TypeError("expected parameter '{}' have string value".format(_get_all_params(self.abroadSufcede)[-1]))
            raise error

        return [str(e) + ("" if suffix is None else suffix) for e in abroad(value1, value2, modifier)] # >= 0.3.52; return list
    
    @classmethod
    def abroadInside(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, string: _opt[str] = None):
        """
        @lifetime >= 0.3.25 \\
        @modified 0.3.29, 0.3.52
        
        This variation of `abroad()` function returns strings in a list. If `string` is `None`, \\
        returned are integers in strings, otherwise integers are placed inside `{}` of the string.
        """
        if string is not None and not isinstance(string, str):
            error = TypeError("expected parameter '{}' have string value".format(_get_all_params(self.abroadInside)[-1]))
            raise error

        ab = abroad(value1, value2, modifier)
        return [str(e) for e in ab] if string is None else [string.format(str(e)) for e in ab]
    
    if _version.VERSION_INFO < (0, 3, 34) and False: # due to use of -abroad()
        @classmethod
        @__.deprecated("Pending removal on 0.3.30 due to reorganization of sequences returned by abroad() function and many of its variations (retrieve tuple via -abroad(...)) during 0.3.28 - 0.3.29")
        def abroadImmutable(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None) -> _AbroadImmutableInitializer:
            """
            @lifetime >= 0.3.25
            
            Immutable variation of `abroad()` function - instead of list returned is tuple. \\
            Equals `tuple(abroad(...))`.
            """
            return tuple(abroad(value1, value2, modifier))
    
    @classmethod
    def abroadConvect(self, *values: _AbroadConvectType[_T]):
        """
        @lifetime >= 0.3.25
        
        Typical math sum operation before returned is list from `abroad()` function. \\
        If from values a value is:
        - an integer - added is this integer
        - a float - added is this number, without fraction
        - a complex - added are both real and imaginary parts
        - sizeable object - added is its length

        Notice: you can also provide negative entities! If resulted number is negative, \\
        up to `abroad()` function, sequence will go in range `[values_sum, -1]`. \\
        Otherwise, it will take this form: `[0, values_sum - 1]`.
        """
        i = 0
        _params = _get_all_params(self.abroadConvect)
        
        if reckon(values) == 0:
            error = exceptions.MissingValueError("expected at least one item in parameter '{}'".format(_params[-1]))
            raise error
        
        for e in values:
            
            if not isinstance(e, (_ReckonNGT, int, float, complex)):
                error = TypeError("from gamut of supported types, parameter '{}' has at least one unsupported type".format(_params[-1]))
                raise error
            
            elif isinstance(e, int):
                i += e
                
            elif isinstance(e, float):
                i += _math.trunc(e)
                
            elif isinstance(e, complex):
                i += _math.trunc(e.real) + _math.trunc(e.imag)
                
            else:
                i += reckon(e)
        return abroad(i)
    
    @classmethod
    @__.deprecated("Deprecated since 0.3.50 and may be removed in the future.")
    def abroadLive(self, *values: _AbroadLiveType[_T]):
        """
        @lifetime >= 0.3.25
        
        Concept from non-monotonous sequences from math. Like graph, \\
        which changes per time. If from values a value is:
        - an integer - this is next point
        - a float - next point doesn't have fraction
        - a complex - next point is sum of real and imaginary parts
        - sizeable object - its length is next point
        """
        a, ret = [[0] for _ in abroad(2)]
        self.clear(a, ret)
        
        if reckon(values) == 0:
            error = exceptions.MissingValueError("expected at least one item in parameter 'values'.")
            raise error
        
        for e in values:
            
            if not isinstance(e, (_ReckonNGT, int, float, complex)):
                error = TypeError(f"from gamut of supported types, parameter 'values' has at least one unsupported type: '{type(e).__name__}'")
                raise error
            
            elif isinstance(e, int):
                a.append(e)
                
            elif isinstance(e, float):
                a.append(_math.trunc(e))
                
            elif isinstance(e, complex):
                a.append(_math.trunc(e.real) + _math.trunc(e.imag))
                
            else:
                a.append(reckon(e))
                
        for i1 in abroad(1, a):
            tmp = a[i1]
            
            if tmp < 0:
                tmp -= 1
                
            else:
                tmp += 1
            
            for i2 in abroad(a[i1 - 1], tmp): 
                ret.append(i2)
                
        return ret
    
    @classmethod
    def abroadFloaty(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, div: __.FloatOrInteger = 10):
        """
        @lifetime >= 0.3.25 \\
        @modified 0.3.29, 0.3.52
        
        Every item from `abroad()` function will be divided by parameter `div`. \\
        It's default value is `10`.
        """
        if not isinstance(div, (int, float)):
            error = TypeError(f"parameter 'div' is not an integer nor floating-point number. Ensure argument got value of type 'int' or 'float'. Received type: {type(div).__name__}")
            raise error
        
        elif isinstance(div, float) and div in (_math.nan, _math.inf):
            error = ValueError("parameter 'div' may not be infinity or not a number.")
            raise error
        
        elif (isinstance(div, int) and div == 0) or (isinstance(div, float) and div == .0):
            error = ZeroDivisionError("parameter 'div' may not be equal zero. This is attempt to divide by zero")
            raise error
        
        ab = abroad(value1, value2, modifier)
        return [e / div for e in ab]
    
    @classmethod
    def abroadSplit(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, limit = 2) -> _AbroadMultiInitializer:
        """
        @lifetime >= 0.3.25
        
        Reference to string slicing. Limit is amount of items, \\
        which can be in one sub-list. May not be equal or below 1.
        """
        lim = 0
        tmp, a = ([0], [[0]])
        self.clear(a, tmp)
        
        if not isinstance(limit, int):
            error = TypeError(f"parameter 'limit' is not an integer. Ensure argument got integer value. Received type: {type(limit).__name__}")
            raise error
        
        elif limit < 1:
            error = ValueError("parameter 'limit' may not be negative, or have value 0 or 1. Start from 2.")
            raise error
        
        for i in abroad(value1, value2, modifier):
            
            if lim % limit == 0:
                a.append(tmp)
                tmp.clear()
                
            else:
                tmp.append(i)
                
            lim += 1
            
        return a
    
    @classmethod
    @__.deprecated("Deprecated since 0.3.50 and may be removed in the future.")
    def abroadVivid(self, *values: _AbroadVividType[_V1, _V2, _M]) -> _AbroadMultiInitializer:
        """
        @lifetime >= 0.3.25
        
        For every value in `values` returned is list `[abroad(V1_1, V2_1?, M_1?), abroad(V1_2, V2_2?, M_2?), ...]`. \\
        Question marks are here to indicate optional values.
        """
        a = [[0]]
        a.clear()
        
        if reckon(values) < 2:
            error = ValueError("expected at least 2 items in parameter 'values'.")
            raise error
        
        for e in values:
            
            if not isinstance(e, tuple):
                error = TypeError(f"parameter 'values' has an item, which isn't a tuple. Ensure every item is a tuple. Received type: {type(e).__name__}")
                raise error
            
            if reckon(e) == 1:
                a.append(+abroad(e[0]))
                
            elif reckon(e) == 2:
                a.append(+abroad(e[0], e[1]))
                
            elif reckon(e) == 3:
                a.append(+abroad(e[0], e[1], e[2]))
                
            else:
                error = ValueError("parameter 'values' may not have empty tuples, nor tuples of size above 3.")
                raise error
            
        return a
    
    @classmethod
    @__.overload
    def abroadEach(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, *, each: None = None) -> _AbroadEachInitializer[int]: ...
    
    @classmethod
    @__.overload
    def abroadEach(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, *, each: _cal[[int], _T]) -> _AbroadEachInitializer[_T]: ...
    
    @classmethod
    def abroadEach(self, value1, /, value2 = None, modifier = None, *, each = None):
        """
        @lifetime >= 0.3.25 (experimental for 0.3.25 - 0.3.26b1)
        
        Invoked is `each` callback for every item in `abroad()` function.
        """
        
        if self.versionInfo >= (0, 3, 44) or True:
            
            if not self.isNone(each) and (not callable(each) or (callable(each) and reckon(_util.ParamVar(each).positional, _util.ParamVar(each).universal) != 1)):
                error = TypeError("expected 'None' or callable with one integer parameter not being keyword-only one")
                raise error
        
        else:
            
            if (not callable(each) and each is not None):
                error = TypeError("expected None or callable with one integer parameter")
                raise error
        
        # because TypeVars are objects themselves, we can pass an object list
        a = [0] if each is None else [object()]
        a.clear()
        
        for i in abroad(value1, value2, modifier):
            
            if each is None:
                a.append(i) # int
            
            else:
                a.append(each(i)) # object
        
        return a
    
    @classmethod
    def abroadHex(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, mode = ABROAD_HEX_INCLUDE):
        """
        @lifetime >= 0.3.25 (10.07.2024) \\
        @modified 0.3.52
        
        This variation of `abroad()` function returns hexadecimal representation of each integer.

        Modes (for 0.3.26rc2; to 0.3.27 support for integers):
        - `self.ABROAD_HEX_INCLUDE` - appends `0x` to each string. It faciliates casting to integer.
        - `self.ABROAD_HEX_INCLUDE_HASH` - appends `#` to each string. Reference from CSS.
        - `self.ABROAD_HEX_EXCLUDE` - nothing is appended.
        """
        a, ab = ([""], abroad(value1, value2, modifier))
        a.clear()
        
        for i in ab:
            
            if not isinstance(mode, _cl.AbroadHexMode):
                error = ValueError("expected a constant preceded with 'ABROAD_HEX_'")
                raise error
            
            elif mode == self.ABROAD_HEX_INCLUDE:
                a.append(hex(i))
                
            elif mode == self.ABROAD_HEX_HASH:
                a.append(_re.sub(r"^0x", "#", hex(i)))
                
            else:
                a.append(_re.sub(r"^0x", "", hex(i)))
        
        return a
    
    @classmethod
    def abroadBinary(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None, include_0b = True):
        """
        @lifetime >= 0.3.25 \\
        @modified 0.3.52
        
        This variation of `abroad()` function returns binary representation of each integer. \\
        Parameter `include_0b` allows to append `0b` before binary notation, what allows \\
        to faciliate casting to integer. Defaults to `True`
        """
        a, ab = ([""], abroad(value1, value2, modifier))
        a.clear()
        
        for i in ab:
            
            if not isinstance(include_0b, bool):
                error = TypeError("expected parameter 'include_0b' to be of type 'bool'.")
                raise error
            
            elif include_0b:
                a.append(bin(i))
                
            else:
                a.append(_re.sub(r"^0b", "", bin(i)))
                
        return a
    
    @classmethod
    def abroadOctal(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
        """
        @lifetime >= 0.3.25 \\
        @modified 0.3.52
        
        This variation of `abroad()` function returns octal representation of each integer. \\
        Every string will be preceded with `0o`
        """
        a, ab = ([""], abroad(value1, value2, modifier))
        a.clear()
        
        for i in ab:
            # if not isinstance(include_0o, bool):
            #    err, s = (TypeError, "Expected parameter 'include_0o' to be of type 'bool'.")
            #    raise err(s)
            # elif include_0o:
                a.append(oct(i))
            # else:
            #   a.append(re.sub(r"^0o", "", oct(i)))
        return a
    
    if False:
        
        @classmethod
        @__.deprecated("Deprecated since 0.3.46 and will be removed in 0.3.48")   
        def upgrade(self, aveytense = True):
            """
            @lifetime >= 0.3.36
            
            Console-specific method; alias to combination: `pip uninstall ...` + `pip install ...`
            
            `aveytense` option allows to upgrade AveyTense only if set to `True` (default value is `True`)
            """
            
            if aveytense:
                
                print(Color("Getting latest stable version of AveyTense...", 8, 69) % Color.BOLD_ITALIC)
                _subprocess.run([_sys.executable, "-m", "pip", "uninstall", "--yes", "AveyTense"])
                _subprocess.run([_sys.executable, "-m", "pip", "install", "AveyTense"])
            
            else:
                _st = Color("{}", 8, 69) % Color.BOLD_ITALIC
                _in = [_sys.executable, "-m", "pip", "install"]
                
                print(_st.format("Upgrade PyPi modules of your choice. Use appropriate module name(s). 'x' exits the program."))
                a = input(_st.format(">>> "))
                _pip_upgraded = False
                
                while a.lower() != "x":
                    
                    a = a.lower().strip()
                    
                    if a == "pip":
                        
                        if self.versionInfo >= (0, 3, 44) or True:
                            
                            if not _pip_upgraded:
                                _subprocess.run([_sys.executable, "py", "-m", "ensurepip", "--upgrade"])
                                _pip_upgraded = True
                                
                            else:
                                print("The 'pip' module has been already upgraded. There is no necessity upgrading this module again, unless you got a message that it can be upgraded via 'pip install --upgrade pip'")
                            
                        elif self.versionInfo >= (0, 3, 42) and self.versionInfo < (0, 3, 44) and False:
                            
                            print("On 0.3.42 gimmick with PyPa get-pip has been excised, consider manually downloading and running it as 'py get-pip.py' (assuming it is in the same directory)")
                            print("See more information there: https://github.com/pypa/get-pip")
                        
                        else:
                        
                            if not _pip_upgraded:
                                
                                import os.path
                                
                                _subprocess.run(["py", os.path.dirname(os.path.realpath(__file__)) + "\\_get_pip.py"])
                                _pip_upgraded = True
                                
                    else:
                        
                        _subprocess.run(_in[:3] + ["uninstall", "--yes", a])
                        _subprocess.run(_in + [a])
                        
                    a = input(_st.format(">>> "))
                
            return self
    
    @classmethod
    def architecture(self, executable = _sys.executable, bits = "", linkage = ""):
        """
        @lifetime >= 0.3.26rc2 (0.3.27a5: added optional parameters)
        
        Returns system's architecture
        """
        return _architecture(executable, bits, linkage)
    
    @classmethod
    def disassemble(
        self,
        x: _HaveCodeType = None,
        /,
        file: __.Optional[__.IO[str]] = None,
        depth: __.Optional[int] = None,
        showCaches = False,
        adaptive = False,
        showOffsets = False
    ):
        """
        @lifetime >= 0.3.26rc3
        
        Detach code of a class, type, function, methods and other compiled objects. \\
        If argument `x` is `None` (by default is `None`), disassembled is last traceback. \\
        See [`dis.dis()`](https://docs.python.org/3/library/dis.html#dis.dis) \\
        Modified 0.3.31: added missing parameter `showOffsets`
        """
        _dis.dis(x, file = file, depth = depth, show_caches = showCaches, adaptive = adaptive, show_offsets = showOffsets)
        return self
    
    # changeover 0.3.42
    if versionInfo >= (0, 3, 42) or True:
        
        @classmethod
        def timeit(self, statement: __.AVT_Callable[[], _Any], /):
            """
            @lifetime >= 0.3.26rc3 \\
            https://aveyzan.xyz/aveytense#aveytense.Tense.timeit
            
            A simplified version of [`timeit.timeit()`](https://docs.python.org/3/library/timeit.html#timeit.timeit).
            
            To invoke callable with arguments, use `lambda: <func-name>(...)`.
            """
            
            if not callable(statement) or util.ParamVar(statement).allCount != 0:
                
                error = TypeError("expected callable without any arguments")
                raise error
            
            c = _time.time()
            statement()
            return _time.time() - c
    
    else:
        
        @classmethod
        def timeit(
            self,
            statement: __.Optional[_Statement] = None,
            /,
            setup: __.Optional[_Statement] = None,
            timer: _Timer = TIMEIT_TIMER_DEFAULT,
            number = TIMEIT_NUMBER_DEFAULT,
            globals: __.Optional[__.AVT_Dict[str, _Any]] = None
            ):
            """
            @lifetime >= 0.3.26rc3
            ```
            "class method" in class Tense
            ```
            See [`timeit.timeit()`](https://docs.python.org/3/library/timeit.html#timeit.timeit) \\
            Return time execution for specific code scrap (`statement`). Basic use::

                Tense.timeit(lambda: pow(3, 2)) # 0.06483080000180053
                Tense.timeit(lambda: math.pow(3, 2)) # 0.1697132999979658
                Tense.timeit(lambda: Tense.pow(3, 2)) # 0.26907890000074985
            """
            return _timeit.timeit(
                stmt = "pass" if self.isNone(statement) else statement,
                setup = "pass" if self.isNone(setup) else setup,
                timer = timer,
                number = number,
                globals = globals
            )
        
    @classmethod
    def socket(self, family: _uni[int, _socket.AddressFamily] = -1, type: _uni[int, _socket.SocketKind] = -1, proto = -1, fileno: _opt[int] = None):
        """
        @lifetime >= 0.3.27a2
        ```
        "class method" in class Tense
        ```
        See [`socket.socket`](https://docs.python.org/3/library/socket.html#socket.socket)
        """
        return _socket.socket(family, type, proto, fileno)
    
    
    @classmethod
    def cast(self, v: _Any, t: __.AVT_Type[_T], /) -> _T: 
        """
        @lifetime >= 0.3.36
        
        Casts a value to specific type, keeping its primal state after type casting.
        """
        
        return v
    
    # OVERLOAD 0.3.34
    @classmethod
    @__.overload
    def shuffle(self, v: str) -> str: ...
    
    # >= 0.3.43
    @classmethod
    @__.overload
    def shuffle(self, v: _util.MutableString) -> _util.MutableString: ...
    
    @classmethod
    @__.overload
    def shuffle(self, v: _ab_mod.AbroadInitializer) -> __.AVT_List[int]: ...
    
    ## 0.3.42: Uniqual (AbstractSet) was in overload with Sequence and both returning 'list',
    # but now Uniqual instances will return 'set'; added Generator and Awaitable; Uniqual moved to
    # separate overload
    ## 0.3.45: After conclusion 'set' builtin cannot be shuffled nor reversed, it will actually
    # return a list. Uniqual is again in fusion with Sequence. Do NOT convert result to 'set'!
    @classmethod
    @__.overload
    def shuffle(self, v: __.Union[__.AVT_Sequence[_T], __.AVT_Uniqual[_T]]) -> __.AVT_List[_T]: ...
    
    if versionInfo >= (0, 3, 53) or True:
        
        @classmethod
        @__.overload
        def shuffle(self, v: __.AVT_Generator[_T_yield_cov, _T_send_con, _T_return_cov]) -> __.AVT_Generator[_T_yield_cov, _T_send_con, _T_return_cov]: ...
        
        @classmethod
        @__.overload
        def shuffle(self, v: __.AVT_AsyncGenerator[_T_yield_cov, _T_send_con]) -> __.AVT_AsyncGenerator[_T_yield_cov, _T_send_con]: ...
    
    else:
        
        @classmethod
        @__.overload
        def shuffle(self, v: __.Union[__.AVT_Generator[_T, _Any, _Any], __.AVT_Awaitable[_T]]) -> __.AVT_List[_T]: ...
        
    if versionInfo < (0, 3, 45) and False:
    
        @classmethod
        @__.overload
        def shuffle(self, v: __.AVT_Uniqual[_T]) -> __.AVT_Set[_T]: ...
        
        @classmethod
        @__.overload
        def shuffle(self, v: _SequenceGeneratorAwaitable[_T]) -> __.AVT_List[_T]: ...
    
    @classmethod
    @__.overload
    def shuffle(self, v: __.AVT_Mapping[_KT, _VT]) -> __.AVT_Dict[_KT, _VT]: ...
    
    @classmethod
    def shuffle(self, v):
        """
        @lifetime >= 0.3.26rc1 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.shuffle
        
        Shuffle a string, mapping or a sequence, and return shuffled iterable \\
        without changing passed iterable.
        """
        
        def _shuffle(x: __.AVT_Iterable[_T], /): # >= 0.3.42
            
            _placeholder = list(x)
            _random.shuffle(_placeholder)
            return _placeholder
            
        if self.isString(v):
            
            _v = "".join(_shuffle(v))
            
        elif isinstance(v, _util.MutableString):
            
            _v = _util.MutableString("".join(_shuffle(v.value)))
            
        elif isinstance(v, _ab_mod.AbroadInitializer):
            
            _v = _shuffle(+v)
            
        # 0.3.53: Shuffle generators
        elif isinstance(v, __.Generator):
            
            _v = self.generator(_shuffle(v))
            
        elif isinstance(v, __.AsyncGenerator):
            
            _v = self.asyncGenerator(_shuffle(_extract_from_async_iterable(v)))
    
        elif isinstance(v, __.Uniqual):
            
            if self.versionInfo >= (0, 3, 45):
                _v = _shuffle(v)
                
            else: # 0.3.45: part of code below doesn't actually work; returned set is sorted, hence list is returned
                _v = set(_shuffle(v))
            
        elif isinstance(v, __.Mapping):
            
            _v = {k: v[k] for k in _shuffle([k for k in v])}
        
        else:
            error = TypeError("expected a string, mapping, sequence, set, generator, or result of abroad() function")
            raise error
            
        return _v
    
    # OVERLOAD 0.3.34
    @classmethod
    @__.overload
    def reverse(self, v: str) -> str: ...
    
    # >= 0.3.43
    @classmethod
    @__.overload
    def reverse(self, v: _util.MutableString) -> _util.MutableString: ...
    
    @classmethod
    @__.overload
    def reverse(self, v: _ab_mod.AbroadInitializer) -> __.AVT_List[int]: ...
    
    ## 0.3.42: Uniqual (AbstractSet) was in overload with Sequence and both returning 'list',
    # but now Uniqual instances will return 'set'; added Generator and Awaitable; Uniqual moved to
    # separate overload
    ## 0.3.45: After conclusion 'set' builtin cannot be shuffled nor reversed, it will actually
    # return a list. Uniqual is again in fusion with Sequence. Do NOT convert result to 'set'!
    @classmethod
    @__.overload
    def reverse(self, v: __.Union[__.AVT_Sequence[_T], __.AVT_Uniqual[_T]]) -> __.AVT_List[_T]: ...
    
    if versionInfo >= (0, 3, 53) or True:
        
        @classmethod
        @__.overload
        def reverse(self, v: __.AVT_Generator[_T_yield_cov, _T_send_con, _T_return_cov]) -> __.AVT_Generator[_T_yield_cov, _T_send_con, _T_return_cov]: ...
        
        @classmethod
        @__.overload
        def reverse(self, v: __.AVT_AsyncGenerator[_T_yield_cov, _T_send_con]) -> __.AVT_AsyncGenerator[_T_yield_cov, _T_send_con]: ...
    
    else:
        
        @classmethod
        @__.overload
        def reverse(self, v: __.Union[__.AVT_Generator[_T, _Any, _Any], __.AVT_Awaitable[_T]]) -> __.AVT_List[_T]: ...
        
    if versionInfo < (0, 3, 45) and False:
    
        @classmethod
        @__.overload
        def reverse(self, v: __.AVT_Uniqual[_T]) -> __.AVT_Set[_T]: ...
        
        @classmethod
        @__.overload
        def reverse(self, v: _SequenceGeneratorAwaitable[_T]) -> __.AVT_List[_T]: ...
    
    @classmethod
    @__.overload
    def reverse(self, v: __.AVT_Mapping[_KT, _VT]) -> __.AVT_Dict[_KT, _VT]: ...
    
    # >= 0.3.42
    @classmethod
    @__.overload
    def reverse(self, v: __.AVT_Reversible[_T]) -> __.AVT_Iterator[_T]: ...
    
    @classmethod
    def reverse(self, v):
        """
        @lifetime >= 0.3.26rc2 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.reverse
        
        Reverse a string, mapping or sequence, and return reversed iterable \\
        without changing passed iterable.
        """
        
        if self.isString(v):
            
            _v = v[::-1]
            
        elif isinstance(v, _util.MutableString):
            
            # ~.util.MutableString.reverse() implemented on 0.3.45
            if self.versionInfo >= (0, 3, 45):
                v.reverse()
                _v = _util.MutableString(v) # 0.3.45: allow instances of this class to the constructor
                v.reverse()
                
            else:
                _v = _util.MutableString(v.value[::-1])
            
        elif isinstance(v, _ab_mod.AbroadInitializer):
            
            _v = (+v)[::-1]
            
        # 0.3.53: Reverse generators
        elif isinstance(v, __.Generator):
            
            _v = self.generator(list(v)[::-1])
            
        elif isinstance(v, __.AsyncGenerator):
            
            _v = self.asyncGenerator(list(_extract_from_async_iterable(v))[::-1])
        
        elif isinstance(v, __.Uniqual): # >= 0.3.42
            
            if self.versionInfo >= (0, 3, 45):
                _v = list(v)[::-1]
                
            else: # 0.3.45: part of code below doesn't actually work; returned set is sorted ascendingly, hence list is returned
                _v = { *tuple(list(v)[::-1]) }
        
        elif isinstance(v, __.Sequence):
            
            _v = list(v)[::-1]
        
        # 'dict' objects normally do not include the 'reverse' method
        elif isinstance(v, __.Mapping):
            
            _v = {k: v[k] for k in [k2 for k2 in v][::-1]}
        
        elif isinstance(v, __.Reversible): #>= 0.3.42
            
            return reversed(v)
            
        else:
            error = TypeError("expected a string, mapping, sequence, set, generator, or result of abroad() function")
            raise error
        
        return _v
    
    # OVERLOAD 0.3.34
    @classmethod
    @__.overload
    def occurrences(self, v: str, *items: str, mode: _lit["case_sensitive"] = "case_sensitive") -> int: ...
    
    @classmethod
    @__.overload
    def occurrences(self, v: str, *items: str, mode: _lit["case_insensitive"]) -> int: ...
    
    @classmethod
    @__.overload
    def occurrences(self, v: _ab_mod.AbroadInitializer, *items: int, mode: _lit["normal"] = "normal") -> int: ...
    
    @classmethod
    @__.overload
    def occurrences(self, v: _ab_mod.AbroadInitializer, *items: int, mode: _lit["absolute"]) -> int: ...
    
    @classmethod
    @__.overload
    def occurrences(self, v: _uni[__.AVT_Sequence[_T], __.AVT_Uniqual[_T]], *items: _T) -> int: ...
    
    @classmethod
    @__.overload
    def occurrences(self, v: __.AVT_Mapping[_KT, _VT], *items: _KT, mode: _lit["key"] = "key") -> int: ...
    
    @classmethod
    @__.overload
    def occurrences(self, v: __.AVT_Mapping[_KT, _VT], *items: _VT, mode: _lit["value"]) -> int: ...
    
    @classmethod
    def occurrences(self, v, *items, mode = "case_sensitive"):
        """
        @lifetime >= 0.3.32 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.occurrences
        
        Returns number of how many times specified item appears \\
        or items appear in a sequence
        """
        
        o = 0
        m = mode.lower()
        
        if not self.isString(mode):
            
            error = TypeError("parameter 'mode' is not a string")
            raise error
        
        if m not in ("case_sensitive", "case_insensitive", "normal", "absolute", "key", "value"):
            
            error = ValueError("parameter 'mode' provides invalid mode")
            raise error
        
        if isinstance(v, (str, _ab_mod.AbroadInitializer, __.Sequence, __.Uniqual, __.Mapping)) and reckon(v) == 0:
            return 0
        
        if self.isString(v):
            
            if m not in ("case_sensitive", "case_insensitive"):
                
                error = ValueError("for strings parameter 'mode' can take one of 2 modes: 'case_sensitive' and 'case_insensitive'")
                raise error
            
            
            _v = v.split()
            _s = list(items)
            
            if not self.isList(_s, str):
                
                error = ValueError("parameter 'items' doesn't utterly consist of string items")
                raise error
            
            if m == "case_insensitive":
                _s = [self.cast(s, str).lower() for s in items]
                
            for s in _v:
                
                if (s in _s and m == "case_sensitive") or (s.lower() in _s and m == "case_insensitive"):
                    o += 1
                    
            return o
                    
        elif isinstance(v, _ab_mod.AbroadInitializer):
            
            if m not in ("normal", "absolute"):
                
                error = ValueError("for instances of internal class being result of abroad() function ({} class objects), parameter 'mode' can take one of 2 modes: 'normal' and 'absolute'".format(_ab_mod.AbroadInitializer.__name__))
                raise error
            
            _i = list(items)
            
            if not self.isList(_i, int):
                
                error = ValueError("parameter 'items' doesn't utterly consist of integer items")
                raise error
            
            if m == "absolute":
                _i = [abs(i) for i in items]
                
                
            for i in v:
                
                if (i in _i and m == "normal") or (abs(i) in _i and m == "absolute"):
                    o += 1
                    
            return o
                    
        elif isinstance(v, (__.Sequence, __.Uniqual)):
            
            _v = list(v)
            
            for e in _v:
                
                if e in items:
                    o += 1
                    
            return o
                    
        elif isinstance(v, __.Mapping):
            
            if m not in ("key", "value"):
                
                error = ValueError("for mappings parameter 'mode' can take one of 2 modes: 'key' and 'value'")
                raise error
            
            if m == "key":
                _v = list(v.keys())
                
            else:
                _v = list(v.values())
                
            for e in _v:
                
                if e in items:
                    o += 1
                    
            return o
            
        else:
            error = TypeError("expected a string, mapping, sequence or result of abroad() function")
            raise error
                    
    # OVERLOAD 0.3.34
    @classmethod
    @__.overload
    def difference(self, v1: __.AVT_Type[_T1], v2: __.AVT_Type[_T2], /, invert: bool = False, value_check: bool = True) -> __.AVT_List[str]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: __.AVT_Type[_T1], v2: __.AVT_Mapping[str, _T2], /, invert: bool = False, value_check: bool = True) -> __.AVT_List[str]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: __.AVT_Mapping[str, _T1], v2: type[_T2], /, invert: bool = False, value_check: bool = True) -> __.AVT_List[str]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: __.AVT_Mapping[_KT1, _VT1], v2: __.AVT_Mapping[_KT2, _VT2], /, invert: _lit[False] = False, value_check: bool = True) -> __.AVT_List[_KT1]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: __.AVT_Mapping[_KT1, _VT1], v2: __.AVT_Mapping[_KT2, _VT2], /, invert: _lit[True], value_check: bool = True) -> __.AVT_List[_KT2]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: __.AVT_Type[_T], v2: _uni[__.Sequence[str], __.Uniqual[str]], /, invert: bool = False, value_check: bool = True) -> __.AVT_List[str]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: _uni[__.Sequence[str], __.Uniqual[str]], v2: __.AVT_Type[_T], /, invert: bool = False, value_check: bool = True) -> __.AVT_List[str]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: _ab_mod.AbroadInitializer, v2: _uni[__.Sequence[int], __.Uniqual[int]], /, invert: bool = False) -> __.AVT_List[int]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: _uni[__.Sequence[int], __.Uniqual[int]], v2: _ab_mod.AbroadInitializer, /, invert: bool = False) -> __.AVT_List[int]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: _ab_mod.AbroadInitializer, v2: _ab_mod.AbroadInitializer, /, invert: bool = False) -> __.AVT_List[int]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: _uni[__.Sequence[_T1], __.Uniqual[_T1]], v2: _uni[__.Sequence[_T2], __.Uniqual[_T2]], /, invert: _lit[False] = False) -> __.AVT_List[_T1]: ...
    
    @classmethod
    @__.overload
    def difference(self, v1: _uni[__.Sequence[_T1], __.Uniqual[_T1]], v2: _uni[__.Sequence[_T2], __.Uniqual[_T2]], /, invert: _lit[True]) -> __.AVT_List[_T2]: ...
    
    @classmethod
    def difference(self, v1, v2, /, invert = False, value_check = True):
        """
        @lifetime >= 0.3.32
        
        Find items, which belong to `v1`, but do not belong to `v2` (math difference `v1 \\ v2`). \\
        With `invert` being `True` it is vice versa (`v2 \\ v1`).
        
        When `value_check` is `True`, values from fields in classes or dictionairies will be also checked. \\
        In this case when values are different, then they are included in the returned list.
        
        For class fields with roundly underscored names, these fields aren't counted.
        """
        _v1, _v2 = [{} for _ in abroad(2)]
        
        if isinstance(v1, type):
            
            if isinstance(v2, type):
                
                _v1 = {k: v1.__annotations__[k] for k in v1.__annotations__ if k[:1] != "_"}
                _v2 = {k: v2.__annotations__[k] for k in v2.__annotations__ if k[:1] != "_"}
            
            elif isinstance(v2, __.Mapping):
                
                if not self.isList([k for k in v2], str):
                    
                    error = ValueError("with comparison with a class expected a string-key-typed mapping")
                    raise error
                
                _v1 = {k: v1.__annotations__[k] for k in v1.__annotations__ if k[:1] != "_"}
                _v2 = {k: v2[k] for k in v2 if k[:1] != "_"}
            
            elif isinstance(v2, (__.Sequence, __.Uniqual)):
                
                if not self.isList([k for k in v2], str):
                    
                    error = ValueError("with comparison with a class expected a string-typed sequence")
                    raise error
                
                _v1 = [k for k in v1.__annotations__]
                _v2 = list(v2)
                
            else:
                error = TypeError("with comparison with a class expected another class or string sequence, mapping with string keys")
                raise error
        
        elif isinstance(v1, __.Mapping):
            
            if isinstance(v2, type):
                
                if not self.isList([k for k in v1], str):
                    
                    error = ValueError("with comparison with a class expected a string-key-typed mapping")
                    raise error
                
                _v1 = {k: v1[k] for k in v1 if k[:1] != "_"}
                _v2 = {k: v2.__annotations__[k] for k in v2.__annotations__ if k[:1] != "_"}
                
            elif isinstance(v2, __.Mapping):
                
                _v1 = {k: v1[k] for k in v1 if k[:1] != "_"}
                _v2 = {k: v2[k] for k in v2 if k[:1] != "_"}
                
            else:
                error = TypeError("with comparison with a mapping expected another mapping or a class")
                raise error
        
        elif isinstance(v1, _ab_mod.AbroadInitializer):
            
            if isinstance(v2, _ab_mod.AbroadInitializer):
                
                _v1 = +v1
                _v2 = +v2
                
                if invert:
                    return [e for e in _v1 if e not in _v2]
                
                else:
                    return [e for e in _v2 if e not in _v1]
                
            elif isinstance(v2, (__.Sequence, __.Uniqual)):
                
                if not self.isList([e for e in v2], int):
                    
                    error = ValueError("with comparison with a result from abroad() function expected an integer sequence")
                    raise error
                
                _v1 = +v1
                _v2 = list(v2)
                
            else:
                error = TypeError("with comparison with a result from abroad() function expected another abroad() function result or integer sequence")
                raise error
            
        elif isinstance(v1, (__.Sequence, __.Uniqual)):
            
            if isinstance(v2, type):
                
                if not self.isList([k for k in v1], str):
                    
                    error = ValueError("with comparison with a class expected a string-typed sequence")
                    raise error
                
                _v1 = list(v1)
                _v2 = [k for k in v2.__annotations__]
                
            elif isinstance(v2, _ab_mod.AbroadInitializer):
                
                if not self.isList([e for e in v2], int):
                    
                    error = ValueError("with comparison with a result from abroad() function expected an integer sequence")
                    raise error
                
                _v1 = list(v1)
                _v2 = +v2
                
            elif isinstance(v2, (__.Sequence, __.Uniqual)):
                
                _v1 = list(v1)
                _v2 = list(v2)
                
        if invert:
            _v1, _v2 = _v2, _v1
            
        _res = [k for k in _v1 if k not in _v2]
        
        if value_check and isinstance(_v1, dict) and isinstance(_v2, dict):
            
            for k in _v1:
                
                if k in _v2 and _v1[k] != _v2[k]:
                    _res.append(k)
        
        _res.sort()
        return _res
    
    # OVERLOAD 0.3.34
    @classmethod
    @__.overload
    def intersection(self, v: int, /, *_: int) -> int: ...
    
    @classmethod
    @__.overload
    def intersection(self, v: bool, /, *_: bool) -> bool: ...
    
    @classmethod
    @__.overload
    def intersection(self, v: __.AVT_Iterable[_T], /, *_: __.AVT_Iterable[_Any]) -> __.AVT_List[_T]: ...
                        
    @classmethod
    def intersection(self, v, /, *_):
        """
        @lifetime >= 0.3.34
        
        Returns list of items, which appear in all sequences (math intersection `v1 \u2229 v2 \u2229 ... \u2229 vN`). \\
        In case of integers returned is bitwise AND (`&`) taken on all integers. \\
        In case of boolean values returned is logical AND (`and`) taken on all boolean values.
        """
        if isinstance(v, bool):
            
            if reckon(_) == 0:
                return v
            
            else:
                
                if not self.isList([e for e in _], bool):
                    
                    error = ValueError("expected every value a boolean value")
                    raise error
                
                _v = v
                
                for e in _:
                    _v = _v and e
                    
                return _v
        
        elif isinstance(v, int):
            
            if reckon(_) == 0:
                return v
            
            else:
                
                if not self.isList([e for e in _], int):
                    
                    error = ValueError("expected every value an integer")
                    raise error
                
                _v = v
                
                for e in _:
                    _v &= e
                    
                return _v
            
        elif isinstance(v, __.Iterable):
            
            if reckon(_) == 0:
                return list(v)
            
            else:
                
                _pre = list(_)
                
                if _sys.version_info >= (3, 9):
                    _checkery = bool(self.isList(_pre, __.Iterable))
                    
                else:
                    _checkery = self.all(_pre, lambda x: issubclass(type(x), __.Iterable))
                
                if not _checkery:
                    
                    error = ValueError("expected every value an iterable")
                    raise error
                
                return list(set(v).intersection(*_))
            
        else:
            error = TypeError("expected every value either integers, boolean values or iterable objects")
            raise error
    
    # OVERLOAD 0.3.34
    @classmethod
    @__.overload
    def union(self, v: int, /, *_: int) -> int: ...
    
    @classmethod
    @__.overload
    def union(self, v: bool, /, *_: bool) -> bool: ...
    
    @classmethod
    @__.overload
    def union(self, v: __.AVT_Iterable[_T1], /, *_: __.AVT_Iterable[_T2]) -> __.AVT_List[_uni[_T1, _T2]]: ...
    
    @classmethod
    def union(self, v, /, *_):
        """
        @lifetime >= 0.3.34
        
        Returns list of items, which appear in any sequences (math union `v1 \u222A v2 \u222A ... \u222A vN`). \\
        In case of integers returned is bitwise OR (`|`) taken on all integers. \\
        In case of boolean values returned is logical OR (`or`) taken on all boolean values.
        """
        
        if isinstance(v, bool):
            
            if reckon(_) == 0:
                return v
            
            else:
                
                if not self.isList([e for e in _], bool):
                    
                    error = ValueError("expected every value a boolean value")
                    raise error
                
                _v = v
                
                for e in _:
                    _v = _v or e
                    
                return _v
        
        elif isinstance(v, int):
            
            if reckon(_) == 0:
                return v
            
            else:
                
                if not self.isList([e for e in _], int):
                    
                    error = ValueError("expected every value an integer")
                    raise error
                
                _v = v
                
                for e in _:
                    _v |= e
                    
                return _v
            
        elif isinstance(v, __.Iterable):
            
            if reckon(_) == 0:
                return list(v)
            
            else:
                
                _pre = list(_)
                
                if _sys.version_info >= (3, 9):
                    _checkery = bool(self.isList(_pre, __.Iterable))
                    
                else:
                    _checkery = self.all(_pre, lambda x: issubclass(type(x), __.Iterable))
                
                if not _checkery:
                    
                    error = ValueError("expected every value an iterable")
                    raise error
                
                return list(set(v).union(*_))
            
        else:
            error = TypeError("expected every value either integers, boolean values or iterable objects")
            raise error
    
    @classmethod
    @__.overload
    def append(self, i: __.AVT_Mapping[_KT1, _VT1], /, *items: __.AVT_Tuple[_KT2, _VT2]) -> __.AVT_Dict[__.Union[_KT1, _KT2], __.Union[_VT1, _VT2]]: ...
    
    @classmethod
    @__.overload
    def append(self, i: __.AVT_Iterable[_T1], /, *items: _T2) -> __.AVT_List[__.Union[_T1, _T2]]: ...
    
    @classmethod
    def append(self, i, /, *items):
        """
        @lifetime >= 0.3.27a4 \\
        @standard-lifetime >= 0.3.39 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.append
        
        Same as `list.append()`, just variable amount of items can be passed. \\
        Input list remains non-modified, and returned is its modified copy.
        
        Since 0.3.34, because mutable sequences are normally coerced to list, allowed are also \\
        all other iterables
        
        Since 0.3.46 mappings are allowed; `items` may only contain 2-item tuples in this case
        """
        
        if self.versionInfo >= (0, 3, 46) or True:
            
            if isinstance(i, __.Mapping) and self.all(items, lambda x: self.isTuple(x) and reckon(x) == 2):
                
                return dict([(k, i[k]) for k in i] + [e for e in items])
            
            elif isinstance(i, __.Iterable):
                
                return list(i) + list(items)
            
            else:
                
                error = TypeError("expected a mapping + 2-item tuples or an iterable")
                raise error
        
        else: # 0.3.41
            
            if not isinstance(i, __.Iterable):
                error = TypeError("expected an iterable")
                raise error
            
            return list(i) + list(items)
    
    @classmethod
    @__.overload
    def extend(self, i: __.AVT_Mapping[_KT1, _VT1], /, *iters: __.AVT_Mapping[_KT2, _VT2]) -> __.AVT_Dict[_uni[_KT1, _KT2], _uni[_VT1, _VT2]]: ...
    
    @classmethod
    @__.overload
    def extend(self, i: __.AVT_Iterable[_T1], /, *iters: __.AVT_Iterable[_T2]) -> __.AVT_List[_uni[_T1, _T2]]: ...
    
    @classmethod
    def extend(self, i, /, *iters):
        """
        @lifetime >= 0.3.27a4 \\
        @standard-lifetime >= 0.3.39 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.extend
        
        Same as `list.extend()`, just variable amount of iterables can be passed. \\
        Input list remains non-modified, and returned is its modified copy.
        
        Since 0.3.34, because mutable sequences are normally coerced to list, allowed are also \\
        all other iterables
        
        Since 0.3.46 mappings are allowed; in this case all items in `i2` must be mappings too.
        """
        
        if self.versionInfo >= (0, 3, 46) or True:
            
            if _sys.version_info >= (3, 9):
                _checkery = (
                    self.isTuple(iters, __.Mapping),
                    self.isTuple(iters, __.Iterable)
                )
                
            else:
                _checkery = (
                    self.all(iters, lambda x: issubclass(type(x), __.Mapping)),
                    self.all(iters, lambda x: issubclass(type(x), __.Iterable))
                )
                
            if isinstance(i, __.Mapping) and _checkery[0]:
                
                return dict([(k, i[k]) for k in i] + [(k, e[k]) for e in iters for k in e])
            
            elif isinstance(i, __.Iterable) and _checkery[1]:
                
                return [e for e in i] + [e for iterable in iters for e in iterable]
            
            else:
                
                error = TypeError("expected mappings only or iterables only")
                raise error
                
            
        else:
            
            # 0.3.41 - 0.3.45
            if not isinstance(i, __.Iterable):
                error = TypeError("expected an iterable")
                raise error
            
            return [e for e in i] + [e for iterable in iters for e in iterable]
    
    if versionInfo >= (0, 3, 50) or True:
    
        @classmethod
        @__.overload
        def exclude(self, i: __.AVT_Mapping[_KT, _VT], /, *items: _KT, filter: __.Literal["keys"] = "keys") -> __.AVT_Dict[_KT, _VT]: ...
        
        @classmethod
        @__.overload
        def exclude(self, i: __.AVT_Mapping[_KT, _VT], /, *items: _VT, filter: __.Literal["values"]) -> __.AVT_Dict[_KT, _VT]: ...
    
    else:
        
        @classmethod
        @__.overload
        def exclude(self, i: __.AVT_Mapping[_KT, _VT], /, *items: _KT, filter: __.Literal["keys", "values"] = "keys") -> __.AVT_Dict[_KT, _VT]: ...
    
    @classmethod
    @__.overload
    def exclude(self, i: __.AVT_Iterable[_T], /, *items: _T) -> __.AVT_List[_T]: ...
    
    @classmethod
    def exclude(self, i, /, *items, filter = "keys"):
        """
        @lifetime >= 0.3.34 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.exclude
        
        Return a new list from iterable without items specified.
        
        Since 0.3.46 mappings are allowed. Keyword-only parameter `filter` *only* take place for mappings, \\
        and can only contain case-sensitive string values: `"keys"` or `"values"`
        """
        if self.versionInfo >= (0, 3, 46) or True:
            
            if isinstance(i, __.Mapping):
                
                if filter == "keys":
                    return dict([(k, i[k]) for k in i if k not in items])
                
                elif filter == "values":
                    return dict([(k, i[k]) for k in i if i[k] not in items])
                
                else:
                    error = TypeError("invalid value for 'filter' parameter, expected either 'keys' or 'values' (case sensitive)")
                    raise error
                
            elif isinstance(i, __.Iterable):
                
                return [e for e in i if e not in items]
            
            else:
                
                error = TypeError("expected a mapping or an iterable")
                raise error
            
        else:
            return [e for e in i if e not in items]
        
    @classmethod
    @__.overload
    def extract(self, i: __.AVT_Mapping[_KT, _VT], /, condition: __.AVT_Callable[[_KT], bool] = ...) -> __.AVT_Dict[_KT, _VT]: ...
        
    @classmethod
    @__.overload
    def extract(self, i: __.AVT_Mapping[_KT, _VT], /, condition: __.AVT_Callable[[_KT, _VT], bool]) -> __.AVT_Dict[_KT, _VT]: ...
    
    @classmethod
    @__.overload
    def extract(self, i: __.AVT_Iterable[_T], /, condition: __.AVT_Callable[[_T], bool] = ...) -> __.AVT_List[_T]: ...
        
    @classmethod
    def extract(self, i, /, condition = ...):
        """
        @lifetime >= 0.3.52
        
        Extracts items from a mapping or iterable which satisfy given `condition`, and returns them in a dictionary or list.
        
        This class method is almost the same as  `~.Tense.expect()`, just a new copy of an iterable/mapping is returned, \\
        and there is no quantity specifier `m`.
        """
        
        if isinstance(i, __.Mapping):
            
            if self.isEllipsis(condition) or reckon(i) == 0:
                return dict(i)
            
            elif self.isLambda(condition):
                p = util.ParamVar(condition)
                key, value = list(i.keys())[0], list(i.values())[0]
                
                if p.positionalCount + p.universalCount == p.allCount == 1:
                    
                    if not isinstance(condition(key), bool):
                        error = TypeError("lambda expression must return a boolean value")
                        raise error
                    
                    return dict([(k, i[k]) for k in i if condition(k)])
                
                elif p.positionalCount + p.universalCount == p.allCount == 2:
                    
                    if not isinstance(condition(key, value), bool):
                        error = TypeError("lambda expression must return a boolean value")
                        raise error
                    
                    return dict([(k, i[k]) for k in i if condition(k, i[k])])
                
                else:
                    error = TypeError("expected one or two parameter in a lambda expression")
                    raise error
                
            else:
                error = TypeError("expected a lambda expression")
                raise error
            
        elif self.isIterable(i):
            
            if self.isEllipsis(condition) or reckon(i) == 0:
                return list(i)
            
            elif self.isLambda(condition):
                p = util.ParamVar(condition)
                e = list(i)[0]
                
                if isinstance(condition(e), bool) and p.positionalCount + p.universalCount == p.allCount == 1:
                    return list([elem for elem in i if condition(elem)])
                
                else:
                    error = TypeError("expected a lambda expression with one parameter")
                    raise error
            
            else:
                error = TypeError("expected a lambda expression")
                raise error
            
        else:
            error = TypeError("expected a mapping or iterable")
            raise error
    
    @classmethod
    def explode(self, s: str, /, separator: _opt[str] = None, max = -1, no_empty = False):
        """
        @lifetime >= 0.3.34
        
        Reference from PHP inbuilt function `explode()`. Split a string \\
        using specified separator into a string list.
        """
        _params = _get_all_params(self.explode)
        
        # error message template
        _msgtmpl = "expected {} in parameter '{}'"
        
        _msg = ["" for _ in abroad(_params)]
        _msg[0] = _msgtmpl.format("a string", _params[0])
        _msg[1] = _msgtmpl.format("a string or None", _params[1])
        _msg[2] = _msgtmpl.format("an integer for -1 above (not being zero)", _params[2])
        
        if not self.isString(s):
            error = TypeError(_msg[0])
            raise error
        
        if not self.isString(separator) and not self.isNone(separator):
            error = TypeError(_msg[1])
            raise error
        
        if not self.isInteger(max) or (self.isInteger(max) and max != -1 and max < 1):
            error = TypeError(_msg[2])
            raise error
        
        if no_empty: 
            return [k for k in s.split(separator, max) if reckon(k) != 0]
        
        return s.split(separator, max)
    
    @classmethod
    @__.overload
    def removePrefix(self, o: str, prefix: str, /) -> str: ...
    
    @classmethod
    @__.overload
    def removePrefix(self, o: bytes, prefix: __.ReadableBuffer, /) -> bytes: ...
    
    @classmethod
    def removePrefix(self, o, prefix, /):
        """
        @lifetime >= 0.3.53
        
        Re-implement PEP 616
        
        Return copy of string or bytes object if prefix was not found,
        otherwise return copy without specific prefix.
        """
        
        if self.isString(o) and self.isString(prefix):
            
            # re-implement pep 616
            if _sys.version_info >= (3, 9):
                return o.removeprefix(prefix)
            else:
                return o[reckon(prefix):] if o.startswith(prefix) else o[:]
            
        elif self.isBytes(o) and isinstance(prefix, __.ReadableBuffer):
            
            if _sys.version_info >= (3, 9):
                return o.removeprefix(prefix)
            else:
                return o[reckon(prefix):] if o.startswith(prefix) else o[:]
            
        else:
            error = TypeError("expected 'str' + 'str' or 'bytes' + 'buffer'")
            raise error
        
    @classmethod
    @__.overload
    def removeSuffix(self, o: str, suffix: str, /) -> str: ...
    
    @classmethod
    @__.overload
    def removeSuffix(self, o: bytes, suffix: __.ReadableBuffer, /) -> bytes: ...
    
    @classmethod
    def removeSuffix(self, o, suffix, /):
        """
        @lifetime >= 0.3.53
        
        Re-implement PEP 616
        
        Return copy of string or bytes object if suffix was not found,
        otherwise return copy without specific suffix.
        """
        
        if self.isString(o) and self.isString(suffix):
            
            # re-implement pep 616
            if _sys.version_info >= (3, 9):
                return o.removesuffix(suffix)
            else:
                return o[:reckon(suffix)] if suffix and o.endswith(suffix) else o[:]
            
        elif self.isBytes(o) and isinstance(suffix, __.ReadableBuffer):
            
            if _sys.version_info >= (3, 9):
                return o.removesuffix(suffix)
            else:
                return o[:reckon(suffix)] if suffix and o.endswith(suffix) else o[:]
            
        else:
            error = TypeError("expected 'str' + 'str' or 'bytes' + 'buffer'")
            raise error
    
    if _version.VERSION_INFO >= (0, 3, 40) or True:

        @classmethod # below: append 'typing.IO[Any]' when tests are done on 0.3.48
        def clear(self, *v: _Clearable): # 0.3.27a4
            """
            @lifetime >= 0.3.27a4 \\
            https://aveyzan.xyz/aveytense#aveytense.Tense.clear
            
            Same as `[list/set/dict].clear()`, just variable amount of lists/sets/dictionaries can be passed. \\
            This type list includes strings and instances of `types.FrameType`.
            
            Supported types (since: + type):
            - originally - mutable sequences
            - 0.3.27b1 - strings
            - 0.3.36 - mutable sets
            - 0.3.37 - mutable dictionaries and instances of `~.Color`
            - 0.3.40 - instances of `types.FrameType` (and fixed strings)
            - 0.3.42 - any objects of classes implementing `clear()` with no arguments, \\
                and instances of `~.util.MutableString`
            - 0.3.50 - file objects
            """
            
            # This doesn't seem as a secure idea, but had to do it since strings are immutable
            # and on this method they are here to be cleared. Only way to clear the string
            # is getting the variable passed to the parameter, which is a string. Basically this
            # is a technique without 'varname' PyPi project.
            
            # Answer is from Stack Overflow https://stackoverflow.com/a/18425523, only revamped it
            # so it can apply to arbitrary amount of arguments. F-string won't work there, as it
            # would be f"{n=}".split("=")[0], referring to 'n', not to any passed variables.
            # 24.02.2025
            
            _frame = _inspect.currentframe().f_back.f_locals
            _getvars = {name: val for name, val in _frame.items() if val in v and self.isString(val)}
                
            # We are assuming variables are defined and won't require pre-definition.
            # If it happened, then we would need to put another exec() invocation in
            # a loop, just as:
            #
            # for n, _v in _getvars.items():
            #     exec("{} = \"{}\"".format(n, _v), _frame)
            
            # If string was a literal, then deduced string will not be empty, original string value will
            # be kept (if we mention typing), but in reality string is cleared. Alternatively, you can do
            # something like this: a1, a2, a3 = ["" for _ in range(3)]
            # 10.03.2025
            
            for e in _getvars:
                exec("{} = \"\"".format(e), _frame)
            
            for _v in v:
                
                # Code below will work for literal strings only, but it is not advisable.
                # We can also omit string type checking (in case of literals nothing really
                # occurs, so in this case 'pass' may be used)
                
                if self.isString(_v):
                    
                    if reckon(_v) > 0:
                        _v = ""
                    
                else:
                    
                    # ~.Color (pre-defined; class overall)
                    if isinstance(_v, Color):
                        _v.clear()
                    
                    # Lists, sets, dictionaries, ... Just with one invocation
                    elif isinstance(_v, (
                        
                        __.MutableSequence,
                        __.MutableUniqual,
                        __.MutableMapping,
                        _util.MutableString,
                        __.FrameType
                        
                    )):
                        
                        _v.clear()
                    
                    # 0.3.50
                    elif isinstance(_v, __.IO): 
                        
                        _name_ = _v.name
                        
                        if not _v.closed:
                            _v.close()
                        
                        open(_name_, "w").close()
                    
                    # 0.3.42
                    elif isinstance(_v, _ClearableAbc) or (hasattr(_v, "clear") and callable(_v.clear)):
                        
                        _clear = self.cast(_v.clear, __.FunctionType)
                        p = util.ParamVar(_clear)
                        
                        if p.allCount == 0:
                            
                            _clear()
                        
                    else:
                        error = ValueError("expected a mutable sequence, mutable mapping, instance of 'types.FrameType', 'aveytense.util.MutableString' or 'aveytense.Color', or a string")
                        raise error
            
    else:
        
        @classmethod
        def clear(self, *v: __.Union[__.AVT_MutableSequence[_T], __.AVT_MutableUniqual[_T], __.AVT_MutableMapping[_Any, _T], Color, str]):
            """
            @lifetime >= 0.3.27a4
            ```ts
            "class method" in class Tense
            ```
            Same as `list.clear()`, just variable amount of lists can be passed. \\
            Since 0.3.27b1 strings are also passable. Since 0.3.36 - sets, and since \\
            0.3.37 - mutable mappings/dictionairies.
            """
            for seq in v:
                
                # 5 defintions
                if self.isString(seq):
                    seq = ""
                    
                elif isinstance(seq, (__.MutableSequence, __.MutableUniqual, __.MutableMapping, Color)):
                    seq.clear()
                    
                else:
                    error = ValueError("expected a mutable sequence, mutable mapping, instance of 'tense.Color' or string")
                    raise error
                
    @classmethod
    def copy(self, x: _T):
        """
        @lifetime >= 0.3.34
        
        Same as `copy.copy()`.
        """
        return _copy.copy(x)
    
    @classmethod
    def deepcopy(self, x: _T, memo: _opt[__.AVT_Dict[int, _Any]] = None, _nil: _Any = []):
        """
        @lifetime >= 0.3.34
        
        Same as `copy.deepcopy()`.
        """
        return _copy.deepcopy(x, memo, _nil)
    
    @classmethod
    def flatten(self, i: __.AVT_Iterable[__.AVT_Iterable[_T]], /):
        """
        @lifetime >= 0.3.49
        
        Same as `itertools.chain.from_iterable()`, just converted to a list. \\
        Since 0.3.50 returned is generator
        """
        
        if not isinstance(i, __.Iterable):
            error = TypeError("passed object isn't iterable")
            raise error
        
        l = self.cast([], __.AVT_List[_T])
        
        _get_ = [([e] if isinstance(e, (str, bytes)) else e) for e in i]
        
        for e in _get_:
            l.extend(e)
        
        return self.generator(l)
        
        # return list(_itertools.chain.from_iterable(i))
        
    @classmethod
    def generator(self, i: __.AVT_Iterable[_T], /, condition: __.AVT_Callable[[_T], bool] = ...):
        """
        @lifetime >= 0.3.50
        
        Creates a generator (before 0.3.53 with generator expression) using an iterable
        """
        
        if not isinstance(i, __.Iterable):
            error = TypeError("passed object isn't iterable")
            raise error
        
        if True: # >= 0.3.53
            
            def _gen_(iterable: __.AVT_Iterable[_T]):
                
                nonlocal condition
                
                if self.isEllipsis(condition):
                    yield from iterable # see pep 380 (>=Py3.3)
                        
                elif _is_bool_callback(condition):
                    yield from [e for e in iterable if condition(e)]
                            
                else:
                    error = TypeError("expected ellipsis or callable object with one parameter only")
                    raise error
                
            gen = _gen_(i)
            gen.__qualname__ = "<aveytense_generator>"
            return gen
            
        else:
            if self.isEllipsis(condition):
                return (e for e in i)
            
            else:
                
                if _is_bool_callback(condition):
                    return (e for e in i if condition(e))
                
                else:
                    error = TypeError("expected one parameter only")
                    raise error
            
    @classmethod
    def asyncGenerator(self, i: __.AVT_Iterable[_T], /, condition: __.AVT_Callable[[_T], bool] = ...):
        """
        @lifetime >= 0.3.53
        
        Creates an asynchronous generator using an iterable
        """
        
        if not isinstance(i, __.Iterable):
            error = TypeError("passed object isn't iterable")
            raise error
        
        async def _asyncgen_(iterable: __.AVT_Iterable[_T]):
            
            nonlocal condition
            
            if self.isEllipsis(condition):
                for e in iterable: # pep 380 is not allowed in async functions
                    yield e
                    
            elif _is_bool_callback(condition):
                for e in iterable:
                    if condition(e):
                        yield e
                        
            else:
                error = TypeError("expected ellipsis or callable object with one parameter only")
                raise error
        
        asyncgen = _asyncgen_(i)
        asyncgen.__qualname__ = "<aveytense_async_generator>"
        return asyncgen
            
    @classmethod
    def getAllItemsTypes(self, i: __.AVT_Iterable[_T], /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.getAllItemsTypes
        
        Returns all items' types in a set-like tuple, from an iterable
        """
        
        if not isinstance(i, __.Iterable):
            error = TypeError("passed object isn't iterable")
            raise error
        
        return _get_all_item_types(i)
    
    @classmethod # 0.3.53: tupleEllipsis
    def getGeneric(self, v: _Any, /, tupleEllipsis: bool = False):
        """
        @lifetime >= 0.3.52 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.getGeneric
        
        Returns generic alias as `<origin>[<args>, ...]` or `None` if it is not possible. \\
        Practically this class method tries to receive an IDE type hint, since normally it is *not* \\
        possible (when not using type hint syntax, aka PEP 484) or it is but deduced type is \\
        different. This speech reminds `typing.reveal_type()`, just is used to detect \\
        non-generic types.
        """
        
        # inspect union expressions (>=3.10)
        def _prepare_union_(*v: type, default: _T = _Any):
            
            if _sys.version_info >= (3, 10):
                
                if reckon(v) > 0:
                    
                    _union_: __.UnionType = v[0]
                
                    for e in v[1:]:
                        _union_ = _union_ | e
                        
                    return _union_

                else:
                    return default # replace with 'None' on 0.3.53
                
            else:
                
                # typing.Union[*v] throws SyntaxError since Python 3.10, use eval() instead
                return self.cast(eval("__.Union[{}]".format(", ".join([t.__qualname__ for t in v])), globals()), __.TypingUnionType)
        
        # use 'types.GenericAlias' if >=3.9 else 'typing._GenericAlias'
        if _sys.version_info >= (3, 9):
            _generic_ = __.GenericAlias
        else:
            _generic_ = _GenericTypes[0]
            
        # use 'types.UnionType' if >=3.10 else 'typing._UnionGenericAlias'; earlier: 'typing._SpecialForm'
        if _sys.version_info >= (3, 10):
            _union_ = __.UnionType
        else:
            _union_ = _UnionTypes[0]
        
        if isinstance(v, __.Iterable):
            
            # 0.3.53: mapping views
            if isinstance(v, (
                __.Mapping,
                __.KeysView,
                __.ValuesView,
                __.ItemsView
            )): 
                    
                if isinstance(v, (
                    __.KeysView,
                    __.ValuesView,
                    __.ItemsView
                )):
                    
                    # we will use their CamelCase equivalents, especially these classes are declared final
                    # in _collections_abc.pyi. Shouldn't make huge difference
                    if _hidden_collections_abc_def_check(v, "dict_items"):
                        _type_origin_ = __.DictItems
                        
                    elif _hidden_collections_abc_def_check(v, "dict_keys"):
                        _type_origin_ = __.DictKeys
                        
                    elif _hidden_collections_abc_def_check(v, "dict_values"):
                        _type_origin_ = __.DictValues
                        
                    else:
                        _type_origin_ = type(v)
                        
                    if not self.isGeneric(_type_origin_):
                        return None
                        
                    if _sys.version_info >= (3, 10): 
                        
                        # the 'mapping' property (since Python 3.10) is exclusive in 'dict_items', 'dict_keys' and 'dict_values'
                        _mapping_ = getattr(v, "mapping", None)
                        
                        # and should return 'types.MappingProxyType' instance
                        if not isinstance(_mapping_, __.MappingProxyType):
                            return None
                        
                        # because 'types.MappingProxyType' inherits from 'collections.abc.Mapping', we can call all these 3 methods just
                        # as mere dict:
                        
                        return _generic_(_type_origin_, (
                            _prepare_union_(*self.getAllItemsTypes(list(_mapping_.keys()))),
                            _prepare_union_(*self.getAllItemsTypes(list(_mapping_.values())))
                        )) if reckon(list(_mapping_.items())) > 0 else None
                        
                    else:
                        
                    
                        if isinstance(v, __.ItemsView):
                            
                            _keys_ = [e[0] for e in v]
                            _values_ = [e[1] for e in v]
                            
                            return _generic_(_type_origin_, (
                                _prepare_union_(*self.getAllItemsTypes(_keys_)),
                                _prepare_union_(*self.getAllItemsTypes(_values_))
                            )) if reckon(_keys_) > 0 else None
                            
                        elif isinstance(v, __.KeysView):
                            
                            return _generic_(_type_origin_, (
                                _prepare_union_(*self.getAllItemsTypes(list(v))),
                                _Any
                            ))
                            
                        elif isinstance(v, __.ValuesView):
                            
                            return _generic_(_type_origin_, (
                                _Any,
                                _prepare_union_(*self.getAllItemsTypes(list(v)))
                            ))
                                
                else:
                    
                    if _hidden_collections_abc_def_check(v, "mappingproxy") or \
                       _hidden_collections_abc_def_check(v, "FrameLocalsProxy"):
                        _type_origin_ = __.MappingProxyType
                        
                    elif not self.isGeneric(type(v)):
                        _type_origin_ = __.Mapping
                        
                    else:
                        _type_origin_ = type(v)
                    
                    return _generic_(_type_origin_, (
                        _prepare_union_(*self.getAllItemsTypes(list(v.keys()))),
                        _prepare_union_(*self.getAllItemsTypes(list(v.values())))
                    )) if reckon(list(v.items())) > 0 else None
                
            elif isinstance(v, __.Generator):
                
                if _hidden_collections_abc_def_check(v, "generator") or not self.isGeneric(type(v)):
                    _type_origin_ = __.AVT_Generator
                else:
                    _type_origin_ = type(v)
                
                _yield_ = _prepare_union_(*self.getAllItemsTypes(list(v)))
                # these both below have default value 'None', visible such as in generator expressions,
                # but generator doesn't have to be returned from generator expression and so these may
                # change and differ from 'None'. setting to 'typing.Any'
                _send_ = _Any
                _return_ = _Any
                
                return _generic_(_type_origin_, (
                    _yield_,
                    _send_,
                    _return_
                )) if reckon(list(v)) > 0 else None
            
            elif isinstance(v, (__.Sequence, __.Uniqual)):
                
                _type_origin_ = type(v)
                
                # since 3.9 both these types are the same, but 'AVT_Tuple' changes to 'typing.Tuple' for 3.8
                # moreover, 'tuple == typing.Tuple' returns 'False'
                if _type_origin_ in (tuple, __.AVT_Tuple):
                    if tupleEllipsis:
                        return _generic_(__.AVT_Tuple, (_prepare_union_(*self.getAllItemsTypes(v)), ...)) if reckon(v) > 0 else None
                    else:
                        return _generic_(__.AVT_Tuple, _get_all_item_types(v, False)) if reckon(v) > 0 else None
                    
                elif _type_origin_ is __.array:
                    
                    if _sys.version_info >= (3, 12):
                        return _generic_(_type_origin_, (_prepare_union_(*self.getAllItemsTypes(v)),))
                    else:
                        return None
                    
                elif _type_origin_ is memoryview:
                    
                    if _sys.version_info >= (3, 14):
                        return _generic_(_type_origin_, (_prepare_union_(*self.getAllItemsTypes(v)),))
                    else:
                        return None
                
                return _generic_(_type_origin_, _prepare_union_(*self.getAllItemsTypes(v))) if reckon(v) > 0 or not self.isGeneric(_type_origin_) else None
                
            elif isinstance(v, __.Iterator): # 0.3.53: revamp
                
                if self.isGeneric(type(v)):
                    _type_origin_ = type(v)
                else:
                    _type_origin_ = __.AVT_Iterator
                
                if _hidden_collections_abc_def_check(v, "bytearray_iterator"):
                    return _generic_(_type_origin_, (bytearray,))
                
                elif _hidden_collections_abc_def_check(v, "bytes_iterator"):
                    return _generic_(_type_origin_, (bytes,))
                
                elif _hidden_collections_abc_def_check(v, "dict_itemiterator"):
                    return _generic_(_type_origin_, (__.ItemsView,))
                
                elif _hidden_collections_abc_def_check(v, "dict_keyiterator"):
                    return _generic_(_type_origin_, (__.KeysView,))
                
                elif _hidden_collections_abc_def_check(v, "dict_valueiterator"):
                    return _generic_(_type_origin_, (__.ValuesView,))
                
                elif _hidden_collections_abc_def_check(v, "list_iterator"):
                    return _generic_(_type_origin_, (_generic_(__.AVT_List, (_prepare_union_(*self.getAllItemsTypes(list(v))),)))) if reckon(list(v)) > 0 else None
                
                elif _hidden_collections_abc_def_check(v, "list_reverseiterator"):
                    return _generic_(_type_origin_, (_generic_(__.AVT_Iterator, (_prepare_union_(*self.getAllItemsTypes(list(v))),)))) if reckon(list(v)) > 0 else None
                
                elif _hidden_collections_abc_def_check(v, "longrange_iterator") or \
                     _hidden_collections_abc_def_check(v, "range_iterator"):
                    return _generic_(_type_origin_, (range,))
                
                elif _hidden_collections_abc_def_check(v, "set_iterator"):
                    return _generic_(_type_origin_, (_generic_(__.AVT_Set, (_prepare_union_(*self.getAllItemsTypes(list(v))),)))) if reckon(list(v)) > 0 else None
                
                elif _hidden_collections_abc_def_check(v, "str_iterator"):
                    return _generic_(_type_origin_, (str,))
                
                elif _hidden_collections_abc_def_check(v, "tuple_iterator"):
                    if tupleEllipsis:
                        return _generic_(_type_origin_, (_generic_(__.AVT_Tuple, (_prepare_union_(*self.getAllItemsTypes(list(v))), ...)))) if reckon(list(v)) > 0 else None
                    else:
                        return _generic_(_type_origin_, (_generic_(__.AVT_Tuple, _get_all_item_types(list(v), False)))) if reckon(list(v)) > 0 else None
                
                elif _hidden_collections_abc_def_check(v, "zip_iterator"):
                    return _generic_(_type_origin_, (zip,))
                
        if isinstance(v, __.TypingCallableType):
            return self.cast(v, _generic_)
            
        elif isinstance(v, __.Awaitable): # collections.abc.Awaitable also includes coroutines
            
            # receive generator without using the 'await' keyword
            _list_from_gen_ = list(v.__await__())
            
            # awaitable: one type parameter, coroutine: three
            if isinstance(v, __.Coroutine):
                
                if _hidden_collections_abc_def_check(v, "coroutine"):
                    _type_origin_ = __.AVT_Coroutine
                else:
                    _type_origin_ = type(v)
            
                return _generic_(_type_origin_, (
                    _prepare_union_(*self.getAllItemsTypes(_list_from_gen_)), # 'yield'
                    _Any, # 'send'
                    _Any # 'return'
                )) if reckon(_list_from_gen_) > 0 else None
                
            else:
                
                return _generic_(_type_origin_, _Any)
            
        elif isinstance(v, __.AsyncIterable): # 0.3.53 // collections.abc.AsyncIterator (one type param) and AsyncGenerator (2 type params)
            
            _list_from_async_ = list(_extract_from_async_iterable(v))
            
            if isinstance(v, __.AsyncGenerator):
                
                if _hidden_collections_abc_def_check(v, "async_generator"):
                    _type_origin_ = __.AVT_AsyncGenerator
                else:
                    _type_origin_ = type(v)
                
                return _generic_(_type_origin_, (
                    _prepare_union_(*self.getAllItemsTypes(_list_from_async_)), # 'yield'
                    _Any # 'return'
                )) if reckon(_list_from_async_) > 0 else None
                
            elif isinstance(v, __.AsyncIterator):
                
                if self.isGeneric(type(v)):
                    _type_origin_ = type(v)
                else:
                    _type_origin_ = __.AVT_AsyncIterator
            
                return _generic_(_type_origin_, (*self.getAllItemsTypes(_list_from_async_),))
            
            else:
                
                if self.isGeneric(type(v)):
                    _type_origin_ = type(v)
                else:
                    _type_origin_ = __.AVT_AsyncIterable
                
                return _generic_(_type_origin_, (_Any,))
            
        elif isinstance(v, (_union_, __.TypingUnionType)):
            
            # both have the '__args__' attribute
            return self.cast(_prepare_union_(*v.__args__), _generic_)
                
        elif isinstance(v, (_generic_, __.TypingGenericType)):
            return self.cast(v, _generic_)
        
        elif isinstance(v, __.Pattern):
            return _generic_(type(v), (v.pattern,))
        
        elif isinstance(v, __.Match):
            return _generic_(type(v), (v.string,))
        
        elif isinstance(v, __.TypingCallableType):
            return self.cast(v, _generic_)
        
        elif callable(v):
            
            p = _util.ParamVar(v)
            
            _annotations_ = dict(p.annotations)
            
            _completed_ = tuple([(_Any if k not in _annotations_ else _annotations_[k]) for k in (*p.all, "return")])
            
            # cannot deduce the 'return' type, unless it has type annotation too, this would be necessary
            # inspecting every 'return' statement within a function
            
            # 0.3.53: ellipsis for Callable once vararg and varkeywords are found
            if p.variableCount == 2:
                
                _completed_no_vars_ = tuple([(_Any if k not in _annotations_ else _annotations_[k]) for k in (*p.all, "return") if k not in dict(p.variable)])
                
                return self.cast(__.AVT_Callable[[*_completed_no_vars_[:-1], ...], _completed_no_vars_[-1]], _generic_) # type: ignore
            
            return self.cast(__.AVT_Callable[[*_completed_[:-1]], _completed_[-1]], _generic_) # type: ignore
                
        return None
    
    @classmethod
    def getFlags(self, v: _Any, /):
        """
        @lifetime >= 0.3.53
        
        Returns flags of a type, buffer or callable object or -1 if it is not possible
        """
        
        if isinstance(v, type):
            
            return v.__flags__
        
        elif isinstance(v, memoryview):
            
            bufferFlags = 0
            
            if v.c_contiguous:
                bufferFlags |= _util.BufferFlags.contiguousC
                
            elif v.f_contiguous:
                bufferFlags |= _util.BufferFlags.contiguousF
                
            if v.readonly: # https://docs.python.org/3/c-api/buffer.html#c.Py_buffer.readonly
                bufferFlags |= _util.BufferFlags.writable
                
            return bufferFlags
        
        elif isinstance(v, __.CoroutineType):
            
            return v.cr_code.co_flags
        
        elif isinstance(v, __.TracebackType):
            
            return v.tb_frame.f_code.co_flags
        
        elif isinstance(v, __.FrameType):
            
            return v.f_code.co_flags
                
        elif callable(v):
            
            return v.__code__.co_flags
        
        else:
            
            return -1
    
    # OVERLOAD 0.3.34
    if False:
        @classmethod
        def eval(self, source: __.Union[str, __.Buffer, _ast.Module, _ast.Expression, _ast.Interactive], ast = False):
            
            if not ast:
                return eval(compile(source))
            
            else:
                
                if not self.isString(source) and not isinstance(source, __.Buffer):
                    error = TypeError("for ast.literal_eval expected a string or buffer")
                    raise error
                
                else:
                    return _ast.literal_eval(str(source) if not self.isString(source) else source)
                
    else:
        
        # for ValueError exception reason, there is no 'str' in this overload, instead create an AST instance
        @classmethod
        @__.overload
        def eval(self, source: _ast.AST, /) -> _Any:
            """@lifetime >= 0.3.26rc2"""
            ...
            
        @classmethod
        @__.overload
        def eval(self, source: _uni[str, __.Buffer, __.CodeType], /, globals: _opt[__.AVT_Dict[str, _Any]] = None, locals: _opt[__.AVT_Mapping[str, object]] = None) -> _Any:
            """@lifetime >= 0.3.26rc2"""
            ...
            
        @classmethod
        @__.overload
        def eval(
            self,
            source: __.AVT_Tuple[_uni[str, __.Buffer, _ast.Module, _ast.Expression, _ast.Interactive], _uni[str, __.Buffer, __.FSPathProvider[_Any]], str],
            /,
            globals: _opt[__.AVT_Dict[str, _Any]] = None,
            locals: _opt[__.AVT_Mapping[str, object]] = None,
            flags: int = 0,
            dont_inherit: bool = False,
            optimize: int = -1
        ) -> _Any:
            """@lifetime >= 0.3.26rc2"""
            ...
            
        @classmethod
        def eval(self, source, /, globals = None, locals = None, flags = 0, dont_inherit = False, optimize = -1):
            
            if (
                isinstance(source, (str, _ast.AST, __.Buffer, __.CodeType)) and
                (isinstance(globals, dict) or globals is None) and
                (isinstance(locals, __.Mapping) or locals is None)
            ):
                
                if isinstance(source, (str, __.Buffer, __.CodeType)):
                            
                    return _builtins.eval(source, globals, locals)
                
                else:
                    
                    return _ast.literal_eval(source)
                    
            elif isinstance(source, tuple):
                
                if reckon(source) == 3 and (
                    isinstance(source[0], (str, __.Buffer, _ast.Module, _ast.Expression, _ast.Interactive)) and # 'source'
                    isinstance(source[1], (str, __.Buffer, _os.PathLike)) and # 'fn': importing 'PathLike' from 'os' since from abc module in this project is a type alias
                    isinstance(source[2], str) and # 'mode'
                    (isinstance(globals, dict) or globals is None) and
                    (isinstance(locals, __.Mapping) or locals is None) and
                    isinstance(flags, int) and
                    isinstance(dont_inherit, bool) and
                    isinstance(optimize, int)
                ):
                    
                    _res = compile(source[0], source[1], source[2], flags, dont_inherit, optimize)
                    
                    if isinstance(_res, _ast.AST):
                        
                        return _ast.literal_eval(_res)
                    
                    elif isinstance(_res, str):
                        
                        try:
                            return _ast.literal_eval(_res)
                        
                        except ValueError:
                            return _builtins.eval(_res, globals, locals)
                    
                    elif isinstance(_res, __.CodeType):
                        return _builtins.eval(_res, globals, locals)
                    
                    return _res # I would care less about this result
            
            error = TypeError("no matching function signature; make sure every type requirement is satisfied")
            raise error
                        
    # OVERLOAD 0.3.34
    @classmethod
    @__.overload
    def bisect(self, a: __.SizeableItemGetter[_T_richComparable], x: _T_richComparable, /, l: int = 0, h: _opt[int] = None, dir: _cl.BisectMode = BISECT_RIGHT, *, key: None = None) -> int:
        """@lifetime >= 0.3.26rc2"""
        ...
    
    @classmethod
    @__.overload
    def bisect(self, a: __.SizeableItemGetter[_T], x: _T_richComparable, /, l: int = 0, h: _opt[int] = None, dir: _cl.BisectMode = BISECT_RIGHT, *, key: _cal[[_T], _T_richComparable]) -> int:
        """@lifetime >= 0.3.26rc2"""
        ...
            
    @classmethod
    def bisect(self, a, x, /, l = 0, h = None, dir = BISECT_RIGHT, *, key = None):
        
        if (
            isinstance(a, __.SizeableItemGetter) and # 0.3.41
            isinstance(x, (__.LeastComparable, __.GreaterComparable)) and # 0.3.41
            self.isInteger(l) and
            (self.isInteger(h) or self.isNone(h)) and
            isinstance(dir, _cl.BisectMode)
        ):
            
            if not _inspect.isfunction(key):
                return _bisect.bisect_right(a, x, l, h) if dir == self.BISECT_RIGHT else _bisect.bisect_left(a, x, l, h)
            
            else:
                return _bisect.bisect_right(a, x, l, h, key = key) if dir == self.BISECT_RIGHT else _bisect.bisect_left(a, x, l, h, key = key)
        
        error = TypeError("no matching function signature; make sure every type requirement is satisfied")
        raise error
    
    # OVERLOAD 0.3.34
    if False:
        @classmethod
        def insort(self, seq: __.MutableSequence[_T], item: _T, low: int = 0, high: _opt[int] = None, mode: _cl.InsortMode = INSORT_RIGHT, key: _opt[_cal[[_T], _T_richComparable]] = None):
            
            _seq = seq
            if mode == self.INSORT_LEFT:
                _bisect.insort_left(_seq, item, low, high, key = key)
                
            elif mode == self.INSORT_RIGHT:
                _bisect.insort_right(_seq, item, low, high, key = key)
                
            else:
                error = TypeError("incompatible value for 'mode' parameter. Expected one of constants: 'INSORT_LEFT' or 'INSORT_RIGHT'")
                raise error
            return _seq
        
    else:
        
        @classmethod
        @__.overload
        def insort(self, a: __.MutableSequence[_T_richComparable], x: _T_richComparable, /, l: int = 0, h: _opt[int] = None, dir: _cl.InsortMode = INSORT_RIGHT, *, key: None = None) -> None:
            """@lifetime >= 0.3.26rc2"""
            ...
            
        @classmethod
        @__.overload
        def insort(self, a: __.MutableSequence[_T], x: _T_richComparable, /, l: int = 0, h: _opt[int] = None, dir: _cl.InsortMode = INSORT_RIGHT, *, key: _cal[[_T], _T_richComparable]) -> None:
            """@lifetime >= 0.3.26rc2"""
            ...
            
        @classmethod
        def insort(self, a, x, /, l = 0, h = None, dir = INSORT_RIGHT, *, key = None):
            
            if (
                isinstance(a, __.SizeableItemGetter) and # 0.3.41
                isinstance(x, (__.LeastComparable, __.GreaterComparable)) and # 0.3.41
                self.isInteger(l) and
                (self.isInteger(h) or self.isNone(h)) and
                isinstance(dir, _cl.InsortMode)
            ):
                
                if not _inspect.isfunction(key):
                    return _bisect.insort_right(a, x, l, h) if dir == self.INSORT_RIGHT else _bisect.insort_left(a, x, l, h)
                
                else:
                    return _bisect.insort_right(a, x, l, h, key = key) if dir == self.INSORT_RIGHT else _bisect.insort_left(a, x, l, h, key = key)
            
            error = TypeError("no matching function signature; make sure every type requirement is satisfied")
            raise error
    
    @classmethod
    def print(self, *values: object, separator: _opt[str] = " ", ending: _opt[str] = "\n", file: _uni[__.Writeable[str], __.Flushable, None] = None, flush = False, reprFirst = False):
        """
        @lifetime >= 0.3.25
        ```
        "class method" in class Tense
        ```
        Same as `print()`, just with `INSERTION` beginning. It can be \\
        changed with `invokeAs` parameter. Since 0.3.26a1 this method \\
        returns reference to this class. Since 0.3.27b1, if setting \\
        `TenseOptions.insertionMessage` was `False`, `invokeAs` \\
        parameter will lose its meaning.
        - 0.3.41: Added `reprFirst` to invoke `repr()` before `str()`, and removed `invokedAs`
        """
        
        # a trick providing default value for 'x'
        _invoke_this = lambda x = object(): repr(x) if hasattr(x, "__repr__") else str(x)
        
        if TenseOptions.insertionMessage is True:
            
            if reprFirst:
                
                print((Color(Time.fencordFormat(), 8, 243) % Color.BOLD) + " " + (Color("INSERTION", 8, 45) % Color.BOLD), *tuple([_invoke_this(e) for e in values]), sep = separator, end = ending, file = file, flush = flush)
            
            else:
                
                print((Color(Time.fencordFormat(), 8, 243) % Color.BOLD) + " " + (Color("INSERTION", 8, 45) % Color.BOLD), *values, sep = separator, end = ending, file = file, flush = flush)
            
        else:
            
            if reprFirst:
                
                print(*tuple([_invoke_this(e) for e in values]), sep = separator, end = ending, file = file, flush = flush)
            
            else:
                
                print(*values, sep = separator, end = ending, file = file, flush = flush)
            
        return self
    
    @classmethod
    @__.overload
    def random(self, x: _uni[__.Sequence[_T], __.Uniqual[_T]], /) -> _T: ...
    
    @classmethod
    @__.overload
    def random(self, x: int, /) -> int: ...
    
    @classmethod
    @__.overload
    def random(self, x: int, y: int, /) -> int: ...
    
    @classmethod
    def random(self, x, y = None, /):
        """
        @lifetime >= 0.3.24 \\
        @standard-lifetime >= 0.3.25 \\
        @modified 0.3.25, 0.3.26rc2 (support for `tkinter.IntVar`), 0.3.31 (cancelled support for `tkinter.IntVar`) \\
        0.3.34 (overloads)
        
        With one parameter, returns an item from a sequence or integer from range [0, x) \\
        With two parameters, returns an integer in specified range [x, y] or [y, x] if x > y.
        """
        if self.isNone(y):
            
            if self.isInteger(x):
                
                if x <= 1:
                    error = ValueError("expected a positive integer above 1")
                    raise error
                
                # note random.randrange() is also a thing
                return _secrets.randbelow(x)
            
            elif isinstance(x, (__.Sequence, __.Uniqual)):
                
                return _random.choice(list(x))
            
        a = [x, y]
        
        if self.isList(a, int):
                
            _x, _y = a[0], a[1]
            
            if x > y:
                _x, _y = _y, _x
            
            return _random.randint(_x, _y)
            
        error = TypeError("no matching function signature")
        raise error
    
    if False:
        @classmethod
        def randomWithout(self, from_: int, to_: int, /, exclude: __.Union[range, _ab_mod.AbroadInitializer, None] = None):
            """
            @lifetime >= 0.3.52
            
            Equivalent to `~.Tense.pick(~.Tense.random(<from>, <oneBeforeStartPoint>), ~.Tense.random(<oneAfterEndpoint>, <to>))`.
            
            where `<oneBeforeStartPoint>` and `<oneAfterEndpoint>` are determined by `exclude` 2-item tuple
            """
            
            if not self.isInteger(from_, to_):
                error = TypeError("expected integers only in parameters '{}' and '{}'".format(*_get_all_params(self.randomWithout))[:2])
                raise error
            
            if not isinstance(exclude, (type(None), range, _ab_mod.AbroadInitializer)):
                error = TypeError("expected 'range' or 'abroad' object, or 'None' in parameter '{}'".format(_get_all_params(self.randomWithout))[2])
                raise error
            
            if isinstance(exclude, range):
                
                if exclude.start > exclude.stop:
                    error = ValueError("conflict with points. expected: 'from_' < 'exclude_start' < 'exclude_stop' < 'to_'")
                    raise error
                
                return self.pick((self.random(from_, exclude.start + 1), self.random(exclude.stop + 1, to_)))
                
    @classmethod
    def randstr(self, lower = True, upper = True, digits = True, special = True, length = 10):
        """
        @lifetime >= 0.3.9 \\
        \\@lifetime >= 0.3.9; < 0.3.24; >= 0.3.25 \\
        to 0.3.34 known as `NennaiRandomize.randomizeStr()`
        ```
        # created 15.07.2024
        "class method" in class NennaiRandomize
        ```
        - `lower` - determine, if you want to include all lowercased letters from english alphabet. Defaults to `True`
        - `upper` - determine, if you want to include all uppercased letters from english alphabet. Defaults to `True`
        - `digits` - determine, if you want to include all numbers. Defaults to `True`
        - `special` - determine, if you want to include all remaining chars accessible normally via English keyboard. \\
        Defaults to `True`
        - `length` - allows to specify the length of returned string. Defaults to `10`.
        """
        # code change 0.3.34
        conv = [""]
        conv.clear()
        ret = ""
        
        if lower:
            conv.extend([e for e in _cp.STRING_LOWER])
                
        if upper:
            conv.extend([e for e in _cp.STRING_UPPER])
                
        if digits:
            conv.extend([e for e in _cp.STRING_DIGITS])
                
        if special:
            conv.extend([e for e in _cp.STRING_SPECIAL])
        
        # there no matter if negative or positive
        for _ in abroad(length):
            ret += self.pick(conv)
            
        return ret
    
    @classmethod
    def uuidPrimary(self, node: _uni[int, None] = None, clockSeq: _uni[int, None] = None):
        """
        @lifetime >= 0.3.26a1 \\
        \\@modified 0.3.31 (cancelled support for `tkinter.IntVar`)
        ```ts
        // created 20.07.2024
        "class method" in class Tense
        ```
        Return an UUID from host ID, sequence number and the current time.
        """
        _n = node
        _c = clockSeq
        return _uuid.uuid1(node = _n, clock_seq = _c)
    
    @classmethod
    def uuidMd5(self, namespace: __.UUID, name: _uni[str, bytes]):
        """
        @lifetime >= 0.3.26a1 \\
        \\@modified 0.3.31 (cancelled support for `tkinter.StringVar`)
        ```ts
        // created 20.07.2024
        "class method" in class Tense
        ```
        Return an UUID from the MD5 (Message Digest) hash of a namespace UUID and a name
        """
        return _uuid.uuid3(namespace = namespace, name = name)
    
    @classmethod
    def uuidRandom(self):
        """
        @lifetime >= 0.3.26a1
        ```ts
        // created 20.07.2024
        "class method" in class Tense
        ```
        Return a random UUID
        """
        return _uuid.uuid4()
    
    @classmethod
    def uuidSha1(self, namespace: __.UUID, name: _uni[str, bytes]):
        """
        @lifetime >= 0.3.26a1 \\
        \\@modified 0.3.31 (cancelled support for `tkinter.StringVar`)
        ```ts
        "class method" in class Tense
        ```
        Return an UUID from the SHA-1 (Secure Hash Algorithm) hash of a namespace UUID and a name
        """
        return _uuid.uuid5(namespace = namespace, name = name)
    
    
    # NOTE: _KT type parameter is not used overall, so we are ignoring it and replacing with Any,
    # what allows to prevent using overloading.
    # 0.3.51: Removed parameter 'secure'
    if versionInfo < (0, 3, 46) and False:
        
        @classmethod
        @__.overload
        def pick(self, i: _uni[__.Sequence[_T], __.Uniqual[_T]], /) -> _T: ... # sets act the same as lists in this case
        
        @classmethod
        @__.overload
        def pick(self, i: __.AVT_Mapping[_KT, _VT], /) -> _VT: ...
    
    @classmethod # before 0.3.46 this signature had no annotations
    def pick(self, i: __.Union[__.Sequence[_T], __.Uniqual[_T], __.AVT_Mapping[_Any, _T]], /):
        """
        @lifetime >= 0.3.8 \\
        @standard-lifetime >= 0.3.24 \\
        @modified 0.3.25, 0.3.26rc2, 0.3.26rc3, 0.3.34 (overloads + mappings), 0.3.46 (no overloads) \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.pick
        
        Returns random item from a sequence (+ mapping since 0.3.34)
        """
        if isinstance(i, (__.Sequence, __.Uniqual)):
            
            if reckon(i) in (0, 1):
                error = TypeError("expected at least 2 items in a sequence/set")
                raise error
            
            _i = list(i) # Sequence and AbstractSet are both Iterable so these are convertible (0.3.46)
            
            return _random.choice(_i)
        
        elif isinstance(i, __.Mapping):
            
            if reckon(i) in (0, 1):
                error = TypeError("expected at least 2 pairs in a mapping/dictionary")
                raise error
            
            _values = [i[k] for k in i]
            return _random.choice(_values)
        
        else:
            error = TypeError("expected a sequence or mapping")
            raise error
    
    if _version.VERSION_INFO < (0, 3, 31) and False: # deprecated since 0.3.25, removed 0.3.31
        
        def error(self, handler: type[Exception], message: _uni[str, None] = None):
            """
            @lifetime >= 0.3.24 \\
            \\@deprecated 0.3.25
            ```
            "class method" in class Tense
            ```
            """
            _user_defined_error = handler
            _user_defined_reason = message
            if _user_defined_reason is None:
                raise _user_defined_error()
            else:
                raise _user_defined_error(_user_defined_reason)
    
    
    @classmethod
    @__.overload
    def invert(self, v: _uni[int, float], /) -> float: ...
    
    @classmethod
    @__.overload
    def invert(self, v: _uni[__.AVT_Sequence[_uni[int, float]], __.AVT_Uniqual[_uni[int, float]], _ab_mod.AbroadInitializer], /) -> __.AVT_List[float]: ...
    
    @classmethod
    @__.overload
    def invert(self, v: __.AVT_Mapping[_KT, _VT], /) -> __.AVT_Dict[_VT, _KT]: ...
    
    @classmethod
    def invert(self, v, /):
        """
        @lifetime >= 0.3.46
        
        Invert an integer or float (`1/v`) or a mapping (key becoming value and value becoming key).
        """
        
        if self.isInteger(v) or self.isFloat(v):
            
            if v in (0, .0):
                error = ZeroDivisionError("division by zero")
                raise error
            
            return 1/v
        
        elif isinstance(v, (__.Sequence, __.Uniqual)) and self.all(v, lambda x: self.isInteger(x) or self.isFloat(x)):
            
            _filter = self.cast([1/e for e in v if e not in (0, .0)], __.AVT_List[float])
            
            if reckon(v) != reckon(_filter):
                error = ZeroDivisionError("division by zero")
                raise error
            
            return self.cast([-e for e in v], __.AVT_List[float])
            
        elif isinstance(v, _ab_mod.AbroadInitializer):
            
            _filter = [1/e for e in v if e not in (0, .0)]
            
            if reckon(v) != reckon(_filter):
                error = ZeroDivisionError("division by zero")
                raise error
            
            return [1/e for e in v]
        
        elif isinstance(v, __.Mapping):
            
            return dict([(v[k], k) for k in v])
        
        else:
            
            error = TypeError("expected an integer, float, sequence/set of integers or floats or a mapping/dictionary")
            raise error
            
    # OVERLOAD 0.3.34
    @classmethod
    @__.overload
    def first(self, i: _uni[__.AVT_Sequence[_T], __.AVT_Uniqual[_T]], /, condition: None = None, default: _S = None) -> _uni[_S, _T]: ...
    
    @classmethod
    @__.overload
    def first(self, i: _uni[__.AVT_Sequence[_T], __.AVT_Uniqual[_T]], /, condition: _cal[[_T], bool], default: _S = None) -> _uni[_S, _T]: ...
            
    @classmethod
    def first(self, i, /, condition = None, default = None):
        """
        @lifetime >= 0.3.26rc2 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.first
        
        Return first element in a `seq` (sequence) which satisfies `condition`. If none found, returned \\
        is default value defined via parameter `default`, which by default has value `None`. On 0.3.27a4 \\
        removed this parameter, it has been restored on 0.3.34
        """
        
        if not _is_bool_callback(condition) and not self.isNone(condition):
            error = TypeError("expected 'condition' parameter to be a callable or 'None'")
            raise error
        
        _seq = list(i)
        
        for _i in abroad(_seq):
            
            if condition is not None and condition(_seq[_i]):
                return _seq[_i]
            
            else:
                if _seq[_i]: return _seq[_i]
                
        return default
    
    # OVERLOAD 0.3.34
    @classmethod
    @__.overload
    def last(self, i: _uni[__.AVT_Sequence[_T], __.AVT_Uniqual[_T]], /, condition: None = None, default: _S = None) -> _uni[_S, _T]: ...
    
    @classmethod
    @__.overload
    def last(self, i: _uni[__.AVT_Sequence[_T], __.AVT_Uniqual[_T]], /, condition: _cal[[_T], bool], default: _S = None) -> _uni[_S, _T]: ...
    
    @classmethod
    def last(self, i, /, condition = None, default = None):
        """
        @lifetime >= 0.3.26rc2 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.last
        
        Return last element in a `seq` (sequence) which satisfies `condition`. If none found, returned is default \\
        value defined via parameter `default`, which by default has value `None`. On 0.3.27a4 removed this parameter, \\
        it has been restored on 0.3.34
        """
        if not _is_bool_callback(condition) and not self.isNone(condition):
            error = TypeError("expected 'condition' parameter to be a callable or 'None'")
            raise error
        
        _seq = list(i)
        
        for _i in self.abroadNegative(1, _seq):
            
            if condition is not None and condition(_seq[_i]):
                return _seq[_i]
            
            else:
                if _seq[_i]: return _seq[_i]
                
        return default
    
    @classmethod
    def probability2(self, x: _T1 = 1, y: _T2 = 0, frequency: int = 1, length: _ProbabilityLengthType = 10000):
        """
        @lifetime >= 0.3.8; < 0.3.24; >= 0.3.25 \\
        @standard-lifetime >= 0.3.9; < 0.3.24; >= 0.3.25 \\
        @modified 0.3.26a3, 0.3.26rc1, 0.3.31, 0.3.46 (utterly bypass `sys.maxsize`) \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.probability2
        
        Randomize a value using probability `frequency/length` applied on parameter `x`. \\
        Math interpretation: `P(x) = frequency/length` and `P(y) = 1 - P(x)`.
        Default values:
        - for `x`: 1
        - for `y`: 0
        - for `frequency`: 1
        - for `length`: 10000 (since 0.3.26a3 `length` can also have value `-1`)

        Default operation: return `x` with `1/10000` chance (0.01%) or `y` with `9999/10000` chance (99.99%).
        
        Value exceptions:
        - for `frequency` equal 0 or `x` equal `y`, returned is `y`
        - for `frequency` greater than (or since 0.3.25 equal) `length` returned is `x`
        """
        
        # due to swap from IntegerEnum to Enum in _ProbabilityLength class's subclass
        # it had to be replaced
        _length = 10000 if length in (-1, self.PROBABILITY_COMPUTE) else length
        _frequency = frequency
        
        # 0.3.33: refraining from using string literals, since they will need to be manually changed
        # once parameter names are changed
        # note that 'return' keyword is reserved for return annotation with '->' operator
        _params = _get_all_params(self.probability2) # 0.3.36: missing 2 after 'probability'
        # _options = [k for k in TenseOptions.__dict__ if k[:1] != "_"]
            
        if not self.isInteger(_frequency):
            error = TypeError("expected an integer in parameter '{}'".format(_params[2]))
            raise error
        
        elif _frequency < 0:
            error = ValueError("expected a non-negative integer in parameter '{}'".format(_params[2]))
            raise error
        
        # types must match, otherwise you can meet an union-typed result, which is not useful during
        # type inspection, since you need to append appropriate 'if' statement!
        # exception: a function result being a union-typed one
        # for 0.3.46 it isn't necessary to both have the same type anyway, responsibility goes to user
        
        if self.versionInfo < (0, 3, 46) and False:
            
            if not self.isList([x, y], type(x)):
                error = TypeError("provided types in parameters '{}' and '{}' do not match".format(_params[0], _params[1]))
                raise error
        
        if not self.isInteger(length) and length != self.PROBABILITY_COMPUTE:
            error = TypeError("expected an integer or constant '{}' in parameter '{}'".format("PROBABILITY_" + self.PROBABILITY_COMPUTE.name, _params[3]))
            raise error
        
        elif _length == 0:
            error = ZeroDivisionError("expected integer value from -1 or above in parameter '{}', but not equal zero".format(_params[3]))
            raise error
        
        elif _length < -1:
            error = ValueError("parameter '{}' may not have a negative integer value".format(_params[3]))
            raise error
        
        if self.versionInfo < (0, 3, 46) and False:
            
            # elif
            if _length > _sys.maxsize and not TenseOptions.disableProbability2LengthLimit:
                error = ValueError("integer value passed to parameter '{}' is too high, expected value below or equal {}. If you want to remove this error, toggle on option '{}'".format(
                    _params[3], _sys.maxsize, "{}.{}".format(TenseOptions.__name__, _options[2])
                ))
                raise error
        
        # these statements are according to probability math definition
        # once 'x' and 'y' are the same, there is no reason to activate loop at all
        
        try: # >= 0.3.51
            if x == y or _frequency == 0:
                return y
            
        except TypeError:
            pass
        
        if _frequency >= _length:
            return x
        
        if self.versionInfo >= (0, 3, 46) or True:
            
            r = self.random(1, _length)
            return x if Math.isInRange(r, 1, _frequency) else y
            
        else:
            
            if TenseOptions.disableProbability2LengthLimit:
                
                # 0.3.33: change in _frequency (removed minus one) so that result will be
                # displayed correctly
                r = self.random(1, _length)
                return x if Math.isInRange(r, 1, _frequency) else y
                
            else:
                # type of list will be deduced anyway, so there annotation may be skipped
                # 0.3.31: shortened code, reduced due to usage of list comprehension
                a = [y for _ in abroad(_length - _frequency)] + [x for _ in abroad(_length - _frequency, _length)]
                return self.pick(a)
        
    if versionInfo >= (0, 3, 46) or True:
        
        @classmethod
        def probability3(self, vf: __.AVT_Mapping[_T, __.Union[int, __.EllipsisType]], /):
            """
            @lifetime >= 0.3.46 \\
            https://aveyzan.xyz/aveytense#aveytense.Tense.probability3
            
            Abridged version of `~.probability()` without `length` parameter (length determined by mapping values), \\
            and `vf` parameter being positional-only non-variable parameter, which only accepts a mapping. Ellipsis \\
            equal 1.
            
            This class method is circa 3 times faster than `~.probability()` due to least amount of lines of code \\
            caused by least amount of statements, and only one, non-variable parameter to inspect
            """
            if _sys.version_info >= (3, 9):
                _check_if_mapping = isinstance(vf, __.Mapping)
                
            else:
                
                try:
                    _check_if_mapping = isinstance(vf, __.Mapping)
                    
                except:
                    _check_if_mapping = issubclass(type(vf), __.Mapping)
            
            if not _check_if_mapping:
                error = TypeError("expected a mapping/dictionary")
                raise error
            
            if reckon(vf) in (0, 1):
                error = TypeError("expected at least 2 pairs in the mapping/dictionary")
                raise error
            
            elif reckon(vf) > _sys.maxsize:
                error = ValueError("too high amount of pairs in the mapping/dictionary, expected least or equal {}".format(_sys.maxsize))
                raise error
            
            else:
                
                _filter = dict([(k, vf[k]) for k in vf if self.isEllipsis(vf[k]) or (self.isInteger(vf[k]) and vf[k] > 0)])
                _keys, _values = [k for k in _filter], [_filter[k] for k in _filter]
                _values = [(1 if not self.isInteger(e) else e) for e in _values]
                
                if reckon(vf) != reckon(_filter):
                    error = TypeError("expected key values have positive integer or ellipsis")
                    raise error
                
                if self.all(_values, lambda x: x == 1):
                        
                    return self.pick(_keys)
                
                if reckon(vf) == 2:
                        
                    return self.probability2(_keys[0], _keys[1], _values[0], _values[0] + _values[1])
                    
                else:
                        
                    _value = 0
                    _ranges = [(0, 0)]
                    _ranges.clear()
                    
                    # amount of tuples in list is determined by amount of non-filtered pairs
                    for e in _values:
                        
                        _ranges += [(_value + 1, _value + e)]
                        _value += e
                    
                    r = self.random(1, _value)
                    
                    for i in abroad(_ranges):
                        
                        if Math.isInRange(r, _ranges[i][0], _ranges[i][1]):
                            return _keys[i]
                    
                    # not probable, but necessary if we don't want to use return annotation
                    error = ValueError("couldn't return the value")
                    raise error
                    
        @classmethod
        def probability(self, *vf: _ProbabilityType[_T]):
            """
            @lifetime >= 0.3.8 \\
            @standard-lifetime >= 0.3.9 \\
            @modified 0.3.19, 0.3.24, 0.3.25, 0.3.26a3, 0.3.26b3, 0.3.26rc1, 0.3.26rc2, 0.3.31, 0.3.46 \\
            https://aveyzan.xyz/aveytense#aveytense.Tense.probability
            
            `vf` accepts 2-item sequences/sets, mappings and single values.
            """
            
            if reckon(vf) == 0:
                
                error = exceptions.MissingValueError("expected at least one value being mapping, or more values")
                raise error
            
            elif reckon(vf) == 1:
                
                e = vf[0]
                
                if not isinstance(e, __.Mapping):
                    error = TypeError("expected a dictionary if there is only one value passed to parameter 'vf'")
                    raise error
                
                if reckon(e) in (0, 1):
                    error = TypeError("expected at least 2 pairs in a dictionary being the only value in parameter 'vf'")
                    raise error
                
                elif reckon(e) > _sys.maxsize:
                    error = ValueError("too high amount of pairs in a dictionary, expected least or equal {}".format(_sys.maxsize))
                    raise error
                
                e = self.cast(e, __.AVT_Mapping[_T, _uni[int, __.EllipsisType, None]])
                _filter = dict([(k, e[k]) for k in e if (self.isEllipsis(e[k]) or self.isNone(e[k])) or (self.isInteger(e[k]) and e[k] > 0)])
                _keys, _values = [k for k in _filter], [_filter[k] for k in _filter]
                _values = [(1 if not self.isInteger(e) else e) for e in _values]
                
                if reckon(e) != reckon(_filter):
                    error = TypeError("expected key values have positive integer, ellipsis or None in a mapping")
                    raise error
                
                _e = {_keys[i]: _values[i] for i in abroad(_keys)}
            
            else:
                
                _e: __.AVT_Dict[_T, int] = {}
                
                for e in vf:
                    
                    if isinstance(e, __.Mapping):
                        
                        if reckon(e) == 0:
                            error = TypeError("expected at least one pair in a mapping")
                            raise error
                        
                        e = self.cast(e, __.AVT_Mapping[_T, _uni[int, __.EllipsisType, None]])
                        _filter = dict([(k, e[k]) for k in e if (self.isEllipsis(e[k]) or self.isNone(e[k])) or (self.isInteger(e[k]) and e[k] > 0)])
                        _keys, _values = [k for k in _filter], [_filter[k] for k in _filter]
                        _values = [(1 if not self.isInteger(e) else e) for e in _values]
                        
                        if reckon(e) != reckon(_filter):
                            error = TypeError("expected key values have positive integer, ellipsis or None in a mapping")
                            raise error
                        
                        _e = self.extend(_e, {_keys[i]: _values[i] for i in abroad(_keys)})
                        
                    elif isinstance(e, (__.Sequence, __.Uniqual)):
                        
                        _ie = list(e) # AbstractSet is not indexable
                        
                        if reckon(_ie) not in (1, 2):
                            error = TypeError("expected sequences and sets of size 1-2 only")
                            raise error
                        
                        elif reckon(_ie) == 1:
                            
                            _v1: _T = _ie[0]
                            _e = self.extend(_e, {_v1: 1})
                            
                        else:
                            
                            _v2: __.AVT_Tuple[_T, int] = (_ie[0], 1 if not self.isInteger(_ie[1]) else _ie[1])
                            _e = self.extend(_e, {_v2[0]: _v2[1]})
                            
                    else:
                        
                        _v3: _T = e
                        _e = self.extend(_e, {_v3: 1})
                        
            return self.probability3(_e)
        
    else:
        @classmethod
        def probability(self, *vf: _ProbabilityType[int], length: _ProbabilityLengthType = PROBABILITY_COMPUTE):
            """
            @since 0.3.8 (standard since 0.3.9) \\
            @lifetime >= 0.3.8 \\
            @modified 0.3.19, 0.3.24, 0.3.25, 0.3.26a3, 0.3.26b3, 0.3.26rc1, 0.3.26rc2, 0.3.31, 0.3.46
            ```ts
            "class method" in class Tense
            ``` \n
            ``` \n
            
            # since 0.3.46
            def probability(
                *vf: int | Sequence[int] | AbstractSet[int] | Mapping[int, int | None | EllipsisType],
                length: int = PROBABILITY_COMPUTE
            ): ...
            
            # for 0.3.25 - 0.3.45
            def probability(
                *vf: int | list[int] | tuple[int, int | None] | __.AVT_Dict[int, int | None] | deque[int],
                length: int = PROBABILITY_COMPUTE
            ): ...

            # for 0.3.24
            def probability(
                *valuesAndFrequencies: int | list[int] | tuple[int] | __.AVT_Dict[int, int | None],
                length: int = PROBABILITY_ALL
            ): ...

            # during 0.3.19 - 0.3.23; on 0.3.19 renamed
            def probability(
                *valuesAndFrequencies: int | list[int] | tuple[int],
                length: int = -1
            ): ...

            # during 0.3.8 - 0.3.18
            def complexity(
                values: list[_T] | tuple[_T],
                frequencies: int | list[int] | tuple[int],
                length: int = 10000
            ): ...
            ```
            Extended version of `Tense.probability2()` method. Instead of only 2 values user can put more than 2. \\
            Nevertheless, comparing to the same method, it accepts integers only.

            *Parameters*:

            - `vf` - this parameter waits at least for 3 values (before 0.3.26a3), for 2 values you need to use `Tense.probability2()` method \\
            instead, because inner code catches unexpected exception `ZeroDivisionError`. For version 0.3.25 this parameter accepts: 
            - integers
            - integer lists of size 1-2
            - integer tuples of size 1-2
            - integer deques of size 1-2
            - integer key-integer/`None`/`...` value dicts
            - integer sets and frozensets of size 1-2 both
            
            For 0.3.46, this range is wider:
            - integers
            - integer sequences/sets of size 1-2 (+ built-ins: lists, tuples, sets, frozensets. Deque counts as a sequence)
            - integer key-integer/`None`/ellipsis value mappings (+ built-ins: dicts)
            
            ||
            
            - `length` (Optional) - integer which has to be a denominator in probability fraction. Defaults to `-1`, what means this \\
            number is determined by `vf` passed values (simple integer is plus 1, dicts - plus value or 1 if it is `None` or ellipsis, \\
            sequence - 2nd item; if `None`, then plus 1). Since 0.3.26b3 put another restriction: length must be least than or equal \\
            `sys.maxsize`, which can be either equal 2\\*\\*31 - 1 (2,147,483,647) or 2\\*\\*63 - 1 (9,223,372,036,854,775,807)
            """
            # explanation:
            # a1 is final list, which will be used to return the integer
            # a2 is temporary list, which will store all single integers, without provided "frequency" value (item 2)
            a1, a2 = [[0] for _ in abroad(2)]
            self.clear(a1, a2)

            # c1 sums all instances of single numbers, and with provided "frequency" - plus it
            # c2 is substraction of length and c1
            # c3 has same purpose as c1, but counts only items without "frequency" (second) item
            # c4 is last variable, which is used as last from all of these - counts the modulo of c2 and c3 (but last one minus 1 as well)
            # c5 gets value from rearmost iteration 
            c1, c2, c3, c4, c5 = [0 for _ in abroad(5)]
            
            # 0.3.33: refraining from using string literals, since they will need to be manually changed
            # once parameter names are changed
            # note that 'return' keyword is reserved for return annotation with '->' operator
            _params = _get_all_params(self.probability)
            
            if not self.isInteger(length) and length != self.PROBABILITY_COMPUTE:
                error = TypeError("expected integer or constant '{}' in parameter '{}'".format("PROBABILITY_" + self.PROBABILITY_COMPUTE.name, _params[1]))
                raise error
            
            _length = -1 if length == self.PROBABILITY_COMPUTE else length
            
            # length checking before factual probability procedure
            if _length < -1:
                error = ValueError("expected integer value from -1 or above in parameter '{}'".format(_params[1]))
                raise error
            
            elif _length == 0:
                error = ZeroDivisionError("expected integer value from -1 or above in parameter '{}', but not equal zero".format(_params[1]))
                raise error
            
            # 0.3.26b3: cannot be greater than sys.maxsize
            # 0.3.33: update of this statement (added the 'or' keyword with expression as right operand)
            elif _length > _sys.maxsize or (_length > _sys.maxsize and reckon(vf) == 2 and not TenseOptions.disableProbability2LengthLimit):
                error = ValueError("integer value passed to parameter '{}' is too high, expected value below or equal {}".format(_params[1], _sys.maxsize))
                raise error
            
            # START 0.3.26a3
            if reckon(vf) == 2:
                
                # alias to elements
                e1, e2 = (vf[0], vf[1])
                
                if self.isInteger(e1):
                    
                    if self.isInteger(e2):
                        
                        # 0.3.33: 'length = _length' instead of 'length = 2'
                        return self.probability2(e1, e2, length = _length)
                    
                    # 0.3.33: _ProbabilitySeq type alias to deputize (_ProbabilitySeqNoDict, dict) tuple
                    # during type checking
                    # 0.3.46: support ABCs
                    elif isinstance(e2, (__.Sequence, __.Uniqual, __.Mapping)):
                        
                        if isinstance(e2, (__.Sequence, __.Uniqual)):
                        
                            if reckon(e2) in (1, 2):
                                
                                _tmp = e2[0] if reckon(e2) == 1 else (e2[0], e2[1])
                                
                                if self.isInteger(_tmp):
                                    
                                    # 0.3.33: 'length = _length' instead of 'length = 2'
                                    return self.probability2(e1, _tmp, length = _length)
                                
                                # notable information: this duo of tuple items are, respectively:
                                # 'value' and 'frequency'
                                elif self.isTuple(_tmp):
                                    
                                    _v, _f = (_tmp[0], _tmp[1])
                                    
                                    if not self.isInteger(_v):
                                        error = TypeError("first item in an iterable is not an integer")
                                        raise error
                                    
                                    if not (self.isInteger(_f) or self.isEllipsis(_f) or self.isNone(_f)):
                                        error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                        raise error
                                    
                                    if self.isNone(_f) or self.isEllipsis(_f):
                                        return self.probability2(e1, _v, length = _length)
                                    
                                    elif _f < 1: # probability fraction cannot be negative
                                        error = ValueError("second item in an iterable is negative or equal zero")
                                        raise error
                                    
                                    return self.probability2(e1, _v, frequency = _f, length = _length)
                                
                                else:
                                    error = RuntimeError("internal error")
                                    raise error
                                
                            else:
                                error = IndexError("length of every iterable may have length 1-2 only")
                                raise error
                            
                        elif isinstance(e2, __.Mapping):
                            
                            if reckon(e2) != 1:
                                error = ValueError("expected one pair in a dictonary, received {}".format(reckon(e2)))
                                raise error
                            
                            # 0.3.33: removed loop, replacing it with inbuilt dictionary methods
                            _v, _f = (self.toList(e2.keys())[0], self.toList(e2.values())[0])
                            
                            if self.isNone(_f) or self.isEllipsis(_f):
                                return self.probability2(e1, _v, length = _length)
                            
                            elif _f < 1:
                                error = ValueError("value in a dictionary is negative or equal zero")
                                raise error
                                
                            return self.probability2(e1, _v, frequency = _f, length = _length)
                        
                        else:
                            error = TypeError("unsupported type in second item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                            raise error
                
                # 0.3.33: _ProbabilitySeq type alias to deputize (_ProbabilitySeqNoDict, dict) tuple
                # during type checking
                # 0.3.46: support ABCs
                elif isinstance(e1, (__.Sequence, __.Uniqual, __.Mapping)):
                    
                    if self.isInteger(e2):
                    
                        if isinstance(e1, (__.Sequence, __.Uniqual)):
                            
                            if reckon(e1) in (1, 2):
                                
                                _tmp = e1[0] if reckon(e1) == 1 else (e1[0], e1[1])
                                
                                if self.isInteger(_tmp):
                                    
                                    # 0.3.33: 'length = _length' instead of 'length = 2'
                                    # + 'e2' and '_tmp' are placed vice versa
                                    return self.probability2(_tmp, e2, length = _length)
                                
                                elif self.isTuple(_tmp):
                                    
                                    _v, _f = (_tmp[0], _tmp[1])
                                    
                                    if not self.isInteger(_v):
                                        error = TypeError("first item in an iterable is not an integer")
                                        raise error
                                    
                                    if not (self.isInteger(_f) or self.isEllipsis(_f) or self.isNone(_f)):
                                        error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                        raise error
                                    
                                    if self.isNone(_f) or self.isEllipsis(_f):
                                        return self.probability2(_v, e2, length = _length)
                                    
                                    elif _f < 1: # probability fraction cannot be negative
                                        error = ValueError(f"second item in an iterable is negative or equal zero")
                                        raise error
                                    
                                    return self.probability2(_v, e2, frequency = _f, length = _length)
                                
                                else:
                                    error = RuntimeError("internal error")
                                    raise error
                                
                            else:
                                error = IndexError("length of every iterable may have length 1-2 only")
                                raise error
                        
                        elif isinstance(e1, __.Mapping):
                            
                            if reckon(e1) != 1:
                                error = ValueError("expected only one pair in a dictonary, received {}".format(reckon(e1)))
                                raise error
                            
                            # 0.3.33: removed loop, replacing it with inbuilt dictionary methods
                            _v, _f = (self.toList(e1.keys())[0], self.toList(e1.values())[0])
                            
                            if self.isNone(_f) or self.isEllipsis(_f):
                                
                                # 0.3.33: '_v' and 'e2' vice versa
                                return self.probability2(_v, e2, length = _length)
                            
                            elif _f < 1:
                                error = ValueError("value in a dictionary is negative or equal zero")
                                raise error
                            
                            # 0.3.33: '_v' and 'e2' vice versa
                            return self.probability2(_v, e2, frequency = _f, length = _length)
                    
                    # 0.3.33: _ProbabilitySeq type alias to deputize (_ProbabilitySeqNoDict, dict) tuple
                    # during type checking
                    # 0.3.46: support ABCs
                    elif isinstance(e2, (__.Sequence, __.Uniqual, __.Mapping)):
                        
                        if isinstance(e1, (__.Sequence, __.Uniqual)):
                        
                            if isinstance(e2, (__.Sequence, __.Uniqual)):
                                
                                if reckon(e1) == 1:
                                    
                                    if reckon(e2) == 1:
                                        
                                        _1, _2 = (e1[0], e2[0])
                                        
                                        if not self.isInteger(_1) or not self.isInteger(_2):
                                            error = TypeError("first item in an iterable is not an integer")
                                            raise error
                                        
                                        return self.probability2(_1, _2, length = _length)
                                    
                                    elif reckon(e2) == 2:
                                        
                                        _1, _2_1, _2_2 = (e1[0], e2[0], e2[1])
                                        
                                        if not self.isInteger(_1) or not self.isInteger(_2_1):
                                            error = TypeError("first item in an iterable is not an integer")
                                            raise error
                                        
                                        if not self.isEllipsis(_2_2) and not self.isInteger(_2_2) and not self.isNone(_2_2):
                                            error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                            raise error
                                        
                                        if self.isNone(_2_2) or self.isEllipsis(_2_2):
                                            
                                            return self.probability2(_1, _2_1, length = _length)
                                        
                                        return self.probability2(_1, _2_1, frequency = _2_2, length = _length)
                                    
                                    else:
                                        error = IndexError("length of every iterable may have length 1-2 only")
                                        raise error
                                
                            elif reckon(e1) == 2:
                                
                                if reckon(e2) == 1:
                                    
                                    _1_1, _1_2, _2 = (e1[0], e1[1], e2[0])
                                    
                                    if not self.isInteger(_1_1) or not self.isInteger(_2):
                                        error = TypeError("first item in an iterable is not an integer")
                                        raise error
                                    
                                    if not self.isEllipsis(_1_2) and not self.isInteger(_1_2) and self.isNone(_1_2):
                                        error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                        raise error
                                    
                                    if self.isNone(_1_2) or self.isEllipsis(_1_2):
                                        
                                        return self.probability2(_1_1, _2, length = _length)
                                    
                                    return self.probability2(_1_1, _2, frequency = _length - _1_2, length = _length)
                                
                                elif reckon(e2) == 2:
                                    
                                    _1_1, _1_2, _2_1, _2_2 = (e1[0], e1[1], e2[0], e2[1])
                                    
                                    if not self.isInteger(_1_1) or not self.isInteger(_2_1):
                                        error = TypeError("first item in an iterable is not an integer")
                                        raise error
                                    
                                    if (
                                        not self.isEllipsis(_1_2) and not self.isInteger(_1_2) and self.isNone(_1_2)) or (
                                        not self.isEllipsis(_2_2) and not self.isInteger(_2_2) and self.isNone(_2_2)
                                    ):
                                        error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                        raise error
                                    
                                    if self.isNone(_1_2) or self.isEllipsis(_1_2):
                                        
                                        if self.isNone(_2_2) or self.isEllipsis(_2_2):
                                            return self.probability2(_1_1, _2_1, length = _length)
                                        
                                        else:
                                            return self.probability2(_1_1, _2_1, frequency = _length - _2_2, length = _length)
                                        
                                    elif self.isInteger(_1_2):
                                        
                                        if self.isNone(_2_2) or self.isEllipsis(_2_2):
                                            return self.probability2(_1_1, _2_1, frequency = _1_2, length = _length)
                                        
                                        else:
                                            return self.probability2(_1_1, _2_1, frequency = _1_2, length = _length if _length > _1_2 + _2_2 else _1_2 + _2_2)
                                        
                                    else:
                                        error = RuntimeError("internal error")
                                        raise error
                                        
                                else:
                                    error = IndexError("length of every iterable may have length 1-2 only")
                                    raise error
                                
                            else:
                                error = IndexError("length of every iterable may have length 1-2 only")
                                raise error
                        
                        elif isinstance(e1, __.Mapping):
                            
                            if reckon(e1) != 1:
                                error = ValueError("expected only one pair in a dictonary, received {}".format(reckon(e1)))
                                raise error
                            
                            # 0.3.33: removed loop, replacing it with inbuilt dictionary methods
                            _v, _f = (self.toList(e1.keys())[0], self.toList(e1.values())[0])
                            
                            if isinstance(e2, (__.Sequence, __.Uniqual)):
                                
                                if self.isNone(_f) or self.isEllipsis(_f):
                                    
                                    if reckon(e2) in (1, 2):
                                        
                                        _tmp = e2[0] if reckon(e2) == 1 else (e2[0], e2[1])
                                
                                        if self.isInteger(_tmp):
                                            
                                            return self.probability2(_v, _tmp, length = _length)
                                        
                                        elif self.isTuple(_tmp):
                                            
                                            # avoid name collision
                                            _v2, _f2 = (_tmp[0], _tmp[1])
                                            
                                            if not self.isInteger(_v2):
                                                error = TypeError("first item in an iterable is not an integer")
                                                raise error
                                            
                                            if not (self.isInteger(_f2) or self.isEllipsis(_f2) or self.isNone(_f2)):
                                                error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                                raise error
                                            
                                            if self.isNone(_f2) or self.isEllipsis(_f2):
                                                return self.probability2(_v, _v2, length = _length)
                                            
                                            elif _f2 < 1:
                                                error = ValueError("second item in an iterable is negative or equal zero")
                                                raise error
                                            
                                            return self.probability2(_v, _v2, frequency = _length - _f2, length = _length)
                                
                                        else:
                                            error = RuntimeError("internal error")
                                            raise error
                                    
                                    else:
                                        error = IndexError("length of every iterable may have length 1-2 only")
                                        raise error
                                
                                elif _f < 1:
                                    error = ValueError("value in a dictionary is negative or equal zero")
                                    raise error
                                
                                if reckon(e2) in (1, 2):
                                        
                                    _tmp = e2[0] if reckon(e2) == 1 else (e2[0], e2[1])
                            
                                    if self.isInteger(_tmp):
                                        
                                        return self.probability2(_v, _tmp, length = _length)
                                    
                                    elif self.isTuple(_tmp):
                                        
                                        # avoid name collision
                                        _v2, _f2 = (_tmp[0], _tmp[1])
                                        
                                        if not self.isInteger(_v2):
                                            error = TypeError("first item in an iterable is not an integer")
                                            raise error
                                        
                                        if not (self.isInteger(_f2) or self.isEllipsis(_f2) or self.isNone(_f2)):
                                            error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                                            raise error
                                        
                                        if self.isNone(_f2) or self.isEllipsis(_f2):
                                            return self.probability2(_v, _v2, length = _length)
                                        
                                        elif _f2 < 1:
                                            error = ValueError("second item in an iterable is negative or equal zero")
                                            raise error
                                        
                                        return self.probability2(_v, _v2, frequency = _length - _f2, length = _length)
                                    
                                    else:
                                        error = RuntimeError("internal error")
                                        raise error
                                
                                else:
                                    error = IndexError("length of every iterable may have length 1-2 only")
                                    raise error
                                    
                            elif isinstance(e2, __.Mapping):
                                
                                if reckon(e2) != 1:
                                    error = ValueError("expected only one pair in a dictonary, received {}".format(reckon(e1)))
                                    raise error
                                
                                _v2, _f2 = (self.toList(e2.keys())[0], self.toList(e2.values())[0])
                                
                                if self.isNone(_f) or self.isEllipsis(_f):
                                    
                                    if self.isNone(_f2) or self.isEllipsis(_f2):
                                        
                                        return self.probability2(_v, _v2, length = _length)
                                    
                                    elif _f2 < 1:
                                        error = ValueError("value in a dictionary is negative or equal zero")
                                        raise error
                                    
                                    return self.probability2(_v, _v2, frequency = _length - _f2, length = _length)
                                
                                elif _f < 1:
                                    error = ValueError("value in a dictionary is negative or equal zero")
                                    raise error
                                
                                return self.probability2(_v, _v2, frequency = _f, length = _length if _length > _f + _f2 else _f + _f2)
                                
                            else:
                                error = TypeError("unsupported type in second item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                                raise error
                        else:
                            error = TypeError("unsupported type in first item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                            raise error
                    else:
                        error = TypeError("unsupported type in first item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                        raise error
                else:
                    error = TypeError("unsupported type in first item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                    raise error         
                        
            # END 0.3.26a3
            
            elif reckon(vf) < 2:
                
                error = self.exceptions.MissingValueError("expected at least 2 items in variable parameter '{}', received {}".format(_params[0], reckon(vf)))
                raise error
            
            # reading all items provided
            for e in vf:
                
                # value is an integer (that means it cannot have "frequency"),
                # which is "value" parameter equivalent
                if self.isInteger(e):
                    a1.append(e)
                    a2.append(e)
                    c1 += 1
                    c3 += 1
                    
                elif isinstance(e, (__.Sequence, __.Uniqual)):
                    # we have only one item, and that item is "value"
                    # 0.3.25 (additional statement for tuple and overall)
                    if reckon(e) == 1:
                        
                        if not self.isInteger(e[0]):
                            error = TypeError("every iterable may have integer as first item")
                            raise error
                        
                        a1.append(e[0])
                        a2.append(e[0])
                        c1 += 1
                        c3 += 1
                        
                    # those are, respectively, "value" and "frequency"
                    elif reckon(e) == 2:
                        
                        if not self.isInteger(e[0]):
                            error = TypeError("every iterable may have integer as first item")
                            raise error
                        
                        if not (self.isInteger(e[1]) or self.isEllipsis(e[1]) or self.isNone(e[1])):
                            error = TypeError("second item in an iterable is neither an integer, 'None', nor an ellipsis")
                            raise error
                        
                        if self.isEllipsis(e[1]) or self.isNone(e[1]):
                            a1.append(e[0])
                            a2.append(e[0])
                            c1 += 1
                            c3 += 1
                        
                        elif e[1] < 1:
                            error = ValueError("second item in an iterable is a negative integer")
                            raise error
                        
                        a1.extend([e[0] for _ in abroad(e[1])])
                        c1 += int(e[1])
                        
                    # if thought that the length is third item, that is wrong presupposition
                    else:
                        error = IndexError("length of every iterable may have length 1-2 only")
                        raise error
                    
                # 0.3.24 (dict support)
                elif isinstance(e, __.Mapping):
                    
                    if reckon(e) == 0:
                        error = ValueError("Expected at least one pair in every dictonary, received {}".format(reckon(e)))
                        raise error
                    
                        for f in e:
                            
                            if not self.isInteger(f):
                                error = KeyError(f"One of keys in dictionaries is not an integer. Ensure every key is of type 'int'. Error thrown by item: '{f}'")
                                raise error
                            
                            if not (self.isInteger(e[f]) or self.isEllipsis(e[f]) or self.isNone(e[f])):
                                error = ValueError(f"One of values in dictionaries is neither an integer, 'None', nor an ellipsis. Ensure every values satisfies this requirement. Error thrown by item: '{f}'")
                                raise error
                            
                            if e[f] < 1:
                                error = ValueError(f"One of values in dictionaries is negative integer or equal zero. Ensure every value is positive integer. Error thrown by item: '{e[f]}'")
                                raise error
                            
                            elif self.isEllipsis(e[f]) or self.isNone(e[f]):
                                a1.append(f)
                                a2.append(f)
                                c1 += 1
                                c3 += 1
                                
                            else:
                                a1.extend([f for _ in abroad(e[f])])
                                c1 += 1
                            
                # incorrect type defined
                else:
                    error = TypeError("unsupported type in an item of variable parameter '{}', expected an integer, iterable with 1-2 items (first item being integer), or dictionary with one pair (key being integer)".format(_params[0]))
                    raise error   
                
            # length minus times when single integers are provided is needed
            # to continue extended probability
            if length == self.PROBABILITY_COMPUTE:
                c2 = c1
                
            else:
                c2 = _length - c1
            
            # hint: if not that minus one, last item will be also included
            # and we want the modulo just for the last item
            if c3 > 1: c3 -= 1
            
            # that instruction shouldn't be complicated
            # also, it is impossible to get into here, since
            # most values do not have "frequency" (aka 2nd item)
            if c2 != c1 and c2 > _length:
                tmp = [0]
                tmp.clear()
                tmp += [a1[i] for i in abroad(_length)]
                a1 = tmp
                del tmp
                
            if c3 == 0: c3 = c1 # 0.3.46
                
            # look in here: used is abroad() method, but before the valid
            # loop, all items of temporary variable will become positive
            elif c2 == c1 or (c2 != c1 and c2 < _length):
                
                for i in abroad(c2):
                    
                    # there we are looking for the highest number, which will
                    # be divisible by number of integers passed to "vf" parameter
                    if i % c3 == 0:
                        c5 = i
                        break
                # this loop is nested as we use to repeat all items from a2 list
                for i in abroad(a2):
                    a1.extend([a2[i] for _ in abroad(c5 / c3)])
                        
                # modulo will be used merely there (0.3.35 patch there)
                try:
                    c4 = c2 % c3
                    
                except ZeroDivisionError:
                    c4 = 0
                
                # that one will be always done (more likely)
                # only indicated whether result in more than zero
                if c4 > 0:
                    a1.extend([a2[reckon(a2) - 1] for _ in abroad(c4)])

            # code with following 'if False' below: as a general warning, you would use Tense.architecture()
            # to find your system's architecture, because it determines about value of sys.maxsize, which is
            # max size for all sequences not entirely sure, if creating 2d sequences to increase 'length'
            # parameter value is a good idea. scrap code below is projected
            if False:
                a3 = [[0]]
                a3.clear()
                _2d_i = 0
                while _2d_i < sys.maxsize:
                    for _ in abroad(sys.maxsize):
                        a3[_2d_i].append(self.pick(a1))
                    _2d_i += 1
                return self.pick(self.pick(a3))
            
            return self.pick(a1) # this will be returned
    
    @classmethod
    def until(self, desiredString: __.Union[str, __.AVT_Sequence[str]], /, message: _opt[str] = None, caseInsensitive: bool = True):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.until
        
        Console-specific method, which will repeat the program until user won't \\
        write correct string. Case is insensitive, may be configured via \\
        optional parameter `caseInsensitive`, which by default has \\
        value `True`. Returned is reference to this class.
        
        0.3.35 - Patch in first parameter `desiredString`
        """
        s = ""
        c = False
        
        if not isinstance(desiredString, (str, __.Sequence)) or (isinstance(desiredString, __.Sequence) and not self.isString(desiredString) and not self.isList(list(desiredString), str)):
            
            error = ValueError("expected a string or string sequence")
            raise error
        
        while c:
            
            s = input(message if message is not None and message != "" else "")
            c = s.lower() != desiredString.lower() if self.isString(desiredString) else s.lower() not in (_s.lower() for _s in desiredString)
            
            if not caseInsensitive:
                c = s != desiredString if self.isString(desiredString) else s not in desiredString
                
        return self
    
    @classmethod
    def sleep(self, seconds: float, /):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.sleep
        
        Define an execution delay; equivalent to `time.sleep()`.
        """
        _time.sleep(seconds)
        return self
    
    @classmethod
    def improvedBogoSort(self, i: __.AVT_Iterable[_T], /, key: __.AVT_Callable[[_T], __.RichComparable] = ...):
        """
        @lifetime >= 0.3.42 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.improvedBogoSort
        
        Sort an iterable with improved bogo sort.
        
        Bogosort uses shuffling iterable's content to return sorted iterable. 'Improved' in the method name \\
        is its auxiliary appendix: this variant finds consecutive values from shuffled iterable, and places \\
        in a list, which will be returned, when list is sorted. This decreases amount of accesses, and shortens execution time.
        
        Returned is tuple with 2 items: accesses (integer) and sorted iterable as a list.
        """
        if isinstance(i, __.Iterable):
            
            l = list(i)
            
        else:
            
            error = TypeError("expected an iterable")
            raise error
        
        if self.isEllipsis(key):
            
            _key = None
            
        elif callable(key) and reckon(util.ParamVar(key).positional, util.ParamVar(key).universal) == 1 and reckon(util.ParamVar(key).keyword) == 0:
            
            _key = key
            
        else:
            
            error = TypeError("expected an one-argument callable or ellipsis as a key")
            raise error
        
        if self.hasattr(l, ("__gt__", "__lt__"), mode = self.constants.MODE_AND):
            pass
            
        else: # a subscripted type which is not comparable
            
            error = TypeError("expected an iterable which provides comparison operations")
            raise error
        
        _accesses = 0    
        
        for _i in abroad(1, l):
            
            while l[:_i] != sorted(l, key = _key)[:_i]:
                
                l[_i - 1:] = self.shuffle(l[_i - 1:])
                _accesses += 1
            
        return _accesses, l
        
    
    @classmethod
    def repeat(self, value: _T, times: _opt[int] = None, /): # 0.3.31: default value 'None'
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Tense.repeat
        """
        
        if times is None:
            while True:
                yield value
                
        else:
            
            if not self.isInteger(times) or times <= 0:
                error = TypeError("expected a positive integer")
                raise error
            
            for _ in abroad(times):
                yield value
                
    @classmethod
    def cycle(self, i: __.AVT_Iterable[_T], /):
        """
        @lifetime >= 0.3.34
        """
        
        if not isinstance(i, __.Iterable):
            error = TypeError("expected an iterable")
            raise error
        
        saved: list[_T] = []
        for e in i:
            yield e
            saved.append(e)
            
        while saved:
            for e in saved:
                yield e
                
    if versionInfo >= (0, 3, 46) or True:
        
        @classmethod
        def count(self, start: int = 0, step: int = 1):
            """@lifetime >= 0.3.34"""
            
            if not self.isTuple((start, step), int):
                error = TypeError("expected both parameters to be integers")
                raise error
            
            n = start
            while True:
                yield n
                n += step
        
    else:
        
        count = _itertools.count # not subscriptable, what would explain overloads
        """@lifetime >= 0.3.34"""
        
    groupby = _itertools.groupby # subscriptable only on .pyi file, not in .py
    """@lifetime >= 0.3.35"""
    
    @classmethod
    def starmap(self, f: _cal[..., _T], i: __.AVT_Iterable[__.AVT_Iterable[_Any]], /):
        """
        @lifetime >= 0.3.35
        """
        if not callable(f) or not self.isString(self.invert(dict(util.ParamVar(f).variable)).get("<args>", None)):
            error = TypeError("expected a callable with vararg")
            raise error
        
        if not isinstance(i, __.Iterable):
            error = TypeError("expected an iterable")
            raise error
        
        for e in i:
            yield f(*e)
    
    __all__ = sorted([n for n in locals() if n[:1] != "_"])
    "@lifetime >= 0.3.26rc2"
    
    __dir__ = lambda self: __all__ # 0.3.42 fixed
    "@lifetime >= 0.3.26rc2"
    
if _version.VERSION_INFO < (0, 3, 43) and False:
    
    tense = Tense
    TenseType = type(Tense)
    TenseInstance = Tense
    "@lifetime >= 0.3.27a5. Instance of `Tense` to use for `>>` and `<<` operators especially"
    
else:
    
    tense = Tense()
    TenseType = Tense

class RGB(_util.Final):
    """
    @lifetime >= 0.3.28 \\
    https://aveyzan.xyz/aveytense#aveytense.RGB
    
    Auxiliary class for `Color` class. Represents red-green-blue color representation.
    """
    def __init__(self, red = 0, green = 0, blue = 0, /):
        
        _parameters = {
            "red": red,
            "green": green,
            "blue": blue
        }
        
        for key in _parameters:
            
            if not Tense.isInteger(_parameters[key]) or (Tense.isInteger(_parameters[key]) and _parameters[key] not in abroad(0x100)):
                error = TypeError("expected a non-negative integer in parameter '{}' in range 0-255".format(key))
                raise error
        
        _tmp = _inspect.currentframe().f_back.f_lineno
        self.__frame = _tmp if type(_tmp) is int else -1
        self.__rgb = (red, green, blue)
        
    def __str__(self):
        """
        @lifetime >= 0.3.28 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?string_conversion
        """
        return "{}({})".format(type(self).__name__, ", ".join([str(e) for e in self.__rgb]))
        
    def __repr__(self):
        """
        @lifetime >= 0.3.28 \\
        [doc](https://aveyzan.xyz/aveytense#aveytense.RGB.__repr__)
        """
        return "<<'{}.{}' object :: {}> defined in line {}>".format(self.__module__, type(self).__name__, self.__str__(), self.__frame) # 0.3.41: Added line inspect
    
    def __hex__(self):
        """
        @lifetime >= 0.3.28 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?hexadecimal_conversion
        
        Provides conversion to hexadecimal format
        """
        _r = hex(self.__rgb[0])[2:] if self.__rgb[0] >= 0x10 else "0" + hex(self.__rgb[0])[2:]
        _g = hex(self.__rgb[1])[2:] if self.__rgb[1] >= 0x10 else "0" + hex(self.__rgb[1])[2:]
        _b = hex(self.__rgb[2])[2:] if self.__rgb[2] >= 0x10 else "0" + hex(self.__rgb[2])[2:]
        return "0x" + _r + _g + _b
    
    def __int__(self):
        """
        @lifetime >= 0.3.28 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?integer_conversion
        
        Converts RGB tuple into its corresponding integer representation
        """
        return int(self.__hex__()[2:], base = 16)
    
    # little deviation from type hinting in methods below
    # read document strings to figure it out
    def __lt__(self, other): 
        """
        @lifetime >= 0.3.28 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?comparison_operators
        
        To return true, following conditions must be satisfied:
        - `int(self) < int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() < other.__int__() if type(other) is type(self) else False
    
    def __gt__(self, other):
        """
        @lifetime >= 0.3.28 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?comparison_operators
        
        To return true, following conditions must be satisfied:
        - `int(self) > int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() > other.__int__() if type(other) is type(self) else False
    
    def __eq__(self, other):
        """
        @lifetime >= 0.3.28 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?comparison_operators
        
        To return true, following conditions must be satisfied:
        - `int(self) == int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() == other.__int__() if type(other) is type(self) else False
    
    def __le__(self, other):
        """
        @lifetime >= 0.3.28 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?comparison_operators
        
        To return true, following conditions must be satisfied:
        - `int(self) <= int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() <= other.__int__() if type(other) is type(self) else False
    
    def __ge__(self, other):
        """
        @lifetime >= 0.3.28 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?comparison_operators
        
        To return true, following conditions must be satisfied:
        - `int(self) >= int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() >= other.__int__() if type(other) is type(self) else False
    
    def __ne__(self, other):
        """
        @lifetime >= 0.3.28 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?comparison_operators
        
        To return true, following conditions must be satisfied:
        - `int(self) != int(other)`
        - `other` must be instance of `RGB` class
        """
        return self.__int__() != other.__int__() if type(other) is type(self) else False
    
    if False: # < 0.3.49
        
        @__.deprecated("deprecated since 0.3.41, will be removed 0.3.49. use `tuple` final property instead")
        def __pos__(self):
            """
            @lifetime >= 0.3.28 \\
            @deprecated >= 0.3.47 (up for removal in 0.3.48) \\
            https://aveyzan.xyz/aveytense#aveytense.RGB.tuple
            
            Returns a RGB tuple
            """
            return self.__rgb
        
        @__.deprecated("deprecated since 0.3.41, will be removed 0.3.49. use `tuple` final property instead")
        def __neg__(self):
            """
            @lifetime >= 0.3.28 \\
            @deprecated >= 0.3.47 (up for removal in 0.3.48) \\
            https://aveyzan.xyz/aveytense#aveytense.RGB.tuple
            
            Returns a RGB tuple
            """
            return self.__rgb
        
        @__.deprecated("deprecated since 0.3.41, will be removed 0.3.49. use `tuple` final property instead")
        def __invert__(self):
            """
            @lifetime >= 0.3.28 \\
            @deprecated >= 0.3.47 (up for removal in 0.3.48) \\
            https://aveyzan.xyz/aveytense#aveytense.RGB.tuple
            
            Returns a RGB tuple
            """
            return self.__rgb
    
    def __bytes__(self):
        """
        @lifetime >= 0.3.41 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?bytes_conversion
        
        Return a new `bytes` instance formed from the RGB tuple's integer values.
        """
        return bytes(self.__rgb) # integer-only tuple so it is convertible
    
    def __hash__(self):
        """
        @lifetime >= 0.3.41 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.__hash__
        
        Returns RGB tuple as a hash.
        """
        return hash(self.__rgb) # hashable; tuple is hashable
    
    def __bool__(self):
        """
        @lifetime >= 0.3.41 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.__bool__
        
        Converts RGB tuple to a boolean value. Always returns `True`
        """
        return True
    
    def __bin__(self):
        """
        @lifetime >= 0.3.41 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?binary_conversion
        
        Converts RGB tuple into its corresponding binary value.
        """
        return bin(self.__int__())
    
    def __oct__(self):
        """
        @lifetime >= 0.3.41 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?octal_conversion
        
        Converts RGB tuple into its corresponding octal value.
        """
        return oct(self.__int__())
    
    @_util.finalproperty
    def hex(self):
        """
        @lifetime >= 0.3.38 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?hexadecimal_conversion
        
        Provides conversion to hexadecimal format
        """
        return self.__hex__()
    
    @_util.finalproperty
    def cssHex(self):
        """
        @lifetime >= 0.3.49 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?hexadecimal_conversion
        
        Provides conversion to hexadecimal format, just with different prefix: \\
        `#` instead of `0x`, to be used in CSS
        """
        return "#" + self.hex[2:]
    
    @_util.finalproperty
    def cssRgb(self):
        """
        @lifetime >= 0.3.49 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?string_conversion
        
        Returns string with format `rgb(r, g, b)`, to be used in CSS. \\
        Equivalent to `str(self).lower()`
        """
        return self.__str__().lower()
    
    @_util.finalproperty
    def oct(self):
        """
        @lifetime >= 0.3.44 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?octal_conversion
        
        Converts RGB tuple into its corresponding octal value.
        """
        return self.__oct__()
    
    @_util.finalproperty
    def bin(self):
        """
        @lifetime >= 0.3.44 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?binary_conversion
        
        Converts RGB tuple into its corresponding binary value.
        """
        return self.__bin__()
    
    @_util.finalproperty
    def tuple(self):
        """
        @lifetime >= 0.3.38 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.tuple
        
        Returns a RGB tuple
        """
        return self.__rgb
    
    @_util.finalproperty
    def r(self):
        """
        @lifetime >= 0.3.45 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?values
        
        Returns R (red) value from RGB tuple.
        """
        return self.tuple[0]
    
    @_util.finalproperty
    def g(self):
        """
        @lifetime >= 0.3.45 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?values
        
        Returns G (green) value from RGB tuple.
        """
        return self.tuple[1]
    
    @_util.finalproperty
    def b(self):
        """
        @lifetime >= 0.3.45 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.?values
        
        Returns B (blue) value from RGB tuple.
        """
        return self.tuple[2]
    
    @staticmethod
    def fromValue(n: _uni[int, str, _util.MutableString], /):
        """
        @lifetime >= 0.3.36 \\
        https://aveyzan.xyz/aveytense#aveytense.RGB.fromValue
        
        Returns a new `RGB` class object using specific integer or string value. \\
        If string was provided, it must contain a valid number in either hexadecimal, \\
        decimal, octal or binary notation.
        
        Updated 0.3.37, 0.3.38, 0.3.39, 0.3.42, 0.3.45
        """
        
        _n = n.value if isinstance(n, _util.MutableString) else n # 0.3.45
        
        if (Tense.isInteger(_n) and Math.isInRange(_n, 0, _cp.RGB_MAX)) or (
            Tense.isString(_n) and ((_is_hexadecimal(_n) or _is_decimal(_n) or _is_octal(_n) or _is_binary(_n)) and Math.isInRange(_int_conversion(_n), 0, _cp.RGB_MAX))
        ):
        
            # General notice: using hex(...)[2:] allows to exclude '0x' prefix from the comparison, and we would need to do that anyway, so we can implicitly
            # convert a string into a RGB tuple.
            # 25.03.2025
            
            if Tense.isInteger(_n):
                
                # >= 0.3.42
                if reckon(hex(_n)[2:]) < 6:

                    _hex = "0" * (6 - reckon(hex(_n)[2:])) + hex(_n)[2:]
                    
                else:
                    
                    _hex = hex(_n)[2:]
                
            else:
                
                # >= 0.3.42
                if _is_hexadecimal(_n):
                    _interpret_base = 16
                    
                elif _is_octal(_n):
                    _interpret_base = 8
                    
                elif _is_binary(_n):
                    _interpret_base = 2
                    
                else:
                    _interpret_base = 0
                
                # >= 0.3.42
                if reckon(_n) < 6:
                    
                    # >= 0.3.45
                    if reckon(_n) == 3:
                        
                        _hex = "".join([c * 2 for c in hex(int(_n, _interpret_base))[2:]])
                        
                    else:
                        
                        _hex = "0" * (6 - reckon(hex(int(_n, _interpret_base))[2:])) + hex(int(_n, _interpret_base))[2:]
                        
                else:    
                
                    _hex = hex(int(_n, _interpret_base))[2:]
                    
            return RGB(int(_hex[: 2], 16), int(_hex[2 : 4], 16), int(_hex[4 :], 16)) # 0.3.42
        
        else:
            
            error = ValueError("expected a number in range 0-16777215")
            raise error
        
        
class RGBA(_util.Final):
    """
    @lifetime >= 0.3.37
    
    Represents red-green-blue-alpha color representation.
    """
    
    def __init__(self, red = 0, green = 0, blue = 0, alpha = 1.0):
        
        _parameters = {
            "red": red,
            "green": green,
            "blue": blue,
        }
        
        for key in _parameters:
            
            if not Tense.isInteger(_parameters[key]) or (Tense.isInteger(_parameters[key]) and _parameters[key] not in abroad(0x100)):
                
                error = TypeError("expected a non-negative integer in parameter '{}' in range 0-255".format(key))
                raise error
            
        if not Tense.isFloat(alpha) or (Tense.isFloat(alpha) and not Math.isInRange(alpha, 0, 1)):
            
            error = TypeError("expected a non-negative float in parameter '{}' in range 0-1".format("alpha"))
            raise error
        
        _tmp = _inspect.currentframe().f_back.f_lineno
        self.__frame = _tmp if type(_tmp) is int else -1
        self.__rgba = (red, green, blue, round(alpha, 2))
        
    def __str__(self):
        """
        @lifetime >= 0.3.37
        """
        return "{}({}, {})".format(type(self).__name__, ", ".join([str(e) for e in self.__rgba][:-1]), self.__rgba[-1])
    
    def __repr__(self):
        """
        @lifetime >= 0.3.37
        """
        return "<<{}.{} object: {}> defined in line {}>".format(self.__module__, type(self).__name__, self.__str__(), self.__frame)
    
    def __hex__(self):
        """
        @lifetime >= 0.3.38
        
        Provides conversion to hexadecimal format. \\
        Does not occur with alpha value - use `float()` instead.
        """
        _r = hex(self.__rgba[0])[2:] if self.__rgba[0] >= 0x10 else "0" + hex(self.__rgba[0])[2:]
        _g = hex(self.__rgba[1])[2:] if self.__rgba[1] >= 0x10 else "0" + hex(self.__rgba[1])[2:]
        _b = hex(self.__rgba[2])[2:] if self.__rgba[2] >= 0x10 else "0" + hex(self.__rgba[2])[2:]
        return "0x" + _r + _g + _b
    
    def __int__(self):
        """
        @lifetime >= 0.3.38
        
        Converts RGBA tuple into its corresponding integer representation. \\
        Does not occur with alpha value - use `float()` instead.
        """
        return int(self.__hex__()[2:], base = 16)
    
    def __float__(self):
        """
        @lifetime >= 0.3.38
        
        Returns alpha value
        """
        return self.__rgba[-1]
    
    # little deviation from type hinting in methods below
    # read document strings to figure it out
    def __lt__(self, other):
        """
        @lifetime >= 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) < int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() < float(int(other)) + float(other) if type(other) is type(self) else False
    
    def __gt__(self, other):
        """
        @lifetime >= 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) > int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() > float(int(other)) + float(other) if type(other) is type(self) else False
    
    def __eq__(self, other):
        """
        @lifetime >= 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) == int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() == float(int(other)) + float(other) if type(other) is type(self) else False
    
    def __le__(self, other):
        """
        @lifetime >= 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) <= int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() <= float(int(other)) + float(other) if type(other) is type(self) else False
    
    def __ge__(self, other):
        """
        @lifetime >= 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) >= int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() >= float(int(other)) + float(other) if type(other) is type(self) else False
    
    def __ne__(self, other):
        """
        @lifetime >= 0.3.38
        
        To return true, following conditions must be satisfied:
        - `int(self) + float(self) != int(other) + float(other)`
        - `other` must be instance of `RGBA` class
        """
        return self.__int__() + self.__float__() != float(int(other)) + float(other) if type(other) is type(self) else False
    
    @__.deprecated("Deprecated since 0.3.47, will be removed in 0.3.48. Use str(self) instead")
    def __pos__(self):
        """
        @lifetime >= 0.3.38
        
        Returns a RGBA tuple
        """
        return self.__rgba
    
    @__.deprecated("Deprecated since 0.3.47, will be removed in 0.3.48. Use str(self) instead")
    def __neg__(self):
        """
        @lifetime >= 0.3.38
        
        Returns a RGBA tuple
        """
        return self.__rgba
    
    @__.deprecated("Deprecated since 0.3.47, will be removed in 0.3.48. Use str(self) instead")
    def __invert__(self):
        """
        @lifetime >= 0.3.38
        
        Returns a RGBA tuple
        """
        return self.__rgba
    
    @staticmethod
    def fromValue(n: _uni[int, str], opacity: float, /):
        """
        @lifetime >= 0.3.38
        
        Returns a new `RGBA` class object using specific integer or string value, and opacity. \\
        If string was provided on first parameter, it must contain a valid number in either hexadecimal, \\
        decimal, octal or binary notation.
        """
        
        _rgb = RGB.fromValue(n).tuple
        
        if not Tense.isFloat(opacity) or (Tense.isFloat(opacity) and not Math.isInRange(opacity, 0, 1)):
            
            error = TypeError("expected a non-negative float in parameter '{}' in range 0-1".format("alpha"))
            raise error
        
        return RGBA(_rgb[0], _rgb[1], _rgb[2], opacity)
    
    
class CMYK(_util.Final):
    """
    @lifetime >= 0.3.28
    
    Auxiliary class for `Color` class. Represents cyan-magenta-yellow color representation. \\
    Once instantiated, returns `RGB` class instance, only with inverted color values, that is: \\
    255 is 0, 254 is 1, 253 is 2 and so on, up to 0 being 255.
    """
    
    def __new__(self, cyan = 0, magenta = 0, yellow = 0, /):
        
        _parameters = {
            "cyan": cyan,
            "magenta": magenta,
            "yellow": yellow
        }
        
        for key in _parameters:
            
            if not isinstance(_parameters[key], int) or (isinstance(_parameters[key], int) and _parameters[key] not in abroad(0x100)):
                error = TypeError("expected a non-negative integer in parameter '" + key + "' in range 0-255")
                raise error
            
        return RGB(
            0xff - cyan,
            0xff - magenta,
            0xff - yellow
        )
        
class _FileRead(__.IntegerFlag):
    "@lifetime >= 0.3.26rc2"
    CHARS = 0
    LINES = 1

# _FileReadType = _lit[_FileRead.CHARS, _FileRead.LINES] # unnecessary since 0.3.27b2
# _T_stringOrIterable = _var("_T_stringOrIterable", bound = _uni[str, _tc.Iterable[str]]) ### < 0.3.36

if _version.VERSION_INFO < (0, 3, 36) and False:
    @__.deprecated("Deprecated since 0.3.32, will be removed on 0.3.36")
    class File:
        """
        @lifetime >= 0.3.25 \\
        \\@author Aveyzan
        ```ts
        // created 18.07.2024
        in module tense
        ```
        Providing file IO operations
        """
        CHARS = _FileRead.CHARS
        LINES = _FileRead.LINES
        
        def __init__(self, fn: _FileType, mode: _FileMode = "r", /, buffering: int = -1, encoding: _opt[str] = None, errors: _opt[str] = None, newline: _opt[str] = None, closefd: bool = True, opener: _opt[_FileOpener] = None):
            
            self.__i = open(fn, mode, buffering, encoding, errors, newline, closefd, opener)
            
        @__.overload
        def read(self, mode: _lit[_FileRead.CHARS, "CHARS", "chars", "_constants", "C"] = CHARS, size: int = -1, /) -> str: ...
        
        @__.overload
        def read(self, mode: _lit[_FileRead.LINES, "LINES", "lines", "l", "L"], hint: int = -1, /) -> __.AVT_List[str]: ...
            
        def read(self, mode = CHARS, size = -1, /):
            "@lifetime >= 0.3.26rc2"
            
            if not Tense.isInteger(size):
                error = TypeError("expected 'size' parameter to be an integer")
                raise error
            
            if self.__i.readable():
                
                if mode in (self.CHARS, "CHARS", "chars", "c", "C"):
                    return self.__i.read(size)
                
                elif mode in (self.LINES, "LINES", "lines", "l", "L"):
                    return self.__i.readlines(size)
                
                else:
                    error = TypeError("expected one of constants: 'CHARS', 'LINES'")
                    raise error
                
            else:
                error = IOError("file is not open for reading")
                raise error
            
        def write(self, content: _T_stringOrIterable):
            "@lifetime >= 0.3.26rc2"
            
            if not Tense.isString(content) and not isinstance(content, __.Iterable):
                error = TypeError("Expected a string iterable or a string")
                raise error
        
            if self.__i.writable():
                
                if Tense.isString(content):
                    self.__i.write(content)
                    
                else:
                    self.__i.writelines(content)
                    
            else:
                error = IOError("file is not open for writing")
                raise error
            
        def pickle(self, o: object, protocol: _opt[int] = None, *, fixImports = True, bufferCallback: _opt[_cal[[_pickle.PickleBuffer], None]] = None):
            "@lifetime >= 0.3.26rc2"
            if isinstance(self.__i, (
                # only on binary mode files
                _io.BufferedRandom,
                _io.BufferedReader,
                _io.BufferedWriter
            )):
                _pickle.dump(o, self.__i, protocol, fix_imports = fixImports, buffer_callback = bufferCallback)
                
            else:
                error = IOError("file is not open in binary mode")
                raise error
            
        def unpickle(self, *, fixImports = True, encoding = "ASCII", errors = "strict", buffers: _opt[__.AVT_Iterable[_Any]] = ()):
            "@lifetime >= 0.3.26rc2"
            
            a = []
            
            if isinstance(self.__i, (
                # only on binary mode files
                _io.BufferedRandom,
                _io.BufferedReader,
                _io.BufferedWriter
            )):
                
                while True:
                
                    try:
                        a.append(_pickle.load(self.__i, fix_imports = fixImports, encoding = encoding, errors = errors, buffers = buffers))
                        
                    except:
                        break
                    
                return a
                
            else:
                error = IOError("file is not open in binary mode")
                raise error

# class _ChangeVarState(tc.IntegerFlag): # to 0.3.28
class _ChangeVarState(__.Enum):
    "@lifetime >= 0.3.26rc1. Internal class for `ChangeVar.setState()` method"
    I = 1
    D = 2

# _ChangeVarStateSelection = _lit[_ChangeVarState.D, _ChangeVarState.I] # unnecessary since 0.3.27b2

class ChangeVar(__.UnaryOperable, __.Comparable, __.AdditionReassignable, __.SubtractionReassignable):
    """
    @lifetime >= 0.3.26rc1 \\
    https://aveyzan.xyz/aveytense#aveytense.ChangeVar
    
    Auxiliary class for creating sentinel inside `while` loop.

    Use `~instance` to receive integer value. \\
    Use `+instance` to increment by 1. \\
    Use `-instance` to decrement by 1. \\
    Use `instance += any_int` to increment by `any_int`. \\
    Use `instance -= any_int` to decrement by `any_int`.
    """
    D = _ChangeVarState.D
    I = _ChangeVarState.I
    __v = 0
    __m = 1
    __default = 0

    def __init__(self, initialValue = 0):
        
        if not Tense.isInteger(initialValue):
            error = TypeError("expected an integer value")
            raise error
        
        self.__v = initialValue
        self.__default = initialValue

    def __pos__(self):
        self.__v += self.__m

    def __neg__(self):
        self.__v -= self.__m

    def __invert__(self):
        return self.__v
    
    def __eq__(self, other: int):
        return self.__v == other if Tense.isInteger(other) else False
    
    def __contains__(self, value: int):
        return self.__v == value if Tense.isInteger(value) else False
    
    def __ne__(self, other: int):
        return self.__v != other if Tense.isInteger(other) else False
    
    def __ge__(self, other: int):
        return self.__v >= other if Tense.isInteger(other) else False
    
    def __gt__(self, other: int):
        return self.__v > other if Tense.isInteger(other) else False
    
    def __le__(self, other: int):
        return self.__v <= other if Tense.isInteger(other) else False
    
    def __lt__(self, other: int):
        return self.__v < other if Tense.isInteger(other) else False
    
    def __iadd__(self, other: int):
        
        if not Tense.isInteger(other):
            error = TypeError("expected an integer as a right operand") # error replaced 0.3.34; earlier was NotInitializedError
            raise error
        
        _tmp = self.__v
        _tmp += other
        self.__v = _tmp
        return _tmp
    
    def __isub__(self, other: int):
        
        if not Tense.isInteger(other):
            error = TypeError("expected an integer as a right operand") # error replaced 0.3.34; earlier was NotInitializedError
            raise error
        
        _tmp = self.__v
        _tmp -= other
        self.__v = _tmp
        return _tmp
    
    def reset(self):
        """
        @lifetime >= 0.3.26rc1

        Reset the counter to value passed to the constructor, or - \\
        if `setDefault()` was invoked before - to value passed \\
        to that method.
        """
        self.__v = self.__default

    def setDefault(self, value):
        """
        @lifetime >= 0.3.26rc1

        Set a new default value. This overwrites current default value. \\
        Whether `reset()` method is used after, internal variable \\
        will have the default value, which was passed to this method. \\
        Otherwise it will refer to value passed to constructor
        """
        if not Tense.isInteger(value):
            error = TypeError("expected an integer value")
            raise error
        
        self.__default = abs(value)

    def setState(self, s: _ChangeVarState = I, m = 1):
        """
        @lifetime >= 0.3.26rc1

        Alternative for `+` and `-` unary operators.

        If `D` for `s` parameter is passed, sentinel will be decremented \\
        by 1, otherwise incremented by 1 (option `I`). Additionally, you \\
        can set a different step via `m` parameter.
        """
        _m = m
        
        if not Tense.isInteger(_m):
            error = TypeError("expected integer value for 'm' parameter")
            raise error
        
        elif abs(_m) == 0:
            _m = 1
            
        if s == self.D:
            self.__v -= abs(_m)
            
        elif s == self.I:
            self.__v += abs(_m)
            
        else:
            error = TypeError("expected 'ChangeVar.I' or 'ChangeVar.D' for 's' parameter")
            raise error
        
    def setModifier(self, m):
        """
        @lifetime >= 0.3.26rc1

        Changes behavior for `+` and `-` unary operators. \\
        If passed integer value was negative, code will \\
        retrieve absolute value of it. If 0 passed, used will be 1
        """
        _params = _get_all_params(self.setModifier)
        
        if not Tense.isInteger(m):
            error = TypeError("expected integer value in parameter '{}'".format(_params[0]))
            raise error
        
        elif abs(m) == 0:
            self.__m == 1
            
        self.__m = abs(m)

class Colors(_util.AbstractFinal):
    """
    @since 0.3.41
    
    Provides colors accessible via names. \\
    All of them are instances of class `~.RGB`.
    
    To test them, use `~.Color("<text>", 24, ~.[Colors/Color.select].<var name>)`
    """
    
    # source: https://htmlcolorcodes.com/color-names/
    
    # below since 0.3.41
    indianRed = RGB(205, 92, 92)
    lightCoral = RGB(240, 128, 128)
    salmon = RGB(250, 128, 114)
    darkSalmon = RGB(233, 150, 122)
    lightSalmon = RGB(233, 160, 122)
    crimson = RGB(220, 20, 60)
    red = RGB(255, 0, 0)
    fireBrick = RGB(178, 34, 34)
    darkRed = RGB(139, 0, 0)
    
    pink = RGB(255, 192, 203)
    lightPink = RGB(255, 182, 193)
    hotPink = RGB(255, 105, 180)
    deepPink = RGB(255, 20, 147)
    mediumVioletRed = RGB(199, 21, 133)
    
    coral = RGB(255, 127, 80)
    tomato = RGB(255, 99, 71)
    orangeRed = RGB(255, 69, 0)
    darkOrange = RGB(255, 140, 0)
    orange = RGB(255, 165, 0)
    
    gold = RGB(255, 215, 0)
    yellow = RGB(255, 255, 0)
    lightYellow = RGB(255, 255, 224)
    lemonChiffon = RGB(255, 250, 205)
    lightGoldenrodYellow = RGB(250, 250, 210)
    papayaWhip = RGB(255, 239, 213)
    moccasin = RGB(255, 228, 181)
    peachPuff = RGB(255, 218, 185)
    paleGoldenrod = RGB(238, 232, 170)
    khaki = RGB(240, 230, 140)
    darkKhaki = RGB(189, 183, 107)
    
    lavender = RGB(230, 230, 250)
    thistle = RGB(216, 191, 216)
    plum = RGB(221, 160, 221)
    violet = RGB(238, 130, 238)
    orchid = RGB(218, 112, 214)
    fuchsia = magenta = RGB(255, 0, 255)
    mediumOrchid = RGB(186, 85, 211)
    mediumPurple = RGB(147, 112, 219)
    rebeccaPurple = RGB(102, 51, 153)
    blueViolet = RGB(138, 43, 226)
    darkViolet = RGB(148, 0, 211)
    darkOrchid = RGB(153, 50, 204)
    darkMagenta = RGB(139, 0, 139)
    purple = RGB(128, 0, 128)
    indigo = RGB(75, 0, 130)
    slateBlue = RGB(106, 90, 205)
    darkSlateBlue = RGB(72, 61, 139)
    mediumSlateBlue = RGB(123, 104, 238)
    
    greenYellow = RGB(173, 255, 47)
    chartreuse = RGB(127, 255, 0)
    lawnGreen = RGB(124, 252, 0)
    lime = RGB(0, 255, 0)
    limeGreen = RGB(50, 250, 50)
    paleGreen = RGB(152, 251, 152)
    lightGreen = RGB(144, 238, 144)
    mediumSpringGreen = RGB(0, 250, 154)
    springGreen = RGB(0, 255, 127)
    mediumSeaGreen = RGB(60, 179, 113)
    seaGreen = RGB(46, 139, 87)
    forestGreen = RGB(34, 139, 34)
    green = RGB(0, 128, 0)
    darkGreen = RGB(0, 100, 0)
    yellowGreen = RGB(154, 205, 50)
    oliveDrab = RGB(107, 142, 35)
    olive = RGB(128, 128, 0)
    darkOliveGreen = RGB(85, 107, 47)
    mediumAquamarine = RGB(102, 205, 170)
    darkSeaGreen = RGB(143, 188, 139)
    lightSeaGreen = RGB(32, 178, 170)
    darkCyan = RGB(0, 139, 139)
    teal = RGB(0, 128, 128)
    
    aqua = cyan = RGB(0, 255, 255)
    lightCyan = RGB(224, 255, 255)
    paleTurquoise = RGB(175, 238, 238)
    aquamarine = RGB(127, 255, 212)
    turquoise = RGB(64, 224, 208)
    mediumTurquoise = RGB(72, 209, 204)
    darkTurquoise = RGB(0, 206, 209)
    cadetBlue = RGB(95, 158, 160)
    steelBlue = RGB(70, 130, 180)
    lightSteelBlue = RGB(176, 196, 222)
    powderBlue = RGB(176, 224, 230)
    lightBlue = RGB(173, 216, 230)
    skyBlue = RGB(135, 206, 235)
    lightSkyBlue = RGB(135, 206, 250)
    deepSkyBlue = RGB(0, 191, 255)
    dodgerBlue = RGB(30, 144, 255)
    cornflowerBlue = RGB(100, 149, 237)
    royalBlue = RGB(65, 105, 225)
    blue = RGB(0, 0, 255)
    mediumBlue = RGB(0, 0, 205)
    darkBlue = RGB(0, 0, 139)
    navy = RGB(0, 0, 128)
    midnightBlue = RGB(25, 25, 112)
    
    cornsilk = RGB(255, 248, 220)
    blanchedDiamond = RGB(255, 235, 205)
    bisque = RGB(255, 228, 196)
    navajoWhite = RGB(255, 222, 173)
    wheat = RGB(245, 222, 179)
    burlyWood = RGB(222, 184, 135)
    tan = RGB(210, 180, 140)
    rosyBrown = RGB(188, 143, 143)
    sandyBrown = RGB(244, 164, 96)
    goldenrod = RGB(218, 165, 32)
    darkGoldenrod = RGB(184, 134, 11)
    peru = RGB(205, 133, 63)
    chocolate = RGB(210, 105, 63)
    saddleBrown = RGB(139, 69, 19)
    sienna = RGB(160, 82, 45)
    brown = RGB(165, 42, 42)
    maroon = RGB(128, 0, 0)
    
    white = RGB(255, 255, 255)
    snow = RGB(255, 250, 250)
    honeyDew = RGB(240, 255, 240)
    mintCream = RGB(244, 255, 250)
    azure = RGB(240, 255, 255)
    aliceBlue = RGB(240, 248, 255)
    ghostWhite = RGB(248, 248, 255)
    whiteSmoke = RGB(245, 245, 245)
    seaShell = RGB(255, 245, 238)
    beige = RGB(245, 245, 220)
    oldLace = RGB(253, 245, 230)
    floralWhite = RGB(255, 250, 240)
    ivory = RGB(255, 255, 240)
    antiqueWhite = RGB(250, 235, 215)
    linen = RGB(250, 240, 230)
    lavenderBlush = RGB(255, 240, 245)
    mistyRose = RGB(255, 228, 225)
    
    gainsboro = RGB(220, 220, 220)
    lightGray = RGB(211, 211, 211)
    silver = RGB(192, 192, 192)
    gray = RGB(128, 128, 128)
    dimGray = RGB(105, 105, 105)
    lightSlateGray = RGB(119, 136, 153)
    slateGray = RGB(112, 128, 144)
    darkSlateGray = RGB(47, 79, 79)
    black = RGB(0, 0, 0)
    # above since 0.3.41
    
    # source: https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit
    
    # below since 0.3.41; more to be added in 0.3.42 or later
    mode256_0 = mode256_16 = black
    mode256_1 = RGB.fromValue(0x800000)
    mode256_2 = RGB.fromValue(0x008000)
    mode256_3 = RGB.fromValue(0x808000)
    mode256_4 = RGB.fromValue(0x000080)
    mode256_5 = RGB.fromValue(0x800080)
    mode256_6 = RGB.fromValue(0x008080)
    mode256_7 = RGB.fromValue(0xc0c0c0)
    mode256_8 = RGB.fromValue(0x808080)
    mode256_9 = mode256_196 = red
    mode256_10 = mode256_46 = lime
    mode256_11 = mode256_226 = yellow
    mode256_12 = mode256_21 = blue
    mode256_13 = mode256_201 = fuchsia
    mode256_14 = mode256_51 = aqua
    mode256_15 = mode256_231 = white
    ### BELOW: 0.3.48
    mode256_17 = RGB.fromValue(0x00005f)
    mode256_18 = RGB.fromValue(0x000087)
    mode256_19 = RGB.fromValue(0x0000af)
    mode256_20 = RGB.fromValue(0x0000d7)
    # 21 = html blue
    mode256_22 = RGB.fromValue(0x005f00)
    mode256_23 = RGB.fromValue(0x005f5f)
    mode256_24 = RGB.fromValue(0x005f87)
    mode256_25 = RGB.fromValue(0x005faf)
    mode256_26 = RGB.fromValue(0x005fd7)
    mode256_27 = RGB.fromValue(0x005fff)
    mode256_28 = RGB.fromValue(0x008700)
    mode256_29 = RGB.fromValue(0x00875f)
    mode256_30 = RGB.fromValue(0x008787)
    mode256_31 = RGB.fromValue(0x0087af)
    mode256_32 = RGB.fromValue(0x0087d7)
    mode256_33 = RGB.fromValue(0x0087ff)
    mode256_34 = RGB.fromValue(0x00af00)
    mode256_35 = RGB.fromValue(0x00af5f)
    mode256_36 = RGB.fromValue(0x00af87)
    mode256_37 = RGB.fromValue(0x00afaf)
    mode256_38 = RGB.fromValue(0x00afd7)
    mode256_39 = RGB.fromValue(0x00afff)
    mode256_40 = RGB.fromValue(0x00d700)
    mode256_41 = RGB.fromValue(0x00d75f)
    mode256_42 = RGB.fromValue(0x00d787)
    mode256_43 = RGB.fromValue(0x00d7af)
    mode256_44 = RGB.fromValue(0x00d7d7)
    mode256_45 = RGB.fromValue(0x00d7ff)
    # 46 = html lime
    mode256_47 = RGB.fromValue(0x00ff5f)
    mode256_48 = RGB.fromValue(0x00ff87)
    mode256_49 = RGB.fromValue(0x00ffaf)
    mode256_50 = RGB.fromValue(0x00ffd7)
    # 51 = html cyan/aqua
    ###
    mode256_232 = RGB.fromValue(0x080808)
    mode256_233 = RGB.fromValue(0x121212)
    mode256_234 = RGB.fromValue(0x1c1c1c)
    mode256_235 = RGB.fromValue(0x262626)
    mode256_236 = RGB.fromValue(0x303030)
    mode256_237 = RGB.fromValue(0x3a3a3a)
    mode256_238 = RGB.fromValue(0x444444)
    mode256_239 = RGB.fromValue(0x4e4e4e)
    mode256_240 = RGB.fromValue(0x585858)
    mode256_241 = RGB.fromValue(0x626262)
    mode256_242 = RGB.fromValue(0x6c6c6c)
    mode256_243 = RGB.fromValue(0x767676)
    mode256_244 = mode256_8 # same color (0x808080)
    mode256_245 = RGB.fromValue(0x8a8a8a)
    mode256_246 = RGB.fromValue(0x949494)
    mode256_247 = RGB.fromValue(0x9e9e9e)
    mode256_248 = RGB.fromValue(0xa8a8a8)
    mode256_249 = RGB.fromValue(0xb2b2b2)
    mode256_250 = RGB.fromValue(0xbcbcbc)
    mode256_251 = RGB.fromValue(0xc6c6c6)
    mode256_252 = RGB.fromValue(0xd0d0d0)
    mode256_253 = RGB.fromValue(0xdadada)
    mode256_254 = RGB.fromValue(0xe4e4e4)
    mode256_255 = RGB.fromValue(0xeeeeee)
    # above since 0.3.41
    
    __all__ = [k for k in locals() if not k.startswith("_")] # >= 0.3.41

Colors = _InternalHelper(Colors, "no_reassign")
Colours = Colors

del _InternalHelper

class Color(__.ModuloOperable[_ColorStylingType, str]):
    """
    @lifetime >= 0.3.26rc1 \\
    https://aveyzan.xyz/aveytense#aveytense.Color
    
    Deputy of experimental class `aveytense.extensions.ANSIColor` (>= 0.3.24; < 0.3.26rc1).
    
    This class uses ANSI escape code for color purposes.

    Unary `+` and `-`, and `~` operators allow to get colored string. \\
    Since 0.3.34 using `str()` will also return colored string, other 3 ways \\
    to do so will remain due to compatibility with older versions of AveyTense.
    
    Modulo operator (`%`) allows to change the font style. The right operand must be \\
    an appropriate constant or lowercased string literal (for single font styles).
    Examples::
    
        Color("Tense") % Color.BOLD
        Color("Countryside!", 8, 0o105) % Color.ITALIC # italic, blue text
        Color("Creativity!", 24, 0xc0ffee) % Color.BOLD # bold, c0ffee hex code text
        Color("Illusive!", 24, 0, 0xc0ffee) % Color.BOLD # bold, c0ffee hex code background, black text
    

    Since 0.3.26rc2 you can use constants, which grant more than one font style simultaneously, like::
    
        Color("Lines!", 8, 93) % Color.UOLINE # lines above and below text

    **Warning**: 24-bit colors load longer than colors from lower bit shelves. In this case it is \\
    recommended to stick to 8-bit colors, but if there isn't a satisfying color, 24-bit color support \\
    will be kept. It is also somewhat a reason of `RGB` and `CMYK` colors existence.
    """
    __fg = None
    __bg = None
    if False: # 0.3.27
        __un = None
    __text = ""
    __bits = 8 # 24 to 0.3.34
    
    select = Colors
    """@since 0.3.41. Alias to `~.Colors`"""

    NORMAL = _ColorStyling.NORMAL
    "@lifetime >= 0.3.26rc1. Mere text"
    
    BOLD = _ColorStyling.BOLD
    "@lifetime >= 0.3.26rc1. Text becomes bold"
    
    FAINT = _ColorStyling.FAINT
    "@lifetime >= 0.3.26rc1. Also works as 'decreased intensity' or 'dim'"
    
    ITALIC = _ColorStyling.ITALIC
    "@lifetime >= 0.3.26rc1. Text becomes oblique. Not widely supported"
    
    UNDERLINE = _ColorStyling.UNDERLINE
    "@lifetime >= 0.3.26rc1. Text becomes underlined. Marked *experimental* as experimenting with underline colors, but normally it is OK to use"
    
    SLOW_BLINK = _ColorStyling.SLOW_BLINK
    "@lifetime >= 0.3.26rc1. Text will blink for less than 150 times per minute"
    
    RAPID_BLINK = _ColorStyling.RAPID_BLINK
    "@lifetime >= 0.3.26rc1. Text will blink for more than 150 times per minute. Not widely supported"
    
    REVERSE = _ColorStyling.REVERSE
    "@lifetime >= 0.3.26rc2. Swap text and background colors"
    
    HIDE = _ColorStyling.HIDE
    "@lifetime >= 0.3.26rc1. Text becomes transparent"
    
    STRIKE = _ColorStyling.STRIKE
    "@lifetime >= 0.3.26rc1. Text becomes crossed out"
    
    DOUBLE_UNDERLINE = _ColorStyling.DOUBLE_UNDERLINE
    "@lifetime >= 0.3.26rc2. Text becomes doubly underlined"
    
    # PROPORTIONAL = _ColorStyling.PROPORTIONAL
    "\\@lifetime >= 0.3.26rc1; < 0.3.26rc2. Proportional spacing. *Experimental*"
    
    FRAME = _ColorStyling.FRAME
    "@lifetime >= 0.3.26rc1. Implemented in mintty as 'emoji variation selector'"
    
    ENCIRCLE = _ColorStyling.ENCIRCLE
    "@lifetime >= 0.3.26rc1. Implemented in mintty as 'emoji variation selector'"
    
    OVERLINE = _ColorStyling.OVERLINE
    "@lifetime >= 0.3.26rc1. Text becomes overlined"
    
    SUPERSCRIPT = _ColorStyling.SUPERSCRIPT
    "@lifetime >= 0.3.26rc2. Text becomes superscripted (implemented in mintty only)"
    
    SUBSCRIPT = _ColorStyling.SUBSCRIPT
    "@lifetime >= 0.3.26rc2. Text becomes subscripted (implemented in mintty only)"
    
    # 2x
    BOLD_ITALIC = _ColorAdvancedStyling.BOLD_ITALIC
    "@lifetime >= 0.3.26rc2. Text becomes bold and oblique"
    
    BOLD_UNDERLINE = _ColorAdvancedStyling.BOLD_UNDERLINE
    "@lifetime >= 0.3.26rc2. Text becomes bold and underlined"
    
    BOLD_STRIKE = _ColorAdvancedStyling.BOLD_STRIKE
    "@lifetime >= 0.3.26rc2. Text becomes bold and crossed out"
    
    BOLD_OVERLINE = _ColorAdvancedStyling.BOLD_OVERLINE
    "@lifetime >= 0.3.26rc2. Text becomes bold and overlined"
    
    ITALIC_UNDERLINE = _ColorAdvancedStyling.ITALIC_UNDERLINE
    "@lifetime >= 0.3.26rc2. Text becomes oblique and underlined"
    
    ITALIC_STRIKE = _ColorAdvancedStyling.ITALIC_STRIKE
    "@lifetime >= 0.3.26rc2. Text becomes oblique and crossed out"
    
    ITALIC_OVERLINE = _ColorAdvancedStyling.ITALIC_OVERLINE
    "@lifetime >= 0.3.26rc2. Text becomes oblique and overlined"
    
    UNDERLINE_STRIKE = _ColorAdvancedStyling.UNDERLINE_STRIKE
    "@lifetime >= 0.3.26rc2. Text becomes underlined and crossed out"
    
    UOLINE = _ColorAdvancedStyling.UOLINE
    "@lifetime >= 0.3.26rc2. Alias to underline-overline. Text gets lines above and below"
    
    STRIKE_OVERLINE = _ColorAdvancedStyling.STRIKE_OVERLINE
    "@lifetime >= 0.3.26rc2. Text becomes crossed out and overlined"
    
    # 3x
    BOLD_ITALIC_UNDERLINE = _ColorAdvancedStyling.BOLD_ITALIC_UNDERLINE
    "@lifetime >= 0.3.26rc2. Text becomes bold, oblique and underlined"
    
    BOLD_ITALIC_STRIKE = _ColorAdvancedStyling.BOLD_ITALIC_STRIKE
    "@lifetime >= 0.3.26rc2"
    
    BOLD_ITALIC_OVERLINE = _ColorAdvancedStyling.BOLD_ITALIC_OVERLINE
    "@lifetime >= 0.3.26rc2"
    
    BOLD_UNDERLINE_STRIKE = _ColorAdvancedStyling.BOLD_UNDERLINE_STRIKE
    "@lifetime >= 0.3.26rc2"
    
    BOLD_UOLINE = _ColorAdvancedStyling.BOLD_UOLINE
    "@lifetime >= 0.3.26rc2"
    
    ITALIC_UNDERLINE_STRIKE = _ColorAdvancedStyling.ITALIC_UNDERLINE_STRIKE
    "@lifetime >= 0.3.26rc2"
    
    ITALIC_UOLINE = _ColorAdvancedStyling.ITALIC_UOLINE
    "@lifetime >= 0.3.26rc2"
    
    ITALIC_STRIKE_OVERLINE = _ColorAdvancedStyling.ITALIC_STRIKE_OVERLINE
    "@lifetime >= 0.3.26rc2"
    
    STRIKE_UOLINE = _ColorAdvancedStyling.STRIKE_UOLINE
    "@lifetime >= 0.3.26rc2"
        
    def __prepare_return(self):
        
        return _colorize(self.__text, self.__bits, self.__fg, self.__bg)
    
    if _version.VERSION_INFO >= (0, 3, 27) or True:
        
        def __init__(self, text: __.Union[str, _util.MutableString], /, bits: _Bits = 8, foregroundColor: _Color = None, backgroundColor: _Color = None): # slash since 0.3.26rc2
            """
            @lifetime >= 0.3.26rc1. Parameters:
            - `text` - string to be colored. Required parameter
            - `bits` - number of bits, possible values: 3, 4, 8, 24. Defaults to 24 (since 0.3.26rc2 - 8)
            - `foregroundColor` - color of the foreground (text). String/integer/`None`. Defaults to `None`
            - `backgroundColor` - color of the background. String/integer/`None`. Defaults to `None`
            
            See https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit for color palette outside 24-bit colors
            """
            _os.system("color")
            
            _params = _get_all_params(self.__init__)
            
            # 0.3.41: Prevent ANSI escape code to be passed to the text (27.02.2025)
            # 0.3.45: Add support for ~.util.MutableString
            if not isinstance(text, (str, _util.MutableString)) or ((Tense.isString(text) and Tense.test(text, r"\x1b\[\d(;\d)*m")) or (isinstance(text, _util.MutableString) and Tense.test(text.value, r"\x1b\[\d(;\d)*m"))):
                error = TypeError("expected string value for '{}' parameter".format(_params[0]))
                raise error
            
            if not Tense.isInteger(bits) or (Tense.isInteger(bits) and bits not in (3, 4, 8, 24)):
                error = TypeError("expected integer value: 3, 4, 8 or 24, for '{}' parameter".format(_params[1]))
                raise error
            
            for e in (foregroundColor, backgroundColor):
                
                # Issue caught and fixed on 0.3.37 (GeckoGM)
                # 0.3.38: Fixed for RGB instances
                # Unfortunately, support for 'types.UnionType' is provided on 3.10, and the project's minimal version is 3.9,
                # so we need to change it (0.3.41); it was an issue with ~.Tense.isNone(). (0.3.41)
                
                if not isinstance(e, (int, str, RGB, __.NoneType)):
                    error = TypeError("expected integer, string or 'None' value for both foreground and background color parameters")
                    raise error
                
                elif Tense.isString(e) and (
                    # changing this order may cause easier error
                    not Tense.isHexadecimal(e) and
                    not Tense.isNumeric(e) and
                    not Tense.isOctal(e) and
                    not Tense.isBinary(e)
                ):
                    error = TypeError("malformed string in either foreground or background color parameters, expected clean binary, decimal, hexademical or octal string")
                    raise error
                
                elif bits == 24 and not Tense.isNone(e) and (
                    Tense.isInteger(e) and e not in abroad(0x1000000) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x1000000) or
                    isinstance(e, RGB) and int(e) not in abroad(0x1000000)
                ):
                    error = ValueError("for 24-bit colors, expected \"RGB\" class instance of integer value, integer or string value in range 0-16777215")
                    raise error
                
                elif bits == 8 and not Tense.isNone(e) and (
                    Tense.isInteger(e) and e not in abroad(0x100) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x100) or isinstance(e, RGB)
                ):
                    error = ValueError("for 8-bit colors, expected integer or string value in range 0-255. Cannot be used with \"RGB\" class instance")
                    raise error
                
                elif bits == 4 and not Tense.isNone(e) and (
                    Tense.isInteger(e) and e not in abroad(0x10) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x10) or isinstance(e, RGB)
                ):
                    error = ValueError("for 4-bit colors, expected integer or string value in range 0-15. Cannot be used with \"RGB\" class instance")
                    raise error
                
                elif bits == 3 and not Tense.isNone(e) and (
                    Tense.isInteger(e) and e not in abroad(0x8) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x8) or isinstance(e, RGB)
                ):
                    error = ValueError("for 3-bit colors, expected integer or string value in range 0-7. Cannot be used with \"RGB\" class instance")
                    raise error
            
            _tmp = _inspect.currentframe().f_back.f_lineno
            self.__frame = _tmp if type(_tmp) is int else -1
            self.__text = text if Tense.isString(text) else text.value # 0.3.45
            self.__bits = bits
            self.__fg = foregroundColor if Tense.isInteger(foregroundColor) else _int_conversion(foregroundColor) if Tense.isString(foregroundColor) else int(foregroundColor) if isinstance(foregroundColor, RGB) else None
            self.__bg = backgroundColor if Tense.isInteger(backgroundColor) else _int_conversion(backgroundColor) if Tense.isString(backgroundColor) else int(backgroundColor) if isinstance(backgroundColor, RGB) else None
            
    else:
        def __init__(self, text: str, /, bits: _Bits = 8, foregroundColor: _Color = None, backgroundColor: _Color = None, underlineColor: _Color = None):
            
            _os.system("color")
            
            if not Tense.isString(text):
                error = TypeError("Expected string value for 'text' parameter")
                raise error
            
            if not Tense.isInteger(bits) or (Tense.isInteger(bits) and bits not in (3, 4, 8, 24)):
                error = TypeError("Expected integer value: 3, 4, 8 or 24, for 'bits' parameter")
                raise error
            
            for e in (foregroundColor, backgroundColor, underlineColor):
                
                if not Tense.isInteger(e) and not Tense.isString(e) and e is not None:
                    error = TypeError(f"Expected integer, string or 'None' value for '{e.__name__}' parameter")
                    raise error
                
                elif Tense.isString(e) and (
                    not _is_hexadecimal(e) and
                    not _is_decimal(e) and
                    not _is_octal(e) and
                    not _is_binary(e)
                ):
                    error = TypeError(f"Malformed string in parameter 'e', expected clean binary, decimal, hexademical or octal string")
                    raise error
                
                elif bits == 24 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x1000000) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x1000000)
                ):
                    error = ValueError(f"For 24-bit colors, expected integer or string value in range 0-16777215")
                    raise error
                
                elif bits == 8 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x100) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x100)
                ):
                    error = ValueError(f"For 8-bit colors, expected integer or string value in range 0-255")
                    raise error
                
                elif bits == 4 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x10) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x10)
                ):
                    error = ValueError(f"For 4-bit colors, expected integer or string value in range 0-15")
                    raise error
                
                elif bits == 3 and e is not None and (
                    Tense.isInteger(e) and e not in abroad(0x8) or
                    Tense.isString(e) and _int_conversion(e) not in abroad(0x8)
                ):
                    error = ValueError(f"For 3-bit colors, expected integer or string value in range 0-7")
                    raise error
                
            self.__text = text
            self.__bits = bits
            self.__fg = foregroundColor if Tense.isInteger(foregroundColor) else _int_conversion(foregroundColor) if Tense.isString(foregroundColor) else None
            self.__bg = backgroundColor if Tense.isInteger(backgroundColor) else _int_conversion(backgroundColor) if Tense.isString(backgroundColor) else None
            self.__un = underlineColor if Tense.isInteger(underlineColor) else _int_conversion(underlineColor) if Tense.isString(underlineColor) else None
    
    def clear(self):
        """
        @lifetime >= 0.3.26rc1
        
        Clear every color for foreground, background and underline. Should \\
        be used before `setBits()` method invocation to avoid conflicts. \\
        By default bits value is reset to 24. Since 0.3.27b1 - 8.
        """
        self.__fg = None
        self.__bg = None
        if False: # 0.3.27
            self.__un = None
        self.__bits = 8
        return self
    
    def setBits(self, bits: _Bits = 8, /):
        """
        @lifetime >= 0.3.26rc1

        Possible values: 3, 4, 8, 24. Default is 24. \\
        Since 0.3.26rc2 default value is 8.
        """
        
        if not Tense.isInteger(bits) or (Tense.isInteger(bits) and bits not in (3, 4, 8, 24)):
            error = TypeError("expected integer value: 3, 4, 8 or 24, for 'bits' parameter")
            raise error
        
        # for e in (self.__fg, self.__bg, self.__un): ### removed 0.3.27
        for e in (self.__fg, self.__bg):
            
            if e is not None:
                
                if bits == 24 and e not in abroad(0x1000000):
                    error = ValueError("internal conflict caught while setting 'bits' value to 24. One of foreground or background values is beyond range 0-16777215. To prevent this conflict, use method 'Color.clear()'.")
                    raise error
                
                elif bits == 8 and e not in abroad(0x100):
                    error = ValueError("internal conflict caught while setting 'bits' value to 8. One of foreground or background values is beyond range 0-255. To prevent this conflict, use method 'Color.clear()'.")
                    raise error
                
                elif bits == 4 and e not in abroad(0x10):
                    error = ValueError("internal conflict caught while setting 'bits' value to 4. One of foreground or background values is beyond range 0-15. To prevent this conflict, use method 'Color.clear()'.")
                    raise error
                
                elif bits == 3 and e not in abroad(0x8):
                    error = ValueError("internal conflict caught while setting 'bits' value to 3. One of foreground or background values is beyond range 0-7. To prevent this conflict, use method 'Color.clear()'.")
                    raise error
                
        self.__bits = bits
    
    def setForegroundColor(self, color: _Color = None, /):
        """
        @lifetime >= 0.3.26rc1
        
        Set foreground color manually.
        """
        _c = color if Tense.isInteger(color) or color is None else _int_conversion(color) if Tense.isString(color) else int(color) if isinstance(color, RGB) else None
        
        if _c is not None:
            
            if self.__bits == 3 and _c not in abroad(0x8):
                error = ValueError(f"for 3-bit colors, expected integer or string value in range 0-7")
                raise error
            
            elif self.__bits == 4 and _c not in abroad(0x10):
                error = ValueError(f"for 4-bit colors, expected integer or string value in range 0-15")
                raise error
            
            elif self.__bits == 8 and _c not in abroad(0x100):
                error = ValueError(f"for 8-bit colors, expected integer or string value in range 0-255")
                raise error
            
            elif self.__bits == 24 and _c not in abroad(0x1000000):
                error = ValueError(f"for 24-bit colors, expected integer, string or RGB/CMYK tuple value in range 0-16777215")
                raise error
            
            else:
                error = ValueError(f"internal 'bits' variable value is not one from following: 3, 4, 8, 24")
                raise error
            
        self.__fg = _c
        return self
    
    def setBackgroundColor(self, color: _Color = None, /):
        """
        @lifetime >= 0.3.26rc1
        
        Set background color manually.
        """
        _c = color if Tense.isInteger(color) or color is None else _int_conversion(color) if Tense.isString(color) else int(color) if isinstance(color, RGB) else None
        
        if _c is not None:
            
            if self.__bits == 3 and _c not in abroad(0x8):
                error = ValueError(f"for 3-bit colors, expected integer or string value in range 0-7")
                raise error
            
            elif self.__bits == 4 and _c not in abroad(0x10):
                error = ValueError(f"for 4-bit colors, expected integer or string value in range 0-15")
                raise error
            
            elif self.__bits == 8 and _c not in abroad(0x100):
                error = ValueError(f"for 8-bit colors, expected integer or string value in range 0-255")
                raise error
            
            elif self.__bits == 24 and _c not in abroad(0x1000000):
                error = ValueError(f"for 24-bit colors, expected integer, string or RGB/CMYK tuple value in range 0-16777215")
                raise error
            
            else:
                error = ValueError(f"internal 'bits' variable value is not one from following: 3, 4, 8, 24")
                raise error
            
        self.__bg = _c
        return self
    
    if _version.VERSION_INFO < (0, 3, 27) and False:
        def setUnderlineColor(self, color: _Color = None, /):
            """
            @lifetime >= 0.3.26rc1
            
            Set underline color manually. *Experimental* \\
            Since 0.3.26rc2 only accepted value is `None`.
            """
            _c = color if Tense.isInteger(color) or color is None else _int_conversion(color)
            if _c is not None:
                if self.__bits == 3 and _c not in abroad(0x8):
                    error = ValueError(f"For 3-bit colors, expected integer or string value in range 0-7")
                    raise error
                
                elif self.__bits == 4 and _c not in abroad(0x10):
                    error = ValueError(f"For 4-bit colors, expected integer or string value in range 0-15")
                    raise error
                
                elif self.__bits == 8 and _c not in abroad(0x100):
                    error = ValueError(f"For 8-bit colors, expected integer or string value in range 0-255")
                    raise error
                
                elif self.__bits == 24 and _c not in abroad(0x1000000):
                    error = ValueError(f"For 24-bit colors, expected integer or string value in range 0-16777215")
                    raise error
                
                else:
                    error = ValueError(f"Internal 'bits' variable value is not one from following: 3, 4, 8, 24")
                    raise error
                
            self.__un = _c
            return self
    
    if False: # < 0.3.48
    
        def __pos__(self):
            """@lifetime >= 0.3.26rc1. Receive colored string"""
            return self.__prepare_return()
        
        def __neg__(self):
            """@lifetime >= 0.3.26rc1. Receive colored string"""
            return self.__prepare_return()
        
        def __invert__(self):
            """@lifetime >= 0.3.26rc1. Receive colored string"""
            return self.__prepare_return()
    
    def __str__(self):
        """@lifetime >= 0.3.34. Receive colored string"""
        return self.__prepare_return()
    
    def __repr__(self):
        """@lifetime >= 0.3.35"""
        return "<<'{}.{}' object :: {}(\"{}\")> defined in line {}>".format(
            self.__module__,
            type(self).__name__,
            type(self).__name__,
            self.__text,
            self.__frame
        )
    
    def __mod__(self, other: _ColorStylingType):
        """
        @lifetime >= 0.3.26rc1
        
        Further styling. Use constant, which is in `__constants__` attribute.
        """
        # below: since 0.3.26rc1
        if other in (self.NORMAL,):
            return self.__prepare_return()
        
        elif other in (self.BOLD,):
            return _re.sub(r"^\x1b\[", "\x1b[1;", self.__prepare_return())
        
        elif other in (self.FAINT,):
            return _re.sub(r"\x1b\[", "\x1b[2;", self.__prepare_return())
        
        elif other in (self.ITALIC,):
            return _re.sub(r"\x1b\[", "\x1b[3;", self.__prepare_return())
        
        elif other in (self.UNDERLINE,):
            return _re.sub(r"\x1b\[", "\x1b[4;", self.__prepare_return())
        
        elif other in (self.SLOW_BLINK,):
            return _re.sub(r"\x1b\[", "\x1b[5;", self.__prepare_return())
        
        elif other in (self.RAPID_BLINK,):
            return _re.sub(r"\x1b\[", "\x1b[6;", self.__prepare_return())
        
        # below: since 0.3.26rc2
        elif other in (self.REVERSE,):
            return _re.sub(r"\x1b\[", "\x1b[7;", self.__prepare_return())
        
        # below: since 0.3.26rc1
        elif other in (self.HIDE,):
            return _re.sub(r"\x1b\[", "\x1b[8;", self.__prepare_return())
        
        elif other in (self.STRIKE,):
            return _re.sub(r"\x1b\[", "\x1b[9;", self.__prepare_return())
        
        elif other in (self.DOUBLE_UNDERLINE,):
            return _re.sub(r"\x1b\[", "\x1b[21;", self.__prepare_return())
        
        # elif other == self.PROPORTIONAL:
        #    return _re.sub(r"\x1b\[", "\x1b[26;", self.__prepare_return())
        
        elif other in (self.FRAME,):
            return _re.sub(r"\x1b\[", "\x1b[51;", self.__prepare_return())
        
        elif other in (self.ENCIRCLE,):
            return _re.sub(r"\x1b\[", "\x1b[52;", self.__prepare_return())
        
        elif other in (self.OVERLINE,):
            return _re.sub(r"\x1b\[", "\x1b[53;", self.__prepare_return())
        
        # below: since 0.3.26rc2
        elif other in (self.SUPERSCRIPT,):
            return _re.sub(r"\x1b\[", "\x1b[73;", self.__prepare_return())
        
        elif other in (self.SUBSCRIPT,):
            return _re.sub(r"\x1b\[", "\x1b[74;", self.__prepare_return())
        # 2x; since 0.3.26rc2
        elif other == self.BOLD_ITALIC:
            return _re.sub(r"\x1b\[", "\x1b[1;3;", self.__prepare_return())
        
        elif other == self.BOLD_UNDERLINE:
            return _re.sub(r"\x1b\[", "\x1b[1;4;", self.__prepare_return())
        
        elif other == self.BOLD_STRIKE:
            return _re.sub(r"\x1b\[", "\x1b[1;9;", self.__prepare_return())
        
        elif other == self.BOLD_OVERLINE:
            return _re.sub(r"\x1b\[", "\x1b[1;53;", self.__prepare_return())
        
        elif other == self.ITALIC_UNDERLINE:
            return _re.sub(r"\x1b\[", "\x1b[3;4;", self.__prepare_return())
        
        elif other == self.ITALIC_STRIKE:
            return _re.sub(r"\x1b\[", "\x1b[3;9;", self.__prepare_return())
        
        elif other == self.ITALIC_OVERLINE:
            return _re.sub(r"\x1b\[", "\x1b[3;53;", self.__prepare_return())
        
        elif other == self.UNDERLINE_STRIKE:
            return _re.sub(r"\x1b\[", "\x1b[4;9;", self.__prepare_return())
        
        elif other == self.UOLINE:
            return _re.sub(r"\x1b\[", "\x1b[4;53;", self.__prepare_return())
        
        elif other == self.STRIKE_OVERLINE:
            return _re.sub(r"\x1b\[", "\x1b[9;53;", self.__prepare_return())
        
        # 3x; since 0.3.26rc2
        elif other == self.BOLD_ITALIC_UNDERLINE:
            return _re.sub(r"\x1b\[", "\x1b[1;3;4;", self.__prepare_return())
        
        elif other == self.BOLD_ITALIC_STRIKE:
            return _re.sub(r"\x1b\[", "\x1b[1;3;9;", self.__prepare_return())
        
        elif other == self.BOLD_ITALIC_OVERLINE:
            return _re.sub(r"\x1b\[", "\x1b[1;3;53;", self.__prepare_return())
        
        elif other == self.BOLD_UNDERLINE_STRIKE:
            return _re.sub(r"\x1b\[", "\x1b[1;4;9;", self.__prepare_return())
        
        elif other == self.BOLD_UOLINE:
            return _re.sub(r"\x1b\[", "\x1b[1;4;53;", self.__prepare_return())
        
        elif other == self.ITALIC_UNDERLINE_STRIKE:
            return _re.sub(r"\x1b\[", "\x1b[3;4;9;", self.__prepare_return())
        
        elif other == self.ITALIC_UOLINE:
            return _re.sub(r"\x1b\[", "\x1b[3;4;53;", self.__prepare_return())
        
        elif other == self.ITALIC_STRIKE_OVERLINE:
            return _re.sub(r"\x1b\[", "\x1b[3;9;53;", self.__prepare_return())
        
        elif other == self.STRIKE_UOLINE:
            return _re.sub(r"\x1b\[", "\x1b[4;9;53;", self.__prepare_return())
        
        else:
            
            if True: # >= 0.3.27
                error = TypeError("expected one from following constant values as a right operand: " + repr(self.__constants__) + " or a specific lowercased string literal when single font style was meant to be applied")
                
            else: # < 0.3.27
                error = TypeError(
                    "Expected any from constant values: " + repr(self.__constants__) + ". You are discouraged to do common operations on these constants, like union as in case of regular expression flags, to satisfy this requirement, because it "
                    "won't warrant that returned string will be styled as thought"
                )
                
            raise error
        
    __all__ = [k for k in locals() if not k.startswith("_")]
    "@lifetime >= 0.3.26rc2. Returns list of all non-underscore-preceded members of class `~.Color`"
        
    __dir__ = lambda self: __all__
    "@lifetime >= 0.3.26rc2"
    
    __constants__ = [n for n in __all__ if n.isupper()]
    """
    @lifetime >= 0.3.26rc2

    Returns list of constants. These can be used as right operand for `%` operator. \\
    They are sorted as in ANSI escape code table, in ascending order
    """
    
Colour = Color
"""
@lifetime >= 0.3.37: type alias `aveytense.Colour`
"""

__author__ = "Aveyzan <aveyzan@gmail.com>"
"@lifetime >= 0.3.26rc3"
__license__ = "MIT"
"@lifetime >= 0.3.26rc3"
__version__ = _version.VERSION
"@lifetime >= 0.3.26rc3"

__all__ = sorted([n for n in globals() if n[:1] != "_"])
__all_deprecated__ = sorted([n for n in globals() if hasattr(globals()[n], "__deprecated__")])
"""
@since 0.3.41

Returns all deprecated declarations within this module.
"""

def __dir__():
    return __all__

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error
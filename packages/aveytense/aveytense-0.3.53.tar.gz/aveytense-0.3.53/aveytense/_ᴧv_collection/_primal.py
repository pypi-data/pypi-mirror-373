"""
@lifetime >= 0.3.24 \\
© 2023-Present Aveyzan // License: MIT

Defines first components for `aveytense` module. Use `aveytense` module instead
"""

import sys as _sys

import datetime as _datetime
import decimal as _decimal
import fractions as _fractions
import math as _math
import numbers as _numbers
import tkinter as _tkinter
import warnings as _warnings

from . import _abroad as _ab_mod
from . import _constants as _lc
from . import _version
from .. import constants as _constants
from .. import types as __

__name__ = "aveytense"
# between @since and @author there is unnecessarily long line spacing
# hence this warning is being thrown; it is being disabled.
_warnings.filterwarnings("ignore", category = SyntaxWarning)

# types
_var = __.TypeVar

_T = _var("_T")
_T_fi = _var("_T_fi", int, float) # Bound to float/int
_T1 = _var("_T1")
_T2 = _var("_T2")
_T3 = _var("_T3")

_Ellipsis = __.EllipsisType
RAM = int
_RAM = __.AVT_MutableSequence[RAM]
_MODE_AND = _constants.MODE_AND
_MODE_OR = _constants.MODE_OR
_Mode = __.Union[_lc.ModeSelection, __.Literal["and", "or"]]
_ReckonTypePre = _ab_mod.ReckonType[_T]
_ReckonNGTPre = _ab_mod.ReckonNGT
_AbroadValue1Pre = _ab_mod.AbroadValue1[_T]
_AbroadValue2Pre = _ab_mod.AbroadValue2[_T]
_AbroadModifierPre = _ab_mod.AbroadModifier[_T]
_FloatOrInteger = __.FloatOrInteger
_OptionalFloatOrInteger = __.Union[_FloatOrInteger, _Ellipsis]
_OptionalInteger = __.Union[int, _Ellipsis]
_TenseVersionType = __.TenseVersionType[int]


def _domain_checker(x: _FloatOrInteger, f: __.Literal["asin", "acos", "asec", "acosec"] = "asin"): # 0.3.38
    
    if f in ("asin", "acos") and (x < -1 or x > 1):
        
        error = ValueError("bad math domain, expected value in range [-1; 1]")
        raise error
    
    elif f in ("asec", "acosec") and abs(x) < 1:
        
        error = ValueError("bad math domain, expected value not in range (-1; 1)")
        raise error
    
    return True

@__.overload
def aveytenseVersion(asString: __.Literal[True] = True) -> _version.VERSION_TYPE: ...

@__.overload
def aveytenseVersion(asString: __.Literal[False]) -> _version._VERSION_INFO: ...

def aveytenseVersion(asString = True):
    """
    @lifetime >= 0.3.25
    ```
    # since 0.3.47
    def aveytenseVersion(asString: bool = True): ...
    # for 0.3.24 - 0.3.46
    def tenseVersion(asTuple: bool = False): ...
    # before 0.3.24
    def tenseVersion(): ...
    ```
    Returns AveyTense version installed. Ensure you have version up-to-date to make everything actually working. If optional parameter \\
    is set to `True`, returned is tuple with 3 items, which together compose version of AveyTense. This argument is also responsible for \\
    deletion of global function `tenseVersionAsTuple()` on 0.3.24. Before 0.3.47 it was called `tenseVersion()`
    """
    
    from .._ᴧv_collection import _version
    
    if asString:
        return _version.VERSION_INFO
    else:
        return _version.VERSION


# declarations

def _reckon_prepend_init(*countables: _ReckonTypePre[_T]):
    
    i = 0
    for e in countables:
        
        if isinstance(e, __.IO):
            
            try:
                for _ in e.read():
                    i += 1
            except:
                pass
            
        # elif isinstance(e, _tkinter.StringVar): # < 0.3.39
        #    i += len(e.get())
            
        elif isinstance(e, __.Iterable):
            
            for _ in e:
                i += 1
                
        elif isinstance(e, __.Sizeable):
            i += len(e)
            
        elif isinstance(e, __.ReckonOperable):
            i += e.__reckon__()
            
        else:
            error = TypeError("expected sizeable or iterable object, or object of class extending '{}' base class".format(__.ReckonOperable.__name__))
            raise error
        
    return i

def _reckon_init(*countables: _ReckonTypePre[_T]):
    return _reckon_prepend_init(*countables)


class _AbroadInitializer:
    """
    @lifetime >= 0.3.25 \\
        
    Better identifier for returned sequence from `abroad()` function
    """
    def __new__(cls, seq: __.AVT_Iterable[int], v1: int, v2: int, m: int, /):
        return _ab_mod.AbroadInitializer(seq, v1, v2, m)
    

def _abroad_prepend_init(value1: _AbroadValue1Pre[_T1], /, value2: _AbroadValue2Pre[_T2] = None, modifier: _AbroadModifierPre[_T3] = None):
    
    _pre = (__.IO, __.Iterable, __.ReckonOperable, __.Sizeable)
    
    conv, v1, v2, m = [0], 0, 0, 0
    del conv[0]
    
    # v1 (value1)
    if isinstance(value1, _pre):
        v1 = _reckon_init(value1)
        
    elif isinstance(value1, int):
        v1 = value1
        
    elif isinstance(value1, float):
        
        if value2 in (_math.inf, _math.nan):
            error = __.IncorrectValueError("'inf' or 'nan' as value for 'value1' (1st parameter) is not allowed.")
            raise error
        
        else:
            v1 = _math.trunc(value1)
            
    elif isinstance(value1, complex):
        v1 = _math.trunc(value1.real)
        
    else:
        error = TypeError("Missing value or invalid type of 'value1' (1st parameter). Used type '{}' does not match any of types, which are allowed in this parameter.".format(type(value1).__name__))
        raise error
    
    # v2 (value2)
    if isinstance(value2, _pre):
        v2 = _reckon_init(value2)
        
    elif isinstance(value2, (bool, _Ellipsis)) or value2 is None:
        
        if isinstance(value1, complex):
            v2 = _math.trunc(value1.imag)
            
        else:
            v2 = v1
            
    elif isinstance(value2, int):
        v2 = value2
        
    elif isinstance(value2, float):
        
        if value2 in (_math.inf, _math.nan):
            error = __.IncorrectValueError("'inf' or 'nan' as value for 'value2' (2nd parameter) is not allowed.")
            raise error
        
        else:
            v2 = _math.trunc(value2)
    else:
        error = TypeError("Invalid type of 'value2' (2nd parameter). Used type '{}' does not match any of types, which are allowed in this parameter.".format(type(value2).__name__))
        raise error
    
    # m (modifier)
    if isinstance(modifier, _pre):
        
        m = _reckon_init(modifier)
        
        if m == 0:
            m = 1
            
    elif isinstance(modifier, int):
        
        if modifier == 0:
            m = 1
            
        else:
            m = abs(modifier)
            
        if m == 0:
            m = 1
            
    elif isinstance(modifier, float):
        
        if modifier == _math.inf:
            error = __.IncorrectValueError("'inf' as value for 'modifier' (3rd parameter) is not allowed")
            raise error
        
        elif modifier == _math.nan:
            m = 1
            
        else:
            m = abs(_math.trunc(modifier))
            if m == 0: m = 1
            
    elif isinstance(modifier, complex):
        
        m = _math.trunc(modifier.real) + _math.trunc(modifier.imag)
        
        if m < 0:
            m = abs(m)
            
        elif m == 0:
            m = 1
            
    elif isinstance(modifier, _Ellipsis) or modifier is None:
        m = 1
        
    else:
        error = TypeError("Invalid type of 'modifier' (3rd parameter). Used type '{}' does not match any of types, which are allowed in this parameter.".format(type(modifier).__name__))
        raise error
    
    # iteration begins
    if (v1 == v2 or isinstance(value1, complex)) and (isinstance(value2, bool) or value2 is None):
        
        if isinstance(value1, complex):
            
            v1 = _math.trunc(value1.real)
            v2 = _math.trunc(value1.imag)
            
            if v1 < v2:
                
                i = v1
                
                while i < v2:
                    
                    if value2 is False:
                        conv.append(-i - 1)
                        
                    else:
                        conv.append(i)
                        
                    i += m
            else:
                
                i = v1
                
                while i > v2:
                    
                    if value2 is False:
                        conv.append(-i - 1)
                        
                    else:
                        conv.append(i)
                        
                    i -= m
                    
            if value2 is False:
                conv.reverse()
                
        else:
            
            if v1 > 0:
                
                i = 0
                
                while i < v1:
                    
                    if value2 is False:
                        conv.append(-i - 1)
                        
                    else:
                        conv.append(i)
                        
                    i += m
            else:
                
                i = v1
                
                while i < 0:
                    
                    if value2 is False:
                        conv.append(-i - 1)
                        
                    else:
                        conv.append(i)
                        
                    i += m
                    
            if value2 is False:
                conv.reverse()
                
        # earlier: return conv (< 0.3.28)
        return _AbroadInitializer(
            conv,
            0 if v1 == v2 else v1,
            v1 if v1 == v2 else v2,
            m
        )
        
    if isinstance(value2, float):
        
        if v2 >= 0 or (v1 < 0 and v2 < 0):
            v2 += 1
            
        else:
            v2 -= 1
            
    if v1 < v2:
        
        i = v1
        
        while i < v2:
            conv.append(i)
            i += m
    else:
        
        i = v1
        
        while i > v2:
            conv.append(i)
            i -= m
            
    # earlier: return conv (< 0.3.28)
    return _AbroadInitializer(conv, v1, v2, m)

def _abroad_init(value1: _AbroadValue1Pre[_T1], /, value2: _AbroadValue2Pre[_T2] = None, modifier: _AbroadModifierPre[_T3] = None):
    return _abroad_prepend_init(value1, value2, modifier)

class Time:
    """
    @lifetime >= 0.3.25 (4th July 2024)
    
    Access to time. Non-standard and may be removed or remade in the future
    """
    
    __forced_unix_year_range = False
    @classmethod
    def forceUnixYearRange(self, option = False, /):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Forces year range to 1st Jan 1970 - 19th Jan 2038. \\
        If set to `False`, it is reset.
        """
        self.__forced_unix_year_range = option
        return self
    
    @classmethod
    def fencordFormat(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returned is present time in `tense.fencord.Fencord` class format.
        Formatted as `%Y-%m-%d %H:%M:%S`. Timezone is user's local timezone. \\
        This format also uses `discord` module.
        """
        return _datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def isLeapYear(self, year: int):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returned is `True` only when:
        - year is an integer and is positive (above 0)
        - year is divisible by 4 and not divisible by 100 or year is divisible by 400
        - if Unix year range is enforced, only years in range 1970 - 2038

        If none of these requirements are granted, returned is `False`.
        """
        b = ((isinstance(year, int) and year >= 1) and (year % 4 == 0 and year % 100 != 0) or year % 400 == 0)
        if self.__forced_unix_year_range: b = b and (year >= 1970 and year <= 2038)
        return b
    
    @classmethod
    def verifyDate(self, year: int, month: int, day: int):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returned is `True` only when every parameter is an integer and year is from 1 up, \\
        month is from 1 up and day is from 1 up, and one of these statements are granted:
        - day has value 31 for months: 1, 3, 5, 7, 8, 10, 12
        - day has value 30 for every month in range 1-12 excluding 2
        - day has value 29 for every month in range 1-12, for 2 only if year is leap
        - day is in range 1-28 for every month in range 1-12
        - additionally, if Unix year range is enforced, year is in range 1970-2038

        If none of these requirements are granted, returned is `False`.
        """
        return (
                isinstance(year, int) and isinstance(month, int) and isinstance(day, int)) and (year >= 1 and month >= 1 and day >= 1) and (
                (day == 31 and month in (1, 3, 5, 7, 8, 10, 12)) or (day == 30 and month in set(_abroad_init(1, 12.1)).difference({2})) or
                (day == 29 and month in _abroad_init(1, 12.1) and self.isLeapYear(year)) or (day < 29 and month in _abroad_init(1, 12.1))
            )
                
    @classmethod
    def getMillennium(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returns current millennium. Expected would be only `return 3`, \\
        but code itself in reality verifies current date and what not.
        """
        return _math.trunc(int(_datetime.datetime.now().strftime("%Y")) / 1000) + 1
    
    @classmethod
    def getCentury(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returns current century. Expected would be only `return 21`, \\
        but code itself in reality verifies current date and what not.
        """
        return _math.trunc(int(_datetime.datetime.now().strftime("%Y")) / 100) + 1
    
    @classmethod
    def getDecade(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returns current decade. Warning: it does not return something like \\
        3rd decade of 21st century, but decade in overall, which have elapsed \\
        since Anno Domini time period. So what that means: for 2024 (4th July \\
        2024, when created this method) returned is 203.

        It does not match 0-to-9 decades, but 1-to-0, so 203 will be returned \\
        by years in range 2021-2030 (not in 2020-2029), including both points.
        """
        return _math.trunc(int(_datetime.datetime.now().strftime("%Y")) / 10) + 1
    
    @classmethod
    def getYear(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returns current year
        """
        return int(_datetime.datetime.now().strftime("%Y"))
    
    @classmethod
    def getMonth(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returns current month
        """
        return int(_datetime.datetime.now().strftime("%m"))
    
    @classmethod
    def getDay(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returns current day. Basing on local timezone.
        Warning: This doesn't return day of the year \\
        or day of the week, but only day of the month
        """
        return int(_datetime.datetime.now().strftime("%d"))
    
    @classmethod
    def getHour(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returns current hour. Basing on local timezone.
        """
        return int(_datetime.datetime.now().strftime("%H"))
    
    @classmethod
    def getMinute(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returns current minute. Basing on local timezone.
        """
        return int(_datetime.datetime.now().strftime("%M"))
    
    @classmethod
    def getSecond(self):
        """
        @lifetime >= 0.3.25 (4th July 2024)
        
        Returns current second. Basing on local timezone.
        """
        return int(_datetime.datetime.now().strftime("%S"))
    
    __all__ = [n for n in locals() if n[:1] != "_"]
    "@lifetime >= 0.3.25"
    
class Math:
    """
    @lifetime >= 0.3.25 (4th July 2024) \\
    https://aveyzan.xyz/aveytense#aveytense.Math
    
    Math methods and constants
    """
    
    #################################### Constants extracted from aveytense.constants ####################################

    NAN = float("nan") # >= 0.3.25 (05.07.2024)
    INF = float("inf") # >= 0.3.25 (05.07.2024)
    E = 2.718281828459045235360287471352 # >= 0.3.25 (04.07.2024)
    PI = 3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461 # >= 0.3.25 (04.07.2024)
    TAU = 6.283185307179586476925287 # >= 0.3.25 (05.07.2024)
    SQRT2 = 1.4142135623730950488016887242097 # >= 0.3.25 (05.07.2024)
    THOUSAND           = 10 ** 3   # >= 0.3.47 (07.06.2025)
    MILLION            = 10 ** 6   # >= 0.3.47 (07.06.2025)
    BILLION            = 10 ** 9   # >= 0.3.47 (07.06.2025)
    TRILLION           = 10 ** 12  # >= 0.3.47 (07.06.2025)
    QUADRILLION        = 10 ** 15  # >= 0.3.47 (07.06.2025)
    QUINTILLION        = 10 ** 18  # >= 0.3.47 (07.06.2025)
    SEXTILLION         = 10 ** 21  # >= 0.3.47 (07.06.2025)
    SEPTILLION         = 10 ** 24  # >= 0.3.47 (07.06.2025)
    OCTILLION          = 10 ** 27  # >= 0.3.47 (07.06.2025)
    NONILLION          = 10 ** 30  # >= 0.3.47 (07.06.2025)
    DECILLION          = 10 ** 33  # >= 0.3.47 (07.06.2025)
    UNDECILLION        = 10 ** 36  # >= 0.3.47 (07.06.2025)
    DUODECILLION       = 10 ** 39  # >= 0.3.47 (07.06.2025)
    TREDECILLION       = 10 ** 42  # >= 0.3.47 (07.06.2025)
    QUATTUOR_DECILLION = 10 ** 45  # >= 0.3.47 (07.06.2025)
    QUINDECILLION      = 10 ** 48  # >= 0.3.47 (07.06.2025)
    SEXDECILLION       = 10 ** 51  # >= 0.3.47 (07.06.2025)
    SEPTEN_DECILLION   = 10 ** 54  # >= 0.3.47 (07.06.2025)
    OCTODECILLION      = 10 ** 57  # >= 0.3.47 (07.06.2025)
    NOVEMDECILLION     = 10 ** 60  # >= 0.3.47 (07.06.2025)
    VIGINTILLION       = 10 ** 63  # >= 0.3.47 (07.06.2025)
    GOOGOL             = 10 ** 100 # >= 0.3.47 (07.06.2025)
    CENTILLION         = 10 ** 303 # >= 0.3.25 (19.07.2024)
    
    # >= 0.3.53 (aveytense.constants >= 0.3.26b3; < 0.3.53)
    JS_MIN_SAFE_INTEGER = -(2**53 - 1)
    """Returns the smallest safe integer in JavaScript"""
    # >= 0.3.53 (aveytense.constants >= 0.3.26b3; < 0.3.53)
    JS_MAX_SAFE_INTEGER = -JS_MIN_SAFE_INTEGER
    """Returns the biggest safe integer in JavaScript"""
    # >= 0.3.53 (aveytense.constants >= 0.3.26b3; < 0.3.53) ## this value is exact
    JS_MIN_VALUE = 4.940656458412465441765687928682213723650598026143247644255856825006755072702087518652998363616359923797965646954457177309266567103559397963987747960107818781263007131903114045278458171678489821036887186360569987307230500063874091535649843873124733972731696151400317153853980741262385655911710266585566867681870395603106249319452715914924553293054565444011274801297099995419319894090804165633245247571478690147267801593552386115501348035264934720193790268107107491703332226844753335720832431936092382893458368060106011506169809753078342277318329247904982524730776375927247874656084778203734469699533647017972677717585125660551199131504891101451037862738167250955837389733598993664809941164205702637090279242767544565229087538682506419718265533447265625e-324
    """Returns the smallest possible number in JavaScript"""
    # >= 0.3.53 (aveytense.constants >= 0.3.26b3; < 0.3.53) ## this value is exact
    JS_MAX_VALUE = 17976931348623139118889956560692130772452639421037405052830403761197852555077671941151929042600095771540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368
    """Returns the biggest possible number in JavaScript"""
    
    @classmethod
    def isNegative(self, x: __.Union[_FloatOrInteger, __.AVT_Sequence[_FloatOrInteger]], /):
        """
        @lifetime >= 0.3.31 \\
        (no doc yet)
        
        Check whether a number is negative. If provided is a sequence, \\
        each number in it must satisfy this condition.
        """
        
        if not isinstance(x, (int, float, __.Sequence)):
            error = TypeError("expected a number (integer or float) or sequence of numbers")
            raise error
        
        elif isinstance(x, (int, float)):
            return x < 0
        
        else:
            
            for e in x:
                
                if not isinstance(e, (int, float)):
                    error = TypeError("expected a number (integer or float) or sequence of numbers")
                    raise error
            
            _r = [e for e in x if e < 0]
            return _reckon_init(_r) == _reckon_init(x)
                
    
    @classmethod
    def isPositive(self, x: __.Union[_FloatOrInteger, __.AVT_Sequence[_FloatOrInteger]], /):
        """
        @lifetime >= 0.3.31 \\
        (no doc yet)
        
        Check whether a number is positive. If provided is a sequence, \\
        each number in it must satisfy this condition.
        """
        
        if not isinstance(x, (int, float, __.Sequence)):
            error = TypeError("expected a number (integer or float) or sequence of numbers")
            raise error
        
        elif isinstance(x, (int, float)):
            return x > 0
        
        else:
            
            for e in x:
                
                if not isinstance(e, (int, float)):
                    error = TypeError("expected a number (integer or float) or sequence of numbers")
                    raise error
            
            _r = [e for e in x if e > 0]
            return _reckon_init(_r) == _reckon_init(x)
    
    @classmethod
    def isPrime(self, x: int, /):
        """
        @lifetime >= 0.3.31 \\
        (no doc yet)
        
        Check whether an integer is prime
        """
        if not isinstance(x, int) or (isinstance(x, int) and self.isNegative(x)):
            error = TypeError("expected a positive integer")
            raise error
        
        if x in (0, 1):
            return False
        
        for i in _abroad_init(2, x):
            
            if x % i == 0:
                return False
            
        return True
    
    @classmethod
    def isComposite(self, x: int, /):
        """
        @lifetime >= 0.3.31 \\
        (no doc yet)
        
        Check whether an integer is composite
        """
        if not isinstance(x, int) or (isinstance(x, int) and self.isNegative(x)):
            error = TypeError("expected a positive integer")
            raise error
        
        if x in (0, 1):
            return False
        
        return not self.isPrime(x)
    
    @classmethod
    def isInRange(self, x: __.Union[_FloatOrInteger, __.AVT_Sequence[_FloatOrInteger]], a: _FloatOrInteger, b: _FloatOrInteger, /, mode = "c"):
        """
        @lifetime >= 0.3.36 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.isInRange
        
        Returns `True`, if number(s) are in specific range [a; b]. \\
        For empty sequences returned is `False`.
        
        On 0.3.39 added optional parameter `mode` to modify intervals:
        - `"c"` (default value) / `"cc"` = `<a; b>` = `a <= x <= b`
        - `"co"` = `<a; b)` = `a <= x < b`
        - `"o"` / `"oo"` = `(a; b)` = `a < x < b`
        - `"oc"` = `(a; b>` = `a < x <= b`
        """
        
        # 0.3.41: Excluding inf and nan
        if all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in [a, b]]):
            
            _mode = mode.lower()
            
            # 0.3.41: Brackets
            if _mode not in ("c", "cc", "oc", "co", "o", "oo"):
                error = TypeError("expected an approriate string value in parameter 'mode' from following: 'c', 'cc', 'oc', 'co', 'o', 'oo' (case insensitive), '[]', '[)', '(]', '()'")
                raise error
        
            _range = [a, b]
            
            if a > b:
                _range.reverse()
            
            if isinstance(x, (int, float)):
                
                if _mode in ("c", "cc"):
                    return x >= _range[0] and x <= _range[1]
                
                elif _mode in ("co",):
                    return x >= _range[0] and x < _range[1]
                
                elif _mode in ("oc",):
                    return x > _range[0] and x <= _range[1]
                
                else:
                    return x > _range[0] and x < _range[1]
            
            elif isinstance(x, __.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
                
                if _reckon_init(x) == 0:
                    return False
                
                _placeholder = True
                
                for e in x:
                    
                    if _mode in ("c", "cc",):
                        _placeholder = _placeholder and (e >= _range[0] and e <= _range[1])
                        
                    elif _mode in ("co",):
                        _placeholder = _placeholder and (e >= _range[0] and e < _range[1])
                        
                    elif _mode in ("oc",):
                        _placeholder = _placeholder and (e > _range[0] and e <= _range[1])
                        
                    else:
                        _placeholder = _placeholder and (e > _range[0] and e < _range[1])
                    
                return _placeholder
        
        error = TypeError("expected 'x' as integer/float or sequence of integers and floats, 'a' and 'b' as integers or floats, all excluding infinity and NaN")
        raise error
                
    
    @classmethod
    def isIncreasing(self, x: __.AVT_Sequence[_FloatOrInteger], /):
        """
        @lifetime >= 0.3.38 \\
        (no doc yet)
        
        Returns `True` if sequence has positive difference for consecutive members, \\
        and has at least 3 integer items.
        """
        
        if isinstance(x, __.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] > 0
                
            return _placeholder
            
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isDecreasing(self, x: __.AVT_Sequence[_FloatOrInteger], /):
        """
        @lifetime >= 0.3.38 \\
        (no doc yet)
        
        Returns `True` if sequence has negative difference for consecutive members, \\
        and has at least 3 number items.
        """
        
        if isinstance(x, __.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] < 0
                
            return _placeholder
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isConstant(self, x: __.AVT_Sequence[_FloatOrInteger], /):
        """
        @lifetime >= 0.3.38 \\
        (no doc yet)
        
        Returns `True` if sequence has difference equal 0 for consecutive members, \\
        and has at least 3 number items.
        """
        
        if isinstance(x, __.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] == 0
                
            return _placeholder
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isNonIncreasing(self, x: __.AVT_Sequence[_FloatOrInteger], /):
        """
        @lifetime >= 0.3.38 \\
        (no doc yet)
        
        Returns `True` if sequence has negative difference or equal 0 for consecutive members, \\
        and has at least 3 number items.
        """
        
        if isinstance(x, __.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] <= 0
                
            return _placeholder
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isNonDecreasing(self, x: __.AVT_Sequence[_FloatOrInteger], /):
        """
        @lifetime >= 0.3.38 \\
        (no doc yet)
        
        Returns `True` if sequence has positive difference or equal 0 for consecutive members, \\
        and has at least 3 number items.
        """
        
        if isinstance(x, __.Sequence) and all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
        
            if _reckon_init(x) < 3:
                return False
            
            _placeholder = True
            
            for i in _abroad_init(_reckon_init(x) - 1):
                
                _placeholder = _placeholder and x[i + 1] - x[i] >= 0
                
            return _placeholder
            
        error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
        raise error
    
    @classmethod
    def isMonotonous(self, x: __.AVT_Sequence[_FloatOrInteger], /):
        """
        @lifetime >= 0.3.38 \\
        (no doc yet)
        
        Returns `True`, if sequence is monotonous (is either increasing, \\
        decreasing, constant, non-decreasing or non-increasing).
        """
        
        if not isinstance(x, __.Sequence) or not all([type(e) in (int, float) and e not in (self.INF, self.NAN) for e in x]):
            error = TypeError("expected a number sequence with at least 3 items, without infinity and NaN")
            raise error
        
        return self.isIncreasing(x) or self.isDecreasing(x) or self.isConstant(x) or self.isNonDecreasing(x) or self.isNonIncreasing(x)
    
    
    @classmethod
    @__.overload
    def isFraction(self, o: __.Any, /) -> __.TypeIs[_fractions.Fraction]: ...
    
    @classmethod
    @__.overload
    def isFraction(self, o: __.Any, /, *_: __.Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isFraction(self, o, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.41 \\
                
        Returns `True`, if value is instance of class `fractions.Fraction`.
        """
        
        if _reckon_init(_) == 0:
            return type(o) is _fractions.Fraction
        
        else:
            _many = (o,) + _
            
            if mode in (_constants.MODE_OR, "or"):
                return any([type(e) is _fractions.Fraction for e in _many])
            
            elif mode in (_constants.MODE_AND, "and"):
                return all([type(e) is _fractions.Fraction for e in _many])
            
            else:
                return False
            
            
    @classmethod
    @__.overload
    def isDecimal(self, o: __.Any, /) -> __.TypeIs[_decimal.Decimal]: ...
    
    @classmethod
    @__.overload
    def isDecimal(self, o: __.Any, /, *_: __.Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isDecimal(self, o, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.38 \\
                
        Returns `True`, if value is decimal string (since 0.3.41 - `~.Tense.isDecimalString()`).
        - since 0.3.41: -  ^  - is instance of class `decimal.Decimal`.
        """
        
        if _reckon_init(_) == 0:
            return type(o) is _decimal.Decimal
        
        else:
            _many = (o,) + _
            
            if mode in (_constants.MODE_OR, "or"):
                return any([type(e) is _decimal.Decimal for e in _many])
            
            elif mode in (_constants.MODE_AND, "and"):
                return all([type(e) is _decimal.Decimal for e in _many])
            
            else:
                return False
            
            
    @classmethod
    @__.overload
    def isNumber(self, o: __.Any, /) -> __.TypeIs[_numbers.Number]: ...
    
    @classmethod
    @__.overload
    def isNumber(self, o: __.Any, /, *_: __.Any, mode: _Mode = _MODE_AND) -> bool: ...
    
    @classmethod
    def isNumber(self, o, /, *_, mode = _MODE_AND):
        """
        @lifetime >= 0.3.41 \\
                
        Returns `True` for any number
        """
        
        # _tuple = (_numbers.Number, _decimal.Decimal, _fractions.Fraction, _tc.Indexable, _tc.IntegerConvertible, _tc.FloatConvertible, _tc.ComplexConvertible, int, float, complex)
        
        if reckon(_) == 0:
            
            return isinstance(o, _numbers.Number)
        
        else:
            
            _many = (o,) + _
            
            if mode in (_constants.MODE_AND, "and"):
                
                return all([isinstance(e, _numbers.Number) for e in _many])
            
            elif mode in (_constants.MODE_OR, "or"):
                
                return any([isinstance(e, _numbers.Number) for e in _many])
            
            else:
                
                return False
    
    
    @classmethod
    def fib(self, n: int, /):
        """
        @lifetime >= 0.3.41 (3rd March 2025) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?miscellaneous_functions
        
        Returns a number from Fibonacci sequence at index `n`.
        
        0.3.51: Allow zero
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected integer value above zero")
            raise error
        
        if n == 0:
            return n
        
        n1, n2, _next, i = 0, 1, 1, 1
        
        while i <= n - 2:
            i += 1
            n1, n2 = n2, _next
            _next = n1 + n2
            
        return _next
        
        
    @classmethod
    def fact(self, n: int, /):
        """
        @lifetime >= 0.3.26rc3 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?miscellaneous_functions
        ```
        # created 20.08.2024
        ```
        Returns factorial of `n` (`n!`)
        """
        
        # CHANGEOVER 0.3.39
        if not isinstance(n, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a non-negative integer")
            raise error
        
        # math.factorial(): since Python 2.6
        if hasattr(_math, "factorial"): 
            return _math.factorial(n)
        
        else:
            
            if n in (0, 1):
                return 1
            
            m, i = 2, 3
            
            # 0.3.41: Do not use 'for' loop in order to bypass limit of 'sys.maxsize'
            while i <= n: 
                m *= i
                i += 1
                
            return m
        
    @classmethod
    def factFalling(self, x: int, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?miscellaneous_functions
        
        Returns falling factorial of `x` at index `n`
        """
        
        if not isinstance(n, int) or not isinstance(x, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a non-negative integer")
            raise error
        
        m, i = x, 1
        
        if n == 0:
            return 1
        
        elif n == 1:
            return x
        
        while i < n:
            m *= (x - i)
            i += 1
        
        return m
        
    @classmethod
    def factRising(self, x: int, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?miscellaneous_functions
        
        Returns rising factorial of `x` at index `n`
        """
        
        if not isinstance(n, int) or not isinstance(x, int) or (isinstance(n, int) and n < 0):
            error = TypeError("expected a non-negative integer")
            raise error
        
        return int(self.pow(-1, n)) * self.factFalling(-x, n)
    
    if False: # < 0.3.49
        @classmethod
        @__.deprecated("deprecated since 0.3.39, will be removed on 0.3.48")
        def outOfRoot(self, number: int, rootScale: int, /):
            """Since 0.3.?"""
            i = number
            while not isinstance(pow(number, 1/rootScale), int): i -= 1
            return [int(pow(i, 1/rootScale)), number - i]
    
    @classmethod
    def asin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns arc sine of `x` 
        """
        _domain_checker(x, "asin")
        
        return _math.asin(_math.radians(x))
    
    @classmethod
    def acos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns arc cosine of `x`
        """
        _domain_checker(x, "acos")
        
        return _math.acos(_math.radians(x))
    
    @classmethod
    def atan(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns arc tangent of `x`. Measured in degrees
        """
        
        return _math.atan(_math.radians(x))
    
    @classmethod
    def acot(self, x: _FloatOrInteger, /):
        """
        @since 0.3.46 (26.05.2025) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns arc cotangent of `x`, Measured in degrees
        """
        
        return self.PI / 2 - _math.atan(_math.radians(x))
    
    @classmethod
    def asinh(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse hyperbolic sine of `x`
        """
        return _math.asinh(_math.radians(x))
    
    @classmethod
    def acosh(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse hyperbolic cosine of `x`
        """
        return _math.acosh(_math.radians(x))
    
    @classmethod
    def atanh(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse hyperbolic tangent of `x`
        """
        return _math.atanh(_math.radians(x))
    
    @classmethod
    def acoth(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse hyperbolic cotangent of `x`
        """
        return 1 / self.atanh(x)
    
    @classmethod
    def acosech(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse hyperbolic cosecant of `x`
        """
        return 1 / self.asinh(x)
    
    @classmethod
    def asech(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse hyperbolic secant of `x`
        """
        return 1 / self.acosh(x)
    
    @classmethod
    def sin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns sine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.sin(_math.radians(x))
    
    @classmethod
    def cos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?trigonometric_functions
        
        Returns cosine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.cos(_math.radians(x))
    
    @classmethod
    def tan(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?trigonometric_functions
        
        Returns tangent of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.tan(_math.radians(x))
    
    @classmethod
    def sinh(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?hyperbolic_functions
        
        Returns hyperbolic sine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.sinh(_math.radians(x))
    
    @classmethod
    def cosh(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?hyperbolic_functions
        
        Returns hyperbolic cosine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.cosh(_math.radians(x))
    
    @classmethod
    def tanh(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?hyperbolic_functions
        
        Returns hyperbolic tangent of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.tanh(_math.radians(x))
    
    @classmethod
    def coth(self, x: _FloatOrInteger, /):
        """
        @since 0.3.46 (22.05.2025) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?hyperbolic_functions
        
        Returns hyperbolic cotangent of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return 1 / self.tanh(x)
    
    @classmethod
    def sech(self, x: _FloatOrInteger, /):
        """
        @since 0.3.46 (22.05.2025) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?hyperbolic_functions
        
        Returns hyperbolic secant of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return 1 / self.cosh(x)
    
    @classmethod
    def cosech(self, x: _FloatOrInteger, /):
        """
        @since 0.3.46 (22.05.2025) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?hyperbolic_functions
        
        Returns hyperbolic cosecant of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return 1 / self.sinh(x)
    
    @classmethod
    def cosec(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?trigonometric_functions
        
        Returns cosecant of `x`. `x` *cannot* be divisible by 90.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.sin(x) == 0:
            error = TypeError("expected a number whose sine isn't equal 0")
            raise error
        
        return 1 / self.sin(x)
    
    @classmethod
    def sec(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?trigonometric_functions
        
        Returns secant of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.cos(x) == 0:
            error = TypeError("expected a number whose cosine isn't equal 0")
            raise error
        
        return 1 / self.cos(x)
    
    @classmethod
    def acosec(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse cosecant of `x`. Equals `asin(1 / x)`.
        """
        _domain_checker(x, "acosec")
        
        return self.asin(1 / x)
    
    @classmethod
    def asec(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse secant of `x`. Equals `acos(1 / x)`
        """
        _domain_checker(x, "asec")
        
        return self.acos(1 / x)
    
    @classmethod
    def cot(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?trigonometric_functions
        
        Returns cotangent of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.tan(x) == 0:
            error = TypeError("expected a number whose tangent isn't equal 0")
            raise error
        
        return 1 / self.tan(x)
    
    @classmethod
    def versin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns versed sine of `x`
        """
        return 1 - self.cos(x)
    
    @classmethod
    def coversin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns coversed sine of `x`
        """
        return 1 - self.sin(x)
    
    @classmethod
    def vercos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        @modified 0.3.39 (renamed from `vercosin`) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns versed cosine of `x`
        """
        return 1 + self.cos(x)
    
    @classmethod
    def covercos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        @modified 0.3.39 (renamed from `covercosin`) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns coversed cosine of `x`
        """
        return 1 + self.sin(x)
    
    @classmethod
    def haversin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns haversed sine of `x`
        """
        return self.versin(x) / 2
    
    @classmethod
    def havercos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        @modified 0.3.39 (renamed from `havercosin`) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns haversed cosine of `x`
        """
        return self.coversin(x) / 2
    
    @classmethod
    def hacoversin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns hacoversed sine of `x`
        """
        return self.vercos(x) / 2
    
    @classmethod
    def hacovercos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        @modified 0.3.39 (renamed from `hacovercos`) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns hacoversed cosine of `x`
        """
        return self.covercos(x) / 2
    
    @classmethod
    def aversin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse versed sine of `x`
        """
        _domain_checker(1 - x, "acos")
        
        return self.acos(1 - x)
    
    @classmethod
    def acoversin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse coversed sine of `x`
        """
        _domain_checker(x - 1, "acos")
        
        return self.acos(x - 1)
    
    @classmethod
    def avercos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse versed cosine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) and not self.isInRange(x, 0, 2):
            error = TypeError("expected a number in range [0; 2]")
            raise error
        
        return self.asin(1 - x)
    
    @classmethod
    def acovercos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (04.07.2025) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse coversed cosine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 2):
            error = TypeError("expected a number in range [0; 2]")
            raise error
        
        return self.asin(x - 1)
    
    @classmethod
    def ahaversin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse haversed sine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 1):
            error = TypeError("expected a number in range [0; 1]")
            raise error
        
        return self.acos(1 - (2 * x))
    
    @classmethod
    def ahavercos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse haversed cosine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 1):
            error = TypeError("expected a number in range [0; 1]")
            raise error
        
        return self.acos(2 * x - 1)
    
    @classmethod
    def ahacoversin(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse hacoversed sine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 1):
            error = TypeError("expected a number in range [0; 1]")
            raise error
        
        return self.asin(1 - (2 * x))
    
    @classmethod
    def ahacovercos(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse hacoversed cosine of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or not self.isInRange(x, 0, 1):
            error = TypeError("expected a number in range [0; 1]")
            raise error
        
        return self.asin(2 * x - 1)
    
    @classmethod
    def exsec(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns exsecant (external secant) of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.cos(x) == 0:
            error = TypeError("expected a number whose cosine isn't equal 0")
            raise error
        
        return self.sec(x) - 1
    
    @classmethod
    def excosec(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?extended_trigonometric_functions
        
        Returns excosecant/coexsecant (external cosecant) of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.sin(x) == 0:
            error = TypeError("expected a number whose sine isn't equal 0")
            raise error
        
        return self.cosec(x) - 1
    
    @classmethod
    def aexsec(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse exsecant of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.isInRange(x, -2, 0, "o"):
            error = TypeError("expected a number not in range (-2; 0); values -2 and 0 are allowed")
            raise error
        
        return self.asec(x + 1)
    
    @classmethod
    def aexcosec(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 (05.07.2024) \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?inverse_trigonometric_functions
        
        Returns inverse excosecant of `x`
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN) or self.isInRange(x, -2, 0, "o"):
            error = TypeError("expected a number not in range (-2; 0); values -2 and 0 are allowed")
            raise error
        
        return self.acosec(x + 1)
    
    @classmethod
    def fma(x: _FloatOrInteger, y: _FloatOrInteger, z: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.46
        
        Fused multiply-add operation (support before Py3.13)
        """
        
        if _sys.version_info >= (3, 13):
            return _math.fma(x, y, z)
        
        else:
            return (x * y) + z
    
    @classmethod
    def log(self, x: _FloatOrInteger, /, base: _OptionalFloatOrInteger = ...): # slash since 0.3.39
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.log
        ```
        # created 05.07.2024
        ```
        Logarithm of `x` with specified base. If `base` is omitted, \\
        returned is logarithm of base e.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number in parameter 'x'")
            raise error
        
        if not isinstance(base, (int, float, __.EllipsisType)):
            error = TypeError("expected a number, 'None' or ellipsis in parameter 'base'")
            raise error
        
        _base = self.E if isinstance(base, __.EllipsisType) else base
        return _math.log(x, _base)
        
    @classmethod
    def log2(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Logarithm of `x` with base 2.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.log2(x)
    
    @classmethod
    def log3(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Logarithm of `x` with base 3.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return self.log(x, 3)
    
    @classmethod
    def log5(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Logarithm of `x` with base 5.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return self.log(x, 5)
    
    @classmethod
    def log7(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Logarithm of `x` with base 7.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return self.log(x, 7)
    
    @classmethod
    def ln(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.log
        ```
        # created 05.07.2024
        "class method" in class Math
        ```
        Natural logarithm of `x`. That is logarithm with base `e`.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return self.log(x)
    
    @classmethod
    def log10(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.log
        ```
        # created 05.07.2024
        ```
        Logarithm of `x` with base 10.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number")
            raise error
        
        return _math.log10(x)
    
    @classmethod
    def sqrt(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.sqrt
        ```
        # created 05.07.2024
        ```
        Square root of `x`.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        return _math.sqrt(x)
    
    @classmethod
    def cbrt(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.cbrt
        ```
        # created 05.07.2024
        ```
        Cube root of `x`. To 0.3.26rc2 this method \\
        wouldn't throw an error if used is Python 3.11 \\
        or greater.
        """
        if not isinstance(x, (int, float)) or x in (self.INF, self.NAN):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        if _sys.version_info >= (3, 11):
            return _math.cbrt(x)
        
        else:
            return _math.pow(x, (1/3))
        
    @classmethod
    def pow(self, x: _FloatOrInteger, y: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.25 \\
        (no doc yet)
        ```
        # created 05.07.2024
        ```
        Equals `x**y`(`x` to the power of `y`).
        """
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)) or any([e in (_math.inf, _math.nan) for e in [x, y]]):
            error = TypeError("both parameters 'x' and 'y' must be numbers not being infinity nor NaN")
            raise error
        
        return _math.pow(x, y)
    
    @classmethod
    def abs(self, x: __.Absolute[_T_fi], /) -> _T_fi:
        """
        https://aveyzan.xyz/aveytense#aveytense.Math.abs
        
        Returns absolute value of a number. \\
        This method is stricter version of `abs()` inbuilt function.
        """
        if not isinstance(x, __.Absolute) or (isinstance(x, __.Absolute) and type(abs(x)) not in (int, float)):
            error = TypeError("expected a number or object of class implementing __abs__ returning either integer or floating-point number")
            raise error
        
        # safety checking, not all __abs__() method implementations return absolute value of a number
        # but it is just in case! abs() function can be manipulated easily with method __abs__()
        return abs(abs(x))

    @classmethod
    def trunc(self, x: __.Truncable[int], /):
        """
        @lifetime >= 0.3.25 \\
        (4th March 2025; no doc yet)
        
        Returns an integer from a floating-point number, wiping out the fraction. \\
        This method is stricter version of `math.trunc()` inbuilt function.
        """
        
        if not isinstance(x, __.Truncable) or (isinstance(x, __.Truncable) and type(_math.trunc(x)) is not int):
            error = TypeError("expected a number or object of class implementing __trunc__ returning an integer")
            raise error
        
        # again, safety checking there
        return _math.trunc(_math.trunc(x))
    
    @classmethod
    def triangular(self, n: int, /):
        """
        @lifetime >= 0.3.27a4 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns triangular number at index `n`
        """
        
        return self.polygonal(n, 3)
    
    @classmethod
    def triangularCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered triangular number at index `n`
        """
        
        return self.polygonalCentered(n, 3)
    
    @classmethod
    def square(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns square number at index `n`
        """
        
        return self.polygonal(n, 4)
    
    @classmethod
    def squareCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered square number at index `n`
        """
        
        return self.polygonalCentered(n, 4)
    
    @classmethod
    def pentagonal(self, n: int, /):
        """
        @lifetime >= 0.3.27a4 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns pentagonal number at index `n`
        """
        
        return self.polygonal(n, 5)
    
    @classmethod
    def pentagonalCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered pentagonal number at index `n`
        """
        
        return self.polygonalCentered(n, 5)
    
    @classmethod
    def hexagonal(self, n: int, /):
        """
        @lifetime >= 0.3.27a4 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns hexagonal number at index `n`
        """
        
        return self.polygonal(n, 6)
    
    @classmethod
    def hexagonalCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered hexagonal number at index `n`
        """
        
        return self.polygonalCentered(n, 6)
    
    @classmethod
    def heptagonal(self, n: int, /):
        """
        @lifetime >= 0.3.27a4 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns heptagonal number at index `n`
        """
        
        return self.polygonal(n, 7)
    
    @classmethod
    def heptagonalCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered heptagonal number at index `n`
        """
        
        return self.polygonalCentered(n, 7)
    
    @classmethod
    def octagonal(self, n: int, /):
        """
        @lifetime >= 0.3.27a4 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns octagonal number at index `n`
        """
        
        return self.polygonal(n, 8)
    
    @classmethod
    def octagonalCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered octagonal number at index `n`
        """
        
        return self.polygonalCentered(n, 8)
    
    @classmethod
    def nonagonal(self, n: int, /):
        """
        @lifetime >= 0.3.27a4 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns nonagonal number at index `n`
        """
        
        return self.polygonal(n, 9)
    
    @classmethod
    def nonagonalCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered nonagonal number at index `n`
        """
        
        return self.polygonalCentered(n, 9)
    
    @classmethod
    def decagonal(self, n: int, /):
        """
        @lifetime >= 0.3.27a4 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns decagonal number at index `n`
        """
        
        return self.polygonal(n, 10)
    
    @classmethod
    def decagonalCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered decagonal number at index `n`
        """
        
        return self.polygonalCentered(n, 10)
    
    @classmethod
    def hendecagonal(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns hendecagonal number at index `n`
        """
        
        return self.polygonal(n, 11)
    
    @classmethod
    def hendecagonalCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered hendecagonal number at index `n`
        """
        
        return self.polygonalCentered(n, 11)
    
    @classmethod
    def dodecagonal(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns dodecagonal number at index `n`
        """
        
        return self.polygonal(n, 12)
    
    @classmethod
    def dodecagonalCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered dodecagonal number at index `n`
        """
        
        return self.polygonalCentered(n, 12)
    
    @classmethod
    def tridecagonal(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns tridecagonal number at index `n`
        """
        
        return self.polygonal(n, 13)
    
    @classmethod
    def tridecagonalCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered tridecagonal number at index `n`
        """
        
        return self.polygonalCentered(n, 13)
    
    @classmethod
    def star(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns star number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return 6 * n * (n - 1) + 1
    
    @classmethod
    def pyramidal(self, n: int, s: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Return pyramidal number at index `n` of a polygon with `s` sides
        """
        if (not isinstance(n, int) or n < 0) or (not isinstance(s, int) or s < 3):
            error = TypeError("expected a positive integer as first parameter and second parameter equal or greater than 3")
            raise error
        
        return self.triangular(n) * (n * (s - 2) - (s - 5)) // 3
    
    @classmethod
    def polygonal(self, n: int, s: int, /):
        """
        @lifetime >= 0.3.27a4 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns polygonal number at index `n` with `s` sides
        """
        if (not isinstance(n, int) or n < 0) or (not isinstance(s, int) or s < 3):
            error = TypeError("expected a positive integer as first parameter and second parameter equal or greater than 3")
            raise error
        
        return ((s - 2) * (n ** 2) - (s - 4) * n) // 2
    
    @classmethod
    def polygonalCentered(self, n: int, s: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered polygonal number at index `n` with `s` sides
        """
        
        if (not isinstance(n, int) or n < 0) or (not isinstance(s, int) or s < 3):
            error = TypeError("expected a positive integer as first parameter and second parameter equal or greater than 3")
            raise error
        
        return n if n == 0 else s * n // 2 * (n - 1) + 1
    
    @classmethod
    def tetrahedral(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns tetrahedral number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return self.factRising(n, 3) // self.fact(3)
    
    @classmethod
    def tetrahedralCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered tetrahedral number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n if n == 0 else (2 * n - 1) * ((n - 1) ** 2 + n + 2) // 3
    
    @classmethod
    def cube(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns cube number at index `n` (equivalent to `n ** 3`)
        """
        
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n ** 3
    
    @classmethod
    def cubeCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered cube number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n if n == 0 else (2 * n - 1) * ((n - 1) ** 2 + n)
    
    @classmethod
    def pentatope(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns pentatope number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return self.factRising(n, 4) // self.fact(4)
    
    @classmethod
    def octahedral(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns octahedral number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n if n == 0 else n * (2 * (n ** 2) + 1) // 3
    
    @classmethod
    def octahedralCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered octahedral number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n if n == 0 else (2 * (n - 1) + 1) * (2 * ((n - 1) ** 2) + 2 * (n - 1) + 3) // 3
    
    @classmethod
    def dodecahedral(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered dodecahedral number at index `n`
        """
        
        return n if n == 0 else n * (3 * n - 1) * (3 * n - 2) // 2
    
    @classmethod
    def dodecahedralCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered dodecahedral number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n if n == 0 else (2 * (n - 1) + 1) * (5 * ((n - 1) ** 2) + 5 * (n - 1) + 1)
    
    @classmethod
    def icosahedral(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns icosahedral number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n if n == 0 else n * (5 * (n ** 2) - 5 * n + 2) // 2
    
    @classmethod
    def icosahedralCentered(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns centered icosahedral number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n if n == 0 else (2 * (n - 1) + 1) * (5 * ((n - 1) ** 2) + 5 * (n - 1) + 3) // 3
    
    @classmethod
    def pronic(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns pronic number at index `n`
        """
        
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n * (n + 1)
    
    @classmethod
    def stellaOctangula(self, n: int, /):
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.?figurate_number_functions
        
        Returns stella octangula number at index `n`
        """
        if not isinstance(n, int) or n < 0:
            error = TypeError("expected a positive integer")
            raise error
        
        return n * (2 * (n ** 2) - 1)
    
    @classmethod
    def diagonals(self, s: int, /, distinct = False):
        """
        @lifetime >= 0.3.41 \\
        (6th March 2025; no doc yet)
        
        Return amount of diagonals in an equilateral polygon with defined amount of sides.
        """
        if not isinstance(s, int) or s < 3:
            error = TypeError("expected at least 3 sides")
            raise error
        
        if distinct: # about distinct: https://en.wikipedia.org/wiki/Diagonal
            return (s - 2) // 2
        
        else:
            return (s * (s - 3)) // 2
    
    @classmethod
    def lcm(self, *i: int):
        """
        @lifetime >= 0.3.31 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.lcm
        
        Return least common multiple of provided integers
        """
        
        if _reckon_init(i) < 2 or (_reckon_init(i) >= 2 and not all([type(e) is int and not self.isNegative(e) for e in i])):
            error = ValueError("expected at least 2 non-negative integers")
            raise error
        
        if _sys.version_info >= (3, 9):
            return _math.lcm(*i)
        
        else:
            from functools import reduce # >= 2.6
            
            def _gcd(a: int, b: int):
                
                while b:      
                    a, b = b, a % b
                return a
            
            def _lcm(a: int, b: int):
                return a * b // _gcd(a, b)
            
            return reduce(_lcm, i)
        
    @classmethod
    def gcd(self, *i: int):
        """
        @lifetime >= 0.3.31 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.gcd
        
        Return greatest common divisor of provided integers
        """
        
        if _reckon_init(i) < 2 or (_reckon_init(i) >= 2 and not all([type(e) is int and not self.isNegative(e) for e in i])):
            error = ValueError("expected at least 2 non-negative integers")
            raise error
        
        if _sys.version_info >= (3, 9):
            return _math.gcd(*i)
        
        else:
            from functools import reduce # >= 2.6
            
            def _gcd(a: int, b: int):
                
                while b:
                    a, b = b, a % b
                return a
            
            return reduce(_gcd, i)
        
    @classmethod
    def toDigits(self, n: int, /):
        """
        @lifetime >= 0.3.39 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.toDigits
        
        Splits an integer to a digit list.
        """
        
        if not isinstance(n, int):
            error = TypeError("expected an integer")
            raise error
        
        if self.abs(n) < 10:
            return [self.abs(n)]
        
        return [int(c, base = 10) for c in str(self.abs(n))]
        
    @classmethod
    def minDigit(self, n: int, /):
        """
        @lifetime >= 0.3.39 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.minDigit
        
        Returns minimum digit in a number. Sign isn't counted.
        """
        
        if not isinstance(n, int):
            error = TypeError("expected an integer")
            raise error
        
        if self.abs(n) < 10:
            return self.abs(n)
        
        return min(self.toDigits(n))
    
    
    @classmethod
    def maxDigit(self, n: int, /):
        """
        @lifetime >= 0.3.39 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.maxDigit
        
        Returns maximum digit in a number. Sign isn't counted.
        """
        
        if not isinstance(n, int):
            error = TypeError("expected an integer")
            raise error
        
        if self.abs(n) < 10:
            return self.abs(n)
        
        return max(self.toDigits(n))
            

    @classmethod
    def lwdp(self, n: int, /):
        """
        @lifetime >= 0.3.39 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.lwdp
        
        Return number *least with digit product* of `n`. To be more explanatory, this method returns a number, which \\
        digits create `n` via multiply operation, e.g. for `n` equal 18, method would return 29, because: 2 * 9 = 18.
        
        If this class method cannot find smallest number with digit product of `n`, it will return -1.
        
        """
        if not isinstance(n, int):
            error = TypeError("expected a non-negative integer")
            raise error
        
        r, m, b, i = 0, 1, self.abs(n), 9
        
        while i > 1: # 0.3.41: changed loop
            
            while b % i == 0:
                
                r += m * i
                m *= 10
                b //= i
                
            i -= 1
        
        if m == 10:
            r += 10
            
        return r if b == 1 else -1
    
    @classmethod
    def perm(self, n: int, k: _OptionalInteger = ..., /): # <- slash since 0.3.40
        """
        @lifetime >= 0.3.39 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.perm
        
        Formula `n! / (n - k)!`
        """
        
        if not isinstance(n, int):
            error = TypeError("expected an integer in first parameter")
            raise error
        
        if not isinstance(k, (int, __.EllipsisType)):
            error = TypeError("expected an integer, None or ellipsis in second parameter")
            raise error
        
        if isinstance(k, __.EllipsisType):
            return self.fact(n)
        
        else:
            return int(self.fact(n) / (self.fact(k) * self.fact(n - k)) * self.fact(k))
        
    @classmethod
    def mean(self, *n: _FloatOrInteger, mode = "a"):
        """
        @lifetime >= 0.3.40 \\
        https://aveyzan.xyz/aveytense#aveytense.Math.mean
        
        - 0.3.41: Floating-point numbers are now allowed
        """
        
        if _reckon_init(n) == 0:
            error = TypeError("expected at least one value")
            raise error
        
        if type(mode) is not str:
            error = TypeError("expected a string in parameter 'mode'")
            raise error
        
        _mode = mode.lower()
        
        if _mode not in ("a", "g", "q", "h"):
            error = TypeError("expected a string value in parameter 'mode' from following: 'a', 'g', 'h' and 'q'")
            raise error
        
        for e in n:
            
            if type(e) not in (int, float) or e in (self.INF, self.NAN) or (_mode == "a" and self.isNegative(e)):
                error = TypeError("expected all values as numbers not being infinity nor NaN; for geometric mean - non-negative numbers only")
                raise error
            
        r = 0
        
        import statistics
        
        if _mode == "a":
            
            if hasattr(statistics, "mean"):
                return statistics.mean(n)
            
            for e in n:
                r += e
                
            return r / _reckon_init(n)
        
        elif _mode == "g":
            
            if hasattr(statistics, "geometric_mean"):
                return statistics.geometric_mean(n)
            
            r = 1
            
            for e in n:
                r *= e
                
            return self.pow(r, (1 / _reckon_init(n)))
        
        # 0.3.41
        elif _mode == "h":
            
            if hasattr(statistics, "harmonic_mean"):
                return statistics.harmonic_mean(n)
            
            r = .0
            
            for e in n:
                
                if e == 0:
                    error = ZeroDivisionError("one of numbers equals zero")
                    raise error
                
                r += 1 / e
                
            return _reckon_init(n) / r
            
        
        else: # root mean square (rms)
            
            for e in n:
                r += e ** 2
                
            return self.sqrt(r / _reckon_init(n))
        
        
    @classmethod
    def stdev(self, *i: int):
        """
        @lifetime >= 0.3.41
                
        Returns standard deviation of all given integers.
        """
        
        if _reckon_init(i) == 0:
            error = TypeError("expected at least one value")
            raise error
        
        for e in i:
            
            if type(e) is not int:
                error = TypeError("expected all values as integers")
                raise error
        
        import statistics
        
        if hasattr(statistics, "stdev"):
            return statistics.stdev(i)
        
        _mean = self.mean(*i, mode = "a")
        _res = .0
        
        for e in i:
            _res += (e - _mean) ** 2
            
        return self.sqrt(_res / _reckon_init(i))
    
    
    @classmethod
    def toRadians(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.41
                
        Returns angle in radians notation. Formula: `x*(π/180)`
        """
        
        if type(x) not in (int, float) or x in (self.NAN, self.INF):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        if hasattr(_math, "radians"):
            return _math.radians(x)
        
        return x * (self.PI / 180)
        
        
    @classmethod
    def toDegrees(self, x: _FloatOrInteger, /):
        """
        @lifetime >= 0.3.41
                
        Returns radians to angle notation. Formula: `x*(180/π)`
        """
        
        if type(x) not in (int, float) or x in (self.NAN, self.INF):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        if hasattr(_math, "degrees"):
            return _math.degrees(x)
        
        return x * (180 / self.PI)
    
    
    @classmethod
    def toGradians(self, x: _FloatOrInteger, /, n = "r"):
        """
        @lifetime >= 0.3.41
                
        Returns radians/degrees to gradians notation.
        """
        if type(x) not in (int, float) or x in (self.NAN, self.INF):
            error = TypeError("expected a number not being infinity nor NaN")
            raise error
        
        if n.lower() not in ("r", "d"):
            error = TypeError("expected 'r' or 'd' in parameter 'n'")
            raise error
        
        if n.lower() == "r":
            return x * (self.PI / 200)
        
        else:
            return x * (9 / 10)
        
        
        
    __all__ = sorted([n for n in locals() if n[:1] != "_"]) # 0.3.41: sorted()
    "@lifetime >= 0.3.25"
    __dir__ = lambda self: __all__
    "@lifetime >= 0.3.25"

_ReckonType = _ReckonTypePre[_T]
_AbroadValue1 = _AbroadValue1Pre[_T]
_AbroadValue2 = _AbroadValue2Pre[_T]
_AbroadModifier = _AbroadModifierPre[_T]

def abroad(value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None):
    """
    @lifetime >= 0.3.9 \\
    @standard-lifetime >= 0.3.10  \\
    @modified 0.3.25 (moved slash to between `value1` and `value2`) \\
    https://aveyzan.xyz/aveytense#aveytense.abroad
    
    Same function as `range()`, but more improved. `abroad()` has the following advantages:
    - supports countable objects, without using `len()` function, for all parameters
    - no overloads, only one version of function; that means there are 3 parameters, last 2 are optional
    - returns mutable sequence of integers, while `range()` returns integer-typed immutable sequence
    - `abroad()` is a function to faciliate recognizion; `range` is simultaneously a function and class
    - modifier will be always positive, negative values doesn't matter (!)
    - sequence begins from least of `value1` and `value2`, if `value2` is `bool` or `None`, begins \\
    from 0 to `value1` (or from `value1` to 0, if `value1` is negative)
    - `value2` as floating-point number allows the truncated integer to become endpoint, which will \\
    be included

    If `value2` is set to `None`, it will behave identically as `True` boolean value. It allows the \\
    iteration to go normally. Setting to `False` will flip the order and making all integers negative, \\
    put in ascending order.

    Function supports `range` class itself. \\
    Below `range()` values and `abroad()` function equivalents:
    ```js \\
    range(23) = abroad(23)
    range(2, 23) = abroad(2, 23)
    range(2, 24) = abroad(2, 23.6) // or just abroad(2, 24)
    range(23, 5, -1) = abroad(23, 5) // modifier skipped, default is 1
    range(23, 5, -3) = abroad(23, 5, 3) // there 3 also can be -3
    range(len("Perfect!")) = abroad("Perfect!")
    ``` \n
    By providing `range()` as an argument of this function, it simultaneously allows to alter the \\
    sequence from immutable to mutable. It is actually recommended to keep the same endpoint as \\
    `range` has, otherwise it may bind with returning not these results. Keep on mind this syntax:
    ```py \\
    abroad(range(0, x, m), x, m) # x - endpoint; m (optional) - step/modifier
    ```
    where `x` is stop/endpoint and `m` is step/modifier. That `m` can be omitted. \\
    That number 0 is set specially, because it may lead with returning unexpected \\
    sequence of numbers. But if it is intentional - sure, why not! But from Aveyzan's \\
    perspective it isn't recommended. \\
    For example:
    ```py \\
    abroad(range(0, 13), 13) # empty sequence
    abroad(range(0, 13), 13.24) # 13
    abroad(range(0, 13), 13, 2) # empty sequence
    abroad(range(0, 13, 2), 13, 2) # 7, 9, 11 (13 / 2 (round up) = 7)
    abroad(range(5, 13), 13) # 7, 8, 9, 10, 11, 12 (13 - 5 - 1 = 7)
    ```

    If `range` function is used commonly, with one parameter, syntax will be shortened:
    ```py \\
    abroad(range(x)) # x - endpoint
    ```
    where `x` is stop/endpoint. This is the common way to convert the immutable sequence to mutable.

    Usages:
    ```py \\
    # value1 = integer | Countable
    # value2 = None
    # modifier = 1
    abroad(92) # 0, 1, 2, 3, ..., 90, 91
    abroad(-92) # -92, -91, -90, ..., -2, -1
    abroad(["jump", "on", "the", "roof"]) # 0, 1, 2, 3
    abroad("Hello!") # 0, 1, 2, 3, 4, 5

    # value1 = integer
    # value2 = integer, float
    # modifier = 1
    abroad(92, 3) # 92, 91, 90, ..., 5, 4
    abroad(3, 92) # 3, 4, 5, ..., 90, 91
    abroad(92, 3.05) # 92, 91, 90, ..., 5, 4, 3 (!)
    abroad(3, 92.05) # 3, 4, 5, ..., 90, 91, 92 (!)

    # value1 = integer
    # value2 = bool | None | ... (None and ellipsis equal True)
    # modifier = 1
    abroad(92, True) # 0, 1, 2, 3, ..., 90, 91
    abroad(-92, True) # -92, -91, -90, ..., -2, -1
    abroad(92, False) # -92, -91, -90, ..., -2, -1
    abroad(-92, False) # 0, 1, 2, 3, ..., 90, 91

    # value1 = complex (under experiments)
    # value2 = bool | None | ... (None and ellipsis equal True)
    # modifier = 1
    abroad(3+9j, True) # 3, 4, ..., 7, 8
    abroad(3+9j, False) # -9, -8, ..., -5, -4
    abroad(3-9j, True) # 3, 2, 1, ..., -7, -8
    abroad(3-9j, False) # 7, 6, 5, ..., -3, -4
    abroad(-3+9j, True) # -3, -2, ..., 7, 8
    abroad(-3+9j, False) # -9, -8, ..., 1, 2
    abroad(-3-9j, True) # -3, -4, -5, ..., -7, -8
    abroad(-3-9j, False) # 7, 6, 5, ..., 3, 2

    # value1 = integer
    # value2 = bool | None (None equals True)
    # modifier = 4 (-4 will also result 4)
    abroad(92, True, 4) # 0, 4, 8, 12, ..., 84, 88
    abroad(-92, True, 4) # -92, -88, -84, ..., -8, -4
    abroad(92, False, 4) # -92, -88, -84, ..., -8, -4
    abroad(-92, False, 4) # 0, 4, 8, 12, ..., 84, 88
    ```
    """
    # if isinstance(value1, ModernString): v1 = value1.get()
    # else: v1 = value1
    # if isinstance(value2, ModernString): v2 = value2.get()
    # else: v2 = value2
    # if isinstance(modifier, ModernString): m = modifier.get()
    # else: m = modifier
    # return _abroad_init(v1, v2, m)
    return _abroad_init(value1, value2, modifier)

def reckon(*countables: _ReckonType[_T]):
    """
    @lifetime >= 0.3.7 \\
    @standard-lifetime >= 0.3.7
    
    Extension of `len()` built-in function. Supports `IO` and \\
    its subclasses, classes having either `__len__`, `__iter__` \\
    or `__reckon__` magic methods.
    """
    i = 0
    
    for e in countables:
        i += _reckon_init(e)
        
    return i

def reckonLeast(*countables: _ReckonType[_T]):
    """
    @lifetime >= 0.3.25 \\
    @standard-lifetime >= 0.3.25
    
    Get least length from iterable objects passed.
    """
    n = 0
    for e in countables:
        if n > reckon(e):
            n = reckon(e)
    return n

def reckonGreatest(*countables: _ReckonType[_T]):
    """
    @lifetime >= 0.3.25 \\
    @standard-lifetime >= 0.3.25
    
    Get greatest length from iterable objects passed.
    """
    n = 0
    for e in countables:
        if n < reckon(e):
            n = reckon(e)
    return n

def reckonIsLeast(countable1: _ReckonType[_T], countable2: _ReckonType[_T], /):
    """
    @lifetime >= 0.3.25 \\
    @standard-lifetime >= 0.3.25
    
    Comparison: Check whether first argument is length-less than the second.
    """
    return reckon(countable1) < reckon(countable2)


def reckonIsGreater(countable1: _ReckonType[_T], countable2: _ReckonType[_T], /):
    """
    @lifetime >= 0.3.25 \\
    @standard-lifetime >= 0.3.25
    
    Comparison: Check whether first argument is length-greater than the second.
    """
    return reckon(countable1) > reckon(countable2)

if False: # < 0.3.49
    
    @__.deprecated("Deprecated since 0.3.42, will be removed on 0.3.48")
    class Reckon(__.Generic[_T]):
        """
        @lifetime >= 0.3.25 (5th July 2024) \\
        @standard-lifetime >= 0.3.25; < 0.3.42 \\
        @deprecated >= 0.3.42
        
        Class version of function `reckon()`
        """
        __countables = None
        def __init__(self, *countables: _ReckonType[_T]):
            self.__countables: list[_ReckonType[_T]] = []
            for e in countables:
                self.__countables.append(e)
                
        def get(self, specific: __.Optional[int] = None, /):
            """
            @lifetime >= 0.3.25 \\
            (standard since 0.3.25)
            ```
            # created 05.07.2024
            "method" in class Reckon
            ```
            Return size of all sizeable objects together. \\
            If `specific` is not `None`, returned is only \\
            at specified index. Out of range is typical \\
            Python error.
            """
            if specific is not None: return reckon(self.__countables[specific])
            else: return reckon(self.__countables)
            
        def least(self):
            """
            @lifetime >= 0.3.25 \\
            (standard since 0.3.25)
            ```
            # created 05.07.2024
            "method" in class Reckon
            ```
            Get least length from iterable objects passed to the constructor.
            """
            n = 0
            for e in self.__countables:
                if n > reckon(e):
                    n = reckon(e)
            return n
        
        def greatest(self):
            """
            @lifetime >= 0.3.25 \\
            (standard since 0.3.25)
            ```
            # created 05.07.2024
            "method" in class Reckon
            ```
            Get greatest length from iterable objects passed to the constructor.
            """
            n = 0
            for e in self.__countables:
                if n < reckon(e):
                    n = reckon(e)
            return n
        
        def isLeast(self, index1: int, index2: int, /):
            """
            @lifetime >= 0.3.25 \\
            (standard since 0.3.25)
            ```
            # created 05.07.2024
            "method" in class Reckon
            ```
            Both arguments lead to sizeable objects passed to the constructor. \\
            Returned is `True`, if size of object at index `index1` is least than \\
            object at index `index2`
            """
            return reckon(self.__countables[index1]) < reckon(self.__countables[index2])
        
        def isGreater(self, index1: int, index2: int, /):
            """
            @lifetime >= 0.3.25 \\
            (standard since 0.3.25)
            ```
            # created 05.07.2024
            "method" in class Reckon
            ```
            Both arguments lead to sizeable objects passed to the constructor. \\
            Returned is `True`, if size of object at index `index1` is greater than \\
            object at index `index2`
            """
            return reckon(self.__countables[index1]) > reckon(self.__countables[index2])
        
    @__.deprecated("Deprecated since 0.3.47, will be removed in 0.3.48")
    class protogen(_RAM):
        """
        @lifetime >= 0.3.25 \\
        (standard since 0.3.20) \\
        \\@modified 0.3.24, 0.3.25 \\
        https://aveyzan.xyz/tense/py/function.abroad.html

        This class is a joke, but alternative of `abroad()` function.
        """
        _ProtogenActivate = _ab_mod.AbroadInitializer
        def __new__(self, value1: _AbroadValue1[_T1], /, value2: _AbroadValue2[_T2] = None, modifier: _AbroadModifier[_T3] = None) -> _ProtogenActivate:
            """
            @lifetime >= 0.3.25 \\
            (standard since 0.3.20) \\
            \\@modified 0.3.24, 0.3.25 \\
            https://aveyzan.xyz/tense/py/function.abroad.html
            
            Construct a new `protogen` object, which will produce next integers, until an endpoint is caught. \\
            For more information, see `abroad()` function.
            """
            return abroad(value1, value2, modifier)
        @staticmethod
        def info():
            """Receive information about this class."""
            print(
                "Class name: protogen",
                "Class name for furry community: a furry species",
                "Class author: Aveyzan",
                "Extends: MutableSequence[int] (can be recognized as list)",
                "Created: 31.10.2023 (31st October 2023)",
                "Available since: Tense 0.3.20",
                "Standard since: Tense 0.3.20",
                "Main target: replacing range() function due to functionality",
                "Usage: similar to range(), identical to abroad()",
                sep = "\n"
            )

if _sys.version_info < (0, 3, 39):
    @__.deprecated("Deprecated since 0.3.31 due to loose of Tkinter support, will be removed on 0.3.36")
    class TenseTk:
        """
        @lifetime >= 0.3.25 \\
                ```
        in module tense
        ```
        TensePy Tk class from `tkinter` module equivalent.
        """
        
        __loc_tk = None
        __loc_frame = None
        __loc_label = None
        __loc_button = None
        __loc_buttons = None
        __loc_checkbutton = None
        __loc_checkbuttons = None
        __loc_radiobutton = None
        __loc_radiobuttons = None
        
        def __init__(self, screenName: __.Optional[str] = None, baseName: __.Optional[str] = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: __.Optional[str] = None) -> None:
            self.__loc_tk = _tkinter.Tk(
                screenName = screenName,
                baseName = baseName,
                className = className,
                useTk = useTk,
                sync = sync,
                use = use
            )
            self.__loc_frame = _tkinter.Frame(self.__loc_tk)
        
        def mainloop(self, n = 0):
            """
            @lifetime >= 0.3.25 \\
                        ```
            "method" in class YamiTk
            ```
            Call main loop of Tk
            """
            if self.__loc_tk is not None:
                self.__loc_tk.mainloop(n)
            else:
                err, s = (__.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self
        
        def setWindowSize(self, x: int, y: int, /):
            """
            @lifetime >= 0.3.25 \\
            3
            ```
            "method" in class YamiTk
            ```
            Set the window size measured in pixels. \\
            `x` means width, and `y` means height of the window
            """
            if self.__loc_tk is not None:
                self.__loc_tk.geometry(f"{x}x{y}")
            else:
                err, s = (__.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self
        
        def setMaxWindowSize(self, x: int, y: int, /):
            """
            @lifetime >= 0.3.25 \\
            3
            ```
            "method" in class YamiTk
            ```
            Set the max window size measured in pixels. \\
            `x` means width, and `y` means height of the window
            """
            if self.__loc_tk is not None:
                self.__loc_tk.maxsize(x, y)
            else:
                err, s = (__.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self
        
        def setTitle(self, title: str, /):
            """
            @lifetime >= 0.3.25 \\
            3
            ```
            "method" in class YamiTk
            ```
            Set title of the window
            """
            if self.__loc_tk is not None:
                self.__loc_tk.title(title)
            else:
                err, s = (__.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self
        
        @property
        def getTk(self):
            """
            @lifetime >= 0.3.25 \\
            3
            ```
            "property" in class YamiTk
            ```
            Return `tkinter.Tk` instance within the class
            """
            if self.__loc_tk is None:
                err, s = (__.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self.__loc_tk
        
        @property
        def getFrame(self):
            """
            @lifetime >= 0.3.25 \\
            3
            ```
            "property" in class YamiTk
            ```
            Return `tkinter.Frame` instance within the class
            """
            if self.__loc_frame is None:
                err, s = (__.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            return self.__loc_frame
        
        def setFrame(self, frame: _tkinter.Frame, /):
            """
            @lifetime >= 0.3.25 \\
            3
            ```
            "method" in class YamiTk
            ```
            Overwrite current `tkinter.Frame` instance
            """
            if self.__loc_frame is None:
                err, s = (__.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            elif not isinstance(frame, _tkinter.Frame):
                err, s = (TypeError, "Parameter 'frame' is not of instance 'tkinter.Frame'.")
                raise err(s)
            else:
                self.__loc_frame = frame
            return self
        
        def setLabel(self, label: _tkinter.Label, /):
            """
            @lifetime >= 0.3.25 \\
            3
            ```
            "method" in class YamiTk
            ```
            Overwrite current `tkinter.Label` instance or set a new value
            """
            if self.__loc_frame is None:
                err, s = (__.NotInitializedError, f"Class '{__class__.__name__}' was not initialized.")
                raise err(s)
            elif not isinstance(label, _tkinter.Label):
                err, s = (TypeError, "Parameter 'label' is not of instance 'tkinter.Label'.")
                raise err(s)
            else:
                self.__loc_label = label
            return self

# not for export
del RAM, _RAM

__all__ = sorted([n for n in globals() if n[:1] != "_"])
__dir__ = __all__

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error
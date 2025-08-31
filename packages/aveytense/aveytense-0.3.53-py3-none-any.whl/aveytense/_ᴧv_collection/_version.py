"""
@lifetime >= 0.3.47 \\
© 2024-Present Aveyzan // License: MIT

Provides version inspection components
"""

from __future__ import annotations
from . import _types as __
from . import _util

__name__ = "aveytense"

_qualifier = ("alpha", "beta", "candidate", "final")
_qualifier_type = __.Literal["alpha", "beta", "candidate", "final"]
_version_tuple_content = (0, 3, 53, "final", 0) # >= 0.3.48
_version_info_type = __.AVT_Tuple[int, int, int, _qualifier_type, int]

# >= 0.3.43; These are used only for overloads in order to hide unnecessary parts of the code
# when used with 'if' via 'VERSION_INFO', like 'sys.version_info'
_current_version_info_type1 = __.AVT_Tuple[__.Literal[0]]
_current_version_info_type2 = __.AVT_Tuple[__.Unpack[_current_version_info_type1], __.Literal[3]]
_current_version_info_type3 = __.AVT_Tuple[__.Unpack[_current_version_info_type2], __.Literal[53]]
_current_version_info_type4 = __.AVT_Tuple[__.Unpack[_current_version_info_type3], __.Literal["final"]]
_current_version_info_type5 = __.AVT_Tuple[__.Unpack[_current_version_info_type4], __.Literal[0]]

_counter_version_type = 0

VERSION = "0.3.53"
"""
@lifetime ≥ 0.3.26b3 \\
https://aveyzan.xyz/aveytense#aveytense.Tense.version

Returns currently used version of AveyTense
"""

VERSION_TYPE = __.Literal["0.3.53"]
"""
@lifetime ≥ 0.3.47
"""

def _qualifier_convert(s: str, /): # 0.3.40
    
    if s == "alpha":
        return 0
    
    elif s == "beta":
        return 1
    
    elif s == "candidate":
        return 2
    
    elif s == "final":
        return 3
    
    else:
        return -1

def _check_if_correct_tuple(t, /): # 0.3.40
    
    return type(t) is tuple and (
        (len(t) in (1, 2, 3) and all([type(e) is int for e in t])) or
        (len(t) == 4 and all([type(e) is int for e in t][:3]) and t[3] in _qualifier) or
        (len(t) == 5 and all([type(e) is int for e in t][:3] + [type(t[4]) is int]) and t[3] in _qualifier)
    )

class _VERSION_INFO:
    """@lifetime ≥ 0.3.40"""
    
    def __init__(self, major: int, minor: int, micro: int, releaselevel: _qualifier_type, serial: int, /): # 0.3.40
        
        global _counter_version_type
        
        if _counter_version_type == 1:
            error = TypeError("cannot instantiate internal class '{}'".format(type(self).__name__))
            raise error
        
        else:
            _counter_version_type = 1
        
        self.__tuple = (major, minor, micro, releaselevel, serial if releaselevel != "final" else 0)
        
    @_util.finalproperty
    def major(self): # 0.3.40
        return self.__tuple[0]
    
    @_util.finalproperty
    def minor(self): # 0.3.40
        return self.__tuple[1]
    
    @_util.finalproperty
    def micro(self): # 0.3.40
        return self.__tuple[2]
    
    @_util.finalproperty
    def releaselevel(self): # 0.3.40
        return self.__tuple[3]
    
    @_util.finalproperty
    def serial(self): # 0.3.40
        return self.__tuple[4]
    
    @_util.finalproperty
    def tuple(self): # 0.3.40
        return self.__tuple
    
    def __str__(self): # 0.3.40
        
        # ansi escape code! for use you can see class ~.Color
        return "-----\nAveyTense {} \nversion_components[\n\033[3m  major = {},\n  minor = {},\n  micro = {},\n  releaselevel = '{}',\n  serial = {}\033[0m\n]\n-----".format(
            "\033[38;5;46m{}.{}.{}\033[0m (final release)".format(self.__tuple[0], self.__tuple[1], self.__tuple[2]) if self.__tuple[3] == "final" else
            "\033[38;5;208m{}.{}.{}a{}\033[0m (alpha release)".format(self.__tuple[0], self.__tuple[1], self.__tuple[2], self.__tuple[4]) if self.__tuple[3] == "alpha" else
            "\033[38;5;226m{}.{}.{}b{}\033[0m (beta release)".format(self.__tuple[0], self.__tuple[1], self.__tuple[2], self.__tuple[4]) if self.__tuple[3] == "beta" else
            "\033[38;5;154m{}.{}.{}rc{}\033[0m (release candidate)".format(self.__tuple[0], self.__tuple[1], self.__tuple[2], self.__tuple[4]),
            self.__tuple[0], self.__tuple[1], self.__tuple[2], self.__tuple[3], self.__tuple[4]
        )
        
    @__.overload
    def __lt__(self, other: _current_version_info_type1) -> __.Literal[False]: ...
        
    @__.overload
    def __lt__(self, other: _current_version_info_type2) -> __.Literal[False]: ...
    
    @__.overload
    def __lt__(self, other: _current_version_info_type3) -> __.Literal[False]: ...
    
    @__.overload
    def __lt__(self, other: _current_version_info_type4) -> __.Literal[False]: ...
    
    @__.overload
    def __lt__(self, other: _current_version_info_type5) -> __.Literal[False]: ...
    
    @__.overload
    def __lt__(self, other: _version_info_type) -> bool: ...
        
    def __lt__(self, other: _version_info_type): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major < other[0]) or
            (len(other) == 2 and self.minor < other[1]) or
            (len(other) == 3 and self.micro < other[2]) or
            (len(other) == 4 and _qualifier_convert(self.releaselevel) < _qualifier_convert(other[3])) or
            (len(other) == 5 and self.serial < other[4])
        ))
        
    @__.overload
    def __gt__(self, other: _current_version_info_type1) -> __.Literal[False]: ...
        
    @__.overload
    def __gt__(self, other: _current_version_info_type2) -> __.Literal[False]: ...
    
    @__.overload
    def __gt__(self, other: _current_version_info_type3) -> __.Literal[False]: ...
    
    @__.overload
    def __gt__(self, other: _current_version_info_type4) -> __.Literal[False]: ...
    
    @__.overload
    def __gt__(self, other: _current_version_info_type5) -> __.Literal[False]: ...
    
    @__.overload
    def __gt__(self, other: _version_info_type) -> bool: ...
        
    def __gt__(self, other: _version_info_type): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major > other[0]) or
            (len(other) == 2 and self.minor > other[1]) or
            (len(other) == 3 and self.micro > other[2]) or
            (len(other) == 4 and _qualifier_convert(self.releaselevel) > _qualifier_convert(other[3])) or
            (len(other) == 5 and self.serial > other[4])
        ))
        
    @__.overload
    def __le__(self, other: _current_version_info_type1) -> __.Literal[True]: ...
        
    @__.overload
    def __le__(self, other: _current_version_info_type2) -> __.Literal[True]: ...
    
    @__.overload
    def __le__(self, other: _current_version_info_type3) -> __.Literal[True]: ...
    
    @__.overload
    def __le__(self, other: _current_version_info_type4) -> __.Literal[True]: ...
    
    @__.overload
    def __le__(self, other: _current_version_info_type5) -> __.Literal[True]: ...
    
    @__.overload
    def __le__(self, other: _version_info_type) -> bool: ...
        
    def __le__(self, other): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major <= other[0]) or
            (len(other) == 2 and self.minor <= other[1]) or
            (len(other) == 3 and self.micro <= other[2]) or
            (len(other) == 4 and _qualifier_convert(self.releaselevel) <= _qualifier_convert(other[3])) or
            (len(other) == 5 and self.serial <= other[4])
        ))
        
    @__.overload
    def __ge__(self, other: _current_version_info_type1) -> __.Literal[True]: ...
        
    @__.overload
    def __ge__(self, other: _current_version_info_type2) -> __.Literal[True]: ...
    
    @__.overload
    def __ge__(self, other: _current_version_info_type3) -> __.Literal[True]: ...
    
    @__.overload
    def __ge__(self, other: _current_version_info_type4) -> __.Literal[True]: ...
    
    @__.overload
    def __ge__(self, other: _current_version_info_type5) -> __.Literal[True]: ...
    
    @__.overload
    def __ge__(self, other: _version_info_type) -> bool: ...
        
    def __ge__(self, other): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major >= other[0]) or
            (len(other) == 2 and self.minor >= other[1]) or
            (len(other) == 3 and self.micro >= other[2]) or
            (len(other) == 4 and _qualifier_convert(self.releaselevel) >= _qualifier_convert(other[3])) or
            (len(other) == 5 and self.serial >= other[4])
        ))
        
    def __eq__(self, other: _version_info_type): # 0.3.40
        
        return bool(_check_if_correct_tuple(other) and (
            (len(other) == 1 and self.major == other[0]) and
            (len(other) == 2 and self.minor == other[1]) and
            (len(other) == 3 and self.micro == other[2]) and
            (len(other) == 4 and _qualifier_convert(self.releaselevel) == _qualifier_convert(other[3])) and
            (len(other) == 5 and self.serial == other[4])
        ))
        
    def __ne__(self, other: _version_info_type): # 0.3.40
        
        return not self.__eq__(other)

VERSION_INFO = _VERSION_INFO(
    _version_tuple_content[0],
    _version_tuple_content[1],
    _version_tuple_content[2],
    _version_tuple_content[3],
    _version_tuple_content[4]
)
"""
@lifetime >= 0.3.26b3 \\
https://aveyzan.xyz/aveytense#aveytense.Tense.versionInfo
"""

VERSION_INFO_TYPE = type(VERSION_INFO)
"""@lifetime >= 0.3.36"""

_VERSION_INFO = _util.abstract(_VERSION_INFO)
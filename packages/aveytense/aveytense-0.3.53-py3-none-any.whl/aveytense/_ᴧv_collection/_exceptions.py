"""
@lifetime ≥ 0.3.47 \\
© 2024-Present Aveyzan // License: MIT

Internal exceptions submodule
"""

from __future__ import annotations # this was missing until 0.3.51

from . import _types
from ..exceptions import *
import sys as _sys

_unbound_local_messages = (
    "cannot access local variable '{}' where it is not associated with a value",
    "local variable '{}' referenced before assignment"
) # ≥ 0.3.47

def _replacement(type: _types.AVT_Type[BaseException], value: BaseException, tb: _types.Optional[_types.TracebackType]): # ≥ 0.3.47
    
    from .. import exceptions
    import os, sys, traceback
    print("Traceback (most recent call last):") # common message; we cannot go without it 
    _get_ = traceback.format_tb(tb, 1)
    
    # at present, there is no way to provide qualified name of an exception
    # unless we don't import everything to global scope
    _name_ = "aveytense.exceptions." + type.__name__ if hasattr(exceptions, type.__name__) else type.__name__
    
    # does PYTHON_COLORS environment variable (https://docs.python.org/3/using/cmdline.html#envvar-PYTHON_COLORS)
    # change values for FORCE_COLOR and NO_COLOR? if yes, that is:
    # for PYTHON_COLORS == "1": FORCE_COLOR = "1" & NO_COLOR = "0"
    # for PYTHON_COLORS == "0": FORCE_COLOR = "0" & NO_COLOR = "1"
    # '--no-color' takes place in 'py' command, when invoked as 'py <pythonFile> --no-color'.
    # without it and PYTHON_COLORS having value 1 (by default) will cause the output being colored
    if sys.version_info >= (3, 13) and "--no-color" not in sys.argv and os.environ.get("PYTHON_COLORS", "1") == "1":
       
        # Normally, 'traceback' module doesn't feature colored traceback (what is a thing in Py3.13), so keep it on mind!
        # 10.06.2025
        _REMOVE_ = "<remove_f120b617be2ee2452caba07c>" # random but something different than ^ and ~
        _print_ = _get_[0].split(", ")
        _file_ = _print_[0][:7] + "\x1b[35m\"" + _print_[0][8:-1] + "\"\x1b[0m"
        _line_ = "line \x1b[35m" + _print_[1][5:] + "\x1b[0m"
        _last_ = _print_[2].split("\n")[:-1]
        
        # this constant has auxiliary character only; _last_ list variable don't need to have 3 items
        # if there are 2, then we are missing an item with ^ and ~ chars only
        if len(_last_) == 2:
            _last_ += [_REMOVE_]
        
        # 0.3.50
        elif len(_last_) == 1:
            _last_ += [", ".join(_print_[2:]).removeprefix("in <module>\n").rstrip()] + [_REMOVE_]
        
        _in_ = "in \x1b[35m" + _last_[0][3:] + "\x1b[0m"
        
        # carets (^) in a traceback entry can appear only once, and cannot be
        # scattered, like: ~~~~^^~~~^^~; correct output: ~~~~^^^^~~~~
        _caret_range_ = [0, 0]
        
        if _last_[2] != _REMOVE_:
            
            while _last_[2][_caret_range_[0]] != "^":
                _caret_range_[0] += 1
            
            _caret_range_[1] = _caret_range_[0]
            
            # if we catch IndexError there, that means carets are placed on the end,
            # and there are no tildes on the right
            try:
                
                while _last_[2][_caret_range_[1]] == "^":
                    _caret_range_[1] += 1
                    
            except IndexError:
                pass
        
        # tildes (~) can be on left or right (or both) of place where carets are placed
        _tilde_range_ = [_last_[2].count(" "), len(_last_[2])]
        
        # ansi escape code. for easier use, check out ~.Color class.
        # 31 means red, 1;31 means bold red, 35 means pink,
        # 1;31 means bold pink, 0 resets the formatting
        
        if _last_[2] == _REMOVE_:
            
            print(
                ", ".join([_file_, _line_, _in_]),
                _last_[1],
                "\x1b[1;35m{}\x1b[0m: \x1b[35m{}\x1b[0m".format(_name_, str(value)),
                sep = "\n"
            )
            
        else:
            
            print(
                ", ".join([_file_, _line_, _in_]),
                # code highlight
                (_last_[1][:_tilde_range_[0]] + \
                    "\x1b[31m" + _last_[1][_tilde_range_[0]:_caret_range_[0]] + \
                    "\x1b[1;31m" + _last_[1][_caret_range_[0]:_caret_range_[1]] + \
                    "\x1b[31m" + _last_[1][_caret_range_[1]:_tilde_range_[1]] + \
                    "\x1b[0m" + _last_[1][_tilde_range_[1]:]
                ),
                # highlight with ^ and ~
                ( 
                    "\x1b[31m" + _last_[2][:_caret_range_[0]] + \
                    "\x1b[1;31m" + _last_[2][_caret_range_[0]:_caret_range_[1]] + \
                    "\x1b[31m" + _last_[2][_caret_range_[1]:] + \
                    "\x1b[0m"
                ),
                "\x1b[1;35m{}\x1b[0m: \x1b[35m{}\x1b[0m".format(_name_, str(value)),
                sep = "\n"
            )
        
    else:
        
        # if we cannot invoke 'try' statement, we need to use traceback.print_tb.
        # we cannot have list item with only whitespaces, tildes and carets in older
        # versions of Python; usually 'try' statement below should throw IndexError
        try: 
        
            _tab_ = _get_[0].split("\n")
            _print_ = "".join(_tab_[:-3])
            
            print(
                _print_,
                _tab_[-3],
                _tab_[-2],
                "{}: {}".format(_name_, str(value)),
                sep = "\n"
            )
            
        except:
            
            traceback.print_tb(tb, 1)
        
_sys.excepthook = _replacement

class _ErrorHandler:
    """
    @lifetime ≥ 0.3.26rc1
    
    Internal class for error handling. Does not exist at runtime

    - `100` - cannot modify a final variable (`any`)
    - `101` - cannot use comparison operators on type which doesn't support them + ...
    - `102` - cannot assign a new value or re-assign a value with any of augmented \\
    assignment operators on type which doesn't support them + ...
    - `103` - object is not iterable (`any`)
    - `104` - attempt to initialize an abstract class + ...
    - `105` - class (`any`) was not initialized
    - `106` - could not compare types - at least one of them does not support comparison \\
    operators
    - `107` - object cannot be called
    - `108` - object cannot use any of unary operators: '+', '-', '~', cannot be called nor be value \\
    of `abs()` in-built function
    - `109` - object cannot use unary +|- operator
    - `110` - object cannot use bitwise NOT operator '~'
    - `111` - import-only module
    - any other - unknown error occured
    """
    def __new__(cls, code: int, *args: str):
        _arg0 = "" if len(args) == 0 else args[0]
        _arg1 = "" if len(args) == 1 else args[1]
        if code == 100:
            _error = (NotReassignableError, "cannot modify a final variable '{}'".format(_arg0) if _arg0 not in (None, "") else "cannot modify a final variable")
        elif code == 101:
            _error = (NotComparableError, "cannot use comparison operators on type which doesn't support them" + _arg0)
        elif code == 102:
            _error = (NotReassignableError, "cannot assign a new value or re-assign " + _arg0)
        elif code == 103:
            _error = (NotIterableError, "object is not iterable ('{}')".format(_arg0) if _arg0 not in (None, "") else "cannot modify a final variable")
        elif code == 104:
            _error = (InitializedError, "attempt to initialize an abstract class '{}'".format(_arg0))
        elif code == 105:
            _error = (NotInitializedError, "class '{}' was not initalized".format(_arg0))
        elif code == 106:
            _error = (NotComparableError, "could not compare types - at least one of them does not support comparison operators")
        elif code == 107:
            _error = (NotCallableError, "class {} cannot be called".format(_arg0))
        elif code == 108:
            _error = (TypeError, "object cannot use any of unary operators: '+', '-', '~'")
        elif code == 109:
            _error = (TypeError, "object cannot use unary '{}' operator".format(_arg0))
        elif code == 110:
            _error = (TypeError, "object cannot use bitwise NOT operator '~'")
        elif code == 111:
            _error = (RuntimeError, "import-only module")
        elif code == 112:
            _error = (AttributeError, "cannot modify a final attribute '{}'".format(_arg0))
        elif code == 113:
            _error = (SubclassedError, "attempt to subclass a final class '{}'".format(_arg0))
        elif code == 114:
            _error = (TypeError, "'{}' cannot be used on '{}'".format(_arg0, _arg1))
        elif code == 115:
            _error = (TypeError, "cannot inspect because class '{}' is abstract".format(_arg0))
        elif code == 116:
            _error = (TypeError, "cannot inspect because class '{}' is final".format(_arg0))
        elif code == 117:
            _error = (AttributeError, "attempt to delete item '{}'".format(_arg0))
        elif code == 118:
            _error = (AttributeError, "attempt to reassign item '{}'".format(_arg0))
        elif code == 119:
            _error = (AttributeError, "cannot modify any fields in class {}".format(_arg0))
        elif code == 120:
            _error = (TypeError, "cannot recast method '{}'".format(_arg0))
        elif code == 121:
            _error = (TypeError, "cannot modify field '{}' with operator '{}'".format(_arg0, _arg1))
        elif code == 122:
            _error = (TypeError, "attempt to set or delete final property '{}'".format(_arg0))
        elif code == 123:
            _error = (TypeError, "cannot change value for an enumerator")
        else:
            _error = (RuntimeError, "unknown error occured")
        error = _error[0](_error[1])
        raise error

# prevent unused
_unbound_local_messages = _unbound_local_messages
_ErrorHandler = _ErrorHandler
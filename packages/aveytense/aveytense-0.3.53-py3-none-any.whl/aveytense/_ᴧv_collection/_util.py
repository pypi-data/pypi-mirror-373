"""
@lifetime >= 0.3.34 \\
© 2025-Present Aveyzan // License: MIT

Core of `aveytense.util`; use `aveytense.util` instead
"""
from __future__ import annotations

import abc as _abc
import dis as _dis
import sys as _sys

from . import _types as __
from ._exceptions import _ErrorHandler as _E

__name__ = "aveytense.util"

_ch = eval # checker

_P = __.ParamSpec("_P")
_T = __.TypeVar("_T")
_T_cov = __.TypeVar("_T_cov", covariant = True)
_T_func = __.TypeVar("_T_func", bound = __.AVT_Callable[..., __.Any])
    
_T_enum = __.TypeVar("_T_enum", bound = __.Enum)
_RichComparable = __.RichComparable

_OptionSelection = __.Literal["frozen", "final", "abstract", "no_reassign", "forced_abstract"] # 0.3.27rc2

_AllMode = __.Literal[
    "clear",
    "lowercased",
    "lowercased_clear",
    "uppercased",
    "uppercased_clear",
    "sunder",
    "lowercased_sunder",
    "uppercased_sunder",
    "dunder",
    "lowercased_dunder",
    "uppercased_dunder",
    "protected",
    "lowercased_protected",
    "uppercased_protected",
    "private",
    "lowercased_private",
    "uppercased_private",
    "all"
] # 0.3.53

_compiler_flags = {
    "optimized": 1,
    "newlocals": 1 << 1,
    "varargs": 1 << 2,
    "varkeywords": 1 << 3,
    "nested": 1 << 4,
    "generator": 1 << 5,
    "nofree": 1 << 6,
    "coroutine": 1 << 7,
    "iterable_coroutine": 1 << 8,
    "async_generator": 1 << 9
} # 0.3.42

_dis_compiler_flags = {_dis.COMPILER_FLAG_NAMES[k].lower(): k for k in _dis.COMPILER_FLAG_NAMES} # 0.3.42

assert _compiler_flags == _dis_compiler_flags # 0.3.42

def _reckon(i: __.AVT_Iterable[_T], /):
    
    _i = 0
    
    for _ in i:
        _i += 1
        
    return _i

def _ih(id: int, /): # internal helper
    
    _m = "eval"
    _c = _i = ""
    
    if id == 10:
        
        _c, _i = "_E(113, t.__name__)", "<final-class inspect>"
        
    elif id == 11:
        
        _c, _i = "_E(116, type(self).__name__)", "<final-class inspect>"
        
    elif id == 12:
        
        _c, _i = "_E(116, t.__name__)", "<final-class inspect>"
        
    elif id == 20:
        
        _c, _i = "_E(104, type(self).__name__)", "<abstract-class inspect>"
    
    elif id == 21:
        
        _c, _i = "_E(115, type(self).__name__)", "<abstract-class inspect>"
        
    elif id == 22:
        
        _c, _i = "_E(115, t.__name__)", "<abstract-class inspect>"
        
    return compile(_c, _i, _m)

if False: # < 0.3.47; not used anymore
    
    def _verify_func(f): # 0.3.42
        
        from functools import partial
        
        func = f.func if isinstance(f, partial) else f if callable(f) else None
        
        if func is not None and func.__code__.co_argcount != 1:
            
            error = TypeError("expected a callable with proper implementation")
            raise error
    
def _return_param(f = object(), s = ""): # 0.3.47
    """
    @lifetime >= 0.3.47
    
    Used to remove private method notation on pre-PEP 570 positional-only parameters in a method. \\
    Not intended to be shared globally; this function is reserved for `~.util.ParamVar` class only.
    ```
        _return_param(Class().method, "__1") # -> __1 instead of _Class__1
        _return_param(Class().method, "__1_") # -> __1_ instead of _Class__1_
        _return_param(Class().method, "__1__") # -> __1__ (no change)
    ```
    """
    
    # 0.3.50: callable(...) and __name__ != __qualname__
    if isinstance(f, __.MethodType) or (callable(f) and f.__name__ != f.__qualname__):
        
        if _sys.version_info >= (3, 9): # 0.3.53: see PEP 616
            _remove_prefix_ = lambda x = "", prefix = "": x.removeprefix(prefix)
            _remove_suffix_ = lambda x = "", suffix = "": x.removesuffix(suffix)
            
        else:
            _remove_prefix_ = lambda x = "", prefix = "": x[_reckon(prefix):] if x.startswith(prefix) else x[:]
            _remove_suffix_ = lambda x = "", suffix = "": x[:_reckon(suffix)] if suffix and x.endswith(suffix) else x[:]
        
        _class_ = "_" +  _remove_suffix_(f.__qualname__, "." + f.__name__)
        
        if s.startswith(_class_ + "__") and not s.endswith("__"):
            return _remove_prefix_(s, _class_)
            
    return s

def _check_if_callable(f): # 0.3.51
    
    return callable(f) or isinstance(f, __.partial)

def _check_if_builtin(f): # 0.3.51
    
    return isinstance(f, (
        __.BuiltinFunctionType,
        __.ClassMethodDescriptorType,
        __.MethodDescriptorType,
        __.MethodWrapperType,
        __.WrapperDescriptorType
    ))

def _param_sanitize(param = "", includeEqualSign = False): # 0.3.51
    """Used in internal class `~.util._BuiltinParamVar`"""
            
    s = ""
    
    for c in param:
        
        if c == "=":
            
            if includeEqualSign:
                s += c
            
            break
        
        s += c
        
    return s.lstrip("*")


class _FlagsType:
    """@lifetime >= 0.3.53"""
    
    _members = [""]
    
    def __setattr__(self, name: str, value: __.Any):
        
        if name in self._members[1:]:
            _E(102, "'{}'".format(name))
        
        self._members.append(name)
        setattr(self, name, value)
        
    def __delattr__(self, name: str):
        
        if name in self._members[1:]:
            error = TypeError("cannot delete member '{}'".format(name))
            raise error
        
        delattr(self, name)
        
class _TypeFlags:
    """@lifetime >= 0.3.53"""
    
    # https://github.com/python/cpython/blob/31a8393cf6a74c870c3484dd68500619f6232c6d/Include/object.h#L598
    # In C notation '1UL' ('unsigned long long') is used to get wider positive value range. In Python this notation doesn't exist,
    # but we can use '1' instead
    # exception is 'mapping' property: see _collections_abc.Mapping.__abc_tpflags__ from _collections_abc.py
    
    @property 
    def mapping(self):
        return 1 << 6
    
    @property
    def heapType(self):
        return 1 << 9
    
    @property
    def baseType(self):
        return 1 << 10
    
    @property
    def ready(self):
        return 1 << 12
    
    @property
    def readying(self):
        return 1 << 13
    
    @property
    def haveGc(self):
        return 1 << 14
    
    @property
    def haveStacklessExtension(self):
        
        import os
        
        if os.environ.get("STACKLESS", False) and _sys.version_info < (3, 10): # Stackless Python exclusive only
            return 1 << 15
        else:
            return 0
    
    @property
    def haveVersionTag(self):
        return 1 << 18
    
    @property
    def validVersionTag(self):
        return 1 << 19
    
    @property
    def abstract(self):
        return 1 << 20
    
    @property
    def longSubclass(self):
        return 1 << 24
    
    @property
    def listSubclass(self):
        return 1 << 25
    
    @property
    def tupleSubclass(self):
        return 1 << 26
    
    @property
    def bytesSubclass(self):
        return 1 << 27
    
    @property
    def unicodeSubclass(self):
        return 1 << 28
    
    @property
    def dictSubclass(self):
        return 1 << 29
    
    @property
    def baseExcSubclass(self):
        return 1 << 30
    
    @property
    def typeSubclass(self):
        return 1 << 31
    
    @property
    def default(self):
        return self.haveStacklessExtension | self.haveVersionTag | 0
    
class _CodeFlags:
    """@lifetime >= 0.3.53"""
    
    # https://github.com/python/cpython/blob/31a8393cf6a74c870c3484dd68500619f6232c6d/Include/code.h#L54
    @property
    def optimized(self):
        return 1
    
    @property
    def newlocals(self):
        return 1 << 1
    
    @property
    def varargs(self):
        return 1 << 2
    
    @property
    def varkeywords(self):
        return 1 << 3
    
    @property
    def nested(self):
        return 1 << 4
    
    @property
    def generator(self):
        return 1 << 5
    
    @property
    def noFree(self):
        return 1 << 6
    
    @property
    def coroutine(self):
        return 1 << 7
    
    @property
    def iterableCoroutine(self):
        return 1 << 8
    
    @property
    def asyncGenerator(self):
        return 1 << 9
    
class _BufferFlags:
    """@lifetime >= 0.3.53"""
    
    # retrieved via 'inspect.BufferFlags' source code for Python 3.13.5
    @property
    def contiguous(self):
        return 0x9
    
    @property
    def contiguousAny(self):
        return 0x98
    
    @property
    def contiguousC(self):
        """C-contiguous"""
        return 0x38
    
    @property
    def contiguousF(self):
        """Fortran contiguous"""
        return 0x58
    
    @property
    def contiguousReadOnly(self):
        return 0x18
    
    @property
    def format(self):
        return 0x4
    
    @property
    def full(self):
        return 0x11d
    
    @property
    def fullReadOnly(self):
        return 0x11c
    
    @property
    def indirect(self):
        return 0x118
    
    @property
    def nd(self):
        return 0x8
    
    @property
    def read(self):
        return 0x100
    
    @property
    def records(self):
        return 0x1d
    
    @property
    def recordsReadOnly(self):
        return 0x1c
    
    @property
    def simple(self):
        return 0x0
    
    @property
    def strided(self):
        return 0x19
    
    @property
    def stridedReadOnly(self):
        return 0x18
    
    @property
    def strides(self):
        return 0x18
    
    @property
    def writable(self):
        return 0x1
    
    @property
    def write(self):
        return 0x200

class _InternalHelper:
    """
    @lifetime >= 0.3.27rc2
    
    Class responsible to shorten code for several classes such as `Final` and `Abstract`
    """
    
    def __new__(cls, t: __.AVT_Type[_T], o: _OptionSelection, /):
        
        _reassignment_operators = {
            "__iadd__": "+=",
            "__isub__": "-=",
            "__imul__": "*=",
            "__itruediv__": "/=",
            "__ifloordiv__": "//=",
            "__imod__": "",
            "__imatmul__": "@=",
            "__iand__": "&=",
            "__ior__": "|=",
            "__ixor__": "^=",
            "__ilshift__": "<<=",
            "__irshift__": ">>=",
            "__ipow__": "**="
        }
        
        _cannot_redo = {"tmp": "tmp2"}
        
        # assuming empty string-string dictionary
        
        if False: # < 0.3.37
            if _cannot_redo["tmp"]:
                del _cannot_redo["tmp"]
                
        else:
            _cannot_redo.clear()
        
        def _no_sa(self: _T, name: str, value): # no setattr
            
            if name in type(self).__dict__:
                _E(118, name)
            
            self.__dict__[name] = value
            
        def _no_da(self: _T, name: str): # no delattr
            
            if name in type(self).__dict__:
                _E(117, name)
                
        def _no_inst(self: _T, *args, **kwds): # no initialize
            _ch(_ih(20))
            
        def _no_cinst(o: object): # no check instance
            nonlocal t
            _ch(_ih(22))
            
        def _no_sub(*args, **kwds): # no subclass
            nonlocal t
            _ch(_ih(10))
            
        def _no_csub(cls: type): # no check subclass
            nonlocal t
            _ch(_ih(12))
            
        def _no_re(op: str): # no reassignment; must return callback so assigned attributes can be methods
            
            def _no_re_internal(self: __.Self, other: _T):
                
                _op = "with operator {}".format(op)
                _E(102, _op)
                
            return _no_re_internal
        
        def _empty_mro(self: _T): # empty method resolution order; peculiar for final classes
            return None
        
        if o in ("frozen", "no_reassign"):
            
            t.__slots__ = ("__weakref__",)
            t.__setattr__ = _no_sa
            t.__delattr__ = _no_da
            
            _cannot_redo["__setattr__"] = _no_sa.__name__
            _cannot_redo["__delattr__"] = _no_da.__name__
            
            if o == "no_reassign":
                
                for key in _reassignment_operators:
                    
                    exec("t.{} = _no_re(\"{}\")".format(key, _reassignment_operators[key])) # f-strings since python 3.6
                    exec("_cannot_redo[\"{}\"] = _no_re(\"{}\").__name__".format(key, _reassignment_operators[key]))
                    
        elif o == "final":
            
            t.__slots__ = ("__weakref__",)
            t.__init_subclass__ = _no_sub
            t.__subclasscheck__ = _no_csub
            t.__mro_entries__ = _empty_mro
            
            _cannot_redo["__init_subclass__"] = _no_sub.__name__
            _cannot_redo["__subclasscheck__"] = _no_csub.__name__
            _cannot_redo["__mro_entries__"] = _empty_mro.__name__
            
        else:
            
            if o == "forced_abstract":
                t.__call__ = _no_inst
                
                _cannot_redo["__call__"] = _no_inst.__name__
            
            else:
                t.__init__ = _no_inst
                t.__instancecheck__ = _no_cinst
                
                _cannot_redo["__init__"] = _no_inst.__name__
                _cannot_redo["__instancecheck__"] = _no_cinst.__name__
            
        for key in _cannot_redo:
            if _cannot_redo[key] != "_no_re_internal" and eval("t.{}.__code__".format(key)) != eval("{}.__code__".format(_cannot_redo[key])):
                _E(120, key)    
        
        return t

class _FinalVar(__.NamedTuple, __.Generic[_T]): # 0.3.35
    x: _T
    """
    @lifetime >= 0.3.35
    
    This attribute holds the value
    """
    
    def __pos__(self):
        
        return self.x
    
    def __str__(self):
        
        return "FinalVar({})".format(str(self.x) if type(self.x) is not str else self.x)
    
    def __repr__(self): # 0.3.40
        
        return "<{}.{} object: {}>".format(self.__module__, type(self).__name__, self.__str__())

def _extend(*dicts: __.AVT_Dict[str, __.Any]):
    """@lifetime >= 0.3.53"""
    
    _list_ = [""]
    _list_.clear()
    
    for e in dicts:
        _list_.extend([k for k in e if not k.startswith("_")])
        
    return _list_

# if not that, then it will behave like normal NamedTuple
_FinalVar = _InternalHelper(_FinalVar, "no_reassign")

if False: # < 0.3.52
    types = __
    """@lifetime >= 0.3.37"""


class Abstract:
    """
    @lifetime >= 0.3.26b3 \\
    https://aveyzan.xyz/aveytense#aveytense.util.Abstract
    
    Creates an abstract class. This type of class forbids class initialization. To prevent this class \\
    being initialized, this class is a protocol class.
    
    To promote a class abstract, it is needed to use inheritance, as shown::
        
        from aveytense.util import Abstract
        
        class A(Abstract): ...
        print(A()) # InitializedError
        
    This is done by overriding `__init__` method. Worth noticing the class doesn't work the same as \\
    `abc.ABC`. Class object construction from `abc.ABC` is allowed only, if there aren't any abstract \\
    methods, meanwhile `~.Abstract` doesn't require any abstract methods to throw an error upon \\
    object initialization.
    """
    
    def __init__(self):
        _ch(_ih(20))
        
    def __init_subclass__(cls):
        cls = _InternalHelper(cls, "abstract")
    
    def __instancecheck__(self, instance: object):
        "@lifetime >= 0.3.27b1. Error is thrown, because class may not be instantiated"
        _ch(_ih(21))
    
    def __subclasscheck__(self, cls: type):
        "@lifetime >= 0.3.27b1. Check whether a class is a subclass of this class"
        return issubclass(cls, type(self))
    
    if False: # 0.3.28 (use abstractmethod instead)
        @staticmethod
        def method(f: _T_func):
            """@lifetime >= 0.3.27rc2"""
            from abc import abstractmethod as _a
            return _a(f)

def abstract(t: __.AVT_Type[_T], /): # <- 0.3.41 slash
    """
    @lifetime >= 0.3.27a5 (formally)
    
    Decorator for abstract classes. To 0.3.27rc2 same as `abc.abstractmethod()`
    """
    t = _InternalHelper(t, "abstract")
    return t

def abstractmethod(f: _T_func, /): # <- 0.3.41 slash
    """@lifetime >= 0.3.27rc2"""
    
    # to accord python implementation
    if False:
        return Abstract.method(f)
    
    else:
        return _abc.abstractmethod(f)
    
if hasattr(_abc, "abstractproperty"):
    from abc import abstractproperty as abstractproperty # deprecated since 3.3
    
else:
    class abstractproperty(property):
        """
        @lifetime >= 0.3.26rc1

        A decorator class for abstract properties.

        Equivalent invoking decorators `aveytense.types.abstract` and in-built `property`.
        """
        __isabstractmethod__ = True

if hasattr(_abc, "abstractstaticmethod"):
    from abc import abstractstaticmethod as abstractstaticmethod # deprecated since 3.3
    
else:
    class abstractstaticmethod(staticmethod):
        """
        @lifetime >= 0.3.26rc1

        A decorator class for abstract static methods.

        Equivalent invoking decorators `aveytense.types.abstract` and in-built `staticmethod`.
        """
        __isabstractmethod__ = True
        
        def __init__(self, f: __.AVT_Callable[_P, _T_cov]):
            f.__isabstractmethod__ = True
            super().__init__(f)

if hasattr(_abc, "abstractclassmethod"):
    from abc import abstractclassmethod as abstractclassmethod # deprecated since 3.3
    
else:
    class abstractclassmethod(classmethod):
        """
        @lifetime >= 0.3.26rc1

        A decorator class for abstract class methods.

        Equivalent invoking decorators `aveytense.types.abstract` and in-built `classmethod`.
        """
        __isabstractmethod__ = True
        
        def __init__(self, f: __.AVT_Callable[__.Concatenate[__.AVT_Type[_T], _P], _T_cov]):
            f.__isabstractmethod__ = True
            super().__init__(f)

# reference to enum.Enum; during experiments and not in use until it is done
# tests done for 0.3.27rc1
class Frozen:
    """
    @lifetime >= 0.3.27b1 (experiments finished 0.3.27rc1, updated: 0.3.27rc2) \\
    https://aveyzan.xyz/aveytense#aveytense.util.Frozen
    
    Creates a frozen class. This type of class doesn't allow change of provided fields \\
    once class has been declared and then initialized.
    """
    
    def __init_subclass__(cls):
        cls = type(cls.__name__, tuple([]), {k: _FinalVar(cls.__dict__[k]) for k in cls.__dict__ if k[:1] != "_"})

def frozen(t: __.AVT_Type[_T], /): # <- 0.3.41 slash
    """
    @lifetime >= 0.3.27rc1

    Alias to `dataclass(frozen = True)` decorator (for 0.3.27rc1). \\
    Since 0.3.27rc2 using different way.
    """
    t = _InternalHelper(t, "frozen")
    return t


class Final:
    """
    @lifetime >= 0.3.26b3 (experimental; to 0.3.27b3 `FinalClass`, experiments ended 0.3.27rc1) \\
    https://aveyzan.xyz/aveytense#aveytense.util.Final
    
    Create a final class. This kind of subclasses disallow further inheritance. Example::
    
        from aveytense.util import Final
        
        class F1(Final): ...
        class F2(F1): ... # SubclassedError
        # with '__init_subclass__ = None', TypeError is thrown with message:
        # 'NoneType' object is not callable
    
    This class is a reference to local class `typing._Final`, with lack of necessity \\
    providing the `_root` keyword to inheritance section.
    """
    __slots__ = ("__weakref__",)

    def __init_subclass__(cls):
        cls = _InternalHelper(cls, "final")
       
    def __instancecheck__(self, instance: object):
        "@lifetime >= 0.3.27rc1. Check whether an object is instance to this class"
        return isinstance(instance, type(self))
    
    def __subclasscheck__(self, cls: type):
        "@lifetime >= 0.3.27rc1. Error is thrown, because this class may not be subclassed"
        _ch(_ih(11))
       
    def __mro_entries__(self):
        return None
    
    @property
    def __mro__(self):
        return None
    
    if False: # 0.3.28 (use finalmethod instead)
        @staticmethod
        def method(f: _T_func):
            """@lifetime >= 0.3.27rc2"""
            
            if _sys.version_info >= (3, 11):
                from typing import final as _f
                
            else:
                from typing_extensions import final as _f
                
            return _f(f)
    
def final(t: __.AVT_Type[_T], /): # <- 0.3.41 slash
    """
    @lifetime >= 0.3.26b3 \\
    https://aveyzan.xyz/aveytense#aveytense.util.final
    """
    t = _InternalHelper(t, "final")
    return t

def finalmethod(f: _T_func, /): # <- 0.3.41 slash
    """
    @lifetime >= 0.3.27rc2 \\
    https://aveyzan.xyz/aveytense#aveytense.util.finalmethod
    """
    if False:
        return Final.method(f)
    
    else:
        
        if isinstance(f, __.MethodType):
            return __.final(f)
        
        else:
            error = TypeError("expected a method")
            raise error
    
class classproperty(__.Generic[_T]):
    """
    @lifetime >= 0.3.43 \\
    *Experimental*
    
    Same as `@classmethod + @property` decorator combination, which was retracted on Python 3.13.
    """
    def __init__(
        self,
        fget: __.Optional[__.AVT_Callable[[__.Any], _T]] = None,
        fset: __.Optional[__.AVT_Callable[[__.Any, __.Any], None]] = None,
        fdel: __.Optional[__.AVT_Callable[[__.Any], None]] = None,
        doc: __.Optional[str] = None,
    ):
        
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or fget.__doc__
    
    def __str__(self):
        
        if self.fget is not None:
            return self.fget.__name__
        
        else:
            return "<anonymous>"
        
    def __repr__(self): # 0.3.44
        
        if self.fget is not None:
            return "<classproperty {}>".format(self.fget.__qualname__)
        
        else:
            return "<anonymous>"
    
    def __get__(self, instance, owner = None):
        
        if self.fget is None:
            error = TypeError("class property '{}' isn't readable".format(self.__str__()))
            raise error
        
        return self.fget(instance)
    
    def __set__(self, instance, value):
        
        if self.fset is None:
            error = TypeError("can't set a value to class property '{}'".format(self.__str__()))
            raise error
        
        self.fset(instance, value)
        
    def __delete__(self, instance):
        
        if self.fdel is None:
            error = TypeError("can't delete class property '{}'".format(self.__str__()))
            raise error
        
        self.fdel(instance)
        
    def getter(self, f: __.AVT_Callable[[__.Any], _T], /):
        
        if not callable(f) or f.__code__.co_argcount != 1 or f.__code__.co_kwonlyargcount != 0:
            error = TypeError("expected a callable with one parameter")
            raise error
        
        self.fget = f
        return type(self)(f, self.fset, self.fdel, f.__doc__ or self.__doc__)
        
    def setter(self, f: __.AVT_Callable[[__.Any, __.Any], None], /):
        
        if not callable(f) or f.__code__.co_argcount != 2 or f.__code__.co_kwonlyargcount != 0:
            error = TypeError("expected a callable with two parameters")
            raise error
        
        self.fset = f
        return type(self)(self.fget, f, self.fdel, self.__doc__)
    
    def deleter(self, f: __.AVT_Callable[[__.Any], None], /):
        
        if not callable(f) or f.__code__.co_argcount != 1 or f.__code__.co_kwonlyargcount != 0:
            error = TypeError("expected a callable with one parameter")
            raise error
        
        self.fdel = f
        return type(self)(self.fget, self.fset, f, self.__doc__)

# it is worth noticing that even if 'finalproperty' class doesn't formally inherit
# from 'property' builtin, it is considered a 'property' builtin anyway. reason it
# does is because of descriptor methods __get__, __set__ and __delete__
# 18.03.2025

class finalproperty(__.Generic[_T]):
    """
    @lifetime >= 0.3.37 \\
    https://aveyzan.xyz/aveytense#aveytense.util.finalproperty
    
    A decorator which creates a final (constant) property. \\
    This property cannot receive new values nor be deleted, what makes \\
    this property read-only. This class doesn't inherit from `property`, \\
    however, it returns a new property - just classified as final.
    
    To create static final properties it is advisable to use `~.finalpropertycontainer` (@lifetime >= 0.3.43) \\
    with parameter `_static_` set to `True`.
    
    Usage of `~.finalproperty` is as simple as `property` inbuilt decorator::
    
        from aveytense.util import finalproperty
        
        class R:
            
            @finalproperty
            def val(self):
                return 42
        
        print(R.val) # <finalproperty 'R.val'>
        print(R().val) # 42
    """
    
    def __init__(self, f: __.AVT_Callable[[__.Any], _T], /):
        
        if isinstance(f, staticmethod):
            f = f.__func__
        
        if not callable(f) or (f.__code__.co_argcount != 1 or f.__code__.co_kwonlyargcount != 0):
            error = TypeError("expected callable with one parameter, or attempt to create final static property with no parameters")
            raise error
        
        self.func = f
        self.__doc__ = f.__doc__
        
    def __str__(self):
        
        if _sys.version_info >= (0, 3, 44):
        
            return "<finalproperty '{}'>".format(self.func.__qualname__)
        
        else:
            
            return "<final-property '{}'>".format(self.func.__qualname__)
        
    @__.overload
    def __get__(self, instance: None, owner: __.Optional[type] = None) -> finalproperty[_T]: ...
    
    @__.overload
    def __get__(self, instance: __.Any, owner: __.Optional[type] = None) -> _T: ...
        
    def __get__(self, instance, owner = None):
        
        if instance is None:
            return self
        
        a = self.func(instance)
        return a
    
    def __set__(self, instance, value):
        
        v = self.func.__name__
        _E(122, v)
        
    def __delete__(self, instance):
        
        v = self.func.__name__
        _E(122, v)

if False: # >= 0.3.43
    
    class finalstaticproperty(__.Generic[_T]):
        
        def __init__(self, f: __.Callable[[], _T], /):
            
            if isinstance(f, staticmethod):
                f = f.__func__
            
            if not callable(f) or (f.__code__.co_argcount != 0 or f.__code__.co_kwonlyargcount != 0):
                error = TypeError("expected callable with no parameters")
                raise error
            
            self.func = f
            self.__name__ = f.__name__
            self.__doc__ = f.__doc__
            
        def __get__(self, instance, owner = None):
            
            if owner is not None and isinstance(owner, type(self)):
                return owner.func.__func__()
            
            return self.func.__func__()
        
        def __set__(self, instance, value):
            
            v = self.func.__name__
            _E(122, v)
            
        def __delete__(self, instance):
            
            v = self.func.__name__
            _E(122, v)

class finalpropertycontainer:
    """
    @lifetime >= 0.3.43 \\
    https://aveyzan.xyz/aveytense#aveytense.util.finalpropertycontainer
    
    Creates final properties much easier, using this decorator and keyword arguments as final property names and their values. Unlike \\
    for enumerator classes, this kind of classes need to be instiatiated in order to have effect. It has no effect if none of properties were \\
    defined (like mere invocation `~.finalpropertycontainer()`). It is recommended to use it instead of `~.finalproperty` decorator, \\
    as it may not work as intended. In this case it is better to use `~.FinalVar` class.
    
    Final properties are assigned to type's `__dict__` read-only attribute as mere inbuilt `property` class instances. If a class already \\
    has attributes, and `properties` keyword-only parameter contains some of their names, then these attributes are transformed to \\
    `property` class instances and are defined as final. Attributes receive values as defined in `properties` keyword-only parameter. \\
    It does not apply to properties nor any kind of methods.
    
    `_static_` in `properties` makes attributes look like in enumerator classes: accessible via reference (worth noticing class itself \\
    becomes an object of itself), so using it with `type()` will lose its meaning. All instance methods and properties are accessible \\
    via this 'class reference' (while it is its instance). In this case class cannot be marked abstract.
    
    Usage is simple::
    
        from aveytense.util import finalpropertycontainer
        
        @finalpropertycontainer(x = 65, y = True)
        class R:
            x = 16
        
        print(R().x, R().y) # 65 True
    """
    
    def __new__(cls, **properties): # 0.3.43
        
        def _internal(t: __.AVT_Type[_T], /):
            
            def _no_re(v):
                
                def _no_re_internal(i):
                    
                    nonlocal v
                    
                    if i == 2:
                        return lambda self, val: _E(122, v)
                
                    else:
                        return lambda self: _E(122, v)
                    
                return _no_re_internal
            
            _members, _properties = ({k for k in t.__dict__}, {k for k in properties if k != "_static_"})
            _new_dict = {"": StopIteration.value}
            del _new_dict[""]
            
            for member in _members:
                for property_ in _properties:
                    
                    _2 = _no_re(property_)(2)
                    _3 = _no_re(property_)(3)
                    
                    if member != property_:
                        
                        _1 = lambda self: properties[property_]
                        _new_dict[property_] = property(_1, _2, _3)
                        
                    else:
                        
                        # must be an attribute
                        if not isinstance(t.__dict__[member], (__.MethodType, property)):
                            
                            _1 = lambda self: t.__dict__[member]
                            _new_dict[property_] = property(_1, _2, _3)
                            
                    # if not this statement, values of each attributes would be randomized  
                    break 
            
            # normally 'dict' doesn't allow concatenating with +, so we need to create temporary 2 lists with 2-item tuples to convert them
            # to 'dict'
            _new_dict = dict(sorted([(k, t.__dict__[k]) for k in t.__dict__] + [(k, _new_dict[k]) for k in _new_dict], key = lambda x: x[0]))
            
            if "_static_" in properties and properties["_static_"] is True:
                
                # __new__ is revoked too, since it doesnt necessarily have to return class instance
                if "__new__" in _new_dict:
                    error = TypeError("static final properties do not require definition of __new__ method in the target class")
                    raise error
                
                _inspect_init = __.cast(__.Optional[__.AnyCallable], _new_dict.get("__init__"))
                
                if _inspect_init is not None and (_inspect_init.__code__.co_argcount != 1 or _inspect_init.__code__.co_kwonlyargcount != 0):
                    error = TypeError("when __init__ method is defined, expected argumentless (excluding first parameter) implementation of the method")
                    raise error
                
                try:
                    _new_type = __.cast(__.AVT_Type[_T], type(t.__name__, t.__bases__, _new_dict)())
                    
                except:
                    
                    try:
                        _new_type = __.cast(__.AVT_Type[_T], __.new_class(t.__name__, t.__bases__, _new_dict)())
                        
                    except:
                        
                        error = TypeError("cannot define static final attributes while the class is abstract")
                        raise error
            
            else:
                # one of these must be invoked
                try:
                    _new_type = __.cast(__.AVT_Type[_T], type(t.__name__, t.__bases__, _new_dict))
                    
                except:
                    _new_type = __.cast(__.AVT_Type[_T], __.new_class(t.__name__, t.__bases__, _new_dict))
                
            t = _new_type
            return t
        
        return _internal

class FinalVar:
    """
    @lifetime >= 0.3.26rc1 \\
    @experimental >= 0.3.26rc1; < 0.3.35
    
    To 0.3.35 this class was in `aveytense.types_collection`. This class formalizes a final variable. On 0.3.35 all ways to get the value \\
    (expect with unary `+`) has been replaced with `x` attribute access. Hence you use the following: `instance.x`.
    """
    
    def __new__(cls, value: _T, /):
        
        return _FinalVar(value)
    
    def __init_subclass__(cls):
        
        def _tmp(cls: __.AVT_Type[__.Self], value: _T, /):
        
            return _FinalVar(value)
        
        cls.__new__ = _tmp
        
FinalVarType = _FinalVar # 0.3.38; see ~.Tense.isFinalVar()

if False: # < 0.3.52
    @final
    class ClassLike(__.Generic[_P, _T]):
        """
        @lifetime >= 0.3.27a3
        
        To 0.3.35 this class was in `aveytense.types_collection`. \\
        A class decorator for functions, transforming them to declarations \\
        similar to classes. Example::
        
            @ClassLike
            def test():
                return 42

            a = test() # returns 42

        """
        def __init__(self, f: __.AVT_Callable[_P, _T]):
            self.f = f
            
        def __call__(self, *args: _P.args, **kwds: _P.kwargs):
            return self.f(*args, **kwds)
        
    classlike = ClassLike # since 0.3.27a3
        
AbstractMeta = _abc.ABCMeta
"""
@lifetime >= 0.3.27b1. Use it as::
```
class AbstractClass(metaclass = AbstractMeta): ...
```
"""

class AbstractFinal:
    """
    @lifetime >= 0.3.27rc1 \\
    https://aveyzan.xyz/aveytense#aveytense.util.AbstractFinal
    
    Creates an abstract-final class. Typically blend of `Abstract` and `Final` classes \\
    within submodule `aveytense.util`. Classes extending this class are \\
    only restricted to modify fields (as in `TenseOptions`) or invoke static methods, \\
    because they cannot be neither initialized nor inherited.
    """
    __slots__ = ("__weakref__",)
    
    def __init__(self):
        _ch(_ih(20))
    
    def __init_subclass__(cls):
        cls = _InternalHelper(cls, "abstract")
        cls = _InternalHelper(cls, "final")
       
    def __mro_entries__(self):
        return None
    
    @property
    def __mro__(self):
        return None
    
    def __instancecheck__(self, instance: object):
        "@lifetime >= 0.3.27rc1. Error is thrown, because class may not be instantiated"
        _ch(_ih(21))
    
    def __subclasscheck__(self, cls: type):
        "@lifetime >= 0.3.27rc1. Error is thrown, because class may not be subclassed"
        _ch(_ih(11))

class FinalFrozen:
    """
    @lifetime >= 0.3.27rc1
    
    Creates a final-frozen class. Typically blend of `Final` and `Frozen` classes \\
    within submodule `aveytense.util`. Classes extending this class cannot \\
    be further extended nor have fields modified by their objects.
    """
    __slots__ = ("__weakref__",)
    
    def __init_subclass__(cls):
        cls = _InternalHelper(cls, "final")
        cls = _InternalHelper(cls, "frozen")
       
    def __instancecheck__(self, instance: object):
        "@lifetime >= 0.3.27rc1. Check whether an object is instance to this class"
        return isinstance(instance, type(self))
    
    def __subclasscheck__(self, cls: type):
        "@lifetime >= 0.3.27rc1. Error is thrown, because this class may not be subclassed"
        _ch(_ih(11))
       
    def __mro_entries__(self):
        return None
    
    @property
    def __mro__(self):
        return None  

class AbstractFrozen:
    """
    @lifetime >= 0.3.27rc1
    
    Creates an abstract-frozen class. Typically blend of `Abstract` and `Frozen` classes \\
    within submodule `aveytense.util`. Classes extending this class cannot \\
    be initialized, nor have their fields modified. During experiments
    
    Possible way to end the experiments would be:
    - extending `enum.Enum` and overriding only some of its declarations, such as `__new__` method
    - extending `type` and raising error in `__setattr__` and `__delattr__`
    - creating private dictionary which will store class names as keys and fields as values, further \\
        used by both pre-mentioned methods
    """
    __slots__ = ()
    
    def __init_subclass__(cls):
        
        def _no_init(self: __.Self):
            _ch(_ih(2))
        
        cls = abstract(frozen(cls))
        
        if cls.__init__.__code__ is not _no_init.__code__:
           error = LookupError("cannot remake __init__ method code on class " + cls.__name__)
           raise error
        
    def __instancecheck__(self, instance: object):
        "@lifetime >= 0.3.27rc1. Error is thrown, because class may not be instantiated"
        _E(115, type(self).__name__)
        
    def __subclasscheck__(self, cls: type):
        "@lifetime >= 0.3.27rc1. Check whether a class is a subclass of this class"
        return issubclass(cls, type(self))


class SortedList(__.Generic[_T]):
    """
    @lifetime >= 0.3.35
    
    Creates a sorted list. Note this class doesn't inherit from `list` builtin itself.
    """
    
    def __init__(self, i: __.AVT_Iterable[_T], /, key: __.Optional[__.AVT_Callable[[_T], _RichComparable]] = None, reverse = False): # 0.3.35
        
        if not isinstance(i, __.Iterable):
            
            error = ValueError("expected an iterable")
            raise error
        
        self.__l = self.__sorted = [e for e in i]
        self.__sorted.sort(key = key, reverse = reverse)
        
    
    def __iter__(self): # 0.3.35
        
        return iter(self.__sorted)
    
    
    def __len__(self): # 0.3.35
        
        return _reckon(self.__sorted)
    
    
    def __getitem__(self, index: int, /): # 0.3.35
        
        return self.__sorted[index]
    
    
    def __contains__(self, item: _T, /): # 0.3.35
        
        return item in self.__sorted
    
    
    def __eq__(self, other, /): # 0.3.35
        
        return type(other) is type(self) and list(self) == list(other)
    
    
    def __ne__(self, other, /): # 0.3.35
        
        return (type(other) is not type(self)) or self.__eq__(other)
        
        
    def __str__(self): # 0.3.35
        
        return "{}({})".format(type(self).__name__, _reckon(self.__l))
    
    
    def __repr__(self): # 0.3.35
        
        return "<{}.{} object: {}>".format(self.__module__, type(self).__name__, self.__str__())
        
        
    def reverse(self, v = False, /):
        """@lifetime >= 0.3.35"""
        
        if v:
            self.__sorted.reverse()
            
            
    def setKey(self, v: __.Optional[__.AVT_Callable[[_T], _RichComparable]] = None, /):
        """@lifetime >= 0.3.35"""
        
        self.__sorted = self.__l
        if v is not None:
            self.__sorted.sort(key = v)
            
def all(name: str = "all", mode: __.Union[_AllMode, __.AVT_Callable[[str], bool]] = "clear", deprecatedInclude: bool = False, deprecatedName: __.Optional[str] = None):
    """
    @lifetime >= 0.3.53
    
    Creates `__all__` or user named attribute for target class as a decorator to store its names in a string list. \\
    This decorator is unrealized concept from 0.3.41
    
    Parameters
    
    - `name`: The name of the attribute that will store the names. Whitespaces around it then underscores around it \\
        are removed from the given name, and `name` becomes a dunder attribute for the type, that is: `__<name>__`
    - `mode`: Either a name of a mode as a string or a callable object with one parameter. Default value is `"clear"` \\
        that retrieves all names without even single underscore preceding
    - `deprecatedInclude`: If set to `True`, given type will receive a dunder attribute for deprecated definitions no \\
        matter the letter case or presence of underscores before or/and after.
    - `deprecatedName`: Only takes place when `deprecatedInclude` is set to `True`. If `None` or empty string, then \\
        attribute for deprecated definitions is `__<name>_deprecated__`, otherwise it is `__<deprecatedName>__`. Same
        actions about the name are performed as with `name` parameter
    """
        
    def _internals(t: __.AVT_Type[_T], /):
        
        if not isinstance(t, type):
            error = TypeError("expected a class")
            raise error
        
        nonlocal name, mode, deprecatedInclude, deprecatedName
        
        if not isinstance(name, str):
            error = TypeError("the 'name' parameter must be a string")
            raise error
        
        if not isinstance(deprecatedInclude, bool):
            error = TypeError("the 'name' parameter must be a boolean value")
            raise error
        
        if not isinstance(deprecatedName, (str, __.NoneType)):
            error = TypeError("the 'deprecatedName' parameter must be a string or 'None'")
            raise error
    
        _dict_ = dict(t.__dict__) # 'mappingproxy', hence we convert to 'dict'
        
        if name.strip().strip("_"):
            _name_ = "__{}__".format(name.strip().strip("_"))
        else:
            error = TypeError("expected at least one char not being underscore and whitespace")
            raise error
        
        if mode == "clear":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if not k.startswith("_")]) })
            
        elif mode == "lowercased":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.islower()]) })
            
        elif mode == "lowercased_clear":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.islower() and not k.startswith("_")]) }) 
            
        elif mode == "uppercased":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.isupper()]) })
            
        elif mode == "uppercased_clear":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.isupper() and not k.startswith("_")]) })
            
        elif mode == "sunder":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if (k.startswith("_") and not k.startswith("__")) and (k.endswith("_") and not k.endswith("__"))]) })
            
        elif mode == "lowercased_sunder":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.islower() and (k.startswith("_") and not k.startswith("__")) and (k.endswith("_") and not k.endswith("__"))]) })
            
        elif mode == "uppercased_sunder":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.isupper() and (k.startswith("_") and not k.startswith("__")) and (k.endswith("_") and not k.endswith("__"))]) })
            
        elif mode == "dunder":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.startswith("__") and k.endswith("__")]) })
            
        elif mode == "lowercased_dunder":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.islower() and k.startswith("__") and k.endswith("__")]) })
            
        elif mode == "uppercased_dunder":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.isupper() and k.startswith("__") and k.endswith("__")]) })
            
        elif mode == "protected":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.startswith("_") and not k.endswith("_")]) })
            
        elif mode == "lowercased_protected":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.islower() and k.startswith("_") and not k.endswith("_")]) })
            
        elif mode == "uppercased_protected":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.isupper() and k.startswith("_") and not k.endswith("_")]) })
            
        elif mode == "private":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.startswith("__") and not k.endswith("__")]) })
            
        elif mode == "lowercased_private":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.islower() and k.startswith("__") and not k.endswith("__")]) })
            
        elif mode == "uppercased_private":
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if k.isupper() and k.startswith("__") and not k.endswith("__")]) })
            
        elif callable(mode) and mode.__code__.co_argcount == 1 and mode.__defaults__ is None:
            _dict_.update({ _name_: sorted([k for k in t.__dict__ if mode(k) ]) })
            
        else:
            error = TypeError("invalid mode, expected callable object with one parameter or a string value from the following: " + str(_AllMode.__args__[0].__args__)[1:-1])
            raise error
        
        if deprecatedInclude:
            
            if deprecatedName and deprecatedName.strip().strip("_"):
                _deprecated_name_ = "__{}__".format(deprecatedName.strip().strip("_"))
                
            else:
                _deprecated_name_ = "__{}_deprecated__".format(_name_.strip().strip("_"))
            
            _dict_.update({ _deprecated_name_: sorted([k for k in t.__dict__ if hasattr(t.__dict__[k], "__deprecated__") or isinstance(t.__dict__[k], __.deprecated)]) })
        
        return __.cast(__.AVT_Type[_T], type(t.__name__, t.__bases__, _dict_))
    
    return _internals

if False:
    class All:
        """
        @since 0.3.41 (in-code)
        
        A special class featuring `__all__` variable for all its subclasses. Experimental
        """
        
        def __new__(cls, handler: __.Callable[[], __.Union[dict[str, __.Any], __.MappingProxyType[str, __.Any]]] = locals, mode = "public"):
            
            from re import match as _match
            from inspect import getfullargspec
            
            if not callable(handler) or _reckon(getfullargspec(handler).args) != 0:
                error = TypeError("expected a callable without arguments")
                raise error
            
            __all__ = sorted([k for k in handler() if not k.startswith("_")])
            
            if mode == "normal": # everything provided
                __all__ = sorted([k for k in handler()])
                    
            elif mode == "non-private": # no double underscore preceding
                __all__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "non-protected": # no single underscore preceding
                __all__ = sorted([k for k in handler() if _match(r"^_[^_]+$", k) is not None])
            
            elif mode == "non-public": # no matter how many underscores preceding
                __all__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "non-sunder": # no single underscores around
                __all__ = sorted([k for k in handler() if _match(r"^_[^_]+_$", k) is None])
                
            elif mode == "non-dunder": # no double underscores around
                __all__ = sorted([k for k in handler() if _match(r"^__[^_]+__$", k) is None])    
                
            elif mode == "non-underscored": # chars other than underscore
                __all__ = sorted([k for k in handler() if _match(r"^_+$", k) is None])
                
            elif mode == "private": # two or more underscores preceding
                __all__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "protected": # single underscore preceding
                __all__ = sorted([k for k in handler() if _match(r"^_[^_]+$", k) is not None])
                
            elif mode == "public": # no underscores preceding
                __all__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is None])
                
            elif mode == "sunder": # one underscore around
                __all__ = sorted([k for k in handler() if _match(r"^_[^_]+_$", k) is not None])
                
            elif mode == "dunder": # two underscores around
                __all__ = sorted([k for k in handler() if _match(r"^__[^__]+__$", k) is not None])
                
            elif mode == "underscored": # no other chars than underscore
                __all__ = sorted([k for k in handler() if _match(r"^_+$", k) is not None])
                
            else:
                error = TypeError("expected a valid mode")
                raise error
            
            return __all__
        
        @classmethod
        def deprecated(self, handler: __.Callable[[], __.Union[dict[str, __.Any], __.MappingProxyType[str, __.Any]]] = locals, mode = "public"):
            """
            @since 0.3.41
            
            All deprecated declarations. Use as::
            
                __all_deprecated__ = All.deprecated()
            """
            
            from re import match as _match
            from inspect import getfullargspec
            
            if not callable(handler) or _reckon(getfullargspec(handler).args) != 0:
                error = TypeError("expected a callable without arguments")
                raise error
            
            __all_deprecated__ = sorted([k for k in handler() if not k.startswith("_") and hasattr(handler()[k], "__deprecated__")])
            
            if mode == "normal": # everything provided
                __all_deprecated__ = sorted([k for k in handler()])
                    
            elif mode == "non-private": # no double underscore preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "non-protected": # no single underscore preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
            
            elif mode == "non-public": # no matter how many underscores preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "non-sunder": # no single underscores around
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_[^_]+_$", k) is None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "non-dunder": # no double underscores around
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^__[^_]+__$", k) is None and hasattr(handler()[k], "__deprecated__")])    
                
            elif mode == "non-underscored": # chars other than underscore
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_+$", k) is None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "private": # two or more underscores preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "protected": # single underscore preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_[^_]+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "public": # no underscores preceding
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_(_)+[^_]+$", k) is None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "sunder": # one underscore around
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_[^_]+_$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "dunder": # two underscores around
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^__[^__]+__$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            elif mode == "underscored": # no other chars than underscore
                __all_deprecated__ = sorted([k for k in handler() if _match(r"^_+$", k) is not None and hasattr(handler()[k], "__deprecated__")])
                
            else:
                error = TypeError("expected a valid mode")
                raise error
            
            return __all_deprecated__
                
    # override builtins.all()
    def all(mode = "public", deprecated = False):
        """
        @unavailable >= 0.3.41
        
        As a decorator, defines `__all__` variable in specific class. Possible modes (case sensitive):
        - `"normal"` - gets all members, no matter the status.
        - `"private"` - gets all private members that aren't dunder.
        - `"protected"` - gets all protected members that aren't private, sunder and dunder.
        - `"public"` (default value) - gets all public members. This also includes sunder and dunder members.
        - `"sunder"` - gets all sunder (single-underscored) members.
        - `"dunder"` - gets all dunder (doubly-underscored) members.
        - `"non-private"` - gets all non-private members. This list features public, protected, sunder and dunder members.
        - `"non-protected"` - gets all non-protected members. This list features public, private, sunder and dunder members.
        - `"non-public"` - gets all non-public members. This list features private and protected members only.
        - `"non-sunder"` - gets all non-sunder members. This list features public, protected, private and dunder members.
        - `"non-dunder"` - gets all non-dunder members. This list features public, protected, private and sunder members.
        
        There are also some discouraging modes:
        - `"underscored"` - gets all members whose names are created with underscores only (like `__`).
        - `"non-underscored"` - gets all members whose names aren't created with underscores only. This list features \\
            all public, protected, private, sunder and dunder methods, what means its very similar to `"normal"`.
            
        Use as::
        
            @~.util.all("<mode>") # valid value from above except <mode> or leave it empty,
            # as ~.util.all()
            class Test: ... # members
        
        In this example, `Test.__all__` will normally obtain all public members.
        """
        
        def _all(t: __.AVT_Type[_T], /):
            
            from re import match as _match
            
            if not isinstance(t, type):
                error = TypeError("expected a class or type alias")
                raise error
            
            v = t.__dict__
            t = __.cast(__.AVT_Type[_T], t)
            t.__all__ = sorted([k for k in v if not k.startswith("_")])
            
            if mode == "normal": # everything provided
                t.__all__ = sorted([k for k in v])
                    
            elif mode == "non-private": # no double underscore preceding
                t.__all__ = sorted([k for k in v if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "non-protected": # no single underscore preceding
                t.__all__ = sorted([k for k in v if _match(r"^_[^_]+$", k) is not None])
            
            elif mode == "non-public": # no matter how many underscores preceding
                t.__all__ = sorted([k for k in v if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "non-sunder": # no single underscores around
                t.__all__ = sorted([k for k in v if _match(r"^_[^_]+_$", k) is None])
                
            elif mode == "non-dunder": # no double underscores around
                t.__all__ = sorted([k for k in v if _match(r"^__[^_]+__$", k) is None])    
                
            elif mode == "non-underscored": # chars other than underscore
                t.__all__ = sorted([k for k in v if _match(r"^_+$", k) is None])
                
            elif mode == "private": # two or more underscores preceding
                t.__all__ = sorted([k for k in v if _match(r"^_(_)+[^_]+$", k) is not None])
                
            elif mode == "protected": # single underscore preceding
                t.__all__ = sorted([k for k in v if _match(r"^_[^_]+$", k) is not None])
                
            elif mode == "public": # no underscores preceding
                t.__all__ = sorted([k for k in v if _match(r"^_(_)+[^_]+$", k) is None])
                
            elif mode == "sunder": # one underscore around
                t.__all__ = sorted([k for k in v if _match(r"^_[^_]+_$", k) is not None])
                
            elif mode == "dunder": # two underscores around
                t.__all__ = sorted([k for k in v if _match(r"^__[^__]+__$", k) is not None])
                
            elif mode == "underscored": # no other chars than underscore
                t.__all__ = sorted([k for k in v if _match(r"^_+$", k) is not None])
                
            else:
                error = TypeError("expected a valid mode")
                raise error
            
            if deprecated:
                t.__all_deprecated__ = sorted([n for n in vars(t) if hasattr(vars(t)[n], "__deprecated__")])
                
            t.__all__ = [e for e in t.__all__ if e != "__all__"]
            return t
                
        return _all
    
_builtin_classes = (int, float, complex, filter, memoryview, bytearray, bytes, str, slice, map, range, bool, list, tuple, set, frozenset, dict, object, reversed, enumerate, zip)

class _ParamNoDefault(Abstract):
    """
    @lifetime >= 0.3.51
    
    Used to denote parameters without default value with final \\
    properties ending with `withDefaults` suffix, in `~.util.ParamVar`.
    """
    
class _BuiltinParamVar:
    """
    @lifetime >= 0.3.51
    
    Used in `~.util.ParamVar` to receive parameters from inbuilt functions. \\
    Noteworthy none of these have annotations.
    """
    
    def __init__(self, f):
        
        if not isinstance(f, (
            __.BuiltinFunctionType,
            __.ClassMethodDescriptorType,
            __.MethodDescriptorType,
            __.MethodWrapperType,
            __.WrapperDescriptorType 
        )):
            error = TypeError("provided object is not a builtin")
            raise error
        
        if _sys.version_info >= (3, 9): # 0.3.53: see PEP 616
            _remove_prefix_ = lambda x = "", prefix = "": x.removeprefix(prefix)
            _remove_suffix_ = lambda x = "", suffix = "": x.removesuffix(suffix)
            
        else:
            _remove_prefix_ = lambda x = "", prefix = "": x[_reckon(prefix):] if x.startswith(prefix) else x[:]
            _remove_suffix_ = lambda x = "", suffix = "": x[:_reckon(suffix)] if suffix and x.endswith(suffix) else x[:]
        
        # 0.3.51
        # If only we were able to do much...
        # Inbuilt functions are supported, but question beg inbuilt methods, which in most
        # cases return signature (*args, **kwargs) with no useful signature information.
        _unsanitized_signature_ = getattr(f, "__text_signature__", None)
        _SPACES_ = " " * 0b111
        
        if type(_unsanitized_signature_) is str:
            
            def _await_comma(s = ""):
                
                s2 = ""
                
                for c in s:
                    
                    s2 += c
                    
                    if c == ",":
                        break
                    
                return _reckon(s2)  
            
            _revoke_first_ = _unsanitized_signature_[: _await_comma(_unsanitized_signature_) + 1]
            
            _signature_ = _remove_prefix_(_remove_prefix_(_unsanitized_signature_,  _revoke_first_), "/, ").replace("\n" + _SPACES_, "")
            _signature2_ = _remove_suffix_(_signature_, ")").split(", ")
            
            self.__signature = _signature_ 
            self.__gleaned_params = list(filter(lambda x: _reckon(x) > 0, _signature2_))
            
        else:
            error = TypeError("unable to retrieve signature")
            raise error
        
    @finalproperty
    def signature(self): # 0.3.51
        
        return "(" + self.__signature.replace("=", " = ")
        
    @finalproperty
    def all(self): # 0.3.51
        
        return tuple([_param_sanitize(p) for p in self.__gleaned_params if p not in ("/", "*")])
        
    @finalproperty
    def allDefaults(self): # 0.3.51
        
        _return_ = [("", StopIteration.value)]
        _return_.clear()
        _return_.extend([(_param_sanitize(p), p[_reckon(_param_sanitize(p, True)):]) for p in self.__gleaned_params if _param_sanitize(p, True).endswith("=")])
        return tuple(_return_)
    
    @finalproperty
    def allWithDefaults(self): # 0.3.51
        
        return tuple([(p, _ParamNoDefault if p not in dict(self.allDefaults) else dict(self.allDefaults)[p]) for p in self.all])
    
    @finalproperty
    def allNoDefaults(self): # 0.3.51
        
        return tuple([p for p in self.all if p not in dict(self.allDefaults)])
    
    @finalproperty
    def positional(self): # 0.3.51
        
        _return_ = [""]
        _return_.clear()
        
        for p in self.__gleaned_params:
            
            # pre-pep 570
            if p == "/" or ("/" not in self.__gleaned_params and not p.endswith("__")):
                break
            
            _return_.append(p)
            
        return tuple(_return_)
    
    @finalproperty
    def positionalDefaults(self): # 0.3.51
        
        return tuple([p for p in self.allDefaults if p[0] in self.positional])
    
    @finalproperty
    def positionalWithDefaults(self): # 0.3.51
        
        return tuple([(p, _ParamNoDefault if p not in dict(self.positionalDefaults) else dict(self.positionalDefaults)[p]) for p in self.positional])
    
    @finalproperty
    def positionalNoDefaults(self): # 0.3.51
        
        return tuple([p for p in self.positional if p not in dict(self.positionalDefaults)])
    
    @finalproperty
    def keyword(self): # 0.3.51
        
        _marker_ = 0
        
        for p in self.__gleaned_params:
            
            # either * or *<param-name>
            if p.startswith("*"):
                break
            
            _marker_ += 1
            
        return tuple([_param_sanitize(p) for p in self.__gleaned_params[_marker_:] if not p.startswith("**")])
    
    @finalproperty
    def keywordDefaults(self): # 0.3.51
        
        return tuple([p for p in self.allDefaults if p[0] in self.keyword])
    
    @finalproperty
    def keywordWithDefaults(self): # 0.3.51
        
        return tuple([(p, _ParamNoDefault if p not in dict(self.keywordDefaults) else dict(self.keywordDefaults)[p]) for p in self.keyword])
    
    @finalproperty
    def keywordNoDefaults(self): # 0.3.51
        
        return tuple([p for p in self.keyword if p not in dict(self.keywordDefaults)])
    
    @finalproperty
    def universal(self): # 0.3.51
        
        return tuple([p for p in self.all if p not in (*self.positional, *self.keyword) and not p.startswith(("*", "/"))])
    
    @finalproperty
    def universalDefaults(self): # 0.3.51
        
        return tuple([p for p in self.allDefaults if p[0] in self.universal])
    
    @finalproperty
    def universalWithDefaults(self): # 0.3.51
        
        return tuple([(p, _ParamNoDefault if p not in dict(self.universalDefaults) else dict(self.universalDefaults)[p]) for p in self.universal])
    
    @finalproperty
    def universalNoDefaults(self): # 0.3.51
        
        return tuple([p for p in self.universal if p not in dict(self.universalDefaults)])
    
    @finalproperty
    def variable(self): # 0.3.51
        
        _return_ = [("", "")]
        _return_.clear()
        
        for p in self.__gleaned_params:
            
            if p.startswith("**"):
                _return_.append((_param_sanitize(p), "<args>"))
                
            elif p.startswith("*") and p != "*":
                _return_.append((_param_sanitize(p), "<kwargs>"))
                
        return tuple(_return_)
    
class ParamVar:
    """
    @lifetime >= 0.3.42 \\
    @unavailable >= 0.3.33; < 0.3.42 \\
    https://aveyzan.xyz/aveytense#aveytense.util.ParamVar
    
    Reference to `inspect.FullArgSpec`, and enriched version \\
    of the same class. Allows to obtain positional, universal, \\
    keyword (and their default values) and variable (`*<param>` \\
    and `**<param>`) arguments, and signature of a callable \\
    object.
    
    *Constructor general information* \\
    If `f` is overloaded function, used is `i` index to denote \\
    specific signature. `f` must be any callable object
    """
    
    def __init__(self, f: __.AVT_Callable[..., __.Any], i = 0, /): # 0.3.42
        
        # Revamp 0.3.51. Sadly, inbuilt functions do not feature the __code__ attribute, what would be easier.
        _overloads_ = None
        
        if _check_if_callable(f) or isinstance(getattr(f, "__code__", None), __.CodeType):
            
            # AttributeError is thrown when trying to access non-overloaded functions, or overloaded, but without the __module__ attribute
            try:
                _overloads_ = __.get_overloads(f)
                
            except AttributeError:
                _overloads_ = None
            
            if not isinstance(i, int) or (_overloads_ is not None and _reckon(_overloads_) > 0 and i not in range(_reckon(_overloads_))):
                error = TypeError("expected an integer in second parameter. keep this parameter as-is, when function isn't overloaded." + \
                                "otherwise, ensure the parameter value is in range <0; overloads_length>. " + \
                                "this does not apply to inbuilt functions")
                raise error
            
            if _check_if_builtin(f) or not isinstance(getattr(f, "__code__", None), __.CodeType):
                
                try:
                    self.__builtin = _BuiltinParamVar(f)
                    
                except TypeError:
                    error = TypeError("expected a callable object with a proper implementation. with type as value use '~.util.ParamVar.fromType()' static method")
                    raise error
                
            else:
                self.__builtin = None
                
        else:
            error = TypeError("expected a callable object with a proper implementation")
            raise error
        
        self.__vartype = ""
        
        if isinstance(f, __.partial):
            self.__func = f.func
            
        elif _overloads_ is not None and _reckon(_overloads_) > 0:
            self.__func = __.cast(__.AVT_Callable[..., __.Any], _overloads_[i])
            
        else:
            self.__func = f
        
        func = f.func if isinstance(f, __.partial) else f
        
        # 0.3.51: Less complexity in this statement. __name__ != __qualname__ is required to deduce if a function belongs to a class as an instance method,
        # passed to the constructor via class reference. If __name__ equals __qualname__, then function doesn't belong to a class and is in globally scope.
        if (isinstance(func, __.MethodType) and not isinstance(func, staticmethod)) or isinstance(func, __.MethodDescriptorType) or (isinstance(func, __.FunctionType) and func.__name__ != func.__qualname__):
            self.__no_first = 1
        
        else:
            self.__no_first = 0
        
    def __str__(self): # 0.3.42
        
        # 0.3.51
        if self.__builtin is not None:
            _annotated_ = ("?", "?")
        else:
            _annotated_ = (str(self.annotatedCount), str(self.annotatedDefaultsCount)) # >= 0.3.44
        
        return "{}(positional: {}, positionalDefaults: {}, universal: {}, universalDefaults: {}, keyword: {}, keywordDefaults: {}, annotated: {}, annotatedDefaults: {}, variable: {}, all: {}, allDefaults: {})".format(
            type(self).__name__,
            self.positionalCount,
            self.positionalDefaultsCount,
            self.universalCount,
            self.universalDefaultsCount,
            self.keywordCount,
            self.keywordDefaultsCount,
            _annotated_[0],
            _annotated_[1], 
            str(self.variableCount) + self.__vartype,
            self.allCount,
            self.allDefaultsCount
        )
        
    def __repr__(self): # 0.3.42
        
        return "<{}.{} object :: {} :: Inspected function -> {}>".format(self.__module__, type(self).__name__, self.__str__(), self.func.__qualname__)
    
    @staticmethod
    def fromType(t, i = 0, /):
        """
        @lifetime >= 0.3.51
        
        Alternative constructor for `~.util.ParamVar`
        """
        
        if isinstance(t, _builtin_classes) or (type(t) is type and hasattr(t, "__new__")):
            return ParamVar(t.__new__, i)
        
        elif type(t) is type and hasattr(t, "__init__"):
            return ParamVar(t.__init__, i)
        
        else:
            error = TypeError("unable to retrieve a function from desired type")
            raise error
    
    @property
    def func(self): # 0.3.42
        """
        @lifetime >= 0.3.42
        
        Represents the function passed to the constructor
        """
        
        return self.__func
    
    @func.setter
    def func(self, v): # 0.3.42
        
        type(self).__init__(self, v)
        
    @func.deleter
    def func(self): # 0.3.43
        
        error = TypeError("unable to delete property {}".format(self.func.__name__))
        raise error
    
    @finalproperty
    def builtin(self):
        """
        @lifetime >= 0.3.52
        
        Returns `True` if function is inbuilt.
        """
        return self.__builtin is not None
    
    @finalproperty
    def signature(self): # 0.3.42
        """
        @lifetime >= 0.3.42 \\
        https://aveyzan.xyz/aveytense#aveytense.util.ParamVar.signature
        
        Returns function's signature
        """
        
        if _sys.version_info >= (0, 3, 44):
            
            # 0.3.51
            if self.__builtin is not None:
                return self.__builtin.signature
            
            _signature_ = "("
            
            # inverting keys and values pairs, because <args> and <kwargs> are normally values (not keys) in dictionary (in tuples: second item)
            # trick with indexes may be needed - whether ~.variable is empty, indexes aren't accessed
            _variable_ = {e[1]: e[0] for e in self.variable}
            
            # on terminals quotes are omitted, so we will be including them to indicate these values are strings
            # 0.3.45: + present ellipsis as '...'
            _quote_ = lambda x: "..." if x is ... else str(x) if type(x) is not str else "\"{}\"".format(x)
            
            # 0.3.47, 0.3.49
            # doing it with __future__.annotations and values of globals() is not preferred idea
            # better catch the error when subscripting
            _quoted_annotations_ = False
            
            if _sys.version_info < (3, 9):
                
                from collections.abc import Sequence
                
                try:
                    _e_ = Sequence[str] # type: ignore
                    _e_ = _e_
                    
                except:
                    _quoted_annotations_ = True
            
            # 0.3.47: Faster to do it than do the same with dict(~.annotations). 'True' and 'False' cannot be deduced in type annotation, they need use with
            # typing.Literal, hence ... if self...get(x, False)
            # 0.3.52: Un-stringify type annotations
            # 0.3.53: Check whether 'globals' in eval() can be passed as a keyword
            
            if True: # >= 0.3.52
                
                if _sys.version_info >= (3, 13):
                    if not _quoted_annotations_:
                        _receive_annotation_ = lambda x = "": ": " + str(eval(self.func.__annotations__[x], globals = self.func.__globals__)) if self.func.__annotations__.get(x, False) is not False else ""
                    else:
                        _receive_annotation_ = lambda x = "": ": \"{}\"".format(str(eval(self.func.__annotations__[x], globals = self.func.__globals__))) if self.func.__annotations__.get(x, False) is not False else ""
                    
                else:
                    if not _quoted_annotations_:
                        _receive_annotation_ = lambda x = "": ": " + str(eval(self.func.__annotations__[x], self.func.__globals__)) if self.func.__annotations__.get(x, False) is not False else ""
                    else:
                        _receive_annotation_ = lambda x = "": ": \"{}\"".format(str(eval(self.func.__annotations__[x], self.func.__globals__))) if self.func.__annotations__.get(x, False) is not False else ""
            
            else:
                if not _quoted_annotations_:
                    _receive_annotation_ = lambda x = "": ": " + str(self.func.__annotations__[x]) if self.func.__annotations__.get(x, False) is not False else ""
                else:
                    _receive_annotation_ = lambda x = "": ": \"{}\"".format(str(self.func.__annotations__[x])) if self.func.__annotations__.get(x, False) is not False else ""
            
            # 0.3.48
            # Fixed annotations (these only applied to parameters with default value)
            
            # pep 570, Py>=3.8
            if self.positionalCount > 0:
                
                _positional_defaults = dict(self.positionalDefaults)
                _annotations_ = [e + _receive_annotation_(e) + (" = " + _quote_(_positional_defaults[e]) if e in _positional_defaults else "") for e in self.positional]
                
                _signature_ += ", ".join(_annotations_) + ", /, "
                
            if self.universalCount > 0:
                
                _universal_defaults = dict(self.universalDefaults)
                _annotations_ = [e + _receive_annotation_(e) + (" = " + _quote_(_universal_defaults[e]) if e in _universal_defaults else "") for e in self.universal]
                
                _signature_ += ", ".join(_annotations_) + ", "
                
            if "<args>" in _variable_:
                
                if not _signature_.endswith(", ") and self.positionalCount > 0: # >= 0.3.45
                    _signature_ += ", "
                
                _signature_ += "*{}, ".format(_variable_["<args>"] + _receive_annotation_(_variable_["<args>"]))
            
            # pep 3102, Py>=3.0
            if self.keywordCount > 0:
                
                _keyword_defaults = dict(self.keywordDefaults)
                _annotations_ = [e + _receive_annotation_(e) + (" = " + _quote_(_keyword_defaults[e]) if e in _keyword_defaults else "") for e in self.keyword]
                
                if "<args>" not in _variable_:
                    _signature_ += "*, "
                    
                _signature_ += ", ".join(_annotations_)
                
            if "<kwargs>" in _variable_:
                
                if not _signature_.endswith(", ") and (any([e > 0 for e in (self.positionalCount, self.universalCount, self.keywordCount)]) or "<args>" in _variable_):
                    _signature_ += ", "
                
                _signature_ += "**{}, ".format(_variable_["<kwargs>"] + _receive_annotation_(_variable_["<kwargs>"]))
            
            if _signature_.endswith(", "):
                _signature_ = _signature_[: _reckon(_signature_) - 2]
                
            _signature_ += ")"
            
            # 0.3.48
            # Return type annotation
            _return_ = dict(self.annotations).get("return", False)
            
            if _return_ is not False:
                _signature_ += " -> {}".format(_return_)
            
        else:
        
            import inspect, re
            
            _signature_ = str(inspect.signature(self.func))
            _signature_ = re.sub(r"=", " = ", _signature_)
            
        return _signature_
        
    @finalproperty
    def all(self): # 0.3.42
        """
        @lifetime >= 0.3.42 \\
        https://aveyzan.xyz/aveytense#aveytense.util.ParamVar.all
        
        Returns all arguments, positioned as they appear in the signature. \\
        Earlier, this property returned arguments in the following way: positional-only, \\
        universal, keyword-only, variable argument, variable keyword argument.
        
        Empty if the function doesn't have any parameters (first parameter in non-static \\
        method isn't counted). Examples::
        
            def f1(p1, p2, /, p3, p4 = 75, *, p5, p6, **p7): ...
            # ("p1", "p2", "p3", "p4", "p5", "p6", "p7")
            def f2(p1, p2, *p3, p4 = 75, p5, **p6): ...
            # ("p1", "p2", "p3", "p4", "p5", "p6")
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.__builtin.all 
        
        c = self.func.__code__
        n = c.co_argcount + c.co_kwonlyargcount
        f = _CodeFlags()
            
        if _sys.version_info >= (0, 3, 44):
                
            _if_varargs = c.co_flags & f.varargs
            _if_varkeywords = c.co_flags & f.varkeywords

            # Include variable arguments in correct places
            if _if_varargs and _if_varkeywords:
                _all_ = (*self.positional, *self.universal, _return_param(self.func, c.co_varnames[n]), *self.keyword, _return_param(self.func, c.co_varnames[n + 1]))
                
            elif _if_varargs:
                _all_ = (*self.positional, *self.universal, _return_param(self.func, c.co_varnames[n]), *self.keyword)
                
            elif _if_varkeywords:
                _all_ = (*self.positional, *self.universal, *self.keyword, _return_param(self.func, c.co_varnames[n]))
                
            else:
                _all_ = (*self.positional, *self.universal, *self.keyword)
                
            return _all_
        
        else:
            
            if c.co_flags & _compiler_flags["varargs"]:
                n += 1
        
            if c.co_flags & _compiler_flags["varkeywords"]:
                n += 1
            
            return c.co_varnames[self.__no_first : n]
    
    @finalproperty
    def allDefaults(self): # 0.3.42
        """
        @lifetime >= 0.3.42 \\
        https://aveyzan.xyz/aveytense#aveytense.util.ParamVar.allDefaults
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - all arguments
        - their default values
        
        Empty whether there are none. It does not apply to variable arguments. Examples::
        
            def f1(p1, p2, /, p3, p4 = 75, *, p5, p6, **p7): ...
            def f2(p1, p2, *p3, p4 = 75, p5, **p6): ...
            # (("p4", "75"),) (both)
        
        Convertible to `dict`
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.__builtin.allDefaults
        
        return self.positionalDefaults + self.universalDefaults + self.keywordDefaults
    
    @finalproperty
    def allWithDefaults(self): # 0.3.51
        """
        @lifetime >= 0.3.51 \\
        https://aveyzan.xyz/aveytense#aveytense.util.ParamVar.allWithDefaults
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - all arguments
        - their default values (internal class if default value in some is not present)
        
        Empty whether there are none. It does apply to variable arguments. Examples::
        
            def f1(p1, p2, /, p3, p4 = 75, *, p5, p6): ...
            def f2(p1, p2, *p3, p4 = 75, p5, **p6): ...
            # (("p1", <paramNoDefault>), ("p2", <paramNoDefault>),
            # ("p3", <paramNoDefault>), ("p4", 75), ("p5", <paramNoDefault>),
            # ("p6", <paramNoDefault>)) (both)
        
        Convertible to `dict`
        """
        
        return tuple([(p, _ParamNoDefault if p not in dict(self.allDefaults) else dict(self.allDefaults)[p]) for p in self.all])
        
    
    @finalproperty
    def allNoDefaults(self): # 0.3.44
        """
        @lifetime >= 0.3.44 \\
        https://aveyzan.xyz/aveytense#aveytense.util.ParamVar.allNoDefaults
        
        Returns tuple holding all kind of parameters whose don't have a default value. \\
        Empty whether there are none. Examples::
        
            def f1(p1, p2, /, p3, p4 = 75, *, p5, p6, **p7): ...
            # ("p1", "p2", "p3", "p5", "p6", "p7")
            def f2(p1, p2, *p3, p4 = 75, p5, **p6): ...
            # ("p1", "p2", "p3", "p5", "p6")
        """
        
        return tuple([e for e in self.all if e not in dict(self.allDefaults)])
    
    @finalproperty
    def positional(self): # 0.3.42
        """
        @lifetime >= 0.3.42
        
        Returns tuple holding all positional-only arguments. Empty whether there are none. Examples::
        
            def f1(p1, p2, p3, p4 = 54, p5 = "", /): ...
            # ("p1", "p2", "p3", "p4", "p5")
            def f2(__p1, __p2, __p3, __p4 = 54, __p5 = ""): ... # pre-PEP 570
            # ("__p1", "__p2", "__p3", "__p4", "__p5")
            def f3(__p1, __p2, __p3, __p4 = 54, /, __p5 = ""): ... # mixed
            # ("__p1", "__p2", "__p3", "__p4")
            
        See PEP 570 for positional-only operator `/`. Variable parameter (`*<param>`) isn't counted.
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.__builtin.positional
        
        c = self.func.__code__
        
        # Code revamp 0.3.47
        if c.co_posonlyargcount > 0:
            # Before 0.3.47, this was only returned, and no doubly underscored arguments
            # as the only way to create positional arguments before PEP 570 were included.
            return tuple([_return_param(self.func, e) for e in c.co_varnames[self.__no_first : c.co_posonlyargcount]])
        
        _tuple_ = c.co_varnames[: c.co_argcount]
        
        if _reckon(_tuple_) == 0:
            a = [""]
            a.clear()
            return tuple(a)
        
        # Parameters in a method have following syntax, as in private methods: _<class-name>__<param-name>.
        # Functions do not use this naming syntax
        if isinstance(self.func, __.MethodType):
            _tuple_ = _tuple_[self.__no_first :]
            _gen_ = (e for e in _tuple_)
            _list_ = [""]
            _list_.clear()
            e = "__a_" # loop statement satisfaction; changed after first iteration
            
            while e.startswith("__") and not e.endswith("__"):
                e = next(_gen_, "")
                
                if e == "":
                    break
                
                _list_.append(_return_param(self.func, e))
                
            return tuple(_list_)
        
        _tuple_end_marker_ = 0
        
        # If argument is completely encased by 2 (or more) underscores at the beginning and ending, then
        # it ISN'T considered positional! Also, we are catching IndexError, as it may occur.
        # Examples for non-positional-only parameters: _1, _1_, _1__, __1__, __1___, ___1__, etc. 
        try:
            while _tuple_[_tuple_end_marker_].startswith("__") and not _tuple_[_tuple_end_marker_].endswith("__"):
                _tuple_end_marker_ += 1
                
        except IndexError:
            pass
            
        return _tuple_[: _tuple_end_marker_]
    
    @finalproperty
    def positionalDefaults(self): # 0.3.42
        """
        @lifetime >= 0.3.42
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - positional-only arguments
        - their default values
        
        Empty whether there are none. Examples::
        
            def f1(p1, p2, p3, p4 = 54, p5 = "", /): ...
            # (("p4", 65), ("p5", ""))
            def f2(__p1, __p2, __p3, __p4 = 54, __p5 = ""): ... # pre-PEP 570
            # (("__p4", 65), ("__p5", ""))
            def f3(__p1, __p2, __p3, __p4 = 54, /, __p5 = ""): ... # mixed
            # (("__p4", 54),)
            
        Convertible to `dict`
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.__builtin.positionalDefaults
        
        # Code revamp 0.3.47
        if self.positionalCount > 0 and self.func.__defaults__ is not None:
            
            _defaults_ = self.func.__defaults__[::-1][self.universalCount:]
            _positional_ = self.positional[::-1]
            
            return tuple([(_positional_[i], _defaults_[i]) for i in range(min(_reckon(_positional_), _reckon(_defaults_)))])[::-1]
                
        a = [("", StopIteration.value)]
        a.clear()
        return tuple(a)
    
    @finalproperty
    def positionalWithDefaults(self): # 0.3.51
        """
        @lifetime >= 0.3.51
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - positional-only arguments
        - their default values (internal class if default value in some is not present)
        
        Empty whether there are none. Examples::
        
            def f1(p1, p2, p3, p4 = 54, p5 = "", /): ...
            # (("p1", <paramNoDefault>), ("p2", <paramNoDefault>),
            # ("p3", <paramNoDefault>), ("p4", 65), ("p5", ""))
            def f2(__p1, __p2, __p3, __p4 = 54, __p5 = ""): ... # pre-PEP 570
            # (("__p1", <paramNoDefault>), ("__p2", <paramNoDefault>),
            # ("__p3", <paramNoDefault>), ("__p4", 54), ("__p5", ""))
            def f3(__p1, __p2, __p3, __p4 = 54, /, __p5 = ""): ... # mixed
            # (("__p1", <paramNoDefault>), ("__p2", <paramNoDefault>),
            # ("__p3", <paramNoDefault>), ("__p4", 54)
            
        Convertible to `dict`
        """
        
        return tuple([(p, _ParamNoDefault if p not in dict(self.positionalDefaults) else dict(self.positionalDefaults)[p]) for p in self.positional])
    
    @finalproperty
    def positionalNoDefaults(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns tuple holding all positional-only arguments whose don't have a default value. \\
        Empty whether there are none. Examples::
        
            def f1(p1, p2, p3, p4 = 54, p5 = "", /): ...
            # ("p1", "p2", "p3")
            def f2(__p1, __p2, __p3, __p4 = 54, __p5 = ""): ... # pre-PEP 570
            # ("__p1", "__p2", "__p3")
            def f3(__p1, __p2, __p3, __p4 = 54, /, __p5 = ""): ... # mixed
            # ("__p1", "__p2", "__p3")
        """
        
        return tuple([e for e in self.positional if e not in dict(self.positionalDefaults)]) 
    
    @finalproperty
    def keyword(self): # 0.3.42
        """
        @lifetime >= 0.3.42
        
        Returns tuple holding all keyword-only arguments. \\
        Empty whether there are none. Example::
        
            def f(p1, *, p2 = 66, p3 = "", p4, **p5): ...
            # ("p2", "p3", "p4")
        
        See PEP 3102 for keyword-only operator `*`. Variable \\
        keyword parameter (`**<param>`) isn't counted.
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.__builtin.keyword
        
        if _sys.version_info >= (0, 3, 47):
            
            c = self.func.__code__
            
            return tuple([_return_param(self.func, e) for e in c.co_varnames[c.co_argcount : c.co_argcount + c.co_kwonlyargcount]])
        
        else:
            
            return self.func.__code__.co_varnames[self.func.__code__.co_argcount : self.func.__code__.co_argcount + self.func.__code__.co_kwonlyargcount]
    
    @finalproperty
    def keywordDefaults(self): # 0.3.42
        """
        @lifetime >= 0.3.42
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - keyword-only arguments
        - their default values
        
        Empty if there are none. Example::
        
            def f(p1, *, p2 = 66, p3 = "", p4, **p5): ...
            # (("p2", 72), ("p3", ""))
            
        Convertible to `dict`
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.__builtin.keywordDefaults
        
        if self.func.__kwdefaults__ is None:
            
            a = [("", StopIteration.value)]
            a.clear()
            return tuple(a)
    
        return tuple([(_return_param(self.func, k), self.func.__kwdefaults__[k]) for k in self.func.__kwdefaults__])
    
    @finalproperty
    def keywordWithDefaults(self): # 0.3.51
        """
        @lifetime >= 0.3.51
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - keyword-only arguments
        - their default values (internal class if default value in some is not present)
        
        Empty if there are none. Example::
        
            def f(p1, *, p2 = 66, p3 = "", p4, **p5): ...
            # >= 0.3.52: (("p2", 72), ("p3", ""), ("p4", <paramNoDefault>))
            # <  0.3.52: None
            
        Convertible to `dict`
        """
        return tuple([(p, _ParamNoDefault if p not in dict(self.keywordDefaults) else dict(self.keywordDefaults)[p]) for p in self.keyword]) # >= 0.3.52: missing return statement
        
    
    @finalproperty
    def keywordNoDefaults(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns tuple holding all keyword arguments whose don't have a default value. \\
        Empty if there are none. Example::
        
            def f(p1, *, p2 = 72, p3 = "", p4, **p5): ...
            # ("p4",)
        """
        return tuple([e for e in self.keyword if e not in dict(self.keywordDefaults)])
    
    @finalproperty
    def universal(self): # 0.3.42
        """
        @lifetime >= 0.3.42
        
        Returns tuple holding all universal arguments. *Universal* arguments are \\
        arguments that can have their values assigned either by position or their \\
        names (keywords).
        
        Empty if there are none. Examples::
        
            def f1(p1, /, p2, p3, p4 = 96, p5 = True, *, p6 = 12): ...
            # ("p2", "p3", "p4", "p5")
            def f2(__p1, /, __p2, __p3, __p4 = 65, __p5 = "", *, __p6 = 12): ...
            # ("__p2", "__p3", "__p4", "__p5")
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.__builtin.universal
        
        c = self.func.__code__
        
        # Code revamp 0.3.47; see self.positional
        if isinstance(self.func, __.MethodType):
            _tuple_ = c.co_varnames[self.__no_first : c.co_argcount]
            return tuple([_return_param(self.func, e) for e in _tuple_ if _return_param(self.func, e) not in self.positional])
            
        else:
            
            # Prevent negative integer slice arguments
            _left = self.__no_first if c.co_posonlyargcount - self.__no_first <= 0 else c.co_posonlyargcount - self.__no_first
            return tuple([e for e in c.co_varnames[_left : c.co_argcount] if e not in self.positional])
    
    @finalproperty
    def universalDefaults(self): # 0.3.42
        """
        @lifetime >= 0.3.42
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - universal arguments
        - their default values
        
        Empty if there are none. Examples::
        
            def f1(p1, /, p2, p3, p4 = 96, p5 = True, *, p6 = 12): ...
            # (("p4", 96), ("p5", True))
            def f2(__p1, /, __p2, __p3, __p4 = 65, __p5 = "", *, __p6 = 12): ...
            # (("__p4", 96), ("__p5", True))
        
        Convertible to `dict`
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.__builtin.universalDefaults
        
        # Code revamp 0.3.47
        if self.positionalCount > 0 and self.func.__defaults__ is not None:
            
            _defaults_ = self.func.__defaults__[self.positionalDefaultsCount:][::-1]
            _universal_ = self.universal[::-1]
            
            return tuple([(_universal_[i], _defaults_[i]) for i in range(min(_reckon(_universal_), _reckon(_defaults_))) if (_universal_[i], _defaults_[i]) not in self.positionalDefaults])[::-1]
        
        a = [("", StopIteration.value)]
        a.clear()
        return tuple(a)
    
    @finalproperty
    def universalWithDefaults(self): # 0.3.51
        """
        @lifetime >= 0.3.51
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - universal arguments
        - their default values (internal class if default value in some is not present)
        
        Empty if there are none. Examples::
        
            def f1(p1, /, p2, p3, p4 = 96, p5 = True, *, p6 = 12): ...
            # (("p2", <paramNoDefault>), ("p3", <paramNoDefault>),
            # ("p4", 96), ("p5", True))
            def f2(__p1, /, __p2, __p3, __p4 = 65, __p5 = "", *, __p6 = 12): ...
            # (("__p2", <paramNoDefault>), ("__p3", <paramNoDefault>),
            # ("__p4", 96), ("__p5", True))
        
        Convertible to `dict`
        """
        
        return tuple([(p, _ParamNoDefault if p not in dict(self.universalDefaults) else dict(self.universalDefaults)[p]) for p in self.universal])
                
    @finalproperty
    def universalNoDefaults(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns tuple holding all universal arguments whose don't have a default value. \\
        Empty if there are none. Examples::
        
            def f1(p1, /, p2, p3, p4 = 96, p5 = True, *, p6 = 12): ...
            # ("p2", "p3")
            def f2(__p1, /, __p2, __p3, __p4 = 65, __p5 = "", *, __p6 = 12): ...
            # ("__p2", "__p3")
        """
        return tuple([e for e in self.universal if e not in dict(self.universalDefaults)])
    
    @finalproperty
    def annotated(self): # 0.3.42
        """
        @lifetime >= 0.3.42
        
        Returns tuple holding names of arguments whose have been annotated a type. Such \\
        parameter can be type annotated since Python 3.5. Example::
        
            def f(p1: bool, p2: int = 90, p3: str = "f", p4 = False): ...
            # ("p1", "p2", "p3")
        
        See PEP 484 for type annotations. Note variable argument and variable keyword \\
        argument are counted too.
        """
        
        # 0.3.51
        if self.__builtin is not None:
            a = [""]
            a.clear()
            return tuple(a)
        
        if True: # >= 0.3.52; correct order
            return tuple([_return_param(self.func, k) for k in self.all if k in self.func.__annotations__ and k != "return"])
        else:
            return tuple([_return_param(self.func, k) for k in self.func.__annotations__ if k != "return"])
    
    @finalproperty
    def annotatedDefaults(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - type-annotated arguments
        - their annotated type and default values (respectively in a 2-item tuple since 0.3.47)
        
        Empty if there are none. Example::
        
            def f(p1: bool, p2: int = 90, p3: str = "f", p4 = False): ...
            # >= 0.3.52:           (("p2", (int, 90)), ("p3", (str, "f)))
            # >= 0.3.47; < 0.3.52: (("p2", ("int", 90)), ("p3", ("str", "f")))
            # <  0.3.47:           (("p2", 90), ("p3", "f"))
        
        Convertible to `dict`
        """
        
        if _sys.version_info >= (0, 3, 47):
            
            _list_ = [("", (StopIteration.value, StopIteration.value))]
            _list_.clear()
            
            # 0.3.51
            if self.__builtin is not None:
                return tuple(_list_)
            
            _defaults_ = dict(self.allDefaults)
            
            for e in self.annotated:
                if e in _defaults_:
                    
                    if True: # >= 0.3.52
                        if _sys.version_info >= (3, 13): # 0.3.53: 'globals' parameter check (if can be passed as keyword)
                            _list_.append((e, (eval(self.func.__annotations__[e], globals = self.func.__globals__), _defaults_[e])))
                        else:
                            _list_.append((e, (eval(self.func.__annotations__[e], self.func.__globals__), _defaults_[e])))
                    else:
                        _list_.append((e, (self.func.__annotations__[e], _defaults_[e])))
                    
            return tuple(_list_)
        
        else:
            return tuple([e for e in self.allDefaults if e[0] in self.annotated])
        
    @finalproperty
    def annotatedWithDefaults(self): # 0.3.51
        """
        @lifetime >= 0.3.51
        
        Returns tuple holding tuples with pair of items with content, respectively:
        - type-annotated arguments
        - their annotated type and default values (respectively in a 2-item tuple) \\
            or internal class if default value in some is not present
        
        Empty if there are none. Example::
        
            def f(p1: bool, p2: int = 90, p3: str = "f", p4 = False): ...
            # (("p1", <paramNoDefault>), ("p2", ("int", 90)), ("p3", ("str", "f")))
        
        Convertible to `dict`
        """
        
        if False:
            _return_ = [("", (StopIteration.value, StopIteration.value))]
            _return_.clear()
            _return_.extend([(p, (
                _ParamNoDefault if p not in self.func.__annotations__ else self.func.__annotations__[p],
                _ParamNoDefault if p not in dict(self.annotatedDefaults) else dict(self.annotatedDefaults)[p][1]
            )) for p in self.annotated])
            return tuple(_return_)
        
        else:
            return tuple([(p, _ParamNoDefault if p not in dict(self.annotatedDefaults) else dict(self.annotatedDefaults)[p]) for p in self.annotated])
    
    @finalproperty
    def annotatedNoDefaults(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns tuple holding names of arguments whose have been annotated a type, \\
        but do not have a default value. Empty if there are none. Example::
        
            def f(p1: bool, p2: int = 90, p3: str = "f", p4 = False): ...
            # ("p1",)
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.annotated
        
        _defaults_ = dict(self.annotatedDefaults)
        return tuple([e for e in self.annotated if e not in _defaults_])
    
    @finalproperty
    def annotations(self): # 0.3.42
        """
        @lifetime >= 0.3.42 \\
        https://aveyzan.xyz/aveytense#aveytense.util.ParamVar.annotations
        
        Same as invocation `self.func.__annotations__`, just sorted as parameters appear in the signature, \\
        and with `return` annotation returned (changeover 0.3.47). Convertible to `dict`
        
        Since 0.3.52 annotations no longer are returned as strings.
        """
        
        # Code revamp 0.3.47
        _list_ = [("", StopIteration.value)]
        _list_.clear()
        
        # 0.3.51
        if self.__builtin is not None:
            return tuple(_list_)
        
        _annotated_ = (*self.all, "return")
        
        for e in _annotated_:
            if e in self.func.__annotations__:
                
                if True: # >= 0.3.52
                    if _sys.version_info >= (3, 13): # 0.3.53: 'globals' parameter check (if can be passed as keyword)
                        _list_.append((_return_param(self.func, e), eval(self.func.__annotations__[e], globals = self.func.__globals__)))
                    else:
                        _list_.append((_return_param(self.func, e), eval(self.func.__annotations__[e], self.func.__globals__)))
                else:
                    _list_.append((_return_param(self.func, e), self.func.__annotations__[e]))
        
        return tuple(_list_)
        
    @finalproperty
    def variable(self): # 0.3.42 
        """
        @lifetime >= 0.3.42
        
        Returns tuple holding variable argument and variable keyword argument - both in separate \\
        internal 2-item tuples (second item being one of keywords: `"<args>"` and `"<kwargs>"`). \\
        Empty if there are none. Examples::
        
            def f1(*args, **kwds): ...
            # (("args", "<args>"), ("kwds", "<kwargs>"))
            def f2(*args): ...
            # (("args", "<args>"))
            def f3(**kwds): ...
            # (("kwds", "<kwargs>"))
        
        Convertible to `dict`. Sometimes preferred to use dictionary comprehension in the following \\
        way: `{e[1]: e[0] for e in self.variable}`, to refer by keyword `"<args>"` \\
        or `"<kwargs>"`. The same can be done with `~.Tense.invert()` class method (>= 0.3.46).
        """
        
        # 0.3.51
        if self.__builtin is not None:
            return self.__builtin.variable
        
        c = self.func.__code__
        f = _CodeFlags()
        
        _filter_ = tuple([e for e in self.all if e not in self.positional and e not in self.universal and e not in self.keyword]) # 0.3.46
        
        if c.co_flags & f.varargs and c.co_flags & f.varkeywords:
            
            self.__vartype = " <args, kwargs>"
            # < 0.3.45: self.allCount, self.allCount + 1
            # < 0.3.46: self.allCount - 2, self.allCount - 1
            # >= 0.3.46
            return tuple([(_filter_[0], "<args>"), (_filter_[1], "<kwargs>")]) 
        
        else:
            
            if c.co_flags & f.varargs:
                self.__vartype = " <args>"
                
            elif c.co_flags & f.varkeywords:
                self.__vartype = " <kwargs>"
                
            else:
                a = [("", "")]
                a.clear()
                return tuple(a)
            
            # < 0.3.45: self.allCount
            # >= 0.3.46
            return tuple([(_filter_[0], __.cast(str, self.__vartype).lstrip())]) 
        
    @finalproperty
    def positionalCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all positional-only parameters"""
        
        return _reckon(self.positional)
    
    @finalproperty
    def positionalDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all positional-only parameters with default values"""
        
        return _reckon(self.positionalDefaults)
    
    @finalproperty
    def positionalNoDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all positional-only parameters without default values"""
        
        return _reckon(self.positionalNoDefaults)
    
    @finalproperty
    def universalCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all universal parameters"""
        
        return _reckon(self.universal)
    
    @finalproperty
    def universalDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all universal parameters with default values"""
        
        return _reckon(self.universalDefaults)
    
    @finalproperty
    def universalNoDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all universal parameters without default values"""
        
        return _reckon(self.universalNoDefaults)
    
    @finalproperty
    def keywordCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all keyword-only parameters"""
        
        return _reckon(self.keyword)
    
    @finalproperty
    def keywordDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all keyword-only parameters with default values"""
        
        return _reckon(self.keywordDefaults)
    
    @finalproperty
    def keywordNoDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all keyword parameters without default values"""
        
        return _reckon(self.keywordNoDefaults)
    
    @finalproperty
    def allCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all parameters"""
        
        return _reckon(self.all)
    
    @finalproperty
    def allDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all parameters with default values"""
        
        return _reckon(self.allDefaults)
    
    @finalproperty
    def allNoDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all parameters without default value"""
        
        return _reckon(self.allNoDefaults)
    
    @finalproperty
    def annotatedCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all parameters which have been annotated a type"""
        
        return _reckon(self.annotated)
    
    @finalproperty
    def annotatedDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all parameters which have been annotated a type, and a default value"""
        
        return _reckon(self.annotatedDefaults)
    
    @finalproperty
    def annotatedNoDefaultsCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all parameters which have been annotated a type, however, don't have default value"""
        
        return _reckon(self.annotatedNoDefaults)
    
    @finalproperty
    def variableCount(self): # 0.3.44
        """
        @lifetime >= 0.3.44
        
        Returns count of all variable parameters (0-2)"""
        
        return _reckon(self.variable)
    
    __all__ = sorted([k for k in locals() if not k.startswith("_")])
    """@lifetime >= 0.3.51"""
        
class MutableString:
    """
    @lifetime >= 0.3.42 \\
    https://aveyzan.xyz/aveytense#aveytense.util.MutableString
    
    Represents a string, which can be mutated.
    """
    
    ### Initializer ###
    def __init__(self, string, /): # 0.3.42
        
        # 0.3.45: allow instances of the class to be used in the constructor
        if not isinstance(string, (str, type(self))):
            error = TypeError("expected a string or instance of the same class")
            raise error
        
        if isinstance(string, str):
            self.__str = list(string)
            
        else:
            self.__str = list(str(string))
    
    ### Conversions ###
    def __str__(self): # 0.3.42
        
        if not all([isinstance(e, str) for e in self.__str]):
            error = TypeError("internal variable isn't a string")
            raise error
        
        else:
            return "".join(self.__str)
    
    def __repr__(self): # 0.3.42
        
        return "<{}.{} object :: {}(\"{}\")> ".format(self.__module__, type(self).__name__, type(self).__name__, self.__str__())
    
    def __hash__(self): # 0.3.42
        
        return hash(str(self))
    
    def __format__(self, format_spec): # 0.3.42
        
        if type(format_spec) is not str:
            error = TypeError("expected a string")
            raise error
        
        return format_spec.format(str(self))  
    
    ### Length ###
    def __len__(self): # 0.3.42
        
        return _reckon(self.__str__())
    
    def __reckon__(self): # 0.3.42
        
        return _reckon(self.__str__())
    
    ### Indexes ###
    @__.overload
    def __getitem__(self, value: __.Union[int, slice]) -> str: ...
    
    @__.overload
    def __getitem__(self, value: str) -> int: ...
    
    def __getitem__(self, value): # 0.3.42
        
        if type(value) is int or type(value) is slice:
            
            if type(value) is int and -(_reckon(self.__str) + 1) >= value >= _reckon(self.__str):
                error = IndexError("index out of range")
                raise error
            
            return str(self)[value]
        
        elif type(value) is str:
            
            return str(self).count(value)
        
        else:
            error = TypeError("expected a slice, substring or integer")
            raise error
        
    def __setitem__(self, name, value):
        
        if type(name) is int or type(name) is slice:
                
            if type(name) is int and -(_reckon(self.__str) + 1) >= name >= _reckon(self.__str):
                error = IndexError("index out of range")
                raise error
            
            self.__str[name] = value
            
        elif type(name) is str:
            
            if type(value) is str:
                self.__str = list(self.__str__().replace(name, value))
                
            else:
                error = TypeError("expected string for string indexes")
                raise error
            
        else:
            error = TypeError("expected a slice, substring or integer")
            raise error
        
    def __delitem__(self, name): # 0.3.42
        
        if type(name) is not int and type(name) is not slice:
            error = TypeError("expected a slice or integer")
            raise error
        
        if type(name) is int and -(_reckon(self.__str) + 1) >= name >= _reckon(self.__str):
            error = IndexError("index out of range")
            raise error
        
        del self.__str[name]
        
    ### Other ###
        
    def __add__(self, other): # 0.3.42
        
        if type(other) is type(self):
            
            return type(self)(str(self) + str(other))
        
        elif type(other) is str:
            
            return type(self)(str(self) + other)
        
        else:
            
            error = TypeError("operation with unsupported type of right operand: '{}'".format(type(other).__name__))
            raise error
        
    def __radd__(self, other): # 0.3.42
        
        try:
            
            return self.__add__(other)
        
        except TypeError:
            
            error = TypeError("operation with unsupported type of left operand: '{}'".format(type(other).__name__))
            raise error
        
    def __iadd__(self, other): # 0.3.42
        
        if type(other) is type(self):
            
            self.__str += list(str(other))
        
        elif type(other) is str:
            
            self.__str += list(other)
        
        else:
            
            error = TypeError("operation with unsupported type of right operand: '{}'".format(type(other).__name__))
            raise error
        
        return self
        
    def __mul__(self, other): # 0.3.42
        
        if type(other) is int:
            
            if other > 0:
                return type(self)(str(self) * other)
            
            elif other == 0: # >= 0.3.43
                return type(self)("")
            
            else:
                error = IndexError("expected an integer above zero")
                raise error
            
        else:
            error = TypeError("expected an integer")
            raise error
        
    def __rmul__(self, other): # 0.3.42
        
        try:
            
            return self.__mul__(other)
        
        except TypeError:
            
            error = TypeError("operation with unsupported type of left operand: '{}'".format(type(other).__name__))
            raise error
        
    def __imul__(self, other): # 0.3.42
        
        if type(other) is int:
            
            if other > 0:
                s = str(self)
                self.__str = list(s * other)
            
            else:
                error = IndexError("expected an integer above zero")
                raise error
            
        else:
            error = TypeError("expected an integer")
            raise error
        
        return self
    
    def __mod__(self, other): # 0.3.42
        
        return str(self.__str__() % other)
    
    def __getnewargs__(self): # 0.3.42
        
        return self.__str__().__getnewargs__()
      
    ### Checking ###
    def __contains__(self, key): # 0.3.42
        
        return key in self.__str__() if type(key) is str else str(key) in self.__str__() if type(key) is type(self) else False
    
    def __lt__(self, other): # 0.3.42
        
        return self.__str__() < other if type(other) is str else self.__str__() < str(other) if type(other) is type(self) else False
    
    def __gt__(self, other): # 0.3.42
        
        return self.__str__() > other if type(other) is str else self.__str__() > str(other) if type(other) is type(self) else False
    
    def __le__(self, other): # 0.3.42
        
        return self.__str__() <= other if type(other) is str else self.__str__() <= str(other) if type(other) is type(self) else False
    
    def __ge__(self, other): # 0.3.42
        
        return self.__str__() >= other if type(other) is str else self.__str__() >= str(other) if type(other) is type(self) else False
    
    def __eq__(self, other): # 0.3.42
        
        return self.__str__() == other if type(other) is str else self.__str__() == str(other) if type(other) is type(self) else False
    
    def __ne__(self, other): # 0.3.42
        
        return self.__str__() != other if type(other) is str else self.__str__() != str(other) if type(other) is type(self) else False
    
    ### Other ###
    def clear(self): # 0.3.42
        """Clear the mutable string."""
        
        a = [""]
        del a[0]
        self.__str = a
        
    def join(self, i: __.AVT_Iterable[__.Any], /, useRepr = False): # 0.3.45
        """
        Extension of `str.join()`, which accepts every iterable's type (unlike for mentioned method it is string iterable only), \\
        with setting `useRepr` that allows to use `repr()` instead of `str()` when set to `True`.
        """
        
        if not isinstance(i, __.Iterable):
            error = TypeError("expected an iterable")
            raise error
        
        if _reckon(i) == 0:
            return "".join(self.__str)
        
        try:
            [str(e) for e in i]
            
        except:
            
            try:
                [repr(e) for e in i]
                
            except:
                
                error = TypeError("couldn't convert all items to string")
                raise error
        
        _invoke = lambda x: str(x) if not useRepr else repr(x)
        
        return "".join(self.__str).join([_invoke(e) for e in i])
    
    def reverse(self): # 0.3.45
        """
        Reverse the mutable string.
        """
        self.__str = self.__str[::-1]
        
    @property
    def value(self): # 0.3.42
        
        return self.__str__()
    
    @value.setter
    def value(self, value): # 0.3.42
        
        if type(value) is type(self):
            
            self.__str = list(str(value))
            
        elif type(value) is str:
            
            self.__str = list(value)
            
        else:
            
            error = TypeError("expected a string or instance of '{}.MutableString'".format(self.__module__))
            raise error
        
    @value.deleter
    def value(self):
        
        error = TypeError("unable to delete property '" + type(self).value.fget.__name__ + "'")
        raise error
    
        
def simpleEnum(etype: type[_T_enum] = __.Enum, boundary: __.Optional[__.FlagBoundary] = None, useArgs = False):
    """
    @lifetime >= 0.3.42
    
    Globally scoped version of `enum._simple_enum()`
    """
    
    import enum
    
    return __.cast(__.AVT_Callable[[type[__.Any]], type[_T_enum]], enum._simple_enum(etype, boundary = boundary, use_args = useArgs))
            
if __name__ == "__main__":
    error = RuntimeError("This file is not for compiling, consider importing it instead.")
    raise error

if False: # < 0.3.50
    
    class StrictEnum:
        """
        @lifetime >= 0.3.43 \\
        *Experimental*
        
        This class decorator allows to create enumerators similar as these in TypeScript.
        """
        
        def __init_subclass__(cls):
            
            # attributes that are callable are lambda functions    
            _is_attribute_ = lambda x: not isinstance(x, (__.FunctionType, __.MethodType, property)) and not (isinstance(x, __.FunctionType) and "<lambda>" in str(x))
            
            if _sys.version_info >= (3, 13):
                _dont_permit_ = ("__module__", )
            
            cls = __.Enum(cls.__name__, [(k, type(cls.__dict__[k])) for k in cls.__dict__ if _is_attribute_(cls.__dict__[k])])
        

Any = __.Any # >= 0.3.43
"""
@lifetime >= 0.3.43

`typing.Any`
"""

if False:
    
    class Unbound:
        """
        @since 0.3.44 (in code)
        
        Indicates unbound variable. Once referenced, throws an error
        """
        
        def __init__(self):
            pass
        
        def __get__(self, instance, owner = None):
            
            if instance is not None:
                error = UnboundLocalError("cannot access local variable '{}' where it is not associated with a value")
                raise error
            
            return type(self) 
        
class uniquelist:
    """
    @lifetime >= 0.3.48 \\
    https://aveyzan.xyz/aveytense#aveytense.util.uniquelist
    
    Returns version of an iterable without duplicate items and changing order, as a list
    """
    
    def __new__(cls, iterable: __.AVT_Iterable[_T] = ..., /):
        
        if iterable is Ellipsis:
            return __.cast(__.AVT_List[_T], [])
        
        _list_ = list(iterable)
        _new_list_: __.AVT_List[_T] = []
        
        for e in _list_:
            
            if e not in _new_list_:
                _new_list_.append(e)
                
        return _new_list_
    
class uniquetuple:
    """
    @lifetime >= 0.3.48 \\
    https://aveyzan.xyz/aveytense#aveytense.util.uniquetuple
    
    Returns version of an iterable without duplicate items and changing order, as a tuple
    
    Alias to `tuple(~.uniquelist(i))`
    """
    
    def __new__(self, iterable: __.AVT_Iterable[_T] = ..., /):
        
        return tuple(uniquelist(iterable))

class Flags(__.NotCallable, _FlagsType):
    """
    @lifetime >= 0.3.53 \\
    https://aveyzan.xyz/aveytense#aveytense.util.Flags
    
    Returns buffer, code and type flags
    """
    
    buffer = _BufferFlags()
    """
    @lifetime >= 0.3.53
    
    Receive buffer flags
    """
    
    code = _CodeFlags()
    """
    @lifetime >= 0.3.53
    
    Receive code flags defined as in `dis.COMPILER_FLAG`
    """
    
    type = _TypeFlags()
    """
    @lifetime >= 0.3.53
    
    Receive type flags
    """
    
    __all__ = sorted(_extend(vars(_BufferFlags), vars(_CodeFlags), vars(_TypeFlags)))
    """
    @lifetime >= 0.3.53
    
    Returns all flag names
    """

Flags = Flags()
BufferFlags = Flags.buffer
"""@lifetime >= 0.3.53"""
CodeFlags = Flags.code
"""@lifetime >= 0.3.53"""
TypeFlags = Flags.type
"""@lfetime >= 0.3.53"""
    
__all__ = sorted([k for k in globals() if not k.startswith("_")]) # 0.3.41: sorted()
__all_deprecated__ = sorted([k for k in globals() if hasattr(globals()[k], "__deprecated__")])
"""
@lifetime >= 0.3.41

Returns all deprecated declarations within this module.
"""

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error
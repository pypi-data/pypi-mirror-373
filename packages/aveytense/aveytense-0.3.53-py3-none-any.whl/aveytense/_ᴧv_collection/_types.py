"""
@lifetime >= 0.3.26rc3 \\
© 2024-Present Aveyzan // License: MIT

Core of `aveytense.types`; import this module instead
"""

from __future__ import annotations
import sys as _sys

from ._exceptions import _ErrorHandler as _E

from abc import (
    ABC as ABC, # 0.3.44
    ABCMeta as ABCMeta, # 0.3.44
    abstractmethod as abstractmethod # 0.3.44
)

from array import (
    array as array, # 0.3.37
    ArrayType as ArrayType # 0.3.37
)

from ast import (
    Expression as Expression, # 0.3.44
    Module as Module, # 0.3.44
    Interactive as Interactive, # 0.3.44
)

from collections import (
    ChainMap as ChainMap, # 0.3.37
    Counter as Counter, # 0.3.37
    defaultdict as defaultdict, # 0.3.37 
    deque as deque, # 0.3.37
    OrderedDict as OrderedDict, # 0.3.44
    UserDict as UserDict, # 0.3.44
    UserList as UserList, # 0.3.44
    namedtuple as namedtuple, # 0.3.44
    UserString as UserString # 0.3.44
)

from collections.abc import (
    AsyncGenerator as AsyncGenerator,
    AsyncIterable as AsyncIterable,
    AsyncIterator as AsyncIterator,
    Awaitable as Awaitable,
    Callable as Callable,
    Collection as Collection,
    Container as Container,
    Coroutine as Coroutine,
    Generator as Generator,
    Hashable as Hashable,
    ItemsView as ItemsView,
    Iterable as Iterable,
    Iterator as Iterator,
    KeysView as KeysView,
    Mapping as Mapping,
    MappingView as MappingView,
    MutableMapping as MutableMapping,
    MutableSequence as MutableSequence,
    MutableSet as MutableUniqual, # pyright: ignore[reportUnusedImport]
    Reversible as Reversible,
    Sequence as Sequence,
    Set as Uniqual, # Naming to this to prevent ambiguity with typing.Set alias
    Sized as Sized,
    ValuesView as ValuesView
)

from contextlib import (
    AbstractAsyncContextManager as AsyncContentManager, # pyright: ignore[reportUnusedImport] ## >= 0.3.53
    AbstractContextManager as ContextManager, # pyright: ignore[reportUnusedImport] ## >= 0.3.53
)

from dataclasses import (
    dataclass as dataclass # 0.3.37
)

from enum import (
    EnumMeta as EnumMeta, # 0.3.26rc1
)

from functools import (
    cached_property as cachedproperty, # 0.3.37
    partial as partial, # 0.3.26
    partialmethod as partialmethod, # 0.3.37
    singledispatchmethod as singledispatchmethod, # 0.3.37
    lru_cache as lru_cache, # 0.3.37
    singledispatch as singledispatch, # 0.3.37
)

from importlib import import_module as import_module # 0.3.44

from inspect import (
    ArgInfo as ArgInfo, # 0.3.26rc3
    Arguments as Arguments, # 0.3.26rc3
    Attribute as Attribute, # 0.3.26rc3
    BlockFinder as BlockFinder, # 0.3.26rc3
    BoundArguments as BoundArguments, # 0.3.26rc3
    ClosureVars as ClosureVars, # 0.3.26rc3
    FrameInfo as FrameInfo, # 0.3.26rc3
    FullArgSpec as FullArgSpec, # 0.3.26rc3
    Parameter as Parameter, # 0.3.26rc3
    Signature as Signature, # 0.3.26rc3
    Traceback as Traceback, # 0.3.26rc3
)

from os import PathLike as PathLike # 0.3.52

from re import (
    Match as Match, # 0.3.26
    Pattern as Pattern # 0.3.26
)

# Imports from 0.3.51 are used for builtin function inspection via ~.util.ParamVar.

from types import (
    AsyncGeneratorType as AsyncGeneratorType, # 0.3.44
    BuiltinFunctionType as BuiltinFunctionType, # 0.3.51
    ClassMethodDescriptorType as ClassMethodDescriptorType, # 0.3.51
    CodeType as CodeType, # 0.3.26rc3
    CoroutineType as CoroutineType, # 0.3.44
    DynamicClassAttribute as DynamicClassAttribute, # 0.3.43
    FrameType as FrameType, # 0.3.37
    FunctionType as FunctionType, # 0.3.37
    MappingProxyType as MappingProxyType, # 0.3.42
    MethodDescriptorType as MethodDescriptorType, # 0.3.51
    MethodWrapperType as MethodWrapperType, # 0.3.51
    MethodType as MethodType, # 0.3.37
    ModuleType as ModuleType, # 0.3.26rc3
    SimpleNamespace as SimpleNamespace, # 0.3.53
    TracebackType as TracebackType, # 0.3.26rc3
    WrapperDescriptorType as WrapperDescriptorType, # 0.3.51
    coroutine as coroutine, # 0.3.26rc1/0.3.34?
    new_class as new_class # 0.3.26rc1/0.3.34?
)

from typing import (
    cast as cast, # 0.3.44
    get_type_hints as get_type_hints, # 0.3.37
    no_type_check as no_type_check, # 0.3.37?
)

from unittest import (
    TestCase as TestCase, # 0.3.26rc3
    TestLoader as TestLoader, # 0.3.26rc3
)

from uuid import UUID as UUID # 0.3.26rc3

__name__ = "aveytense.types"
    
### ENUMS & FLAGS ###
# 0.3.44: Additional checking to ensure these enumerator and flag classes exist already.

import enum as _enum

class Enum(_enum.Enum): # accessible for >=Py3.8
    """
    @lifetime >= 0.3.26rc1 [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)
    """
    
class Flag(_enum.Flag): # accessible for >=Py3.8
    """
    @lifetime >= 0.3.26rc1 [`enum.Flag`](https://docs.python.org/3/library/enum.html#enum.Flag)
    """
    
class ReprEnum(Enum): # >=Py3.11; practically subclass of enum.Enum and nothing in the body. Try to define for least than Py3.11
    """
    @lifetime >= 0.3.26rc1 [`enum.ReprEnum`](https://docs.python.org/3/library/enum.html#enum.ReprEnum)
    """

if _sys.version_info >= (3, 11):
    
    from enum import verify as verify, EnumCheck as EnumCheck, EnumType as EnumType
    
    # If not the same (as before 3.13 it can occur), we need to ensure they are the same by using type assignment
    try:
        assert ReprEnum == _enum.ReprEnum
        
    except AssertionError:
        ReprEnum = _enum.ReprEnum
        
        
class EnumDict(Enum): # base class ignored after assignment below
    """
    @lifetime >= 0.3.26rc1 [`enum.EnumDict`](https://docs.python.org/3/library/enum.html#enum.EnumDict)
    
    Undocumented internal class `enum._EnumDict` before Python 3.13
    """
    
if _sys.version_info >= (3, 13):
    EnumDict = _enum.EnumDict
    
else:
    # questionable: since when enum._EnumDict was in enum.py file?
    if _sys.version_info >= (3, 4):
        EnumDict = _enum._EnumDict
        
    else:
        EnumDict = None
    
class FlagBoundary(Enum): # >=Py3.11. Define for least than Py3.11
    """
    @lifetime >= 0.3.26rc1 [`enum.FlagBoundary`](https://docs.python.org/3/library/enum.html#enum.FlagBoundary)
    
    Control how out of range values are handled.
    
    `STRICT` -> error is raised             (default for `Flag`) \\
    `CONFORM` -> extra bits are discarded \\
    `EJECT` -> lose flag status \\
    `KEEP` -> keep flag status and all bits (default for `IntFlag`)
    """
    STRICT = _enum.auto() # 1; enum.auto accessible for >=Py3.8
    CONFORM = _enum.auto() # 2
    EJECT = _enum.auto() # 3
    KEEP = _enum.auto() # 4

class IntegerFlag(_enum.IntFlag): # accessible for >=Py3.8 (can be recreated via bases: >= Py3.11 (int, ReprEnum, Flag, boundary=FlagBoundary.KEEP), < Py3.11 (int, Flag))
    """
    @lifetime >= 0.3.26rc1. [`enum.IntFlag`](https://docs.python.org/3/library/enum.html#enum.IntFlag)
    """

if _sys.version_info >= (3, 11):
    
    class IntegerEnum(_enum.IntEnum):
        """
        @lifetime >= 0.3.26rc1. [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
        """
        
    class StringEnum(_enum.StrEnum):
        """
        @lifetime >= 0.3.26rc1. [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)
        """
        
else:
    
    class IntegerEnum(int, ReprEnum):
        """
        @lifetime >= 0.3.26rc1. [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
        """
        
    class StringEnum(str, ReprEnum):
        """
        @lifetime >= 0.3.26rc1. [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)
        """
        
        def __new__(cls, *values):
            "values must already be of type `str`"
            if len(values) > 3:
                raise TypeError('too many arguments for str(): %r' % (values, ))
            if len(values) == 1:
                # it must be a string
                if not isinstance(values[0], str):
                    raise TypeError('%r is not a string' % (values[0], ))
            if len(values) >= 2:
                # check that encoding argument is a string
                if not isinstance(values[1], str):
                    raise TypeError('encoding must be a string, not %r' % (values[1], ))
            if len(values) == 3:
                # check that errors argument is a string
                if not isinstance(values[2], str):
                    raise TypeError('errors must be a string, not %r' % (values[2]))
            value = str(*values)
            member = str.__new__(cls, value)
            member._value_ = value
            return member

        @staticmethod
        def _generate_next_value_(name, start, count, last_values):
            """
            Return the lower-cased version of the member name.
            """
            return name.lower()
        
### UTILITY TYPES ###

if _sys.version_info >= (3, 5):
    from typing import (
        Generic as Generic, # 0.3.26b3
        Optional as Optional, # 0.3.26rc1
        Union as Union # 0.3.26rc1
    )
    
else:
    from typing_extensions import (
        Generic as Generic, # 0.3.26b3
        Optional as Optional, # 0.3.26rc1
        Union as Union # 0.3.26rc1
    )

if _sys.version_info >= (3, 5, 2):
    from typing import TYPE_CHECKING as TYPE_CHECKING # 0.3.37
else:
    from typing_extensions import TYPE_CHECKING as TYPE_CHECKING # 0.3.37
    

if _sys.version_info >= (3, 5, 3):
    from typing import ClassVar as ClassVar # 0.3.26b3
else:
    from typing_extensions import ClassVar as ClassVar # 0.3.26b3


if _sys.version_info >= (3, 6, 2):
    from typing import NoReturn as NoReturn # 0.3.26b3
else:
    from typing_extensions import NoReturn as NoReturn # 0.3.26b3

if _sys.version_info >= (3, 7):
    
    # uuid.SafeUUID (>= Py3.7) is decorated by internal decorator enum._simple_enum(enum.Enum),
    # but we will use inheritance for backward-compatibility.
    
    from uuid import SafeUUID as SafeUUID
    
else:
    
    class SafeUUID(_enum.Enum):
        safe = 0
        unsafe = -1
        unknown = None

if _sys.version_info >= (3, 7, 4):
    from typing import ForwardRef as ForwardRef # 0.3.26rc3
else:
    from typing_extensions import ForwardRef as ForwardRef # 0.3.26rc3


if _sys.version_info >= (3, 8):
    
    from typing import (
        Final as Final, # 0.3.26rc1
        Protocol as Protocol, # 0.3.26rc1
        TypedDict as TypedDict, # 0.3.37
    )
    
    from types import CellType as CellType # 0.3.37
    
else:
    from typing_extensions import (
        Final as Final, # 0.3.26rc1
        Protocol as Protocol, # 0.3.26rc1
        TypedDict as TypedDict, # 0.3.37
    )
    
# 0.3.42: Inspect type subscription with abstract base classes from 'collections.abc'
# 0.3.46: Inspect type substription with inbuilt classes from 'builtins' in submodule '{thisModuleParent}._subscript_builtins'
# 0.3.52: Migrate inbuilt classes there; types with AVT_ prefix only have purpose for typing, more specifically, subscripting.
# These change when going since or below Python 3.9. Some generic classes can throw errors when inspecting them in isinstance()
# or issubclass(), hence ordinarily classes without AVT_ prefix are exported.
if _sys.version_info >= (3, 9):
    
    # do not remove these unused imports!
    
    from builtins import (
        dict as AVT_Dict, # pyright: ignore[reportUnusedImport]
        frozenset as AVT_FrozenSet, # pyright: ignore[reportUnusedImport]
        list as AVT_List, # pyright: ignore[reportUnusedImport]
        set as AVT_Set, # pyright: ignore[reportUnusedImport]
        tuple as AVT_Tuple, # pyright: ignore[reportUnusedImport]
        type as AVT_Type # pyright: ignore[reportUnusedImport]
    )
    
    from collections import (
        ChainMap as AVT_ChainMap, # pyright: ignore[reportUnusedImport]
        Counter as AVT_Counter,  # pyright: ignore[reportUnusedImport]
        OrderedDict as AVT_OrderedDict, # pyright: ignore[reportUnusedImport]
        defaultdict as AVT_DefaultDict, # pyright: ignore[reportUnusedImport]
        deque as AVT_Deque # pyright: ignore[reportUnusedImport]
    )
    
    from collections.abc import (
        AsyncGenerator as AVT_AsyncGenerator, # pyright: ignore[reportUnusedImport]
        AsyncIterable as AVT_AsyncIterable, # pyright: ignore[reportUnusedImport]
        AsyncIterator as AVT_AsyncIterator, # pyright: ignore[reportUnusedImport]
        Awaitable as AVT_Awaitable, # pyright: ignore[reportUnusedImport]
        Callable as AVT_Callable, # pyright: ignore[reportUnusedImport]
        Collection as AVT_Collection, # pyright: ignore[reportUnusedImport]
        Container as AVT_Container, # pyright: ignore[reportUnusedImport]
        Coroutine as AVT_Coroutine, # pyright: ignore[reportUnusedImport]
        Generator as AVT_Generator, # pyright: ignore[reportUnusedImport]
        ItemsView as AVT_ItemsView, # pyright: ignore[reportUnusedImport]
        Iterable as AVT_Iterable, # pyright: ignore[reportUnusedImport]
        Iterator as AVT_Iterator, # pyright: ignore[reportUnusedImport]
        KeysView as AVT_KeysView, # pyright: ignore[reportUnusedImport]
        Mapping as AVT_Mapping, # pyright: ignore[reportUnusedImport]
        MappingView as AVT_MappingView, # pyright: ignore[reportUnusedImport]
        MutableMapping as AVT_MutableMapping, # pyright: ignore[reportUnusedImport]
        MutableSequence as AVT_MutableSequence, # pyright: ignore[reportUnusedImport]
        MutableSet as AVT_MutableUniqual, # pyright: ignore[reportUnusedImport]
        Reversible as AVT_Reversible, # pyright: ignore[reportUnusedImport]
        Sequence as AVT_Sequence, # pyright: ignore[reportUnusedImport]
        Set as AVT_Uniqual, # pyright: ignore[reportUnusedImport]
        ValuesView as AVT_ValuesView # pyright: ignore[reportUnusedImport]
    )
    
    from contextlib import (
        AbstractAsyncContextManager as AVT_AsyncContextManager, # pyright: ignore[reportUnusedImport] ## >= 0.3.53
        AbstractContextManager as AVT_ContextManager # pyright: ignore[reportUnusedImport] ## >= 0.3.53
    )
    
    from re import (
        Match as AVT_Match, # pyright: ignore[reportUnusedImport]
        Pattern as AVT_Pattern # pyright: ignore[reportUnusedImport]
    )
    
    from typing import (
        IO as IO,
        Annotated as Annotated, # 0.3.26rc1
        BinaryIO as BinaryIO, # 0.3.26rc3
        TextIO as TextIO # 0.3.26rc3
    )
    
    from types import GenericAlias as GenericAlias # 0.3.37
    
else:
    
    from typing import (
        
        Dict as AVT_Dict, # pyright: ignore[reportUnusedImport]
        FrozenSet as AVT_FrozenSet, # pyright: ignore[reportUnusedImport]
        List as AVT_List, # pyright: ignore[reportUnusedImport]
        Set as AVT_Set, # pyright: ignore[reportUnusedImport]
        Tuple as AVT_Tuple, # pyright: ignore[reportUnusedImport]
        Type as AVT_Type, # pyright: ignore[reportUnusedImport]
        
        ChainMap as AVT_ChainMap, # pyright: ignore[reportUnusedImport]
        Counter as AVT_Counter,  # pyright: ignore[reportUnusedImport]
        OrderedDict as AVT_OrderedDict, # pyright: ignore[reportUnusedImport]
        DefaultDict as AVT_DefaultDict, # pyright: ignore[reportUnusedImport]
        Deque as AVT_Deque, # pyright: ignore[reportUnusedImport]
        
        AsyncGenerator as AVT_AsyncGenerator, # pyright: ignore[reportUnusedImport]
        AsyncIterable as AVT_AsyncIterable, # pyright: ignore[reportUnusedImport]
        AsyncIterator as AVT_AsyncIterator, # pyright: ignore[reportUnusedImport]
        Awaitable as AVT_Awaitable, # pyright: ignore[reportUnusedImport]
        Callable as AVT_Callable, # pyright: ignore[reportUnusedImport]
        Collection as AVT_Collection, # pyright: ignore[reportUnusedImport]
        Container as AVT_Container, # pyright: ignore[reportUnusedImport]
        Coroutine as AVT_Coroutine, # pyright: ignore[reportUnusedImport]
        Generator as AVT_Generator, # pyright: ignore[reportUnusedImport]
        ItemsView as AVT_ItemsView, # pyright: ignore[reportUnusedImport]
        Iterable as AVT_Iterable, # pyright: ignore[reportUnusedImport]
        Iterator as AVT_Iterator, # pyright: ignore[reportUnusedImport]
        KeysView as AVT_KeysView, # pyright: ignore[reportUnusedImport]
        Mapping as AVT_Mapping, # pyright: ignore[reportUnusedImport]
        MappingView as AVT_MappingView, # pyright: ignore[reportUnusedImport]
        MutableMapping as AVT_MutableMapping, # pyright: ignore[reportUnusedImport]
        MutableSequence as AVT_MutableSequence, # pyright: ignore[reportUnusedImport]
        MutableSet as AVT_MutableUniqual, # pyright: ignore[reportUnusedImport]
        Reversible as AVT_Reversible, # pyright: ignore[reportUnusedImport]
        Sequence as AVT_Sequence, # pyright: ignore[reportUnusedImport]
        Set as AVT_Uniqual, # pyright: ignore[reportUnusedImport]
        ValuesView as AVT_ValuesView, # pyright: ignore[reportUnusedImport]
        
        AsyncContextManager as AVT_AsyncContextManager, # pyright: ignore[reportUnusedImport]
        ContextManager as AVT_ContextManager, # pyright: ignore[reportUnusedImport]
        
        Match as AVT_Match, # pyright: ignore[reportUnusedImport]
        Pattern as AVT_Pattern # pyright: ignore[reportUnusedImport]
    )
    
    from typing_extensions import (
        IO as IO,
        Annotated as Annotated, # 0.3.26rc1
        BinaryIO as BinaryIO, # 0.3.26rc3
        TextIO as TextIO # 0.3.26rc3
    )

if _sys.version_info >= (3, 10):
    
    from typing import (
        ParamSpec as ParamSpec, # 0.3.26rc1
        ParamSpecArgs as ParamSpecArgs, # 0.3.26rc1
        ParamSpecKwargs as ParamSpecKwargs, # 0.3.26rc1
        TypeGuard as TypeGuard, # 0.3.26rc1
        TypeAlias as TypeAlias, # 0.3.26rc1
        Concatenate as Concatenate, # 0.3.26rc1
        is_typeddict as is_typeddict, # 0.3.37
        get_args as get_args, # 0.3.26rc1 (renamed 0.3.34 from `getArgs`)
        get_origin as get_origin # 0.3.37
    )
    
    from types import (
        UnionType as UnionType, # 0.3.37
        EllipsisType as EllipsisType,
        NotImplementedType as NotImplementedType, # 0.3.37
        NoneType as NoneType # 0.3.26
    )
    
    from inspect import get_annotations as get_annotations # 0.3.37
else:
    
    from typing_extensions import (
        ParamSpec as ParamSpec, # 0.3.26rc1
        ParamSpecArgs as ParamSpecArgs, # 0.3.26rc1
        ParamSpecKwargs as ParamSpecKwargs, # 0.3.26rc1
        TypeGuard as TypeGuard, # 0.3.26rc1
        TypeAlias as TypeAlias, # 0.3.26rc1
        Concatenate as Concatenate, # 0.3.26rc1
        is_typeddict as is_typeddict, # 0.3.37
        final as _final,
        get_args as get_args, # 0.3.26rc1 (renamed 0.3.34 from `getArgs`)
        get_origin as get_origin # 0.3.37
    )
    
    NotImplementedType = type(NotImplemented) # >= 0.3.52
    
    # warrant usage for Py3.8 and Py3.9
    @_final
    class NoneType:
        "@lifetime >= 0.3.26"
        def __bool__(self) -> Literal[False]: ...
        
    @_final
    class EllipsisType: ...
        
    NoneType = cast(NoneType, type(None))
    EllipsisType = cast(EllipsisType, type(Ellipsis))
    
    del _final

# Literal (3.8+) bugfix (to 3.10.1); AveyTense 0.3.40
if _sys.version_info >= (3, 10, 1):
    from typing import Literal as Literal # 0.3.26rc1
    
else:
    from typing_extensions import Literal as Literal # 0.3.26rc1

if _sys.version_info >= (3, 11):
    
    # AveyTense 0.3.40
    # NewType (3.5.2+): the error message for subclassing instances of NewType was improved on 3.11
    
    from typing import (
        LiteralString as LiteralString, # 0.3.26rc1
        Never as Never, # 0.3.26rc1
        NewType as NewType, # 0.3.26rc1
        Self as Self, # 0.3.26rc1
        Any as Any, # 0.3.26rc1
        NotRequired as NotRequired, # 0.3.26rc1
        Required as Required, # 0.3.26rc1
        assert_never as assert_never, # 0.3.37
        assert_type as assert_type, # 0.3.37
        clear_overloads as clear_overloads, # 0.3.37
        final as final, # 0.3.37
        get_overloads as get_overloads, # 0.3.37
        overload as overload, # 0.3.26rc1
        reveal_type as reveal_type # 0.3.37
    )
    
else:
    
    from typing_extensions import (
        LiteralString as LiteralString, # 0.3.26rc1
        Never as Never, # 0.3.26rc1
        NewType as NewType, # 0.3.26rc1
        Self as Self, # 0.3.26rc1
        Any as Any, # 0.3.26rc1
        NotRequired as NotRequired, # 0.3.26rc1
        Required as Required, # 0.3.26rc1
        assert_never as assert_never, # 0.3.37
        assert_type as assert_type, # 0.3.37
        clear_overloads as clear_overloads, # 0.3.37
        dataclass_transform as dataclass_transform, # 0.3.37
        final as final, # 0.3.37
        get_overloads as get_overloads, # 0.3.37
        overload as overload, # 0.3.26rc1
        reveal_type as reveal_type # 0.3.37
    )


if _sys.version_info >= (3, 12):
    
    # AveyTense 0.3.40
    # Unpack (3.11+): see PEP 692 (changed the repr of Unpack[])
    # dataclass_transform (3.11+) was lacking frozen_default parameter
    
    from typing import (
        TypeAliasType as TypeAliasType, # 0.3.26rc1
        Unpack as Unpack, # 0.3.26rc1
        dataclass_transform as dataclass_transform, # 0.3.37
        override as override # 0.3.37
    )
    
    from types import get_original_bases as get_original_bases # 0.3.40
    from collections.abc import Buffer as _Buffer # 0.3.37
    from inspect import BufferFlags as BufferFlags # 0.3.26rc2
    
else:
    from typing_extensions import (
        Buffer as _Buffer, # 0.3.37
        TypeAliasType as TypeAliasType, # 0.3.26rc1
        Unpack as Unpack, # 0.3.26rc1
        dataclass_transform as dataclass_transform, # 0.3.37
        override as override # 0.3.37
    )
    
    class BufferFlags(IntegerFlag): # 0.3.26rc2
        SIMPLE = 0x0
        WRITABLE = 0x1
        FORMAT = 0x4
        ND = 0x8
        STRIDES = 0x10 | ND
        C_CONTIGUOUS = 0x20 | STRIDES
        F_CONTIGUOUS = 0x40 | STRIDES
        ANY_CONTIGUOUS = 0x80 | STRIDES
        INDIRECT = 0x100 | STRIDES
        CONTIG = ND | WRITABLE
        CONTIG_RO = ND
        STRIDED = STRIDES | WRITABLE
        STRIDED_RO = STRIDES
        RECORDS = STRIDES | WRITABLE | FORMAT
        RECORDS_RO = STRIDES | FORMAT
        FULL = INDIRECT | WRITABLE | FORMAT
        FULL_RO = INDIRECT | FORMAT
        READ = 0x100
        WRITE = 0x200


if _sys.version_info >= (3, 13):
    
    from warnings import deprecated as deprecated # 0.3.37
    
    # AveyTense 0.3.40
    # TypeVar & TypeVarTuple (3.11+): see PEP 696 ('default' parameter availability checking)
    # NamedTuple (3.5.2+) - backporting all updates of this class
    
    from typing import (
        NamedTuple as NamedTuple, # 0.3.26rc1
        Protocol as Protocol, # 0.3.26rc1
        TypeIs as TypeIs, # 0.3.26rc1
        TypeVar as TypeVar, # 0.3.26b3
        TypeVarTuple as TypeVarTuple, # 0.3.26rc3
        NoDefault as NoDefault, # 0.3.26rc1
        ReadOnly as ReadOnly, # 0.3.26rc1
        get_protocol_members as get_protocol_members, # 0.3.37
        is_protocol as is_protocol, # 0.3.37
        runtime_checkable as runtime, # pyright: ignore[reportUnusedImport]  # 0.3.26rc1
        runtime_checkable as runtime_checkable
    )
    
else:
    from typing_extensions import (
        deprecated as deprecated, # 0.3.37
        NamedTuple as NamedTuple, # 0.3.26rc1
        Protocol as Protocol, # 0.3.26rc1
        TypeIs as TypeIs, # 0.3.26rc1
        TypeVar as TypeVar, # 0.3.26b3
        TypeVarTuple as TypeVarTuple, # 0.3.26rc3
        NoDefault as NoDefault, # 0.3.26rc1
        ReadOnly as ReadOnly, # 0.3.26rc1
        get_protocol_members as get_protocol_members, # 0.3.37
        is_protocol as is_protocol, # 0.3.37
        runtime_checkable as runtime, # pyright: ignore[reportUnusedImport]  # 0.3.26rc1
        runtime_checkable as runtime_checkable
    )
    
# pending removals as in https://docs.python.org/3/library/typing.html#deprecation-timeline-of-major-features
if _sys.version_info < (3, 14):
    
    from collections.abc import ByteString as ByteString # 0.3.37
    
else:
    
    ByteString = Union[bytes, bytearray, memoryview] # 0.3.37
    
if _sys.version_info < (3, 15):
    
    from typing import no_type_check_decorator as no_type_check_decorator
    noTypeCheckDecorator = no_type_check_decorator # 0.3.26rc1    
    
if _sys.version_info < (3, 18):

    from typing import AnyStr as AnyStr
    
else:
    
    AnyStr = TypeVar("AnyStr", bytes, str)
    
_T = TypeVar("_T")
_T_con = TypeVar("_T_con", contravariant = True)
_T_cov = TypeVar("_T_cov", covariant = True)
_AnyStr_cov = TypeVar("_AnyStr_cov", str, bytes, covariant = True)
_KT_con = TypeVar("_KT_con", contravariant = True)
_KT_cov = TypeVar("_KT_cov", covariant = True)
_VT_cov = TypeVar("_VT_cov", covariant = True)
_P = ParamSpec("_P")

# 0.3.52
# These both local variables below hold special names that Python uses in lambda and generator expressions.
# We use this way to ensure the change with this attribute's value will happen simultaneously with AveyTense.
_LambdaName = (lambda: None).__name__ # "<lambda>"
_GenExprName = (i for i in (1,)).__qualname__ # "<genexpr>"

class _GenExprTypeMeta(type):
    """@lifetime >= 0.3.52"""
    def __instancecheck__(self, obj: object):
        return isinstance(obj, Generator) and obj.__qualname__.endswith(_GenExprName)

class _LambdaTypeMeta(type):
    """@lifetime >= 0.3.52"""
    def __instancecheck__(self, obj: object):
        return isinstance(obj, FunctionType) and obj.__name__.endswith(_LambdaName)

class GenExprType(metaclass = _GenExprTypeMeta):
    """
    @lifetime >= 0.3.52
    
    Use this class to find, if a generator object is actually created from generator expression, with `isinstance()`.
    """
    __init__ = None
    
class LambdaType(metaclass = _LambdaTypeMeta):
    """
    @lifetime >= 0.3.44 \\
    @modified 0.3.52
    
    Use this class to find, if a callable is actually a lambda expression, with `isinstance()`.
    
    NOTE: this class isn't the same as Python's `types.LambdaType`, and it is reserved for `isinstance()` only
    """
    if False: # projected
        def __new__(
            cls,
            code: CodeType,
            globals: AVT_Dict[str, Any],
            argdefs: Optional[AVT_Tuple[object, ...]] = None,
            closure: Optional[AVT_Tuple[CellType, ...]] = None,
            kwdefaults: Optional[AVT_Dict[str, object]] = None
        ):
            # using assumption 'types.LambdaType' is type alias to 'types.FunctionType',
            # return 'types.FunctionType', just without the 'name' parameter required
            return FunctionType(code, globals, _LambdaName, argdefs, closure, kwdefaults)
    else:
        __init__ = None
    
class _SpecialFormMeta(type):
    """@lifetime >= 0.3.52"""
    def __instancecheck__(self, obj: object): # 0.3.53: enhance type checking
        
        from typing import _SpecialForm
        from typing_extensions import _SpecialForm as _ExtSpecialForm
        
        # since 3.13 'typing.Annotated' is instance of 'typing._SpecialForm'
        if _sys.version_info >= (3, 13):
            return isinstance(obj, (_SpecialForm, _ExtSpecialForm))
        else:
            return isinstance(obj, (_SpecialForm, _ExtSpecialForm)) or obj is Annotated
        
        """elif _sys.version_info >= (3, 11):
            return isinstance(obj, _SpecialForm) or obj in (Annotated,)
        
        else:
            return isinstance(obj, _SpecialForm) or obj in (Annotated, Self, Never, LiteralString)"""
    
# Let's be honest, I was having trouble re-creating these classes with type annotations.
# In reality none of these are protocols, because these get appropriate values assigned later,
# these definitions are only for correct type hinting
class AnyMeta(Protocol):
    """@lifetime >= 0.3.52"""
    def __instancecheck__(self, obj: object) -> bool: ...
    def __repr__(self) -> str: ...
    
@final
class DictKeys(AVT_KeysView[_KT_cov], Generic[_KT_cov, _VT_cov]):
    """
    @lifetime >= 0.3.53
    
    Generic version of class `_collections_abc.dict_keys` (generic only on stub files)
    """
    def __eq__(self, value: object, /) -> bool: ...
    def __reversed__(self) -> AVT_Iterator[_KT_cov]: ...
    __hash__: ClassVar[None]  # type: ignore[assignment]
    if _sys.version_info >= (3, 13):
        def isdisjoint(self, other: AVT_Iterable[_KT_cov], /) -> bool: ...
    if _sys.version_info >= (3, 10):
        @property
        def mapping(self) -> MappingProxyType[_KT_cov, _VT_cov]: ...

@final
class DictValues(AVT_ValuesView[_VT_cov], Generic[_KT_cov, _VT_cov]):
    """
    @lifetime >= 0.3.53
    
    Generic version of class `_collections_abc.dict_values` (generic only on stub files)
    """
    def __reversed__(self) -> AVT_Iterator[_VT_cov]: ...
    if _sys.version_info >= (3, 10):
        @property
        def mapping(self) -> MappingProxyType[_KT_cov, _VT_cov]: ...

@final
class DictItems(AVT_ItemsView[_KT_cov, _VT_cov]):
    """
    @lifetime >= 0.3.53
    
    Generic version of class `_collections_abc.dict_items` (generic only on stub files)
    """
    def __eq__(self, value: object, /) -> bool: ...
    def __reversed__(self) -> AVT_Iterator[AVT_Tuple[_KT_cov, _VT_cov]]: ...
    __hash__: ClassVar[None]  # type: ignore[assignment]
    if _sys.version_info >= (3, 13):
        def isdisjoint(self, other: AVT_Iterable[AVT_Tuple[_KT_cov, _VT_cov]], /) -> bool: ...
    if _sys.version_info >= (3, 10):
        @property
        def mapping(self) -> MappingProxyType[_KT_cov, _VT_cov]: ...
    
class ProtocolMeta(Protocol):
    """@lifetime >= 0.3.52"""
    __protocol_attrs__: ClassVar[AVT_Set[str]]
    def __init__(cls, *args: Any, **kwargs: Any) -> None: ...
    def __new__(
        mcls: AVT_Type[Self],
        name: str,
        bases: AVT_Tuple[type, ...],
        namespace: AVT_Dict[str, Any],
        /,
        **kwargs: Any
    ) -> Self: ...
    def __subclasscheck__(self, cls: type) -> bool: ...
    def __instancecheck__(self, obj: object) -> bool: ...
    
class SpecialForm(metaclass = _SpecialFormMeta):
    """
    @lifetime >= 0.3.52
    
    Use this class to find, if a type is actually a special form from `typing`
    """
    
class TypedDictMeta(Protocol):
    """@lifetime >= 0.3.52"""
    def __new__(cls, typename: str, fields: AVT_Dict[str, Any] = {}, /, *, total: bool = True) -> Self: ...
    
class TypingNoDefaultType:
    """@lifetime >= 0.3.53"""
    
class TypingTupleType(tuple):
    """
    @lifetime >= 0.3.53
    
    Get internal class for deprecated type alias `typing.Tuple` (inaccessible via mere `tuple`)
    """
    
class TypingBaseGenericType(Protocol):
    """@lifetime >= 0.3.53"""
    __slots__: None
    _name: Optional[str] # ?
    _inst: bool # ?
    @property
    def __origin__(self) -> Union[type, TypeAliasType]: ...
    def __init__(self, origin: type, args: AVT_Tuple[Any, ...], *, inst: bool = True, name = None) -> None: ...
    def __dir__(self) -> AVT_List[str]: ...
    def __instancecheck__(self, obj: object) -> bool: ...
    def __subclasscheck__(self, cls: type) -> NoReturn: ...
    def __setattr__(self, attr: str, val: Any) -> None: ...
    def __getattr__(self, attr: str) -> Any: ...
    def __mro_entries__(self, bases: AVT_Iterable[object]) -> AVT_Tuple[type, ...]: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ... 

class TypingGenericType(TypingBaseGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for generic aliases before `types.GenericAlias` (>=Py3.9)
    """
    @property
    def __origin__(self) -> Union[type, TypeAliasType]: ...
    @property
    def __args__(self) -> AVT_Tuple[Any, ...]: ...
    @property
    def __parameters__(self) -> AVT_Tuple[Any, ...]: ...
    def __init__(self, origin: type, args: AVT_Tuple[Any, ...], *, inst: bool = True, name = None) -> None: ...
    def __eq__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...
    if _sys.version_info >= (3, 10):
        def __or__(self, other: type) -> UnionType: ...
        def __ror__(self, other: type) -> UnionType: ...
    else:
        def __or__(self, other: type) -> TypingUnionType: ...
        def __ror__(self, other: type) -> TypingUnionType: ...
    def __getitem__(self, args: Any) -> Self: ...
    def __repr__(self) -> str: ...
    def __iter__(self) -> AVT_Generator[Any, Any, None]: ...
    def __reduce__(self) -> AVT_Tuple[Any, ...]: ...
    def copy_with(self, args: Any) -> Self: ...
    def _determine_new_args(self, args: Any) -> AVT_Tuple[Any, ...]: ...
    def _make_substitution(self, args: AVT_Iterable[type], new_arg_by_param: Any) -> AVT_List[Any]: ...
    ### inherited from typing._BaseGenericAlias ###
    _name: Optional[str] # ?
    _inst: bool # ?
    def __dir__(self) -> AVT_List[str]: ...
    def __instancecheck__(self, obj: object) -> bool: ...
    def __subclasscheck__(self, cls: type) -> NoReturn: ...
    def __setattr__(self, attr: str, val: Any) -> None: ...
    def __getattr__(self, attr: str) -> Any: ...
    def __mro_entries__(self, bases: AVT_Iterable[object]) -> AVT_Tuple[type, ...]: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...    

class TypingAnnotatedType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Annotated` class
    """
    __iter__: None
    @property
    def __origin__(self) -> Union[type, TypeAliasType]: ...
    @property
    def __metadata__(self) -> Any: ...
    def __init__(self, origin: type, metadata: Any) -> None: ...
    def __repr__(self) -> str: ...
    def __reduce__(self) -> AVT_Tuple[Any, ...]: ...
    def __eq__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...
    def __getattr__(self, attr: str) -> Any: ...
    def __mro_entries__(self, bases: AVT_Iterable[object]) -> AVT_Tuple[type, ...]: ...
    def copy_with(self, args: Any) -> Self: ...
    
class TypingCallableType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `collections.abc.Callable` class
    """
    __iter__: None
    def __repr__(self) -> str: ...
    def __reduce__(self) -> AVT_Tuple[Any, ...]: ...
    
class TypingConcatenateType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Concatenate` class
    """
    def copy_with(self, args: Any) -> Self: ...
    
class TypingLiteralType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Literal` class
    """
    def __eq__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...
    
class TypingUnionType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Union` class
    """
    __iter__: None
    def __eq__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __reduce__(self) -> AVT_Tuple[Any, ...]: ...
    def __instancecheck__(self, obj: object) -> bool: ...
    def __subclasscheck__(self, cls: type) -> bool: ...
    def copy_with(self, args: Any) -> Self: ...
    
class TypingUnpackType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Unpack` class
    """
    def __repr__(self) -> str: ...
    def __getitem__(self, args: Any) -> Self: ...
    @property
    def __typing_unpacked_tuple_args__(self) -> Optional[AVT_Tuple[Any, ...]]: ...
    @property
    def __typing_is_unpacked_typevartuple__(self) -> bool: ...
    
import _collections_abc, _hashlib, hashlib, hmac as _hmac, typing as _typing, typing_extensions as _typing_ext

cached_property = cachedproperty

AnnotationForm = Any # 0.3.48; _typeshed.AnnotationForm
AnyMeta = cast(AnyMeta, type(Any)) # >= 0.3.52

if False: # < 0.3.52
    Callback = Callable # 0.3.26b3
    Containable = Container # >= 0.3.26rc1
    Invocable = Callable # >= 0.3.26rc1
    SpecVar = ParamSpec
    SpecVarArgs = ParamSpecArgs
    SpecVarKwargs = ParamSpecKwargs
    TypeTupleVar = TypeVarTuple
    
Hash = _hashlib.HASH # >= 0.3.44

# 0.3.53: '_hashlib.HASHXOF' undefined before Python 3.9
if _sys.version_info >= (3, 9): 
    Hashxof = _hashlib.HASHXOF # >= 0.3.44
else:
    Hashxof = type(hashlib.shake_128()) # >= 0.3.44

Hmac = _hmac.HMAC # >= 0.3.44
InComparable = AVT_Container # >= 0.3.26rc1
Interface = Protocol # >= 0.3.44
LenOperable = Sized # >= 0.3.26rc1
Pack = Concatenate
ProtocolMeta = cast(ProtocolMeta, type(Protocol)) # >= 0.3.52
ReadableBuffer = _Buffer # >= 0.3.44; refer to _typeshed.ReadableBuffer
ReadOnlyBuffer = _Buffer # >= 0.3.44; refer to _typeshed.ReadOnlyBuffer
Sizeable = Sized # >= 0.3.26rc3
TypedDictMeta = cast(TypedDictMeta, type(TypedDict("a", {}))) # >= 0.3.52

# typing >= Py3.14?; typing_extensions >= 4.13.0 (<= 4.13.2 for Python 3.8)
if hasattr(_typing_ext, "TypeForm"): 
    # >= 0.3.52
    TypeForm = _typing_ext.TypeForm # type: ignore 

TypingAnnotatedType = cast(TypingAnnotatedType, type(Annotated[int, "$"])) # >= 0.3.52
TypingBaseGenericType = cast(TypingBaseGenericType, type(TypeGuard[int]).__base__) # >= 0.3.53

# Python 3.8 returns 'typing._GenericAlias', since Python 3.9 returned type is independent
TypingCallableType = cast(TypingCallableType, type(AVT_Callable[..., Any])) # >= 0.3.52

# 0.3.53: Before Python 3.11, it is a TypeError for missing 'typing.ParamSpec' at the end of type parameters list
# 0.3.52 used ellipsis instead
TypingConcatenateType = cast(TypingConcatenateType, type(Concatenate[int, _P])) # >= 0.3.52

TypingGenericType = cast(TypingGenericType, type(TypeGuard[int])) # >= 0.3.52
TypingLiteralType = cast(TypingLiteralType, type(Literal[""])) # >= 0.3.52
TypingNoDefaultType = cast(TypingNoDefaultType, type(NoDefault)) # >= 0.3.53

# Even if 'typing.Tuple' is deprecated, it actually has an internal class that implements it.
# 'type(tuple)' would return 'type' instead. 'type(tuple[int])' is 'typing._GenericAlias' for Python 3.8
# and 'types.GenericAlias' since Python 3.9
TypingTupleType = cast(TypingTupleType, type(_typing.Tuple)) # >= 0.3.53

# Python 3.8 returns 'typing._GenericAlias', since Python 3.9 returned type is independent
TypingUnionType = cast(TypingUnionType, type(Union[int, str])) # >= 0.3.52

TypingUnpackType = cast(TypingUnpackType, type(Unpack[AVT_Tuple[int, str]])) # >= 0.3.52

Unused = object # >= 0.3.44; refer to _typeshed.Unused
WriteableBuffer = _Buffer # >= 0.3.44; refer to _typeshed.WriteableBuffer

async def _f(): pass
_coroutine = _f()

CoroutineWrapperType = type(_coroutine.__await__()) # >= 0.3.53

_coroutine.close()
del _coroutine
del _collections_abc, _hashlib, hashlib, _hmac, _typing, _typing_ext # not for export!

noTypeCheck = no_type_check # >= 0.3.26rc1
newClass = new_class # >= 0.3.26rc3

# these type aliases are not official; not recommended to use them
StringUnion = Union[_T, str]
"@lifetime >= 0.3.26rc3"
IntegerUnion = Union[_T, int]
"@lifetime >= 0.3.26rc3"
FloatUnion = Union[_T, float]
"@lifetime >= 0.3.26rc3"
ComplexUnion = Union[_T, complex]
"@lifetime >= 0.3.26rc3"
IntegerFloatUnion = Union[_T, int, float]
"@lifetime >= 0.3.26rc3"
IntegerStringUnion = Union[_T, int, str]
"@lifetime >= 0.3.26rc3"
BooleanUnion = Union[_T, bool]
"@lifetime >= 0.3.26rc3"
TrueUnion = Union[_T, Literal[True]]
"@lifetime >= 0.3.26rc3"
FalseUnion = Union[_T, Literal[False]]
"@lifetime >= 0.3.26rc3"
OptionalCallable = Optional[AVT_Callable[_P, _T]]
"@lifetime >= 0.3.26rc3. `typing.Optional[typing.Callable[**P, T]]` = `((**P) -> T) | None`"
AnyCallable = AVT_Callable[..., Any]
"@lifetime >= 0.3.26rc3. `typing.Callable[..., typing.Any]` = `(...) -> Any`"
OptionalUnion = Optional[Union[_T]]
"@lifetime >= 0.3.26rc3. `typing.Optional[typing.Union[T]]`"

### ABSTRACT BASE CLASSES ###
# These from _typeshed.pyi and not in collections.abc

@runtime
class ItemGetter(Protocol[_T_con, _T_cov]): # v = self[key] (type determined by _T_cov)
    """
    @lifetime >= 0.3.26rc3

    An ABC with one method `__getitem__`. Type parameters:
    - first equals type for `key`
    - second equals returned type

    This method is invoked whether we want to get value \\
    via index notation `self[key]`, as instance of the class.
    """
    def __getitem__(self, key: _T_con, /) -> _T_cov: ...

if _sys.version_info >= (3, 9):
    
    @runtime
    class ClassItemGetter(Protocol): # v = self[key] (not instance)
        """
        @lifetime >= 0.3.26rc3

        An ABC with one method `__class_getitem__`. No type parameters.

        This method is invoked whether we want to get value \\
        via index notation `self[key]`, as reference to the class.
        """
        def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...

class SizeableItemGetter(Sizeable, ItemGetter[int, _T_cov]):
    """
    @lifetime >= 0.3.27a3

    An ABC with methods `__len__` and `__getitem__`. Type parameters:
    - first equals returned type for `__getitem__`
    """
    ...

@runtime
class ItemSetter(Protocol[_T_con, _T_cov]): # self[key] = value
    """
    @lifetime >= 0.3.26rc3

    An ABC with one method `__setitem__`. Type parameters:
    - first equals type for `key`
    - second equals type for `value`

    This method is invoked whether we want to set a new value for \\
    specific item accessed by `key`, as `self[key] = value`.
    """
    def __setitem__(self, key: _T_con, value: _T_cov, /) -> None: ...

@runtime
class ItemDeleter(Protocol[_T_con]): # del self[key]
    """
    @lifetime >= 0.3.26rc3

    An ABC with one method `__delitem__`. Type parameters:
    - first equals type for `key`

    This method is invoked whether we want to delete specific item \\
    using `del` keyword as `del self[key]`.
    """
    def __delitem__(self, key: _T_con, /) -> None: ...

@runtime
class Getter(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26

    An ABC with one method `__get__`. Type parameters:
    - first equals returned type
    """
    def __get__(self, instance: object, owner: Optional[type] = None, /) -> _T_cov: ...

@runtime
class Setter(Protocol[_T_con]):
    """
    @lifetime >= 0.3.27a3

    An ABC with one method `__set__`. Type parameters:
    - first equals type for `value`
    """
    def __set__(self, instance: object, value: _T_con, /) -> None: ...
    
@runtime
class Deleter(Protocol):
    """
    @lifetime >= 0.3.44
    
    An ABC with one method `__delete__`. No type parameters.
    """
    def __delete__(self, instance: object, /) -> None: ...
    
class Descriptor(
    Setter[_T_con],
    Getter[_T_cov],
    Deleter
):
    """
    @lifetime >= 0.3.44
    
    An ABC providing descriptor methods: `__get__`, `__set__` and `__delete__`
    """
    ...

@runtime
class FinalDescriptor(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.44
    
    An ABC providing descriptor methods, just `__set__` and `__delete__` throw an error. \\
    The same as `~.util.finalproperty` works.
    """
    def __get__(self, instance: Optional[object], owner: Optional[type] = None, /) -> _T_cov: ...
    def __set__(self, instance: Optional[object], value: Any, /) -> NoReturn: ...
    def __delete__(self, instance: Optional[object], /) -> NoReturn: ...
    

class KeysProvider(ItemGetter[_KT_con, Any]):
    """
    @lifetime >= 0.3.26

    An ABC with one method `keys`. Type parameters:
    - first equals key
    - second equals value
    """
    def keys(self) -> Iterable[_KT_con]: ...

@runtime
class ItemsProvider(Protocol[_KT_cov, _VT_cov]):
    """
    @lifetime >= 0.3.26

    An ABC with one method `items`. Type parameters:
    - first equals key
    - second equals value
    """
    def items(self) -> Uniqual[tuple[_KT_cov, _VT_cov]]: ...
    
@runtime
class Buffer(Protocol):
    """
    @lifetime >= 0.3.44
    
    An ABC with one method `__buffer__`.
    """
    def __buffer__(self, flags: int, /) -> memoryview: ...
    
Buffer = _Buffer

@runtime
class BufferReleaser(Protocol):
    """
    @lifetime >= 0.3.26

    An ABC with one method `__release_buffer__`.
    """
    def __release_buffer__(self, buffer: memoryview, /) -> None: ...
    
@runtime
class BufferManager(Protocol):
    """
    @lifetime >= 0.3.44
    
    An ABC with methods for buffer management.
    """
    def __buffer__(self, flags: int, /) -> memoryview: ...
    def __release_buffer__(self, buffer: memoryview, /) -> None: ...

@runtime
class NewArgumentsGetter(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26

    An ABC with one method `__getnewargs__`. Type parameters:
    - first equals type for returned tuple
    """
    def __getnewargs__(self) -> AVT_Tuple[_T_cov]: ...

class ItemManager(
    ItemGetter[_T_con, _T_cov],
    ItemSetter[_T_con, _T_cov],
    ItemDeleter[_T_con]
):
    """
    @lifetime >= 0.3.26rc3

    An ABC with following methods:
    - `__getitem__` - two type parameters (key type, return type)
    - `__setitem__` - two type parameters (key type, return type)
    - `__delitem__` - one type parameter (key type)
    """
    ...

@runtime
class SubclassHooker(Protocol):
    """
    @lifetime >= 0.3.26

    An ABC with one method `__subclasshook__`. No type parameters.

    Description: \\
    "Abstract classes can override this to customize `issubclass()`. \\
    This is invoked early on by `abc.ABCMeta.__subclasscheck__()`. \\
    It should return True, False or NotImplemented. If it returns \\
    NotImplemented, the normal algorithm is used. Otherwise, it \\
    overrides the normal algorithm (and the outcome is cached)."
    """
    def __subclasshook__(cls, subclass: type, /) -> bool: ...

@runtime
class LengthHintProvider(Protocol):
    """
    @lifetime >= 0.3.26rc3

    An ABC with one method `__length_hint__`. No type parameters.

    This method is invoked like in case of `list` built-in, just on behalf of specific class. \\
    It should equal invoking `len(self())`, as seen for `list`: "Private method returning \\
    an estimate of `len(list(it))`". Hard to explain this method, still, this class will be kept. 
    """
    def __length_hint__(self) -> int: ...

@runtime
class FSPathProvider(Protocol[_AnyStr_cov]):
    """
    @lifetime >= 0.3.27a3. See also [`os.PathLike`](https://docs.python.org/3/library/os.html#os.PathLike)

    An ABC with one method `__fspath__`. Type parameter \\
    needs to be either `str` or `bytes` unrelated to both. \\
    That type is returned via this method.
    """
    def __fspath__(self) -> _AnyStr_cov: ...

@runtime
class BytearrayConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc3

    An unofficial ABC with one method `__bytearray__`, which *has* to equal invoking `bytearray(self)`.
    """
    def __bytearray__(self) -> bytearray: ...

@runtime
class ListConvertible(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc3

    An unofficial ABC with one method `__tlist__` (before 0.3.27a3 - `__list__`), which *has* to equal invoking `list(self)`. \\
    Returned list type is addicted to covariant type parameter.
    """
    
    def __tlist__(self) -> AVT_List[_T_cov]:
        "@lifetime >= 0.3.26rc3. Return `list(self)`"
        ...

@runtime
class TupleConvertible(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc3

    An unofficial ABC with one method `__ttuple__` (before 0.3.27a3 - `__tuple__`), which *has* to equal invoking `tuple(self)`. \\
    Returned tuple type is addicted to covariant type parameter.
    """
    
    def __ttuple__(self) -> AVT_Tuple[_T_cov, ...]:
        "@lifetime >= 0.3.26rc3. Return `tuple(self)`"
        ...

@runtime
class SetConvertible(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc3

    An unofficial ABC with one method `__tset__` (before 0.3.27a3 - `__set_init__`), which *has* to equal invoking `set(self)`. \\
    Returned set type is addicted to covariant type parameter.
    """
    
    def __tset__(self) -> AVT_Set[_T_cov]:
        "@lifetime >= 0.3.26rc3. Return `set(self)`"
        ...

@runtime
class ReckonOperable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An unofficial ABC with one method `__reckon__`, which equals `aveytense.reckon(self)`. \\
    Returned type is always an integer.
    """
    def __reckon__(self) -> int:
        """
        @lifetime >= 0.3.26rc1

        Return `reckon(self)`.
        """
        ...

@runtime
class Absolute(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__abs__`, which equals invoking `abs(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __abs__(self) -> _T_cov: ...

@runtime
class Truncable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__trunc__`, which equals invoking `math.trunc(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __trunc__(self) -> _T_cov: ...

@runtime
class BooleanConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__bool__` which equals invoking `bool(self)`.
    """
    def __bool__(self) -> bool: ...
    
    if _sys.version_info < (0, 3, 44): # __nonzero__ is only on Py2
        def __nonzero__(self) -> bool: ...

@runtime
class IntegerConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__int__`, which equals invoking `int(self)`
    """
    def __int__(self) -> int: ...

@runtime
class FloatConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__float__`, which equals invoking `float(self)`
    """
    def __float__(self) -> float: ...

@runtime
class ComplexConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__complex__`, which equals invoking `complex(self)`
    """
    def __complex__(self) -> complex: ...

@runtime
class BytesConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__bytes__`, which equals invoking `bytes(self)`
    """
    def __bytes__(self) -> bytes: ...

if False: # < 0.3.48
    
    @runtime
    @deprecated("Deprecated since unicode() function doesn't exist. Deprecated since 0.3.41, and will be removed on 0.3.48")
    class UnicodeRepresentable(Protocol):
        """
        @lifetime >= 0.3.26rc3 \\
        @deprecated >= 0.3.41, up for removal on 0.3.48

        An ABC with one method `__unicode__`, which equals invoking `unicode(self)` (Py2)
        """
        def __unicode__(self) -> str: ...

@runtime
class BinaryRepresentable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__bin__`, which equals invoking `bin(self)`.

    In reality there is no such magic method as `__bin__`, but I encourage \\
    Python working team to think about it.
    """
    def __bin__(self) -> str: ...

@runtime
class OctalRepresentable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__oct__`, which equals invoking `oct(self)`
    """
    def __oct__(self) -> str: ...

@runtime
class HexadecimalRepresentable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__hex__`, which equals invoking `hex(self)`
    """
    def __hex__(self) -> str: ...

@runtime
class StringConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__str__`, which equals invoking `str(self)`
    """
    def __str__(self) -> str: ...

@runtime
class Representable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__repr__`, which equals invoking `repr(self)`
    """
    def __repr__(self) -> str: ...

@runtime
class Indexable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__index__`. This allows to use self inside slice expressions, \\
    those are: `slice(self, ..., ...)` and `iterable[self: ... : ...]` (`self` can be \\
    placed anywhere)
    """
    def __index__(self) -> int: ...

@runtime
class Positive(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__pos__`, which equals `+self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __pos__(self) -> _T_cov: ...

@runtime
class Negative(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__neg__`, which equals `-self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __neg__(self) -> _T_cov: ...

@runtime
class Invertible(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__invert__`, which equals `~self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __invert__(self) -> _T_cov: ...

BufferOperable = Buffer
"@lifetime >= 0.3.26rc1. *aveytense.types.Buffer*"

@runtime
class LeastComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Can be compared with `<`
    """
    def __lt__(self, other: _T_con) -> bool: ...

@runtime
class GreaterComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Can be compared with `>`
    """
    def __gt__(self, other: _T_con) -> bool: ...

@runtime
class LeastEqualComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Can be compared with `<=`
    """
    def __le__(self, other: _T_con) -> bool: ...

@runtime
class GreaterEqualComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Can be compared with `>=`
    """
    def __ge__(self, other: _T_con) -> bool: ...

@runtime
class EqualComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26rc1

    Can be compared with `==`
    """
    def __eq__(self, other: _T_con) -> bool: ...

@runtime
class InequalComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26rc1

    Can be compared with `!=`
    """
    def __ne__(self, other: _T_con) -> bool: ...


class Comparable(
    LeastComparable[Any],
    GreaterComparable[Any],
    LeastEqualComparable[Any],
    GreaterEqualComparable[Any],
    EqualComparable[Any],
    InequalComparable[Any],
    InComparable[Any]
):
    """
    @lifetime >= 0.3.26b3

    An ABC supporting any form of comparison with operators \\
    `>`, `<`, `>=`, `<=`, `==`, `!=`, `in` (last 3 missing before 0.3.26rc1)
    """
    ...

class ComparableWithoutIn(
    LeastComparable[Any],
    GreaterComparable[Any],
    LeastEqualComparable[Any],
    GreaterEqualComparable[Any],
    EqualComparable[Any]
):
    """
    @lifetime >= 0.3.27a2

    An ABC same as `Comparable`, but without the `in` keyword support
    """
    ...

@runtime
class BitwiseAndOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__and__`, which equals `self & other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __and__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseOrOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__or__`, which equals `self | other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __or__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseXorOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__xor__`, which equals `self ^ other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __xor__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseLeftOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__lshift__`, which equals `self << other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __lshift__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseRightOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__rshift__`, which equals `self >> other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __lshift__(self, other: _T_con) -> _T_cov: ...

class BitwiseOperable(
    BitwiseAndOperable[Any, Any],
    BitwiseOrOperable[Any, Any],
    BitwiseXorOperable[Any, Any],
    BitwiseLeftOperable[Any, Any],
    BitwiseRightOperable[Any, Any]
):
    """
    @lifetime >= 0.3.26rc1

    Can be used with `&`, `|`, `^`, `<<` and `>>` operators
    """
    ...

@runtime
class BitwiseAndReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__iand__`, which equals `self &= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __iand__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseOrReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__ior__`, which equals `self |= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ior__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseXorReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__ixor__`, which equals `self ^= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ixor__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseLeftReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__ilshift__`, which equals `self <<= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ilshift__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseRightReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__irshift__`, which equals `self >>= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __irshift__(self, other: _T_con) -> _T_cov: ...

class BitwiseReassignable(
    BitwiseAndOperable[Any, Any],
    BitwiseOrOperable[Any, Any],
    BitwiseXorOperable[Any, Any],
    BitwiseLeftReassignable[Any, Any],
    BitwiseRightReassignable[Any, Any]):
    """
    @lifetime >= 0.3.26rc1

    Can be used with `&=`, `|=`, `^=`, `<<=` and `>>=` operators
    """
    ...

class BitwiseCollection(
    BitwiseReassignable,
    BitwiseOperable
):
    """
    @lifetime >= 0.3.26rc1

    Can be used with `&`, `|` and `^` operators, including their \\
    augmented forms: `&=`, `|=` and `^=`, with `~` use following::

        class Example(BitwiseCollection, Invertible[_T]): ...
    """
    ...

class UnaryOperable(Positive[Any], Negative[Any], Invertible[Any]):
    """
    @lifetime >= 0.3.26rc1

    Can be used with `+`, `-` and `~` operators preceding the type
    """
    ...

class Indexed(ItemGetter[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc2
    
    An ABC with one method `__getitem__`, which equals `self[key]`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `key` parameter.
    """
    ...

@runtime
class AsyncNextOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__anext__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __anext__(self) -> Awaitable[_T_cov]: ...

@runtime
class AsyncExitOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__aexit__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __aexit__(self, exc_type: Optional[type[Exception]] = None, exc_value: Optional[Exception] = None, traceback: Optional[TracebackType] = None) -> Awaitable[_T_cov]: ...

@runtime
class AsyncEnterOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__aenter__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __aenter__(self) -> Awaitable[_T_cov]: ...

@runtime
class ExitOperable(Protocol):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__exit__`. Returned type is addicted to covariant type parameter.
    """
    def __exit__(self, exc_type: Optional[type[Exception]] = None, exc_value: Optional[Exception] = None, traceback: Optional[TracebackType] = None) -> bool: ...

@runtime
class EnterOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__enter__`. Returned type is addicted to covariant type parameter.
    """
    def __enter__(self) -> _T_cov: ...

@runtime
class Ceilable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__ceil__`, which equals `ceil(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __ceil__(self) -> _T_cov: ...

@runtime
class Floorable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__floor__`, which equals `floor(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __floor__(self) -> _T_cov: ...

@runtime
class Roundable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__round__`, which equals `round(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __round__(self, ndigits: Optional[int] = None) -> _T_cov: ...

@runtime
class NextOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__next__`, which equals `next(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __next__(self) -> _T_cov: ...

CeilOperable = Ceilable
FloorOperable = Floorable
RoundOperable = Roundable

@runtime
class AdditionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__add__`, which equals `self + other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __add__(self, other: _T_con) -> _T_cov: ...

@runtime
class SubtractionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__sub__`, which equals `self - other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __sub__(self, other: _T_con) -> _T_cov: ...

@runtime
class MultiplicationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__mul__`, which equals `self * other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __mul__(self, other: _T_con) -> _T_cov: ...

@runtime
class MatrixMultiplicationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__matmul__`, which equals `self @ other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __matmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class TrueDivisionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__truediv__`, which equals `self / other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __truediv__(self, other: _T_con) -> _T_cov: ...

@runtime
class FloorDivisionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__floordiv__`, which equals `self // other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __floordiv__(self, other: _T_con) -> _T_cov: ...

@runtime
class DivmodOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__divmod__`, which equals `divmod(self, other)`. \\
    Returned type is addicted to covariant type parameter as the second type parameter \\
    first is type for `other` parameter.
    """
    def __divmod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ModuloOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__mod__`, which equals `self % other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __mod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ExponentiationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__pow__`, which equals `self ** other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __pow__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedAdditionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__radd__`, which equals `other + self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __radd__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedSubtractionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rsub__`, which equals `other - self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rsub__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedMultiplicationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rmul__`, which equals `other * self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedMatrixMultiplicationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rmatmul__`, which equals `other @ self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmatmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedTrueDivisionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rtruediv__`, which equals `other / self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rtruediv__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedFloorDivisionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rfloordiv__`, which equals `other // self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rfloordiv__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedDivmodOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rdivmod__`, which equals `divmod(other, self)`. \\
    Returned type is addicted to covariant type parameter as the second type parameter; \\
    first is type for `other` parameter.
    """
    def __rdivmod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedModuloOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rmod__`, which equals `other % self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedExponentiationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rpow__`, which equals `other ** self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rpow__(self, other: _T_con) -> _T_cov: ...

@runtime
class AdditionReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__iadd__`, which equals `self += other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __iadd__(self, other: _T_con) -> _T_cov: ...

@runtime
class SubtractionReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__isub__`, which equals `self -= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __isub__(self, other: _T_con) -> _T_cov: ...

@runtime
class MultiplicationReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__imul__`, which equals `self *= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imul__(self, other: _T_con) -> _T_cov: ...

@runtime
class MatrixMultiplicationReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__imatmul__`, which equals `self @= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imatmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class TrueDivisionReassingable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__itruediv__`, which equals `self /= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __itruediv__(self, other: _T_con) -> _T_cov: ...

@runtime
class FloorDivisionReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__ifloordiv__`, which equals `self //= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ifloordiv__(self, other: _T_con) -> _T_cov: ...

@runtime
class ModuloReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__imod__`, which equals `self %= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ExponentiationReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__ipow__`, which equals `self **= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ipow__(self, other: _T_con) -> _T_cov: ...

class ReflectedArithmeticOperable(
    ReflectedAdditionOperable[Any, Any],
    ReflectedSubtractionOperable[Any, Any],
    ReflectedMultiplicationOperable[Any, Any],
    ReflectedMatrixMultiplicationOperable[Any, Any],
    ReflectedTrueDivisionOperable[Any, Any],
    ReflectedFloorDivisionOperable[Any, Any],
    ReflectedDivmodOperable[Any, Any],
    ReflectedModuloOperable[Any, Any]
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind (except bitwise) of reflected arithmetic operations with following operators:
    ```
        + - * @ / // % ** divmod
    ```
    where left operand is `other` and right is `self`
    """
    ...

class ArithmeticOperable(
    AdditionOperable[Any, Any],
    SubtractionOperable[Any, Any],
    MultiplicationOperable[Any, Any],
    MatrixMultiplicationOperable[Any, Any],
    TrueDivisionOperable[Any, Any],
    FloorDivisionOperable[Any, Any],
    DivmodOperable[Any, Any],
    ModuloOperable[Any, Any],
    ExponentiationOperable[Any, Any],
    ReflectedArithmeticOperable
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind (except bitwise) of arithmetic operations, including their \\
    reflected equivalents, with following operators:
    ```
        + - * @ / // % ** divmod
    ```
    Both `self` and `other` can be either left or right operands.
    """
    ...

class ArithmeticReassignable(
    AdditionReassignable[Any, Any],
    SubtractionReassignable[Any, Any],
    MultiplicationReassignable[Any, Any],
    MatrixMultiplicationReassignable[Any, Any],
    TrueDivisionReassingable[Any, Any],
    FloorDivisionReassignable[Any, Any],
    ModuloReassignable[Any, Any],
    ExponentiationReassignable[Any, Any]
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind (except bitwise) of augmented/re-assigned arithmetic operations \\
    with following operators:
    ```
        += -= *= @= /= //= %= **=
    ```
    """
    ...

class ArithmeticCollection(
    ArithmeticOperable,
    ArithmeticReassignable
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind (except bitwise) of augmented/re-assigned and normal arithmetic operations \\
    with following operators:
    ```
        + - * @ / // % ** divmod += -= *= @= /= //= %= **=
    ```
    """
    ...

class OperatorCollection(
    ArithmeticCollection,
    BitwiseCollection,
    UnaryOperable,
    Comparable
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind of augmented/re-assigned, reflected and normal arithmetic operations \\
    with following operators:
    ```
        + - * @ / // % ** divmod & | ^ += -= *= @= /= //= %= **= &= |= ^=
    ```
    unary assignment with `+`, `-` and `~`, and comparison with following operators:
    ```
        > < >= <= == != in
    ```
    """
    ...

class LenGetItemOperable(LenOperable, ItemGetter[int, _T_cov]):
    """
    @lifetime >= 0.3.26rc2
    
    An ABC with `__getitem__` and `__len__` methods. Those are typical in sequences.
    """
    ...

@runtime
class Formattable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__format__`, which equals invoking `format(self)`.
    """
    def __format__(self, format_spec: str = "") -> str: ...

@runtime
class Flushable(Protocol): # _typeshed.SupportsFlush
    """
    @lifetime >= 0.3.27b1

    An ABC with one method `flush()`.
    """
    def flush(self) -> object: ...

@runtime
class Writeable(Protocol[_T_con]): # _typeshed.SupportsWrite
    """
    @lifetime >= 0.3.27b1

    An ABC with one method `write()`.
    """
    def write(self, s: _T_con, /) -> object: ...
    

@runtime
class Copyable(Protocol):
    """
    @lifetime >= 0.3.34
    
    An ABC with one method `__copy__`.
    """
    if _sys.version_info >= (0, 3, 43):
        def __copy__(self) -> Self: ...
    
    else:
        def copy(self) -> Self: ... 

@runtime
class DeepCopyable(Protocol):
    """
    @lifetime >= 0.3.43
    
    An ABC with one method `__deepcopy__`.
    """
    def __deepcopy__(self, memo: Optional[dict[int, Any]] = None) -> Self: ...
    
### NEGATIONS ###
    
@runtime
class NotIterable(Protocol):
    """
    @lifetime >= 0.3.26b3

    Cannot be used with `for` loop
    """
    __iter__ = None

@runtime
class NotCallable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.45

    Cannot be called as a function (as `self()`)
    """
    if _sys.version_info >= (0, 3, 45):
        __call__ = None
    
    else:
        def __call__(self, *args, **kwds):
            _E(107)
            
NotInvocable = NotCallable # >= 0.3.26rc1

@runtime
class NotUnaryOperable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    Cannot be used with preceding operators `+`, `-` and `~`
    """
    def __pos__(self):
        _E(108, "")
        
    def __neg__(self):
        _E(108, "")
        
    def __invert__(self):
        _E(108, "")

@runtime
class NotReassignable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    This class does not support any form of re-assignment, those are augmented \\
    assignment operators: `+=`, `-=`, `*=`, `**=`, `/=`, `//=`, `%=`, `>>=`, `<<=`, \\
    `&=`, `|=`, `^=`. Setting new value also is prohibited.
    """
    __slots__ = ("__weakref__",)
    __op = (
        "; used operator '+='", # 0
        "; used operator '-='", # 1
        "; used operator '*='", # 2
        "; used operator '/='", # 3
        "; used operator '//='", # 4
        "; used operator '**='", # 5
        "; used operator '<<='", # 6
        "; used operator '>>='", # 7
        "; used operator '%='", # 8
        "; used operator '&='", # 9
        "; used operator '|='", # 10
        "; used operator '^='", # 11
    )
    
    def __set__(self, i: Self, v: _T_con):
        
        s = " variable that isn't assignable and re-assignable"
        _E(102, s)
            
    def __iadd__(self, o: _T_con):
        i = 0
        _E(102, self.__op[i])
        
    def __isub__(self, o: _T_con):
        i = 1
        _E(102, self.__op[i])
        
    def __imul__(self, o: _T_con):
        i = 2
        _E(102, self.__op[i])
        
    def __ifloordiv__(self, o: _T_con):
        i = 4
        _E(102, self.__op[i])
        
    def __idiv__(self, o: _T_con):
        i = 3
        _E(102, self.__op[i])
        
    def __itruediv__(self, o: _T_con):
        i = 3
        _E(102, self.__op[i])
        
    def __imod__(self, o: _T_con):
        i = 8
        _E(102, self.__op[i])
        
    def __ipow__(self, o: _T_con):
        i = 5
        _E(102, self.__op[i])
        
    def __ilshift__(self, o: _T_con):
        i = 6
        _E(102, self.__op[i])
        
    def __irshift__(self, o: _T_con):
        i = 7
        _E(102, self.__op[i])
        
    def __iand__(self, o: _T_con):
        i = 9
        _E(102, self.__op[i])
        
    def __ior__(self, o: _T_con):
        i = 10
        _E(102, self.__op[i])
        
    def __ixor__(self, o: _T_con):
        i = 11
        _E(102, self.__op[i])

@runtime
class NotComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Cannot be compared with operators `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`
    """
    __slots__ = ()
    __op = (
        "; used operator '<'", # 0
        "; used operator '>'", # 1
        "; used operator '<='", # 2
        "; used operator '>='", # 3
        "; used operator '=='", # 4
        "; used operator '!='", # 5
        "; used operator 'in'", # 6
    )
    def __lt__(self, other: _T_con):
        i = 0
        _E(102, self.__op[i])
        
    def __gt__(self, other: _T_con):
        i = 1
        _E(102, self.__op[i])
        
    def __le__(self, other: _T_con):
        i = 2
        _E(102, self.__op[i])
        
    def __ge__(self, other: _T_con):
        i = 3
        _E(102, self.__op[i])
        
    def __eq__(self, other: _T_con):
        i = 4
        _E(102, self.__op[i])
        
    def __ne__(self, other: _T_con):
        i = 5
        _E(102, self.__op[i])
        
    def __contains__(self, other: _T_con):
        i = 6
        _E(102, self.__op[i])
    
class Allocator:
    """
    @lifetime >= 0.3.27b3

    An allocator class. Classes extending this class have access to `__alloc__` magic method, \\
    but it is advisable to use it wisely.
    """
    __a = bytearray()

    def __init__(self, b: Union[bytearray, BytearrayConvertible], /):
        
        if isinstance(b, BytearrayConvertible):
            self.__a = b.__bytearray__()
            
        elif isinstance(b, bytearray):
            self.__a = b
            
        else:
            error = TypeError("Expected a bytearray object or object of class extending 'BytearrayConvertible' class")
            raise error
    
    def __alloc__(self):
        return self.__a.__alloc__()
    
RichComparable = Union[LeastComparable[Any], GreaterComparable[Any]]

__all__ = sorted([k for k in globals() if not k.startswith("_")])
__abc__ = sorted([k for k in globals() if is_protocol(globals()[k])])
__all_deprecated__ = sorted([k for k in globals() if hasattr(globals()[k], "__deprecated__")]) # 0.3.44

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error
#!/usr/bin/env python3
"""

"""
# Imports:
from __future__ import annotations

# ##-- stdlib imports
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
import types
import collections
import contextlib
import hashlib
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref
import atexit # for @atexit.register
import faulthandler
# ##-- end stdlib imports

from bibtexparser import model
from bibtexparser.library import Library

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final, override, overload

if TYPE_CHECKING:
    from jgdv import Maybe, Either, Result
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from bibble.util import NameParts_d
    from bibtexparser.middlewares import NameParts
    type StringBlock     = model.String
    type Preamble        = model.Preamble
    type Field           = model.Field
    type Block           = model.Block
    type Entry           = model.Entry
    type String          = model.String
    type FailedBlock     = model.ParsingFailedBlock
    type ErrorBlock      = model.MiddlewareErrorBlock
    type CommentBlock    = model.ExplicitComment | model.ImplicitComment
    type UniMiddleware   = Middleware_p | AdaptiveMiddleware_p
    type BidiMiddleware  = BidirectionalMiddleware_p
    type Middleware      = UniMiddleware | BidiMiddleware

    type StrLike         = list|set|String|NameParts_d|NameParts
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:
ALLOW_INPLACE_MOD_K : Final[str] = "allow_inplace_modification"
ALLOW_PARALLEL_K    : Final[str] = "allow_parallel_execution"
LOGGER_K            : Final[str] = "logger"
KEEP_MATH_K         : Final[str] = "keep_math"
ENCLOSE_URLS_K      : Final[str] = "enclose_urls"

TQDM_WIDTH          : Final[int] = 150
##--|
## Enums / Flags

class Capability_f(enum.Flag):
    """ A Flag for where middlewares can be in the read/write stack """

    insist_front = enum.auto()
    insist_end   = enum.auto()
    read_time    = enum.auto()
    write_time   = enum.auto()
    validate     = enum.auto()
    transform    = enum.auto()
    report       = enum.auto()
    dependent    = enum.auto()

##--|
## Bibtexparser protcols

@runtime_checkable
class Library_p(Protocol):
    """ The core methods of a library """

    def add(self, blocks:list[Block], fail_on_duplicate_key:bool = False) -> None: ...

    def remove(self, blocks:list[Block]) -> None: ...

    def replace(self, old_block:Block, new_block:Block, fail_on_duplicate_key:bool=True) -> None: ...

    def blocks(self) -> list[Block]: ...

    def failed_blocks(self) -> list[FailedBlock]: ...

    def strings(self) -> list[StringBlock]: ...

    def strings_dict(self) -> dict[str, StringBlock]: ...

    def entries(self) -> list[Entry]: ...

    def entries_dict(self) -> dict[str, Entry]: ...

    def preambles(self) -> list[Preamble]: ...

    def comments(self) -> list[CommentBlock]: ...

@runtime_checkable
class Middleware_p(Protocol):
    """ A Middleware is something with a 'transform' method """

    def transform(self, library:Library_p) -> Library_p: ...

@runtime_checkable
class BlockMiddleware_p(Protocol):
    """ A (non-adaptive) block middleware has 'transform_x' methods """

    def transform(self, library:Library_p) -> Library_p: ...

    def transform_block(self, block:Block, library:Library_p) -> list[Block]: ...

    def transform_entry(self, entry:Entry, library:Library_p) -> list[Block]: ...

    def transform_string(self, string:model.StringBlock, library:Library_p) -> list[Block]: ...

    def transform_preamble(self, preamble:model.Preamble, library:Library_p) -> list[Block]: ...

    def transform_explicit_comment(self, comment:model.ExplicitComment, library:Library_p) -> list[Block]: ...

    def transform_implicit_comment(self, comment:model.ImplicitComment, library:Library_p) -> list[Block]: ...

##--| New Middleware protocols:

@runtime_checkable
class BidirectionalMiddleware_p(Protocol):
    """ A Single middleware that holds the logic for reading and writing,
    Intended for undoing what is done on read, prior to writing.

    eg: Latex Decoding, then Encoding
    """

    def read_transform(self, library:Library_p) -> Library_p: ...

    def write_transform(self, library:Library_p) -> Library_p: ...

@runtime_checkable
class AdaptiveMiddleware_p(Protocol):
    """ Middleware that looks up defined transforms using the type name, by mro.
    The form for method lookup is either:
    - transform_{type(block).__class__}
    - {direction}_transform_{type(block).__class__}

    An adaptive middleware doesn't need all the 'transform_X' methods a BlockMiddleware_p does.

    """

    def get_transforms_for(self, block:Block, *, direction:Maybe[str]=None) -> list[Callable[[Block, Library_p], list[Block]]]: ...

##--| IO Protocols

@runtime_checkable
class PairStack_p(Protocol):
    """ Protocol for both storing both read and write middlewares

    """

    def add(self, *args:BidiMiddleware, read:Maybe[list|Middleware]=None, write:Maybe[list|Middleware]=None) -> Self: ...

    def read_stack(self) -> list[Middleware]: ...

    def write_stack(self) -> list[Middleware]: ...

@runtime_checkable
class Reader_p(Protocol):
    """ Readers take source text, or a file, or a directory,
    parses the read bibtex, running middlewares on the parsed bibtex
    """

    def read(self, source:str|pl.Path, *, into:Maybe[Library]=None, append:Maybe[list[Middleware]]=None) -> Maybe[Library]: ...

    def read_dir(self, source:pl.Path, *, ext:str, into:Maybe[Library]=None, append:Maybe[list[Middleware]]=None) -> Maybe[Library]: ...

@runtime_checkable
class Writer_p(Protocol):
    """ Writers take a library, format it, and write it to a file.
    *typically* it formats as bibtex, but doesn't *have* to.
    (eg: RstWriter)
    """

    def write(self, library:Library, *, file:Maybe[pl.Path]=None, append:Maybe[list[Middleware]]=None) -> str: ...

##--| Middleware protocols

@runtime_checkable
class CustomWriteBlock_p(Protocol):
    """ Writers can be Visitors, in which case they call ths visit method on
    blocks

    """

    def visit(self, writer:Writer_p) -> list[str]: ...

@runtime_checkable
class ReadTime_p(Protocol):
    """ Protocol for signifying a middleware is for use on parsing bibtex to
    data
    """

    def on_read(self) -> Never: ...

@runtime_checkable
class WriteTime_p(Protocol):
    """ Protocol for signifying middleware is for use on writing data to bibtex

    """

    def on_write(self) -> Never: ...

@runtime_checkable
class EntrySkipper_p(Protocol):
    """ A whitelist based test for middlewares.
    Middleware's set their skiplist on init,
    and can call 'should_skip_entry' when transforming blocks

    eg: for only processing type='article' entries, not books
    """

    def set_entry_skiplist(self, whitelist:list[str]) -> None: ...

    def should_skip_entry(self, entry:Entry, library:Library) -> bool: ...

@runtime_checkable
class FieldMatcher_p(Protocol):
    """ The protocol util.FieldMatcher_m relies on

    A Middleware with the FieldMatcher_m mixin will call the implemented field_h
    on each field that matches in an entry.
    """

    def set_field_matchers(self, *, white:list[str], black:list[str]) -> Self: ...

    def match_on_fields(self, entry: Entry, library: Library) -> Result[Entry, Exception]: ...

    def field_h(self, field:Field, entry:Entry) -> Result[list[Field], Exception]: ...

@runtime_checkable
class StrTransformer_p(Protocol):
    """ Describes the StringTransform_m """

    def transform_strlike(self, slike:StrLike) -> Result[StrLike, Exception]: ...

    def _transform_raw_str(self, python_string:str) -> Result[str, Exception]: ...

@runtime_checkable
class DependentMiddleware_p(Protocol):
    """
    For middlewares that depend on a middleware to be able to work themselves.

    eg: metadata applicator requires path reader
    """

    def requires_in_same_stack(self) -> list[type]: ...
    """ The given types need to be in the same stack """

    def requires_in_parse_stack(self) -> list[type]: ...
    """ The given types need to be in the parse stack """

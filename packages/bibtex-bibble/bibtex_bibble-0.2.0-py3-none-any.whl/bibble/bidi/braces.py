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

import jgdv
from jgdv import Proto, Mixin
from bibble import _interface as API  # noqa: N812
from bibble.util.middlecore import IdenBidiMiddleware
from bibtexparser import model

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType, Never
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final, override, overload

if TYPE_CHECKING:
    from jgdv import Maybe
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from bibtexparser import Library
    type Entry  = model.Entry
    type String = model.String
    type Field  = model.Field
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:
OBRACE : Final[str]           = "{"
CBRACE : Final[str]           = "}"
DQUOTE : Final[str]           = '"'
STRINGS_CAN_BE_UNESCAPED_INTS = False
ENTRY_POTENTIALLY_INT_FIELDS  = [
    "year",
    "month",
    "volume",
    "number",
    "pages",
    "edition",
    "chapter",
    "issue",
]
# Body:

@Proto(API.BidirectionalMiddleware_p)
class BraceWrapper(IdenBidiMiddleware):
    """ a Bidirectional replacement for bibtexparsers 'Add/RemoveEnclosingMiddleware' """

    def __init__(self, *, wrappers:Maybe[tuple[str,str]]=None, on_ints:bool=True, **kwargs):
        super().__init__(**kwargs)
        self._wrapper = wrappers or (OBRACE, CBRACE)
        self._on_ints = on_ints

    def _wrap(self, value: str, *, maybe_int_rule:bool=False) -> str:
        """ Take 'value' and wrap it in (by default) braces """
        if maybe_int_rule and not self._on_ints and value.isdigit():
            return value

        ochar, cchar = self._wrapper
        return f"{ochar}{value}{cchar}"

    def _unwrap(self, value: str) -> str:
        """ remove wrapping (by default) braces """
        ochar, cchar = self._wrapper
        start, end   = len(ochar), 0 - len(cchar)
        value        = value.strip()
        if value.startswith(ochar) and value.endswith(cchar):
            return value[start:end]
        else:
            return value

    def write_transform_Entry(self, entry:Entry, *args, **kwargs) -> list[Entry]:
        for field in entry.fields:
            field.value = self._wrap(field.value, maybe_int_rule=field.key in ENTRY_POTENTIALLY_INT_FIELDS)
        else:
            return [entry]

    def write_transform_String(self, string:String, *args, **kwargs) -> list[String]:
        string.value = self._wrap(string.value, maybe_int_rule=STRINGS_CAN_BE_UNESCAPED_INTS)
        return [string]

    def read_transform_Entry(self, entry: Entry, library: Library) -> list[Entry]:
        for field in entry.fields:
            field.value = self._unwrap(field.value)
        else:
            return [entry]

        Never()

    def read_transform_String(self, string: String, library: Library) -> list[String]:
        string.value = self._unwrap(string.value)
        return [string]

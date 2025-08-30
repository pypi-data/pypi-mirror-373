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
import weakref
from uuid import UUID, uuid1

# ##-- end stdlib imports

# ##-- 3rd party imports
from jgdv import Proto, Mixin
import bibtexparser
import bibtexparser.model as model
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)
from jgdv.files.tags import SubstitutionFile

# ##-- end 3rd party imports

import bibble._interface as API
from bibble.util.middlecore import IdenBlockMiddleware

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
    from jgdv import Maybe
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    type Entry = model.Entry
    type Field = model.Field
    from bibtexparser.library import Library
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

@Proto(API.WriteTime_p)
class FieldSorter(IdenBlockMiddleware):
    """ Sort the entries of a field
    firsts are exact matches that go at the front.
    lasts are a list of patterns to match on
    """

    _first_defaults : ClassVar[list[str]] = []
    _last_defaults  : ClassVar[list[str]] = []

    def __init__(self, *, first:Maybe[list[str]]=None, last:Maybe[list[str]]=None, **kwargs):
        super().__init__(**kwargs)
        self._firsts   = first or self._first_defaults
        self._lasts    = last or self._last_defaults
        self._stem_re  = re.compile("^[a-zA-Z_]+")

    def on_write(self):
        Never()

    def field_sort_key(self, field:Field) -> str|tuple:
        match self._stem_re.match(field.key):
            case None:
                key = field.key
            case x:
                key = x[0]
        try:
            return (self._lasts.index(key), field.key)
        except ValueError:
            return key

    def transform_Entry(self, entry:Entry, library:Library) -> list[Entry]:
        # Get the firsts in order if they exist
        firsts = [y for x in self._firsts if (y:=entry.get(x,None)) is not None]
        rest, lasts = [], []
        for field in entry.fields:
            match self._stem_re.match(field.key):
                case None:
                    key = field.key
                case x:
                    key = x[0]
            if key in self._firsts:
                continue
            if key not in self._lasts:
                rest.append(field)
            else:
                lasts.append(field)

        # Sort the lasts
        rest  = sorted(rest, key=self.field_sort_key)
        lasts = sorted(lasts, key=self.field_sort_key)
        entry.fields = firsts + rest + lasts
        return [entry]

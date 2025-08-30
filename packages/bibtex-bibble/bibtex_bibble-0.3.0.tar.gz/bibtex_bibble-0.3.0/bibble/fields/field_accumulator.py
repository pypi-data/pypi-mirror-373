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
from bibtexparser.library import Library
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)
from jgdv.files.tags import SubstitutionFile

# ##-- end 3rd party imports

# ##-- 1st party imports
from bibble.model import MetaBlock
from bibble.util.mixins import ErrorRaiser_m, FieldMatcher_m
from bibble import _interface as API
from . import _interface as FieldsAPI
from bibble.util.middlecore import IdenBlockMiddleware

# ##-- end 1st party imports

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
    from jgdv import Maybe, Result
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    type Entry = model.Entry
    type Field = model.Field
    type Block = model.Block
    from bibtexparser.library import Library

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

@Proto(API.FieldMatcher_p)
@Mixin(ErrorRaiser_m, FieldMatcher_m)
class FieldAccumulator(IdenBlockMiddleware):
    """ Create a set of all the values of a field, of all entries, in a library.

    'name' : the name of the accumulation block to store result in
    'fields' : the fields to accumulate values of.

    Fields can be individual values, or lists/sets of values

    """


    def __init__(self, *, name:str, fields:list[str], **kwargs):
        super().__init__(**kwargs)
        self._attr_target = name
        match fields:
            case list():
                self._target_fields = fields
            case x:
                raise TypeError(type(x))

        self.set_field_matchers(white=self._target_fields, black=[])
        self._collection = set()

    def transform(self, library:Library) -> Library:
        super().transform(library)
        library.add(FieldsAPI.AccumulationBlock(name=self._attr_target, data=self._collection, fields=self._target_fields))
        return library

    def transform_Entry(self, entry, library) -> list[Block]:
        match self.match_on_fields(entry, library):
            case model.Entry() as x:
                return [x]
            case Exception() as err:
                return [self.make_error_block(entry, err)]
            case x:
                raise TypeError(type(x))

    def field_h(self, field, entry) -> Result(list[Field], Exception):
        match field.value:
            case str() as value:
                self._collection.add(value)
            case list() | set() as value:
                self._collection.update(value)
            case x:
                raise TypeError(type(x))

        return []

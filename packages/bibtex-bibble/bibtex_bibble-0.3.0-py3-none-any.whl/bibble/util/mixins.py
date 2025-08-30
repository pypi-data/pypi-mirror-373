#!/usr/bin/env python3
"""

"""

# Imports:
from __future__ import annotations

# ##-- stdlib imports
import atexit#  for @atexit.register
import collections
import contextlib
import datetime
import enum
import faulthandler
import functools as ftz
import hashlib
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref

# ##-- end stdlib imports

# ##-- 3rd party imports
import bibtexparser
import bibtexparser.model as model
from bibtexparser import exceptions as bexp
from bibtexparser import middlewares as ms
from bibtexparser.model import MiddlewareErrorBlock

# ##-- end 3rd party imports

# ##-- 1st party imports
from bibble import _interface as API
import bibble.model as bmodel

# ##-- end 1st party imports

# ##-- types
# isort: off
# General
import abc
import collections.abc
import typing
import types
from typing import cast, assert_type, assert_never
from typing import Generic, NewType, Never
from typing import no_type_check, final, override, overload
# Protocols and Interfaces:
from typing import Protocol, runtime_checkable
# isort: on
# ##-- end types

# ##-- type checking
# isort: off
if typing.TYPE_CHECKING:
    from typing import Final, ClassVar, Any, Self
    from typing import Literal, LiteralString
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from jgdv import Maybe, Either, Result, Rx
    type Middleware = API.Middleware_p | API.BidirectionalMiddleware_p

## isort: on
# ##-- end type checking


##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:
EMPTY       : Final[Rx]   = re.compile(r"^$")
OR_REG      : Final[str]  = r"|"
ANY_REG     : Final[Rx]   = re.compile(r".")
# Body:

class MiddlewareValidator_m:
    """ For ensuring the middlewares of a reader/writer  are appropriate,
    by excluding certain middlewares.
    """
    _middlewares : list[Middleware]

    def exclude_middlewares(self, proto:type):
        if not issubclass(proto, Protocol):
            raise TypeError("Tried to validate middlewares with a non-protocol", proto)
        failures = []
        for middle in self._middlewares:
            # note: no 'not'.
            if isinstance(middle, proto):
                failures.append(middle)
            elif not isinstance(middle, API.Middleware_p|API.BidirectionalMiddleware_p):
                failures.append(middle)
        else:
            if bool(failures):
                raise TypeError("Bad middlewares", failures)

class ErrorRaiser_m:
    """ Mixin for easily combining middleware errors into a block"""

    def make_error_block(self, entry:API.Entry, err:Exception) -> MiddlewareErrorBlock:
        return bmodel.FailedBlock(block=entry, error=err, source=self)

class FieldMatcher_m:
    """ Mixin to process fields if their key matchs a regex
    defaults are in the attrs _field_blacklist and _field_whitelist, _entry_whitelist
    Call set_field_matchers to extend.
    Call match_on_fields to start.
    Call maybe_skip_entry to compare the lowercase entry type to a whitelist
    Implement field_handler to use.

    match_on_fields calls entry.set_field on the field_handlers result
    """

    def set_field_matchers(self, *, white:list[str], black:list[str]) -> Self:
        """ sets the blacklist and whitelist regex's
        returns self to help in building parse stacks
        """
        match white:
            case []:
                self._field_white_re = ANY_REG
            case [*xs]:
                self._field_white_re = re.compile(OR_REG.join(xs))

        match black:
            case []:
                self._field_black_re = EMPTY
            case [*xs]:
                self._field_black_re = re.compile(OR_REG.join(xs))

        return self

    def match_on_fields(self, entry: API.Entry, library: API.Library) -> Result[API.Entry, Exception]:
        errors : list[str] = []
        whitelist, blacklist = self._field_white_re, self._field_black_re
        for field in entry.fields:
            match field:
                case model.Field(key=str() as key) if whitelist.match(key) and not blacklist.match(key):
                    res = self.field_h(field, entry)
                case _:
                    continue

            match res:
                case [*xs]:
                    for x in xs:
                        entry.set_field(x)
                case Exception() as err:
                    errors += err.args
                case x:
                    raise TypeError(type(x), self)
        else:
            if bool(errors):
                return ValueError(*errors)

            return entry

    def field_h(self, field:API.Field, entry:API.Entry) -> Result[list[API.Field], Exception]:
        raise NotImplementedError("Implement the field handler")

class EntrySkipper_m:
    """
    Be able to skip entries by their type
    """

    def set_entry_skiplists(self, *, white:Maybe[list[str]]=None, black:Maybe[list[str]]=None) -> None:
        self._entry_whitelist = [x.lower() for x in white or []]
        self._entry_blacklist = [x.lower() for x in black or []]

    def should_skip_entry(self, entry:API.Entry, library:API.Library) -> bool:
        low_type = entry.entry_type.lower()
        match self._entry_blacklist:
            case list() as xs if low_type in xs:
                return True
            case _:
                pass

        match self._entry_whitelist:
            case []:
                return False
            case list() as xs if low_type in xs:
                return False
            case _:
                return True

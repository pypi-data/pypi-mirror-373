#!/usr/bin/env python3
"""
Refactored from bibtexparser.middlewares.names

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
# from dataclasses import InitVar, dataclass, field
# from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError

if TYPE_CHECKING:
    from jgdv import Maybe, M_
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    type MbList = Maybe[list[str]]
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:
JOIN_STR : Final[str] = ", "
# Body:

def escape_last_slash(string: str) -> str:
    """Escape the last slash in a string if it is not escaped."""
    # Find the number of trailing slashes
    stripped = string.rstrip("\\")
    num_slashes = len(string) - len(stripped)
    if num_slashes % 2 == 0:
        # Even number: everything is escaped
        return string
    else:
        # Odd number: need to escape one.
        return string + "\\"

##--|

class NameParts_d:
    """A dataclass representing the parts of a person name.

    The different parts are defined according to BibTex's implementation
    of name parts (first, von, last, jr).
    """
    __slots__ = ("first", "von", "last", "jr")

    first :  list[str]
    von   :  list[str]
    last  :  list[str]
    jr    :  list[str]

    def __init__(self, *, first:MbList=None, von:MbList=None, last:MbList=None, jr:MbList=None):
        self.first = first or []
        self.von   = von   or []
        self.last  = last  or []
        self.jr    = jr    or []

    def merge(self, *, format:Maybe[list[str]]=None) -> str:
        match format:
            case None:
                format = ["von_last", "jr", "first"]
            case str():
                pass
            case x:
                raise TypeError(type(x))

        parts = {
            "first"  : " ".join(self.first) if self.first else None,
            "von"    : " ".join(self.von) if self.von else None,
            "last"   : " ".join(self.last) if self.last else None,
            "jr"     : " ".join(self.jr) if self.jr else None,
        }
        parts['von_last'] = " ".join(name for name in [parts['von'], parts['last']] if name)
        ordered = [parts[x] for x in format]
        return JOIN_STR.join(escape_last_slash(name) for name in ordered if name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} : {self.merge()}>"

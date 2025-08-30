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

import bibble._interface as API

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
    from jgdv import Maybe, Fifo, Lifo
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    type UniMiddleware   = API.UniMiddleware
    type BidiMiddleware  = API.BidiMiddleware
    type Middleware      = API.Middleware

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:

# Body:

class PairStack:
    """ A pair of middleware stacks,
    allowing reader/writer pairs to be added at the same time

    The read stack is Fifo, the write stack is Lifo.
    So any transforms are undone in the correct order before writing.
    Parse[m1, m2, m3] -> Write[m3, m2, m1]

    eg: Parse[LatexToUnicode, SplitName] -> Write[MergeNames, UnicodeToLatex]

    """
    _read_time  : Fifo[Middleware]
    _write_time : Lifo[Middleware]

    def __init__(self):
        self._read_time  = []
        self._write_time = []

    def add(self, *bidis:BidiMiddleware, read:Maybe[list[Middleware]]=None, write:Maybe[list[Middleware]]=None) -> Self:
        """
        Add middlewares to the read/write stacks.
        Args *must* be bidirection, and will be added to both.
        kwargs 'read' and 'write' just add to specific stacks
        """
        read  = read or []
        write = write or []

        for mid in bidis:
            match mid:
                case None:
                     pass
                case API.BidirectionalMiddleware_p():
                    self._read_time.append(mid)
                    self._write_time.append(mid)
                case x:
                    raise TypeError(type(x))

        for x in read:
            match x:
                case None:
                    pass
                case API.Middleware_p():
                    self._read_time.append(x)
                case API.BidirectionalMiddleware_p():
                    self._read_time.append(x)
                case _:
                    raise TypeError(type(x))

        for x in write:
            match x:
                case None:
                    pass
                case API.Middleware_p():
                    self._write_time.append(x)
                case API.BidirectionalMiddleware_p():
                    self._write_time.append(x)
                case _:
                    raise TypeError(type(x))

        return self

    def read_stack(self) -> list[Middleware]:
        """ Return the read stack """
        return self._read_time[:]

    def write_stack(self) -> list[Middleware]:
        """ Return the write stack """
        return self._write_time[::-1]

    def has_read_transform(self, mid:type[Middleware]|Middleware) -> bool:
        match mid:
            case type():
                return any(isinstance(x, mid) for x in self._read_time)
            case API.Middleware_p():
                return mid in self._read_time
            case _:
                return False

    def has_write_transform(self, mid:type[Middleware]|Middleware) -> bool:
        match mid:
            case type():
                return any(isinstance(x, mid) for x in self._write_time)
            case API.Middleware_p():
                return mid in self._write_time
            case _:
                return False

    def __contains__(self, other:type[Middleware]|Middleware) -> bool:
        return self.has_read_transform(other) or self.has_write_transform(other)

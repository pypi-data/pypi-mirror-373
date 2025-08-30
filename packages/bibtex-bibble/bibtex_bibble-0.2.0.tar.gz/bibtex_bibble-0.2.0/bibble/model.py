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
from bibtexparser import model
from jgdv import Maybe, Proto

# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
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
    from jgdv import Maybe
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from bibtexparser.libary import Library
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

@Proto(API.CustomWriteBlock_p)
class MetaBlock(model.Block):
    """ A Metadata Block baseclass that does not get written out (typically),
    But can hold information about the library
    """

    @classmethod
    def find_in(cls, lib:Library) -> Maybe[Self]:
        """ Find a block of this cls in a given library """
        for block in lib.blocks:
            if isinstance(block, cls):
                return block
        else:
            return None

    def __init__(self, **kwargs):
        super().__init__(0)
        self.data = dict(kwargs)

    def visit(self, *args, **kwargs) -> list[str]:
        return []


class FailedBlock(model.MiddlewareErrorBlock):
    """ Records errors encountered by a middleware """

    def __init__(self, *, block:model.Block, error:Exception, source:type|str):
        super().__init__(block, error)
        self._block_type = type(block).__name__
        match source:
            case API.Middleware_p() as mw:
                self.source_middleware = type(source).__name__
            case type():
                self.source_middleware = source.__name__
            case str():
                self.source_middleware = source
            case x:
                raise TypeError(type(x))


    def __repr__(self):
        key = self.ignore_error_block.key
        return f"<{self.__class__.__name__}: {key}>"

    def report(self, *, i:int, total:int, source_file:Maybe[str|pl.Path]=None, **kwargs) -> list[str]:
        match source_file:
            case None:
                report = f"({i}/{total}) [{self.source_middleware}] Bad <{self._block_type}>: {self.start_line} : {self.error}"
            case str() | pl.Path():
                report = f"({i}/{total}) [{self.source_middleware}] Bad <{self._block_type}>: {source_file}:{self.start_line} : {self.error}"
            case x:
                raise TypeError(type(x))

        return [report]


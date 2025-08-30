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
import bibtexparser
import bibtexparser.model as model
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)
from jgdv import Proto
# ##-- end 3rd party imports

import bibble._interface as API
from bibble.util.middlecore import IdenLibraryMiddleware
import bibble.model as bmodel

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

    type Logger = logmod.Logger
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

class FailureHandler(IdenLibraryMiddleware):
    """ Middleware to Filter failed blocks of a library,
    either to a logger output, or to a file
    Put at end of parse stack

    Will log out where the failed blocks start by line.
    """

    def __init__(self, **kwargs):
        file_target = kwargs.pop("file", None)
        super().__init__(**kwargs)
        match file_target:
            case str() as x:
                self.file_target = pl.Path(x)
            case pl.Path() as x:
                self.file_target = x
            case _:
                self.file_target = None


    def transform(self, library):
        total    = len(library.failed_blocks)
        reported = []
        for i, block in enumerate(library.failed_blocks, start=1):
            source_file = self._find_source_file(block, library)
            match block:
                case bmodel.FailedBlock():
                    report = block.report(i=i, total=total, source_file=source_file)[0]
                case model.ParsingFailedBlock() if source_file:
                    report = f"({i}/{total}) Bad Block: : {block.start_line} : {source_file} : {block.error}"
                case model.ParsingFailedBlock():
                    report = f"({i}/{total}) Bad Block: : {block.start_line} : {block.error}"
                case x:
                    raise TypeError(type(x))
            ##--|
            reported.append((report, block.error, block.raw))
            self._logger.info(report)
        else:
            self.write_failures_to_file(reported)
        return library

    def write_failures_to_file(self, reports:list) -> None:
        match reports:
            case []:
                return
            case _ if self.file_target is None:
                return
            case _:
                pass

        total = len(reports)
        with self.file_target.open("w") as f:
            for rep, err, raw in reports:
                f.writelines(["\n\n--------------------\n",
                               rep,
                               f"\nError: {err}",
                               "\n--------------------\n",
                               raw,
                               ])

    def _find_source_file(self, block, library) -> Maybe[str]:
        match block:
            case model.Entry():
                target_key = block.key
            case _:
                return None

        match bmodel.MetaBlock.find_in(library):
            case None:
                return None
            case bmodel.MetaBlock() as meta if 'sources' not in meta.data:
                return None
            case bmodel.MetaBlock() as meta:
                data = meta.data
                sources = meta.data['sources']

        for source in sources:
            if source in data and target_key in data[source]:
                return source
            ##--|
        else:
            return None

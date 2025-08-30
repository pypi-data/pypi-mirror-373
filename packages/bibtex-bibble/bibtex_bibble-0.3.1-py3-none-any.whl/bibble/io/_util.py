#!/usr/bin/env python3
"""


"""
# mypy: disable-error-code="attr-defined"
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
from bibble.model import MetaBlock

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

    from bibtexparser import Library
    from bibble._interface import Middleware

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:

# Body:

class Runner_m:
    """
    Shared code for running middlewares
    """

    def _run_writewares(self, library:Library, *, append:Maybe[list[Middleware]]=None) -> Library:
        """ Run write transforms on the library before writing,
        can handle bidirectional middlewares
        """
        append     = append or []
        fail_count = len(library.failed_blocks)
        for middleware in itz.chain(self._middlewares, append):
            fail_count = len(library.failed_blocks)
            self._logger.debug("- Running Write Middleware: %s", middleware.metadata_key())
            if hasattr(middleware, "handle_meta_entry"):
                middleware.handle_meta_entry(library)
            match middleware:
                case API.Middleware_p():
                    library = middleware.transform(library=library)
                case API.BidirectionalMiddleware_p():
                    library = middleware.write_transform(library=library)
                case x:
                    raise TypeError(type(x))

            if fail_count < (new_fcount:=len(library.failed_blocks)):
                self._logger.debug("Added %s failures", new_fcount - fail_count)
                fail_count = new_fcount

        else:
            self._record_transform_chain("write_transforms", library, append)
            return library

    def _run_readwares(self, library:Library, *, append:Maybe[list[Middleware]]=None) -> Library:
        append     = append or []
        fail_count = len(library.failed_blocks)
        for middleware in itz.chain(self._middlewares, append):
            self._logger.debug("- Running Read Middleware: %s", middleware.metadata_key())
            if hasattr(middleware, "handle_meta_entry"):
                middleware.handle_meta_entry(library)
            match middleware:
                case API.Middleware_p():
                    library = middleware.transform(library=library)
                case API.BidirectionalMiddleware_p():
                    library = middleware.read_transform(library=library)
                case x:
                    raise TypeError(type(x))

            if fail_count < (new_fcount:=len(library.failed_blocks)):
                self._logger.debug("Added %s failures", new_fcount - fail_count)
                fail_count = new_fcount

        else:
            self._record_transform_chain("read_transforms", library, append)
            return library

    def _record_transform_chain(self, meta_key:str, library:Library, append:list[Middleware]) -> None:
        """
        Record the metadata keys used on this library in a meta block
        """
        keys = [x.metadata_key() for x in itz.chain(self._middlewares, append)]
        match MetaBlock.find_in(library):
            case None:
                library.add(MetaBlock(read_stack=keys))
            case MetaBlock() as mb if meta_key in mb.data:
                mb.data[meta_key] += keys
            case MetaBlock() as mb:
                mb.data[meta_key] = keys
            case x:
                raise TypeError(type(x))


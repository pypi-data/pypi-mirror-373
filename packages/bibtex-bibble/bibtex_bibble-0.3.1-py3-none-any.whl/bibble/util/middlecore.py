#!/usr/bin/env python3
"""
Refactored core middleware classes from bibtexparser

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
import sys
# ##-- end stdlib imports

import tqdm
import bibble._interface as API
from bibble.model import MetaBlock
import jgdv
from jgdv._abstract.protocols.general import DILogger_p
from jgdv import Proto
from bibtexparser.library import Library
from bibtexparser import model

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

    type Logger          = logmod.Logger
    type Block           = model.Block
    type Entry           = model.Entry
    type String          = model.String
    type Preamble        = model.Preamble
    type ExplicitComment = model.ExplicitComment
    type ImplicitComment = model.ImplicitComment
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:

# Body:

@Proto(DILogger_p)
class _BaseMiddleware:
    """
    The base middleware.
    has a metadata key,
    stores allow_inplace and allow_parallel
    and can have an injected logger.

    Any extra init kwargs are stored in _extra
    """
    allow_inplace : bool
    allow_parallel : bool

    @classmethod
    def metadata_key(cls) -> str:
        """Identifier of the middleware.
        This key is used to identify the middleware in a blocks metadata.
        """
        return f"bibble-{cls.__name__}"

    def __init__(self, **kwargs):
        """

        """
        inplace             = kwargs.pop(API.ALLOW_INPLACE_MOD_K, True)
        self.allow_inplace  = inplace
        self.allow_parallel = kwargs.pop(API.ALLOW_PARALLEL_K, False)
        fallback_name       = f"{type(self).__module__}.{type(self).__name__}"
        self._logger        = kwargs.pop(API.LOGGER_K, logmod.getLogger(fallback_name))
        self._extra         = kwargs

    def logger(self) -> Logger:
        return self._logger

    def _get_lib_iterator(self, library:Library) -> tuple[Library, Iterator[Block]]:
        match self.allow_inplace:
            case True:
                library = library
            case False:
                library = deepcopy(library)
            case x:
                raise TypeError(type(x))

        match self._extra:
            case {"tqdm":True} if sys.stdout.isatty():
                iterator = tqdm.tqdm(enumerate(library.blocks),
                                     desc=type(self).__name__,
                                     total=len(library.blocks),
                                     ncols=API.TQDM_WIDTH)
            case _:
                iterator = enumerate(library.blocks)

        return library, iterator

    def handle_meta_entry(self, library:Library) -> None:
        """ An optional entry hook for middlewares,
        which is given the library's metablock before transform is called.

        Use case: conditionally setting PathWriter suppress paths
        """
        pass
class IdenLibraryMiddleware(_BaseMiddleware):
    """ Identity Library Middleware, does nothing """

    def transform(self, library:Library) -> Library:
        match library:
            case Library() if self.allow_inplace:
                return library
            case Library():
                return deepcopy(library)

@Proto(API.AdaptiveMiddleware_p, API.Middleware_p)
class IdenBlockMiddleware(_BaseMiddleware):
    """ Identity Block Middleware, does nothing
    If passed 'tqdm'=True uses tqdm around the block level loop
    """
    _transform_cache : dict[type, list[Callable]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transform_cache = dict()

    def get_transforms_for(self, block:Block, *, direction:Maybe[str]=None) -> list[Callable]:
        """ Get all transforms of the form transform_{Type},
        by mro, from most -> least specific
        """
        assert(direction is None)
        if type(block) not in self._transform_cache:
            mro = type(block).mro()
            formatted = [f"transform_{x.__name__}" for x in mro]
            methods = [getattr(self, x, None) for x in formatted]
            self._transform_cache[type(block)] = [x for x in methods if x is not None]

        return self._transform_cache[type(block)]

    def transform(self, library:Library) -> Library:
        library, iterator = self._get_lib_iterator(library)
        blocks = []
        for i,block in iterator:
            match self.get_transforms_for(block):
                case [x, *_]: # Use the first found transform,
                    transform = x
                case _: # No transforms for this block type, do nothing
                    blocks.append(block)
                    continue

            match transform(block, library):
                case None: # remove block
                    continue
                case []: # Keep original (it might have been modified)
                    blocks.append(block)
                case [*xs]: # new blocks
                    blocks += xs
                case x:
                    raise TypeError(type(x), i, block)

        else:
            # Remove the old blocks
            library.remove(library.blocks[:])
            # Add the new blocks
            library.add(blocks)
            return library

@Proto(API.AdaptiveMiddleware_p, API.BidirectionalMiddleware_p)
class IdenBidiMiddleware(_BaseMiddleware):

    _transform_cache : dict[str, list[Callable]]
    _reader : Maybe[API.Middleware]
    _writer : Maybe[API.Middleware]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reader          = None
        self._writer          = None
        self._transform_cache = dict()


    def handle_meta_entry(self, library:Library) -> None:
        match self._reader:
            case None:
                pass
            case mw if not hasattr(mw, "handle_meta_entry"):
                pass
            case mw:
                mw.handle_meta_entry(library)

        match self._writer:
            case None:
                pass
            case mw if not hasattr(mw, "handle_meta_entry"):
                pass
            case mw:
                mw.handle_meta_entry(library)


    def get_transforms_for(self, block:Block, *, direction:Maybe[str]=None) -> list[Callable]:
        """ Get all transforms of the form {direction}_transform_{Type},
        by mro, from most -> least specific
        """
        cache_key = f"{direction}_{type(block).__name__}"
        if cache_key not in self._transform_cache:
            mro       = type(block).mro()
            formatted = [f"{direction}_transform_{x.__name__}" for x in mro]
            methods   = [getattr(self, x, None) for x in formatted]
            self._transform_cache[cache_key] = [x for x in methods if x is not None]

        return self._transform_cache[cache_key]


    def read_transform(self, library:Library) -> Library:
        library, iterator = self._get_lib_iterator(library)
        blocks   = []
        for i,block in iterator:
            match self.get_transforms_for(block, direction="read"):
                case [x, *_]: # Use the first found transform,
                    transform = x
                case _:
                    blocks.append(block)
                    continue

            match transform(block, library):
                case [] | None: # Transform gave nothing, so keep the original block.
                    blocks.append(block)
                case [*xs]:
                    # new blocks
                    blocks += xs
                case x:
                    raise TypeError(type(x), i, block)
        else:
            # Remove the old blocks
            library.remove(library.blocks[:])
            assert(len(library.blocks) == 0), len(library.blocks)
            # Add the new blocks
            library.add(blocks)
            return library

    def write_transform(self, library:Library) -> Library:
        library, iterator = self._get_lib_iterator(library)
        blocks = []
        for i,block in iterator:
            match self.get_transforms_for(block, direction="write"):
                case [x, *_]: # Use the first found transform,
                    transform = x
                case _:
                    blocks.append(block)
                    continue

            match transform(block, library):
                case [] | None: # Transform gave nothing, so keep the original block.
                    blocks.append(block)
                case [*xs]: # new blocks
                    blocks += xs
                case x:
                    raise TypeError(type(x), i, block)
        else:
            # Remove the old blocks
            library.remove(library.blocks[:])
            # Add the new blocks
            library.add(blocks)
            return library

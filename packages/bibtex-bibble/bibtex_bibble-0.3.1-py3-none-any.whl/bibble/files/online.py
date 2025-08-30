#!/usr/bin/env python3
"""

See EOF for license/metadata/notes as applicable
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
from bibtexparser.middlewares.middleware import (BlockMiddleware, LibraryMiddleware)
from jgdv import Proto, Mixin
from jgdv.files.bookmarks import BookmarkCollection
from jgdv.files.tags import TagFile
from waybackpy import WaybackMachineSaveAPI

# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from . import  _interface as FAPI
from ._firefox import FirefoxController
from bibble.util.mixins import FieldMatcher_m, EntrySkipper_m
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
    from jgdv import Maybe
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    from bibtexparser.library import Library

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##--|

@Mixin(EntrySkipper_m)
class OnlineDownloader(IdenBlockMiddleware):
    """
      if the entry is 'online', and it doesn't have a file associated with it,
      download it as a pdf and add it to the entry
    """
    _whitelist = ("online", "blog")
    _target_dir         : pl.Path

    def __init__(self, *, target:pl.Path, **kwargs):
        super().__init__(**kwargs)
        self._extra.setdefault("tqdm", True)
        self.set_entry_skiplists(white=self._whitelist, black=[])
        self._target_dir         = target

    def transform(self, library:Library) -> Library:
        try:
            result = super().transform(library)
            return result
        finally:
            FirefoxController.close()

    def transform_Entry(self, entry, library):
        if self.should_skip_entry(entry, library):
            return [entry]

        match entry.get("url"), entry.get("file"):
            case _, pl.Path()|str():
                self._logger.info("Entry %s : Already has file", entry.key)
                return entry
            case None, _:
                self._logger.warning("Entry %s : no url found", entry.key)
                return entry
            case model.Field(value=url), None:
                safe_key = entry.key.replace(":","_")
                dest     = (self._target_dir / safe_key).with_suffix(".pdf")
                FirefoxController.save_pdf(url, dest)
                # add it to the entry
                entry.set_field(model.Field("file", value=dest))

        return [entry]

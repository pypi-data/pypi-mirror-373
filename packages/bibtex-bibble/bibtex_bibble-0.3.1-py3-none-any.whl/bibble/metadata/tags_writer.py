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
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)
from jgdv import Mixin, Proto
from jgdv.files.tags import SubstitutionFile

# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from . import _interface as MAPI
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

    from bibtexparser import Library
    type Entry = model.Entry
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##--|

@Proto(API.WriteTime_p)
class TagsWriter(IdenBlockMiddleware):
    """
      Reduce tag set to a string.
      Pass in to_keywords=True to convert tags -> keywords for bibtex2html
    """

    def __init__(self, *, to_keywords:bool=False, **kwargs):
        super().__init__(**kwargs)
        self._to_keywords = to_keywords

    def on_write(self):
        Never()

    def transform_Entry(self, entry:Entry, library:Library) -> list[Entry]:
        match entry.get(MAPI.TAGS_K):
            case None:
                self._logger.warning("Entry has No Tags on write: %s", entry.key)
                entry.set_field(model.Field(MAPI.TAGS_K, ""))
            case model.Field(value=val) if not bool(val): # type: ignore
                self._logger.warning("Entry has No Tags on write: %s", entry.key)
                entry.set_field(model.Field(MAPI.TAGS_K, ""))
            case model.Field(value=set() as vals):
                entry.set_field(model.Field(MAPI.TAGS_K, ",".join(sorted(vals)))) # type: ignore

        if self._to_keywords:
            entry.set_field(model.Field(MAPI.KEYWORDS_K, entry.get(MAPI.TAGS_K).value))

        return [entry]

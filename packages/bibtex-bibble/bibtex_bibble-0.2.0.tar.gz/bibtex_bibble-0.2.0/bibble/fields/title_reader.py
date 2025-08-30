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
from jgdv import Proto
import bibtexparser
import bibtexparser.model as model
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)

# ##-- end 3rd party imports

from bibble._interface import ReadTime_p
from bibble.util.middlecore import IdenBlockMiddleware
from . import _interface as API_F

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType, Never
# Protocols:
from typing import Protocol, runtime_checkable
# Typing Decorators:
from typing import no_type_check, final, override, overload

if TYPE_CHECKING:
    from jgdv import Maybe
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    type Entry = model.Entry
    from bibtexparser.library import Library

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##--|

@Proto(ReadTime_p)
class TitleCleaner(IdenBlockMiddleware):
    """
      strip whitespace from the title, and (optional) subtitle
    """

    def on_read(self):
        Never()

    def transform_Entry(self, entry, library):
        match entry.get(API_F.TITLE_K):
            case None:
                self._logger.warning("Entry has no title: %s", entry.key)
            case model.Field(value=str() as value):
                entry.set_field(model.Field(API_F.TITLE_K, value.strip()))
            case _:
                pass

        match entry.get(API_F.SUBTITLE_K):
            case None:
                pass
            case model.Field(value=str() as value):
                entry.set_field(model.Field(API_F.SUBTITLE_K, value.strip()))
            case _:
                pass

        return [entry]

@Proto(ReadTime_p)
class TitleSplitter(IdenBlockMiddleware):
    """
      Split Title Into Title and Subtitle, If Subtitle Doesn't Exist Yet

    strips whitespace as well
    """

    def on_read(self):
        Never()

    def transform_Entry(self, entry:Entry, library:Library):
        match entry.get(API_F.TITLE_K), entry.get(API_F.SUBTITLE_K):
            case None, _:
                self._logger.warning("Entry has no title: %s", entry.key)
            case model.Field(value=title), model.Field(value=subtitle):
                entry.set_field(model.Field(API_F.TITLE_K, title.strip()))
                entry.set_field(model.Field(API_F.SUBTITLE_K, subtitle.strip()))
                pass
            case model.Field(value=value), None if API_F.TITLE_SEP in value:
                title, *rest = value.split(API_F.TITLE_SEP)
                entry.set_field(model.Field(API_F.TITLE_K, title.strip()))
                entry.set_field(model.Field(API_F.SUBTITLE_K, " ".join(rest).strip()))
            case model.Field(value=value), None:
                entry.set_field(model.Field(API_F.TITLE_K, value.strip()))
            case None, None:
                pass

        return [entry]

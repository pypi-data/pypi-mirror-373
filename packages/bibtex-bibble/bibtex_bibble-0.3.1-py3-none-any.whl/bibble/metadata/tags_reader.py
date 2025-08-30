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
from jgdv import Mixin, Proto
from jgdv.files.tags import TagFile

# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from bibble.util.middlecore import IdenBlockMiddleware

# ##-- end 1st party imports

from . import _interface as MAPI

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

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

@Proto(API.ReadTime_p)
class TagsReader(IdenBlockMiddleware):
    """
      Read Tag strings, split them into a set, and keep track of all mentioned tags
      By default the classvar _all_tags is cleared on init, pass clear=False to not

    tags are normalized through the TagFile
    """
    _all_tags : ClassVar[TagFile] = TagFile()

    _clear_on_transform : bool

    @staticmethod
    def tags_to_str():
        return str(TagsReader._all_tags)

    def __init__(self, *, clear:bool=True, **kwargs):
        super().__init__(**kwargs)
        self._clear_on_transform = clear

    def on_read(self):
        Never()

    def transform(self, library:Library) -> Library:
        if self._clear_on_transform:
            TagsReader._all_tags = TagFile()

        return super().transform(library)

    def transform_Entry(self, entry, library) -> list:
        tf = TagsReader._all_tags

        match entry.get(MAPI.TAGS_K):
            case None:
                self._logger.warning("Entry has no Tags on parse: %s", entry.key)
                entry.set_field(model.Field(MAPI.TAGS_K, set()))
            case model.Field(value=val) if not bool(val):
                self._logger.warning("Entry has no Tags on parse: %s", entry.key)
                entry.set_field(model.Field(MAPI.TAGS_K, set()))
            case model.Field(value=str() as val):
                as_set = set(tf.norm_tag(x) for x in val.split(","))
                entry.set_field(model.Field(MAPI.TAGS_K, as_set))
                tf.update(as_set)
            case model.Field(value=set()):
                pass

        return [entry]

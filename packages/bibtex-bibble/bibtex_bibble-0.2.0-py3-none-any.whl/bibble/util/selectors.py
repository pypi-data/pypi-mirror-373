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
from random import choices
from uuid import UUID, uuid1

# ##-- end stdlib imports

# ##-- 3rd party imports
import bibtexparser
import bibtexparser.model as model
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)
from bibtexparser.middlewares.names import (NameParts,
                                            parse_single_name_into_parts)

# ##-- end 3rd party imports

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

class SelectN(LibraryMiddleware):
    """ Select N random entries """

    def __init__(self, *, count:int=1):
        super().__init__()
        self._count = count

    def transform(self, library):
        entries = library.entries
        chosen = choices(entries, k=self._count)
        return library

class SelectEntriesByType(LibraryMiddleware):
    """ Select entries of a particular type """
    default_targets = ("article",)
    _entry_targets  : list[str]

    def __init__(self, *, targets:Maybe[Iterable[str]]=None):
        super().__init__()
        self._entry_targets = [x.lower() for x in (targets or self.default_targets)]

    def transform(self, library):
        chosen = [x for x in library.entries if x.entry_type.lower() in self._entry_targets]
        return Library(chosen)

class SelectTags(LibraryMiddleware):
    """ Select entries of with a particular tag """
    _targets : set[str]

    def __init__(self, *, tags:Iterable[str]):
        super().__init__()
        self._targets = set(tags)

    def transform(self, library:Library) -> Library:
        chosen = [x for x in library.entries if bool(x.fields_dict['tags'].value & self._targets)]
        return Library(chosen)

class SelectAuthor(LibraryMiddleware):
    """ TODO select entries by a set of authors

    should run name split on them
    """
    _targets : set[str]

    def __init__(self, *, authors:Iterable[str]):
        super().__init__()
        self._targets = set(authors)

    def transform(self, library):
        raise NotImplementedError()

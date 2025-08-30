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
from jgdv import Proto, Mixin
import bibtexparser
import bibtexparser.model as model
import isbn_hyphenate
import pyisbn
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)

# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from . import _interface as MAPI
from bibble.util.middlecore import IdenBlockMiddleware
from bibble.util.mixins import ErrorRaiser_m
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

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##--|

@Proto(API.WriteTime_p)
@Mixin(ErrorRaiser_m)
class IsbnWriter(IdenBlockMiddleware):
    """
      format the isbn for writing
    """

    def on_write(self):
        Never()

    def transform_Entry(self, entry, library) -> list:
        f_dict = entry.fields_dict
        if MAPI.ISBN_K not in f_dict:
            return [entry]
        if MAPI.INVALID_ISBN_K in f_dict:
            return [entry]
        if not bool(f_dict[MAPI.ISBN_K].value):
            return [entry]

        try:
            isbn = isbn_hyphenate.hyphenate(f_dict[MAPI.ISBN_K].value)
            entry.set_field(model.Field(MAPI.ISBN_K, isbn))
            return [entry]
        except isbn_hyphenate.IsbnError as err:
            self._logger.warning("Writing ISBN failed: %s : %s", f_dict[MAPI.ISBN_K].value, err)
            return [entry,
                    self.make_error_block(entry, err)
                    ]

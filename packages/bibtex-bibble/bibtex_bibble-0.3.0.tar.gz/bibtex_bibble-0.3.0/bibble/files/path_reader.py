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
from bibtexparser.middlewares.middleware import (BlockMiddleware, LibraryMiddleware)
from jgdv import Proto, Mixin

# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from bibble.util.mixins import ErrorRaiser_m, FieldMatcher_m
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

##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

@Proto(API.ReadTime_p)
@Mixin(ErrorRaiser_m, FieldMatcher_m)
class PathReader(IdenBlockMiddleware):
    """
      Convert file paths in bibliography to pl.Path's, expanding relative paths
      according to lib_root
    """

    _whitelist = ("file",)

    def __init__(self, *, lib_root:Maybe[pl.Path]=None, **kwargs):
        super().__init__(**kwargs)
        self._lib_root = lib_root or pl.Path.cwd()
        self.set_field_matchers(white=kwargs.pop("whitelist", self._whitelist), black=[])  # type: ignore[attr-defined]

    def on_read(self):
        Never()

    def transform_Entry(self, entry, library):
        match self.match_on_fields(entry, library):
            case model.Entry() as x:
                return [x]
            case Exception() as err:
                return [self.make_error_block(entry, err)]
            case x:
                raise TypeError(type(x))

    def field_h(self, field, entry):
        base = pl.Path(field.value)
        match base.parts[0]:
            case "/":
                field.value = base
            case "~":
                field.value = base.expanduser().resolve()
            case _:
                field.value = self._lib_root / base

        if not field.value.exists():
            return ValueError(f"File does not exist: {field.value}")

        return [field]

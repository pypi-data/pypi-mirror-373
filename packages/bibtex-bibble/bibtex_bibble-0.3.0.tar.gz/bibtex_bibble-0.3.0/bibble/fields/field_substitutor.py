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
from jgdv import Mixin
import bibtexparser
import bibtexparser.model as model
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)
from jgdv.files.tags import SubstitutionFile

# ##-- end 3rd party imports

# ##-- 1st party imports
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

@Mixin(ErrorRaiser_m, FieldMatcher_m)
class FieldSubstitutor(IdenBlockMiddleware):
    """
      For a given field(s), and a given jgdv.SubstitutionFile,
    replace the field value as necessary in each entry.

    If force_single_value is True, only the first replacement will be used,
    others will be discarded

    eg: for target=['tags'],
    and subs({'AI': ['artificial_intelligence', 'agents', 'machine_learning'])
    and entry(fields={'tags': 'ai'})
    will give: entry(fields={''tags': ['artificial_intelligence', 'agents', 'machine_learning']})

    """

    def __init__(self, *, fields:list[str], subs:SubstitutionFile, force_single_value:bool=False, **kwargs):
        super().__init__(**kwargs)
        match fields:
            case list():
                self._target_fields = fields
            case x:
                raise TypeError(type(x))

        self._subs               = subs
        self._force_single_value = force_single_value
        self.set_field_matchers(white=self._target_fields, black=[])

    def transform_Entry(self, entry, library):
        if self._subs is None or not bool(self._subs):
            return [entry]

        match self.match_on_fields(entry, library):
            case model.Entry() as x:
                return [x]
            case Exception() as err:
                return [self.make_error_block(entry, err)]
            case x:
                raise TypeError(type(x))

    def field_h(self, field, entry):
        """  """
        match field.value:
            case str() as value if self._force_single_value:
                head, *_ = list(self._subs.sub(value))
                return [model.Field(field.key, head)]
            case str() as value:
                subs = list(self._subs.sub(value))
                return [model.Field(field.key, subs)]
            case list() | set() as value:
                result = self._subs.sub_many(*value)
                return [model.Field(field.key, result)]
            case value:
                return ValueError("Unsupported replacement field value type", entry.key, type(value))

        return []

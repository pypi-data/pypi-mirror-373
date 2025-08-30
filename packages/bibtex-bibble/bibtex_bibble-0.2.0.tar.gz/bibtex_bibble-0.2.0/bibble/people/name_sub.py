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
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)
from bibtexparser.middlewares.names import NameParts
from jgdv import Proto, Mixin
from jgdv.files.tags import SubstitutionFile

# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from . import _interface as API_N
from bibble.util.mixins import ErrorRaiser_m, FieldMatcher_m
from bibble.fields.field_substitutor import FieldSubstitutor
from bibble.util.name_parts import NameParts_d

# ##-- end 1st party imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##--|

@Proto(API.ReadTime_p)
class NameSubstitutor(FieldSubstitutor):
    """ replaces names in author and editor fields as necessary """

    def __init__(self, *, subs:SubstitutionFile, **kwargs):
        super().__init__(fields=[API_N.AUTHOR_K, API_N.EDITOR_K],
                         subs=subs,
                         **kwargs)

    def on_read(self):
        Never()

    def field_h(self, field, entry):
        match field.value:
            case str():
                return ValueError("Name parts should already be combined, but authors shouldn't be merged yet")
            case [*xs] if any(isinstance(x, NameParts|NameParts_d) for x in xs):
                return ValueError("Name parts should already be combined, but authors shouldn't be merged yet")
            case []:
                return [field]
            case [*xs]:
                clean_names = []
                for name in xs:
                    match self._subs.sub(name):
                        case None:
                            clean_names.append(name)
                        case set() as val:
                            head, *_ = val
                            clean_names.append(head)
                else:
                    return [model.Field(field.key, clean_names)]
            case value:
                return ValueError("Unsupported replacement field value type(%s): %s", entry.key, type(value))

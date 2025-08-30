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
from bibtexparser import exceptions as bexp
from bibtexparser import middlewares as ms
from bibtexparser.model import MiddlewareErrorBlock
from pylatexenc.latexencode import (RULE_REGEX, UnicodeToLatexConversionRule,
                                    UnicodeToLatexEncoder)

from jgdv import Proto, Mixin
# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from . import _interface as LAPI
from ._util import UnicodeHelper_m
from bibble.util.mixins import ErrorRaiser_m, FieldMatcher_m
from bibble.util.str_transform_m import StringTransform_m
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
    from jgdv import Maybe, Result
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    type U2LRule = UnicodeToLatexConversionRule
    type Entry = model.Entry
    type Field = model.Field
    type Block = model.Block
    from bibtexparser.library import Library
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##--|

##--|

@Proto(API.WriteTime_p, API.StrTransformer_p)
@Mixin(UnicodeHelper_m, FieldMatcher_m, StringTransform_m)
class LatexWriter(IdenBlockMiddleware):
    """ Unicode->Latex Transform.
    all strings in the library except urls, files, dois and crossrefs
    see https://pylatexenc.readthedocs.io/en/latest/latexencode/

    to customize the conversion rules, use pylatexenc.latexencode
    and call rebuild_encoder with them

    """

    _blacklist = ("url", "file", "doi", "crossref")

    def __init__(self, **kwargs):
        kwargs.setdefault(API.ALLOW_INPLACE_MOD_K, False)
        super().__init__(**kwargs)
        self.set_field_matchers(black=self._blacklist, white=[])
        self._total_options               = {}
        self._total_rules : list[U2LRule] = [
            self.build_encode_rule(LAPI.ENCODING_RULES)
        ]
        if kwargs.get(API.KEEP_MATH_K, True):
            self._total_rules.append(self.build_encode_rule(LAPI.MATH_RULES))

        if kwargs.get(API.ENCLOSE_URLS_K, False):
            self._total_rules.append(self.build_encode_rule(LAPI.URL_RULES))

        self.rebuild_encoder()

    def on_write(self):
        Never()

    def transform_Entry(self, entry: Entry, library: Library) -> list[Block]:
        match self.match_on_fields(entry, library):
            case model.Entry() as x:
                return [x]
            case Exception() as err:
                return [self.make_error_block(entry, err)]
            case x:
                raise TypeError(type(x))

    def field_h(self, field:model.Field, entry) -> Result[list[Field], Exception]:
        match self.transform_strlike(field.value):
            case Exception() as err:
                return err
            case x:
                return [model.Field(key=field.key, value=x)]

    def _transform_raw_str(self, python_string: str) -> Result[str, Exception]:
        try:
            return self._encoder.unicode_to_latex(python_string)
        except Exception as e:
            return e

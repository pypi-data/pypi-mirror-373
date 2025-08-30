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
from jgdv import Proto, Mixin
import bibtexparser
import bibtexparser.model as model
from bibtexparser.library import Library
from bibtexparser import exceptions as bexp
from bibtexparser import middlewares as ms
from bibtexparser.model import MiddlewareErrorBlock
# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from . import _interface as LAPI
from bibble.util.mixins import ErrorRaiser_m, FieldMatcher_m
from bibble.util.str_transform_m import StringTransform_m
from ._util import UnicodeHelper_m
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
    from jgdv import Maybe, VList, Result
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    type Entry = model.Entry
    type Block = model.Block
    type Field = model.Field
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##--|

@Proto(API.ReadTime_p)
@Mixin(UnicodeHelper_m, ErrorRaiser_m, FieldMatcher_m, StringTransform_m)
class LatexReader(IdenBlockMiddleware):
    """ Latex->unicode transform.
    all strings in the library, except urls, files, doi's and crossrefs
    """

    _blacklist = ("url", "file", "doi", "crossref")
    _total_rules   : dict
    _total_options : dict

    def __init__(self, *, extra:Maybe[dict]=None, **kwargs):
        super().__init__(**kwargs)
        self.set_field_matchers(black=self._blacklist, white=[])
        self._total_options = {
            LAPI.KEEP_BRACED_K : kwargs.pop(LAPI.KEEP_BRACED_K, False),
            LAPI.MATH_MODE_K   : kwargs.pop(LAPI.MATH_MODE_K, 'text'),
        }
        self._total_rules : dict[str, VList[LAPI.MacroTextSpec]] = {
            f"{self.metadata_key()}-simplify-urls" : self.build_decode_rule(LAPI.URL_SIMPL)
        }
        match extra:
            case dict():
                self._total_rules.update(extra)
            case None:
                pass

        self.rebuild_decoder()

    def on_read(self):
        Never()

    def transform_Entry(self, entry: Entry, library: Library) -> list[Block]:
        match self.match_on_fields(entry, library):
            case model.Entry() as x:
                return [x]
            case ValueError() as err:
                return [self.make_error_block(entry, err)]

    def field_h(self, field:Field, entry) -> Result[list[Field], Exception]:
        match self.transform_strlike(field.value):
            case Exception() as err:
                return err
            case x:
                return [model.Field(key=field.key, value=x)]

    def _transform_raw_str(self, python_string: str) -> Result[str, Exception]:
        """Transforms a python string to a latex string

        Returns:
            Tuple[str, str]: The transformed string and a possible error message
        """
        try:
            return self._decoder.latex_to_text(python_string)
        except Exception as e:
            return e

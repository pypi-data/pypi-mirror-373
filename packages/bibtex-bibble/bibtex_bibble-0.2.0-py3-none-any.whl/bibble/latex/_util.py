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
import collections
import contextlib
import hashlib
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref
import atexit # for @atexit.register
import faulthandler
# ##-- end stdlib imports

from pylatexenc.latexencode import (RULE_REGEX, UnicodeToLatexConversionRule,
                                    UnicodeToLatexEncoder)
from pylatexenc.latex2text import (LatexNodes2Text, MacroTextSpec,
                                   get_default_latex_context_db)
from pylatexenc.macrospec import LatexContextDb

from bibtexparser import model

from . import _interface as LAPI
from jgdv import Mixin
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
# from dataclasses import InitVar, dataclass, field
# from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError

if TYPE_CHECKING:
    from jgdv import Maybe, VList
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    type U2LRule = UnicodeToLatexConversionRule
    type Entry = model.Field
    type Block = model.Block
    from bibtexparser.library import Library
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:

# Body:

class UnicodeHelper_m:
    """
    A Helper for using pylatexenc

    Builds Encoders using lists of str pairs
    and Decoders using dicts
    """

    @staticmethod
    def prep_encode_tuples(tuples:list) -> list:
        """ prep tuples of str,str for conversion rules,
        as re.Pattern,str
        """
        result = []
        for x,y in tuples:
            assert(isinstance(y, str))
            match x:
                case str():
                    result.append((re.compile(x), y))
                case re.Pattern():
                    result.append((x, y))
                case x:
                    raise TypeError(type(x))
        else:
            return result

    @staticmethod
    def build_encode_rule(tuples:list) -> U2LRule:
        compiled = UnicodeHelper_m.prep_encode_tuples(tuples)
        return UnicodeToLatexConversionRule(rule_type=RULE_REGEX, rule=compiled)

    @staticmethod
    def build_decode_rule(pair:tuple) -> MacroTextSpec:
        name, replacement = pair
        return MacroTextSpec("url", simplify_repl="%s")

    @staticmethod
    def build_encoder(*, rules:list[str|U2LRule], kwargs:dict) -> UnicodeToLatexEncoder:
        if any(not isinstance(x, str|UnicodeToLatexConversionRule) for x in rules):
            raise TypeError("Encoding Rules need to be UniicodeToLatexConversionRules, use LatexWriter.build_encode_rule")

        rules.append(LAPI.DEFAULT_RULES_K)
        logging.debug("Building Latex Encoder: %s", rules)
        return UnicodeToLatexEncoder(conversion_rules=rules, **kwargs)

    @staticmethod
    def build_decoder(*, rules:dict[str,VList[MacroTextSpec]], kwargs:dict) -> LatexNodes2Text:
        context_db : LatexContextDb = get_default_latex_context_db()
        logging.debug("Building Latex Decoder: %s", rules)
        for cat, y in rules.items():
            match y:
                case list() if all(isinstance(y2, MacroTextSpec) for y2 in y):
                    context_db.add_context_category(cat, prepend=True, macros=y)
                case MacroTextSpec():
                     context_db.add_context_category(cat, prepend=True, macros=[y])
                case _:
                    raise TypeError("Bad Decode Rules Specified", cat, y)

        return LatexNodes2Text(latex_context=context_db, **kwargs)

    def rebuild_encoder(self, *, rules:Maybe[list[U2LRule]]=None, **kwargs) -> None:
        """ Accumulates rules and rebuilds the encoder """
        self._total_rules += [x for x in (rules or []) if x not in self._total_rules]
        self._total_options.update(kwargs)
        self._encoder = self.build_encoder(rules=self._total_rules[:], kwargs=self._total_options)

    def rebuild_decoder(self, *, rules:dict=None, **kwargs) -> None:
        self._total_rules.update(rules or {})
        self._total_options.update(kwargs)
        self._decoder = self.build_decoder(rules=self._total_rules, kwargs=self._total_options)

    def _test_encode(self, text) -> str:
        """ utility to test latex encoding """
        return self._encoder.unicode_to_latex(text)

    def _test_decode(self, text:str) -> str:
        """ utility to test decoding """
        return self._decoder.latex_to_text(text)

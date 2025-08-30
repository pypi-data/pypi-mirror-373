#!/usr/bin/env python3
"""

"""
from __future__ import annotations
# Imports:

# ##-- stdlib imports
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
import collections
import contextlib
import hashlib
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref
import atexit # for @atexit.register
import faulthandler
# ##-- end stdlib imports

import jinja2
from .writer import BibbleWriter
from bibble import _interface as API
from . import _interface as API_W
from bibble.util.mixins import MiddlewareValidator_m
from bibble.model import MetaBlock
from bibble.util import PairStack
from bibtexparser.writer import BibtexFormat

from ._util import Runner_m

# ##-- types
# isort: off
# General
import abc
import collections.abc
import typing
import types
from typing import cast, assert_type, assert_never
from typing import Generic, NewType, Never
from typing import no_type_check, final, override, overload
# Protocols and Interfaces:
from typing import Protocol, runtime_checkable
# isort: on
# ##-- end types

# ##-- type checking
# isort: off
if typing.TYPE_CHECKING:
    from typing import Final, ClassVar, Any, Self
    from typing import Literal, LiteralString
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable
    from logmod import Logger
    from bibtexparser.model import Block

    from jgdv import Maybe

    from bibtexparser.library import Library
    from bibtexparser.writer import BibtexFormat

    type Middleware = API.Middleware_p | API.BidirectionalMiddleware_p
## isort: on
# ##-- end type checking

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:
NEWLINE            : Final[str]   = "\n"
DEFAULT_TEMPLATES  : Final[dict]  = {
    "lib"          : "lib.bib.jinja",
    "header"       : "header.bib.jinja",
    "entry"        : "entry.bib.jinja",
    "footer"       : "footer.bib.jinja",
}
DEFAULT_LOADER     : Final[jinja2.BaseLoader]  = jinja2.PackageLoader("bibble", "_templates")

# Body:

class JinjaWriter(BibbleWriter):
    """
    Use jinja templates to write out bibtex
    """
    _env        : jinja2.Environment
    _templates  : dict[str, Maybe[jinja2.Template]]

    def __init__(self, stack:PairStack, *, format:Maybe[BibtexFormat]=None, logger:Maybe[Logger]=None, templates:Maybe[pl.Path]=None) -> None:
        x : Any
        super().__init__(stack, format=format, logger=logger)
        self._join_char = NEWLINE
        match templates:
            case None:
                loaders = [DEFAULT_LOADER]
            case pl.Path() as x:
                loaders = [jinja2.FileSystemLoader(x), DEFAULT_LOADER]
        self._env = jinja2.Environment(
            loader=jinja2.ChoiceLoader(loaders),
            autoescape=jinja2.select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
            )
        self._env.filters['wrap'] = self._wrap_braces
        self._templates = {}
        self.update_templates(DEFAULT_TEMPLATES)

    def update_templates(self, templates:dict[str, Maybe[str]]) -> None:
        for key, name in templates.items():
            match name:
                case None:
                    self._templates[key] = None
                case str() as x:
                    self._templates[key] = self._env.get_template(name)

    def make_header(self, library:Library, title:Maybe[str]=None) -> list[str]:
        if self._templates['header'] is None:
            return []
        return [self._templates['header'].render(title=title)]

    def make_footer(self, library, file:None|pl.Path=None) -> list[str]:
        if self._templates['footer'] is None:
            return []
        return [self._templates['footer'].render(file=file)]

    def make_lib(self, *, header:list[str], body:list[str], footer:list[str]) -> str:
        if self._templates['lib'] is None:
            return self._join_char.join([*header, *body, *footer]).strip()

        return self._templates['lib'].render(
            header=self._join_char.join(header),
            body=self._join_char.join(body),
            footer=self._join_char.join(footer),
            ).strip()

    def visit_entry(self, block:Block) -> list[str]:
        return [self._templates['entry'].render(entry_type=block.entry_type,
                                                key=block.key,
                                                available_keys=block.fields_dict.keys(),
                                                entry=block.fields_dict,
                                                )]


    def write(self, library, *, templates:Maybe[dict]=None, **kwargs) -> str:
        x : Any
        match templates:
            case None:
                pass
            case dict() as x:
                self.update_templates(templates)
        return super().write(library, **kwargs)


    def _wrap_braces(self, val:str) -> str:
        return "".join(["{", str(val), "}"])

#!/usr/bin/env python3
"""

"""
# ruff: noqa: ANN201, ARG001, ANN001, ARG002, ANN202

# Imports
from __future__ import annotations

# ##-- stdlib imports
import logging as logmod
import pathlib as pl
import warnings
# ##-- end stdlib imports

# ##-- 3rd party imports
import pytest
# ##-- end 3rd party imports

import bibble._interface as API
from bibtexparser import Library
from .. import Reader
from bibble.bidi import BraceWrapper

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

# Vars:
EXAMPLE_BIB : Final[str] = """
@article{test_art,
  title  = {Blah},
  year   = {1992},
  author = {Bob},
}

"""
# Body:

class TestBibbleReader:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match Reader([]):
            case API.Reader_p():
                assert(True)
            case x:
                 assert(False), x

    def test_read(self):
        reader = Reader([])
        match reader.read(EXAMPLE_BIB):
            case Library() as lib:
                assert(len(lib.entries) == 1)
                entry                                    = lib.entries[0]
                assert(entry.key                         == "test_art")
                assert(entry.entry_type                  == "article")
                assert(entry.fields_dict['title'].value  == "{Blah}")
                assert(entry.fields_dict['author'].value == "{Bob}")
                assert(entry.fields_dict['year'].value   == "{1992}")
            case x:
                 assert(False), x


    def test_read_with_middleware(self):
        reader = Reader([BraceWrapper()])
        match reader.read(EXAMPLE_BIB):
            case Library() as lib:
                assert(len(lib.entries) == 1)
                entry                                    = lib.entries[0]
                assert(entry.key                         == "test_art")
                assert(entry.entry_type                  == "article")
                assert(entry.fields_dict['title'].value  == "Blah")
                assert(entry.fields_dict['author'].value == "Bob")
                assert(entry.fields_dict['year'].value   == "1992")
            case x:
                 assert(False), x

    @pytest.mark.skip
    def test_todo(self):
        pass

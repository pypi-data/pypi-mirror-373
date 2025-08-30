#!/usr/bin/env python3
"""

"""
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

from bibtexparser import Library, model
import bibble._interface as API
from bibble.bidi import BraceWrapper
from .. import RstWriter
from importlib.resources import files

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

##-- data
data_path = files(__package__) / "_data"
##-- end data

# Vars:
EXAMPLE_EMPTY_LIB : Final[pl.Path] = cast("pl.Path", data_path) / "empty_lib.rst"
EXAMPLE_LIB       : Final[pl.Path] = cast("pl.Path", data_path) / "simple_lib.rst"

# Body:

class TestRstWriter:

    def test_sanity(self):
        assert(True is not False)

    def test_ctor(self):
        match RstWriter([]):
            case API.Writer_p():
                assert(True)
            case x:
                 assert(False), x

    def test_write_empty_lib(self):
        lib = Library([])
        writer = RstWriter([])
        match writer.write(lib):
            case str() as x:
                assert(bool(x))
                assert(x.strip() == EXAMPLE_EMPTY_LIB.read_text().strip())
                assert(True)
            case x:
                 assert(False), x

    def test_basic_entry_write(self):
        lib = Library([model.Entry("article", "test_art", [
            model.Field("year", 1992),
            model.Field("author", "Bob"),
            model.Field("title", "Testing Title"),
            model.Field("tags", "blah,bloo"),
        ])])
        writer = RstWriter([])
        match writer.write(lib):
            case str() as x:
                assert(bool(x))
                assert(x.strip() == EXAMPLE_LIB.read_text().strip())
                assert(True)
            case x:
                 assert(False), x

    @pytest.mark.skip
    def test_todo(self):
        pass

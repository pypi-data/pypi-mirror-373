#!/usr/bin/env python3
"""

"""
# ruff: noqa: ANN201, ARG001, ANN001, ARG002, ANN202, B011

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
from .. import Writer
from bibtexparser import Library, model
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
EXAMPLE_NO_WRAP : Final[str] = """
@article{test_art,
 year         = 1992,
 author       = Bob,
 title        = Testing Title,
}
"""

EXAMPLE_WRAP : Final[str] = """
@article{test_art,
 year         = {1992},
 author       = {Bob},
 title        = {Testing Title},
}
"""

EXAMPLE_ALIGNED : Final[str] = """
@article{test_art,
year                        = {1992},
author                      = {Bob},
title                       = {Testing Title},
}
"""

# Body:

class TestBibbleWriter:

    def test_sanity(self):
        assert(True is not False)

    def test_ctor(self):
        match Writer([]):
            case API.Writer_p():
                assert(True)
            case x:
                 assert(False), x

    def test_basic_write(self):
        lib = Library([model.Entry("article", "test_art", [
            model.Field("year", 1992),
            model.Field("author", "Bob"),
            model.Field("title", "Testing Title"),
        ])])
        writer = Writer([])
        match writer.write(lib):
            case str() as x:
                assert(x.strip() == EXAMPLE_NO_WRAP.strip())
                assert(True)
            case x:
                 assert(False), x

    def test_write_with_wrap(self):
        lib = Library([model.Entry("article", "test_art", [
            model.Field("year", 1992),
            model.Field("author", "Bob"),
            model.Field("title", "Testing Title"),
        ])])
        writer = Writer([BraceWrapper()])
        match writer.write(lib):
            case str() as x:
                assert(x.strip() == EXAMPLE_WRAP.strip())
                assert(True)
            case x:
                 assert(False), x

    def test_custom_aligned(self):
        column = 30
        lib = Library([model.Entry("article", "test_art", [
            model.Field("year", 1992),
            model.Field("author", "Bob"),
            model.Field("title", "Testing Title"),
        ])])
        writer = Writer([BraceWrapper()])
        writer.format.value_column = column
        writer.format.indent = ""

        match writer.write(lib):
            case str() as x:
                assert(x.strip() == EXAMPLE_ALIGNED.strip())
                # All lines with values (so not top and last)
                # must be the start of a value at 'column'.
                # ie: '{'
                assert(all([x[column] == "{" for x in x.strip().splitlines()[1:-1]]))
                assert(True)
            case x:
                 assert(False), x

    @pytest.mark.skip
    def test_todo(self):
        pass

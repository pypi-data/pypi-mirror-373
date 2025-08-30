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


##--|
import bibble._interface as API
from .. import JinjaWriter
from bibtexparser import Library, model
from bibble.bidi import BraceWrapper
##--|

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

    from jgdv import Maybe
## isort: on
# ##-- end type checking

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:
TEST_TEMPLATES : Final[pl.Path] = pl.Path(__file__).parent / "_templates"

# Body:
class TestJinjaWriter:

    @pytest.fixture(scope="function")
    def lib(self, mocker):
        lib = Library([model.Entry("article", "test_art", [
            model.Field("year", 1992),
            model.Field("author", "Bob"),
            model.Field("title", "Testing Title"),
        ])])
        return lib


    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_basic(self):
        match JinjaWriter([]):
            case API.Writer_p():
                assert(True)
            case x:
                raise TypeError(type(x))

    def test_basic_write(self, lib):
        writer = JinjaWriter([], templates=TEST_TEMPLATES)
        templates = {
            "entry": "just_title_entry.jinja",
            "lib" : None,
        }
        match writer.write(lib, templates=templates):
            case str() as x:
                assert(x.strip() == "Testing Title")
                assert(True)
            case x:
                 assert(False), x


    def test_write_template_control(self, lib):
        templates = {
            "entry"   : "title_year_entry.jinja",
            "header"  : "simple_header.jinja",
            "footer"  : "simple_footer.jinja",
            "lib"     : None,
        }
        expect = [
            "A Simple Header",
            "Testing Title : 1992",
            "A Simple Footer",
        ]
        writer = JinjaWriter([], templates=TEST_TEMPLATES)
        match writer.write(lib, templates=templates):
            case str() as x:
                for act,exp in zip(x.split("\n"), expect, strict=True):
                    assert(act == exp)
            case x:
                 assert(False), x


    def test_write_lib_template(self, lib):
        templates = {
            "entry"   : "title_year_entry.jinja",
            "header"  : "simple_header.jinja",
            "footer"  : "simple_footer.jinja",
            "lib"     : "simple_lib.jinja",
        }
        expect = [
            "A Simple Header",
            "blah",
            "Testing Title : 1992",
            "bloo",
            "A Simple Footer",
        ]
        writer = JinjaWriter([], templates=TEST_TEMPLATES)
        match writer.write(lib, templates=templates):
            case str() as x:
                for act,exp in zip(x.split("\n"), expect, strict=True):
                    assert(act == exp)
            case x:
                 assert(False), x


    def test_write_bib_entry_template(self, lib):
        templates = {
            "header"  : None,
            "footer"  : None,
            "lib"     : None,
        }
        expect = """
        @article{test_art,
        year   = {1992},
        author = {Bob},
        title  = {Testing Title},
        }
        """

        writer = JinjaWriter([], templates=TEST_TEMPLATES)
        match writer.write(lib, templates=templates):
            case str() as x:
                for act,exp in zip(x.strip().split("\n"), expect.strip().split("\n"), strict=True):
                    assert(act.strip() == exp.strip())
            case x:
                 assert(False), x



    ##--|
    @pytest.mark.skip
    def test_todo(self):
        pass

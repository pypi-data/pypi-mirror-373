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
from bibtexparser import model
from bibtexparser.library import Library
from bibble.model import FailedBlock
from .. import FailureHandler

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

# Vars:

# Body:

class TestFailureHandler:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match FailureHandler(file="blah"):
            case API.Middleware_p() as fh:
                assert(fh.file_target == pl.Path("blah"))
            case x:
                 assert(False), x

    def test_good_library(self, caplog):
        obj = FailureHandler()
        lib = Library()
        match obj.transform(lib):
            case Library():
                assert(True)
            case x:
                 assert(False), x

        assert("Bad Block" not in caplog.text)

    def test_bad_library(self, caplog):
        obj = FailureHandler()
        lib = Library()
        bad_entry = model.Entry("test", "blah", [], 0, "this is some raw text")
        lib.add(FailedBlock(block=bad_entry, error=ValueError("Couldn't parse"), source="test"))
        match obj.transform(lib):
            case Library():
                assert(True)
            case x:
                 assert(False), x

        assert("Bad <Entry>" in caplog.text)

    def test_bad_library_write(self, caplog, tmp_path):
        obj = FailureHandler(file=tmp_path / "failure.log")
        assert(not obj.file_target.exists())
        lib = Library()
        bad_entry = model.Entry("test", "blah", [], 0, "this is some raw text")
        lib.add(FailedBlock(block=bad_entry, error=ValueError("Couldn't parse"), source="test"))
        match obj.transform(lib):
            case Library():
                assert(True)
            case x:
                 assert(False), x

        assert("(1/1) [test] Bad <Entry>: 0" in caplog.text)
        assert(obj.file_target.exists())
        log_text = obj.file_target.read_text()

        for x in ["--------------------",
                  "(1/1) [test] Bad <Entry>: 0",
                  "Error: Couldn't parse",
                  "this is some raw text",
                  ]:
            assert(x in log_text), x


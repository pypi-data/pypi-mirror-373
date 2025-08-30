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
from bibtexparser import model
from bibtexparser.library import Library
from .. import DuplicateKeyHandler
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

class TestDuplicateHandler:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match DuplicateKeyHandler():
            case API.Middleware_p():
                assert(True)
            case x:
                raise TypeError(type(x))

    def test_good_library(self, caplog):
        obj = DuplicateKeyHandler()
        lib = Library()
        match obj.transform(lib):
            case Library():
                assert(True)
            case x:
                 assert(False), x

        assert("Duplicate Key" not in caplog.text)

    def test_bad_library_for_keys(self, caplog):
        obj = DuplicateKeyHandler()
        lib = Library()
        orig_entry =  model.Entry("test", "blah", [], 0, "this is some raw text")
        bad_entry = model.Entry("test", "blah", [], 0, "a duplicate entry key block")
        lib.add(orig_entry)
        assert(not lib.failed_blocks)
        lib.add(bad_entry)
        assert(lib.failed_blocks)
        match obj.transform(lib):
            case Library() as l2:
                assert(lib is l2)
                assert(len(l2.entries) == 2)
                assert(not l2.failed_blocks)
                assert(True)
            case x:
                 assert(False), x

        assert("Duplicate Key" in caplog.text)


    def test_bad_library_for_fields(self, caplog):
        obj = DuplicateKeyHandler()
        lib = Library()
        bad_entry = model.Entry("test", "blah",
                                [
                                    model.Field("bloo", "aweg"),
                                    model.Field("bloo", "qqqq")
                                ],
                                0, "a duplicate entry key block")
        assert("bloo_2" not in bad_entry)
        fail_block = model.DuplicateFieldKeyBlock(["bloo"], bad_entry)
        lib.add(fail_block)
        assert(lib.failed_blocks)
        match obj.transform(lib):
            case Library() as l2:
                assert(lib is l2)
                assert(len(l2.entries) == 1)
                assert(not l2.failed_blocks)
                assert(True)
            case x:
                 assert(False), x

        assert("duplicate fields" in caplog.text)
        assert("bloo" in bad_entry)
        assert("bloo_2" in bad_entry)

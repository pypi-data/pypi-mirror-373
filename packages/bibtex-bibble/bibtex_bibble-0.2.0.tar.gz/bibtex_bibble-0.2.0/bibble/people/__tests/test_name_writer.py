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
from bibtexparser import model, Library
from .. import NameWriter
from bibble.util.name_parts import NameParts_d

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

# Body:

class TestNameWriter:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match NameWriter(parts=True, authors=True):
            case API.Middleware_p():
                assert(True)
            case x:
                 assert(False), x

    def test_basic_merge(self):
        authors = model.Field("authors", ["Bill", "Bob"])
        entry = model.Entry("test", "test:blah", [authors])
        lib   = Library([entry])
        mid   = NameWriter(parts=True, authors=True)
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(l2.entries[0].fields[0].value == "Bill and Bob")
            case x:
                assert(False), x

    def test_merge_nameparts(self):
        authors = model.Field("authors", [
            NameParts_d(first=["Bill"], last=["Builder"]),
            NameParts_d(first=["Bob"], von=["de", "la"], last=["Builder"]),
        ])
        entry = model.Entry("test", "test:blah", [authors])
        lib   = Library([entry])
        mid   = NameWriter(parts=True, authors=True)
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(l2.entries[0].fields[0].value == "Builder, Bill and de la Builder, Bob")
            case x:
                assert(False), x

    @pytest.mark.skip
    def test_todo(self):
        pass

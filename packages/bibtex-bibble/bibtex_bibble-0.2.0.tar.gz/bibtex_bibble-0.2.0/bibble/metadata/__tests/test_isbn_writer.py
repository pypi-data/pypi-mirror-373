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

from bibtexparser import model, Library
import bibble._interface as API
from .. import IsbnWriter

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

class TestIsbnWriter:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match IsbnWriter():
            case API.AdaptiveMiddleware_p():
                assert(True)
            case x:
                 assert(False), x
                 
    def test_basic_format(self):
        field = model.Field("isbn", "9780192805928")
        entry = model.Entry("test", "test", [field])
        lib   = Library([entry])
        mid   = IsbnWriter()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(l2.entries[0].fields[0].value == "978-0-19-280592-8")
                assert(not l2.failed_blocks)
            case x:
                 assert(False), x

    def test_basic_format_fail(self):
        field = model.Field("isbn", "978019")
        entry = model.Entry("test", "test", [field])
        lib   = Library([entry])
        mid   = IsbnWriter()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(bool(l2.failed_blocks))
            case x:
                 assert(False), x
                 

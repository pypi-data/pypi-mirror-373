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
from .. import IsbnValidator

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

class TestIsbnValidator:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match IsbnValidator():
            case API.AdaptiveMiddleware_p():
                assert(True)
            case x:
                 assert(False), x
                 
    def test_basic_check(self):
        field = model.Field("isbn", "9780192805928")
        entry = model.Entry("test", "test", [field])
        lib   = Library([entry])
        mid   = IsbnValidator()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(l2.entries[0].fields[0].value == "9780192805928")
                assert(not l2.failed_blocks)
            case x:
                 assert(False), x
                 

    def test_basic_check_fail(self):
        field = model.Field("isbn", "978019")
        entry = model.Entry("test", "test", [field])
        lib   = Library([entry])
        mid   = IsbnValidator()
        match mid.transform(lib):
            case Library() as l2:
                assert(bool(l2.failed_blocks))
                assert(l2 is lib)
            case x:
                 assert(False), x
                 

        
    @pytest.mark.skip
    def test_todo(self):
        pass

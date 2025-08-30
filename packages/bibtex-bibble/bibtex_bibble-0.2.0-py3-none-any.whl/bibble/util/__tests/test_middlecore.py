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
from ..middlecore import IdenLibraryMiddleware, IdenBlockMiddleware

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

class TestIdenLibMiddleware:

    @pytest.fixture(scope="function")
    def setup(self):
        pass

    @pytest.fixture(scope="function")
    def cleanup(self):
        pass

    ##--|

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match IdenLibraryMiddleware():
            case IdenLibraryMiddleware():
                assert(True)
            case x:
                 assert(False), x

    def test_basic_inplace(self):
        lib = Library()
        mid = IdenLibraryMiddleware()
        assert(mid.transform(lib) is lib)

    def test_basic_out_of_place(self):
        lib = Library()
        mid = IdenLibraryMiddleware(allow_inplace_modification=False)
        assert(mid.transform(lib) is not lib)

    ##--|

    @pytest.mark.skip
    def test_todo(self):
        pass

class TestIdenBlockMiddleware:

    @pytest.fixture(scope="function")
    def setup(self):
        pass

    @pytest.fixture(scope="function")
    def cleanup(self):
        pass

    ##--|

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match IdenBlockMiddleware():
            case IdenBlockMiddleware():
                assert(True)
            case x:
                 assert(False), x

    def test_basic_inplace(self):
        lib = Library()
        mid = IdenBlockMiddleware()
        assert(mid.transform(lib) is lib)

    def test_basic_out_of_place(self):
        lib = Library()
        mid = IdenLibraryMiddleware(allow_inplace_modification=False)
        assert(mid.transform(lib) is not lib)

    ##--|

    @pytest.mark.skip
    def test_todo(self):
        pass

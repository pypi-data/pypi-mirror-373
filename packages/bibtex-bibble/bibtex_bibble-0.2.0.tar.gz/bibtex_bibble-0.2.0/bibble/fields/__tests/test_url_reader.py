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

from bibtexparser.library import Library
from bibtexparser import model
import bibble._interface as API
from .. import _interface as API_F
from .. import CleanUrls, ExpandUrls

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

class TestCleanUrls:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match CleanUrls():
            case CleanUrls():
                assert(True)
            case x:
                 assert(False), x

    def test_clean_DOI(self):
        mid           = CleanUrls()
        entry1        = model.Entry("test", "first",  [
            model.Field("doi", "https://doi.org/blah/bloo"),
        ])
        lib    = Library()
        lib.add(entry1)
        assert(mid.transform(lib) is lib)
        assert(entry1.fields_dict['doi'].value == "blah/bloo")

    def test_clean_URL(self):
        mid           = CleanUrls()
        entry1        = model.Entry("test", "first",  [
            model.Field("url", "db/blah/bloo"),
        ])
        lib    = Library()
        lib.add(entry1)
        assert(mid.transform(lib) is lib)
        assert(entry1.fields_dict['biburl'].value == "https://dblp.org/db/blah/bloo")
        assert("bibsource" in entry1.fields_dict)

    def test_clean_EE(self):
        mid           = CleanUrls()
        entry1        = model.Entry("test", "first",  [
            model.Field("ee", "https:://www.blah.com"),
        ])
        lib    = Library()
        lib.add(entry1)
        assert(mid.transform(lib) is lib)
        assert(entry1.fields_dict['url'].value == "https:://www.blah.com")
        assert(entry1.fields_dict['ee'].value == "")

    
class TestExpandUrls:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133
        
    def test_ctor(self):
        match ExpandUrls():
            case API.AdaptiveMiddleware_p():
                assert(True)
            case x:
                 assert(False), x

    @pytest.mark.skip
    def test_todo(self):
        pass

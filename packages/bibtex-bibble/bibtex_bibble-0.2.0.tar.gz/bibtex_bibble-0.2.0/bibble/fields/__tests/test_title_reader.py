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
from bibble.fields import TitleCleaner, TitleSplitter
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

class TestTitleCleaner:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match TitleCleaner():
            case TitleCleaner():
                assert(True)
            case x:
                 assert(False), x

    def test_clean(self):
        initial_title =  "   a test title with whitespace   "
        mid    = TitleCleaner()
        entry1 = model.Entry("test", "first",  [
            model.Field("title", initial_title),
            model.Field("subtitle", initial_title),
        ])
        lib    = Library()
        lib.add(entry1)
        assert(mid.transform(lib) is lib)
        assert(initial_title.endswith(" "))
        assert(entry1.fields_dict['title'].value == initial_title.strip())
        assert(entry1.fields_dict['subtitle'].value == initial_title.strip())

    def test_clean_ignores_other_fields(self):
        initial_title =  "  a test title with whitespace   "
        mid    = TitleCleaner()
        entry1 = model.Entry("test", "first",  [
            model.Field("title", initial_title),
            model.Field("not_title", initial_title),
        ])
        lib    = Library()
        lib.add(entry1)
        assert(mid.transform(lib) is lib)
        assert(initial_title.endswith(" "))
        assert(entry1.fields_dict['title'].value == initial_title.strip())
        assert(entry1.fields_dict['not_title'].value == initial_title)

class TestTitleSplitter:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match TitleSplitter():
            case API.AdaptiveMiddleware_p():
                assert(True)
            case x:
                 assert(False), x

    def test_clean(self):
        initial_title =  "  a test title with whitespace   "
        mid    = TitleSplitter()
        entry1 = model.Entry("test", "first",  [
            model.Field("title", initial_title),
            model.Field("subtitle", initial_title),
        ])
        lib    = Library()
        lib.add(entry1)
        assert(mid.transform(lib) is lib)
        assert(initial_title.endswith(" "))
        assert(entry1.fields_dict['title'].value == initial_title.strip())
        assert(entry1.fields_dict['subtitle'].value == initial_title.strip())

    def test_clean_ignores_other_fields(self):
        initial_title =  "  a test title with whitespace   "
        mid    = TitleSplitter()
        entry1 = model.Entry("test", "first",  [
            model.Field("title", initial_title),
            model.Field("not_title", initial_title),
        ])
        lib    = Library()
        lib.add(entry1)
        assert(mid.transform(lib) is lib)
        assert(initial_title.endswith(" "))
        assert(entry1.fields_dict['title'].value == initial_title.strip())
        assert(entry1.fields_dict['not_title'].value == initial_title)

    def test_split(self):
        initial_title =  "  a test title with whitespace : the subtitle   "
        target = "a test title with whitespace"
        target_sub = "the subtitle"
        mid    = TitleSplitter()
        entry1 = model.Entry("test", "first",  [
            model.Field("title", initial_title),
        ])
        lib    = Library()
        lib.add(entry1)
        assert(mid.transform(lib) is lib)
        assert(initial_title.endswith(" "))
        assert(entry1.fields_dict['title'].value == target)
        assert(entry1.fields_dict['subtitle'].value == target_sub)

    def test_split_doesnt_override_subtitle(self):
        initial_title =  "  a test title with whitespace : the subtitle   "
        initial_sub   =  " diff subtitle "
        target_sub    = "diff subtitle"
        mid           = TitleSplitter()
        entry1        = model.Entry("test", "first",  [
            model.Field("title", initial_title),
            model.Field("subtitle", initial_sub),
        ])
        lib    = Library()
        lib.add(entry1)
        assert(mid.transform(lib) is lib)
        assert(initial_title.endswith(" "))
        assert(entry1.fields_dict['title'].value == initial_title.strip())
        assert(entry1.fields_dict['subtitle'].value == target_sub)

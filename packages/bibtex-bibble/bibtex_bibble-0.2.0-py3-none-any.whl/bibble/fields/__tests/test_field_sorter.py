#!/usr/bin/env python3
"""

"""
from __future__ import annotations

import logging as logmod
import pathlib as pl
from typing import (Any, Callable, ClassVar, Generic, Iterable, Iterator,
                    Mapping, Match, MutableMapping, Sequence, Tuple, TypeAlias,
                    TypeVar, cast)
import warnings

import pytest
from bibtexparser import model
import bibble._interface as API
from bibble.fields import FieldSorter

logging = logmod.root

class TestFieldSorter:

    @pytest.fixture(scope="function")
    def sorter(self):
        return FieldSorter(first=["title", "author", "editor"], last=["doi", "url", "file"])

    @pytest.fixture(scope="function")
    def entry(self):
        return model.Entry("book", "blah", [])

    def get_field_order(self, entry) -> list[str]:
        return [x.key for x in entry.fields]

    ##--|

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self, sorter):
        match sorter:
            case API.Middleware_p():
                assert(True)
            case x:
                 assert(False), x

    def test_basic(self, sorter, entry):
        result = sorter.transform_Entry(entry, None)
        assert(result == [entry])

    def test_one_field(self, sorter, entry):
        entry.set_field(model.Field("test", ""))
        result = sorter.transform_Entry(entry, None)
        assert(result == [entry])

    def test_two_fields(self, sorter, entry):
        entry.set_field(model.Field("author", ""))
        entry.set_field(model.Field("title", ""))
        assert(self.get_field_order(entry) == ["author", "title"])
        result = sorter.transform_Entry(entry, None)
        assert(self.get_field_order(entry) == ["title", "author"])

    def test_firsts_and_lasts(self, sorter, entry):
        entry.set_field(model.Field("author", ""))
        entry.set_field(model.Field("file", ""))
        entry.set_field(model.Field("title", ""))
        entry.set_field(model.Field("misc", ""))
        assert(self.get_field_order(entry) == ["author", "file", "title", "misc"])
        result = sorter.transform_Entry(entry, None)
        assert(self.get_field_order(entry) == ["title", "author", "misc", "file"])

    def test_key_stemming(self, sorter, entry):
        entry.set_field(model.Field("file2", ""))
        entry.set_field(model.Field("file3", ""))
        entry.set_field(model.Field("file4", ""))
        entry.set_field(model.Field("file", ""))
        assert(self.get_field_order(entry) == ["file2", "file3", "file4", "file"])
        result = sorter.transform_Entry(entry, None)
        assert(self.get_field_order(entry) == ["file", "file2", "file3", "file4"])

    def test_stem_sorting(self, sorter, entry):
        entry.set_field(model.Field("file2", ""))
        entry.set_field(model.Field("url", ""))
        entry.set_field(model.Field("doi", ""))
        entry.set_field(model.Field("file", ""))
        assert(self.get_field_order(entry) == ["file2", "url", "doi", "file"])
        result = sorter.transform_Entry(entry, None)
        assert(self.get_field_order(entry) == ["doi", "url", "file", "file2"])

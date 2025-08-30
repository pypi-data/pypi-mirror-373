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
from .. import TagsReader

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

class TestTagsReader:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    @pytest.mark.skip
    def test_ctor(self):
        match TagsReader():
            case API.AdaptiveMiddleware_p():
                assert(True)
            case x:
                 assert(False), x

    def test_no_tags_read(self):
        entry = model.Entry("test", "test:blah", [])
        lib   = Library([entry])
        mid   = TagsReader()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(l2.entries[0].fields[0].value == set())
            case x:
                 assert(False), x

    def test_basic_tag_read(self):
        tags  = model.Field("tags", "ai,machine_learning,logic")
        entry = model.Entry("test", "test:blah", [tags])
        lib   = Library([entry])
        mid   = TagsReader()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(l2.entries[0].fields[0].value == {"ai","machine_learning","logic"})
            case x:
                 assert(False), x

    def test_basic_norm_read(self):
        # note: space between machine and learning
        tags  = model.Field("tags", "ai   ,machine learning,   logic")
        entry = model.Entry("test", "test:blah", [tags])
        lib   = Library([entry])
        mid   = TagsReader()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(l2.entries[0].fields[0].value == {"ai","machine_learning","logic"})
            case x:
                 assert(False), x

    def test_tag_accumulation(self):
        # note: space between machine and learning
        tags1  = model.Field("tags", "ai   ,machine learning,   logic")
        entry1 = model.Entry("test", "test:blah", [tags1])
        lib1   = Library([entry1])

        tags2  = model.Field("tags", "anthropology,literature")
        entry2 = model.Entry("test", "test:blah", [tags2])
        lib2   = Library([entry2])

        mid   = TagsReader(clear=False)
        mid.transform(lib1)
        assert(len(mid._all_tags) == 3)
        for tag in {"ai","machine_learning", "logic"}:
            assert(tag in mid._all_tags)

        mid.transform(lib2)
        assert(len(mid._all_tags) == 5)
        for tag in {"ai","machine_learning", "logic", "anthropology", "literature"}:
            assert(tag in mid._all_tags)

    def test_todo(self):
        pass

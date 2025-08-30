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

from bibtexparser import model, Library
import bibble._interface as API
from .. import TagsWriter

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

class TestTagsWriter:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match TagsWriter():
            case API.AdaptiveMiddleware_p():
                assert(True)
            case x:
                 assert(False), x

    def test_basic_write(self):
        tags  = model.Field("tags", {"ai","machine_learning","literature"})
        entry = model.Entry("test", "test:blah", [tags])
        lib   = Library([entry])
        mid   = TagsWriter()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(l2.entries[0].fields[0].value == "ai,literature,machine_learning")
            case x:
                 assert(False), x

    def test_to_keywords(self):
        tags  = model.Field("tags", {"ai","machine_learning","literature"})
        entry = model.Entry("test", "test:blah", [tags])
        lib   = Library([entry])
        mid   = TagsWriter(to_keywords=True)
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert("keywords" in l2.entries[0].fields_dict)
                assert(l2.entries[0].fields_dict['keywords'].value == "ai,literature,machine_learning")
            case x:
                 assert(False), x

    def test_no_tags_write(self):
        entry = model.Entry("test", "test:blah", [])
        lib   = Library([entry])
        mid   = TagsWriter()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(l2.entries[0].fields[0].value == "")
            case x:
                 assert(False), x

    @pytest.mark.skip
    def test_todo(self):
        pass

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

from jgdv.files.tags import SubstitutionFile
from bibtexparser import model
from bibtexparser.library import Library
import bibble._interface as API
import bibble.model as bmodel
from .. import FieldSubstitutor

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
class TestFieldSubstitutor:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match FieldSubstitutor(fields=[], subs={}):
            case API.AdaptiveMiddleware_p():
                assert(True)
            case x:
                 assert(False), x

    def test_substitution(self):
        subs   = SubstitutionFile()
        subs.update(("bob", ["bob", "bill", "jan"]))
        mid    = FieldSubstitutor(name="test", fields=["author"], subs=subs)
        entry1 = model.Entry("test", "first",  [model.Field("author", "bob")])
        entry2 = model.Entry("test", "second", [model.Field("author", "jill")])
        entry3 = model.Entry("test", "third",  [model.Field("author", "bob")])
        lib    = Library()
        lib.add(entry1)
        lib.add(entry2)
        lib.add(entry2)
        assert(mid.transform(lib) is lib)
        assert(set(entry1.fields_dict['author'].value) == {"bob", "bill", "jan"})
        assert(set(entry2.fields_dict['author'].value) == {"jill"})

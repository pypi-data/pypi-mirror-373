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

from bibtexparser import Library, model
import bibble._interface as API
from .. import NameReader
from ..name_reader import _SplitAuthors_m, _NameToParts_m, NameParts_d

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

class TestSplitAuthors:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_basic_split(self):
        obj = _SplitAuthors_m()
        match obj._split_authors("bob and jim"):
            case ["bob", "jim"]:
                assert(True)
            case x:
                 assert(False), x

    def test_no_split(self):
        obj = _SplitAuthors_m()
        match obj._split_authors("{bob and jim}"):
            case ["{bob and jim}"]:
                assert(True)
            case x:
                 assert(False), x

    def test_split_some(self):
        obj = _SplitAuthors_m()
        match obj._split_authors("andy and {bob and jim} and jill"):
            case ["andy", "{bob and jim}", "jill"]:
                assert(True)
            case x:
                 assert(False), x

    def test_split_nothing(self):
        obj = _SplitAuthors_m()
        match obj._split_authors(""):
            case []:
                assert(True)
            case x:
                assert(False), x

class TestNameToParts:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_basic(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("Bob"):
            case NameParts_d() as np:
                assert(np.last == ["Bob"])
            case x:
                 assert(False), x

    def test_first_last(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("Bob Builder"):
            case NameParts_d() as np:
                assert(np.first == ["Bob"])
                assert(np.last == ["Builder"])
            case x:
                 assert(False), x

    def test_first_initials_last(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("Bob A. B. C. Builder"):
            case NameParts_d() as np:
                assert(np.first == ["Bob", "A.", "B.", "C."])
                assert(np.last == ["Builder"])
            case x:
                 assert(False), x

    def test_first_von_last(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("Bob von Builder"):
            case NameParts_d() as np:
                assert(np.first == ["Bob"])
                assert(np.last == ["Builder"])
                assert(np.von == ["von"])
            case x:
                 assert(False), x

    def test_first_de_la_last(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("Bob de la Builder"):
            case NameParts_d() as np:
                assert(np.first == ["Bob"])
                assert(np.last == ["Builder"])
                assert(np.von == ["de", "la"])
            case x:
                 assert(False), x

    def test_last_first(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("Builder, Bob"):
            case NameParts_d() as np:
                assert(np.first == ["Bob"])
                assert(np.last == ["Builder"])
            case x:
                 assert(False), x

    def test_von_last_first(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("von Builder, Bob"):
            case NameParts_d() as np:
                assert(np.first == ["Bob"])
                assert(np.last == ["Builder"])
                assert(np.von == ["von"])
            case x:
                 assert(False), x

    def test_von_last_jr_first(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("von Builder, jr, Bob"):
            case NameParts_d() as np:
                assert(np.first == ["Bob"])
                assert(np.last == ["Builder"])
                assert(np.von == ["von"])
                assert(np.jr == ["jr"])
            case x:
                 assert(False), x

    def test_last_first_initials(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("Builder, Bob A. B. C."):
            case NameParts_d() as np:
                assert(np.first == ["Bob", "A.", "B.", "C."])
                assert(np.last == ["Builder"])
            case x:
                 assert(False), x

    def test_wrapped(self):
        obj = _NameToParts_m()
        match obj._name_to_parts("{The Order}"):
            case NameParts_d() as np:
                assert(np.last == ["{The Order}"])
            case x:
                 assert(False), x

class TestNameReader:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match NameReader():
            case API.Middleware_p():
                assert(True)
            case x:
                 assert(False), x

    def test_split_names(self):
        authors = model.Field("author", "Bill and Bob")
        entry   = model.Entry("test", "test:blah", [authors])
        lib     = Library([entry])
        mid     = NameReader(authors=True, parts=False)
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(l2.entries[0].fields[0].value == ["Bill", "Bob"])
            case x:
                 assert(False), x

    def test_name_parts(self):
        authors = model.Field("author", "Bill and Bob")
        entry   = model.Entry("test", "test:blah", [authors])
        lib     = Library([entry])
        mid     = NameReader(authors=True, parts=True)
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(len(l2.entries[0].fields[0].value) == 2)
            case x:
                 assert(False), x

        match l2.entries[0].fields[0].value:
            case [NameParts_d() as a, NameParts_d() as b]:
                assert(a.last == ["Bill"])
                assert(b.last == ["Bob"])
            case x:
                 assert(False), x

    @pytest.mark.skip
    def test_todo(self):
        pass

#!/usr/bin/env python3
"""

"""
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

import bibble._interface as API
from bibtexparser import model
import bibble.model as bmodel

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

class TestBibbleMetaBlock:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match bmodel.MetaBlock():
            case bmodel.MetaBlock():
                assert(True)
            case x:
                 assert(False), x


    def test_visit(self):
        obj = bmodel.MetaBlock()
        match obj.visit():
            case []:
                assert(True)
            case x:
                 assert(False), x


class TestFailureBlock:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match bmodel.FailedBlock(block=model.Entry("test", "blah", []), error=ValueError("test"), source="testing"):
            case bmodel.FailedBlock():
                assert(True)
            case x:
                assert(False), x


    def test_visit(self):
        obj = bmodel.FailedBlock(block=model.Entry("test", "blah", []), error=ValueError("test"), source="testing")
        match obj.report(i=0, total=0):
            case [str()]:
                assert(True)
            case x:
                 assert(False), x


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

import bibble._interface as API
from .. import PairStack

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

class TestPairStack:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match PairStack():
            case API.PairStack_p():
                assert(True)
            case x:
                 assert(False), x

    def test_addition_handles_none(self, mocker):
        pair = PairStack()
        pair.add(None, None, read=[None, None], write=[None, None])
        assert(len(pair.read_stack()) == 0)
        assert(len(pair.write_stack()) == 0)

    def test_addition_errors_on_non_middlewares(self, mocker):
        pair = PairStack()
        with pytest.raises(TypeError):
            pair.add(2)

    def test_addition_errors_on_non_middlewares_read(self, mocker):
        pair = PairStack()
        with pytest.raises(TypeError):
            pair.add(read=[False])

    def test_addition_errors_on_non_middlewares_write(self, mocker):
        pair = PairStack()
        with pytest.raises(TypeError):
            pair.add(write="blah")

    def test_addition_read(self, mocker):
        pair = PairStack()
        mock_mw = mocker.Mock(API.Middleware_p)
        pair.add(read=[mock_mw])
        assert(len(pair.read_stack()) == 1)
        assert(len(pair.write_stack()) == 0)

    def test_addition_write(self, mocker):
        pair = PairStack()
        mock_mw = mocker.Mock(API.Middleware_p)
        pair.add(write=[mock_mw])
        assert(len(pair.write_stack()) == 1)
        assert(len(pair.read_stack()) == 0)

    def test_addition_bidirectional(self, mocker):
        pair = PairStack()
        mock_mw = mocker.Mock(API.BidirectionalMiddleware_p)
        pair.add(mock_mw)
        assert(len(pair.write_stack()) == 1)
        assert(len(pair.read_stack()) == 1)

    def test_symmetric_stacks(self, mocker):
        pair      = PairStack()
        bidi1     = mocker.Mock(API.BidirectionalMiddleware_p)
        bidi2     = mocker.Mock(API.BidirectionalMiddleware_p)
        mw1       = mocker.Mock(API.Middleware_p)
        mw2       = mocker.Mock(API.Middleware_p)
        pair.add(bidi1, read=[mw1], write=[mw2]).add(bidi2)
        assert(len(pair.read_stack()) == 3)
        assert(len(pair.write_stack()) == 3)
        assert(pair.read_stack() == [bidi1, mw1, bidi2])
        assert(pair.write_stack() == [bidi2, mw2, bidi1])

    ##--|

    @pytest.mark.skip
    def test_todo(self):
        pass

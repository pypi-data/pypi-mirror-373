#!/usr/bin/env python3
"""


"""
# Imports:
from __future__ import annotations

# ##-- stdlib imports
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
import types
import collections
import contextlib
import hashlib
from copy import deepcopy
from uuid import UUID, uuid1
from weakref import ref
import atexit # for @atexit.register
import faulthandler
# ##-- end stdlib imports

from bibble.util.middlecore import IdenLibraryMiddleware
from bibble.model import MetaBlock

# ##-- types
# isort: off
import abc
import collections.abc
from typing import TYPE_CHECKING, cast, assert_type, assert_never
from typing import Generic, NewType, Never
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
    from typing import Self, Literal
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

class DataInsertMW(IdenLibraryMiddleware):
    """
    Inserts kwargs data into the metablock
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self._data = dict(kwargs)

    def update(self, data:dict) -> None:
        self._data.update(data)

    def transform(self, library):
        match MetaBlock.find_in(library):
            case None:
                block = MetaBlock(**self._data)
                library.add(block)
            case block:
                block.data.update(self._data)

        return library

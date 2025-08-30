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

from jgdv import Proto, Mixin
from bibtexparser import model, Library
import bibble._interface as API
from bibble.util.middlecore import IdenBlockMiddleware

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

    type Field = model.Field
    type Entry = model.Entry
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

# Vars:

# Body:

@Proto(API.Middleware_p)
class EntrySorter(IdenBlockMiddleware):
    """ Reorder the entries in a library according to a sort key
    Key defaults to sort by the entry key

    eg: sort by year, or type, or author
    ie: EntrySorterMiddleware(key=lambda x: x.fields_dict['year'].value)
    """

    def __init__(self, *args, key:Maybe[Callable]=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        match key:
            case x if callable(x):
                self._key_fn = key
            case _:
                self._key_fn = lambda x: x.key


    def transform(self, library:Library) -> Library:
        l2 = super().transform(library)
        # Sort entries
        entries = sorted(library.entries, key=self._key_fn)
        l2.remove(entries)
        l2.add(entries)
        # Insert
        return l2

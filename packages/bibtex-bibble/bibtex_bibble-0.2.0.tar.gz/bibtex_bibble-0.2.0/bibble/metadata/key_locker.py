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
import weakref
from copy import deepcopy
from uuid import UUID, uuid1

# ##-- end stdlib imports

# ##-- 3rd party imports
import bibtexparser
import bibtexparser.model as model
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)
from jgdv import Mixin, Proto

# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from . import _interface as MAPI
from bibble.util.middlecore import IdenBlockMiddleware
from bibble.util.mixins import ErrorRaiser_m
# ##-- end 1st party imports

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
    from jgdv import Maybe, Rx, RxStr
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
##--|

@Proto(API.ReadTime_p)
@Mixin(ErrorRaiser_m)
class KeyLocker(IdenBlockMiddleware):
    """ Ensure key/crossref consistency by:
    removing unwanted chars in the key,
    'locking' the key with a specific suffix (by default a '_').

    Also formats crossref values so they match.
    Already locked keys are ignored.

    __init__ takes:
    - regex = the regex of chars to remove.
    - sub   = the substitute for removed chars
    """

    def __init__(self, *, regex:Maybe[RxStr|Rx]=None, sub:Maybe[str]=None, lock_suffix:Maybe[str]=None, key_suffix:Maybe[RxStr|Rx]=None, **kwargs):
        super().__init__(**kwargs)
        self._remove_re         : Rx         = re.compile(regex or MAPI.KEY_CLEAN_RE)
        self._key_suffix_re     : Rx         = re.compile(key_suffix or MAPI.KEY_SUFFIX_RE)
        self._sub               : str        = sub or MAPI.KEY_SUB_CHAR
        self._lock_suffix       : str        = MAPI.LOCK_SUFFIX
        self._bad_lock          : str        = f"{self._lock_suffix}{self._lock_suffix}"

    def on_read(self):
        Never()

    def transform_Entry(self, entry, library) -> list:
        entry = deepcopy(entry)
        entry.key = self.clean_key(entry.key)
        match entry.get(MAPI.CROSSREF_K):
            case None:
                pass
            case model.Field(value=value):
                entry.set_field(model.Field(MAPI.CROSSREF_K, self.clean_key(value)))

        return [entry]

    def clean_key(self, key:str) -> str:
        """ Convert the entry key to a canonical form """
        if key.endswith(self._lock_suffix) and not key.endswith(self._bad_lock):
            return key

        # Remove bad chars
        clean_key = self._remove_re.sub(self._sub, key)
        # Enforce the correct suffix
        clean_key = self._key_suffix_re.sub(self._lock_suffix, clean_key)
        return clean_key

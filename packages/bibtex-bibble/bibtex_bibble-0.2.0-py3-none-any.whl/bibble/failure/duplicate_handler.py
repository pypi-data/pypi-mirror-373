#!/usr/bin/env python3
"""

See EOF for license/metadata/notes as applicable
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
from uuid import UUID, uuid1

# ##-- end stdlib imports

# ##-- 3rd party imports
from jgdv import Proto, Mixin
import bibtexparser
import bibtexparser.model as model
from bibtexparser.library import Library
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware, LibraryMiddleware)

# ##-- end 3rd party imports

import bibble._interface as API
from . import _interface as MAPI
from bibble.util.middlecore import IdenLibraryMiddleware

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

##--|

class DuplicateFinder(IdenLibraryMiddleware):

    def transform(self, library:Library) -> Library:
        keys = set()
        for entry in library.entries:
            if entry.key in keys:
                # duplicate
                pass
            else:
                keys.add(entry.key)
        else:
            return library


class DuplicateKeyHandler(IdenLibraryMiddleware):
    """ take duplicate entries and edit their key to be unique """

    def transform(self, library:Library):
        if not bool(library.failed_blocks):
            return library

        key_count, field_count = 0, 0
        self.logger().info("Handling %s failed blocks", len(library.failed_blocks))
        for failed in library.failed_blocks:
            match failed:
                case model.DuplicateBlockKeyBlock():
                    self._dedup_key(failed, library)
                    key_count   += 1
                case model.DuplicateFieldKeyBlock():
                    self._dedup_fields(failed, library)
                    field_count += 1
                case _:
                    self.logger().info("Skipping block: %s", failed)
                    pass
        else:
            self.logger().info("Adjusted %s duplicate keys ", key_count)
            self.logger().info("Adjusted %s duplicate fields ", field_count)
            return library

    def _dedup_key(self, failed, library) -> None:
        uuid          = uuid1().hex
        duplicate     = failed.ignore_error_block
        original      = duplicate.key
        duplicate.key = f"{duplicate.key}_dup_{uuid}"
        library.add(duplicate)
        library.remove(failed)
        self.logger().warning("Duplicate Key found: %s -> %s", original, duplicate.key)

    def _dedup_fields(self, failed, library) -> None:
        entry       = failed.ignore_error_block
        found       = set()
        duplicates  = set()
        for field in entry.fields:
            if field.key not in found:
                found.add(field.key)
                continue

            duplicates.add(field.key)
            count = 2

            while (curr:=f"{field.key}_{count}") in found:
                duplicates.add(field.key)
                count += 1
                if 100 < count:
                    raise ValueError("Deduplicating fields is stuck")
            else:
                field.key = curr
                found.add(curr)
        else:
            self.logger().warning("Duplicate Fields (%s): %s",
                                  entry.key,
                                  duplicates)
            library.add(entry)
            library.remove(failed)

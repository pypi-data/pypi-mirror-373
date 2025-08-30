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
ISBN_STRIP_RE                      = re.compile(r"[\s-]")
ISBN_K         : Final[str]        = "isbn"
INVALID_ISBN_K : Final[str]        = "invalid_isbn"

KEY_CLEAN_RE   : Final[re.Pattern] = re.compile(r"[/:{}]+")
KEY_SUFFIX_RE  : Final[re.Pattern] = re.compile(r"_*$")
KEY_SUB_CHAR   : Final[str]        = "_"
LOCK_SUFFIX    : Final[str]        = "_"

CROSSREF_K     : Final[str]        = "crossref"

FILE_K         : Final[str]        = "file"
ORPHANED_K     : Final[str]        = "orphaned"
PDF_LOCKED_K   : Final[str]        = "pdf_locked"

BIBTEX_EXIF    : Final[str]        = "Bibtex"
DESC_EXIF      : Final[str]        = "Description"

QPDF_CHECK     : Final[str]        = "--check"
QPDF_LINEAR    : Final[str]        = "--linearize"
QPDF_IS_ENCRPT : Final[str]        = "--is-encrypted"
QPDF_REQ_PASS  : Final[str]        = "--requires-password"
QPDF_OK_CODES  : Final[tuple]      = (2,)

EPUB_SUFF      : Final[str]        = ".epub"
PDF_SUFF       : Final[str]        = ".pdf"
PDF_COPY_SUFF  : Final[str]        = "_copy"
PDF_ORIG_SUFF  : Final[str]        = ".pdf_original"

TAGS_K         : Final[str]        = "tags"
KEYWORDS_K     : Final[str]        = "keywords"

# Body:

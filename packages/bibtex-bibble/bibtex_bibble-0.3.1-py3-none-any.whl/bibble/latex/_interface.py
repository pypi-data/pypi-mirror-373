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

from pylatexenc.latex2text import (LatexNodes2Text, MacroTextSpec,
                                   get_default_latex_context_db)

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
DEFAULT_RULES_K : Final[str] = "defaults"
KEEP_BRACED_K   : Final[str] = "keep_braced_groups"
MATH_MODE_K     : Final[str] = "math_mode"

##--| Encoding Rules:
## Turned into conversion rules using UnicodeHelper_m.builde_encode_rule
ENCODING_RULES : Final[list[tuple]] =[
    (r"ẹ", r'\\{d}'),
    (r"é", r"\\'{e}"),

    (r"ǒ", r'\\v{o}'),
    (r"ọ", r'\\d{o}'),

    (r"ǔ", r'\\v{u}'),
    (r"ụ", r'\\d{u}'),

    (r"Ẇ", r'\\.{W}'),

    (r"ș", r'\\,{s}'),
    (r"Ș", r'\\,{S}'),
]
URL_RULES : Final[list[tuple]] = [
    (r"(https?://\S*\.\S*)", r"\\url{\1}"),
    (r"(www.\S*\.\S*)",      r"\\url{\1}"),
]
MATH_RULES : Final[list[tuple]] = [
    (r"(?<!\\)(\$.*[^\\]\$)", r"\1"),
]

##--| Decoding rules
## Turned into macrotextspecs using UnicodeHelper_m.build_decode_rule
URL_SIMPL : Final[tuple[str, str]] = ("url", "%s")

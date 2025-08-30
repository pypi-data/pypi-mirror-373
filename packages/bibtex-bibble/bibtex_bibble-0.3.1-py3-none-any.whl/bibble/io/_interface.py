#!/usr/bin/env python3
"""

"""
# Imports:
from __future__ import annotations

from bibtexparser.writer import BibtexFormat

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

# Vars:
VAL_SEP      : Final[str] = " = "
FAIL_COMMENT : Final[str] = "% WARNING Processing failed for the following {n} lines.\n% Error: {err}.\n% Raw Original:"
FAIL_PARTIAL : Final[str] = "% Partially Processed Block:"
FAIL_END     : Final[str] = "% End of Error Report"

# Body:

def default_format() -> BibtexFormat:
    """ Build a default formatter """
    fmt                         = BibtexFormat()
    fmt.value_column            = 15
    fmt.indent                  = " "
    fmt.block_separator         = "\n"
    fmt.trailing_comma          = True
    fmt.parsing_failed_comment = FAIL_COMMENT
    return fmt

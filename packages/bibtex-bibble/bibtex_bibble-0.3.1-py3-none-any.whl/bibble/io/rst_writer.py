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
from uuid import UUID, uuid1

# ##-- end stdlib imports

from bibtexparser import model
from bibtexparser.library import Library
from bibble.io.writer import BibbleWriter

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

    type Block = model.Block
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

SPACE          : Final[str] = " "
INDENT_AMOUNT  : Final[int] = 3
##--|
class RstWriter(BibbleWriter):
    """ Write bibtex entries as Rst. """

    # These need to match the BibEntryDirective of the sphinx domain
    _label      : ClassVar[str]       = ".. _{}:"
    _entry      : ClassVar[str]       = ".. bibtex:entry:: {}"
    _entry_args : ClassVar[list[str]] = ["title","author", "editor", "year", "tags",
                                         "journal", "booktitle", "within",
                                         "platform", "publisher", "institution",
                                         "series", "url", "doi", "isbn", "edition",
                                         "crossref", "identifier",
                                         ]
    _indent     : ClassVar[str]       = SPACE*INDENT_AMOUNT

    def visit_entry(self, block:Block) -> list[str]:
        result = [
            self._entry.format(block.key), "\n",
            ]
        match block.entry_type:
            case "case" | "legal" | "judicial" | "law":
                result += self._build_legal_entry(block)
            case "standard" | "online" | "blog" | "dataset":
                result += self._build_online_entry(block)
            case "tweet" | "thread":
                result += self._build_social_media_entry(block)
            case _:
                result += self._build_simple_entry(block)

        # Debug info:
        # result += self._build_debug_info(block)
        return result

    def make_header(self, library:Library, title:Maybe[str]=None) -> list[str]:
        match title:
            case None:
                title = "A Bibtex File"
            case str():
                pass

        lines = [".. -*- mode: ReST -*-\n\n",
                 f".. _{title}:\n\n",
                 "="*len(title), "\n",
                 title, "\n",
                 "="*len(title), "\n\n",
                 ".. contents:: Entries:\n",
                 "   :class: bib_entries\n",
                 "   :local:\n\n",
                 # TODO mode this to a template:
                 # f"For the raw bibtex, see `the raw file <raw_{title}>`_.\n\n",
                 # f".. _`raw_{title}`: https://github.com/jgrey4296/bibliography/blob/main/main/{title}.bib\n\n",
                 ]
        return lines


    def _build_simple_entry(self, block:Block) -> list[str]:
        result = []
        result += self._title_add(block)
        result += self._must_add(block, "tags")
        result += self._can_add(block, "author", "editor", "year", "series")
        result += self._can_add(block, "journal", "booktitle", "doi", "url", "isbn", "publisher")
        result += self._can_add(block, "incollection", "institution", "crossref")
        # TODO volume, number, pages, chapter
        return result

    def _build_legal_entry(self, block:Block) -> list[str]:
        assert(block.entry_type in ["case", "legal","judicial", "law"])
        result = []
        result += self._can_add(block, "title", "short_parties")
        result += self._must_add(block, "tags")
        result += self._can_add(block, "author", "editor", "year", "series")
        result += self._can_add(block, "journal", "booktitle", "doi", "url", "isbn", "publisher")
        result += self._can_add(block, "incollection", "institution")
        # TODO volume, number, pages, chapter
        return result

    def _build_online_entry(self, block:Block) -> list[str]:
        assert(block.entry_type in ["standard", "online", "blog", "dataset"])
        result = []
        result += self._title_add(block)
        result += self._must_add(block, "tags")
        result += self._can_add(block, "author", "editor", "year", "series", "url")
        result += self._can_add(block, "journal", "booktitle", "doi", "isbn", "publisher")
        result += self._can_add(block, "incollection", "institution", "identifier")
        # TODO volume, number, pages, chapter
        return result

    def _build_social_media_entry(self, block:Block) -> list[str]:
        assert(block.entry_type in ["tweet","thread"])
        result = []
        result += self._title_add(block)
        result += self._must_add(block, "tags")
        result += self._can_add(block, "author", "editor", "year", "series")
        result += self._can_add(block, "journal", "booktitle", "doi", "url", "isbn", "publisher")
        result += self._can_add(block, "incollection", "institution")
        # TODO volume, number, pages, chapter
        return result


    def _build_debug_info(self, block:Block) -> list[str]:
        result = ["\n\n..\n",
                  f"{self._indent} Fields:\n",
                  "{} {}\n".format(self._indent, ", ".join(block.fields_dict.keys())),
                  f"{self._indent} Object Keys:\n",
                  "{} {}\n".format(self._indent,
                                   ", ".join([x for x in dir(block) if "__" not in x])),
                  "\n\n",
                  ]
        return result


    def _title_add(self, block:Block) -> list[str]:
        """ Format and return the title """
        match block.get('title', None), block.get("subtitle", None):
            case model.Field(value=str() as title), model.Field(value=str() as subtitle):
                return [f"{self._indent}:title: {title}: {subtitle}\n"] # type:ignore
            case model.Field(value=str() as title), _:
                return [f"{self._indent}:title: {title}\n"] # type: ignore
                pass
            case _:
                raise KeyError("no title", block.key)

    def _must_add(self, block:Block, field:str) -> list[str]:
        match block.get(field, None):
            case model.Field(key=key, value=val):
                return [f"{self._indent}:{key}: {val}\n"] # type: ignore
            case _:
                raise KeyError('Entry missing required field', block.key, field)

    def _can_add(self, block:Block, *keys:str) -> list[str]:
        result = []
        for key in keys:
            match block.get(key, None):
                case None:
                    continue
                case model.Field(value=val):
                    result.append(f"{self._indent}:{key}: {val}\n") # type: ignore

        else:
            return result

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
import bibtexparser
import bibtexparser.model as model
from bibtexparser import middlewares as ms
from bibtexparser.middlewares.middleware import (BlockMiddleware,
                                                 LibraryMiddleware)
from jgdv import Mixin, Proto

# ##-- end 3rd party imports

# ##-- 1st party imports
import bibble._interface as API
from bibble.util.mixins import FieldMatcher_m
from bibble.util.middlecore import IdenBlockMiddleware
from bibble.util.name_parts import NameParts_d

# ##-- end 1st party imports

import pyparsing as pp
from . import _interface as API_N

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
    from jgdv import Maybe, Result
    from typing import Final
    from typing import ClassVar, Any, LiteralString
    from typing import Never, Self, Literal
    from typing import TypeGuard
    from collections.abc import Iterable, Iterator, Callable, Generator
    from collections.abc import Sequence, Mapping, MutableMapping, Hashable

    type Block = model.Block
    type Field = model.Field
    type Entry = model.Entry
    from bibtexparser.library import Library
    type Parser = pp.core.ParserElement
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

PARSE_STATE = API_N.NameSplitState_e
##--|

class _SplitAuthors_m:
    """ Adapated from bibtexparser's split_multiple_persons_names, originally by Blair Bonnett

    Splits names by intermediary 'and's.
    Like its original, treats non-breaking space and '~'s as regular chars not whitespace.

    'and's within braces are returned un modified.
    eg: '{Simon and Schuster}' -> ['{Simon and Schuster}']

    """

    def _build_split_parser(self) -> Parser:
        return pp.Literal("and")

    def _split_authors(self, val:str, *, strict=True) -> list[str]:
        return self._split_authors_fsm(val, strict=strict)

    def _split_authors_pp(self, val:str, *, strict=True) -> list[str]:
        """
        TODO
        """
        val = val.strip()
        if not bool(val):
            return []

        parser = self._build_split_parser()

        return []

    def _split_authors_fsm(self, val:str, *, strict=True) -> list[str]:
        val = val.strip()
        if not bool(val):
            return []

        # Processing variables.
        step         = PARSE_STATE.start_ws  # Current step.
        pos          = 0  # Current position in string.
        bracelevel   = 0  # Current bracelevel.
        spans        = [[0]]  # Spans of names within the string.
        possible_end = 0  # Possible end position of a name.
        whitespace   = API_N.NAME_WHITESPACE # Allowed whitespace characters.

        # Loop over the string.
        namesiter = iter(val)
        for char in namesiter:
            pos += 1
            match char:
                case "\\":
                    try:
                        next(namesiter)
                    except StopIteration:
                        # If we're at the end of the string, then the \ is just a \.
                        pass
                    pos += 1
                    continue
                case API_N.OBRACE:
                    # Change in brace level.
                    if step == API_N.NameSplitState_e.next_word:
                        spans[-1].append(possible_end)
                        spans.append([pos - 1])

                    bracelevel += 1
                    step = API_N.NameSplitState_e.start_ws
                    continue
                case API_N.CBRACE:
                    if bracelevel:
                        bracelevel -= 1

                    step = API_N.NameSplitState_e.start_ws
                    continue
                case _:
                    pass

            # Ignore everything inside a brace.
            if bracelevel:
                step = API_N.NameSplitState_e.start_ws
                continue

            match step:
                case API_N.NameSplitState_e.start_ws if char in whitespace:
                    # Looking for a whitespace character to start the ' and '. When we find
                    # one, mark it as the possible end of the previous word.
                    step = API_N.NameSplitState_e.find_a
                    possible_end = pos - 1
                case API_N.NameSplitState_e.find_a if char in ("a", "A"):
                    # Looking for the letter "a".
                    step = API_N.NameSplitState_e.find_n
                case API_N.NameSplitState_e.find_a if char not in whitespace:
                    # NB, we can have multiple whitespace characters so we need to handle that here.
                    step = API_N.NameSplitState_e.start_ws
                case API_N.NameSplitState_e.find_n if char in ("n", "N"):
                    # Looking for the letter n.
                    step = API_N.NameSplitState_e.find_d
                case API_N.NameSplitState_e.find_n if char in whitespace:
                    step = API_N.NameSplitState_e.find_a
                    possible_end = pos - 1
                case API_N.NameSplitState_e.find_n:
                    step = API_N.NameSplitState_e.start_ws
                case API_N.NameSplitState_e.find_d if char in ("d", "D"):
                    # Looking for the letter d.
                    step = API_N.NameSplitState_e.end_ws
                case API_N.NameSplitState_e.find_d if char in whitespace:
                    step = API_N.NameSplitState_e.find_a
                    possible_end = pos - 1
                case API_N.NameSplitState_e.find_d:
                    step = API_N.NameSplitState_e.start_ws
                case API_N.NameSplitState_e.end_ws if char in whitespace:
                    # And now the whitespace to end the ' and '.
                    step = API_N.NameSplitState_e.next_word
                case API_N.NameSplitState_e.end_ws:
                    step = API_N.NameSplitState_e.start_ws
                case API_N.NameSplitState_e.next_word if char not in whitespace:
                    # Again, we need to handle multiple whitespace characters. Keep going
                    # until we find the start of the next word.
                    # Finish the previous word span, start the next,
                    # and do it all again.
                    spans[-1].append(possible_end)
                    spans.append([pos - 1])
                    step = API_N.NameSplitState_e.start_ws

        # Finish the last word.

        spans[-1].append(None)

        # Extract and return the names.
        return [val[start:end] for start, end in spans]

class _NameToParts_m:
    """ Adapted from bibtexparser's parse_single_name_into_parts, originally by Blair Bonnett.

    Parses an individual name into a NameParts_d, a simple data structure containing:
    - first : list. First names.
    - von   : list.
    - last  : list. Last Names.
    - jr    : list.

    Bibtex Names are of one of the forms:
    - first von last
    - von last, first
    - von last, jr, first
    """

    def _build_parts_parser(self) -> Parser:
        return pp.Literal("and")

    def _name_to_parts(self, val:str, *, strict=True) -> NameParts_d:
        val = val.strip()
        if not bool(val):
            return NameParts_d()

        sections, cases = self._parse_name_fsm(val, strict=strict)
        # No non-whitespace input.
        if not sections or not any(bool(section) for section in sections):
            return NameParts_d()

        match sections:
            case [x]:
                parts = self._first_von_last(x, cases)
            case [*xs]:
                parts = self._von_last_first(xs, cases)

        return parts

    def _parse_name_pp(self, val, *, strict=True) -> tuple[list, list]:
        """ TODO """
        return [], []

    def _parse_name_fsm(self, val, *, strict=True) -> tuple[list, list]:
        # We'll iterate over the input once, dividing it into a list of words for
        # each comma-separated section. We'll also calculate the case of each word
        # as we work.
        sections    = [[]]   # Sections of the name.
        cases       = [[]]   # 1 = uppercase, 0 = lowercase, -1 = caseless.
        word        = []     # Current word.
        case        = -1     # Case of the current word.
        level       = 0      # Current brace level.
        bracestart  = False  # Will the next character be the first within a brace?
        controlseq  = True   # Are we currently processing a control sequence?
        specialchar = None   # Are we currently processing a special character?
        whitespace  = API_N.NAME_WHITESPACE

        # Using an iterator allows us to deal with escapes in a simple manner.
        nameiter = iter(val)
        for char in nameiter:
            # An escape.
            match char:
                case "\\":
                    try:
                        escaped = next(nameiter)
                        # BibTeX doesn't allow whitespace escaping. Copy the slash and fall
                        # through to the normal case to handle the whitespace.
                        if escaped in whitespace:
                            word.append(char)
                            char = escaped
                        else:
                            if bracestart:
                                # Is this the first character in a brace?
                                bracestart = False
                                controlseq = escaped.isalpha()
                                specialchar = True
                                # Can we use it to determine the case?
                            elif (case == -1) and escaped.isalpha():
                                if escaped.isupper():
                                    case = 1
                                else:
                                    case = 0

                            # Copy the escape to the current word and go to the next
                            # character in the input.
                            word.append(char)
                            word.append(escaped)
                            continue
                    except StopIteration:
                        # If we're at the end of the string, then the \ is just a \.
                        word.append(char)
                case API_N.OBRACE:
                    # Start of a braced expression.
                    level += 1
                    word.append(char)
                    bracestart = True
                    controlseq = False
                    specialchar = False
                    continue
                case API_N .CBRACE:
                    # All the below cases imply this (and don't test its previous value).
                    bracestart = False
                    # End of a braced expression.
                    # Check and reduce the level.
                    if level:
                        level -= 1
                    else:
                        if strict:
                            raise ValueError(name=val, reason="Unmatched closing brace")
                        word.insert(0, "{")

                    # Update the state, append the character, and move on.
                    controlseq = False
                    specialchar = False
                    word.append(char)
                    continue
                case _ if level:
                    # All the below cases imply this (and don't test its previous value).
                    bracestart = False
                    # Inside a braced expression.
                    # Is this the end of a control sequence?
                    if controlseq:
                        if not char.isalpha():
                            controlseq = False
                    # If it's a special character, can we use it for a case?
                    elif specialchar:
                        if (case == -1) and char.isalpha():
                            if char.isupper():
                                case = 1
                            else:
                                case = 0

                    # Append the character and move on.
                    word.append(char)
                    continue

            # End of a word.
            # NB. we know we're not in a brace here due to the previous case.
                case x if x == "," or x in whitespace:
                    # All the below cases imply this (and don't test its previous value).
                    bracestart = False
                    # Don't add empty words due to repeated whitespace.
                    if word:
                        sections[-1].append("".join(word))
                        word = []
                        cases[-1].append(case)
                        case = -1
                        controlseq = False
                        specialchar = False

                    # End of a section.
                    if char == ",":
                        if len(sections) < 3:
                            sections.append([])
                            cases.append([])
                        elif strict:
                            raise ValueError(name=val, reason="Too many commas")
                    continue
            ##--|
            # Regular character.
            word.append(char)
            if (case == -1) and char.isalpha():
                if char.isupper():
                    case = 1
                else:
                    case = 0
        else:
            pass
        ##--|
        # Unterminated brace?
        if level:
            if strict:
                raise ValueError(name=val, reason="Unterminated opening brace")
            while level:
                word.append(API_N.CBRACE)
                level -= 1

        # Handle the final word.
        if word:
            sections[-1].append("".join(word))
            cases[-1].append(case)

        # Get rid of trailing sections.
        if not sections[-1]:
            # Trailing comma?
            if (len(sections) > 1) and strict:
                raise ValueError(name=val, reason="Trailing comma at end of name")
            sections.pop(-1)
            cases.pop(-1)

        return sections, cases

    def _first_von_last(self, p0, cases) -> NameParts_d:
        # Form 2: "First von Last"
        parts = NameParts_d()

        # One word only: last cannot be empty.
        if len(p0) == 1:
            parts.last = p0

        # Two words: must be first and last.
        elif len(p0) == 2:
            parts.first = p0[:1]
            parts.last = p0[1:]

        # Need to use the cases to figure it out.
        else:
            cases = cases[0]

            # - First is the longest sequence of words starting with uppercase
            # that is not the whole string.
            # - von is then the longest sequence # whose last word starts with
            # lowercase that is not the whole # string.
            # - Last is the rest.
            # NB., this means last cannot be empty.

            # At least one lowercase letter.
            if 0 in cases:
                # Index from end of list of first and last lowercase word.
                firstl = cases.index(0) - len(cases)
                lastl = -cases[::-1].index(0) - 1
                if lastl == -1:
                    lastl -= 1  # Cannot consume the rest of the string.

                # Pull the parts out.
                parts.first = p0[:firstl]
                parts.von = p0[firstl : lastl + 1]
                parts.last = p0[lastl + 1 :]

            # No lowercase: last is the last word, first is everything else.
            else:
                parts.first = p0[:-1]
                parts.last = p0[-1:]
        ##--|
        return parts

    def _von_last_first(self, sections, cases) -> NameParts_d:
        # Form 2 ("von Last, First") or 3 ("von Last, jr, First")
        # As long as there is content in the first name partition, use it as-is.
        parts = NameParts_d()
        first = sections[-1]
        if first and first[0]:
            parts.first = first

        # And again with the jr part.
        if len(sections) == 3:
            jr = sections[-2]
            if jr and jr[0]:
                parts.jr = jr

        # Last name cannot be empty; if there is only one word in the first
        # partition, we have to use it for the last name.
        last = sections[0]
        if len(last) == 1:
            parts.last = last
            return parts

        # Have to look at the cases to figure it out.
        lcases = cases[0]

        def rindex(k, x, default):
            """Returns the index of the rightmost occurrence of x in k."""
            for i in range(len(k) - 1, -1, -1):
                if k[i] == x:
                    return i
            return default

        # Check if at least one of the words is lowercase
        if 0 in lcases:
            # Excluding the last word, find the index of the last lower word
            split = rindex(lcases[:-1], 0, -1) + 1
            parts.von = sections[0][:split]
            parts.last = sections[0][split:]

        # All uppercase => all last.
        else:
            parts.last = sections[0]

        ##--|
        return parts

##--|

@Proto(API.ReadTime_p)
@Mixin(FieldMatcher_m, _SplitAuthors_m, _NameToParts_m)
class NameReader(IdenBlockMiddleware):
    """ A Refactored version of bibtexparser's SplitNameParts and SeparateCoAuthors
    """
    _whitelist = ("author", "editor", "translator")

    def __init__(self, *, parts:bool=True, authors:bool=True,  **kwargs):
        super().__init__(**kwargs)
        self._do_split_authors = authors
        self._do_name_parts = parts
        self.set_field_matchers(white=self._whitelist, black=[])
        if self._do_name_parts and not self._do_split_authors:
            raise ValueError("Can't generate name parts if you don't split authors")

    def on_read(self):
        Never()

    def transform_Entry(self, entry:Entry, library:Library) -> list[Entry]:
        match self.match_on_fields(entry, library):
            case model.Entry() as x:
                return [x]
            case Exception() as err:
                return [self.make_error_block(entry, err)]
            case x:
                raise TypeError(type(x))

    def field_h(self, field:Field, entry:Entry) -> Result[list[Field], Exception]:
        result = []
        match self._do_split_authors:
            case True:
                authors = self._split_authors(field.value)
            case False:
                authors = field.value
            case x:
                raise TypeError(type(x))

        match authors:
            case str():
                pass
            case [*xs] if self._do_name_parts:
                parts = [self._name_to_parts(x) for x in xs]
                result.append(model.Field(field.key, parts))
            case [*xs]:
                result.append(model.Field(field.key, list(xs)))
            case x:
                raise TypeError(type(x))

        return result

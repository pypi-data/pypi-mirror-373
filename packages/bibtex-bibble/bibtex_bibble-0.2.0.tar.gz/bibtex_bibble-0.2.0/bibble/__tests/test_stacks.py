#!/usr/bin/env python3
"""

"""
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

from importlib.resources import files
import bibtexparser as BTP
from bibtexparser import Library
from bibtexparser import middlewares as ms
from bibble.util import PairStack

try:
    import bibble as BM
    if not hasattr(BM.metadata, "ApplyMetaData"):
        raise ImportError()
except (ImportError, ImportWarning):
    pytest.skip("Skipping Metadata Writing Tests as an external tool is missing",
                allow_module_level=True)



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

##-- data
data_path : pl.Path = files(__package__) / "_data"
##-- end data

# Vars:
sort_firsts = ["title", "author", "editor", "year", "tags", "booktitle", "journal", "volume", "number", "edition", "edition_year", "publisher"]
sort_lasts  = ["isbn", "doi", "url", "file", "crossref"]
sub_fields  = ["publisher", "journal", "series", "institution"]
meta_keys   = {"all", "apply", "latex", "rst", "subs", "check", "fsort", "esort", "count",}
# Body:

def build_new_stack(_libroot:pl.Path, *, _namesubs:Maybe=None, _tagsubs:Maybe=None, _othersubs:Maybe=None, **kwargs) -> PairStack:
    """ Build a new PairStack of middlewares, with optional and required elements
    Because of how pairstack works, to see the parse stack, read from top to bottom.
    To see the write transforms, read from bottom to top.
    """
    _meta = set(x for x,y in kwargs.items() if y is True)
    if bool((extra:=_meta - meta_keys)):
        msg = "Unrecognised meta keys provided"
        raise ValueError(msg, extra)

    ALL   = "all" in _meta
    APPLY = ALL or "apply" in _meta
    LATEX = ALL or "latex" in _meta
    FSORT = ALL or "fsort" in _meta
    ESORT = ALL or "esort" in _meta
    COUNT = ALL or "count" in _meta
    SUBS  = ALL or "subs" in _meta
    CHECK = ALL or "check" in _meta

    stack = PairStack()
    # Very first/last middlewares:
    #
    stack.add(read=[BM.failure.DuplicateKeyHandler(),
                    ],
              write=[
                  BM.failure.FailureHandler(),
                  BM.metadata.ApplyMetadata() if APPLY else None,
              ])
    # Add bidirectional transforms
    stack.add(BM.bidi.BraceWrapper(),
              BM.bidi.BidiLatex() if LATEX else None,
              BM.bidi.BidiPaths(lib_root=_libroot),
              BM.bidi.BidiNames(parts=True, authors=True),
              BM.bidi.BidiIsbn(),
              BM.bidi.BidiTags(),
              None,
              read=[
                  BM.metadata.KeyLocker(),
                  BM.fields.TitleSplitter()
              ],
              write=[
                  BM.fields.FieldSorter(first=sort_firsts, last=sort_lasts) if FSORT else None,
                  BM.metadata.EntrySorter() if ESORT else None,
              ])

    if COUNT:
        # Accumulate various fields
        stack.add(write=[
            BM.fields.FieldAccumulator(name="all-tags",     fields=["tags"]),
            BM.fields.FieldAccumulator(name="all-pubs",     fields=["publisher"]),
            BM.fields.FieldAccumulator(name="all-series",   fields=["series"]),
            BM.fields.FieldAccumulator(name="all-journals", fields=["journal"]),
            BM.fields.FieldAccumulator(name="all-people",   fields=["author", "editor"]),
        ])

    if SUBS:
        stack.add(write=[
            # NameSubs need to merge with BidiNames
            # BM.people.NameSubstitutor(_namesubs) if _namesubs is not None else None,
            BM.fields.FieldSubstitutor(fields=["tags"], subs=_tagsubs) if _tagsubs is not None else None,
            BM.fields.FieldSubstitutor(fields=sub_fields, subs=_othersubs, force_single_value=True) if _othersubs is not None else None,
        ])

    if CHECK:
        stack.add(write=[BM.metadata.FileCheck()])

    stack.add(read=[BM.failure.FailureHandler()])
    return stack

##--|

class TestFullStack:

    def test_sanity(self):
        assert(True is not False)

    def test_simple_stack(self):
        match build_new_stack(pl.Path.cwd()):
            case PairStack():
                assert(True)
            case x:
                 assert(False), x

    def test_bad_meta_val(self):
        with pytest.raises(ValueError):
            build_new_stack(pl.Path.cwd(), unknown=True)

    def test_apply_kw(self):
        without_stack = build_new_stack(pl.Path.cwd(), apply=False)
        with_stack    = build_new_stack(pl.Path.cwd(), apply=True)

        assert(BM.metadata.ApplyMetadata not in without_stack)
        assert(BM.metadata.ApplyMetadata in with_stack)


    def test_full_reader(self):
        stack = build_new_stack(pl.Path.cwd(), all=True)
        reader = BM.io.Reader(stack)
        assert(True)

    def test_full_writer(self):
        stack = build_new_stack(pl.Path.cwd(), all=True)
        reader = BM.io.Reader(stack)
        assert(True)

    def test_read(self):
        stack = build_new_stack(pl.Path.cwd())
        reader = BM.io.Reader(stack)
        match reader.read(data_path / "1320_orig.bib"):
            case Library() as lib:
                assert(bool(lib.entries))
                assert(not bool(lib.failed_blocks))
                assert(len(lib.entries) == 3)
                authors = {repr(x.fields_dict['author'].value) for x in lib.entries}
                assert(len(authors) == 1)
            case x:
                assert(False), x


    def test_write(self):
        stack       = build_new_stack(pl.Path.cwd())
        reader      = BM.io.Reader(stack)
        lib         = reader.read(data_path / "1320_orig.bib")
        cleaned     = (data_path / "1320_clean.bib").read_text().strip()
        writer      = BM.io.Writer(stack)
        match writer.write(lib):
            case str() as x:
                assert(bool(x))
                assert(x.strip() == cleaned)
            case x:
                assert(False), x


    def test_read_merge(self):
        stack        = build_new_stack(pl.Path.cwd())
        reader       = BM.io.Reader(stack)
        lib          = reader.read(data_path / "1320_orig.bib")
        starting_len = len(lib.entries)
        match reader.read(data_path / "1868.bib", into=lib):
            case Library() as lib2:
                assert(starting_len < len(lib2.entries))
                assert(lib2 is lib)
            case x:
                 assert(False), x


    def test_read_failure(self, caplog):
        """ reads a file with two entries with the same key """
        stack        = build_new_stack(pl.Path.cwd())
        reader       = BM.io.Reader(stack)
        match reader.read(data_path / "1320_duplicates.bib"):
            case Library():
                assert("Handling 1 failed blocks" in caplog.text)
                assert("Adjusted 1 duplicate keys" in caplog.text)
                assert(True)
            case x:
                assert(False), x

#!/usr/bin/env python3
"""

"""
# ruff: noqa: ANN201, ARG001, ANN001, ARG002, ANN202

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

import bibble._interface as API
from bibtexparser import model, Library
import sh

try:
    from .. import ApplyMetadata, FileCheck, _interface as MAPI
except (ImportError, ImportWarning):
    pytest.skip("Skipping Metadata Writing Tests as an external tool is missing",
                allow_module_level=True)


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

# Body:

class TestApplyMetadata:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133

    def test_ctor(self):
        match ApplyMetadata():
            case API.AdaptiveMiddleware_p():
                assert(True)
            case x:
                 assert(False), x

    def test_no_file_entry(self):
        entry = model.Entry("test", "test:blah", [])
        lib   = Library([entry])
        mid   = ApplyMetadata()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
            case x:
                 assert(False), x


    def test_orphaned_entry(self):
        field = model.Field("file", "does/not/exist.pdf")
        entry = model.Entry("test", "test:blah", [field])
        lib   = Library([entry])
        mid   = ApplyMetadata()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert(l2.entries[0].fields_dict.get(MAPI.ORPHANED_K, None) is not None)
            case x:
                 assert(False), x


    def test_noop_from_meta_match(self, mocker, tmpdir, caplog):
        logger = logmod.getLogger("test")
        caplog.set_level(logmod.INFO, logger.name)
        tmpfile = pl.Path(tmpdir) / "test.pdf"
        tmpfile.touch()
        assert(tmpfile.exists())
        field = model.Field("file", tmpfile)
        entry = model.Entry("test", "test:blah", [field])
        lib   = Library([entry])
        mid   = ApplyMetadata(logger=logger)
        mid.metadata_matches_entry = mocker.Mock(return_value=True)
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(not bool(lib.failed_blocks))
                assert("No Metadata Update Necessary" in caplog.text)
            case x:
                 assert(False), x
                 


    def test_locked_entry(self, mocker, tmpdir):
        tmpfile = pl.Path(tmpdir) / "test.pdf"
        tmpfile.touch()
        assert(tmpfile.exists())
        field                      = model.Field("file", tmpfile)
        entry                      = model.Entry("test", "test:blah", [field])
        lib                        = Library([entry])
        mid                        = ApplyMetadata()
        mid.pdf_is_modifiable      = mocker.Mock(return_value=False)
        mid.metadata_matches_entry = mocker.Mock(return_value=False)
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(bool(l2.failed_blocks))
                assert(l2.entries[0].fields_dict.get(MAPI.PDF_LOCKED_K, None) is not None)
            case x:
                assert(False), x

    @pytest.mark.skip
    def test_todo(self):
        """
        Still to test:
        - modifiable failure
        - original metadata backup
        - epub update
        - pdf update
        - pdf validation
        - pdf finalization
        - get_file and get_files
        """
        pass

class TestFileCheck:

    def test_sanity(self):
        assert(True is not False) # noqa: PLR0133


    def test_ctor(self):
        match FileCheck():
            case API.AdaptiveMiddleware_p():
                assert(True)
            case x:
                assert(False), x

    def test_orphan_check(self, mocker, tmpdir):
        tmpfile = pl.Path(tmpdir) / "test.pdf"
        tmpfile.touch()
        assert(tmpfile.exists())
        field = model.Field("file", tmpfile)
        entry = model.Entry("test", "test:blah", [field])
        lib   = Library([entry])
        mid   = FileCheck()
        mid.pdf_is_modifiable = mocker.Mock(return_value=True)
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(MAPI.ORPHANED_K not in l2.entries[0].fields_dict)
                assert(not bool(lib.failed_blocks))
            case x:
                 assert(False), x


    def test_orphan_check_fail(self, tmpdir):
        tmpfile = pl.Path(tmpdir) / "test.pdf"
        assert(not tmpfile.exists())
        field = model.Field("file", tmpfile)
        entry = model.Entry("test", "test:blah", [field])
        lib   = Library([entry])
        mid   = FileCheck()
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(MAPI.ORPHANED_K in l2.entries[0].fields_dict)
                assert(not bool(lib.failed_blocks))
            case x:
                 assert(False), x


    def test_lock_check_fail(self, mocker, tmpdir):
        tmpfile = pl.Path(tmpdir) / "test.pdf"
        tmpfile.touch()
        assert(tmpfile.exists())
        field = model.Field("file", tmpfile)
        entry = model.Entry("test", "test:blah", [field])
        lib   = Library([entry])
        mid   = FileCheck()
        mid.pdf_is_modifiable = mocker.Mock(return_value=False)
        match mid.transform(lib):
            case Library() as l2:
                assert(l2 is lib)
                assert(MAPI.PDF_LOCKED_K in lib.entries[0].fields_dict)
                assert(not bool(lib.failed_blocks))
            case x:
                 assert(False), x


    @pytest.mark.skip
    def test_todo(self):
        """
        still to test:
        - epub existence
        """
        pass

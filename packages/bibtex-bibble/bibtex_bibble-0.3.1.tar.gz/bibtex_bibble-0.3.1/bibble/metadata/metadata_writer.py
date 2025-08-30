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
import json
import logging as logmod
import pathlib as pl
import re
import time
import types
import weakref
from uuid import UUID, uuid1

# ##-- end stdlib imports

# ##-- 3rd party imports
import bibtexparser as BTP
import jsonlines
import sh
from bibtexparser import model
from bibtexparser.middlewares import NameParts

from jgdv import Proto, Mixin

# ##-- end 3rd party imports

import bibble._interface as API
from . import _interface as MAPI
from bibble.util.middlecore import IdenBlockMiddleware
from bibble.util.mixins import ErrorRaiser_m
from bibble.util.name_parts import NameParts_d

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

    type Field  = model.Field
    type Entry  = model.Entry
##--|

# isort: on
# ##-- end types

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

try:
    exiftool = sh.exiftool
    calibre  = sh.ebook_meta
    qpdf     = sh.qpdf
    pdfinfo  = sh.pdfinfo
except sh.CommandNotFound:
    raise ImportError("Metadata writing disabled due to missing external tools")
##--|

class _EntryFileGetter_m:
    """ Mixin for getting the paths of files in the entry
    can return a list of all file_{N} field values
    """

    def _get_files(self, entry:Entry) -> list[pl.Path]:
        """ gets all paths of fields with 'file' in the field name """
        paths : list[pl.Path] = []
        for field in entry.fields:
            match field.value:
                case _ if MAPI.FILE_K not in field.key:
                    continue
                case None:
                    continue
                case pl.Path() as path:
                    paths.append(path)
                case str() as pathstr:
                    paths.append(pl.Path(pathstr))
                case x:
                    raise TypeError(type(x))
        else:
            return paths

    def _get_file(self, entry:Entry) -> Maybe[pl.Path]:
        """ Gets the main file fields path of an entry """
        path : pl.Path
        pathstr : str
        match entry.fields_dict.get(MAPI.FILE_K, None):
            case BTP.model.Field(value=pl.Path() as path):
                return path
            case BTP.model.Field(value=str() as pathstr):
                return pl.Path(pathstr)
            case _:
                return None

class _Metadata_Check_m:
    """A mixin for checking the metadata fof files"""

    def backup_original_metadata(self, path:pl.Path) -> None:
        """
        If self._backup is set, backup the files metadata as jsonlines there
        Uses exiftool to export the metadata as json,
        which is then appended into the backup as a jsonlines file.
        """
        assert(hasattr(self, "_backup"))
        match self._backup:
            case pl.Path():
                pass
            case _:
                return

        try:
            result = json.loads(exiftool("-J", str(path)))[0]
        except sh.ErrorReturnCode:
            raise ValueError("Couldn't retrieve metadata as json", path) from None

        with jsonlines.open(self._backup, mode='a') as f:
            f.write(result)

    def metadata_matches_entry(self, path:pl.Path, entry:Entry) -> bool:
        """ Test the given path to see if the metadata matches.
        This is quite naive.
        From exiftool, it looks for either:
        - a 'Bibtex' field,
        - a 'Description' field,

        and compares that to the raw entry's text.

        TODO switch to use a stored hash instead
        """
        assert(hasattr(self, "_logger"))
        try:
            result = json.loads(exiftool("-J", str(path)))[0]
        except sh.ErrorReturnCode:
            self._logger.warning("Couldn't match metadata", path)
            return False

        bib_field_matches  = result.get(MAPI.BIBTEX_EXIF, None) == entry.raw
        desc_field_matches = result.get(MAPI.DESC_EXIF, None) == entry.raw

        return bib_field_matches or desc_field_matches

class _Pdf_Update_m:
    """A Mixin for pdf specific metadata manipulation"""

    def update_pdf_by_exiftool(self, path:pl.Path, entry:Entry) -> None:
        """
        exiftool -{tag}="{content}" {file}
        https://exiftool.org/
        """
        assert(hasattr(self, "_logger"))
        # Build args:
        args = self._entry_to_exiftool_args(entry)

        self._logger.debug("Pdf update args: %s : %s", path, args)
        # Call
        try:
            exiftool(*args, str(path))
        except sh.ErrorReturnCode as err:
            raise ChildProcessError("Exiftool update failed", err) from None

    def pdf_is_modifiable(self, path:pl.Path) -> bool:
        """ Use qpdf to test the pdf for encryption or password locking,
        """
        try:
            cmd1 = qpdf(MAPI.QPDF_IS_ENCRPT, str(path), _ok_code=MAPI.QPDF_OK_CODES)
            cmd2 = qpdf(MAPI.QPDF_REQ_PASS, str(path), _ok_code=MAPI.QPDF_OK_CODES)
        except sh.ErrorReturnCode as err:
            return False

        return True

    def pdf_validate(self, path:pl.Path) -> None:
        """
        Validates a pdf using qpdf
        https://qpdf.readthedocs.io/en/stable/

        code 0 for fine,
        code 2 for errors
        code 3 for warnings
        writes to stderr for issues
        """
        try:
            qpdf(MAPI.QPDF_CHECK, str(path))
        except sh.ErrorReturnCode:
            raise ChildProcessError("PDF Failed Validation") from None

    def pdf_finalize(self, path:pl.Path) -> None:
        """ run qpdf --linearize,

        on success, delete the original if it exists
        """
        assert(hasattr(self, "_logger"))
        assert(path.suffix == MAPI.PDF_SUFF)
        self._logger.debug("Finalizing Pdf: %s", path)
        original  : pl.Path = pl.Path(path)
        copied    : pl.Path = path.with_stem(path.stem + MAPI.PDF_COPY_SUFF)
        backup    : pl.Path = path.with_suffix(MAPI.PDF_ORIG_SUFF)
        if copied.exists():
            raise FileExistsError("The temp copy for linearization shouldn't already exist", original)

        path.rename(copied)
        try:
            qpdf(str(copied), MAPI.QPDF_LINEAR, original)
        except sh.ErrorReturnCode:
            copied.rename(original)
            raise ChildProcessError("Linearization Failed") from None
        else:
            if backup.exists():
                backup.unlink()
            if original.exists() and copied.exists() and original != copied:
                copied.unlink()

    def _entry_to_exiftool_args(self, entry:Entry) -> list[str]:
        """
        Extract and format the entry as exiftool args
        Uses XMP for the metadata under a custom XMP-bib namespace
        # TODO add exiftool config to bibble
        """
        fields = entry.fields_dict
        args   = []

        # XMP-bib:
        # The custom full bibtex entry
        args += [f'-bibtex={entry.raw}']

        # General
        match fields:
            case {"title": t, "subtitle": st}:
                args += ['-title={}: {}'.format(t.value, st.value)]
            case {"title": t}:
                args += ['-title={}'.format(t.value)]
            case {"short_parties": t}:
                args += ['-title={}'.format(t.value)]

        match fields:
            case {"author": a}:
                args += ['-author={}'.format(a.value)]
            case {"editor": a}:
                args += ['-author={}'.format(a.value)]

        args += ['-Year={}'.format(fields['year'].value)]

        if 'tags' in fields:
            args += ['-Keywords={}'.format(",".join(fields['tags'].value))]
        if 'isbn' in fields:
            args += ['-ISBN={}'.format(fields['isbn'].value)]
        if 'edition' in fields:
            args += ['-xmp-prism:edition={}'.format(fields['edition'].value)]
        if 'publisher' in fields:
            args += ["-publisher={}".format(fields['publisher'].value)]
        if 'url' in fields:
            args += ["-xmp-prism:link={}".format(fields['url'].value)]
        if 'doi' in fields:
            args += ['-xmp-prism:DOI={}'.format(fields['doi'].value)]
        if 'institution' in fields:
            args += ['-xmp-prism:organization={}'.format(fields['institution'].value)]
        if 'issn' in fields:
            args += ['-xmp-prism:issn={}'.format(fields['issn'].value)]

        return args

class _Epub_Update_m:
    """A Mixin for epub-specific metadata manipulation"""

    def update_epub_by_calibre(self, path:pl.Path, entry:Entry) -> None:
        """ Uses calibre to modify epub metadata
        https://manual.calibre-ebook.com/generated/en/cli-index.html
        """
        assert(hasattr(self, "_logger"))
        args = self.entry_to_calibre_args(entry)

        self._logger.debug("Ebook update args: %s : %s", path, args)
        try:
            calibre(str(path), *args)
        except sh.ErrorReturnCode:
            raise ChildProcessError("Calibre Update Failed") from None

    def entry_to_calibre_args(self, entry:Entry) -> list[str]:
        fields  : dict        = entry.fields_dict
        args    : list        = []

        match fields:
            case {"title":t, "subtitle":st}:
                args.append(f"--title={t.value}: {st.value}")
            case {"title":t}:
                args.append(f"--title={t.value}")
            case {"short_parties":t}:
                args.append(f"--title={t.value}")

        # authors should be joined into one string already
        match fields:
            case {"author":str() as auth}:
                args += ['--authors={}'.format(auth)]
            case {"editor":str() as ed}:
                args += ['--authors={}'.format(ed)]
            case {"author":list()|NameParts()|NameParts_d() as bad}:
                raise TypeError("Author Should have been reduced already", entry.key, bad)
            case {"editor":list()|NameParts()|NameParts_d() as bad}:
                raise TypeError("Editor Should have been reduced already", entry.key, bad)

        if 'publisher' in fields:
            args += ["--publisher={}".format(fields['publisher'].value)]
        if 'series' in fields:
            args += ["--series={}".format(fields['series'].value)]
        if 'number' in fields:
            args += ['--index={}'.format(fields['number'].value)]
        if 'volume' in fields:
            args += ['--index={}'.format(fields['volume'].value)]
        if 'isbn' in fields:
            args += ['--isbn={}'.format(fields['isbn'].value)]
        if 'doi' in fields:
            args += ['--identifier=doi:{}'.format(fields['doi'].value)]
        if 'tags' in fields:
            args += ['--tags={}'.format(",".join(fields['tags'].value))]
        if 'year' in fields:
            args += ['--date={}'.format(fields['year'].value)]

        args += ['--comments={}'.format(entry.raw)]

        return args

##--|

@Proto(API.WriteTime_p)
@Mixin(_Pdf_Update_m, _Epub_Update_m, _EntryFileGetter_m, _Metadata_Check_m, ErrorRaiser_m)
class ApplyMetadata(IdenBlockMiddleware):
    """ Apply metadata to files mentioned in bibtex entries
      uses xmp-prism tags and some custom ones for pdfs,
      and epub standard.

    TODO add a 'meta_update' status field to the entry for [locked,failed]
      """
    _backup   : Maybe[pl.path]
    _failures : list[Exception]

    def __init__(self, *, backup:Maybe[pl.Path]=None, **kwargs):
        super().__init__(**kwargs)
        self._extra.setdefault("tqdm", True)
        self._backup   = backup
        self._failures = []

    def on_write(self):
        Never()

    def transform_Entry(self, entry:Entry, library:API.Library_p) -> list[Entry]:
        result : list[Entry] = []
        match self._get_file(entry):
            case None:
                pass
            case pl.Path() as x if not x.exists():
                update = BTP.model.Field(MAPI.ORPHANED_K, True)
                entry.set_field(update)
                result.append(entry)
            case pl.Path() as x if self.metadata_matches_entry(x, entry):
                self._logger.info("No Metadata Update Necessary: %s", x)
            case pl.Path() as x if x.suffix == MAPI.PDF_SUFF:
                for field in self.process_pdf(x, entry):
                    entry.set_field(field)
                else:
                    result.append(entry)
            case pl.Path() as x if x.suffix == MAPI.EPUB_SUFF:
                for field in self.process_epub(x, entry):
                    entry.set_field(field)
                else:
                    result.append(entry)
            case x:
                self._failures.append(TypeError("Unknown File Type", entry.key, x))
                self._logger.warning("Found a file that wasn't an epub or pdf: %s", x)

        for x in self._failures:
            result.append(self.make_error_block(entry, x))
        else:
            self._failures = []
            return result

    def process_epub(self, epub:pl.Path, entry:Entry) -> list[Field]:
        try:
            self.backup_original_metadata(epub)
            self.update_epub_by_calibre(epub, entry)
        except (ValueError, ChildProcessError) as err:
            self._failures.append(ValueError("Epub meta update failed", epub, *err.args))
            self._logger.warning("Epub Update failed: %s : %s", epub, err)
            return []
        else:
            if not epub.exists():
                raise FileNotFoundError("File has gone missing", epub)
            return []

    def process_pdf(self, pdf:pl.Path, entry:Entry) -> list[Field]:
        if not self.pdf_is_modifiable(pdf):
            locked_field = BTP.model.Field(MAPI.PDF_LOCKED_K , True)
            self._failures.append(ValueError("Pdf is locked", pdf))
            return [locked_field]

        try:
            self.backup_original_metadata(pdf)
            self.update_pdf_by_exiftool(pdf, entry)
            self.pdf_validate(pdf)
            self.pdf_finalize(pdf)
        except (ValueError, ChildProcessError, FileExistsError) as err:
            self._failures.append(ValueError("Pdf Meta update failed", pdf, *err.args))
            self._logger.warning("Pdf Update Failed: %s : %s", pdf, err)
            return []
        else:
            if not pdf.exists():
                raise FileNotFoundError("File has gone missing", pdf)
            return []

##--|

@Mixin(_Pdf_Update_m, _EntryFileGetter_m)
class FileCheck(IdenBlockMiddleware):
    """ Like ApplyMetadata, but just checks for files that can't be modified or are missing,
    so they can be fixed.
    ie: its faster

      Annotate entries with 'pdf_locked' if the pdf can't be modified,
      "orphan_file" if the pdf or epub does not exist
    """

    def transform_Entry(self, entry:Entry, library:API.Library_p) -> list[Entry]:
        """
        TODO remove orphan/lock field if its no longer the case
        """
        match self._get_file(entry):
            case None:
                return []
            case pl.Path() as x if not x.exists():
                update = BTP.model.Field(MAPI.ORPHANED_K, True)
                entry.set_field(update)
            case pl.Path() as x if x.suffix == MAPI.PDF_SUFF and MAPI.PDF_LOCKED_K in entry.fields_dict:
                pass
            case pl.Path() as x if x.suffix == MAPI.PDF_SUFF and not self.pdf_is_modifiable(x):
                update = BTP.model.Field(MAPI.PDF_LOCKED_K, True)
                entry.set_field(update)
            case pl.Path() as x if x.suffix == MAPI.PDF_SUFF:
                update = BTP.model.Field(MAPI.PDF_LOCKED_K,  False)
                entry.set_field(update)
            case _:
                return []

        return [entry]

#!/usr/bin/env python3
"""
Bibble, a bibtexparser middleware library.
"""

from importlib import metadata

__version__ = metadata.version("bibtex-bibble")

from . import model
from bibble.library import BibbleLib
from bibble.util.pair_stack import PairStack
from bibble import metadata as metadata
from bibble import bidi
from bibble import files
from bibble import fields
from bibble import latex
from bibble import people
from bibble import failure
from bibble import util
from bibble import io

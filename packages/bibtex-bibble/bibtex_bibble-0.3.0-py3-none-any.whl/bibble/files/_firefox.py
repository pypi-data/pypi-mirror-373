#!/usr/bin/env python3
"""

"""
# Imports:
from __future__ import annotations

# ##-- stdlib imports
import datetime
import base64
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

from selenium.webdriver import Firefox, FirefoxOptions, FirefoxService
from selenium.webdriver.common.print_page_options import PrintOptions
import bibble._interface as API
from . import _interface as FAPI
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

class FirefoxController:
    """ A Static controller for starting and closing firefox via selenium """

    @staticmethod
    def setup(*, opts:list, kwargs:dict) -> None:
        """ Setups a selenium driven, headless firefox to print to pdf

        """
        if hasattr(FirefoxController, FAPI.FF_DRIVER):
            logging.info("Skipping Firefox Setup")
            return getattr(FirefoxController, FAPI.FF_DRIVER)

        logging.info("Setting up headless Firefox")
        options = FirefoxOptions()
        for x in opts:
            options.add_argument(x)

        for x,y in kwargs.items():
            options.set_preference(x, y)

        # options.binary_location = "/usr/bin/firefox"
        # options.binary_location = "/snap/bin/geckodriver"
        service                  = FirefoxService(executable_path=FAPI.GECKO_DRIVER)
        driver                   = Firefox(options=options, service=service)
        driver.set_page_load_timeout(FAPI.LOAD_TIMEOUT)
        setattr(FirefoxController, FAPI.FF_DRIVER, driver)
        return driver

    @staticmethod
    def close() -> None:
        if not hasattr(FirefoxController, FAPI.FF_DRIVER):
            return

        logging.info("Closing Firefox")
        getattr(FirefoxController, FAPI.FF_DRIVER).quit()

    @staticmethod
    def save_pdf(url, dest) -> None:
        """ prints a url to a pdf file using selenium """
        if not isinstance(dest, pl.Path):
            raise FileNotFoundError("Destination to save pdf to is not a path", dest)

        if dest.suffix != ".pdf":
            raise FileNotFoundError("Destination isn't a pdf", dest)

        if dest.exists():
            logging.info("Destination already exists: %s", dest)
            return

        driver = FirefoxController.setup(opts=FAPI.SELENIUM_OPTS, kwargs=FAPI.SELENIUM_PREFS)
        logging.info("Saving: %s", url)
        print_ops = PrintOptions()
        print_ops.page_range = "all"

        driver.get(FAPI.READER_PREFIX + url)
        time.sleep(FAPI.LOAD_TIMEOUT)
        pdf       = driver.print_page(print_options=print_ops)
        pdf_bytes = base64.b64decode(pdf)

        if not bool(pdf_bytes):
            logging.warning("No Bytes were downloaded")
            return

        logging.info("Saving to: %s", dest)
        with dest.open("wb") as f:
            f.write(pdf_bytes)

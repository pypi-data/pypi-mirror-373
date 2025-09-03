###############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Utility functions used for testing.
"""
import logging
import os
import shutil
import tempfile
from os.path import exists, join, normpath

from ..Utils import TemporaryDir

__all__ = (
    "which",
    "MockFunc",
    "processFile",
    "processFileWithName",
    "MockLoggingHandler",
    "TemporaryDir",
    "TESTDATA_PATH",
)

TESTDATA_PATH = normpath(join(*([__file__] + [os.pardir] * 4 + ["testdata"])))


def which(cmd):
    """
    find a command in the path
    """
    try:
        return next(
            join(d, cmd)
            for d in os.environ["PATH"].split(os.pathsep)
            if exists(join(d, cmd))
        )
    except StopIteration:
        return None


class MockFunc:
    """
    Helper class to record the arguments a callback is called with.
    """

    def __init__(self):
        self.args = None
        self.kwargs = None
        self.__name__ = "mock"

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def processFile(data, function):
    """
    Process the string data via the function 'function' that accepts a filename
    as parameter.
    """
    fdesc, path = tempfile.mkstemp()
    f = os.fdopen(fdesc, "w")
    try:
        f.write(data)
        f.close()
        return function(path)
    finally:
        os.remove(path)


def processFileWithName(data, name, function):
    """
    Process the string data via the function 'function' that accepts a filename
    as parameter, using the given name for the file.
    """
    with TemporaryDir() as path:
        filepath = os.path.join(path, name)
        with open(filepath, "w") as f:
            f.write(data)
        return function(filepath)


# Code taken from http://stackoverflow.com/a/1049375/576333
class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs.
    To use it:
    >>> mlh = MockLoggingHandler()
    >>> logging.getLogger().addHandler(mlh)
    >>> logging.debug('hello')
    >>> mlh.messages['debug']  # doctest: +SKIP
    ['hello']
    """

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            "debug": [],
            "info": [],
            "warning": [],
            "error": [],
            "critical": [],
        }

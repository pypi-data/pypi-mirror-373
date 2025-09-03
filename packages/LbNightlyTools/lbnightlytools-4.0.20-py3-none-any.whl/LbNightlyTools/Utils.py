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
Common utility functions.
"""

import sys

__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

import codecs
import contextlib
import json
import logging
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

import gitlab
from LbPlatformUtils import requires
from LbPlatformUtils.architectures import ARCH_DEFS, get_supported_archs

DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def setDayNamesEnv(day=None):
    """
    Set the environment variables TODAY and YESTERDAY if not already set.

    @param day: weekday number for 'TODAY', if not specified, defaults to
                today.
    """
    if day is None:
        day = datetime.today().weekday()
    os.environ["TODAY"] = os.environ.get("TODAY", DAY_NAMES[day])
    # Note: it works for day == 0 too
    os.environ["YESTERDAY"] = os.environ.get("YESTERDAY", DAY_NAMES[day - 1])


def _timeoutTerminateCB(proc, msg):
    """
    Safely terminate a running Popen object.
    """
    if proc.poll() is None:
        try:
            logging.warning(msg)
            proc.terminate()
        except:  # pylint: disable=W0702
            pass


def timeout_call(*popenargs, **kwargs):
    """Reimplementation of subprocess.call with the addition of a timeout
    option.
    """
    from subprocess import Popen

    timer = None
    try:
        timeout = kwargs.pop("timeout")
        msg = kwargs.pop("timeoutmsg", "on command " + repr(popenargs))
        msg = f"Timeout reached {msg} ({timeout}s): terminated."
        from threading import Timer

        proc = Popen(*popenargs, **kwargs)
        timer = Timer(timeout, _timeoutTerminateCB, [proc, msg])
        timer.start()
        result = proc.wait()
        timer.cancel()
        return result
    except KeyError:
        return Popen(*popenargs, **kwargs).wait()
    finally:
        # ensure that we do not wait for the timer if there is an abnormal exit
        if timer:
            timer.cancel()


def tee_call(*args, **kwargs):
    """
    Wrapper for Popen to run a command and collect the output.

    The arguments are those of Popen, with the addition of
    @param verbose: if True, the output and error are printed while the process
                    is running.

    @return: tuple with return code, stdout and stderr

    Example:
    >>> result = tee_call(['echo hello'], shell=True, verbose=True)
    hello
    >>> result == (0, b'hello\\n', b'')
    True
    """
    import errno
    import select
    import sys
    from subprocess import PIPE, Popen

    verbose = kwargs.pop("verbose", False)
    if "stdout" not in kwargs:
        kwargs["stdout"] = PIPE
    if "stderr" not in kwargs:
        kwargs["stderr"] = PIPE

    proc = Popen(*args, **kwargs)

    if not verbose:
        out, err = proc.communicate()
        retcode = proc.returncode
    else:
        # code inspired (mostly copied) from subprocess module
        poller = select.poll()
        files = {
            proc.stdout.fileno(): (proc.stdout, sys.stdout),
            proc.stderr.fileno(): (proc.stderr, sys.stderr),
        }
        out = []
        err = []
        output = {proc.stdout.fileno(): out, proc.stderr.fileno(): err}

        select_POLLIN_POLLPRI = select.POLLIN | select.POLLPRI

        poller.register(proc.stdout, select_POLLIN_POLLPRI)
        poller.register(proc.stderr, select_POLLIN_POLLPRI)

        def close_unregister_and_remove(fd):
            poller.unregister(fd)
            files[fd][0].close()
            files.pop(fd)

        while files:
            try:
                ready = poller.poll()
            except OSError as e:
                if e.args[0] == errno.EINTR:
                    continue
                raise
            for fd, mode in ready:
                if mode & select_POLLIN_POLLPRI:
                    data = os.read(fd, 4096)
                    if not data:
                        close_unregister_and_remove(fd)
                    output[fd].append(data)
                    files[fd][1].write(data.decode("utf-8", errors="replace"))
                else:
                    # Ignore hang up or errors.
                    close_unregister_and_remove(fd)
        retcode = proc.wait()

    return retcode, b"".join(out), b"".join(err)


def log_call(*args, **kwargs):
    """
    Wrapper for Popen to run a command and collect the output.

    The arguments are those of Popen, with the addition of
    @param logger: a logging.Logger instance to be used to print messages
                  [default: default logger].
    @param log_level: level the output of the command should use
                      [default: logging.DEBUG]

    @return: dictionary with retcode, stdout and stderr

    Example:
    >>> import logging
    >>> import sys
    >>> logger = logging.getLogger('hi')
    >>> logger.addHandler(logging.StreamHandler(sys.stdout))
    >>> logger.setLevel(logging.INFO)
    >>> result = log_call(['echo hello'], shell=True, logger=logging.getLogger('hi'),
    ... log_level=logging.DEBUG)
    >>> result == {'retcode': 0, 'stdout': b'hello\\n', 'stderr': b''}
    True
    >>> result = log_call(['echo hello'], shell=True, logger=logging.getLogger('hi'),
    ... log_level=logging.INFO)  # doctest: +SKIP
    hello
    >>> result == {'retcode': 0, 'stdout': b'hello\\n', 'stderr': b''}
    True
    """
    import errno
    import select
    from subprocess import PIPE, Popen

    log = kwargs.pop("logger", logging).log
    log_level = kwargs.pop("log_level", logging.DEBUG)

    if "stdout" not in kwargs:
        kwargs["stdout"] = PIPE
    if "stderr" not in kwargs:
        kwargs["stderr"] = PIPE

    proc = Popen(*args, **kwargs)

    # code inspired (mostly copied) from subprocess module
    poller = select.poll()

    select_POLLIN_POLLPRI = select.POLLIN | select.POLLPRI
    out = []
    err = []

    files = {x.fileno(): x for x in (proc.stdout, proc.stderr) if x}
    output = {proc.stdout.fileno(): out}
    if proc.stderr:
        output[proc.stderr.fileno()] = err
    spilled_output = {x.fileno(): b"" for x in (proc.stdout, proc.stderr) if x}

    poller.register(proc.stdout, select_POLLIN_POLLPRI)
    if proc.stderr:
        poller.register(proc.stderr, select_POLLIN_POLLPRI)

    def close_unregister_and_remove(fd):
        poller.unregister(fd)
        files[fd].close()
        files.pop(fd)

    while files:
        try:
            ready = poller.poll()
        except OSError as e:
            if e.args[0] == errno.EINTR:
                continue
            raise
        for fd, mode in ready:
            if mode & select_POLLIN_POLLPRI:
                data = os.read(fd, 4096)
                if not data:
                    close_unregister_and_remove(fd)
                output[fd].append(data)
                data = spilled_output[fd] + data
                spilled_output[fd] = b""
                for line in data.splitlines(True):
                    if line.endswith(b"\n"):
                        log(log_level, line.decode("utf-8", errors="replace").rstrip())
                    else:
                        spilled_output[fd] += line
            else:
                # Ignore hang up or errors.
                close_unregister_and_remove(fd)
    retcode = proc.wait()

    return {"retcode": retcode, "stdout": b"".join(out), "stderr": b"".join(err)}


def _retry_wrapper(func, check=None):
    """
    Decorator to add retrying to functions.
    The optional predicate 'check' can be used to map the output of 'func' to
    success or failure (default: True -> success)
    """
    if check is None:
        check = bool

    from functools import wraps

    @wraps(func)
    def wrapped(*args, **kwargs):
        count = retry = kwargs.pop("retry", 0)
        retry_sleep = kwargs.pop("retry_sleep", 0)
        if retry <= 1:
            # no retry
            return func(*args, **kwargs)
        else:
            while retry:
                retval = func(*args, **kwargs)
                if check(retval):
                    return retval
                retry -= 1
                if retry and retry_sleep:
                    time.sleep(retry_sleep)
            raise RuntimeError(f"the command {args[0]} failed {count} times")

    return wrapped


retry_call = _retry_wrapper(subprocess.call, lambda rc: rc == 0)
retry_tee_call = _retry_wrapper(tee_call, lambda rv: rv["retcode"] == 0)
retry_log_call = _retry_wrapper(log_call, lambda rv: rv["retcode"] == 0)


def ensureDirs(dirs):
    """
    Ensure that the specified directories exist, creating them if needed.
    """
    if isinstance(dirs, str):
        dirs = (dirs,)
    for path in dirs:
        if not os.path.exists(path):
            os.makedirs(path)


def genDocId(data):
    """
    Internal function to generate the document id from the data dictionary.

    The data field used to prepare the id are (in order):

         ['slot', 'build_id', 'project', 'platform', 'type']

    unless the special field '_id' is defined, in which case its value is used
    as id.

    >>> genDocId({'slot': 'lhcb-head', 'build_id': 123, 'type': 'config'})
    'lhcb-head.123.config'
    >>> genDocId({'slot': 'lhcb-head', 'build_id': 123,
    ... 'platform': 'x86_64-slc6-gcc48-opt', 'type': 'start'})
    'lhcb-head.123.x86_64-slc6-gcc48-opt.start'
    >>> genDocId({'slot': 'lhcb-head', 'build_id': 123,
    ... 'platform': 'x86_64-slc6-gcc48-opt', 'type': 'tests',
    ... 'project': 'Gaudi'})
    'lhcb-head.123.Gaudi.x86_64-slc6-gcc48-opt.tests'
    >>> genDocId({'slot': 'lhcb-head', '_id': 'something'})
    'something'
    """
    if "_id" in data:
        return data["_id"]
    fields = ["slot", "build_id", "project", "platform", "type"]
    return ".".join([str(data[f]) for f in fields if f in data])


def wipeDir(path):
    """
    Helper function to remove a directory.
    """
    # FIXME: this can be done asynchronously
    logging.info("Removing directory %s", path)
    if os.path.exists(path):
        shutil.rmtree(path)
        ensureDirs([path])


def recursive_update(dest, data):
    """
    Similar to dict.update, update a dictionary with the entries from
    another one, but do it recursively, if the element in both sides are
    dictionaries.

    >>> a = {'a': {'x': 1}, 'b': {'n': 0}, 'c': [1, 2, 3]}
    >>> b = {'a': {'y': 2}, 'b': 'abc', 'c': {}}
    >>> recursive_update(a, b) == {'a': {'x': 1, 'y': 2}, 'b': 'abc', 'c': {}}
    True
    >>> a == {'a': {'x': 1, 'y': 2}, 'b': 'abc', 'c': {}}
    True

    It can also be used to deep clone a dictionary:

    >>> a = {'a': {'a': {'a': 1}}, 'b': [1, 2, 3]}
    >>> copy = {}
    >>> _ = recursive_update(copy, a)
    >>> copy == a
    True
    >>> copy is a
    False
    >>> copy['a'] is a['a']
    False
    """
    from collections.abc import Mapping, MutableMapping

    if not isinstance(dest, MutableMapping):
        raise TypeError("argument 1 must be a mutable mapping")
    if not isinstance(data, Mapping):  # try to convert to dictionary
        data = dict(data)
    for k in data:
        try:
            if k not in dest:
                dest[k] = type(data[k])()
            recursive_update(dest[k], data[k])
        except (TypeError, ValueError):
            dest[k] = data[k]
    return dest


class SlotAborted(Exception):
    """
    Exception raised when a slot was aborted.
    """

    pass


class Dashboard:
    """
    Wrapper for the CouchDB-based dashboard.
    """

    if os.environ.get("PRIVATE_DIR"):
        CRED_FILE = os.path.join(os.environ["PRIVATE_DIR"], "couchdb-admin")
    else:
        CRED_FILE = os.path.expanduser(os.path.join("~", "private", "couchdb-admin"))

    SERVER_URL = os.environ.get("COUCHDB_HOST", "https://lhcb-couchdb.cern.ch/")

    @classmethod
    def dbName(cls, flavour):
        """
        Return database name for the given flavour.
        """
        return f"nightlies-{flavour}"

    def __init__(self, credentials=None, flavour="nightly", server=None, dbname=None):
        """
        @param credentials: pair with (username, password) of a valid account
                            on the server
        @param flavour: build flavour, used to select the database to use
        @param server: URL of the server
        @param dbname: database name (overrides flavour)
        """
        import socket

        import couchdb

        self._log = logging.getLogger("Dashboard")

        if credentials is None:
            cred_data = None
            if os.path.exists(self.CRED_FILE):
                self._log.debug("taking credentials from %s", self.CRED_FILE)
                cred_data = open(self.CRED_FILE).read()
            elif os.environ.get("COUCHDB_ADMIN"):
                self._log.debug("taking credentials from COUCHDB_ADMIN")
                cred_data = os.environ["COUCHDB_ADMIN"]

            if cred_data:
                # make a tuple with the first two lines of the file
                credentials = tuple([l.strip() for l in cred_data.splitlines()][:2])
            else:
                self._log.warning("no couchdb credentials found")

        self.flavour = flavour

        if not server:
            server = self.SERVER_URL
        if not server.endswith("/"):
            server += "/"
        if not dbname:
            dbname = self.dbName(flavour)

        self._log.debug("preparing connection to dashboard (%s%s)", server, dbname)
        self.server = couchdb.Server(server)
        self.server.resource.credentials = credentials
        self.db = self.server[dbname]
        self._log.debug("connected")

    def lastBuildId(self, slot):
        """
        Return the latest build id recorded for the given slot.
        """
        # the keys in the view are [slot, id] or [slot, id, platform]
        # id is numeric and '.' counts as larger than any number
        rows = list(self.db.view("summaries/lastBuildId", key=slot, group=True))
        return rows[0].value if rows else 0

    def urlForKey(self, key):
        """
        Return the URL that can be used for retrieveing the data for a given key.
        """
        return "/".join((self.db.resource.url, key))

    def update(self, key, changes):
        """
        Update the content of an object in the database.

        @param key: object id in the database
        @param changes: either a dictionary to update the content of the object
                        with or a callable accepting a dict as input and
                        returning the updated object
        """
        from time import sleep

        from couchdb import ResourceConflict, ServerError

        self._log.debug("updating %s", self.urlForKey(key))

        if callable(changes):
            chg = changes
        else:

            def chg(d):
                return recursive_update(d, changes)

        allowed_server_errors = 3
        seconds_between_server_retries = 60
        while True:
            # this will be the error message if the changes cannot be applied
            new = ": cannot apply changes"
            try:
                old = self.db.get(key, {})
                # work on a clone of the object to detect actual changes
                new = chg(json.loads(json.dumps(old)))
                if new != old:
                    self.db[key] = new
                else:
                    self._log.debug("no change")
                break
            except ResourceConflict:
                self._log.debug("conflict updating %r, retrying", key)
            except ServerError as err:
                self._log.warning("problems contacting the server: %s", err)
                if allowed_server_errors >= 0:
                    self._log.debug("retrying in %d s", seconds_between_server_retries)
                    sleep(seconds_between_server_retries)
                    allowed_server_errors -= 1
                else:
                    self._log.error(
                        "failed to connect to %s, giving up", self.server.resource.url
                    )
                    exit(2)
            except:
                self._log.debug("failed to store %r", new)
                raise

    def __getitem__(self, key):
        return self.db[key]

    def assert_not_aborted(self, key):
        """
        Raise SlotAborted exception if the slot is flagged as aborted
        """
        try:
            info = self.db[key].get("aborted")
            if info:
                raise SlotAborted(key, info)
        except KeyError:
            pass


class TaskQueue:
    """
    Simple class to schedule asynchronous operations.
    """

    def __init__(self):
        """
        Initialize the task queue, the worker thread will be started if needed.
        """
        from queue import Queue

        self.queue = Queue()
        self._thread = None

    @property
    def thread(self):
        """
        Worker thread, created on demand.
        """
        if self._thread is None or not self._thread.is_alive():

            def worker(q):
                "Worker main loop."
                while True:
                    try:
                        action, args, kwargs = q.get()
                        action(*args, **kwargs)
                    finally:
                        q.task_done()

            from threading import Thread

            self._thread = Thread(target=worker, args=(self.queue,))
            # do not wait for the thread when exiting the application
            self._thread.daemon = True
            self._thread.start()

        return self._thread

    def add(self, task, args=None, kwargs=None):
        """
        Add a new task to the queue.

        @param task: callable to be executed
        @param args: positional arguments to pass to the task callable
        @param kwargs: keyword arguments to pass to the task callable
        """
        assert self.thread and self.thread.is_alive(), "worker thread not available"
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = {}
        self.queue.put((task, args, kwargs))

    def join(self):
        """
        Waits until all the tasks completed.
        """
        self.queue.join()


class JenkinsTest:
    """
    Class representing a test ready to be run
    """

    SLOT = "slot"
    SBID = "slot_build_id"
    PROJECT = "project"
    PLATFORM = "platform"
    TESTGROUP = "testgroup"
    TESTRUNNER = "testrunner"
    TESTENV = "testenv"
    LABEL = "os_label"
    COUNT = "count"
    JOB_ALLATTRIBUTES = [
        SLOT,
        SBID,
        PROJECT,
        PLATFORM,
        LABEL,
        TESTGROUP,
        TESTRUNNER,
        TESTENV,
        COUNT,
    ]

    @classmethod
    def fromJenkinsString(cls, test_string):
        """Build the obkject from the string passed to Jenkins"""
        test_list = test_string.split(".")
        slot = test_list[0]
        slot_build_id = test_list[1]
        project = test_list[2]
        platform = test_list[3]
        os_label = None
        testgroup = None
        testrunner = None
        testenv = None
        count = 1

        # Check it the param nb 5 is specified and if it is != None
        if len(test_list) > 4:
            if test_list[4].lower() != "none":
                os_label = test_list[4]

        # If the label is still None, we take it from teh platform
        if os_label is None:
            os_label = platform.split("-")[1]

        # Now check for the test group and runner
        if len(test_list) > 5:
            testgroup = test_list[5]

        if len(test_list) > 6:
            testrunner = test_list[6]

        if len(test_list) > 7:
            testenv = test_list[7]

        if len(test_list) > 8:
            count = test_list[8]

        return JenkinsTest(
            slot,
            slot_build_id,
            project,
            platform,
            os_label,
            testgroup,
            testrunner,
            testenv,
            count,
        )

    @classmethod
    def fromScheduledTest(cls, stest):
        """Build the object from a scheduled test object"""
        return JenkinsTest(
            stest.slot,
            stest.build_id,
            stest.project,
            stest.platform,
            stest.os_label,
            stest.testgroup,
            stest.testrunner,
            stest.testenv,
            stest.count,
        )

    def __init__(
        self,
        slot,
        slot_build_id,
        project,
        platform,
        os_label=None,
        testgroup=None,
        testrunner=None,
        testenv=None,
        count=1,
    ):
        """Basic constructor"""
        self.slot_build_id = slot_build_id
        self.slot = slot
        self.project = project
        self.platform = platform
        self.testgroup = testgroup
        self.testrunner = testrunner
        self.os_label = os_label
        self.testenv = testenv
        self.count = count

    def getParameterLines(self):
        """Returns a list of key=value lines for each parameter"""
        return [f"{x}={getattr(self, x)}\n" for x in JenkinsTest.JOB_ALLATTRIBUTES]

    def toJenkinsString(self):
        """Generate the job description for Jenkins"""
        return ".".join(
            [
                self.slot,
                str(self.slot_build_id),
                self.project,
                self.platform,
                self.os_label if self.os_label else "None",
                self.testgroup,
                self.testrunner if self.testrunner else "qmtest",
                self.testenv if self.testenv else "None",
                str(self.count),
            ]
        )

    def __str__(self):
        """
        Convert to string
        """
        return ".".join(
            [f"{k}={getattr(self, k)}" for k in JenkinsTest.JOB_ALLATTRIBUTES]
        )


def _packcmd(srcs, dest, cwd=".", dereference=True, exclude=None):
    """
    Helper function to call the packing command.
    """
    from subprocess import call

    cmd = ["zip", "-r", "-q"]
    if not dereference:
        cmd.append("-y")
    cmd.append(dest)
    cmd.append("-@")
    if exclude:
        for n in [tpl.format(x) for x in exclude for tpl in ("{}", "{}/", "{}/**")]:
            cmd.extend(["-x", n])

    from tempfile import TemporaryFile

    with TemporaryFile("w+") as file_list:
        file_list.write("\n".join(srcs))
        file_list.write("\n")
        file_list.flush()
        file_list.seek(0)
        try:
            result = call(cmd, cwd=cwd, stdin=file_list)
        except Exception as x:
            log = logging.getLogger("_packcmd")
            log.warning("exception while packing: %s: %s", type(x).__name__, x)
            result = 9
    return result


def _packtestcmd(srcs_, dest, cwd=".", dereference=True, exclude=None):
    """
    Helper function to call the package test command.
    """
    from subprocess import call

    return call(["unzip", "-t", "-q", dest], cwd=cwd)


def _find_broken_links(*args, **kwargs):
    """
    Find all broken links in the paths passed as arguments.

    Optionally, one can pass the root directory to start from as cwd.
    """
    cwd = kwargs.get("cwd", ".")
    for rel_src in args:
        src = os.path.join(cwd, rel_src)
        if os.path.isdir(src):
            yield from _find_broken_links(
                *[
                    os.path.join(rel_src, f)
                    for f in os.listdir(src)
                    if f not in (os.curdir, os.pardir)
                ],
                cwd=cwd,
            )
        elif os.path.islink(src) and not os.path.exists(src):
            yield rel_src


def pack(srcs, dest, cwd=".", checksum=None, dereference=True, exclude=None):
    """
    Package the directories 'srcs' into the package (tarball) 'dest' working
    from the directory 'cwd'.
    If a string is passed as 'checksum', together with the package a checksum
    file is produced with name <dest>.<checksum>.  The supported checksum types
    are those understood by the hashlib module (e.g. 'md5', 'sha1', etc.).

    If the creation of the package fails or the package is not consistent with
    the files to be packed, the packing is retried up to 3 times.
    """
    log = logging.getLogger("pack")

    if dereference:
        # check that we do not have broken links
        if not exclude:
            exclude = []

        def broken_link(path):
            "helper to report broken links"
            log.warning("ignore broken link %s", path)
            return path

        exclude.extend(broken_link(bl) for bl in _find_broken_links(*srcs, cwd=cwd))

    ensureDirs(os.path.dirname(dest))
    ok = False
    retry = 3
    while (not ok) and (retry >= 0):
        retry -= 1
        srcs_msg = ", ".join(srcs[:4]) + ("..." if len(srcs) > 4 else "")
        log.debug("packing %s as %s (from %s)", srcs_msg, dest, cwd)
        if _packcmd(srcs, dest, cwd, dereference, exclude) != 0:
            log.warning("failed to produce %s", dest)
            continue

        log.debug("checking %s", dest)
        if _packtestcmd(srcs, dest, cwd, dereference, exclude) != 0:
            log.warning("invalid package %s", dest)
            continue

        if checksum:
            import hashlib

            absdest = os.path.join(cwd, dest)
            hashsum = hashlib.new(checksum)
            log.debug("computing checksum (%s)", checksum)
            with open(absdest, "rb") as packfile:
                for chunk in iter(lambda: packfile.read(8192), b""):
                    hashsum.update(chunk)
            with open(absdest + "." + checksum, "w") as checkfile:
                checkfile.write(f"{hashsum.hexdigest()} *{os.path.basename(absdest)}\n")
            log.debug("checksum written to %s", dest + "." + checksum)
        # everything seems correct, stop retrying
        ok = True
    if not ok:
        log.error("failed to pack %s, I'm ignoring it", srcs)
        if os.path.exists(os.path.join(cwd, dest)):
            os.remove(os.path.join(cwd, dest))


def shallow_copytree(src, dst, ignore=None):
    """Create a shallow (made of symlinks) copy of a directory tree.

    The destination directory might exist and in that case it will be
    recursively filled with links pointing to the corresponding entries inside
    the source directory.
    If the destination does not exist, then shallow_copytree is equivalent to
    os.symlink.

    The optional argument `ignore` is a callable with the same semantics of
    the equivalent argument of shutil.copytree:

       callable(src, names) -> ignored_names

    """
    src = os.path.realpath(src)
    if not os.path.exists(dst):
        os.symlink(src, dst)
    elif os.path.isdir(src):
        names = [name for name in os.listdir(src) if name not in (".", "..")]
        ignored_names = set() if ignore is None else set(ignore(src, names))
        for name in set(names) - ignored_names:
            shallow_copytree(os.path.join(src, name), os.path.join(dst, name), ignore)


def find_path(name, search_path=None):
    """
    Look for a file or directory in a search path.

    If the search path is not specified, the concatenation of CMTPROJECTPATH
    and CMAKE_PREFIX_PATH is used.

    >>> find_path('true', ['/usr/local/bin', '/bin'])
    '/bin/true'
    >>> print(find_path('cannot_find_me', []))
    None
    """
    from os import environ, pathsep
    from os.path import exists, join

    if search_path is None:
        search_path = environ.get("CMAKE_PREFIX_PATH", "").split(pathsep) + environ.get(
            "CMTPROJECTPATH", ""
        ).split(pathsep)

    try:
        return next(
            join(path, name) for path in search_path if exists(join(path, name))
        )
    except StopIteration:
        logging.warning("%s not found in %r", name, search_path)
    return None


class IgnorePackageVersions:
    """
    Helper class which instances can be used as ignore argument of
    shallow_copytree to ignore versions of packages when cloning a container
    project.
    """

    def __init__(self, packages):
        """
        @param packages: list of objects describing packages, which must have a
                         property 'name' and a property 'version'
        """
        self._exclusions = {
            os.path.basename(pack.name): [pack.version] for pack in packages
        }

    def __call__(self, src, names):
        """
        Implements the semantic of the 'ignore' argument of shallow_copytree.
        """
        return self._exclusions.get(os.path.basename(src), [])


def applyenv(envdict, definitions):
    """
    Modify the environment  described by 'envdict' from a list of definitions
    of the type 'name=value', expanding the variables in 'value'.

    >>> env = {}
    >>> applyenv(env, ['foo=bar'])
    >>> env['foo']
    'bar'
    >>> applyenv(env, ['baz=some_${foo}'])
    >>> env['baz']
    'some_bar'

    If a variable in the value is not known, it is replaces with an empty
    string:

    >>> applyenv(env, ['unknown=${var}'])
    >>> env['unknown']
    ''
    """
    from collections import defaultdict
    from string import Template

    # use a temporary dictionary where unkown values default to ''
    tmp = defaultdict(str, envdict)
    # keep track of all explicitly set names
    all_names = set(envdict)
    # apply changes
    for item in definitions:
        name, value = item.split("=", 1)
        all_names.add(name)
        tmp[name] = Template(value).safe_substitute(tmp)
    # copy changes in the input dictionary excluding the variables
    # created as temporary empty placeholders
    envdict.update((k, v) for k, v in list(tmp.items()) if k in all_names)


def setenv(definitions):
    """
    Modify the environment from a list of definitions of the type 'name=value',
    expanding the variables in 'value'.

    >>> setenv(['foo=bar'])
    >>> os.environ['foo']
    'bar'

    @note: it is equivalent to 'applyenv(os.environ, definitions)'
    """
    applyenv(os.environ, definitions)


@contextlib.contextmanager
def chdir(dirname=None, create=False):
    """
    Context manager useful to switch to a directory for a context block and
    back to the previous location once we are out put the block.

    See http://www.astropython.org/snippet/2009/10/chdir-context-manager
    """
    curdir = os.getcwd()
    try:
        if dirname is not None:
            if not os.path.isdir(dirname) and create:
                os.makedirs(dirname)
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


def write_patch(patchfile, olddata, newdata, filename):
    """
    Write the difference between olddata and newdata (of filename) in
    patchfile.

    @param patchfile: file object to which write the differences
    @param olddata: old version of the data
    @param newdata: new version of teh data
    @param fileanme: name of the file to be used in the diff headers
    """
    from difflib import context_diff

    if hasattr(olddata, "splitlines"):
        olddata = olddata.splitlines(True)
    if hasattr(newdata, "splitlines"):
        newdata = newdata.splitlines(True)
    for l in context_diff(
        olddata,
        newdata,
        fromfile=os.path.join("a", filename),
        tofile=os.path.join("b", filename),
    ):
        patchfile.write(l)


class JobParams:
    """
    Helper class to format job parameters.

    >>> print(JobParams(b='x', a=1))
    a=1
    b=x
    """

    def __init__(self, **kwargs):
        """
        Initialize the instance
        """
        self.__dict__.update(kwargs)

    def __str__(self):
        """
        Convert the instance to parameter file format.
        """
        data = []
        for k in sorted(self.__dict__):
            if not k.startswith("_"):
                data.append(f"{k}={getattr(self, k)}")
        return "\n".join(data)


def postToMergeRequest(name_or_id, mreq_iid, message, new_comment=False, token=None):
    """
    Add the passed message as comment to a merge request in gitlab.cern.ch.

    @param name_or_id: qualified name or id of a project in gitlab
    @param mreq_iid: local id of the merge request
    @param message: what to post to the merge request
    @param new_comment: whether to always post a new comment or edit
    @param token: gitlab API token (default: os.environ['GITLAB_TOKEN'])
    """
    server = gitlab.Gitlab(
        "https://gitlab.cern.ch/", token or os.environ["GITLAB_TOKEN"]
    )
    logging.debug("looking for merge request %s in project %s", mreq_iid, name_or_id)
    try:
        project = server.projects.get(name_or_id)
        mreq = project.mergerequests.get(mreq_iid)
        if new_comment:
            mreq.notes.create({"body": message})
        else:
            time_tag = datetime.now().strftime("%Y-%m-%d %H:%M")
            message = f"- __[{time_tag}]__ {message}"
            server.auth()  # sets server.user to the authenticated user
            all_notes = mreq.notes.list(all=True, order_by="created_at", sort="desc")
            # NB: replying to a plain note makes it a discussion, so next
            # time it won't be found and a new one will be made.
            own_plain_notes = [
                note
                for note in all_notes
                if (
                    note.author["id"] == server.user.id
                    and not note.system
                    and note.type != "DiscussionNote"
                )
            ]
            last_note = own_plain_notes[0] if own_plain_notes else None
            # update an existing note only if it is not too long
            # gitlab has a limit of 1000000 characters
            if last_note and len(last_note.body) < 500000:
                last_note.body = last_note.body + "\n" + message
                last_note.save()
            else:
                mreq.notes.create({"body": message})
    except Exception as err:
        logging.error(str(err))
        raise


def getMRTitle(name_or_id, mreq_iid, token=None):
    """
    Return the title of a merge request in gitlab.cern.ch.

    @param name_or_id: qualified name or id of a project in gitlab
    @param mreq_iid: local id of the merge request
    @param token: gitlab API token (default: os.environ['GITLAB_TOKEN'])
    """
    token = token or os.environ.get("GITLAB_TOKEN")
    if not token:
        # the MR title is icing on the cake, we do not need to fail
        return ""

    server = gitlab.Gitlab("https://gitlab.cern.ch/", token)
    logging.debug("looking for merge request %s in project %s", mreq_iid, name_or_id)
    try:
        project = server.projects.get(name_or_id)
        mreq = project.mergerequests.get(mreq_iid)
        return mreq.title
    except Exception as err:
        logging.error(str(err))
        raise


def getMRTargetBranch(name_or_id, mreq_iid, token=None):
    """
    Return the target branch of a merge request in gitlab.cern.ch.

    @param name_or_id: qualified name or id of a project in gitlab
    @param mreq_iid: local id of the merge request
    @param token: gitlab API token (default: os.environ['GITLAB_TOKEN'])
    """
    token = token or os.environ.get("GITLAB_TOKEN")
    if not token:
        # if we cannot interrogate Gitlab, we can assume 'master'
        return "master"

    server = gitlab.Gitlab("https://gitlab.cern.ch/", token)
    logging.debug("looking for merge request %s in project %s", mreq_iid, name_or_id)
    try:
        project = server.projects.get(name_or_id)
        mreq = project.mergerequests.get(mreq_iid)
        return mreq.target_branch
    except Exception as err:
        logging.error(str(err))
        raise


def getDefaultBranch(name_or_id, token=None):
    """
    Return the name of the default branch of a project.

    This is needed to resolve the special version "HEAD".
    """
    token = token or os.environ.get("GITLAB_TOKEN")
    if not token:
        # if we cannot interrogate Gitlab, we can assume 'master'
        return "master"

    server = gitlab.Gitlab("https://gitlab.cern.ch/", token)
    logging.debug("query default branch name for project %s", name_or_id)
    try:
        project = server.projects.get(name_or_id)
        logging.debug(
            "project %s default branch is %s", name_or_id, project.default_branch
        )
        return project.default_branch
    except Exception as err:
        logging.error(str(err))
        raise


def getAllMergeRequestIDs(
    name_or_id, state="opened", filters=None, labels=None, token=None
):
    """
    Return a list of all the ids of the merge resquests of a project in GitLab.

    @param name_or_id:  name or id of the project
    @param state: state of the merge request (usually 'opened')
    """
    server = gitlab.Gitlab(
        "https://gitlab.cern.ch/", token or os.environ["GITLAB_TOKEN"]
    )
    logging.debug("looking for %s merge requests in project %s", state, name_or_id)
    try:
        if filters:
            filters = [f.split("=", 1) for f in filters if "=" in f]
        else:
            filters = []

        if labels is None:
            labels = []
        elif isinstance(labels, str):
            labels = [labels]
        labels = set(labels)

        def accepted(mr):
            """
            Helper to keep only mrege requests matching the filters.
            """
            # first apply the filters
            for k, v in filters:
                if str(getattr(mr, k)) != v:
                    return False
            # of what remains we accept
            #  - those with the right label, if specified
            return labels.intersection(mr.labels)

        project = server.projects.get(name_or_id)
        mrs = [
            mr.iid
            for mr in project.mergerequests.list(state=state, all=True)
            if accepted(mr)
        ]
        mrs.sort()
        return mrs
    except Exception as err:
        logging.error(str(err))
        raise


def gitlabProjectExists(project):
    """
    Quick check to see if a project exists and is public in Gitlab.
    """
    try:
        logging.debug("probing %s in Gitlab", project)
        url = f"https://gitlab.cern.ch/{project}.git/info/refs?service=git-upload-pack"
        return urllib.request.urlopen(url).getcode() == 200
    except Exception:
        return False


MR_COMMENT_TMPLS = {
    True: (
        "Validation started with [{slot}#{id}]("
        "https://lhcb-nightlies.web.cern.ch/nightly/{slot}/{id}/)"
    ),
    False: (
        "Automatic merge failed in [{slot}#{id}]("
        "https://lhcb-nightlies.web.cern.ch/nightly/{slot}/{id}/{proj}/checkout"
    ),
}


def notifyMergeRequest(proj, name_or_id, mreq_iid, success, token=None):
    """
    Post the link to the slot build as comment to a merge request.
    """
    if (
        not proj
        or not proj.slot
        or not proj.slot.build_id
        or (os.environ.get("NO_UPDATE_MR", "false").lower() not in ("false", "0", ""))
    ):
        # noting to notify
        return
    if not token and "GITLAB_TOKEN" not in os.environ:
        logging.warning(
            "cannot post comment to gitlab for project %s, mr %s", name_or_id, mreq_iid
        )
        return

    message = MR_COMMENT_TMPLS[success].format(
        slot=proj.slot.name, id=proj.slot.build_id, proj=proj.name
    )
    postToMergeRequest(name_or_id, mreq_iid, message, token=token)


def cpuinfo():
    """
    Return the CPU information of the machine as a list of dictionaries.

    Only Linux is supported.
    """
    cpuinfo = []
    try:
        current = {}
        for l in open("/proc/cpuinfo"):
            try:
                k, v = (x.strip() for x in l.split(":", 1))
                if k == "processor":
                    current = {k: v}
                    cpuinfo.append(current)
                elif k == "flags":
                    current[k] = v.split()
                else:
                    current[k] = v
            except ValueError:
                pass  # ignore lines without a ':'
    except OSError:
        pass  # ignore missing /proc/cpuinfo
    return cpuinfo


def write_json(obj, filename, pretty=True):
    """
    Write a JSON serialized object to file.
    """
    with codecs.open(filename, "w", "utf-8") as f:
        json.dump(obj, f, indent=2 if pretty else None)


def natsort_key(v, _nsre=re.compile(r"(\d+)")):
    """
    See https://stackoverflow.com/a/16090640
    """
    return tuple(int(x) if x.isdigit() else x.lower() for x in _nsre.split(v))


class TemporaryDir:
    """
    Helper class to create a temporary directory and manage its lifetime.

    An instance of this class can be used inside the 'with' statement and
    returns the path to the temporary directory.
    """

    def __init__(self, chdir=False, keep=False, skel=None):
        """Constructor.

        @param chdir: change to the temporary directory while inside the
                      context
        @param keep: do not delete the temporary directory once out of context
        @param skel: fill the temporary directory with the content of the
                     provided directory
        """
        import tempfile
        from os.path import join

        self.chdir = chdir
        self.keep = keep
        self.path = tempfile.mkdtemp()
        self.old_dir = None
        if skel:
            for src, _dirs, files in os.walk(skel):
                dst = join(self.path, os.path.relpath(src, skel))
                if not os.path.exists(dst):
                    os.makedirs(dst)
                    shutil.copymode(src, dst)
                for f in [join(src, f) for f in files]:
                    shutil.copy(f, dst)

    def join(self, *args):
        """
        Equivalent to os.path.join(self.path, *args).
        """
        return os.path.join(self.path, *args)

    def __str__(self):
        """String representation (path to the temporary directory)."""
        return self.path

    def remove(self):
        """
        Remove the temporary directory.
        After a call to this method, the object is not usable anymore.
        """
        if self.path:  # allow multiple calls to the remove method
            shutil.rmtree(self.path, ignore_errors=True)
            self.path = None

    def __enter__(self):
        """
        Context Manager protocol 'enter' function.
        """
        if self.chdir:
            self.old_dir = os.getcwd()
            os.chdir(self.path)
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context Manager protocol 'exit' function.
        Remove the temporary directory and let the exceptions propagate.
        """
        if self.old_dir:
            os.chdir(self.old_dir)
            self.old_dir = None
        if not self.keep:
            self.remove()
        else:
            print("WARNING: not removing temporary directory", self.path)
        return False


def compatible_lcg_external_files(ext_file_name):
    """
    Given a filename like `/some/path/LCG_externals_<platform>.txt` return a list of
    names where `<platform>` is replaced with a compatible architecture.
    """
    # we want to always try, at least, the passed name
    paths = [ext_file_name]

    # split the name in components
    parts = re.match(r"^(.*/LCG_externals_)([^-]+(?:-[^-]+){3})(\.txt)$", ext_file_name)
    if not parts:
        # no need to continue if we do not understand the filename
        return paths
    head, platform, tail = parts.groups()
    _, os_id, comp, opt = platform.split("-")

    # this is a trick to promote "x86_64+avx2" to "x86_64_v3"
    arch = requires(platform).split("-", 1)[0]

    # if it's a known architecture we extend the list with the
    # architectures we can use
    archs = get_supported_archs(ARCH_DEFS[arch]) if arch in ARCH_DEFS else [arch]

    comp_parts = comp.split("+")
    comps = ["+".join(comp_parts[0:n]) for n in range(len(comp_parts), 0, -1)]

    opt_parts = opt.split("+")
    opts = ["+".join(opt_parts[0:n]) for n in range(len(opt_parts), 0, -1)]

    # list of externals files we could use
    paths.extend(
        f"{head}{arch}-{os_id}-{comp}-{opt}{tail}"
        for arch in archs
        for comp in comps
        for opt in opts
    )

    # remove duplicates (preserving the order)
    unique = []
    for path in paths:
        if path not in unique:
            unique.append(path)

    return unique


def coerce_str(s):
    """
    Get a str out of str or bytes.
    """
    return s.decode("utf-8", errors="replace") if isinstance(s, bytes) else s

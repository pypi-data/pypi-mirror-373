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
import contextlib
import logging
import os
from os.path import exists, join, normpath, relpath
from subprocess import PIPE, Popen

logging.basicConfig(level=logging.FATAL)

# Uncomment to disable the tests.
# __test__ = False

from LbNightlyTools import Utils
from LbNightlyTools.tests.utils import TemporaryDir

_testdata = normpath(join(*([__file__] + [os.pardir] * 4 + ["testdata"])))


def _getfilelist(path, start=".", followlinks=True):
    """
    Get the list of files and directories in a directory as they are returned
    by 'zip -Z1' (in arbitrary order).
    """
    for root, dirs, files in os.walk(join(start, path), followlinks=followlinks):
        yield relpath(root, start) + "/"
        for filename in files:
            yield relpath(join(root, filename), start)
        if not followlinks:
            # when not following links we need to check if some of the directories are
            # symlinks
            for filename in dirs:
                if os.path.islink(os.path.join(root, filename)):
                    yield relpath(join(root, filename), start)


def test_basic():
    "Utils.pack() basic functionality"
    with TemporaryDir() as tmpdir:
        dest = os.path.join(tmpdir, "indexer.zip")
        Utils.pack(["indexer"], dest, cwd=_testdata, checksum="md5")
        assert exists(dest)
        assert exists(dest + ".md5")
        list_tar = Popen(["unzip", "-Z1", dest], stdout=PIPE)
        out, _ = list_tar.communicate()
        assert list_tar.returncode == 0
        found_files = {l.strip().decode("utf-8") for l in out.splitlines()}
        expected_files = set(_getfilelist("indexer", _testdata))
        assert expected_files == found_files
        md5sum_check = Popen(
            ["md5sum", "--check", os.path.basename(dest + ".md5")],
            cwd=os.path.dirname(dest),
        )
        assert md5sum_check.wait() == 0

    with TemporaryDir() as tmpdir:
        dest = os.path.join(tmpdir, "indexer.zip")
        Utils.pack(["indexer"], dest, cwd=_testdata)
        assert exists(dest)
        assert not exists(dest + ".md5")
        list_tar = Popen(["unzip", "-Z1", dest], stdout=PIPE)
        out, _ = list_tar.communicate()
        assert list_tar.returncode == 0
        found_files = {l.strip().decode("utf-8") for l in out.splitlines()}
        expected_files = set(_getfilelist("indexer", _testdata))
        assert expected_files == found_files


def test_dereference_links():
    "Utils.pack() with dereferencing symbolic links"
    # (implicitly cleans broken links)
    with TemporaryDir() as tmpdir:
        linksdir = os.path.join(tmpdir, "links")
        os.makedirs(os.path.join(linksdir, "dir_a"))
        with open(os.path.join(linksdir, "a.txt"), "w") as f:
            f.write("test file")
        os.symlink("a.txt", os.path.join(linksdir, "b.txt"))
        os.symlink(
            os.path.join(os.pardir, "a.txt"), os.path.join(linksdir, "dir_a", "a.txt")
        )
        os.symlink("dir_a", os.path.join(linksdir, "dir_b"))
        os.symlink("no_file", os.path.join(linksdir, "broken"))

        dest = os.path.join(tmpdir, "links.zip")
        Utils.pack(["links"], dest, cwd=tmpdir, checksum="md5")
        assert exists(dest)
        assert exists(dest + ".md5")
        list_tar = Popen(["unzip", "-Z1", dest], stdout=PIPE)
        out, _ = list_tar.communicate()
        assert list_tar.returncode == 0
        found_files = {l.strip().decode("utf-8") for l in out.splitlines()}
        expected_files = set(_getfilelist("links", tmpdir))
        expected_files.remove("links/broken")
        assert expected_files == found_files
        md5sum_check = Popen(
            ["md5sum", "--check", os.path.basename(dest + ".md5")],
            cwd=os.path.dirname(dest),
        )
        assert md5sum_check.wait() == 0


def test_symlinks():
    "Utils.pack() with symbolic links"
    # (preserve broken links)
    with TemporaryDir(keep=True) as tmpdir:
        linksdir = os.path.join(tmpdir, "links")
        os.makedirs(os.path.join(linksdir, "dir_a"))
        with open(os.path.join(linksdir, "a.txt"), "w") as f:
            f.write("test file")
        os.symlink("a.txt", os.path.join(linksdir, "b.txt"))
        os.symlink(
            os.path.join(os.pardir, "a.txt"), os.path.join(linksdir, "dir_a", "a.txt")
        )
        os.symlink("dir_a", os.path.join(linksdir, "dir_b"))
        os.symlink("no_file", os.path.join(linksdir, "broken"))

        dest = os.path.join(tmpdir, "links.zip")
        Utils.pack(["links"], dest, cwd=tmpdir, checksum="md5", dereference=False)
        assert exists(dest)
        assert exists(dest + ".md5")
        list_tar = Popen(["unzip", "-Z1", dest], stdout=PIPE)
        out, _ = list_tar.communicate()
        assert list_tar.returncode == 0
        found_files = {l.strip().decode("utf-8") for l in out.splitlines()}
        expected_files = set(_getfilelist("links", tmpdir, followlinks=False))
        assert expected_files == found_files
        md5sum_check = Popen(
            ["md5sum", "--check", os.path.basename(dest + ".md5")],
            cwd=os.path.dirname(dest),
        )
        assert md5sum_check.wait() == 0


def test_exclude():
    "Utils.pack() basic functionality"
    with TemporaryDir() as tmpdir:
        dest = os.path.join(tmpdir, "build_tests.zip")
        Utils.pack(["build_tests"], dest, cwd=_testdata, exclude=["build_tests/orig"])
        assert exists(dest)
        list_tar = Popen(["unzip", "-Z1", dest], stdout=PIPE)
        out, _ = list_tar.communicate()
        assert list_tar.returncode == 0
        found_files = {l.strip().decode("utf-8") for l in out.splitlines()}
        expected_files = {
            l
            for l in _getfilelist("build_tests", _testdata)
            if "build_tests/orig" not in l
        }
        assert expected_files == found_files


@contextlib.contextmanager
def custom_packcmd(newcmd):
    """Helper context to replace the packing command in Utils."""
    old = Utils._packcmd
    Utils._packcmd = newcmd
    yield
    Utils._packcmd = old


@contextlib.contextmanager
def custom_packtestcmd(newcmd):
    """Helper context to replace the package test command in Utils."""
    old = Utils._packtestcmd
    Utils._packtestcmd = newcmd
    yield
    Utils._packtestcmd = old


def failer_cmd(src, dest, cwd=".", dereference=True, exclude=None):
    return 1


def test_failing_packer():
    "Utils.pack() failing packer"
    with TemporaryDir() as tmpdir:
        dest = os.path.join(tmpdir, "indexer.zip")
        # create an empty file to test the removal of corrupted packages
        open(dest, "wb").close()
        with custom_packcmd(failer_cmd):
            Utils.pack(["indexer"], dest, cwd=_testdata, checksum="md5")
        assert not exists(dest)
        assert not exists(dest + ".md5")


def test_failing_tester():
    "Utils.pack() failing tester"
    with TemporaryDir() as tmpdir:
        dest = os.path.join(tmpdir, "indexer.zip")
        # create an empty file to test the removal of corrupted packages
        open(dest, "wb").close()
        with custom_packtestcmd(failer_cmd):
            Utils.pack(["indexer"], dest, cwd=_testdata, checksum="md5")
        assert not exists(dest)
        assert not exists(dest + ".md5")

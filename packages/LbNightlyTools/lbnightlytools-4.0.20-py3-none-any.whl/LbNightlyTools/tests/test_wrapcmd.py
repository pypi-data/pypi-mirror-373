###############################################################################
# (c) Copyright 2023 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import os
import re
import sys

import pytest

from LbNightlyTools.Scripts.wrapcmd import main
from LbNightlyTools.tests.utils import TemporaryDir


def test_basic(monkeypatch, capsysbinary):
    with TemporaryDir() as tmp:
        monkeypatch.setattr(
            sys,
            "argv",
            ["lbn-wrapcmd", tmp, "some_target", "bash", "-c", "echo this is my test"],
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        stdout = capsysbinary.readouterr().out

        assert exc_info.value.args[0] == 0
        assert stdout == b"this is my test\n"

        logfiles = [
            f
            for f in os.listdir(tmp)
            if re.match(r"\d+-some_target-[0-9a-f]+-build.log", f)
        ]
        assert len(logfiles) == 1
        with open(os.path.join(tmp, logfiles[0]), "rb") as logfile:
            log = logfile.read()

        assert stdout in log
        assert b"bash -c 'echo this is my test'" in log
        assert b"command exited with" not in log


def test_failure(monkeypatch, capsysbinary):
    with TemporaryDir() as tmp:
        monkeypatch.setattr(sys, "argv", ["lbn-wrapcmd", tmp, "failed_target", "false"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        stdout = capsysbinary.readouterr().out

        assert exc_info.value.args[0] == 1
        assert stdout == b""

        logfiles = [
            f
            for f in os.listdir(tmp)
            if re.match(r"\d+-failed_target-[0-9a-f]+-build.log", f)
        ]
        assert len(logfiles) == 1
        with open(os.path.join(tmp, logfiles[0]), "rb") as logfile:
            log = logfile.read()

        assert b"false" in log
        assert b"command exited with 1" in log


def test_cat_special_case(monkeypatch, capfdbinary):
    with TemporaryDir() as tmp:
        tmpfile = os.path.join(tmp, "input_data.txt")
        with open(tmpfile, "wb") as f:
            f.write(b"some input data\n")

        monkeypatch.setattr(
            sys, "argv", ["lbn-wrapcmd", tmp, "cat_something", "cat", tmpfile]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        stdout = capfdbinary.readouterr().out

        assert exc_info.value.args[0] == 0
        assert stdout == b"some input data\n"

        logfiles = [
            f
            for f in os.listdir(tmp)
            if re.match(r"\d+-cat_something-[0-9a-f]+-build.log", f)
        ]
        assert len(logfiles) == 1
        with open(os.path.join(tmp, logfiles[0]), "rb") as logfile:
            log = logfile.read()

        assert (b"cat " + tmpfile.encode()) in log
        assert b"some input data\n" not in log
        assert b"command exited with" not in log


def test_create_target_dir(monkeypatch):
    with TemporaryDir() as tmp:
        target_dir = os.path.join(tmp, "some_target_dir")
        monkeypatch.setattr(
            sys, "argv", ["lbn-wrapcmd", target_dir, "some_target", "true"]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.args[0] == 0
        assert os.path.isdir(target_dir)
        logfiles = [
            f
            for f in os.listdir(target_dir)
            if re.match(r"\d+-some_target-[0-9a-f]+-build.log", f)
        ]
        assert len(logfiles) == 1


def test_wrong_arguments(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["lbn-wrapcmd", "not_enough_args"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.args[0] != 0

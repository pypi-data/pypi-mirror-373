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
import logging

import pytest

import LbNightlyTools.BuildMethods as bm


class mock_apptainer_call:
    def __init__(self, max_failures):
        self.max_failures = max_failures
        self.n_of_invocations = 0

    def __call__(self, *_args, **_kwargs):
        self.n_of_invocations += 1
        if self.n_of_invocations <= self.max_failures:
            return {"stdout": b"Failed to get file information for file descriptor 3\n"}
        else:
            return {"stdout": b"all good!\n"}


@pytest.mark.parametrize(
    "max_failures,expected_message",
    [
        (1, "apptainer successfully started on attempt 1"),
        (10, "giving up after repeated failures of apptainer"),
    ],
)
def test_workaroud(monkeypatch, caplog, max_failures, expected_message):
    """
    https://gitlab.cern.ch/lhcb-core/LbNightlyTools/-/issues/119
    """
    # avoid sleep time between retries
    monkeypatch.setattr(bm, "sleep", lambda _: None)
    # avoid running anything and pretend we ran apptainer and that fails a number of times
    monkeypatch.setattr(bm, "_log_call", mock_apptainer_call(max_failures))
    # avoid wrapping the command with apptainer
    monkeypatch.setenv("BINARY_TAG", "dummy")
    # capture DEBUG logging messages
    caplog.set_level(logging.DEBUG)

    bm.log_call(["true"])

    assert "apptainer failed to start on attempt 0" in caplog.text
    assert expected_message in caplog.text

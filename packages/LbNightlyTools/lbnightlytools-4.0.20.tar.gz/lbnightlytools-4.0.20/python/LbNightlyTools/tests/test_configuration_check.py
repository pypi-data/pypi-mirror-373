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
# Uncomment to disable the tests.
# __test__ = False

from LbNightlyTools.Configuration import Slot, check_slot


def test_ok():
    assert check_slot(Slot("slot"))


def test_warning_exceptions():
    assert not check_slot(Slot("slot", warning_exceptions="")), "bad type not detected"
    assert not check_slot(
        Slot("slot", warning_exceptions=[123])
    ), "bad inner type not detected"


def test_error_exceptions():
    assert not check_slot(Slot("slot", error_exceptions="")), "bad type not detected"
    assert not check_slot(
        Slot("slot", error_exceptions=[123])
    ), "bad inner type not detected"


def test_platforms():
    # note: we use Slot.fromDict to bypass the check on platform string in the constructor
    assert not check_slot(
        Slot.fromDict(dict(slot="slot", platforms=""))
    ), "bad type not detected"
    assert not check_slot(
        Slot.fromDict(dict(slot="slot", platforms=[123]))
    ), "bad inner type not detected"
    assert not check_slot(
        Slot.fromDict(dict(slot="slot", platforms=["x86_64-centos7-gcc9-opt, x"]))
    ), "bad inner value not detected"
    assert not check_slot(
        Slot.fromDict(dict(slot="slot", platforms=["x86_64-centos7-gcc9"]))
    ), "bad inner value not detected"

    good_platforms = [
        "x86_64-centos7-gcc9-do0",
        "x86_64+avx2+fma-centos7-gcc8-opt+g",
        "skylake_avx512-centos8-clang9-opt",
        "x86_64_v3-centos8-clang9+cuda123-opt",
        "armv8.1_a-centos7-gcc11-opt",
        "armv8.1_a-el9-gcc13-opt",
    ]
    assert check_slot(Slot("slot", platforms=good_platforms)), "false positive"
    assert check_slot(
        Slot.fromDict(dict(slot="slot", platforms=good_platforms))
    ), "false positive"


def test_env():
    assert not check_slot(Slot("slot", env="")), "bad type not detected"
    assert not check_slot(Slot("slot", env=[123])), "bad inner type not detected"
    assert not check_slot(Slot("slot", env=["dummy"])), "bad inner value not detected"
    assert not check_slot(Slot("slot", env=["123-"])), "bad inner value not detected"
    assert check_slot(Slot("slot", env=("a=1", "BINARY_TAG=stuff"))), "false positive"

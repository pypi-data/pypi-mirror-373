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

import pickle

from LbNightlyTools.Configuration import DBASE, Package, Project, Slot, slots


def setup():
    slots.clear()


def test_project():
    orig = Project(
        "Gaudi",
        "v26r1",
        checkout="git",
        checkout_opts=dict(url="http://git.cern.ch/pub/gaudi"),
        build_method="cmake",
        env=["USE_MAKE=1"],
    )
    clone = pickle.loads(pickle.dumps(orig))
    assert orig == clone


def test_package():
    orig = Package("AppConfig", "head")
    clone = pickle.loads(pickle.dumps(orig))
    assert orig == clone


def _test_dataproject():  # FIXME: temporarily disabled
    orig = DBASE([Package("AppConfig", "head")])
    clone = pickle.loads(pickle.dumps(orig))
    assert orig == clone


def _test_slot():  # FIXME: temporarily disabled
    orig = Slot(
        "test",
        [
            Project(
                "Gaudi",
                "v26r1",
                checkout="git",
                checkout_opts=dict(url="http://git.cern.ch/pub/gaudi"),
                build_method="cmake",
                env=["USE_MAKE=1"],
            ),
            DBASE([Package("AppConfig", "head")]),
        ],
        build_method="cmt",
        env=["Hello=World"],
    )
    clone = pickle.loads(pickle.dumps(orig))
    assert orig == clone

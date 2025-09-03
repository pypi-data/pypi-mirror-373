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

import LbTools


def test_get_info():
    info = LbTools.get_toolchain_info("103")
    assert "LHCB_Core" in info
    assert "LHCB_7" in info

    assert info["LHCB_Core"]["x86_64-centos7-clang12-dbg"]["compiler"] == "Clang 12.0.0"
    assert info["LHCB_Core"]["x86_64-centos7-gcc11-opt"]["compiler"] == "GNU 11.3.0"

    assert (
        info["LHCB_Core"]["x86_64-centos9-gcc12-opt"]["packages"]["Python"]["version"]
        == "3.9.12"
    )


def test_get_packages():
    deps, not_found, version_mismatch = LbTools.get_toolchain_packages(
        "103",
        "x86_64-centos9-gcc12-opt",
        {
            "Python": "3.9.12",
            "DummyExternal": "1.0.0",
            "ROOT": "6.26.00",
        },
    )
    assert set(deps) == {"Python", "ROOT"}
    assert not_found == ["DummyExternal"]
    assert version_mismatch == ["ROOT"]

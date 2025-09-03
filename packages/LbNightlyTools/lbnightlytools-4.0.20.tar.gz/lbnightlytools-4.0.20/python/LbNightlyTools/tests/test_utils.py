###############################################################################
# (c) Copyright 2017 CERN                                                     #
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
import re

from LbNightlyTools.Utils import compatible_lcg_external_files, recursive_update


def test_empty_lists_clone():
    old = {"entries": []}
    new = recursive_update({}, old)
    assert "entries" in new
    assert type(new["entries"]) is list
    assert new["entries"] == []


def test_lcg_ext_files():
    def shorten(files):
        """
        ignore non interesting entries in the list of files
        """
        return [f for f in files if re.search(r"x86_64(-|_v|\+)", f)]

    assert compatible_lcg_external_files("unknown") == ["unknown"]

    assert shorten(
        compatible_lcg_external_files("/path/LCG_externals_x86_64-slc6-gcc9-opt.txt")
    ) == [
        "/path/LCG_externals_x86_64-slc6-gcc9-opt.txt",
        "/path/LCG_externals_x86_64_v2-slc6-gcc9-opt.txt",
    ]
    assert shorten(
        compatible_lcg_external_files(
            "/path/LCG_externals_x86_64+avx2-slc6-gcc9-opt.txt"
        )
    ) == [
        "/path/LCG_externals_x86_64+avx2-slc6-gcc9-opt.txt",
        "/path/LCG_externals_x86_64_v3-slc6-gcc9-opt.txt",
        "/path/LCG_externals_x86_64_v2-slc6-gcc9-opt.txt",
        "/path/LCG_externals_x86_64-slc6-gcc9-opt.txt",
    ]
    assert shorten(
        compatible_lcg_external_files(
            "/path/LCG_externals_x86_64_v2-centos7-gcc11+dd4hep-dbg.txt"
        )
    ) == [
        "/path/LCG_externals_x86_64_v2-centos7-gcc11+dd4hep-dbg.txt",
        "/path/LCG_externals_x86_64_v2-centos7-gcc11-dbg.txt",
        "/path/LCG_externals_x86_64-centos7-gcc11+dd4hep-dbg.txt",
        "/path/LCG_externals_x86_64-centos7-gcc11-dbg.txt",
    ]

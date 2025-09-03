import os
import re
from os.path import exists, join, normpath

import pytest
from LbEnv import which

from LbNightlyTools.Configuration import Project, Slot
from LbNightlyTools.tests.utils import TemporaryDir

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


_testdata = normpath(join(*([__file__] + [os.pardir] * 4 + ["testdata"])))


def test_basic_build():
    with TemporaryDir():
        slot = Slot("slot", build_tool="echo")
        slot.projects.append(Project("Gaudi", "HEAD", checkout="ignore"))
        slot.checkout()

        res = slot.clean()
        assert "Gaudi" in res
        assert res["Gaudi"].returncode == 0
        assert "clean" in res["Gaudi"].stdout

        res = slot.build()
        assert "Gaudi" in res
        assert res["Gaudi"].returncode == 0
        assert "build" in res["Gaudi"].stdout

        res = slot.test()
        assert "Gaudi" in res
        assert res["Gaudi"].returncode == 0
        assert "test" in res["Gaudi"].stdout


def test_make_build():
    dummy_src = join(_testdata, "build_tests", "orig", "dummy", ".")
    with TemporaryDir(chdir=True):
        slot = Slot(
            "slot",
            build_tool="make",
            projects=[
                Project(
                    "dummy", "head", checkout="copy", checkout_opts=dict(src=dummy_src)
                )
            ],
        )
        slot.checkout()

        res = slot.build()
        assert exists(join("dummy", "Makefile"))
        assert "dummy" in res
        assert res["dummy"].returncode == 0
        assert b"=== building all ===" in res["dummy"].stdout
        assert exists(join("dummy", "all"))

        res = slot.test()
        assert "dummy" in res
        assert res["dummy"].returncode == 0
        assert b"=== running tests ===" in res["dummy"].stdout
        assert exists(join("dummy", "test_results"))

        res = slot.clean()
        assert "dummy" in res
        assert res["dummy"].returncode == 0
        assert b"=== cleaning ===" in res["dummy"].stdout
        assert exists(join("dummy", "Makefile"))
        assert not exists(join("dummy", "all"))
        assert not exists(join("dummy", "test_results"))


def test_cmt_build():
    if not which("cmt"):
        pytest.skip("cmt is missing")

    dummy_src = join(
        _testdata, "artifacts", "packs", "src", "TestProject.HEAD.testing-slot.src.zip"
    )

    config = "x86_64-centos7-gcc9-opt"
    print("platform:", config)

    with TemporaryDir(chdir=True):
        slot = Slot(
            "slot",
            build_tool="cmt",
            projects=[
                Project(
                    "TestProject",
                    "HEAD",
                    checkout="unzip",
                    checkout_opts=dict(src=dummy_src),
                )
            ],
            env=[
                "BINARY_TAG=" + config,
                "CMTCONFIG=${BINARY_TAG}",
            ],
        )
        slot.checkout()

        proj_root = join("TestProject")
        with open(join(proj_root, "Makefile"), "a") as mkf:
            # the Makefile in TestProject does not include tests and purge
            mkf.write(
                "test:\n"
                "\t@echo === running tests ===\n"
                "clean:\n"
                "\tcd TestProjectSys/cmt; $(MAKE) clean\n"
                "\t$(RM) -r InstallArea\n"
                "purge: clean\n"
                "\t$(RM) TestProjectSys/cmt/Makefile\n"
            )

        res = slot.build()
        assert exists(join(proj_root, "Makefile"))
        assert "TestProject" in res
        assert res["TestProject"].returncode == 0
        assert exists(join(proj_root, "TestProjectSys", config, "HelloWorld.exe"))
        assert exists(join(proj_root, "TestProjectSys", "cmt", "Makefile"))
        assert exists(join(proj_root, "InstallArea", config, "bin", "HelloWorld.exe"))

        res = slot.test()
        assert "TestProject" in res
        assert res["TestProject"].returncode == 0

        res = slot.clean()
        assert "TestProject" in res
        assert res["TestProject"].returncode == 0
        assert not exists(join(proj_root, "TestProjectSys", config, "HelloWorld.exe"))
        assert not exists(join(proj_root, "TestProjectSys", "cmt", "Makefile"))
        assert not exists(
            join(proj_root, "InstallArea", config, "bin", "HelloWorld.exe")
        )


def test_old_cmake_build():
    dummy_src = join(_testdata, "build_tests", "orig", "dummy", ".")
    with TemporaryDir(chdir=True):
        slot = Slot(
            "slot",
            build_tool="cmake",
            projects=[
                Project(
                    "dummy", "head", checkout="copy", checkout_opts=dict(src=dummy_src)
                )
            ],
        )
        slot.checkout()

        res = slot.build()
        assert exists(join("dummy", "", "Makefile"))
        assert "dummy" in res
        assert res["dummy"].returncode == 0
        assert b"=== configure ===" in res["dummy"].stdout
        assert b"=== building all ===" in res["dummy"].stdout
        assert b"=== unsafe-install ===" in res["dummy"].stdout
        assert b"=== post-install ===" in res["dummy"].stdout
        assert b"=== cleaning ===" in res["dummy"].stdout
        assert exists(join("dummy", "all-installed"))
        assert exists(join("dummy", "cache_preload.cmake"))

        res = slot.test()
        assert "dummy" in res
        assert res["dummy"].returncode == 0
        assert b"=== running tests ===" in res["dummy"].stdout
        assert exists(join("dummy", "test_results"))

        res = slot.clean()
        assert "dummy" in res
        assert res["dummy"].returncode == 0
        assert b"=== purge ===" in res["dummy"].stdout
        assert exists(join("dummy", "Makefile"))
        assert not exists(join("dummy", "all"))
        assert not exists(join("dummy", "test_results"))


_REQUIRED_CMDS = ["cmake", "ninja", "ccache"]


@pytest.mark.skipif(
    not ("BINARY_TAG" in os.environ and all(which(cmd) for cmd in _REQUIRED_CMDS)),
    reason=f"requires commands {_REQUIRED_CMDS} and $BINARY_TAG",
)
def test_cmake_build(tmpdir):
    proj_src = join(_testdata, "build_tests", "test_project", ".")
    with tmpdir.as_cwd():
        slot = Slot(
            "slot",
            build_tool="cmake",
            projects=[
                Project("LCG", "103", disabled=True),
                Project(
                    "test_project",
                    "head",
                    checkout="copy",
                    checkout_opts=dict(src=proj_src),
                ),
            ],
        )
        slot.checkout()

        res = slot.build()
        assert exists(join("test_project", "cache_preload.cmake"))
        assert exists(join("test_project", "build", "build.ninja"))
        assert exists(join("test_project", "build", "test_project_cmd"))
        assert exists(
            join(
                "test_project",
                "InstallArea",
                os.environ["BINARY_TAG"],
                "bin",
                "test_project_cmd",
            )
        )
        res = res.get("test_project")
        assert res is not None
        assert res.returncode == 0
        stdout = res.stdout
        assert b"#### CMake (new) configure ####" in stdout
        assert b"#### CMake (new) build ####" in stdout
        assert b"#### CMake (new) install ####" in stdout

        res = slot.test()
        res = res.get("test_project")
        assert res is not None
        assert res.returncode == 0
        stdout = res.stdout
        assert b"#### CMake (new) configure ####" in stdout
        assert b"#### CMake (new) test ####" in stdout
        assert re.search(b"Start \\d+: my_test", stdout)
        assert re.search(b"my_test[ . ]+Passed", stdout)

        res = slot.clean()
        res = res.get("test_project")
        assert res is not None
        assert res.returncode == 0
        stdout = res.stdout
        assert b"#### CMake (new) clean ####" in stdout
        assert not exists(join("test_project", "build", "test_project_cmd"))

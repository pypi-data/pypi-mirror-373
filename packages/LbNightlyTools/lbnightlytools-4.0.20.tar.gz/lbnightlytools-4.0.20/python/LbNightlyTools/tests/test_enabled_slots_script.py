##############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import pytest

# Uncomment to disable the tests.
pytestmark = pytest.mark.skip("FIXME: to review (required CouchDB connection?)")
__author__ = "Colas Pomies <colas.pomies@cern.ch>"
__test_mode__ = True

import json
import os
import re
from os.path import exists, join

import LbNightlyTools.Configuration
from LbNightlyTools.Scripts import EnabledSlots
from LbNightlyTools.tests.utils import TemporaryDir

_env_bk = dict(os.environ)


class TmpDirWithConfig(TemporaryDir):
    def __init__(self, *args, **kwargs):
        TemporaryDir.__init__(self, *args, **kwargs)
        os.makedirs(os.path.join(self.path, "configs"))


def setup():
    global _env_bk
    _env_bk = dict(os.environ)
    os.environ["JENKINS_HOME"] = "JENKINS_HOME"
    LbNightlyTools.Configuration.slots.clear()


def teardown():
    global _env_bk
    os.environ.clear()
    os.environ.update(_env_bk)
    LbNightlyTools.Configuration.slots.clear()


def generated_files(pattern=r"^slot-params-.*\.txt$"):
    return [x for x in os.listdir(".") if re.match(pattern, x)]


def test_wrong_number_arguments():
    with TemporaryDir(chdir=True):
        try:
            EnabledSlots.Script().run(["abc"])
            assert False, "Script should have exited"
        except SystemExit as x:
            assert x.code != 0
            assert not generated_files()


def test_no_data():
    with TemporaryDir(chdir=True):
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert not generated_files()


def test_no_file():
    with TmpDirWithConfig(chdir=True):
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert not generated_files()


def test_one_file_json_chmod_111():
    conf_data = {
        "slot": "lhcb-TEST",
        "description": "Test for unit test",
        "disabled": False,
        "projects": [],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }

    with TmpDirWithConfig(chdir=True):
        with open("configs/lhcb-TEST.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data))
        os.chmod("configs/lhcb-TEST.json", 0o111)
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/lhcb-TEST.json"))
        assert not generated_files()


def test_one_file_json_disabled_false():
    conf_data = {
        "slot": "lhcb-TEST",
        "description": "Test for unit test",
        "disabled": False,
        "projects": [],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }

    with TmpDirWithConfig(chdir=True):
        with open("configs/lhcb-TEST.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data))
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/lhcb-TEST.json"))
        assert json.load(open("configs/lhcb-TEST.json")) == conf_data
        assert generated_files() == ["slot-params-lhcb-TEST.txt"]


def test_one_file_json_disabled_true():
    conf_data = {
        "slot": "lhcb-TEST",
        "description": "Test for unit test",
        "disabled": True,
        "projects": [],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }

    with TmpDirWithConfig(chdir=True):
        with open("configs/lhcb-TEST.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data))
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/lhcb-TEST.json"))
        assert json.load(open("configs/lhcb-TEST.json")) == conf_data
        assert not generated_files()


def test_one_file_json_no_disabled():
    conf_data = {
        "slot": "lhcb-TEST",
        "description": "Test for unit test",
        "projects": [],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }

    with TmpDirWithConfig(chdir=True):
        with open("configs/lhcb-TEST.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data))
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/lhcb-TEST.json"))
        assert json.load(open("configs/lhcb-TEST.json")) == conf_data
        assert generated_files() == ["slot-params-lhcb-TEST.txt"]


def test_one_file_json_no_slot():
    conf_data = {
        "description": "Test for unit test",
        "disabled": False,
        "projects": [],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }

    with TmpDirWithConfig(chdir=True):
        with open("configs/lhcb-TEST.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data))
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/lhcb-TEST.json"))
        assert json.load(open("configs/lhcb-TEST.json")) == conf_data
        assert generated_files() == ["slot-params-lhcb-TEST.txt"]


def test_two_files_json():
    conf_data1 = {
        "description": "Test for unit test",
        "disabled": False,
        "projects": [],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }
    conf_data2 = {
        "slot": "lhcb-TEST2",
        "description": "Test for unit test",
        "disabled": False,
        "projects": [],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }

    with TmpDirWithConfig(chdir=True):
        print(generated_files(".*"))
        with open("configs/lhcb-TEST1.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data1))
        with open("configs/lhcb-TEST2.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data2))
        print(LbNightlyTools.Configuration.slots)
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/lhcb-TEST1.json"))
        assert exists(join("configs/lhcb-TEST2.json"))
        assert json.load(open("configs/lhcb-TEST1.json")) == conf_data1
        assert json.load(open("configs/lhcb-TEST2.json")) == conf_data2
        print(LbNightlyTools.Configuration.slots)
        assert sorted(generated_files()) == [
            "slot-params-lhcb-TEST1.txt",
            "slot-params-lhcb-TEST2.txt",
        ]


def test_one_job_xml_disbaled_false():
    test_xml = """
    <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="configuration.xsd">
        <slot disabled="false" hidden="false" name="lhcb-TEST" renice="+2" mails="true" description="lhcb-TEST use for unit TEST">
        </slot>
    </configuration>
    """
    with TmpDirWithConfig(chdir=True):
        with open("configs/configuration.xml", "w") as cfg_file:
            cfg_file.write(test_xml)
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/configuration.xml"))
        assert generated_files() == ["slot-params-lhcb-TEST.txt"]


def test_one_job_xml_disabled_true():
    test_xml = """
    <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="configuration.xsd">
        <slot disabled="true" hidden="false" name="lhcb-TEST" renice="+2" mails="true" description="lhcb-TEST use for unit TEST">
        </slot>
    </configuration>
    """
    with TmpDirWithConfig(chdir=True):
        with open("configs/configuration.xml", "w") as cfg_file:
            cfg_file.write(test_xml)
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/configuration.xml"))
        assert not generated_files()


def test_one_job_xml_no_disabled():
    test_xml = """
    <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="configuration.xsd">
        <slot hidden="false" name="lhcb-TEST" renice="+2" mails="true" description="lhcb-TEST use for unit TEST">
        </slot>
    </configuration>
    """
    with TmpDirWithConfig(chdir=True):
        with open("configs/configuration.xml", "w") as cfg_file:
            cfg_file.write(test_xml)
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/configuration.xml"))
        assert generated_files() == ["slot-params-lhcb-TEST.txt"]


def test_two_job_xml():
    test_xml = """
    <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="configuration.xsd">
        <slot disabled="false" hidden="false" name="lhcb-TEST1" renice="+2" mails="true" description="lhcb-TEST1 use for unit TEST">
        </slot>
        <slot disabled="false" hidden="false" name="lhcb-TEST2" renice="+2" mails="true" description="lhcb-TEST2 use for unit TEST">
        </slot>
    </configuration>
    """
    with TmpDirWithConfig(chdir=True):
        with open("configs/configuration.xml", "w") as cfg_file:
            cfg_file.write(test_xml)
        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/configuration.xml"))
        assert sorted(generated_files()) == [
            "slot-params-lhcb-TEST1.txt",
            "slot-params-lhcb-TEST2.txt",
        ]


def test_same_job_xml_and_json():
    test_xml = """
     <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="configuration.xsd">
        <slot disabled="false" hidden="false" name="lhcb-TEST" renice="+2" mails="true" description="lhcb-TEST use for unit TEST">
        </slot>
    </configuration>
    """
    conf_data = {
        "slot": "lhcb-TEST",
        "description": "Test for unit test",
        "disabled": False,
        "projects": [],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }

    with TmpDirWithConfig(chdir=True):
        with open("configs/configuration.xml", "w") as cfg_file:
            cfg_file.write(test_xml)
        with open("configs/lhcb-TEST.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data))

        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/configuration.xml"))
        assert exists(join("configs/lhcb-TEST.json"))
        assert generated_files() == ["slot-params-lhcb-TEST.txt"]


def test_different_job_xml_and_json():
    test_xml = """
     <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="configuration.xsd">
        <slot disabled="false" hidden="false" name="lhcb-TEST1" renice="+2" mails="true" description="lhcb-TEST1 use for unit TEST">
        </slot>
    </configuration>
    """
    conf_data = {
        "slot": "lhcb-TEST2",
        "description": "Test for unit test",
        "disabled": False,
        "projects": [],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }

    with TmpDirWithConfig(chdir=True):
        with open("configs/configuration.xml", "w") as cfg_file:
            cfg_file.write(test_xml)
        with open("configs/lhcb-TEST.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data))

        retval = EnabledSlots.Script().run([])
        assert retval == 0
        assert exists(join("configs/configuration.xml"))
        assert exists(join("configs/lhcb-TEST.json"))
        assert sorted(generated_files()) == [
            "slot-params-lhcb-TEST1.txt",
            "slot-params-lhcb-TEST2.txt",
        ]


def test_one_job_param():
    with TemporaryDir(chdir=True):
        retval = EnabledSlots.Script().run(["--slots", "lhcb-test"])
        assert retval == 0
        assert generated_files() == ["slot-params-lhcb-test.txt"]


def test_two_job_param():
    with TemporaryDir(chdir=True):
        retval = EnabledSlots.Script().run(["--slots", "lhcb-test lhcb-test2"])
        assert retval == 0
        assert sorted(generated_files()) == [
            "slot-params-lhcb-test.txt",
            "slot-params-lhcb-test2.txt",
        ]
    with TemporaryDir(chdir=True):
        retval = EnabledSlots.Script().run(["--slots", "lhcb-test, lhcb-test2"])
        assert retval == 0
        assert sorted(generated_files()) == [
            "slot-params-lhcb-test.txt",
            "slot-params-lhcb-test2.txt",
        ]


def test_mr_builds():
    conf_data = {
        "slot": "lhcb-master",
        "description": "Test for unit test",
        "projects": ["Rec"],
        "default_platforms": ["x86_64-slc6-gcc48-opt", "x86_64-slc6-gcc46-opt"],
        "USE_CMT": True,
    }
    mr_token = {
        "sources": ["lhcb/Rec!1753"],
        "trigger": {
            "merge_request_iid": 1753,
            "project_id": 401,
            "discussion_id": "d708ea762deae76f7d718eb0eefbc9b66c134190",
            "note_id": 2913001,
        },
        "platforms": None,
        "merge": False,
    }
    os.environ["MR_TOKEN"] = json.dumps(mr_token)
    with TmpDirWithConfig(chdir=True):
        with open("configs/lhcb-master.json", "w") as slot_file:
            slot_file.write(json.dumps(conf_data))
        retval = EnabledSlots.Script().run(["--resolve-mrs", "--no-submit"])
        assert retval == 0
        assert sorted(generated_files()) == [
            "slot-params-lhcb-master-mr.txt",
            "slot-params-lhcb-master-ref.txt",
        ]
    del os.environ["MR_TOKEN"]


for n, f in list(locals().items()):
    if n.startswith("test"):
        f.setup = LbNightlyTools.Configuration.slots.clear

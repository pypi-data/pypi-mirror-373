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

import json
import os

import pytest

from LbNightlyTools import Configuration
from LbNightlyTools.tests.utils import TemporaryDir, processFile

# Uncomment to disable the tests.
# __test__ = False


@pytest.fixture
def test_configuration(tmpdir, monkeypatch):
    monkeypatch.syspath_prepend(tmpdir)
    packdir = os.path.join(str(tmpdir), "lhcbnightlyconf")
    os.makedirs(packdir)
    with open(os.path.join(packdir, "configuration.py"), "w") as f:
        f.write(
            """from LbNightlyTools.Configuration import Slot, Project
slots = [Slot('special-slot-from-python',
     desc='Special slot described directly in Python',
     projects=[Project('Gaudi', 'v23r5'),
               Project('LHCb', 'v32r5', dependencies=['Gaudi'])])]
hidden_slots = [Slot('hidden-slot',
     desc='Special slot described directly in Python',
     projects=[Project('Gaudi', 'v23r5'),
               Project('LHCb', 'v32r5', dependencies=['Gaudi'])])]

duplicates = [Slot('one'), Slot('one')]
"""
        )
    with open(os.path.join(packdir, "__init__.py"), "w") as f:
        f.write("from .configuration import slots\n")


def show(left, right, width=80, headers=None):
    """
    Pretty print two objects side by side, highlighting the differences.
    """
    from pprint import pformat

    half_width = (width - 3) // 2
    left_lines = pformat(left, width=half_width).splitlines()
    right_lines = pformat(right, width=half_width).splitlines()

    to_extend = left_lines if len(left_lines) < len(right_lines) else right_lines
    to_extend.extend([""] * abs(len(right_lines) - len(left_lines)))

    format_str = f"{{0:<{half_width}}} {{2}} {{1:<{half_width}}}"

    def format_line(a, b):
        return format_str.format(a, b, " " if a == b else "|")

    if headers:
        print(format_line(*headers))
        print(width * "-")

    print("\n".join(format_line(a, b) for a, b in zip(left_lines, right_lines)))


def assert_equals(found, expected):
    show(found, expected, width=120, headers=("found", "expected"))
    assert found == expected


def add_defaults(expected):
    """
    Helper to avoid hardcoding everywhere default values.
    """
    slot_defaults = {
        "packages": [],
        "description": "Generic nightly build slot.",
        "build_tool": "cmake",
        "build_id": 0,
        "disabled": False,
        "env": [],
        "platforms": [],
        "preconditions": [],
        "error_exceptions": [],
        "warning_exceptions": [],
    }
    project_defaults = {
        "checkout": "default",
        "checkout_opts": {},
        "disabled": False,
        "env": [],
        "overrides": {},
        "dependencies": [],
        "with_shared": False,
    }
    package_defaults = {"checkout": "default", "container": "DBASE"}

    for k in slot_defaults:
        if k not in expected:
            expected[k] = slot_defaults[k]

    for project in expected["projects"]:
        for k in project_defaults:
            if k not in project:
                project[k] = project_defaults[k]

    for package in expected.get("packages", []):
        for k in package_defaults:
            if k not in package:
                package[k] = package_defaults[k]


def test_loadJSON():
    "Configuration.parse(json_file)"
    data = {
        "slot": "slot-name",
        "projects": [
            {"name": "Gaudi", "version": "v23r5"},
            {"dependencies": ["Gaudi"], "name": "LHCb", "version": "v32r5"},
        ],
    }
    expected = {
        "build_tool": "cmake",
        "slot": "slot-name",
        "projects": [
            {"name": "Gaudi", "version": "v23r5"},
            {"name": "LHCb", "version": "v32r5", "dependencies": ["Gaudi"]},
        ],
    }
    add_defaults(expected)

    found = processFile(json.dumps(data), Configuration.parse).toDict()
    assert_equals(found, expected)


def test_loadJSON_2():
    "Configuration.parse(json_with_slot)"
    data = {
        "projects": [
            {"name": "Gaudi", "version": "v23r5"},
            {"name": "LHCb", "version": "v32r5", "dependencies": ["Gaudi"]},
        ],
        "cmake_cache": {"KEY": "VALUE"},
    }
    expected = {
        "slot": "special-slot",
        "projects": [
            {"name": "Gaudi", "version": "v23r5"},
            {"name": "LHCb", "version": "v32r5", "dependencies": ["Gaudi"]},
        ],
        "build_tool": "cmake",
        "cmake_cache": {"KEY": "VALUE"},
    }
    add_defaults(expected)

    with TemporaryDir() as path:
        filepath = os.path.join(path, "special-slot.json")
        with open(filepath, "w") as f:
            f.write(json.dumps(data))
        slot = Configuration.getSlot("special-slot", path)
        found = slot.toDict()

    assert_equals(slot.cache_entries, expected["cmake_cache"])
    print("")
    assert_equals(found, expected)


def test_loadJSON_3():
    "JSON with data packages"
    data = {
        "slot": "slot-with-packages",
        "packages": [
            {"checkout_opts": {"export": True}, "name": "ProdConf", "version": "v1r19"},
            {
                "checkout_opts": {"export": True},
                "container": "PARAM",
                "name": "TMVAWeights",
                "version": "v1r4",
            },
        ],
        "projects": [],
    }
    expected = dict(data)
    add_defaults(expected)
    expected["projects"] = [
        {
            "checkout": "ignore",
            "disabled": False,
            "name": "DBASE",
            "no_test": True,
            "platform_independent": True,
            "version": "None",
        },
        {
            "checkout": "ignore",
            "disabled": False,
            "name": "PARAM",
            "no_test": True,
            "platform_independent": True,
            "version": "None",
        },
    ]

    slot = Configuration.Slot.fromDict(data)
    found = slot.toDict()

    # order of projects and packages is not relevant in this case
    found["projects"].sort(key=lambda p: p.get("name"))
    found["packages"].sort(key=lambda p: p.get("name"))
    expected["projects"].sort(key=lambda p: p.get("name"))
    expected["packages"].sort(key=lambda p: p.get("name"))

    assert_equals(found, expected)


def test_loadPy_legacy():
    "Configuration.getSlot from Python (legacy)"
    script = """from LbNightlyTools.Configuration import *
Slot('special-slot-from-python',
     desc='Special slot described directly in Python',
     projects=[Project('Gaudi', 'v23r5'),
               Project('LHCb', 'v32r5', dependencies=['Gaudi'])])
"""
    expected = {
        "slot": "special-slot-from-python",
        "description": "Special slot described directly in Python",
        "projects": [
            {"name": "Gaudi", "version": "v23r5"},
            {"name": "LHCb", "version": "v32r5", "dependencies": ["Gaudi"]},
        ],
    }
    add_defaults(expected)

    if "special-slot-from-python" in Configuration.slots:
        del Configuration.slots["special-slot-from-python"]
    assert "special-slot-from-python" not in Configuration.slots

    with TemporaryDir() as path:
        filepath = os.path.join(path, "configuration.py")
        with open(filepath, "w") as f:
            f.write(script)
        slot = Configuration.getSlot("special-slot-from-python", path)
        found = slot.toDict()

    assert_equals(found, expected)


def test_loadPy_1(test_configuration):
    "Configuration.getSlot from Python"
    expected = {
        "slot": "special-slot-from-python",
        "description": "Special slot described directly in Python",
        "projects": [
            {"name": "Gaudi", "version": "v23r5"},
            {"name": "LHCb", "version": "v32r5", "dependencies": ["Gaudi"]},
        ],
    }
    add_defaults(expected)

    slot = Configuration.getSlot("special-slot-from-python")
    assert_equals(slot.toDict(), expected)

    try:
        Configuration.getSlot("hidden-slot")
        assert False, "RuntimeError expected when looking for hidden-slot"
    except RuntimeError:
        pass

    slot = Configuration.getSlot(
        "hidden-slot", "lhcbnightlyconf.configuration:hidden_slots"
    )
    expected["slot"] = "hidden-slot"
    assert_equals(slot.toDict(), expected)

    try:
        Configuration.loadConfig("lhcbnightlyconf.configuration:duplicates")
        assert False, "we should not be able to get duplicated names"
    except AssertionError:
        pass

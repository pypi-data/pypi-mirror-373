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

from LbNightlyTools.Configuration import DBASE, Package, Project, Slot, slots
from LbNightlyTools.MergeRequestBuilds import create_mr_slots


@pytest.fixture
def reset_slots():
    slots.clear()
    yield
    slots.clear()


def create_master_slot():
    return Slot(
        "lhcb-master",
        projects=[
            Project("Detector", "v0-patches"),
            Project("LHCb", "master"),
            Project("Lbcom", "master"),
            Project("Rec", "master"),
            DBASE(packages=[Package("PRConfig", "HEAD")]),
        ],
        platforms=["x86_64-centos7-gcc9-opt"],
    )


def test_branch_mode(reset_slots):
    model_slot = create_master_slot()
    model_slots = [model_slot]

    with pytest.raises(ValueError):
        create_mr_slots(
            ["lhcb/Rec!1753", "lhcb/Rec!1755"],
            platforms=None,
            merge=False,
            model_slots=model_slots,
            with_downstream=True,
            force_model=None,
        )

    ref_slot, test_slot = create_mr_slots(
        ["lhcb/Rec!1753"],
        platforms=None,
        merge=False,
        model_slots=model_slots,
        with_downstream=True,
        force_model=None,
    )

    assert (
        ref_slot.projects["Detector"].checkout_opts["commit"]
        == test_slot.projects["Detector"].checkout_opts["commit"]
        == "b8b797e6496307132af05b4d2be29d7ee9416ad1"
    )

    assert (
        ref_slot.projects["LHCb"].checkout_opts["commit"]
        == test_slot.projects["LHCb"].checkout_opts["commit"]
        == "a41659c4ad4113c83d3a7789679228219057c921"
    )

    assert (
        ref_slot.projects["Rec"].checkout_opts["commit"]
        == "14f25f03810120eaae280e1f6b38e86a87f00b38"
    )

    assert (
        test_slot.projects["Rec"].checkout_opts["commit"]
        == "414ae00f32e2f738eb935e6a1847b010a087586c"
    )


def test_integration_mode(reset_slots):
    model_slot = create_master_slot()
    model_slots = [model_slot]

    ref_slot, test_slot = create_mr_slots(
        [
            "lhcb/LHCb@2ad1a811",  # a commit
            "lhcb/Rec!1755",
            "lhcb/Rec!1753",  # multiple MRs per project
            "lhcb-datapkg/PRConfig!135",  # a data package
            "lhcb-datapkg/AppConfig!100",  # a data package not in model
        ],
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model=None,
    )

    # the reference slot does not checkout commits or merge MRs
    assert all(not p.checkout_opts for p in ref_slot.projects)

    assert (
        test_slot.projects["LHCb"].checkout_opts["commit"]
        == "2ad1a8118eb04037fde5d9c522fb169de96f80bb"
    )
    assert not test_slot.projects["Lbcom"].checkout_opts
    assert test_slot.projects["Rec"].checkout_opts == {"merges": [1755, 1753]}
    assert test_slot.projects["DBASE"].packages["PRConfig"].checkout_opts == {
        "merges": [135]
    }
    assert test_slot.projects["DBASE"].packages["AppConfig"].checkout_opts == {
        "merges": [100]
    }


def test_model_deduction(reset_slots):
    model_slots = [
        Slot(
            "model-a",
            projects=[
                Project("Detector", "master"),
                Project("LHCb", "master"),
                Project("Lbcom", "master"),
                Project("Rec", "master"),
            ],
            platforms=["x86_64-el9-gcc13-opt", "x86_64-el9-gcc13-dbg"],
            metadata={"ci_test_model": True},
        ),
        Slot(
            "model-b",
            projects=[
                Project("LHCb", "run2-patches"),
                Project("Lbcom", "run2-patches"),
                Project("Rec", "run2-patches"),
            ],
            platforms=["x86_64-el9-gcc13-opt"],
            metadata={"ci_test_model": True},
        ),
        Slot(
            "model-c",
            projects=[
                Project("LHCb", "sim10-patches"),
                Project("Gauss", "Sim10"),
            ],
            platforms=["x86_64-el9-gcc13-opt"],
        ),
        Slot(
            "model-d",
            projects=[
                Project("LHCb", "run2-patches"),
                Project("Lbcom", "master"),
            ],
            platforms=["x86_64-el9-gcc13-opt", "x86_64-el9-gcc13-dbg"],
        ),
        Slot(
            "model-e",
            projects=[
                Project("LHCb", "run2-patches"),
                Project("Lbcom", "run2-patches"),
                Project("Gauss", "Sim10"),
            ],
            platforms=["x86_64-el9-gcc13-opt"],
        ),
    ]

    _, test_slot = create_mr_slots(
        [
            "lhcb/LHCb!4412",  # target master
        ],
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model=None,
    )
    assert test_slot.metadata["ci_test"]["model"] == "model-a"

    _, test_slot = create_mr_slots(
        [
            "lhcb/LHCb!4377",  # target run2-patches
        ],
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model=None,
    )
    assert test_slot.metadata["ci_test"]["model"] == "model-b"
    assert not test_slot.metadata.get("ci_test_model")

    _, test_slot = create_mr_slots(
        [
            "lhcb/LHCb!4377",  # target run2-patches
            "lhcb/Lbcom!700",  # target master
        ],
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model=None,
    )
    assert test_slot.metadata["ci_test"]["model"] == "model-d"

    _, test_slot = create_mr_slots(
        [
            "lhcb/LHCb!4407",  # target sim10-patches
            "lhcb/Lbcom!700",  # target master
        ],
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model=None,
    )
    assert test_slot.metadata["ci_test"]["model"] == "model-c"
    # Lbcom is not in the model, so it should be added
    assert hasattr(test_slot, "Lbcom")
    assert test_slot.projects["LHCb"].checkout_opts == {"merges": [4407]}
    assert test_slot.projects["Lbcom"].checkout_opts == {"merges": [700]}
    assert not test_slot.projects["Gauss"].checkout_opts

    with pytest.raises(RuntimeError):
        # no slot matches
        create_mr_slots(
            [
                "lhcb/LHCb!4407",  # target sim10-patches
                "lhcb/Gauss!1037",  # target master
            ],
            platforms=None,
            merge=True,
            model_slots=model_slots,
            with_downstream=True,
            force_model=None,
        )

    with pytest.raises(RuntimeError):
        # two slots match
        create_mr_slots(
            [
                "lhcb/Gauss!1031",  # target Sim10
            ],
            platforms=None,
            merge=True,
            model_slots=model_slots,
            with_downstream=True,
            force_model=None,
        )

    _, test_slot = create_mr_slots(
        [
            "lhcb/LHCb!4280",  # target 2018-patches
        ],
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model="model-a",
    )
    assert test_slot.metadata["ci_test"]["model"] == "model-a"
    assert test_slot.LHCb.version == "2018-patches"
    assert test_slot.Lbcom.version == "master"

    with pytest.raises(RuntimeError):
        # two slots match
        create_mr_slots(
            [
                "lhcb/LHCb!4280",  # target 2018-patches
            ],
            platforms=None,
            merge=True,
            model_slots=model_slots,
            with_downstream=True,
            force_model="unknown",
        )

    with pytest.raises(RuntimeError):
        # no slot matches
        create_mr_slots(
            [
                "lhcb/LHCb!4407",  # target sim10-patches
                "lhcb/LHCb!4412",  # target master
            ],
            platforms=None,
            merge=True,
            model_slots=model_slots,
            with_downstream=True,
            force_model=None,
        )

    with pytest.raises(RuntimeError):
        # no slot matches (project not in any slot)
        create_mr_slots(
            [
                "lhcb/Brunel!1209",  # target run2-patches
            ],
            platforms=None,
            merge=True,
            model_slots=model_slots,
            with_downstream=True,
            force_model=None,
        )


def test_platforms_overrides(reset_slots):
    model_slots = [
        Slot(
            "model-a",
            projects=[
                Project("Detector", "master"),
                Project("LHCb", "master"),
            ],
            platforms=["x86_64-el9-gcc13-opt", "x86_64-el9-gcc13-dbg"],
            metadata={"ci_test_model": True},
        ),
        Slot(
            "model-b",
            projects=[
                Project("Detector", "master"),
                Project("LHCb", "master"),
            ],
            platforms=["x86_64-el9-gcc13-opt", "x86_64-el9-gcc13-dbg"],
            metadata={"ci_test_platforms": ["x86_64-el9-gcc13-dbg"]},
        ),
    ]

    _, test_slot = create_mr_slots(
        [
            "lhcb/LHCb!4412",  # target master
        ],
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model="model-a",
    )
    assert test_slot.metadata["ci_test"]["model"] == "model-a"
    # make sure we get all platforms
    assert test_slot.platforms == ["x86_64-el9-gcc13-opt", "x86_64-el9-gcc13-dbg"]

    _, test_slot = create_mr_slots(
        [
            "lhcb/LHCb!4412",  # target master
        ],
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model="model-b",
    )
    assert test_slot.metadata["ci_test"]["model"] == "model-b"
    # make sure we get only the ci-test platforms
    assert test_slot.platforms == ["x86_64-el9-gcc13-dbg"]

    _, test_slot = create_mr_slots(
        [
            "lhcb/LHCb!4412",  # target master
        ],
        platforms=["x86_64-el9-gcc13-opt"],
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model="model-a",
    )
    assert test_slot.metadata["ci_test"]["model"] == "model-a"
    # make sure we get the requested platforms
    assert test_slot.platforms == ["x86_64-el9-gcc13-opt"]

    _, test_slot = create_mr_slots(
        [
            "lhcb/LHCb!4412",  # target master
        ],
        platforms="x86_64-el9-gcc13-opt , x86_64-el9-gcc12-dbg",
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model="model-a",
    )
    assert test_slot.metadata["ci_test"]["model"] == "model-a"
    # make sure we get the requested platforms
    assert test_slot.platforms == ["x86_64-el9-gcc13-opt", "x86_64-el9-gcc12-dbg"]


@pytest.mark.parametrize(
    "sources, args, expected_env",
    [
        (["lhcb/Rec!1755"], {"env": ["SOME_VAR=some_value"]}, ["SOME_VAR=some_value"]),
        (
            ["lhcb/Rec!1755"],
            {"env": ["name=value", "name2=value2"]},
            ["name=value", "name2=value2"],
        ),
        (
            ["lhcb/Rec!1755"],
            {"geom_overrides": ["name=value", "name2=value2"]},
            ["GEOMETRY_VERSION_OVERRIDE=name=value,name2=value2"],
        ),
        (
            ["lhcb/Rec!1755"],
            {"cond_overrides": ["name=value", "name2=value2"]},
            ["CONDITIONS_VERSION_OVERRIDE=name=value,name2=value2"],
        ),
        (
            ["lhcb/Rec!1755"],
            {"env": ["a=1"], "geom_overrides": ["b=2"], "cond_overrides": ["c=3"]},
            ["a=1", "GEOMETRY_VERSION_OVERRIDE=b=2", "CONDITIONS_VERSION_OVERRIDE=c=3"],
        ),
        (
            [],
            {"force_model": "lhcb-master", "env": ["SOME_VAR=some_value"]},
            ["SOME_VAR=some_value"],
        ),
    ],
)
def test_env_override(reset_slots, sources, args, expected_env):
    model_slot = create_master_slot()
    model_slots = [model_slot]

    all_args = dict(
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model=None,
    )
    all_args.update(args)

    _, test_slot = create_mr_slots(
        sources,
        **all_args,
    )
    assert test_slot.env == expected_env


def test_conddb_mr(reset_slots):
    model_slot = create_master_slot()
    model_slots = [model_slot]

    _, test_slot = create_mr_slots(
        ["lhcb-conddb/lhcb-conditions-database!123"],
        platforms=None,
        merge=True,
        model_slots=model_slots,
        with_downstream=True,
        force_model="lhcb-master",
        cond_overrides=["master=test1"],
    )
    # no change to the list of projects
    assert {project.name for project in test_slot.projects} == {
        project.name for project in model_slot.projects
    }
    assert all(project.enabled for project in test_slot.projects)
    assert test_slot.env == ["CONDITIONS_VERSION_OVERRIDE=master=test1"]
    # Detector and LHCb are implicitly "requested" when we override the environment variables
    assert test_slot.metadata["ci_test"]["requested_projects"] == [
        "Detector",
        "LHCb",
        "lhcb-conditions-database",
    ]

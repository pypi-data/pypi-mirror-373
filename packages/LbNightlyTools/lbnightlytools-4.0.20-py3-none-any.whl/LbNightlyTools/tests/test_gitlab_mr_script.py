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

import json
import os
from copy import deepcopy
from pathlib import Path

import pytest

from LbNightlyTools.Scripts import GitlabMR


@pytest.fixture
def hook_content():
    with open(Path(__file__).parent.joinpath("ci-test-hook-content.json")) as f:
        return json.load(f)


def test_get_hook_args(hook_content):
    args = GitlabMR.get_hook_args(hook_content)
    assert args.sources == ["lhcb/Rec!1753"]
    assert args.merge


def test_gitlab_feedback(hook_content):
    if not os.environ.get("GITLAB_TOKEN"):
        # for some reason getting a note requires a token
        return
    source = GitlabMR.get_hook_trigger(hook_content)
    note, discussion = GitlabMR.gitlab_note_discussion(source)
    assert hasattr(note, "awardemojis")
    assert hasattr(discussion, "notes")


def test_main():
    GitlabMR.get_main_job_config(
        [
            "gaudi/Gaudi!123",
            "lhcb/LHCb@v50r6",
            "lhcb-datapkg/TCK/HltTCK!5",
            "--branch",
            "--platforms=x86_64-centos7-gcc8-opt,x86_64-centos7-gcc8-dbg",
        ]
    )

    with pytest.raises(GitlabMR.TriggerError):
        # projects without namespaces should fail
        GitlabMR.get_main_job_config(["LHCb!123"])

    with pytest.raises(GitlabMR.TriggerError):
        # bare MRs should fail
        GitlabMR.get_main_job_config(["!123"])

    with pytest.raises(GitlabMR.TriggerError):
        # multiple sources for a project
        GitlabMR.get_main_job_config(["gaudi/Gaudi!123", "gaudi/Gaudi!456"])

    with pytest.raises(GitlabMR.TriggerError):
        # non-existant project
        GitlabMR.get_main_job_config(["lhcb/Foo!123"])

    with pytest.raises(GitlabMR.TriggerError):
        # non-existant MR
        GitlabMR.get_main_job_config(["lhcb/LHCb!1234567"])

    with pytest.raises(GitlabMR.TriggerError):
        # non-existant commit
        GitlabMR.get_main_job_config(["lhcb/LHCb@1234567890abcdef"])

    with pytest.raises(SystemExit):
        GitlabMR.get_main_job_config(["--help"])
    # TODO test stdout here


def test_main_with_hook(hook_content):
    hook_var = "TEST_MAIN_WITH_HOOK"
    args = ["--hook-var=" + hook_var]

    content = deepcopy(hook_content)
    content["object_attributes"]["note"] += " --branch"
    os.environ[hook_var] = json.dumps(content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert config["sources"] == ["lhcb/Rec!1753"]
    assert not config["merge"]
    assert not config["model"]

    # support full URLs to Gitlab
    content["object_attributes"][
        "note"
    ] = "/ci-test --branch https://gitlab.cern.ch/lhcb/LHCb/-/merge_requests/111"
    os.environ[hook_var] = json.dumps(content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert "lhcb/LHCb!111" in config["sources"]

    # deduce group when not specified
    content["object_attributes"]["note"] = "/ci-test --branch LHCb!111"
    os.environ[hook_var] = json.dumps(content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert "lhcb/LHCb!111" in config["sources"]

    # deduce group/project when not specified
    content["object_attributes"]["note"] = "/ci-test --branch !111"
    os.environ[hook_var] = json.dumps(content)
    try:
        config = GitlabMR.get_main_job_config(args)[0]
        assert False
    except GitlabMR.TriggerError as e:
        message = str(e)
        assert "lhcb/Rec!1753" in message and "lhcb/Rec!111" in message
        assert "Some projects given multiple times" in message

    # deduce group/project when not specified
    content["object_attributes"]["note"] = "/ci-test --merge !111"
    os.environ[hook_var] = json.dumps(content)
    try:
        config = GitlabMR.get_main_job_config(args)[0]
        assert False
    except GitlabMR.TriggerError as e:
        message = str(e)
        assert "lhcb/Rec!1753" in message and "lhcb/Rec!111" in message
        assert "is already merged" in message

    # again without --merge as that should be default
    content["object_attributes"]["note"] = "/ci-test !111"
    os.environ[hook_var] = json.dumps(content)
    try:
        config = GitlabMR.get_main_job_config(args)[0]
        assert False
    except GitlabMR.TriggerError as e:
        message = str(e)
        assert "lhcb/Rec!1753" in message and "lhcb/Rec!111" in message
        assert "is already merged" in message

    # throw an exception when parser fails
    content["object_attributes"]["note"] = "/ci-test --garbage"
    os.environ[hook_var] = json.dumps(content)
    try:
        GitlabMR.get_main_job_config(args)
    except GitlabMR.TriggerError as e:
        assert "unrecognized argument" in str(e)

    # throw an exception when parser fails
    content["object_attributes"]["note"] = "/ci-test garbage"
    os.environ[hook_var] = json.dumps(content)
    try:
        GitlabMR.get_main_job_config(args)
    except GitlabMR.TriggerError as e:
        assert "is not a valid source specification" in str(e)

    # support for usage (--help) message
    content["object_attributes"]["note"] = "/ci-test --help"
    os.environ[hook_var] = json.dumps(content)
    try:
        GitlabMR.get_main_job_config(args)
    except GitlabMR.TriggerError as e:
        message = str(e)
        assert message.startswith("usage:") and "positional arguments" in message

    # with/without downstream
    content["object_attributes"]["note"] = "/ci-test --branch LHCb!111"
    os.environ[hook_var] = json.dumps(content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert config["with_downstream"] is True

    content["object_attributes"][
        "note"
    ] = "/ci-test --branch LHCb!111 --with-downstream"
    os.environ[hook_var] = json.dumps(content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert config["with_downstream"] is True

    content["object_attributes"][
        "note"
    ] = "/ci-test --branch LHCb!111 --without-downstream"
    os.environ[hook_var] = json.dumps(content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert config["with_downstream"] is False

    content["object_attributes"][
        "note"
    ] = "/ci-test --branch LHCb!111 --model lhcb-head"
    os.environ[hook_var] = json.dumps(content)
    config = GitlabMR.get_main_job_config(args)[0]
    assert config["model"] == "lhcb-head"

    del os.environ[hook_var]


@pytest.mark.parametrize(
    "args,key,expected",
    [
        (["--env", "name=value"], "env", ["name=value"]),
        (["--env", "name=value,other=value"], "env", ["name=value", "other=value"]),
        (
            ["--env", "name=value,other=value,third=value"],
            "env",
            ["name=value", "other=value", "third=value"],
        ),
        (
            ["--env", "name=value", "--env", "other=value,third=value"],
            "env",
            ["name=value", "other=value", "third=value"],
        ),
        (["--geom-overrides", "name=value"], "geom_overrides", ["name=value"]),
        (
            [
                "--cond-overrides",
                "name=value",
                "--cond-overrides",
                "other=value,third=value",
            ],
            "cond_overrides",
            ["name=value", "other=value", "third=value"],
        ),
    ],
)
def test_env_override_options(args, key, expected):
    config = GitlabMR.get_main_job_config(args + ["--branch", "lhcb/LHCb!111"])[0]
    assert config[key] == expected

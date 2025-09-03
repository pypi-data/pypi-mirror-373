#!/usr/bin/env python
###############################################################################
# (c) Copyright 2019 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Script for handling GitLab hooks on MR comments for a `/ci-test`
trigger. It collects and passes the necessary information to the main
job that creates the build slots.

Well formed triggers must start with `/ci-test`, optionally preceded by
whitespace. Everything after `/ci-test` until the end of the line is
interpreted as arguments. Valid arguments are those defined by the
parser returned by `get_hook_parser()`.

A command line interface `lbn-gitlab-mr` is provided, which is the entry
point used by the `gitlab-mr` jenkins job triggered by the hook.
The code for the actual hook is located at [1].

Example uses:
- from MR lhcb/Rec!222
    /ci-test
    /ci-test --platforms=x86_64+avx2+fma-centos7-gcc8-opt
    /ci-test --branch
    /ci-test --branch lhcb/LHCb@v50r6 gaudi/Gaudi@a729b15e6
- from the command line
    lbn-gitlab-mr lhcb/Rec!222
    lbn-gitlab-mr lhcb/Rec!222 --platforms=x86_64+avx2+fma-centos7-gcc8-opt
    lbn-gitlab-mr lhcb/Rec!222 --branch
    lbn-gitlab-mr lhcb/Rec!222 --branch lhcb/LHCb@v50r6 gaudi/Gaudi@a729b15e6

[1]: https://gitlab.cern.ch/lhcb-core/lb-nightly-builds-frontend/blob/711225cddd663ba3622f3ea8f82d010ec5e287f7/lbnighties/ajax.py#L102-129

"""  # noqa
import argparse
import json
import logging
import os
import re
from itertools import chain

import gitlab

from LbNightlyTools.GitlabUtils import _getGitlabProject, _gitlabServer, gitlabGroup

logger = logging.getLogger(__name__)

TRIGGER = "/ci-test"
TRIGGER_LINE_RE = rf"^\s*{TRIGGER}($|\s+)"


class TriggerError(Exception):
    pass


class MissingTriggerError(Exception):
    pass


def get_hook_parser():
    """Return a parser for arguments received via the hook trigger."""

    parser = argparse.ArgumentParser(prog=TRIGGER, add_help=False)
    parser.add_argument(
        "sources",
        nargs="*",
        metavar="source",
        help=(
            "Non-default merge requests or commits. Examples of valid "
            "sources: lhcb/LHCb!222, lhcb/LHCb@v50r6, gaudi/Gaudi@a729b15e6 "
            "(if group/project is omitted assume that of trigger project)."
        ),
    )
    parser.add_argument("--platforms", help="Comma-separated list of platforms.")
    parser.add_argument(
        "--build-reference",
        action="store_true",
        help="Also launch reference build for integration test mode",
    )
    mr_opts_group = parser.add_mutually_exclusive_group()
    mr_opts_group.add_argument(
        "--merge",
        action="store_true",
        default=True,
        help="Integration test mode (tip of target branch + MRs).",
    )
    mr_opts_group.add_argument(
        "--branch", action="store_false", dest="merge", help="Branch only test mode"
    )
    # extra parameters passed to the main job, useful for testing, e.g.
    # --param scripts_version=branch-of-nightlies-jenkins-scripts
    # --param JENKINS_OVERRIDE_PIP_REQUIREMENTS=git+https://gitlab.
    #         cern.ch/lhcb-core/LbNightlyTools.git@some-branch
    parser.add_argument(
        "--param", dest="params", action="append", default=[], help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--with-downstream",
        dest="with_downstream",
        action="store_true",
        default=True,
        help="build and test downstream projects (the default)",
    )
    parser.add_argument(
        "--without-downstream",
        dest="with_downstream",
        action="store_false",
        help="do not build projects downstream of the specified ones",
    )
    parser.add_argument(
        "--model",
        help="name of the slot to use as model (default: auto detect)",
    )
    parser.add_argument(
        "--geom-overrides",
        metavar="OLD=NEW",
        action="append",
        help="add a geometry version override in the format 'orig_version=new_version[,...]'",
    )
    parser.add_argument(
        "--cond-overrides",
        metavar="OLD=NEW",
        action="append",
        help="add a condition version override in the format 'orig_version=new_version[,...]'",
    )
    parser.add_argument(
        "--env",
        metavar="NAME=VALUE",
        action="append",
        help="add an environment variable override in the format 'name=value[,...]'",
    )

    # Throw on error from parse_args instead of exiting
    def error(message):
        raise TriggerError(message + "\n\n" + parser.format_help())

    parser.error = error
    return parser, [
        "sources",
        "platforms",
        "merge",
        "params",
        "build_reference",
        "with_downstream",
        "model",
        "geom_overrides",
        "cond_overrides",
        "env",
    ]


def parse_comment(comment):
    commands = [
        line.strip() for line in comment.splitlines() if re.match(TRIGGER_LINE_RE, line)
    ]
    if not commands:
        return None  # trigger likely present, but not alone on a line
    elif len(commands) == 1:
        return commands[0].split()
    else:
        raise TriggerError("Comment includes multiple triggers")


def get_hook_args(content):
    """
    Return arguments by parsing the contents of the gitlab hook.

    @param content: Contents of gitlab hook
    """

    comment = content["object_attributes"]["note"]
    logger.debug(f"comment is\n{comment}")
    command_args = parse_comment(comment)
    if not command_args:
        return None
    assert command_args[0] == TRIGGER
    # TODO if len(args) == 0 and if this is not the top comment in
    # the discussion, find the last comment in the discussion with
    # /ci-test and take the arguments from there
    trigger_project = content["merge_request"]["target"]["path_with_namespace"]
    trigger_group = trigger_project.rsplit("/", 1)[0]
    trigger_source = "{}!{}".format(trigger_project, content["merge_request"]["iid"])

    class HelpAction(argparse.Action):
        def __call__(self, parser, *args, **kwargs):
            raise TriggerError(parser.format_help())

    parser = get_hook_parser()[0]
    parser.add_argument(
        "-h",
        "--help",
        nargs=0,
        action=HelpAction,
        dest=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
        help="show this help message and exit",
    )
    args = parser.parse_args(command_args[1:])

    # assume trigger project and group if not given
    def normalize_source(arg):
        URL = (
            r"^https://gitlab\.cern\.ch/(?P<path>.*)/-"
            r"/merge_requests/(?P<iid>[0-9]+)$"
        )
        if arg.startswith("!"):  # !123
            return trigger_project + arg
        elif re.match(URL, arg):
            # https://gitlab.cern.ch/lhcb/LHCb/-/merge_requests/2761
            m = re.match(URL, arg)
            return m.group("path") + "!" + m.group("iid")
        elif "/" not in arg and "!" in arg:  # Rec!123
            proj, _ = arg.split("!", 1)
            return f"{gitlabGroup(proj, default=trigger_group)}/{arg}"
        else:
            return arg

    args.sources = [normalize_source(arg) for arg in args.sources]

    # add trigger source as an implicit argument
    args.sources.insert(0, trigger_source)
    return args


def get_hook_trigger(content):
    """
    Return the ids of the note and discussion where the hook was triggered.

    @param content: Contents of gitlab hook
    """
    return dict(
        project_id=content["project"]["id"],
        merge_request_iid=content["merge_request"]["iid"],
        discussion_id=content["object_attributes"]["discussion_id"],
        note_id=content["object_attributes"]["id"],
    )


def gitlab_note_discussion(trigger_source):
    """
    Return GitLab note and discussion objects for the hook.

    @param trigger_source: IDs of project, mr, note and discussion.
    """
    gitlab_server = _gitlabServer()
    project = gitlab_server.projects.get(trigger_source["project_id"])
    mr = project.mergerequests.get(trigger_source["merge_request_iid"])
    return (
        mr.notes.get(trigger_source["note_id"]),
        mr.discussions.get(trigger_source["discussion_id"]),
    )


def gitlab_award_emoji(obj, name):
    """Award an emoji without failing if it exists already."""
    try:
        obj.awardemojis.create({"name": name})
    except gitlab.GitlabCreateError:
        pass


def invalid_source_reason(source, merge):
    """Return why source is invalid or None."""
    path_re = r"[A-Za-z0-9_\-.]+"
    project_re = rf"({path_re}/)+({path_re})"
    source_re = rf"^(?P<project>{project_re})(!(?P<mr>[0-9]+)|@(?P<ref>.+))$"
    m = re.match(source_re, source)
    if not m:
        return f'"{source}" is not a valid source specification'
    try:
        project = _getGitlabProject(m.group("project"))
        if m.group("mr"):
            mr = project.mergerequests.get(m.group("mr"))
            if merge:
                if mr.attributes["state"] == "merged":
                    return f'"{source}" is already merged'
                if mr.attributes["merge_status"] == "cannot_be_merged":
                    return f'"{source}" cannot be merged'
        elif m.group("ref"):
            project.repository_tree(ref=m.group("ref"))
    except gitlab.GitlabGetError as e:
        if e.response_code == 404:
            return f'"{source}" does not exist'
        raise
    return None


def get_main_job_config(command_args=None):
    """
    Parse options from command line and hook content (if available).
    Returns a tuple (json configuration, extra parameters, output file).

    @param command_args: Optional arguments to use instead of sys.argv.
    """
    hook_parser, hook_params = get_hook_parser()
    parser = argparse.ArgumentParser(
        parents=[hook_parser],
        description=f"define a main job from a {TRIGGER} hook",
    )
    parser.add_argument("--debug", action="store_true", help="debugging output")
    parser.add_argument(
        "--output", default="gitlab-slots-build.txt", help="output file name"
    )
    parser.add_argument(
        "--feedback",
        action="store_true",
        help="send feedback to GitLab discussion if working on a hook",
    )
    parser.add_argument(
        "--hook-var",
        help="name of environment variable containing hook content. "
        "Command line arguments take precedence",
    )
    args = parser.parse_args(command_args)

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    logger.debug(f"args: {args}")

    log_error = logger.error
    if args.hook_var:
        if args.sources:
            parser.error("cannot give both sources and --hook-var")
        if args.hook_var not in os.environ:
            parser.error(f"environment variable {args.hook_var} not defined")

        content = json.loads(os.environ[args.hook_var])
        logger.debug(f"hook content is\n{json.dumps(content, indent=2)}")

        # find the note and discussion ids for feedback (from here and
        # subsequent jobs)
        hook_trigger = get_hook_trigger(content)

        if args.feedback:
            note, discussion = gitlab_note_discussion(hook_trigger)
            # acknowledge the hook was received
            gitlab_award_emoji(note, "robot")

            def log_error(message):
                logger.error(message)
                gitlab_award_emoji(note, "rotating_light")
                discussion.notes.create(
                    {"body": f"Action failed with\n```\n{message}\n```"}
                )

        try:
            hook_args = get_hook_args(content)
        except TriggerError as e:
            log_error(str(e))
            raise

        if hook_args is None:
            logger.info("No trigger found in comment")
            raise MissingTriggerError("No trigger found in comment")
        else:
            logger.info(f"Found trigger with arguments {hook_args}")

        # set arguments from hook whenever they were not given on the
        # command line
        # But always overwrite the merge and with_downstream options based on what's in the hook
        # (FIXME: (MCl) this is because the default in the script args would override the explicit value from the hook)
        for p in hook_params:
            arg = getattr(hook_args, p)
            if (arg and not getattr(args, p)) or p in ("merge", "with_downstream"):
                setattr(args, p, arg)
    elif not args.sources:
        parser.error("specify at least one source or --hook-var")

    invalid = [
        _f for _f in [invalid_source_reason(s, args.merge) for s in args.sources] if _f
    ]
    if invalid:
        msg = "\n".join(invalid)
        log_error(msg)
        raise TriggerError(msg)

    if not args.merge:
        unique_projects = {re.split("!|@", s)[0] for s in args.sources}

        if len(unique_projects) < len(args.sources):
            msg = f"Some projects given multiple times: {args.sources}"
            log_error(msg)
            raise TriggerError(msg)

    # for branch only mode we always build a reference
    if not args.merge:
        args.build_reference = True

    # flatten list of comma-separated values
    for name in ("geom_overrides", "cond_overrides", "env"):
        if getattr(args, name):
            setattr(
                args,
                name,
                list(
                    chain.from_iterable(
                        value.split(",") for value in getattr(args, name)
                    )
                ),
            )

    # pass the hook arguments plus some other selected configuration
    config = {p: getattr(args, p) for p in hook_params}
    if args.hook_var:
        config["trigger"] = hook_trigger
    params = config.pop("params")

    return config, params, args.output


def main():
    try:
        config, params, output_fn = get_main_job_config()
    except MissingTriggerError:
        # we didn't find a proper trigger, so don't do anything
        # except the hook acknowledgement emoji
        logger.info("Missing trigger: not triggering main job")
        return 0
    except TriggerError:
        # error already logged, just return
        logger.info("Error in trigger: not triggering main job")
        return 0

    logger.info(f"json job configuration:\n{json.dumps(config, indent=2)}")

    # Write the file which defines variables for the main job.
    # MR_TOKEN: JSON containing the important configuration (i.e. hook
    #           arguments and id of discussion for feedback).
    with open(output_fn, "w") as f:
        for param in params:
            f.write(param + "\n")
        f.write("MR_TOKEN=" + json.dumps(config) + "\n")

    return 0

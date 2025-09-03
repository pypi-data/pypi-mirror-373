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
"""
Common utility functions used in scripts.
@author Marco Clemencic <marco.clemencic@cern.ch>
"""

import logging
import os
import re
import socket
import sys
from datetime import datetime
from functools import reduce

from LbNightlyTools.Configuration import Slot, findSlot
from LbNightlyTools.Utils import SlotAborted, TaskQueue, TemporaryDir, recursive_update
from LbNightlyTools.Utils import retry_call as call

# We first try to import from LbCommon, then revert to the old package (LbUtils)
# if needed
try:
    from LbCommon.Script import PlainScript as _PlainScript
except:
    from LbUtils.Script import PlainScript as _PlainScript

# change the default log format in LbUtils.Script
try:
    import LbCommon.Log as _lblog
except:
    import LbUtils.Log as _lblog

_lblog._default_log_format = "%(asctime)s:" + _lblog._default_log_format


class PlainScript(_PlainScript):
    def parseOpts(self, args):
        """
        Override LbUtils.Script.PlainScript logging settings.
        """
        _PlainScript.parseOpts(self, args)
        # set the level to the handlers too
        for hdlr in self.log.handlers:
            hdlr.setLevel(self.log.level)
        # reset the message format (LbUtils.Script uses a fixed one for DEBUG)
        if self.log.level <= logging.DEBUG:
            formatter = logging.Formatter(_lblog._default_log_format)
            for h in self.log.handlers:
                h.setFormatter(formatter)

    def run(self, args=sys.argv[1:]):
        try:
            return _PlainScript.run(self, args)
        except SlotAborted as err:
            self.log.warning("slot was aborted: %s", err)
            return 0


def addBasicOptions(parser):
    """
    Add some basic (common) options to the option parser (optparse.OptionParser
    instance).
    """
    parser.add_option(
        "--build-id",
        action="store",
        help="string to add to the tarballs of the build to "
        "distinguish them from others, the string can "
        "be a format string using the parameter "
        '"slot" [default: %default]',
    )

    parser.add_option(
        "--slot-build-id",
        action="store",
        type="int",
        help="numeric id of the build [default: "
        "taken from the slot configuration, "
        "the environment ${slot_build_id} or 0]",
    )

    parser.add_option(
        "--artifacts-dir",
        action="store",
        metavar="DIR",
        help="directory where to store the artifacts",
    )

    parser.add_option(
        "--projects",
        action="store",
        help="comma-separated list of projects to consider" " [default: all]",
    )

    parser.add_option(
        "--summary-prefix",
        action="store",
        help="prefix to use for generated summary directories" " [default: none]",
    )

    parser.set_defaults(
        build_id="{slot}",
        slot_build_id=None,
        artifacts_dir="artifacts",
        summary_prefix="",
    )
    return parser


def addBuildDirOptions(parser):
    """
    Add build directory specific options to the parser.
    """
    from optparse import OptionGroup

    group = OptionGroup(parser, "Build Dir Options")

    group.add_option(
        "--clean", action="store_true", help="purge the build directory before building"
    )

    group.add_option(
        "--no-clean",
        action="store_false",
        dest="clean",
        help="do not purge the build directory before " "building",
    )

    group.add_option(
        "--no-unpack",
        action="store_true",
        help="assume that the sources are already present",
    )

    parser.add_option_group(group)
    parser.set_defaults(clean=False, no_unpack=False)
    return parser


def addDeploymentOptions(parser):
    """
    Add report-specific options to the parser.
    """
    from optparse import OptionGroup

    group = OptionGroup(parser, "Deployment Options")

    group.add_option(
        "--rsync-dest",
        action="store",
        metavar="DEST",
        help="deploy artifacts to this location using rsync "
        "(accepts the same format specification as "
        "--build-id)",
    )

    parser.add_option_group(group)
    parser.set_defaults(rsync_dest=None)
    return parser


def addDashboardOptions(parser, with_submit=True):
    """
    Add dashboard-related options to the option parser (optparse.OptionParser
    instance).
    """
    from optparse import OptionGroup

    group = OptionGroup(parser, "Dashboard Options")

    if with_submit:
        group.add_option(
            "--submit",
            action="store_true",
            default=False,
            help="submit the results to Dashboard server",
        )

        group.add_option(
            "--no-submit",
            action="store_false",
            dest="submit",
            help="do not submit the results to Dashboard server " "(default)",
        )

    group.add_option(
        "--flavour", default="nightly", help="which build server to use (build flavour)"
    )

    group.add_option(
        "--db-url", help="database server to use instead of the default one"
    )

    group.add_option(
        "--db-name", help="override database name " "[default: nightlies-{flavour}]"
    )

    parser.add_option_group(group)
    return parser


def expandTokensInOptions(options, opt_names, **kwargs):
    """
    Given an options instance, the list of option names, and the list of
    keywords to replace, replace the options with the correct expanded stings.

    >>> from optparse import Values
    >>> options = Values()
    >>> options.name = '{token}'
    >>> expandTokensInOptions(options, ['name'], token='Hello')
    >>> options.name
    'Hello'
    """
    for opt_name in opt_names:
        try:
            val = getattr(options, opt_name)
            if val:
                setattr(options, opt_name, val.format(**kwargs))
        except AttributeError:
            pass


class RsyncDestination:
    """
    Class to manage deployments via rsync.
    """

    def __init__(self, rsync_dest, listener=None):
        """
        @param rsync_dest: root destination endpoint for rsync
        @param listener: optional message listener to notify when the sync is
                         completed
        """
        self.log = logging.getLogger("deployment.rsync")
        self.rsync_dest = rsync_dest
        self.listener = listener

    def accept(self, msg):
        """
        Implements the receiver side of the message protocol.

        Accepts artifacts and transfer them via rsync.

        Message: {'type': 'artifacts',
                  'path': <path to file or dir>,
                  'dest': <optional name at destination>}
        """
        if msg.get("type", "").startswith("artifacts") and "path" in msg:
            kwargs = {"path": msg["path"], "dest": msg.get("dest")}
            try:
                retcode = self.transfer(**kwargs)
            except:
                retcode = 1
            if self.listener:
                msg = dict(msg)
                msg.update({"type": "ready." + msg["type"], "retcode": retcode})
                self.listener.send(msg)

    def transfer(self, path, dest=None):
        """
        Copy file to the rsync destination.
        """
        cmd = ["eos", "cp", "-p", "--no-overwrite"]
        if self.log.getEffectiveLevel() > logging.DEBUG:
            cmd.append("--silent")

        dest = os.path.join(self.rsync_dest, dest) if dest else self.rsync_dest

        self.log.debug("deploying %s to %s", path, dest)

        env = dict(os.environ)
        env["EOS_MGM_URL"] = env["EOS_BASE_URL"]

        # FIXME: workaround for SLC5
        # with TemporaryDir() as tmpdir:
        #     # eos client wants to create basename(path) into dest, so we cheat
        #     os.symlink(path, os.path.join(tmpdir, os.path.basename(dest)))
        #     if os.path.isdir(path):
        #         cmd.append('--recursive')
        #         path += '/'  # eos client requires '/' at end of directories
        #     cmd.extend([path, os.path.dirname(dest)])
        #     return call(cmd, env=env, retry=3)
        def copy_files(srcs, dst):
            call(["eos", "mkdir", "-p", dst], env=env)
            self.log.debug(str(["eos", "cp", "--no-overwrite"] + srcs + [dst + "/"]))
            call(["eos", "cp", "--no-overwrite"] + srcs + [dst + "/"], env=env)

        if os.path.isfile(path):
            copy_files([path], dest)
        else:
            for root, dirs, files in os.walk(path):
                if files:
                    copy_files(
                        [os.path.join(root, f) for f in files],
                        os.path.join(dest, os.path.relpath(root, path)),
                    )
        return 0


class DashboardUpdate:
    """
    Handles dashboard database updates.
    """

    def __init__(self, script):
        from LbNightlyTools.Utils import Dashboard

        self.log = logging.getLogger("DashboardUpdate")
        opts = script.options

        if not opts.submit:
            self.log.debug("dashboard update not requested")
            self.dashboard = None
            return

        self.slot = script.slot
        self.platform = script.platform
        self.no_test = self.slot.no_test
        self.build_url = os.environ.get("BUILD_URL")
        self.hostname = os.environ.get("docker_hostname", socket.gethostname())
        self.doc_name = f"{self.slot.name}.{self.slot.build_id}"
        self.script_type = {
            "slot-config": "checkout",
            "build-result": "build",
            "tests-result": "test",
        }[script.json_type]

        self.dashboard = Dashboard(
            credentials=None,
            flavour=opts.flavour,
            server=opts.db_url,
            dbname=opts.db_name or Dashboard.dbName(opts.flavour),
        )

    def checkout_started(self, config):
        """
        record start of slot checkout
        """
        self.log.debug("checkout_started")
        data = {
            "type": "slot-info",
            "slot": self.slot.name,
            "build_id": self.slot.build_id,
            "config": recursive_update({}, config),  # clone object
            "checkout": {"host": self.hostname, "projects": {}},
            "builds": {},
            "tests": {},
        }
        config = data["config"]  # ignore the input data and work on the clone
        # move some infos from the config (message) to the checkout field
        data["date"] = config.pop("date")
        data["checkout"]["started"] = config.pop("started")
        data["checkout"]["trigger_url"] = config.pop("trigger_url")

        data["checkout"]["build_url"] = self.build_url

        def changes(d):
            "reset the slot info"
            if "_rev" in d:
                d = {"_rev": d["_rev"], "_id": d["_id"]}
            else:
                d = {}
            return recursive_update(d, data)

        self.dashboard.update(self.doc_name, changes)

    def checkout_update(self, msg):
        self.log.debug("checkout_update")

        def changes(d):
            name = msg.pop("project")
            d["checkout"]["projects"][name] = msg
            return d

        self.dashboard.update(self.doc_name, changes)

    def checkout_completed(self, config):
        """
        record end of slot checkout
        """
        self.log.debug("checkout_completed")
        data = {"config": recursive_update({}, config), "checkout": {}}  # clone object
        config = data["config"]  # ignore the input data and work on the clone
        # drop some data from the message
        config.pop("date")
        config.pop("started")
        config.pop("trigger_url")
        # move fields from config message to checkout field
        data["checkout"]["completed"] = config.pop("completed")
        self.dashboard.update(self.doc_name, data)

    def update_ready_builds(self, msg):
        """
        update the "ready-builds" object
        """
        self.log.debug("update_ready_builds: %s", msg["project"].name)

        def changes(d):
            d["type"] = "ready-builds"
            if "entries" not in d:
                d["entries"] = []
            d["entries"].append(
                {
                    "project": msg["project"].name,
                    "version": msg["project"].version,
                    "slot": self.slot.name,
                    "build_id": self.slot.build_id,
                    "platform": self.platform,
                    "time": str(datetime.now()),
                    "retcode": msg.get("retcode"),
                    "no_test": (self.slot.no_test or msg["project"].no_test),
                    "scripts": {
                        "repository": os.environ.get("scripts_repository"),
                        "version": os.environ.get("scripts_version"),
                    },
                    "venv": {
                        "JENKINS_OVERRIDE_PIP_REQUIREMENTS": os.environ.get(
                            "JENKINS_OVERRIDE_PIP_REQUIREMENTS"
                        ),
                        "JENKINS_RESET_VIRTUALENV": os.environ.get(
                            "JENKINS_RESET_VIRTUALENV"
                        ),
                        "env_hash": os.environ.get("env_hash"),
                        "temp_env": os.environ.get("temp_env"),
                    },
                }
            )
            return d

        self.dashboard.update("ready-builds", changes)

    def drop_build(self):
        """
        remove info about specific build (platform)
        """
        self.log.debug("drop_build")

        def changes(d):
            for k in ("builds", "tests"):
                if self.platform in d.get(k, ""):
                    del d[k][self.platform]
            return d

        self.dashboard.update(self.doc_name, changes)

    def global_build_started(self, msg):
        """
        set build start info
        """
        self.log.debug("global_build_started")
        data = {
            "builds": {
                self.platform: {
                    "info": {
                        "started": msg["started"],
                        "host": self.hostname,
                        "build_url": self.build_url,
                    }
                }
            }
        }
        self.dashboard.update(self.doc_name, data)

    def global_build_completed(self, msg):
        """
        set build completion info
        """
        self.log.debug("global_build_completed")
        data = {"builds": {self.platform: {"info": {"completed": msg["completed"]}}}}
        self.dashboard.update(self.doc_name, data)

    def project_build_started(self, msg):
        """
        set project build start
        """
        self.log.debug("project_build_started: %s", msg["project"])
        data = {
            "builds": {
                self.platform: {
                    msg["project"]: {
                        "started": msg["started"],
                        "build_url": self.build_url,
                    }
                }
            }
        }
        self.dashboard.update(self.doc_name, data)

    def project_build_completed(self, msg):
        """
        set project build completion
        """
        self.log.debug("project_build_completed: %s", msg["project"])
        data = {
            "builds": {
                self.platform: {
                    msg["project"]: {
                        "completed": msg["completed"],
                        "retcode": msg["retcode"],
                        "warnings": msg["warnings"],
                        "errors": msg["errors"],
                    }
                }
            }
        }
        self.dashboard.update(self.doc_name, data)

    def project_test_started(self, msg):
        """
        set project build start
        """
        self.log.debug("project_test_started: %s", msg["project"])
        data = {
            "tests": {
                self.platform: {
                    msg["project"]: {
                        "started": msg["started"],
                        "completed": None,
                        "host": self.hostname,
                        "build_url": self.build_url,
                    }
                }
            }
        }
        self.dashboard.update(self.doc_name, data)

    def project_test_completed(self, msg):
        """
        set project build completion
        """
        self.log.debug("project_test_completed: %s", msg["project"])
        from collections import defaultdict

        results = defaultdict(list)
        for res in msg["results"]:
            results[res["outcome"]].append(res["id"])
        # check that we are trying to update the result we created
        current = self.dashboard.db[self.doc_name]
        build_url = reduce(
            lambda d, k: d.get(k) or {},
            ["tests", self.platform, msg["project"], "build_url"],
            current,
        )
        if build_url != self.build_url:
            # some other build owns this entry, let's not mess with it
            self.log.warning(
                "attempt to update results from another test job (this: %s, other: %s)",
                self.build_url,
                build_url,
            )
            return
        # update the results
        data = {
            "tests": {
                self.platform: {
                    msg["project"]: {"completed": msg["completed"], "results": results}
                }
            }
        }
        self.dashboard.update(self.doc_name, data)

    def accept(self, msg):
        """
        Implements the receiver side of the message protocol.
        """
        if self.dashboard is None:
            return  # ignore all messages, no update requested
        msg_type = msg.get("type", "")
        if self.script_type == "checkout" and not msg_type:
            if "project" in msg:
                self.checkout_update(msg)
            elif "completed" in msg:
                self.checkout_completed(msg)
            else:
                self.checkout_started(msg)

        elif self.script_type == "build":
            if msg_type == "drop-build":
                self.drop_build()
            elif msg_type == "job-start":
                self.global_build_started(msg)
            elif msg_type == "job-end":
                self.global_build_completed(msg)
            elif msg_type == "ready.artifacts.build":
                self.update_ready_builds(msg)
            elif "artifacts" in msg_type:
                return  # ignore some types of messages
            elif not msg_type:
                if "completed" in msg:
                    self.project_build_completed(msg)
                else:
                    self.project_build_started(msg)

        elif self.script_type == "test" and not msg_type:
            if "completed" in msg:
                self.project_test_completed(msg)
            else:
                self.project_test_started(msg)


class PeriodicTestMsg:
    """
    Handles sending the message to the queue
    of ready builds for the periodic tests.
    """

    def __init__(self, script):
        from LbNightlyTools.Utils import Dashboard

        self.slot = script.slot
        self.platform = script.platform
        self.log = logging.getLogger("PeriodicTestMsg")
        self.dashboard = Dashboard(flavour="periodic")

    @classmethod
    def doc_id(cls, queue="BuildReady"):
        return f"nightly-builds:{queue}"

    def builds_ready(self, project):
        """
        sends the message that builds are ready
        """
        slot, build_id, platform = (
            self.slot.name,
            self.slot.build_id,
            self.platform,
        )
        self.log.debug(
            "build ready for %s/%s/%s/%s",
            slot,
            build_id,
            project,
            platform,
        )
        try:

            def add_build(doc):
                """
                Update or create a "builds-ready" object
                """
                doc["type"] = "builds-ready"
                if "builds" not in doc:
                    doc["builds"] = []
                doc["builds"].append(
                    {
                        "slot": slot,
                        "project": project,
                        "platform": platform,
                        "build_id": build_id,
                    }
                )
                return doc

            self.dashboard.update(self.doc_id(), add_build)
        except Exception as x:
            self.log.warning("problems recording build: %s: %s", type(x).__name__, x)

    def accept(self, msg):
        """
        Implements the receiver side of the message protocol.
        """
        msg_type = msg.get("type", "")

        if msg_type == "ready.artifacts.build":
            self.builds_ready(msg["project"].name)


class NotifyLbTaskRun:
    """
    Notify lbtaskrun that a new build is ready to be published to CVMFS.
    """

    def __init__(self, script):
        self.slot = script.slot
        self.platform = script.platform
        self.log = logging.getLogger("NotifyLbTaskRun")

    def builds_ready(self, msg):
        """
        sends the message that builds are ready
        """
        try:
            if not os.path.exists(
                os.path.join(
                    os.environ.get(
                        "ARTIFACTS_DIR",
                        os.path.join("artifacts", str(self.slot.build_id)),
                    ),
                    "packs",
                    self.platform,
                    "{project}.{version}.{slot}.{build_id}.{platform}.zip".format(
                        project=msg["project"].name,
                        version=msg["project"].version,
                        slot=self.slot.name,
                        build_id=self.slot.build_id,
                        platform=self.platform,
                    ),
                )
            ):
                # we didn't produce a binary artifact, we must not try to install it on CVMFS
                # (it would cause an error in lbtaskrun)
                return
            token_fn = os.path.join(
                os.environ.get(
                    "PRIVATE_DIR", os.path.join(os.environ["HOME"], "private")
                ),
                "lbtaskrun_token_notify_nightly_built",
            )
            with open(token_fn) as fp:
                token = fp.read().strip()

            import requests

            r = requests.put(
                "https://lhcb-core-tasks.web.cern.ch/hooks/build-ready/ci/{}/{}/{}/{}/".format(
                    self.slot.name,
                    self.slot.build_id,
                    msg["project"].name,
                    self.platform,
                ),
                headers={"Authorization": f"Bearer {token}"},
            )
            r.raise_for_status()
        except Exception as e:
            self.log.exception("Failed to send build ready message to lbtaskweb")

    def accept(self, msg):
        """
        Implements the receiver side of the message protocol.
        """
        msg_type = msg.get("type", "")

        if msg_type == "ready.artifacts.build":
            self.builds_ready(msg)


class BaseScript(PlainScript):
    """
    Base class for LbNightlyToolsScripts
    """

    __usage__ = "%prog [options] <slot name or config file>"
    __version__ = ""

    def defineOpts(self):
        """
        Prepare the option parser.
        """
        addBasicOptions(self.parser)
        addBuildDirOptions(self.parser)
        addDeploymentOptions(self.parser)
        addDashboardOptions(self.parser)

    def _setupReceivers(self):
        """
        Prepare deployment destinations.
        """
        if hasattr(self.options, "rsync_dest") and self.options.rsync_dest:
            self.receivers.append(RsyncDestination(self.options.rsync_dest, self))
        if hasattr(self.options, "submit"):
            db_update = DashboardUpdate(self)
            if db_update.dashboard:

                def abort_check():
                    db_update.dashboard.assert_not_aborted(db_update.doc_name)

                self.assert_not_aborted = abort_check
            self.receivers.append(db_update)
            self.receivers.append(PeriodicTestMsg(self))
            self.receivers.append(NotifyLbTaskRun(self))

    def assert_not_aborted(self):
        pass

    def _setup(self, build_dir=None, json_type=None, make_dirs=True, summary_base=""):
        """
        Initialize variables.
        """
        # pylint: disable=W0201
        from os.path import join

        from LbNightlyTools.Utils import ensureDirs

        self.receivers = []
        self.tasks = TaskQueue()

        self.json_type = json_type

        opts = self.options
        if len(self.args) != 1:
            self.parser.error("wrong number of arguments")

        self.slot = findSlot(
            self.args[0],
            flavour=opts.flavour,
            server=opts.db_url,
            dbname=opts.db_name,
            raise_if_aborted=True,
        )

        from LbNightlyTools.Utils import setDayNamesEnv

        setDayNamesEnv()

        # FIXME: we need something better
        self.platform = os.environ.get("CMTCONFIG") or os.environ.get("BINARY_TAG")

        self.starttime = datetime.now()

        expandTokensInOptions(
            opts, ["build_id", "artifacts_dir", "rsync_dest"], slot=self.slot.name
        )

        self.build_dir = join(os.getcwd(), "build" if build_dir is None else build_dir)
        self.artifacts_dir = join(os.getcwd(), opts.artifacts_dir)

        self.summary_base = summary_base

        # ensure that we have the artifacts directory for the sources
        if make_dirs:
            ensureDirs([self.artifacts_dir, self.build_dir])
            if self.summary_base:
                ensureDirs([self._summaryDir()])

        if opts.slot_build_id is not None:
            self.slot.build_id = self.options.slot_build_id
        elif not self.slot.build_id:
            self.slot.build_id = int(os.environ.get("slot_build_id", 0))

        if opts.projects:
            proj_names = {proj.name.lower(): proj.name for proj in self.slot.projects}
            try:
                opts.projects = {
                    proj_names[p.strip().lower()] for p in opts.projects.split(",")
                }
            except KeyError as exc:
                self.parser.error(f'requested project not in slot: "{exc.args}"')
        else:
            opts.projects = None

        self._setupReceivers()

    def __del__(self):
        """
        Clean up.
        """
        if hasattr(self, "tasks"):
            self.tasks.join()

    def _summaryDir(self, *subdirs):
        """
        Return the path to the summary directory for a given project.

        If extra arguments are given, the output is equivalent to
        os.path.join(self._summaryDir(proj), level1, level2).
        """
        # note that os.path.join('', '') -> ''
        return os.path.join(
            self.artifacts_dir,
            self.options.summary_prefix,
            self.summary_base,
            self.platform,
            *[p.name if hasattr(p, "name") else p for p in subdirs],
        )

    def _buildDir(self, proj, *subdirs):
        """
        Return the path to the build directory for a given project.

        If extra arguments are given, the output is equivalent to
        os.path.join(self._buildDir(proj), level1, level2).
        """
        return os.path.join(self.build_dir, proj.baseDir, *subdirs)

    def send(self, msg, sync=False):
        """
        Send a message to the receivers.

        If the parameter sync is True, the call will block until the message is
        handled, otherwise the handling will be deferred.
        """
        if sync:
            for receiver in self.receivers:
                receiver.accept(msg)
        else:
            self.tasks.add(self.send, (msg, True))

    def dumpGitStatus(self, proj):
        from subprocess import Popen

        if os.path.isdir(self._buildDir(proj, ".git")):
            with open(self._summaryDir(proj, "git-status.txt"), "wb") as f:
                self.log.debug('running "git status" in %s', self._buildDir(proj))
                Popen(
                    ["git", "status", "--porcelain"], stdout=f, cwd=self._buildDir(proj)
                ).communicate()


def genPackageName(proj, platform, build_id=None, artifacts_dir=None):
    """
    Generate the source/binary tarball name for a project/package.

    >>> from LbNightlyTools.Configuration import Project, Package
    >>> genPackageName(Project('Gaudi', 'HEAD'),
    ...                'x86_64-slc6-gcc48-opt')
    'packs/x86_64-slc6-gcc48-opt/Gaudi.HEAD.x86_64-slc6-gcc48-opt.zip'
    >>> genPackageName(Package('Gen/DecFiles', 'HEAD'), 'src')
    'packs/src/Gen_DecFiles.head.src.zip'
    >>> genPackageName(Project('Gaudi', 'v25r0'),
    ...                'x86_64-slc6-gcc48-dbg',
    ...                build_id='dummy', artifacts_dir='artifacts')
    'artifacts/packs/x86_64-slc6-gcc48-dbg/Gaudi.v25r0.dummy.x86_64-slc6-gcc48-dbg.zip'
    """
    packname = [proj.name.replace("/", "_"), proj.version.replace("/", "_")]
    if build_id:
        packname.append(build_id)
    packname.append(platform)
    packname.append("zip")
    packname = ".".join(packname)
    packname = os.path.join("packs", platform, packname)
    if artifacts_dir:
        packname = os.path.join(artifacts_dir, packname)
    return packname

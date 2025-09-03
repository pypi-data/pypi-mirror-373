#!/usr/bin/env python
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
Generate a basic nightly builds configuration file from a list of projects and
versions.
"""
import codecs
import json
import os
import urllib.error
import urllib.parse
import urllib.request

import LbNightlyTools.CheckoutMethods
import LbNightlyTools.Configuration
from LbNightlyTools.Scripts.Common import PlainScript
from LbNightlyTools.Utils import Dashboard, JobParams

ERR_EXCEPT = ["distcc\\[", "::error::", "^ *Error *$"]
WARN_EXCEPT = [
    ".*/boost/.*",
    "^--->> genreflex: WARNING:.*",
    " note:",
    "distcc\\[",
    (
        "Warning\\:\\ The\\ tag\\ (use-distcc|no-pyzip|"
        "LCG\\_NIGHTLIES\\_BUILD|COVERITY|"
        "use\\-dbcompression)\\ is\\ not\\ used.*"
    ),
    ".*#CMT---.*Warning: Structuring style used.*",
    ".*/Boost/.*warning:.*",
    ".*/ROOT/.*warning:.*",
    (".*stl_algo.h:[0-9]+: warning: array subscript is above array " "bounds"),
    # CMake developer warning.
    # this is to ignore CMake (>=3.15) warning about "project(Project)"
    # missing in the top level CMakeLists.txt
    r"CMake Warning \(dev\) in CMakeLists\.txt\:",
    r"This warning is for project developers",
]

# FIXME: we need a better way to define the default platforms
DEFAULT_PLATFORMS = ""

# get the correct case for projects
try:
    from LbEnv import fixProjectCase

except ImportError:
    try:
        from LbConfiguration.Project import project_names as PROJECT_NAMES
    except ImportError:
        # if we cannot find the list of names, we use a minimal hardcoded list
        PROJECT_NAMES = [
            "LHCb",
            "DaVinci",
            "DecFilesTests",
            "MooreOnline",
            "LbScripts",
            "VanDerMeer",
            "LHCbDirac",
            "LHCbGrid",
        ]

    # convert the names to a a conversion dictionary
    PROJECT_NAMES = {name.lower(): name for name in PROJECT_NAMES}

    def fixProjectCase(name):
        """
        Convert a project name to it's canonical case.

        >>> fixProjectCase('GAUDI')
        'Gaudi'
        >>> fixProjectCase('davinci')
        'DaVinci'
        >>> fixProjectCase('uNkNoWn')
        'Unknown'
        """
        return PROJECT_NAMES.get(name.lower(), name.capitalize())


def toListOfPairs(s):
    """
    Convert a spaces-separated string to a list of pairs.
    Raise ValueError if the list length is not even.

    >>> toListOfPairs('a b c d e f')
    [('a', 'b'), ('c', 'd'), ('e', 'f')]
    """
    items = s.split()
    if len(items) % 2:
        raise ValueError("input must contain even number of entries")
    return list(zip(items[::2], items[1::2]))


def genConfig(
    slot="lhcb-release",
    build_id=0,
    projects=None,
    packages=None,
    platforms=None,
    build_tool="cmake",
):
    """
    Return the configuration dictionary.
    """
    config_projects = []
    added = []
    for proj, vers in projects or []:
        proj = fixProjectCase(proj)
        if proj in added:
            raise ValueError(
                f"project {proj} repeated: each project can " "appear only once"
            )
        project = {"name": proj, "version": vers, "checkout_opts": {"export": True}}
        # LCG might be in the list, but just as a hint
        if proj.lower() == "lcg":
            project["disabled"] = True

        added.append(proj)

        # look for a project-specific checkout method
        if hasattr(LbNightlyTools.CheckoutMethods, proj.lower()):
            project["checkout"] = proj.lower()

        if proj in ("Geant4",):
            project["with_shared"] = True

        config_projects.append(project)

    config_packages = []
    for pack, vers in packages or []:
        package = {"version": vers, "checkout_opts": {"export": True}}
        # the package name could by just the name or <container>:<name>
        if ":" not in pack:
            package["name"] = pack
        else:
            package["container"], package["name"] = pack.split(":", 1)
        if package not in config_packages:  # ignore duplicates
            config_packages.append(package)

    # prepare the configuration dictionary
    config = {
        "slot": slot,
        "build_id": build_id,
        "description": "Slot used for releasing projects.",
        "projects": config_projects,
        "packages": config_packages,
        "build_tool": build_tool.lower(),
        "no_patch": True,
        "with_version_dir": True,
        "error_exceptions": ERR_EXCEPT,
        "warning_exceptions": WARN_EXCEPT,
        "platforms": platforms or [],
        "cmake_cache": {
            "GAUDI_STRICT_VERSION_CHECK": True,
            "GAUDI_LEGACY_CMAKE_SUPPORT": True,
        },
    }

    return config


class ConfigGenerator(PlainScript):
    """
    Given a list of projects and versions, generate a basic configuration file.
    """

    __usage__ = "%prog [options] project version [project version...]"

    def defineOpts(self):
        """
        Options specific to this script.
        """
        self.parser.add_option(
            "-s", "--slot", help="name of the slot to add to the JSON data"
        )
        self.parser.add_option(
            "-b", "--build-id", help="build id to add to the JSON data"
        )
        self.parser.add_option(
            "-o",
            "--output",
            help='name of the output file [default "-", ' "i.e. standard output]",
        )
        self.parser.add_option(
            "--cmt",
            action="store_const",
            const="cmt",
            dest="build_tool",
            help="configure to use CMT for the build "
            '(equivalent to "--build-tool=cmt")',
        )
        self.parser.add_option(
            "--platforms",
            help="space or comma -separated list of "
            "platforms required [default: %default]",
        )
        self.parser.add_option(
            "--packages",
            help="space-separated list of data packages, " "with versions, to add",
        )
        self.parser.add_option(
            "-t",
            "--build-tool",
            action="store",
            help="which build tool to use " "(case insensitive) [default: %default]",
        )
        self.parser.set_defaults(
            slot="lhcb-release",
            build_id=0,
            output="-",
            platforms=DEFAULT_PLATFORMS,
            packages="",
            build_tool="cmake",
        )

    def genConfig(self):
        opts = self.options
        return genConfig(
            slot=opts.slot,
            build_id=opts.build_id,
            projects=toListOfPairs(" ".join(self.args)),
            packages=toListOfPairs(opts.packages),
            platforms=opts.platforms.replace(",", " ").split(),
            build_tool=opts.build_tool,
        )

    def main(self):
        """
        Script logic.
        """

        if len(self.args) % 2 != 0:
            self.parser.error(
                "wrong number of arguments: we need a list of "
                "projects and their versions"
            )

        try:
            # prepare the configuration dictionary
            config = self.genConfig()
        except ValueError as err:
            self.parser.error(str(err))

        if self.options.output != "-":
            LbNightlyTools.Configuration.save(self.options.output, config)
        else:
            print(LbNightlyTools.Configuration.configToString(config))

        return 0


class _ReleaseTriggerBase(PlainScript):
    """
    Base class for the release trigger script.
    """

    DEFAULT_BUILD_TOOL = "cmake"

    @property
    def dashboard(self):
        if not hasattr(self, "_dashboard"):
            self._dashboard = Dashboard(flavour="release")
        return self._dashboard

    def _gen_release_params(self, stack):
        projects_list = " ".join(" ".join(pv) for pv in stack.get("projects", []))
        packages_list = " ".join(" ".join(pv) for pv in stack.get("packages", []))
        platforms = " ".join(stack.get("platforms", []))
        build_tool = stack.get("build_tool", self.DEFAULT_BUILD_TOOL)

        if projects_list or packages_list:
            if projects_list:
                self.log.debug("projects: %s", projects_list)
            if packages_list:
                self.log.debug("packages: %s", packages_list)
            if platforms:
                self.log.debug("platforms: %s", platforms)
            self.log.debug("build_tool: %s", build_tool)

            data = JobParams(
                projects_list=projects_list,
                packages_list=packages_list,
                platforms=platforms,
                build_tool=build_tool,
            )
        else:
            self.log.error("invalid stack configuration")
            data = None
        return data

    def _gen_checkout_params(self):
        data = JobParams(
            slot="lhcb-release",
            flavour="release",
            slot_build_id=self.next_id(),
            trigger_url=os.environ.get("BUILD_URL"),
        )
        self.log.debug("slot_build_id: %d", data.slot_build_id)
        return data


class Starter(_ReleaseTriggerBase):
    """
    Generate a property file suitable to trigger a slot from the environment
    variables:
    - projects_list
    - packages_list
    - platforms
    - build_tool
    """

    __usage__ = "%prog"
    PARAM_FILE = "release-params.txt"

    def defineOpts(self):
        """
        Options specific to this script.
        """
        pass  # no special options

    def next_id(self):
        doc = self.dashboard.db.get("last_id", {"type": "last_id", "value": 0})
        doc["value"] = max(doc["value"], self.dashboard.lastBuildId("lhcb-release")) + 1
        self.dashboard.update("last_id", doc)
        return doc["value"]

    def main(self):
        """
        Script logic.
        """
        if self.args:
            self.parser.error("wrong number of arguments")
        # connect to the dashboard (to have a better debug output later on)
        self.dashboard

        # ensure that we will not trigger by mistake
        if os.path.exists(self.PARAM_FILE):
            os.remove(self.PARAM_FILE)
        # handle stack requested via the environment
        env = os.environ
        self.log.info("generating %s", self.PARAM_FILE)
        data = self._gen_checkout_params()
        key = f"{data.slot}.{data.slot_build_id}"
        self.log.info("create dashboard entry %s", self.dashboard.urlForKey(key))
        self.dashboard.db[key] = {
            "type": "slot-info",
            "slot": data.slot,
            "build_id": data.slot_build_id,
            "config": genConfig(
                slot=data.slot,
                build_id=data.slot_build_id,
                projects=toListOfPairs(env.get("projects_list", "")),
                packages=toListOfPairs(env.get("packages_list", "")),
                platforms=env.get("platforms", "").split(),
                build_tool=env.get("build_tool", self.DEFAULT_BUILD_TOOL),
            ),
        }
        with open(self.PARAM_FILE, "w") as params:
            params.write(str(data))

        return 0


class Poll(_ReleaseTriggerBase):
    """
    Poll a URL for the list of stacks not yet released and return those that
    need to be built.
    """

    __usage__ = "%prog [options] url"
    PARAM_FILE_TPL = "release-params-{0}.txt"

    def defineOpts(self):
        """
        Options specific to this script.
        """
        pass  # no special options

    # FIXME: I'd like to use @property, but it requires inheritance from 'object'
    def get_stacks(self):
        doc = self.dashboard.db.get("stacks")
        return doc["value"] if doc else []

    def set_stacks(self, value):
        self.dashboard.update("stacks", {"type": "stacks", "value": value})

    def main(self):
        """
        Script logic.
        """
        if len(self.args) != 1:
            self.parser.error("wrong number of arguments")

        # URL to poll
        url = self.args[0]

        # get the stacks triggered last time
        self.log.debug("load previous state")
        previous = self.get_stacks()
        self.log.debug("found %d stacks", len(previous))

        # retrieve the list of stacks to build
        self.log.debug("retrieving %s", url)
        stacks = json.loads(urllib.request.urlopen(url).read())
        # sort the list for stable behavior
        for stack in stacks:
            for k in stack:
                if hasattr(stack[k], "sort"):
                    stack[k].sort()
        stacks.sort()
        self.log.debug("found %d stacks", len(stacks))

        # ensure that we will not trigger by mistake
        self._clean_stacks_params()
        # generate one param file for each stack to be built
        for idx, stack in enumerate([s for s in stacks if s not in previous]):
            filename = self.PARAM_FILE_TPL.format(idx)
            self.log.info("generating %s", filename)
            data = self._gen_release_params(stack)
            if data:
                with open(filename, "w") as params:
                    params.write(str(data))

        # overwrite the last run data for the next poll
        if stacks != previous:
            self.log.debug("write new state")
            self.set_stacks(stacks)
        else:
            self.log.debug("no changes to the state")

        return 0

    def _clean_stacks_params(self):
        """
        Remove param files matching the produced file names.
        """
        self.log.debug("removing old param files")
        from glob import glob

        for f in glob(self.PARAM_FILE_TPL.format("*")):
            os.remove(f)


_manifest_template = """<?xml version='1.0' encoding='UTF-8'?>
<manifest>
  <project name="{project}" version="{version}" />
  <heptools>
    <version>{heptools}</version>
    <binary_tag>{platform}</binary_tag>
    <lcg_system>{system}</lcg_system>
  </heptools>{used_projects}{used_data_pkgs}
</manifest>
"""


def createManifestFile(project, version, platform, build_dir):
    """
    Generate a manifest.xml from the CMT configuration.
    """
    import logging
    import re
    import sys
    from os.path import abspath, dirname
    from subprocess import PIPE, Popen

    container_package = (project + "Sys") if project != "Gaudi" else "GaudiRelease"
    container_dir = os.path.join(build_dir, container_package, "cmt")
    env = {key: value for key, value in os.environ.items() if key not in ("PWD", "CWD")}
    # inject the (guessed) build root in the environment
    env["CMTPROJECTPATH"] = ":".join(
        [dirname(dirname(abspath(build_dir))), env.get("CMTPROJECTPATH", "")]
    )
    proc = Popen(
        ["cmt", "show", "projects"], cwd=build_dir, env=env, stdout=PIPE, stderr=PIPE
    )
    out, _err = proc.communicate()
    out = out.decode("utf-8", errors="replace")

    # no check because we must have a dependency on LCGCMT
    match = re.search(r"LCGCMT_([^ ]+)", out)
    if not match:
        logging.error(
            'problem with "cmt show projects":\n' "--- output ---\n%s\n--------------",
            out,
        )
        logging.info("CMTPROJECTPATH=%s", env["CMTPROJECTPATH"])
        sys.exit(1)
    heptools = match.group(1)

    projects = [
        '    <project name="{}" version="{}" />'.format(
            fixProjectCase(name), vers.split("_")[-1]
        )
        for name, vers in [
            x.split()[0:2] for x in out.splitlines() if re.match(r"^  [^ ]", x)
        ]
        if name not in ("DBASE", "PARAM", "LCGCMT")
    ]
    if projects:
        projects.insert(0, "\n  <used_projects>")
        projects.append("  </used_projects>")

    data_pkgs = []
    if "DBASE" in out or "PARAM" in out:
        proc = Popen(
            ["cmt", "show", "uses"],
            cwd=container_dir,
            env=env,
            stdout=PIPE,
            stderr=PIPE,
        )
        out, _err = proc.communicate()
        out = out.decode("utf-8", errors="replace").splitlines()
        data_pkgs = [
            x.replace(" ", ",").split(",")[1:4:2]
            for x in out
            if re.search(r"DBASE|PARAM", x)
        ]

        def findVersion(pkg):
            v = next(x.split()[3] for x in out if re.match(rf"^#.*{pkg}", x))
            if v == "v*":
                v = "*"
            return v

        data_pkgs = [
            '    <package name="{}" version="{}" />'.format(
                hat + "/" + name if hat else name, findVersion(name)
            )
            for name, hat in data_pkgs
        ]
        if data_pkgs:
            data_pkgs.insert(0, "\n  <used_data_pkgs>")
            data_pkgs.append("  </used_data_pkgs>")

    return _manifest_template.format(
        project=project,
        version=version,
        platform=platform,
        system=platform[: platform.rfind("-")],
        heptools=heptools,
        used_projects="\n".join(projects),
        used_data_pkgs="\n".join(data_pkgs),
    )

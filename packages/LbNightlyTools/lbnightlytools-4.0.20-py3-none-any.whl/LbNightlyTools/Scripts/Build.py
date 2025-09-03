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
Module containing the classes and functions used to build a
"Nightly Build Slot".

@author: Marco Clemencic <marco.clemencic@cern.ch>
"""

import codecs
import html
import logging
import os
import re
import shutil
import socket
import stat
from collections import defaultdict
from datetime import datetime
from os.path import join
from string import Template

from LbNightlyTools.Utils import coerce_str

try:
    from multiprocessing import cpu_count
except ImportError:
    cpu_count = lambda: 0

from LbNightlyTools.Configuration import DataProject, log_timing
from LbNightlyTools.HTMLUtils import XTerm2HTML
from LbNightlyTools.Scripts.CollectBuildLogs import Script as CBLScript
from LbNightlyTools.Scripts.Common import BaseScript, genPackageName
from LbNightlyTools.Utils import chdir, cpuinfo, ensureDirs, log_call, pack
from LbNightlyTools.Utils import tee_call as _tee_call
from LbNightlyTools.Utils import timeout_call as call
from LbNightlyTools.Utils import wipeDir, write_json

# no-op 'call' function for testing
# call = lambda *a,**k: None

__log__ = logging.getLogger(__name__)

LOAD_AVERAGE_SCALE = 1.2
GB_PER_BUILD_JOB = 1.5
HOSTNAME = os.environ.get("docker_hostname", socket.gethostname())
MAX_REPORTED_ISSUES = 100  # per severity


def listAllFiles(path, excl=None):
    """
    Return the list of all files in a directory and in its subdirectories.
    """
    if excl is None:
        excl = lambda _: False
    for root, dirs, files in os.walk(path):
        for f in files:
            if not excl(f):
                yield join(root, f)
        dirs[:] = [d for d in dirs if not excl(d)]


def unpackArtifacts(src, dest):
    """
    Helper function to unpack the artifacts in src to the build
    directory dest.
    """
    # FIXME: this can be done asynchronously
    if not os.path.isdir(src):
        __log__.debug("Ignore missing directory %s", src)
        return
    __log__.info("Unpacking artifacts from %s to %s", src, dest)
    for f in os.listdir(src) if os.path.isdir(src) else []:
        if f.endswith(".tar.bz2"):
            f = os.path.join(src, f)
            __log__.info("  unpacking %s to %s", f, dest)
            # do not overwrite existing sources when unpacking
            # (we must preserve user changes, anyway we have the
            # --clean option)
            call(
                ["tar", "-x", "--no-overwrite-dir", "--keep-old-files", "-f", f],
                cwd=dest,
            )
        elif f.endswith(".zip"):
            f = os.path.join(src, f)
            __log__.info("  unpacking %s to %s", f, dest)
            # do not overwrite existing sources when unpacking
            # (we must preserve user changes, anyway we have the
            # --clean option)
            call(["unzip", "-n", "-q", f], cwd=dest)


try:
    from LbEnv import which
except ImportError:

    def which(cmd):
        """
        Find the given command in the directories specified in the environment
        variable PATH.

        """
        if os.path.isfile(cmd):
            return os.path.abspath(cmd)
        for full_cmd in [
            os.path.join(path, cmd)
            for path in os.environ.get("PATH", "").split(os.pathsep)
        ]:
            if os.path.isfile(full_cmd):
                return full_cmd
        return None


DEFAULT_FILE_PERM = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
DEFAULT_DIR_PERM = (
    stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
)


def fix_permissions(path, file_perm=DEFAULT_FILE_PERM, dir_perm=DEFAULT_DIR_PERM):
    """
    Make sure all entries in a directory have required permissions.
    """
    for root, dirs, files in os.walk(path):
        for p in [os.path.join(root, p) for p in files]:
            os.chmod(p, file_perm)
        for p in [os.path.join(root, p) for p in dirs]:
            os.chmod(p, dir_perm)


class Script(BaseScript):
    """
    Script to build the projects in a slot configuration.
    """

    # unavoidable or fake warnings
    # pylint: disable=E1002,W0201
    def defineBuildOptions(self):
        """
        Add build-specific options to the parser.
        """
        from optparse import OptionGroup

        group = OptionGroup(self.parser, "Build Options")

        group.add_option(
            "-j",
            "--jobs",
            action="store",
            type="int",
            help="number of parallel jobs to use during the build "
            "(default: $LBN_BUILD_JOBS or the smallest "
            f"between total memory / {GB_PER_BUILD_JOB:g}GB and N of cores + 1)",
        )

        group.add_option(
            "-l",
            "--load-average",
            action="store",
            type="float",
            help="load average limit for parallel builds, use 0 "
            "to remove the limit (default: "
            f"$LBN_LOAD_AVERAGE or N of cores x {LOAD_AVERAGE_SCALE:g})",
        )

        group.add_option(
            "--ccache",
            action="store_true",
            dest="use_ccache",
            help="use ccache to speed up builds (default if "
            "the environment variable CCACHE_DIR is defined)",
        )

        group.add_option(
            "--no-ccache",
            action="store_false",
            dest="use_ccache",
            help="do not use ccache (default if "
            "the environment variable CCACHE_DIR is not defined)",
        )

        group.add_option(
            "--coverity",
            action="store_true",
            help="enable special Coverity static analysis on the "
            "build (Coverity commands must be on the PATH)",
        )

        group.add_option(
            "--coverity-commit",
            action="store_true",
            help="commit Coverity detected defects to the "
            "database (default if the Coverity analysis is "
            "run)",
        )

        group.add_option(
            "--no-coverity-commit",
            action="store_false",
            dest="coverity_commit",
            help="do not commit Coverity detected defects to the " "database",
        )

        self.parser.add_option_group(group)
        if "LBN_LOAD_AVERAGE" in os.environ:
            load_average = float(os.environ["LBN_LOAD_AVERAGE"])
        else:
            load_average = cpu_count() * LOAD_AVERAGE_SCALE

        if "LBN_BUILD_JOBS" in os.environ:
            jobs = int(os.environ["LBN_BUILD_JOBS"])
        else:
            # see http://stackoverflow.com/a/28161352
            sys_mem = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
            jobs = min(cpu_count() + 1, int(sys_mem / (GB_PER_BUILD_JOB * 1024**3)))

        self.parser.set_defaults(
            jobs=jobs,
            load_average=load_average,
            use_ccache="CCACHE_DIR" in os.environ,
            coverity=False,
            coverity_commit=True,
        )

    def defineOpts(self):
        """
        Prepare the option parser.
        """
        from LbNightlyTools.Scripts.Common import (
            addBasicOptions,
            addBuildDirOptions,
            addDashboardOptions,
            addDeploymentOptions,
        )

        addBasicOptions(self.parser)
        self.defineBuildOptions()
        addBuildDirOptions(self.parser)
        addDeploymentOptions(self.parser)
        addDashboardOptions(self.parser)

    def write(self, path, data):
        """
        Simple function to write some text (UTF-8) to a file.

        @param path: name of the file to write
        @param data: string to write
        """
        self.log.debug("writing %s", path)
        ensureDirs([os.path.dirname(path)])
        with codecs.open(path, "w", "utf-8") as f:
            f.write(data)

    def writeBin(self, path, data):
        """
        Simple function to write some binary data to a file.

        @param path: name of the file to write
        @param data: string to write
        """
        self.log.debug("writing (bin) %s", path)
        ensureDirs([os.path.dirname(path)])
        with open(path, "wb") as f:
            f.write(data)

    def _prepareBuildDir(self):
        """
        Prepare the build directory unpacking all the available artifacts
        tarballs, cleaning it before if requested.
        """
        if self.options.clean:
            wipeDir(self.build_dir)

        if not self.options.no_unpack:
            unpackArtifacts(
                os.path.join(self.artifacts_dir, "packs", "src"), self.build_dir
            )
            unpackArtifacts(
                os.path.join(self.artifacts_dir, "packs", self.platform), self.build_dir
            )
            unpackArtifacts(os.path.join(self.artifacts_dir, "ccache"), self.build_dir)

            if os.path.exists(os.path.join(self.artifacts_dir, "slot.patch")):
                self.log.warning(
                    "Applying patch file: {}".format(
                        os.path.join(self.artifacts_dir, "slot.patch")
                    )
                )
                log_call(
                    [
                        "patch",
                        "-p1",
                        "-i",
                        os.path.join(self.artifacts_dir, "slot.patch"),
                    ],
                    cwd=self.build_dir,
                )

        def dumpConfSummary():
            """Create special summary file used by SetupProject."""
            data = defaultdict(list)
            env = self.slot.environment()
            # collect the expanded values for  CMTPROJECTPATH and
            # CMAKE_PREFIX_PATH in the local environment
            for name in ("CMTPROJECTPATH", "CMAKE_PREFIX_PATH"):
                if name in env:
                    data[name] = os.path.expandvars(env[name]).split(":")
            if data:
                py_templ = Template(
                    """# -*- coding: utf-8 -*-
cmtProjectPathList = ${path}

# relocate
try:
    from os.path import dirname
    nightlyBuildRoot = ${build_root}
    newRoot = dirname(__file__)
    cmtProjectPathList = [s.replace(nightlyBuildRoot, newRoot)
                          for s in cmtProjectPathList]
except NameError:
    pass # __file__ gets defined only with LbScripts > v8r0\n"""
                )
                values = {
                    "path": repr(data["CMAKE_PREFIX_PATH"] + data["CMTPROJECTPATH"]),
                    "build_root": repr(self.build_dir),
                }
                summ = py_templ.substitute(values)
                self.write(self._summaryDir("confSummary.py"), summ)
                # FIXME: this is for backward compatibility with old lb-run
                self.write(os.path.join(self.artifacts_dir, "confSummary.py"), summ)

                cmake_templ = Template(
                    """set(NIGHTLY_BUILD_ROOT ${build_root})
set(CMAKE_PREFIX_PATH ${path} $${CMAKE_PREFIX_PATH})

string(REPLACE "$${NIGHTLY_BUILD_ROOT}" "$${CMAKE_CURRENT_LIST_DIR}"
       CMAKE_PREFIX_PATH "$${CMAKE_PREFIX_PATH}")\n"""
                )
                values = {
                    "path": " ".join(
                        data["CMAKE_PREFIX_PATH"] + data["CMTPROJECTPATH"]
                    ),
                    "build_root": self.build_dir,
                }
                cmake = cmake_templ.substitute(values)
                self.write(self._summaryDir("searchPath.cmake"), cmake)
                # FIXME: this is for backward compatibility with old lb-run
                self.write(os.path.join(self.artifacts_dir, "searchPath.cmake"), cmake)

        dumpConfSummary()

    def _sourcesLists(self, proj):
        """
        Return the list of files in the sources directories for a project.

        @param proj: project instance to scan
        """
        return sorted(listAllFiles(self._buildDir(proj), self._file_excl_rex.match))

    def _manifestRequired(self, proj, build_result):
        """
        Return True if the manifest.xml is required for the project.
        """
        return (
            self.slot.name == "lhcb-release"
            and not isinstance(proj, DataProject)
            and build_result.returncode == 0
        )

    def _ensureGeneratedManifest(self, proj, build_result):
        """
        Generate a manifest.xml if not present and required.
        """
        if not self._manifestRequired(proj, build_result):
            return

        manifest_file = self._buildDir(
            proj, "InstallArea", self.platform, "manifest.xml"
        )
        if not os.path.exists(manifest_file) and not os.path.exists(
            self._buildDir(proj, "manifest.xml")
        ):
            self.log.warning(
                "%s not generated by the build, " "we try to produce one", manifest_file
            )
            from LbNightlyTools.Scripts.Release import createManifestFile

            # ensure that the destination directory exists, in case
            # of builds that failed very badly
            if not os.path.exists(os.path.dirname(manifest_file)):
                os.makedirs(os.path.dirname(manifest_file))
            with open(manifest_file, "w") as manif:
                manif.write(
                    createManifestFile(
                        proj.name, proj.version, self.platform, proj.baseDir
                    )
                )

    def main(self):
        """
        Main function of the script.
        """
        if len(self.args) != 1:
            self.parser.error("wrong number of arguments")

        opts = self.options

        self._setup(json_type="build-result", summary_base="build")
        self._file_excl_rex = re.compile(
            rf"^(InstallArea)|(build(\.{self.platform})?)|({self.platform})|"
            r"(\.git)|(\.svn)|"
            rf"(\.{self.platform}\.d)|(Testing)|(.*\.pyc)|"
            r"(cov-out)$"
        )

        # See LBCORE-637 (we do not want ccache for releases)
        if opts.use_ccache and os.environ.get("flavour") == "release":
            self.log.warning("cannot use ccache for releases")
            opts.use_ccache = False

        # let's not overwrite what requested in the slot configuration
        if "CMAKE_USE_CCACHE" not in self.slot.cache_entries:
            self.slot.cache_entries["CMAKE_USE_CCACHE"] = opts.use_ccache
        if "GAUDI_DIAGNOSTICS_COLOR" not in self.slot.cache_entries:
            self.slot.cache_entries["GAUDI_DIAGNOSTICS_COLOR"] = "YES"
        # FIXME: workaround for typo in Gaudi cmake
        # see https://gitlab.cern.ch/gaudi/Gaudi/merge_requests/578
        if "GAUDI_DIAGNOTICS_COLOR" not in self.slot.cache_entries:
            self.slot.cache_entries["GAUDI_DIAGNOTICS_COLOR"] = "YES"

        # See LBCORE-637, LBCORE-953
        if (
            str(self.slot.build_tool) == "CMT" and opts.use_ccache and which("ccache")
        ):  # CMT requires ccache in the PATH
            for e in self.slot.env:
                if e.startswith("CMTEXTRATAGS="):
                    self.slot.env.append("CMTEXTRATAGS=${CMTEXTRATAGS}," "use-ccache")
                    break
            else:  # this must match the 'for'
                self.slot.env.append("CMTEXTRATAGS=use-ccache")

        if opts.submit and not opts.projects:
            # ensure that results for the current slot/build/platform are
            # not in the dashboard (useful in case of rebuild), but only
            # if we need to publish the results and it's not a partial build
            self.send({"type": "drop-build"})

        self.assert_not_aborted()
        self.send(
            {
                "type": "job-start",
                "host": HOSTNAME,
                "build_number": os.environ.get("BUILD_NUMBER", 0),
                "started": self.starttime.isoformat(),
            }
        )

        self._prepareBuildDir()

        make_cmd = (
            {
                "all": [
                    "cov-build",
                    "--dir",
                    "cov-out",
                    "--build-description",
                    f"{self.slot.name}-{self.slot.build_id}",
                    "make",
                ]
            }
            if opts.coverity
            else None
        )
        # FIXME: we should use the search path
        cov_strip = [
            "--strip-path",
            "/afs/cern.ch/sw/lcg/releases",
            "--strip-path",
            "/cvmfs/sft.cern.ch/lcg/releases",
            "--strip-path",
            "/cvmfs/lhcb.cern.ch/lib/lcg/releases",
        ]

        # add timing report and command echo
        def echo_call(*args, **kwargs):
            """call a command logging it"""
            self.log.debug("running %s", " ".join(args[0]))
            result = _tee_call(*args, **kwargs)
            __log__.debug("command exited with code %d", result[0])
            return result

        tee_call = log_timing(self.log)(echo_call)

        # record CPU details
        write_json(cpuinfo(), self._summaryDir("cpuinfo.json"))

        from subprocess import STDOUT

        with chdir(self.build_dir):
            sources = []

            def record_start(proj):
                """helper function to keep track of the start of the build"""
                self.assert_not_aborted()
                # keep a list of the files in the source directories before the build
                sources[:] = self._sourcesLists(proj)
                self.send({"project": proj.name, "started": datetime.now().isoformat()})

            if os.path.exists(os.path.join(self.artifacts_dir, "slot.patch")):
                self.log.warning("Applaying patch file")
                log_call(
                    [
                        "patch",
                        "-p1",
                        "-i",
                        os.path.join(self.artifacts_dir, "slot.patch"),
                    ]
                )

            for proj, result in self.slot.buildGen(
                projects=opts.projects,
                jobs=opts.jobs,
                max_load=opts.load_average,
                args=["-k"],
                make_cmd=make_cmd,
                stderr=STDOUT,
                # if not in release builds (i.e. no_patch = False) allow missing artifacts
                relaxed_install=not self.slot.no_patch,
                before=record_start,
            ):
                summary_dir = self._summaryDir(proj)
                ensureDirs([summary_dir])

                if result.returncode != 0:
                    self.log.warning(
                        "build of %s exited with code %d", proj, result.returncode
                    )
                    if opts.coverity:
                        self.log.warning("Coverity analysis skipped")

                self._ensureGeneratedManifest(proj, result)

                collect_retcode = 0
                if str(proj.build_tool) == "CMake":
                    stdout = coerce_str(result.stdout)
                    open(join(summary_dir, "build-raw.log"), "w").write(stdout)
                    loglines = stdout.splitlines(True)
                    starts = [
                        (line.split()[-2], idx)
                        for idx, line in enumerate(loglines)
                        if line.startswith("#### CMake ")
                    ]
                    end = len(loglines)
                    regions = {}
                    for key, start in starts[-1::-1]:
                        regions[key] = (start, end)
                        end = start
                    collect_retcode = CBLScript().run(
                        [
                            "--debug",
                            "--exclude",
                            ".*unsafe-install.*",
                            "--exclude",
                            ".*python.zip.*",
                            "--exclude",
                            ".*precompile-.*",
                            self._buildDir(proj, "build"),
                            join(summary_dir, "build.log"),
                        ]
                    )
                    with open(join(summary_dir, "build.log"), "a") as f:
                        for key in ["unsafe-install", "post-install", "install"]:
                            start, end = regions.get(key, (0, 0))
                            f.writelines(loglines[start:end])

                elif str(proj.build_tool) == "CMT":
                    collect_retcode = CBLScript().run(
                        [
                            "--debug",
                            "--cmt",
                            "--platform",
                            self.platform,
                            self._buildDir(proj),
                            join(summary_dir, "build.log"),
                        ]
                    )
                if collect_retcode or not os.path.exists(
                    join(summary_dir, "build.log")
                ):
                    with open(join(summary_dir, "build.log"), "w") as f:
                        f.write(proj.build_log)

                # build job specific infos for the report
                env = proj.environment()
                # mask possible secrets in the environment
                for k in env:
                    if re.search(r"pass(w(or)?d)?|secret|token|admin", k.lower()):
                        env[k] = "***"

                report = genBuildReport(
                    join(summary_dir, "build.log"),
                    join(summary_dir, "build_log"),
                    self._buildDir(proj),
                    self.build_dir,
                    exceptions={
                        "warning": self.slot.warning_exceptions,
                        "error": self.slot.error_exceptions,
                    },
                    extra_info={
                        "project": proj.name,
                        "version": proj.version,
                        "slot": self.slot.name,
                        "slot_build_id": self.slot.build_id,
                        "host": HOSTNAME,
                        "platform": self.platform,
                        "started": result.started.isoformat(),
                        "completed": result.completed.isoformat(),
                        "retcode": result.returncode,
                        "environment": env,
                    },
                )

                self.send(report)

                for f, d in (
                    ("sources.list", sources),
                    ("sources_built.list", self._sourcesLists(proj)),
                ):
                    self.write(self._summaryDir(proj, f), "\n".join(d) + "\n")

                if not isinstance(proj, DataProject) and not os.path.exists(
                    self._buildDir(proj, "manifest.xml")
                ):
                    inst_area = os.path.join(proj.baseDir, "InstallArea")
                    if os.path.exists(inst_area):
                        self.log.info("packing %s", inst_area)
                        pack(
                            [inst_area, os.path.join(proj.baseDir, "build")],
                            genPackageName(
                                proj,
                                self.platform,
                                build_id=self.options.build_id,
                                artifacts_dir=self.artifacts_dir,
                            ),
                            cwd=self.build_dir,
                            checksum="md5",
                            # preserve symlinks in build directory (except CMT)
                            # FIXME: this is only needed because we split build and tests
                            dereference=str(proj.build_tool) == "CMT",
                        )
                        if os.path.exists(os.path.join(proj.baseDir, "build")):
                            self.log.debug(
                                "removing %s", os.path.join(proj.baseDir, "build")
                            )
                            self.tasks.add(
                                shutil.rmtree,
                                (os.path.join(proj.baseDir, "build"),),
                                {"ignore_errors": True},
                            )
                    else:
                        self.log.warning(
                            "%s missing, binary package not " "produced", inst_area
                        )

                # FIXME
                if proj.with_shared:
                    shr_pack = genPackageName(
                        proj,
                        "shared",
                        build_id=self.options.build_id,
                        artifacts_dir=self.artifacts_dir,
                    )
                    to_pack_list = set(
                        open(join(summary_dir, "sources_built.list"))
                    ) - set(open(join(summary_dir, "sources.list")))
                    pack(
                        [
                            os.path.relpath(f.strip(), self.build_dir)
                            for f in sorted(to_pack_list)
                            if f.strip()
                        ],
                        shr_pack,
                        cwd=self.build_dir,
                        checksum="md5",
                    )

                self.dumpGitStatus(proj)

                echo_call(
                    ["zip", "-r", "-m", "-q", proj.name, proj.name],
                    cwd=os.path.dirname(summary_dir),
                )
                if opts.coverity:
                    # fix Permissions of artifacts in Coverity builds
                    fix_permissions(self.artifacts_dir)
                self.send(
                    {
                        "type": "artifacts.build",
                        "project": proj,
                        "platform": self.platform,
                        "path": self.artifacts_dir,
                    }
                )

                # add current project to the path strip settings
                cov_strip.append("--strip-path")
                cov_strip.append(os.path.dirname(os.path.abspath(proj.baseDir)))

                if opts.coverity and result.returncode == 0:
                    isDebug = self.log.level <= logging.DEBUG
                    wipeDir(join(proj.baseDir, "cov-out", "output"))
                    cov_result = tee_call(
                        [
                            "cov-analyze",
                            "--dir",
                            "cov-out",
                            "--all",
                            "--enable-constraint-fpp",
                            "--enable-fnptr",
                            "--enable-single-virtual",
                            "--force",
                        ]
                        + cov_strip,
                        cwd=proj.baseDir,
                        verbose=isDebug,
                    )
                    log_name = summary_dir + ".cov-analyze"
                    with open(log_name + ".log", "w") as f:
                        f.write(cov_result[1])
                    with open(log_name + ".err.log", "w") as f:
                        f.write(cov_result[2])

                    if not opts.coverity_commit:
                        continue
                    if cov_result[0] != 0:
                        self.log.warning(
                            "Coverity analysis for %s exited with "
                            "code %d, not committing",
                            proj,
                            cov_result[0],
                        )
                    elif "COVERITY_PASSPHRASE" in os.environ:
                        cov_result = tee_call(
                            [
                                "cov-commit-defects",
                                "--dir",
                                "cov-out",
                                "--host",
                                "lcgapp10.cern.ch",
                                "--port",
                                "8080",
                                "--user",
                                "admin",
                                "--stream",
                                f"LHCb-{proj.name}-Stream",
                            ],
                            cwd=proj.baseDir,
                        )
                        log_name = summary_dir + ".cov-commit-defects"
                        with open(log_name + ".log", "w") as f:
                            f.write(cov_result[1])
                        with open(log_name + ".err.log", "w") as f:
                            f.write(cov_result[2])
                    else:
                        self.log.warning(
                            "Coverity analysis cannot be committed" ": missing password"
                        )
                    for extra_file in [
                        join(
                            proj.baseDir,
                            "cov-out",
                            "output",
                            "cov-blame",
                            "cov-blame-errors.log",
                        )
                    ]:
                        if os.path.exists(extra_file):
                            ensureDirs([summary_dir + "-extra"])
                            shutil.copy(
                                extra_file,
                                join(
                                    summary_dir + "-extra", os.path.basename(extra_file)
                                ),
                            )

                    # fix Permissions of artifacts in Coverity builds
                    fix_permissions(self.artifacts_dir)
                    self.send(
                        {
                            "type": "artifacts.coverity",
                            "project": proj,
                            "platform": self.platform,
                            "path": self.artifacts_dir,
                        }
                    )

        # ensure we do not have pending tasks
        self.tasks.join()

        self.completetime = datetime.now()

        self.send(
            {"type": "job-end", "completed": self.completetime.isoformat()}, sync=True
        )

        self.log.info("build completed in %s", self.completetime - self.starttime)

        return 0


def genBuildReport(
    build_log,
    output_dir,
    proj_build_root=None,
    slot_build_root=None,
    exceptions=None,
    extra_info=None,
):
    from os.path import dirname, isdir, join
    from subprocess import CalledProcessError, check_output

    from LbNightlyTools.BuildLogScanner import (
        scan_build_log,
        split_build_log,
        strip_build_root,
    )
    from LbNightlyTools.HTMLUtils import (
        ANSI2HTML,
        ClassifyByLineNo,
        TableizeLine,
        WrapLine,
    )
    from LbNightlyTools.Scripts.CollectBuildLogs import (
        TABLE_HEAD,
        TABLE_TAIL,
        GitlabUrlFormat,
        IssueLinker,
        report_dict,
        write_report_index,
    )

    # collect git infos
    git_info = {}
    try:
        if proj_build_root and isdir(join(proj_build_root, ".git")):
            # we can only support projects with checkout recorded in
            # https://gitlab.cern.ch/lhcb-nightlies
            url = check_output(
                ["git", "config", "remote.lhcb-nightlies.url"], cwd=proj_build_root
            )
            git_info["name"] = os.path.basename(os.path.splitext(url)[0])

            git_info["commit"] = check_output(
                ["git", "rev-parse", "HEAD"], cwd=proj_build_root
            ).strip()
            git_info["files"] = set(
                check_output(
                    ["git", "ls-tree", "--name-only", "-r", "HEAD"], cwd=proj_build_root
                ).splitlines()
            )
            git_info["url"] = (
                "https://gitlab.cern.ch/lhcb-nightlies/" "{name}/blob/{commit}/"
            ).format(**git_info)
    except CalledProcessError:
        # could not extract git info
        git_info = {}

    # 1. strip build root and split log file in chunks (sections)
    input_data = codecs.open(build_log, "r", encoding="utf-8", errors="ignore")
    if proj_build_root:
        input_data = strip_build_root(proj_build_root, input_data)
    if slot_build_root:
        input_data = strip_build_root(slot_build_root, input_data)
    chunks = split_build_log(input_data)

    # 2. for each chunk look for errors or warnings using specific scanners
    #    and record the begin and end positions of each diagnostics
    reports = {chunk_id: scan_build_log(lines) for chunk_id, lines in chunks}

    # 3. generate report files
    ensureDirs([output_dir])
    ensureDirs(dirname(join(output_dir, chunk_id)) for chunk_id, _ in chunks)

    for chunk_id, chunk in chunks:
        classification = ClassifyByLineNo(
            (
                (issue.log_range[0] + 1, issue.log_range[1] + 1),
                {"warning": "alert-warning", "error": "alert-danger"}.get(
                    issue.severity, ""
                ),
            )
            for issue in reports[chunk_id]
        )
        actions = [
            lambda line: html.escape(line, quote=True),
            ANSI2HTML(),
            WrapLine("pre"),
            TableizeLine(
                line_id_prefix=chunk_id + "_",
                add_line_nos=True,
                row_class=classification,
            ),
        ]
        if git_info:
            actions.append(
                IssueLinker(
                    [
                        issue
                        for issue in reports[chunk_id]
                        if issue.source.name in git_info["files"]
                    ],
                    GitlabUrlFormat(git_info["url"]),
                )
            )

        def process(line):
            for action in actions:
                line = action(line)
            return line

        with codecs.open(join(output_dir, chunk_id + ".html"), "w", "utf-8") as h:
            h.write(TABLE_HEAD)
            h.writelines(process(line.rstrip()) + "\n" for line in chunk)
            h.write(TABLE_TAIL)

    jreport = report_dict(chunks, reports)
    # filter issues to remove excluded ones
    jreport["ignored_issues"] = {severity: {} for severity in jreport["issues"]}
    exceptions = {
        severity: [(exp, re.compile(exp)) for exp in exceptions[severity]]
        for severity in exceptions or {}
    }
    for severity in exceptions:
        # remove excluded issues from the report and count them per regexp
        for text, exp in exceptions[severity]:
            before = len(jreport["issues"][severity])
            jreport["issues"][severity] = [
                issue
                for issue in jreport["issues"][severity]
                if not exp.search(issue["desc"])
            ]
            after = len(jreport["issues"][severity])
            jreport["ignored_issues"][severity][text] = before - after

    jreport.update(
        {
            "warnings": len(jreport["issues"]["warning"]),
            "errors": len(jreport["issues"]["error"]),
            "coverity_messages": len(jreport["issues"]["coverity"]),
        }
    )

    # limit the number of presented issues (see LBCORE-1210)
    # it's done here because I want jreport[severity's] to contain the total
    for severity in jreport["issues"]:
        count = len(jreport["issues"][severity])
        if count > MAX_REPORTED_ISSUES:
            jreport["ignored_issues"][severity]["too many issues"] = (
                count - MAX_REPORTED_ISSUES
            )
            jreport["issues"][severity][MAX_REPORTED_ISSUES:] = []

    if extra_info:
        jreport.update(extra_info)

    write_json(jreport, join(output_dir, "report.json"))
    write_report_index(jreport, output_dir)
    return jreport


def run():
    return Script().run()

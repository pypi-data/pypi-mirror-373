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
Module containing the classes and functions used to test a
"Nightly Build Slot".

@author: Marco Clemencic <marco.clemencic@cern.ch>
"""

import codecs
import json
import os
import shutil
from datetime import datetime, timedelta
from subprocess import call

from LbDevTools import DATA_DIR
from LbPlatformUtils import requires

from LbNightlyTools.Scripts.Build import unpackArtifacts, wipeDir
from LbNightlyTools.Scripts.Common import BaseScript
from LbNightlyTools.Utils import Dashboard, JobParams, chdir
from LbNightlyTools.Utils import cpuinfo as get_cpuinfo
from LbNightlyTools.Utils import ensureDirs, write_json

CTEST_CONVERTER = os.path.join(DATA_DIR, "cmake", "CTestXML2HTML")
if not os.path.exists(CTEST_CONVERTER):
    CTEST_CONVERTER = None


def fixFailureCauses(summary_file):
    """
    Process summary.json file to fix missing failure cause.
    """
    import logging
    from os.path import exists, join

    dirname = os.path.dirname(summary_file)
    if not exists(summary_file):
        ensureDirs(dirname)
        with open(summary_file, "wb") as summary:
            summary.write(b"{}\n")
        return
    with open(summary_file, "rb+") as summary:
        touched = False
        try:
            results = json.load(summary)
        except:
            return  # ignore broken files
        for test in results:
            if (
                test.get("outcome", "PASS") != "PASS"
                and "Causes" in test.get("fields", [])
                and not test["cause"]
            ):
                test["cause"] = (
                    open(join(dirname, test["id"], "causes"))
                    .read()
                    .strip()
                    .replace("<pre>", "")
                    .replace("</pre>", "")
                )
                touched = True
        if touched:
            logging.info("adding failure causes in %s", summary_file)
            summary.seek(0)
            json.dump(results, summary, sort_keys=True, indent=4)
            summary.truncate()


class Script(BaseScript):
    """
    Script to test the projects described in a slot configuration.
    """

    # unavoidable or fake warnings
    # pylint: disable=E1002,W0201
    def defineTestOptions(self):
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
            "(default: $LBN_BUILD_JOBS or 1)",
        )

        self.parser.add_option_group(group)
        self.parser.set_defaults(jobs=int(os.environ.get("LBN_BUILD_JOBS", "1")))

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
        self.defineTestOptions()
        addBuildDirOptions(self.parser)
        addDeploymentOptions(self.parser)
        addDashboardOptions(self.parser)

    def _copy_build_artifacts(
        self, proj, target_dir, include, root=None, exclude_dirs=None
    ):
        """
        Find all files matching the 'include' regexp in the project directory
        and copy them to 'target_dir' in the artifacts directory.
        """
        import re

        if isinstance(include, str):
            include = re.compile(include)
        if isinstance(exclude_dirs, str):
            exclude_dirs = re.compile(exclude_dirs)

        self.log.debug("looking for files matching /%s/", include.pattern)
        from os.path import dirname, exists, join, relpath
        from zipfile import ZIP_DEFLATED, ZipFile

        proj_root = root or self._buildDir(proj)
        zip_name = self._summaryDir(target_dir, proj) + ".zip"

        def all_requested_files():
            """get all files in the project directory matching the filter"""
            for root, dirs, files in os.walk(proj_root):
                if exclude_dirs:
                    dirs[:] = [d for d in dirs if not exclude_dirs.match(d)]
                for f in files:
                    if include.match(f):
                        yield join(root, f)

        # FIXME: it should be better to use a temporary file
        ensureDirs(dirname(zip_name))
        zip_empty = True
        with ZipFile(zip_name, mode="w", compression=ZIP_DEFLATED) as dest_zip:
            for src in all_requested_files():
                try:
                    dest_zip.write(src, relpath(src, proj_root))
                except OSError:
                    # ignore failures in the copy (not fatal)
                    pass
            zip_empty = len(dest_zip.infolist()) == 0
        if zip_empty and exists(zip_name):
            os.remove(zip_name)

    def copy_new_refs(self, proj):
        return self._copy_build_artifacts(
            proj, "newrefs", r".*\.new$", exclude_dirs=r"^build$"
        )

    def copy_ctest_xml(self, proj):
        return self._copy_build_artifacts(
            proj, "cdash", r".*Test\.xml$", self._buildDir(proj, "build")
        )

    def main(self):
        """
        Script main logic.
        """

        self._setup(json_type="tests-result", summary_base="tests")

        opts = self.options

        # prepare build directory
        if opts.clean:
            wipeDir(self.build_dir)
        if not opts.no_unpack:
            unpackArtifacts(
                os.path.join(self.artifacts_dir, "packs", "src"), self.build_dir
            )
            unpackArtifacts(
                os.path.join(self.artifacts_dir, "packs", self.platform), self.build_dir
            )

        cpuinfo = get_cpuinfo()
        # run tests
        with chdir(self.build_dir):

            def before(proj):
                """callback used before testing a project"""
                self.assert_not_aborted()
                self.send({"project": proj.name, "started": datetime.now().isoformat()})
                if not os.path.exists(self._summaryDir(proj)):
                    os.makedirs(self._summaryDir(proj))
                write_json(cpuinfo, self._summaryDir(proj, "cpuinfo.json"))

            for proj, _ in self.slot.testGen(
                projects=opts.projects, before=before, jobs=opts.jobs
            ):
                html_src = self._buildDir(proj, "build", "html")
                # Always use the most recent CTEST_CONVERTER, if available
                # and we are in a CMake project
                if os.path.exists(self._buildDir(proj, "build", "Testing")):
                    if CTEST_CONVERTER:
                        if os.path.exists(html_src):
                            shutil.rmtree(html_src)
                        call([CTEST_CONVERTER], cwd=self._buildDir(proj, "build"))
                summary_json = os.path.join(html_src, "summary.json")
                fixFailureCauses(summary_json)

                # update annotations with cpuinfo summary
                try:
                    annotations_json = os.path.join(html_src, "annotations.json")
                    with codecs.open(annotations_json, "rb", "utf-8") as ann:
                        annotations = json.load(ann)

                    if "cpuinfo" not in annotations:
                        annotations["cpuinfo"] = [
                            f"ncpus: {len(cpuinfo)}",
                            "model name: {}".format(cpuinfo[0]["model name"]),
                            "flags: {}".format(" ".join(cpuinfo[0]["flags"])),
                        ]
                        write_json(annotations, annotations_json)
                except Exception as x:  # ignore errors reading summary file
                    self.log.warning("failed to update annotations.json: %s", x)

                self.dumpGitStatus(proj)

                try:
                    results = json.load(codecs.open(summary_json, "rb", "utf-8"))
                except:  # ignore errors reading summary file
                    results = []

                html_dst = self._summaryDir(proj, "results")
                if os.path.exists(html_dst):
                    shutil.rmtree(html_dst)
                if os.path.exists(html_src):
                    shutil.copytree(html_src, html_dst)

                self.copy_new_refs(proj)
                self.copy_ctest_xml(proj)

                self.log.debug("compressing artifacts")
                call(
                    ["zip", "-r", "-m", "-q", proj.name, proj.name],
                    cwd=self._summaryDir(),
                )
                self.send(
                    {
                        "project": proj.name,
                        "completed": datetime.now().isoformat(),
                        "results": results,
                    }
                )
                self.send(
                    {"type": "artifacts", "project": proj, "path": self.artifacts_dir}
                )

        # ensure we do not have pending tasks
        self.tasks.join()

        return 0


class Poll(BaseScript):
    # number of tests to trigger per iteration
    BATCH_SIZE = int(os.environ.get("TESTS_BATCH_SIZE") or "20")
    FILENAME_TPL = "test-{slot}-{build_id}-{project}-{platform}.txt"

    def main(self):
        """
        Main logic of the script.
        """
        d = Dashboard(flavour=self.options.flavour)

        # builds older than this are considered too old to care about
        expiration_time = str(datetime.now() - timedelta(hours=18))

        def test_id(entry):
            try:
                return "{slot}.{build_id}.{platform}.{project}".format(**entry)
            except KeyError:
                return None

        ready_builds = d.db.get("ready-builds", {"entries": []})
        entries = list(ready_builds["entries"])
        entries.sort(key=lambda e: e.get("time", "0000-00-00 00:00:00"), reverse=True)
        triggered = []
        to_drop = []
        used_ids = set()
        for entry in entries:
            # do not run test if disabled
            do_not_trigger = entry.get("no_test") or entry["slot"] == "lhcb-coverity"
            if entry.get("time", expiration_time) <= expiration_time:
                to_drop.append(entry)
                self.log.warning("expired entry: %s", entry)
            elif do_not_trigger:
                # no need to keep entries that do not need to be tested
                to_drop.append(entry)
            elif test_id(entry) in used_ids:
                self.log.warning("duplicated entry: %s", entry)
                to_drop.append(entry)
            else:
                self.log.debug("triggering %s", entry)
                with open(self.FILENAME_TPL.format(**entry), "w") as params:
                    jp = JobParams(
                        slot=entry["slot"],
                        slot_build_id=entry["build_id"],
                        project=entry["project"],
                        platform=entry["platform"],
                        os_label=entry.get("os_label", entry["platform"].split("-")[1]),
                        flavour=self.options.flavour,
                    )
                    for k, v in entry.get("scripts", {}).items():
                        if v:
                            setattr(jp, f"scripts_{k}", v)
                    for k, v in entry.get("venv", {}).items():
                        if v:
                            setattr(jp, k, v)
                    label = "-tests"
                    arch_label = requires(jp.platform).split("-")[0] + label
                    # FIXME: until we have new labels on all hosts we need something special
                    #        for x86_64 and avx2
                    if "avx2" in jp.platform:
                        arch_label = "avx2" + label  # should become 'broadwell' + label
                    else:
                        arch_label = arch_label.replace("x86_64-", "nightly-").replace(
                            "nehalem-", "nightly-"
                        )
                    jp.tests_node = arch_label
                    params.write(str(jp))
                    params.write("\n")
                triggered.append(entry)
                used_ids.add(test_id(entry))
                if len(triggered) == self.BATCH_SIZE:
                    break
        to_drop.extend(triggered)
        # drop also all entries that duplicate a test just triggered
        for entry in entries:
            if entry not in to_drop and test_id(entry) in used_ids:
                self.log.warning("duplicated entry: %s", entry)
                to_drop.append(entry)

        if self.options.submit:

            def strip_removed_entries(d):
                """callback to update the dashboard document"""
                if "entries" not in d:
                    d["entries"] = []
                d["entries"] = [entry for entry in d["entries"] if entry not in to_drop]
                return d

            d.update("ready-builds", strip_removed_entries)
        self.log.info(
            "triggered %d tests, %d pending",
            len(triggered),
            len(entries) - len(to_drop),
        )


def run():
    return Script().run()

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
Module containing the classes and functions used to checkout a set of projects,
fixing their dependencies to produce a consistent set.
"""
__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

import codecs
import html
import json
import logging
import os
import re
import shutil
from datetime import date, datetime
from itertools import chain
from os.path import join
from subprocess import call

from LbNightlyTools.Configuration import DataProject
from LbNightlyTools.HTMLUtils import AddGitlabLinks, XTerm2HTML
from LbNightlyTools.Scripts.Common import BaseScript, genPackageName
from LbNightlyTools.Utils import chdir, ensureDirs, pack

__log__ = logging.getLogger(__name__)


class PathPrefixRemover:
    """
    Callable that remove "path" prefix from a text
    """

    def __init__(self, path):
        path = path.rstrip("/")
        self._pattern = re.compile(re.escape(path) + r"/?\b")

    def __call__(self, text):
        "remove prefix from text"
        return self._pattern.sub("", text)


def highlightCmdLines(text):
    """
    hightlight command lines in checkout log
    """
    return re.sub(
        r"^(\([^)]*\)\$.*)$",
        r'<span class="console-cmd">\1</span>',
        text,
        flags=re.MULTILINE,
    )


# Special `.htaccess` configurationt to allow old entry points to work with
# new layout
HTACCESS_DATA = r"""RewriteEngine On
# this is a clever trick to avoid RewriteBase
# see http://stackoverflow.com/a/21063276
RewriteCond "%{REQUEST_URI}::$1" "^(.*?/)(.*)::\2$"
RewriteRule "^(.*)$" "-" [E=BASE:%1]
# Helper to list the content of a zip file
RewriteCond "%{DOCUMENT_ROOT}/%{REQUEST_URI}" !-f
RewriteRule "^(.+)/.list" "%{ENV:BASE}listzip.php?zip=$1.zip" [PT,B,L]
# Map old entry points to new ones
# - checkout artifacts
RewriteRule "checkout_job_url.txt" "%{ENV:BASE}checkout/job_url.txt" [R,L]
RewriteRule "^(.*)\.checkout\.log(.*)" "%{ENV:BASE}checkout/$1.log$2" [R,L]
# - build artifacts
RewriteRule "^summaries\.([^/]*)/(.*/build.*)" "%{ENV:BASE}build/$1/$2" [R,L]
RewriteRule "^cpuinfo\.(.*)\.json" "%{ENV:BASE}build/$1/cpuinfo.json" [R,L]
RewriteRule "^summaries\.([^/]*)/RPMs_report.json" "%{ENV:BASE}rpms/build/$1/RPMs_report.json" [R,L]
# - test artifacts
RewriteRule "^summaries\.([^/]*)/([^/]*)/html/(.*)" "%{ENV:BASE}tests/$1/$2/results/$3" [R,L]
# Extract artifacts from specific zip files
RewriteCond "%{DOCUMENT_ROOT}/%{REQUEST_URI}" !-f
RewriteRule "^(build|tests)/([^/]+)/([^/]+)/(.+)" "%{ENV:BASE}extract.php?zip=$1/$2/$3.zip&path=$3/$4" [PT,B,L]
RewriteCond "%{DOCUMENT_ROOT}/%{REQUEST_URI}" !-f
RewriteRule "^checkout/(.+)" "%{ENV:BASE}extract.php?zip=checkout.zip&path=checkout/$1" [PT,B,L]
"""


class Script(BaseScript):
    """
    Script to checkout a consistent set of projects as described in a
    configuration file.

    The configuration file must be in JSON format containing an object with the
    attribute 'projects', a list of objects with defining the projects to be
    checked out.

    For example::
        {"projects": [{"name": "Gaudi",
                       "version": "v23r5",
                       "checkout": "specialCheckoutFunction"},
                      {"name": "LHCb",
                       "version": "v32r5",
                       "overrides": {"GaudiObjDesc": "HEAD",
                                     "GaudiPython": "v12r4",
                                     "Online/RootCnv": null}}]}
    """

    def defineOpts(self):
        """User options -- has to be overridden"""
        from LbNightlyTools.Scripts.Common import (
            addBasicOptions,
            addDashboardOptions,
            addDeploymentOptions,
        )

        addBasicOptions(self.parser)
        addDashboardOptions(self.parser)
        addDeploymentOptions(self.parser)

        self.parser.add_option(
            "--ignore-checkout-errors",
            action="store_true",
            dest="ignore_checkout_errors",
            help="continue to checkout if there is a " "failure (default)",
        )
        self.parser.add_option(
            "--no-ignore-checkout-errors",
            action="store_false",
            dest="ignore_checkout_errors",
            help="stop the checkout if there is a failure",
        )
        self.parser.set_defaults(ignore_checkout_errors=True)

    def packname(self, element):
        """
        Return the filename of the archive (package) of the given project.
        """
        return genPackageName(
            element,
            "src",
            build_id=self.options.build_id,
            artifacts_dir=self.artifacts_dir,
        )

    def main(self):
        """Main logic of the script"""
        self._setup(build_dir=join("tmp", "checkout"), json_type="slot-config")

        opts = self.options
        slot = self.slot

        # prepare special environment, if needed
        os.environ.update(slot.environment())

        # Prepare JSON doc for the database
        cfg = slot.toDict()
        cfg["date"] = os.environ.get("DATE", date.today().isoformat())
        cfg["started"] = self.starttime.isoformat()
        platforms = os.environ.get("platforms", "").strip().split()
        if platforms:
            cfg["platforms"] = platforms
        cfg["trigger_url"] = os.environ.get("trigger_url")

        # publish the configuration before the checkout
        self.send(cfg)

        # prepare artifacts directory layout
        ensureDirs(
            os.path.join(self.artifacts_dir, d) for d in ("packs/src", "checkout")
        )
        if "BUILD_URL" in os.environ:
            with open(
                os.path.join(self.artifacts_dir, "checkout", "job_url.txt"), "w"
            ) as f:
                f.write(os.environ["BUILD_URL"])
                f.write("\n")

        script = self

        class CheckoutContext:
            def __init__(self, project):
                script.assert_not_aborted()
                self._msg = {"project": project.name}
                self.result = {}

            def __enter__(self):
                self.send(started=datetime.now().isoformat())
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                if exc_type:
                    if "error" not in self.result:
                        self.result["error"] = []
                    self.result["error"].append(f"{exc_type.__name__}: {exc_value}")
                self.send(completed=datetime.now().isoformat(), **self.result)

            def send(self, **kwargs):
                self._msg.update(kwargs)
                for key_to_drop in ("stdout", "stderr"):
                    if key_to_drop in self._msg:
                        del self._msg[key_to_drop]
                script.send(dict(self._msg))

        with chdir(self.build_dir):
            slot.checkout(
                projects=opts.projects,
                ignore_errors=opts.ignore_checkout_errors,
                context=CheckoutContext,
            )

            with open(join(self.artifacts_dir, "slot.patch"), "w") as patchfile:
                if not slot.no_patch:
                    slot.patch(patchfile, dryrun=True)
                else:
                    self.log.info("not patching the sources")

            # generate explicit dependencies
            # - map position in the list with project name
            proj_idx = {p["name"]: i for i, p in enumerate(cfg["projects"])}
            # - extract dependencies and update the configuration dict
            # - make sure platform independent projects are correctly flagged
            # - make sure lcg-toolchains (if present) is in all dependencies
            dependencies = slot.dependencies()
            for projname, deps in dependencies.items():
                projdict = cfg["projects"][proj_idx[projname]]
                projdict["dependencies"] = deps
                if (
                    projname != "lcg-toolchains"
                    and "lcg-toolchains" in slot.projects
                    and "lcg-toolchains" not in deps
                ):
                    projdict["dependencies"].append("lcg-toolchains")
                if slot.projects[projname].platform_independent:
                    projdict["platform_independent"] = True
            # disable non interesting projects (only in "-mr" slots)
            if (
                "ci_test" in slot.metadata
                and slot.metadata["ci_test"].get("is_test")
                and slot.metadata["ci_test"].get("requested_projects")
            ):
                from networkx.algorithms.dag import ancestors, descendants

                deps = slot.dependencyGraph()
                # - we have to build the projects explicitly listed
                #   (excluding data packages)
                needed = set(slot.metadata["ci_test"]["requested_projects"]) & set(deps)
                # - plus all projects that use the listed ones (if requested)
                if slot.metadata["ci_test"].get("with_downstream", True):
                    needed.update(
                        list(chain.from_iterable(descendants(deps, p) for p in needed))
                    )
                # - test projects that changed or depend on those that changed
                need_testing = set(needed)
                # - and all projects that are needed to build those we need
                needed.update(
                    list(chain.from_iterable(ancestors(deps, p) for p in needed))
                )
                # - disable everything else
                #   (making sure we do not enable something already disabled)
                for p in cfg["projects"]:
                    if not p["disabled"]:
                        n = p["name"]
                        getattr(slot, n).disabled = p["disabled"] = n not in needed
                        getattr(slot, n).no_test = p["no_test"] = n not in need_testing

                __log__.debug("projects to build: %s", needed)
                __log__.debug("projects to test: %s", need_testing)

        # write the checkout log of projects to dedicated files
        for project in slot.activeProjects:
            if hasattr(project, "checkout_log"):
                __log__.debug("writing checkout log for %s", project)
                co_logfile = join(
                    self.artifacts_dir, "checkout", ".".join((project.name, "log"))
                )
                with codecs.open(co_logfile, "w", "utf-8") as co_log:
                    co_log.write(project.checkout_log)
                with codecs.open(co_logfile + ".html", "w", "utf-8") as co_log:
                    html_filters = [
                        AddGitlabLinks(),
                        PathPrefixRemover(self.build_dir),
                        highlightCmdLines,
                    ]
                    conv = XTerm2HTML(
                        show_line_no=True,
                        is_escaped=True,
                        plugins_function=html_filters,
                    )
                    co_log.write(conv.head(title=os.path.basename(co_logfile)))
                    log = html.escape(project.checkout_log, quote=True)
                    if not isinstance(log, str):
                        log = log.decode("utf-8", errors="replace")
                    co_log.write(conv.process(log))
                    co_log.write(conv.tail())

        def containers():
            """
            Generator for the container projects in the slot.
            """
            for cont in slot.projects:
                if isinstance(cont, DataProject):
                    yield cont

        packages = list(chain.from_iterable(cont.packages for cont in containers()))

        for element in chain(slot.activeProjects, packages):
            # ignore missing directories
            # (the project may not have been checked out)
            if not os.path.exists(join(self.build_dir, element.baseDir)):
                self.log.warning("no sources for %s, skip packing", element)
                continue
            if isinstance(element, DataProject):
                continue  # ignore DataProjects, because we pack packages

            self.log.info("packing %s %s...", element.name, element.version)

            pack(
                [element.baseDir],
                self.packname(element),
                cwd=self.build_dir,
                checksum="md5",
            )
        for container in containers():
            container = container.name
            self.log.info("packing %s (links)...", container)
            contname = [container]
            if self.options.build_id:
                contname.append(self.options.build_id)
            contname.append("src.zip")
            pack(
                [container],
                join(self.artifacts_dir, "packs", "src", ".".join(contname)),
                cwd=self.build_dir,
                checksum="md5",
                dereference=False,
                exclude=[p.baseDir for p in packages],
            )

        donetime = datetime.now()
        cfg["completed"] = donetime.isoformat()

        # Save a copy as metadata for tools like lbn-install
        with codecs.open(
            join(self.artifacts_dir, "slot-config.json"), "w", "utf-8"
        ) as config_dump:
            data = {"slot": slot.name, "build_id": slot.build_id, "type": "slot-config"}
            data.update(cfg)
            json.dump(data, config_dump, indent=2)

        # Allow old entry points to work with new layout
        with codecs.open(
            join(self.artifacts_dir, ".htaccess"), "w", "utf-8"
        ) as htaccess_file:
            htaccess_file.write(HTACCESS_DATA)
        for helper in ("extract.php", "listzip.php"):
            shutil.copy(
                join(os.path.dirname(__file__), helper),
                join(self.artifacts_dir, helper),
            )

        # publish the updated configuration JSON
        self.send(cfg)

        self.log.debug("compressing artifacts")
        call(["zip", "-r", "-m", "-q", "checkout", "checkout"], cwd=self.artifacts_dir)
        self.send({"type": "artifacts", "path": self.artifacts_dir}, sync=True)

        # ensure we do not have pending tasks
        self.tasks.join()

        self.log.info(
            "sources ready for build (time taken: %s).", donetime - self.starttime
        )

        return 0


def run():
    return Script().run()

###############################################################################
# (c) Copyright 2013-2020 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
def ansi2html():
    """
    Script to convert a console output to html.
    """
    import os
    from optparse import OptionParser

    from LbNightlyTools.HTMLUtils import convertFile

    parser = OptionParser(usage="%prog [options] <input> <output>")

    try:
        opts, (input, output) = parser.parse_args()
    except ValueError:
        parser.error("wrong number of arguments")

    return convertFile(input, output)


def build_log_to_html():
    """
    Collect the build logs produced by lbn-wrapcmd and write the content grouped by
    subdir and target.
    """
    from LbNightlyTools.Scripts.CollectBuildLogs import LogToHTML as Script

    return Script().run()


def check_preconditions():
    from LbNightlyTools.CheckSlotPreconditions import Script

    return Script().run()


def collect_build_logs():
    """
    Collect the build logs produced by lbn-wrapcmd and write the content grouped by
    subdir and target.
    """
    from LbNightlyTools.Scripts.CollectBuildLogs import Script

    return Script().run()


def enabled_slots():
    from LbNightlyTools.Scripts.EnabledSlots import Script

    return Script().run()


def generate_compatspec():
    from LbRPMTools.LHCbCompatSpecBuilder import Script

    return Script().run()


def generate_do0spec():
    #
    # Little tool to generate -do0 RPM spec while we have a problem in the RPM generation.
    #
    # To find the list of LCG_XX_[...]dbg rpms from the LCG repo for e.g. LCG_79 do:
    # for f in  /afs/cern.ch/sw/lcg/external/rpms/lcg/LCG_79_*; do basename $f \
    # | sed -e 's/-79.noarch.rpm//' | sed -e 's/1.0.0//' | grep dbg; done
    #
    # You have have a lits of entries like: LCG_79_yoda_1.3.1_x86_64_slc6_gcc49_dbg
    # N.b. the RPM version ahs been removed !
    #
    # On each of them run:
    # lbn-generate-do0spec <name> && rpmbuild -bb tmp.spec

    import logging
    import sys

    # First checking args
    if len(sys.argv) == 1:
        logging.error("Please specify RPM name")
        sys.exit(2)

    rpmname = sys.argv[1]

    if rpmname.find("dbg") == -1:
        logging.error("RPM is not in dbg config, cannot create meta for do0 version")
        sys.exit(2)

    do0name = rpmname.replace("dbg", "do0")
    logging.warning(f"Generating tmp.spec for {do0name} depending on {rpmname}")

    # Now generating the spec
    from subprocess import call

    call(["lbn-generate-metaspec", "-o", "tmp.spec", do0name, "1.0.0", rpmname])


def generate_extspec():
    from LbRPMTools.LHCbExternalsSpecBuilder import Script

    return Script().run()


def generate_genericspec():
    from LbRPMTools.LHCbGenericSpecBuilder import GenericScript

    return GenericScript().run()


def generate_lbscriptsspec():
    from LbRPMTools.LHCbLbScriptsSpecBuilder import Script

    return Script().run()


def generate_metaspec():
    from LbRPMTools.LHCbMetaSpecBuilder import MetaScript

    return MetaScript().run()


def generate_spec():
    from LbRPMTools.LHCbRPMSpecBuilder import Script

    return Script().run()


def gen_release_config():
    from LbNightlyTools.Scripts.Release import ConfigGenerator as Script

    return Script().run()


def index():
    from LbNightlyTools.Scripts.Index import Script

    return Script().run()


def install():
    from LbNightlyTools.Scripts.Install import Script

    return Script().run()


def list_platforms():
    """
    Simple script to extract the list of requested platforms from the slot
    configuration file.
    """
    __author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

    import os
    import sys

    from LbNightlyTools.Configuration import findSlot

    usage = f"Usage: {os.path.basename(sys.argv[0])} configuration_file"

    if "-h" in sys.argv or "--help" in sys.argv:
        print(usage)
        sys.exit(0)

    if len(sys.argv) != 2:
        print(usage, file=sys.stderr)
        sys.exit(1)

    print(" ".join(findSlot(sys.argv[1]).platforms))


def preconditions():
    from LbNightlyTools.Scripts.Preconditions import Script

    return Script().run()


def release_poll():
    from LbNightlyTools.Scripts.Release import Poll as Script

    return Script().run()


def release_trigger():
    from LbNightlyTools.Scripts.Release import Starter as Script

    return Script().run()


def reschedule_tests():
    """
    Query the results database to find missing tests and produce the
    expected_builds.json file needed to re-schedule them.
    """
    import json
    import time
    from datetime import date

    # Parse command line
    from optparse import OptionParser

    from LbNightlyTools import Dashboard
    from LbNightlyTools.Scripts.Common import addDashboardOptions

    parser = OptionParser(description=__doc__)

    parser.add_option(
        "--day",
        action="store",
        help="day to check as yyyy-mm-dd (default: today)",
        default=str(date.today()),
    )
    parser.add_option(
        "-o",
        "--output",
        action="store",
        help="output file name [default: standard output]",
    )
    addDashboardOptions(parser)

    opts, args = parser.parse_args()

    if args:
        parser.error("unexpected arguments")

    # Initialize db connection
    dashboard = Dashboard(
        credentials=None,
        flavour=opts.flavour,
        server=opts.db_url,
        dbname=opts.db_name or Dashboard.dbName(opts.flavour),
    )

    # Prepare data
    day_start = time.mktime(time.strptime(opts.day, "%Y-%m-%d"))
    expected_builds = []

    def expected_build_info(slot, project, platform, timestamp):
        from os.path import join

        version = None
        for p in slot["projects"]:
            if project == p["name"] and not p.get("no_test"):
                version = p["version"]
                break
        else:
            # cannot find the project in the slot or the project is not tested
            return None
        build_id = str(slot["build_id"])
        filename = join(
            "artifacts",
            opts.flavour,
            slot["slot"],
            build_id,
            ".".join([project, version, slot["slot"], build_id, platform, "zip"]),
        )
        return [
            filename,
            slot["slot"],
            slot["build_id"],
            project,
            platform,
            timestamp,
            platform.split("-")[1],
        ]

    for row in dashboard.db.iterview(
        "summaries/byDay", batch=100, key=opts.day, include_docs=True
    ):
        slot_name = row.doc["slot"]
        build_id = row.doc["build_id"]

        for platform in row.doc["config"]["platforms"]:
            builds = set()
            tests = set()
            started = day_start
            if platform in row.doc["builds"]:
                builds.update(
                    p
                    for p in row.doc["builds"][platform]
                    if p != "info" and "completed" in row.doc["builds"][platform][p]
                )
                started = row.doc["builds"][platform]["info"]["started"]
            if platform in row.doc["tests"]:
                tests.update(
                    p
                    for p in row.doc["tests"][platform]
                    if "completed" in row.doc["builds"][platform][p]
                )
            expected_builds.extend(
                expected_build_info(row.doc["config"], project, platform, started)
                for project in builds - tests
            )

    if opts.output:
        import codecs

        json.dump(expected_builds, codecs.open(opts.output, "w", "utf-8"), indent=2)
    else:
        print(json.dumps(expected_builds, indent=2))


def rpm():
    from LbRPMTools.PackageSlot import Script

    return Script().run()


def rpm_validator():
    """
    Command line client that interfaces to the YUMChecker class

    :author: Stefan-Gabriel Chitic
    """
    import json
    import logging
    import optparse
    import os
    import sys
    import tempfile
    import traceback

    from lbinstall.YumChecker import YumChecker

    # Class for known install exceptions
    ###############################################################################

    class LHCbRPMReleaseConsistencyException(Exception):
        """Custom exception for lb-install

        :param msg: the exception message
        """

        def __init__(self, msg):
            """Constructor for the exception"""
            # super( LHCbRPMReleaseConsistencyException, self).__init__(msg)
            Exception.__init__(self, msg)

    # Classes and method for command line parsing
    ###############################################################################

    class LHCbRPMReleaseConsistencyOptionParser(optparse.OptionParser):
        """Custom OptionParser to intercept the errors and rethrow
        them as LHCbRPMReleaseConsistencyExceptions"""

        def error(self, msg):
            """
            Arguments parsing error message exception handler

            :param msg: the message of the exception
            :return: Raises LHCbRPMReleaseConsistencyException with the exception message
            """
            raise LHCbRPMReleaseConsistencyException(
                "Error parsing arguments: " + str(msg)
            )

        def exit(self, status=0, msg=None):
            """
            Arguments parsing error message exception handler

            :param status: the status of the application
            :param msg: the message of the exception
            :return: Raises LHCbRPMReleaseConsistencyException with the exception message
            """
            raise LHCbRPMReleaseConsistencyException(
                "Error parsing arguments: " + str(msg)
            )

    class LHCbRPMReleaseConsistencyClient:
        """Main class for the tool"""

        def __init__(
            self,
            configType,
            arguments=None,
            dry_run=False,
            prog=" LHCbRPMReleaseConsistency",
        ):
            """Common setup for both clients"""
            self.configType = configType
            self.log = logging.getLogger(__name__)
            self.arguments = arguments
            self.checker = None
            self.prog = prog

            parser = LHCbRPMReleaseConsistencyOptionParser(usage=usage(self.prog))
            parser.add_option(
                "-d",
                "--debug",
                dest="debug",
                default=False,
                action="store_true",
                help="Show debug information",
            )
            parser.add_option(
                "--info",
                dest="info",
                default=False,
                action="store_true",
                help="Show logging messages with level INFO",
            )
            parser.add_option(
                "--build-folder",
                dest="buildfolder",
                default="/data/archive/artifacts/release/" "lhcb-release/",
                action="store",
                help="Add custom folder for builds",
            )
            parser.add_option(
                "--repo-url",
                dest="repourl",
                default="https://cern.ch/lhcb-nightlies-artifacts/"
                "release/lhcb-release/",
                action="store",
                help="Add custom repo url",
            )
            parser.add_option(
                "--no-details",
                dest="nodetails",
                default=False,
                action="store_true",
                help="Displays only the name of" " the missing packages.",
            )
            self.parser = parser

        def main(self):
            """Main method for the ancestor:
            call parse and run in sequence

            :returns: the return code of the call
            """
            rc = 0
            try:
                opts, args = self.parser.parse_args(self.arguments)
                # Checkint the siteroot and URL
                # to choose the siteroot
                self.siteroot = tempfile.gettempdir()

                # Now setting the logging depending on debug mode...
                if opts.debug or opts.info:
                    logging.basicConfig(
                        format="%(levelname)-8s: " "%(funcName)-25s - %(message)s"
                    )
                    if opts.info:
                        logging.getLogger().setLevel(logging.INFO)
                    else:
                        logging.getLogger().setLevel(logging.DEBUG)

                self.buildfolder = opts.buildfolder
                self.repourl = opts.repourl

                # Getting the function to be invoked
                self.run(opts, args)

            except LHCbRPMReleaseConsistencyException as lie:
                print("ERROR: " + str(lie), file=sys.stderr)
                self.parser.print_help()
                rc = 1
            except:
                print("Exception in lb-install:", file=sys.stderr)
                print("-" * 60, file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                print("-" * 60, file=sys.stderr)
                rc = 1
            return rc

        def run(self, opts, args):
            """Main method for the command

            :param opts: The option list
            :param args: The arguments list
            """
            # Parsing first argument to check the mode

            # Setting up repo url customization
            # By default repourl is none, in which case the hardcoded default
            # is used skipConfig allows returning a config with the LHCb
            # repositories

            from lbinstall.LHCbConfig import Config

            conf = Config(self.siteroot)
            local_url = f"{self.repourl}"
            local_folder = f"{self.buildfolder}"
            conf.repos["local_repo"] = {"url": local_url}
            rpm_list = [f for f in os.listdir(local_folder) if f.endswith(".rpm")]

            self.checker = YumChecker(
                siteroot=self.siteroot,
                config=conf,
                strict=True,
                simple_output=opts.nodetails,
            )
            platform = args[0]
            packages = []
            tmp_platform = platform.replace("-", "_")
            for rpm in rpm_list:
                if tmp_platform not in rpm:
                    continue
                tmp = rpm.split("-")
                if len(tmp) > 0:
                    name = tmp[0]
                    name = name.replace("+", r"\+")
                else:
                    raise Exception("No packages found")
                if len(tmp) > 1:
                    version = tmp[1]
                    vaersion = version.split(".")[0]
                else:
                    version = None
                if len(tmp) > 2:
                    release = tmp[2]
                    release = release.split(".")[0]
                else:
                    release = None

                packages.extend(self.checker.queryPackages(name, None, None))
            for rpmname, version, release in packages:
                self.log.info(
                    "Checking consistency for: %s %s %s", rpmname, version, release
                )
            json_file = os.path.join(
                local_folder, "build", platform, "RPMs_report.json"
            )
            res = self.checker.getMissingPackgesFromTuples(packages, force_local=True)
            new_data = {}
            for missing in res:
                req = missing["dependency"]
                req_name = f"{req.name}.{req.version}.{req.release}"
                p = missing["package"]
                p_name = f"{p.name}.{p.version}.{p.release}"
                if not new_data.get(p_name, None):
                    new_data[p_name] = []
                new_data[p_name].append(req_name)
            if not os.path.isdir(os.path.dirname(json_file)):
                os.makedirs(os.path.dirname(json_file))
            with open(json_file, "w") as outfile:
                new_data = {"missing_dependencies": new_data}
                json.dump(new_data, outfile)

    ###############################################################################
    def usage(cmd):
        """Prints out how to use the script...

        :param cmd: the command executed
        """
        cmd = os.path.basename(cmd)
        return f"""\n{cmd} - '

    It can be used in the following way:

    {cmd} [build_id]
    Verifies the consistency of RPM(s) from the yum repository for all the releases
    in the build id.

    """

    def LHCbRPMReleaseConsistency(configType="LHCbConfig", prog="lbyumcheck"):
        """
        Default caller for command line LHCbRPMReleaseConsistency client
        :param configType: the configuration used
        :param prog: the name of the executable
        """

        logging.basicConfig(format="%(levelname)-8s: %(message)s")
        logging.getLogger().setLevel(logging.WARNING)
        return LHCbRPMReleaseConsistencyClient(configType, prog=prog).main()

    # Main just chooses the client and starts it
    return LHCbRPMReleaseConsistency()


def test_poll():
    from LbNightlyTools.Scripts.Test import Poll as Script

    return Script().run()


def lbq_builddone():
    """
    Send the message that a build for a project has been done
    """
    __author__ = "Ben Couturier <ben.couturier@cern.ch>"

    from LbNightlyTools.Configuration import Slot
    from LbNightlyTools.Scripts.Common import PeriodicTestMsg, PlainScript

    class Script(PlainScript):
        """
        Sends the message that a build has been done
        """

        __usage__ = "%prog <slot> <project> <config> <buildId>"
        __version__ = ""

        def main(self):
            """
            Main function of the script.
            """
            # Checking the arguments
            if len(self.args) != 4:
                self.log.error("Please specify <slot> <project> <platform> <build_id>")
                exit(1)

            slot, project, platform, build_id = self.args

            # make this script look enough like a nightly BaseScript
            self.slot = Slot(slot, build_id=build_id)
            self.platform = platform
            msg = PeriodicTestMsg(self)
            msg.builds_ready(project)

    return Script().run()


def lbq_buildnotif():
    """
    Receive messages that a build for a project has been done
    """
    __author__ = "Ben Couturier <ben.couturier@cern.ch>"

    from pprint import pprint

    from LbNightlyTools.Scripts.Common import PeriodicTestMsg, PlainScript
    from LbNightlyTools.Utils import Dashboard

    class Script(PlainScript):
        """
        Sends the message that a build has been done
        """

        __usage__ = "%prog --queue <queue>"
        __version__ = ""

        def defineOpts(self):
            """
            Options specific to this script.
            """
            self.parser.add_option(
                "-q",
                "--queue",
                default=None,
                help="Name of the (persistent) queue to store the messages",
            )

        def main(self):
            """
            Main function of the script.
            """

            if not self.options.queue:
                raise Exception(
                    "No point in just getting messages on a newly created queue. Name the queue with -q"
                )

            dashboard = Dashboard(flavour="periodic")

            class PopBuilds:
                def __init__(self):
                    self.buildsDone = []

                def __call__(self, doc):
                    if "builds" in doc:
                        self.buildsDone = doc["builds"]
                        doc["builds"] = []
                    return doc

            pop_builds = PopBuilds()
            dashboard.update(PeriodicTestMsg.doc_id(self.options.queue), pop_builds)
            pprint(pop_builds.buildsDone)

    return Script().run()


def lbq_getteststorun():
    """
    Request for a periodic test to be run
    """
    __author__ = "Ben Couturier <ben.couturier@cern.ch>"

    from LbNightlyTools.Scripts.Common import PlainScript
    from LbNightlyTools.Utils import Dashboard, JenkinsTest

    class Script(PlainScript):
        """
        Sends the message that a build has been done
        """

        __usage__ = "%prog"
        __version__ = ""

        def defineOpts(self):
            """Define options."""
            from LbNightlyTools.Scripts.Common import addBasicOptions

            self.parser.add_option(
                "-j",
                "--jenkins",
                action="store_true",
                default=False,
                help="Store the jobs to run in Jenkins format",
            )
            addBasicOptions(self.parser)

        def main(self):
            """
            Main function of the script.
            """
            dashboard = Dashboard(flavour="periodic")
            doc = dashboard.db.get("frontend:tests-to-start", {"requests": []})
            testsToRun = list(doc["requests"])

            if not testsToRun:
                self.log.warning("nothing to do")
                return

            for idx, testToRun in enumerate(testsToRun):
                # Just printing out CSV by default
                if not self.options.jenkins:
                    # In this case the callback just prints the message
                    print(testToRun)
                else:
                    # Here we write out the files for Jenkins
                    self.log.warning("Job %d: %s", idx, testToRun)
                    jenkins_test = JenkinsTest(
                        testToRun["slot"],
                        testToRun["build_id"],
                        testToRun["project"],
                        testToRun["platform"],
                        testToRun["os_label"],
                        testToRun["group"],
                        testToRun["runner"],
                        testToRun["env"],
                    )
                    filename = f"test-params-{idx}.txt"
                    with open(filename, "w") as paramfile:
                        paramfile.writelines(jenkins_test.getParameterLines())
                        paramfile.writelines("tests_node=" + testToRun["os_label"])
                        self.log.warning(filename)

            # remove triggered jobs from the DB
            def remove_triggered(doc):
                if "requests" not in doc:
                    doc["requests"] = []
                doc["requests"] = [
                    entry for entry in doc["requests"] if entry not in testsToRun
                ]
                return doc

            dashboard.update("frontend:tests-to-start", remove_triggered)

    return Script().run()


def get_configs():
    """
    Simple script to check out the current nightly slots configurations.
    """
    import os
    from subprocess import check_call

    cmd = ["git", "clone"]
    if "configs_branch" in os.environ:
        cmd.extend(["-b", os.environ["configs_branch"]])
    cmd.extend(["https://gitlab.cern.ch/lhcb-core/LHCbNightlyConf.git", "configs"])

    check_call(cmd)

    with open("configs/extra_config.py", "w") as f:
        f.write(os.environ.get("extra_config_py", ""))
        f.write("\n")

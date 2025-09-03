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
def check_periodic_tests():
    from LbNightlyTools.Utils import JenkinsTest

    """
    Simple script to check which tests should be run for a given date
    """
    __author__ = "Ben Couturier <ben.couturier@cern.ch>"

    import datetime
    import json
    import logging
    import re
    import sys

    from LbPeriodicTools.LbPeriodicStarter import PeriodicTestStarter

    from LbNightlyTools.Scripts.Common import PlainScript

    class Script(PlainScript):
        """
        Script to print the list of tests to run on a given day,
        based on the config specified
        """

        __usage__ = "%prog [options] <config.json>"
        __version__ = ""

        def defineOpts(self):
            """Define options."""
            from LbNightlyTools.Scripts.Common import addBasicOptions

            self.parser.add_option(
                "-o",
                "--output",
                action="store",
                help="output file format " "[default: test-params-{0}.txt]",
                default="test-params-{0}.txt",
            )
            self.parser.add_option(
                "-d",
                "--date",
                action="store",
                help="Date for the tests " "Format: YYYY-MM-dd HH:MM [default: today]",
            )
            self.parser.add_option(
                "-i",
                "--interval",
                action="store",
                help="Interval for test checks in seconds " "[default: 60s]",
                default="60",
            )
            addBasicOptions(self.parser)

        def main(self):
            """
            Main function of the script.
            """

            # Checking we did pass an argument
            if len(self.args) != 1:
                self.parser.error("Please specify config file")

            config_file = self.args[0]

            # Checking the date at which to run
            opts = self.options
            testdate = datetime.datetime.today()
            if opts.date:
                testdate = datetime.datetime.strptime(opts.date, "%Y-%m-%d %H:%M")

            testdateend = testdate + datetime.timedelta(seconds=int(opts.interval))
            self.log.warning(
                "Running tests from {} for the period {}/{}".format(
                    config_file,
                    testdate.strftime("%Y-%m-%d %H:%M:%S"),
                    testdateend.strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

            # Checking which jobs to run
            starter = PeriodicTestStarter(
                config_file, testdate.strftime("%Y-%m-%d %H:%M:%S"), int(opts.interval)
            )

            all_tests = starter.getAllTests()
            tests_to_run = []
            for test_template, test_list in all_tests:
                self.log.warning(
                    f"{test_template}: {len(test_list)} actual tests to run"
                )
                for test_instance in test_list:
                    # tests_to_run.append(test_instance.__dict__)
                    tests_to_run.append(test_instance)

            for idx, ttr in enumerate(tests_to_run):
                jenkins_test = JenkinsTest.fromScheduledTest(ttr)
                tests_node = re.search("os_label=([^/]+)", (str(ttr)))
                with open(opts.output.format(idx), "w") as paramfile:
                    paramfile.writelines(jenkins_test.getParameterLines())
                    if tests_node:
                        paramfile.writelines("tests_node=" + tests_node.group(1))
                self.log.warning(opts.output.format(idx))

    return Script().run()


def check_periodic_tests_msg():
    """
    Simple script to check which tests should be run for a given date
    """
    __author__ = "Ben Couturier <ben.couturier@cern.ch>"

    import datetime
    import fnmatch
    import re

    from LbPeriodicTools.LbPeriodicStarter import PeriodicTestStarter

    from LbNightlyTools.Scripts.Common import PeriodicTestMsg, PlainScript
    from LbNightlyTools.Utils import Dashboard, JenkinsTest

    class Script(PlainScript):
        """
        Script to print the list of tests to run on a given day,
        based on the config specified
        """

        __usage__ = "%prog [options] <config.json>"
        __version__ = ""

        def defineOpts(self):
            """Define options."""
            from LbNightlyTools.Scripts.Common import addBasicOptions

            self.parser.add_option(
                "-o",
                "--output",
                action="store",
                help="output file format [default: test-params-{0}.txt]",
                default="test-params-{0}.txt",
            )
            self.parser.add_option(
                "-d",
                "--date",
                action="store",
                help="Date for the tests Format: YYYY-MM-dd HH:MM [default: today]",
            )
            self.parser.add_option(
                "-i",
                "--interval",
                action="store",
                help="Interval for test checks in seconds [default: 60s]",
                default="60",
            )
            self.parser.add_option(
                "-q",
                "--queue",
                default=None,
                help="Name of the (persistent) queue to store the messages",
            )

            addBasicOptions(self.parser)

        def main(self):
            """
            Main function of the script.
            """

            # Checking we did pass an argument
            if len(self.args) < 1:
                self.parser.error("Please specify config file")

            config_file = self.args[0]

            # # Checking the date at which to run
            opts = self.options
            testdate = datetime.datetime.today()

            if not self.options.queue:
                raise Exception(
                    "No point in just getting messages "
                    "on a newly created queue. "
                    "Name the queue with -q"
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
            buildsDone = pop_builds.buildsDone

            testdate = datetime.datetime.today().replace(hour=00, minute=00, second=00)
            testdateend = testdate + datetime.timedelta(seconds=int(opts.interval))

            self.log.warning(
                "Running tests from {} for the period {}/{}".format(
                    config_file,
                    testdate.strftime("%Y-%m-%d %H:%M:%S"),
                    testdateend.strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

            # Checking which jobs to run
            starter = PeriodicTestStarter(
                config_file, testdate.strftime("%Y-%m-%d %H:%M:%S"), int(opts.interval)
            )
            all_tests = starter.getAllTests()
            tests_to_run = []
            idx = 0
            for test_template, test_list in all_tests:
                for test_tmp in test_list:
                    for build in buildsDone:
                        if (
                            test_tmp.slot == build["slot"]
                            and test_tmp.build_id == build["build_id"]
                            and test_tmp.project == build["project"]
                            and fnmatch.fnmatch(build["platform"], test_tmp.platform)
                        ):
                            tests_to_run.append(test_tmp)
                            print(test_tmp)
                            jenkins_test = JenkinsTest.fromScheduledTest(test_tmp)
                            tests_node = re.search("os_label=([^/]+)", (str(test_tmp)))
                            with open(opts.output.format(idx), "w") as parfile:
                                parfile.writelines(jenkins_test.getParameterLines())
                                if tests_node:
                                    parfile.writelines(
                                        "tests_node=" + tests_node.group(1)
                                    )
                            self.log.warning(opts.output.format(idx))
                            idx += 1

    return Script().run()

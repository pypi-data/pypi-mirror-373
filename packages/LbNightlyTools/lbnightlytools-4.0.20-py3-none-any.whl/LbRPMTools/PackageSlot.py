###############################################################################
# (c) Copyright 2014-2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Class to generate RPM packages for a whole slot

Created on Feb 27, 2014

@author: Ben Couturier
"""

import logging
import os
import shutil

__log__ = logging.getLogger(__name__)

# Main Script to generate the RPMs for a build slot
#
###############################################################################
from LbNightlyTools.Scripts.Common import PlainScript


class Script(PlainScript):
    """
    Script to produce the RPM for a LHCb Nightly slot.
    """

    __usage__ = "%prog [options] <slot_config.json>"
    __version__ = ""

    def addRpmOptions(self, parser):
        """
        Add some basic (common) options to the option parser
        """
        from optparse import OptionGroup

        group = OptionGroup(self.parser, "RPM Options")
        group.add_option(
            "-p",
            "--platform",
            dest="platform",
            default=None,
            action="store",
            help="Force platform",
        )
        group.add_option(
            "-s",
            "--shared",
            dest="shared",
            default=False,
            action="store_true",
            help="Build shared RPM",
        )
        group.add_option(
            "-g",
            "--glimpse",
            dest="glimpse",
            default=False,
            action="store_true",
            help="Build glimpse RPM",
        )
        group.add_option(
            "--shared-tar",
            dest="sharedTar",
            default=None,
            action="store",
            help="Shared tar to be included",
        )
        group.add_option(
            "--builddir",
            dest="builddir",
            default=None,
            action="store",
            help="Force LCG dir if different from the one containing the config file",
        )
        group.add_option(
            "-b",
            "--buildarea",
            dest="buildarea",
            default="/tmp",
            action="store",
            help="Force build root",
        )
        group.add_option(
            "-o",
            "--output",
            dest="output",
            default=None,
            action="store",
            help="File name for the generated specfile [default output to stdout]",
        )
        group.add_option(
            "--keep-rpmdir",
            dest="keeprpmdir",
            action="store_true",
            default=False,
            help="Keep the directories used to build the RPMs",
        )
        group.add_option(
            "--dry-run",
            dest="dryrun",
            action="store_true",
            default=False,
            help="Only prepare the spec, not the RPMs",
        )
        group.add_option(
            "--manifest",
            dest="manifestfile",
            default=None,
            action="store",
            help="Force the manifest file to be used",
        )
        group.add_option(
            "--rpmreldir",
            dest="rpmreldir",
            default=None,
            action="store",
            help="Specify the RPM release directory",
        )
        group.add_option(
            "--checkrelease",
            dest="checkrelease",
            default=False,
            action="store_true",
            help="Check the RPM repository to check whether the release number should be incremented",
        )
        parser.add_option_group(group)
        return parser

    def defineOpts(self):
        """
        Prepare the option parser.
        """
        from LbNightlyTools.Scripts.Common import addBasicOptions

        addBasicOptions(self.parser)
        self.parser.add_option(
            "--flavour",
            default="nightly",
            help="nightly builds flavour " "[default: %default]",
        )
        self.addRpmOptions(self.parser)

    def _createRpmDirs(self, buildarea, buildname):
        """
        Create directories necessary to the build
        """
        from .LHCbRPMSpecBuilder import RpmDirConfig

        return RpmDirConfig(buildarea, buildname)

    def _callRpmbuild(self, specfilename, fullrpmpath, artifactdir):
        """Call the rpmbuild command itself"""

        rpmsdir = os.path.join(artifactdir, "rpms")
        if self.options.dryrun:
            self.log.warning(f"Dry run mode, not calling RPM build for {specfilename}")
            shutil.copy(specfilename, rpmsdir)
            self.log.warning(f"Dry run mode, spec file copied to {rpmsdir}")
            return

        # Now calling the rpmbuild command
        from subprocess import PIPE, Popen

        myenv = os.environ.copy()
        myenv["QA_RPATHS"] = "0x0002"
        process = Popen(
            ["rpmbuild", "-bb", specfilename],
            stdout=PIPE,
            stderr=PIPE,
            env=myenv,
            errors="replace",
        )

        (stdout, stderr) = process.communicate()
        log_fn = self.log.info if process.returncode == 0 else self.log.error
        # XXX Careful we should not be caching the stdout and stderr
        if stdout:
            log_fn(stdout)
        if stderr:
            log_fn(stderr)

        if process.returncode != 0:
            self.log.error("RPM build failed")
            raise Exception("RPM build failed")

        if not os.path.exists(fullrpmpath):
            self.log.error(f"Cannot find RPM: {fullrpmpath}")
            raise Exception(f"Cannot find RPM: {fullrpmpath}")
        else:
            self.log.info(f"Copying {fullrpmpath} to {rpmsdir}")
            shutil.copy(fullrpmpath, rpmsdir)

    def _getManifestFilename(self, builddir, project, version, platform):
        # Checking if the file was overriden (needed fro tests)
        if self.options.manifestfile != None:
            self.log.info(
                f"Using manifest.xml filename overriden to: {self.options.manifestfile}"
            )
            return self.options.manifestfile

        # Checking for the existence of the manifest.xml file
        projbuilddir = os.path.join(
            builddir, project.upper(), project.upper() + "_" + version
        )
        if platform != None:
            manifestxmlfile = os.path.join(
                projbuilddir, "InstallArea", platform, "manifest.xml"
            )
        else:
            manifestxmlfile = os.path.join(projbuilddir, "manifest.xml")

        if not os.path.exists(manifestxmlfile):
            self.log.error(f"Missing manifest.xml file: {manifestxmlfile}")
            raise Exception(f"Missing manifest.xml file: {manifestxmlfile}")
        else:
            self.log.info(f"Using manifest.xml file: {manifestxmlfile}")
        return manifestxmlfile

    def _buildRpm(
        self,
        project,
        version,
        platform,
        rpmbuildarea,
        builddir,
        artifactdir,
        keeprpmdir,
    ):
        """Build the RPM for the project them and copy them to the target area"""

        # First check if there is a shared RPM to build
        hasShared = self._buildExtraSharedRpm(
            project, version, rpmbuildarea, artifactdir, keeprpmdir
        )

        rpmbuildname = "_".join([project, version, platform])

        # Creating the temp directories to prepare the RPMs
        rpmconf = self._createRpmDirs(rpmbuildarea, rpmbuildname)

        # Locating the manifest file
        manifestxmlfile = self._getManifestFilename(
            builddir, project, version, platform
        )

        # Parsing the manifest.xml file
        from LbTools.Manifest import Parser

        manifest = Parser(manifestxmlfile)

        # Now generating the spec
        from LbRPMTools.LHCbRPMSpecBuilder import LHCbBinaryRpmSpec, getBuildInfo

        (_absFilename, buildlocation, _fprojectVersion, _fcmtconfig) = getBuildInfo(
            manifestxmlfile
        )
        spec = LHCbBinaryRpmSpec(
            project, version, platform, rpmbuildarea, buildlocation, manifest
        )
        if hasShared:
            spec.addExtraRequire("_".join([project, version, "shared"]))

        # Check if a non default RPM release dir was specified
        if self.options.rpmreldir != None:
            self.log.warning(
                f"Setting RPM release dir from options: {self.options.rpmreldir}"
            )
            spec.setRPMReleaseDir(self.options.rpmreldir)

        if self.options.checkrelease:
            self.log.warning("Incrementing the release number based on YUM repo")
            spec.setCheckRelease(self.options.checkrelease)

        specfilename = os.path.join(rpmconf.topdir, rpmbuildname + ".spec")
        self.log.info(f"Writing spec file to {specfilename}")
        with open(specfilename, "w") as outputfile:
            outputfile.write(spec.getSpec())

        # Building the name of the expected RPM
        rpmname = spec.getRPMName()
        fullrpmpath = os.path.join(rpmconf.rpmsdir, spec.getArch(), rpmname)
        self._callRpmbuild(specfilename, fullrpmpath, artifactdir)

        # Remove tmpdirectory
        if not keeprpmdir:
            rpmconf.removeBuildArea()
            self.log.info(f"Removing: {rpmconf.buildarea} ")
        else:
            self.log.info(f"Keeping: {rpmconf.buildarea} ")

    def _buildExtraSharedRpm(
        self, project, version, rpmbuildarea, artifactdir, keeprpmdir
    ):
        """Build the RPM for the extra shared zip filed produced by some projects
        like geant4"""

        hasShared = False
        rpmbuildname = "_".join([project, version, "shared"])

        # Creating the temp directories to prepare the RPMs
        rpmconf = self._createRpmDirs(rpmbuildarea, rpmbuildname)

        # Looking for archive with sources
        srcArchive = self._findExtraSharedArchive(project, version, artifactdir)
        if srcArchive != None:
            self.log.info(f"Taking sources from {srcArchive}")
            hasShared = True
        else:
            # No zip find, no need to do anything...
            hasShared = False
            return hasShared

        # Now generating the spec
        from LbRPMTools.LHCbRPMSpecBuilder import LHCbExtraSharedRpmSpec

        spec = LHCbExtraSharedRpmSpec(project, version, srcArchive, rpmbuildarea)
        # Check if a non default RPM release dir was specified
        if self.options.rpmreldir != None:
            self.log.warning(
                f"Setting RPM release dir from options: {self.options.rpmreldir}"
            )
            spec.setRPMReleaseDir(self.options.rpmreldir)

        if self.options.checkrelease:
            self.log.warning("Incrementing the release number based on YUM repo")
            spec.setCheckRelease(self.options.checkrelease)

        specfilename = os.path.join(rpmconf.topdir, rpmbuildname + ".spec")
        with open(specfilename, "w") as outputfile:
            outputfile.write(spec.getSpec())

        # Building the name of the expected RPM
        rpmname = spec.getRPMName()

        fullrpmpath = os.path.join(rpmconf.rpmsdir, spec.getArch(), rpmname)
        self._callRpmbuild(specfilename, fullrpmpath, artifactdir)

        # Remove tmpdirectory
        if not keeprpmdir:
            rpmconf.removeBuildArea()
            self.log.info(f"Removing: {rpmconf.buildarea} ")
        else:
            self.log.info(f"Keeping: {rpmconf.buildarea} ")

    def _buildSharedRpm(
        self,
        project,
        version,
        rpmbuildarea,
        builddir,
        artifactdir,
        keeprpmdir,
        isPlatformIndependent=False,
    ):
        """Build the RPM for the project them and copy them to the target area"""

        rpmbuildname = "_".join([project, version])

        # Creating the temp directories to prepare the RPMs
        rpmconf = self._createRpmDirs(rpmbuildarea, rpmbuildname)

        # Looking for archive with sources
        srcArchive = self._findSrcArchive(project, version, artifactdir)
        if srcArchive != None:
            self.log.info(f"Taking sources from {srcArchive}")
        else:
            self.log.error("Could not find archive with shared sources")
            raise Exception("Could not find archive with shared sources")

        # Only doing the following for platform independent projects: in this case
        # we can have dependencies. In the other case, this is a RPM containing sources
        # that the binary RPM depends on.
        manifest = None
        if isPlatformIndependent:
            # Locating the manifest file
            manifestxmlfile = self._getManifestFilename(
                builddir, project, version, None
            )

            # Parsing the manifest.xml file
            from LbTools.Manifest import Parser

            manifest = Parser(manifestxmlfile)

        # Now generating the spec
        from LbRPMTools.LHCbRPMSpecBuilder import LHCbSharedRpmSpec

        spec = LHCbSharedRpmSpec(project, version, srcArchive, rpmbuildarea, manifest)
        # Check if a non default RPM release dir was specified
        if self.options.rpmreldir != None:
            self.log.warning(
                f"Setting RPM release dir from options: {self.options.rpmreldir}"
            )
            spec.setRPMReleaseDir(self.options.rpmreldir)

        if self.options.checkrelease:
            self.log.warning("Incrementing the release number based on YUM repo")
            spec.setCheckRelease(self.options.checkrelease)

        specfilename = os.path.join(rpmconf.topdir, rpmbuildname + ".spec")
        with open(specfilename, "w") as outputfile:
            outputfile.write(spec.getSpec())

        # Building the name of the expected RPM
        rpmname = spec.getRPMName()
        fullrpmpath = os.path.join(rpmconf.rpmsdir, spec.getArch(), rpmname)
        self._callRpmbuild(specfilename, fullrpmpath, artifactdir)

        # Remove tmpdirectory
        if not keeprpmdir:
            rpmconf.removeBuildArea()
            self.log.info(f"Removing: {rpmconf.buildarea} ")
        else:
            self.log.info(f"Keeping: {rpmconf.buildarea} ")

    def _buildLbScriptsRpm(
        self, project, version, rpmbuildarea, artifactdir, keeprpmdir
    ):
        """Build the RPM for the project them and copy them to the target area"""

        rpmbuildname = "_".join([project, version])

        # Creating the temp directories to prepare the RPMs
        rpmconf = self._createRpmDirs(rpmbuildarea, rpmbuildname)

        # Looking for archive with sources
        srcArchive = self._findSrcArchive(project, version, artifactdir)
        if srcArchive != None:
            self.log.info(f"Taking sources from {srcArchive}")
        else:
            self.log.warning("Doing clean checkout of the sources")

        # Now generating the spec
        from LbRPMTools.LHCbRPMSpecBuilder import LHCbLbScriptsRpmSpec

        spec = LHCbLbScriptsRpmSpec(project, version, srcArchive, rpmbuildarea)
        # Check if a non default RPM release dir was specified
        if self.options.rpmreldir != None:
            self.log.warning(
                f"Setting RPM release dir from options: {self.options.rpmreldir}"
            )
            spec.setRPMReleaseDir(self.options.rpmreldir)

        if self.options.checkrelease:
            self.log.warning("Incrementing the release number based on YUM repo")
            spec.setCheckRelease(self.options.checkrelease)

        specfilename = os.path.join(rpmconf.topdir, rpmbuildname + ".spec")
        with open(specfilename, "w") as outputfile:
            outputfile.write(spec.getSpec())

        # Building the name of the expected RPM
        rpmname = spec.getRPMName()
        fullrpmpath = os.path.join(rpmconf.rpmsdir, spec.getArch(), rpmname)
        self._callRpmbuild(specfilename, fullrpmpath, artifactdir)

        # Remove tmpdirectory
        if not keeprpmdir:
            rpmconf.removeBuildArea()
            self.log.info(f"Removing: {rpmconf.buildarea} ")
        else:
            self.log.info(f"Keeping: {rpmconf.buildarea} ")

    def _buildDatapkgRpm(
        self, project, fulldatapkg, version, rpmbuildarea, artifactdir, keeprpmdir
    ):
        """Build the RPM for the datapkg and copy them to the target area"""
        fulldatapkg
        datapkg = fulldatapkg
        if "/" in datapkg:
            (_hat, datapkg) = fulldatapkg.split("/")

        rpmbuildname = "_".join([project, datapkg])

        # Creating the temp directories to prepare the RPMs
        rpmconf = self._createRpmDirs(rpmbuildarea, rpmbuildname)

        # Looking for archive with sources
        srcArchive = self._findDatapkgArchive(
            project, fulldatapkg, version, artifactdir
        )
        if srcArchive != None:
            self.log.info(f"Taking sources from {srcArchive}")
        else:
            self.log.warning("Doing clean checkout of the sources")

        # Now generating the spec
        from LbRPMTools.LHCbRPMSpecBuilder import LHCbDatapkgRpmSpec

        spec = LHCbDatapkgRpmSpec(
            project, fulldatapkg, version, srcArchive, rpmbuildarea
        )
        # Check if a non default RPM release dir was specified
        if self.options.rpmreldir != None:
            self.log.warning(
                f"Setting RPM release dir from options: {self.options.rpmreldir}"
            )
            spec.setRPMReleaseDir(self.options.rpmreldir)

        if self.options.checkrelease:
            self.log.warning("Incrementing the release number based on YUM repo")
            spec.setCheckRelease(self.options.checkrelease)

        specfilename = os.path.join(rpmconf.topdir, rpmbuildname + ".spec")
        with open(specfilename, "w") as outputfile:
            outputfile.write(spec.getSpec())

        # Building the name of the expected RPM
        rpmname = spec.getRPMName()
        fullrpmpath = os.path.join(rpmconf.rpmsdir, spec.getArch(), rpmname)
        self._callRpmbuild(specfilename, fullrpmpath, artifactdir)

        # Remove tmpdirectory
        if not keeprpmdir:
            rpmconf.removeBuildArea()
            self.log.info(f"Removing: {rpmconf.buildarea} ")
        else:
            self.log.info(f"Keeping: {rpmconf.buildarea} ")

    def _buildGlimpseRpm(
        self,
        project,
        version,
        platform,
        rpmbuildarea,
        builddir,
        artifactdir,
        keeprpmdir,
    ):
        """Build the RPM for glimpse index and copy them to the target area"""

        rpmbuildname = "_".join(["glimpse", project, version])

        # Creating the temp directories to prepare the RPMs
        rpmconf = self._createRpmDirs(rpmbuildarea, rpmbuildname)

        # Locating the manifest file
        manifestxmlfile = self._getManifestFilename(
            builddir, project, version, platform
        )

        # Parsing the manifest.xml file
        from LbTools.Manifest import Parser

        manifest = Parser(manifestxmlfile)

        # Looking for archive with sources
        srcArchive = self._findGlimpseArchive(project, version, artifactdir)
        if srcArchive != None:
            self.log.info(f"Taking sources from {srcArchive}")
        else:
            self.log.warning("Doing clean checkout of the sources")

        # Now generating the spec
        from LbRPMTools.LHCbRPMSpecBuilder import LHCbGlimpseRpmSpec

        spec = LHCbGlimpseRpmSpec(project, version, srcArchive, rpmbuildarea, manifest)
        # Check if a non default RPM release dir was specified
        if self.options.rpmreldir != None:
            self.log.warning(
                f"Setting RPM release dir from options: {self.options.rpmreldir}"
            )
            spec.setRPMReleaseDir(self.options.rpmreldir)

        if self.options.checkrelease:
            self.log.warning("Incrementing the release number based on YUM repo")
            spec.setCheckRelease(self.options.checkrelease)

        specfilename = os.path.join(rpmconf.topdir, rpmbuildname + ".spec")
        with open(specfilename, "w") as outputfile:
            outputfile.write(spec.getSpec())

        # Building the name of the expected RPM
        rpmname = spec.getRPMName()
        fullrpmpath = os.path.join(rpmconf.rpmsdir, spec.getArch(), rpmname)
        self._callRpmbuild(specfilename, fullrpmpath, artifactdir)

        # Remove tmpdirectory
        if not keeprpmdir:
            rpmconf.removeBuildArea()
            self.log.info(f"Removing: {rpmconf.buildarea} ")
        else:
            self.log.info(f"Keeping: {rpmconf.buildarea} ")

    def _findGlimpseArchive(self, project, version, artifactdir):
        """Locate the source RPM"""
        # Checking if we find the src archive
        packname = [project, version]
        if self.options.build_id:
            packname.append(self.options.build_id)
        packname.append("index")
        packname.append("zip")
        archname = ".".join(packname)

        fullarchname = os.path.join(artifactdir, "packs", "index", archname)
        self.log.info(f"Looking for file: {fullarchname}")
        if os.path.exists(fullarchname):
            return os.path.abspath(fullarchname)
        else:
            return None

    def _findSrcArchive(self, project, version, artifactdir):
        """Locate the source RPM"""
        # Checking if we find the src archive
        packname = [project, version]
        if self.options.build_id:
            packname.append(self.options.build_id)
        packname.append("src")
        packname.append("zip")
        archname = ".".join(packname)

        fullarchname = os.path.join(artifactdir, "packs", "src", archname)
        self.log.info(f"Looking for file: {fullarchname}")
        if os.path.exists(fullarchname):
            return os.path.abspath(fullarchname)
        else:
            return None

    def _findExtraSharedArchive(self, project, version, artifactdir):
        """Locate the Extra Shared RPM"""
        # Checking if we find the src archive
        packname = [project, version]
        if self.options.build_id:
            packname.append(self.options.build_id)
        packname.append("shared")
        packname.append("zip")
        archname = ".".join(packname)

        fullarchname = os.path.join(artifactdir, "packs", "shared", archname)
        self.log.info(f"Looking for file: {fullarchname}")
        if os.path.exists(fullarchname):
            return os.path.abspath(fullarchname)
        else:
            return None

    def _findDatapkgArchive(self, project, datapkg, version, artifactdir):
        """Locate the source RPM"""
        # Checking if we find the src archive
        fixeddatapkg = datapkg.replace("/", "_")
        packname = [fixeddatapkg, version]

        if self.options.build_id:
            packname.append(self.options.build_id)

        packname.append("src")
        packname.append("zip")
        archname = ".".join(packname)

        fullarchname = os.path.join(artifactdir, "packs", "src", archname)
        self.log.info(f"Looking for file: {fullarchname}")
        if os.path.exists(fullarchname):
            return os.path.abspath(fullarchname)
        else:
            return None

    def _isPlatformIndependent(self, project, version, artifactdir):
        """Check if a project is platform independent

        A project is defined to be platform independent if we can find a
        manifest.xml in the top level directory of the source achive.

        Note that this method is slow because it needs to scan the source
        archive, so the result should be cached.
        """
        import zipfile

        srcArchive = self._findSrcArchive(project, version, artifactdir)
        if not srcArchive:
            self.log.warning(
                "assuming platform depdendent project " "(missing source archive)"
            )
            return False
        manifest = "{P}/{P}_{v}/manifest.xml".format(P=project.upper(), v=version)
        try:
            for info in zipfile.ZipFile(srcArchive, "r"):
                if info.filename == manifest:
                    return True
        except Exception as exc:
            self.log.warning(
                "assuming platform dependent project (%s: %s)",
                exc.__class__.__name__,
                exc,
            )
            return False

    def main(self):
        """
        Main method for the script
        """
        from LbNightlyTools.Scripts.Common import expandTokensInOptions

        if len(self.args) != 1:
            self.parser.error("wrong number of arguments")

        # Same logic as BuildSlot lo locate the builddir
        builddir = self.options.builddir
        if builddir == None:
            builddir = os.path.join(os.getcwd(), "build")

        # Now loading the slot configuration
        from LbNightlyTools.Configuration import findSlot

        self.slot = findSlot(self.args[0], flavour=self.options.flavour)
        # FIXME: to be ported to the new configuration classes
        self.config = self.slot.toDict()

        expandTokensInOptions(
            self.options, ["build_id", "artifacts_dir"], slot=self.config["slot"]
        )

        # Check the final artifacts dir
        if self.options.artifacts_dir is not None:
            artifactdir = self.options.artifacts_dir
        else:
            artifactdir = os.path.join(os.getcwd(), "artifacts")
        if not os.path.exists(os.path.join(artifactdir, "rpms")):
            os.makedirs(os.path.join(artifactdir, "rpms"))

        # Check plaform to package for
        platform = (
            self.options.platform
            or os.environ.get("BINARY_TAG")
            or os.environ.get("CMTCONFIG")
        )

        if not platform and not self.options.shared:
            raise Exception("Could not find platform")

        # temp area used to build the RPMs
        from tempfile import mkdtemp

        rpmbuildarea = mkdtemp(prefix="rpm")
        keeprpmdir = self.options.keeprpmdir

        if self.options.shared:
            for p in self.config["packages"]:
                fulldatapkg = p["name"]
                project = p.get("container", "DBASE")
                version = p["version"]
                self.log.info(
                    f"Preparing RPM for datapkg {project} {fulldatapkg} {version}"
                )
                self._buildDatapkgRpm(
                    project, fulldatapkg, version, rpmbuildarea, artifactdir, keeprpmdir
                )

        requested_projects = (
            None
            if not self.options.projects
            else [p.strip().lower() for p in self.options.projects.split(",")]
        )
        for p in self.config["projects"]:
            project = p["name"]
            if (
                (requested_projects and project.lower() not in requested_projects)
                or project.lower() in ("dbase", "param", "lcgcmt")
                or p.get("disabled")
            ):
                self.log.warning(f"Skipping project {project}")
                continue  # project not requested: skip
            version = p["version"]

            platform_independent = p.get(
                "platform_independent"
            ) or self._isPlatformIndependent(project, version, artifactdir)
            if self.options.shared:
                if project.lower() == "lbscripts":
                    self.log.info(f"Preparing RPM for LbScripts {version}")
                    self._buildLbScriptsRpm(
                        project, version, rpmbuildarea, artifactdir, keeprpmdir
                    )
                else:
                    self.log.info(
                        "Preparing RPM for project %s %s src", project, version
                    )
                    self._buildSharedRpm(
                        project,
                        version,
                        rpmbuildarea,
                        builddir,
                        artifactdir,
                        keeprpmdir,
                        platform_independent,
                    )
            elif self.options.glimpse:
                if platform_independent:
                    self.log.info(
                        "Platform independent. No glimpse for %s %s", project, version
                    )
                else:
                    self.log.info(
                        "Preparing Glimpse RPM for project %s %s", project, version
                    )
                    self._buildGlimpseRpm(
                        project,
                        version,
                        platform,
                        rpmbuildarea,
                        builddir,
                        artifactdir,
                        keeprpmdir,
                    )
            else:
                if platform_independent:
                    self.log.info(
                        "No platform specific RPM needed for project %s %s",
                        project,
                        version,
                    )
                else:
                    self.log.info(
                        f"Preparing RPM for project {project} {version} {platform}"
                    )
                    self._buildRpm(
                        project,
                        version,
                        platform,
                        rpmbuildarea,
                        builddir,
                        artifactdir,
                        keeprpmdir,
                    )

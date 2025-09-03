###############################################################################
# (c) Copyright 2014-2022 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Class to generate RPM Specfile

Created on Feb 27, 2014

@author: Ben Couturier
"""

import logging
import os
import re
from string import Template

from lbinstall.Installer import Installer

from LbNightlyTools.Utils import TemporaryDir

try:
    from LbEnv.ProjectEnv.lookup import MissingProjectError, findProject
except ImportError:
    from LbConfiguration.SP2.lookup import MissingProjectError, findProject

__log__ = logging.getLogger(__name__)

PREFIX = "/opt/LHCbSoft"

# FIXME: we need better way to manage this list... util we drop PARAM
PARAM_PKGS = {
    "BcVegPyData",
    "ChargedProtoANNPIDParam",
    "Geant4Files",
    "GenXiccData",
    "InstallAreaPatch",
    "LHCbBkg",
    "MCatNLOData",
    "MIBData",
    "ParamFiles",
    "QMTestFiles",
    "TMVAWeights",
}


# FIXME: we should drop this functionality
def is_platform_independent(project, version):
    try:
        return os.path.exists(
            os.path.join(findProject(project, version, "dummy"), "manifest.xml")
        )
    except MissingProjectError:
        return False


def convertToLHCbClassicVersion(version):
    """Convert a version of the type X.Y[.Z[.T]] to vXrY[pZ[tT]].
    Leaves the other strings unaffected
    """

    # Case when we specify the version as point separated numbers
    if re.match(r"^\d[\d.]*$", version):
        # this is a X.Y CMake style version, so we map it to vXr*
        # - get the first 4 element max (we support vXrYpZtT)
        parts = version.split(".")[:4]
        return "".join(a + b for a, b in zip("vrpt", parts))

    return version


class RpmDirConfig:
    """Placeholder for directory config"""

    def __init__(self, buildarea, buildname):
        self.buildarea = buildarea
        self.buildname = buildname

        self.topdir = f"{buildarea}/rpmbuild"
        self.tmpdir = f"{buildarea}/tmpbuild"
        self.rpmtmp = f"{buildarea}/tmp"
        self.srcdir = os.path.join(self.topdir, "SOURCES")
        self.rpmsdir = os.path.join(self.topdir, "RPMS")
        self.srpmsdir = os.path.join(self.topdir, "SRPMS")
        self.builddir = os.path.join(self.topdir, "BUILD")

        # And creating them if needed
        for d in [self.rpmtmp, self.srcdir, self.rpmsdir, self.srpmsdir, self.builddir]:
            if not os.path.exists(d):
                os.makedirs(d)

        self.buildroot = os.path.join(self.tmpdir, f"{buildname}-buildroot")
        if not os.path.exists(self.buildroot):
            os.makedirs(self.buildroot)

    def removeBuildArea(self):
        """Clean up the dirs"""
        import shutil

        if os.path.exists(self.buildarea):
            shutil.rmtree(self.buildarea)


#
# Base class for spec files
#
###############################################################################
class LHCbBaseRpmSpec:
    """Class representing a LHCb project"""

    def __init__(self, project, version, prodRPMReleaseDir=None):
        self._project = project
        self._version = version
        self._lhcb_release_version = 0
        self._prodRPMReleaseDir = prodRPMReleaseDir
        self._checkRelease = False

    def getSpec(self):
        """Build the global spec file"""

        # First we make sure we have a correct release number for the RPM
        # It is created at -1 in constructor.
        # At this point, we can check in the release directory if we need to bump up
        # the release number or keep the current one....
        self._setNextReleaseNumberFromRepo()

        # Now returning the spec itself...
        return (
            str(self._createHeader())
            + str(self._createRequires())
            + str(self._createDescription())
            + str(self._createInstall())
            + str(self._createTrailer())
        )

    def _createHEPToolsRequires(self):
        """Creates the dependency on the HepTools (LHCbExternals) RPMs"""

        # Looking up the heptools version from the manifest.xml
        heptools = self._manifest.getHEPTools()
        if not heptools:
            raise Exception("Missing heptools configuration")
        (heptools_version, heptools_binary_tag, used_packages) = heptools

        # Looking for the LCG platform, i.e. the one used in the
        # RPM name
        (lcg_platform, lcg_system) = self._manifest.getLCGConfig()

        # Getting the list of packages for that LCG version from the toolchain
        from LbTools import get_toolchain_packages

        try:
            packages_info, missing, version_mimatch = get_toolchain_packages(
                heptools_version, lcg_platform, used_packages
            )
            for p in missing:
                __log__.warning(f"Could not find package {p} in toolchain")
            for p in version_mimatch:
                tp = packages_info[p]
                v = used_packages[p]
                __log__.warning(
                    "Version mismatch for %s, expected %s, got %s", p, v, tp["version"]
                )
        except Exception as e:
            packages_info = {}
            __log__.warning("Could not look-up toolchain packages: %s", str(e))

        # at this stage "packages_info" contain a list of package we depend on, with info for the toochain
        # that we need to create the RPM name for the "Requires" statement.

        # a package from the toolchain is a map such as:
        # {u'directory': u'Catch2', u'platform': u'x86_64-centos9-gcc12-opt', u'version': u'2.13.9',
        # u'hash': u'7861b', u'dependencies': [u'Python-3.9.12-9a1bc']}
        def rpm_name(name, package):
            return "{n}-{c}_{v}_{p}".format(
                n=name,
                c=package["hash"],
                v=package["version"],
                p=package["platform"].replace("-", "_"),
            )

        requires = []
        for n, p in list(packages_info.items()):
            requires.append("Requires:" + rpm_name(n, p))
        return "\n".join(requires) + "\n"

    def _createExtToolsRequires(self):
        """Creates the dependency on the external (middleware) RPMs"""
        binary_tag, exttools = self._manifest.getExtTools()
        binary_tag = binary_tag.replace("-", "_")
        return "".join(
            "Requires: {name}_{vers}_{platf}\n".format(
                name=name, vers=vers.replace("-", "_"), platf=binary_tag
            )
            for name, vers in sorted(exttools.items())
        )

    def setRPMReleaseDir(self, rpmRelDir):
        """Set the location for the RPM release directory"""
        self._prodRPMReleaseDir = rpmRelDir

    def setCheckRelease(self, checkRelease):
        """Set the flags enabling the check of the release number in the YUM repository"""
        self._checkRelease = checkRelease

    def _getMatchingRPMFromRepo(self, name, version):
        """Looking up a package by name in the YUM repo"""
        with TemporaryDir() as siteroot:
            return Installer(siteroot=siteroot).remoteFindPackage(name, version=version)

    def _setNextReleaseNumberFromRepo(self):
        """Checks the RPM release dir (see constructor for the class) to find the
        next release number for the package.
        """
        if self._lhcb_release_version <= 0:
            if self._checkRelease:
                projver = ".".join(
                    [
                        str(n)
                        for n in [
                            self._lhcb_maj_version,
                            self._lhcb_min_version,
                            self._lhcb_patch_version,
                        ]
                    ]
                )
                __log__.debug(
                    f"Looking for releases of {self.getRPMName(norpmver=True)} / {projver}"
                )
                packages = self._getMatchingRPMFromRepo(
                    self.getRPMName(norpmver=True), projver
                )
                __log__.debug(f"Found package {packages}")
                if not packages:
                    self._lhcb_release_version = 1
                else:
                    prev_releases = [int(p.release) for p in packages]
                    __log__.debug("Previous versions releases")
                    nextver = max(prev_releases) + 1
                    self._lhcb_release_version = nextver
                    __log__.warning(
                        f"Release number set to {self._lhcb_release_version}"
                    )
            elif self._prodRPMReleaseDir != None and os.path.exists(
                self._prodRPMReleaseDir
            ):
                __log__.warning(f"Looking for releases in {self._prodRPMReleaseDir}")
                # Getting the prefix of out RPM
                prefix = self.getRPMName(norelease=True)
                # Now getting the list of already released versions
                allfiles = [
                    f
                    for f in os.listdir(self._prodRPMReleaseDir)
                    if f.startswith(prefix)
                ]
                # If the list is empty, release number is "1"...
                if len(allfiles) == 0:
                    __log__.warning(
                        "Did not find any releases in the directory - Release number is 1"
                    )
                    self._lhcb_release_version = 1
                else:
                    __log__.warning(
                        f"Found {len(allfiles)} files matching checking latest release"
                    )
                    allrels = []
                    # Getting the releae numbers from the files found
                    for f in allfiles:
                        m = re.match(r"-(\d+)\.", f[len(prefix) :])
                        if m != None:
                            allrels.append(int(m.group(1)))
                        else:
                            __log__.warning(
                                f"Released RPM {f} does not abide by naming convention for release"
                            )

                    # Now checking the latest one and increase number
                    newrel = sorted(allrels)[-1] + 1
                    __log__.warning(f"New release is {newrel}")
                    self._lhcb_release_version = newrel

            else:
                # In the case the directory does not exist, still set it to one...
                self._lhcb_release_version = 1


#
# Spec for shared RPMs
#
###############################################################################
class LHCbSharedRpmSpec(LHCbBaseRpmSpec):
    """Class representing the Spec file for an RPM containing the shared files for the project"""

    def __init__(self, project, version, sharedTar, buildarea, manifest=None):
        """Constructor"""
        super().__init__(project, version)
        __log__.debug(f"Creating Shared RPM for {project}/{version}")
        self._project = project
        self._version = version
        self._sharedTar = sharedTar
        self._buildarea = buildarea
        self._lhcb_maj_version = 1
        self._lhcb_min_version = 0
        self._lhcb_patch_version = 0
        self._lhcb_release_version = 0
        self._arch = "noarch"
        self._manifest = manifest

    def getArch(self):
        """Return the architecture, always noarch for our packages"""
        return self._arch

    def getRPMName(self, norelease=False, norpmver=False):
        """Return the architecture, always noarch for our packages"""
        projname = "_".join([self._project.upper(), self._version])
        projver = ".".join(
            [
                str(n)
                for n in [
                    self._lhcb_maj_version,
                    self._lhcb_min_version,
                    self._lhcb_patch_version,
                ]
            ]
        )
        if norpmver:
            return projname
        if norelease:
            return "-".join([projname, projver])
        full = "-".join([projname, projver, str(self._lhcb_release_version)])
        final = ".".join([full, self._arch, "rpm"])
        return final

    def _createHeader(self):
        """
        Prepare the RPM header
        """
        header = Template(
            """%define lhcb_maj_version ${lhcb_maj_version}
%define lhcb_min_version ${lhcb_min_version}
%define lhcb_patch_version ${lhcb_patch_version}
%define lhcb_release_version ${lhcb_release_version}
%define buildarea ${buildarea}
%define project ${project}
%define projectUp ${projectUp}
%define lbversion ${version}

%global __os_install_post /usr/lib/rpm/check-buildroot

%define _topdir %{buildarea}/rpmbuild
%define tmpdir %{buildarea}/tmpbuild
%define _tmppath %{buildarea}/tmp

Name: %{projectUp}_%{lbversion}
Version: %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Release: %{lhcb_release_version}
Vendor: LHCb
Summary: %{project}
License: GPL
Group: LHCb
BuildRoot: %{tmpdir}/%{name}-buildroot
BuildArch: noarch
AutoReqProv: no
Prefix: /opt/LHCbSoft
Provides: /bin/sh
Provides: %{projectUp}_%{lbversion} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}

"""
        ).substitute(
            buildarea=self._buildarea,
            project=self._project,
            projectUp=self._project.upper(),
            version=self._version,
            lhcb_maj_version=self._lhcb_maj_version,
            lhcb_min_version=self._lhcb_min_version,
            lhcb_patch_version=self._lhcb_patch_version,
            lhcb_release_version=self._lhcb_release_version,
        )

        return header

    def _createRequires(self):
        """
        Prepare the Requires section of the RPM
        """

        tmp = ""
        # Dependencies to LHCb projects
        if self._manifest != None:
            for dproject, origversion in self._manifest.getUsedProjects():
                dvcersion = convertToLHCbClassicVersion(origversion)
                if is_platform_independent(dproject, dversion):
                    tmp += f"Requires: {dproject.upper()}_{dversion}\n"
                else:
                    raise Exception(
                        "Platform independent project cannot depend on a platform dependent one"
                    )
        return tmp

    def _createDescription(self):
        """
        Prepare the Requires section of the RPM
        """
        tmp = "%description\n"
        tmp += "%{project}\n\n"
        return tmp

    def _createInstall(self):
        """
        Prepare the Install section of the RPM
        """
        spec = "%install\n"
        spec += "mkdir -p ${RPM_BUILD_ROOT}/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}\n"
        if self._sharedTar != None:
            spec += f"cd  ${{RPM_BUILD_ROOT}}/opt/LHCbSoft/lhcb && unzip -q -o {self._sharedTar}"
        else:
            spec += f"cd  ${{RPM_BUILD_ROOT}}/opt/LHCbSoft/lhcb && getpack --no-eclipse-config --no-config -P -r {self._project: } {self._version}"

        spec += "\n\n"
        return spec

    def _createTrailer(self):
        """
        Prepare the RPM header
        """
        trailer = Template(
            """
%post

%postun

%clean

%files
%defattr(-,root,root)
/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}

%define date    %(echo `LC_ALL=\"C\" date +\"%a %b %d %Y\"`)

%changelog

* %{date} User <ben.couturier..rcern.ch>
- first Version
"""
        ).substitute(
            buildarea=self._buildarea,
            project=self._project,
            projectUp=self._project.upper(),
            version=self._version,
        )

        return trailer


#
# Spec for Extra shared RPMs
#
###############################################################################
class LHCbExtraSharedRpmSpec(LHCbBaseRpmSpec):
    """Class representing the Spec file for an RPM containing the shared files for the project"""

    def __init__(self, project, version, sharedTar, buildarea):
        """Constructor"""
        super().__init__(project, version)
        __log__.debug(f"Creating Shared RPM for {project}/{version}")
        self._project = project
        self._version = version
        self._sharedTar = sharedTar
        self._buildarea = buildarea
        self._lhcb_maj_version = 1
        self._lhcb_min_version = 0
        self._lhcb_patch_version = 0
        self._lhcb_release_version = 0
        self._arch = "noarch"

    def getArch(self):
        """Return the architecture, always noarch for our packages"""
        return self._arch

    def getRPMName(self, norelease=False, norpmver=False):
        """Return the architecture, always noarch for our packages"""
        projname = "_".join([self._project.upper(), self._version, "shared"])
        projver = ".".join(
            [
                str(n)
                for n in [
                    self._lhcb_maj_version,
                    self._lhcb_min_version,
                    self._lhcb_patch_version,
                ]
            ]
        )
        if norpmver:
            return projname
        if norelease:
            return "-".join([projname, projver])
        full = "-".join([projname, projver, str(self._lhcb_release_version)])
        final = ".".join([full, self._arch, "rpm"])
        return final

    def _createHeader(self):
        """
        Prepare the RPM header
        """
        header = Template(
            """
%define lhcb_maj_version ${lhcb_maj_version}
%define lhcb_min_version ${lhcb_min_version}
%define lhcb_patch_version ${lhcb_patch_version}
%define lhcb_release_version ${lhcb_release_version}
%define buildarea ${buildarea}
%define project ${project}
%define projectUp ${projectUp}
%define lbversion ${version}

%global __os_install_post /usr/lib/rpm/check-buildroot

%define _topdir %{buildarea}/rpmbuild
%define tmpdir %{buildarea}/tmpbuild
%define _tmppath %{buildarea}/tmp

Name: %{projectUp}_%{lbversion}_shared
Version: %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Release: %{lhcb_release_version}
Vendor: LHCb
Summary: %{project}
License: GPL
Group: LHCb
BuildRoot: %{tmpdir}/%{name}-buildroot
BuildArch: noarch
AutoReqProv: no
Prefix: /opt/LHCbSoft
Provides: /bin/sh
Provides: %{projectUp}_%{lbversion}_shared = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}

"""
        ).substitute(
            buildarea=self._buildarea,
            project=self._project,
            projectUp=self._project.upper(),
            version=self._version,
            lhcb_maj_version=self._lhcb_maj_version,
            lhcb_min_version=self._lhcb_min_version,
            lhcb_patch_version=self._lhcb_patch_version,
            lhcb_release_version=self._lhcb_release_version,
        )

        return header

    def _createRequires(self):
        """
        Prepare the Requires section of the RPM
        """
        return ""

    def _createDescription(self):
        """
        Prepare the Requires section of the RPM
        """
        tmp = "%description\n"
        tmp += "%{project}\n\n"
        return tmp

    def _createInstall(self):
        """
        Prepare the Install section of the RPM
        """
        spec = "%install\n"
        spec += "mkdir -p ${RPM_BUILD_ROOT}/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}\n"
        if self._sharedTar != None:
            spec += f"cd  ${{RPM_BUILD_ROOT}}/opt/LHCbSoft/lhcb && unzip -q -o {self._sharedTar}"
        else:
            spec += f"cd  ${{RPM_BUILD_ROOT}}/opt/LHCbSoft/lhcb && getpack --no-eclipse-config --no-config -P -r {self._project: } {self._version}"

        spec += "\n\n"
        return spec

    def _createTrailer(self):
        """
        Prepare the RPM header
        """
        trailer = Template(
            """
%post

%postun

%clean

%files
%defattr(-,root,root)
/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}

%define date    %(echo `LC_ALL=\"C\" date +\"%a %b %d %Y\"`)

%changelog

* %{date} User <ben.couturier..rcern.ch>
- first Version
"""
        ).substitute(
            buildarea=self._buildarea,
            project=self._project,
            projectUp=self._project.upper(),
            version=self._version,
        )

        return trailer


#
# Spec for binary RPMs
#
###############################################################################
class LHCbBinaryRpmSpec(LHCbBaseRpmSpec):
    """Class representing a LHCb project"""

    def __init__(self, project, version, cmtconfig, buildarea, buildlocation, manifest):
        """Constructor taking the actual file name"""
        super().__init__(project, version)
        __log__.debug(f"Creating RPM for {project}/{version}/{cmtconfig}")
        self._project = project
        self._cmtconfig = cmtconfig
        self._buildarea = buildarea
        self._buildlocation = buildlocation
        self._manifest = manifest
        # This is the version in LHCb Format
        self._version = version
        # These are used for the main version of the package
        self._lhcb_maj_version = 1
        self._lhcb_min_version = 0
        self._lhcb_patch_version = 0
        self._lhcb_release_version = 0
        self._arch = "noarch"
        self._extraRequires = []

    def addExtraRequire(self, req):
        """Add a requirement for another package to the list"""
        self._extraRequires.append(req)

    def getExtraRequires(self):
        """Add a requirement for another package to the list"""
        return "\n".join([f"Requires: {r}" for r in self._extraRequires])

    def getArch(self):
        """Return the architecture, always noarch for our packages"""
        return self._arch

    def getRPMName(self, norelease=False, norpmver=False):
        """Return the architecture, always noarch for our packages"""
        projname = "_".join(
            [self._project.upper(), self._version, self._cmtconfig.replace("-", "_")]
        )
        if norpmver:
            return projname
        projver = ".".join(
            [
                str(n)
                for n in [
                    self._lhcb_maj_version,
                    self._lhcb_min_version,
                    self._lhcb_patch_version,
                ]
            ]
        )
        if norelease:
            return "-".join([projname, projver])
        full = "-".join([projname, projver, str(self._lhcb_release_version)])
        final = ".".join([full, self._arch, "rpm"])
        return final

    def _createHeader(self):
        """
        Prepare the RPM header
        """
        header = Template(
            """
%define _binaries_in_noarch_packages_terminate_build   0
%define lhcb_maj_version ${lhcb_maj_version}
%define lhcb_min_version ${lhcb_min_version}
%define lhcb_patch_version ${lhcb_patch_version}
%define lhcb_release_version ${lhcb_release_version}
%define buildarea ${buildarea}
%define buildlocation ${buildlocation}
%define project ${project}
%define projectUp ${projectUp}
%define cmtconfig ${config}
%define lbversion ${version}
%define cmtconfigrpm ${configrpm}

%global __os_install_post /usr/lib/rpm/check-buildroot

%define _topdir %{buildarea}/rpmbuild
%define tmpdir %{buildarea}/tmpbuild
%define _tmppath %{buildarea}/tmp

Name: %{projectUp}_%{lbversion}_%{cmtconfigrpm}
Version: %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Release: %{lhcb_release_version}
Vendor: LHCb
Summary: %{project}
License: GPL
Group: LHCb
BuildRoot: %{tmpdir}/%{name}-buildroot
BuildArch: noarch
AutoReqProv: no
Prefix: /opt/LHCbSoft
Provides: /bin/sh
Requires: %{projectUp}_%{lbversion}
${extraRequires}
\n"""
        ).substitute(
            buildarea=self._buildarea,
            buildlocation=self._buildlocation,
            project=self._project,
            projectUp=self._project.upper(),
            version=self._version,
            config=self._cmtconfig,
            configrpm=self._cmtconfig.replace("-", "_"),
            rpmversion=self._version + "_" + self._cmtconfig.replace("-", "_"),
            lhcb_maj_version=self._lhcb_maj_version,
            lhcb_min_version=self._lhcb_min_version,
            lhcb_patch_version=self._lhcb_patch_version,
            lhcb_release_version=self._lhcb_release_version,
            extraRequires=self.getExtraRequires(),
        )

        return header

    def _createDataPackageDependency(self, pack, ver):
        """
        Create the correct dependency line for the package
        """
        tarBallName = "{}_{}".format(
            "PARAM" if pack in PARAM_PKGS else "DBASE", pack.replace("/", "_")
        )

        # Now parsing the version, including possible '*' and 'v*'
        if ver in ("*", "v*"):
            (major, minor, patch, gpatch) = ("*", None, None, None)
        else:
            _txt_version_style = (
                r"v([0-9\*]+)r([0-9\*]+)(?:p([0-9\*]+))?(?:g([0-9\*]+))?"
            )
            m = re.match(_txt_version_style, ver)
            if m is not None:
                (major, minor, patch, gpatch) = m.groups()
            else:
                # Case when we specify data package versions as point separated numbers
                _txt_version_point_sep = r"(\d+).(\d+)"
                m = re.match(_txt_version_point_sep, ver)
                if m is None:
                    raise Exception(
                        f"Version '{ver}' for data package {pack} is not allowed, use *, v*, vXrYpZ or X.Y"
                    )
                else:
                    (major, minor, patch, gpatch) = m.groups() + (None, None)
                    # Special case for the '0' which is translated to *
                    if minor == "0":
                        minor = "*"

        if gpatch != None:
            raise Exception(f"Data package version {ver} not handled by RPM tools")

        reqstr = None
        if major == "*":
            # In this case we do not care about the version at all
            # We omit the version from the RPM req
            reqstr = f"Requires: {tarBallName}"
        elif minor == "*":
            # Classic vXr* for data packages
            # In that case we depend on the Provides with the major version number included
            reqstr = f"Requires: {tarBallName}_v{major}"
        elif patch == "*":
            # Classic vXrYp* for data packages
            # In that case we depend on the Provides with the major and minor version numbers included
            reqstr = f"Requires: {tarBallName}_v{major}r{minor}"
        elif patch != None:
            reqstr = f"Requires: {tarBallName} = {major}.{minor}.{patch}"
        else:
            reqstr = f"Requires: {tarBallName} = {major}.{minor}"

        return reqstr + "\n"

    def _createRequires(self):
        """
        Prepare the Requires section of the RPM
        """
        tmp = ""

        # Dependencies to LHCb projects
        for dproject, origversion in self._manifest.getUsedProjects():
            dversion = convertToLHCbClassicVersion(origversion)
            if is_platform_independent(dproject, dversion):
                tmp += f"Requires: {dproject.upper()}_{dversion}\n"
            else:
                tmp += f"Requires: {dproject.upper()}_{dversion}_%{{cmtconfigrpm}}\n"
        # Dependency to LCGCMT
        tmp += self._createHEPToolsRequires()
        tmp += self._createExtToolsRequires()

        # Dependency to data packages
        for pack, ver in self._manifest.getUsedDataPackages():
            tmp += self._createDataPackageDependency(pack, ver)

        return tmp

    def _createDescription(self):
        """
        Prepare the Requires section of the RPM
        """
        tmp = "%description\n"
        tmp += "%{project}\n\n"
        return tmp

    def _createInstall(self):
        """
        Prepare the Install section of the RPM
        """
        spec = "%install\n"
        spec += "mkdir -p ${RPM_BUILD_ROOT}/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/InstallArea/%{cmtconfig}\n"
        spec += "rsync -arL %{buildlocation}/%{projectUp}/%{projectUp}_%{lbversion}/InstallArea/%{cmtconfig} ${RPM_BUILD_ROOT}/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/InstallArea/\n"
        spec += "\n\n"
        return spec

    def _createTrailer(self):
        """
        Prepare the RPM header
        """
        trailer = Template(
            """
%post

%postun

%clean

%files
%defattr(-,root,root)
/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/InstallArea/%{cmtconfig}

%define date    %(echo `LC_ALL=\"C\" date +\"%a %b %d %Y\"`)

%changelog

* %{date} User <ben.couturier..rcern.ch>
- first Version
"""
        ).substitute(
            buildarea=self._buildarea,
            project=self._project,
            projectUp=self._project.upper(),
            version=self._version,
            config=self._cmtconfig,
            configrpm=self._cmtconfig.replace("-", "_"),
            rpmversion=self._version + "_" + self._cmtconfig.replace("-", "_"),
        )

        return trailer


#
# Spec for the glimpse RPMs
#
###############################################################################
class LHCbGlimpseRpmSpec(LHCbBaseRpmSpec):
    """Class representing the Spec file for an RPM containing the shared files for the project"""

    def __init__(self, project, version, sharedTar, buildarea, manifest):
        """Constructor"""
        super().__init__(project, version)
        __log__.debug(f"Creating Shared RPM for {project}/{version}")
        self._project = project
        self._version = version
        self._sharedTar = sharedTar
        self._buildarea = buildarea
        self._lhcb_maj_version = 1
        self._lhcb_min_version = 0
        self._lhcb_patch_version = 0
        self._lhcb_release_version = 0
        self._manifest = manifest
        self._arch = "noarch"

    def getArch(self):
        """Return the architecture, always noarch for our packages"""
        return self._arch

    def getRPMName(self, norelease=False, norpmver=False):
        """Return the architecture, always noarch for our packages"""
        projname = "_".join([self._project.upper(), self._version, "index"])
        if norpmver:
            return projname
        projver = ".".join(
            [
                str(n)
                for n in [
                    self._lhcb_maj_version,
                    self._lhcb_min_version,
                    self._lhcb_patch_version,
                ]
            ]
        )
        if norelease:
            return "-".join([projname, projver])
        full = "-".join([projname, projver, str(self._lhcb_release_version)])
        final = ".".join([full, self._arch, "rpm"])
        return final

    def _createHeader(self):
        """
        Prepare the RPM header
        """
        header = Template(
            """
%define lhcb_maj_version ${lhcb_maj_version}
%define lhcb_min_version ${lhcb_min_version}
%define lhcb_patch_version ${lhcb_patch_version}
%define lhcb_release_version ${lhcb_release_version}
%define buildarea ${buildarea}
%define project ${project}
%define projectUp ${projectUp}
%define lbversion ${version}

%global __os_install_post /usr/lib/rpm/check-buildroot

%define _topdir %{buildarea}/rpmbuild
%define tmpdir %{buildarea}/tmpbuild
%define _tmppath %{buildarea}/tmp

Name: %{projectUp}_%{lbversion}_index
Version: %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Release: %{lhcb_release_version}
Vendor: LHCb
Summary: %{project} glimpse index
License: GPL
Group: LHCb
BuildRoot: %{tmpdir}/%{name}-buildroot
BuildArch: noarch
AutoReqProv: no
Prefix: /opt/LHCbSoft
Provides: /bin/sh
Provides: %{projectUp}_%{lbversion}_index = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Requires: %{projectUp}_%{lbversion}

"""
        ).substitute(
            buildarea=self._buildarea,
            project=self._project,
            projectUp=self._project.upper(),
            version=self._version,
            lhcb_maj_version=self._lhcb_maj_version,
            lhcb_min_version=self._lhcb_min_version,
            lhcb_patch_version=self._lhcb_patch_version,
            lhcb_release_version=self._lhcb_release_version,
        )

        return header

    def _createRequires(self):
        """
        Prepare the Requires section of the RPM
        """
        tmp = ""

        # Dependencies to LHCb projects
        for dproject, origversion in self._manifest.getUsedProjects():
            dversion = convertToLHCbClassicVersion(origversion)
            tmp += f"Requires: {dproject.upper()}_{dversion}_index\n"
        return tmp

    def _createDescription(self):
        """
        Prepare the Requires section of the RPM
        """
        tmp = "%description\n"
        tmp += "%{project} glimpse indices\n\n"
        return tmp

    def _createInstall(self):
        """
        Prepare the Install section of the RPM
        """
        spec = "%install\n"
        spec += "mkdir -p ${RPM_BUILD_ROOT}/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}\n"
        spec += f"cd  ${{RPM_BUILD_ROOT}}/opt/LHCbSoft/lhcb && unzip -q -o {self._sharedTar}\n"
        spec += "mv  ${RPM_BUILD_ROOT}/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/.glimpse_filenames ${RPM_BUILD_ROOT}/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/.glimpse_filenames.config"

        spec += "\n\n"
        return spec

    def _createTrailer(self):
        """
        Prepare the RPM header
        """
        ###trailer = Template('''
        trailer = """
%post

if [ "$MYSITEROOT" ]; then
PREFIX=$MYSITEROOT
else
PREFIX=%{prefix}
fi

echo "Fixing the file: ${PREFIX}/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/.glimpse_filenames.config"
REALPATH=$(cd $PREFIX/lhcb && /bin/pwd || echo $PREFIX/lhcb)
sed -e '2,$'"s|^|${REALPATH}/%{projectUp}/%{projectUp}_%{lbversion}/|" ${PREFIX}/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/.glimpse_filenames.config > ${PREFIX}/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/.glimpse_filenames

%postun

%clean

%files
%defattr(-,root,root)
/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}

%define date    %(echo `LC_ALL=\"C\" date +\"%a %b %d %Y\"`)

%changelog

* %{date} User <ben.couturier..rcern.ch>
- first Version
"""
        # ).substitute(buildarea = self._buildarea,
        #                project = self._project,
        #                projectUp = self._project.upper(),
        #                version = self._version)

        return trailer


#
# Spec for Datapackage RPMs
#
###############################################################################
class LHCbDatapkgRpmSpec(LHCbBaseRpmSpec):
    """Class representing the Spec file for an RPM containing the shared files for the project"""

    def __init__(self, project, fulldatapkg, version, sharedTar, buildarea, release=0):
        """Constructor"""
        super().__init__(project, version)
        __log__.debug(f"Creating Data Pkg RPM for {project}/{version}")
        self._project = project
        self._fulldatapkg = fulldatapkg
        if "/" in fulldatapkg:
            self._package = fulldatapkg.split("/")[-1]
        else:
            self._package = fulldatapkg
        self._normfulldatapkg = fulldatapkg.replace("/", "_")
        self._fullname = "_".join([self._project.upper(), self._normfulldatapkg])
        self._fullnameWithVer = "_".join(
            [self._project.upper(), self._normfulldatapkg, self._version]
        )
        self._versiondir = os.path.join(self._project.upper(), self._fulldatapkg)
        self._version = version
        self._sharedTar = sharedTar
        self._buildarea = buildarea
        (
            self._lhcb_maj_version,
            self._lhcb_min_version,
            self._lhcb_patch_version,
        ) = parseVersion(version)
        self._lhcb_release_version = release
        self._arch = "noarch"

    def getArch(self):
        """Return the architecture, always noarch for our packages"""
        return self._arch

    def getRPMName(self, norelease=False, norpmver=False):
        """Return the architecture, always noarch for our packages"""
        projname = "_".join(
            [self._project.upper(), self._normfulldatapkg, self._version]
        )
        if norpmver:
            return projname
        # We keep this package to 1.0.0, but the requirements map the vXrY
        projver = ".".join([str(n) for n in [1, 0, 0]])
        if norelease:
            return "-".join([projname, projver])
        full = "-".join([projname, projver, str(self._lhcb_release_version)])
        final = ".".join([full, self._arch, "rpm"])
        return final

    def _createHeader(self):
        """
        Prepare the RPM header
        """
        header = Template(
            """
%define lhcb_maj_version ${lhcb_maj_version}
%define lhcb_min_version ${lhcb_min_version}
%define lhcb_patch_version ${lhcb_patch_version}
%define lhcb_release_version ${lhcb_release_version}
%define buildarea ${buildarea}
%define project ${project}
%define projectUp ${projectUp}
%define normfulldatapkg ${normfulldatapkg}
%define fulldatapkg ${fulldatapkg}
%define fullname ${fullname}
%define fullnameWithVer ${fullnameWithVer}
%define package ${package}
%define lbversion ${version}
%define _postshell /bin/bash
%define prefix ${prefix}
%define versiondir ${versiondir}

%global __os_install_post /usr/lib/rpm/check-buildroot

%define _topdir %{buildarea}/rpmbuild
%define tmpdir %{buildarea}/tmpbuild
%define _tmppath %{buildarea}/tmp

Name: %{fullnameWithVer}
Version: 1.0.0
Release: %{lhcb_release_version}
Vendor: LHCb
Summary: %{project}
License: GPL
Group: LHCb
BuildRoot: %{tmpdir}/%{name}-buildroot
BuildArch: noarch
AutoReqProv: no
Prefix: %{prefix}
Provides: /bin/sh
Provides: /bin/bash

Provides: %{package} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{fullname} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{package}_v%{lhcb_maj_version} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{fullname}_v%{lhcb_maj_version} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{package}_v%{lhcb_maj_version}r%{lhcb_min_version} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Provides: %{fullname}_v%{lhcb_maj_version}r%{lhcb_min_version} = %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Requires: %{projectUp}_common
Requires(post): LBSCRIPTS

"""
        ).substitute(
            buildarea=self._buildarea,
            project=self._project,
            projectUp=self._project.upper(),
            normfulldatapkg=self._normfulldatapkg,
            fulldatapkg=self._fulldatapkg,
            version=self._version,
            lhcb_maj_version=self._lhcb_maj_version,
            lhcb_min_version=self._lhcb_min_version,
            lhcb_patch_version=self._lhcb_patch_version,
            lhcb_release_version=self._lhcb_release_version,
            fullname=self._fullname,
            fullnameWithVer=self._fullnameWithVer,
            versiondir=self._versiondir,
            package=self._package,
            prefix=PREFIX,
        )

        return header

    def _createRequires(self):
        """
        Prepare the Requires section of the RPM
        """
        return ""

    def _createDescription(self):
        """
        Prepare the Requires section of the RPM
        """
        tmp = "%description\n"
        tmp += "%{fullname} %{version}\n\n"
        return tmp

    def _createInstall(self):
        """
        Prepare the Install section of the RPM
        """
        spec = "%install\n"
        spec += "mkdir -p ${RPM_BUILD_ROOT}%{prefix}/lhcb/%{versiondir}\n"
        spec += (
            f"cd  ${{RPM_BUILD_ROOT}}%{{prefix}}/lhcb && unzip -q -o {self._sharedTar}"
        )
        spec += "\n\n"
        return spec

    def _createTrailer(self):
        """
        Prepare the RPM header
        """
        trailer = """

%clean

%post -p /bin/bash

if [ "$MYSITEROOT" ]; then
PREFIX=$MYSITEROOT
else
PREFIX=%{prefix}
fi

if [ -f $PREFIX/etc/update.d/%{package}_Update.py ]; then
rm -f $PREFIX/etc/update.d/%{package}_Update.py
fi

if [ -f $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/Update.py ]; then
echo "Creating link in update.d"
mkdir -p -v $PREFIX/etc/update.d
ln -s $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/Update.py $PREFIX/etc/update.d/%{package}_Update.py
echo "Running Update script"
. $PREFIX/LbEnv.sh --siteroot $PREFIX 2>/dev/null
echo "Now using python:"
which python
echo "PYTHONPATH: $PYTHONPATH"
echo "PATH: $PATH"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
python $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/Update.py
fi

if [ -f $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/PostInstall.py ]; then
echo "Running PostInstall script"
. $PREFIX/LbEnv.sh --siteroot $PREFIX 2>/dev/null
python $PREFIX/lhcb/%{versiondir}/%{lbversion}/cmt/PostInstall.py
fi

%postun -p /bin/bash
if [ "$MYSITEROOT" ]; then
PREFIX=$MYSITEROOT
else
PREFIX=%{prefix}
fi
echo "In uninstall script"
if [ -h $PREFIX/etc/update.d/%{package}_Update.py ]; then
echo "Removing link to update script:  $PREFIX/etc/update.d/%{package}_Update.py"
rm $PREFIX/etc/update.d/%{package}_Update.py
fi

%files
%defattr(-,root,root)
%{prefix}/lhcb/%{versiondir}/%{lbversion}


%define date    %(echo `LC_ALL=\"C\" date +\"%a %b %d %Y\"`)

%changelog

* %{date} User <ben.couturier..rcern.ch>
- first Version
"""

        return trailer


#
# Spec for LbScript RPM
#
###############################################################################
class LHCbLbScriptsRpmSpec(LHCbBaseRpmSpec):
    """Class representing the Spec file for an RPM containing the shared files for the project"""

    def __init__(self, project, version, sharedTar, buildarea):
        """Constructor"""
        super().__init__(project, version)
        __log__.debug(f"Creating Shared RPM for {project}/{version}")
        self._project = project
        self._version = version
        self._sharedTar = sharedTar
        self._buildarea = buildarea
        self._lhcb_maj_version = 1
        self._lhcb_min_version = 0
        self._lhcb_patch_version = 0
        self._lhcb_release_version = 0
        self._arch = "noarch"

    def getArch(self):
        """Return the architecture, always noarch for our packages"""
        return self._arch

    def getRPMName(self, norelease=False, norpmver=False):
        """Return the architecture, always noarch for our packages"""
        projname = "_".join([self._project.upper(), self._version])
        if norpmver:
            return projname
        projver = ".".join(
            [
                str(n)
                for n in [
                    self._lhcb_maj_version,
                    self._lhcb_min_version,
                    self._lhcb_patch_version,
                ]
            ]
        )
        if norelease:
            return "-".join([projname, projver])
        full = "-".join([projname, projver, str(self._lhcb_release_version)])
        final = ".".join([full, self._arch, "rpm"])
        return final

    def _createHeader(self):
        """
        Prepare the RPM header
        """
        header = Template(
            """
%define lhcb_maj_version ${lhcb_maj_version}
%define lhcb_min_version ${lhcb_min_version}
%define lhcb_patch_version ${lhcb_patch_version}
%define lhcb_release_version ${lhcb_release_version}
%define buildarea ${buildarea}
%define project ${project}
%define projectUp ${projectUp}
%define lbversion ${version}
%define _postshell /bin/bash
%define prefix ${prefix}

%global __os_install_post /usr/lib/rpm/check-buildroot

%define _topdir %{buildarea}/rpmbuild
%define tmpdir %{buildarea}/tmpbuild
%define _tmppath %{buildarea}/tmp

Name: %{projectUp}_%{lbversion}
Version: %{lhcb_maj_version}.%{lhcb_min_version}.%{lhcb_patch_version}
Release: %{lhcb_release_version}
Vendor: LHCb
Summary: %{project}
License: GPL
Group: LHCb
BuildRoot: %{tmpdir}/%{name}-buildroot
BuildArch: noarch
AutoReqProv: no
Prefix: %{prefix}
Provides: /bin/sh
Provides: /bin/bash

"""
        ).substitute(
            buildarea=self._buildarea,
            project=self._project,
            projectUp=self._project.upper(),
            version=self._version,
            lhcb_maj_version=self._lhcb_maj_version,
            lhcb_min_version=self._lhcb_min_version,
            lhcb_patch_version=self._lhcb_patch_version,
            lhcb_release_version=self._lhcb_release_version,
            prefix=PREFIX,
        )

        return header

    def _createRequires(self):
        """
        Prepare the Requires section of the RPM
        """
        return """

"""

    def _createDescription(self):
        """
        Prepare the Requires section of the RPM
        """
        tmp = "%description\n"
        tmp += "%{project} %{lbversion}\n\n"
        return tmp

    def _createInstall(self):
        """
        Prepare the Install section of the RPM
        """
        spec = "%install\n"
        spec += "mkdir -p ${RPM_BUILD_ROOT}/opt/LHCbSoft/lhcb/%{projectUp}/%{projectUp}_%{lbversion}\n"
        spec += f"cd  ${{RPM_BUILD_ROOT}}/opt/LHCbSoft/lhcb && unzip -q -o {self._sharedTar}"
        spec += "\n\n"
        return spec

    def _createTrailer(self):
        """
        Prepare the RPM header
        """
        trailer = """

%post -p /bin/bash

if [ "$MYSITEROOT" ]; then
PREFIX=$MYSITEROOT
else
PREFIX=%{prefix}
fi

if [ -f $PREFIX/etc/update.d/%{package}_Update.py ]; then
rm -f $PREFIX/etc/update.d/%{package}_Update.py
fi

if [ -f $PREFIX/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/%{project}Sys/cmt/Update.py ]; then
echo "Creating link in update.d"
mkdir -p -v $PREFIX/etc/update.d
ln -s $PREFIX/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/%{project}Sys/cmt/Update.py $PREFIX/etc/update.d/%{package}_Update.py
echo "Running Update script"
. $PREFIX/LbEnv.sh --siteroot $PREFIX 2>/dev/null
echo "Now using python:"
which python
echo "PYTHONPATH: $PYTHONPATH"
echo "PATH: $PATH"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
python $PREFIX/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/%{project}Sys/cmt/Update.py
fi

if [ -f $PREFIX/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/%{project}Sys/cmt/PostInstall.py ]; then
echo "Running PostInstall script"
export LBRPM_INSTALL=1
python $PREFIX/lhcb/%{projectUp}/%{projectUp}_%{lbversion}/%{project}Sys/cmt/PostInstall.py
fi

%postun

%clean

%files
%defattr(-,root,root)
%{prefix}/lhcb/%{projectUp}/%{projectUp}_%{lbversion}

%define date    %(echo `LC_ALL=\"C\" date +\"%a %b %d %Y\"`)

%changelog

* %{date} User <ben.couturier..rcern.ch>
- first Version
"""

        return trailer


#
# Various utilities to extract info about the build
#
###############################################################################
def splitpath(path):
    """Split a path to all its components"""
    spath = []
    while True:
        (head, tail) = os.path.split(path)
        if len(head) == 0 or len(tail) == 0:
            break
        spath.insert(0, tail)
        path = head
    return spath


def getBuildInfo(manifestFileName):
    """
    Get info about the build from the manifest filename itself
    """
    realFilename = os.path.realpath(manifestFileName)
    splitPath = splitpath(realFilename)
    if len(splitPath) < 4 or splitPath[-3] != "InstallArea":
        # The manifest is not in the standard location
        return (realFilename, None, None, None)
    else:
        barea = realFilename
        for _i in range(5):
            barea = os.path.dirname(barea)
        return (realFilename, barea, splitPath[-4], splitPath[-2])


def parseVersion(version):
    """
    Parse the version string
    """
    maj_version = 1
    min_version = 0
    patch_version = 0

    m = re.match(r"v([\d]+)r([\d]+)$", version)
    if m != None:
        maj_version = m.group(1)
        min_version = m.group(2)
    else:
        # Checking whether the version matches vXrYpZ in that case
        m = re.match(r"v([\d]+)r([\d]+)p([\d]+)", version)
        if m != None:
            maj_version = m.group(1)
            min_version = m.group(2)
            patch_version = m.group(3)
        else:
            raise Exception(f"Version {version} does not match format vXrY or vXrYpZ")

    return (maj_version, min_version, patch_version)


# Main Script to generate the spec file
#
###############################################################################
from LbNightlyTools.Scripts.Common import PlainScript


class Script(PlainScript):
    """
    Script to generate the Spec file for an LHCb project.
    """

    __usage__ = "%prog [options] <manifest.xml>"
    __version__ = ""

    def addBasicOptions(self, parser):
        """
        Add some basic (common) options to the option parser
        """
        parser.add_option(
            "-v",
            "--version",
            dest="version",
            default=None,
            action="store",
            help="Force LCG version",
        )
        parser.add_option(
            "-p",
            "--platform",
            dest="platform",
            default=None,
            action="store",
            help="Force platform",
        )
        parser.add_option(
            "-s",
            "--shared",
            dest="shared",
            default=False,
            action="store_true",
            help="Build shared RPM",
        )
        parser.add_option(
            "--shared-tar",
            dest="sharedTar",
            default=None,
            action="store",
            help="Shared tar to be included",
        )
        parser.add_option(
            "--builddir",
            dest="builddir",
            default=None,
            action="store",
            help="Force LCG dir if different from the one containing the config file",
        )
        parser.add_option(
            "-b",
            "--buildarea",
            dest="buildarea",
            default="/tmp",
            action="store",
            help="Force build root",
        )
        parser.add_option(
            "-o",
            "--output",
            dest="output",
            default=None,
            action="store",
            help="File name for the generated specfile [default output to stdout]",
        )
        return parser

    def defineOpts(self):
        """
        Prepare the option parser.
        """
        self.addBasicOptions(self.parser)

    def createBuildDirs(self, buildarea, buildname):
        """
        Create directories necessary to the build
        """
        self.topdir = f"{buildarea}/rpmbuild"
        self.tmpdir = f"{buildarea}/tmpbuild"
        self.rpmtmp = f"{buildarea}/tmp"
        self.srcdir = os.path.join(self.topdir, "SOURCES")
        self.rpmsdir = os.path.join(self.topdir, "RPMS")
        self.srpmsdir = os.path.join(self.topdir, "SRPMS")
        self.builddir = os.path.join(self.topdir, "BUILD")

        # And creating them if needed
        for d in [self.rpmtmp, self.srcdir, self.rpmsdir, self.srpmsdir, self.builddir]:
            if not os.path.exists(d):
                os.makedirs(d)

        self.buildroot = os.path.join(self.tmpdir, f"{buildname}-buildroot")

        if not os.path.exists(self.buildroot):
            os.makedirs(self.buildroot)

    def main(self):
        """
        Main method for the script
        """
        if len(self.args) != 1:
            self.parser.error("wrong number of arguments")

        # Extracting info from filename
        filename = self.args[0]
        self.log.warning(f"Processing file {filename}")
        (_absFilename, buildlocation, _fprojectVersion, _fcmtconfig) = getBuildInfo(
            filename
        )

        # Parsing the XML itself
        from LbTools.Manifest import Parser

        manifest = Parser(filename)

        (project, version) = manifest.getProject()
        (_LCGVerson, cmtconfig, _packages) = manifest.getHEPTools()
        (lcg_platform, lcg_system) = manifest.getLCGConfig()

        buildarea = self.options.buildarea
        self.createBuildDirs(buildarea, project + "_" + version + "_" + cmtconfig)
        if self.options.shared:
            spec = LHCbSharedRpmSpec(
                project, version, self.options.sharedTar, buildarea
            )
        elif self.options.glimpse:
            spec = LHCbGlimpseRpmSpec(
                project, version, self.options.sharedTar, buildarea, manifest
            )
        else:
            spec = LHCbBinaryRpmSpec(
                project, version, cmtconfig, buildarea, buildlocation, manifest
            )

        if self.options.output:
            with open(self.options.output, "w") as outputfile:
                outputfile.write(spec.getSpec())
        else:
            print(spec.getSpec())

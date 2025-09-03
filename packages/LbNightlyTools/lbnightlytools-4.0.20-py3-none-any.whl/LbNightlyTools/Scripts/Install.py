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
Module containing the classes and functions used install in a directory the
products of a nightly build.
"""
__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

import html.parser
import json
import logging
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from socket import gethostname
from subprocess import PIPE, STDOUT, Popen, call
from tempfile import mkstemp

try:
    from urllib.parse import urlparse, urlunparse
except ImportError:  # Python2
    from urllib.parse import urlparse, urlunparse

ARTIFACTS_URL = "https://lhcb-nightlies-artifacts.web.cern.ch/lhcb-nightlies-artifacts"
ARTIFACTS_URL_XROOTD = (
    "root://eosproject.cern.ch//eos/project/l/lhcbwebsites/www/lhcb-nightlies-artifacts"
)

CHECK_SSL = True


def urlopen(url):
    """
    Wrapper for urllib2.urlopen to enable or disable SSL verification.
    """
    if not CHECK_SSL and sys.version_info >= (2, 7, 9):
        # with Python >= 2.7.9 SSL certificates are validated by default
        # but we can ignore them
        from ssl import PROTOCOL_SSLv23, SSLContext

        return urllib.request.urlopen(url, context=SSLContext(PROTOCOL_SSLv23))
    return urllib.request.urlopen(url)


def _list_http(url):
    """
    Implementation of listdir for HTTP.

    The HTTP server must allow listing of directories with the typical Apache
    format.
    """
    if url.startswith(ARTIFACTS_URL):
        try:
            return _list_xrootd(url.replace(ARTIFACTS_URL, ARTIFACTS_URL_XROOTD))
        except Exception:
            pass

    class ListHTMLParser(html.parser.HTMLParser):
        """
        Specialized HTML parser to extract the list of files from standard
        Apache directory listing.
        """

        # pylint: disable=R0904
        def __init__(self):
            html.parser.HTMLParser.__init__(self)
            self.data = []
            self._href = None
            self._text = ""

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                attrs = dict(attrs)
                self._href = attrs.get("href")
                self._text = ""

        def handle_data(self, data):
            if self._href:
                self._text += data

        def handle_endtag(self, tag):
            if tag == "a":
                # ignore special entries like sorting links ("?...") or link to
                # parent directory
                if (
                    self._href
                    and "?" not in self._href
                    and "parent directory" not in self._text.lower()
                ):
                    self.data.append(self._href)
                self._href = None
                self._text = ""

    parser = ListHTMLParser()
    parser.feed(urlopen(url).read().decode("utf-8", errors="replace"))
    return parser.data


def _list_ssh(url):
    """
    Implementation of listdir for SSH.
    """
    host, path = url.split(":", 1)
    proc = Popen(["ssh", host, f"ls -a1 {path!r}"], stdout=PIPE)
    return proc.communicate()[0].decode("utf-8", errors="replace").splitlines()


def _list_xrootd(url):
    """
    List a directory using "xrdfs .. ls ..."
    """
    u = urlparse(url)
    proc = Popen(
        ["xrdfs", urlunparse((u.scheme, u.netloc, "", "", "", "")), "ls", u.path],
        stdout=PIPE,
    )
    root = u.path if u.path.endswith("/") else (u.path + "/")
    # "xrdfs ls" always returns full path, so we have to strip that part
    return [
        f.replace(root, "")
        for f in proc.communicate()[0].decode("utf-8", errors="replace").splitlines()
    ]


def _url_protocol(url):
    """
    @return the protocol id of the given URL
    """
    if re.match(r"https?://", url):
        return "http"
    elif url.startswith("root://"):
        return "root"
    elif re.match(r"([a-z0-9]+@)?[a-z][a-z0-9.]*:", url):
        return "ssh"
    else:
        return "file"


def listdir(url):
    """
    @return the list of entries in a directory, being it over HTTP, ssh or
            local filesystem.
    """
    protocol = _url_protocol(url)
    listing = {
        "http": _list_http,
        "ssh": _list_ssh,
        "root": _list_xrootd,
        "file": os.listdir,
    }[protocol](url)
    return sorted(listing)


def getURL(url, dst):
    """
    Generic URL retriever with support for 'http:', 'file:' and 'ssh:'
    protocols.
    """
    protocol = _url_protocol(url)

    def getHTTP(url, dst):
        """Retrieve from 'http:'."""
        # code copied from shutil.copyfile
        fsrc = None
        fdst = None
        if url.startswith(ARTIFACTS_URL):
            try:
                return getXRootD(url.replace(ARTIFACTS_URL, ARTIFACTS_URL_XROOTD), dst)
            except Exception:
                pass
        try:
            fsrc = urlopen(url)
            with open(dst, "wb") as fdst:
                shutil.copyfileobj(fsrc, fdst)
        finally:
            if fsrc:
                fsrc.close()

    def getSSH(url, dst):
        """Retrieve from 'ssh:'."""
        call(["scp", "-q", url, dst])

    def getXRootD(url, dst):
        call(["xrdcp", "--force", "--nopbar", url, dst])

    return {
        "http": getHTTP,
        "ssh": getSSH,
        "root": getXRootD,
        "file": shutil.copy2,
    }[
        protocol
    ](url, dst)


def unpack(url, dest, exclude=None):
    """
    Unpack a tarball from 'url' into the directory 'dest'.
    """
    # download on a local file
    log = logging.getLogger("unpack")
    protocol = _url_protocol(url)
    tmpfd = None
    if exclude is None:
        exclude = []
    try:
        if protocol != "file":
            tmpfd, tmpname = mkstemp()
            os.close(tmpfd)
            log.info("retrieving %s", url)
            log.debug("using tempfile %s", tmpname)
            getURL(url, tmpname)
        else:
            tmpname = os.path.abspath(url)
        log.info("unpacking %s", url)
        if url.endswith(".tar.bz2"):
            retcode = call(
                ["tar", "-x", "-f", tmpname] + [f"--exclude={n}" for n in exclude],
                cwd=dest,
            )
        elif url.endswith(".zip"):
            cmd = ["unzip", "-q", "-o", tmpname]
            for n in exclude:
                cmd.extend(["-x", n])
            retcode = call(cmd, cwd=dest)

    finally:
        if tmpfd is not None:
            os.remove(tmpname)
    return retcode


def install(url, dest, exclude=None):
    """
    Install the file at 'url' in the directory 'dest'.

    If url points to a tarball, it is unpacked, otherwise it is just copied.
    """
    log = logging.getLogger("install")
    if not os.path.exists(dest):
        log.info('creating directory "%s"', dest)
        os.makedirs(dest)
    if url.endswith(".tar.bz2") or url.endswith(".zip"):
        return unpack(url, dest, exclude)
    else:
        log.info("installing %s", url)
        return getURL(url, os.path.join(dest, url.rsplit("/", 1)[1]))


def getDependencies(projects, slot_configuration):
    """Extract dependencies of a list of projects,
    using the slot configuration passed"""

    needed_projects = set()
    log = logging.getLogger("getDependencies")

    # Iterating over the projects
    for proj in projects:
        # First check the configuration
        proj_lower = proj.lower()
        pdata = None
        for cp in slot_configuration.get("projects", []) + slot_configuration.get(
            "packages", []
        ):
            # Comparing lower case to be sure...
            if cp["name"].lower() == proj_lower:
                pdata = cp
                break

        # If pdata still None, we have a problem...
        if pdata == None:
            raise Exception(f"Project {proj} not in slot metadata")

        # Looking up the project/dependency info
        pdeps = pdata.get("dependencies", [])

        # Adding the direct deps to the set
        for dep in pdeps:
            log.debug(f"{proj_lower} depends on {dep}")
            needed_projects.add(dep)

        # check for extra packages in container projects:
        needed_projects |= {
            pack["name"]
            for pack in slot_configuration.get("packages", [])
            if pack.get("container", "").lower() == proj_lower
        }

        # Now looking for transitive deps and adding dependencies
        alldeps = getDependencies(pdeps, slot_configuration)
        needed_projects |= alldeps

    return needed_projects


def requiredPackages(
    files,
    slot=None,
    build_id=None,
    projects=None,
    platforms=None,
    skip=None,
    metadataurl=None,
    add_dependencies=True,
):
    """
    Extract from the list of tarballs those that need to be installed considering
    the list of requested projects (default: all of them), platforms (default:
    all of them) and what to skip (default: nothing).
    """
    log = logging.getLogger("requiredPackages")

    if skip is None:
        skip = set()
    else:
        skip = set(skip)
    if projects:
        # change to lowercase to make the check case-insensitive
        projects = [p.lower() for p in projects]

    # Checking that we have the right info for the dependencies
    if add_dependencies and metadataurl == None:
        raise Exception("Dependency analysis requires slot configuration URL")

    slot_configuration = None
    # Getting the project metadata
    if metadataurl != None:
        try:
            tmpfd, tmpname = mkstemp()
            os.close(tmpfd)
            log.info("retrieving %s", metadataurl)
            log.debug("using tempfile %s", tmpname)
            getURL(metadataurl, tmpname)
            slot_configuration = json.load(open(tmpname))
        finally:
            os.remove(tmpname)

    # Actually getting the dependencies and merging them with the project list
    if add_dependencies and projects is not None:
        allprojects = getDependencies(projects, slot_configuration)
        for proj in allprojects:
            if proj not in projects:
                log.debug(f"Adding {proj} to the list of projects")
                projects.append(proj.lower())

    build_id = str(slot_configuration.get("build_id", build_id))

    if projects:
        # data packages may have '/' in the name, which is converted in '_'
        # in the tarball filename
        projects = {p.replace("/", "_") for p in projects}

    for filename in files:
        # file names have the format
        #   <project>.<version>.<tag.id>.<platform>{.zip,.tar.bz2}
        ext = ".zip" if filename.endswith(".zip") else ".tar.bz2"
        tokens = os.path.basename(filename[: -len(ext)]).split(".", 4)
        slot_tmp, build_id_tmp, project, platform = (
            tokens[2],
            tokens[3],
            tokens[0],
            tokens[-1],
        )
        if len(tokens) > 4 and (slot_tmp != slot or build_id_tmp != build_id):
            continue
        if projects is None or project.lower() in projects:
            if platforms is None or platform in platforms:
                if filename not in skip:
                    yield filename


def findGlimpseFilenames(path):
    """
    Give a top directory, return the iterator over all the .glimpse_filenames
    files that can be found (excluding some special directories).
    """
    excluded_dirs = {
        "DOC",
        "docs",
        "scripts",
        "scripts.old",
        "DBASE",
        "PARAM",
        "TOOLS",
        "XmlEditor",
    }
    log = logging.getLogger("findGlimpseFilenames")
    path = os.path.abspath(path)
    log.debug("Looking for .glimpse_filenames in %s", path)
    for root, dirs, files in os.walk(path):
        if ".glimpse_filenames" in files:
            yield os.path.join(root, ".glimpse_filenames")
            # do not enter subdirectories (we assume no nested indexes)
            dirs[:] = []
        elif "Makefile" in files:
            # do not descend the projects substructure
            dirs[:] = []
        else:
            # do not descend the known special directories
            dirs[:] = list(set(dirs) - excluded_dirs)


def fixGlimpseIndexes(iterable):
    """
    Give a list of of paths to .glimpse_filenames files, replace the relative
    paths with absolute ones.
    """
    log = logging.getLogger("fixGlimpseIndexes")
    log.debug("Fixing .glimpse_filenames")
    for filename in iterable:
        log.debug(" - %s", filename)
        f = open(filename)
        lines = f.readlines()
        f.close()
        root = os.path.dirname(filename)
        # join the file directory on all the lines except the first one
        # (it's a number)
        lines = lines[:1] + [os.path.join(root, l) for l in lines[1:]]
        f = open(filename, "w")
        f.writelines(lines)
        f.close()


def createVersionSymlinks(dest, config):
    from os import symlink
    from os.path import exists, join
    from re import MULTILINE, search

    def makeVersionLink(dest, name, version):
        tgt = join(dest, f"{name}_{version}")
        if not exists(tgt):
            logging.debug("creating %s", tgt)
            symlink(name, tgt)

    for project in config.get("projects", []):
        name = project.get("name")
        version = project.get("version")
        if name and version != "None" and exists(join(dest, name)):
            makeVersionLink(dest, name, version)
            # look for the declared project version
            try:
                with open(join(dest, name, "CMakeLists.txt")) as cml:
                    data = "".join(l for l in cml if not l.lstrip().startswith("#"))

                version = None
                # try old style CMake configuration
                version_match = search(
                    r"gaudi_project\(\s*[^\s)]+\s+([^\s)]+)\s*[^)]*\)", data, MULTILINE
                )
                if version_match:
                    version = version_match.group(1)
                else:  # try new style CMake configuration
                    version_match = search(
                        r"project\(\s*[^\s)]+\s+VERSION\s+([\d.]+)\s*[^)]*\)",
                        data,
                        MULTILINE,
                    )
                    if version_match:  # map X.Y.Z to vXrYpZ
                        version = "".join(
                            a + b
                            for a, b in zip("vrp", version_match.group(1).split("."))
                        )

                if version:
                    makeVersionLink(dest, name, version)
                else:
                    logging.debug(
                        "version not found in %s", join(dest, name, "CMakeLists.txt")
                    )
            except OSError:
                pass  # ignore failures reading the CMakeLists.txt


from LbNightlyTools.Scripts.Common import PlainScript


class Script(PlainScript):
    """
    Script to install a in a directory a nightly build or a part of it.
    """

    __usage__ = "%prog [options] slot-name[ |.|/]build-id"
    __version__ = ""

    def defineOpts(self):
        parser = self.parser
        parser.add_option(
            "--artifacts-root",
            action="store",
            metavar="URI",
            help="URL or directory where the build artifacts can "
            "be found [default: %default]",
        )
        parser.add_option(
            "--flavour",
            action="store",
            help="nightly build flavour to use " "[default: %default]",
        )
        parser.add_option(
            "--projects",
            action="store",
            help="comma-separated list of projects to install " "[default: all]",
        )
        parser.add_option(
            "--platforms",
            action="store",
            help="comma-separated list of platforms to install "
            '(the special platform "src" is always included '
            'and "shared" is included if "src" is not '
            "the only specified platform)"
            " [default: all]",
        )
        parser.add_option(
            "--dest",
            action="store",
            help="directory where to install the artifacts "
            "[default: <slot-name>/<build-id>]",
        )

        parser.add_option(
            "--nodeps",
            action="store_true",
            help="Disable the download of dependencies for a project "
            "[default: False]",
            default=False,
        )

        parser.add_option(
            "-k",
            "--insecure",
            action="store_true",
            help="skip SSL validation",
            default=False,
        )

        parser.add_option(
            "--no-git",
            action="store_true",
            help='do not extract ".git" directories from tarfiles',
        )

        parser.add_option(
            "--with-git",
            action="store_false",
            dest="no_git",
            help='do extract ".git" directories from tarfiles',
        )

        parser.add_option(
            "--no-build-dir",
            action="store_true",
            help='do not extract "build" directories from (binary) tarfiles',
        )

        parser.add_option(
            "--with-build-dir",
            action="store_false",
            dest="no_build_dir",
            help='do extract "build" directories from (binary) tarfiles',
        )

        parser.add_option(
            "-j",
            "--jobs",
            help="number of parallel download+unpack jobs to use [default: -1, all CPUs]",
        )

        parser.set_defaults(
            artifacts_root=ARTIFACTS_URL,
            flavour="nightly",
            no_git=False,
            no_build_dir=True,
            jobs="-1",
        )

    def main(self):
        from joblib import Parallel, delayed

        # split the 'comma-separated list' options
        opts = self.options
        if opts.projects:
            opts.projects = [v.strip() for v in opts.projects.split(",")]
        if opts.platforms:
            opts.platforms = [v.strip() for v in opts.platforms.split(",")]
            if opts.platforms != ["src"]:
                opts.platforms.append("shared")  # ensure that 'src' is included
            opts.platforms.append("src")  # ensure that 'src' is included

        try:
            if len(self.args) == 1:
                self.args = self.args[0].split("." if "." in self.args[0] else "/")
            slot, build_id = self.args
        except ValueError:
            self.parser.error("wrong number of arguments")

        if opts.insecure:
            global CHECK_SSL
            CHECK_SSL = False
            self.log.debug("ignoring SSL certificates")

        dest = opts.dest or os.path.join(slot, build_id)
        if not os.path.exists(dest):
            self.log.debug(f"creating directory {dest}")
            os.makedirs(dest)

        url = "/".join([opts.artifacts_root, opts.flavour, slot, build_id])
        history_file = os.path.join(dest, ".installed")

        # URL for the slot-config file used to get the dependencies
        metadataurl = "/".join([url, "slot-config.json"])

        lock_file = os.path.join(dest, ".lock")
        self.log.debug("check for lock file %s", lock_file)
        for _ in range(30):
            if not os.path.exists(lock_file):
                break
            time.sleep(10)
        else:
            # the log file is still there: give up
            try:
                pid, timestamp = open(lock_file).readline().strip().split(":", 1)
                self.log.error(
                    "lockfile %s still present " "(generated by pid %s on %s)",
                    lock_file,
                    pid,
                    timestamp,
                )
                return 2
            except OSError:
                # if we cannot read the file, probably it just disappeared
                pass
            except ValueError:
                # the lock file looks invalid, we can ignore it
                pass

        f = open(lock_file, "w")
        f.write(f"{os.getpid()}@{gethostname()}:{datetime.now().isoformat()}\n")
        f.close()
        self.log.debug("created lock file %s", lock_file)

        try:
            # when lbn-install is asked to install some projects, we expect
            # that the tarfiles for those projects are available
            expected_files_patterns = [
                re.compile(f".*/{re.escape(project)}\\..*\\.{re.escape(platform)}\\.")
                for project in (opts.projects or [])
                for platform in (opts.platforms or [])
                if platform != "shared"  # the shared pack is optional
                and project.upper() not in ("DBASE", "PARAM")  # ignore data projects
            ]
            tarfiles = [
                f"packs/{subdir}/{f}"
                for subdir in listdir(url + "/packs")
                for f in listdir(url + "/packs/" + subdir)
                if f.endswith(".tar.bz2") or f.endswith(".zip")
            ]
            # check that all expected patterns have a match in the list of tarfiles
            missing_patterns = [
                rex.pattern
                for rex in expected_files_patterns
                if not any(rex.match(f) for f in tarfiles)
            ]
            # if one is missing it's a fatal error
            if missing_patterns:
                raise RuntimeError(
                    "expected in the artifacts files matching the patterns {}".format(
                        ", ".join(f"r'{p}'" for p in missing_patterns)
                    )
                )

            installed = {}
            if os.path.exists(history_file):
                installed = dict([l.strip().split(":", 1) for l in open(history_file)])
            tarfiles = requiredPackages(
                tarfiles,
                slot,
                build_id,
                opts.projects,
                opts.platforms,
                installed,
                metadataurl,
                add_dependencies=not opts.nodeps,
            )

            required_files = list(tarfiles)  # tarfiles is a generator (so far)
            required_files.append("slot-config.json")
            # add required non-zip files
            other_files = {
                "configuration.xml",
                "confSummary.py",
                "searchPath.cmake",
                "slot.patch",
            }
            already_installed = set(installed)
            required_files.extend(
                other_files.intersection(listdir(url)) - already_installed
            )
            if required_files:
                self.log.info("installing %d files", len(required_files))
            else:
                self.log.info("nothing to install")

            # search for indexes already present so that we can skip fixing them
            pre_existing_indexes = set(findGlimpseFilenames(dest))

            index_installed = False

            def do_install(f):
                """Worker function for running the installation

                When one process fails all the other running processes are
                killed. This results in the "finally:" blocks not being called
                and the temporary files are left hanging around.

                Instead return a tuple of (status, result) where status is a
                boolean representing if the install was successful. If the
                install failed, result is an exception that should be raised.
                """
                exclude_list = []
                if opts.no_git:
                    exclude_list.append("*/.git/*")
                if opts.no_build_dir:
                    exclude_list.append("*/build/*")
                # Glitches are common so retry up to three times
                for i in range(3):
                    if install(
                        url + "/" + f, dest, exclude=exclude_list
                    ):  # 0 or None mean success
                        status, result = False, RuntimeError(f"error installing {f}")
                    else:
                        status, result = True, (f, datetime.now().isoformat())
                        break
                return status, result

            installed = {}
            for status, result in Parallel(n_jobs=int(opts.jobs) or 1)(
                delayed(do_install)(f) for f in required_files
            ):
                if status:
                    installed[result[0]] = result[1]
                else:
                    raise result

            for f in installed:
                # record what has been installed so far
                with open(history_file, "w") as histfile:
                    histfile.writelines(
                        ["{}:{}\n".format(*i) for i in sorted(installed.items())]
                    )
                if "index" in f:
                    index_installed = True
            if os.path.exists(os.path.join(dest, "slot.patch")):
                self.log.warning(
                    "Applying patch file: {}".format(os.path.join(dest, "slot.patch"))
                )
                command = ["patch", "-p1", "-f", "-i", "slot.patch"]
                proc = Popen(command, cwd=dest, stdout=PIPE, stderr=STDOUT)
                out, _ = proc.communicate()
                self.log.debug(
                    "output of %s:\n%s", command, out.decode("utf-8", errors="replace")
                )

            if index_installed:
                fixGlimpseIndexes(
                    f
                    for f in findGlimpseFilenames(dest)
                    if f not in pre_existing_indexes
                )

            # if 'confSummary.py' was just installed and actually exists,
            # we use it to generate a setup script for the CMTPROJECTPATH.
            if (
                "confSummary.py" in installed
                and "confSummary.py" not in already_installed
                and os.path.exists(os.path.join(dest, "confSummary.py"))
            ):
                # generate shell script equivalents
                data = {}
                exec(open(os.path.join(dest, "confSummary.py")).read(), data)
                search_path = data.get("cmtProjectPathList", [])
                # we need to prepend the installation directory
                search_path.insert(0, os.path.abspath(dest))
                # write bash script
                shell_name = os.path.join(dest, "setupSearchPath.sh")
                self.log.info("writing %s", shell_name)
                with open(shell_name, "w") as shell_script:
                    shell_script.write(
                        "export CMTPROJECTPATH={}\n".format(":".join(search_path))
                    )
                # write tcsh script
                shell_name = os.path.join(dest, "setupSearchPath.csh")
                self.log.info("writing %s", shell_name)
                with open(shell_name, "w") as shell_script:
                    shell_script.write(
                        "setenv CMTPROJECTPATH {}\n".format(":".join(search_path))
                    )

            # Create symlinks required to make lb-run work
            try:
                self.log.info("create version symlinks")
                createVersionSymlinks(
                    dest, json.load(open(os.path.join(dest, "slot-config.json")))
                )
            except OSError:
                pass  # could not read slot-config.json or create the links

        except Exception as ex:
            self.log.error(f"Fatal error: {ex}")
            if logging.getLogger().level <= logging.DEBUG:
                # re-raise the exception in debug mode
                raise
            return 1

        finally:
            # this is call even after an exception or a return
            self.log.debug("removing lock file %s", lock_file)
            os.remove(lock_file)

        return 0

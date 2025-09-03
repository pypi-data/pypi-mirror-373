###############################################################################
# (c) Copyright 2013-2023 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Module grouping the common build functions.
"""
__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

import logging
import os
import re
import shlex
from datetime import datetime
from time import sleep

from LbNightlyTools.Utils import compatible_lcg_external_files, find_path
from LbNightlyTools.Utils import log_call as _log_call

try:  # py3
    from shlex import quote
except ImportError:  # py2
    from shlex import quote

__log__ = logging.getLogger(__name__)
__log__.setLevel(logging.DEBUG)

try:
    from LbDevTools import initProject
except ImportError:

    def initProject(dest):
        log = __log__.getChild("initProject")
        if not os.path.exists(os.path.join(dest, "Makefile")):
            log.debug("create default generic Makefile")
            with open(os.path.join(dest, "Makefile"), "w") as f:
                f.write("include $(LBCONFIGURATIONROOT)/data/Makefile\n")
        if not os.path.exists(os.path.join(dest, "toolchain.cmake")):
            log.debug("create default toolchain.cmake")
            with open(os.path.join(dest, "toolchain.cmake"), "w") as f:
                f.write("include($ENV{LBUTILSROOT}/data/toolchain.cmake)\n")


def _apptainer_wrap_cmd(platform, cmd, host_root, cont_root, env, cwd):
    """
    Return the passed command wrapped in an apptainer invocation.
    """
    import re

    from whichcraft import which

    apptainer = which("apptainer")
    if not apptainer:
        return cmd

    image = None
    if re.match(r"x86_64.*-centos7-.*", platform):
        image = "/cvmfs/lhcb.cern.ch/containers/os-base/centos7-devel/prod/amd64"
    elif re.match(r"x86_64.*-slc[56]-.*", platform):
        image = "/cvmfs/lhcb.cern.ch/containers/os-base/slc6-devel/prod/amd64"
    elif re.match(r"x86_64.*-el9-.*", platform):
        image = "/cvmfs/lhcb.cern.ch/containers/os-base/alma9-devel/prod/amd64"
    elif re.match(r"arm.*-centos7-.*", platform):
        image = "/cvmfs/lhcb.cern.ch/containers/os-base/centos7-devel/prod/aarch64"
    elif re.match(r"arm.*-el9-.*", platform):
        image = "/cvmfs/lhcb.cern.ch/containers/os-base/alma9-devel/prod/aarch64"

    if not image:
        return cmd

    apptainer_cmd = [
        apptainer,
        "exec",
        "--contain",
        "--bind",
        "/cvmfs",
        "--bind",
        f"{host_root}:{cont_root}",
        # we bind host_root as itself to fix issues with non relocatable local conda environments
        "--bind",
        host_root,
    ]

    apptainer_cmd.extend(
        ["--pwd", os.path.join(cont_root, os.path.relpath(cwd, host_root))]
    )

    # guarantee that we have all system directories in PATH in the container
    if env.get("PATH"):
        env["PATH"] = (
            env["PATH"]
            + ":/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        )
    # make sure the special dir `/.singularity.d/libs` is always in LD_LIBRARY_PATH,
    # see https://apptainer.org/docs/user/main/environment_and_metadata.html#environment-from-the-host
    if env.get("LD_LIBRARY_PATH"):
        env["LD_LIBRARY_PATH"] = env["LD_LIBRARY_PATH"] + ":/.singularity.d/libs"
    else:
        env["LD_LIBRARY_PATH"] = "/.singularity.d/libs"

    for variable in ("PATH", "LD_LIBRARY_PATH"):
        if env.get(variable):
            apptainer_cmd.extend(["--env", f"{variable}={env[variable]}"])

    if "APPTAINER_FLAGS" in env:
        apptainer_cmd.extend(shlex.split(env["APPTAINER_FLAGS"]))

    apptainer_cmd.append(image)

    apptainer_cmd.extend(cmd)

    __log__.debug("apptainer command: %s", " ".join(quote(a) for a in apptainer_cmd))
    return apptainer_cmd


def log_call(cmd, *args, **kwargs):
    """
    Helper to use apptainer and send log messages of log_call to __log__ by default.
    """
    if "logger" not in kwargs:
        kwargs["logger"] = __log__.getChild(cmd[0].replace(".", "_"))

    host_root = os.environ.get("WORKSPACE") or os.getcwd()
    cont_root = "/workspace"

    # patch the environment for the wrapped command
    kwargs["env"] = {
        key: value.replace(host_root, cont_root)
        for key, value in (kwargs.get("env") or os.environ).items()
    }
    # patch the command line arguments
    cmd = [value.replace(host_root, cont_root) for value in cmd]

    cmd = _apptainer_wrap_cmd(
        os.environ["BINARY_TAG"],
        cmd,
        host_root,
        cont_root,
        env=kwargs["env"],
        cwd=kwargs.get("cwd", os.getcwd()),
    )

    # Workaround for https://gitlab.cern.ch/lhcb-core/LbNightlyTools/-/issues/119
    for attempt in range(5):
        if attempt != 0:
            sleep(10)
        result = _log_call(cmd, *args, **kwargs)
        if (
            b"Failed to get file information for file descriptor 3"
            not in result["stdout"]
        ):
            if attempt != 0:
                __log__.debug("apptainer successfully started on attempt %d", attempt)
            break
        __log__.debug("apptainer failed to start on attempt %d", attempt)
    else:
        __log__.warning("giving up after repeated failures of apptainer")
    return result


def ensure_dir(path):
    """
    Make sure that a directory exist, creating it and printing a warning if not.
    """
    if not os.path.exists(path):
        __log__.warning("directory %s is missing, I create it", path)
        os.makedirs(path)


def to_cmake_version(v):
    """
    Helper to convert "vXrYpZ" to "X.Y.Z".

    >>> to_cmake_version('v1r0p0')
    '1.0.0'
    """
    return ".".join(re.findall(r"\d+", v))


class BuildResults:
    """
    Class used to analyze the build reports of projects.
    """

    def __init__(self, project, returncode, stdout, stderr, started, completed=None):
        """
        Initialize the instance with raw data from the build.
        """
        self.project = project
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.started = started
        self.completed = completed or datetime.now()


class make:
    """
    Base class for build tools based on make.
    """

    def _make(self, target, proj, **kwargs):
        """
        Internal function to wrap the call to make for CMT.

        @param target: name of the target to build
        @param proj: Project instance to build
        @param jobs: number of parallel build processes [default: 1]
        @param max_load: maximum allowed load beyond which no new process are
                         started
        @param env: dictionary used to override environment variables from the
                    project configuration
        @param args: list of extra arguments to pass to make
        @param make_cmd: command to be used to build [default: ['make']]
        """
        jobs = kwargs.get("jobs")
        max_load = kwargs.get("max_load")

        env = proj.environment()
        env.update(kwargs.get("env", {}))
        # "unset" variables set to None
        env = {key: value for key, value in env.items() if value is not None}

        cmd_kwargs = {"env": env, "cwd": proj.baseDir}
        if "stderr" in kwargs:
            cmd_kwargs["stderr"] = kwargs["stderr"]

        cmd = kwargs.get("make_cmd") or "make"
        if isinstance(cmd, str):
            cmd = cmd.split()
        else:
            # make a copy of make_cmd argumens to avoid modifying it
            cmd = list(cmd)

        if jobs:
            cmd.append(f"-j{jobs}")
        if max_load:
            cmd.append(f"-l{max_load:.1f}")
        cmd.extend(kwargs.get("args", []))
        cmd.append(target)

        ensure_dir(cmd_kwargs["cwd"])
        initProject(cmd_kwargs["cwd"])

        __log__.debug("running %s", " ".join(cmd))
        started = datetime.now()
        result = log_call(cmd, **cmd_kwargs)
        completed = datetime.now()
        __log__.debug("command exited with code %d", result["retcode"])

        out = (
            ("#### {} {} ####\n" "# Start: {}\n" "# Command: {}\n{}" "# End: {}\n")
            .format(
                self,
                target,
                started.isoformat(),
                " ".join(quote(a) for a in cmd),
                result["stdout"].decode("utf-8", errors="replace"),
                completed.isoformat(),
            )
            .encode("utf-8")
        )
        return BuildResults(
            proj, result["retcode"], out, result["stderr"], started, completed
        )

    def build(self, proj, **kwargs):
        """
        Build a project.
        """
        return self._make("all", proj, **kwargs)

    def clean(self, proj, **kwargs):
        """
        Clean the build products.
        """
        return self._make("clean", proj, **kwargs)

    def test(self, proj, **kwargs):
        """
        Run the tests.
        """
        return self._make("test", proj, **kwargs)

    def __str__(self):
        """
        Conversion to string.
        """
        return "make"


class cmt(make):
    """
    Class to wrap the build/test semantics for CMT-based projects.
    """

    def _make(self, target, proj, **kwargs):
        """
        Override basic make call to set the environment variable USE_CMT=1.
        """
        env = kwargs.pop("env", {})
        # PWD and CWD may cause troubles to CMT, so we unset them
        env.update({"USE_CMT": "1", "PWD": None, "CWD": None})
        if "CMTROOT" not in env and "make_cmd" not in kwargs:
            kwargs["make_cmd"] = ["cmt", "run", "make"]
        return make._make(self, target, proj, env=env, **kwargs)

    def clean(self, proj, **kwargs):
        """
        Override default clean method to call the 'purge' target (more
        aggressive).
        """
        return self._make("purge", proj, **kwargs)

    def test(self, proj, **kwargs):
        """
        Run the tests in a Gaudi/LHCb project using CMT.
        """
        env = kwargs.get("env", {})
        if "CMTCONFIG" not in env:
            env["CMTCONFIG"] = os.environ.get("CMTCONFIG") or os.environ.get(
                "BINARY_TAG"
            )
        if "GAUDI_QMTEST_HTML_OUTPUT" not in env:
            bin_dir = os.path.join(os.path.abspath(proj.baseDir), "build", "html")
            env["GAUDI_QMTEST_HTML_OUTPUT"] = bin_dir
        kwargs["env"] = env
        return self._make("test", proj, **kwargs)

    def __str__(self):
        """
        Conversion to string.
        """
        return "CMT"


class cmake_old(make):
    """
    Class to wrap the build/test semantics for CMT-based projects.
    """

    def _cache_preload_file(self, proj):
        """
        Name of the cache preload file to be passed to CMake.
        """
        return os.path.join(proj.baseDir, "cache_preload.cmake")

    def _prepare_cache(self, proj, cache_entries=None):
        """
        Prepare the cache_preload.cmake file passed to CMake during the
        configuration.
        """
        # prepare the cache to give to CMake: add the launcher rules commands,
        # followed by what is found passed as argument
        if cache_entries is None:
            cache_entries = []
        elif hasattr(cache_entries, "items"):
            cache_entries = list(cache_entries.items())

        # add the RULE_LAUNCH settings for the build
        launcher_cmd = "lbn-wrapcmd <CMAKE_CURRENT_BINARY_DIR> <TARGET_NAME>"
        cache_entries = [
            (f"GAUDI_RULE_LAUNCH_{n}", launcher_cmd)
            for n in ("COMPILE", "LINK", "CUSTOM")
        ] + cache_entries
        cache_entries.extend(
            (f"{p.name}_INSTALL_VERSION", p.version)
            for p in (proj.slot.projects if proj.slot else [])
        )

        cache_file = self._cache_preload_file(proj)
        ensure_dir(os.path.dirname(cache_file))
        with open(cache_file, "w") as cache:
            cache.writelines(
                [
                    'set({} "{}" CACHE STRING "override")\n'.format(*item)
                    for item in cache_entries
                ]
            )

            # constrain versions of projects not built in the slot
            if proj.slot:
                cache.writelines(
                    f'set({p.name}_EXACT_VERSION "{to_cmake_version(p.version)}" CACHE STRING "")\n'
                    for p in proj.slot.projects
                    if p.disabled
                )

    def _make(self, target, proj, **kwargs):
        """
        Override basic make call to set the environment variable USE_CMT=1.
        """
        # copy kwargs to be able to change it
        kwargs = dict(kwargs)
        self._prepare_cache(proj, cache_entries=kwargs.pop("cache_entries", None))

        env = kwargs.pop("env", {})
        preload_file = os.path.join(os.getcwd(), self._cache_preload_file(proj))
        env.update(
            {"USE_CMAKE": "1", "USE_MAKE": "1", "CMAKEFLAGS": "-C" + preload_file}
        )
        try:
            kwargs["make_cmd"] = kwargs["make_cmd"].get(target)
        except (KeyError, TypeError, AttributeError):
            # no target-specific make_cmd
            pass
        if "relaxed_install" in kwargs:
            del kwargs["relaxed_install"]
        return make._make(self, target, proj, env=env, **kwargs)

    def build(self, proj, **kwargs):
        """
        Override the basic build method to call the different targets used in
        CMake builds: configure, all, unasfe-install, post-install.
        """
        kwargs["args"] = ["BUILDDIR=build"] + kwargs.get("args", [])
        output = [
            self._make(target, proj, **kwargs)
            for target in (
                "configure",
                "all",
                "unsafe-install",
                "post-install",
                "clean",
            )
        ]

        # Write configuration logfile fragment for "collect logs" script
        ensure_dir(os.path.join(proj.baseDir, "build", "configure"))
        with open(
            os.path.join(
                proj.baseDir,
                "build",
                "configure",
                f"{output[0].completed:%s%f000}-build.log",
            ),
            "wb",
        ) as conf_log:
            # conf_log.write('\033[0;32m({})\$ {}\033[0m\n'.format(
            #     os.path.join(proj.baseDir), ' '.join(quote(a) for a in cmd)))
            conf_log.writelines(output[0].stdout.splitlines(True)[2:-1])
            conf_log.write(
                f"\033[0;34mConfiguration completed in {(output[0].completed - output[0].started).total_seconds()} seconds\033[0m\n".encode()
            )

        output = (
            output[1].returncode,  # use the build return code
            b"".join(step.stdout for step in output),
            b"".join(step.stderr for step in output),
            output[0].started,
            output[-1].completed,
        )

        return BuildResults(proj, *output)

    def clean(self, proj, **kwargs):
        """
        Override default clean method to call the 'purge' target (more
        aggressive).
        """
        return self._make("purge", proj, **kwargs)

    def test(self, proj, **kwargs):
        """
        Run the tests in a Gaudi/LHCb project using CMT.
        """
        kwargs["args"] = ["BUILDDIR=build"] + kwargs.get("args", [])
        flags = []  # ["--repeat until-pass:3"]
        if "jobs" in kwargs:
            flags.append("-j{}".format(kwargs.pop("jobs")))

        for i, arg in enumerate(kwargs["args"]):
            if arg.startswith("ARGS="):
                kwargs["args"][i] += " " + " ".join(flags)
                break
        else:  # (this else matches the for) no ARGS= in args
            kwargs["args"].append("ARGS={}".format(" ".join(flags)))

        output = [
            self._make(target, proj, **kwargs) for target in ("configure", "test")
        ]
        output = (
            output[-1].returncode,  # use the test return code
            b"".join(step.stdout for step in output),
            b"".join(step.stderr for step in output),
            output[0].started,
            output[-1].completed,
        )

        return BuildResults(proj, *output)

    def __str__(self):
        """
        Conversion to string.
        """
        return "CMake (old)"


class cmake_new:
    # known "kwargs" not to be propagated to subprocess
    SPECIAL_ARGS = (
        "jobs",
        "max_load",
        "args",
        "make_cmd",
        "cache_entries",
        "step",
        "relaxed_install",
    )

    def _cache_preload_file(self, proj):
        """
        Name of the cache preload file to be passed to CMake.
        """
        return os.path.join(proj.baseDir, "cache_preload.cmake")

    def _prepare_cache(self, proj, cache_entries=None, log_writer=None):
        """
        Prepare the cache_preload.cmake file passed to CMake during the
        configuration.
        """
        # prepare the cache to give to CMake: add the launcher rules commands,
        # followed by what is found passed as argument
        if cache_entries is None:
            cache_entries = []
        elif hasattr(cache_entries, "items"):
            cache_entries = list(cache_entries.items())

        cache_file = self._cache_preload_file(proj)
        ensure_dir(os.path.dirname(cache_file))
        with open(cache_file, "w") as cache:
            cache.writelines(
                [
                    'set({} "{}" CACHE STRING "override")\n'.format(*item)
                    for item in cache_entries
                ]
            )
            # force use of ccache
            cache.writelines(
                f'set(CMAKE_{lang}_COMPILER_LAUNCHER ccache CACHE STRING "override")\n'
                for lang in ("C", "CXX")
            )
            # enable rule wrappers
            cache.writelines(
                (
                    f'set(CMAKE_RULE_LAUNCH_{action} "lbn-wrapcmd <CMAKE_CURRENT_BINARY_DIR> <TARGET_NAME>"\n'
                    '    CACHE STRING "override")\n'
                )
                for action in ("COMPILE", "LINK", "CUSTOM")
            )
            # constrain versions of projects not built in the slot
            if proj.slot:
                cache.writelines(
                    f'set({p.name}_EXACT_VERSION "{to_cmake_version(p.version)}" CACHE STRING "")\n'
                    for p in proj.slot.projects
                    if p.disabled
                )

        if log_writer:
            log_writer(
                f"created cache preload file:\n```{cache_file}\n{open(cache_file).read().rstrip()}\n```\n"
            )

    def _env(self, project, env=None):
        """
        Compute the environment for the project.
        """
        new_env = project.environment()
        if env:
            new_env.update(env)
        return new_env

    def _call(self, proj, cmd, **kwargs):
        # strip special kwargs before command invocation
        cmd_kwargs = {
            n: v for n, v in list(kwargs.items()) if n not in self.SPECIAL_ARGS
        }
        cmd_kwargs["env"] = self._env(proj, kwargs.get("env"))

        __log__.debug("running %s", " ".join(cmd))
        started = datetime.now()
        result = log_call(cmd, **cmd_kwargs)
        completed = datetime.now()
        __log__.debug("command exited with code %d", result["retcode"])

        out = (
            (
                "#### {} {} ####\n"
                "# Start: {}\n"
                "# Command: {}\n{}"
                "# Return code: {}\n"
                "# End: {}\n"
            )
            .format(
                self,
                kwargs.get("step", "(no step name)"),
                started.isoformat(),
                " ".join(quote(a) for a in cmd),
                result["stdout"].decode("utf-8", errors="replace"),
                result["retcode"],
                completed.isoformat(),
            )
            .encode("utf-8", errors="replace")
        )
        return BuildResults(
            proj, result["retcode"], out, result["stderr"], started, completed
        )

    def configure(self, proj, **kwargs):
        """
        Configure the project.
        """
        # Prepare configuration logfile fragment for "collect logs" script
        started = datetime.now()
        config_log = os.path.join(
            proj.baseDir, "build", "configure", f"{started:%s%f000}-build.log"
        )
        ensure_dir(os.path.dirname(config_log))
        # make sure we start from an empty one
        if os.path.exists(config_log):
            os.remove(config_log)

        def write_to_log(data):
            """
            Helper to open+write+close the log file.
            """
            with open(config_log, "ab") as log:
                log.write(
                    data.encode("utf-8", errors="replace")
                    if hasattr(data, "encode")
                    else data
                )

        if "LCG_EXTERNALS_FILE" in kwargs.get("cache_entries", []):
            ext_file = kwargs["cache_entries"]["LCG_EXTERNALS_FILE"]
            # we usually pass "$ENV{BINARY_TAG}" as platform in LCG_EXTERNALS_FILE
            ext_file = ext_file.replace("$ENV{BINARY_TAG}", os.environ["BINARY_TAG"])
            # find an existing, compatible externals file
            for ext_file in compatible_lcg_external_files(ext_file):
                # FIXME: this does not guarantee the file is actually good
                #        we may have multiple compatible files, but only one
                #        with the right time and the full list of requirements
                #        (we should re-run the precondition check to find the
                #        right match)
                if os.path.exists(ext_file):
                    # let's use this one instead of the suggested one
                    kwargs["cache_entries"]["LCG_EXTERNALS_FILE"] = ext_file
                    # and make sure we use the required architecture flags
                    kwargs["cache_entries"]["LHCB_PLATFORM"] = os.environ["BINARY_TAG"]
                    kwargs["cache_entries"]["LCG_ARCHITECTURE"] = os.environ[
                        "BINARY_TAG"
                    ].split("-", 1)[0]
                    break

        self._prepare_cache(
            proj, cache_entries=kwargs.get("cache_entries"), log_writer=write_to_log
        )

        # basic cmake command
        cmd = [
            "cmake",
            "-S",
            proj.baseDir,
            "-B",
            os.path.join(proj.baseDir, "build"),
            "-G",
            kwargs.get("generator", "Ninja"),
            "-C",
            self._cache_preload_file(proj),
        ]
        # get the toolchain to use
        if proj.slot and hasattr(proj.slot, "LCG"):
            LCG_VERSION = proj.slot.LCG.version
        elif "LCG_VERSION" in os.environ:
            LCG_VERSION = os.environ["LCG_VERSION"]
        else:
            out = (
                "\033[0;31mslot configuration error: "
                "version of LCG not defined (required for new "
                "CMake configuration)\033[0m\n"
            )
            write_to_log(out)
            return BuildResults(proj, 1, out, "", started, datetime.now())

        # When the configuration sets LCG_EXTERNALS_FILE, we have to use the
        # toolchain special/lcg-nightly.cmake
        if "LCG_EXTERNALS_FILE" not in kwargs.get("cache_entries", []):
            toolchain = find_path(
                os.path.join(
                    "lcg-toolchains",
                    f"LCG_{LCG_VERSION}",
                    "{}.cmake".format(os.environ["BINARY_TAG"]),
                ),
                search_path=self._env(proj)
                .get("CMAKE_PREFIX_PATH", "")
                .split(os.pathsep),
            )
        else:
            toolchain = find_path(
                os.path.join("lcg-toolchains", "special", "lcg-nightly.cmake"),
                search_path=self._env(proj)
                .get("CMAKE_PREFIX_PATH", "")
                .split(os.pathsep),
            )

        if not toolchain:
            out = (
                "\033[0;31mslot configuration error: "
                "cannot find toolchain file for {} {}\033[0m\n"
            ).format(LCG_VERSION, os.environ["BINARY_TAG"])
            write_to_log(out)
            return BuildResults(proj, 1, out, "", started, datetime.now())

        cmd.append("-DCMAKE_TOOLCHAIN_FILE=" + toolchain)

        write_to_log(
            "\033[0;32m({})$ {}\033[0m\n".format(
                os.getcwd(), " ".join(quote(a) for a in cmd)
            )
        )
        result = self._call(proj, cmd, step="configure", **kwargs)

        # write configuration log
        write_to_log(
            "".join(
                result.stdout.decode("utf-8", errors="replace").splitlines(True)[3:-2]
            )
        )
        write_to_log(
            f"\033[0;34mConfiguration completed in {(result.completed - result.started).total_seconds()} seconds\033[0m\n"
        )

        return result

    def install(self, proj, **kwargs):
        # modify all cmake_install.cmake scripts to do not fail if an artifact
        # is missing
        if kwargs.get("relaxed_install"):
            for dirpath, _dirnames, filenames in os.walk(
                os.path.join(proj.baseDir, "build")
            ):
                if "cmake_install.cmake" in filenames:
                    with open(os.path.join(dirpath, "cmake_install.cmake")) as f:
                        data = f.read()
                    with open(os.path.join(dirpath, "cmake_install.cmake"), "w") as f:
                        f.write(data.replace("file(INSTALL", "file(INSTALL OPTIONAL"))
        return self._call(
            proj,
            [
                "cmake",
                "--install",
                os.path.join(proj.baseDir, "build"),
                "--prefix",
                os.path.join(proj.baseDir, "InstallArea", os.environ["BINARY_TAG"]),
            ],
            step="install",
            **kwargs,
        )

    def build(self, proj, **kwargs):
        config_result = self.configure(proj, **kwargs)
        if config_result.returncode:
            # no point trying to build if we failed to configure
            return config_result

        cmd = ["cmake", "--build", os.path.join(proj.baseDir, "build")]
        if "jobs" in kwargs:
            cmd.extend(["-j", str(kwargs["jobs"])])
        if "args" in kwargs:
            cmd.append("--")
            cmd.extend((arg if arg != "-k" else "-k0") for arg in kwargs["args"])
        build_result = self._call(proj, cmd, step="build", **kwargs)

        install_result = self.install(proj, **kwargs)

        output = (
            build_result.returncode,  # use the build return code
            b"".join(
                step.stdout for step in (config_result, build_result, install_result)
            ),
            b"".join(
                step.stderr for step in (config_result, build_result, install_result)
            ),
            config_result.started,
            install_result.completed,
        )

        return BuildResults(proj, *output)

    def clean(self, proj, **kwargs):
        return self._call(
            proj,
            [
                "cmake",
                "--build",
                os.path.join(proj.baseDir, "build"),
                "--target",
                "clean",
            ],
            step="clean",
            **kwargs,
        )

    def test(self, proj, **kwargs):
        config_result = self.configure(proj, **kwargs)
        if config_result.returncode:
            # no point trying to run the tests if we failed to configure
            return config_result

        cmd = ["ctest", "-T", "test"]
        # cmd.extend(['--repeat', 'until-pass:3'])
        if "jobs" in kwargs:
            cmd.extend(["-j", str(kwargs["jobs"])])
        test_result = self._call(
            proj, cmd, step="test", cwd=os.path.join(proj.baseDir, "build"), **kwargs
        )

        output = (
            test_result.returncode,  # use the test return code
            b"".join(step.stdout for step in (config_result, test_result)),
            b"".join(step.stderr for step in (config_result, test_result)),
            config_result.started,
            test_result.completed,
        )

        return BuildResults(proj, *output)

    def __str__(self):
        return "CMake (new)"


def is_new_cmake_style(project_dir):
    """
    Check if the project uses the old or new CMake configuration style.
    """
    top_config = os.path.join(project_dir, "CMakeLists.txt")
    if not os.path.exists(top_config):
        # no CMakeLists.tst -> it's a CMT project
        return False
    if os.path.exists(os.path.join(project_dir, "toolchain.cmake")):
        # custom toolchain file in the sources -> must be old style
        return False
    with open(top_config) as f:
        content = f.read()
    # new style projects do not call "find_package(GaudiProject)"
    return not bool(re.search(r"find_package\s*\(\s*GaudiProject", content))


class cmake:
    """
    Dispatcher to use the old or new style CMake build procedure
    depending on the project.
    """

    def __init__(self):
        self._proj_dir = None
        self._impl_instance = None

    def _impl(self, project):
        """
        Return the correct implementation of CMake builder for the given project.
        """
        if project.baseDir != self._proj_dir:
            self._impl_instance = (
                cmake_new() if is_new_cmake_style(project.baseDir) else cmake_old()
            )
        return self._impl_instance

    def build(self, proj, **kwargs):
        return self._impl(proj).build(proj, **kwargs)

    def clean(self, proj, **kwargs):
        return self._impl(proj).clean(proj, **kwargs)

    def test(self, proj, **kwargs):
        return self._impl(proj).test(proj, **kwargs)

    def __str__(self):
        """
        Conversion to string.
        """
        return "CMake"


class no_build:
    """
    No-op build tool, used for projects that do no require a build
    (e.g. projects containing only data packages).
    """

    def build(self, proj, **kwargs):
        """
        Build method.
        """
        __log__.debug("no build for %s", proj)
        return BuildResults(proj, 0, f"no build for {proj}", "", datetime.now())

    def clean(self, proj, **kwargs):
        """
        Clean method.
        """
        __log__.debug("no clean for %s", proj)
        return BuildResults(proj, 0, f"no clean for {proj}", "", datetime.now())

    def test(self, proj, **kwargs):
        """
        Test method.
        """
        __log__.debug("no test for %s", proj)
        return BuildResults(proj, 0, f"no test for {proj}", "", datetime.now())

    def __str__(self):
        """
        Conversion to string.
        """
        return "no-build"


class echo:
    """
    Dummy build tool class used for testing.
    """

    def _report(self, target, proj, **kwargs):
        """
        Helper.
        """
        output = " ".join([target, str(proj), str(kwargs)])
        __log__.debug(output)
        return BuildResults(proj, 0, output, "", datetime.now())

    def build(self, proj, **kwargs):
        """
        Build method.
        """
        return self._report("build", proj, **kwargs)

    def clean(self, proj, **kwargs):
        """
        Clean method.
        """
        return self._report("clean", proj, **kwargs)

    def test(self, proj, **kwargs):
        """
        Test method.
        """
        return self._report("test", proj, **kwargs)

    def __str__(self):
        """
        Conversion to string.
        """
        return "echo"


default = cmake


def getMethod(method=None):
    """
    Helper function to get a build method by name.

    If method is a callable we return it, otherwise we look for the name in the
    current module or as a function coming from another module.
    If method is None, we return the default checkout method.
    """
    if method is None:
        return default
    if hasattr(method, "build"):
        return method
    if isinstance(method, str):
        if "." in method:
            # method is a fully qualified function name
            m, f = method.rsplit(".", 1)
            return getattr(__import__(m, fromlist=[f]), f)
        else:
            # it must be a name in this module
            return globals()[method]

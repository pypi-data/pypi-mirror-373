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
Common functions to deal with the configuration files.
"""
__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

import copy
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict, namedtuple
from datetime import datetime
from io import StringIO

from LbNightlyTools import BuildMethods, CheckoutMethods
from LbNightlyTools.Utils import (
    Dashboard,
    IgnorePackageVersions,
    applyenv,
    ensureDirs,
    find_path,
    shallow_copytree,
    write_patch,
)

__log__ = logging.getLogger(__name__)
__meta_log__ = logging.getLogger(__name__ + ".meta")
__meta_log__.setLevel(
    logging.DEBUG if os.environ.get("DEBUG_METACLASSES") else logging.WARNING
)

_slot_factories = set()


def slot_factory(f):
    """
    Decorator used to flag a function as a Slot factory to correctly
    trace the module defining a slot.
    """
    global _slot_factories
    _slot_factories.add(f.__name__)
    return f


# constants
GP_EXP = re.compile(r"gaudi_project\(([^)]+)\)")
HT_EXP = re.compile(r"set\(\s*heptools_version\s+([^)]+)\)")
VALID_PLATFORM_RE = r"^[0-9a-z_+.]+-[0-9a-z_]+-[0-9a-z_+]+-[0-9a-z_+]+$"

# all configured slots (Slot instances)
slots = {}

DEFAULT_REQUIRED_EXTERNALS = [
    "AIDA",
    "Boost",
    "CASTOR",
    "CLHEP",
    "COOL",
    "CORAL",
    "CppUnit",
    "eigen",
    "expat",
    "fastjet",
    "fftw",
    "gperftools",
    "graphviz",
    "GSL",
    "HepMC",
    "HepPDT",
    "libunwind",
    "mysql",
    "neurobayes",
    "oracle",
    "pyanalysis",
    "pygraphics",
    "Python",
    "pytools",
    "Qt5",
    "RELAX",
    "ROOT",
    "sqlite",
    "tbb",
    "vdt",
    "XercesC",
    "xqilla",
    "xrootd",
]


def sortedByDeps(deps):
    """
    Take a dictionary of dependencies as {'depender': ['dependee', ...]} and
    return the list of keys sorted according to their dependencies so that
    that a key comes after its dependencies.

    >>> sortedByDeps({'4':['2','3'],'3':['1'],'2':['1'],'1':['0'],'0':[]})  # doctest: +SKIP
    ['0', '1', '2', '3', '4']
    """

    def unique(iterable):
        """Return only the unique elements in the list l.

        >>> unique([0, 0, 1, 2, 1])
        [0, 1, 2]
        """
        uniquelist = []
        for item in iterable:
            if item not in uniquelist:
                uniquelist.append(item)
        return uniquelist

    def recurse(keys):
        """
        Recursive helper function to sort by dependency: for each key we
        first add (recursively) its dependencies then the key itself."""
        result = []
        for k in keys:
            result.extend(recurse(deps[k]))
            result.append(k)
        return unique(result)

    return recurse(deps)


class UTFStringIO(StringIO):
    """
    Avoid issues with mixed ASCII and Unicode inputs to StringIO.
    """

    def write(self, s):
        if isinstance(s, bytes):
            s = s.decode("utf-8", errors="replace")
        return StringIO.write(self, s)


class RecordLogger:
    """
    Decorator to collect the log messages of a Logger instance in a data member
    of the instance.

    @param logger: Logger instance or name (default: use the root Logger)
    @param data_member: name of the property of the instance bound to the method
                        where to record the log (default: method name + '_log')
    """

    def __init__(self, logger="", data_member=None):
        """
        Initialize the decorator.
        """
        if isinstance(logger, str):
            logger = logging.getLogger(logger)
        self.logger = logger
        self.data_member = data_member

    def __call__(self, method):
        """
        Decorate the method.
        """
        from functools import wraps

        logger = self.logger
        data_member = self.data_member or (method.__name__ + "_log")

        @wraps(method)
        def log_recorder(self, *args, **kwargs):
            data = UTFStringIO()
            hdlr = logging.StreamHandler(data)
            logger.addHandler(hdlr)

            try:
                result = method(self, *args, **kwargs)
            finally:
                setattr(self, data_member, data.getvalue())
                logger.removeHandler(hdlr)

            return result

        return log_recorder


def log_timing(logger="", level=logging.DEBUG):
    """
    Decorator to add log messages about the time a method takes.
    """
    if isinstance(logger, str):
        logger = logging.getLogger(logger)

    def decorate(method):
        from functools import wraps

        @wraps(method)
        def log_timing_wrapper(*args, **kwargs):
            start_time = datetime.now()
            logger.log(level, "Started at: %s", start_time)
            result = method(*args, **kwargs)
            end_time = datetime.now()
            logger.log(level, "Completed at: %s", end_time)
            logger.log(level, "Elapsed time: %s", end_time - start_time)
            return result

        return log_timing_wrapper

    return decorate


def log_enter_step(msg=None):
    """
    Decorator to log entering and exiting from a method of an object.
    """

    def decorate(method):
        from functools import wraps

        @wraps(method)
        def log_enter_step_wrapper(self, *args, **kwargs):
            __log__.info(msg + " %s", self)
            __log__.debug("  with args %s, %s", args, kwargs)
            return method(self, *args, **kwargs)

        return log_enter_step_wrapper

    return decorate


def extend_kwargs(extra_opts_name):
    """
    Decorator to define default keyword arguments of a method via an instance
    property.

    >>> class MyClass(object):
    ...     def __init__(self):
    ...         self.defaults = {'a': 0, 'b': 1}
    ...     @extend_kwargs('defaults')
    ...     def __call__(self, **kwargs):
    ...         print(kwargs)
    ...
    >>> obj = MyClass()
    >>> obj()
    {'a': 0, 'b': 1}
    >>> obj.defaults = {'c': -1}
    >>> obj(d=-2)
    {'c': -1, 'd': -2}
    """

    def decorate(method):
        from functools import wraps

        @wraps(method)
        def extend_kwargs_wrapper(self, *args, **kwargs):
            opts = dict(getattr(self, extra_opts_name))
            opts.update(kwargs)
            return method(self, *args, **opts)

        return extend_kwargs_wrapper

    return decorate


class _BuildToolProperty:
    """
    Descriptor for the build_tool property of a slot
    """

    def __get__(self, instance, owner):
        "getter"
        if (
            hasattr(instance, "ignore_slot_build_tool")
            and instance.ignore_slot_build_tool
        ):
            return instance._build_tool
        try:
            return instance.slot.build_tool
        except AttributeError:
            return instance._build_tool

    def __set__(self, instance, value):
        "setter"
        __meta_log__.debug("setting %s build tool to %s", instance, value)
        if hasattr(instance, "slot") and instance.slot:
            raise AttributeError("can't change build tool to a project " "in a slot")
        from LbNightlyTools.BuildMethods import getMethod as getBuildMethod

        instance._build_tool = getBuildMethod(value)()


class _CheckoutMethodProperty:
    """
    Descriptor for the checkout property of a project.
    """

    def __init__(self, default=None):
        self.default = default

    def __get__(self, instance, owner):
        "getter"
        return instance._checkout_wrap if instance is not None else self.default

    @classmethod
    def make_wrapper(self, instance, method):
        """
        helper to add wrappers to the checkout method of the instance
        """
        from functools import partial, update_wrapper

        timelog = log_timing(CheckoutMethods.__log__)
        reclog = RecordLogger(CheckoutMethods.__log__, data_member="checkout_log")
        info = log_enter_step("checking out")
        opts = extend_kwargs("checkout_opts")
        return update_wrapper(
            partial(opts(info(reclog(timelog(method)))), instance), method
        )

    def getCheckoutMethod(self, instance, method):
        """
        Helper to map "method" to the correct checkout method.

        If not None, map the method argument to the corresponding checkout
        method.  If None, we select an appropriate default: an explicit default,
        or a method based on the instance name or the generic default.
        """
        from LbNightlyTools.CheckoutMethods import getMethod as get

        if method is None:
            # we want the default method
            if self.default:
                # we have an explicit default
                method = get(self.default)
            else:
                try:
                    # other wise we try from the name of the instance
                    method = get(instance.name.lower())
                except:
                    # else, if that fails, we use the generic default
                    method = get()
        else:
            # setting from an explicit value
            method = get(method)

        return method

    def __set__(self, instance, value):
        "setter"
        if isinstance(value, tuple):
            value, instance.checkout_opts = value
        method = self.getCheckoutMethod(instance, value)
        instance._checkout = method
        instance._checkout_wrap = self.make_wrapper(instance, method)


class _ProjectMeta(type):
    """
    Metaclass for Project.
    """

    def __new__(cls, name, bases, dct):
        """
        Instrument Project classes.
        """
        __meta_log__.debug("preparing class %s(%s)", name, bases)
        if "build_tool" in dct:
            build_tool = dct.get("build_tool")
            __meta_log__.debug("selected build tool %s", build_tool)
        else:
            for base in bases:
                if hasattr(base, "__build_tool__"):
                    build_tool = base.__build_tool__
                    __meta_log__.debug("inherited build tool %s", build_tool)
                    break
            else:  # this 'else' is bound to the 'for' loop
                __meta_log__.debug("use default build tool")
                build_tool = None
        dct["__build_tool__"] = build_tool
        dct["build_tool"] = _BuildToolProperty()
        if "name" in dct:
            __meta_log__.debug("default name %s", dct.get("name"))
            dct["__project_name__"] = dct.pop("name")
        __meta_log__.debug("prepare checkout method property")
        if "checkout" not in dct:
            for base in bases:
                if hasattr(base, "checkout"):
                    __meta_log__.debug("inherited checkout %s", base.checkout)
                    dct["checkout"] = base.checkout
                    break
        dct["checkout"] = _CheckoutMethodProperty(dct.get("checkout"))

        __meta_log__.debug("adding build logging wrappers")
        timelog = log_timing(BuildMethods.__log__)
        reclog = RecordLogger(BuildMethods.__log__)
        for method in ("build", "clean", "test"):
            if method in dct:
                info = log_enter_step(method + "ing")
                dct[method] = info(reclog(timelog(dct[method])))

        return type.__new__(cls, name, bases, dct)

    def __call__(self, *args, **kwargs):
        """
        Use the class name as project name in classes derived from Project
        (if it does not end by 'Project').
        """
        name = None
        if hasattr(self, "__project_name__"):
            name = self.__project_name__
        elif not self.__name__.endswith("Project"):
            name = self.__name__
        if name:
            # we prepend the class name to the arguments.
            args = (name,) + args
        __meta_log__.debug("instantiating: %s(*%r, **%r)", self.__name__, args, kwargs)
        return type.__call__(self, *args, **kwargs)


class Project(metaclass=_ProjectMeta):
    """
    Describe a project to be checked out, built and tested.
    """

    __checkout__ = None

    def __init__(self, name, version, **kwargs):
        """
        @param name: name of the project
        @param version: version of the project as 'vXrY' or 'HEAD', where 'HEAD'
                        means the head version of all the packages
        @param dependencies: optional list of dependencies (as list of project
                             names), can be used to extend the actual (code)
                             dependencies of the project
        @param overrides: dictionary describing the differences between the
                          versions of the packages in the requested projects
                          version and the ones required in the checkout
        @param checkout: callable that can check out the specified project, or
                         tuple (callable, kwargs), with kwargs overriding
                         checkout_opts
        @param checkout_opts: dictionary with extra options for the checkout
                              callable
        @param disabled: if set to True, the project is taken into account only
                         for the configuration
        @param env: override the environment for the project
        @param build_tool: build method used for the project
        @param with_shared: if True, the project requires packing of data
                            generated at build time in the source tree
        @param platform_independent: if True, the project does not require a
                                     build, just the checkout [default: False]
        @param no_test: if True, the tests of the project should not be run
        """
        self.name = name
        self.version = "HEAD" if version.upper() == "HEAD" else version

        # slot owning this project
        self.slot = None

        self.disabled = kwargs.get("disabled", False)
        self.overrides = kwargs.get("overrides", {})
        self._deps = kwargs.get("dependencies", [])
        self.env = kwargs.get("env", [])

        # we need to try setting checkout_opts before checkout, because
        # it could be overridden if checkout is a tuple
        self.checkout_opts = kwargs.get("checkout_opts", {})
        # Get the checkout method using:
        #  - checkout parameter
        #  - __checkout__ class property
        #  - name of the project
        #  - default
        self.checkout = kwargs.get("checkout") or self.__checkout__

        self.build_tool = kwargs.get("build_tool", self.__build_tool__)
        self.with_shared = kwargs.get("with_shared", False)
        self.platform_independent = kwargs.get("platform_independent", False)
        self.no_test = kwargs.get("no_test", False)
        if "ignore_slot_build_tool" in kwargs:
            self.ignore_slot_build_tool = kwargs["ignore_slot_build_tool"]

        self.build_results = None

    def toDict(self):
        """
        Return a dictionary describing the project, suitable to conversion to
        JSON.
        """
        data = {
            "name": self.name,
            "version": self.version,
            "dependencies": self._deps,
            "overrides": self.overrides,
            "checkout": self._checkout.__name__,
            "checkout_opts": self.checkout_opts,
            "disabled": self.disabled,
            "env": self.env,
            "with_shared": self.with_shared,
        }
        if self.platform_independent:
            data["platform_independent"] = True
        if self.no_test:
            data["no_test"] = True
        if hasattr(self, "ignore_slot_build_tool") and self.ignore_slot_build_tool:
            data["ignore_slot_build_tool"] = True
        if not self.slot or data.get("ignore_slot_build_tool"):
            data["build_tool"] = self.build_tool.__class__.__name__
        return data

    @classmethod
    def fromDict(cls, data):
        """
        Create a Project instance from a dictionary like the one returned by
        Project.toDict().
        """
        return cls(**data)

    def __eq__(self, other):
        """Equality operator."""
        elems = (
            "__class__",
            "name",
            "version",
            "disabled",
            "overrides",
            "_deps",
            "env",
            "_checkout",
            "checkout_opts",
        )
        for elem in elems:
            if getattr(self, elem) != getattr(other, elem):
                return False
        return self.build_tool.__class__.__name__ == other.build_tool.__class__.__name__

    def __ne__(self, other):
        """Non-equality operator."""
        return not (self == other)

    def __getstate__(self):
        """
        Allow pickling.
        """
        dct = {
            elem: getattr(self, elem)
            for elem in (
                "name",
                "version",
                "disabled",
                "overrides",
                "_deps",
                "env",
                "checkout_opts",
            )
        }
        dct["build_tool"] = self._build_tool.__class__.__name__
        dct["checkout"] = self._checkout
        return copy.deepcopy(dct)

    def __setstate__(self, state):
        """
        Allow unpickling.
        """
        for key in state:
            setattr(self, key, state[key])

    def build(self, **kwargs):
        """
        Build the project.
        @param jobs: number of parallel jobs to use [default: cpu count + 1]
        """
        if "jobs" not in kwargs:
            from multiprocessing import cpu_count

            kwargs["jobs"] = cpu_count() + 1
        self.build_results = self.build_tool.build(self, **kwargs)
        return self.build_results

    def clean(self, **kwargs):
        """
        Clean the project.
        """
        return self.build_tool.clean(self, **kwargs)

    def test(self, **kwargs):
        """
        Test the project.
        """
        return self.build_tool.test(self, **kwargs)

    @property
    def baseDir(self):
        """Name of the project directory (relative to the build directory)."""
        if self.slot and self.slot.with_version_dir:
            upcase = self.name.upper()
            bdir = os.path.join(upcase, f"{upcase}_{self.version}")
            __log__.debug(
                "Using file structure with version directory. Base dir=%s", bdir
            )
            return bdir
        return f"{self.name}/"

    @property
    def enabled(self):
        return not self.disabled

    @enabled.setter
    def enabled(self, value):
        self.disabled = not value

    def dependencies(self):
        """
        Return the dependencies of a checked out project using the information
        retrieved from the configuration files.
        @return: list of used projects (all converted to lowercase)
        """
        proj_root = self.baseDir

        def fromCMake():
            """
            Helper to extract dependencies from CMake configuration.
            """
            deps = []
            cmake = os.path.join(proj_root, "CMakeLists.txt")
            # arguments to the gaudi_project call
            args = GP_EXP.search(open(cmake).read()).group(1).split()
            if "USE" in args:
                # look for the indexes of the range 'USE' ... 'DATA'
                use_idx = args.index("USE") + 1
                if "DATA" in args:
                    data_idx = args.index("DATA")
                else:
                    data_idx = len(args)
                deps = [p for p in args[use_idx:data_idx:2]]

            # artificial dependency on LCGCMT, if needed
            toolchain = os.path.join(proj_root, "toolchain.cmake")
            if os.path.exists(toolchain) and HT_EXP.search(open(toolchain).read()):
                # we set explicit the version of heptools,
                # so we depend on LCGCMT and LCG
                deps.extend(["LCGCMT", "LCG"])
            if "DATA" in args:
                # if we need data packages, add a dependency on DBASE and PARAM
                deps.extend(["DBASE", "PARAM"])
            return deps

        def fromCMT():
            """
            Helper to extract dependencies from CMT configuration.
            """
            cmt = os.path.join(proj_root, "cmt", "project.cmt")
            # from all the lines in project.cmt that start with 'use',
            # we extract the second word (project name) and convert it to
            # lower case
            return [
                l.split()[1]
                for l in [l.strip() for l in open(cmt)]
                if l.startswith("use")
            ]

        def fromProjInfo():
            """
            Helper to get the dependencies from an info file in the project,
            called 'project.info'.
            The file must be in "config" format (see ConfigParser module) and
            the dependencies must be declared as a comma separated list in
            the section project.

            E.g.:
            [Project]
            dependencies: ProjectA, ProjectB
            """
            import configparser

            config = configparser.ConfigParser()
            config.read(os.path.join(proj_root, "project.info"))
            return [
                proj.strip()
                for proj in config.get("Project", "dependencies").split(",")
            ]

        def fromLHCbProjectYml():
            """
            Helper to get the dependencies from a metadata file in the project,
            called 'lhcbproject.yml'.
            The file (in YAML) must contain a `dependencies` field as a list of
            strings

            E.g.::

                ---
                name: MyProject
                dependencies:
                  - ProjectA
                  - ProjectB
            """
            import yaml

            return yaml.safe_load(open(os.path.join(proj_root, "lhcbproject.yml")))[
                "dependencies"
            ]

        def fromLHCbProjectJson():
            """
            Helper to get the dependencies from a metadata file in the project,
            called 'lhcbproject.json'.
            The file (in JSON) must contain a `dependencies` field as a list of
            strings

            E.g.::

                {
                    "name": "MyProject",
                    "dependencies": [
                        "ProjectA",
                        "ProjectB"
                    ]
                }
            """
            import json

            return json.load(open(os.path.join(proj_root, "lhcbproject.json")))[
                "dependencies"
            ]

        # Try all the helpers until one succeeds
        deps = []
        for helper in (
            fromCMake,
            fromCMT,
            fromLHCbProjectJson,
            fromLHCbProjectYml,
            fromProjInfo,
        ):
            try:
                deps = helper()
                break
            except:
                pass
        else:
            __log__.warning("cannot discover dependencies for %s", self)

        deps = sorted(set(deps + self._deps))
        if self.slot:
            # helper dict to map case insensitive name to correct project names
            names = {p.name.lower(): p.name for p in self.slot.projects}

            def fixNames(iterable):
                "helper to fix the cases of names in dependencies"
                return [names.get(name.lower(), name) for name in iterable]

            deps = fixNames(deps)

        return deps

    def __str__(self):
        """String representation of the project."""
        return f"{self.name}/{self.version}"

    def id(self):
        """
        String representing the project instance.

        >>> p = Project('AProject', 'v1r0')
        >>> p.id()
        'AProject/v1r0'
        >>> s = Slot('test', build_id=10, projects=[p])
        >>> s.AProject.id()
        'nightly/test/10/AProject'
        """
        return (self.slot.id() + "/" + self.name) if self.slot else str(self)

    def __hash__(self):
        return hash(self.id())

    def environment(self, envdict=None):
        """
        Return a dictionary with the environment for the project.

        If envdict is provided, it will be used as a starting point, otherwise
        the environment defined by the slot or by the system will be used.
        """
        # get the initial env from the argument or the system
        if envdict is None:
            envdict = os.environ
        # if we are in a slot, we first process the environment through it
        if self.slot:
            result = self.slot.environment(envdict)
        else:
            # we make a copy to avoid changes to the input
            result = dict(envdict)
        applyenv(result, self.env)
        return result

    def _fixCMakeLists(self, patchfile=None, dryrun=False):
        """
        Fix the 'CMakeLists.txt'.
        """
        from os.path import exists, join

        cmakelists = join(self.baseDir, "CMakeLists.txt")

        if exists(cmakelists):
            __log__.info("patching %s", cmakelists)
            with open(cmakelists) as f:
                data = f.read()
            try:
                # find the project declaration call
                m = GP_EXP.search(data)
                if m is None:
                    __log__.warning(
                        "%s does not look like a Gaudi/CMake "
                        "project, I'm not touching it",
                        self,
                    )
                    return
                args = m.group(1).split()
                # the project version is always the second
                args[1] = self.version

                # fix the dependencies
                if "USE" in args:
                    # look for the indexes of the range 'USE' ... 'DATA'
                    use_idx = args.index("USE") + 1
                    if "DATA" in args:
                        data_idx = args.index("DATA")
                    else:
                        data_idx = len(args)
                    # for each key, get the version (if available)
                    for i in range(use_idx, data_idx, 2):
                        if hasattr(self.slot, args[i]):
                            args[i + 1] = getattr(self.slot, args[i]).version
                # FIXME: we should take into account the declared deps
                start, end = m.start(1), m.end(1)
                newdata = data[:start] + " ".join(args) + data[end:]
            except:  # pylint: disable=W0702
                __log__.error("failed parsing of %s, not patching it", cmakelists)
                return

            if newdata != data:
                if not dryrun:
                    with open(cmakelists, "w") as f:
                        f.write(newdata)
                if patchfile:
                    write_patch(patchfile, data, newdata, cmakelists)

    def _fixCMakeToolchain(self, patchfile=None, dryrun=False):
        """
        Fix 'toolchain.cmake'.
        """
        from os.path import exists, join

        toolchain = join(self.baseDir, "toolchain.cmake")

        if exists(toolchain):
            # case insensitive list of projects
            projs = {p.name.lower(): p for p in self.slot.projects}
            for name in ("heptools", "lcgcmt", "lcg"):
                if name in projs:
                    heptools_version = projs[name].version
                    break
            else:
                # no heptools in the slot
                return
            __log__.info("patching %s", toolchain)
            with open(toolchain) as f:
                data = f.read()
            try:
                # find the heptools version setting
                m = HT_EXP.search(data)
                if m is None:
                    __log__.debug(
                        "%s does not set heptools_version, " "no need to touch", self
                    )
                    return
                start, end = m.start(1), m.end(1)
                newdata = data[:start] + heptools_version + data[end:]
            except:  # pylint: disable=W0702
                __log__.error("failed parsing of %s, not patching it", toolchain)
                return

            if newdata != data:
                if not dryrun:
                    with open(toolchain, "w") as f:
                        f.write(newdata)
                if patchfile:
                    write_patch(patchfile, data, newdata, toolchain)

    def _fixCMake(self, patchfile=None, dryrun=False):
        """
        Fix the CMake configuration of a project, if it exists, and write
        the changes in 'patchfile'.
        """
        self._fixCMakeLists(patchfile, dryrun=dryrun)
        self._fixCMakeToolchain(patchfile, dryrun=dryrun)

    def _fixCMT(self, patchfile=None, dryrun=False):
        """
        Fix the CMT configuration of a project, if it exists, and write
        the changes in 'patchfile'.
        """
        from os.path import exists, join

        project_cmt = join(self.baseDir, "cmt", "project.cmt")

        if exists(project_cmt):
            __log__.info("patching %s", project_cmt)
            with open(project_cmt) as f:
                data = f.readlines()

            # case insensitive list of projects
            projs = {p.name.upper(): p for p in self.slot.projects}

            newdata = []
            for line in data:
                tokens = line.strip().split()
                if len(tokens) == 3 and tokens[0] == "use":
                    if tokens[1] in projs:
                        tokens[1] = projs[tokens[1]].name
                        tokens[2] = ""
                        line = " ".join(tokens) + "\n"
                        __log__.info("result %s", line)
                newdata.append(line)

            if newdata != data:
                if not dryrun:
                    with open(project_cmt, "w") as f:
                        f.writelines(newdata)
                if patchfile:
                    write_patch(patchfile, data, newdata, project_cmt)

        # find the container package
        requirements = join(self.baseDir, self.name + "Release", "cmt", "requirements")
        if not exists(requirements):
            requirements = join(self.baseDir, self.name + "Sys", "cmt", "requirements")

        if exists(requirements):
            __log__.info("patching %s", requirements)
            with open(requirements) as f:
                data = f.readlines()

            used_pkgs = set()

            newdata = []
            for line in data:
                tokens = line.strip().split()
                if len(tokens) >= 3 and tokens[0] == "use":
                    tokens[2] = "*"
                    if len(tokens) >= 4 and tokens[3][0] not in ("-", "#"):
                        used_pkgs.add("{3}/{1}".format(*tokens))
                    else:
                        used_pkgs.add(tokens[1])
                    line = " ".join(tokens) + "\n"
                newdata.append(line)

            for added_pkg in set(self.overrides.keys()) - used_pkgs:
                if "/" in added_pkg:
                    hat, added_pkg = added_pkg.rsplit("/", 1)
                else:
                    hat = ""
                newdata.append(f"use {added_pkg} * {hat}\n")

            if not dryrun:
                with open(requirements, "w") as f:
                    f.writelines(newdata)

            if patchfile:
                write_patch(patchfile, data, newdata, requirements)

    def _fixProjectConfigJSON(self, patchfile=None, dryrun=False):
        """
        Fix 'dist-tools/projectConfig.json'.
        """
        import codecs
        import json
        from os.path import exists, join

        configfile = join(self.baseDir, "dist-tools", "projectConfig.json")

        if exists(configfile):
            __log__.info("patching %s", configfile)
            with codecs.open(configfile, encoding="utf-8") as f:
                data = f.read()

            config = json.loads(data)
            data = data.splitlines(True)

            config["version"] = self.version

            # case insensitive list of projects
            projs = {p.name.lower(): p.version for p in self.slot.projects}
            # update project versions (if defined
            if "used_projects" in config:
                for dep in config["used_projects"]["project"]:
                    dep[1] = projs.get(dep[0].lower(), dep[1])

            if "heptools" in config:
                for name in ("heptools", "lcgcmt", "lcg"):
                    if name in projs:
                        config["heptools"]["version"] = projs[name]
                        break

            newdata = json.dumps(config, indent=2).splitlines(True)

            if not dryrun:
                with codecs.open(configfile, "w", encoding="utf-8") as f:
                    f.writelines(newdata)

            if patchfile:
                write_patch(patchfile, data, newdata, configfile)

    def patch(self, patchfile=None, dryrun=False):
        """
        Modify dependencies and references of the project to the other projects
        in a slot.

        @param patchfile: a file object where the applied changes can be
                          recorded in the form of "patch" instructions.

        @warning: It make sense only for projects within a slot.
        """
        if not self.slot:
            raise ValueError(f"project {self} is not part of a slot")

        self._fixCMake(patchfile, dryrun=dryrun)
        self._fixCMT(patchfile, dryrun=dryrun)
        self._fixProjectConfigJSON(patchfile, dryrun=dryrun)


class Package:
    """
    Describe a package to be checked out.
    """

    checkout = _CheckoutMethodProperty()

    def __init__(self, name, version, **kwargs):
        """
        @param name: name of the package
        @param version: version of the package as 'vXrY' or 'HEAD'
        @param checkout: callable that can check out the specified package
        @param checkout_opts: dictionary with extra options for the checkout
                              callable
        """
        self.name = name
        if version.lower() == "head":
            version = "head"
        self.version = version
        self.container = None
        # we need to try setting checkout_opts before checkout, because
        # it could be overridden if checkout is a tuple
        self.checkout_opts = kwargs.get("checkout_opts", {})
        self.checkout = kwargs.get("checkout")

    @property
    def slot(self):
        return self.container.slot if self.container else None

    def toDict(self):
        """
        Return a dictionary describing the package, suitable to conversion to
        JSON.
        """
        data = {
            "name": self.name,
            "version": self.version,
            "checkout": self._checkout.__name__,
            "checkout_opts": self.checkout_opts,
        }
        if self.container:
            data["container"] = self.container.name
        return data

    def __eq__(self, other):
        """Equality operator."""
        elems = ("__class__", "name", "version", "_checkout", "checkout_opts")
        for elem in elems:
            if getattr(self, elem) != getattr(other, elem):
                return False
        return True

    def __ne__(self, other):
        """Non-equality operator."""
        return not (self == other)

    def __getstate__(self):
        """
        Allow pickling.
        """
        dct = {
            elem: getattr(self, elem) for elem in ("name", "version", "checkout_opts")
        }
        dct["checkout"] = self._checkout
        return copy.deepcopy(dct)

    def __setstate__(self, state):
        """
        Allow unpickling.
        """
        for key in state:
            setattr(self, key, state[key])

    @property
    def baseDir(self):
        """Name of the package directory (relative to the build directory)."""
        if self.container:
            return os.path.join(self.container.baseDir, self.name, self.version)
        else:
            return os.path.join(self.name, self.version)

    @RecordLogger(CheckoutMethods.__log__)
    @log_timing(CheckoutMethods.__log__)
    def build(self, **kwargs):
        """
        Build the package and return the return code of the build process.
        """
        from .CheckoutMethods import __log__ as log
        from .CheckoutMethods import log_call

        base = self.baseDir
        if os.path.exists(os.path.join(base, "Makefile")):
            log.info("building %s (make)", self)
            return log_call(["make"], cwd=base, **kwargs)
        elif os.path.exists(os.path.join(base, "cmt", "requirements")):
            log.info("building %s (cmt make)", self)
            # CMT is very sensitive to these variables (better to unset them)
            env = {
                key: value
                for key, value in list(os.environ.items())
                if key not in ("PWD", "CWD", "CMTSTRUCTURINGSTYLE")
            }
            base = os.path.join(base, "cmt")

            log_call(["cmt", "config"], cwd=base, env=env, **kwargs)
            return log_call(["cmt", "make"], cwd=base, env=env, **kwargs)
        log.info("%s does not require build", self)
        return {
            "retcode": 0,
            "stdout": f"{self} does not require build",
            "stderr": "",
        }

    def getVersionLinks(self):
        """
        Return a list of version aliases for the current package (only if the
        requested version is not vXrY[pZ]).
        """
        if re.match(r"v\d+r\d+(p\d+)?$", self.version):
            return []
        base = self.baseDir
        aliases = ["v999r999"]
        if os.path.exists(os.path.join(base, "cmt", "requirements")):
            for l in open(os.path.join(base, "cmt", "requirements")):
                l = l.strip()
                if l.startswith("version"):
                    version = l.split()[1]
                    aliases.append(version[: version.rfind("r")] + "r999")
                    break
        return aliases

    def __str__(self):
        """String representation of the package."""
        return f"{self.name}/{self.version}"


class _ContainedList:
    """
    Helper class to handle a list of projects bound to a slot.
    """

    __type__ = None
    __container_member__ = ""
    __id_member__ = "name"

    def _assertType(self, element):
        """
        Ensure that the type of the parameter is the allowed one.
        """
        types = self.__type__
        if not isinstance(element, types):
            try:
                if len(types) > 1:
                    typenames = ", ".join(t.__name__ for t in types[:-1])
                    typenames += " and " + types[-1].__name__
                elif types:
                    typenames = types[0].__name__
                else:
                    typenames = "()"
            except TypeError:
                typenames = types.__name__
            msg = f"only {typenames} instances are allowed"
            raise ValueError(msg)
        return element

    def __init__(self, container, iterable=None):
        """
        Initialize the list from an optional iterable, which must contain
        only instances of the required class.
        """
        self.container = container
        if iterable is None:
            self._elements = []
        else:
            self._elements = [self._assertType(i) for i in iterable]
            for element in self._elements:
                setattr(element, self.__container_member__, self.container)

    def __eq__(self, other):
        """Equality operator."""
        return (self.__class__ == other.__class__) and (
            self._elements == other._elements
        )

    def __ne__(self, other):
        """Non-equality operator."""
        return not (self == other)

    def __getitem__(self, key):
        """
        Get contained element either by name or by position.
        """
        if isinstance(key, str):
            for element in self._elements:
                id_key = getattr(element, self.__id_member__)
                if key in (id_key, id_key.replace("/", "_")):
                    return element
            raise KeyError(f"{self.__type__.__name__.lower()} {key!r} not found")
        return self._elements[key]

    def __setitem__(self, key, value):
        """
        Item assignment that keeps the binding between container and containee
        in sync.
        """
        if isinstance(key, slice):
            for v in value:
                self._assertType(v)
        else:
            self._assertType(value)
        old = self[key]
        self._elements[key] = value
        if isinstance(key, slice):
            for elem in value:
                setattr(elem, self.__container_member__, self.container)
            for elem in old:
                setattr(elem, self.__container_member__, None)
        else:
            setattr(value, self.__container_member__, self.container)
            setattr(old, self.__container_member__, None)

    def __iter__(self):
        """
        Implement Python iteration protocol.
        """
        yield from self._elements

    def __contains__(self, item):
        """
        Implement Python membership protocol.
        """

        def match(element):
            if item is element:
                return True
            key = getattr(element, self.__id_member__)
            return item == key or item == key.replace("/", "_")

        return any(match(element) for element in self)

    def insert(self, idx, element):
        """
        Item insertion that binds the added object to the container.
        """
        self._assertType(element)
        setattr(element, self.__container_member__, self.container)
        return self._elements.insert(idx, element)

    def append(self, element):
        """
        Item insertion that binds the added object to the container.
        """
        self._assertType(element)
        setattr(element, self.__container_member__, self.container)
        return self._elements.append(element)

    def extend(self, iterable):
        """
        Extend list by appending elements from the iterable.
        """
        for element in iterable:
            self.append(element)

    def __delitem__(self, key):
        """
        Item removal that disconnect the element from the container.
        """
        if isinstance(key, slice):
            old = self[key]
        else:
            old = [self[key]]
        for el in old:
            self.remove(el)

    def remove(self, element):
        """
        Item removal that disconnect the element from the container.
        """
        self._assertType(element)
        self._elements.remove(element)
        setattr(element, self.__container_member__, None)

    def __len__(self):
        """
        Return the number of elements in the list.
        """
        return len(self._elements)


class ProjectsList(_ContainedList):
    """
    Helper class to handle a list of projects bound to a slot.
    """

    __type__ = Project
    __container_member__ = "slot"


class PackagesList(_ContainedList):
    """
    Helper class to handle a list of projects bound to a slot.
    """

    __type__ = Package
    __container_member__ = "container"


class DataProject(Project):
    """
    Special Project class for projects containing only data packages.
    """

    ignore_slot_build_tool = True
    build_tool = "no_build"

    def __init__(self, name, packages=None, **kwargs):
        """
        Initialize the instance with name and list of packages.
        """
        # we use 'None' as version just to comply with Project.__init__, but the
        # version is ignored
        Project.__init__(self, name, "None", **kwargs)
        # data projects are platform independent by definition
        self.platform_independent = True
        # data projects cannot be tested by definition
        self.no_test = True
        if packages is None:
            packages = []
        self._packages = PackagesList(self, packages)

    def toDict(self):
        """
        Return a dictionary describing the data project, suitable to conversion
        to JSON.
        """
        data = {
            "name": self.name,
            "version": self.version,
            "checkout": "ignore",
            "disabled": False,
            "platform_independent": True,
            "no_test": True,
        }
        return data

    def __eq__(self, other):
        """Equality operator."""
        return Project.__eq__(self, other) and (self.packages == other.packages)

    def __ne__(self, other):
        """Non-equality operator."""
        return not (self == other)

    def __getstate__(self):
        """
        Allow pickling.
        """
        dct = Project.__getstate__(self)
        dct["_packages"] = self._packages
        dct["checkout"] = None
        return copy.deepcopy(dct)

    def __setstate__(self, state):
        """
        Allow unpickling.
        """
        for key in state:
            setattr(self, key, state[key])

    def __str__(self):
        """String representation of the project."""
        return self.name

    @property
    def baseDir(self):
        """Name of the package directory (relative to the build directory)."""
        return self.name.upper()

    @property
    def packages(self):
        "List of contained packages"
        return self._packages

    def __getattr__(self, name):
        """
        Get the project with given name in the slot.
        """
        try:
            return self._packages[name]
        except KeyError:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {name!r}"
            )

    def checkout(self, **kwargs):
        """
        Special checkout method to create a valid local copy of a DataProject
        using an existing one as a baseline (cloning it with symlinks).
        """
        from shutil import rmtree

        from .CheckoutMethods import __log__ as log

        # look for an existing version of the project before creating the local
        # directory
        path = find_path(self.baseDir)

        log.debug("create packages directories")
        ensureDirs([os.path.dirname(package.baseDir) for package in self.packages])

        log.debug("create shallow clone of %s", self.name)

        ignore_package_versions = IgnorePackageVersions(self.packages)

        def ignore(src, names):
            ignored = ignore_package_versions(src, names)
            ignored.extend(name for name in names if name.startswith(".cvmfs"))
            return ignored

        if path:
            shallow_copytree(path, self.baseDir, ignore)
        else:
            cmt_dir = os.path.join(self.baseDir, "cmt")
            ensureDirs([cmt_dir])
            with open(os.path.join(cmt_dir, "project.cmt"), "w") as proj_cmt:
                proj_cmt.write(f"project {self.name}\n")

        # separate checkout arguments from build arguments
        co_kwargs = {key: value for key, value in kwargs.items() if key in {"export"}}
        b_kwargs = {key: value for key, value in kwargs.items() if key in {"jobs"}}

        log.info("checkout data packages in %s", self.name)
        outputs = [package.checkout(**co_kwargs) for package in self.packages]

        log.info("building data packages in %s", self.name)
        outputs += [package.build(**b_kwargs) for package in self.packages]

        log.debug("create symlinks")
        for package in self.packages:
            for link in package.getVersionLinks():
                dest = os.path.normpath(os.path.join(package.baseDir, os.pardir, link))
                if os.path.islink(dest) or os.path.exists(dest):
                    __log__.debug("removing %s", dest)
                    if os.path.isdir(dest) and not os.path.islink(dest):
                        rmtree(dest)
                    else:
                        os.remove(dest)
                __log__.debug("creating symlink %s for %s", link, package.name)
                os.symlink(package.version, dest)

        from .CheckoutMethods import _merge_outputs

        return _merge_outputs(outputs)


class DBASE(DataProject):
    pass


class PARAM(DataProject):
    pass


class _SlotMeta(type):
    """
    Metaclass for Slot.
    """

    def __new__(cls, name, bases, dct):
        """
        Instrument Slot classes.
        """
        dct["__build_tool__"] = dct.get("build_tool")
        dct["build_tool"] = _BuildToolProperty()
        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        """
        Class initialization by the metaclass.
        """
        super().__init__(name, bases, dct)

        if "projects" in dct:
            cls.__projects__ = dct["projects"]
        cls.projects = property(lambda self: self._projects)

        env = dct.get("env", [])
        if bases and hasattr(bases[0], "__env__"):
            cls.__env__ = bases[0].__env__ + env
        else:
            cls.__env__ = env


class Slot(metaclass=_SlotMeta):
    """
    Generic nightly build slot.
    """

    __slots__ = (
        "_name",
        "_projects",
        "env",
        "_build_tool",
        "disabled",
        "desc",
        "platforms",
        "error_exceptions",
        "warning_exceptions",
        "preconditions",
        "cache_entries",
        "build_id",
        "no_patch",
        "with_version_dir",
        "no_test",
        "metadata",
        "_source",
    )
    __projects__ = []
    __env__ = []

    def __init__(self, name, projects=None, **kwargs):
        """
        Initialize the slot with name and optional list of projects.

        @param name: name of the slot
        @param projects: (optional) list of Project instances
        @param env: (optional) list of strings ('name=value') used to modify the
                    environment for the slot
        @param disabled: if True the slot should not be used in the nightly
                         builds
        @param desc: description of the slot
        @param platforms: list of platform ids the slot should be built for
        @param warning_exceptions: list of regex of warnings that should be
                                   ignored
        @param error_exceptions: list of regex of errors that should be ignored
        @param cache_entries: dictionary of CMake cache variables to preset
        @param build_id: numeric id for the build
        @param no_patch: if set to True, sources will not be patched (default to
                         False) Kept for retro-compatibility
        @param with_version_dir: if set to True, sources will be checkout in
                                 the path: Project/Project_version
        @param no_test: if set to True, tests should not be run for this slot)
        @param metadata: dictionary with extra information, e.g. for the dashboard
        """
        self._name = name
        self.build_id = kwargs.get("build_id", 0)

        if projects is None:
            projects = self.__projects__
        self._projects = ProjectsList(self, projects)
        self.env = kwargs.get("env", list(self.__env__))
        self.build_tool = kwargs.get("build_tool", self.__build_tool__)
        self.disabled = kwargs.get("disabled", False)
        desc = kwargs.get("desc")
        if desc is None:
            desc = (self.__doc__ or "<no description>").strip()
        self.desc = desc

        self.platforms = kwargs.get("platforms", [])
        if isinstance(self.platforms, str):
            self.platforms = [self.platforms]
        for p in self.platforms:
            assert re.match(VALID_PLATFORM_RE, p), f"invalid platform: {p!r}"

        self.error_exceptions = kwargs.get("error_exceptions", [])
        self.warning_exceptions = kwargs.get("warning_exceptions", [])

        self.preconditions = kwargs.get("preconditions", [])

        self.cache_entries = kwargs.get("cache_entries", {})

        self.no_patch = kwargs.get("no_patch", False)
        self.with_version_dir = kwargs.get("with_version_dir", False)
        self.no_test = kwargs.get("no_test", False)

        self.metadata = kwargs.get("metadata", {})

        # get the name of the Python module calling the constructor,
        # excluding irrelevant frames
        import inspect

        caller = inspect.currentframe().f_back
        while caller.f_code.co_name in _slot_factories:
            caller = caller.f_back
        self._source = caller.f_globals["__name__"]

        # add this slot to the global list of slots
        global slots
        slots[name] = self

    def toDict(self):
        """
        Return a dictionary describing the slot, suitable to conversion to JSON.
        """
        from itertools import chain

        data = {
            "slot": self.name,
            "description": self.desc,
            "projects": [proj.toDict() for proj in self.projects],
            "disabled": self.disabled,
            "build_tool": self.build_tool.__class__.__name__,
            "env": self.env,
            "error_exceptions": self.error_exceptions,
            "warning_exceptions": self.warning_exceptions,
            "preconditions": self.preconditions,
            "build_id": self.build_id,
        }
        if self.cache_entries:
            data["cmake_cache"] = self.cache_entries
        if self.no_patch:
            data["no_patch"] = True
        if self.with_version_dir:
            data["with_version_dir"] = True
        if self.no_test:
            data["no_test"] = True
        if self.metadata:
            data["metadata"] = self.metadata

        pkgs = list(
            chain.from_iterable(
                [pack.toDict() for pack in cont.packages]
                for cont in self.projects
                if isinstance(cont, DataProject)
            )
        )
        data["packages"] = pkgs
        data["platforms"] = self.platforms

        return data

    @classmethod
    @slot_factory
    def fromDict(cls, data):
        """
        Create a Slot instance from a dictionary like the one returned by
        Slot.toDict().
        """
        containers = {}
        for pkg in data.get("packages", []):
            container = pkg.get("container", "DBASE")
            if container not in containers:
                containers[container] = globals()[container]()
            container = containers[container]
            pkg = Package(
                pkg["name"],
                pkg["version"],
                checkout=pkg.get("checkout"),
                checkout_opts=pkg.get("checkout_opts", {}),
            )
            container.packages.append(pkg)

        slot = cls(
            name=data.get("slot", None),
            projects=list(containers.values()),
            env=data.get("env", []),
            desc=data.get("description"),
            disabled=data.get("disabled", False),
            metadata=data.get("metadata", {}),
        )
        slot.platforms = data.get("platforms", data.get("default_platforms", []))

        if data.get("USE_CMT"):
            slot.build_tool = "cmt"
        if "build_tool" in data:
            slot.build_tool = data["build_tool"]

        slot.projects.extend(
            [
                Project.fromDict(prj)
                for prj in data.get("projects", [])
                if prj["name"] not in containers
            ]
        )

        slot.error_exceptions = data.get("error_exceptions", [])
        slot.warning_exceptions = data.get("warning_exceptions", [])
        slot.preconditions = data.get("preconditions", [])

        slot.cache_entries = data.get("cmake_cache", {})

        slot.build_id = data.get("build_id", 0)

        slot.no_patch = data.get("no_patch", False)
        slot.with_version_dir = data.get("with_version_dir", False)
        slot.no_test = data.get("no_test", False)

        return slot

    def __eq__(self, other):
        """
        Equality operator.
        """
        elems = (
            "__class__",
            "name",
            "projects",
            "env",
            "disabled",
            "desc",
            "platforms",
            "error_exceptions",
            "warning_exceptions",
            "preconditions",
        )
        for elem in elems:
            if getattr(self, elem) != getattr(other, elem):
                return False
        return self.build_tool.__class__.__name__ == other.build_tool.__class__.__name__

    def __ne__(self, other):
        """Non-equality operator."""
        return not (self == other)

    def __getstate__(self):
        """
        Allow pickling.
        """
        dct = {
            elem: getattr(self, elem)
            for elem in (
                "_projects",
                "env",
                "disabled",
                "desc",
                "platforms",
                "error_exceptions",
                "warning_exceptions",
                "preconditions",
            )
        }
        dct["_name"] = self._name
        dct["build_tool"] = self._build_tool.__class__.__name__
        return copy.deepcopy(dct)

    def __setstate__(self, state):
        """
        Allow unpickling.
        """
        for key in state:
            setattr(self, key, state[key])
        global slots
        slots[self._name] = self

    def _clone(self, new_name):
        """
        Return a new instance configured as this one except for the name.
        """
        return Slot(new_name, projects=self.projects)

    @property
    def name(self):
        """
        Name of the slot.
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        Change the name of the slot, keeping the slots global list in sync.
        """
        global slots
        del slots[self._name]
        self._name = value
        slots[self._name] = self

    @property
    def enabled(self):
        return not self.disabled

    @enabled.setter
    def enabled(self, value):
        self.disabled = not value

    def __getattr__(self, name):
        """
        Get the project with given name in the slot.
        """
        try:
            return self._projects[name]
        except KeyError:
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {name!r}"
            )

    def __delattr__(self, name):
        """
        Remove a project from the slot.
        """
        self.projects.remove(self.projects[name])

    def __dir__(self):
        """
        Return the list of names of the attributes of the instance.
        """
        return list(self.__dict__.keys()) + [proj.name for proj in self.projects]

    def __str__(self):
        """String representation of the slot."""
        return f"{self.name}.{self.build_id}" if self.build_id else self.name

    def id(self):
        """
        String representing the slot instance.

        >>> s = Slot('test', build_id=10)
        >>> s.id()
        'nightly/test/10'
        >>> s = Slot('another')
        >>> s.metadata['flavour'] = 'testing'
        >>> s.id()
        'testing/another/0'
        """
        return "/".join(
            [
                self.metadata.get("flavour", "nightly"),
                self.name,
                str(self.build_id),
            ]
        )

    def __hash__(self):
        return hash(self.id())

    @property
    def activeProjects(self):
        """
        Generator yielding the projects in the slot that do not have the
        disabled property set to True.
        """
        for p in self.projects:
            if p.enabled:
                yield p

    def checkout(self, projects=None, ignore_errors=False, **kwargs):
        """
        Checkout all the projects in the slot.
        """

        class NullContext:
            def __init__(self, project):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        context = kwargs.pop("context", NullContext)

        results = OrderedDict()
        for project in self.activeProjects:
            if projects is None or project.name in projects:
                results[project.name] = {}
                try:
                    with context(project) as ctx:
                        results[project.name] = project.checkout(**kwargs)
                        ctx.result = results[project.name]
                except (RuntimeError, AssertionError) as x:
                    msg = f"failed to checkout {project}: {type(x).__name__}: {x}"
                    if "error" not in results[project.name]:
                        results[project.name]["error"] = []
                    results[project.name]["error"].append(msg)
                    if ignore_errors:
                        __log__.warning(msg)
                    else:
                        raise
        return results

    def patch(self, patchfile=None, dryrun=False):
        """
        Patch all active projects in the slot to have consistent dependencies.
        """
        if self.no_patch:
            raise ValueError(f"slot {self} cannot be patched (no_patch=True)")
        for project in self.activeProjects:
            project.patch(patchfile, dryrun=dryrun)

    def dependencies(self, projects=None):
        """
        Dictionary of dependencies between projects (only within the slot).
        """
        deps = self.fullDependencies()
        if projects:
            for unwanted in set(deps) - set(projects):
                deps.pop(unwanted)
        for key in deps:
            deps[key] = [val for val in deps[key] if val in deps]
        return deps

    def fullDependencies(self):
        """
        Dictionary of dependencies of projects (also to projects not in the
        slot).
        """
        return OrderedDict([(p.name, p.dependencies()) for p in self.projects])

    def dependencyGraph(self, keep_extern_nodes=False):
        """
        Return a networkx.DiGraph of the dependencies between projects.

        If keep_extern_nodes is False, only the projects in the slot are considered,
        otherwise we get also dependencies outside the slot.

        The edges go from dependee to depender (e.g. Gaudi -> LHCb).
        """
        from networkx import DiGraph

        if keep_extern_nodes:
            deps = self.fullDependencies()
        else:
            deps = self.dependencies()
        return DiGraph((d, p) for p in deps for d in deps[p])

    def environment(self, envdict=None):
        """
        Return a dictionary with the environment for the slot.

        If envdict is provided, it will be used as a starting point, otherwise
        the environment defined by the system will be used.
        """
        result = dict(os.environ) if envdict is None else dict(envdict)
        applyenv(result, self.env)
        # ensure that the current directory is first in the CMake and CMT
        # search paths
        from os import pathsep

        curdir = os.getcwd()
        for var in ("CMTPROJECTPATH", "CMAKE_PREFIX_PATH"):
            if var in result:
                result[var] = pathsep.join([curdir, result[var]])
            else:
                result[var] = curdir
        return result

    def _projects_by_deps(self, projects=None):
        deps = self.dependencies(projects=projects)
        return [
            project
            for project in [
                getattr(self, project_name) for project_name in sortedByDeps(deps)
            ]
            if project.enabled
        ]

    def buildGen(self, **kwargs):
        """
        Generator to build projects in the slot, one by one.

        @param projects: optional list of projects to build [default: all]

        @return: tuples (project_name, build_result)
        """
        before = kwargs.pop("before", None)
        for project in self._projects_by_deps(kwargs.pop("projects", None)):
            if project.enabled:
                if before:
                    before(project)
                yield (
                    project,
                    project.build(cache_entries=self.cache_entries, **kwargs),
                )

    def build(self, **kwargs):
        """
        Build projects in the slot.

        @param projects: optional list of projects to build [default: all]
        """
        return OrderedDict(
            (proj.name, result) for proj, result in self.buildGen(**kwargs)
        )

    def clean(self, **kwargs):
        """
        Clean projects in the slot.

        @param projects: optional list of projects to build [default: all]
        """
        results = OrderedDict()
        for project in self._projects_by_deps(kwargs.pop("projects", None)):
            results[project.name] = project.clean(**kwargs)
        return results

    def testGen(self, **kwargs):
        """
        Generator to test projects in the slot, one by one.

        @param projects: optional list of projects to build [default: all]
        """
        if self.no_test:
            raise ValueError(f"slot {self} cannot be tested (no_test=True)")
        before = kwargs.pop("before", None)
        for project in self._projects_by_deps(kwargs.pop("projects", None)):
            if project.enabled and not project.no_test:
                if before:
                    before(project)
                yield (
                    project,
                    project.test(cache_entries=self.cache_entries, **kwargs),
                )

    def test(self, **kwargs):
        """
        Test projects in the slot.

        @param projects: optional list of projects to build [default: all]
        """
        return OrderedDict(
            (proj.name, result) for proj, result in self.testGen(**kwargs)
        )


def extractVersion(tag):
    """
    Extract the version number from as SVN tag.

    >>> extractVersion('GAUDI_v23r8')
    'v23r8'
    >>> extractVersion('LCGCMT_preview')
    'preview'
    >>> extractVersion('HEAD')
    'HEAD'
    """
    if "_" in tag:
        return tag.split("_", 1)[1]
    return tag


def save(dest, config):
    """
    Helper function to dump the current configuration to a file.
    """
    f = open(dest, "w")
    f.write(configToString(config))
    f.close()


def configToString(config):
    """
    Convert the configuration to a string.
    """
    import json

    if isinstance(config, Slot):
        config = config.toDict()
    return str(json.dumps(config, sort_keys=True, indent=2, separators=(",", ": ")))


def parse(path):
    """
    Create a Slot instance from a JSON file describing the configuration.
    """
    import json
    from os.path import basename, splitext

    __log__.debug("loading %s", path)
    data = json.load(open(path, "rb"))
    if "slot" not in data:
        data["slot"] = splitext(basename(path))[0]
    slot = Slot.fromDict(data)
    slot._source = path
    return slot


def getSlot(name, module=None):
    """
    Find the slot with the given name.

    It's possible to specify a module name then forwarded to loadConfig().
    """
    slot = loadConfig(module).get(name)
    if slot:
        __log__.debug(f"using slot {slot.name} from {slot._source}")
    else:
        raise RuntimeError(
            "cannot find slot {}{}".format(name, (" in " + module) if module else "")
        )
    return slot


###############################################################################
# Helpers
###############################################################################
@slot_factory
def cloneSlot(slot, name):
    """
    Clone a slot creating a new one with the given name.
    """
    if not name:
        raise ValueError("name argument must not be empty")
    if isinstance(slot, str):
        global slots
        slot = slots[slot]
    desc = slot.toDict()
    desc["slot"] = name
    return Slot.fromDict(copy.deepcopy(desc))


# used by try_call to keep track of the failures
_failures_count = 0


def try_call(msg, default_result=None):
    """
    Decorator to wrap a function call in a try-except block and ignore
    exceptions (printing a warning message).
    """

    def decorate(method):
        from functools import wraps

        @wraps(method)
        def wrapper(*args, **kwargs):
            global _failures_count
            try:
                return method(*args, **kwargs)
            except Exception as x:
                _failures_count += 1
                __log__.warning(
                    msg.format(*args, **kwargs) + f": {x.__class__.__name__}: {x}"
                )
                return default_result

        return wrapper

    return decorate


def loadConfig(module=None):
    """
    Load all slots from a config module.
    """
    from importlib import import_module
    from os.path import abspath, exists, isdir, join, splitext

    import git

    orig_path = list(sys.path)
    try:
        if module is None:
            module_name, attribute = "lhcbnightlyconf", "slots"
        elif ":" in module:
            module_name, attribute = module.split(":", 1)
        else:
            module_name, attribute = module, "slots"
        sys.path.insert(0, os.curdir)
        sys.path.insert(0, "configs")
        m = import_module(module_name)
        try:  # to get the commit id of the config directory
            config_id = (
                git.Repo(m.__path__[0], search_parent_directories=True)
                .rev_parse("HEAD")
                .hexsha
            )
        except git.GitError:
            config_id = None
        slot_list = getattr(m, attribute)
        logging.debug("using explicit configuration")
        slot_dict = {}
        for slot in slot_list:
            assert (
                slot.name not in slot_dict
            ), f"Slot {slot.name} defined in 2 places: {slot_dict[slot.name]._source} and {slot._source}"
            if config_id:
                slot.metadata["config_id"] = config_id
            slot_dict[slot.name] = slot
        return slot_dict
    except (ImportError, AttributeError, TypeError):
        import traceback

        traceback.print_exc()
    sys.path = orig_path

    logging.warning("using implicit configuration")
    configdir = "configs" if module is None else module

    if not isdir(configdir):
        global _failures_count
        _failures_count += 1
        __log__.warning("%s is not a valid directory", configdir)
        return slots

    __log__.debug("loading all slots from %s", configdir)
    names = os.listdir(configdir)
    names.sort()

    # protect from exceptions
    parse_ = try_call("failed to parse {0}")(parse)
    import_module = try_call("failed to import {0}")(import_module)

    # Get all slots defined as JSON
    for name in [name for name in names if name.endswith(".json")]:
        parse_(join(configdir, name))

    # Now looking for python modules to load
    # First finding all python modules in this directory
    submodules = [f[0] for f in map(splitext, names) if f[1] == ".py"]

    # Now importing them in turn...
    old_path = list(sys.path)
    try:
        sys.path.insert(0, abspath(configdir))
        for submodule in submodules:
            __log__.debug("loading %s", submodule)
            import_module(submodule)
    finally:
        sys.path = old_path
    __log__.debug("loaded %d slots", len(slots))
    return slots


def findSlot(name, flavour="nightly", server=None, dbname=None, raise_if_aborted=False):
    """
    Helper to load a Slot configuration from filename or from slot name.

    If name matches '<name>.<build_id>', the configuration is retrieved from
    the dashboard.
    """
    if re.match(r"^[-_0-9a-zA-Z]+\.\d+$", name):
        url = "/".join(
            [server or Dashboard.SERVER_URL, dbname or Dashboard.dbName(flavour), name]
        )
        __log__.debug("retrieving %s", url)
        raw = json.load(urllib.request.urlopen(url))
        slot = Slot.fromDict(raw["config"])
        if raw.get("aborted"):
            if raise_if_aborted:
                from LbNightlyTools.Utils import SlotAborted

                raise SlotAborted(name, raw["aborted"])
            slot.metadata["aborted"] = raw["aborted"]
        return slot
    elif os.path.exists(name.split("#")[0]):
        return parse(name)
    else:
        return getSlot(name)


KeyTuple = namedtuple("KeyTuple", ["flavour", "name", "id", "project"])
KeyTuple.__str__ = lambda self: "/".join(str(i) for i in self if i is not None)


def _parse_key(key):
    """
    Parse a key like "[flavour/]slotname[/build_id][/project]" to its parts.

    Returns a named tuple with the elements.

    NOTE: if `flavour/` is present, there must be also at least one of `/build_id`
          or `/project`, as the string "a/b" is always interpreted as "slot/project"
    """
    # defaults for optional entries
    flavour, build_id, project = "nightly", "0", None
    name = None  # used to flag invalid keys

    tokens = key.split("/")
    if len(tokens) == 1:  # only slot name
        name = tokens[0]
    elif len(tokens) == 2:  # slot/build_id or slot/project
        name = tokens[0]
        if tokens[1].isdigit():
            build_id = tokens[1]
        else:
            project = tokens[1]
    elif len(tokens) == 3:  # f/s/b, f/s/p or s/b/p
        if tokens[2].isdigit():  # f/s/b
            flavour, name, build_id = tokens
        elif tokens[1].isdigit():  # s/b/p
            name, build_id, project = tokens
        else:  # f/s/p
            flavour, name, project = tokens
    elif len(tokens) == 4:
        if tokens[2].isdigit():
            flavour, name, build_id, project = tokens

    if not name:
        raise ValueError(f"{key!r} is not a valid key")

    return KeyTuple(flavour, name, int(build_id), project)


def get(key):
    """
    Return the instance identified by a key like "[flavour/]slotname[/build_id][/project]".

    When the build_id part is present, the slot configuration is taken from CouchDB.
    """
    flavour, slot, build_id, project = _parse_key(key)
    if build_id:
        slot = f"{slot}.{build_id}"
    slot = findSlot(slot, flavour)
    slot.metadata["flavour"] = flavour
    # clone slot instance
    slot = Slot.fromDict(slot.toDict())
    if project is None:
        return slot
    else:
        return slot.projects[project]


def pushDataToFrontEnd(config_module):
    """
    Sends slots name that can be built to the front-end
    """
    front_end_token = os.environ.get("FRONT_END_TOKEN", None)
    front_end_url = os.environ.get("FRONT_END_URL", None)

    if front_end_url is None:
        raise Exception("Front-end url does not exists in the environment")

    if front_end_token is None:
        raise Exception("Front-end token does not exists in the environment")

    params = {
        "token": front_end_token,
        "slots": ";".join([name for name in sorted(loadConfig(config_module))]),
    }
    send_data = urllib.parse.urlencode(params)
    response = urllib.request.urlopen(front_end_url, send_data)
    response.read()


def check_slot(slot):
    """
    Check that a slot configuration is valid.
    """
    good = True
    log = logging.getLogger(slot.name)

    def check_type(field_name, types, value=None):
        if value is None:
            value = getattr(slot, field_name)
        if not isinstance(value, types):
            log.error(
                "invalid %s type: found %s, expected one of [%s]",
                field_name,
                type(value).__name__,
                ", ".join(t.__name__ for t in types),
            )
            return False
        return True

    def check_list_of_strings(field_name, name, regex):
        good = check_type(field_name, (list, tuple))
        if good:
            for x in getattr(slot, field_name):
                if check_type(name, (str,), x):
                    if not re.match(regex, x):
                        log.error("invalid %s value: %r", name, x)
                        good = False
                else:
                    good = False
        return good

    for field_name in ("warning_exceptions", "error_exceptions"):
        good &= check_type(field_name, (list, tuple))
        for x in getattr(slot, field_name):
            try:
                re.compile(x)
            except Exception as err:
                good = False
                log.error("%s: invalid value %r: %s", field_name, x, err)

    good &= check_list_of_strings("platforms", "platform", VALID_PLATFORM_RE)
    good &= check_list_of_strings("env", "env setting", r"^[a-zA-Z_][a-z0-9A-Z_]*=")

    return good


def check_config():
    from argparse import ArgumentParser

    import LbNightlyTools.Configuration as LBNC
    from LbNightlyTools.Configuration import loadConfig
    from LbNightlyTools.GitlabUtils import resolveMRs

    parser = ArgumentParser()
    parser.add_argument(
        "module",
        nargs="?",
        help="name of the Python module to import to get the slots from"
        ' (by default "lhcbnightlyconf"),'
        ' an optional ":name" suffix can be used to specify the attribute '
        "of the module that contains the list of slots to use (by default "
        '"slots")',
    )
    parser.add_argument(
        "--debug",
        action="store_const",
        dest="log_level",
        const=logging.DEBUG,
        help="print debug messages",
    )
    parser.add_argument(
        "--dump-json",
        metavar="FILENAME",
        help="dump all loaded slots configuration as a JSON list of objects",
    )
    parser.add_argument(
        "--resolve-mrs",
        action="store_true",
        help="resolve symbolic merge requests (all, label=X...) to a list "
        "pairs (mr_iid, commit_id)",
    )
    parser.set_defaults(
        module="lhcbnightlyconf", log_level=logging.INFO, resolve_mrs=False
    )
    args = parser.parse_args()

    if args.resolve_mrs and not os.environ.get("GITLAB_TOKEN"):
        parser.error(
            "evironment variable GITLAB_TOKEN must be " "set to use --resolve-mrs"
        )

    logging.basicConfig(level=args.log_level)

    slots = loadConfig(args.module)

    print(
        f"{len(slots)} slots configured ({len([s for s in list(slots.values()) if s.enabled])} enabled)"
    )
    if args.resolve_mrs:
        for slot in list(slots.values()):
            resolveMRs(slot)

    from tabulate import tabulate

    print(
        tabulate(
            [
                [
                    name,
                    "X" if slots[name].enabled else " ",
                    slots[name]._source,
                ]
                for name in sorted(slots)
            ],
            headers=("slot", "enabled", "source"),
            tablefmt="grid",
        )
    )

    logging.debug("running semantics checks")
    if not all(check_slot(slot) for slot in slots.values()):
        return 1

    logging.debug("converting slots to JSON")
    json_str = json.dumps([slots[name].toDict() for name in sorted(slots)], indent=2)
    if args.dump_json:
        logging.info("writing slot details to %s", args.dump_json)
        with open(args.dump_json, "w") as f:
            f.write(json_str)

    if LBNC._failures_count:
        logging.error(
            "%d failures loading nightly builds configuration", LBNC._failures_count
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(check_config())

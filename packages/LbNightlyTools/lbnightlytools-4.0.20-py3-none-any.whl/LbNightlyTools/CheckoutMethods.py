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
# pylint: disable=I0011
"""
Module grouping the common checkout functions.
"""
import logging
import os
import re
import shutil
import sys
from subprocess import PIPE, Popen

from LbNightlyTools.GitlabUtils import gitlabGroup
from LbNightlyTools.Utils import (
    ensureDirs,
    getAllMergeRequestIDs,
    getDefaultBranch,
    getMRTargetBranch,
    gitlabProjectExists,
    log_call,
    notifyMergeRequest,
    retry_log_call,
)

__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

__log__ = logging.getLogger(__name__)
__log__.setLevel(logging.DEBUG)


def decorate_log_call(func):
    """
    Wrap *log_call functions to send log messages to __log__ by default.
    """
    from functools import wraps

    @wraps(func)
    def wrapped(*args, **kwargs):  # pylint: disable=C0111
        if args:
            cmd = args[0]
            if "logger" not in kwargs:
                kwargs["logger"] = __log__.getChild(cmd[0].replace(".", "_"))
            where = os.path.abspath(kwargs.get("cwd", os.getcwd()))
            kwargs["logger"].debug("(%s)$ %s", where, " ".join(map(repr, cmd)))
        return func(*args, **kwargs)

    return wrapped


log_call = decorate_log_call(log_call)
retry_log_call = decorate_log_call(retry_log_call)


def _merge_outputs(outputs):
    """
    Helper function to merge the tuples returned by log_call.

    >>> out = _merge_outputs([{'retcode': 1, 'stdout': 'a\\n', 'stderr': ''},
    ...                       {'retcode': 0, 'stdout': 'b\\n', 'stderr': ''}])
    >>> out == {'retcode': 1, 'stdout': 'a\\nb\\n', 'stderr': ''}
    True

    The output is guaranteed to be str even when some of the inputs are bytes.

    >>> out = _merge_outputs([{'retcode': 1, 'stdout': 'a\\n', 'stderr': b''},
    ...                       {'retcode': 0, 'stdout': b'b\\n', 'stderr': ''}])
    >>> out == {'retcode': 1, 'stdout': 'a\\nb\\n', 'stderr': ''}
    True
    """
    from LbNightlyTools.Utils import coerce_str

    returncode = 0
    for out in outputs:
        if out["retcode"]:
            returncode = out["retcode"]
    return {
        "retcode": returncode,
        "stdout": "".join(coerce_str(step["stdout"]) for step in outputs),
        "stderr": "".join(coerce_str(step["stderr"]) for step in outputs),
    }


def ignore(desc, export=False):
    """
    Special checkout function used to just declare a project version in the
    configuration but do not perform the checkout, so that it's picked up from
    the release area.
    """
    log = __log__.getChild("ignore")
    log.info("checkout not requested for %s", desc)
    return {
        "retcode": 0,
        "stdout": f"checkout not requested for {desc}",
        "stderr": "",
    }


class GitRepository:
    """
    Class to simplify manipulation of local git repositories.
    """

    def __init__(self, path=os.curdir, url=None):
        """
        Create an instance from an existing repository or cloning a remote one.
        """
        log = __log__.getChild("git")
        if url:
            log.debug("cloning git repository %s", url)
            retry_log_call(
                ["git", "clone", "--no-checkout", url, path], retry=3, retry_sleep=600
            )
        assert os.path.isdir(os.path.join(path, ".git")), "not a git repository"
        self.path = path

        if url and "gitlab.cern.ch" in url:
            # fetch merge request branches (if it's a gitlab repository)
            proc = Popen(
                ["git", "config", "--get-all", "remote.origin.fetch"],
                cwd=self.path,
                stdout=PIPE,
            )
            if "origin/merge-requests" not in proc.communicate()[0].decode(
                "utf-8", errors="replace"
            ):
                # it must be configured
                __log__.getChild("git").debug("getting merge-requests branches")
                fetch = (
                    "+refs/merge-requests/*/head:"
                    "refs/remotes/origin/merge-requests/*"
                )
                log_call(
                    ["git", "config", "--add", "remote.origin.fetch", fetch],
                    cwd=self.path,
                )
                retry_log_call(
                    ["git", "fetch", "-q", "origin"],
                    cwd=self.path,
                    retry=3,
                    retry_sleep=600,
                )

    def remotes(self):
        """
        Return the remote repositories defined for fetch, as a dictionary
        name -> url.
        """
        proc = Popen(["git", "remote", "-v"], cwd=self.path, stdout=PIPE)
        lines = proc.communicate()[0].decode("utf-8", errors="replace").splitlines()
        pattern = re.compile(r"(\S+)\s+(\S+)\s+\(fetch\)$")
        return dict(m.groups() for m in map(pattern.match, lines) if m)

    def branches(self):
        """
        Return a list of all branches (local and remote) known by the
        repository.
        """
        proc = Popen(["git", "branch", "-a"], cwd=self.path, stdout=PIPE)
        return {
            branch[2:].rstrip()
            for branch in proc.communicate()[0]
            .decode("utf-8", errors="replace")
            .splitlines()
        }

    def tags(self):
        """
        Return a list of all tags known by the repository.
        """
        proc = Popen(["git", "tag"], cwd=self.path, stdout=PIPE)
        return {
            tag.strip()
            for tag in proc.communicate()[0]
            .decode("utf-8", errors="replace")
            .splitlines()
        }

    def add_remote(self, name, url, retry=True):
        """
        Add a new remote repository definition.
        """
        __log__.getChild("git").debug("adding remote %s as %s", url, name)
        log_call(["git", "remote", "add", name, url], cwd=self.path)
        retry_log_call(
            ["git", "fetch", "-q", name],
            cwd=self.path,
            retry=3 if retry else 0,
            retry_sleep=600,
        )
        retry_log_call(
            ["git", "fetch", "-q", "--tags", name],
            cwd=self.path,
            retry=3 if retry else 0,
            retry_sleep=600,
        )

    def create_branch(self, name, commit="HEAD"):
        __log__.getChild("git").debug(
            "creating and checkint out branch %s from %s", name, commit
        )
        log_call(["git", "checkout", "-b", name, commit], cwd=self.path)

    def resolve_commit(self, commit, remote="origin"):
        """
        Try to resolve the commit as a qualified branch name (from the remote),
        and return the found name and the commit id.

        If the commit is not the name of a branch, it's used as is.
        """
        if not commit or commit == "HEAD":
            # get the current branch name (http://stackoverflow.com/a/1418022)
            commit = self.rev_parse("--abbrev-ref", "HEAD")
        else:
            branches = self.branches()

            if commit not in branches:
                for branch in [f"{remote}/{commit}", f"{commit}"]:
                    if ("remotes/" + branch) in branches:
                        commit = branch
                        break

        commit_id = self.rev_parse(commit)
        return commit, commit_id

    def checkout(self, commit, paths=None, quiet=False):
        """
        Checkout the required commit, optionally limited to the specified
        paths.
        """
        if isinstance(paths, str):
            paths = [paths]
        if paths:
            paths.insert(0, "--")
        else:
            paths = []
        cmd = ["git", "checkout", commit] + paths
        if quiet:
            cmd.insert(2, "--quiet")
        return log_call(cmd, cwd=self.path)

    def init_submodules(self):
        """
        Initialize and update defined submodules, if present.
        """
        if os.path.exists(os.path.join(self.path, ".gitmodules")):
            try:
                retry_log_call(
                    ["git", "submodule", "update", "--init", "--recursive"],
                    cwd=self.path,
                    retry=3,
                    retry_sleep=30,
                )
            except RuntimeError as err:
                __log__.warning(str(err))
            return [
                os.path.join(self.path, l.split()[1])
                for l in Popen(
                    ["git", "submodule", "status", "--recursive"],
                    cwd=self.path,
                    stdout=PIPE,
                )
                .communicate()[0]
                .decode("utf-8", errors="replace")
                .splitlines()
            ]
        return []

    def merge(self, commit, extra_args=None):
        """
        Merge the specified commit into the current branch.
        """
        cmd = ["git", "merge", "--no-ff"]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(commit)
        results = log_call(cmd, cwd=self.path)
        if results["retcode"]:
            __log__.getChild("git").debug("revert to previous state")
            self.reset(hard=True)
        return results

    def reset(self, commit="HEAD", hard=False):
        """
        Call a git reset on the repository.
        """
        cmd = ["git", "reset"]
        if hard:
            cmd.append("--hard")
        cmd.append(commit)
        log_call(cmd, cwd=self.path)

    def tag(self, name, commit="HEAD", message=None, force=False):
        """
        Tag a given commit (default HEAD).
        """
        cmd = ["git", "tag"]
        if force:
            cmd.append("-f")
        if message:
            cmd.extend(["-m", message])
        cmd.extend([name, commit])
        log_call(cmd, cwd=self.path)

    def push_tag(self, name, remote="origin", force=False):
        """
        Push a tag to the remote repository.
        """
        cmd = ["git", "push"]
        if force:
            cmd.append("-f")
        cmd.extend([remote, "tag", name])
        log_call(cmd, cwd=self.path)

    def push_branch(self, name, remote="origin", force=False):
        """
        Push a branch to the remote repository.
        """
        cmd = ["git", "push"]
        if force:
            cmd.append("-f")
        cmd.extend([remote, name])
        log_call(cmd, cwd=self.path)

    def rev_parse(self, *args):
        """
        Simple wrapper around "git rev-parse".
        """
        cmd = ["git", "rev-parse"]
        cmd.extend(args)
        return (
            Popen(cmd, cwd=self.path, stdout=PIPE)
            .communicate()[0]
            .decode("utf-8", errors="replace")
            .strip()
        )

    def show_branch(self, *args):
        """
        Simple wrapper around "git show-branch".
        """
        cmd = ["git", "show-branch"]
        cmd.extend(args)
        log_call(cmd, cwd=self.path)


class GitMergeHandler(GitRepository):
    """
    Helper to handle merges to a git repository.
    """

    def __init__(self, commit, url=None, remote_name=None, path=os.curdir):
        """
        Initialize the handler with the details of the merge:

        @param commit: commit to merge
        @param url: (optional) url for the incoming commit
        @param remote_name: (optional) name to use for the remote repository
        """
        GitRepository.__init__(self, path)
        self.apply_result = None
        self.remote_name = self.prepare_remote(remote_name, url)
        self.commit, self.commit_id = self.resolve_commit(commit, self.remote_name)
        if url is None:
            url = self.remotes()[self.remote_name]
        __log__.getChild("git").debug(
            "merging %s from %s (%s)", self.commit, self.remote_name, url
        )

    def prepare_remote(self, remote_name, url):
        """
        Deduce a valid remote name for the url or check if the provided one can
        be used. If needed add and fetch the remote repository.

        Return the correct remote name.
        """
        # check if we need a name for the remote
        remotes = self.remotes()
        if remote_name is None:
            if url is None:
                return "origin"
            # see if the url is already known
            for remote_name in remotes:
                if url == remotes[remote_name]:
                    break
            else:
                # we need a new name
                remote_name = "merge_source"
                i = 0
                while remote_name in remotes:
                    remote_name = f"merge_source_{i}"
                    i += 1
        elif remote_name in remotes and url and url != remotes[remote_name]:
            raise RuntimeError(
                "remote name %s already used for %s", remote_name, remotes[remote_name]
            )

        if remote_name not in remotes:
            # we need to fetch
            self.add_remote(remote_name, url)

        return remote_name

    def apply(self):
        """
        Apply the merge.
        """
        self.apply_result = self.merge(self.commit)["retcode"] == 0
        return self.apply_result

    def __str__(self):
        """
        String representation.
        """
        if self.commit_id.startswith(self.commit):
            if self.remote_name == "origin":
                return self.commit_id
            else:
                return f"{self.commit_id} ({self.remote_name})"
        else:
            return f"{self.commit_id} ({self.commit})"


class GitLabMergeRequestHandler(GitRepository):
    """
    Helper to handle (CERN) GitLab merge requests.
    """

    def __init__(self, iid, path=os.curdir, commit=None):
        """
        Initialize the handler with the merge request id.
        """
        GitRepository.__init__(self, path)

        url = self.remotes().get("origin", "")
        if "gitlab.cern.ch" not in url:
            raise RuntimeError(
                "cannot handle merge requests for"
                f" repositories not in GitLab ({url})"
            )

        self.prepare()

        self.apply_result = None
        self.gitlab_name = url.split("/", 3)[-1].replace(".git", "")
        self.iid = iid
        self.commit, self.commit_id = self.resolve_commit(
            commit or f"merge-requests/{iid}"
        )

        __log__.getChild("git").debug(
            "applying merge request %s: %s",
            iid,
            "{gitlab_name}!{iid}".format(**self.__dict__),
        )

    def prepare(self):
        """
        Fetch merge request special branches from GitLab, if needed.
        """
        proc = Popen(
            ["git", "config", "--get-all", "remote.origin.fetch"],
            cwd=self.path,
            stdout=PIPE,
        )
        if "origin/merge-requests" not in proc.communicate()[0].decode(
            "utf-8", errors="replace"
        ):
            # it must be configured
            __log__.getChild("git").debug("getting merge-requests branches")
            fetch = (
                "+refs/merge-requests/*/head:" "refs/remotes/origin/merge-requests/*"
            )
            log_call(
                ["git", "config", "--add", "remote.origin.fetch", fetch], cwd=self.path
            )
            retry_log_call(
                ["git", "fetch", "-q", "origin"],
                cwd=self.path,
                retry=3,
                retry_sleep=600,
            )

    def apply(self):
        """
        Apply the merge.
        """
        self.apply_result = self.merge(self.commit)["retcode"] == 0
        return self.apply_result

    def __str__(self):
        """
        String representation.
        """
        return f"{self.commit_id[:8]} ({self.gitlab_name}!{self.iid})"


def git(proj, url=None, commit=None, export=False, merges=None):
    """
    Checkout from a git repository.

    @param proj: Configuration.Project instance
    @param url: git repository URL (default derived from proj.name)
    @param commit: commit id to checkout (default derived from proj.version)
    @param export: whether to use git "checkout" or "archive"
    @param merge: merge options as (<url>, <commit> [, <remote_name>]) or
                  as merge request id or (merge id, commit), or a list of them,
                  or 'all' for all opened merge requests
    """
    output = {"retcode": 0, "stdout": "", "stderr": "", "warning": [], "error": []}
    log = __log__.getChild("git")

    if not url:
        from .Configuration import Package

        gitlab_name = "{group}/{name}".format(
            group="lhcb-datapkg"
            if isinstance(proj, Package)
            else gitlabGroup(proj.name),
            name=proj.name,
        )
        url = f"https://gitlab.cern.ch/{gitlab_name}.git"
        inGitLab = True
    else:
        inGitLab = "gitlab.cern.ch" in url
        gitlab_name = url.split("/", 3)[-1].replace(".git", "")

    if proj.version.lower() == "head":
        commit_requested = getDefaultBranch(gitlab_name)
        if not merges:
            if "GITLAB_TOKEN" in os.environ:
                # version 'HEAD' implies all merge requests
                # (see LBCORE-1132)
                merges = ["all"]
            else:
                log.warning("merge requests not applied: no Gitlab token")
                output["warning"].append("merge requests not applied: no Gitlab token")
    elif re.match(r"mr[0-9]+$", proj.version):
        commit_requested = getDefaultBranch(gitlab_name)
        if not merges:
            assert (
                inGitLab
            ), f"cannot handle merge requests for projects not in GitLab ({proj})"
            merges = [int(proj.version[2:])]
            commit_requested = getMRTargetBranch(gitlab_name, merges[0])
    else:
        commit_requested = proj.version

    if not commit:
        commit = commit_requested

    dest = proj.baseDir
    repo = GitRepository(dest, url)
    commit, commit_id = repo.resolve_commit(commit)

    if isinstance(merges, (tuple, str, int)):
        merges = [merges]

    if merges and any(str(m).startswith("all") for m in merges):
        assert inGitLab, (
            "cannot handle merge requests for" f" projects not in GitLab ({proj})"
        )
        assert "GITLAB_TOKEN" in os.environ, (
            "cannot connect to GitLab ",
            "(missing token)",
        )
        idx, merge = [(i, m) for i, m in enumerate(merges) if str(m).startswith("all")][
            0
        ]
        filters = merge.lower().split(":")[1:]
        # ensure that we get only merge requests for the requested branch
        filters.append("target_branch=%s" % (commit_requested or commit))

        slotname = None
        if hasattr(proj, "slot") and proj.slot:
            slotname = proj.slot.name
        elif hasattr(proj, "container") and proj.container and proj.container.slot:
            slotname = proj.container.slot.name
        all_merges = getAllMergeRequestIDs(
            gitlab_name, filters=filters, labels=[slotname, "all-slots"]
        )
        merges = merges[:idx] + all_merges + merges[idx + 1 :]

    log.debug("checking out %s from %s (%s)", proj, url, commit)

    def merge_hdlr(merge):
        """
        Return an instance of the appropriate merge handler:

        int -> GitLab merge request
        commit -> git merge
        (int, commit) -> GitLab merge request
        (url, commit) -> git merge
        (url, commit, source_name) -> git merge
        """
        if isinstance(merge, int):
            return GitLabMergeRequestHandler(merge, path=dest)
        elif isinstance(merge, str):
            return GitMergeHandler(merge, path=dest)  # pylint: disable=E0601
        elif isinstance(merge, (tuple, list)):
            if len(merge) == 2:
                if isinstance(merge[0], int):
                    miid, commit = merge
                    return GitLabMergeRequestHandler(miid, path=dest, commit=commit)
                else:
                    url, commit = merge
                    return GitMergeHandler(commit, url, path=dest)
            elif len(merge) == 3:
                url, commit, source = merge
                return GitMergeHandler(commit, url, source, path=dest)
        raise RuntimeError("invalid merge description %r", merge)

    if merges:
        if export:
            log.warning("merges option is ignored when export is True")
            merges = []
    else:
        merges = []

    merge_hdlrs = []
    if not export:
        log.debug("checkout commit %s for %s", commit, proj)
        result = repo.checkout(commit_id)
        assert (
            result["retcode"] == 0
        ), "could not checkout commit '{}'{}: retcode {retcode}".format(
            commit_id, "" if commit == commit_id else f" ({commit})", **result
        )
        # do merges
        for merge in merges:
            merge = merge_hdlr(merge)
            success = merge.apply()
            if isinstance(merge, GitLabMergeRequestHandler):
                notifyMergeRequest(proj, gitlab_name, merge.iid, success)
            if not success:
                output["warning"].append(f"failed to merge {merge}")
            merge_hdlrs.append(merge)
        repo.init_submodules()
        if hasattr(proj, "overrides") and proj.overrides:
            for subdir, version in proj.overrides.items():
                if version is None:
                    log.debug("removing %s", subdir)
                    shutil.rmtree(path=os.path.join(dest, subdir), ignore_errors=True)
                else:
                    log.debug("checking out commit %s for dir %s", version, subdir)
                    if repo.checkout(version, subdir)["retcode"]:
                        output["warning"].append(
                            f"failed to checkout commit {version} for {subdir}"
                        )
    else:
        # FIXME: the outputs of git archive is not collected
        log.debug("export commit %s for %s", commit, proj)
        repo.checkout(commit_id)
        submodules = repo.init_submodules()

        def git_export(path, commit):
            """
            helper for a git equivalent of svn export
            """
            log.debug("export commit %s in %s", commit, path)
            proc1 = Popen(["git", "archive", commit], cwd=path, stdout=PIPE)
            proc2 = Popen(
                ["tar", "--extract", "--overwrite", "--file", "-"],
                cwd=path,
                stdin=proc1.stdout,
            )
            proc1.stdout.close()  # Allow proc1 to receive a SIGPIPE if proc2 exits.
            if proc2.wait() or proc1.wait():
                log.warning("problems exporting commit %s in %s", commit, path)
            shutil.rmtree(path=os.path.join(path, ".git"), ignore_errors=True)

        git_export(dest, commit)
        for path in submodules:
            git_export(path, "HEAD")

    from LbNightlyTools.Configuration import Project

    if not isinstance(proj, Project):  # it's a Package
        xenv_name = os.path.join(dest, proj.name.replace("/", "_") + ".xenv")
        xenv_oldname = xenv_name.replace(".xenv", "Environment.xml")
        if not os.path.exists(xenv_oldname):
            if os.path.exists(xenv_name):
                log.debug(
                    "create symlink %s -> %s",
                    os.path.basename(xenv_oldname),
                    os.path.basename(xenv_name),
                )
                os.symlink(os.path.basename(xenv_name), xenv_oldname)

    log.debug("checkout of %s completed in %s", proj, dest)
    log.debug("using commit %s (%s)", commit_id, commit_requested)
    for merge in merge_hdlrs:
        if merge.apply_result:
            log.debug("merged commit %s", merge)
        else:
            log.debug("not merged commit %s", merge)
    try:
        if hasattr(proj, "slot") and proj.slot and proj.slot.build_id and not export:
            if not gitlabProjectExists(f"lhcb-nightlies/{proj.name}"):
                log.warning(
                    f"lhcb-nightlies/{proj.name} does not exist, will try to create it"
                )

            def branch_name():
                if os.environ.get("flavour", "nightly") != "nightly":
                    return "{}/{}".format(os.environ["flavour"], proj.slot.name)
                return proj.slot.name

            def tag_name(previous=False):
                "compute a tag name for current slot/build_id"
                return f"{branch_name()}/{(proj.slot.build_id - 1) if previous else proj.slot.build_id}"

            commit = "HEAD"
            log.debug("record build sources in lhcb-nightlies")
            repo.add_remote(
                "lhcb-nightlies",
                f"ssh://git@gitlab.cern.ch:7999/lhcb-nightlies/{proj.name}.git",
                retry=False,
            )
            # log.debug('branches in lhcb-nightlies:')
            # for b in repo.branches():
            #     if 'lhcb-nightlies' in b:
            #         log.debug(' - %r', b)
            project_uses_branches = True
            if ("remotes/lhcb-nightlies/" + branch_name()) in repo.branches():
                log.debug("found branch %s", branch_name())
                if repo.rev_parse("HEAD:") != repo.rev_parse(
                    f"remotes/lhcb-nightlies/{branch_name()}:"
                ):
                    log.debug("content change detected")
                    if repo.rev_parse(f"{commit_id}:") == repo.rev_parse("HEAD:"):
                        log.debug(
                            "we are in sync with the original commit, reset the branch"
                        )
                        # to respect the logic used in "git show-branch" below,
                        # we need a merge commit from the latest version of the branch
                        # and the current commit, but that is possible only if the branch
                        # contains at least one extra commit
                        repo.checkout(commit_id, quiet=True)
                        log_call(
                            [
                                "git",
                                "commit",
                                "--allow-empty",
                                "--message",
                                "Reset branch",
                            ],
                            cwd=repo.path,
                        )
                        repo.checkout(commit_id, quiet=True)
                    repo.merge(
                        "remotes/lhcb-nightlies/" + branch_name(),
                        extra_args=["-sours", "--no-edit"],
                    )
                    repo.push_branch("HEAD:" + branch_name(), remote="lhcb-nightlies")
                else:
                    log.debug("no change detected")
                    commit = "remotes/lhcb-nightlies/" + branch_name()

            elif tag_name(previous=True) not in repo.tags():
                log.debug("first time in this slot, create the branch")
                # it's the first time we have this project in the slot
                repo.create_branch(branch_name())
                repo.push_branch(branch_name(), remote="lhcb-nightlies", force=True)

            else:  # old logic
                project_uses_branches = False
                # look for a tag with the same content (tree)
                tree = repo.rev_parse("HEAD:")
                proc = Popen(
                    [
                        "git",
                        "for-each-ref",
                        "--python",
                        "--sort=-*creatordate",
                        "--format=%(refname),",
                    ],
                    cwd=repo.path,
                    stdout=PIPE,
                )
                # (test requested commit first)
                log.debug("looking for an equivalent commit")
                for ref in eval(
                    f"[{commit_requested!r},"
                    + proc.communicate()[0].decode("utf-8", errors="replace")
                    + "]"
                ):
                    if repo.rev_parse(ref + ":") == tree:
                        proc = Popen(
                            ["git", "rev-list", "--max-count=1", ref],
                            cwd=repo.path,
                            stdout=PIPE,
                        )
                        commit = (
                            proc.communicate()[0]
                            .decode("utf-8", errors="replace")
                            .strip()
                        )
                        log.debug("reusing commit %s (%s)", commit, ref)
                        break  # we found a commit with the same content
                else:  # we could not find it, so we stick to HEAD
                    log.debug("none found")

            repo.tag(tag_name(), commit=commit, force=True)
            repo.push_tag(tag_name(), remote="lhcb-nightlies", force=True)
            # make sure the commit id of HEAD is exactly that used for the tag
            repo.checkout(tag_name(), quiet=True)
            if (
                not proj.slot.metadata.get("ci_test")
                and tag_name(previous=True) in repo.tags()
            ):
                # report changes between the previous build and this one
                # (unless it's a special ci-test slot)
                if project_uses_branches:
                    repo.show_branch(
                        "--sha1-name", tag_name(previous=True) + "~", tag_name() + "~"
                    )
                else:
                    repo.show_branch("--sha1-name", tag_name(previous=True), tag_name())
    except Exception as x:  # pylint: disable=W0703
        log.warning("failed to record built sources: %s", x)
    return output


def svn(desc, url, export=False):
    """
    Checkout from an svn repository.
    """
    log = __log__.getChild("svn")
    log.debug("checking out %s from %s", desc, url)
    dest = desc.baseDir
    output = log_call(["svn", "checkout" if not export else "export", url, dest])
    log.debug("checkout of %s completed in %s", desc, dest)
    return output


def copy(desc, src, export=False):
    """
    Copy the content of a directory.
    """
    log = __log__.getChild("copy")
    log.debug("copying %s from %s", desc, src)
    dest = desc.baseDir
    shutil.copytree(os.path.join(src, os.curdir), dest)
    log.debug("copy of %s completed in %s", desc, dest)
    return {"retcode": 0, "stdout": f"copied {desc} from {src}", "stderr": ""}


def untar(desc, src, export=False):
    """
    Unpack a tarball in the current directory (assuming that the tarball
    already contains the <PROJECT>/<PROJECT>_<version> directories).
    """
    log = __log__.getChild("untar")
    log.debug("unpacking %s", src)
    output = log_call(["tar", "-x", "-f", src])
    dest = desc.baseDir
    if not os.path.isdir(dest):
        raise RuntimeError("the tarfile %s does not contain %s", src, desc.baseDir)
    log.debug("unpacking of %s from %s completed", desc, src)
    return output


def unzip(desc, src, export=False):
    """
    Unpack a tarball in the current directory (assuming that the tarball
    already contains the <PROJECT>/<PROJECT>_<version> directories).
    """
    log = __log__.getChild("unzip")
    log.debug("unpacking %s", src)
    output = log_call(["unzip", "-q", "-o", src])
    dest = desc.baseDir
    if not os.path.isdir(dest):
        raise RuntimeError("the zipfile %s does not contain %s", src, desc.baseDir)
    log.debug("unpacking of %s from %s completed", desc, src)
    return output


LCG_MAKEFILE_TEMPLATE = """
configure:
\tfor s in "{src}"/* ; do if [ -d "$$s" ] ; then ln -svf "$$s" . ; else cp -vf "$$s" . ; fi ; done
\tfor s in LCG_externals_*.txt ; do sed -i 's*{src}*'$$(pwd)'*' "$$s" ; done

all:
install:
\tmkdir -p InstallArea/$${{CMTCONFIG:-$$BINARY_TAG}}
\ttouch InstallArea/$${{CMTCONFIG:-$$BINARY_TAG}}/.empty
unsafe-install: install
post-install:
test:
"""


def lcg(proj, src=None):
    """
    Special checkout method to create a shallow clone of the LCG special
    project.
    """
    log = __log__.getChild("lcg")

    if not src:
        src = proj.src
    dest = proj.baseDir

    if not os.path.exists(dest):
        log.debug("created %s", dest)
        os.makedirs(dest)

    with open(os.path.join(dest, "Makefile"), "w") as mkf:
        mkf.write(LCG_MAKEFILE_TEMPLATE.format(src=src))
        log.debug("created %s", mkf.name)

    log.info("created shallow project %s in %s", proj, dest)

    return {"retcode": 0, "stdout": "", "stderr": ""}


def lbscripts(proj, url=None, export=False, merges=None, commit=None):
    """
    Specific checkout wrapper for lbscripts
    """
    from .LbScriptsUtils import (
        updateInstallProject,
        updateLbConfigurationRequirements,
        updateVersionCmt,
    )

    log = __log__.getChild("lbscripts")

    # Utilities to gather the results of our calls
    outputs = []

    def call(*args, **kwargs):
        "helper to simplify the code"
        kwargs["logger"] = log
        outputs.append(log_call(*args, **kwargs))

    # First checking out LbScripts with GIT
    outputs.append(git(proj, url=url, commit=commit, export=export, merges=merges))

    # Now hacking the sources.
    # We need to set the version in LbConfiguration and in install_project
    updateInstallProject(proj.baseDir, proj.version)
    updateLbConfigurationRequirements(proj.baseDir, proj.version)

    # Create the version.cmt file in all packages
    updateVersionCmt(proj.baseDir, proj.version)

    # Now calling make directly after the checkout
    # This is needed to have the InstallArea directory in the source archive
    call(["make", "USE_CMT=1"], cwd=proj.baseDir)

    # make sure that the project is flagged as platform independent
    proj.platform_independent = True

    # Returning the checkout results
    return _merge_outputs(outputs)


def default(*args, **kwargs):
    return git(*args, **kwargs)


def getMethod(method=None):
    """
    Helper function to get a checkout method by name.

    If method is a callable we return it, otherwise we look for the name in the
    current module or as a function coming from another module.
    If method is None, we return the default checkout method.
    """
    if method is None:
        return default
    if hasattr(method, "__call__"):
        return method
    if isinstance(method, str):
        if "." in method:
            # method is a fully qualified function name
            m, f = method.rsplit(".", 1)
            return getattr(__import__(m, fromlist=[f]), f)
        else:
            # it must be a name in this module
            return globals()[method]

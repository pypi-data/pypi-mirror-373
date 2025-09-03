###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Gitlab utilities
"""
import logging

_logger = logging.getLogger(__name__)

GITLAB_URL = "https://gitlab.cern.ch/"


def cached(f):
    """
    Decorator to add caching to functions.
    """
    from functools import wraps

    _cache = {}

    @wraps(f)
    def wrapper(*args, **kwargs):
        _logger.debug("%s invoked with %r", f.__name__, (args, kwargs))
        try:
            key = (tuple(args), tuple(kwargs.items()))
            if key in _cache:
                _logger.debug("result in cache")
                return _cache[key]
        except TypeError:
            # a TypeError at this point means one of the arguments is not hashable
            _logger.debug("unhashable arguments, invoking the function")
            return f(*args, **kwargs)
        _logger.debug("result not in cache, invoking the function")
        result = _cache[key] = f(*args, **kwargs)
        return result

    return wrapper


@cached
def _gitlabServer():
    import os

    import gitlab

    return gitlab.Gitlab(GITLAB_URL, private_token=os.environ.get("GITLAB_TOKEN"))


@cached
def _getGitlabProject(project_id):
    return _gitlabServer().projects.get(project_id)


@cached
def getMRCommit(project_id, mr_iid):
    mr = _getGitlabProject(project_id).mergerequests.get(mr_iid)
    for c in mr.commits():
        return c.id
    return None


@cached
def _getAllProjectMRs(project_id):
    return _getGitlabProject(project_id).mergerequests.list(state="opened", all=True)


def getMergeRequests(project_id, labels=None, wip=None, target_branch=None):
    from gitlab import GitlabGetError

    wip_condition = (
        (lambda _: True) if wip is None else (lambda mr: mr.work_in_progress == wip)
    )
    label_condition = (lambda _: True) if not labels else ()
    if labels:
        labels = set(labels)
        label_condition = lambda mr: labels.intersection(mr.labels)
    else:
        label_condition = lambda _: True
    condition = lambda mr: (
        mr.target_branch == target_branch and wip_condition(mr) and label_condition(mr)
    )
    try:
        return sorted(
            (mr.iid, getMRCommit(project_id, mr.iid))
            for mr in _getAllProjectMRs(project_id)
            if condition(mr)
        )

    except GitlabGetError:
        _logger.warning("problem getting MRs for %s", project_id)
        return []


_SPECIAL_GITLAB_GROUPS = {
    "gaudi": "gaudi",
    "gaussino": "Gaussino",
    "gaussinoextlibs": "Gaussino",
}


def gitlabGroup(project, default="lhcb"):
    """
    Gitlab group containing the given project.

    >>> gitlabGroup('Moore')
    'lhcb'
    >>> gitlabGroup('Gaudi')
    'gaudi'
    >>> gitlabGroup('GaussinoExtLibs')
    'Gaussino'
    """
    return _SPECIAL_GITLAB_GROUPS.get(project.lower(), default)


def getProjectId(project):
    """
    Given a Project instance return the corresponding Gitlab project id
    ('group/name').
    """
    from LbNightlyTools.Configuration import Package

    project_id = project.name

    if "url" in project.checkout_opts:
        if project.checkout_opts["url"].startswith(GITLAB_URL):
            project_id = project.checkout_opts["url"][len(GITLAB_URL) :]
            if project_id.endswith(".git"):
                project_id = project_id[:-4]

    if isinstance(project, Package):
        project_id = "lhcb-datapkg/" + project_id
    elif "/" not in project_id:
        project_id = f"{gitlabGroup(project_id)}/{project_id}"

    return project_id


@cached
def getBranchCommitId(project_id, branch):
    project = _getGitlabProject(project_id)
    return project.branches.get(branch).commit["id"]


@cached
def getDefaultBranch(project_id):
    project = _getGitlabProject(project_id)
    return project.default_branch


def resolveProjectMRs(project):
    """
    Given a project, convert the list of requested MRs to a list
    of (mr_iid, commit_id) pairs.

    The supported merge requests are:
    - 'all' (same as 'label=all-slots' + 'label=<slot-name>',
      if the project is in a slot)
    - 'label=<abc>'
    - '<id>'

    If the project version is 'HEAD', it's equivalent to version=<default_branch>
    and adding 'all' to the merges.

    The project is not modified.
    """
    project_id = getProjectId(project)
    target_branch = project.version

    merges = project.checkout_opts.get("merges", [])
    if not isinstance(merges, list):
        merges = [merges]
    else:
        merges = list(merges)

    if target_branch.lower() == "head":
        target_branch = getDefaultBranch(project_id)
        merges.insert(0, "all")

    new_merges = []
    for m in merges:
        if m == "all":
            tmp = getMergeRequests(
                project_id, labels=("all-slots",), target_branch=target_branch
            )
            if project.slot:
                tmp.extend(
                    getMergeRequests(
                        project_id,
                        labels=(project.slot.name,),
                        target_branch=target_branch,
                    )
                )
            tmp.sort()
            new_merges.extend(tmp)
        elif isinstance(m, int):
            new_merges.append((m, getMRCommit(project_id, m)))
        elif isinstance(m, str) and m.startswith("label="):
            new_merges.extend(
                getMergeRequests(
                    project_id, labels=(m[6:],), target_branch=target_branch
                )
            )
        else:
            new_merges.append(m)

    # deduplicate
    merges = []
    for m in new_merges:
        if m not in merges:
            merges.append(m)

    return merges


def resolveMRs(item):
    from gitlab import GitlabGetError

    from LbNightlyTools.Configuration import DataProject, Package, Project, Slot

    if isinstance(item, Slot):
        resolveMRs(item.projects)
    elif isinstance(item, DataProject):
        resolveMRs(item.packages)
    elif isinstance(item, (Project, Package)):
        if isinstance(item, Package) or not item.disabled:
            item.checkout_opts["merges"] = resolveProjectMRs(item)
            if not "commit" in item.checkout_opts:
                try:
                    item.checkout_opts["commit"] = getBranchCommitId(
                        getProjectId(item),
                        (
                            getDefaultBranch(getProjectId(item))
                            if item.version.lower() == "head"
                            else item.version
                        ),
                    )
                except GitlabGetError:
                    # this means the requested version is a tag rather
                    # (not a branch)
                    pass
        else:  # disabled project case, just clean up pointless checkout opts
            item.checkout = ("ignore", {})
    else:
        return [resolveMRs(p) for p in item]
    return item


@cached
def getMRLabels(project, mr_iid):
    try:
        project_id = getProjectId(project)
        mr = _getGitlabProject(project_id).mergerequests.get(mr_iid)
        return mr.labels
    except Exception as err:
        _logger.warning("exception in getMRLabels(%s,%s): %s", project, mr_iid, err)
        return []

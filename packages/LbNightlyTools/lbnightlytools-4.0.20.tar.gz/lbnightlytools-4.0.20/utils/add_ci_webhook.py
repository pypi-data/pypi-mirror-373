import logging
import os
import subprocess

import gitlab

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

out = subprocess.check_output(["lb-sdb-query", "listProjects"])
PROJECTS = out.splitlines()
HOOK_URL = "https://lhcb-nightlies.web.cern.ch/jenkins/"
HOOK_TOKEN = os.environ["HOOK_TOKEN"]
GITLAB_TOKEN = os.environ["GITLAB_TOKEN"]


def find_hook(project, url):
    for hook in project.hooks.list(all=True):
        if hook.attributes["url"] == url:
            return hook


def setup_webhook(project):
    # Find or create a webhook for HOOK_URL
    try:
        hook = find_hook(project, url=HOOK_URL)
    except gitlab.exceptions.GitlabListError:
        logger.warning(
            "Insufficient permissions for {}, skipping".format(
                project.attributes["path_with_namespace"]
            )
        )
        return
    if not hook:
        hook = project.hooks.create(data={"url": HOOK_URL})

    # Configure the webhook
    data = {}
    # - set all _events attributes to False
    for attr in hook.attributes:
        if attr.endswith("_events"):
            data[attr] = False
    # - except the note_events (comments)
    data["note_events"] = True
    data["push_events_branch_filter"] = ""
    # - set token and ssl verification
    data["token"] = HOOK_TOKEN
    data["enable_ssl_verification"] = True
    hook.save(**data)


gitlab_server = gitlab.Gitlab("https://gitlab.cern.ch/", GITLAB_TOKEN)
for project in PROJECTS:
    path = "lhcb/" + project
    logger.info(f"Setting up {path}...")
    try:
        p = gitlab_server.projects.get(path)
    except gitlab.exceptions.GitlabGetError:
        logger.warning(f"Could not get project {path}")
    setup_webhook(p)

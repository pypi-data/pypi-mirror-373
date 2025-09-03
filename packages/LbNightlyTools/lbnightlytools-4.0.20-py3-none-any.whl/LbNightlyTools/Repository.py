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
Code handling interactions with artifacts repository
"""

import logging
import os
from io import BytesIO
from os import makedirs
from os.path import dirname, exists, join
from shutil import copyfileobj
from subprocess import CalledProcessError, call
from tempfile import mkstemp

from requests import get, head, put
from requests.compat import urljoin, urlparse

EOS_ROOT = "root://eoslhcb.cern.ch/"
_repo_handlers = {}


def register_for(*schemes):
    """
    Decorator used to register the concrete type of repository
    """

    def _reg(cls):
        global _repo_handlers
        _repo_handlers.update((s, cls) for s in schemes)
        return cls

    return _reg


def get_repo_type(uri):
    """
    Returns type of repository based on uri provided in the argument.
    It may return "eos", "file", "http" or None
    """

    result = urlparse(uri)
    if not result.scheme or result.scheme == "file":
        if result.path.startswith("/eos/"):
            return "eos"
        else:
            return "file"
    elif result.scheme == "root":
        return "eos"
    elif result.scheme in ("http", "https"):
        return "http"
    return None


class ArtifactsRepository:
    """
    Class representing artifacts repository.
    """

    def __init__(self, uri):
        """
        Initialises the repository based on its URI
        """
        self.uri = uri

    def pull(self, artifacts_name):
        """
        Pulls artifact from repository as in-memory binary stream.
        Raises exceptions if the artifact cannot be opened.

        Arguments:
        artifacts_name: name of the artifacts file

        Returns: BytesIO object
        """
        raise NotImplementedError("Should be implemented in the inheriting class")

    def push(self, file_object, remote_name):
        """
        Pushes artifacts to the repository

        Arguments:
        file_object: file object with the data to be pushed to repository
        remote_name: name of the artifcats file in the repository

        Returns: True if the artifacts have been pushed, False otherwise
        """
        raise NotImplementedError("Should be implemented in the inheriting class")

    def exist(self, artifacts_name):
        """
        Checks if artifacts exist

        Arguments:
        artifacts_name: name of the artifcats file

        Returns: True if the artifacts exist, False otherwise
        """
        raise NotImplementedError("Should be implemented in the inheriting class")


@register_for(None)
def unknown_uri(uri):
    raise ValueError(f"Unsupported uri {uri!r}")


@register_for("file")
class FileRepository(ArtifactsRepository):
    """
    Class defining repository in the local file system.
    """

    def pull(self, artifacts_name):
        with open(join(self.uri, artifacts_name), "rb") as f:
            artifact = f.read()
        return BytesIO(artifact)

    def push(self, file_object, remote_name):
        try:
            makedirs(join(self.uri, dirname(remote_name)))
        except OSError:
            pass
        fdst = open(join(self.uri, remote_name), "wb")
        try:
            copyfileobj(file_object, fdst)
        except OSError:
            return False
        return True

    def exist(self, artifacts_name):
        return exists(join(self.uri, artifacts_name))


@register_for("eos")
class EosRepository(ArtifactsRepository):
    """
    Class defining repository on EOS.
    """

    def pull(self, artifacts_name):
        fd, path = mkstemp()
        call(["xrdcp", "-f", join(self.uri, artifacts_name), path])
        with open(path, "rb") as f:
            artifact = f.read()
        os.close(fd)
        os.remove(path)
        return BytesIO(artifact)

    def push(self, file_object, remote_name):
        try:
            call(
                ["xrdfs", EOS_ROOT, "mkdir", "-p", join(self.uri, dirname(remote_name))]
            )
        except FileExistsError:
            pass
        fd, path = mkstemp()
        with open(path, "wb") as f:
            f.write(file_object.read())
        try:
            call(["xrdcp", path, join(self.uri, remote_name)])
        except (CalledProcessError, OSError) as ex:
            logging.warning(f"Pushing artifacts to the repository failed: {ex}")
            return False
        finally:
            os.close(fd)
            os.remove(path)
        return True

    def exist(self, artifacts_name):
        return exists(join(self.uri, artifacts_name))


@register_for("http")
class HttpRepository(ArtifactsRepository):
    """
    Class defining repository through HTTP request methods.
    """

    def pull(self, artifacts_name):
        r = get(urljoin(self.uri, artifacts_name))
        r.raise_for_status()
        return BytesIO(r.content)

    def push(self, file_object, remote_name, auth=None):
        r = put(
            urljoin(self.uri, remote_name),
            data=file_object,
            auth=auth,
        )
        if r.status_code == 201:
            return True
        return False

    def exist(self, artifacts_name):
        r = head(urljoin(self.uri, artifacts_name))
        if r.status_code == 200:
            return True
        return False


def connect(uri, *args, **kwargs):
    """
    Function returning the artifacts repository
    object based on the URI provided in the argument.
    """
    global _repo_handlers
    return _repo_handlers[get_repo_type(uri)](uri, *args, **kwargs)

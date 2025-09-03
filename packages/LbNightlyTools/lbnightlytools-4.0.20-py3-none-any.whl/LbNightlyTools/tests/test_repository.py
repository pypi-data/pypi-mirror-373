import filecmp
import os
from os.path import exists, join, normpath
from shutil import copyfile, copyfileobj
from tempfile import mkstemp

from LbNightlyTools.Repository import connect

_testdata = normpath(join(*([__file__] + [os.pardir] * 4 + ["testdata"])))
artifacts_repo = join(_testdata, "artifacts_repo")


def test_repo_push():
    src = join(
        _testdata, "artifacts", "packs", "src", "TestProject.HEAD.testing-slot.src.zip"
    )
    dst = "TestProjectPush.HEAD.testing-slot.src.zip"
    repo = connect(artifacts_repo)
    with open(src, "rb") as f:
        repo.push(f, dst)

    assert exists(join(artifacts_repo, dst))
    assert filecmp.cmp(src, join(artifacts_repo, dst))
    os.remove(join(artifacts_repo, dst))


def test_repo_pull():
    artifact = "TestProject.HEAD.testing-slot.src.zip"
    src = join(
        _testdata, "artifacts", "packs", "src", "TestProject.HEAD.testing-slot.src.zip"
    )
    dst = join(artifacts_repo, artifact)
    copyfile(src, dst)
    fd, path = mkstemp()
    repo = connect(artifacts_repo)
    with open(path, "wb") as lp:
        with repo.pull(artifact) as remote:
            copyfileobj(remote, lp)

    assert exists(path)
    assert filecmp.cmp(join(artifacts_repo, artifact), path)
    os.close(fd)
    os.remove(path)
    os.remove(dst)

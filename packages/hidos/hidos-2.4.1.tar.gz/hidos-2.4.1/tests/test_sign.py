import pytest

from hidos.git import GitRepoFacade
from hidos.repo import SuccessionRepository
from hidos.archive import SuccessionArchive
from hidos.exceptions import (
    SignedCommitVerifyFailedWarning, SignedCommitVerifyFailedError
)
from hidos.util import load_openssh_public_key_file

from sshsig.allowed_signers import (
    load_for_git_allowed_signers_file,
    save_for_git_allowed_signers_file,
)

import git

import json
from pathlib import Path
from io import StringIO

CASES_DIR = Path(__file__).parent / "cases"
PUBLIC_SIGN_KEY = Path(__file__).parent / "data/test_sign_key.pub"
NOT_SIGN_KEY = Path(__file__).parent / "data/not_sign_key.pub"


def load(hist_case, stem):
    with open(CASES_DIR / "hist" / hist_case / f"{stem}.json") as f:
        return json.load(f)


def test_authorized_keys_file_read():
    got1 = load_openssh_public_key_file(PUBLIC_SIGN_KEY)
    assert 1 == len(got1)
    expected = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGc/pGTE+yQT9LdZdR0NCvAnboWV0wT/5d7F5GTKk7QJ"
    assert [expected] == [str(k) for k in got1]

    out = StringIO()
    save_for_git_allowed_signers_file(got1, out)
    got2 = out.getvalue()
    assert '* namespaces="git" {}\n'.format(expected) == got2
    out.close()

    got3 = set(load_for_git_allowed_signers_file(StringIO(got2)))
    assert got1 == got3


@pytest.fixture
def tmp_signed_repo(tmp_git_dir, git_environ):
    keys = load_openssh_public_key_file(PUBLIC_SIGN_KEY)
    branch_name = "signed_branch"
    repo = SuccessionRepository(GitRepoFacade(tmp_git_dir))
    repo.create_succession(branch_name, keys)
    assert repo.history.revisions
    succ = repo.get_succession(branch_name)
    assert succ.dsi.base64 == "co89-SHi5bbOAR2hmbsputtwqQg"
    return repo


def test_git_signed_0(tmp_signed_repo):
    expect1 = load("signed_0", "history")
    assert expect1 == tmp_signed_repo.history.as_pod()
    archive = SuccessionArchive(tmp_signed_repo.history)
    expect2 = load("signed_0", "archive")
    assert expect2 == archive.as_pod()


def test_git_signed_1(tmp_signed_repo, tmp_hello_file, tmp_hola_file):
    tmp_signed_repo.commit_edition(tmp_hello_file, "signed_branch", "0.3")
    tmp_signed_repo.commit_edition(tmp_hola_file.parent, "signed_branch", "1.1")
    expect1 = load("signed_1", "history")
    assert expect1 == tmp_signed_repo.history.as_pod()
    archive = SuccessionArchive(tmp_signed_repo.history)
    expect2 = load("signed_1", "archive")
    assert expect2 == archive.as_pod()


def test_fail_signed_create(tmp_git_dir, git_environ):
    keys = load_openssh_public_key_file(NOT_SIGN_KEY)
    branch_name = "signed_branch"
    repo = SuccessionRepository(GitRepoFacade(tmp_git_dir))
    with pytest.warns(SignedCommitVerifyFailedWarning):
        with pytest.raises(SignedCommitVerifyFailedError):
            repo.create_succession(branch_name, keys)
    repo = git.Repo(tmp_git_dir)
    assert 0 == len(repo.heads)

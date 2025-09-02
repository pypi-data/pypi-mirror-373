import json, pytest
from os import listdir
from pathlib import Path

import hidos
from hidos import EditionId
from hidos.git import GitRepoFacade
from hidos.dulwich import DulwichRepoFacade
from hidos.repo import SuccessionRepository, revision_history
from hidos.archive import SuccessionArchive, history_successions
from hidos.exceptions import *

from .mock import MockRepoFacade, MockRevisionHistory

# NOTE: ./conftest.py contains pytest fixtures

CASES_DIR = Path(__file__).parent / "cases"
DATA_DIR = Path(__file__).parent / "data"
HIST_CASES = set(listdir(CASES_DIR / "hist"))
IGNORE_CASES = set(["ignore_overwrite_1", "ignore_overwrite_2"])


def load(hist_case, stem):
    with open(CASES_DIR / "hist" / hist_case / f"{stem}.json") as f:
        return json.load(f)


# RepoFacade = GitRepoFacade
RepoFacade = DulwichRepoFacade


@pytest.mark.parametrize("case", HIST_CASES)
def test_roundtrip_mock_history(case):
    pod = load(case, "history")
    history = MockRevisionHistory.from_pod(pod)
    assert pod == history.as_pod()


@pytest.mark.parametrize("case", HIST_CASES - IGNORE_CASES)
def test_succession_archive(case):
    repo = MockRepoFacade(load(case, "history"))
    arc = SuccessionArchive(repo.history())
    expect = load(case, "archive")
    assert expect == arc.as_pod()


@pytest.mark.parametrize("case", IGNORE_CASES)
def test_warn_succession_archive_warn(case):
    with pytest.warns(EditionRevisionWarning):
        test_succession_archive(case)


@pytest.fixture
def tmp_repo(tmp_git_dir, git_environ):
    repo = SuccessionRepository(GitRepoFacade(tmp_git_dir))
    branch_name = "some_branch"
    repo.create_succession(branch_name)
    succ = repo.get_succession(branch_name)
    assert succ.dsi.base64 == "rgFhVew4t_RgKnl8VXNmNEvuY3g"
    assert succ.latest() == None
    return repo


def test_empty_repo(tmp_git_dir, git_environ):
    hist = revision_history(RepoFacade(tmp_git_dir))
    expect1 = {"revisions": []}
    assert expect1 == hist.as_pod()
    assert 0 == len(history_successions(hist))


def test_git_unsigned_0(tmp_repo):
    expect1 = load("unsigned_0", "history")
    assert expect1 == tmp_repo.history.as_pod()
    archive = SuccessionArchive(tmp_repo.history)
    expect2 = load("unsigned_0", "archive")
    assert expect2 == archive.as_pod()

    succ = tmp_repo.get_succession("some_branch")
    assert succ.latest() == None


def test_git_unsigned_1(tmp_repo, tmp_hello_file, tmp_hola_file):
    tmp_repo.commit_edition(tmp_hello_file, "some_branch", "0.3")
    tmp_repo.commit_edition(tmp_hola_file.parent, "some_branch", "1.1")
    expect1 = load("unsigned_1", "history")
    assert expect1 == tmp_repo.history.as_pod()
    archive = SuccessionArchive(tmp_repo.history)
    expect2 = load("unsigned_1", "archive")
    assert expect2 == archive.as_pod()


def test_obsolete(tmp_repo, tmp_hello_file):
    tmp_repo.commit_edition(tmp_hello_file, "some_branch", "0.3")
    tmp_repo.commit_edition(tmp_hello_file, "some_branch", "1.1")
    tmp_repo.commit_edition(tmp_hello_file.parent, "some_branch", "1.2.0.1")
    succ = tmp_repo.get_succession("some_branch")
    assert succ.root.refine().edid == EditionId("1.1")
    assert succ.root.refine(expand_to_unlisted=True).edid == EditionId("1.2.0.1")
    assert succ.root.subs[0].obsolete
    assert succ.root.subs[0].subs[3].obsolete
    assert not succ.root.subs[1].obsolete
    assert not succ.root.subs[1].subs[1].obsolete
    assert not succ.root.subs[1].subs[2].subs[0].obsolete
    assert succ.root.subs[1].subs[2].refine() is None
    assert succ.root.subs[1].subs[2].refine(expand_to_unlisted=True).edid == EditionId("1.2.0.1")
    assert succ.latest() == succ.root.refine()
    assert succ.latest() == succ.root.subs[1].subs[1]
    assert succ.latest(True) == succ.root.subs[1].subs[2].subs[0].subs[1]


def test_not_succession_repo():
    git_dir = DATA_DIR / "bare_repos" / "not_succession.git"
    repo = SuccessionRepository(RepoFacade(git_dir))
    archive = SuccessionArchive(repo.history)
    assert not len(archive.successions)


def test_commit_bad_branch(tmp_repo, tmp_hello_file):
    with pytest.raises(ValueError):
      tmp_repo.commit_edition(tmp_hello_file, "bogus_branch", "1.1")

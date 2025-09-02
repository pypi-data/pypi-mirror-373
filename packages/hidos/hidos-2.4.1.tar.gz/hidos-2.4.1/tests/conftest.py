import git, pytest

import os, stat
from pathlib import Path

GIT_CONFIG = Path(__file__).parent / "data/gitconfig"
TEST_SIGN_KEY = Path(__file__).parent / "data/test_sign_key"


@pytest.fixture
def tmp_git_dir(tmp_path_factory):
    ret = tmp_path_factory.mktemp("repo")
    repo = git.Repo.init(ret)
    repo.git.config("user.signingkey", str(TEST_SIGN_KEY))
    os.chmod(TEST_SIGN_KEY, stat.S_IRUSR)
    return ret


@pytest.fixture
def tmp_hello_file(tmp_path_factory):
    file_path = tmp_path_factory.mktemp("repo") / "hello.txt"
    with open(file_path, "w") as file:
        print("Hello World", file=file)
    return file_path


@pytest.fixture
def tmp_hola_file(tmp_path_factory):
    file_path = tmp_path_factory.mktemp("repo") / "hola.txt"
    with open(file_path, "w") as file:
        print("Hola Mundo", file=file)
    return file_path


@pytest.fixture
def git_environ(monkeypatch):
    name = "A. Tester"
    email = "tester@example.com"
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(GIT_CONFIG))
    monkeypatch.setenv("GIT_AUTHOR_NAME", name)
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", email)
    monkeypatch.setenv("GIT_COMMITTER_NAME", name)
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", email)
    date = "2000-01-01 00:00:00"
    monkeypatch.setenv("GIT_AUTHOR_DATE", date)
    monkeypatch.setenv("GIT_COMMITTER_DATE", date)
    monkeypatch.setenv("TZ", "UTC")

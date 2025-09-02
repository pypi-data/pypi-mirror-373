import pytest

import os, json, tempfile
from pathlib import Path

import git

import hidos
from hidos import __main__

# NOTE: ./conftest.py contains pytest fixtures

PUBLIC_SIGN_KEY = Path(__file__).parent / "data/test_sign_key.pub"
SNAPSHOT_CASE = Path(__file__).parent / "cases" / "snapshot"


def test_cache_path(tmp_path, capsys):
    retcode = __main__.main(["--offline", "--cache", str(tmp_path), "cache", "path"])
    assert 0 == retcode
    captured = capsys.readouterr()
    assert tmp_path == Path(captured.out.rstrip())


def _run_nocache(args):
    if isinstance(args, str):
        args = args.split()
    with tempfile.TemporaryDirectory() as tmp:
        return __main__.main(["--offline", "--cache", str(tmp)] + args)


def _gitrun(git_dir, args):
    if isinstance(args, str):
        args = args.split()
    return _run_nocache(["git", "--git-dir", str(git_dir)] + args)


def test_create_succ(tmp_git_dir, git_environ, capsys, tmp_hello_file):
    _gitrun(tmp_git_dir, "create some_branch")
    captured = capsys.readouterr()
    dsi = captured.out.rstrip()
    assert dsi == "dsi:rgFhVew4t_RgKnl8VXNmNEvuY3g"
    _gitrun(tmp_git_dir, "dsi some_branch")
    captured = capsys.readouterr()
    assert captured.out.rstrip() == dsi

    _gitrun(tmp_git_dir, f"commit {tmp_hello_file} some_branch 1.1")

    _gitrun(tmp_git_dir, "list")
    expect = {"dsi:rgFhVew4t_RgKnl8VXNmNEvuY3g": {"refs":{"heads":["some_branch"]}}}
    captured = capsys.readouterr()
    assert expect == json.loads(captured.out)


def test_create_signed(tmp_git_dir, git_environ, capsys, tmp_hello_file):
    _gitrun(tmp_git_dir, f"create some_branch --keys {PUBLIC_SIGN_KEY}")
    captured = capsys.readouterr()
    dsi = captured.out.rstrip()
    assert dsi == "dsi:co89-SHi5bbOAR2hmbsputtwqQg"
    _gitrun(tmp_git_dir, "dsi some_branch")
    captured = capsys.readouterr()
    assert captured.out.rstrip() == dsi


def test_list_editions(tmp_git_dir, git_environ, tmp_hello_file, capsys):
    _gitrun(tmp_git_dir, "create some_branch")
    captured = capsys.readouterr()
    dsi = captured.out.rstrip()
    assert dsi == "dsi:rgFhVew4t_RgKnl8VXNmNEvuY3g"
    _gitrun(tmp_git_dir, f"commit {tmp_hello_file} some_branch 1.1")
    _gitrun(tmp_git_dir, f"commit {tmp_hello_file} some_branch 1.2")
    _gitrun(tmp_git_dir, "info some_branch")
    expect = {
        'dsi': "rgFhVew4t_RgKnl8VXNmNEvuY3g",
        'editions': ['1.1', '1.2'],
        'init': "swh:1:rev:ae016155ec38b7f4602a797c557366344bee6378",
        'signed': False,
    }
    captured = capsys.readouterr()
    assert expect == json.loads(captured.out)

    _gitrun(tmp_git_dir, "info some_branch 1.2")
    expect = {
        'number': "1.2",
        'author_date': "2000-01-01",
        'snapshot': "swh:1:cnt:557db03de997c86a4a028e1ebd3a1ceb225be238",
        'record': "swh:1:rev:0ca841057dd8bf3cf19151ae44e398d727dc342c",
    }
    captured = capsys.readouterr()
    assert expect == json.loads(captured.out)


def test_edition_conflict(tmp_git_dir, git_environ, tmp_hello_file):
    _gitrun(tmp_git_dir, "create some_branch")
    _gitrun(tmp_git_dir, f"commit {tmp_hello_file} some_branch 1.1")
    with pytest.raises(ValueError):
        _gitrun(tmp_git_dir, f"commit {tmp_hello_file} some_branch 1.1")


def test_work_dir_not_succession(tmp_path, git_environ, tmp_hello_file, capsys):
    repo = git.Repo.init(tmp_path)
    _gitrun(repo.git_dir, "create some_branch")
    assert len(repo.heads) == 1
    repo.head.reference = repo.heads[0]
    retcode = _gitrun(repo.git_dir, f"commit {tmp_hello_file} some_branch 1.1")
    assert retcode != 0
    captured = capsys.readouterr()
    assert "branch" in captured.err
    assert "checked" in captured.err


def test_not_git_dir(tmp_path, capsys):
    retcode = _gitrun(tmp_path, "create some_branch")
    assert retcode != 0
    captured = capsys.readouterr()
    assert "directory" in captured.err
    assert "git" in captured.err.lower()


def test_commit_hidden_file_entry(tmp_git_dir, git_environ, capsys):
    _gitrun(tmp_git_dir, "create some_branch")
    src = SNAPSHOT_CASE / 'with_hidden_file'
    retcode = _gitrun(tmp_git_dir, f"commit {src} some_branch 1.1")
    assert retcode != 0
    errlow = capsys.readouterr().err.lower()
    assert "directory" in errlow
    assert "hidden" in errlow
    assert ".bad_filename" in errlow


def test_commit_hidden_dir_entry(tmp_git_dir, git_environ, capsys):
    _gitrun(tmp_git_dir, "create some_branch")
    src = SNAPSHOT_CASE / 'with_hidden_dir'
    retcode = _gitrun(tmp_git_dir, f"commit {src} some_branch 1.1")
    assert retcode != 0
    errlow = capsys.readouterr().err.lower()
    assert "directory" in errlow
    assert "hidden" in errlow
    assert ".bad_dirname" in errlow


def test_commit_symlink_entry(tmp_git_dir, git_environ, capsys):
    _gitrun(tmp_git_dir, "create some_branch")
    src = SNAPSHOT_CASE / 'with_symlink'
    retcode = _gitrun(tmp_git_dir, f"commit {src} some_branch 1")
    assert retcode != 0
    errlow = capsys.readouterr().err.lower()
    assert "symbolic link" in errlow
    assert "article.xml" in errlow


def test_commit_exec_bit_entry(tmp_git_dir, git_environ, capsys):
    _gitrun(tmp_git_dir, "create some_branch")
    src = SNAPSHOT_CASE / 'with_exec_bit'
    retcode = _gitrun(tmp_git_dir, f"commit {src} some_branch 1.2.3")
    assert retcode == 0
    capsys.readouterr()

    retcode = _gitrun(tmp_git_dir, "info some_branch 1.2.3")
    assert retcode == 0
    expect = {
        'number': "1.2.3",
        'author_date': "2000-01-01",
        'snapshot': "swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f",
        'record': "swh:1:rev:2e165d057f413128a8cac174884daac689277452",
    }
    captured = capsys.readouterr()
    assert json.loads(captured.out) == expect


def test_cli_fail_empty_subdir(tmp_git_dir, git_environ, capsys):
    _gitrun(tmp_git_dir, "create branchy")
    with tempfile.TemporaryDirectory() as srcdir:
        os.mkdir(os.path.join(srcdir, "this_not_ok"))
        retcode = _gitrun(tmp_git_dir, f"commit {srcdir} branchy 1")
    assert retcode != 0
    errlow = capsys.readouterr().err.lower()
    assert "empty" in errlow
    assert "director" in errlow

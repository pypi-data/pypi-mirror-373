import pytest

import os, tempfile
from pathlib import Path

from hidos import util
from hidos import __main__


SNAPSHOT_CASE = Path(__file__).parent / "cases" / "snapshot"

CASE_SWHIDS = {
    'just_a_file.txt': 'swh:1:cnt:e7ee9eec323387d82a370674c1e2996d25c2414d',
    'smallest': 'swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f',
    'with_hidden_file': 'swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f',
    'with_hidden_dir': 'swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f',
    'with_exec_bit': 'swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f',
}


def test_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        assert "swh:1:dir:" + util.EMPTY_TREE == util.swhid_from_path(tmpdir)


def test_with_subdir():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(os.path.join(tmpdir, "empty_subdir_should_be_ignored"))
        assert "swh:1:dir:" + util.EMPTY_TREE == util.swhid_from_path(tmpdir)


@pytest.mark.parametrize("case", CASE_SWHIDS.keys())
def test_swhids(case):
    assert CASE_SWHIDS[case] == util.swhid_from_path(SNAPSHOT_CASE / case)


def test_with_symlink():
    with pytest.raises(ValueError):
        util.swhid_from_path(SNAPSHOT_CASE / "with_symlink")


def test_cli_hash(capsys):
    src = SNAPSHOT_CASE / 'smallest'
    retcode = __main__.main(["hash", str(src)])
    assert retcode == 0
    got = capsys.readouterr().out.strip() 
    assert got == "swh:1:dir:4d02543c1c3971067d4a9f27d1c9f3cc559e335f"

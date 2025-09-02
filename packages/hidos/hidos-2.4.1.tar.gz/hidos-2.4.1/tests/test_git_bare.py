import pytest
from pathlib import Path

import hidos
import hidos.cache


DATA_DIR = Path(__file__).parent / "data"


def test_read_export():
    pytest.importorskip("fastimport")

    with open(DATA_DIR / "test_succession_archive.export", 'rb') as f:
        succs = hidos.cache.successions_from_export(f)
        assert 1 == len(succs)
        succ = succs.pop()
        edids = [str(e.edid) for e in succ.root.all_subeditions() if e.snapshot]
        assert ['0.2', '1.1'] == edids


def test_read_git_bare():
    with open(DATA_DIR / "wk1LzCaCSKkIvLAYObAvaoLNGPc.tar", 'rb') as f:
        succs = hidos.successions_from_git_bare_tarballs([f])
        assert 1 == len(succs)
        succ = succs.pop()
        edids = [str(e.edid) for e in succ.root.all_subeditions() if e.snapshot]
        assert ['0.1', '0.2', '0.3', '0.4', '1.1', '2.1', '2.2'] == edids

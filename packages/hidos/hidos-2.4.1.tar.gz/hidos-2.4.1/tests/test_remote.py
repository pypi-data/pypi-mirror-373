import pytest
from .util import PODify

from hidos.dulwich import DulwichRepoFacade
from hidos.archive import SuccessionArchive
from hidos.dsi import BaseDsi
from hidos.remote import FederatedClient
from hidos.repo import revision_history

from requests_cache import CachedSession

import json, os
from os import listdir
from pathlib import Path

# NOTE: ./conftest.py contains pytest fixtures

CASES_DIR = Path(__file__).parent / "cases"
SUCC_CASES = set(listdir(CASES_DIR / "succ"))
SWHA_BEARER_TOKEN_PATH = Path(__file__).parent / "swha_bearer_token.txt"

if SWHA_BEARER_TOKEN_PATH.exists():
    with open(SWHA_BEARER_TOKEN_PATH) as f:
        os.environ["SWHA_BEARER_TOKEN"] = f.read().strip()
else:
    os.environ["SWHA_BEARER_TOKEN"] = "FOR_OFFLINE_TESTING_USE"


def load(case, stem):
    with open(CASES_DIR / "succ" / case / f"{stem}.json") as f:
        return json.load(f)

def dump(case, got, stem):
    with open(CASES_DIR / "succ" / case / f"{stem}.json", "w") as f:
        return json.dump(got, f)


@pytest.mark.parametrize("case", SUCC_CASES)
def test_cached_succession(case):
    case_dir = CASES_DIR / "succ" / case
    gitcache = set(os.listdir(case_dir / "cache")) - {"http"}
    assert len(gitcache) == 1
    gitcache = gitcache.pop()
    assert gitcache.endswith(".git")
    dsi = BaseDsi(gitcache[:-4])

    git_dir = case_dir / "cache" / gitcache
    hist = revision_history(DulwichRepoFacade(git_dir))
    # dump(case, hist.as_pod(), "got")
    assert load(case, "history") == hist.as_pod()
    archive = SuccessionArchive(hist)
    ds = archive.find_succession(dsi)
    assert ds

    http_cache = CachedSession(
        case_dir / "cache" / "http",
        backend='filesystem',
        allowable_codes=(200, 404),
        stale_if_error=True,
    )
    offline = True  # and False
    c = FederatedClient(http_cache, offline=offline)

    with open(case_dir / "remote_branches.json") as f:
        expected_remotes = set(PODify(json.load(f)))
    assert expected_remotes == set(PODify(c.lookup_remote_branches(dsi)))

    expected_origins = set(e[0] for e in expected_remotes)
    assert expected_origins == c.get_origins(dsi)

    edition_dates_path = case_dir / "edition_dates.json"
    if edition_dates_path.exists():
        with open(case_dir / "edition_dates.json") as f:
            expect_dates = PODify(json.load(f))
        assert expect_dates == PODify(c.edition_archive_dates(ds))

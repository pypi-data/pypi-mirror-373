from __future__ import annotations

import io, glob, os, shutil, tarfile, tempfile
from datetime import datetime
from pathlib import Path
from subprocess import PIPE, run
from typing import BinaryIO

from platformdirs import user_cache_path
from requests_cache import CachedSession

from .archive import Succession, history_successions
from .dsi import BaseDsi, EditionId
from .dulwich import DulwichBackend, repo_from_export
from .remote import FederatedClient, RemoteBranchId
from .repo import revision_history


def successions_from_export(
    fastexport: BinaryIO | bytes | bytearray | memoryview
) -> set[Succession]:
    if isinstance(fastexport, (bytes, bytearray, memoryview)):
        fastexport = io.BytesIO(fastexport)
    return history_successions(revision_history(repo_from_export(fastexport)))


def make_git_bare_tarball(repo: str, outpath: Path) -> None:
    # code adapted from Software Heritage GitBareCooker
    with tempfile.TemporaryDirectory(prefix="git-bare-") as workdir:
        gitdir = os.path.join(workdir, "clone.git")
        run(["git", "clone", "--bare", "--single-branch", repo, gitdir], check=True)

        # Remove example hooks; they take ~40KB and we don't use them
        for filename in glob.glob(os.path.join(gitdir, "hooks", "*.sample")):
            os.unlink(filename)

        """Moves all objects from :file:`.git/objects/` to a packfile."""
        run(["git", "-C", gitdir, "repack", "-d"], check=True)

        # Remove their non-packed originals
        run(["git", "-C", gitdir, "prune-packed"], check=True)

        result = run(
            ["git", "-C", gitdir, "rev-parse", "HEAD"],
            stdout=PIPE,
            text=True,
            check=True,
        )
        rev_hash_hex = result.stdout.strip()

        path = os.path.join(gitdir, "refs/heads/master")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fd:
            fd.write(rev_hash_hex)

        """Creates the final .tar file."""
        with tarfile.TarFile(outpath, mode="w") as tf:
            tf.add(gitdir, arcname=f"swh:1:rev:{rev_hash_hex}.git", recursive=True)


class SuccessionDataMissing(Exception):
    pass


class SuccessionCache:
    def __init__(self, cache_root: Path | None = None, offline: bool = False):
        self.cache_root = cache_root or user_cache_path("hidos", ensure_exists=True)
        self.offline = offline
        http_cache = CachedSession(
            self.cache_root / "http",
            allowable_codes=(200, 404),
            cache_control=True,
            stale_if_error=offline,
        )
        self._client = FederatedClient(http_cache, offline=offline)

    def clear(self) -> None:
        shutil.rmtree(self.cache_root)

    def lookup_remote_branches(self, dsi: BaseDsi) -> set[RemoteBranchId]:
        return self._client.lookup_remote_branches(dsi)

    def get(self, dsi: BaseDsi) -> Succession:
        if not isinstance(dsi, BaseDsi):
            dsi = BaseDsi(dsi)
        subcache = self.cache_root / dsi.base64
        if subcache.exists():
            repo = DulwichBackend.read_repo(subcache)
            if repo is None:
                raise SuccessionDataMissing(dsi)
        elif self.offline:
            raise SuccessionDataMissing(dsi)
        else:
            repo = DulwichBackend.init_bare_repo(subcache)
        if not self.offline:
            for branch in self._client.lookup_remote_branches(dsi):
                repo.fetch(branch.origin, branch.name)
        for succ in history_successions(revision_history(repo)):
            if succ.dsi == dsi:
                return succ
        raise SuccessionDataMissing(dsi)

    def archive_dates(self, succ: Succession) -> dict[EditionId, datetime | None]:
        return self._client.edition_archive_dates(succ)

from __future__ import annotations

from hashlib import blake2b
from pathlib import Path
from typing import Iterable, Mapping, Protocol

from .archive import Succession, history_successions
from .dsi import BaseDsi
from .history import RevisionHistory, RevisionRecord

from sshsig import PublicKey


class ReadRepoFacade(Protocol):
    def tips(self) -> Iterable[RevisionRecord]: ...

    def fetch(self, origin: str, branch: str) -> None: ...


class RepoFacade(ReadRepoFacade, Protocol):
    def branches(self, remote: bool = False) -> Mapping[str, RevisionRecord]: ...

    def create_remote(self, origin: str) -> str: ...

    def commit_genesis_record(
        self, new_branch_name: str, keys: set[PublicKey] | None
    ) -> RevisionRecord: ...

    def commit_edition(
        self, src_path: Path, branch_name: str, edition: str
    ) -> RevisionRecord: ...


class Backend(Protocol):
    def init_bare_repo(self, path: Path) -> ReadRepoFacade: ...

    def read_repo(self, path: Path) -> ReadRepoFacade | None: ...

    def local_repo(self, path: Path) -> RepoFacade | None: ...


def revision_history(repo: ReadRepoFacade) -> RevisionHistory:
    return RevisionHistory(repo.tips())


class SuccessionRepository:
    def __init__(self, repo: RepoFacade) -> None:
        self.history = revision_history(repo)
        self._repo = repo
        self._branches = dict(repo.branches())
        self._remote_heads = dict(repo.branches(remote=True))
        self._successions = {s.dsi: s for s in history_successions(self.history)}

    @property
    def dsis(self) -> Iterable[BaseDsi]:
        return self._successions.keys()

    def get_succession(self, branch_name: str) -> Succession | None:
        tip = self._branches.get(branch_name)
        if not tip:
            tip = self._remote_heads.get(branch_name)
        if not tip:
            return None
        init = self.history.find_genesis(tip)
        dsi = BaseDsi.from_sha1_git(init.hexsha) if init else None
        return self._successions.get(dsi) if dsi else None

    def heads(self, dsi: BaseDsi, remote: bool = False) -> set[str]:
        ret = set()
        succ = self._successions.get(dsi)
        if succ is not None:
            heads = self._remote_heads if remote else self._branches
            for name, rev in heads.items():
                if rev == succ.tip_rev:
                    ret.add(name)
        return ret

    def branches(self) -> Mapping[BaseDsi, Iterable[str]]:
        ret = dict()
        for succ in history_successions(self.history):
            bs = set()
            for name, rev in self._branches.items():
                if rev == succ.tip_rev:
                    bs.add(name)
            ret[succ.dsi] = bs
        return ret

    def _add_rec(self, rec: RevisionRecord, branch_name: str) -> None:
        self.history.add_record(rec)
        self._branches[branch_name] = rec
        self._successions = {s.dsi: s for s in history_successions(self.history)}

    def create_succession(
        self, new_branch: str, keys: set[PublicKey] | None = None
    ) -> None:
        rev = self._repo.commit_genesis_record(new_branch, keys)
        self._add_rec(rev, new_branch)

    def commit_edition(self, src_path: Path, branch_name: str, edition: str) -> None:
        if not self.get_succession(branch_name):
            msg = "Branch {} is not a valid digital succession"
            raise ValueError(msg.format(branch_name))
        rev = self._repo.commit_edition(src_path, branch_name, edition)
        self._add_rec(rev, branch_name)


def origin_hash(origin: str) -> str:
    key = blake2b(digest_size=4)
    key.update(origin.encode())
    return key.hexdigest()

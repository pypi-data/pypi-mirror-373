from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from datetime import date
from typing import TYPE_CHECKING
from warnings import warn

from .dsi import BaseDsi, Dsi, EditionId
from .exceptions import EditionRevisionWarning
from .history import Snapshot, DirectoryRecord, RevisionHistory, RevisionRecord

from sshsig import PublicKey


if TYPE_CHECKING:
    from .util import POD


class Edition(ABC):
    def __init__(self, succession: Succession, edid: EditionId):
        self.suc = succession
        self.edid = edid
        self.date: date | None = None

    @property
    def succession(self) -> Succession:
        return self.suc

    @property
    def dsi(self) -> Dsi:
        return Dsi(self.suc.dsi, self.edid)

    @property
    def unlisted(self) -> bool:
        return self.edid.unlisted

    @property
    def obsolete(self) -> bool:
        latest = self.suc.latest(self.unlisted)
        snap_ed = self.refine()
        if latest and snap_ed:
            return snap_ed.edid < latest.edid
        return False

    @abstractmethod
    def update(self, dir_rec: DirectoryRecord, revision: str, d: date) -> None: ...

    @abstractmethod
    def refine(self, *, expand_to_unlisted: bool = False) -> Edition | None: ...

    @abstractmethod
    def snapshot_editions(self) -> Iterable[SnapshotEdition]: ...

    def all_subeditions(self) -> Iterable[Edition]:
        return []

    @property
    def snapshot(self) -> Snapshot | None:
        return None

    @property
    def hexsha(self) -> str | None:
        return None

    @property
    def swhid(self) -> str | None:
        return None


class CoarseEdition(Edition):
    def __init__(self, succession: Succession, edid: EditionId):
        super().__init__(succession, edid)
        self.subs: dict[int, Edition] = dict()

    def update(self, dir_rec: DirectoryRecord, revision: str, d: date) -> None:
        for num, sub_rec in dir_rec.subs.items():
            sub_ed = self.subs.get(num)
            if not sub_ed:
                if sub_rec.obj:
                    sub_ed = SnapshotEdition(
                        self.suc, self.edid.sub(num), sub_rec.obj, revision, d
                    )
                else:
                    sub_ed = CoarseEdition(self.suc, self.edid.sub(num))
                self.subs[num] = sub_ed
            sub_ed.update(sub_rec, revision, d)
        if dir_rec.obj:
            msg = "Ignored snapshot object data for edition {}"
            warn(msg.format(self.edid), EditionRevisionWarning)

    def refine(self, *, expand_to_unlisted: bool = False) -> Edition | None:
        for subid in reversed(sorted(self.subs.keys())):
            if subid > 0 or expand_to_unlisted or self.unlisted:
                ret = self.subs[subid].refine(expand_to_unlisted=expand_to_unlisted)
                if ret is not None:
                    return ret
        return None

    def snapshot_editions(self) -> Iterable[SnapshotEdition]:
        ret: list[SnapshotEdition] = []
        for sub in self.subs.values():
            ret += sub.snapshot_editions()
        return ret

    def all_subeditions(self) -> Iterable[Edition]:
        ret: list[Edition] = []
        for sub in self.subs.values():
            ret.append(sub)
            ret += sub.all_subeditions()
        return ret


class SnapshotEdition(Edition):
    def __init__(
        self,
        succession: Succession,
        edid: EditionId,
        snapshot: Snapshot,
        revision: str,
        d: date,
    ):
        super().__init__(succession, edid)
        self._snapshot = snapshot
        self.revision = revision
        self.date = d

    def update(self, dir_rec: DirectoryRecord, revision: str, d: date) -> None:
        if dir_rec.subs:
            msg = "Ignored subedition directories for snapshot edition {}"
        elif dir_rec.obj and dir_rec.obj.hexsha != self._snapshot.hexsha:
            msg = "Ignored revised snapshot object data for snapshot edition {}"
        else:
            msg = None
        if msg:
            warn(msg.format(self.edid), EditionRevisionWarning)

    def refine(self, *, expand_to_unlisted: bool = False) -> Edition:
        return self

    def snapshot_editions(self) -> Iterable[SnapshotEdition]:
        return [self]

    @property
    def snapshot(self) -> Snapshot:
        return self._snapshot

    @property
    def hexsha(self) -> str:
        return self._snapshot.hexsha

    @property
    def swhid(self) -> str:
        return self._snapshot.swhid

    @property
    def is_dir(self) -> bool:
        return self._snapshot.is_dir

    def as_pod(self) -> POD:
        ret: dict[str, POD] = dict()
        ret["edid"] = str(self.edid)
        ret["object_type"] = "dir" if self.is_dir else "cnt"
        ret["object_id"] = self.hexsha
        ret["revision"] = self.revision
        ret["date"] = self.date.isoformat() if self.date else None
        return ret


def revision_chain(tip_rev: RevisionRecord) -> Sequence[RevisionRecord]:
    chain = list()
    rev: RevisionRecord | None = tip_rev
    while rev:
        chain.append(rev)
        if len(rev.parents) > 1:
            msg = "Non-linear succession commit histories not supported."
            raise NotImplementedError(msg)
        rev = rev.parent
    return list(reversed(chain))


class Succession:
    def __init__(self, init_rev: RevisionRecord, tip_rev: RevisionRecord):
        self.hexsha = init_rev.hexsha
        self.tip_rev = tip_rev
        self.root = CoarseEdition(self, EditionId())
        self.allowed_keys: set[PublicKey] | None = None
        chain = revision_chain(tip_rev)
        if init_rev != chain[0]:
            msg = "{} is not initial commit for commit history to {}"
            raise ValueError(msg.format(init_rev.hexsha, tip_rev.hexsha))
        for rev in chain:
            self.root.update(rev.dir, rev.hexsha, rev.date)
            if rev.allowed_keys is not None:
                self.allowed_keys = rev.allowed_keys
        self._all_editions = [self.root, *self.root.all_subeditions()]

    @property
    def dsi(self) -> BaseDsi:
        """Return Digital Succession Id"""
        return BaseDsi.from_sha1_git(self.hexsha)

    @property
    def revision(self) -> str:
        return self.tip_rev.hexsha

    @property
    def is_signed(self) -> bool:
        return self.allowed_keys is not None

    def get(self, edid: EditionId) -> Edition | None:
        for e in self._all_editions:
            if e.edid == edid:
                return e
        return None

    def latest(self, unlisted_ok: bool = False) -> Edition | None:
        return self.root.refine(expand_to_unlisted=unlisted_ok)

    def snapshot_editions(self) -> Iterable[SnapshotEdition]:
        return self.root.snapshot_editions()

    def all_editions(self) -> Iterable[Edition]:
        return self._all_editions

    def all_revisions(self) -> Iterable[RevisionRecord]:
        ret = set()
        todo = {self.tip_rev}
        while todo:
            dothis = todo.pop()
            ret.add(dothis)
            todo.update(dothis.parents)
        return ret

    def as_pod(self) -> POD:
        ret: dict[str, POD] = dict()
        ret["dsi"] = str(self.dsi)
        eds = list()
        for sub in self.snapshot_editions():
            eds.append(sub.as_pod())
        if self.allowed_keys is not None:
            ret["allowed_keys"] = [str(k) for k in self.allowed_keys]
        ret["editions"] = eds
        return ret


def history_successions(history: RevisionHistory) -> set[Succession]:
    ret = set()
    for init in history.genesis_records():
        tip = history.find_tip(init)
        if tip:
            ret.add(Succession(init, tip))
    return ret


class SuccessionArchive:
    def __init__(self, history: RevisionHistory) -> None:
        self.successions = dict()
        for succ in history_successions(history):
            self.successions[succ.dsi] = succ

    def find_succession(self, base_dsi: BaseDsi | str) -> Succession | None:
        return self.successions.get(BaseDsi(base_dsi))

    def as_pod(self) -> POD:
        ret: dict[str, POD] = dict()
        ret["successions"] = [succ.as_pod() for succ in self.successions.values()]
        return ret

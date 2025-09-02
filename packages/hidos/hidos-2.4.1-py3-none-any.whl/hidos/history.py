# (c) 2024 E. Castedo Ellerman <castedo@castedo.com>
# Released under the MIT License (https://spdx.org/licenses/MIT)

"""Data records of essential info from Git records in DSGL.

DSGL: Document Succession Git Layout.

Some abstraction above actual Git record information.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from warnings import warn
from typing import TYPE_CHECKING, Sequence
from abc import abstractmethod
from collections.abc import Iterable

from sshsig import PublicKey

from .exceptions import SuccessionSplitWarning


if TYPE_CHECKING:
    from .util import POD


class Snapshot:
    def __init__(self, hexsha: str, is_dir: bool):
        self.hexsha = hexsha
        self.is_dir = is_dir

    @property
    def swhid(self) -> str:
        return "swh:1:{}:{}".format("dir" if self.is_dir else "cnt", self.hexsha)

    def as_pod(self) -> POD:
        return self.swhid

    @abstractmethod
    def copy(self, dest_path: Path) -> None: ...


class DirectoryRecord:
    def __init__(self, is_empty_git_tree: bool) -> None:
        self.is_empty_git_tree = is_empty_git_tree
        self.obj: Snapshot | None = None
        self.subs: dict[int, DirectoryRecord] = dict()

    @property
    def empty(self) -> bool:
        return len(self.subs) == 0 and not self.obj

    def descend(self, indexes: list[int]) -> DirectoryRecord | None:
        ret: DirectoryRecord | None = self
        if indexes:
            sub = self.subs.get(indexes[0])
            ret = sub.descend(indexes[1:]) if sub else None
        return ret

    def as_pod(self) -> POD:
        if self.obj:
            return self.obj.as_pod()
        ret = dict()
        for num, sub in self.subs.items():
            ret[str(num)] = sub.as_pod()
        return ret


class RevisionRecord:
    def __init__(self, hexsha: str):
        self.hexsha = hexsha
        self.allowed_keys: set[PublicKey] | None = None

    @abstractmethod
    def valid_link(self) -> bool:
        """
        Test that link to parents is valid for signed succesions.
        """
        ...

    @property
    def is_init(self) -> bool:
        return not self.parents

    @property
    @abstractmethod
    def parents(self) -> Sequence[RevisionRecord]: ...

    @property
    def parent(self) -> RevisionRecord | None:
        if len(self.parents) > 1:
            warn("More than one single parent", SuccessionSplitWarning)
            return None
        return self.parents[0] if self.parents else None

    @property
    @abstractmethod
    def dir(self) -> DirectoryRecord: ...

    def subdir(self, path: Path) -> DirectoryRecord | None:
        return self.dir.descend([int(p) for p in path.parts])

    @property
    @abstractmethod
    def date(self) -> datetime.date: ...

    def as_pod(self) -> POD:
        ret: dict[str, POD] = dict()
        ret["hexsha"] = self.hexsha
        ret["parents"] = [p.hexsha for p in self.parents]
        if self.allowed_keys is not None:
            ret["allowed_keys"] = [str(k) for k in self.allowed_keys]
        ret["date"] = self.date.isoformat()
        ret["state"] = self.dir.as_pod()
        return ret


class RevisionHistory:
    def __init__(self, recs: Iterable[RevisionRecord] = ()) -> None:
        self.revisions: dict[str, RevisionRecord] = dict()
        self._descent: dict[str, set[RevisionRecord]] = dict()
        self.add_records(recs)

    def add_records(self, recs: Iterable[RevisionRecord]) -> None:
        for rec in recs:
            self.add_record(rec)

    def add_record(self, rec: RevisionRecord) -> None:
        if rec.hexsha not in self.revisions:
            for p in rec.parents:
                self.add_record(p)
                assert p.hexsha in self.revisions
                children = self._descent.setdefault(p.hexsha, set())
                children.add(rec)
            self.revisions[rec.hexsha] = rec

    def genesis_records(self) -> set[RevisionRecord]:
        ret = set()
        for rev in self.revisions.values():
            if not rev.parents:
                if rev.allowed_keys is not None or rev.dir.is_empty_git_tree:
                    # if empty tree, then a genesis record for unsigned succession
                    ret.add(rev)
        return ret

    def find_geneses(self, cur: RevisionRecord) -> set[RevisionRecord]:
        ret = set()
        if not cur.parents:
            ret.add(cur)
        else:
            for p in cur.parents:
                ret.update(self.find_geneses(p))
        return ret

    def find_genesis(self, cur: RevisionRecord) -> RevisionRecord | None:
        found = self.find_geneses(cur)
        if len(found) > 1:
            warn("More than one genesis record", SuccessionSplitWarning)
            return None
        return found.pop() if found else None

    def _find_tips(self, start: RevisionRecord, unsigned: bool) -> set[RevisionRecord]:
        ret = set()
        if start.hexsha in self.revisions:
            children = self._descent.get(start.hexsha)
            if children:
                for child in children:
                    if unsigned or child.valid_link():
                        ret.update(self._find_tips(child, unsigned))
            else:
                ret.add(start)
        return ret

    def find_tip(self, start: RevisionRecord) -> RevisionRecord | None:
        assert not start.parents
        unsigned = start.allowed_keys is None
        found = self._find_tips(start, unsigned)
        if len(found) > 1:
            warn("More than one succession tip revision", SuccessionSplitWarning)
            return None
        return found.pop() if found else None

    def as_pod(self) -> POD:
        ret: dict[str, POD] = dict()
        ret["revisions"] = [r.as_pod() for r in self.revisions.values()]
        return ret

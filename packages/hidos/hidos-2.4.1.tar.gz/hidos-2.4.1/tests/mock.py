from __future__ import annotations

import datetime

from hidos.history import *

from sshsig import PublicKey


class MockSnapshot(Snapshot):
    @staticmethod
    def from_pod(pod):
        if not isinstance(pod, str):
            raise ValueError
        if pod[0:6] != "swh:1:" or pod[6:10] not in ["cnt:", "dir:"]:
            raise ValueError
        return Snapshot(pod[10:], pod[6:10] == "dir:")


class MockDirectoryRecord(DirectoryRecord):
    @staticmethod
    def from_pod(pod):
        ret = MockDirectoryRecord(pod == {})
        if isinstance(pod, str):
            ret.obj = MockSnapshot.from_pod(pod)
        elif isinstance(pod, dict):
            for key, sub in pod.items():
                ret.subs[int(key)] = MockDirectoryRecord.from_pod(sub)
        else:
            raise ValueError
        return ret


def signing_keys_from_pod(pod: POD) -> set[PublicKey] | None:
    if pod is None:
        return None
    ret = set()
    if isinstance(pod, list):
        for sub in pod:
            if isinstance(sub, str):
                ret.add(PublicKey.from_openssh_str(sub))
            else:
               raise ValueError
    else:
       raise ValueError
    return ret


class MockRevisionRecord(RevisionRecord):
    def __init__(self, hexsha, dir_rec, cache, date):
        super().__init__(hexsha)
        self.cache = cache
        self._parent_ids = list()
        self._date = date
        self._dir = dir_rec

    def valid_link(self) -> bool:
        return True

    @property
    def parents(self):
        return [self.cache[name] for name in self._parent_ids]

    @property
    def dir(self):
        return self._dir

    @property
    def date(self):
        return self._date

    @staticmethod
    def from_pod(pod, cache):
        if not isinstance(pod, dict):
            raise ValueError
        hexsha = pod.get("hexsha")
        if not isinstance(hexsha, str):
            raise ValueError
        dir_rec = MockDirectoryRecord.from_pod(pod["state"])
        parents = pod["parents"]
        if not isinstance(parents, list):
            raise ValueError
        sdate = pod["date"]
        if not isinstance(sdate, str):
            raise ValueError
        ret = MockRevisionRecord(hexsha, dir_rec, cache, datetime.date.fromisoformat(sdate))
        ret._parent_ids = [str(p) for p in parents]
        ret.allowed_keys = signing_keys_from_pod(pod.get("allowed_keys"))
        cache[hexsha] = ret
        return ret


class MockRevisionHistory(RevisionHistory):
    def __init__(self, recs):
        super().__init__(recs)

    @staticmethod
    def from_pod(pod):
        cache = dict()
        if not isinstance(pod, dict):
            raise ValueError
        revisions = pod.get("revisions")
        if not isinstance(revisions, list):
            raise ValueError
        for subpod in revisions:
            rev = MockRevisionRecord.from_pod(subpod, cache)
        return MockRevisionHistory(cache.values())


class MockRepoFacade:
    def __init__(self, pod):
        self.pod = pod

    def history(self):
        return MockRevisionHistory.from_pod(self.pod)

from __future__ import annotations

import datetime, io, os, sys, tarfile, tempfile
from datetime import timezone
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    Callable,
    Iterable,
    Mapping,
    Sequence,
    TYPE_CHECKING,
    cast,
)
from urllib.parse import urlparse
from warnings import warn

try:
    from collections.abc import Buffer
except ImportError:
    from typing_extensions import Buffer  # hail mary for Python 3.11

from sshsig import verify, InvalidSignature
from sshsig.allowed_signers import load_for_git_allowed_signers_file

import dulwich.client
import dulwich.errors
import dulwich.repo
from dulwich.object_store import BaseObjectStore
from dulwich.objects import Blob, Commit, ObjectID, Tree

from .dulwish import cast_lookup, tree_lookup_path

from . import util
from .history import Snapshot, DirectoryRecord, RevisionHistory, RevisionRecord
from .repo import ReadRepoFacade, origin_hash


if TYPE_CHECKING:
    from _typeshed import StrPath  # (os.PathLike[str] | str)


def _dulwich_repo_records(repo: dulwich.repo.BaseRepo) -> Iterable[RevisionRecord]:
    heads = repo.refs.as_dict(b"refs/heads").values()
    remotes = repo.refs.as_dict(b"refs/remotes").values()
    objids = set(heads) | set(remotes)
    return (DulwichRevisionRecord(i, repo.object_store) for i in objids)


def repo_history(git_repo_path: StrPath) -> RevisionHistory:
    repo = dulwich.repo.Repo(str(git_repo_path))
    return RevisionHistory(_dulwich_repo_records(repo))


def _mem_repo_from_local_repo(git_repo_path: StrPath) -> dulwich.repo.MemoryRepo:
    try:
        temp_repo = dulwich.repo.Repo(str(git_repo_path))
    except dulwich.errors.NotGitRepository as ex:
        raise ValueError from ex
    objects = [temp_repo.object_store[i] for i in temp_repo.object_store]
    refs = temp_repo.get_refs()
    ret = dulwich.repo.MemoryRepo.init_bare(objects, refs)
    assert isinstance(ret, dulwich.repo.MemoryRepo)
    return ret


def history_from_git_bare_tarballs(
    tarballs: Iterable[BinaryIO | Buffer],
) -> RevisionHistory:
    ret = RevisionHistory()
    for git_bare in tarballs:
        if isinstance(git_bare, Buffer):
            git_bare = io.BytesIO(git_bare)
        with tempfile.TemporaryDirectory("git-bare") as tempdir:
            with tarfile.open(fileobj=git_bare) as tarball:
                tarball.extractall(tempdir, filter='data')
            subdirs = os.listdir(tempdir)
            if len(subdirs) != 1:
                raise ValueError("Tarball should have one top directory")
            mem_repo = _mem_repo_from_local_repo(os.path.join(tempdir, subdirs[0]))
        ret.add_records(_dulwich_repo_records(mem_repo))
    return ret


class _DulwichRepoFacade(ReadRepoFacade):
    def __init__(self, repo: dulwich.repo.BaseRepo):
        self._repo = repo

    def tips(self) -> Iterable[RevisionRecord]:
        return _dulwich_repo_records(self._repo)

    def branches(self, remote: bool = False) -> Mapping[str, RevisionRecord]:
        ret = dict()
        prefix = b"refs/remotes" if remote else b"refs/heads"
        for ref, dulid in self._repo.refs.as_dict(prefix).items():
            ret[ref.decode()] = DulwichRevisionRecord(dulid, self._repo.object_store)
        return ret

    def fetch(self, origin: str, branch: str) -> None:
        if not isinstance(self._repo, dulwich.repo.Repo):
            raise NotImplementedError()
        gitclient = dulwich.client.HttpGitClient(origin)
        parsed = urlparse(origin)
        remote_ref = f"refs/heads/{branch}".encode()
        ref_prefix = [remote_ref]
        progress = cast(Callable[[bytes], None], sys.stderr.buffer.write)
        result = gitclient.fetch(
            parsed.path, self._repo, ref_prefix=ref_prefix, progress=progress
        )
        sys.stderr.buffer.write(b"\r\033[K")  # CSI Erase in Line ANSI escape sequence
        sys.stderr.flush()
        got = result.refs.get(remote_ref)
        if got:
            rid = origin_hash(origin)
            self._repo.refs[f"refs/remotes/{rid}/{branch}".encode()] = got


def repo_from_export(fastexport: BinaryIO) -> ReadRepoFacade:
    import dulwich.fastexport

    warn("fastexport support experimental", DeprecationWarning)
    repo = dulwich.repo.MemoryRepo()
    processor = dulwich.fastexport.GitImportProcessor(repo)
    processor.import_stream(fastexport)
    return _DulwichRepoFacade(repo)


class DulwichRepoFacade(_DulwichRepoFacade):
    def __init__(self, git_repo_path: Path):
        try:
            assert isinstance(git_repo_path, Path)
            super().__init__(dulwich.repo.Repo(str(git_repo_path)))
        except dulwich.errors.NotGitRepository as ex:
            raise ValueError from ex


class DulwichBackend:
    @staticmethod
    def init_bare_repo(path: Path) -> ReadRepoFacade:
        repo = dulwich.repo.Repo.init_bare(str(path), mkdir=True)
        return _DulwichRepoFacade(repo)

    @staticmethod
    def read_repo(path: Path) -> ReadRepoFacade | None:
        try:
            return _DulwichRepoFacade(dulwich.repo.Repo(str(path)))
        except dulwich.errors.NotGitRepository:
            return None

    @staticmethod
    def local_repo(path: Path) -> None:
        raise NotImplementedError


class DulwichSnapshotObject(Snapshot):
    def __init__(self, dulid: ObjectID, store: BaseObjectStore):
        dul = store[dulid]
        store.close()
        super().__init__(dulid.decode('ascii'), isinstance(dul, Tree))
        self.dul = dul
        self._store = store
        assert isinstance(self.dul, (Blob, Tree))

    def copy(self, dest_path: Path) -> None:
        # TODO: log warnings about any special file mode flags getting ignored
        if not self.is_dir:
            assert isinstance(self.dul, Blob)
            with open(dest_path, "wb") as f:
                f.write(self.dul.data)
        else:
            assert isinstance(self.dul, Tree)
            todo = {("", self.dul.id)}
            while todo:
                (subpath, dulid) = todo.pop()
                tree = cast_lookup(self._store.__getitem__, dulid, Tree)
                os.makedirs(dest_path / subpath)
                for name, mode, subid in tree.iteritems():
                    obj = self._store[subid]
                    if isinstance(obj, Blob):
                        filepath = dest_path / subpath / name.decode('ascii')
                        with open(filepath, "wb") as f:
                            f.write(obj.data)
                    else:
                        todo.add((subpath / name.decode('ascii'), subid))
        self._store.close()


class DulwichDirectoryRecord(DirectoryRecord):
    def __init__(self, dulid: ObjectID, store: BaseObjectStore):
        super().__init__(dulid.decode('ascii') == util.EMPTY_TREE)
        dul = cast_lookup(store.__getitem__, dulid, Tree)
        for name, mode, subid in dul.iteritems():
            if name == b"object":
                self.obj = DulwichSnapshotObject(subid, store)
            else:
                try:
                    num = int(name)
                    if num >= 0:
                        self.subs[num] = DulwichDirectoryRecord(subid, store)
                except ValueError:
                    pass
        store.close()


class DulwichRevisionRecord(RevisionRecord):
    def __init__(self, dulid: ObjectID, store: BaseObjectStore):
        super().__init__(dulid.decode('ascii'))
        self._store = store
        self._dul = cast_lookup(store.__getitem__, dulid, Commit)
        self._parents: list[DulwichRevisionRecord] | None = None
        allowed_obj = tree_lookup_path(
            store.__getitem__, self._dul.tree, "signed_succession/allowed_signers"
        )
        if isinstance(allowed_obj, Blob):
            text_stream = io.TextIOWrapper(io.BytesIO(allowed_obj.data))
            self.allowed_keys = set(load_for_git_allowed_signers_file(text_stream))
        else:
            self.allowed_keys = None
        self._store.close()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, DulwichRevisionRecord) and self._dul == other._dul

    def __hash__(self) -> int:
        return hash(self._dul)

    @property
    def parents(self) -> Sequence[RevisionRecord]:
        if self._parents is None:
            self._parents = [
                DulwichRevisionRecord(p, self._store) for p in self._dul.parents
            ]
        return self._parents

    def valid_link(self) -> bool:
        if self.parents and self._parents:  # keeping mypy happy
            return all(self._valid_child(p) for p in self._parents)
        else:
            # make sure genesis record for signed succession is signed consistently
            return self._valid_child(self)

    def _valid_child(self, parent_rev: DulwichRevisionRecord) -> bool:
        # self is the child
        if parent_rev.allowed_keys is None:
            # absence of allowed keys means succession has been capped/frozen
            return False
        c = self._dul
        if c.gpgsig is None:
            return False
        if hasattr(c, "raw_without_sig"):
            crypto_msg = c.raw_without_sig()
        else:
            crypto_msg = raw_without_sig(c)
        try:
            verify(crypto_msg, c.gpgsig, parent_rev.allowed_keys)
            return True
        except InvalidSignature:
            return False
        except NotImplementedError as ex:
            warn(f"Signature encoding feature not supported: {ex}")
            return False

    @property
    def dir(self) -> DirectoryRecord:
        return DulwichDirectoryRecord(self._dul.tree, self._store)

    @property
    def date(self) -> datetime.date:
        secs_since_epoch: int = self._dul.author_time
        author_dt = datetime.datetime.fromtimestamp(secs_since_epoch, timezone.utc)
        return author_dt.date()


def raw_without_sig(self: Commit) -> bytes:
    tmp = self.copy()
    assert isinstance(tmp, Commit)
    tmp._gpgsig = None
    tmp.gpgsig = None
    ret = tmp.as_raw_string()
    if self.message == b'' and not ret.endswith(b"\n\n"):
        # work around for https://github.com/jelmer/dulwich/issues/1429
        ret += b'\n'
    return ret

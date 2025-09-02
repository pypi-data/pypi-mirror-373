from __future__ import annotations

import binascii, datetime, io, os, tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from warnings import warn

import git
from git.objects import Blob, Commit, Tree
from git.objects.base import Object
from git.refs.head import Head
from git.repo.base import Repo
from git.exc import InvalidGitRepositoryError

from sshsig import PublicKey
from sshsig.allowed_signers import (
    load_for_git_allowed_signers_file,
    save_for_git_allowed_signers_file,
)

from . import util
from .dsi import EditionId
from .exceptions import SignedCommitVerifyFailedError, SuccessionCheckedOut
from .exceptions import SignedCommitVerifyFailedWarning
from .history import Snapshot, DirectoryRecord, RevisionRecord
from .repo import ReadRepoFacade, RepoFacade, origin_hash


def git_path_in_tree(path: str, tree: Tree) -> bool:
    try:
        tree.join(path)
        return True
    except KeyError:
        return False


def add_to_tree(
    repo: Repo, tree: Tree | str, path_in_tree: str, src_path: Path
) -> Tree:
    index = git.IndexFile.from_tree(repo, tree)
    if src_path.is_dir():
        if any(util.incompatible_entries(src_path)):
            raise ValueError(f"Invalid snapshot directory contents: {src_path}")
        src_path = src_path.resolve()
        g = git.cmd.Git(src_path)  # src_path is working dir
        # also need to set --work-tree git option to get git add to work
        g.set_persistent_git_options(
            git_dir=repo.git_dir, work_tree=src_path, c="core.fileMode=false"
        )
        temp_index = git.IndexFile.from_tree(repo, util.EMPTY_TREE)
        with g.custom_environment(GIT_INDEX_FILE=temp_index.path):
            g.add(".")
            subtree = g.write_tree()
        assert subtree == util.sha1_hex_for_dir(src_path)
        index.write()
        with g.custom_environment(GIT_INDEX_FILE=index.path):
            g.read_tree(subtree, prefix=path_in_tree)
        index.update()
    else:
        blob_hash = repo.git.hash_object("-w", "--", src_path)
        assert blob_hash == util.sha1_hex_for_file(src_path)
        blob = Blob(
            repo,
            binascii.a2b_hex(blob_hash),
            mode=Blob.file_mode,
            path=path_in_tree,
        )
        index.add([blob])
    return index.write_tree()


class _GitRepoFacade:
    def __init__(self, repo: Repo):
        self.repo = repo

    def tips(self) -> Iterable[RevisionRecord]:
        ret = list()
        for ref in self.repo.references:
            if isinstance(ref, Head):
                ret.append(GitRevisionRecord(ref.commit))
        return ret

    def branches(self, remote: bool = False) -> Mapping[str, RevisionRecord]:
        heads = set(self.repo.heads)
        if remote:
            refs = {r for r in self.repo.references if isinstance(r, Head)}
            refs -= heads
        else:
            refs = heads
        return {r.name: GitRevisionRecord(r.commit) for r in refs}

    def create_remote(self, origin: str) -> str:
        ret = origin_hash(origin)
        if ret not in self.repo.remotes:
            self.repo.create_remote(ret, origin)
        return ret

    def fetch(self, origin: str, branch: str) -> None:
        rid = self.create_remote(origin)
        remote = self.repo.remote(rid)
        remote.fetch(refspec=f"refs/heads/{branch}")

    def commit_genesis_record(
        self, new_branch: str, allowed_keys: set[PublicKey] | None
    ) -> RevisionRecord:
        if allowed_keys:
            # creating a signed succession
            with tempfile.TemporaryDirectory() as tmp:
                allowed_signers = Path(tmp) / "allowed_signers"
                save_for_git_allowed_signers_file(allowed_keys, allowed_signers)
                path_in_tree = "signed_succession/allowed_signers"
                new_tree = add_to_tree(
                    self.repo, util.EMPTY_TREE, path_in_tree, allowed_signers
                )
                params = [new_tree, "-S"]
        else:
            # creating an unsigned succession
            params = [util.EMPTY_TREE]
        with open("/dev/null") as empty_msg:
            hexsha = self.repo.git.commit_tree(*params, istream=empty_msg)
        ret = GitRevisionRecord(self.repo.commit(hexsha))
        if allowed_keys:
            # creating a signed succession
            # make sure the creator can successfully sign successive commits
            if not ret.valid_link():
                raise SignedCommitVerifyFailedError(new_branch)
        self.repo.create_head(new_branch, hexsha)
        return ret

    def is_checked_out(self, branch_name: str) -> bool:
        return not self.repo.bare and self.repo.active_branch.name == branch_name

    def commit_edition(
        self, src_path: Path, branch_name: str, edition: str
    ) -> RevisionRecord:
        if branch_name not in self.repo.heads:
            raise ValueError("Branch {} not found".format(branch_name))
        if self.is_checked_out(branch_name):
            raise SuccessionCheckedOut(branch_name)
        branch = self.repo.heads[branch_name]
        edid = EditionId(edition)
        path_in_tree = "/".join(str(i) for i in edid) + "/object"
        if git_path_in_tree(path_in_tree, branch.commit.tree):
            msg = f"Edition {edid} already stored in {branch_name}"
            raise ValueError(msg)
        new_tree = add_to_tree(self.repo, branch.commit.tree, path_in_tree, src_path)
        tip_rev = GitRevisionRecord(branch.commit)
        params = ["-m", str(edid), "-p", branch.commit, new_tree]
        if tip_rev.allowed_keys is not None:
            params += ["-S"]
        hexsha = self.repo.git.commit_tree(*params)
        ret = GitRevisionRecord(self.repo.commit(hexsha))
        if tip_rev.allowed_keys:
            # we are amending a signed succession
            if not ret.valid_link():
                raise SignedCommitVerifyFailedError(branch_name)
        branch.commit = hexsha
        return ret


class GitRepoFacade(_GitRepoFacade):
    def __init__(self, git_repo_path: Path):
        try:
            super().__init__(Repo(git_repo_path))
        except InvalidGitRepositoryError as ex:
            raise ValueError(ex)


class GitBackend:
    @staticmethod
    def init_bare_repo(path: Path) -> ReadRepoFacade:
        return _GitRepoFacade(Repo.init(path, mkdir=True, bare=True))

    @staticmethod
    def read_repo(path: Path) -> ReadRepoFacade | None:
        return GitBackend.local_repo(path)

    @staticmethod
    def local_repo(path: Path) -> RepoFacade | None:
        try:
            return _GitRepoFacade(Repo(path))
        except InvalidGitRepositoryError:
            return None


def git_read_tree_update_files(repo: Repo, treehash: str, work_dir: Path) -> None:
    work_dir = work_dir.resolve()
    os.makedirs(work_dir)
    g = git.cmd.Git(work_dir)
    # also need to set --work-tree git option to get work_dir to work
    g.set_persistent_git_options(git_dir=repo.git_dir, work_tree=work_dir)
    with tempfile.TemporaryDirectory() as tmp:
        g.update_environment(GIT_INDEX_FILE=os.path.join(tmp, "index"))
        # call git read-tree with -m -u options
        g.read_tree(treehash, m=True, u=True)


def verify_commit(commit: Commit, allowed_signers: Path) -> bool:
    try:
        g = git.cmd.Git()
        g.set_persistent_git_options(
            git_dir=commit.repo.git_dir,
            c=f"gpg.ssh.allowedSignersFile={allowed_signers}",
        )
        g.verify_commit(commit.hexsha)
        return True
    except git.exc.GitCommandError as e:
        warn(str(e), SignedCommitVerifyFailedWarning)
    return False


class GitSnapshotObject(Snapshot):
    def __init__(self, git_entry: Object):
        super().__init__(git_entry.hexsha, isinstance(git_entry, Tree))
        self._gobj = git_entry

    def copy(self, dest_path: Path) -> None:
        if self.is_dir:
            git_read_tree_update_files(self._gobj.repo, self.hexsha, dest_path)
        else:
            assert isinstance(self._gobj, Blob)
            os.makedirs(Path(dest_path).parent, exist_ok=True)
            with open(dest_path, "wb") as file:
                self._gobj.stream_data(file)


class GitDirectoryRecord(DirectoryRecord):
    def __init__(self, git_tree: Tree):
        super().__init__(git_tree.hexsha == util.EMPTY_TREE)
        for entry in git_tree:
            if entry.name == "object":
                self.obj = GitSnapshotObject(git_tree / "object")
            elif isinstance(entry, Tree):
                try:
                    num = int(entry.name)
                    if num >= 0:
                        self.subs[num] = GitDirectoryRecord(entry)
                except ValueError:
                    pass


class GitRevisionRecord(RevisionRecord):
    def __init__(self, git_commit: Commit):
        super().__init__(git_commit.hexsha)
        self._git_commit = git_commit
        self._parents: list[GitRevisionRecord] | None = None
        try:
            entry = git_commit.tree.join("signed_succession/allowed_signers")
        except KeyError:
            entry = None
        if entry and isinstance(entry, Blob):
            byte_stream = io.BytesIO(entry.data_stream.read())
            text_stream = io.TextIOWrapper(byte_stream)
            self.allowed_keys = set(load_for_git_allowed_signers_file(text_stream))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GitRevisionRecord):
            return False
        return self._git_commit == other._git_commit

    def __hash__(self) -> int:
        return self._git_commit.__hash__()

    @property
    def parents(self) -> Sequence[RevisionRecord]:
        if self._parents is None:
            self._parents = [GitRevisionRecord(p) for p in self._git_commit.parents]
        return self._parents

    def valid_link(self) -> bool:
        if self.parents and self._parents:  # keeping mypy happy
            return all(self._valid_child(p) for p in self._parents)
        else:
            # make sure genesis record for signed succession is signed consistently
            return self._valid_child(self)

    def _valid_child(self, allowed_signers_rev: GitRevisionRecord) -> bool:
        # allowed_signers_rev is the parent, self is the child
        if allowed_signers_rev.allowed_keys is None:
            # absence of allowed keys means succession has been capped/frozen
            return False
        tree = allowed_signers_rev._git_commit.tree
        entry = tree.join("signed_succession/allowed_signers")
        with tempfile.TemporaryDirectory() as tmp:
            allowed_signers = Path(tmp) / "allowed_signers"
            with open(allowed_signers, "wb") as fout:
                entry.stream_data(fout)
            return verify_commit(self._git_commit, allowed_signers)

    @property
    def dir(self) -> GitDirectoryRecord:
        return GitDirectoryRecord(self._git_commit.tree)

    @property
    def date(self) -> datetime.date:
        secs_since_epoch: int = self._git_commit.authored_date
        dt = datetime.datetime.fromtimestamp(secs_since_epoch, datetime.timezone.utc)
        return dt.date()

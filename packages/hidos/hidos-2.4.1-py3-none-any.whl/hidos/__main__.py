from __future__ import annotations

import json, logging, os, sys
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, TYPE_CHECKING

import requests.exceptions

from . import util
from .archive import SnapshotEdition
from .cache import SuccessionCache, SuccessionDataMissing
from .cli import CmdLine, SubCmd
from .dsi import BaseDsi, Dsi, EditionId
from .exceptions import SuccessionCheckedOut
from .repo import RepoFacade, SuccessionRepository, origin_hash
from .util import LOG

if TYPE_CHECKING:
    from .archive import Edition, Succession
    from .remote import RemoteBranchId


def version() -> str:
    try:
        from ._version import version

        return str(version)
    except ImportError:
        return "0.0.0"


def printerr(*args: Any) -> None:
    print(*args, file=sys.stderr)


@dataclass
class CmdBase(CmdLine):
    cache: Path | None
    offline: bool

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        parser.add_argument("--cache", type=Path, help="Hidos cache path")
        parser.add_argument(
            "--offline", action="store_true", help="run in offline mode"
        )


@dataclass
class PrintCachePath(CmdBase):
    """print the file system path of the Hidos cache"""

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        pass

    def run(self) -> int:
        cache = SuccessionCache(self.cache, self.offline)
        print(cache.cache_root)
        return 0


@dataclass
class ListCacheDsi(CmdBase):
    """list document successions in the Hidos cache"""

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        pass

    def run(self) -> int:
        cache = SuccessionCache(self.cache, self.offline)
        for name in os.listdir(cache.cache_root):
            try:
                print("dsi:" + BaseDsi(name).base64)
            except ValueError:
                pass
        return 0


@dataclass
class ClearCache(CmdBase):
    """clear (delete) the Hidos cache"""

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        pass

    def run(self) -> int:
        cache = SuccessionCache(self.cache, self.offline)
        cache.clear()
        return 0


class CacheSubCmd(SubCmd):
    """subcommands for working with the Hidos cache"""

    @classmethod
    def add_arguments(klass, parser: ArgumentParser) -> None:
        m = klass.cmd_map(parser)
        m.add("clear", ClearCache)
        m.add("list", ListCacheDsi)
        m.add("path", PrintCachePath)


@dataclass
class GitCmdBase(CmdBase):
    git_dir: Path | None

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        parser.add_argument(
            "--git-dir", type=Path, help="path to the .git repository directory"
        )

    def get_git_repo(self) -> RepoFacade:
        try:
            from .git import GitBackend
        except ImportError:
            msg = "GitPython library must be installed to use git subcommand."
            raise SystemExit(msg)
        path = self.git_dir or Path(".")
        repo = GitBackend.local_repo(path)
        if repo is None:
            msg = f"Invalid Git directory: {path}"
            msg += "\nUse option --git-dir or change to a Git directory."
            raise SystemExit(msg)
        return repo

    def get_repo(self) -> SuccessionRepository:
        return SuccessionRepository(self.get_git_repo())


@dataclass
class PrintDsi(GitCmdBase):
    """print document succession identifier"""

    branch: str

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        parser.add_argument(
            "branch", help="Git branch name of document succession", metavar="BRANCH"
        )

    def run(self) -> int:
        repo = self.get_repo()
        succ = repo.get_succession(self.branch)
        if not succ:
            msg = f"Branch {self.branch} is not a valid branch or succession"
            printerr(msg)
            return 1
        print(f"dsi:{succ.dsi}")
        return 0


@dataclass
class PrintSuccessions(GitCmdBase):
    """list Git branches of document successions"""

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        pass

    def run(self) -> int:
        repo = self.get_repo()
        pod = dict()
        for dsi in sorted(repo.dsis):
            refs = dict()
            if heads := list(repo.heads(dsi)):
                refs['heads'] = heads
            if remotes := list(repo.heads(dsi, remote=True)):
                refs['remotes'] = remotes
            pod[f"dsi:{dsi}"] = dict(refs=refs)
        json.dump(pod, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0


@dataclass
class CreateSuccession(GitCmdBase):
    """create new document succession"""

    new_branch: str
    keys: Path | None

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        parser.add_argument(
            "new_branch", help="name of new Git branch", metavar="NEW_BRANCH"
        )
        parser.add_argument(
            "-k", "--keys", type=Path, help="path to SSH public key file"
        )

    def run(self) -> int:
        repo = self.get_repo()
        keys = util.load_openssh_public_key_file(self.keys) if self.keys else None
        repo.create_succession(self.new_branch, keys=keys)
        succ = repo.get_succession(self.new_branch)
        assert succ
        print(f"dsi:{succ.dsi}")
        return 0


def snapshot_content_errmsg(src_path: Path) -> str | None:
    if src_path.is_dir():
        bad = next(util.incompatible_entries(src_path), None)
        if bad is not None:
            if bad.name.startswith("."):
                msg = "Hidden file/subdirectory not allowed in snapshot: {}"
            elif bad.is_symlink():
                msg = "Symbolic link not allowed in snapshot: {}"
            elif bad.is_dir() and not any(bad.iterdir()):
                msg = "Empty subdirectory not allowed in snapshot: {}"
            else:
                msg = "Incompatible file/subdirectory within snapshot directory: {}"
            return msg.format(bad)
    elif not src_path.is_file():
        return "Snapshot content must be a regular file or directory."
    return None


@dataclass
class CommitEdition(GitCmdBase):
    """commit file or directory to document succession"""

    src_path: Path
    branch: str
    edition: str
    unlisted: bool

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        parser.add_argument(
            "src_path",
            type=Path,
            help="path to file or directory to commit",
            metavar="SRC_PATH",
        )
        parser.add_argument(
            "branch", help="Git branch name of document succession", metavar="BRANCH"
        )
        parser.add_argument(
            "edition", help="edition number of commit", metavar="EDITION"
        )
        parser.add_argument(
            "--unlisted",
            action="store_true",
            help="commit unlisted edition (edition number with a zero component)",
        )

    def run(self) -> int:
        repo = self.get_repo()
        try:
            edid = EditionId(self.edition)
            if edid[-1] == 0:
                printerr(f"Edition number must not end in zero: '{self.edition}'")
                return 1
            unlisted_number = any(i == 0 for i in edid)
            if unlisted_number and not self.unlisted:
                msg = "An edition number with a component equal to zero is unlisted."
                msg += "\nUse the --unlisted option if this is intentional."
                printerr(msg)
                return 1
            if self.unlisted and not unlisted_number:
                msg = "Unlisted edition numbers must have some component equal to zero."
                printerr(msg)
                return 1
        except ValueError:
            printerr(f"Invalid edition number: '{self.edition}'")
            return 1
        if errmsg := snapshot_content_errmsg(self.src_path):
            printerr(errmsg)
            return 1
        try:
            repo.commit_edition(self.src_path, self.branch, self.edition)
        except SuccessionCheckedOut:
            msg = "Succession branch {} should not be checked-out".format(self.branch)
            msg += "\nRun git checkout to switch to a different branch"
            printerr(msg)
            return 1
        return 0


@dataclass
class AddRemoteBranches(GitCmdBase):
    """add remote branches of document succession to local Git repository"""

    dsi: str

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        parser.add_argument(
            "dsi", help="Document Succession Identifier", metavar="[dsi:]DSI"
        )

    def run(self) -> int:
        cache = SuccessionCache(self.cache, offline=self.offline)
        branches = cache.lookup_remote_branches(BaseDsi(self.dsi))
        if not branches:
            printerr("No remote repositories found")
            return 1
        git_repo = self.get_git_repo()
        for branch in branches:
            git_repo.create_remote(branch.origin)
            if not self.offline:
                git_repo.fetch(branch.origin, branch.name)
        return 0


@dataclass
class GitBranchEditionCmdBase(GitCmdBase):
    branch: str
    edition: str | None

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        parser.add_argument(
            "branch", help="Git branch name of document succession", metavar="BRANCH"
        )
        parser.add_argument(
            "edition", nargs="?", help="edition number", metavar="EDITION"
        )

    def get_edition(self) -> Edition | None:
        repo = self.get_repo()
        succ = repo.get_succession(self.branch)
        if not succ:
            msg = f"Branch {self.branch} is not a valid branch or succession."
            printerr(msg)
            return None
        try:
            edid = EditionId() if self.edition is None else EditionId(self.edition)
        except ValueError as ex:
            printerr(ex, f"Bad edition number: '{self.edition}'.")
            return None
        ret = succ.get(edid)
        if ret is None:
            printerr(f"Edition {edid} is not in the succession.")
            return None
        return ret


@dataclass
class GitGetSnapshotContents(GitBranchEditionCmdBase):
    """from Git repository, get snapshot contents of document succession edition"""

    output: Path

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        GitBranchEditionCmdBase.add_arguments(parser)
        parser.add_argument(
            '-o',
            '--output',
            type=Path,
            help="output destination path for snapshot contents",
        )

    def run(self) -> int:
        ed = self.get_edition()
        if not ed:
            return 1
        return copy_snapshot_contents(ed, self.output)


@dataclass
class GitSuccessionInfo(GitBranchEditionCmdBase):
    """get document succession information"""

    def run(self) -> int:
        ed = self.get_edition()
        if not ed:
            return 1
        if not ed.edid:
            print_succession_info(ed.suc)
        else:
            print_edition_info(ed)
        return 0


class GitSubCmd(SubCmd):
    """subcommands for working with a Git repository"""

    @classmethod
    def add_arguments(klass, parser: ArgumentParser) -> None:
        GitCmdBase.add_arguments(parser)
        m = klass.cmd_map(parser)
        m.add("add", AddRemoteBranches)
        m.add("commit", CommitEdition)
        m.add("create", CreateSuccession)
        m.add("dsi", PrintDsi)
        m.add("get", GitGetSnapshotContents)
        m.add("info", GitSuccessionInfo)
        m.add("list", PrintSuccessions)


def copy_snapshot_contents(ed: Edition, output: Path | None) -> int:
    refined = ed.refine()
    if refined is None:
        printerr(f"Succession {ed.suc.dsi} has no editions.")
        return 1
    assert refined.snapshot
    if output is None:
        if refined.snapshot.is_dir:
            msg = f"Use --output; edition {ed.dsi} snapshot is a directory."
            printerr(msg)
            return 1
        output = Path("/dev/stdout")
    refined.snapshot.copy(output)
    return 0


def print_succession_info(
    succ: Succession, branches: set[RemoteBranchId] | None = None
) -> None:
    pod: dict[str, Any] = dict()
    pod["dsi"] = succ.dsi.base64
    pod["signed"] = succ.is_signed
    if succ.allowed_keys is not None:
        pod["allowed_signers"] = [str(k) for k in succ.allowed_keys]
    pod["init"] = f"swh:1:rev:{succ.hexsha}"
    pod["editions"] = [str(e.edid) for e in succ.snapshot_editions()]
    if branches is not None:
        pod["origins"] = list()
        for b in branches:
            pod["origins"].append(
                {'id': origin_hash(b.origin), 'origin': b.origin, 'branch': b.name}
            )
    json.dump(pod, sys.stdout, indent=2)
    sys.stdout.write("\n")


def print_edition_info(
    ed: Edition, dates: dict[EditionId, datetime | None] | None = None
) -> None:
    pod: dict[str, Any] = dict()
    pod["number"] = str(ed.edid)
    if isinstance(ed, SnapshotEdition):
        pod["snapshot"] = ed.snapshot.swhid
        assert ed.date
        pod["author_date"] = str(ed.date)
        if dates is not None:
            arc_date = dates.get(ed.edid)
            pod["archive_date"] = arc_date.date().isoformat() if arc_date else None
        pod["record"] = f"swh:1:rev:{ed.revision}"
    else:
        pod["subeditions"] = [str(se.edid) for se in ed.snapshot_editions()]
    json.dump(pod, sys.stdout, indent=2)
    sys.stdout.write("\n")


@dataclass
class SuccessionEditionCmdBase(CmdBase):
    dsi: str

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        parser.add_argument(
            "dsi",
            help="Document Succession Identifier (and optional edition number)",
            metavar="[dsi:]DSI[/EDITION]",
        )

    def get_edition(self, cache: SuccessionCache) -> Edition | None:
        try:
            dsi = Dsi(self.dsi)
        except ValueError as ex:
            printerr(ex)
            return None
        try:
            succ = cache.get(dsi.base)
        except SuccessionDataMissing:
            printerr(f"Succession data not found for '{self.dsi}'.")
            return None
        ret = succ.get(dsi.edid)
        if ret is None:
            printerr(f"Edition {dsi.edid} is not in the succession.")
            return None
        return ret


@dataclass
class GetSuccessionSnapshot(SuccessionEditionCmdBase):
    """get snapshot contents of document succession edition"""

    output: Path

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        SuccessionEditionCmdBase.add_arguments(parser)
        parser.add_argument(
            '-o',
            '--output',
            type=Path,
            help="output destination path for snapshot contents",
        )

    def run(self) -> int:
        cache = SuccessionCache(self.cache, offline=self.offline)
        ed = self.get_edition(cache)
        if not ed:
            return 1
        return copy_snapshot_contents(ed, self.output)


@dataclass
class PrintHash(CmdBase):
    """print the SWHID for snapshot contents"""

    src_path: Path

    @staticmethod
    def add_arguments(parser: ArgumentParser) -> None:
        parser.add_argument(
            "src_path",
            type=Path,
            help="path to file or directory of snapshot contents",
            metavar="SRC_PATH",
        )

    def run(self) -> int:
        if errmsg := snapshot_content_errmsg(self.src_path):
            printerr(errmsg)
            return 1
        print(util.swhid_from_path(self.src_path))
        return 0


@dataclass
class GetSuccessionInfo(SuccessionEditionCmdBase):
    """get document succession information"""

    def run(self) -> int:
        cache = SuccessionCache(self.cache, offline=self.offline)
        ed = self.get_edition(cache)
        if not ed:
            return 1
        if ed.edid:
            dates = cache.archive_dates(ed.suc)
            print_edition_info(ed, dates)
        else:
            branches = cache.lookup_remote_branches(ed.suc.dsi)
            print_succession_info(ed.suc, branches)
        return 0


class HidosCmd(SubCmd):
    @classmethod
    def add_arguments(klass, parser: ArgumentParser) -> None:
        CmdBase.add_arguments(parser)
        m = klass.cmd_map(parser)
        m.add("cache", CacheSubCmd)
        m.add("get", GetSuccessionSnapshot)
        m.add("git", GitSubCmd)
        m.add("hash", PrintHash)
        m.add("info", GetSuccessionInfo)


def main(args: Any = None) -> int:
    LOG.setLevel(logging.INFO)
    LOG.addHandler(logging.StreamHandler())

    parser = ArgumentParser(prog="hidos")
    parser.add_argument("--version", action="version", version=version())
    HidosCmd.add_arguments(parser)
    try:
        parsed_args = parser.parse_args(args)
        return HidosCmd.run_cmd_line(parsed_args)
    except SystemExit as ex:
        if ex.code is None:
            return 0
        if isinstance(ex.code, int):
            return ex.code
        print(ex.code, file=sys.stderr)
        return 1
    except requests.exceptions.HTTPError as ex:
        if parsed_args.offline:
            if ex.response is not None and ex.response.status_code == 504:
                assert ex.request
                msg = "In offline mode and cache item missing: {}"
                printerr(msg.format(ex.request.url))
                return 1
        raise ex from None


if __name__ == "__main__":
    exit(main())

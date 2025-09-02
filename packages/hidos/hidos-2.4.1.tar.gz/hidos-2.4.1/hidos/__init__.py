from __future__ import annotations

from typing import BinaryIO, Iterable, TYPE_CHECKING
from warnings import warn

from .archive import CoarseEdition, Edition, SnapshotEdition, Succession
from .dsi import BaseDsi, Dsi, EditionId


if TYPE_CHECKING:
    from _typeshed import StrPath  # (os.PathLike[str] | str)
    from collections.abc import Buffer


__all__ = [
    'BaseDsi',
    'CoarseEdition',
    'Dsi',
    'Edition',
    'EditionId',
    'SnapshotEdition',
    'Succession',
    'repo_successions',
    'successions_from_git_bare_tarballs',
]


def repo_successions(git_repo_path: StrPath) -> set[Succession]:
    from .archive import history_successions
    from .dulwich import repo_history

    return history_successions(repo_history(git_repo_path))


def successions_from_git_bare_tarballs(
    tarballs: Iterable[BinaryIO | Buffer],
) -> set[Succession]:
    from .archive import history_successions
    from .dulwich import history_from_git_bare_tarballs

    return history_successions(history_from_git_bare_tarballs(tarballs))


def successions_from_git_bare(
    git_bare: BinaryIO | bytes | bytearray | memoryview,
) -> set[Succession]:
    warn("use successions_from_git_bare_tarballs", DeprecationWarning)
    return successions_from_git_bare_tarballs([git_bare])

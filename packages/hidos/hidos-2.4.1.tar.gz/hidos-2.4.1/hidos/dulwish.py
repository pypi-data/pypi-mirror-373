# dulwish.py -- wishful high-level functions for Dulwich
# (c) 2024 E. Castedo Ellerman <castedo@castedo.com>
# Released under the MIT License (https://spdx.org/licenses/MIT)

from __future__ import annotations

from pathlib import Path
from typing import Callable, TYPE_CHECKING, TypeVar

from dulwich.errors import NotTreeError
from dulwich.objects import Blob, ObjectID, ShaFile, SubmoduleEncountered, Tree


if TYPE_CHECKING:
    from typing import TypeAlias

    PathLike: TypeAlias = Path | str
    ObjectGetter: TypeAlias = Callable[[ObjectID], ShaFile]
    ShaFileType = TypeVar("ShaFileType", bound=ShaFile)


def cast_lookup(
    lookup: ObjectGetter, sha: ObjectID, sha_file_type: type[ShaFileType]
) -> ShaFileType:
    """Strongly typed helper function for object store __getitem__.

    Example:
        lookup = repo.object_store.__getitem__
        tree = cast_lookup(lookup, sha, Tree)
        # mypy knows that tree is of type Tree
    """
    obj = lookup(sha)
    if not isinstance(obj, sha_file_type):
        raise ValueError(f"ShaFile object {sha!r} is not of type {sha_file_type}")
    return obj


def tree_lookup_path(
    lookup: ObjectGetter, tree_id: ObjectID, path: PathLike
) -> Blob | Tree | None:
    """Strongly typed helper function for Tree.lookup_path.

    Example:
        lookup = repo.object_store.__getitem__
        baz = tree_lookup_path(lookup , tree_sha, "foo/bar/baz.txt")
        # mypy knows baz is None or of type Blob or Tree

    Raises:
        Unexpected exceptions due to reasons other than the path
        not leading to a Blob or Tree within the same repo.
    """
    try:
        tree = cast_lookup(lookup, tree_id, Tree)
        mode, sha = tree.lookup_path(lookup, str(path).encode("ascii"))
        ret = lookup(sha)
        assert isinstance(ret, (Blob, Tree))
        return ret
    except (KeyError, NotTreeError, SubmoduleEncountered):
        return None

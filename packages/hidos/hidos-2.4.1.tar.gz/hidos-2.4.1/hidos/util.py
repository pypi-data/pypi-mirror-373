from __future__ import annotations

import dataclasses, logging, os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Mapping, TextIO, cast

import dulwich.objects

from sshsig import PublicKey


if TYPE_CHECKING:
    from _typeshed import StrPath  # (os.PathLike[str] | str)

    JSONType = None | str | int | float | list['JSONType'] | dict[str, 'JSONType']

    # Persistable/Plain-Old-Data type
    # Like JSONType but no float due to rounding errors of float (de)serialization.
    POD = None | str | int | list['POD'] | dict[str, 'POD']


LOG = logging.getLogger('hidos')

# git hash-object -t tree /dev/null
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def JSON_list(value: JSONType) -> list[JSONType]:
    return value if isinstance(value, list) else []


def JSON_get_list(d: JSONType, key: str) -> list[JSONType]:
    return JSON_list(d.get(key) if isinstance(d, dict) else [])


def JSON_dict(value: JSONType) -> dict[str, JSONType]:
    return value if isinstance(value, dict) else {}


def JSON_get_dict(d: JSONType, key: str) -> dict[str, JSONType]:
    return JSON_dict(d.get(key) if isinstance(d, dict) else {})


def JSON_get_str(d: JSONType, key: str, *subkeys: str) -> str:
    value = d.get(key) if isinstance(d, dict) else ""
    if len(subkeys):
        return JSON_get_str(value, *subkeys)
    return value if isinstance(value, str) else ""


def PODify(x: Any) -> POD:
    if hasattr(x, 'as_pod'):
        return cast(POD, x.as_pod())
    if isinstance(x, (type(None), str, int, list, dict)):
        return x
    if isinstance(x, Iterable):
        return [PODify(e) for e in x]
    if isinstance(x, Mapping):
        ret: dict[str, POD] = dict()
        for k, v in x.items():
            if not isinstance(k, str):
                raise ValueError
            ret[k] = PODify(v)
        return ret
    if dataclasses.is_dataclass(x) and not isinstance(x, type):
        return list(dataclasses.astuple(x))
    raise ValueError


def load_openssh_public_key_file(file: Path | TextIO) -> set[PublicKey]:
    """Read public key file in "OpenSSH format".

    Multiple lines are read as a concatenation of multiple OpenSSH format files.
    """
    if isinstance(file, Path):
        with open(file, encoding="ascii") as f:
            return load_openssh_public_key_file(f)
    ret = set()
    for line in file.readlines():
        ret.add(PublicKey.from_openssh_str(line))
    return ret


def incompatible_entries(path: StrPath) -> Iterator[Path]:
    """Iterator of directory tree entries that are snapshot incompatible.

    Raises:
        NotADirectoryError: if path not a directory.
    """
    for entry in os.scandir(path):
        if entry.name.startswith("."):
            yield Path(entry.path)
        elif entry.is_dir():
            if any(os.scandir(entry.path)):
                yield from incompatible_entries(entry.path)
            else:
                yield Path(entry.path)
        elif entry.is_symlink() or not entry.is_file():
            yield Path(entry.path)


def sha1_hex_for_file(path: StrPath) -> str:
    blob = dulwich.objects.Blob()
    blob.data = Path(path).read_bytes()
    return blob.sha().hexdigest()


def sha1_hex_for_dir(path: StrPath) -> str:
    """Get git SHA1 hex hash for DSGL snapshot filtered directory.

    Raises:
        NotADirectoryError: if path not a directory.
    """
    tree = dulwich.objects.Tree()
    for entry in os.scandir(path):
        if not entry.name.startswith("."):
            if entry.is_file() and not entry.is_symlink():
                mode = 0o100644
                sha = sha1_hex_for_file(entry.path)
            elif entry.is_dir():
                mode = 0o040000
                sha = sha1_hex_for_dir(entry.path)
            else:
                raise ValueError(entry.path)
            if sha != EMPTY_TREE:
                tree.add(entry.name.encode(), mode, sha.encode('ascii'))
    return tree.sha().hexdigest()


def swhid_from_path(path: StrPath) -> str:
    """Get SWHID for DSGL snapshot file or directory.

    Raises:
        ValueError: if path not to directory nor file.
    """
    if os.path.isfile(path):
        return "swh:1:cnt:" + sha1_hex_for_file(path)
    if os.path.isdir(path):
        return "swh:1:dir:" + sha1_hex_for_dir(path)
    raise ValueError(path)

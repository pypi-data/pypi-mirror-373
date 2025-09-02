from __future__ import annotations

# Python standard library
import base64
import binascii
import functools
from typing import Any, Iterable, Iterator
from warnings import warn


@functools.total_ordering
class EditionId:
    def __init__(self, value: str | EditionId | Iterable[int] = tuple()):
        self._tuple: tuple[int, ...]
        if isinstance(value, EditionId):
            self._tuple = value._tuple
        else:
            if isinstance(value, str):
                try:
                    self._tuple = tuple(int(s) for s in value.split("."))
                except ValueError as ex:
                    msg_def = "Edition numbers consist of point-separated integers."
                    raise ValueError(msg_def) from ex
            else:
                if any(not isinstance(i, int) for i in value):
                    raise ValueError("EditionId components must all be int")
                self._tuple = tuple(value)
            if any(i < 0 for i in self._tuple):
                raise ValueError("EditionId component integers must be non-negative")
            if any(i > 9999 for i in self._tuple):
                msg = "EditionId component integers must not have more than 4 digits"
                raise ValueError(msg)

    def sub(self, num: int) -> EditionId:
        return EditionId((*self._tuple, num))

    @property
    def listed(self) -> bool:
        return not self.unlisted

    @property
    def unlisted(self) -> bool:
        return 0 in self._tuple

    def __getitem__(self, i: int) -> int:
        return self._tuple[i]

    def __len__(self) -> int:
        return len(self._tuple)

    def __str__(self) -> str:
        return ".".join((str(i) for i in self._tuple))

    def __hash__(self) -> int:
        return hash(self._tuple)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, EditionId):
            return self._tuple == other._tuple
        return False

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, EditionId):
            return self._tuple >= other._tuple
        raise TypeError("Must compare a EditionId to a EditionId")

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self) -> Iterator[int]:
        return iter(self._tuple)


@functools.total_ordering
class BaseDsi:
    raw: bytes
    base64: str

    def __init__(self, value: BaseDsi | str):
        if isinstance(value, BaseDsi):
            self.raw = value.raw
            self.base64 = value.base64
        else:
            value = str(value)
            if value.startswith("dsi:"):
                value = value[4:]
            if value.endswith("="):
                msg = "DSI strings should not end with '=': {}"
                warn(msg.format(value), SyntaxWarning)
                value = value[:-1]
            if len(value) != 27:
                raise ValueError(f"DSI must be 27 characters: {value}")
            self.base64 = value
            try:
                self.raw = base64.urlsafe_b64decode(value + "=")
            except binascii.Error:
                raise ValueError(f"DSI must be valid base64url encoding: {value}")
            assert len(self.raw) == 20
            roundtrip = base64.urlsafe_b64encode(self.raw).decode()
            if roundtrip[26] != self.base64[26]:
                raise ValueError(f"Last character not valid for DSI: {value}")
            assert roundtrip == (self.base64 + "=")

    @classmethod
    def from_sha1_git(self, hexstr: str) -> BaseDsi:
        if len(hexstr) != 40:
            raise ValueError("SHA-1 hash must be 40 characters")
        url = base64.urlsafe_b64encode(binascii.a2b_hex(hexstr)).decode()
        assert url[-1] == "="
        return BaseDsi(url[:-1])

    @property
    def sha1_git(self) -> str:
        return binascii.b2a_hex(self.raw).decode()

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.base64

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseDsi):
            return self.raw == other.raw
        if isinstance(other, Dsi):
            return self.raw == other.base.raw and not other.edid
        return False

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, BaseDsi):
            return self.base64 >= other.base64
        if isinstance(other, Dsi):
            return self.base64 > other.base.base64 or self == other
        raise TypeError("Must compare a BaseDsi to a BaseDsi or Dsi")

    def __hash__(self) -> int:
        return hash(self.raw)


@functools.total_ordering
class Dsi:
    def __init__(
        self, value: BaseDsi | Dsi | str, edition: EditionId | None = None
    ):
        self.base: BaseDsi
        self.edid: EditionId
        if isinstance(value, Dsi):
            self.base = value.base
            self.edid = value.edid
        elif isinstance(value, BaseDsi):
            self.base = value
            self.edid = EditionId() if edition is None else edition
        else:
            parts = value.split("/", 1)
            if len(parts) > 2:
                raise ValueError(f"Invalid DSI: {value}")
            self.base = BaseDsi(parts[0])
            try:
                self.edid = EditionId(parts[1]) if parts[1] else EditionId()
            except IndexError:
                self.edid = EditionId()
        if edition is not None:
            edid = EditionId(edition)
            if self.edid != EditionId() and self.edid != edition:
                raise ValueError(f"Conflicting edition: {value} vs {edition}")
            self.edid = edid

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        eds = str(self.edid)
        return str(self.base) if not eds else f"{self.base}/{eds}"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Dsi):
            return self.base == other.base and self.edid == other.edid
        if isinstance(other, BaseDsi):
            return self.base == other and not self.edid
        return False

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, Dsi):
            if self.base == other.base:
                return self.edid >= other.edid
            return self.base > other.base
        if isinstance(other, BaseDsi):
            return self.base >= other
        raise TypeError("Must compare a Dsi to a Dsi or BaseDsi")

    def __hash__(self) -> int:
        return hash((self.base, self.edid))

import pytest

from hidos.dsi import BaseDsi, Dsi, EditionId


def test_empty_edition_id():
    empty = EditionId()
    assert len(empty) == 0
    assert str(empty) == ""
    assert empty.listed is True


def test_edition_id_bad_values():
    with pytest.raises(ValueError):
        EditionId("")
    with pytest.raises(ValueError):
        EditionId("1.-1")
    with pytest.raises(ValueError):
        EditionId("-1")
    with pytest.raises(ValueError):
        EditionId("1.b1")
    with pytest.raises(ValueError):
        EditionId([1, 1.2])


def test_edition_id_compare():
    assert EditionId("1.1") > EditionId("0.3")
    assert EditionId("1.11") > EditionId("1.9")


def test_dsi():
    dsi = Dsi("DZFCt68peNNajZ34WtZni9VYxzo")
    assert len(dsi.edid) == 0
    s = "DZFCt68peNNajZ34WtZni9VYxzo/1"
    dsi = Dsi("DZFCt68peNNajZ34WtZni9VYxzo/1")
    assert dsi.edid == EditionId("1")
    assert str(dsi) == s
    assert dsi == Dsi(s)


@pytest.mark.filterwarnings("ignore:DSI ")
def test_last_base_dsi_char():
    # In edition 2 of DSI spec, last character is restricted,
    # because 40 bytes are getting encoded, two bits of base64url are unused.
    ok_last_char = list("AEIMQUYcgkosw048")
    some26 = "01234567890123456789012345"
    for ci in range(256):
        ch = chr(ci)
        if ch not in ok_last_char:
            with pytest.raises(ValueError):
                BaseDsi(some26 + ch)


def test_dsi_equality():
    bd = BaseDsi("1wFGhvmv8XZfPx0O5Hya2e9AyXo")
    d1 = Dsi("dsi:1wFGhvmv8XZfPx0O5Hya2e9AyXo/1")
    assert bd == Dsi("1wFGhvmv8XZfPx0O5Hya2e9AyXo")
    assert bd == Dsi("dsi:1wFGhvmv8XZfPx0O5Hya2e9AyXo")
    assert bd == Dsi("dsi:1wFGhvmv8XZfPx0O5Hya2e9AyXo/")
    assert bd == Dsi("1wFGhvmv8XZfPx0O5Hya2e9AyXo", EditionId())
    assert bd != Dsi("1wFGhvmv8XZfPx0O5Hya2e9AyXo", EditionId("1"))
    assert d1 == Dsi("1wFGhvmv8XZfPx0O5Hya2e9AyXo", EditionId("1"))
    assert d1 != Dsi("1wFGhvmv8XZfPx0O5Hya2e9AyXo/2")


def test_edition_order():
    assert EditionId() < EditionId("1")
    assert EditionId("2") > EditionId("1")
    assert EditionId("1.4") < EditionId("1.20")
    assert EditionId("2.1") > EditionId("1.2")


def test_dsi_order():
    lo = BaseDsi("1wFGhvmv8XZfPx0O5Hya2e9AyXo")
    hi = BaseDsi("DZFCt68peNNajZ34WtZni9VYxzo")
    assert lo <= lo
    assert lo < hi
    assert lo < Dsi(lo, EditionId("1"))
    assert Dsi(lo, EditionId("1")) > lo
    assert Dsi(lo, EditionId("2")) > Dsi(lo, EditionId("1"))
    assert Dsi(lo, EditionId("2")) < Dsi(hi, EditionId("1"))

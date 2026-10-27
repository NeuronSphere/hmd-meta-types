"""Blob attributes round-trip, including the empty blob (HMD_META_TYPES_ISSUE_001).

New tests, not baseline: the empty-blob case failed before 2026-10-27.
"""

from hmd_meta_types import Entity


def test_empty_blob_round_trips(anoun):
    entity = anoun(field1="x", blobfield=b"")
    data = entity.serialize()
    assert data["blobfield"] == ""
    back = Entity.deserialize(anoun, data)
    assert back.blobfield == b""
    assert isinstance(back.blobfield, bytes)


def test_blob_round_trips(anoun):
    entity = anoun(field1="x", blobfield=b"\x00\x01\xff")
    back = Entity.deserialize(anoun, entity.serialize())
    assert back.blobfield == b"\x00\x01\xff"


def test_absent_and_null_blob_stay_none(anoun):
    assert Entity.deserialize(anoun, {"field1": "x"}).blobfield is None
    assert (
        Entity.deserialize(anoun, {"field1": "x", "blobfield": None}).blobfield is None
    )

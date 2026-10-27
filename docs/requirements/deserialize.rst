.. Deserialization requirements

Deserialization
===============

.. req:: Read input the way json.loads and deserialize do
    :id: HMD_META_TYPES_REQ_DES_001
    :status: implemented

    ``Deserialize`` shall parse JSON as ``json.loads`` does (key order kept, a
    repeated key's last value, NaN and Infinity accepted, integers of any size,
    ``1`` an int and ``1.0`` a float) and decode attributes as
    ``Entity.deserialize`` does: only truthy values are decoded, so an empty
    ``[]`` or ``{}`` passes through as it is, and ``__schema`` is dropped. The
    one exception is a blob's empty string, which is decoded
    (:need:`HMD_META_TYPES_REQ_DES_004`).

.. req:: Parse timestamps like dateutil's isoparse
    :id: HMD_META_TYPES_REQ_DES_002
    :status: implemented

    Timestamps shall be parsed as ``dateutil.parser.isoparse`` (2.8.2) parses
    them: common, week and ordinal dates; any single separator character; times
    with or without colons; fractions with ``.`` or ``,`` truncated to
    microseconds; hour 24; ``Z`` and ``±HH``, ``±HHMM``, ``±HH:MM`` offsets, a
    zero offset being UTC.

.. req:: Decode base64 as Python does
    :id: HMD_META_TYPES_REQ_DES_003
    :status: implemented

    Base64 shall decode as ``base64.b64decode`` with ``validate=False``:
    characters outside the alphabet are skipped, decoding stops at the first
    complete padding, and a truncated quad is an error. Decoded collection and
    mapping bytes shall be read as Latin-1 text before parsing.

.. req:: An empty blob round-trips
    :id: HMD_META_TYPES_REQ_DES_004
    :status: implemented

    Python and Go shall deserialize a blob attribute whose value is the empty
    string ``""`` to empty bytes (``b""``), so ``b""`` serializes to ``""`` and
    reads back unchanged. Until 2026-10-27 Python skipped decoding the falsy
    ``""`` and rejected it as a ``str``, answering HTTP 500 in services
    (:need:`HMD_META_TYPES_ISSUE_001`). The corpus case ``blob_empty`` pins it for
    Go; ``src/python/test/test_blob.py`` and ``test_corpus.py`` pin it for Python.

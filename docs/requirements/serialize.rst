.. Serialization requirements

Serialization
=============

.. req:: Serialize in Python's key order
    :id: HMD_META_TYPES_REQ_SER_001
    :status: implemented

    ``Serialize`` shall write every set attribute in definition order, then
    ``identifier``, ``_updated``, ``_created``, omitting unset and ``None``
    values but keeping falsy ones (``0``, ``false``, ``""``).

.. req:: Write timestamps with isoformat
    :id: HMD_META_TYPES_REQ_SER_002
    :status: implemented

    A timestamp shall serialize as Python's ``datetime.isoformat()``: a four-digit
    year, microseconds only when non-zero, and ``+00:00`` for an aware value
    (aware values are stored in UTC).

.. req:: Base64-encode collections and mappings
    :id: HMD_META_TYPES_REQ_SER_003
    :status: implemented

    A collection or mapping shall serialize as the base64 of its ``json.dumps``
    text, encoded as Latin-1, unless raw collections are requested
    (``encode_blobs=False``), in which case it is written as JSON.

.. req:: Base64-encode blobs
    :id: HMD_META_TYPES_REQ_SER_004
    :status: implemented

    A blob shall serialize as standard, padded base64.

.. req:: Write relationship references and the schema name
    :id: HMD_META_TYPES_REQ_SER_005
    :status: implemented

    A relationship shall end with ``ref_to`` then ``ref_from``. With
    ``IncludeSchema``, ``__schema`` (the definition's full name) shall come last.

.. req:: Produce Python's JSON text
    :id: HMD_META_TYPES_REQ_SER_006
    :status: implemented

    JSON text shall match ``json.dumps`` with its defaults: ``", "`` and ``": "``
    separators, ``ensure_ascii`` escaping (surrogate pairs above the BMP, lone
    surrogates kept), floats as ``repr`` (``1e+16``, ``1e-05``, ``100.0``,
    ``NaN``, ``Infinity``), and integers of any size.

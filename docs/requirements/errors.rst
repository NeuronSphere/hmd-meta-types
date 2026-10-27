.. Error requirements

Errors
======

.. req:: Report Python's error category
    :id: HMD_META_TYPES_REQ_ERR_001
    :status: implemented

    Every rejection shall carry the category Python's rejection maps to:
    ``type``, ``missing_required``, ``extra_fields``, ``required_null``, ``enum``,
    ``validation``, ``schema``, ``unknown_type``, ``ref_type``, ``missing_ref`` or
    ``decode``. ``tools/corpus/golden.py`` defines the mapping from Python
    exceptions. Messages may differ.

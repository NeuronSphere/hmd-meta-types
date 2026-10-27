.. Setter requirements

Setting Attributes
==================

.. req:: Check value types like type_mapping
    :id: HMD_META_TYPES_REQ_SET_001
    :status: implemented

    A value shall be accepted only for its attribute's type: ``integer`` and
    ``epoch`` take an int or a bool (Python's ``isinstance(True, int)``),
    ``float`` a float but not an int, ``string`` a string, ``bool`` a bool,
    ``timestamp`` a timestamp, ``collection`` an array, ``mapping`` an object and
    ``blob`` bytes. ``None`` is always accepted for an attribute that is not
    required.

.. req:: Check required and declared attributes in Python's order
    :id: HMD_META_TYPES_REQ_SET_002
    :status: implemented

    Construction shall check, in order: a relationship's ``ref_from`` and
    ``ref_to`` (present, then strings), missing required attributes, attributes
    the definition does not declare, then each value in input order. Setting a
    required attribute to ``None`` shall be an error.

.. req:: Check enum membership by Python equality
    :id: HMD_META_TYPES_REQ_SET_003
    :status: implemented

    An enum value shall be accepted when it equals an item of ``enum_def`` by
    Python's ``==``. An enum attribute without ``enum_def`` shall be an
    unknown-type error, as Python's ``KeyError`` is.

.. req:: Apply validation rules
    :id: HMD_META_TYPES_REQ_SET_004
    :status: implemented

    For strings, ``regex`` shall match from the start of the value and
    ``datetime`` shall succeed as CPython 3.11's ``strptime`` does (whole value,
    unpadded numbers allowed, no leap-year fix for a year-less Feb 29). For
    integers and floats, ``min`` and ``max`` shall compare exactly, and NaN shall
    pass, as Python's comparisons with NaN are false.

.. req:: Validate collections and mappings against their JSON Schema
    :id: HMD_META_TYPES_REQ_SET_005
    :status: implemented

    A collection or mapping whose attribute has a ``schema`` shall be validated
    with draft 2020-12 unless ``$schema`` names another draft, without format
    assertions, as ``jsonschema.validate`` does.

.. req:: Reject types meta-types does not know
    :id: HMD_META_TYPES_REQ_SET_006
    :status: implemented

    Setting a non-``None`` value on an attribute whose type is not one of the ten
    meta-types types (real lang packs use ``int`` and ``boolean``) shall be an
    unknown-type error, as Python's ``KeyError`` is.

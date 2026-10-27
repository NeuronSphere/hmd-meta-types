.. Definition requirements

Entity Definitions
==================

.. req:: Load .hms definitions in source order
    :id: HMD_META_TYPES_REQ_DEF_001
    :status: implemented

    ``LoadDefinition`` shall read a ``.hms`` file's name, namespace, metatype,
    ``ref_from``/``ref_to`` and attributes, keeping attribute order exactly as
    written, because serialization follows it. ``required`` shall follow Python
    truthiness. The internal attributes ``identifier``, ``_updated`` and
    ``_created`` shall follow the declared ones, as Python's
    ``attributes | internal_attributes`` orders them.

.. req:: Answer definition questions the way Python's generated classes do
    :id: HMD_META_TYPES_REQ_DEF_002
    :status: implemented

    ``FullName`` shall be ``namespace.name`` (just ``name`` without a namespace),
    matching ``get_namespace_name``. Setting an attribute shall look up declared
    attributes before internal ones, as ``_setter`` does, while serialization uses
    the merged order. A definition that is not a JSON object, or has no name, shall
    be an error.

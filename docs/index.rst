.. hmd-meta-types

hmd-meta-types
====================

The ``hmd-meta-types`` repository is a library that provides python
support for classes generated from the hmd meta-type schema. This library
provides base classes for hmd entities that provide a common set of functionality
that is leveraged in persistence and service implementations.

There are three core python base classes:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Class
      - Description
    * - ``Entity``
      - The root base class that provides the implementation for most common
        functionality, including runtime type checking, serialization, identifier property,
        equality checking and hashing.
    * - ``Noun(Entity)``
      - The base class for hmd nouns. Adds support to cache associated relationships to other
        noun instances.
    * - ``Relationship(Entity)``
      - The base class for hmd relationships. Relationships are links between two noun instances.
        Adds support for the "from" and "to" noun instances.

Example
+++++++

The following example shows a sample shows a sample definition of a relationship entity along with
the python code that is generated. This will serve to illustrate the functionality of the
base classes.

.. code-block:: json

    {
      "name": "repo_instance_req_repo_instance",
      "namespace": "hmd_lang_deployment",
      "metatype": "relationship",
      "ref_from": "hmd_lang_deployment.repo_instance",
      "ref_to": "hmd_lang_deployment.repo_instance",
      "attributes": {
        "role": {
          "description": "The role the referenced repo_class assumes relative to the referring repo_class.",
          "type": "string",
          "required": true
        },
        "config": {
           "description": "Sample configuration data.",
           "type": "mapping",
           "required": false
        }
      }
    }

This json defines a relationship entity that joins two instances of the type,
``hmd_lang_deployment.repo_instance``. It also has a required attribute named, ``role``,
that is a string and an attribute named, ``config`` that is a mapping.

The following python code is generated from this schema file. Note that the class extends
the ``Relationship`` base class.

.. code-block:: python

    from hmd_meta_types import Relationship, Noun, Entity
    from hmd_lang_deployment.repo_instance import RepoInstance
    from hmd_lang_deployment.repo_instance import RepoInstance
    from datetime import datetime
    from typing import List, Dict, Any

    class RepoInstanceReqRepoInstance(Relationship):

        _entity_def = \
            {'name': 'repo_instance_req_repo_instance', 'namespace': 'hmd_lang_deployment', 'metatype': 'relationship', 'ref_from': 'hmd_lang_deployment.repo_instance', 'ref_to': 'hmd_lang_deployment.repo_instance', 'attributes': {'role': {'description': 'The role the referenced repo_class assumes relative to the referring repo_class.', 'type': 'string', 'required': True}, 'config': {'description': 'Sample configuration data.', 'type': 'mapping', 'required': False}}}

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        @staticmethod
        def entity_definition():
            return RepoInstanceReqRepoInstance._entity_def

        @staticmethod
        def get_namespace_name():
            return Entity.get_namespace_name(RepoInstanceReqRepoInstance._entity_def)

        @staticmethod
        def ref_from_type():
            return RepoInstance

        @staticmethod
        def ref_to_type():
            return RepoInstance

        @property
        def role(self) -> str:
            return self._getter("role")

        @role.setter
        def role(self, value: str) -> None:
            self._setter("role", value)

        @property
        def config(self) -> Dict:
            return self._getter("config")

        @config.setter
        def config(self, value: Dict) -> None:
            self._setter("config", value)


Property Types
++++++++++++++

Both relationship and noun entities can define a collection of attributes. There are 6
primitive types and 3 blob types.

The primitive types include the following:

.. list-table::
    :widths: 25 25 75
    :header-rows: 1

    * - Type
      - Python Type
      - Description
    * - string
      - ``str``
      -
    * - integer
      - ``int``
      -
    * - float
      - ``float``
      -
    * - enum
      - ``str``
      - A constrained set of string values.
    * - timestamp
      - ``datetime``
      - A timestamp object that contains up-to micro-second precision.

Blob types are serialized and stored persistently as base64-encoded strings (see Serialization). The
``collection`` and ``mapping`` types are intended to provide a convenient way to store simple
(json-serailizable) data using common language support, not as a way to model entity relationships.

The blob types include:

.. list-table::
    :widths: 25 25 75
    :header-rows: 1

    * - Type
      - Python Type
      - Description
    * - collection
      - ``list``
      - A list of json-serializable python objects.
    * - mapping
      - ``dict``
      - A python dictionary of json-serializable python objects.
    * - blob
      - ``bytes``
      -


Property Getters/Setters
++++++++++++++++++++++++

In the generated code, attributes are created using the python ``@property`` wrapper. The
implementation simply delegates to the ``Entity._setter`` and ``Entity._getter`` methods.

The ``Entity._setter`` method does runtime type checking to verify the data being stored and
fails if a field marked as required is set to ``None``.

Serialization Support
+++++++++++++++++++++

All hmd entities are serialized into simple json documents for transmission over the wire
for persistence. The ``Entity.serialize`` and ``Entity.deserialize`` methods are used for
for this purpose.

Primitive data types (``string``, ``integer``, ``float``, ``enum``) are serialized as json primitives.

Timestamp fields are serialized as ISO 8601 formatted strings.

Blob fields are serialized as base64-encoded strings. For the ``collection`` and ``mapping`` types,
the following python code is used for serialization.

.. code-block:: python

    # serialization
    b64encode(dumps(python_type).encode(encoding="utf-8")).decode("utf-8")

    # deserailization
    loads(b64decode(serialized_string.encode(encoding="utf-8")).decode("utf-8"))

For the ``blob`` type, the following python code is used for serialization:

.. code-block:: python

    # serialization
    b64encode(python_bytes).decode("utf-8")

    # deserailization
    b64decode(serailized_string.encode(encoding="utf-8"))



.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

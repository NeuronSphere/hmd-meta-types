.. hmd-meta-types requirements

Requirements
============

What the Go implementation of hmd-meta-types
(``src/go/metatypes``, module ``github.com/neuronsphere/hmd-meta-types/src/go/metatypes``)
must do, as `sphinx-needs <https://sphinx-needs.readthedocs.io/>`_ items linked to
the tests that verify them. The program is NERD005 in hmd-entity-storage (Go
persistence stack); this is its phase 2.

The Python implementation in ``src/python`` is the reference. The golden corpus in
``testdata/corpus`` pins its behavior: ``tools/corpus/golden.py`` records what Python
does with every case, and the Go tests must reproduce it byte for byte. Where Go
deliberately differs, the difference is a requirement in :doc:`differences`.

IDs are ``HMD_META_TYPES_REQ_<AREA>_<NNN>``. A Go test declares coverage with
``// Requirements: REQ_<AREA>_<NNN>``. ``make reqs-check`` (hmd-cli-bartleby's
reqtrace) fails on an untested requirement or an untagged test.

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Area
     - Covers
   * - ``DEF``
     - Loading ``.hms`` entity definitions
   * - ``SER``
     - Serializing an entity to Python's JSON bytes
   * - ``DES``
     - Deserializing, including timestamps and base64
   * - ``SET``
     - The setter's type, required, enum, validation and schema checks
   * - ``ERR``
     - Error categories shared with Python
   * - ``CORPUS``
     - The golden corpus and the generated go_lib code
   * - ``DIFF``
     - Deliberate differences from Python

.. toctree::
   :maxdepth: 1

   definition
   serialize
   deserialize
   setter
   errors
   corpus
   differences
   traceability

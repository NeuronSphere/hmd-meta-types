.. Python implementation requirements

Python Implementation
=====================

What the Python implementation in ``src/python`` must keep doing while the Go
port is built. The golden corpus is the shared contract. Its goldens are
Python's own output, so Python drifting from them breaks the Go side's
reference. reqtrace reads only Go and Robot tests, so these requirements are
``trace-exempt``, and each one names the pytest tests that verify it.
Concerns with the current Python behavior are listed in :doc:`../known_issues`.

.. req:: Python reproduces every corpus golden
    :id: HMD_META_TYPES_REQ_PY_001
    :status: implemented
    :tags: trace-exempt

    For every case in ``testdata/corpus/cases.json``, Python meta-types shall
    produce exactly ``golden/<case>.json``, or reject the input with the
    category in ``golden/<case>.error``. Verified by
    ``src/python/test/test_corpus.py::test_python_matches_golden``
    (156 cases). A deliberate behavior change regenerates the goldens with
    ``make docker-corpus-golden`` and changes Go in the same commit.

.. req:: Python keeps its baseline behavior
    :id: HMD_META_TYPES_REQ_PY_002
    :status: implemented
    :tags: trace-exempt

    The Python implementation shall keep passing every test that existed
    before the Go port began. These are tagged ``baseline`` and select with
    ``pytest -m baseline``: 18 tests in ``test_noun.py``,
    ``test_relationship.py`` and ``test_utils.py``. The TypeScript
    implementation's 29 Jest tests are not part of this floor
    (:need:`HMD_META_TYPES_ISSUE_010`).

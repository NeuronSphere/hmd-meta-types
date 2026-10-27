"""The golden corpus still describes this implementation.

testdata/corpus/golden holds what Python meta-types does with every case; the Go
implementation (src/go/metatypes) is tested against those files. If this test
fails, Python's behavior changed: decide whether the change is intended, then
regenerate with `make docker-corpus-golden` so Go is held to the new behavior.
"""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "testdata" / "corpus"


def _golden_module():
    spec = importlib.util.spec_from_file_location(
        "corpus_golden", ROOT / "tools" / "corpus" / "golden.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


golden = _golden_module()
CLASSES = golden.load_classes()
CASES = json.loads((CORPUS / "cases.json").read_text())


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_python_matches_golden(case):
    cls = CLASSES[case["entity"]]
    error_file = CORPUS / "golden" / f"{case['name']}.error"
    if error_file.exists():
        with pytest.raises(Exception) as exc:
            golden.run(cls, case["input"], case["include_schema"], case["encode_blobs"])
        assert golden.classify(exc.value) == error_file.read_text().strip()
    else:
        out = golden.run(
            cls, case["input"], case["include_schema"], case["encode_blobs"]
        )
        assert out == (CORPUS / "golden" / f"{case['name']}.json").read_text()

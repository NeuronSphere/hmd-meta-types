"""Generate (or check) the Python goldens of the meta-types round-trip corpus.

For every case in testdata/corpus/cases.json, Python meta-types deserializes the
raw input and serializes it again. The JSON text of the result
(``json.dumps`` defaults) is the golden: testdata/corpus/golden/<case>.json.
A case Python rejects gets testdata/corpus/golden/<case>.error, holding the
error category the Go implementation must also report.

Classes are built the way hmd-tmpl-vocabgen's python_lib template builds them:
the .hms file loaded in order as the entity definition, one property per
attribute calling _getter/_setter, and ref_from_type/ref_to_type for
relationships.

  python tools/corpus/golden.py            # write goldens
  python tools/corpus/golden.py --check D  # Python→Go→Python: re-read Go's outputs in D

Needs src/python on PYTHONPATH (the Makefile's docker-corpus-* targets set it).
"""

import json
import sys
from pathlib import Path

from hmd_meta_types import Entity, Noun, Relationship
from hmd_meta_types.entity import ValidationException

ROOT = Path(__file__).resolve().parents[2] / "testdata" / "corpus"
SCHEMAS = ROOT / "schemas"


def load_classes():
    defs = {}
    for f in sorted(SCHEMAS.rglob("*.hms")):
        d = json.loads(f.read_text())
        defs[f"{d['namespace']}.{d['name']}"] = d
    classes = {}

    def make(fqn):
        if fqn in classes:
            return classes[fqn]
        d = defs[fqn]
        base = Relationship if d["metatype"] == "relationship" else Noun
        ns = {
            "_entity_def": d,
            "entity_definition": staticmethod(lambda d=d: d),
            "get_namespace_name": staticmethod(lambda d=d: Entity.get_namespace_name(d)),
        }
        for attr in d.get("attributes", {}):
            ns[attr] = property(
                lambda self, a=attr: self._getter(a),
                lambda self, v, a=attr: self._setter(a, v),
            )
        if base is Relationship:
            ns["ref_from_type"] = staticmethod(lambda d=d: make(d["ref_from"]))
            ns["ref_to_type"] = staticmethod(lambda d=d: make(d["ref_to"]))
        cls = type("".join(p.capitalize() for p in d["name"].split("_")), (base,), ns)
        classes[fqn] = cls
        return cls

    return {fqn.split(".")[-1]: make(fqn) for fqn in defs}


def classify(ex: Exception) -> str:
    """The error category both implementations must agree on."""
    msg = str(ex)
    if isinstance(ex, KeyError):
        return "unknown_type"
    if isinstance(ex, ValidationException):
        return "validation"
    if isinstance(ex, TypeError) and "expected a value of one of the types" in msg:
        return "type"
    if isinstance(ex, TypeError) and "required positional argument" in msg:
        return "missing_ref"
    if msg.startswith("Missing required fields"):
        return "missing_required"
    if msg.startswith("Extra fields present"):
        return "extra_fields"
    if msg.startswith("Cannot set required field"):
        return "required_null"
    if "expected one of" in msg:
        return "enum"
    if msg.startswith("Invalid value for field"):
        return "schema"
    if "reference must be of type str" in msg:
        return "ref_type"
    return "decode"


def run(cls, raw: str, include_schema: bool, encode_blobs: bool):
    entity = Entity.deserialize(cls, json.loads(raw))
    return json.dumps(entity.serialize(encode_blobs=encode_blobs, include_schema=include_schema))


def main():
    classes = load_classes()
    cases = json.loads((ROOT / "cases.json").read_text())
    golden = ROOT / "golden"
    check_dir = Path(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--check" else None
    failures = checked = 0
    if check_dir is None:
        golden.mkdir(exist_ok=True)
        for old in golden.iterdir():
            old.unlink()
    for c in cases:
        cls = classes[c["entity"]]
        if check_dir is not None:
            go_out = check_dir / f"{c['name']}.json"
            want = golden / f"{c['name']}.json"
            if not want.exists() or not c["encode_blobs"]:
                continue
            checked += 1
            again = run(cls, go_out.read_text(), c["include_schema"], True)
            if again != want.read_text():
                failures += 1
                print(f"MISMATCH {c['name']}:\n  python: {want.read_text()}\n  go→py:  {again}")
            continue
        try:
            out = run(cls, c["input"], c["include_schema"], c["encode_blobs"])
        except Exception as ex:  # noqa: BLE001 -- every rejection is a recorded outcome
            (golden / f"{c['name']}.error").write_text(classify(ex) + "\n")
            continue
        (golden / f"{c['name']}.json").write_text(out)
        if c["encode_blobs"]:
            again = run(cls, out, c["include_schema"], True)
            if again != out:
                failures += 1
                print(f"NOT IDEMPOTENT {c['name']}:\n  first:  {out}\n  second: {again}")
    if check_dir is not None:
        print(f"python→go→python: {checked} Go outputs re-read by Python, {failures} mismatches")
    else:
        n_ok = len(list(golden.glob("*.json")))
        n_err = len(list(golden.glob("*.error")))
        print(f"goldens: {n_ok} serialized, {n_err} rejected, {failures} not idempotent")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

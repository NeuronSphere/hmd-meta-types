"""Write testdata/corpus/cases.json: the inputs of the meta-types round-trip corpus.

Each case is an entity name, serialize options, and the raw JSON text a service
would receive. The text is kept raw so literal forms (1E2, 1.50, big integers,
duplicate keys, key order) reach both implementations unchanged.

Run: python tools/corpus/cases.py (make docker-corpus-golden)
"""

import json
from base64 import b64encode
from pathlib import Path


def b64(text: str) -> str:
    return b64encode(text.encode("latin-1")).decode("ascii")


def b64u(text: str) -> str:
    """Base64 of UTF-8 bytes: what a non-Python client may send."""
    return b64encode(text.encode("utf-8")).decode("ascii")


TS = '"_created": "2026-10-26T10:31:09+00:00", "_updated": "2026-10-26T11:00:00.250000+00:00"'
FULL = (
    '{"identifier": "id-1", "name_text": "hello", "count": 42, "ratio": 2.5, '
    '"flag": true, "kind": "beta", "happened_at": "2026-10-26T10:31:09.123456+00:00", '
    '"seen_epoch": 1761474669, '
    f'"tags": "{b64(json.dumps([1, 2.5, "a", None, True, {"k": [1, 2]}]))}", '
    f'"props": "{b64(json.dumps({"z": 1, "a": {"y": 2.0, "b": [3]}, "m": "x"}))}", '
    '"payload": "AAEC/w==", ' + TS + "}"
)

CASES = []


def case(name, entity, raw, include_schema=False, encode_blobs=True):
    json.loads(raw)  # every input must be valid JSON for Python
    CASES.append(
        {
            "name": name,
            "entity": entity,
            "include_schema": include_schema,
            "encode_blobs": encode_blobs,
            "input": raw,
        }
    )


A, R, V, S, B, L = (
    "all_types",
    "required_types",
    "validated",
    "with_schema",
    "bad_types",
    "all_types_links_required_types",
)

# --- all_types: every type, optional -------------------------------------------
case("all_full", A, FULL)
case("all_full_include_schema", A, FULL, include_schema=True)
case("all_full_raw_blobs", A, FULL, encode_blobs=False)
case("all_empty", A, "{}")
case(
    "all_nulls",
    A,
    '{"name_text": null, "count": null, "ratio": null, "flag": null, "kind": null, '
    '"happened_at": null, "seen_epoch": null, "tags": null, "props": null, "payload": null, '
    '"identifier": null, "_created": null, "_updated": null}',
)
case(
    "all_falsy",
    A,
    '{"name_text": "", "count": 0, "ratio": 0.0, "flag": false, "seen_epoch": 0, "tags": [], "props": {}}',
)
case("all_key_order_reversed", A, '{"payload": "QUJD", "tags": "W10=", "count": 1, "name_text": "x"}')
case("all_schema_key_ignored", A, '{"__schema": "hmd_meta_corpus.all_types", "count": 1}')
case("all_duplicate_key_last_wins", A, '{"count": 1, "name_text": "a", "count": 2}')
case("all_extra_field", A, '{"count": 1, "bogus": 1}')

# integers and epochs
case("int_bool_accepted", A, '{"count": true, "seen_epoch": false}')
case("int_big", A, '{"count": 1180591620717411303424, "seen_epoch": -9223372036854775809}')
case("int_negative_zero", A, '{"count": -0}')
case("int_float_rejected", A, '{"count": 5.0}')
case("int_string_rejected", A, '{"count": "5"}')
case("epoch_float_rejected", A, '{"seen_epoch": 1.5}')

# floats
case("float_forms", A, '{"ratio": 1E2}')
case("float_trailing_zero", A, '{"ratio": 1.50}')
case("float_large", A, '{"ratio": 1e16}')
case("float_just_below_exp", A, '{"ratio": 1234567890123456.0}')
case("float_small", A, '{"ratio": 0.00001}')
case("float_small_plain", A, '{"ratio": 0.0001}')
case("float_precision", A, '{"ratio": 0.1}')
case("float_long", A, '{"ratio": 123456789.123456789}')
case("float_negative_zero", A, '{"ratio": -0.0}')
case("float_max", A, '{"ratio": 1.7976931348623157e308}')
case("float_tiny", A, '{"ratio": 5e-324}')
case("float_nan", A, '{"ratio": NaN}')
case("float_inf", A, '{"ratio": Infinity}')
case("float_neg_inf", A, '{"ratio": -Infinity}')
case("float_int_rejected", A, '{"ratio": 5}')
case("float_bool_rejected", A, '{"ratio": true}')

# bool, enum, string
case("bool_int_rejected", A, '{"flag": 1}')
case("bool_string_rejected", A, '{"flag": "true"}')
case("enum_valid", A, '{"kind": "gamma"}')
case("enum_invalid", A, '{"kind": "delta"}')
case("enum_wrong_case", A, '{"kind": "Alpha"}')
case("string_escapes", A, '{"name_text": "caf\\u00e9 \\ud83d\\ude00 \\u007f tab\\t nl\\n q\\" bs\\\\ sl/ \\u0001"}')
case("string_raw_utf8", A, '{"name_text": "naïve 日本"}')
case("string_int_rejected", A, '{"name_text": 5}')
case("identifier_int_rejected", A, '{"identifier": 5}')

# timestamps
for name, value in [
    ("ts_z", "2026-10-26T10:31:09Z"),
    ("ts_utc_offset", "2026-10-26T10:31:09+00:00"),
    ("ts_offset_fraction", "2026-10-26T10:31:09.5+05:30"),
    ("ts_negative_offset", "2026-10-26T23:59:59-0800"),
    ("ts_hour_offset", "2026-10-26T10:31:09+05"),
    ("ts_naive", "2026-10-26T10:31:09"),
    ("ts_naive_micro", "2026-10-26T10:31:09.000001"),
    ("ts_date_only", "2026-10-26"),
    ("ts_basic", "20261026T103109"),
    ("ts_space_sep", "2026-10-26 10:31:09"),
    ("ts_no_seconds", "2026-10-26T10:31"),
    ("ts_seven_digits", "2026-10-26T10:31:09.1234567"),
    ("ts_three_digits", "2026-10-26T10:31:09.123Z"),
    ("ts_year_999", "0999-01-02T03:04:05"),
    ("ts_crosses_day", "2026-12-31T23:30:00-01:00"),
    ("ts_week", "2026-W43"),
    ("ts_week_day", "2026-W43-1T08:00"),
    ("ts_week_basic", "2026W437"),
    ("ts_ordinal", "2026-299"),
    ("ts_ordinal_basic", "2026299T12"),
    ("ts_year_month", "2026-10"),
    ("ts_year_only", "2026"),
    ("ts_hour_24", "2026-10-26T24:00:00"),
    ("ts_hour_only_z", "2026-10-26T10Z"),
    ("ts_comma_fraction", "2026-10-26T10:31:09,5"),
    ("ts_basic_offset", "2026-10-26T103109+0530"),
    ("ts_neg_zero_offset", "2026-10-26T10:31:09-00:00"),
    ("ts_other_separator", "2026-10-26x10:31:09"),
    ("ts_leap_day", "2024-02-29T00:00:00"),
]:
    case(name, A, json.dumps({"happened_at": value}))
for name, value in [
    ("ts_bad_month", "2026-13-01"),
    ("ts_bad_leap_day", "2026-02-29"),
    ("ts_hour_24_minutes", "2026-10-26T24:30"),
    ("ts_bad_week", "2026-W54"),
    ("ts_bad_ordinal", "2026-366"),
    ("ts_offset_too_big", "2026-10-26T10:31:09+24:00"),
    ("ts_mixed_colons", "2026-10-26T10:3109"),
    ("ts_unicode", "2026-10-26T10:31:09\u00a0"),
    ("ts_trailing", "2026-10-26T10:31:09Zjunk"),
    ("ts_too_short_time", "2026-10-26T1"),
]:
    case(name, A, json.dumps({"happened_at": value.encode().decode("unicode_escape")}))
case("ts_empty_rejected", A, '{"happened_at": ""}')
case("ts_garbage", A, '{"happened_at": "not a date"}')
case("ts_number", A, '{"happened_at": 5}')
case("ts_created_naive", A, '{"_created": "2026-10-26T10:31:09"}')

# blobs
case("blob_canonical", A, '{"payload": "QUJD"}')
case("blob_high_bytes", A, '{"payload": "/w=="}')
case("blob_junk_chars", A, '{"payload": "QU JD!"}')
case("blob_bad_padding", A, '{"payload": "QUI"}')
case("blob_empty_rejected", A, '{"payload": ""}')
case("blob_number", A, '{"payload": 5}')

# collections and mappings
case("coll_nested", A, json.dumps({"tags": b64(json.dumps([[1, [2, [3]]], {"b": 1, "a": 2}, -0.0, 1e100, 10**25]))}))
case("coll_compact_json", A, json.dumps({"tags": b64('[1,2,{"a":1}]')}))
case("coll_literal_forms", A, json.dumps({"tags": b64("[1.50, 1E2, -0, 0.00001, NaN]")}))
case("coll_unicode_ascii_escaped", A, json.dumps({"tags": b64(json.dumps(["café", "😀"]))}))
case("coll_utf8_bytes", A, json.dumps({"tags": b64u('["café", "日本"]')}))
case("coll_duplicate_keys", A, json.dumps({"tags": b64('[{"a": 1, "b": 2, "a": 3}]')}))
case("coll_empty_raw", A, '{"tags": []}')
case("coll_empty_encoded", A, json.dumps({"tags": b64("[]")}))
case("coll_raw_nonempty", A, '{"tags": [1]}')
case("coll_is_dict", A, json.dumps({"tags": b64('{"a": 1}')}))
case("coll_bad_json", A, json.dumps({"tags": b64("[1, ")}))
case("map_ordered", A, json.dumps({"props": b64('{"z": 1, "a": 2, "m": {"y": null, "b": true}}')}))
case("map_empty_raw", A, '{"props": {}}')
case("map_raw_nonempty", A, '{"props": {"a": 1}}')
case("map_is_list", A, json.dumps({"props": b64("[1]")}))
case("map_utf8_bytes", A, json.dumps({"props": b64u('{"k": "ü"}')}))

# --- required_types ----------------------------------------------------------------
REQ = (
    '{"payload": "QUJD", "props": "e30=", "tags": "W10=", "seen_epoch": 1, '
    '"happened_at": "2026-10-26T10:31:09+00:00", "kind": "alpha", "flag": false, '
    '"ratio": 0.5, "count": 0, "name_text": ""}'
)
case("req_complete", R, REQ)
case("req_complete_include_schema", R, REQ, include_schema=True)
case("req_missing_one", R, REQ.replace('"name_text": ""', '"identifier": "x"'))
case("req_missing_and_extra", R, REQ.replace('"name_text": ""', '"bogus": 1'))
case("req_null", R, REQ.replace('"name_text": ""', '"name_text": null'))
case("req_null_internal_ok", R, REQ.replace('"name_text": ""', '"name_text": "n", "identifier": null'))

# --- validated -----------------------------------------------------------------------
case(
    "val_all_ok",
    V,
    '{"code": "ABC-123", "iso_date": "2026-10-26", "stamp_text": "2026-10-26T10:31:09.123456+0000", '
    '"score": 100, "weight": 9.5}',
)
case("val_regex_prefix_match", V, '{"code": "ABC-12x"}')
case("val_regex_fail", V, '{"code": "abc-123"}')
case("val_date_bad_day", V, '{"iso_date": "2026-02-30"}')
case("val_date_bad_format", V, '{"iso_date": "26-10-2026"}')
case("val_date_trailing", V, '{"iso_date": "2026-10-26T00:00"}')
case("val_date_unpadded", V, '{"iso_date": "2026-1-5"}')
case("val_stamp_bad_offset", V, '{"stamp_text": "2026-10-26T10:31:09.1+25:00"}')
case("val_score_min_edge", V, '{"score": 0}')
case("val_score_over", V, '{"score": 101}')
case("val_score_under", V, '{"score": -1}')
case("val_score_bool", V, '{"score": true}')
case("val_weight_min_edge", V, '{"weight": 0.5}')
case("val_weight_under", V, '{"weight": 0.4}')
case("val_weight_nan", V, '{"weight": NaN}')

# --- validated_formats ----------------------------------------------------------------
F = "validated_formats"
case(
    "fmt_all_ok",
    F,
    json.dumps(
        {
            "day_month": "26 Oct 2026",
            "full_month": "OCTOBER 26, 2026",
            "clock_12h": "12:30 am",
            "ordinal": "2026-299",
            "short_year": "261026",
            "leap_no_year": "02-28",
            "spaced": "2026   10  26",
            "both_rules": "2026-10-26",
        }
    ),
)
for name, field, value in [
    ("fmt_leap_no_year", "leap_no_year", "02-29"),
    ("fmt_bad_month_name", "day_month", "26 Okt 2026"),
    ("fmt_bad_clock", "clock_12h", "13:30 PM"),
    ("fmt_day_366_nonleap", "ordinal", "2026-366"),
    ("fmt_day_366_leap", "ordinal", "2024-366"),
    ("fmt_short_year_69", "short_year", "690101"),
    ("fmt_unpadded_day", "day_month", "5 Oct 2026"),
    ("fmt_space_padded_day", "day_month", " 5 Oct 2026"),
    ("fmt_regex_ok_date_bad", "both_rules", "2026-13-01"),
    ("fmt_regex_bad_date_ok", "both_rules", "2025-10-26"),
]:
    case(name, F, json.dumps({field: value}))

# --- with_schema ------------------------------------------------------------------------
case(
    "schema_ok",
    S,
    json.dumps(
        {
            "items": b64(json.dumps([{"name": "a", "n": 1}, {"name": "b"}])),
            "config": b64(json.dumps({"mode": "a", "limits": {"max": 2.5}})),
        }
    ),
)
case("schema_item_missing_name", S, json.dumps({"items": b64(json.dumps([{"n": 1}]))}))
case("schema_item_wrong_type", S, json.dumps({"items": b64(json.dumps([{"name": "a", "n": 1.5}]))}))
case("schema_config_extra", S, json.dumps({"config": b64(json.dumps({"mode": "a", "x": 1}))}))
case("schema_config_bad_enum", S, json.dumps({"config": b64(json.dumps({"mode": "c"}))}))
case("schema_config_negative", S, json.dumps({"config": b64(json.dumps({"mode": "b", "limits": {"max": -1}}))}))
case("schema_empty_raw_skips", S, '{"items": [], "config": {}}')

# --- bad_types --------------------------------------------------------------------------
case("bad_label_only", B, '{"label": "x"}')
case("bad_int_type", B, '{"x_pos": 1}')
case("bad_boolean_type", B, '{"active": true}')
case("bad_null_skips_type", B, '{"x_pos": null, "active": null}')

# --- relationship -----------------------------------------------------------------------
REL = (
    '{"ref_from": "hmd_meta_corpus.all_types/a1", "note": "n", "strength": 0.75, '
    '"since": "2026-10-26T10:31:09Z", "ref_to": "hmd_meta_corpus.required_types/r1", "identifier": "rel-1"}'
)
case("rel_full", L, REL)
case("rel_full_include_schema", L, REL, include_schema=True)
case("rel_minimal", L, '{"ref_to": "t", "ref_from": "f", "note": ""}')
case("rel_missing_ref_to", L, '{"ref_from": "f", "note": "n"}')
case("rel_ref_not_string", L, '{"ref_from": 5, "ref_to": "t", "note": "n"}')
case("rel_missing_required", L, '{"ref_from": "f", "ref_to": "t"}')
case("rel_ref_null", L, '{"ref_from": null, "ref_to": "t", "note": "n"}')


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "testdata" / "corpus" / "cases.json"
    out.write_text(json.dumps(CASES, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out}: {len(CASES)} cases")

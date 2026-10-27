package metatypes

import (
	"testing"
	"time"
)

// TestStrptimeDirectives covers the directive table and the checks after a match.
//
// Requirements: REQ_SET_004
func TestStrptimeDirectives(t *testing.T) {
	ok := []struct{ v, f string }{
		{"2026-10-26", "%Y-%m-%d"},
		{"2026-1-5", "%Y-%m-%d"},
		{"26 oct 2026", "%d %b %Y"},
		{"Monday, 26 October 2026", "%A, %d %B %Y"},
		{"12:00 PM", "%I:%M %p"},
		{"2026-10-26T10:31:09.5+05:30", "%Y-%m-%dT%H:%M:%S.%f%z"},
		{"2026-10-26T10:31:09Z", "%Y-%m-%dT%H:%M:%S%z"},
		{"100%", "100%%"},
		{"2026.10", "%Y.%m"},
	}
	for _, c := range ok {
		if err := strptime(c.v, c.f); err != nil {
			t.Errorf("strptime(%q, %q) = %v", c.v, c.f, err)
		}
	}
	bad := []struct{ v, f string }{
		{"2026-02-29", "%Y-%m-%d"},
		{"02-29", "%m-%d"},
		{"2026-10-26 ", "%Y-%m-%d"},
		{"2026x10", "%Y.%m"},
		{"10:31:61", "%H:%M:%S"},
		{"2026", "%Y%"},
		{"2026", "%Q"},
	}
	for _, c := range bad {
		if err := strptime(c.v, c.f); err == nil {
			t.Errorf("strptime(%q, %q) succeeded, want an error", c.v, c.f)
		}
	}
}

// TestUnsupportedStrptimeDirectives pins the documented difference: directives
// Python accepts but the port does not implement are rejected, not ignored.
//
// Requirements: REQ_DIFF_002
func TestUnsupportedStrptimeDirectives(t *testing.T) {
	for _, f := range []string{"%U", "%W", "%w", "%u", "%G", "%V", "%c", "%x", "%X", "%Z"} {
		err := strptime("x", f)
		if _, ok := err.(errUnsupportedDirective); !ok {
			t.Errorf("strptime with %s = %v, want errUnsupportedDirective", f, err)
		}
	}
}

// TestRegexIsRE2 pins the documented difference: patterns use Go's RE2 syntax.
// Python-only constructs such as lookahead fail validation instead of matching.
//
// Requirements: REQ_DIFF_001
func TestRegexIsRE2(t *testing.T) {
	if _, err := pyRegexp(`(?=A)A`); err == nil {
		t.Fatal("lookahead compiled; RE2 should reject it")
	}
	re, err := pyRegexp(`[A-Z]{3}-\d+`)
	if err != nil {
		t.Fatal(err)
	}
	if !re.MatchString("ABC-12x") || re.MatchString("xABC-12") {
		t.Fatal("re.match semantics: anchored at the start, not the end")
	}
}

// TestSetTruncatesToMicroseconds pins the documented difference for values set
// from Go: time.Time has nanoseconds, Python's datetime has microseconds.
//
// Requirements: REQ_DIFF_003, REQ_SER_002
func TestSetTruncatesToMicroseconds(t *testing.T) {
	ts := NewTimestamp(time.Date(2026, 10, 26, 10, 31, 9, 123456789, time.UTC))
	if got := ts.ISOFormat(); got != "2026-10-26T10:31:09.123456+00:00" {
		t.Fatalf("ISOFormat() = %s", got)
	}
	naive := NaiveTimestamp(time.Date(999, 1, 2, 3, 4, 5, 0, time.FixedZone("", 3600)))
	if got := naive.ISOFormat(); got != "0999-01-02T03:04:05" {
		t.Fatalf("naive ISOFormat() = %s", got)
	}
	d := MustLoadDefinition([]byte(`{"name": "t", "metatype": "noun", "attributes": {"at": {"type": "timestamp"}}}`))
	e := NewNoun(d)
	if err := e.SetAttr("at", NewTimestamp(time.Date(10000, 1, 1, 0, 0, 0, 0, time.UTC))); CategoryOf(err) != CatType {
		t.Fatalf("year 10000 = %v, want a type error (Python's datetime stops at 9999)", err)
	}
}

// TestPyB64Decode covers binascii.a2b_base64's non-strict mode.
//
// Requirements: REQ_DES_003
func TestPyB64Decode(t *testing.T) {
	ok := map[string]string{
		"QUJD":       "ABC",
		"QU JD!":     "ABC",
		"QUI=":       "AB",
		"QQ==":       "A",
		"QQ==QUJD":   "A",
		"QQ=x=":      "A\x0c", // CPython: only a complete pad sequence stops decoding
		"":           "",
		"\nQ\nUJD\n": "ABC",
	}
	for in, want := range ok {
		got, err := pyB64Decode(in)
		if err != nil || string(got) != want {
			t.Errorf("pyB64Decode(%q) = %q, %v; want %q", in, got, err, want)
		}
	}
	for _, in := range []string{"QUI", "Q", "QUJDQ", "Q===", "\xc3\xa9"} {
		if got, err := pyB64Decode(in); err == nil {
			t.Errorf("pyB64Decode(%q) = %q, want an error", in, got)
		}
	}
}

// TestDefinitionLoading checks order, required truthiness and the internal
// attribute merge.
//
// Requirements: REQ_DEF_001, REQ_DEF_002
func TestDefinitionLoading(t *testing.T) {
	d, err := LoadDefinition([]byte(`{"name": "rel", "namespace": "a.b", "metatype": "relationship",
		"ref_from": "a.b.x", "ref_to": "a.b.y",
		"attributes": {"z": {"type": "string", "required": "yes"}, "a": {"type": "integer", "required": 0},
		"identifier": {"type": "integer"}}}`))
	if err != nil {
		t.Fatal(err)
	}
	var names []string
	for _, a := range d.merged {
		names = append(names, a.Name)
	}
	if got := len(names); got != 5 || names[0] != "z" || names[1] != "a" || names[2] != "identifier" || names[3] != "_updated" {
		t.Fatalf("merged order = %v", names)
	}
	if !d.Attributes[0].Required || d.Attributes[1].Required {
		t.Fatal("required follows Python truthiness")
	}
	if d.merged[2].Type != "string" {
		t.Fatal("attributes | internal_attributes: the internal definition wins for serialize")
	}
	if d.lookup("identifier").Type != "integer" {
		t.Fatal("_setter looks up declared attributes first")
	}
	if d.FullName() != "a.b.rel" || !d.IsRelationship() || d.RefFromType != "a.b.x" {
		t.Fatalf("definition fields: %+v", d)
	}
	for _, bad := range []string{`[]`, `{"attributes": {}}`, `{`} {
		if _, err := LoadDefinition([]byte(bad)); err == nil {
			t.Errorf("LoadDefinition(%s) succeeded", bad)
		}
	}
}

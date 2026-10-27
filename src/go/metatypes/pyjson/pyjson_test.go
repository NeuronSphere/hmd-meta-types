package pyjson

import (
	"math"
	"testing"
)

// TestFloatReprMatchesPython checks repr(float) for the boundaries of fixed and
// scientific notation. Expected strings are CPython 3.11's repr.
//
// Requirements: REQ_SER_006
func TestFloatReprMatchesPython(t *testing.T) {
	cases := []struct {
		f    float64
		want string
	}{
		{0, "0.0"},
		{math.Copysign(0, -1), "-0.0"},
		{1, "1.0"},
		{100, "100.0"},
		{2.5, "2.5"},
		{0.1, "0.1"},
		{0.0001, "0.0001"},
		{0.00001, "1e-05"},
		{1.5e-05, "1.5e-05"},
		{1234567890123456, "1234567890123456.0"},
		{1e16, "1e+16"},
		{1.5e16, "1.5e+16"},
		{1e100, "1e+100"},
		{123456789.123456789, "123456789.12345679"},
		{5e-324, "5e-324"},
		{math.MaxFloat64, "1.7976931348623157e+308"},
		{-2.75, "-2.75"},
		{math.NaN(), "NaN"},
		{math.Inf(1), "Infinity"},
		{math.Inf(-1), "-Infinity"},
	}
	for _, c := range cases {
		if got := FloatRepr(c.f); got != c.want {
			t.Errorf("FloatRepr(%v) = %s, want %s", c.f, got, c.want)
		}
	}
}

// TestParseDumpsMatchesPython checks json.loads followed by json.dumps. Expected
// strings are what CPython 3.11 prints for the same input.
//
// Requirements: REQ_SER_006, REQ_DES_001
func TestParseDumpsMatchesPython(t *testing.T) {
	cases := []struct{ in, want string }{
		{`{"b":1,"a":[1.50,1E2,-0,true,null]}`, `{"b": 1, "a": [1.5, 100.0, 0, true, null]}`},
		{`{"a":1,"b":2,"a":3}`, `{"a": 3, "b": 2}`},
		{`[1e400, -1e400, 1e-400]`, `[Infinity, -Infinity, 0.0]`},
		{`123456789012345678901234567890`, `123456789012345678901234567890`},
		{"\"caf\x5cu00e9 \x5cud83d\x5cude00 \x5cu007f \x5ct\"", "\"caf\x5cu00e9 \x5cud83d\x5cude00 \x5cu007f \x5ct\""},
		{"\"lone \x5cud800 surrogate\"", "\"lone \x5cud800 surrogate\""},
		{"\"na\xc3\xafve\"", "\"na\x5cu00efve\""},
		{` [ ] `, `[]`},
		{`{}`, `{}`},
		{`[NaN, Infinity, -Infinity]`, `[NaN, Infinity, -Infinity]`},
		{`"\/"`, `"/"`},
	}
	for _, c := range cases {
		v, err := Parse(c.in)
		if err != nil {
			t.Errorf("Parse(%s): %v", c.in, err)
			continue
		}
		if got := Dumps(v); got != c.want {
			t.Errorf("Dumps(Parse(%s)) = %s, want %s", c.in, got, c.want)
		}
	}
}

// TestParseRejectsWhatPythonRejects checks inputs json.loads refuses.
//
// Requirements: REQ_DES_001
func TestParseRejectsWhatPythonRejects(t *testing.T) {
	for _, in := range []string{``, `01`, `1.`, `1e`, `[1,]`, `{"a" 1}`, `{a: 1}`, "\"tab\there\"", `"\x"`, `nul`, `[1] x`, `+1`} {
		if v, err := Parse(in); err == nil {
			t.Errorf("Parse(%q) = %s, want an error", in, Dumps(v))
		}
	}
}

// TestEqualAndCompareFollowPython checks ==, < and > between JSON values.
//
// Requirements: REQ_SET_003, REQ_SET_004
func TestEqualAndCompareFollowPython(t *testing.T) {
	one, _ := Parse(`1`)
	oneF, _ := Parse(`1.0`)
	tru, _ := Parse(`true`)
	nan, _ := Parse(`NaN`)
	objA, _ := Parse(`{"a": 1, "b": [1, 2]}`)
	objB, _ := Parse(`{"b": [1, 2.0], "a": true}`)
	if !Equal(one, oneF) || !Equal(one, tru) || Equal(nan, nan) || !Equal(objA, objB) {
		t.Fatal("Equal does not follow Python's ==")
	}
	if c, ok := Compare(one, FloatValue(0.5)); !ok || c != 1 {
		t.Fatalf("Compare(1, 0.5) = %d, %v", c, ok)
	}
	if _, ok := Compare(nan, one); ok {
		t.Fatal("comparisons with NaN must report not-ok, as Python's are all False")
	}
	big1, _ := Parse(`9007199254740993`)
	if c, _ := Compare(big1, FloatValue(9007199254740992)); c != 1 {
		t.Fatal("int/float comparison must be exact, as in Python")
	}
}

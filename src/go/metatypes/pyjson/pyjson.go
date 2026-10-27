// Package pyjson reads and writes JSON exactly the way Python's json module does
// with its defaults, so Go output can be byte-identical to Python output.
//
// That means: objects keep key order (a repeated key keeps its first position and
// takes its last value), integers have arbitrary precision, floats print as Python's
// repr (1e+16, 1e-05, 100.0), NaN and Infinity are accepted and written, strings are
// written with ensure_ascii escaping, and separators are ", " and ": ".
//
// Strings may hold lone UTF-16 surrogates (Python allows them); they are kept as
// WTF-8 byte sequences so they survive a round trip.
package pyjson

import (
	"fmt"
	"math"
	"math/big"
	"strconv"
	"strings"
	"unicode/utf8"
)

// Kind is the JSON type of a Value.
type Kind uint8

const (
	Null Kind = iota
	Bool
	Number
	String
	Array
	Object
)

func (k Kind) String() string {
	return [...]string{"null", "bool", "number", "string", "array", "object"}[k]
}

// Num is a JSON number the way Python holds it after json.loads: an int of any
// size, or a float.
type Num struct {
	IsFloat bool
	Int     *big.Int // when !IsFloat
	Float   float64  // when IsFloat
}

// Member is one key and value of an Object, in order.
type Member struct {
	Key   string
	Value Value
}

// Value is a JSON value. The zero Value is null.
type Value struct {
	kind Kind
	b    bool
	num  Num
	s    string
	arr  []Value
	obj  []Member
}

func NullValue() Value              { return Value{} }
func BoolValue(b bool) Value        { return Value{kind: Bool, b: b} }
func StringValue(s string) Value    { return Value{kind: String, s: s} }
func FloatValue(f float64) Value    { return Value{kind: Number, num: Num{IsFloat: true, Float: f}} }
func IntValue(i *big.Int) Value     { return Value{kind: Number, num: Num{Int: new(big.Int).Set(i)}} }
func Int64Value(i int64) Value      { return Value{kind: Number, num: Num{Int: big.NewInt(i)}} }
func ArrayValue(vs []Value) Value   { return Value{kind: Array, arr: vs} }
func ObjectValue(ms []Member) Value { return Value{kind: Object, obj: ms} }

func (v Value) Kind() Kind        { return v.kind }
func (v Value) IsNull() bool      { return v.kind == Null }
func (v Value) Bool() bool        { return v.b }
func (v Value) Num() Num          { return v.num }
func (v Value) Str() string       { return v.s }
func (v Value) Array() []Value    { return v.arr }
func (v Value) Members() []Member { return v.obj }

// Get returns the value of key in an Object.
func (v Value) Get(key string) (Value, bool) {
	for _, m := range v.obj {
		if m.Key == key {
			return m.Value, true
		}
	}
	return Value{}, false
}

// Truthy is Python's bool(): false for null, False, 0, 0.0, "", [] and {}.
func (v Value) Truthy() bool {
	switch v.kind {
	case Bool:
		return v.b
	case Number:
		if v.num.IsFloat {
			return v.num.Float != 0 // NaN is truthy, as in Python
		}
		return v.num.Int.Sign() != 0
	case String:
		return v.s != ""
	case Array:
		return len(v.arr) > 0
	case Object:
		return len(v.obj) > 0
	}
	return false
}

// Equal is Python's ==: numbers and booleans compare by value (1 == 1.0 == True),
// objects ignore key order, NaN is never equal.
func Equal(a, b Value) bool {
	if isNumeric(a) && isNumeric(b) {
		ra, oka := a.rat()
		rb, okb := b.rat()
		if !oka || !okb {
			// NaN never equals; infinities equal themselves.
			return a.kind == Number && b.kind == Number && a.num.IsFloat && b.num.IsFloat &&
				!math.IsNaN(a.num.Float) && a.num.Float == b.num.Float
		}
		return ra.Cmp(rb) == 0
	}
	if a.kind != b.kind {
		return false
	}
	switch a.kind {
	case Null:
		return true
	case String:
		return a.s == b.s
	case Array:
		if len(a.arr) != len(b.arr) {
			return false
		}
		for i := range a.arr {
			if !Equal(a.arr[i], b.arr[i]) {
				return false
			}
		}
		return true
	case Object:
		if len(a.obj) != len(b.obj) {
			return false
		}
		for _, m := range a.obj {
			bv, ok := b.Get(m.Key)
			if !ok || !Equal(m.Value, bv) {
				return false
			}
		}
		return true
	}
	return false
}

func isNumeric(v Value) bool { return v.kind == Number || v.kind == Bool }

// rat is the exact value of a number or bool; false for NaN and infinities.
func (v Value) rat() (*big.Rat, bool) {
	if v.kind == Bool {
		if v.b {
			return big.NewRat(1, 1), true
		}
		return new(big.Rat), true
	}
	if !v.num.IsFloat {
		return new(big.Rat).SetInt(v.num.Int), true
	}
	if math.IsNaN(v.num.Float) || math.IsInf(v.num.Float, 0) {
		return nil, false
	}
	return new(big.Rat).SetFloat64(v.num.Float), true
}

// Compare compares two numeric values (numbers or bools) the way Python's < and >
// do. ok is false when either side is not numeric or is NaN, in which case Python's
// comparisons are all False.
func Compare(a, b Value) (cmp int, ok bool) {
	if !isNumeric(a) || !isNumeric(b) {
		return 0, false
	}
	af, bf := a.float(), b.float()
	if math.IsNaN(af) || math.IsNaN(bf) {
		return 0, false
	}
	if math.IsInf(af, 0) || math.IsInf(bf, 0) {
		switch {
		case af < bf:
			return -1, true
		case af > bf:
			return 1, true
		}
		return 0, true
	}
	ra, _ := a.rat()
	rb, _ := b.rat()
	return ra.Cmp(rb), true
}

func (v Value) float() float64 {
	if v.kind == Bool {
		if v.b {
			return 1
		}
		return 0
	}
	if v.num.IsFloat {
		return v.num.Float
	}
	f, _ := new(big.Float).SetInt(v.num.Int).Float64()
	return f
}

// SyntaxError is a json.loads failure.
type SyntaxError struct {
	Msg string
	Pos int
}

func (e *SyntaxError) Error() string { return fmt.Sprintf("%s: char %d", e.Msg, e.Pos) }

// Parse is json.loads(text) with Python's defaults (strict=True).
func Parse(text string) (Value, error) {
	p := &parser{s: text}
	p.ws()
	v, err := p.value()
	if err != nil {
		return Value{}, err
	}
	p.ws()
	if p.i != len(p.s) {
		return Value{}, p.err("Extra data")
	}
	return v, nil
}

type parser struct {
	s string
	i int
}

func (p *parser) err(msg string) error { return &SyntaxError{Msg: msg, Pos: p.i} }

func (p *parser) ws() {
	for p.i < len(p.s) {
		switch p.s[p.i] {
		case ' ', '\t', '\n', '\r':
			p.i++
		default:
			return
		}
	}
}

func (p *parser) value() (Value, error) {
	if p.i >= len(p.s) {
		return Value{}, p.err("Expecting value")
	}
	switch c := p.s[p.i]; {
	case c == '{':
		return p.object()
	case c == '[':
		return p.array()
	case c == '"':
		s, err := p.str()
		return StringValue(s), err
	case strings.HasPrefix(p.s[p.i:], "null"):
		p.i += 4
		return NullValue(), nil
	case strings.HasPrefix(p.s[p.i:], "true"):
		p.i += 4
		return BoolValue(true), nil
	case strings.HasPrefix(p.s[p.i:], "false"):
		p.i += 5
		return BoolValue(false), nil
	case strings.HasPrefix(p.s[p.i:], "NaN"):
		p.i += 3
		return FloatValue(math.NaN()), nil
	case strings.HasPrefix(p.s[p.i:], "Infinity"):
		p.i += 8
		return FloatValue(math.Inf(1)), nil
	case strings.HasPrefix(p.s[p.i:], "-Infinity"):
		p.i += 9
		return FloatValue(math.Inf(-1)), nil
	case c == '-' || (c >= '0' && c <= '9'):
		return p.number()
	}
	return Value{}, p.err("Expecting value")
}

// number matches Python's NUMBER_RE: (-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?
func (p *parser) number() (Value, error) {
	start := p.i
	if p.s[p.i] == '-' {
		p.i++
	}
	digits := func() int {
		n := 0
		for p.i < len(p.s) && p.s[p.i] >= '0' && p.s[p.i] <= '9' {
			p.i++
			n++
		}
		return n
	}
	if p.i < len(p.s) && p.s[p.i] == '0' {
		p.i++
	} else if digits() == 0 {
		p.i = start
		return Value{}, p.err("Expecting value")
	}
	isFloat := false
	if p.i+1 < len(p.s) && p.s[p.i] == '.' && p.s[p.i+1] >= '0' && p.s[p.i+1] <= '9' {
		p.i++
		digits()
		isFloat = true
	}
	if p.i < len(p.s) && (p.s[p.i] == 'e' || p.s[p.i] == 'E') {
		save := p.i
		p.i++
		if p.i < len(p.s) && (p.s[p.i] == '+' || p.s[p.i] == '-') {
			p.i++
		}
		if digits() == 0 {
			p.i = save
		} else {
			isFloat = true
		}
	}
	lit := p.s[start:p.i]
	if isFloat {
		f, err := strconv.ParseFloat(lit, 64)
		if err != nil && !isRangeErr(err) {
			return Value{}, p.err("Invalid number")
		}
		return FloatValue(f), nil
	}
	n, ok := new(big.Int).SetString(lit, 10)
	if !ok {
		return Value{}, p.err("Invalid number")
	}
	return Value{kind: Number, num: Num{Int: n}}, nil
}

// Python's float() rounds out-of-range literals to infinity or zero rather than failing.
func isRangeErr(err error) bool {
	ne, ok := err.(*strconv.NumError)
	return ok && ne.Err == strconv.ErrRange
}

func (p *parser) array() (Value, error) {
	p.i++ // [
	vals := []Value{}
	p.ws()
	if p.i < len(p.s) && p.s[p.i] == ']' {
		p.i++
		return ArrayValue(vals), nil
	}
	for {
		p.ws()
		v, err := p.value()
		if err != nil {
			return Value{}, err
		}
		vals = append(vals, v)
		p.ws()
		if p.i >= len(p.s) {
			return Value{}, p.err("Expecting ',' delimiter")
		}
		switch p.s[p.i] {
		case ',':
			p.i++
		case ']':
			p.i++
			return ArrayValue(vals), nil
		default:
			return Value{}, p.err("Expecting ',' delimiter")
		}
	}
}

func (p *parser) object() (Value, error) {
	p.i++ // {
	members := []Member{}
	index := map[string]int{}
	p.ws()
	if p.i < len(p.s) && p.s[p.i] == '}' {
		p.i++
		return ObjectValue(members), nil
	}
	for {
		p.ws()
		if p.i >= len(p.s) || p.s[p.i] != '"' {
			return Value{}, p.err("Expecting property name enclosed in double quotes")
		}
		key, err := p.str()
		if err != nil {
			return Value{}, err
		}
		p.ws()
		if p.i >= len(p.s) || p.s[p.i] != ':' {
			return Value{}, p.err("Expecting ':' delimiter")
		}
		p.i++
		p.ws()
		v, err := p.value()
		if err != nil {
			return Value{}, err
		}
		// dict(pairs): a repeated key keeps its first position and takes the last value.
		if at, seen := index[key]; seen {
			members[at].Value = v
		} else {
			index[key] = len(members)
			members = append(members, Member{Key: key, Value: v})
		}
		p.ws()
		if p.i >= len(p.s) {
			return Value{}, p.err("Expecting ',' delimiter")
		}
		switch p.s[p.i] {
		case ',':
			p.i++
		case '}':
			p.i++
			return ObjectValue(members), nil
		default:
			return Value{}, p.err("Expecting ',' delimiter")
		}
	}
}

func (p *parser) str() (string, error) {
	p.i++ // opening quote
	var b strings.Builder
	for {
		if p.i >= len(p.s) {
			return "", p.err("Unterminated string starting at")
		}
		c := p.s[p.i]
		switch {
		case c == '"':
			p.i++
			return b.String(), nil
		case c == '\\':
			p.i++
			if p.i >= len(p.s) {
				return "", p.err("Unterminated string starting at")
			}
			esc := p.s[p.i]
			p.i++
			switch esc {
			case '"', '\\', '/':
				b.WriteByte(esc)
			case 'b':
				b.WriteByte('\b')
			case 'f':
				b.WriteByte('\f')
			case 'n':
				b.WriteByte('\n')
			case 'r':
				b.WriteByte('\r')
			case 't':
				b.WriteByte('\t')
			case 'u':
				r, err := p.hex4()
				if err != nil {
					return "", err
				}
				if r >= 0xd800 && r <= 0xdbff && strings.HasPrefix(p.s[p.i:], `\u`) {
					save := p.i
					p.i += 2
					lo, err := p.hex4()
					if err == nil && lo >= 0xdc00 && lo <= 0xdfff {
						r = 0x10000 + (r-0xd800)<<10 + (lo - 0xdc00)
					} else {
						p.i = save
					}
				}
				writeWTF8(&b, r)
			default:
				return "", p.err("Invalid \\escape")
			}
		case c < 0x20:
			return "", p.err("Invalid control character at")
		default:
			b.WriteByte(c)
			p.i++
		}
	}
}

func (p *parser) hex4() (rune, error) {
	if p.i+4 > len(p.s) {
		return 0, p.err("Invalid \\uXXXX escape")
	}
	n, err := strconv.ParseUint(p.s[p.i:p.i+4], 16, 32)
	if err != nil {
		return 0, p.err("Invalid \\uXXXX escape")
	}
	p.i += 4
	return rune(n), nil
}

// writeWTF8 writes r as UTF-8, or as the generalized 3-byte encoding when r is a
// lone surrogate (which utf8 refuses to encode).
func writeWTF8(b *strings.Builder, r rune) {
	if r >= 0xd800 && r <= 0xdfff {
		b.WriteByte(byte(0xe0 | r>>12))
		b.WriteByte(byte(0x80 | (r>>6)&0x3f))
		b.WriteByte(byte(0x80 | r&0x3f))
		return
	}
	b.WriteRune(r)
}

// decodeWTF8 is utf8.DecodeRuneInString that also decodes lone surrogates.
// Bytes that are not valid either way decode as themselves (as Latin-1).
func decodeWTF8(s string) (rune, int) {
	r, n := utf8.DecodeRuneInString(s)
	if r != utf8.RuneError || n > 1 {
		return r, n
	}
	if len(s) >= 3 && s[0] == 0xed && s[1]&0xc0 == 0x80 && s[2]&0xc0 == 0x80 {
		return rune(s[0]&0x0f)<<12 | rune(s[1]&0x3f)<<6 | rune(s[2]&0x3f), 3
	}
	if len(s) > 0 {
		return rune(s[0]), 1
	}
	return utf8.RuneError, 0
}

// Dumps is json.dumps(v) with Python's defaults.
func Dumps(v Value) string {
	var b strings.Builder
	write(&b, v)
	return b.String()
}

func write(b *strings.Builder, v Value) {
	switch v.kind {
	case Null:
		b.WriteString("null")
	case Bool:
		if v.b {
			b.WriteString("true")
		} else {
			b.WriteString("false")
		}
	case Number:
		if v.num.IsFloat {
			b.WriteString(FloatRepr(v.num.Float))
		} else {
			b.WriteString(v.num.Int.String())
		}
	case String:
		WriteString(b, v.s)
	case Array:
		b.WriteByte('[')
		for i, e := range v.arr {
			if i > 0 {
				b.WriteString(", ")
			}
			write(b, e)
		}
		b.WriteByte(']')
	case Object:
		b.WriteByte('{')
		for i, m := range v.obj {
			if i > 0 {
				b.WriteString(", ")
			}
			WriteString(b, m.Key)
			b.WriteString(": ")
			write(b, m.Value)
		}
		b.WriteByte('}')
	}
}

// WriteString writes s as a JSON string with Python's ensure_ascii escaping:
// everything outside ' '..'~' is escaped, non-BMP characters as surrogate pairs.
func WriteString(b *strings.Builder, s string) {
	const hex = "0123456789abcdef"
	u4 := func(r rune) {
		b.WriteString(`\u`)
		b.WriteByte(hex[r>>12&0xf])
		b.WriteByte(hex[r>>8&0xf])
		b.WriteByte(hex[r>>4&0xf])
		b.WriteByte(hex[r&0xf])
	}
	b.WriteByte('"')
	for i := 0; i < len(s); {
		r, n := decodeWTF8(s[i:])
		i += n
		switch {
		case r == '\\':
			b.WriteString(`\\`)
		case r == '"':
			b.WriteString(`\"`)
		case r == '\n':
			b.WriteString(`\n`)
		case r == '\r':
			b.WriteString(`\r`)
		case r == '\t':
			b.WriteString(`\t`)
		case r == '\b':
			b.WriteString(`\b`)
		case r == '\f':
			b.WriteString(`\f`)
		case r >= 0x20 && r <= 0x7e:
			b.WriteRune(r)
		case r >= 0x10000:
			r -= 0x10000
			u4(0xd800 | (r>>10)&0x3ff)
			u4(0xdc00 | r&0x3ff)
		default:
			u4(r)
		}
	}
	b.WriteByte('"')
}

// FloatRepr is Python's repr(float): the shortest round-tripping digits, in fixed
// notation for exponents -4..15 (always with a fractional part) and scientific
// otherwise (1e+16, 1.5e-05).
func FloatRepr(f float64) string {
	switch {
	case math.IsNaN(f):
		return "NaN"
	case math.IsInf(f, 1):
		return "Infinity"
	case math.IsInf(f, -1):
		return "-Infinity"
	case f == 0:
		if math.Signbit(f) {
			return "-0.0"
		}
		return "0.0"
	}
	s := strconv.FormatFloat(f, 'e', -1, 64) // e.g. -1.2345e+06
	sign := ""
	if s[0] == '-' {
		sign, s = "-", s[1:]
	}
	epos := strings.IndexByte(s, 'e')
	mant, expStr := s[:epos], s[epos+1:]
	exp, _ := strconv.Atoi(expStr)
	digits := strings.Replace(mant, ".", "", 1)
	switch {
	case exp < -4 || exp >= 16:
		out := digits[:1]
		if len(digits) > 1 {
			out += "." + digits[1:]
		}
		es := "+"
		if exp < 0 {
			es, exp = "-", -exp
		}
		return fmt.Sprintf("%s%se%s%02d", sign, out, es, exp)
	case exp >= 0:
		if len(digits) <= exp+1 {
			return sign + digits + strings.Repeat("0", exp+1-len(digits)) + ".0"
		}
		return sign + digits[:exp+1] + "." + digits[exp+1:]
	default:
		return sign + "0." + strings.Repeat("0", -exp-1) + digits
	}
}

// ToAny converts v to plain Go values for libraries that take decoded JSON:
// map[string]any (key order lost), []any, string, bool, nil, *big.Int-backed
// json-like numbers as float64 or int64 where exact.
func ToAny(v Value) any {
	switch v.kind {
	case Bool:
		return v.b
	case Number:
		if v.num.IsFloat {
			return v.num.Float
		}
		if v.num.Int.IsInt64() {
			return v.num.Int.Int64()
		}
		f, _ := new(big.Float).SetInt(v.num.Int).Float64()
		return f
	case String:
		return v.s
	case Array:
		out := make([]any, len(v.arr))
		for i, e := range v.arr {
			out[i] = ToAny(e)
		}
		return out
	case Object:
		out := make(map[string]any, len(v.obj))
		for _, m := range v.obj {
			out[m.Key] = ToAny(m.Value)
		}
		return out
	}
	return nil
}

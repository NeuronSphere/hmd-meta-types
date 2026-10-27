package metatypes

import (
	"errors"
	"strings"
)

const b64Alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

var b64Table = func() [256]byte {
	var t [256]byte
	for i := range t {
		t[i] = 0xff
	}
	for i := 0; i < len(b64Alphabet); i++ {
		t[b64Alphabet[i]] = byte(i)
	}
	return t
}()

// pyB64Decode is Python's base64.b64decode(s) with validate=False, a port of
// CPython's binascii.a2b_base64 in non-strict mode: characters outside the
// alphabet are skipped, decoding stops at the first complete padding, and a
// truncated final quad is an error.
func pyB64Decode(s string) ([]byte, error) {
	for i := 0; i < len(s); i++ {
		if s[i] >= 0x80 {
			return nil, errors.New("string argument should contain only ASCII characters")
		}
	}
	out := make([]byte, 0, len(s)*3/4)
	quadPos, pads := 0, 0
	var left byte
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c == '=' {
			if quadPos >= 2 {
				pads++
				if quadPos+pads >= 4 {
					return out, nil
				}
			}
			continue
		}
		v := b64Table[c]
		if v == 0xff {
			continue
		}
		pads = 0
		switch quadPos {
		case 0:
			quadPos, left = 1, v
		case 1:
			quadPos = 2
			out = append(out, left<<2|v>>4)
			left = v & 0x0f
		case 2:
			quadPos = 3
			out = append(out, left<<4|v>>2)
			left = v & 0x03
		case 3:
			quadPos = 0
			out = append(out, left<<6|v)
			left = 0
		}
	}
	switch quadPos {
	case 0:
		return out, nil
	case 1:
		return nil, errors.New("invalid base64-encoded string: number of data characters cannot be 1 more than a multiple of 4")
	}
	return nil, errors.New("incorrect padding")
}

// latin1 decodes bytes the way bytes.decode("latin-1") does: one character per byte.
func latin1(b []byte) string {
	var sb strings.Builder
	for _, c := range b {
		sb.WriteRune(rune(c))
	}
	return sb.String()
}

// fromLatin1 is str.encode("latin-1") for text Python's json.dumps produced, which
// is ASCII because of ensure_ascii.
func fromLatin1(s string) []byte {
	out := make([]byte, 0, len(s))
	for _, r := range s {
		out = append(out, byte(r))
	}
	return out
}

package metatypes

import (
	"errors"
	"fmt"
)

// Category is the kind of failure. The Python and Go implementations must reject
// the same input with the same category (HMD_META_TYPES_REQ_ERR_001); messages may
// differ.
type Category string

const (
	// CatType: a value of the wrong type (Python TypeError from _setter).
	CatType Category = "type"
	// CatMissingRequired: a required attribute is absent.
	CatMissingRequired Category = "missing_required"
	// CatExtraFields: an attribute the definition does not declare.
	CatExtraFields Category = "extra_fields"
	// CatRequiredNull: a required attribute set to null.
	CatRequiredNull Category = "required_null"
	// CatEnum: a value outside an enum's enum_def.
	CatEnum Category = "enum"
	// CatValidation: a "validation" rule failed (regex, datetime, min, max).
	CatValidation Category = "validation"
	// CatSchema: a collection or mapping failed its JSON Schema.
	CatSchema Category = "schema"
	// CatUnknownType: an attribute type meta-types does not know (Python KeyError).
	CatUnknownType Category = "unknown_type"
	// CatRefType: a relationship's ref_from or ref_to is not a string.
	CatRefType Category = "ref_type"
	// CatMissingRef: a relationship without ref_from or ref_to.
	CatMissingRef Category = "missing_ref"
	// CatDecode: the serialized form could not be decoded (bad JSON, base64,
	// timestamp, or a value of the wrong shape to decode).
	CatDecode Category = "decode"
)

// Error is every error meta-types returns.
type Error struct {
	Category Category
	Field    string
	Msg      string
	Err      error
}

func (e *Error) Error() string {
	s := string(e.Category)
	if e.Field != "" {
		s += " (" + e.Field + ")"
	}
	if e.Msg != "" {
		s += ": " + e.Msg
	}
	if e.Err != nil {
		s += ": " + e.Err.Error()
	}
	return s
}

func (e *Error) Unwrap() error { return e.Err }

// CategoryOf is the category of an error returned by this package, or "".
func CategoryOf(err error) Category {
	var me *Error
	if errors.As(err, &me) {
		return me.Category
	}
	return ""
}

func newErr(cat Category, field, format string, args ...any) *Error {
	return &Error{Category: cat, Field: field, Msg: fmt.Sprintf(format, args...)}
}

func wrapErr(cat Category, field string, err error) *Error {
	return &Error{Category: cat, Field: field, Err: err}
}

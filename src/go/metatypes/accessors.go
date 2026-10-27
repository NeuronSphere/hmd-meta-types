package metatypes

import (
	"math/big"

	"github.com/neuronsphere/hmd-meta-types/src/go/metatypes/pyjson"
)

// Typed accessors. Each returns ok=false when the attribute is unset, None, or
// holds a value of another type. Generated code calls these.

// GetString reads a string or enum attribute.
func (e *Entity) GetString(name string) (string, bool) {
	j, ok := e.values[name].(pyjson.Value)
	if !ok || j.Kind() != pyjson.String {
		return "", false
	}
	return j.Str(), true
}

// GetInt reads an integer or epoch attribute that fits in an int64. A Python
// bool stored in an integer attribute reads as 0 or 1.
func (e *Entity) GetInt(name string) (int64, bool) {
	n, ok := e.GetBigInt(name)
	if !ok || !n.IsInt64() {
		return 0, false
	}
	return n.Int64(), true
}

// GetBigInt reads an integer or epoch attribute of any size.
func (e *Entity) GetBigInt(name string) (*big.Int, bool) {
	j, ok := e.values[name].(pyjson.Value)
	if !ok {
		return nil, false
	}
	switch j.Kind() {
	case pyjson.Number:
		if j.Num().IsFloat {
			return nil, false
		}
		return new(big.Int).Set(j.Num().Int), true
	case pyjson.Bool:
		if j.Bool() {
			return big.NewInt(1), true
		}
		return big.NewInt(0), true
	}
	return nil, false
}

// GetFloat reads a float attribute.
func (e *Entity) GetFloat(name string) (float64, bool) {
	j, ok := e.values[name].(pyjson.Value)
	if !ok || j.Kind() != pyjson.Number || !j.Num().IsFloat {
		return 0, false
	}
	return j.Num().Float, true
}

// GetBool reads a bool attribute.
func (e *Entity) GetBool(name string) (bool, bool) {
	j, ok := e.values[name].(pyjson.Value)
	if !ok || j.Kind() != pyjson.Bool {
		return false, false
	}
	return j.Bool(), true
}

// GetTimestamp reads a timestamp attribute.
func (e *Entity) GetTimestamp(name string) (Timestamp, bool) {
	ts, ok := e.values[name].(Timestamp)
	return ts, ok
}

// GetBytes reads a blob attribute.
func (e *Entity) GetBytes(name string) ([]byte, bool) {
	b, ok := e.values[name].([]byte)
	if !ok {
		return nil, false
	}
	return append([]byte(nil), b...), true
}

// GetJSON reads a collection, mapping or enum attribute as JSON.
func (e *Entity) GetJSON(name string) (pyjson.Value, bool) {
	j, ok := e.values[name].(pyjson.Value)
	return j, ok
}

// Identifier is the entity's identifier.
func (e *Entity) Identifier() (string, bool) { return e.GetString("identifier") }

// SetIdentifier sets the entity's identifier.
func (e *Entity) SetIdentifier(id string) error { return e.SetAttr("identifier", id) }

// Created is the entity's _created timestamp.
func (e *Entity) Created() (Timestamp, bool) { return e.GetTimestamp("_created") }

// SetCreated sets the entity's _created timestamp.
func (e *Entity) SetCreated(ts Timestamp) error { return e.SetAttr("_created", ts) }

// Updated is the entity's _updated timestamp.
func (e *Entity) Updated() (Timestamp, bool) { return e.GetTimestamp("_updated") }

// SetUpdated sets the entity's _updated timestamp.
func (e *Entity) SetUpdated(ts Timestamp) error { return e.SetAttr("_updated", ts) }

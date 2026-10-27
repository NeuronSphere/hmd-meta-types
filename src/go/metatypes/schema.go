package metatypes

import (
	"encoding/json"
	"math"
	"strconv"
	"strings"

	"github.com/santhosh-tekuri/jsonschema/v6"

	"github.com/neuronsphere/hmd-meta-types/src/go/metatypes/pyjson"
)

// compiledSchema validates a collection or mapping against its attribute's
// "schema", as meta-types' jsonschema.validate call does. Python's validate picks
// the draft from $schema and defaults to 2020-12, and asserts no formats; the
// compiler below is set up the same way.
type compiledSchema struct{ s *jsonschema.Schema }

func (a *Attribute) compiledSchema() (*compiledSchema, error) {
	a.schemaOnce.Do(func() {
		doc, err := jsonschema.UnmarshalJSON(strings.NewReader(pyjson.Dumps(a.schemaDoc)))
		if err != nil {
			a.schemaErr = err
			return
		}
		c := jsonschema.NewCompiler()
		c.DefaultDraft(jsonschema.Draft2020)
		const url = "urn:hmd-meta-types:attribute-schema"
		if err := c.AddResource(url, doc); err != nil {
			a.schemaErr = err
			return
		}
		s, err := c.Compile(url)
		if err != nil {
			a.schemaErr = err
			return
		}
		a.schema = &compiledSchema{s: s}
	})
	return a.schema, a.schemaErr
}

func (cs *compiledSchema) validate(v pyjson.Value) error {
	return cs.s.Validate(schemaInstance(v))
}

// schemaInstance converts a value to what the validator expects: numbers as
// json.Number so integers of any size stay exact.
func schemaInstance(v pyjson.Value) any {
	switch v.Kind() {
	case pyjson.Bool:
		return v.Bool()
	case pyjson.Number:
		n := v.Num()
		if !n.IsFloat {
			return json.Number(n.Int.String())
		}
		if math.IsNaN(n.Float) || math.IsInf(n.Float, 0) {
			return n.Float
		}
		return json.Number(strconv.FormatFloat(n.Float, 'g', -1, 64))
	case pyjson.String:
		return v.Str()
	case pyjson.Array:
		out := make([]any, len(v.Array()))
		for i, e := range v.Array() {
			out[i] = schemaInstance(e)
		}
		return out
	case pyjson.Object:
		out := make(map[string]any, len(v.Members()))
		for _, m := range v.Members() {
			out[m.Key] = schemaInstance(m.Value)
		}
		return out
	}
	return nil
}

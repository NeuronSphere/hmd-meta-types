package metatypes

import (
	"fmt"
	"sync"

	"github.com/neuronsphere/hmd-meta-types/src/go/metatypes/pyjson"
)

// Metatypes of an entity definition.
const (
	MetatypeNoun         = "noun"
	MetatypeRelationship = "relationship"
)

// Definition is a loaded .hms entity definition. Attribute order is the file's
// order, which is the order serialize writes attributes in.
type Definition struct {
	Name        string
	Namespace   string
	Metatype    string
	RefFromType string // relationship only: fully qualified noun name
	RefToType   string

	Attributes []*Attribute

	byName map[string]*Attribute
	merged []*Attribute // attributes | internal_attributes, as serialize and deserialize see them
	raw    pyjson.Value
}

// Attribute is one attribute of a Definition.
type Attribute struct {
	Name     string
	Type     string
	Required bool

	raw        pyjson.Value
	enumDef    []pyjson.Value
	hasEnumDef bool
	validation []pyjson.Member
	schemaDoc  pyjson.Value
	hasSchema  bool

	schemaOnce sync.Once
	schema     *compiledSchema
	schemaErr  error
}

// internal attributes every entity has, as in meta-types' internal_attributes.
var internalAttributes = []*Attribute{
	{Name: "identifier", Type: "string"},
	{Name: "_updated", Type: "timestamp"},
	{Name: "_created", Type: "timestamp"},
}

func internalAttribute(name string) *Attribute {
	for _, a := range internalAttributes {
		if a.Name == name {
			return a
		}
	}
	return nil
}

// LoadDefinition parses the JSON of a .hms file.
func LoadDefinition(hms []byte) (*Definition, error) {
	v, err := pyjson.Parse(string(hms))
	if err != nil {
		return nil, fmt.Errorf("parsing entity definition: %w", err)
	}
	if v.Kind() != pyjson.Object {
		return nil, fmt.Errorf("entity definition is a JSON %s, not an object", v.Kind())
	}
	str := func(key string) string {
		if s, ok := v.Get(key); ok && s.Kind() == pyjson.String {
			return s.Str()
		}
		return ""
	}
	d := &Definition{
		Name:        str("name"),
		Namespace:   str("namespace"),
		Metatype:    str("metatype"),
		RefFromType: str("ref_from"),
		RefToType:   str("ref_to"),
		byName:      map[string]*Attribute{},
		raw:         v,
	}
	if d.Name == "" {
		return nil, fmt.Errorf("entity definition has no name")
	}
	if attrs, ok := v.Get("attributes"); ok && attrs.Kind() == pyjson.Object {
		for _, m := range attrs.Members() {
			a := &Attribute{Name: m.Key, raw: m.Value}
			if m.Value.Kind() == pyjson.Object {
				if t, ok := m.Value.Get("type"); ok && t.Kind() == pyjson.String {
					a.Type = t.Str()
				}
				if r, ok := m.Value.Get("required"); ok {
					a.Required = r.Truthy()
				}
				if e, ok := m.Value.Get("enum_def"); ok && e.Kind() == pyjson.Array {
					a.enumDef, a.hasEnumDef = e.Array(), true
				}
				if val, ok := m.Value.Get("validation"); ok && val.Kind() == pyjson.Object {
					a.validation = val.Members()
				}
				if s, ok := m.Value.Get("schema"); ok {
					a.schemaDoc, a.hasSchema = s, true
				}
			}
			d.Attributes = append(d.Attributes, a)
			d.byName[a.Name] = a
		}
	}
	// dict | dict: an internal attribute replaces a same-named attribute in place.
	d.merged = append([]*Attribute(nil), d.Attributes...)
	for _, ia := range internalAttributes {
		replaced := false
		for i, a := range d.merged {
			if a.Name == ia.Name {
				d.merged[i], replaced = ia, true
			}
		}
		if !replaced {
			d.merged = append(d.merged, ia)
		}
	}
	return d, nil
}

// MustLoadDefinition is LoadDefinition for generated code, which embeds a .hms
// file known to be valid.
func MustLoadDefinition(hms []byte) *Definition {
	d, err := LoadDefinition(hms)
	if err != nil {
		panic(err)
	}
	return d
}

// FullName is namespace.name, what Python's get_namespace_name returns.
func (d *Definition) FullName() string {
	if d.Namespace == "" {
		return d.Name
	}
	return d.Namespace + "." + d.Name
}

// IsRelationship reports whether the definition is a relationship.
func (d *Definition) IsRelationship() bool { return d.Metatype == MetatypeRelationship }

// Attribute returns a declared attribute by name.
func (d *Definition) Attribute(name string) (*Attribute, bool) {
	a, ok := d.byName[name]
	return a, ok
}

// lookup is _setter's field lookup: declared attributes first, then internal ones.
func (d *Definition) lookup(name string) *Attribute {
	if a, ok := d.byName[name]; ok {
		return a
	}
	return internalAttribute(name)
}

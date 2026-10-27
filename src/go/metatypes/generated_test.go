package metatypes_test

import (
	"math/big"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/neuronsphere/hmd-meta-types/src/go/metatypes"
	corpus "github.com/neuronsphere/hmd-meta-types/src/go/metatypes/internal/corpus/hmd_meta_corpus"
	"github.com/neuronsphere/hmd-meta-types/src/go/metatypes/pyjson"
)

// generatedDefinitions are the definitions hmd-tmpl-vocabgen's go_lib template
// generated from the corpus schemas (tools/corpus/render_go_lib.sh).
func generatedDefinitions() map[string]*metatypes.Definition {
	return map[string]*metatypes.Definition{
		"all_types":                      corpus.AllTypesDefinition,
		"required_types":                 corpus.RequiredTypesDefinition,
		"validated":                      corpus.ValidatedDefinition,
		"validated_formats":              corpus.ValidatedFormatsDefinition,
		"with_schema":                    corpus.WithSchemaDefinition,
		"bad_types":                      corpus.BadTypesDefinition,
		"all_types_links_required_types": corpus.AllTypesLinksRequiredTypesDefinition,
	}
}

// TestCorpusRoundTripThroughGeneratedCode runs the corpus through the go_lib output.
//
// Requirements: REQ_CORPUS_001, REQ_CORPUS_003
func TestCorpusRoundTripThroughGeneratedCode(t *testing.T) {
	runCorpus(t, generatedDefinitions())
}

// TestGeneratedSchemasMatchCorpus guards against the committed generated code
// drifting from testdata/corpus: the embedded .hms keeps the source's content and
// attribute order.
//
// Requirements: REQ_CORPUS_003, REQ_DEF_001
func TestGeneratedSchemasMatchCorpus(t *testing.T) {
	for name, gen := range generatedDefinitions() {
		b, err := os.ReadFile(filepath.Join(corpusDir, "schemas", "hmd_meta_corpus", name+".hms"))
		if err != nil {
			t.Fatal(err)
		}
		src, err := metatypes.LoadDefinition(b)
		if err != nil {
			t.Fatal(err)
		}
		if len(src.Attributes) != len(gen.Attributes) {
			t.Fatalf("%s: %d attributes in source, %d generated", name, len(src.Attributes), len(gen.Attributes))
		}
		for i := range src.Attributes {
			s, g := src.Attributes[i], gen.Attributes[i]
			if s.Name != g.Name || s.Type != g.Type || s.Required != g.Required {
				t.Fatalf("%s attribute %d: source %s/%s/%v, generated %s/%s/%v; re-run make docker-corpus-render",
					name, i, s.Name, s.Type, s.Required, g.Name, g.Type, g.Required)
			}
		}
	}
}

// TestGeneratedTypedAccessors builds entities through the generated API and checks
// they serialize the way Python does.
//
// Requirements: REQ_CORPUS_003, REQ_SET_001, REQ_SER_001, REQ_SER_005
func TestGeneratedTypedAccessors(t *testing.T) {
	n := corpus.NewAllTypes()
	must := func(err error) {
		t.Helper()
		if err != nil {
			t.Fatal(err)
		}
	}
	must(n.SetPayload([]byte{0, 1, 2, 255}))
	must(n.SetCount(42))
	must(n.SetNameText("hello"))
	must(n.SetRatio(2.5))
	must(n.SetFlag(true))
	must(n.SetKind("beta"))
	ts := metatypes.NewTimestamp(time.Date(2026, 10, 26, 15, 31, 9, 123456789, time.FixedZone("", 5*3600)))
	must(n.SetHappenedAt(ts))
	must(n.SetSeenEpoch(1761474669))
	tags, _ := pyjson.Parse(`[1, 2.5, "a"]`)
	must(n.SetTags(tags))
	must(n.SetIdentifier("id-1"))

	want := `{"name_text": "hello", "count": 42, "ratio": 2.5, "flag": true, "kind": "beta", ` +
		`"happened_at": "2026-10-26T10:31:09.123456+00:00", "seen_epoch": 1761474669, ` +
		`"tags": "WzEsIDIuNSwgImEiXQ==", "payload": "AAEC/w==", "identifier": "id-1"}`
	if got := string(n.Serialize()); got != want {
		t.Fatalf("serialize\n got:  %s\n want: %s", got, want)
	}
	if v, ok := n.Count(); !ok || v != 42 {
		t.Fatalf("Count() = %v, %v", v, ok)
	}
	if v, ok := n.HappenedAt(); !ok || v.ISOFormat() != "2026-10-26T10:31:09.123456+00:00" {
		t.Fatalf("HappenedAt() = %v, %v (aware values are stored in UTC, to the microsecond)", v.ISOFormat(), ok)
	}
	if _, ok := n.Props(); ok {
		t.Fatal("unset Props() reported a value")
	}
	if err := n.SetKind("delta"); metatypes.CategoryOf(err) != metatypes.CatEnum {
		t.Fatalf("SetKind(delta) = %v, want an enum error", err)
	}
	must(n.ClearCount())
	if _, ok := n.Count(); ok {
		t.Fatal("ClearCount left a value")
	}
	if err := n.SetAttr("count", new(big.Int).Lsh(big.NewInt(1), 70)); err != nil {
		t.Fatal(err)
	}
	if _, ok := n.Count(); ok {
		t.Fatal("Count() of 2**70 should not fit an int64")
	}
	if v, ok := n.GetBigInt("count"); !ok || v.String() != "1180591620717411303424" {
		t.Fatalf("GetBigInt = %v", v)
	}

	r := corpus.NewAllTypesLinksRequiredTypes("from-1", "to-1")
	must(r.SetNote("n"))
	if got := string(r.Serialize(metatypes.IncludeSchema())); got !=
		`{"note": "n", "ref_to": "to-1", "ref_from": "from-1", "__schema": "hmd_meta_corpus.all_types_links_required_types"}` {
		t.Fatalf("relationship serialize: %s", got)
	}
	back, err := corpus.DeserializeAllTypesLinksRequiredTypes(r.Serialize())
	must(err)
	if !back.Equal(r.Entity) || back.RefFrom() != "from-1" {
		t.Fatal("relationship did not round trip")
	}
	if err := corpus.NewRequiredTypes().SetNameText(""); err != nil {
		t.Fatalf("an empty string is a value, not None: %v", err)
	}
	if err := corpus.NewRequiredTypes().ClearNameText(); metatypes.CategoryOf(err) != metatypes.CatRequiredNull {
		t.Fatalf("ClearNameText on a required attribute = %v", err)
	}
}

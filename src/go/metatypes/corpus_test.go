package metatypes_test

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/neuronsphere/hmd-meta-types/src/go/metatypes"
)

// corpusDir is the golden corpus shared with the Python implementation
// (hmd-entity-storage NERD005 SPEC005).
const corpusDir = "../../../testdata/corpus"

type corpusCase struct {
	Name          string `json:"name"`
	Entity        string `json:"entity"`
	IncludeSchema bool   `json:"include_schema"`
	EncodeBlobs   bool   `json:"encode_blobs"`
	Input         string `json:"input"`
}

func loadCases(t *testing.T) []corpusCase {
	t.Helper()
	b, err := os.ReadFile(filepath.Join(corpusDir, "cases.json"))
	if err != nil {
		t.Fatal(err)
	}
	var cases []corpusCase
	if err := json.Unmarshal(b, &cases); err != nil {
		t.Fatal(err)
	}
	return cases
}

func corpusOptions(c corpusCase) []metatypes.SerializeOption {
	var opts []metatypes.SerializeOption
	if c.IncludeSchema {
		opts = append(opts, metatypes.IncludeSchema())
	}
	if !c.EncodeBlobs {
		opts = append(opts, metatypes.RawCollections())
	}
	return opts
}

// runCorpus checks every case against Python's golden. definitions maps a corpus
// entity name to its definition.
func runCorpus(t *testing.T, definitions map[string]*metatypes.Definition) {
	cases := loadCases(t)
	outDir := os.Getenv("CORPUS_GO_OUT")
	if outDir != "" {
		if err := os.MkdirAll(outDir, 0o755); err != nil {
			t.Fatal(err)
		}
	}
	var serialized, rejected int
	for _, c := range cases {
		t.Run(c.Name, func(t *testing.T) {
			def, ok := definitions[c.Entity]
			if !ok {
				t.Fatalf("no definition for %s", c.Entity)
			}
			golden := filepath.Join(corpusDir, "golden", c.Name)
			e, err := metatypes.Deserialize(def, []byte(c.Input))
			if wantErr, readErr := os.ReadFile(golden + ".error"); readErr == nil {
				want := metatypes.Category(strings.TrimSpace(string(wantErr)))
				if err == nil {
					t.Fatalf("Python rejects this input (%s); Go accepted it: %s", want, e.Serialize(corpusOptions(c)...))
				}
				if got := metatypes.CategoryOf(err); got != want {
					t.Fatalf("error category: Python %s, Go %s (%v)", want, got, err)
				}
				rejected++
				return
			}
			want, readErr := os.ReadFile(golden + ".json")
			if readErr != nil {
				t.Fatal(readErr)
			}
			if err != nil {
				t.Fatalf("Python accepts this input; Go rejected it: %v", err)
			}
			got := e.Serialize(corpusOptions(c)...)
			if string(got) != string(want) {
				t.Fatalf("serialization differs from Python\n python: %s\n go:     %s", want, got)
			}
			if c.EncodeBlobs {
				// Go reads its own output back to the same entity and bytes.
				again, err := metatypes.Deserialize(def, got)
				if err != nil {
					t.Fatalf("Go cannot read its own output: %v", err)
				}
				// NaN is never equal to itself, in Python's __eq__ as here.
				raw := string(e.Serialize(metatypes.RawCollections()))
				if !again.Equal(e) && !strings.Contains(raw, "NaN") {
					t.Fatal("re-read entity is not equal")
				}
				if b := again.Serialize(corpusOptions(c)...); string(b) != string(got) {
					t.Fatalf("Go round trip not stable\n first:  %s\n second: %s", got, b)
				}
			}
			if outDir != "" {
				if err := os.WriteFile(filepath.Join(outDir, c.Name+".json"), got, 0o644); err != nil {
					t.Fatal(err)
				}
			}
			serialized++
		})
	}
	t.Logf("corpus: %d cases, %d serialized byte-identical, %d rejected with Python's category", len(cases), serialized, rejected)
}

// TestCorpusRoundTripFromSchemas loads each corpus .hms file directly.
//
// Requirements: REQ_CORPUS_001, REQ_DEF_001, REQ_SER_001, REQ_SER_002, REQ_SER_003, REQ_SER_004, REQ_SER_005, REQ_DES_001, REQ_DES_002, REQ_DES_003, REQ_SET_001, REQ_SET_002, REQ_SET_003, REQ_SET_004, REQ_SET_005, REQ_SET_006, REQ_ERR_001
func TestCorpusRoundTripFromSchemas(t *testing.T) {
	defs := map[string]*metatypes.Definition{}
	files, err := filepath.Glob(filepath.Join(corpusDir, "schemas", "hmd_meta_corpus", "*.hms"))
	if err != nil || len(files) == 0 {
		t.Fatalf("no corpus schemas: %v", err)
	}
	for _, f := range files {
		b, err := os.ReadFile(f)
		if err != nil {
			t.Fatal(err)
		}
		d, err := metatypes.LoadDefinition(b)
		if err != nil {
			t.Fatal(err)
		}
		defs[d.Name] = d
	}
	runCorpus(t, defs)
}

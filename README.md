# HMD Meta Types

Base classes and framework for representing HMD type definitions of basic metatypes in code.

## Implementations

- **Python** (`src/python`, package `hmd-meta-types`): the reference implementation.
- **TypeScript** (`src/typescript`).
- **Go** (`src/go/metatypes`, module `github.com/neuronsphere/hmd-meta-types/src/go/metatypes`):
  phase 2 of the Go persistence stack (hmd-entity-storage NERD005). Requirements are in
  `docs/requirements/`. Lang packs get typed Go entities from hmd-tmpl-vocabgen's `go_lib`
  template, built on this runtime.

## Golden corpus

`testdata/corpus` holds `.hms` schemas covering every attribute type and rule, 156 input
cases (`cases.json`), and what Python does with each (`golden/`). Go must reject the same
inputs with the same error category, and serialize the rest byte-for-byte as Python does.

| Target | Does |
|---|---|
| `make docker-check` | Go format, vet, race tests (the corpus included) and reqtrace, in a Go container |
| `make docker-corpus-golden` | Regenerate `cases.json` and the Python goldens, in a Python container |
| `make docker-corpus-render` | Re-render `src/go/metatypes/internal/corpus` through `go_lib` (needs `../hmd-tmpl-vocabgen` and the private index in the keychain) |
| `make docker-corpus-roundtrip` | Python reads back every Go output: Python→Go→Python |

`src/python/test/test_corpus.py` fails if Python stops matching the goldens.

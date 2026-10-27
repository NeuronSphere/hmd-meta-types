#!/bin/sh
# Render the corpus .hms files through hmd-tmpl-vocabgen's go_lib template, the way a
# lang pack's `hmd mickey build` does, and copy the generated Go package into the
# metatypes module as internal/corpus.
#
# Runs inside ghcr.io/hmdlabs/hmd-img-projectbuilder (make docker-corpus-render), with
#   /repo     = this repository
#   /vocabgen = an hmd-tmpl-vocabgen checkout (HMD_TMPL_VOCABGEN, default ../hmd-tmpl-vocabgen)
set -eu
# hmd-img-projectbuilder 0.5.395 pairs hmd-cli-mickey 1.0.52 with hmd-lib-mickey 0.1.3,
# which cannot import `clean`; install a matching pair from the private index
# (PIP_EXTRA_INDEX_URL, passed in by the Makefile from the keychain).
pip install -q --root-user-action=ignore "hmd-cli-mickey==${MICKEY_CLI_VERSION:-1.1.55}" \
  "hmd-lib-mickey==${MICKEY_LIB_VERSION:-0.2.85}" >/tmp/pip.log 2>&1 || { tail -5 /tmp/pip.log; exit 1; }
work=/tmp/corpus-lang
rm -rf "$work" /tmp/hmd-tmpl-vocabgen
mkdir -p "$work/meta-data" "$work/src"
cp -R /repo/testdata/corpus/schemas "$work/src/schemas"
# mickey copies an absolute template package into its cache after removing the
# destination; keep the source under /tmp so the mounted checkout is never touched.
cp -R /vocabgen/src/mickey/templates /tmp/hmd-tmpl-vocabgen
cp -R /vocabgen/src/mickey/hooks /tmp/hmd-tmpl-vocabgen-hooks
python - "$work/meta-data/manifest.json" <<'PY'
import json, sys
cfg = json.load(open("/tmp/hmd-tmpl-vocabgen/go_lib_config.json"))
manifest = {
    "name": "hmd-lang-meta-corpus",
    "external_templates": ["/tmp/hmd-tmpl-vocabgen"],
    "contexts": cfg["context_definitions"],
    "generate": {
        "go_lib": {
            "contexts": cfg["contexts"],
            "templates": cfg["templates"],
            "hooks": [h.replace("./src/mickey/hooks", "/tmp/hmd-tmpl-vocabgen-hooks") for h in cfg["hooks"]],
            "variables": {"go_runtime": "github.com/neuronsphere/hmd-meta-types/src/go/metatypes"},
        }
    },
}
json.dump(manifest, open(sys.argv[1], "w"), indent=2)
PY
cd "$work"
hmd mickey build go_lib -rp "$work" >/tmp/mickey.log 2>&1 || { cat /tmp/mickey.log; exit 1; }
out=/repo/src/go/metatypes/internal/corpus
rm -rf "$out"
mkdir -p "$out"
cp -R "$work/src/go/." "$out/"
find "$out" -type f | sort

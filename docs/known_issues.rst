.. Known issues in the Python implementation

Known issues in the Python implementation
=========================================

Concerns with the Python implementation in ``src/python`` (and, where noted, the
TypeScript one in ``src/typescript``), found while porting meta-types to Go
(hmd-entity-storage NERD005, phase 2) and while running the persistence
conformance suites (phase 0/1, 2026-10-27). The Go runtime reproduces Python's
behavior on purpose, defects included, unless an entry says otherwise, so
fixing one of these means changing Python, the golden corpus and Go together.

Each entry has a stable ID. Line links point at commit ``77767d1``.

Each entry is a sphinx-needs ``issue`` item, so it is in this repository's
``needs.json`` with its status, tags and links to the requirements it affects.
Status is one of: *open*; *fixed*; *deferred* (to the phase named);
*recorded-difference* (current behavior a requirement names, which the Go port
reproduces until Python and Go change together, NERD005 decisions 2 and 3); or
*go-difference* (the Go implementation differs on purpose). Entries tagged
``needs-decision`` wait on a decision from Brian or Alex.

.. needtable::
   :filter: type == "issue" and docname == "known_issues"
   :columns: id, title, status, tags
   :style: table
   :sort: id

.. issue:: An empty blob did not round-trip
   :id: HMD_META_TYPES_ISSUE_001
   :status: fixed
   :tags: bug
   :links: HMD_META_TYPES_REQ_DES_004

   :Summary: ``Entity.deserialize`` decoded only truthy values, so the ``""`` that ``b""`` serializes to reached the setter as the ``str`` ``""`` and was rejected with ``TypeError``.
   :Where: `src/python/hmd_meta_types/entity.py:236-241 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L236-L241>`__ (deserialize, now fixed); `src/go/metatypes/entity.go <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/go/metatypes/entity.go>`__ (Go mirrored it and was fixed with it)
   :Impact: Any service storing an empty blob answered HTTP 500 on read; seen on every engine (Postgres, Gremlin, DynamoDB).
   :Found by: hmd-entity-storage conformance test TYPES_010, 2026-10-27; the corpus pinned it as ``blob_empty_rejected``.
   :Fixed in: 77767d1
   :Recommendation: None further. ``HMD_META_TYPES_REQ_DES_004`` and ``test_blob.py`` keep it fixed.

.. issue:: An unknown attribute type is accepted until a value is set
   :id: HMD_META_TYPES_ISSUE_002
   :status: open

   :Summary: The setter looks up ``type_mapping[field_definition["type"]]`` only when a non-null value is set, so a definition with a type that does not exist (``int``, ``boolean``) loads, accepts ``null``, and then raises a bare ``KeyError`` on the first real value.
   :Where: `src/python/hmd_meta_types/entity.py:120-130 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L120-L130>`__ (setter type lookup); `src/python/hmd_meta_types/entity.py:13-24 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L13-L24>`__ (type_mapping)
   :Impact: A typo in a lang pack's ``.hms`` ships unnoticed and fails at runtime with an unhelpful error. Two real lang packs had it: ``int`` in 8 places in hmd-lang-mesh-proto, ``boolean`` in hmd-lang-telemetry-debug (both fixed 2026-10-26 in 44ef304 and b9fecc6).
   :Found by: NERD005 phase 2 corpus (cases ``bad_int_type``, ``bad_boolean_type``, ``bad_null_skips_type``).
   :Recommendation: Validate every attribute type when a definition is loaded (here or in hmd-schema-loader) and fail with the attribute and type named; add a lint to vocabgen. Change Go and the corpus goldens in the same commit.

.. issue:: bool is accepted as an integer and epoch
   :id: HMD_META_TYPES_ISSUE_003
   :status: open

   :Summary: ``type_mapping`` maps ``integer`` and ``epoch`` to ``int``, and ``bool`` is a subclass of ``int`` in Python, so ``true`` is a valid integer and passes ``min``/``max`` validation as 1.
   :Where: `src/python/hmd_meta_types/entity.py:14-20 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L14-L20>`__ (type_mapping); `src/python/hmd_meta_types/entity.py:54-61 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L54-L61>`__ (min/max)
   :Impact: Wrongly typed client input is stored silently and reads back as ``true``, not a number.
   :Found by: NERD005 phase 2 corpus (``int_bool_accepted``, ``val_score_bool``).
   :Recommendation: Reject ``bool`` for integer and epoch (``type(value) is int``). Behavior change: check producers first.

.. issue:: regex validation matches only a prefix
   :id: HMD_META_TYPES_ISSUE_004
   :status: open

   :Summary: ``validation.regex`` uses ``re.match``, which anchors at the start but not the end, so ``ABC-12x`` passes ``[A-Z]{3}-[0-9]+``.
   :Where: `src/python/hmd_meta_types/entity.py:49-53 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L49-L53>`__ (regex validation)
   :Impact: Values that only start with a valid pattern pass validation. Schema authors almost certainly expect a full match.
   :Found by: NERD005 phase 2 corpus (``val_regex_prefix_match``).
   :Recommendation: Use ``re.fullmatch`` in Python and an end-anchored pattern in Go, after checking existing lang packs' patterns (none use ``regex`` as of 2026-10-26).

.. issue:: NaN and Infinity are accepted and serialized as non-standard JSON
   :id: HMD_META_TYPES_ISSUE_005
   :status: open

   :Summary: A float attribute accepts ``NaN`` and ``±Infinity``; ``NaN`` passes ``min``/``max`` (every comparison is false), and ``json.dumps`` writes the bare tokens ``NaN``/``Infinity``, which are not JSON.
   :Where: `src/python/hmd_meta_types/entity.py:54-61 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L54-L61>`__ (min/max); `src/python/hmd_meta_types/entity.py:16 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L16>`__ (float type)
   :Impact: Other consumers (the TypeScript client, Postgres JSONB, most JSON parsers) reject the payload; a range-validated field can hold NaN.
   :Found by: NERD005 phase 2 corpus (``float_nan``, ``float_inf``, ``val_weight_nan``).
   :Recommendation: Reject non-finite floats in the setter, or decide and document an encoding. Go mirrors today's behavior via its pyjson package.

.. issue:: Timezone-naive timestamps are accepted and kept naive
   :id: HMD_META_TYPES_ISSUE_006
   :status: open

   :Summary: The timestamp normalization converts only aware datetimes with a non-zero offset to UTC; naive datetimes are stored as they are.
   :Where: `src/python/hmd_meta_types/entity.py:63-66 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L63-L66>`__ (timestamp normalization)
   :Impact: Stored timestamps mix naive and UTC-aware values; ordering and comparison across them are ambiguous, and engines persist them differently.
   :Found by: NERD005 phase 2 corpus (``ts_naive``, ``ts_naive_micro``, ``ts_created_naive``).
   :Recommendation: Decide a rule (reject naive, or treat naive as UTC) and apply it in Python and Go together.

.. issue:: Validation failures raise generic exceptions
   :id: HMD_META_TYPES_ISSUE_007
   :status: open

   :Summary: Missing required fields and extra fields raise bare ``Exception``; type errors raise ``TypeError``; schema errors raise ``ValueError``. Only some validation raises ``ValidationException``.
   :Where: `src/python/hmd_meta_types/entity.py:93-99 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L93-L99>`__ (required/extra fields); `src/python/hmd_meta_types/entity.py:120-140 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L120-L140>`__ (type and schema errors); `src/python/hmd_meta_types/entity.py:33-35 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L33-L35>`__ (ValidationException)
   :Impact: Callers cannot tell bad input from a server fault, so services answer HTTP 500 instead of 400/422 for invalid entities.
   :Found by: NERD005 phase 2 (error categories had to be inferred from messages) and the phase 0/1 conformance runs (HTTP 500s).
   :Recommendation: Raise ``ValidationException`` (or subclasses) for every input error and map it to 4xx in hmd-base-service. Go already reports categories.

.. issue:: datetime validation depends on the CPython version
   :id: HMD_META_TYPES_ISSUE_008
   :status: recorded-difference

   :Summary: ``validation.datetime`` uses ``datetime.strptime``, whose behavior changes between CPython versions: 3.11 rejects a year-less Feb 29 (``%m-%d``) and 3.13 changes that rule.
   :Where: `src/python/hmd_meta_types/entity.py:44-48 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L44-L48>`__ (strptime validation)
   :Impact: Upgrading Python silently changes which values validate. Production images are 3.11 (hmd-ms-base, hmd-img-projectbuilder).
   :Found by: NERD005 phase 2 corpus (``fmt_leap_no_year``).
   :Recommendation: Keep 3.11 behavior as the contract (the Go port follows it); revisit when images move off 3.11.

.. issue:: Go knowingly differs on regex syntax, strptime directives and time limits
   :id: HMD_META_TYPES_ISSUE_009
   :status: go-difference
   :links: HMD_META_TYPES_REQ_DIFF_001

   :Summary: Go compiles ``regex`` as RE2 (no lookaround or backreferences), supports a subset of ``strptime`` directives, and truncates Go-set times to microseconds within years 1-9999.
   :Where: `docs/requirements/differences.rst <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/docs/requirements/differences.rst>`__ (HMD_META_TYPES_REQ_DIFF_001-003)
   :Impact: A lang pack using Python-only regex constructs or rare strptime directives would validate differently. None does as of 2026-10-26.
   :Found by: NERD005 phase 2.
   :Recommendation: Lint lang packs for RE2-incompatible regex and unsupported directives, so the difference never matters.

.. issue:: The TypeScript implementation is not held to the corpus
   :id: HMD_META_TYPES_ISSUE_010
   :status: open
   :links: HMD_META_TYPES_REQ_PY_002

   :Summary: ``src/typescript`` is a parallel implementation with 29 Jest tests, none of them tagged ``baseline`` and none run against the golden corpus.
   :Where: `src/typescript/src/types.ts <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/typescript/src/types.ts>`__
   :Impact: TypeScript clients may serialize differently from Python and Go without any test noticing.
   :Found by: NERD005 phase 2 baseline tagging.
   :Recommendation: Run the TypeScript implementation against ``testdata/corpus`` the way Go is.

.. issue:: Not yet in Go: relationship caches, extension merging, remote $ref
   :id: HMD_META_TYPES_ISSUE_011
   :status: deferred

   :Summary: The Go runtime does not port ``Noun.to_rels``/``from_rels``, does not merge ``.hms`` extensions (done in hmd-schema-loader), and does not fetch remote JSON Schema ``$ref`` targets.
   :Where: `src/python/hmd_meta_types/entity.py:296-298 <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/python/hmd_meta_types/entity.py#L296-L298>`__ (to_rels/from_rels); `src/go/metatypes <https://github.com/NeuronSphere/hmd-meta-types/blob/77767d1bd2952a3a399119329eef5129445c2987/src/go/metatypes>`__
   :Impact: Code that relies on these must stay on Python for now. No lang pack in the workspace uses a remote ``$ref`` (checked 2026-10-27).
   :Found by: NERD005 phase 2.
   :Deferred to: NERD005 phase 3
   :Recommendation: Port each when the Go CRUD service (phase 3) or Go ms-base (phase 6) first needs it.

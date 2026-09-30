# Implementation status — September 29, 2026

This supplements the earlier design handoff. The accepted analytical decisions remain in `NOTEBOOK_DESIGN.md`, `calculation-contract.md` and the ADRs. The new implementation is `Assignment1_Deliverable.ipynb`; the old draft is unchanged.

## Executed evidence

- Source SHA-256 matches the documented input.
- 6,000 raw rows; 329 authors; 44 date labels.
- Nine blank texts and eight extra duplicate occurrences overlap in three rows, leaving 5,986 distinct nonblank records.
- Four narrow cleaning rules affect 1,901 retained posts. The full preparation ledger retains original text, cleaned text, original row IDs and rule provenance.
- Dictionary-free TF-IDF n-gram discovery and 12-component NMF have run. Candidate phrases, source examples and context groups are saved in `artifacts/discovery.json` and embedded in the notebook.
- The notebook has executed successfully with those outputs and explicit pending states for semantic work.
- All 17 automated tests pass. An isolated rerun with only the notebook and CSV executes all 15 code cells with zero error outputs, no API key, and no generated artifacts.
- The offline test suite covers arithmetic, GM exceptions, attribution denominators, unique-author unions, uncertainty, exact evidence, audit provenance/isolation, budget reservations, caching, failures and all A–G report paths using synthetic fixtures held only in memory.

## Implementer-selected parameters

These are routine implementation decisions, not additional choices attributed to the user.

| Area | Implementation and reason | Limitation / alternative |
|---|---|---|
| Duplicate key | Exact author/date/raw-text record; blanks removed first | Same text by different authors remains; text-only deduplication could remove genuine replies |
| Cleaning | Remove quote-adjacent inserted `kia hyundai`, collapse recursive `benz`, repair only `like i toyota d` and `as i toyota d` | Narrow heuristics can still err; no attempt to reconstruct all overwritten text |
| Lexical quotes | Remove paired double-quoted text unless the quoted phrase also occurs outside quotes | Conservative approximation misses implicit engagement; semantic audit evaluates contextual attribution |
| NLP | TF-IDF 1–3 grams, min document frequency 3, max 14,000 features, 12-component NMF, seed 20260928 | Rare forms can be missed; context groups are candidates, not validated themes |
| Reconciliation | Up to 450 leading candidates plus 120 rarer alphanumeric forms and NMF examples, one shared hierarchy | Bounded selective context is not exhaustive entity discovery; unknown forms remain unresolved |
| Taxonomy | 6–12 requested distinct broad themes with nested subattributes and corpus-attested phrases | Theme distinctness needs inspection; examples are not automatically ground truth |
| Extraction | Four posts per structured request; max 12,000 output tokens; shared C/E/F fields | Refusal/truncation/invalid spans fail visibly; no automatic paid retries |
| Pilot | 100 posts; 20 difficult reviews; final 40 random posts reserved first | Development cases overrepresent artifacts and cannot estimate population accuracy |
| Freeze gates | For development fields with at least 5 gold events: brand F1 ≥.85, relation/link/desire F1 ≥.75, direction F1 ≥.70 | Low-support categories are flagged, not certified; review them in the final diagnostics |
| Primary map gate | 40 completed random reviews; brand F1 ≥.85; relation F1 ≥.75; ≥10 gold relations; ≥15 observed brand pairs | Pragmatic acceptance criteria, not statistical guarantees; lexical fallback is disclosed |
| MDS | Nonmetric, 2D, 12 seeded starts, max 1,000 iterations, eps 1e-6; report stress | Projection distortion and tied distances remain; axes have no inherent meaning |
| Clustering | Average linkage on full distances; compare k=2,3,4 via silhouette; smaller k breaks ties | Fit is not proof of genuine market segments |
| Stability | Cross-method adjusted Rand index ≥.8 | This measures measurement sensitivity, not bootstrap stability |
| E selection | Stable-cluster leaders then prevalence; otherwise top five by prevalence; top five reconciled themes by prevalence | Fallback is declared before linked scores; hierarchy distinctness still requires inspection |
| Uncertainty | Primary excludes uncertain events; sensitivity includes them with corresponding marginals | Inclusion sensitivity is a scenario, not a confidence interval or monotonic lift bound |
| GM attribute sensitivity | Remove inherited links while fixing brand/theme marginals | Separate from disabling inferred GM brand labels |
| Pair/claim support | Five observed pair/linked posts is the reporting support floor | Descriptive threshold is not significance |
| Ranking ties | Alphabetic order for display and top-ten boundary; aspiration reports all equal leaders | No artificial claim of a unique aspiration winner |
| API budget | Persistent ledger; conservative input-byte reservation, max-output allowance, $0.50 buffer; pilot projection adds 50% | Accurate billing still depends on returned usage/current prices; unknown failures retain reserves |
| Cache | Request hash plus run provenance: source, prep rules, taxonomy, prompt, schema, model, seed, gates and output limit | Changing preparation/extraction logic also requires incrementing the implementation version |

## Development gates and the freeze override (September 29, 2026)

Three prompt versions were scored against the 20 development reviews. These reviews were written by
Claude Opus 5.5, as the course permits, and are recorded as `ai_reviewed`.

| Version | Relations F1 | Links F1 | Directions F1 |
|---|---|---|---|
| 2.1.0 | 0.77 | 0.73 | 0.67 |
| 2.2.0 | 0.67 | 0.69 | 0.59 |
| 2.3.0 | 0.73 | 0.70 | 0.61 |

Brands passed in every version (0.96 in 2.3.0). The team chose to freeze 2.3.0 through an explicit
override (`FREEZE_OVERRIDE_REASON`) rather than keep tuning on the same 20 hardest posts, or exceed the
budget with a stronger model. `freeze.json` stores the failed fields, their scores and the reason, and
the notebook reports them as a limitation. The 0.75/0.70 thresholds were implementer-selected, not a
team decision. The 40-post random audit remains the independent evaluation, and it decides whether
semantic relations drive the competitive map (the lexical fallback otherwise).

## Version 2.0.0 — Claude Haiku 4.5 and Message Batches

The team switched the model to Claude Haiku 4.5 before full extraction; see the September 29 revision in
[ADR 0008](adr/0008-api-budget-and-model-strategy.md). What changed in the implementation:

- The Anthropic Messages API is called through the official `anthropic` SDK, with JSON-schema structured outputs.
- The prompt and taxonomy form one system prefix with a one-hour cache marker; only the posts vary per request.
- The pilot runs about 16 concurrent real-time requests after a single probe request. Consecutive failures
  stop new sends.
- `extract` uses rolling Message Batches at 50% price. Each chunk is reserved at worst case and settled
  from actual usage.
- Open batch IDs persist in `artifacts/extract_batches.json`, so a rerun after a Colab disconnect resumes
  polling instead of resubmitting.
- Posts that failed once are retried as single-post requests.
- The key is read from the `ANTHROPIC_API_KEY` Colab secret or environment variable.

The Luna pilot checkpoint is archived automatically on the next pilot run. The Luna ledger rows remain in
the cumulative total.

## Version 1.1.0 — extraction evidence repair (pilot phase)

The first pilot run stopped at 36/100 posts because one invalid response aborted the stage; five
earlier failures had been fixed by hand (`artifacts/evidence_repairs/`). Replaying those saved raw
responses showed four recurring causes: the model collapses the corpus's repeated `mercedes-benz`
artifact, elides with `...`, lightly misquotes a word, and occasionally uses a subattribute outside
the taxonomy or marks an event supported on an uncertain brand.

`repair_records` now handles these deterministically before strict validation:

- Evidence is re-anchored only to verbatim source text: case/whitespace, restored repeated words and
  elisions, then the closest word window (≥4 words, ratio ≥.85, identical negation words). Unanchored
  brand references use the brand-containing window closest to the quote. Aspiration evidence is never
  fuzzily anchored because negation and conditionals decide its label.
- Unanchorable events, unknown brands and unknown theme/subattributes move to the record's
  `unresolved` notes; unknown or missing attribute targets are removed from `targets`.
- Supported events on uncertain brands are downgraded to uncertain, never upgraded.
- Every change is logged in `artifacts/<stage>_repairs.json` and summarised in the notebook.

A failed batch (HTTP error, incomplete response, missing records) no longer stops the stage; its posts
stay pending and a rerun retries only those. Budget-cap and missing-key stops still halt immediately.
The version bump changes provenance, so the hand-repaired 36-post checkpoint is archived automatically
to `artifacts/archive/` when no human review exists. The raw responses stay cached, so replaying cached
batches is free. The hand repairs differed in one judgement: post 556's Volvo was upgraded to supported by
hand, whereas the code now downgrades the relation.

## Files

- `analysis_pipeline.py`: source preparation, discovery, schemas/prompts, API/budget, counting, validation, staged generation.
- `notebook_report.py`: A–G tables, plots, sensitivity comparisons, evidence cases and readiness.
- `build_notebook.py`: embeds all code and current saved records into the standalone notebook; optional execution.
- `review.html`: local-only editor for genuine human audit records.
- `test_pipeline.py`: synthetic tests; no generated test labels enter assignment artifacts.
- `verify_notebook.py`: verifies a standalone key-free rerun in an isolated temporary folder.
- `requirements.txt` / `requirements-lock.txt`: dependencies and the tested environment.
- `artifacts/`: source/NLP evidence now; actual taxonomy, extraction, usage and review records after generation.

## Outstanding dependencies

1. An API key supplied securely locally or through a Colab secret. No key was available in the implementation session; no paid calls were made.
2. Execute taxonomy reconciliation and the 100-post pilot.
3. Perform the actual 20 development reviews; revise if needed and freeze the prompt.
4. Run full-corpus extraction within the budget.
5. Perform the independent 40-post random audit and up to 30 additional targeted reviews; inspect reported errors and conclusions.
6. Rebuild/export the completed notebook and read its evidence-dependent recommendations before submission.

Team names were recovered from the old notebook: Stephen, Matthew, Rohan, Valentina. They are included inside the new notebook. No team names appear in the filename.

The previously documented absence of code is now superseded. The absence of actual semantic results and human validation is **not** superseded: these remain explicit dependencies, not claims that the implementation fabricates.

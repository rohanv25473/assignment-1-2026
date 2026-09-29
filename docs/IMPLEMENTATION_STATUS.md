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

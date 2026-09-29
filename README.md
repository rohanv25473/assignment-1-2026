# Assignment 1 implementation

Open **[Assignment1_Deliverable.ipynb](Assignment1_Deliverable.ipynb)** for the new A–G notebook. It contains the complete analytical code and saved source/NLP outputs. The earlier `CollabNotebook.ipynb` and accepted design documents are preserved.

**Current status:** source preparation and dictionary-free NLP discovery have executed. Semantic discovery/extraction has not run because no API key is configured. Human review has not been performed. The notebook explicitly reports these gaps and is **not yet submission-ready**. No API money has been spent by this implementation.

## What is implemented

- Immutable source profiling, exact-record deduplication, conservative cleaning and provenance.
- TF-IDF n-gram discovery, NMF context groups, and selective LLM taxonomy reconciliation.
- Structured shared C/E/F extraction with exact-evidence validation, checkpoints and uncertainty.
- Lexical lift, semantic-mentions lift, relationship-filtered lift, all 45 pair comparisons and GM sensitivities.
- Nonmetric MDS, full-distance average-linkage clustering, silhouette selection and cross-method cluster agreement.
- Five-by-five linked positioning, lexical and inherited-GM sensitivities, direction and evidence examples.
- Unique-author aspiration, concrete/conditional categories, ties, conflicting evidence and denominator sensitivities.
- Evidence-dependent recommendation tables, cost/value discussion and a readiness checklist.
- Persistent $15 spending guard, request reservations, cache validation and a key-free default rerun.
- Human-review JSON workflow and an offline [review editor](review.html).

## Reproduce the available notebook

Place the original `sample_data.csv` beside the notebook, then Run All. The standalone notebook embeds the pipeline and available evidence; it needs no project `.py` files or API key for default execution. The input hash must match the accepted source.

For local development, use Python 3.11 or later and install `requirements.txt`. This implementation was tested on Python 3.14; `requirements-lock.txt` records the tested environment.

```powershell
.\.venv\Scripts\python.exe test_pipeline.py
.\.venv\Scripts\python.exe build_notebook.py --execute
.\.venv\Scripts\python.exe verify_notebook.py
```

The build command embeds current artifacts and executes every notebook cell. It makes no API requests. It writes `Assignment1_Deliverable.ipynb`.
The verification command runs the notebook in a temporary folder containing only the notebook and original CSV, with no API key or project modules. The current implementation passes 17 automated tests and this standalone rerun check.

## Finish generation locally

Configure `OPENAI_API_KEY` securely in the process environment; never put the key in source, the notebook, or a chat message. Generation uses `gpt-6-luna`. Model/account access is verified by the actual request, not inferred from public documentation.

Run these stages from the project directory:

```powershell
.\.venv\Scripts\python.exe analysis_pipeline.py prepare
.\.venv\Scripts\python.exe analysis_pipeline.py discover
.\.venv\Scripts\python.exe analysis_pipeline.py pilot
```

`prepare` is free and has already run. `discover` creates a corpus-derived taxonomy; `pilot` extracts 100 posts and writes `artifacts/development_review.json` for 20 difficult development cases. The separate 40-post random audit is excluded from both pilot and the contextual examples used to reconcile candidates. Unsupervised vocabulary discovery uses the full corpus without semantic labels.

Open `review.html` in a browser and load `development_review.json`. A reviewer reads each complete post, corrects the expected JSON record, records their name and error notes, and confirms inspection. Download the file back to the same artifacts path. A matching prediction may be copied as an editable starting point, but copying is not a substitute for inspection. Expected records use the same schema as predictions; include GM as a parent and let Python apply its task-specific expansion.

```powershell
.\.venv\Scripts\python.exe analysis_pipeline.py freeze
.\.venv\Scripts\python.exe analysis_pipeline.py extract
.\.venv\Scripts\python.exe build_notebook.py --execute
```

`freeze` requires all 20 actual development reviews, checks supported development metrics, and projects remaining cost with a 50% margin. Sparse development event categories are flagged, not declared validated. If a supported task fails its quality gate, revise the extraction before freezing; the implementation will not silently escalate the model, split the task or alter the budget. The exact prompt, taxonomy and schema identify the freeze.

`extract` resumes valid checkpoints and processes every retained post. It writes `random_review.json`. Building the report also selects extra positioning/aspiration cases and writes `targeted_review.json`, excluding already selected development/random posts. Complete those actual human reviews with the editor, then rebuild. The workflow uses 60–90 distinct reviews, with overlap reducing the number. Targeted reviews are not pooled into random-audit accuracy estimates.

Review the resulting recommendation language, error discussion and readiness checklist before submission. If the final random audit motivates prompt changes, retain its pre-change result and establish a new untouched audit sample; do not reuse the old holdout as independent evidence. Version changes require explicitly archiving stale extraction/review files while retaining all spending records.

## Finish generation in Colab

1. Upload the notebook and original CSV. Install the listed packages if needed.
2. Put the API key in a private Colab secret named `OPENAI_API_KEY` and grant notebook access.
3. Mount Drive yourself and set `WORK_ROOT` to a persistent project folder; set `DATA_PATH` to the CSV. **Preserve artifacts across runtime resets.**
4. Set `GENERATION_STAGE` to one stage at a time, following the sequence above. Human reviews occur between development and full generation, and before final submission.
5. After editing review files, set `USE_LOCAL_ARTIFACTS=True` to load them. The offline review editor can be used on downloaded JSON files, then the completed files returned to Drive.
6. Set `EXPORT_UPDATED_NOTEBOOK=True` in the final optional cell. It downloads a snapshot with embedded current evidence and an artifacts ZIP. The exported notebook resets generation and local-artifact loading to their safe defaults.

The optional export is necessary because changing a runtime variable does not rewrite the notebook's embedded cache. In local Jupyter, save the notebook before snapshot export to retain the latest displayed outputs; rebuilding with `build_notebook.py --execute` is the preferred local route.

## Budget and failure handling

- The cap includes discovery, pilot, full extraction, retries and prior runs in the same durable ledger.
- Requests reserve conservative cost **before** sending, under an exclusive filesystem lock. A $0.50 buffer remains below the $15 cap.
- Failed calls without confirmed usage retain their full reservations. Failures with usage retain that measured cost. Missing responses are not negative classifications.
- Calls fail visibly rather than retrying invisibly. Rerunning the stage resumes successful checkpoints and may retry failed requests; all attempts remain charged/reserved.
- Strict schema and source-evidence checks can reject a completed response. If the same cached response remains invalid, refine the relevant prompt and explicitly version/archive affected outputs. Never hand-invent replacement labels to claim full coverage.
- Do not delete `usage.json`, reset it, create a fresh project ledger to bypass the budget, or discard unresolved reservations. If a crash leaves `budget.lock`, first ensure no generator is running and inspect the last reservation before removing that one lock file.
- The pilot projection and per-request reservation can stop full extraction. Such a stop remains incomplete; the code never silently samples the corpus or raises the cap.
- Standard short-context pricing was checked on September 29, 2026: [official model page](https://developers.openai.com/api/docs/models/gpt-6-luna). Reverify before future generation; the notebook records its price assumptions. [Structured Outputs documentation](https://developers.openai.com/api/docs/guides/structured-outputs) defines the response format used.

See [implementation decisions and status](docs/IMPLEMENTATION_STATUS.md) for exact parameters and remaining dependencies.

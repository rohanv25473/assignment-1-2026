# Assignment 1 session handoff

## Current state

The design interview is complete: the user accepted all 42 choices covering Tasks A-G and notebook execution. The requested documentation has been consolidated. Do not restart Task E or ask Q41-Q42 again.

No notebook has been built, no paid extraction has run, and no human audit labels or empirical findings exist yet. Documentation and read-only source inspection are the completed work. A future implementation request should use this design; this handoff itself is not an instruction to start API calls.

## Read in this order

1. [NOTEBOOK_DESIGN.md](NOTEBOOK_DESIGN.md): complete notebook specification, dependency order, task outputs, alternatives, validation, execution, and submission checklist.
2. [analysis-decisions.md](analysis-decisions.md): all accepted Q1-Q42 with reasons and alternatives.
3. [calculation-contract.md](calculation-contract.md): exact A-F counting rules, formulas, GM cases, and worked synthetic checks.
4. [ADR index](adr/README.md): 12 accepted records and subsequent refinements.
5. [CONTEXT.md](../CONTEXT.md): agreed domain vocabulary.

The latest [documentation audit](DOCUMENTATION_AUDIT.md) verifies coverage against the entire session and assignment requirements. [Source inspection](source-inspection.md) preserves the verified input fingerprint and data-quality counts, including overlapping blank/duplicate exclusions.

The source instructions are in `MSBT&AI_F2026_Assignment_1.docx`. Use only `sample_data.csv` as the complete corpus. The user explicitly excluded `CollabNotebook.ipynb`; do not inspect or reuse it.

## Decisions that must survive the handoff

- A-E use post-based counts and a common retained-post denominator. Attribute themes have subattributes. All marques are eligible; a supplied brand/model dictionary is not the starting point.
- Retain original text and correct only high-confidence artifacts; ambiguous references can remain unresolved. Quoted claims count only when substantively engaged with.
- GM-only references expand to Chevrolet, Buick, GMC, and Cadillac unless a child or clear model is identified. Provenance and no-expansion sensitivity are required.
- B uses same-post lexical co-occurrence. C's primary numerator is a competitive relation; also compute semantic-mention co-occurrence to isolate recognition effects.
- GM does not generate a semantic clique among children. A supported GM-to-other relation expands endpoints. Vehicle attributes can inherit to children with flags and sensitivity.
- D prefers validated semantic input, otherwise lexical input. Use inverse-one-plus-lift dissimilarity, 2D nonmetric MDS, reported stress, and clustering of full distances with two to four groups.
- E selects five brands by stable cluster coverage and prevalence before viewing scores. Use five supported distinct themes, semantic feature targets, direction where clear, and linked rates/lift.
- F considers every reliably identified marque. Count each author once per marque if any concrete or conditional ownership desire occurs during the period; show the categories, post counts, and discussing-author fractions separately. Flag later rejection. **GM-only desire does not transfer to child marques.**
- G gives about three evidence-supported actions with limitations and a test of value. Historical findings are not proof of current preferences or causal sales effects.
- The total API budget is **$15**, including discovery, pilot, retries, fallback, and later tasks. The user has stated that an OpenAI key is available. Initial model strategy: Luna; Sol only if quality and budget justify it. Verify exact availability and current pricing before implementation.
- After mappings/themes are fixed, share a structured extraction pass for C/E/F, splitting only if the pilot reveals quality problems. Count shared usage once.
- Submit a notebook with outputs, extraction results, prompts, usage logs, and completed human audit labels embedded. Default execution uses saved results with the original CSV; optional explicit regeneration uses a key and budget controls. Keep original-generation and incremental-rerun costs separate.

## Manual review commitments

The 100-post pilot runs automatically. Review 20 difficult development posts, freeze the prompt, and use 40 separate random audit posts for independent evaluation. Do not label the development cases as untouched test data.

For E, inspect two supporting posts for each of the five strongest associations discussed (up to 10 additional posts). For F, inspect up to 10 predicted positives and 10 difficult nonpositive/uncertain cases. Reuse already-reviewed posts. Total agreed review is up to 90 distinct posts with no overlap, fewer with reuse.

These reviews have not happened. Do not fabricate annotations or describe an LLM-generated label as a human judgment. Extra targeted cases test failure modes and claim meaning, not unbiased overall accuracy.

## What remains before a final deliverable

- Build and run the notebook when the user requests implementation.
- Supply team member names before submission and obtain actual human audit annotations.
- Choose and document routine implementation details: NLP tooling, cleaning/quote rules, duplicate key, exact metrics, quality/coverage gates, dissimilarity-compatible clustering method, stability/fallback criteria, uncertainty sensitivity, cache encoding, retries, and conservative budget reservations.
- Set these choices before selecting favorable results. They were not individually chosen by the user; do not present them as if they were.
- Produce actual frequency tables, matrices, maps, positioning, aspiration ranking, and recommendations.
- Recheck the assignment instructions against the completed notebook. The document states September 28 at 11:59 p.m. for Fall 2026.

If full-corpus extraction of acceptable quality would exceed $15, expose the conflict rather than silently sampling or overspending. If a holdout-driven prompt revision occurs, preserve the earlier audit result or use a fresh holdout for an independent evaluation.

## Interview provenance

The user invoked `grill-with-docs`, which composes `grilling` and `domain-modeling`. Skills live under `C:/Users/Rohan Verma/.codex/skills/`. The user asked for ADRs to be recorded as choices were finalized, and all 42 recommendations were accepted or explicitly revised during the conversation. Key revisions: no human approvals during notebook execution; GM expansion with task-specific exceptions; $15 instead of the proposed $25 budget; and targeted review additions for E/F.

The detailed record is authoritative. The next session should follow the user's new request using this documentation, rather than treating old pending-question text from earlier conversation turns as current.


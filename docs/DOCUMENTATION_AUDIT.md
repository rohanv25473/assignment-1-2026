# Documentation audit against the full design session

Audited September 28, 2026 against the available full conversation, the original assignment document, all 12 ADRs, the glossary, decision record, calculation contract, notebook guide, and handoff.

## Finding

All 42 numbered design choices and their accepted clarifications are recorded. No accepted analytical decision was found missing. This confirms coverage of the agreed methodology, not that every software parameter has been selected or that analysis has been executed. The guide explicitly separates accepted requirements from routine implementation refinements and missing empirical inputs.

## Decision coverage

| Session decisions | Preserved content | Primary records |
| --- | --- | --- |
| Q1-Q5 | Sample treated as original; post prevalence and author coverage; model aliases and uncertainty; product attributes; all-marque eligibility | Decision record, ADRs 0001/0002/0006 |
| Q6-Q8/Q8a | Conservative cleaning; corrected quote policy; GM expansion only when no child is identified; child marques remain separate | ADRs 0002/0003, calculation contract |
| Q9-Q12 | Corpus-derived discovery; automated execution; hierarchical themes; important attributes; base manual review | ADRs 0006/0007 |
| Q13-Q15 | Lexical mentions, same-post pairs, common denominator, unsmoothed lift, counts, GM sensitivity | ADR 0001, decision record, calculation contract |
| Q16-Q20 | Semantic relation definition, full corpus, relation boundaries, GM relation exception, evidence and uncertainty | ADR 0004, calculation contract |
| Q21-Q23 | Model strategy, explicit $15 revision, pilot and final audit distinction, quantified matrix comparison | ADRs 0007/0008, decision record |
| Q24-Q26 | Conditional primary map, inverse-one-plus-lift dissimilarity, nonmetric MDS, full-distance clustering | ADR 0005 |
| Q27-Q32 | Five-brand selection before scores; feature links and direction; plural/ambiguous targets; GM attribute inheritance; extra positioning checks | ADR 0009 |
| Q33-Q38 | Aspiration definition and universe; unique-author ranking; GM desire exception; period-level desire; extra validation | ADR 0010 |
| Q39-Q40 | About three evidence-qualified client actions, robustness and historical scope | ADR 0011 |
| Q41-Q42 | Shared C/E/F extraction, embedded saved results, explicit regeneration, cost provenance | ADR 0012 |

## Corrections and refinements checked explicitly

- The user corrected Q7: substantive discussion is primary; simple row-anywhere counting is only an alternative.
- The user rejected runtime human approvals, then accepted actual manual review before submission. No document treats generated annotations as completed human review.
- The $15 cap supersedes the earlier $25 suggestion and applies to the cumulative assignment API work, including pilot and retries.
- Q22 uses the 20 difficult cases for development, plus 40 independent random audit cases. Q32/Q38 subsequently allow up to 30 additional targeted posts, for at most 90 distinct reviewed posts with no overlap.
- GM has distinct mention, competitive-relation, attribute-inheritance, and aspiration rules. The aspiration exception was accepted after discussion of the alternative's disadvantages.
- The primary semantic numerator differs from ordinary co-occurrence. The intermediate semantic-mentions-only matrix prevents that change from being misrepresented as an accuracy improvement.
- Final default reruns use saved outputs and do not silently incur new API spend; original generation costs remain reported.

## Assignment requirement coverage

| Instructor requirement | Documented implementation evidence |
| --- | --- |
| Code and main outputs | Per-task output lists and notebook acceptance checklist |
| What, why, and at least one alternative | Q1-Q42 decision table, ADRs, and task-specific guide alternatives |
| Toy checks and manual semantic inspection | Worked synthetic calculations; pilot/holdout/targeted review plan and provenance |
| Frequency tables, both lift matrices, reconciliation, MDS, aspiration details | A-F output lists and exact calculation definitions |
| LLM model, calls, input/output/total tokens, approximate cost | Shared usage schema, cumulative ledger, original versus rerun accounting |
| Whether semantic intelligence was worth its cost | Explicit cost-benefit assessment section linking audit findings, measurement changes, and managerial consequences |
| Limitations and least-trusted analyses | Task G and submission checklist; method-dependent conclusions and source limitations |
| Team names inside the notebook | Required, with names still to be supplied |

## Changes made during this audit

1. Made USA scope, Canvas submission, and optional full sentiment analysis explicit.
2. Corrected the guide's computational sequence so the independent audit informs the selection of Task D's primary matrix; the earlier sequence placed the final audit after the map choice.
3. Added a dedicated assessment of whether semantic interpretation justified its cost, beyond the already-recorded cost ledger requirement.
4. Clarified that valid evidence can name a model, alias, or parent rather than contain a literal canonical-brand token.
5. Reverified input checks and preserved them in [source-inspection.md](source-inspection.md), including the overlap between blank and duplicate records: 5,986 unique nonblank raw records, not 5,983.

These changes clarify implementation and preserve evidence; they do not alter accepted analytical choices.

## What was never finalized in the interview

The exact NLP packages, correction expressions, quote-segmentation algorithm, duplicate key, numeric evaluation/coverage gates, cluster linkage and stability metric, comparison cutoffs, retry policy, cache encoding, and uncertainty sensitivity mechanics were not chosen by the user. The guide instructs the implementer to document these before interpreting results and to seek input only if a choice materially changes scope, measurement, or budget.

Actual model availability/pricing must be checked when implementing. Team names, actual human audit annotations, and all empirical analysis outputs remain to be obtained. Do not fill these gaps with fabricated results or silently describe unchosen parameters as user-approved decisions.

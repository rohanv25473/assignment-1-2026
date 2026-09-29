# Assignment 1: agreed notebook design

All 42 design questions are accepted. This guide translates the interview into a notebook specification. It records what to build and how to justify it; it contains no empirical findings. The source data has been inspected, but API extraction, manual annotation, statistical analysis, and notebook construction remain to be performed.

Use [analysis-decisions.md](analysis-decisions.md) for the complete what/why/alternative record, [calculation-contract.md](calculation-contract.md) for formulas and worked examples, and [the ADRs](adr/README.md) for consequential design choices. The original assignment is `MSBT&AI_F2026_Assignment_1.docx`.

## Objective and constraints

Act as an analytics consultant to JD Power studying entry-level luxury-car discussion in the USA. Discover entities and attributes from the corpus, compare lexical and semantic competitive associations, visualize competition, assess positioning and aspiration, and produce about three evidence-qualified recommendations.

- Use only `sample_data.csv`, treated as the complete original assignment corpus. Do not scrape or seek another corpus.
- Ignore the existing `CollabNotebook.ipynb`; the user explicitly excluded it from this design task.
- Explain each major choice with a rationale, a reasonable alternative, validation evidence, and limitations. A polished implementation is not a substitute for this reasoning.
- The final notebook executes without human classification or approval prompts. Manual review is a separate, pre-submission activity whose completed annotations are embedded.
- Use an OpenAI key for generation, with **$15 total API spend** across discovery, pilot, full extraction, fallback calls, and retries. Default submitted-notebook execution reuses saved results.
- Include team names inside the notebook, not in the filename. Names still need to be supplied before submission.
- The assignment document states submission of a Python notebook on Canvas by September 28, 11:59 p.m., for Fall 2026. Do not substitute the date of execution for the period represented by the data.
- Full sentiment analysis is optional. Criticism still contributes nonnegative mention counts; attribute direction is a separate descriptive label and never turns a lift count negative.

## Computational order and notebook presentation

The displayed notebook should follow A-G, but it can reuse a shared extraction result across sections. A practical dependency order is:

1. Load and profile the original CSV; establish the common retained-post universe.
2. Discover candidate names and phrases, create the corpus-derived mappings and theme hierarchy, and define extraction rules.
3. Reserve the final random audit; run the 100-post pilot and inspect the 20 targeted development cases. Check all output types, adjust, and freeze the final prompt and schema.
4. Run the shared extraction for all usable posts within the budget, with recorded failures and provenance. Reuse valid identical pilot outputs only if they match the final prompt/model/schema.
5. Produce Task A frequencies and lock a single 10-brand set for B/C. Frequency outputs may reuse the shared labels; identify the exact label source rather than silently mixing lexical and semantic counts.
6. Compute B/C and complete the independent random audit of the frozen extraction before deciding whether C's quality supports the primary D map. Apply the documented coverage/quality gates and build D. Select E's five brands before looking at positioning scores.
7. Produce E/F outputs and their targeted evidence checks, then interpret G and assemble the saved-results notebook. E/F extraction labels can be audited with the same frozen-pass random sample before their aggregate findings are interpreted.

This order avoids repeated calls and allows F to consider all discovered marques. Do not limit the shared extraction schema to the top 10 if that would discard aspiration toward other brands. If new canonical labels appear after freezing, record a versioned refinement and determine which cached results require regeneration; do not silently mix taxonomies.

## Input preparation and audit trail

The source has 6,000 records, three fields, and no header. The first record is data. Inspection found 329 usernames, 9 blank texts, and 8 exact duplicate rows. A documentation-audit recheck found 5,986 unique nonblank three-field records: three duplicate occurrences overlap with blank-text exclusions. See [source-inspection.md](source-inspection.md) for the source fingerprint and checks. Recompute and report actual exclusions when implementing; this provisional count does not predetermine any further cleaned-empty-text policy. Do not remove equal text from different authors without justification.

Retain original row IDs, username, date label, raw text, cleaned text, exclusion reason, and cleaning-rule provenance. The date labels appear to encode months across 2006-2011; verify the interpretation before relying on chronology. Their coarseness is one reason F measures desire expressed during the period.

The apparent artifacts include `kia hyundai` next to quotation marks, `toyota d` in ordinary prose, and repeated `mercedes-benz benz`. Use narrow, example-supported corrections and compare results before and after cleaning. Do not erase genuine marque references by applying a global replacement without checking context. Retain uncertain corruption as a limitation.

Include all retained posts in the lift denominator, including posts with no target marque. Exclude clearly quoted-only references, but include a quoted claim that the author substantively engages with. The baseline uses transparent deterministic approximations; semantic extraction uses context. Preserve attribution uncertainty.

## Task A: entity and attribute discovery

Use NLP phrase extraction and context clustering to surface names and attribute phrases from the corpus. Use selective LLM interpretation to reconcile ambiguous groups. No supplied brand/model dictionary is the starting point; the resulting corpus-derived lexicon is a legitimate output used by the lexical baseline.

Map unambiguous models and aliases to consumer-facing marques. Keep Lexus/Toyota, Acura/Honda, and similar marques separate. Abstain when context does not resolve an ambiguous form. All marques are eligible for the top 10, including mass-market comparison points.

Rank brands by distinct usable posts and show author coverage. Discover broad themes with nested subattributes, and rank themes by distinct-post prevalence with author coverage. Count a theme once per post even when several of its subattributes occur. Keep purchase desire and general praise outside the product-attribute taxonomy.

Required outputs: candidate-to-canonical mapping with examples; theme/subattribute hierarchy; brand and attribute counts and prevalence; author coverage; top-10 brand table; cleaning impact; ambiguous/unresolved examples. The actual taxonomy and winners cannot be prefilled from examples used during the interview.

Alternative to explain: raw mention counts, literal brand names only, preselected luxury brands, flat attributes, or unrestricted topics.

## Task B: transparent lexical lift

Match cleaned text with the approved corpus-derived names and unambiguous aliases. Use binary brand presence and unordered same-post pairs. Calculate unsmoothed lift with all retained posts as the denominator, blank the diagonal, distinguish zero co-occurrence from undefined zero-marginal cases, and show underlying pair counts.

Required outputs: the 10-by-10 lift matrix, pair-count matrix, marginal counts, concise definition of mention/co-occurrence, and a hand-checked toy example. Report the effect of disabling GM expansion. High lift with few observations is weak support for a managerial claim.

Alternative to explain: sentence windows, literal names only, smoothing, or counting every quote anywhere in the row.

## Task C: semantic attribution and reconciliation

The shared LLM pass records substantive brand references and supported competitive relations. Relations include explicit comparison, shared evaluation, and consideration together for purchase; both praise and criticism count. Bare lists and unrelated remarks do not qualify. Keep evidence spans and allow uncertainty.

Produce the primary relationship-filtered semantic lift matrix and an intermediate semantic-mentions-only co-occurrence matrix. The latter isolates recognition changes; the former also changes the numerator to a narrower event. Use consistent semantic marginals, as defined in the calculation contract. A lower semantic ratio is not automatically an error correction or evidence of model superiority.

Required outputs: semantic counts and primary matrix; intermediate comparison; all 45 off-diagonal pair comparisons using counts, lift differences, rank correlation, and strongest-pair overlap; representative posts explaining major changes; and consequences for apparent closest competitors. Show uncertainty volumes and GM sensitivity.

Alternative to explain: treating any two substantive mentions as a competitive pair, forced classification, or processing only a sample.

## GM rules across tasks

These rules are deliberately different and must not be silently unified.

| Analysis | Accepted GM treatment |
| --- | --- |
| Brand mentions | A GM-only reference adds Chevrolet, Buick, GMC, and Cadillac. Identifiable children or clear models suppress inference of the other children. Other brands in the post still count normally. |
| Lexical pairs | Expanded children co-occur under the normal same-post rule. Even a GM stock post can inflate these pairs; retain the sensitivity check. |
| Semantic competitive pairs | GM alone creates no child-to-child clique. A supported GM-versus-Toyota relation expands to four child-to-Toyota relations when no child is identified. |
| Vehicle attributes | Clear GM vehicle attributes inherit to children, marked inherited. Corporate-finance statements do not become vehicle features. Show an inherited-link-off sensitivity. |
| Aspiration | GM-only desire stays unresolved at child level. No child receives aspiration without an identifiable child reference, even though mention denominators retain the earlier expansion. |

## Task D: MDS and clusters

Prefer C's relation-filtered matrix if the audit and pair coverage support it; otherwise use B and explain the fallback. Convert finite off-diagonal lift to `1/(1+lift)`, explicitly set self-distances to zero, and fit a two-dimensional nonmetric MDS representation. Use reproducible starts and report stress.

Cluster the full dissimilarity matrix, then color the mapped points. Compare two to four clusters using fit and interpretation. Do not derive clustering solely from the potentially distorted 2D coordinates. Axes have no intrinsic feature labels; rotating or reflecting a map does not change the relationships.

Required outputs: labeled primary map with clusters, stress and cluster-selection justification, the alternate-measurement map, and changed neighbors/memberships. Discuss whether the projection and underlying pair support allow the apparent structure to be trusted.

Alternative to explain: metric MDS with another transform, clustering the 2D display, or committing to a preferred matrix regardless of audit quality.

## Task E: brand-attribute positioning

Select five brands from the fixed top 10 before inspecting attribute scores: take the most prevalent member of each stable D cluster and fill remaining slots by prevalence. Choose five supported, distinct attribute themes from A. If cluster stability does not support that selection rule, document a defensible fallback before reviewing the positioning scores.

Use semantic brand-attribute links. Assign a shared attribute to each clear target; leave it unassigned if an antecedent cannot be resolved. Report linked counts, within-brand rates, and linked association lift for the 25 cells. Compare with a lexical same-post alternative. Keep direction and evidence with subattributes; an association with price or reliability alone does not imply favorable positioning.

Required outputs: five-by-five association display, linked counts/rates, selection justification, illustrative attribution examples, inherited-GM sensitivity, and an evidence-based interpretation of positioning.

Alternative to explain: selecting the five most prevalent brands regardless of cluster, co-occurrence-only attribution, or direction-free themes without interpretive caution.

## Task F: aspiration

Identify the author's desire to buy or own, distinguishing concrete intent from conditional/dream desire. Exclude mere praise, current ownership alone, advice to others, negated desire, and quoted-only wishes. Evaluate every reliably identified marque discovered in A, not just the top 10.

Rank by distinct authors with any qualifying desire during the period, once per author-brand. Also show concrete and conditional author counts, post counts, and the fraction of discussing authors with desire. Category sets can overlap, and authors can desire multiple marques. Flag later rejection or conflicting evidence; this measure is not a current purchase forecast. GM-only desire does not inherit to children.

Required outputs: operational definition and borderline examples, aspiration counts and ranking, evidence for the leading marque(s), category and denominator comparisons, conflict/unresolved counts, and audit errors. Handle ties and sparse support explicitly. Do not claim a unique, well-established winner if the evidence does not support one.

Alternative to explain: purchase plans only, a single keyword, total-post ranking, fraction-only ranking, latest-stance inference, or transferring parent desire to all children.

## Task G: recommendations

Produce about three recommendations after seeing the results. Each names a client action, supporting evidence, a limitation that could change the advice, and a way to test its value. Combine findings where useful rather than forcing one recommendation per task.

Label robust conclusions and method-dependent conclusions. Explain which sensitivity changes the latter and what further evidence would help. Focus historical evidence on benchmarking and research priorities; do not imply current-market representativeness or causal sales effects.

Required output: a compact recommendation table with action, evidence references, robustness/limitations, and follow-up test. Include the analyses trusted least and why.

## Validation and manual-review plan

| Set | Purpose | Quantity and interpretation |
| --- | --- | --- |
| Automatic pilot | Prompt/schema/cost development; check C/E/F outputs separately | 100 posts, not 100 manual labels |
| Targeted development review | Investigate artifacts, aliases, quotes, GM, and semantic errors; revise before freezing | 20 posts within development; excluded from independent accuracy estimates |
| Independent random audit | Evaluate the frozen extraction on a fixed-seed sample | 40 posts kept out of pilot/prompt development; report uncertainty and observed support |
| Positioning support review | Check meanings behind the five strongest associations discussed | Two posts each, at most 10 extra; reuse earlier reviewed posts |
| Aspiration diagnostics | Examine predicted desires and hard misses | Up to 10 predicted positives plus 10 nonpositive/uncertain cases; reuse earlier reviewed posts |

The agreed workload is up to 90 distinct reviewed posts when there is no overlap, fewer when cases are reused. Earlier references to 60 described the base audit before E/F additions. Selected examples are diagnostic and must not be pooled with the random sample to claim an overall error rate. Two supporting posts do not prove an entire association.

For every reviewed item, save post ID, expected labels, automated labels, evidence, error type, review-set membership, and reviewer/provenance. Humans must actually perform the required review; LLM-generated expected labels cannot be passed off as human inspection. If the final holdout motivates prompt changes, preserve the reported pre-change result or use a fresh holdout for a new independent estimate.

Perform toy checks for marginals, co-occurrence, lift, zeros, repeated mentions, GM rules, linked-attribute rates, and unique-author aspiration. The calculation contract contains a worked synthetic example. Tests verify arithmetic and invariants; semantic quality requires inspected evidence.

## Shared records and provenance

The exact schema is an implementation choice, but it needs these contents:

| Record | Minimum content |
| --- | --- |
| Brand reference | Post ID, canonical marque or unresolved candidate, evidence span, direct/model/alias/GM provenance, certainty |
| Competitive relation | Post ID, unordered pair, relation type, evidence, certainty, inherited-parent provenance if applicable |
| Attribute mention/link | Post ID, theme, subattribute, clear target(s) or unresolved target, evidence, optional clear direction, inherited flag |
| Aspiration | Post ID, author, identifiable marque or parent-only target, concrete/conditional/nonqualifying/uncertain status, evidence, conflict flags |
| Usage | Step or shared-task group, call/request identifier, model, input/output/total tokens, cached-input breakdown where available, retry status, price version, approximate cost |
| Run provenance | Input hash, preparation rules, mappings/taxonomy version, prompt/schema version, model/settings, random seeds, completed/failed coverage |

Keep all discovered marques available for F. Validate brand names against canonical IDs and check that evidence spans actually occur in the supplied text. Evidence may contain a model, alias, or GM parent reference instead of the canonical child brand name; validate that provenance rather than requiring a literal canonical token. A missing response is an execution failure, not a negative label. The full-corpus analysis cannot silently drop such posts and still claim completion.

## Model, cost, and saved execution

The accepted initial model strategy is GPT-6 Luna with structured outputs and GPT-6 Sol as a conditional quality fallback. Verify exact model IDs, availability, current API behavior, and prices at implementation time using official documentation; no API result or current account entitlement has been verified by this design session.

Project full-run cost from the pilot before starting. Track a persistent cumulative ledger across notebook restarts and include retries, changed-prompt calls, and fallback calls. Reserve enough budget for the next request using conservative input and maximum-output estimates; leave a safety buffer. A platform spend control is additional protection, not the sole guarantee, because enforcement can lag. If the budget prevents full-corpus completion at acceptable quality, expose that conflict rather than silently sampling or overspending.

A shared call supporting C/E/F is counted once. Show a joint shared-extraction cost row; if assigning a portion to individual tasks, label that allocation as an estimate and reconcile it to the actual total. Do not triple-count tokens to meet the per-step reporting requirement.

The submitted notebook includes outputs and embedded saved extraction records, prompts, usage logs, and completed audit labels. With the original CSV present, default execution reproduces calculations and plots from saved data, without requiring a key or fresh paid requests. An explicit regeneration setting enables API calls with credentials supplied securely. Input/provenance mismatches must be visible rather than silently serving stale outputs. Report original generation usage separately from new execution usage; saved reruns have no new calls but the original generation was not free.

## Was semantic interpretation worth its cost?

Include an explicit assessment after the usage table; reporting dollars alone does not satisfy the assignment. Connect observed audit errors, changed brand/pair attribution, altered neighbors/clusters, and any changed positioning or aspiration interpretation to the additional semantic work. State whether those changes materially affect a recommendation. An unchanged recommendation can support the conclusion that a simpler baseline was sufficient for that particular decision, even if the semantic output is more detailed.

For selective discovery and the shared C/E/F pass, state the capability gained, observed error patterns, actual cost, and limitation of the assessment. Count shared costs once and do not attribute improvements caused merely by a narrower pair definition to model accuracy. If no direct comparator isolates a particular semantic task's benefit, say so instead of claiming a measured return on that portion of the cost.

## Routine choices still to document during implementation

The interview settles analytical intent, not every parameter. The implementer should choose and explain exact NLP tools, correction patterns, duplicate key, ranking tie handling, validation metrics, evidence-span schema, retry logic, and cache encoding. Choose numerical quality/coverage gates before selecting favorable results. Choose a dissimilarity-compatible clustering algorithm, fit statistic, stability criteria, and MDS restart settings. Define how uncertain-label sensitivity is computed and how E's brand selection falls back when clusters are unstable.

Do not attribute these unchosen details to the user. Resolve routine choices with documented reasoning; return to the user if a choice changes the accepted measurement, budget, or scope. Team names and actual human audit annotations remain necessary inputs for final submission.

## Submission acceptance checklist

- All seven task sections contain code, main outputs, interpretation, method rationale, and a considered alternative.
- Source schema and retained-post denominator are correct and reproducible; raw evidence and cleaning provenance are preserved.
- Brand/theme tables, two primary lift matrices, the intermediate reconciliation, maps/clusters, positioning, and aspiration details are displayed.
- Semantic-pair filtering and the GM exceptions are explicit; an apparent method improvement is not inferred solely from different numbers.
- Toy calculations and real manual audit evidence are included, with development and held-out review distinguished.
- API model/call/token/cost reporting is complete, shared costs are counted once, and total generation spending respects $15.
- The notebook explicitly evaluates whether added semantic interpretation changed measurement or managerial advice enough to justify its cost.
- Default reruns use valid saved records, and optional regeneration is explicit.
- Recommendations distinguish robust from method-dependent evidence and discuss the least trustworthy analyses.
- Team names are inside the notebook. No credentials are embedded. All claimed empirical findings come from executed analysis.

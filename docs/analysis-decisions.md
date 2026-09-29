# Assignment 1 analysis decisions

All 42 interview decisions are accepted: Tasks A-G (Q1-Q40) and notebook execution (Q41-Q42). This is a design record, not a results report: no final rankings, lift matrices, model outputs, or human audit labels have been produced. Start with [the notebook design guide](NOTEBOOK_DESIGN.md), use [the calculation contract](calculation-contract.md) for formulas, and read [the session handoff](SESSION_HANDOFF.md) for the current work status.

## Corpus and known risks

- Treat `sample_data.csv` as the complete assignment corpus, despite the assignment document naming `Edmunds.csv`.
- The CSV has 6,000 data rows and no header. It contains 9 blank-text rows and 8 exact duplicate rows. The pipeline will establish the final usable-post count after applying the agreed exclusions.
- A later read-only check verified 5,986 unique nonblank three-field records; blank and duplicate exclusions overlap. This is provisional before any further justified exclusions. See [source-inspection.md](source-inspection.md).
- Text contains flattened quoted replies and apparent preprocessing artifacts. Examples include `kia hyundai` beside quotation marks, `toyota d` where "said" would fit, and long runs of `mercedes-benz benz`. The original text must remain available for inspection.
- Date labels appear to span 2006-2011. Conclusions describe this historical discussion corpus, not the current automobile market.

## Task A: brands and attributes

| Choice | Agreed decision and reason | Reasonable alternative | Validation or consequence |
| --- | --- | --- | --- |
| Q1 Corpus | Analyze only the supplied `sample_data.csv` and treat it as the original assignment file. | Wait for or assume a larger `Edmunds.csv`. | State the scope explicitly in the notebook. |
| Q2 Brand importance | Rank marques by the number of distinct usable posts that reference each; report author coverage as a check on prolific posters. Repetition within one post does not add weight. | Rank by raw token frequency. | Compare prevalence with author coverage. |
| Q3 Models and aliases | Map clear models, abbreviations, and variants to their parent marque. Leave ambiguous forms unresolved unless context supports the mapping. | Map every possible model token aggressively. | Audit clear and ambiguous examples and report unresolved frequency. |
| Q4 Product attributes | Count car features and evaluative dimensions. Keep purchase intent for Task F and general praise separate. | Use an unrestricted topic list. | Inspect whether extracted phrases really describe car attributes. |
| Q5 Eligible brands | Let all automobile marques compete for the top 10, including mass-market comparison brands. Keep consumer-facing marques separate from corporate parents. | Restrict the list to a preselected luxury segment. | Explain whether each resulting marque is a direct competitor or comparison point. |
| Q6 Text artifacts | Preserve raw text; apply a documented set of high-confidence corrections; leave uncertain corruption unresolved. | Count every literal brand-looking token. | Inspect examples of every rule and compare rankings before and after cleaning. |
| Q7 Quoted text | Primary counts reflect brands the author substantively discusses, including quoted claims they engage with. Exclude clearly quoted-only references. | Count every brand anywhere in the row. | Use deterministic quote rules for Task B, semantic review for Task C, and report residual ambiguity. |
| Q8 GM | When `GM` appears without any identifiable Chevrolet, Buick, GMC, or Cadillac reference, add all four marques. When one or more children are identified by name or clear model, add only those children. | Keep GM as a parent-only entity. | This literal rule can assign all four to nonvehicle discussion; show results with expansion disabled as a sensitivity check. |
| Q9 Discovery | Generate name and attribute candidates from the corpus using NLP phrase extraction and context clustering, then use an LLM selectively to reconcile ambiguous groups. Discovery and reconciliation are automated; humans inspect a sample before submission. Do not require human approval of mappings during execution or start with a supplied brand/model dictionary. | Have an LLM label every post during discovery. | Record the corpus-derived mapping and examples; separately document the one-time manual audit. |
| Q10 Attribute hierarchy | Use broad themes with specific subattributes, such as performance with acceleration and handling. | Use only flat labels or one broad performance bucket. | Preserve subattribute frequencies so aggregation is visible. |
| Q11 Important attributes | Rank themes by distinct-post prevalence, show author coverage and leading subattributes, and select five supported, distinct themes for Task E. | Select the five most frequent themes regardless of overlap. | Explain why selected themes add distinct positioning information. |
| Q12 Audit | Inspect 40 fixed-seed random posts plus 20 targeted difficult posts involving models, quotes, artifacts, or GM. Q22 later clarified that the 20 targeted posts are development cases and the 40 random posts are a separate final holdout. | Use a small convenience sample. | Record expected and automated labels and error types. Only the unseen random sample estimates general error rates; the targeted cases cannot be described as independent validation. |

## Task B: lexical lift baseline

| Choice | Agreed decision and reason | Reasonable alternative | Validation or consequence |
| --- | --- | --- | --- |
| Q13 Lexical mentions | Match cleaned text against the canonical Task A brand/model/alias mapping. Use only unambiguous aliases, count each marque once per post, and apply deterministic quote rules. | Match literal brand names only. | Inspect false positives from quotes and false negatives from aliases. |
| Q14 Co-occurrence | Two distinct top-10 marques in the same usable post form one pair, independent of their distance or repetition. Use every usable post in the denominator, including posts with no top-10 brand. | Sentence-level co-occurrence. | Verify counts and lift manually on a toy corpus. |
| Q15 Lift | Report `N * n_AB / (n_A * n_B)` without smoothing, pair counts beside the lift matrix, blank diagonal, and zero for unobserved pairs. Interpret high lift with low pair support cautiously. | Add a smoothing constant. | Recompute with GM expansion disabled; use toy-data checks. |

## Task C: semantic lift and reconciliation

| Choice | Agreed decision and reason | Reasonable alternative | Validation or consequence |
| --- | --- | --- | --- |
| Q16 Semantic pair | The primary semantic matrix counts a pair when the author meaningfully connects the marques. Also compute an LLM-mention-only, same-post check to separate entity-recognition changes from pair-rule changes. | Treat any two substantive mentions as the only semantic pair rule. | Explicitly state that the primary Task C numerator is a stricter relation event than Task B's co-mention numerator. |
| Q17 Coverage | After a pilot, process every usable post for the final semantic matrix. | Estimate lift from a stratified sample. | Log all API calls and usage; project cost before the full run. |
| Q18 Relation boundary | Count explicit comparisons, shared evaluations, and brands considered together for purchase. Praise and criticism both count. Exclude bare lists and unrelated remarks. | Require literal "versus" or explicit purchase language. | Inspect boundary cases in the manual audit. |
| Q19 GM and relations | Apply the agreed GM expansion to brand counts. Do not create relations among the four GM marques from a lone `GM` mention. A relation between GM and another marque expands to each inferred child-to-other pair. | Make all four children a semantic clique whenever GM appears. | Explain GM-driven B/C disagreements and show the no-expansion sensitivity. |
| Q20 Uncertainty | Permit `uncertain`, require supporting text spans, exclude uncertain labels from primary counts, and report their volume and a sensitivity analysis. | Force every case into a definite label. | Audit abstentions and borderline examples. |
| Q21 Model and budget | Use an OpenAI API key. Pilot GPT-6 Luna with structured outputs; consider GPT-6 Sol only if the quality audit justifies it. Cap total notebook API spend at $15, including pilot, retries, and later tasks. | Use a stronger model for every post or leave cost open-ended. | Log model, call count, input/output/total tokens, and estimated cost by step; stop conservatively before the cap. Check current pricing at execution time. |
| Q22 Pilot and audit | Run an automatic 100-post pilot, inspect the 20 difficult cases from Task A, revise and freeze the prompt, then process the corpus. Audit 40 separate random posts after freezing. No human input is needed when the final notebook runs. | Revise the prompt after seeing the final random audit. | Treat pilot cases as development checks, not an unbiased accuracy estimate. |
| Q23 Comparison | Compare all 45 unordered brand pairs with pair counts, lift differences, rank correlation, and strongest-pair overlap. Inspect representative posts for major changes and note changes to apparent closest competitors. | Compare matrices by eye alone. | Separate entity-resolution effects, relation-filter effects, artifacts, and GM effects. |

## Task D: competitive map

| Choice | Agreed decision and reason | Reasonable alternative | Validation or consequence |
| --- | --- | --- | --- |
| Q24 Preferred matrix | Use Task C's semantic matrix for the primary map if its manual audit supports the classifications and there are enough observed pairs to map. Show the Task B lexical map as a sensitivity check. If Task C is too sparse or unreliable, use Task B as primary and explain the switch. | Preselect one matrix regardless of quality or coverage. | Compare visible neighbors and clusters across the two measurement choices. |
| Q25 Distance and MDS | Convert lift to dissimilarity as `1 / (1 + lift)` and use nonmetric MDS in two dimensions. This handles zero lift and preserves the rank ordering of associations. | Log-transform lift and use metric MDS. | Use a fixed seed and multiple starts; report stress and avoid assigning inherent meaning to the map axes. |
| Q26 Clustering | Cluster the full brand dissimilarity matrix and color the resulting groups on the MDS plot. Compare two to four clusters using fit and interpretability, and flag membership changes between Task B and C. | Cluster the plotted two-dimensional coordinates. | Check whether map distortion or measurement choice changes the visible groups. |

## Implementation refinements

No interview questions remain unanswered. Numerical quality gates, exact clustering linkage, and other routine implementation details must still be chosen and justified before interpreting outputs; they are not user-selected parameters. See [the design guide](NOTEBOOK_DESIGN.md).

## Task E: brand-attribute positioning

| Choice | Agreed decision and reason | Reasonable alternative | Validation or consequence |
| --- | --- | --- | --- |
| Q27 Five brands | Select from Task A's top 10 before inspecting brand-attribute scores. Take the most prevalent brand in each stable Task D cluster, then fill remaining slots by post prevalence. | Take the five most prevalent brands regardless of cluster. | Covers distinct competitor groups and limits selection based on favorable positioning results. Handling unstable clusters still needs a documented fallback. |
| Q28 Attribution and association | Use evidence-supported LLM brand-attribute links, count each link once per post, and report linked counts, attribute rates within each brand's posts, and association lift using the common post denominator. | Link every brand and attribute appearing in the same post. | Use lexical same-post associations as a sensitivity check and inspect multi-brand examples. |
| Q29 Direction | Use broad themes in the main table while retaining subattributes and supporting passages; label direction only when clearly supported by wording. | Report theme counts alone. | Distinguish positive and negative descriptions without requiring full sentiment analysis; never equate frequent theme discussion with a strength. |
| Q30 Shared/unclear targets | Assign an attribute to every clearly identified target, including clear plural references. Keep an unresolved attribute mention unassigned to any brand. | Assign to every brand in the post. | Audit antecedents and report unassigned mentions; do not convert an unresolved target into a negative attribute finding. |
| Q31 GM inheritance | Expand clear GM-level vehicle attributes to the four children under the earlier GM rule. Mark these links as inherited and provide a sensitivity result excluding inherited links. Corporate finance descriptions are not vehicle attributes. | Retain attributes at GM parent level while expanding only brand counts. | Distinguish inherited from direct evidence; interpretation must disclose the effect of inheritance. |
| Q32 Positioning audit | Check attribution and direction in the existing 20 development and 40 random audit posts; also inspect two supporting posts for each of the five strongest associations discussed, at most 10 additional posts and fewer where already reviewed. | Rely solely on the existing audit even when it does not cover key findings. | Extra examples check claim meaning, not general accuracy or proof of the entire association. Keep them separate from the random error estimate. |

## Task F: aspiration

| Choice | Agreed decision and reason | Reasonable alternative | Validation or consequence |
| --- | --- | --- | --- |
| Q33 Definition | Count the author's expressed desire to buy or own, including clear conditional/dream ownership. Track concrete purchase intent separately from conditional desire. Praise, current ownership alone, recommendations to others, negation, and quoted-only desire do not qualify. | Restrict aspiration to concrete purchase plans. | Audit desire versus admiration, ownership, and hypothetical language. Report category differences rather than equating dreams with imminent sales. |
| Q34 Eligible brands | Evaluate all reliably identified automobile marques discovered in Task A, including those outside its top 10. | Restrict to the same top 10. | Show supporting counts and uncertainty for sparse brands. |
| Q35 Ranking | Rank by distinct authors expressing qualifying desire, one vote per author-brand across concrete and conditional categories combined. Also show category-specific results, aspiration-post counts, and the fraction of each brand's discussing authors expressing desire. | Rank by post count or normalized desire fraction alone. | Limits dominance by repeat posters; shows popularity versus intensity among a brand's discussing audience. This author-level ranking is specific to Task F. |
| Q36 GM desire | Keep GM expansion in mention statistics, but leave GM-only desire unresolved at the marque level. Assign child-brand desire only when a child is identified. | Transfer GM-only desire to all four children with a sensitivity check. | Avoids claiming a specific marque was desired without evidence. This is an explicit exception to attribute inheritance in Task E. |
| Q37 Time and reversals | Count each author-brand once if the author expresses qualifying desire at any time during the corpus period, even with later rejection. Flag conflicting evidence and label this period-level expressed desire. | Infer and rank each author's latest stance. | Coarse dates limit reliable chronology; never describe this measure as current intent or imminent sales. |
| Q38 Aspiration audit | Label aspiration in the existing audit and inspect up to 10 predicted positive posts plus 10 difficult nonpositive/uncertain posts, prioritizing leading brands, negation, conditional desire, ownership, and quotations. Reuse reviewed posts where possible. | Rely solely on the existing random sample. | Targeted checks diagnose errors and missed desires; they do not estimate unbiased overall accuracy or recall. |

## Task G: recommendations

| Choice | Agreed decision and reason | Reasonable alternative | Validation or consequence |
| --- | --- | --- | --- |
| Q39 Actionable format | Present about three recommendations, each with a client action, supporting findings, a limitation that could change the advice, and a way to test its value. Let the evidence determine the recommendations. | Summarize insights without explicit actions, or force one recommendation per analysis. | Connect recommendations to competitive, attribute, and/or aspiration evidence; do not invent results to fill a template. |
| Q40 Robustness and scope | Label conclusions robust when relevant sensitivity checks and supporting evidence sustain them; otherwise label them method-dependent, explain what changes them, and recommend investigation. Use historical findings to guide benchmarking and research priorities. | Show only the preferred method's conclusions without sensitivity distinctions. | Avoid claims about current market preferences or causal sales effects; uncertainty must affect the strength of the recommendation. |

## Notebook execution

| Choice | Agreed decision and reason | Reasonable alternative | Validation or consequence |
| --- | --- | --- | --- |
| Q41 Shared extraction | After corpus-derived mappings and themes are fixed, use a shared structured LLM pass for competitive relations, brand-attribute links, and aspiration. Split the affected extraction if the pilot reveals quality problems, within the $15 total budget. | Independent full-corpus calls for C, E, and F. | Validate each output type separately and account for shared calls once, not three times. |
| Q42 Saved results | Include displayed outputs, saved extractions, prompts, usage logs, and completed audit labels in the submitted notebook. Default reruns reuse saved results; explicit regeneration uses a key and budget controls. The original CSV remains the input. | Make live paid calls on every run. | Distinguish original generation costs from incremental rerun costs. Cache validity must reflect source data, prompt, mappings, and model changes. |

## Notebook evidence to produce later

- Brand and attribute frequency tables, two primary lift matrices with underlying counts, the semantic comparison, MDS map with clustering, brand-attribute positioning, aspiration analysis, and a small set of actionable recommendations.
- Method explanations for every major choice: what was done, why, at least one alternative, and limitations.
- Toy-data checks for counting and lift; recorded manual inspections for semantic tasks.
- Per-LLM-step model, API calls, input/output/total tokens, approximate cost, and an assessment of whether semantic interpretation was worth its cost.
- Team names inside the notebook, not in its filename.

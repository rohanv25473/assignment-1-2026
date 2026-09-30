# Architecture and analytical decision records

All records below are accepted through the interview. The question-by-question history and alternatives are in [analysis-decisions.md](../analysis-decisions.md); the consolidated implementation guide is [NOTEBOOK_DESIGN.md](../NOTEBOOK_DESIGN.md).

| ADR | Decision | Questions |
| --- | --- | --- |
| [0001](0001-post-level-evidence.md) | Post-level evidence, corpus scope, and importance | Q1-Q5, Q13-Q15 |
| [0002](0002-cleaned-substantive-references.md) | Conservative cleaning and substantive references | Q3, Q6-Q7 |
| [0003](0003-expand-gm-only-references.md) | GM expansion and semantic relation exception | Q8/Q8a, Q19 |
| [0004](0004-relationship-filtered-semantic-lift.md) | Relationship-filtered semantic lift and reconciliation | Q16-Q20, Q23 |
| [0005](0005-cluster-from-full-brand-distances.md) | Nonmetric MDS and clustering full distances | Q24-Q26 |
| [0006](0006-corpus-derived-attribute-hierarchy.md) | Corpus-derived names and attribute hierarchy | Q4, Q9-Q11 |
| [0007](0007-automated-pipeline-with-independent-audit.md) | Automated execution, pilot, and independent audit | Q9, Q12, Q22 |
| [0008](0008-api-budget-and-model-strategy.md) | Model strategy and $15 cumulative budget (revised: Claude Haiku 4.5 with Message Batches) | Q17, Q21 |
| [0009](0009-semantic-brand-attribute-positioning.md) | Positioning, attribution, inherited links, validation | Q27-Q32 |
| [0010](0010-aspiration-as-expressed-ownership-desire.md) | Author-level expressed ownership desire | Q33-Q38 |
| [0011](0011-evidence-qualified-client-recommendations.md) | Evidence-qualified client actions | Q39-Q40 |
| [0012](0012-shared-extraction-and-reproducible-submission.md) | Shared extraction and saved default execution | Q41-Q42 |

Later accepted decisions refine earlier records. In particular, Q22 distinguishes development cases from the final audit; Q32 and Q38 add targeted review beyond the base 60; Q36 prevents GM desire from inheriting to children; Q41-Q42 establish shared calls and cached submission. These are deliberate refinements, not unresolved contradictions.

# Share semantic extraction and reproduce results from saved records

Status: accepted, Q41-Q42. Scope: notebook execution and submission.

Once Task A's corpus-derived mappings and attribute themes are fixed, extract competitive relations, brand-attribute links, and aspiration in a shared structured pass. Test each output type in the pilot; split an affected task if combined extraction harms quality, while preserving the $15 total budget. Independent full-corpus calls were considered but repeat input and can create inconsistent attribution.

Submit the notebook with displayed outputs and saved extractions, prompts, usage logs, and completed audit labels embedded. Default execution reuses saved results to reproduce analysis from the original CSV; an explicit regeneration option can make new calls using a key and budget guard. Mandatory paid calls on every rerun were rejected.

## Consequences

Count a shared API call only once in the cost ledger and identify all tasks it supports. Report historical generation costs separately from incremental rerun costs. Cached execution is not evidence that the original analysis cost zero. Check input, prompt, schema, model, and taxonomy provenance before reusing outputs. Do not embed credentials. The approved manual audit remains a pre-submission activity; saved annotations are not yet available and must not be fabricated.

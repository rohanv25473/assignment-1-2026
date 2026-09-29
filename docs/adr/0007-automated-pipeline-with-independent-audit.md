# Automate execution and separate prompt development from the final audit

Status: accepted, revised Q9 and Q12/Q22. Scope: LLM development and validation for A-C.

The submitted notebook must run without interactive human classification or approval. Before submission, run an automatic 100-post pilot, inspect 20 targeted difficult cases, revise the prompt, and freeze it before the full-corpus run. Evaluate on 40 separate fixed-seed random posts kept out of prompt development. This resolves the user's no-HITL requirement while meeting the instructor's requirement for manual inspection.

## Consequences

The existing 20 difficult cases are used for development, so the base workload is 60 reviewed posts, not 100 manual pilot labels plus 60 more. Development examples can demonstrate error patterns and fixes; they cannot support an unbiased final accuracy estimate. Record the final audit as static annotations and results in the submitted notebook. All review remains to be performed; never claim these are already human-validated labels. If the final audit is used to change the prompt, a new untouched evaluation sample is needed for an independent estimate.

Q32 and Q38 subsequently added up to 10 positioning-support posts and up to 20 aspiration diagnostic posts, reusing previously reviewed posts where possible. The final agreed workload is at most 90 distinct reviewed posts without overlap. See [ADR 0009](0009-semantic-brand-attribute-positioning.md) and [ADR 0010](0010-aspiration-as-expressed-ownership-desire.md). These additions are targeted diagnostics, not extra independent random audit observations.

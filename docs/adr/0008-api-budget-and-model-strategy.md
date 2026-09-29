# Constrain all LLM work to a total fifteen-dollar budget

Status: accepted, Q17/Q21 and the user's explicit budget revision. Scope: all assignment API work.

Use an OpenAI API key, begin with GPT-6 Luna and structured outputs, and consider GPT-6 Sol if pilot errors justify a stronger model. Total API spending for the assignment is capped at $15, including development, retries, and later Tasks E-F; this replaces the earlier proposed $25 cap. Estimate full cost from the pilot, track usage by step, and stop conservatively before the available budget is exhausted.

## Consequences

Model escalation must fit the remaining budget. Full-corpus semantic processing remains the accepted goal; a budget stop must not be reported as a complete corpus analysis. Record model identifiers, API calls, input/output/total tokens, and approximate costs for every LLM step and discuss value gained. The user has stated that an API key is available, but no key has been requested, stored, or used during this interview. Q41-Q42 subsequently accepted shared extraction and cached default reruns; see [ADR 0012](0012-shared-extraction-and-reproducible-submission.md).

Prior documentation checks supported the named models. Recheck availability, pricing, and the exact model identifier at implementation time; do not assume old quoted prices are still current. A platform spend limit can supplement the notebook's own conservative budget checks, but enforcement may lag. The exact safety buffer and restart/cache accounting design are implementation details still to specify.

Sources to verify again: [model catalog](https://developers.openai.com/api/docs/models), [pricing](https://developers.openai.com/api/docs/pricing), [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), and [spend limits](https://developers.openai.com/api/docs/guides/spend-limits).

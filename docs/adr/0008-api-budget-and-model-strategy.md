# Constrain all LLM work to a total fifteen-dollar budget

Status: accepted, Q17/Q21 and the user's explicit budget revision. Scope: all assignment API work.

Use an OpenAI API key, begin with GPT-6 Luna and structured outputs, and consider GPT-6 Sol if pilot errors justify a stronger model. Total API spending for the assignment is capped at $15, including development, retries, and later Tasks E-F; this replaces the earlier proposed $25 cap. Estimate full cost from the pilot, track usage by step, and stop conservatively before the available budget is exhausted.

## Consequences

Model escalation must fit the remaining budget. Full-corpus semantic processing remains the accepted goal; a budget stop must not be reported as a complete corpus analysis. Record model identifiers, API calls, input/output/total tokens, and approximate costs for every LLM step and discuss value gained. The user has stated that an API key is available, but no key has been requested, stored, or used during this interview. Q41-Q42 subsequently accepted shared extraction and cached default reruns; see [ADR 0012](0012-shared-extraction-and-reproducible-submission.md).

Prior documentation checks supported the named models. Recheck availability, pricing, and the exact model identifier at implementation time; do not assume old quoted prices are still current. A platform spend limit can supplement the notebook's own conservative budget checks, but enforcement may lag. The exact safety buffer and restart/cache accounting design are implementation details still to specify.

Sources to verify again: [model catalog](https://developers.openai.com/api/docs/models), [pricing](https://developers.openai.com/api/docs/pricing), [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), and [spend limits](https://developers.openai.com/api/docs/guides/spend-limits).

## Revision — September 29, 2026: Claude Haiku 4.5 with Message Batches

During the pilot the team decided to switch generation from OpenAI GPT-6 Luna to Anthropic Claude Haiku 4.5 (`claude-haiku-4-5`), using the Anthropic Messages API with JSON-schema structured outputs. The $15 cumulative cap is unchanged and still includes the earlier Luna discovery and pilot calls (about $0.07).

At standard Haiku 4.5 prices ($1 input / $5 output per million tokens), the full corpus was estimated at $15–16, which does not fit the cap. The team therefore chose the Message Batches API (50% discount, stacking with prompt caching; usually finished within an hour, guaranteed within 24) for full extraction, estimated at about $8. The 100-post pilot runs as concurrent real-time requests.

The budget guard still reserves each request's worst case (the full output limit, with all input priced at the one-hour cache-write rate) before sending. Batches are submitted in rolling chunks: a chunk is reserved at worst case, then settled from actual usage when it ends, which frees budget for the next chunk. `freeze` projects the remaining extraction at batch prices with the 50% safety margin.

The model change alters extraction provenance, so the Luna pilot is archived and the pilot reruns on Haiku 4.5 before the 20 development reviews. The reviews and freeze gates judge Haiku's quality; it is not assumed.

Sources: [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing), [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), [batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing).

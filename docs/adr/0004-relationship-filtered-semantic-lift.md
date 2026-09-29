# Filter semantic brand pairs by competitive relationship

Status: accepted, Q16-Q20 and Q23. Scope: Task C and comparisons to B.

The primary LLM-based matrix will count a pair when the author compares, jointly evaluates, or considers the marques as purchase alternatives. A lexical matrix instead counts same-post co-mentions. This stronger semantic event may produce more managerially relevant edges, but the two numerators are not identical; an LLM-mention-only same-post matrix will help separate recognition effects from the relationship filter.

## Consequences

The notebook must label the semantic matrix's event precisely, audit borderline relations, compare all 45 unordered pairs, and avoid claiming that every difference proves the LLM is more accurate.

Shared evaluations count, including criticism: "BMW and Audi are both expensive" qualifies. A bare list or unrelated remarks do not. Require evidence spans, allow uncertain classifications, omit uncertain labels from primary event counts, and report abstentions and sensitivity to their inclusion. Process all usable posts after the pilot.

Use semantic brand marginals for both semantic variants. The relationship-filtered numerator counts supported relations; the intermediate same-post variant counts joint semantic brand presence. See [the calculation contract](../calculation-contract.md) for exact definitions. Compare pair counts, lift differences, rank correlation, strongest-pair overlap, representative explanations of major changes, and changes in apparent closest competitors.

# Use cleaned, substantive references while retaining raw text

Status: accepted, Q3 and Q6-Q7. Scope: shared preparation and entity attribution.

The supplied CSV contains flattened replies and apparent preprocessing insertions that look like car marques. We will keep the raw posts, apply only high-confidence artifact corrections, and count brands the author substantively discusses rather than every token in a row. Literal matching remains a documented alternative and sensitivity check because quote boundaries and corruption cannot always be recovered.

## Consequences

Each cleaning rule needs examples and a before/after effect check. The lexical baseline approximates substantive discussion with deterministic rules; semantic classification may disagree where text structure is ambiguous.

Map unambiguous model references and aliases to marques; use context for ambiguous forms and abstain if it does not resolve them. Quoted claims count when the author engages with them; clearly quoted-only references do not. Counting every brand anywhere in a row remains an alternative, explicitly rejected as the primary method after the user's Q7 correction.

The observed `kia hyundai`, `toyota d`, and repeated `mercedes-benz benz` strings motivate an audit, not permission to replace every occurrence blindly. Exact correction patterns and quote-detection rules still need evidence-based implementation and examples.

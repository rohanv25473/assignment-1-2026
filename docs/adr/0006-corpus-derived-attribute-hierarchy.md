# Discover a hierarchy of vehicle attributes from the corpus

Status: accepted, Q4 and Q9-Q11. Scope: Task A and inputs to E.

Use NLP phrase extraction and context clustering to find candidates in the supplied posts, then use selective LLM interpretation to reconcile names and phrases. Build broad attribute themes with specific subattributes, such as performance with acceleration and handling. A supplied brand/model dictionary, a flat attribute list, and unrestricted topics were considered as alternatives; the chosen design keeps discovery grounded in the corpus while preserving distinctions within a theme.

Rank themes by distinct-post prevalence, report author coverage and leading subattributes, and keep purchase intent and general praise separate. Task E will use five supported themes describing distinct aspects of cars. Theme names in the interview were examples, not a preselected final taxonomy. Q27-Q29 subsequently finalized the five-brand selection rule and use of clear directional labels; see [ADR 0009](0009-semantic-brand-attribute-positioning.md).

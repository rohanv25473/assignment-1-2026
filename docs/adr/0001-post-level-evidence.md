# Count distinct posts as the main unit of evidence

Status: accepted, Q1-Q5 and Q13-Q15. Scope: Tasks A-B and the common post universe for C-D.

The assignment asks which marques and attributes are important and later compares brand associations. We will rank them by distinct usable-post prevalence and calculate lift from post-level binary events, with author coverage as a robustness check. Raw token counts would let repeated names and a few prolific posters dominate; changing the unit later would alter every ranking and matrix.

## Consequences

Repeated mentions within one post add no weight. The notebook must state the usable-post denominator and verify lift on a toy corpus.

Use only `sample_data.csv` as the complete assignment corpus. Discover the top 10 automobile marques from it without a supplied brand/model dictionary; mass-market marques remain eligible and Lexus/Toyota or Acura/Honda stay separate. Attribute themes also use distinct-post prevalence with author coverage. Include usable posts without a top-10 brand in the denominator. The alternative of sentence-level co-occurrence was considered and rejected for the primary baseline.

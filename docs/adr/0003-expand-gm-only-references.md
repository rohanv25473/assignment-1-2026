# Expand GM-only references to four child marques

Status: accepted, Q8/Q8a and Q19. Scope: marque labels and semantic relations.

When a post says `GM` without identifying a child marque or clear child model, the agreed rule adds Chevrolet, Buick, GMC, and Cadillac. If one or more children are identifiable, only those children are added. This deliberately favors broad coverage of the GM family over literal marque precision, despite the alternative of keeping GM separate as a corporate parent.

## Consequences

The rule can turn a company or stock discussion into four brand mentions and inflate lexical pair counts. The notebook must report a no-expansion sensitivity check. Semantic pair counts require a meaningful relation; a lone GM mention does not create six relationships among the four children.

This exception is deliberate: do not silently replace it with parent-only attribution in a fresh session. Other marques explicitly present in the post continue to count normally. When the text meaningfully compares GM with Toyota and no GM child is identifiable, Task C creates four child-to-Toyota relations; it creates no child-to-child relations merely from the expansion. If Cadillac or its clear model is identified, do not additionally infer the other three GM marques. Retain provenance so expanded labels can be removed for sensitivity analysis.

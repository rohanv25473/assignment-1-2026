# Calculation contract for Tasks A-F

This makes the accepted post-based design precise for a future implementer. Equations and edge handling below spell out the agreed definitions; they do not report results. Where the interview left an implementation detail unresolved, it is identified as such.

## Common corpus and counting rules

Use only `sample_data.csv`. Read it without a header and assign username, date-label, and post-text fields. Preserve the source and original row identifiers. Establish one common usable-post universe before comparing methods and report exclusions. The intended preparation removes blank texts and exact duplicate records; the exact duplicate key and treatment of text that becomes empty after cleaning should be documented during implementation. Do not silently remove posts because no top-10 marque was detected or because a semantic classifier abstained.

Let `N` be the number of retained posts. Discover and freeze the same 10 marques from Task A for the B/C comparison. Count a brand, attribute theme, or unordered pair at most once per post. Multiple subattribute mentions under one theme do not give the theme multiple votes in that post. Author coverage is a companion statistic for A-E; Task F explicitly uses distinct authors for its primary ranking.

Keep raw and cleaned text, mapping provenance, and GM-expanded labels available for inspection. Actual cleaning patterns must be justified on examples; the observed artifacts are not a license to invent missing original text.

## Task B: ordinary post co-occurrence lift

For marque `A`, define `x_A(p)=1` when the baseline recognizes it in post `p` after the agreed preparation and GM rule; otherwise 0.

```
n_A  = sum_p x_A(p)
n_AB = sum_p x_A(p) * x_B(p)
L_B(A,B) = N * n_AB / (n_A * n_B)
```

Use unordered pairs, an unsmoothed matrix, a blank displayed diagonal, and a separate pair-count matrix. When both marginal counts are positive and the joint count is zero, lift is zero. If a marginal count is zero, the ratio is undefined, not zero: flag it explicitly rather than divide by zero. The top-10 choice should normally provide positive support, but semantic abstention or a sensitivity variant can remove it.

## Task C: two variants using semantic attribution

Let `y_A(p)=1` when the LLM supports a substantive reference to `A`, after applying the agreed GM rule. An uncertain reference is excluded from this primary event count, while the post remains in `N`.

```
m_A = sum_p y_A(p)
j_AB = sum_p y_A(p) * y_B(p)
L_C_mentions(A,B) = N * j_AB / (m_A * m_B)
```

This intermediate matrix uses the same co-occurrence event definition as B and helps isolate changes in brand recognition and attribution.

Let `r_AB(p)=1` only when a supported competitive relation links `A` and `B` in the post. Both corresponding semantic brand labels must be present. Shared evaluation, comparison, and purchase alternatives qualify; mere listing or unrelated remarks do not.

```
s_AB = sum_p r_AB(p)
L_C_relation(A,B) = N * s_AB / (m_A * m_B)
```

`L_C_relation` is the primary semantic association ratio requested by the agreed design. Its numerator measures a narrower event than ordinary joint presence. Label it as relationship-filtered semantic lift and do not interpret its difference from B as a pure accuracy gain. For a fixed semantic label set, `s_AB <= j_AB`; the relation filter can lower lift even when brand extraction is identical. Use the same zero-support rules as B.

Evidence spans and an uncertain category are required. Validate evidence against the source text. The precise sensitivity treatment of uncertain labels and API failures remains to be specified; neither missing responses nor uncertainty should silently masquerade as confident negative labels.

## GM worked examples

These are illustrative cases for testing the accepted rule, not actual analysis outputs.

| Text case | Marque labels from the GM rule | Baseline pairs | Semantic relations |
| --- | --- | --- | --- |
| GM stock, no child identified | Chevrolet, Buick, GMC, Cadillac | All six child-to-child pairs | None from the parent mention alone |
| GM compared with Toyota, no child identified | Four GM children plus Toyota | All ten unordered pairs among these five labels | Four child-to-Toyota pairs; no automatic child-to-child pairs |
| GM's Cadillac compared with Lexus | Cadillac plus Lexus | Cadillac-Lexus | Cadillac-Lexus when the comparison is supported |
| GM mentioned with identifiable Cadillac and Buick | Cadillac and Buick; no Chevrolet/GMC inference | Cadillac-Buick | Only if the text meaningfully relates the children |

Identifiable models count as identifying their marque. Explicit non-GM brands are unaffected. Run the agreed no-expansion sensitivity with provenance-based removal; keep the primary 10-brand set for a direct matrix comparison and separately report any ranking changes.

## Reconciliation and validation

Compare the 45 unordered off-diagonal pairs. Report counts, lift differences, rank correlation, strongest-pair overlap, and representative posts explaining large changes. Contrast B with `L_C_mentions`, then `L_C_mentions` with `L_C_relation`. Record changes in apparent closest competitors and the effect of disabling GM expansion.

Use a small toy corpus to hand-check `N`, marginals, pair counts, repeated mentions, posts without target brands, zero pairs, and the GM exception. Inspect semantic labels using the accepted 20 development cases and 40 independent random audit posts. Exact correlation type, top-pair cutoff, error metrics, and numerical acceptance thresholds have not been selected; choose and explain them before interpreting final results.

## Task D: dissimilarity, MDS, and clusters

For finite off-diagonal lift `L(A,B)`, use `d(A,B)=1/(1+L(A,B))`. Set self-distance to zero explicitly; do not apply the off-diagonal formula to a blank lift diagonal. The matrix is symmetric and nonnegative. An unobserved pair with valid marginals has lift zero and distance one. Undefined lifts require an explicit handling decision, not automatic conversion to maximum distance.

Use two-dimensional nonmetric MDS, report stress, and use reproducible starts. The map seeks to preserve ordering of dissimilarities; it does not establish causal rivalry, market share, or attribute direction. The display axes have no inherent semantic meaning. Strong ties and many equal maximum distances can limit interpretability.

Fit clusters to the full dissimilarity matrix and display them as colors on the MDS coordinates. Compare two to four clusters using fit and interpretation. The exact clustering algorithm/linkage and fit statistic remain implementation choices. Prefer semantic input only if audit quality and pair coverage justify it; otherwise use the lexical baseline. Show measurement sensitivity and flag changed neighbors or cluster memberships. Numerical fallback thresholds remain to be specified before selecting favorable results.

## Task E: linked attribute rates and association

Select five brands from the fixed top 10 before inspecting positioning scores: choose the most prevalent brand from each stable Task D cluster, then fill by prevalence. The five themes must have support and describe distinct aspects. If no stable cluster structure exists, document a fallback before inspecting positioning scores; the fallback itself was not specified by the user.

For a theme `T`, let `z_T(p)=1` when it is substantively discussed, including cases where its brand target is unresolved. Let `a_BT(p)=1` when a supported link assigns that theme to brand `B`. A link requires the brand label and theme to be present. Aggregate subattributes by a union of posts, not by summing subattribute frequencies.

```
m_B = number of posts with semantic brand B
t_T = sum_p z_T(p)
k_BT = sum_p a_BT(p)
linked_attribute_rate(B,T) = k_BT / m_B
linked_attribute_lift(B,T) = N * k_BT / (m_B * t_T)
```

These equations spell out Q28's linked counts, within-brand rate, and common-denominator association. The linked numerator is narrower than same-post brand-theme presence, as in Task C. Retain unassigned themes in `t_T`, count no invented brand link, and keep the post in `N`. A zero numerator with positive marginals produces zero; a zero marginal produces an undefined rate or lift.

Compute the lexical sensitivity from lexical brand/theme presence using internally consistent marginals and the same `N`; do not silently mix lexical numerators with semantic denominators. Report all 25 cells with counts and support, not only the highest lift values.

Broad-theme association describes discussion, not praise. Retain evidence, subattribute, and clear direction at the link level. When opposite descriptions occur within one brand-theme-post, count the theme once and preserve the conflicting evidence rather than inventing a single favorable direction. The exact direction labels are an implementation choice.

Apply GM attribute inheritance only to clear vehicle attributes under the agreed child-reference rule. Tag inherited links. For the requested inherited-link sensitivity, remove those links and state which marginals remain fixed; a separate full GM-expansion-off comparison may also change the brand marginals. Do not imply these two sensitivity definitions are identical.

## Task F: author-level aspiration

For each post and identifiable brand, keep evidence for concrete purchase intent, conditional/dream ownership, nonqualifying desire, and uncertainty. A positive aspiration must refer to the author and have a supported marque; GM-only desire remains parent-level and does not enter child aspiration counts. Current ownership or praise alone is insufficient. A conditional statement qualifies only when it expresses personal desire, not merely an arbitrary hypothetical.

Let `C_B` be authors with at least one supported concrete-intent post for brand `B`; let `D_B` be authors with at least one supported conditional-desire post. Let `U_B` be authors with a semantic discussion reference to `B`, using the established mention rule, including GM-expanded mention labels.

```
aspiring_authors(B) = |C_B union D_B|
concrete_authors(B) = |C_B|
conditional_authors(B) = |D_B|
aspiration_fraction(B) = |C_B union D_B| / |U_B|
aspiration_posts(B) = distinct posts with either supported desire category
```

Rank all reliably identified marques by `aspiring_authors`. The two category counts can overlap; do not sum them as unique people. An author may desire multiple marques. Usernames are observed author identifiers, not verified unique consumers, and these counts are not market share. Report ties honestly instead of claiming a unique winner without support.

GM expansion can enlarge `U_B` without enlarging child aspiration numerators. Disclose that effect on the companion fraction; the primary aspiration count remains direct to the identifiable marque. Keep GM-level desires available as unresolved child attribution.

Use any qualifying expression during the corpus period, even when another post later rejects the brand. Flag contradictory evidence and avoid a current-intent interpretation. Uncertain desire is excluded from primary positive counts, with volume and examples reported. Inspect aspiration labels in the existing audit plus up to 10 predicted positives and 10 hard nonpositive/uncertain cases. Targeted false-negative examples do not by themselves estimate population recall.

## A small worked example for the notebook's toy checks

The following posts and labels are synthetic and serve only to verify counting. They are not corpus findings or completed human validation.

| Post | Author | Text | Intended labels |
| --- | --- | --- | --- |
| 1 | u1 | I plan to buy BMW instead of Audi; BMW handles well. | BMW, Audi; competitive pair; BMW-performance; concrete BMW desire |
| 2 | u1 | I would love a BMW if I could afford it. Audi seats are comfortable. | BMW, Audi; no asserted competitive pair in this toy; Audi-comfort; conditional BMW desire |
| 3 | u2 | Audi seats are comfortable. | Audi; Audi-comfort; no desire |
| 4 | u3 | Traffic was heavy today. | No target brands; retained in N |

With `N=4`, BMW has 2 posts, Audi 3, and lexical joint presence 2. Lexical lift is `4*2/(2*3)=4/3`. With only the first post labeled as a competitive relation, semantic relation lift is `4*1/(2*3)=2/3`; the changed numerator alone explains the difference.

Comfort appears in 2 posts, both linked to Audi. Audi's linked comfort rate is `2/3`, and attribute lift is `4*2/(3*2)=4/3`. BMW-performance has count 1, rate `1/2`, and lift `4*1/(2*1)=2`.

BMW has 2 aspiration posts but only 1 aspiring author. Its concrete and conditional author counts are both 1, and their union is 1. Audi has 0 aspiring authors. These calculations validate arithmetic and deduplication; the semantic label for the second post remains an explicit synthetic test assumption.

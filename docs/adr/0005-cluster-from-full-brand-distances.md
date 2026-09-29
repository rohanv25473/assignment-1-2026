# Map and cluster from brand dissimilarities

Status: accepted, Q24-Q26. Scope: Task D.

The competitive map will turn lift into dissimilarity with `1 / (1 + lift)` and use two-dimensional nonmetric MDS. Clusters will be fitted to the full dissimilarity matrix and then shown as colors on the map. Clustering plotted coordinates would make group membership depend on distortion introduced by the two-dimensional display; this choice keeps clustering tied to the measured brand relationships.

## Consequences

The notebook must report MDS stress, compare two to four cluster solutions, and check whether visible neighbors or cluster memberships change when lexical rather than validated semantic lift is used.

Use Task C's semantic matrix as primary only if the audit supports its labels and pair coverage is sufficient. Otherwise use Task B and explain the switch. Show the other map as a sensitivity check. Set self-distances to zero, use reproducible starts, and interpret proximity through measured association; the axes have no inherent luxury, price, or performance meaning. Exact linkage, cluster-fit statistic, and numerical quality/coverage gates were not selected by the user and must not be presented as finalized choices.

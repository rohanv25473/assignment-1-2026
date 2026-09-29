# Source inspection evidence

This records read-only data checks from the session, reverified on September 28, 2026. These are input-quality observations, not brand rankings or semantic findings. They support the design choices and should be reproduced by the notebook rather than hard-coded as final outputs.

Source: `sample_data.csv`, 3,391,987 bytes.

SHA-256: `1af81f6b88bec9ae0bf1cf668eaefdee86cc69b5ad27d3d74a797ab4a7991bad`

| Check | Observation |
| --- | --- |
| CSV structure | 6,000 records, each with 3 fields; no header row |
| Inferred fields | Username, date label, post text |
| Distinct usernames | 329 |
| Distinct date labels | 44 |
| Blank text after whitespace trimming | 9 records |
| Extra exact duplicate occurrences across all three raw fields | 8 |
| Unique nonblank raw records | 5,986 |
| Duplicate occurrences overlapping blank-text records | 3; only 5 additional exact duplicates remain after dropping blank texts |
| Raw text length in characters | Minimum 1, median 357, maximum 6,961 |
| Largest author contribution | `blueguydotcom`: 558 raw posts |

The 5,986 figure applies to the specific combination of whitespace-blank exclusion and exact three-field deduplication. It is not automatically the final denominator if a separately justified rule excludes additional posts. Earlier rough subtraction of 9 and 8 as disjoint exclusions would be wrong.

Date labels such as `6-Oct` through `11-Nov` appear to represent year/month values spanning 2006-2011; the CSV does not document that interpretation. Preserve labels and do not silently parse them as day/month dates.

## Suspicious strings and parent references

| Raw string/check | Posts containing it | Interpretation limit |
| --- | --- | --- |
| `kia hyundai` | 1,697 | Often occurs beside quotation marks around ordinary prose; not a validated count of genuine marque references |
| `mercedes-benz benz` | 312 | Often repeated in long runs; normalization needs context |
| `toyota d` | 434 | Often occupies a position where "said" would fit; substring observation, not proof every instance needs the same correction |
| Whole-word `GM` | 269 | Case-insensitive lexical count, before semantic filtering |
| GM posts with none of Chevrolet/Chevy/Buick/GMC/Cadillac/Caddy as whole words | 149 | This lexical check misses model-based child references; it is not the final GM-only semantic count |

The phrase counts above use case-insensitive substring matching. They must not be relabeled as final brand frequencies. Original first-record text around "under-achieving" and examples such as "like I toyota d" motivated conservative artifact correction and semantic inspection.

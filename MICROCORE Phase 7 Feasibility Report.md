# Deliverable 13 — Feasibility of the 5 billion token target

## 1. Bottom line

The target is not reachable with licensed, security-relevant material. A realistic total is approximately 3.24 B globally unique tokens, leaving a gap of roughly 1.76 B. That conclusion is built from measured inputs, not from a ceiling inherited from earlier phases.

| Scenario | Baseline unique | Phase 7 measured net | Academic projection | Total | Gap to 5 B |
|---|---:|---:|---:|---:|---:|
| Conservative | 2,058.5 M | 349.3 M | 605.1 M | **3,013.0 M** | 1,987.0 M |
| Realistic | 2,172.8 M | 349.3 M | 719.0 M | **3,241.3 M** | 1,758.7 M |
| Optimistic | 2,241.5 M | 349.3 M | 791.7 M | **3,382.8 M** | 1,617.2 M |

## 2. How each column is derived

Baseline uniqueness: the 2,287,196,994 accumulation has never been globally deduplicated. Global uniqueness is applied as a 0.90 / 0.95 / 0.98 range and is explicitly an assumption, not a measurement. It is the weakest input in the model and it moves the total by 183 M across the range.

Phase 7 measured net: 349,287,979, measured and deduplicated as described in Deliverables 11 and 12. This is the only column with no assumption in it.

Academic projection: two populations, each a measured count times a measured mean, then haircut for relevance and quality.

| Component | Gross | Conservative | Realistic | Optimistic |
|---|---:|---:|---:|---:|
| arXiv | 413.2 M | 314.0 M (×0.76) | 360.7 M (×0.873) | 388.6 M (×0.9405) |
| Europe PMC | 447.9 M | 291.1 M (×0.65) | 358.3 M (×0.80) | 403.1 M (×0.90) |
| Total | 861.1 M | 605.1 M | 719.0 M | 791.7 M |

The arXiv multiplier combines relevance (0.80 / 0.90 / 0.95 — proportion of CC-BY papers that are actually about security once cross-listings are filtered) with quality (0.95 / 0.97 / 0.99). The Europe PMC multiplier is a single relevance term, applied because the 81.7% title-level pass rate is generous and full-text precision is lower.

## 3. What already failed to close the gap

| Attempt | Outcome | Tokens added |
|---|---|---:|
| Measuring 28 approved-but-never-measured Phase 5 repositories | Success | 326.3 M |
| NIST exhaustive enumeration, 1,910 probes | Success | 13.5 M |
| CISA full advisory walk, 3,203 documents | Success | 7.7 M |
| NCSC UK sitemap, 1,281 pages | Success | 1.8 M |
| ENISA sitemap | Partial — landing pages only | 0.13 M |
| arXiv stratified census and PDF sampling | Discovery only, no bulk acquisition | 0 |
| Europe PMC / PLOS harvest | Discovery and sampling | 0 |
| 46 non-code candidates probed | 5 usable, 27 closed | 0 |

Total new: 349.3 M. That is 7% of the target in a phase that exhausted the easy licensed ground.

## 4. What remains, honestly priced

| Opportunity | Realistic incremental | Confidence | Blocker |
|---|---:|---|---|
| Europe PMC full acquisition (32,518 records) | 358 M | medium | retrieval throughput; 33 s/doc on EBI route, faster on NCBI |
| arXiv CC-BY acquisition (22,044 papers) | 361 M | medium | 40 GB transfer, ~1.8 MB/PDF |
| Expand code from 59 to ~250 licensed security repositories | 400–700 M | low | duplication risk rises sharply; each repo adds less than the last |
| IETF RFC and draft corpus | 80–120 M | low | licence is conditional, not open; not measured in Phase 7 |
| DOAJ-hosted CC-BY security journals | 50–150 M | low | unenumerated; overlapping with PMC likely |
| Unmeasured CERT bodies (CCCS, ANSSI, NCSC-NL, CERT-EU, JPCERT, CSA) | 15–30 M | medium | per-document licence review, multilingual |
| NVD CVE 2.0 full feed | near zero | medium | vulnrichment at 385.6 M already derives from NVD |

Summing the plausible column: roughly 1.26–1.72 B. Adding the optimistic end of that to the optimistic scenario reaches approximately 4.6–5.1 B, which sounds like the target is in sight. It is not, for three reasons.

1. The code expansion figure is the largest and least defensible line. 59 repositories produced 334 M because five of them produced 200 M. Repositories 200 to 250 will be small tools averaging a few million tokens each.
2. The remaining document opportunities overlap each other. Europe PMC, DOAJ journals and PMC-deposited conference papers are not three populations; they are one population counted three ways from different indexes.
3. Every line above is gross. The 5 B target is unique tokens. Each new addition must be deduplicated against 3.2 B of existing material, and the duplicate rate will rise, not fall, as the corpus grows.

## 5. The three routes to 5 B that are not available

| Route | Why it is excluded |
|---|---|
| Stack v3 / general code dumps | Forbidden by the project's own security-first mandate. Roughly 1.5 B tokens of non-security code would close the gap instantly and destroy the corpus's purpose. |
| Non-open-access literature | Publisher copyright. ACM, IEEE, Springer, Elsevier, USENIX and NDSS are all closed. This is where the missing 1.5 B lives. |
| Synthetic generation | Explicitly forbidden. Manufacturing 1.5 B tokens of generated security text would satisfy the arithmetic and falsify the corpus. |

## 6. The defensible target

If the objective is a corpus that is licensed, security-relevant, deduplicated and honest, the reachable ceiling is approximately 3.2–3.4 B in this phase plus 1.2–1.7 B of further real work, for a total of roughly 4.4–5.1 B only under optimistic assumptions across every line simultaneously — and that outcome requires the code expansion to succeed at 250+ repositories with a duplicate rate that does not rise. That is a research programme, not a work package.

The recommended statement to the project is: 5 B unique security tokens is achievable only if the definition of "security material" is widened to include generic systems code. If it is not widened, the honest ceiling is 3.2–3.4 B now and approximately 4.5 B after the remaining licensed work is completed.

## 7. What would change this conclusion

Three findings would justify revisiting it:

- A licensed corpus of 1 B+ security tokens that Phase 7 did not find. Nothing in 116 probes suggests one exists.
- A change in the licensing position of a major publisher, which would open ACM or IEEE.
- Permission from a rights holder for a specific closed corpus, which is a procurement action outside the project's control.

Absent one of those, the gap is structural and should be reported as such rather than closed by redefining the measurement.

# Deliverable 10 — 5-Billion-Token Feasibility Model

## Headline

Phase 6 measured **434,731,317 net new tokens** from 30 repositories, and located a further ~270 M of approved but unmeasured supply, including an academic pool the project had wrongly written off. The realistic ceiling moves from 2.49 B to **2.66 B**. The gap to 5 B falls from 2.51 B to 2.34 B.

Five billion remains out of reach under the required standards — but the previous ceiling was too low, and this phase proves it rather than asserting it.

## Line items

| Line | Gross tokens | Evidence class | Note |
|---|---|---|---|
| Existing carried corpus | 1,852,465,677 | VERIFIED_MEASURED, provisional | never globally deduplicated |
| Phase 6 measured, excluding duplicate and advisory data | 217,295,659 | VERIFIED_MEASURED | 29 repositories |
| GitHub advisory-database | 217,435,658 | VERIFIED_MEASURED | 412,537 files; formulaic and record-duplicated |
| arXiv cs.CR CC-BY | 150,400,000 | PROJECTED from SAMPLE_MEASURED | 12,360 papers × 12,168 mean |
| NIST SP 800 series | 95,000,000 | PROJECTED | document count × density |
| PLOS ONE security articles | 25,000,000 | PROJECTED | paper density × count |
| Remaining Phase 5 Tier A (Impacket, GhostPack, pwndbg, angr, Capstone, jadx, Zephyr…) | 200,000,000 | PROJECTED | Phase 5 estimate minus what Phase 6 measured |
| D3FEND | 900,000 | PROJECTED | |
| DISA STIGs | 60,000,000 | CONDITIONAL — counted at zero | terms unread |
| IETF RFCs | 45,000,000 | CONDITIONAL — counted at zero | copyright retained |
| OSTI reports | 20,000,000 | CONDITIONAL — counted at zero | per-record rights |
| Generated lab procedure | 0–300,000,000 | GENERATED, capped at 20 % | not measurement |

## Deduplication haircuts applied

| Line | Conservative | Realistic | Optimistic | Justification |
|---|---|---|---|---|
| Existing corpus | −13.6 % | −7.2 % | −2.8 % | measured exact duplication is 1.6 %; documentation families and NVD/OSV overlap push it higher; the high end reflects the Phase 5 assumption that has never been tested |
| Phase 6 non-advisory | −15 % | −10 % | −5 % | vendored code, licence-text repetition across repositories |
| Advisory database | −50 % | −40 % | −30 % | record-level duplication across ecosystems and severe schema repetition; this is the weakest-evidenced haircut in the model |
| arXiv | −30 % | −15 % | −5 % | conference-version overlap, extraction loss, figure captions |
| NIST | −15 % | −10 % | −5 % | overlapping guidance across special publications |
| PLOS | −20 % | −10 % | −5 % | same |
| Tier A remainder | −20 % | −10 % | −5 % | repository overlap |

None of these rates is measured at corpus scale. The advisory haircut alone could move the total by 40 M.

## Scenarios

| Scenario | Existing | Phase 6 non-adv | Advisory | arXiv | NIST | PLOS | Tier A | Generated | **Total** | Gap to 5 B |
|---|---|---|---|---|---|---|---|---|---|---|
| **Conservative** | 1,600.0 M | 184.7 M | 108.7 M | 105.3 M | 80.8 M | 0 | 0 | 0 | **2,079.5 M** | 2,920.5 M |
| **Realistic** | 1,720.3 M | 195.6 M | 130.5 M | 127.8 M | 85.5 M | 22.5 M | 180 M | 200 M | **2,661.7 M** | 2,338.3 M |
| **Optimistic** | 1,800.0 M | 206.4 M | 152.2 M | 142.9 M | 90.3 M | 23.8 M | 195 M | 300 M + 124 M conditional | **3,034.6 M** | 1,965.4 M |

The conservative scenario counts only what is already measured plus the two strongest projections, and excludes all generation. The optimistic scenario assumes every conditional resolves favourably, generation reaches its 20 % cap, and deduplication is unusually gentle.

## What changed from Phase 5, and why

Phase 5 concluded 2.11 / 2.49 / 2.80 B. The revision has three causes, all evidenced:

1. **Azure Sentinel: 108 M measured.** Phase 5 did not know that a single licence-clean repository contained more detection logic than the entire rest of the security corpus.
2. **GitHub advisory-database: 217 M measured.** Large and formulaic, and therefore heavily discounted, but it is real tokens under CC-BY-4.0.
3. **arXiv CC-BY: 22.5 % of cs.CR**, established by a 200-paper licence census. Phase 5 had observed only that arXiv's *default* licence is non-exclusive and stopped there. That was an error of sampling, not of law.

## What still cannot be reached

Even the optimistic scenario is 1.97 B short. The remaining shortfall is concentrated in exactly the place the brief says it will be:

| Missing capability | Why it cannot be bought with tokens |
|---|---|
| Tool-use trajectories | no public corpus of real investigations exists under any licence |
| Judgement under ambiguity | requires case narratives that practitioners do not publish with reuse rights |
| Wireless and hardware depth | the research is either proprietary, in tools (GPL), or in papers with no licence |
| DFIR at scale | real telemetry is confidential by nature |

## Routes to 5 B, restated after Phase 6

| Route | Adds | Cost |
|---|---|---|
| Foundation layer, labelled and sampled at low ratio | 2.3 B | the corpus is 5 B but only ~55 % is security-attributable; must be labelled honestly |
| Large-scale generation | 300–400 M realistically | months of compute, and beyond 20 % the model learns the generator |
| Relaxing licences to include GPL/AGPL | ~250 M | forfeits commercial use; does not close the gap |
| General code volume | 2.3 B needed | Stack v3 by another name; explicitly excluded |

## Recommendation

Build to **2.7 B at roughly 72 % security-attributable**, report it as 2.7 B, and stop optimising the number. If 5 B is a hard external requirement, adopt the labelled foundation layer and never describe the foundation tokens as security training data.

## Confidence statement

Measured: 2.29 B of the model's inputs (existing 1.852 B plus 435 M new). Projected: ~470 M. Generated: 0–300 M. Deduplication: entirely estimated. The final figure carries ±300 M of uncertainty, and no part of it is a verified globally unique count.

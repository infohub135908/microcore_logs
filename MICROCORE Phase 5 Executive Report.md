# Deliverable 11 — Final 5 B Feasibility Assessment

## The conclusion

**Five billion tokens of high-quality, licence-clean, cybersecurity-first material is not reachable from the sources that exist.** The realistic ceiling is approximately **2.5 B unique cl100k tokens**, with a range of 2.1–2.8 B. That is 42–56 % of the target. This is a supply finding, not an effort finding: more searching does not create material that no one has published under a usable licence.

The number is not a failure of the plan. At 2.5 B with 70 % security-attributable content, MICROCORE is a fundamentally different model from the one the current 1.8 B mixture would produce. The target was set before the supply was measured; the measurement now exists and it disagrees with the target.

## Scenarios

| Scenario | Unique tokens | Dedup rate | Composition | What must be true |
|---|---|---|---|---|
| **Conservative** | **2.11 B** | 32 % | security-attributable ≈ 62 % | DISA and IETF both rejected; generated procedure capped at 150 M; Tier A admit rate at the low end of calibration |
| **Realistic** | **2.49 B** | 20 % | security-attributable ≈ 70 % | IETF approved, DISA rejected; 250 M generated; Tier A yields as projected |
| **Optimistic** | **2.80 B** | 10 % | security-attributable ≈ 72 % | both approved; every conditional resolves favourably; 300 M generated; dedup lower than expected |

Evidence categories: the 1.85 B already measured is **measured**. The 320 M, 210 M, 180 M and 250 M increments are **sample projections**. The dedup rates are **unverified estimates** inferred from known vendoring and republication patterns; they have not been measured at corpus scale. No figure here is a measurement of global uniqueness, because that measurement has never been taken.

## What it would take to reach 5 B

Three routes exist, and each has a price the user has already ruled out or should weigh explicitly.

**Route 1 — a labelled foundation layer (recommended if 5 B is non-negotiable).** Add 2.5 B of general code and text, but label it in the manifest as `layer: foundation` and sample it at a fixed low ratio during training. The corpus is 5 B; the security signal per step stays the same because the foundation share is controlled at the sampler, not the corpus. This satisfies the token target honestly without pretending the extra 2.5 B is security knowledge. It does require the two-tier manifest and a documented sampling policy.

**Route 2 — large-scale synthetic generation (partially viable).** Generating 2.5 B tokens of security procedure would require roughly 1.7 M episodes at 1,500 tokens. Even at high throughput that is months of generation and a substantial quality-assurance effort, and beyond ~20 % of the corpus the model begins to learn the generator's regularities. It can close perhaps 300–400 M of the gap. It cannot close 2.5 B without becoming the dominant source, which contradicts the goal.

**Route 3 — relax licensing.** Re-admit GPL and CC-BY-SA material (Velociraptor, Sigma rules, MobSF, OWASP prose, Radare2, Volatility). This would add perhaps 150–250 M, not 2.5 B, and it forfeits the commercial-use requirement outright. Not recommended, and it does not solve the arithmetic anyway.

**Route 4 — reacquire general code volume.** This is Stack v3 by another name. The user has explicitly abandoned it and the reasoning still holds: it optimises the metric and damages the model.

## Why the gap is where it is

The shortfall is concentrated in the two layers that define the specialist:

| Layer | Needed at 5 B | Measured or projected supply | Gap |
|---|---|---|---|
| Direct security knowledge | 1.50 B | ~0.75 B | ~750 M |
| Security procedure / tool use | 750 M | ~300 M (mostly generated) | ~450 M |
| Security-relevant code | 1.25 B | ~1.05 B | ~200 M |
| Foundations | 1.00 B | ~1.00 B (held) | 0 |
| Enterprise / cloud / identity | 500 M | ~400 M | ~100 M |

Foundations are the only layer that is already full, and they are the layer the current corpus over-weights.

## Recommendation

Do not treat 5 B as the objective. Treat **2.5 B unique, 70 % security-attributable, fully licence-cleared and globally deduplicated** as the objective, and report the token total honestly as 2.5 B. If a 5 B number is required for external reasons, adopt Route 1 with an explicit foundation layer and never describe the foundation tokens as security training data.

The project's stated goal — "not another general-purpose code model" — is better served by 2.5 B of the right material than by 5 B of mixed material. The earlier phases demonstrated that the general-code route reaches its number easily and produces the wrong model. This phase demonstrates that the security-first route has a real ceiling, and that the ceiling is high enough to matter.

## What remains unverified

- Global cross-source uniqueness: never measured. The 2.5 B is gross minus an estimated dedup rate.
- Tier A projections: extrapolated from ten measured sources and Phase 4 yields, not from full ingestion.
- Generated-procedure quality: assumed to pass validity gates; not yet demonstrated at scale.
- Dedup rates: inferred from vendoring patterns observed in the 38 measured repositories, not computed corpus-wide.
- Legal status of DISA, IETF and NPSL material: unresolved, and each shifts the total by tens of millions of tokens.

Any of these could move the number by 200–300 M in either direction. None of them can move it to 5 B.

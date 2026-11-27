# Deliverable 1 — Executive Acquisition Assessment

## The short answer

5 B unique, legally usable cl100k tokens is achievable. It is achievable from sources that require no negotiation, no payment and no institutional agreement, starting today. The obstacle is no longer availability; it is selection discipline.

That answer rests on one measured fact, not on a catalogue claim: the strictly permissive slice of The Stack v3 is on the order of **137B tokens** (sample-based bounds 77B–271B), and the dataset is downloadable without gating. Against a shortfall of 3,187,800,278 after the current verified 1,812,199,722, that is a factor of roughly forty.

## What changed in this phase

Phase 3 closed at 1,295,372,327 verified tokens and concluded that the public permissive surface topped out near 1.9 B. That conclusion was right about the surface it had measured — hand-picked repositories and vendor documentation — and wrong about the ceiling, because it treated The Stack v2's gating as if it applied to v3. It does not.

| Claim from Phase 3 | Phase 4 finding |
|---|---|
| The Stack v2 is gated behind a Software Heritage/INRIA agreement | True of v2. **The Stack v3 sets `gated: false`** and serves contents inline |
| Bulk permissive code is not obtainable without a new agreement | False. 8,192 Parquet shards are openly downloadable |
| The public permissive surface is ~1.9 B | Understated by two orders of magnitude; the surface is ~137B in one dataset |
| The gap is an acquisition problem | It is a filtering, mixture and licensing-hygiene problem |

This phase also added 516,827,395 freshly measured tokens from 28 repositories not previously counted, chosen for language and domain breadth rather than size. See `10_measurement_register.md`.

## The three things that actually constrain the corpus

**Licence hygiene, not licence availability.** In the shards examined, 96–98 % of files are `no_license` and are excluded outright. Of what remains, roughly two thirds of the bytes survive MICROCORE's narrower allowlist. The binding constraint is that a permissive label from ScanCode is not the same as a licence we accept, and a database licence (ODC-By) is not a licence to any individual file.

**Quality, not quantity.** A 2.3 % file-admission rate on a capped trial run means the pipeline is doing real work. Padding the corpus with the other 97.7 % would be easy and would produce a worse model.

**Domain balance, not token count.** Generic permissive code is abundant and cyber-specific material is scarce, for a documented reason: the best community security corpora are either unlicensed (HackTricks, InternalAllTheThings) or share-alike (OWASP CheatSheetSeries and WSTG, CC-BY-SA-4.0). If the corpus is filled from Stack v3, MICROCORE becomes a code model with a security veneer. The composition rules in `08_composition_quality.md` exist to prevent exactly that.

## Honest weaknesses of this assessment

* The Stack v3 projection rests on four of 8,192 shards. It is a sample, labelled as such, with a stated interval — not a measurement of the corpus.
* No Stack v3 token has been acquired beyond a 2.5 M-token pipeline trial, and none is counted in any total here.
* Global cross-source deduplication still has not been run. The 1,812,199,722 figure remains a provisional sum, as the brief correctly insists.
* Telemetry and lab trajectories remain at zero and near-zero. Those are the pillars where 5 B is not the problem and behaviour is: they are rate-limited by execution time and review capacity, not by data.
* The cyber-specific gap (Active Directory, wireless, firmware, cloud control planes, DFIR case material) is not closed by any source found in this phase. It must be built or licensed.

## What would falsify this assessment

One test: pull 32 random shards, run `stackv3_acquire.py` over each with the allowlist and quality gate, and count admitted cl100k tokens. If the mean yield falls below 15 B per full pass over the dataset, the projection is wrong and the plan reverts to a multi-source build. Given four shards at 2.0–6.5 % byte share, a collapse that severe is unlikely, but it is the number to check before committing engineering time.

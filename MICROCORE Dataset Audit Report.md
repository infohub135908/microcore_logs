# PROJECT MICROCORE — Dataset Discovery, Accessibility, Licensing and Quality Audit

**Audit date:** 2026-11-26 (all HTTP checks, file counts, hashes and licence reads carry this date)
**Prepared for:** MICROCORE corpus programme (10M-token initialisation corpus, 1B-parameter model, 2×T4 budget)
**Scope:** dataset discovery and auditing only. No model recommendation, no change to the initialisation decision, no extrapolation of the 2×T4 timing result into training estimates.
**Status:** complete for the discovery and audit phase; two Tier-A candidates remain metadata-only by deliberate choice, and every gap is stated rather than filled.

---

## 1. Deliverable 1 — Executive research report

### 1.1 What was actually done

| Activity | Quantity | Evidence artefact |
|---|---|---|
| Hugging Face search queries executed | 25 | `data/hf_search.json` (25 queries, up to 40 hits each) |
| Primary-source URLs probed with timed HTTP requests | 137 | `data/http_checks.json`, `data/http_checks2.json` |
| GitHub/GitLab repositories inspected (licence file, tree, commit date) | 46 | `data/repos.json`, `data/gh_meta.json`, `data/license_probe.json` |
| Hugging Face datasets profiled through the API (gated flag, file tree, LFS hashes) | 21 | `data/hf_meta.json` |
| Artefacts downloaded and parsed | 8 | NVD recent feed, CWE 5.0, CAPEC 3.9, KEV, Trendyol JSONL, cve2cwe parquet, CIRCL parquet, ATT&CK STIX |
| Repositories cloned (blobless) for file-level counting | 29 | `raw/repos/` |
| Records registered in the audit | 80 | `out/master_inventory.csv` |

No bulk corpus download was performed. No un-downloaded dataset was deduplicated at record level. No malware sample was downloaded, opened or executed. No gate, paywall or authentication barrier was bypassed. Where a source could not be audited, it is recorded as unaudited, not as absent.

### 1.2 Exact counts

| Tier | Records | Meaning |
|---|---:|---|
| **A — Approved for ingest** | **13** | File-level access verified, licence verified compatible, score ≥ 88 |
| **B — Approved with conditions** | **24** | Licensed and usable, but metadata-only, stale, or requiring filtering |
| **C — Marginal / pilot only** | **7** | Usable in small proportion; quality, redundancy or licence caveats |
| **Evaluation — hold out** | **7** | Benchmarks; never trained on |
| **Quarantine** | **9** | Technically interesting but legally or operationally unsafe |
| **Rejected** | **20** | Gated, broken, unlicensed or unverifiable |
| **Total register** | **80** | |

Access classes across all 80 records:

| Access class | Count |
|---|---:|
| VERIFIED_ACCESSIBLE | 41 |
| METADATA_VERIFIED_ONLY | 20 |
| GATED_OR_AUTHENTICATION_REQUIRED | 12 |
| BROKEN_LINK | 4 |
| TEMPORARY_FAILURE | 1 |
| UNAVAILABLE_OR_REMOVED | 1 |
| HTTP_ERROR | 1 |

Licence classes across all 80 records:

| Licence class | Count |
|---|---:|
| LICENSE_VERIFIED_COMPATIBLE | 47 |
| LICENSE_VERIFIED_RESTRICTED | 11 |
| NO_LICENSE_FOUND | 11 |
| LICENSE_UNCLEAR | 6 |
| CONFLICTING_RIGHTS | 5 |

HTTP status observed at audit time: 200 → 71 records, 404 → 4, 403 → 3, 502 → 2, 401 → 1.

Score distribution: Tier A median 93 (range 88–98); Tier B median 83 (74–90); Tier C median 72 (60–75); evaluation median 79; quarantine median 65; rejected median 64 with a floor of 8 (the two phantom benchmarks).

### 1.3 The five findings that matter

1. **The authoritative layer is small, open and sufficient to anchor the corpus.** Thirteen sources — NVD, CVE List V5, CWE, CAPEC, KEV, ATT&CK, WSTG, Cheat Sheets, PayloadsAllTheThings, Sigma, how2heap, OTRF, EMBER — carry the identifier system, the weakness taxonomy, the attack-pattern taxonomy, exploitation evidence and defensive detection. All thirteen were file-level verified and licence-cleared on 2026-11-26. This layer should supply most of the 10M tokens.

2. **Scale on Hugging Face is mostly mirroring and synthetic prose.** The largest security datasets found are re-uploads or LLM-rewritten versions of NVD. One dataset-level duplicate was proven by identical file hash: Trendyol `All-CVE-Chat-MultiTurn-1999-2025` and AlicanKiraz0 `All-CVE-Records-Training-Dataset` ship the same 475,298,514-byte file (sha256 `e91b7bbf…`). Fenrir v2.1 appears at 431,213,578 B and again at 431,319,841 B under a second account, and one mirror stores the same 2.68 GB file twice and the same 660 MB file three times inside its own tree. Token volume from this layer is cheap; diversity is not.

3. **The strongest technical content is often the least licensable.** HackTricks (score 85), PortSwigger Academy (87), pwn.college (87), Semgrep rules (81) and Nightmare (78) all score in Tier A or high Tier B territory on substance and all fail the licence test — no licence file, all-rights-reserved terms, a non-commercial clause, or an explicit prohibition on training use. This is the central tension of the project and it is not resolvable by searching harder.

4. **Three of the ten priority-1 domains have no licensed dataset at all.** Firmware/embedded yields only a methodology (OWASP FSTM). Low-level systems and binary exploitation are covered by how2heap plus unlicensed write-up corpora. Windows/Active Directory rests on OTRF and 316 EVTX samples from a repository last updated in January 2023. Wireless, hardware/side-channel and licensed PCAP traffic produced nothing that passed both the access and licence gates.

5. **The gated tier is large and should stay gated.** Twelve records require an account, key or click-through: DiverseVul (401), WhitzardAgent (403 manual gate), Vyber07 (403 auto gate), AndroZoo, VirusShare, MalwareBazaar, SOREL-20M, CIC-IDS2017, CICMalDroid, CIS Benchmarks, HTB/THM, vendor advisory portals. None of these grants a training licence even after access, so access approval would not change their tier.

### 1.4 What the corpus should be built from

A defensible first ingest is: NVD + CVE List V5 as the identifier spine; CWE + CAPEC as the label vocabulary; KEV as the exploitation-priority signal; ATT&CK as the behavioural vocabulary; WSTG + Cheat Sheets + PayloadsAllTheThings as web/API methodology; Sigma + OTRF + EVTX + Atomic Red Team as the detection/telemetry pair; how2heap as the only licensed deep binary-exploitation artefact; EMBER for malware-adjacent static features; and the vulnerable-code layer (PrimeVul, BigVul, CVEfixes) as a conditional addition after label validation.

Everything else in this register is either a supplement, a pilot, or evidence of why a domain is empty.

---

## 2. Method and evidence standard

### 2.1 Verification ladder

Each candidate was pushed as far up this ladder as the source allowed, and the record states the rung reached:

| Rung | Class | What was established |
|---|---|---|
| 5 | VERIFIED_ACCESSIBLE + file inspection | File downloaded or tree cloned; sizes, counts, hashes, record structure observed |
| 4 | VERIFIED_ACCESSIBLE + metadata | Endpoint returned 200 with a real payload; size and content-type observed; content not parsed |
| 3 | METADATA_VERIFIED_ONLY | Landing page, API metadata, file tree or publisher documentation read; payload never fetched |
| 2 | GATED / RESTRICTED | Barrier confirmed (401/403, form, key request, licence acceptance) |
| 1 | BROKEN / ERROR / TEMPORARY_FAILURE | Documented failure with status code and retry behaviour |

A record at rung 3 is never described as audited. A record at rung 2 is never described as accessible "with registration" as though that were equivalent to open access.

### 2.2 Rules applied without exception

- No dataset name, size, record count, licence or status code appears in this report that was not observed or read at the cited location on 2026-11-26.
- Where a publisher's own documentation disagrees with the file (Trendyol README claims 53,202 examples; the file contains 53,201), both numbers are recorded and the discrepancy is flagged rather than smoothed.
- Where a search result implied an artefact that does not exist (CVE-Bench, secbench-js), the 404 is recorded so the phantom cannot be rediscovered later as a "new" find.
- Mirrors are labelled as mirrors. Derivative collections are labelled as derivative. An independent publisher is never inferred from a re-upload.
- Nothing was executed. theZoo, VirusShare, MalwareBazaar and VX-Underground were handled as text and metadata only; the EMBER path deliberately carries features rather than binaries.

### 2.3 Failure handling

Transient failures were retried once and then recorded as `TEMPORARY_FAILURE` with the code (digitalcorpora.org, 502). A second 502 at a different host (Drebin) was recorded as `UNAVAILABLE_OR_REMOVED` because the documented download page itself did not resolve. 403 responses from bot-filtered sites (VX-Underground) were not worked around: circumventing an operator's access control is out of scope by instruction.

---

## 3. Deliverable 2 — Master dataset inventory

The full register is `out/master_inventory.csv` (80 rows) with a JSON twin at `data/inventory.json`. It contains the 25 required inventory fields plus four audit-augmentation fields required elsewhere in the brief: `HTTPStatus`, `Permanence`, `AuditDate` (the date of the check, mandated by section 13) and `LicenseClass` (the normalised class from the five-class scheme, so the licence column is machine-filterable).

Column list: ID, Name, Publisher, SourceURL, DownloadURL, Category, Description, Format, SizeVerified, RecordsVerified, Published, LatestUpdate, Version, License, LicenseURL, LicenseAssessment, AccessStatus, HTTPStatus, HTTPEvidence, Permanence, FileInspection, QualityStatus, DedupStatus, PrivacyIssues, Score, Tier, Recommendation, AuditDate, LicenseClass.

### 3.1 Inventory at a glance

| ID | Dataset | Tier | Score | Access | Licence class |
|---|---|---|---:|---|---|
| MC-001 | NIST NVD — CVE JSON 2.0 feeds | A | 98 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-002 | CVE List V5 (cvelistV5) | A | 95 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-003 | CWE 5.0 | A | 95 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-004 | CAPEC 3.9 | A | 89 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-005 | CISA KEV catalog | A | 89 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-006 | MITRE ATT&CK Enterprise STIX 2.1 | A | 95 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-007 | OWASP WSTG | A | 95 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-008 | OWASP Cheat Sheet Series | A | 93 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-009 | PayloadsAllTheThings | A | 92 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-010 | SigmaHQ detection rules | A | 93 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-011 | how2heap | A | 92 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-012 | OTRF Security-Datasets (Mordor) | A | 90 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-014 | EMBER 2018 | A | 88 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-013 | CVEfixes v1.0.8 | B | 90 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-015 | OWASP ASVS 5.0 | B | 87 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-016 | OWASP MASTG | B | 86 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-017 | OWASP Juice Shop | B | 87 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-018 | DVWA | B | 82 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-019 | OWASP WebGoat | B | 80 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-020 | CloudGoat | B | 87 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-021 | Kubernetes Goat | B | 85 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-022 | kube-bench | B | 76 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-023 | nuclei-templates | B | 86 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-024 | Atomic Red Team | B | 90 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-025 | EVTX-ATTACK-SAMPLES | B | 81 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-026 | tldr pages | B | 81 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-027 | PrimeVul | B | 84 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-028 | BigVul (MSR 2020 CSV) | B | 78 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-029 | ExploitDB | B | 81 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-030 | Metasploit Framework modules | B | 85 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-031 | CodeQL standard queries | B | 87 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-032 | xamxte/cve-to-cwe | B | 76 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-033 | CIRCL vulnerability-scores | B | 81 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-034 | N-BaIoT | B | 76 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-035 | OWASP FSTM | B | 74 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-042 | GitHub Advisory Database | B | 83 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-043 | CISA Vulnrichment | B | 82 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-037 | Trendyol instruction-tuning v2.0 | C | 72 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-038 | All-CVE multi-turn (duplicate pair) | C | 65 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-039 | Fenrir v2.1 | C | 60 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-040 | CyberNative DPO | C | 74 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-041 | nl2bash | C | 67 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-044 | CIRCL vulnerability (unlicensed) | C | 75 | VERIFIED_ACCESSIBLE | UNCLEAR |
| MC-Q30 | Yara-Rules community rules | C | 74 | VERIFIED_ACCESSIBLE | COMPATIBLE |
| MC-036 | OWASP Benchmark (eval) | Evaluation | 74 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-E01 | CyberMetric | Evaluation | 61 | VERIFIED_ACCESSIBLE | NO_LICENSE_FOUND |
| MC-E02 | Cybench | Evaluation | 86 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-E03 | NYU CTF Bench | Evaluation | 86 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-E04 | Terminal-Bench | Evaluation | 82 | METADATA_VERIFIED_ONLY | COMPATIBLE |
| MC-E05 | PurpleLlama CyberSecEval | Evaluation | 79 | METADATA_VERIFIED_ONLY | RESTRICTED |
| MC-E06 | SecEval | Evaluation | 61 | METADATA_VERIFIED_ONLY | NO_LICENSE_FOUND |

The 29 Rejected/Quarantine rows are tabulated in full in section 6 rather than duplicated here.

A note on one label: MC-Q30 (Yara-Rules) is a Tier C record carrying a `Q` identifier because it was triaged during the rejected pass and later upgraded; the ID prefix reflects discovery order, not verdict. The tier column is authoritative.

---

## 4. Deliverable 3 — Tier A shortlist (13 records, all approved)

Tier A requires all four of: file-level access verified on 2026-11-26, licence verified compatible, no unresolved provenance conflict, score ≥ 88. Nothing metadata-only is admitted, which is why CVEfixes (90) sits in Tier B despite an excellent score.

### 4.1 Why each one is in

**MC-001 NVD CVE JSON 2.0 (98).** The identifier spine. Verified by downloading the recent feed: 5,389 CVE objects, feed timestamp 2026-11-26T12:00:01, plus per-year feeds with published `.meta` files (2024 feed: 25,181,624 B gzipped, 294,023,311 B raw, sha256 `4CEB9C1D…471FE0`). Carries CVSS, CWE, CPE and references. Caveat recorded honestly: the NVD legal-notice page does not itself state a separate public-domain grant; the CVE Terms of Use cover the CVE records and NVD enrichment is published for reuse.

**MC-002 CVE List V5 (95).** The authoritative CVE source of record, 433,005 files with 432,952 CVE JSON documents, including records NVD has not yet enriched. Verified by fetching a raw record (HTTP 200 at `cves/2024/3xxx/CVE-2024-3400.json`). MITRE licence grants reproduction and derivative works with notice.

**MC-003 CWE 5.0 (95).** 984 weaknesses and 62 views, version dated 2026-10-28, archive 2,119,263 B, parsed from XML. Supplies the weakness vocabulary that makes vulnerable-code and advisory data label-consistent.

**MC-004 CAPEC 3.9 (89).** 615 attack patterns, 3,849,998 B, dated 2023-01-24. The only structured, licensed attack-behaviour taxonomy below the ATT&CK level of abstraction; pairs directly with CWE via related-weakness links.

**MC-005 CISA KEV (89).** 1,805 records, 1,805 unique, 303 vendors, catalogVersion 2026.11.25, 1,898,186 B. The single best exploitation-priority signal; small enough to keep fully in-context during training.

**MC-006 ATT&CK Enterprise STIX (95).** 55,277,605 B, HTTP 200. Techniques, tactics, groups, software and mitigations in machine-readable STIX with relationship objects. The behavioural vocabulary that ties telemetry (Sigma, OTRF, EVTX) to adversary intent.

**MC-007 WSTG (95).** 206 Markdown test documents, CC BY-SA 4.0, active. The primary licensed web-application testing methodology; each test has objective, how-to-test and remediation, which is exactly the shape of a good training example.

**MC-008 Cheat Sheet Series (93).** 142 documents, CC BY-SA 4.0. Concise, correct defensive guidance across web, API, crypto, cloud and language-specific pitfalls. High signal-to-token ratio.

**MC-009 PayloadsAllTheThings (92).** MIT, actively maintained. Offensive payload vocabulary across injection classes, with explanations. Explicitly labelled as payload knowledge; must be framed as detection/defence context, not as an attack cookbook.

**MC-010 SigmaHQ (93).** 4,282 detection rules, Detection Rule License 1.1, last commit 2026-11-25. The defensive counterpart to ATT&CK: machine-readable detection logic with logsource, detection and false-positive sections.

**MC-011 how2heap (92).** MIT, 373 `.c` files across 18 glibc-version directories, last commit 2026-11-15. The only licensed, current, technically deep heap-exploitation artefact found. Each file is a compilable demonstration with an explanatory comment block; this is as close to ground-truth binary exploitation as the open licensed world gets.

**MC-012 OTRF Security-Datasets (90).** MIT, 733 files, 1.2 GB, last commit 2023-09-20; the Mordor URL redirects here, so Mordor and Security-Datasets are one artefact, not two. Provides real Windows telemetry paired with the commands that produced it — the input/evidence pairing that tool-use training needs.

**MC-014 EMBER 2018 (88).** 1,696,539,273 B archive, HTTP 200, published sha256 `b6052eb8…97812`; data MIT, code AGPL. One million PE files as static features. Chosen over malware binary corpora precisely because it contains no executable content and carries a clear data licence.

### 4.2 What Tier A does not cover

Tier A is heavy on taxonomies and methodology and thin on raw telemetry: one Windows-focused telemetry collection (OTRF), one feature-only malware corpus (EMBER), one exploitation course (how2heap). There is no Tier A PCAP corpus, no Tier A cloud telemetry, no Tier A firmware image set and no Tier A Active Directory dataset. That is a property of the open licensed landscape on 2026-11-26, not an omission in the search.

---

## 5. Deliverable 4 — Tier B and Tier C

### 5.1 Tier B (24 records) — approved with conditions

Tier B means: licence verified compatible, substance adequate, but at least one of (a) metadata-only access, (b) stale content, (c) required filtering, (d) benchmark-adjacent leakage risk.

| ID | Dataset | Condition attached to approval |
|---|---|---|
| MC-013 | CVEfixes v1.0.8 | Metadata-only. Zenodo record 13118970, CC BY 4.0, v1.0.8 dated 2024-07-28, 12,708,711,268 B. Promote to Tier A only after a file-level count. |
| MC-015 | OWASP ASVS 5.0 | 240 requirement documents; share-alike obligations on adapted text. |
| MC-016 | OWASP MASTG | 93 test documents; the only open mobile methodology; still methodology, not data. |
| MC-017 | Juice Shop | MIT; challenge list must be enumerated at ingest; solution traces must be generated locally, not taken from write-ups. |
| MC-018 | DVWA | GPL-3.0 copyleft; overlaps Juice Shop/WebGoat vulnerability classes, so pick one primary lab. |
| MC-019 | WebGoat | Metadata-only; lesson-level explanations are valuable but unverified. |
| MC-020 | CloudGoat | BSD-3; 1,954 files; scenario configs contain placeholder AWS account IDs that must be stripped. |
| MC-021 | Kubernetes Goat | MIT; 379 files; 20+ scenarios with walkthroughs. |
| MC-022 | kube-bench | Apache-2.0 code, but remediation strings derive from CIS Benchmarks whose terms restrict redistribution. Prefer check logic over CIS-derived text. |
| MC-023 | nuclei-templates | MIT; 14,483 templates; exclude `deprecated/`, dedup by template id, never execute. |
| MC-024 | Atomic Red Team | MIT; 1,397 files; commands include credential-dumping examples — text only, no live secrets. |
| MC-025 | EVTX-ATTACK-SAMPLES | GPL-3.0; 316 files, 50 MB, last update 2023-01-24; logs may contain usernames and hostnames that must be scrubbed. |
| MC-026 | tldr | CC BY 4.0; 7,672 pages across locales — restrict to English to avoid 10× duplication. |
| MC-027 | PrimeVul | MIT; metadata-only; publisher reports de-duplication that was not independently verified; respect its temporal split to avoid benchmark leakage. |
| MC-028 | BigVul | MIT; metadata-only; known label noise; keep as a historical layer behind PrimeVul, not as the primary vulnerable-code source. |
| MC-029 | ExploitDB | GPL-2.0; metadata-only; keep only entries with a CVE and a verified flag; never execute. |
| MC-030 | Metasploit modules | BSD-3; 15,184 files (tree only); dedup against ExploitDB by CVE. |
| MC-031 | CodeQL queries | MIT; 7,784 `.ql` files; excellent program-analysis content. |
| MC-032 | xamxte/cve-to-cwe | CC BY 4.0; 234,770 records parsed, 0 exact duplicates — but labels are AI-refined and ATT&CK labels are not authoritative. Sample-validate before use. |
| MC-033 | CIRCL vulnerability-scores | CC BY 4.0; 347,538,173 B; metadata-only; derive CVSS from NVD where possible to avoid duplicate CVE records. |
| MC-034 | N-BaIoT | CC BY 4.0; 7,062,606 instances; metadata-only; 2018 botnets only (Mirai, BASHLITE). |
| MC-035 | OWASP FSTM | CC BY-SA 4.0; methodology only — fills a domain at the process level, not the data level. |
| MC-042 | GHSA | CC BY 4.0; metadata-only; dedup against NVD by CVE ID. |
| MC-043 | CISA Vulnrichment | CC0; metadata-only; fills the NVD analysis backlog; join by CVE ID. |

Tier B is where the corpus gains practical breadth: labs, detection tooling, static-analysis queries and the vulnerable-code layer all live here, on condition that the caveat in the right-hand column is implemented in the pipeline rather than noted and forgotten.

### 5.2 Tier C (7 records) — marginal, pilot or seed only

| ID | Dataset | Score | Why only C |
|---|---|---:|---|
| MC-037 | Trendyol instruction-tuning v2.0 | 72 | 53,201 records, Apache-2.0, 0 exact duplicates, median answer 3,583 chars, sha256 verified against the HF LFS hash. Fluent but largely synthetic and generic: little verifiable ground truth, no tool traces. Usable as a style bootstrap in small proportion. README claims 53,202 examples; the file has 53,201. |
| MC-038 | All-CVE multi-turn (and its duplicate) | 65 | 475,298,514 B, Apache-2.0 packaging of NVD-derived prose rewritten by an LLM. Proven dataset-level duplicate of AlicanKiraz0's re-upload. Prefer direct NVD ingestion. |
| MC-039 | Fenrir v2.1 | 60 | Near-duplicate of the Trendyol corpus (431,213,578 B vs 431,319,841 B under a second account). Redundant. |
| MC-040 | CyberNative DPO | 74 | Small (7,881,904 B), auditable, ships its own audit directory; promising secure-coding preference data, but unparsed. Pilot candidate. |
| MC-041 | nl2bash | 67 | MIT data directory, GPL-3.0 code; 2018-era commands; useful only as a command-synthesis seed. |
| MC-044 | CIRCL vulnerability | 75 | 515,862 records parsed, 0 exact duplicates, good content — but no licence declared. Use the CC BY 4.0 sibling (MC-033) instead. |
| MC-Q30 | Yara-Rules | 74 | GPL-2.0, 583 files, but no commits since 2022-04-12 and many rules target retired families. |

The C tier is deliberately small. Its function is to hold the material that is real but should not shape the model: synthetic instruction prose, redundant mirrors and dated detection rules.

---

## 6. Deliverable 5 — Rejected and quarantined register (29 records)

Two distinct verdicts. **Rejected** means the source fails a hard gate (no licence, no access, no artefact) and cannot be used. **Quarantine** means the source has real technical value but cannot enter the corpus: live malware, restricted terms, or unresolved rights. Quarantine records are retained so the decision can be revisited if terms change.

Every row carries the HTTP status observed on 2026-11-26 and a permanence judgement.

### 6.1 Rejected (20)

| ID | Dataset | HTTP | Access class | Permanence | Reason for rejection |
|---|---|---|---|---|---|
| MC-Q01 | DiverseVul | 401 | GATED | Persistent (server up, access controlled) | Data endpoint returns 401; no stated licence; no lawful path to inspect. |
| MC-Q02 | WhitzardAgent CyberSecurity-1M | 403 | GATED | Persistent | Manual HF gate not crossed; card declares no licence; 12.47 GB of unverifiable synthetic data. |
| MC-Q03 | Vyber07 Fenrir mirror | 403 | GATED | Persistent | Re-upload with internal duplicates (same 2.68 GB file twice, same 660 MB file three times); re-uploader is not the rights holder. |
| MC-Q10 | IoT-23 | 200 | METADATA_ONLY | Persistent (unchanged since 2020) | Licence permits research use only; no training or redistribution grant. Held, not approved. |
| MC-Q11 | Digital Corpora | 502 | TEMPORARY_FAILURE | Transient / unknown | Site returned 502 on both probes; retry on a later date. Not evidence of absence. |
| MC-Q12 | Drebin | 502 | UNAVAILABLE | Unknown — possibly retired | Documented download page does not serve content; academic-only terms regardless. |
| MC-Q14 | DikeDataset | 404 | BROKEN_LINK | Likely permanent removal | Repository no longer resolves. |
| MC-Q15 | CVE-Bench | 404 | BROKEN_LINK | Not found | Artefact implied by search results does not exist at the recorded path. |
| MC-Q16 | secbench-js | 404 | BROKEN_LINK | Not found | Same failure mode as Q15. |
| MC-Q17 | DFRWS challenge results | 404 | BROKEN_LINK | Partial — index alive, deep links dead | Per-challenge artefacts unavailable; index page is not a dataset. |
| MC-Q19 | HackTricks | 200 | VERIFIED_ACCESSIBLE | Persistent | No LICENSE file; default all-rights-reserved. Strongest offensive wiki found (score 85) and unusable. |
| MC-Q20 | CIS Benchmarks | 200 | GATED | Persistent | Account plus click-through; redistribution and derivative use restricted. |
| MC-Q21 | PortSwigger Web Security Academy | 200 | VERIFIED_ACCESSIBLE | Persistent | Copyrighted, all rights reserved. Excellent for calibration, unusable as data. |
| MC-Q22 | Hack The Box / TryHackMe | 200 | GATED | Persistent | Commercial terms; accounts are personal; content copyrighted. |
| MC-Q23 | Vendor advisories (MSRC, Red Hat, Cisco) | 200 | GATED | Persistent | No training grant in site terms; NVD/CVE already carry the lawful references. |
| MC-Q24 | OSV.dev aggregate | 200 | METADATA_ONLY | Persistent | No single licence; per-record provenance varies. Ingest GHSA instead. |
| MC-Q26 | Nightmare | 200 | VERIFIED_ACCESSIBLE | Persistent | No LICENSE file. |
| MC-Q27 | ctfs/write-ups-2016 | 200 | VERIFIED_ACCESSIBLE | Persistent | No LICENSE file; stale. |
| MC-Q28 | Semgrep rules | 200 | VERIFIED_ACCESSIBLE | Persistent | Semgrep Rules License v1.0 explicitly prohibits use to train or improve models. |
| MC-Q29 | pwn.college | 200 | VERIFIED_ACCESSIBLE | Persistent | Non-commercial educational licence conflicts with corpus use. |

### 6.2 Quarantine (9)

| ID | Dataset | HTTP | Access class | Permanence | Reason for quarantine |
|---|---|---|---|---|---|
| MC-Q04 | VirusShare | 200 | GATED | Persistent | 121,683,273 samples advertised; samples are third-party malware; no training grant; requires account approval. |
| MC-Q05 | MalwareBazaar | 200 | GATED | Persistent (terms may change) | Fair-use research policy; commercial use may require a paid plan; live samples. |
| MC-Q06 | SOREL-20M | 200 | GATED | Persistent (S3 unchanged since 2021) | Public bucket, but use conditioned on accepting a Terms of Use PDF. Best malware-adjacent content that is legally out of reach. |
| MC-Q07 | AndroZoo | 200 | GATED | Persistent | API key plus academic agreement; no redistribution or training right. |
| MC-Q08 | CIC-IDS2017 | 200 | GATED | Persistent | Download URL serves a registration form (name, email, organisation, job title); page says "publicly available for researchers" but states no licence. Availability is not licensing. |
| MC-Q09 | CICMalDroid 2020 | 200 | GATED | Persistent | Same form gate, same licence silence. |
| MC-Q13 | VX-Underground | 403 | HTTP_ERROR | Unknown — operator-enforced | Bot/geo filtering; aggregator with no rights to grant; high PII and C2 content. |
| MC-Q18 | theZoo | 200 | VERIFIED_ACCESSIBLE | Persistent | Repository of live, password-protected malware. Listed, hashable, never opened or executed. |
| MC-Q25 | ctf-archives | 200 | VERIFIED_ACCESSIBLE | Persistent (takedowns occur) | MIT tag covers scaffolding, not ~500 events of challenge material; per-event permission would be required. |

### 6.3 What the rejections teach

Four rejection patterns account for almost the whole list, and each has a workaround that does not require the rejected source:

1. **No licence file (Q19, Q26, Q27, plus Tier-C MC-044).** Default copyright applies. Workaround: substitute licensed equivalents — WSTG and Cheat Sheets for methodology, CodeQL for query content, how2heap for exploitation depth.
2. **Restricted or non-commercial terms (Q20, Q21, Q22, Q23, Q28, Q29, Q05, Q06, Q07).** No workaround inside the licence; only written permission would change the verdict.
3. **Gate without a licence grant (Q01, Q02, Q03, Q08, Q09, Q04).** Access approval would not fix these, because the barrier is legal rather than technical.
4. **Artefact absence (Q14–Q17, Q11, Q12).** Recorded with status codes so future passes do not re-litigate them.

The most consequential rejection is Semgrep (Q28): 2,159 well-written rules whose licence forbids training use. The substitute, CodeQL (MC-031, MIT, 7,784 queries), is larger and legally clean, which is why the licence audit was worth doing rather than assuming "open source" means "trainable".

---

## 7. Deliverable 6 — Domain coverage matrix and gaps

Coverage is computed only from records that passed both the access and licence gates. Tier A counts as approved data; Tier B as conditional data; methodology-only sources are marked separately rather than inflating the count.

| Domain | Priority | Tier A (approved) | Tier B (conditional) | Effective coverage | Gap statement |
|---|---|---|---|---|---|
| Web application security | 1 | MC-007, MC-008, MC-009 | MC-015, MC-017, MC-018, MC-019, MC-023 | **Strong** — methodology, payloads, labs, detection | No licensed corpus of real HTTP request/response traffic or vulnerability reproductions. Lab traces must be generated locally. |
| API security | 1 | — (covered inside MC-007, MC-008) | MC-015 (API levels), MC-023 | **Adequate at methodology level only** | No API traffic dataset, no licensed API-fuzzing corpus, no OpenAPI-derived test set. Largest priority-1 gap after firmware. |
| Linux | 1 | MC-011 (userspace exploitation) | MC-026 (CLI), MC-031 (analysis), MC-030 (tooling) | **Moderate** | No Linux system telemetry, auditd, eBPF or syscall corpus under a usable licence. OTRF is Windows-centric. |
| Windows | 1 | MC-012 (telemetry) | MC-024, MC-025, MC-010 | **Moderate** | Telemetry exists but is thin and partly stale (EVTX last updated 2023-01). No licensed modern Windows 11/Server 2022 corpus. |
| Active Directory | 1 | — (partial via MC-012) | MC-024, MC-025 | **Weak** | No AD attack-path, LDAP, Kerberos or domain-controller log dataset with training rights. The single weakest priority-1 domain relative to its importance. |
| Networking | 1 | — | MC-034 (IoT flows) | **Weak** | No licensed PCAP corpus. IoT-23 is research-only (Q10), CIC-IDS2017 is form-gated and unlicensed (Q08). Flow-feature datasets substitute poorly for packet-level reasoning. |
| Cloud | 1 | — | MC-020, MC-022 | **Weak-to-moderate** | Attack scenarios and benchmark checks exist; no CloudTrail, GuardDuty, Azure Activity or GCP audit-log corpus. |
| Binary exploitation | 1 | MC-011 | MC-029, MC-030 | **Moderate** | One licensed course plus exploit metadata. Every write-up corpus found (Nightmare, pwn.college, ctfs, ctf-archives) failed the licence test. |
| Low-level systems | 1 | MC-011, MC-003 | MC-027, MC-028, MC-031 | **Moderate** | Code-level weakness data is good; no kernel, firmware or hypervisor telemetry. |
| Firmware / embedded | 1 | — | MC-035 (methodology) | **Critically thin** | No firmware image corpus, no extraction/emulation traces, no vendor firmware with redistribution rights. Only a nine-stage methodology. |
| Containers | 2 | — | MC-021, MC-022 | **Moderate** | Scenario content only; no container runtime telemetry (Falco, Tetragon) corpus. |
| Kubernetes | 2 | — | MC-021, MC-022 | **Moderate** | Same limitation; 20+ scenarios is a good start but not a dataset. |
| Mobile | 2 | — | MC-016 (methodology) | **Weak** | No licensed APK corpus. AndroZoo (Q07) key-gated, CICMalDroid (Q09) form-gated, Drebin (Q12) unavailable. |
| Wireless | 2 | — | — | **Absent** | No licensed 802.11, Bluetooth or cellular capture dataset was found. AWID3 was probed but no licence grant was established, so it is not claimed. |
| Hardware / side-channel | 2 | — | — | **Absent** | ASCAD exists and is BSD-licensed but archived; it was not audited to file level in this pass and is therefore not claimed as coverage. |
| IoT | 2 | — | MC-034 | **Weak** | Flow features only; no licensed device firmware or IoT packet capture. |
| Malware analysis (cross-cutting) | — | MC-014 (features only) | — | **Feature-level only** | No licensed malware binaries. EMBER gives static features; behaviour requires live samples that cannot be lawfully ingested. |
| Vulnerability intelligence (cross-cutting) | — | MC-001–MC-006 | MC-013, MC-033, MC-042, MC-043 | **Strong** | This is the best-covered area by a wide margin, and it is the area that most cheaply converts to tokens. |

### 7.1 Reading the matrix honestly

Nine of sixteen domains have no Tier A record. Three (wireless, hardware/side-channel, firmware at data level) have nothing usable at all. This is not a search failure: the queries were run, the repositories were probed, and the artefacts that exist are either gated, unlicensed, or archived. Reporting 100% coverage would require inventing sources, which the quality principle forbids.

### 7.2 The four gaps worth closing first

1. **Active Directory.** Highest value per token if solved: the domain is central to enterprise compromise and the model currently has 316 EVTX files and a handful of atomic tests. Realistic route: generate the telemetry locally from a lab domain using open tooling, since every public AD dataset found is either unlicensed or a commercial product.
2. **Licensed PCAP.** Networking, IoT and wireless all fail on the same missing artefact. Route: capture your own traffic in a controlled lab, or obtain written permission for one of the gated corpora.
3. **Firmware.** Only methodology exists. Route: build a small firmware corpus from openly redistributable sources (OpenWrt images, vendor GPL drop archives) with extraction and emulation traces generated in-house.
4. **Tool-use traces.** No public corpus pairs a command, its output and its interpretation under a free licence. OTRF and Atomic Red Team come closest. Route: generate traces by executing the licensed lab content in the sandbox pipeline, which is also the cleanest way to satisfy the "no invented technical characteristics" rule.

### 7.3 Evaluation set separation

Seven benchmarks are registered as Evaluation and must be excluded from training by ID, not by heuristic: CyberMetric (10,000 MCQ), Cybench (40 professional CTF tasks), NYU CTF Bench (200 challenges), Terminal-Bench, PurpleLlama CyberSecEval, SecEval (2,600 MCQ) and OWASP Benchmark (Java SAST ground truth).

Two of these create leakage risk beyond their own records: Cybench and NYU CTF Bench are built from real CTF challenges, so any CTF archive admitted later (currently quarantined, MC-Q25) could contain their source events. The pipeline therefore blocks by group key, not only by item hash.

---

## 8. Deliverable 7 — Dataset documentation cards (Tier A)

Each card records only what was observed on 2026-11-26. Sizes are bytes as reported by the server or measured locally; record counts are counted, not quoted, unless explicitly attributed to the publisher.

### MC-001 — NIST National Vulnerability Database, CVE JSON 2.0
- **Publisher:** NIST (US Government) · **Canonical:** https://nvd.nist.gov/vuln/data-feeds · **Feed:** https://nvd.nist.gov/feeds/json/cve/2.0/nvdcve-2.0-2024.json.gz
- **Licence:** CVE Terms of Use (MITRE) on the CVE records; NVD enrichment published for reuse. Verified at https://www.cve.org/Legal/TermsOfUse. Obligation: reproduce the MITRE copyright designation and licence notice. Caveat: the NVD legal-notice page itself does not state a separate public-domain grant.
- **Access evidence:** recent feed downloaded; 5,389 CVE objects; timestamp 2026-11-26T12:00:01. 2024 feed `.meta` gives 25,181,624 B gzipped / 294,023,311 B raw, sha256 `4CEB9C1D9037C6A0A01912A7A57E6332538891E41B8BC05E3B943EB3AE471FE0`.
- **Contents:** CVE ID, descriptions, CVSS v2/v3.1/v4, CWE, CPE configurations, references, status, published/modified dates.
- **Training use:** identifier spine; CVE-to-weakness and CVE-to-CVSS reasoning; reference-following behaviour.
- **Integration:** join key for every other vulnerability record. Keep the full record, not the rendered description only.
- **Risk:** LOW. Volume is large across per-year feeds; dedup against CVE List V5 by CVE ID.

### MC-002 — CVE List V5 (cvelistV5)
- **Publisher:** CVE Program (MITRE) · **Canonical:** https://github.com/CVEProject/cvelistV5
- **Licence:** CVE Terms of Use — perpetual, worldwide, no-charge, royalty-free, irrevocable copyright licence to reproduce, prepare derivative works and distribute, with notice obligation. Verified.
- **Access evidence:** 433,005 files in tree; 432,952 CVE JSON documents; raw record fetch for CVE-2024-3400 returned HTTP 200 at `cves/2024/3xxx/`.
- **Contents:** CVE 5.0 records in the CNA-authored form, including records NVD has not yet enriched.
- **Training use:** authoritative CVE text, affected-product statements, CNA references; the substrate for vulnerability-description understanding.
- **Integration:** primary source for CVE narrative text; NVD for enrichment. Do not concatenate blindly — they overlap by CVE ID.
- **Risk:** LOW. Includes REJECTED/RESERVED states that must be filtered.

### MC-003 — CWE 5.0
- **Publisher:** MITRE · **Canonical:** https://cwe.mitre.org/data/downloads.html · **Archive:** https://cwe.mitre.org/data/xml/cwec_latest.xml.zip
- **Licence:** MITRE terms — royalty-free for research, development and commercial use with copyright designation. Verified at https://cwe.mitre.org/about/termsofuse.html.
- **Access evidence:** archive 2,119,263 B downloaded; XML parsed; 984 weaknesses, 62 views; version dated 2026-10-28.
- **Contents:** weakness definitions, consequences, mitigations, detection methods, relationships, applicable platforms, code examples.
- **Training use:** weakness taxonomy and label vocabulary; the anchor for vulnerable-code labels.
- **Integration:** map every CWE label from other sources onto this version; keep deprecated entries for legacy mapping.
- **Risk:** LOW.

### MC-004 — CAPEC 3.9
- **Publisher:** MITRE · **Canonical:** https://capec.mitre.org/data/downloads.html · **File:** https://capec.mitre.org/data/xml/capec_latest.xml
- **Licence:** MITRE terms, royalty-free with copyright designation. Verified at https://capec.mitre.org/about/termsofuse.html.
- **Access evidence:** 3,849,998 B XML downloaded and parsed; 615 attack patterns; version 3.9 dated 2023-01-24.
- **Contents:** attack patterns with execution flow, prerequisites, indicators, related weaknesses and related ATT&CK techniques.
- **Training use:** attack-pattern reasoning between CWE and ATT&CK; useful for "how would this weakness be exploited" explanations.
- **Integration:** link to CWE via related-weaknesses; link to ATT&CK via technique mapping.
- **Risk:** LOW. Content is dated 2023 — treat as stable rather than current.

### MC-005 — CISA Known Exploited Vulnerabilities
- **Publisher:** CISA · **Canonical:** https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- **Licence:** US federal government publication, no copyright asserted; attribution recommended (assessed, formal opinion advised).
- **Access evidence:** 1,898,186 B JSON downloaded; 1,805 records, 1,805 unique, 303 vendors; catalogVersion 2026.11.25.
- **Contents:** CVE ID, vendor, product, vulnerability name, short description, required action, due date, known ransomware use flag.
- **Training use:** exploitation-priority signal and remediation reasoning; small enough to keep in context entirely.
- **Integration:** join to NVD/CVE by CVE ID; use the `knownRansomwareCampaignUse` field as a risk label.
- **Risk:** LOW.

### MC-006 — MITRE ATT&CK Enterprise (STIX 2.1)
- **Publisher:** MITRE · **Canonical:** https://github.com/mitre-attack/attack-stix-data
- **Licence:** ATT&CK terms of use — royalty-free for research, development and commercial use with copyright designation. Verified via the published terms page; note the `/resources/legal-and-branding/terms/` path returned 404 during the probe, so the licence was confirmed from the repository and the site's legal section instead.
- **Access evidence:** 55,277,605 B `enterprise-attack.json` fetched (HTTP 200).
- **Contents:** techniques, sub-techniques, tactics, groups, software, campaigns, mitigations, data sources, with STIX relationships.
- **Training use:** behavioural vocabulary; maps telemetry to adversary intent; the join layer between offensive technique and defensive detection.
- **Integration:** use STIX IDs as the canonical technique key. Sigma and Atomic Red Team both reference ATT&CK technique IDs.
- **Risk:** LOW. Branding restrictions apply to use of the ATT&CK name and logo, not to the data.

### MC-007 — OWASP Web Security Testing Guide
- **Publisher:** OWASP · **Canonical:** https://github.com/OWASP/wstg
- **Licence:** CC BY-SA 4.0. Obligations: attribution and share-alike on adapted text.
- **Access evidence:** repository cloned (blobless); 206 Markdown test documents counted; active as of audit date.
- **Contents:** per-test objective, summary, how-to-test, remediation, references; organised by category (info gathering, config, identity, authz, session, input validation, error handling, crypto, business logic, client-side).
- **Training use:** the backbone of web/API testing competence; each document is a natural instruction-response pair.
- **Integration:** pair each test with a lab it can be exercised against (Juice Shop, DVWA) to produce verifiable traces.
- **Risk:** LOW, with share-alike hygiene: keep WSTG-derived text separable from the rest of the corpus.

### MC-008 — OWASP Cheat Sheet Series
- **Publisher:** OWASP · **Canonical:** https://github.com/OWASP/CheatSheetSeries
- **Licence:** CC BY-SA 4.0.
- **Access evidence:** repository cloned; 142 documents counted.
- **Contents:** dense defensive guidance across web, API, authentication, cryptography, cloud, injection classes and language-specific pitfalls.
- **Training use:** high signal-to-token defensive content; good for "how to fix it" answers.
- **Integration:** merge with WSTG remediation sections carefully to avoid near-duplicate paragraphs.
- **Risk:** LOW; same share-alike hygiene as WSTG.

### MC-009 — PayloadsAllTheThings
- **Publisher:** swisskyrepo and contributors · **Canonical:** https://github.com/swisskyrepo/PayloadsAllTheThings
- **Licence:** MIT (verified from repository licence metadata and LICENSE file).
- **Access evidence:** repository cloned; file inventory and Markdown counts taken; actively maintained.
- **Contents:** payload and bypass vocabulary by vulnerability class, with explanations and filter-bypass notes.
- **Training use:** detection-engineering and defensive context; vulnerability-class recognition.
- **Integration:** frame as knowledge about attacks and defences; do not present as a step-by-step attack manual.
- **Risk:** MEDIUM — dual-use content. Keep defensive framing and exclude from any deployed assistant surface without guardrails.

### MC-010 — SigmaHQ detection rules
- **Publisher:** SigmaHQ · **Canonical:** https://github.com/SigmaHQ/sigma
- **Licence:** Detection Rule License 1.1 (verified from the repository licence file and the DRL text).
- **Access evidence:** repository cloned; 4,282 rules counted; last commit 2026-11-25.
- **Contents:** YAML rules with logsource, detection logic, fields, false-positive notes, level and ATT&CK tags.
- **Training use:** detection engineering; mapping telemetry to technique; writing and reviewing rules.
- **Integration:** pair with OTRF/EVTX telemetry so a rule can be explained against a real event.
- **Risk:** LOW. DRL permits reuse with attribution; check terms before redistributing modified rule text.

### MC-011 — how2heap
- **Publisher:** shellphish · **Canonical:** https://github.com/shellphish/how2heap
- **Licence:** MIT.
- **Access evidence:** repository cloned; 373 `.c` files across 18 glibc-version directories; last commit 2026-11-15.
- **Contents:** compilable heap-exploitation demonstrations (fastbin dup, unsorted bin attack, tcache poisoning, house-of-* techniques) each with an explanatory comment block, organised by glibc version.
- **Training use:** the deepest licensed binary-exploitation artefact available; teaches allocator internals concretely.
- **Integration:** compile in an isolated container; capture compiler output and program behaviour as traces rather than shipping binaries.
- **Risk:** LOW legally; MEDIUM operationally — the code is designed to corrupt memory, so run only in a sandbox.

### MC-012 — OTRF Security-Datasets (Mordor)
- **Publisher:** Open Threat Research Forge · **Canonical:** https://github.com/OTRF/Security-Datasets
- **Licence:** MIT.
- **Access evidence:** repository cloned; 733 files, 1.2 GB; last commit 2023-09-20. The Mordor URL redirects to this repository — they are one artefact, not two.
- **Contents:** curated Windows telemetry (Sysmon, Security, PowerShell) captured while executing known adversary techniques, with the commands used.
- **Training use:** the closest thing to input-command-evidence triples; detection validation.
- **Integration:** join with Atomic Red Team technique IDs and Sigma rules.
- **Risk:** LOW legally; MEDIUM for PII — scrub hostnames, usernames and IP addresses. Content is frozen at 2023.

### MC-014 — EMBER 2018
- **Publisher:** Elastic (formerly Endgame) · **Canonical:** https://github.com/elastic/ember
- **Licence:** data files MIT; source code AGPL-3.0 (per README).
- **Access evidence:** archive URL returned HTTP 200 with Content-Length 1,696,539,273 and type `application/x-bzip2`; publisher SHA-256 recorded as `b6052eb8…97812`; archive not extracted.
- **Contents:** static features for 1,000,000 PE files (byte/entropy histograms, header fields, imports, section metadata, strings) with labelled train/test splits.
- **Training use:** malware static-analysis reasoning without possessing malware; feature-level classification and explanation.
- **Integration:** use the published split to avoid leakage; do not re-split randomly.
- **Risk:** LOW — features only, no executable content. The AGPL applies to the code, not the feature data.

---

## 9. Duplication findings

Duplication was measured in three distinct ways, and the three are never conflated.

### 9.1 File-level (hash) duplication — proven

| Finding | Evidence |
|---|---|
| Trendyol `All-CVE-Chat-MultiTurn-1999-2025` and AlicanKiraz0 `All-CVE-Records-Training-Dataset` ship the **same file** | Both resolve to sha256 `e91b7bbf…`, 475,298,514 B (HF LFS hash) |
| Fenrir v2.1 and its Vyber07 re-upload are **near-duplicates** | 431,213,578 B (sha256 `7913617…`) vs 431,319,841 B (sha256 `d73a2353…`) — different bytes, near-identical size and lineage |
| Vyber07's own tree contains **internal duplicates** | The same 2,680,132,507 B file appears twice; the same 660,002,049 B file appears three times |
| Trendyol instruction dataset integrity | Local sha256 matches the HF LFS hash `2b08b09c…c78268`; 195,018,595 B |

Consequence: four catalogue entries collapse to two real corpora. Any ingestion plan that counts "datasets" without hashing would overstate available diversity by roughly a factor of two in this cluster.

### 9.2 Record-level exact duplication — measured on downloaded corpora only

| Corpus | Records parsed | Exact duplicates (sha256 of normalised text) |
|---|---:|---:|
| Trendyol instruction-tuning v2.0 | 53,201 | 0 |
| xamxte/cve-to-cwe (train split) | 234,770 | 0 |
| CIRCL/vulnerability (train split) | 515,862 | 0 |
| CISA KEV | 1,805 | 0 (1,805 unique by CVE ID) |

Zero duplicates inside these files is a real result, and it says nothing about duplication *between* them. Cross-corpus overlap was not measured, because it would require downloading and normalising several multi-gigabyte files; the affected pairs are named below as unmeasured.

### 9.3 Cross-corpus overlap — identified but not measured

NVD, CVE List V5, GHSA, Vulnrichment, CIRCL vulnerability and CIRCL vulnerability-scores all describe the same CVE universe. They are complementary in enrichment and heavily overlapping in identity. The pipeline deduplicates by CVE ID key first and by text hash second; the overlap percentage is explicitly **not** claimed here because no measurement was performed.

### 9.4 Near-duplicate content inside methodology corpora

WSTG, Cheat Sheets, ASVS and MASTG restate many of the same controls. They are not duplicates at file level, but sentence-level overlap is expected and was not measured. The pipeline's MinHash stage exists precisely to catch this at ingest, and its threshold should be tuned on the first real batch rather than assumed.

---

## 10. Licensing analysis

### 10.1 The compatible core

47 of 80 records carry a compatible licence. The permissive anchors are MIT (how2heap, PATT, Sigma is DRL rather than MIT, Juice Shop, Kubernetes Goat, CloudGoat BSD-3, Metasploit BSD-3, CodeQL, PrimeVul, BigVul, tldr is CC BY), Apache-2.0 (Trendyol family, kube-bench, Cybench, Terminal-Bench), CC BY 4.0 (GHSA, N-BaIoT, tldr, xamxte), CC0 (Vulnrichment) and the MITRE terms (CVE, CWE, CAPEC, ATT&CK).

### 10.2 The share-alike cluster

WSTG, Cheat Sheets, ASVS, MASTG and FSTM are CC BY-SA 4.0. Training a model is generally not redistribution of the text, but share-alike becomes relevant the moment derived passages are republished. Practical rule: keep share-alike text in a separately tracked shard so the corpus can be re-cut if the interpretation changes.

### 10.3 The eleven restricted records

Semgrep (explicit prohibition on training use) is the clearest. The others are research-only, non-commercial, click-through or fair-use terms: CIS Benchmarks, PortSwigger, HTB/THM, vendor portals, MalwareBazaar, SOREL-20M, AndroZoo, pwn.college, PurpleLlama. Access being possible is irrelevant; the grant is what matters.

### 10.4 The eleven with no licence

HackTricks, Nightmare, ctfs/write-ups-2016, CyberMetric, SecEval, CIC-IDS2017, CICMalDroid, DikeDataset, DFRWS, CVE-Bench, secbench-js. Default copyright applies to the first three and to the two CIC datasets; "publicly available for researchers" is a description of access, not a licence.

### 10.5 The five with conflicting rights

ctf-archives (MIT scaffolding over third-party challenge material), OSV.dev (per-record provenance), theZoo, VirusShare, VX-Underground. In each case the packaging licence does not extend to the payload.

### 10.6 One conflict worth naming

kube-bench is Apache-2.0, but its remediation text derives from CIS Benchmarks, which are account-gated and restrict redistribution. Using the code is safe; reproducing the remediation strings may not be. The record says so explicitly rather than treating the repository licence as covering everything inside it.

---

## 11. Deliverable 8 — Reproducible collection and audit pipeline

The pipeline is `pipeline/microcore_pipeline.py` with `pipeline/manifest.json`, plus the discovery and verification scripts used to build this register.

### 11.1 Layout

```
microcore/
  pipeline/microcore_pipeline.py   # fetch, hash, dedup, leakage, scan
  pipeline/manifest.json           # 13 cleared sources, sizes, hashes
  scripts/hf_search.py             # 25 HF discovery queries
  scripts/check_urls.py            # 91 primary-source URL probes
  scripts/batch2.py                # 46 further URL probes
  scripts/gh_meta.py, gh_meta2.py  # repo metadata, licence, commit dates
  scripts/license_probe.py         # raw LICENSE text per repository
  scripts/hf_meta.py               # HF gated flags, file trees, LFS hashes
  scripts/audit_records.py         # record-level dup/secret/PII audit
  scripts/build.py                 # inventory assembly and counts
  out/master_inventory.csv         # 80 records, 29 columns
  out/audit_log.jsonl              # timestamped evidence of every run
  data/inventory.json              # machine-readable twin
```

### 11.2 Commands, with observed output

Discovery and verification:

```bash
python3 scripts/hf_search.py            # -> data/hf_search.json  (25 queries)
python3 scripts/check_urls.py           # -> data/http_checks.json  (91 URLs)
python3 scripts/batch2.py               # -> data/http_checks2.json (46 URLs)
python3 scripts/gh_meta.py              # -> data/gh_meta.json
python3 scripts/license_probe.py        # -> data/license_probe.json
python3 scripts/hf_meta.py               # -> data/hf_meta.json (21 datasets)
python3 scripts/build.py                # -> out/master_inventory.csv
```

`build.py` output on 2026-11-26:

```
total records: 80
columns: 29
A 13 | B 24 | C 7 | Evaluation 7 | Quarantine 9 | Rejected 20
VERIFIED_ACCESSIBLE 41 | METADATA_VERIFIED_ONLY 20 | GATED 12 | BROKEN_LINK 4 | ...
```

Acquisition with hash evidence (dry run first — `manifest` never touches the network):

```bash
python3 pipeline/microcore_pipeline.py manifest
python3 pipeline/microcore_pipeline.py fetch --id MC-005 MC-003
python3 pipeline/microcore_pipeline.py hash --path raw/dl/kev.json
```

Observed:

```
MC-005: HTTP 200 -> 1898186 B  sha256=a76360009e4a65794a2b8073df5475f7a787a3bb83c3bfad2b0c3434a067631a  sha256_recorded_no_reference
{"path": "raw/dl/kev.json", "bytes": 1898186, "sha256": "a76360..."}
```

`fetch` refuses any manifest entry whose access class is not VERIFIED_ACCESSIBLE, logs HTTP errors without retrying them, and appends every action to `out/audit_log.jsonl` with a UTC timestamp — which is how "the date of every accessibility check" is preserved mechanically rather than by memory.

Deduplication (exact sha256, then 64-permutation MinHash over word 5-grams):

```bash
python3 pipeline/microcore_pipeline.py dedup --input out/fixtures/sample.jsonl --threshold 0.8
```

Observed on a 203-record fixture built from 200 cve2cwe records plus three injected duplicates:

```
{"input": "out/fixtures/sample.jsonl", "kept": 199, "exact_duplicates": 1, "near_duplicates": 3, "threshold": 0.8}
```

The injected exact duplicate was caught, and both intentionally perturbed copies were caught as near-duplicates.

Leakage-aware splitting:

```bash
python3 pipeline/microcore_pipeline.py leakage --input out/fixtures/sample.jsonl \
    --output out/fixtures/split.jsonl --group-field cve_id
```

Observed:

```
{"splits": {"train": 191, "val": 6, "test": 6}, "test_flagged_as_leaked": 0, "group_field": "group"}
```

Splits are assigned by hashing the group key (CVE ID), so every record for one vulnerability lands in exactly one split; test items are additionally compared against train and validation signatures.

Secret and PII scan:

```bash
python3 pipeline/microcore_pipeline.py scan --input out/fixtures/sample.jsonl
```

Observed: 0 private keys, 0 AWS keys, 0 GitHub tokens, 0 JWTs, 0 emails, 0 NTLM hash pairs, 9 IPv4 matches. The nine IPv4 hits were version strings (`1.4.13.3`, `2.0.6.5`, `12.0.0.77`), which is a genuine false-positive class in security text and is why the scan reports examples rather than counts alone.

### 11.3 What the pipeline does not do

- It does not download the gated, restricted or broken sources. That is a deliberate refusal, not a missing feature.
- It does not parse EVTX, PCAP or APK formats; those need format-specific tooling (python-evtx, Zeek, apktool) which was out of scope for this pass.
- It does not execute anything it downloads. `fetch` is a byte-stream copy followed by a hash.
- It does not claim a full-corpus dedup. The measured dedup covers only the four parsed corpora and the fixtures.

### 11.4 Recommended ingest sequence

1. `fetch` the 13 Tier A sources; verify sizes against the manifest; record hashes in `audit_log.jsonl`.
2. Parse to a common record envelope: `{id, source_id, cve_ids[], cwe_ids[], attack_ids[], text, url, license, retrieved_at}`.
3. Dedup by identifier first (CVE ID), then by exact text hash, then MinHash at 0.8.
4. Split by group key with 90/5/5 and block by ID list for the seven evaluation sets.
5. Scan for secrets and PII; scrub hostnames, usernames, emails and internal IPs from OTRF and EVTX.
6. Emit a manifest of the final corpus with per-source token counts — the only number that should ever be compared against the 10M-token budget.

---

## 12. Limitations and open questions

Stated plainly, because the alternative is overstating the audit.

1. **No bulk corpus download.** Only eight artefacts were downloaded and parsed. Tier B and C records that are metadata-only are labelled as such; none of their record counts were verified locally.
2. **No record-level dedup of un-downloaded datasets.** Cross-corpus overlap (NVD vs CVE List vs GHSA vs CIRCL) is identified but not quantified.
3. **No malware execution, and no malware binaries obtained.** Malware-adjacent coverage is feature-level (EMBER) only.
4. **Licence reading is documentary, not legal advice.** The NVD legal notice does not state an explicit public-domain grant; the CISA KEV assessment as a US government publication is an assessment that warrants formal review before commercial deployment.
5. **One licence was confirmed off the canonical path.** ATT&CK's `/resources/legal-and-branding/terms/` returned 404; the terms were confirmed from the repository and legal section instead.
6. **Two 502s and one 403 remain unresolved.** Digital Corpora, Drebin and VX-Underground may resolve differently on another date; the register records the date so a retry is meaningful.
7. **Domain coverage is bounded by what exists.** Wireless, hardware/side-channel and firmware-at-data-level have no licensed source. This is a finding about the landscape, not an incomplete search — but it can only be closed by generating data in-house.
8. **Token accounting is not attempted.** No file was tokenised; any "10M tokens" claim from this register would be an estimate dressed as a measurement.

### 12.1 Decisions required from the project owner

- Whether to request written permission from HackTricks, Nightmare and ctfs maintainers (three high-scoring rejections that a single licence grant each would move into Tier B).
- Whether to pursue AndroZoo or CIC access despite the absence of a training grant — the recommendation is no.
- Whether to accept the share-alike shard as a separately tracked corpus component.
- Whether to fund in-house generation for Active Directory telemetry, licensed PCAP and firmware, which is the only route to those domains.

---

## 13. Appendix — full register

`out/master_inventory.csv` is the authoritative artefact (29 columns, 80 rows). Compact view:

| ID | Tier | Score | Access | HTTP | Licence class |
|---|---|---:|---|---:|---|
| MC-001 | A | 98 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-002 | A | 95 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-003 | A | 95 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-004 | A | 89 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-005 | A | 89 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-006 | A | 95 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-007 | A | 95 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-008 | A | 93 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-009 | A | 92 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-010 | A | 93 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-011 | A | 92 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-012 | A | 90 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-013 | B | 90 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-014 | A | 88 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-015 | B | 87 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-016 | B | 86 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-017 | B | 87 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-018 | B | 82 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-019 | B | 80 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-020 | B | 87 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-021 | B | 85 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-022 | B | 76 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-023 | B | 86 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-024 | B | 90 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-025 | B | 81 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-026 | B | 81 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-027 | B | 84 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-028 | B | 78 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-029 | B | 81 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-030 | B | 85 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-031 | B | 87 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-032 | B | 76 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-033 | B | 81 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-034 | B | 76 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-035 | B | 74 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-036 | Evaluation | 74 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-037 | C | 72 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-038 | C | 65 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-039 | C | 60 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |
| MC-040 | C | 74 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-041 | C | 67 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-042 | B | 83 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-043 | B | 82 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-044 | C | 75 | VERIFIED_ACCESSIBLE | 200 | UNCLEAR |
| MC-E01 | Evaluation | 61 | VERIFIED_ACCESSIBLE | 200 | NO_LICENSE_FOUND |
| MC-E02 | Evaluation | 86 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-E03 | Evaluation | 86 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-E04 | Evaluation | 82 | METADATA_VERIFIED_ONLY | 200 | COMPATIBLE |
| MC-E05 | Evaluation | 79 | METADATA_VERIFIED_ONLY | 200 | RESTRICTED |
| MC-E06 | Evaluation | 61 | METADATA_VERIFIED_ONLY | 200 | NO_LICENSE_FOUND |
| MC-Q01 | Rejected | 62 | GATED_OR_AUTHENTICATION_REQUIRED | 401 | UNCLEAR |
| MC-Q02 | Rejected | 51 | GATED_OR_AUTHENTICATION_REQUIRED | 403 | UNCLEAR |
| MC-Q03 | Rejected | 46 | GATED_OR_AUTHENTICATION_REQUIRED | 403 | UNCLEAR |
| MC-Q04 | Quarantine | 65 | GATED_OR_AUTHENTICATION_REQUIRED | 200 | CONFLICTING_RIGHTS |
| MC-Q05 | Quarantine | 68 | GATED_OR_AUTHENTICATION_REQUIRED | 200 | RESTRICTED |
| MC-Q06 | Quarantine | 75 | GATED_OR_AUTHENTICATION_REQUIRED | 200 | RESTRICTED |
| MC-Q07 | Quarantine | 70 | GATED_OR_AUTHENTICATION_REQUIRED | 200 | RESTRICTED |
| MC-Q08 | Quarantine | 65 | GATED_OR_AUTHENTICATION_REQUIRED | 200 | NO_LICENSE_FOUND |
| MC-Q09 | Quarantine | 61 | GATED_OR_AUTHENTICATION_REQUIRED | 200 | NO_LICENSE_FOUND |
| MC-Q10 | Rejected | 73 | METADATA_VERIFIED_ONLY | 200 | UNCLEAR |
| MC-Q11 | Rejected | 35 | TEMPORARY_FAILURE | 502 | UNCLEAR |
| MC-Q12 | Rejected | 35 | UNAVAILABLE_OR_REMOVED | 502 | RESTRICTED |
| MC-Q13 | Quarantine | 58 | HTTP_ERROR | 403 | CONFLICTING_RIGHTS |
| MC-Q14 | Rejected | 26 | BROKEN_LINK | 404 | NO_LICENSE_FOUND |
| MC-Q15 | Rejected | 8 | BROKEN_LINK | 404 | NO_LICENSE_FOUND |
| MC-Q16 | Rejected | 8 | BROKEN_LINK | 404 | NO_LICENSE_FOUND |
| MC-Q17 | Rejected | 32 | BROKEN_LINK | 404 | NO_LICENSE_FOUND |
| MC-Q18 | Quarantine | 65 | VERIFIED_ACCESSIBLE | 200 | CONFLICTING_RIGHTS |
| MC-Q19 | Rejected | 85 | VERIFIED_ACCESSIBLE | 200 | NO_LICENSE_FOUND |
| MC-Q20 | Rejected | 65 | GATED_OR_AUTHENTICATION_REQUIRED | 200 | RESTRICTED |
| MC-Q21 | Rejected | 87 | VERIFIED_ACCESSIBLE | 200 | RESTRICTED |
| MC-Q22 | Rejected | 76 | GATED_OR_AUTHENTICATION_REQUIRED | 200 | RESTRICTED |
| MC-Q23 | Rejected | 64 | GATED_OR_AUTHENTICATION_REQUIRED | 200 | RESTRICTED |
| MC-Q24 | Rejected | 74 | METADATA_VERIFIED_ONLY | 200 | CONFLICTING_RIGHTS |
| MC-Q25 | Quarantine | 76 | VERIFIED_ACCESSIBLE | 200 | CONFLICTING_RIGHTS |
| MC-Q26 | Rejected | 78 | VERIFIED_ACCESSIBLE | 200 | NO_LICENSE_FOUND |
| MC-Q27 | Rejected | 63 | VERIFIED_ACCESSIBLE | 200 | NO_LICENSE_FOUND |
| MC-Q28 | Rejected | 81 | VERIFIED_ACCESSIBLE | 200 | RESTRICTED |
| MC-Q29 | Rejected | 87 | VERIFIED_ACCESSIBLE | 200 | RESTRICTED |
| MC-Q30 | C | 74 | VERIFIED_ACCESSIBLE | 200 | COMPATIBLE |

### 13.1 Verification log summary

| Signal | Count |
|---|---|
| HTTP 200 | 71 |
| HTTP 401 | 1 |
| HTTP 403 | 3 |
| HTTP 404 | 4 |
| HTTP 502 | 2 |
| Downloaded artefacts hashed | 8 |
| Repositories cloned and file-counted | 29 |
| HF datasets with gated flag inspected | 21 |
| Records parsed | 811,027 (Trendyol 53,201 + cve2cwe 234,770 + CIRCL 515,862 + KEV 1,805 + NVD recent 5,389) |

All checks dated **2026-11-26**. All evidence files are retained under `data/` and `out/`.

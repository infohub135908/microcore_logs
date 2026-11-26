# MICROCORE Phase 2 — Executive Research Report

**Discovery, deep inspection, licensing audit and 5-billion-token feasibility assessment**

| | |
|---|---|
| Report date | 2026-11-27 |
| Register baseline | Phase 1 audit of 2026-11-26 |
| Sources screened in Phase 2 | ~315 platform records (Zenodo 180, Figshare 75, Dataverse 60, Kaggle 60 lookups) + 18 GitHub repositories + 10 Hugging Face gap queries |
| Sources newly verified at file level | 8 repositories (6 newly acquired, 2 re-measured) |
| New records added to register | 23 (MC-101 … MC-123) |
| Unified register size | 103 records, 35 required columns + licence class |
| Verified, training-eligible tokens | **101,738,163** (cl100k_base) / 142,236,999 (GPT-2 BPE) |
| Target | 5,000,000,000 |
| Verified coverage | **2.04 %** |
| Verified shortfall | **4,898,261,837 tokens** |

---

## 1. What was actually done

Phase 2 was run as an evidence-first exercise. Every number below comes from a file that was
downloaded, parsed and tokenised in this session, or from an API response that was recorded.
Nothing in this report is inferred from a landing page, a search snippet or a README claim
unless it is explicitly labelled as metadata-only.

The work proceeded in eight passes:

1. **Repository reconciliation** — fetched the committed MICROCORE GitHub repository and executed
   its committed pipeline to test the claims made in the Phase 1 audit.
2. **Platform discovery** — queried Zenodo, Figshare, Dataverse, Kaggle and Hugging Face with 23
   targeted queries covering the domains where Phase 1 had the thinnest coverage (PCAP, firmware,
   Active Directory, cloud audit logs, ICS/SCADA, memory forensics, Windows telemetry).
3. **Repository-level verification** — 18 GitHub repositories were inspected through the REST API
   (file counts, last commit, licence file), then cloned or tarballed for licence reading.
4. **Licence reading** — licence files were opened and the grant was read, not assumed from a
   repository badge.
5. **Acquisition** — five large corpora were downloaded and extracted (azure-docs, PowerShell-Docs,
   Kubernetes website, attack_data, Atomic Red Team) plus six small ones.
6. **Token measurement** — a two-tokeniser harness (`measure.py`, `measure_text.py`) measured every
   acquired corpus with `tiktoken cl100k_base` (tokenizer A) and GPT-2 BPE via Hugging Face
   `tokenizers` (tokenizer B).
7. **Deduplication measurement** — MinHash + LSH banding (64 permutations, 5-word shingles,
   threshold 0.8) was run over the whole English Kubernetes corpus to obtain a real, measured
   near-duplicate rate rather than an assertion.
8. **Pipeline rebuild and test** — a new pipeline (`pipeline/pipeline.py`) was written, with 12
   tests, run, and its actual output captured (`pipeline/out/test_results.txt`).

## 2. Repository reconciliation: what the committed artefacts actually contain

The Phase 1 audit report describes a repository containing a pipeline, a manifest, a master
inventory, audit logs, fixtures and a split file. That is not what is committed.

On 2026-11-27 the main branch of `infohub135908/microcore_logs` was downloaded as a zip archive
(48,786 bytes). It contains **three top-level files and nothing else**:

| Committed file | Size | Lines | What it is |
|---|---|---|---|
| `MICROCORE Collection Pipeline.py` | — | 250 | The pipeline script |
| `MICROCORE Dataset Audit Report.md` | — | 801 | The Phase 1 narrative report |
| `MICROCORE Master Dataset Inventory.csv` | — | 81 | 80 records + header |

There is no `pipeline/manifest.json`, no `data/`, no `out/`, no `out/audit_log.jsonl`, no
`out/fixtures/sample.jsonl`, no `out/fixtures/split.jsonl`. Consequently the audit report's
references to those artefacts **cannot be independently verified from the repository**, and this
report does not treat them as verified. The Phase 1 register itself (80 records) is verified
because the CSV is committed and was re-parsed here.

(The fourth file mentioned in the assignment brief, an unrelated DMN audit document, is not present
on the main branch and was not read, per instruction.)

### 2.1 Executing the committed pipeline

The committed pipeline was executed exactly as written from a clean checkout:

```
$ python3 "MICROCORE Collection Pipeline.py"
FileNotFoundError: [Errno 2] No such file or directory:
  '/home/user/workspace/p2/repo/pipeline/manifest.json'
```

Findings from reading all 250 lines afterwards:

| Check | Result | Evidence |
|---|---|---|
| Manifest/directory structure exists | **No** | `MANIFEST = ROOT/"pipeline"/"manifest.json"` is read at import time; the file is not committed |
| Paths work from committed location | **No** | `ROOT = Path("/home/user/workspace/microcore")` is hard-coded and escapes the repository |
| Licence gate, not just accessibility | **No** | `grep -n "licen"` returns only report strings; no branch refuses an unlicensed source |
| Hash mismatch causes rejection/quarantine | **No** | mismatch is written as a `"HASH_MISMATCH"` label into a per-file record and processing continues |
| Dedup scales beyond fixtures | **No** | `for i, a in enumerate(records): for b in records[i+1:]` — quadratic all-pairs |
| Leakage produces reproducible evidence | **No** | leakage is flagged in-memory and discarded; no exclusion list is persisted or applied |
| Scan followed by quarantine/redaction | **No** | findings are counted, the record still reaches the output file |
| Token counting | **No** | absent entirely |

Every one of these gaps is closed in the replacement pipeline (Deliverable 9), and each closure has
a passing test.

## 3. Discovery results

Discovery was deliberately narrow and deep rather than broad and shallow. The 23 queries returned
roughly 315 records; the useful yield was small, and that is a finding in itself: **the public
cyber-dataset ecosystem is dominated by small academic uploads, not by large licensed corpora.**

| Platform | Queries | Records returned | Deep-verified (licence + files + size via API) | Verdict |
|---|---|---|---|---|
| Zenodo | 14 | 180 | 9 | 9 viable, mostly small or binary |
| Dataverse (Harvard) | 4 | 60 | 5 | **5 with CC0** — best licensing outcome of the run |
| Kaggle | 3 + 8 metadata lookups | 60 | 8 | heavily gated, licences mixed (NC/AGPL/unknown) |
| Figshare | 5 | 75 | 0 | query semantics return keyword noise (pneumonia, 3D printers); no usable cyber corpus surfaced |
| Hugging Face | 10 gap queries | — | 0 | PCAP, firmware, CloudTrail, AD and Windows-event-log coverage is close to absent |
| GitHub (targeted) | 18 repositories | — | 18 | **the only source of large, cleanly licensed text corpora** |

### 3.1 Highest-value discoveries

**1. Splunk `attack_data` (MC-101, Apache-2.0, 3,852 files, 2.1 GB extracted).**
Real telemetry produced by executing Atomic Red Team tests and attack_range scenarios: Windows event
logs, Sysmon, PowerShell operational logs, Linux auditd, CloudTrail, Kubernetes audit, Zeek and
Suricata output, each file labelled with its ATT&CK technique and expected Splunk sourcetype. This
is the single most valuable practical DFIR source found in either phase. A 60-file stratified sample
(6,913,711 B) measured **2,391,735 cl100k tokens**, i.e. 0.346 tokens per byte — a very high density
because log lines are tokenised poorly but are numerous. Extrapolating that ratio to 2.1 GB would
imply ~727M tokens, but the sample is biased toward the first technique folders and duplicate
scenario content is unknown, so the figure is recorded as an estimate, not as verified volume.

**2. Atomic Red Team `atomics/` (MC-102, MIT, 739 YAML files, 60.6 MB).**
Measured **16,010,220 cl100k / 22,623,455 GPT-2 tokens**. ATT&CK-mapped test definitions with
executor commands, platform constraints and detection notes. Text-only, no binaries, permissive
licence: the cleanest large addition to the offensive-knowledge domain.

**3. Microsoft `azure-docs` (MC-103, CC BY 4.0, 15,480 Markdown files, 172.6 MB).**
Measured **38,636,210 cl100k / 50,486,791 GPT-2 tokens**. The largest single verified block of
training-eligible text in the whole corpus.

**4. Kubernetes website, English only (MC-105, CC BY 4.0, 2,532 files).**
Measured **5,894,026 cl100k**. The naive figure for the repository is 22,322,374 cl100k, but 6,467
of the 8,999 Markdown files are translations of the same pages into 16 other languages. Counting
them would have inflated the corpus by ~16.4M tokens of duplicated semantics. This is exactly the
mirror-duplication failure mode the specification warns about, caught by inspection rather than
assumption.

**5. Harvard Dataverse CC0 collections (MC-109 … MC-111).**
Five datasets are released under **CC0 1.0** — ADFA IDS (989.84 MB, 9 files), StreamSpot
(427.17 MB, 7 files), Cadets (406.74 MB, 2 files), a port-scan/Slowloris dataset (53.59 MB) and a
hypervisor-level memory-dump collection (194.7 GB, 1,554 files). CC0 removes the licensing question
entirely; what remains is a parsing and PII problem, because the content is tabular, graph or binary.

### 3.2 What was rejected, and why

- `swisskyrepo/InternalAllTheThings` (MC-120) — 185 files of excellent Active Directory material,
  **no licence file at all**. Public visibility is not a reuse grant. Quarantined.
- `mkerrisk/man-pages` — no root licence, last commit 2021-09-02. Not usable.
- `elastic/detection-rules` — Elastic Licence 2.0; training and redistribution restricted. Rejected.
- `Kitsune` (Kaggle) — AGPL-3.0 applied to a dataset; unresolved copyleft over data. Hold.
- `UNSW-NB15` mirrors — CC BY-NC-SA 4.0 plus they are mirrors of the same underlying data, not
  independent corpora. Counted once, evaluation-only.
- `CIC-IoMT`, CIC-IDS2017 PCAP — HTTP 403 and a signed-request gate; no licence text granting
  training rights. Gated, not accessible, not counted.
- Figshare discovery — returned no relevant cyber corpus across five queries; recorded as a failed
  search rather than silently dropped.

## 4. Token accounting

Two tokenisers, reported separately, because the choice of tokeniser changes the answer by 30–45 %
on this material (markup-heavy XML and YAML tokenise far worse under GPT-2 than under cl100k).

| Tokeniser | Training-eligible verified tokens | Share of 5B |
|---|---|---|
| A — `tiktoken cl100k_base` | 101,738,163 | 2.04 % |
| B — GPT-2 BPE | 142,236,999 | 2.84 % |

Sixteen distinct sources were measured at file level (a seventeenth row restates the Kubernetes corpus after dedup and is not added again). Two are excluded from the eligible total:
Sigma (Detection Rule Licence 1.1) and LOLBAS (GPL-3.0) are licence-restricted. OTRF was only partially
materialised (58 of 733 files) so its 51,796 tokens are recorded as partial and excluded entirely.

The full per-source table is in `08_corpus_token_yield_report.md` and `token_yield.csv`.

### 4.1 Deduplication, measured rather than assumed

Rather than assert that duplication was handled, the LSH implementation was run over the complete
English Kubernetes corpus:

| Metric | Value |
|---|---|
| Documents | 2,532 |
| Exact duplicates | 1 |
| Near-duplicates (Jaccard ≥ 0.8, MinHash 64 perms, 5-word shingles) | 120 |
| Tokens before | 5,894,026 |
| Tokens after | 5,459,909 |
| Reduction | **7.4 %** |
| Wall clock | 29 s |

This was a real run on real data, not a fixture. It is nevertheless a *sample-level* result: no
deduplication has been performed across the 103-source register as a whole, and this report does not
claim otherwise. The cross-source rate is unknown and is likely higher, because azure-docs `includes/`
fragments appear inside many articles, PowerShell cmdlet pages repeat across version trees, and
attack_data scenario folders reuse the same helper scripts.

### 4.2 The 5B verdict

**5,000,000,000 unique, high-quality, lawful tokens is not attainable from the public
cyber-security corpus as it exists today.** The verified total after this phase is 101.7M tokens from
16 measured sources, and the realistic ceiling from every remaining identified source — including
full NVD history, CVEfixes, Ghidra, ReactOS, OpenWrt and the full attack_data corpus — is in the
order of 1.2–1.6B tokens, much of it code rather than prose. The gap is structural, not a search
failure:

1. **The corpus is small.** Cyber-security is a small-text domain. NVD — the largest authoritative
   database in the field — yields 14.5M tokens for an entire year and about 100M for its full
   25-year history.
2. **The largest artefacts are binary.** PCAPs, memory images and malware samples dominate the byte
   counts (TII-SSRC-23 32.5 GB, Kitsune 64.2 GB, the Dataverse memory dumps 194.7 GB) and yield
   almost no natural-language tokens until they are decoded into text.
3. **The best material is unlicensed.** InternalAllTheThings, HackTricks, man-pages, CIC datasets
   and most Hugging Face cyber collections have no reuse grant.
4. **What is licensed and large is documentation and code**, not adversary tradecraft.

Reaching 5B therefore requires three things that this phase can specify but not deliver:
licensed source code at scale (~2B), decoded binary/telemetry corpora (~1B), and controlled
generation from labs (~2B). The roadmap in Deliverable 10 quantifies each.

## 5. Domain coverage after Phase 2

| Domain | Verified tokens | Status |
|---|---|---|
| Vulnerability research | 17.5M | strong |
| Detection engineering / ATT&CK | 15.8M | strong |
| Windows / PowerShell | 7.9M | good |
| Cloud / Kubernetes | 44.5M | good |
| Offensive tradecraft | 16.9M | good |
| Binary exploitation / RE | 0.5M | thin (how2heap, capa only) |
| Malware analysis | 0.26M | thin |
| DFIR / telemetry | 2.4M sampled | promising, unquantified |
| Firmware / embedded | 0 | **gap** |
| Active Directory | 0 | **gap** (best source unlicensed) |
| Networking / protocols | 0 | **gap** |
| Mobile | 0 | **gap** |
| ICS/SCADA | 0 | **gap** (data exists, PCAP-encoded) |
| Agentic tool-use | 0 | **gap** (must be generated) |

## 6. Answers to the five required questions

**1. Which new datasets were discovered?**
23 new records: 8 GitHub repositories with verified licences (attack_data, Atomic Red Team,
azure-docs, PowerShell-Docs, Kubernetes website, capa-rules, Ghidra, OpenWrt, ReactOS, LOLBAS,
SecLists, GTFOBins, man-pages, InternalAllTheThings, elastic detection-rules, awsdocs EC2), 5 Harvard
Dataverse CC0 datasets, 9 Zenodo uploads, 6 Kaggle datasets. Two Figshare and one CIRCL-family search
returned nothing usable and are recorded as failures.

**2. How many passed both the technical and legal gates?**
Of 23 new records: **11 passed both gates** (MC-101, MC-102, MC-103, MC-104, MC-105, MC-106, MC-108,
MC-118, plus three Dataverse CC0 items at metadata level: MC-109, MC-110, MC-111). Six are
conditional or hold-for-review (MC-107 LOLBAS GPL-3.0, MC-116 OpenWrt, MC-117 ReactOS, MC-112/113/114
Zenodo pending content inspection), and six failed outright (no licence, gated, or restricted).

**3. How many unique verified tokens do we have?**
**101,738,163 tokens (cl100k_base)** across 16 measured sources, after excluding licence-restricted
material and partial measurements. In GPT-2 BPE the same material is 142,236,999 tokens. Only 7.4 %
deduplication has been measured, and only on one corpus; the true post-dedup figure is lower and
unknown.

**4. How many tokens are still required?**
**4,898,261,837** (97.96 % of target) if measured against cl100k_base. Even under the most generous
credible assumptions about the remaining identified sources, roughly 3.4–3.8B tokens must come from
material that does not exist yet and has to be generated under controlled conditions.

**5. What are the best next steps?**
(a) Parse attack_data fully — highest measured density of practical DFIR text, already licensed.
(b) Fetch the complete NVD history and CVEfixes; both are cheap and together may add ~250M tokens.
(c) Clear the licence question on Ghidra, ReactOS and OpenWrt to unlock ~1B tokens of
binary-analysis and Windows-internals code.
(d) Build the lab-generation programme described in Deliverable 10 — it is not optional padding but
the only credible path to the remaining volume, and it must produce labelled, verifiable traces.

## 7. Integrity statement

- No dataset, URL, licence, size, record count or status code in this report was invented. Where a
  value was not verified it is labelled `not verified`, `not measured` or `metadata-only`.
- No gate, paywall, authentication barrier or terms acceptance was bypassed. CIC, Kaggle-gated and
  request-form datasets were recorded as gated and not acquired.
- No downloaded executable or malware sample was executed. attack_data and Zenodo malware archives
  are treated as quarantine-only material.
- Metadata-level verification is never reported as file-level inspection; the
  `FileInspectionLevel` column distinguishes L2/L3/L4/L5 per record.
- Deduplication has not been completed across the corpus, only measured on one 2,532-document
  corpus, and the report says so.
- Token counts are measured with two named tokenisers and are estimates with respect to the
  project's future production tokeniser.
- Failed searches and rejected candidates are preserved in the register and in Deliverable 5.
- The committed repository contains three files, not four, and none of the claimed evidence
  artefacts; that discrepancy is recorded rather than smoothed over.

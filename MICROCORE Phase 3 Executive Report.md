# MICROCORE Phase 3 — Strategic Feasibility Report

Audit date: 2026-11-26/27. Accounting tokenizer: `tiktoken cl100k_base`; secondary `GPT-2 BPE`.
All token figures in this report are measured on downloaded content unless the row is explicitly marked as an estimate.

## 1. Why the Phase 2 strategy was too narrow

Phase 2 searched for objects named like cybersecurity datasets and found 103 of them. That search was correct but structurally capped, for three reasons that are visible in the Phase 2 register itself:

1. **The named-dataset ecosystem is mostly small and documentation-shaped.** Excluding the five large items (azure-docs, Atomic Red Team, NVD 2024, ATT&CK, PowerShell docs), the median Phase 2 source contributed well under 1M tokens.
2. **The largest security artefacts are binary.** 194.7 GB of hypervisor memory dumps, 64.2 GB of PCAP, 1.1 GB of firmware traces and 32.5 GB of IoT traffic capture contribute exactly zero tokens until a parser turns them into text, and the parser output is far smaller and far more repetitive than the byte count suggests.
3. **The units were wrong.** A cybersecurity model has to reason about the systems it investigates. The source code of an HTTP server, the source of the TLS library it links, the kernel structures behind a syscall and the API documentation for the handles it touches are all training data for that reasoning, and none of them carry a security label.

Phase 2's own ceiling estimate (1.1–2.7B tokens) was a ceiling on *label-defined* security data. This phase re-measures the ceiling on *capability-defined* data. The conclusion changes materially, and the number that matters is measured, not asserted.

## 2. What the five-pillar strategy changes

| Pillar | Phase 2 treatment | Phase 3 treatment |
|---|---|---|
| A — pure security data | the whole search | retained, plus enrichment sources (advisories, nuclei templates, CISA) |
| B — open-source code | absent | **primary** — permissively licensed OS, compiler, runtime, network and tool source |
| C — systems documentation | incidental (vendor docs) | **primary** — vendor reference docs, standards, textbooks, course material |
| D — telemetry and binary-derived text | listed as unavailable | measured, and found to be far smaller than its byte count implies |
| E — controlled labs | proposed | **executed** on a real host, with a schema and measured tokens per trajectory |

The strategic inversion is this: stop asking which datasets are about security, and start asking which large, licence-filtered corpora contain the material a security practitioner must read. Then measure.

## 3. What was measured in this phase

| Category | Verified cl100k |
|---|---|
| Existing Phase 2 baseline | 101,738,163 |
| Newly acquired cybersecurity data (nuclei, payloads, Vulnrichment) | 45,002,874 |
| New source-code corpora | 1,021,540,498 |
| Technical foundations (documentation) | 127,088,180 |
| Parsed telemetry and forensics | 0 (measured 84,852,864 raw, 99.94% redundant) |
| Controlled lab traces | 2,612 |
| Cross-source deduplication removed | 0 (not performed) |
| **Final verified corpus** | **1,295,372,327** |
| Remaining to 5B | 3,704,627,673 |

Four results dominate.

**Two compiler and runtime trees dominate: LLVM and FreeBSD.** `llvm/llvm-project` yielded 375,526,610 cl100k tokens from 1,066 MB across 107,768 eligible files of 192,617 seen; `freebsd/freebsd-src` yielded 292,318,188 from 913 MB across 76,125 files. FreeBSD is BSD-2-Clause at the repository level, and 6,728 files carrying a GPL or otherwise incompatible SPDX header were excluded by the file-level filter rather than inheriting the repository licence. LLVM is Apache-2.0 with the LLVM exception. Neither is a security dataset; both are the material a security engineer is expected to have read. `dotnet/runtime` was third at 119,312,899.

**Microsoft's reference documentation is a five-repository, 127,088,180 token block of directly relevant systems text.** The Win32 API repository alone (`MicrosoftDocs/win32`, 57,098,595) documents handles, security descriptors, ACLs, services, registry and process internals — the exact objects a Windows investigation manipulates. Phase 2 had measured only azure-docs and PowerShell docs from this family, so this is a genuinely new block, not a re-count.

**Telemetry conversion, measured properly, does not deliver the tokens its byte count promises.** Converting 3,000,003 NGIDS-DS host rows into `key=value` text produced 84,852,864 tokens on a two-file sample; but the corpus contains only 1,218 distinct (process, syscall, category, label) tuples across 2,000,002 rows — a unique ratio of 0.061 %. Aggregating to per-process syscall sessions and exact-deduplicating collapsed 3,000,003 rows to 462 unique sessions and 253,279 tokens on three files. Row-level telemetry conversion is duplicate padding; session-level aggregation is the only defensible form. This is why the 0.7B telemetry bucket in the Phase 2 architecture is not achievable as written.

**A 1.4 GB CVE archive is 1.4 GB of schema, not of knowledge.** `cisagov/vulnrichment` (CC0, verified) streamed to 385,561,606 raw cl100k tokens over 228,246 files and 1,445.9 MB. Reparsing and keeping only content-bearing fields — descriptions, reference URLs, CPE criteria, version ranges, CVSS vectors, vendor and product names — cut that to 154,447,747. A 6,000-record sample then showed that only 21.09 % of 12-token sequences are novel, and that 42.4 % of content tokens are reference URLs, so 32,573,030 tokens are counted. The ratio between the number a directory listing suggests and the number that is actually trainable is about twelve to one.

## 4. The largest newly discovered opportunities

| Opportunity | Evidence | Status | Realistic eligible tokens |
|---|---|---|---|
| Permissive OS and systems source (FreeBSD, LLVM, Rust, Go, PostgreSQL, OpenSSL, Kubernetes, Moby, .NET runtime, Node, nginx, curl, httpd, OpenSSH) | measured this phase | acquired | 1,021,540,498 |
| Microsoft Learn reference documentation (5 repositories) | measured this phase | acquired | 127,088,180 |
| Security content with explicit permissive licences (nuclei templates, PayloadsAllTheThings, GitHub Advisory Database, CISA Vulnrichment) | measured this phase | acquired | 45,002,874 |
| **The Stack v2** — 67.53 TB uncompressed, 3.28 B files, 658 languages, per-file `detected_licenses` from ScanCode and a `permissive` / `no_license` flag | dataset card, verified 2026-11-26 | gated: bulk content requires a Software Heritage + INRIA agreement | order 1–3 B within the permissive subset; **not counted** |
| **Software Heritage archive** — 29 B unique files, 441 M projects, content-addressed | archive statistics, 2026 | API-open, bulk graph gated | provenance layer, not a blanket corpus |
| Debian source archive with DEP-5 `debian/copyright` per package | licence metadata verified | accessible, unparsed | 0.2–0.6 B after GPL exclusion |
| NIST SP 800 / FIPS corpus | public domain in the US, foreign rights reserved | accessible, not yet parsed | 20–60 M |
| arXiv cs.CR / cs.SE / cs.NI subset (CC-BY/CC0 only) | per-article licence | accessible, licence filter needed | 30–90 M |

The Stack v2 is the only identified object that can supply billions of tokens on its own. That is not a claim that MICROCORE has them; it is a statement about where the volume physically is, and about the single legal step (a signed agreement) that stands between the project and it.

## 5. Constraints that did not move

* **Copyleft remains excluded.** The Linux kernel, systemd, git, GPL tooling and YARA rule sets are accessible and technically excellent, and they are held in the restricted register. Their combined eligible contribution is zero until counsel resolves the derived-corpus question. FreeBSD exists precisely because a permissive OS kernel is available; that is why it was chosen over Linux for measurement.
* **Gated corpora are not counted.** The Stack v2, the Software Heritage bulk graph and the Kaggle TII-SSRC-23 set stay at `GATED_OR_AUTHENTICATION_REQUIRED` with zero tokens.
* **Binary volume is not token volume.** 194.7 GB of memory images is an evidence archive, not a text corpus. Only parsed, deduplicated, semantically meaningful records count, and the measurement above shows how small that is for row-level telemetry.
* **Documentation is not free of rights.** CC-BY-NC-SA courseware (MIT OCW) and CC-BY-SA wikis are excluded from the eligible total for the same reason GPL code is: the share-alike or non-commercial term attaches to the derived corpus.

## 6. A credible route to 5B

The route has four stages, in descending order of certainty.

1. **Finish the measurable public permissive surface (now → 1,021,540,498 → ~1.1–1.3 B).** Complete the code batch, add the remaining permissive ecosystems (TensorFlow, VS Code, Home Assistant, PyTorch, Godot, Django, Apache, CNCF), parse Debian with DEP-5 filtering, and extract NIST and the CC-BY arXiv subset. This is ordinary engineering with no legal unknown. It reaches roughly a quarter of the target.
2. **Obtain the Software Heritage / INRIA agreement and build a permissively filtered Stack v2 subset (→ 5 B and beyond).** This is the only step that changes the order of magnitude. The filtering machinery already exists in the dataset (per-file SPDX, `permissive` flag, opt-out list) and the pipeline in this phase already implements the file-level gate it would need. The work is contractual and then mechanical: select permissive files, exclude `no_license`, exclude opt-outs, cap per repository and per publisher, deduplicate against the measured corpus.
3. **Generate verified lab trajectories (0.5–1.5 B over time).** Measured at 522 cl100k tokens per shallow trajectory; deeper multi-step labs run to several thousand. This is the only pillar that produces the agentic behaviour the model actually needs, and it is rate-limited by execution, not by rights.
4. **Do not use the remainder as an excuse to pad.** If stages 1–3 land short, the correct output is a documented shortfall, not synthetic filler.

## 7. Honest statement of the current position

Measured, deduplicated only within single corpora, legally gated: **1,295,372,327 cl100k tokens (25.91 % of 5 B)**. Shortfall: **3,704,627,673**.

That number is roughly five times the Phase 2 baseline and it was produced in one phase by changing what counted as data. It is still nowhere near 5 B, and no amount of further searching of the named-dataset ecosystem will close the gap. The gap closes at the Stack v2 agreement, or it does not close at all.

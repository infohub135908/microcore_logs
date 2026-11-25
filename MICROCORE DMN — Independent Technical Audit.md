# MICROCORE Dual-Memory Network — Independent Deep Research & Technical Validation

**Audit date:** 25 November 2026
**Object of audit:** proposed "MICROCORE Dual-Memory Network (DMN)" vs. the stated 12-layer / d=732 Transformer baseline
**Scope:** mathematical validity, parameter accounting, compute/hardware feasibility, novelty, capability expectations, experimental design
**Stance:** adversarial. This audit was instructed to try to disprove the proposal, not defend it.

---

## Provenance and evidence standard

Three things were done independently and are reported as such:

1. **Primary-source reading.** *Muir* (arXiv:2611.08376v1), *Gated DeltaNet-2* (arXiv:2605.22791), and *A Controlled Study of Attention-Only Transformers* (arXiv:2607.18363) were retrieved and read in full (equations, configuration tables, result tables, limitations). Numbers attributed to them below come from those papers.
2. **Executed code.** A parameter and compute ledger was written from first principles, **validated against the published Muir and GDN-2 configurations**, then run. All parameter counts in Part 4 are program output, not estimates. The scripts are attached (`audit_v2.py`, `compute_audit.py`).
3. **No GPU measurements were made.** Every throughput or VRAM figure below is either quoted from a paper (and labelled with that paper's hardware) or is an analytical estimate explicitly marked as such. Nothing here was benchmarked on a T4.

Claims sourced only from abstracts, blog posts, or secondary summaries are marked **[secondary]**. Claims that could not be verified are marked **[unverified]** and are not used to support any conclusion.

---

# Part 1 — Executive Verdict

| Question | Answer |
|---|---|
| **Is the proposed DMN mathematically valid?** | **No, not as written.** The printed update contains no value term. Taken literally it is a pure erasure operator that cannot store information and outputs zero from a zero initial state. The dimensions are consistent; the *content* is missing. It also omits decay, normalization, and the read-before-write ordering that the published rules require. It is repairable — the correct form is the Gated Delta Rule-2 — but then it is no longer the proposal, it is GDN-2. |
| **Is it architecturally coherent?** | **Partly.** Each piece is individually standard. But the dual-memory split is not a mechanism: with additive fusion it is algebraically identical to a single wider memory with a block-diagonal erase matrix (proof in §3.6). So the architecture is a constrained reparameterization of a single-memory model, plus extra projections, at 2× the state cost. |
| **Is it feasible at 150M parameters?** | **Yes, but it does not fit as specified.** At 150M with cl100k (100,256-token vocabulary) the embedding matrix alone is 34–49% of the budget. Dual memory consumes a further 27–31%, which is worth roughly 880 FFN channels — a ≈28% FFN cut, or about 5 layers of depth. The "preserved wide FFN" requirement and the dual-memory requirement are in direct conflict at this parameter count. |
| **Is it suitable for a 3B-token budget?** | **Not demonstrably.** 3B tokens is 20 tokens/parameter — Chinchilla-optimal, i.e. the *minimum* defensible. Recurrent-state architectures have no published evidence at 150M/3B; all supporting results are at 100B tokens (33× more data). There is no evidence that the fast/slow distinction can be *learned* from 3B tokens rather than merely initialized. |
| **Is it likely to beat the baseline?** | **Unlikely at this operating point.** Two independent reasons: (a) at sequence length 2,048 the quadratic attention term is only ~29% of block FLOPs, so the efficiency motive for recurrence is nearly absent — a hybrid saves ~32% of training FLOPs analytically but far less in wall-clock; (b) the only measured throughput data (Muir, 8×TPU7x) shows recurrent models running at **0.34×–0.45×** the throughput of a Transformer with Splash Attention at 2K–4K sequence length, i.e. exactly MICROCORE's regime. |
| **Is it novel enough to be called a new architecture?** | **No.** Every component is published: gated delta rule, channel-wise decay (KDA), decoupled erase/write (GDN-2), fused low-rank gating + matched-filter readout + FFN reinvestment (Muir), hybrid interleaving (Jamba/Samba/Qwen3-Next/Kimi Linear), multi-timescale memory via per-channel decay (KDA, Muir, MS-GLA), and fast/slow state pairs (LPC-SM, Titans). The specific combination is, by the §3.6 proof, a reparameterization rather than a new mechanism. |
| **Should MICROCORE proceed with it?** | **No — not as specified, and not as the primary architecture.** The dual-memory concept should be dropped to at most a single ablation arm. A repaired dense Transformer should be the primary, with one single-memory 3:1 hybrid arm as the challenger. |

**One-line verdict:** the proposal is a plausible-sounding restatement of published gated-linear-attention work, with a broken central equation and a memory split that is provably redundant, applied at a scale and sequence length where its only real advantage (sub-quadratic sequence scaling) cannot materialize.

---

# Part 2 — Literature Review

## 2.1 The three named papers — verified

All three arXiv identifiers are **real and current**. Titles, authors, and dates verified against arXiv listings:

| Paper | Authors | Date | ID | Code |
|---|---|---|---|---|
| *Muir: Linear Attention with Sensitivity-Allocated Gating and Matched-Filter Readout* | Tushaar Gangavarapu, Gil Tabak, Clemens J.S. Schaefer (UT Austin / Google) | 5 Nov 2026 | arXiv:2611.08376 | not located |
| *Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention* | Ali Hatamizadeh, Yejin Choi, Jan Kautz (NVIDIA) | 21 May 2026 | arXiv:2605.22791 | [NVlabs/GatedDeltaNet-2](https://github.com/nvlabs/gateddeltanet-2) |
| *A Controlled Study of Attention-Only Transformers* | Henry Ndubuaku, Karen Mosoyan, Jakub Mroz, Noah Cylich, et al. | 20 Jul 2026 | arXiv:2607.18363 | [Cactus-Compute (Needle 2)](https://huggingface.co/Cactus-Compute/needle2) |

Sources: [arXiv listing for 2611.08376](https://arxiv.org/abs/2611.08376), [arXiv HTML for 2605.22791](https://arxiv.org/html/2605.22791), [arXiv HTML for 2607.18363](https://arxiv.org/html/2607.18363).

## 2.2 Comparative table

| Architecture | Mechanism | Scale / tokens / data | Headline result | Relevance to MICROCORE |
|---|---|---|---|---|
| **Transformer** (baseline) | softmax attention + FFN | 166M–1.34B / 100B FineWeb-Edu (as run in Muir & GDN-2) | reference | the real competitor |
| **Gated DeltaNet-2** | $S_t=(I-k_t(b_t\odot k_t)^\top)D_tS_{t-1}+k_t(w_t\odot v_t)^\top$; channel-wise decay, channel-wise erase ($d_k$) + write ($d_v$) gates; chunkwise WY, C=64, fp32 state | 1.3B / 100B FineWeb-Edu / 4K seq / H100 | recurrent-only: Wiki ppl 15.90 vs Transformer 19.22; real-world retrieval **29.88 vs 38.07** (Transformer wins); hybrid: 15.62 ppl, 42.28 retrieval | the correct form of the proposal's update; its own data shows recurrent-only loses retrieval |
| **Muir** | GDN-2 update + matched-filter **readout gain** $\gamma_t$ on the query; all five gates fused into one rank-512 low-rank projection; saved params reinvested in FFN (+30.4% width) | 166M–1.34B / 100B FineWeb-Edu / 4K seq / 8×TPU7x | NLL −36.2 millinats vs Transformer, −20.4 vs GDN-2 at 1.34B; passkey 1M = 90% (static γ); **real-world extraction 34.60 vs Transformer 45.92** | closest prior art; the proposal is essentially Muir minus the readout gain plus a redundant second state |
| **Attention-only (SAN)** | FFN deleted; freed budget → more attention depth; QK-norm; GQA | **6M–87M** / 68B SYNTH, up to 105B / 8×H100 | iso-depth −0.47 nats, iso-FLOP −0.26, **iso-param only −0.006 nats**; on FineWeb-Edu iso-param gap **0.0398 nats** favouring FFN; deficit is *parametric recall only* | the only paper at MICROCORE's scale; justifies keeping an FFN, but at far lower width than assumed |
| **Qwen3-Next / Kimi Linear** | Gated DeltaNet (KDA) + full attention at **3:1** | 48–80B total / 3B active | production long-context | establishes 3:1 as the practical ratio |
| **Jamba** | Mamba + attention, 7:1, MoE | 52B/12B active, 250B tokens | **1:3 and 1:7 are "virtually no difference"** in performance | ratio is not the sensitive knob |
| **LPC-SM** | fast state every token + slow state at chunk boundaries, learned write gates | small-scale | dual-timescale state | **prior art for the exact fast/slow idea** |
| **Titans** | neural long-term memory updated by surprise-gradient at test time + short-term attention | various | test-time memorization | different mechanism; shows the space is crowded |
| **Wang (2026)**, *Recurrent Amplification and Exact Nonexpansiveness Criteria* | stability theory for rank-one erasure with channel-wise decay | theory | one-step spectral radius <1 does **not** bound the period product; 0.9994 → 1.3977 over 4,096 tokens in a Qwen3.5-0.8B head | required reading before trusting any gate bound |
| **"Some Attention is All You Need for Retrieval"** | ablation of attention vs SSM layers in RecurrentGemma, Jamba | 1.6B–9B | ablating attention → **0% retrieval**; SSM layers show no compensation | retrieval capability is localised in the attention layers |
| RetNet / RWKV / Mamba-2 / Hymba / MS-GLA / GLA / DeltaNet | see citations | — | — | listed for completeness; **[secondary]** — not independently verified here |

Sources: [Muir PDF](https://arxiv.org/pdf/2611.08376), [GDN-2](https://arxiv.org/html/2605.22791), [SAN](https://arxiv.org/html/2607.18363), [Jamba](https://ar5iv.labs.arxiv.org/html/2403.19887), [Qwen3-Next/Kimi Linear ratios](https://www.edgepedia.org/hybrid-attention-ssm-architectures), [LPC-SM](https://arxiv.org/pdf/2604.03263v1), [Titans](https://arxiv.org/abs/2501.00663), [Wang 2026](https://arxiv.org/abs/2611.27109), [retrieval ablation](https://ar5iv.labs.arxiv.org/html/2510.19861).

## 2.3 Critical reading of the two key papers

Reading the papers rather than the summaries changes the picture in three ways.

**(a) The baselines look under-tuned, so the claimed margins are upper bounds.** In Muir's Table 1, the 1.34B Transformer reaches WikiText perplexity 17.17 and FineWeb-Edu NLL 2.0335 after 100B tokens. A 1.34B Transformer at 100B tokens of FineWeb-Edu is normally well below that. More tellingly, Muir reports RULER variable-tracking at 1K context of **8.8% for the 1.34B Transformer** versus 60.0% for Muir. Transformer variable tracking at 1K is normally far above 8.8%; a number that low is much more consistent with an evaluation-format or configuration problem in the baseline arm than with a genuine architectural deficit. The same caution applies to GDN-2's 19.22 WikiText ppl for its Transformer arm.

This does not prove the recurrent architectures are worse than reported — but it does mean **none of the reported margins can be transferred to MICROCORE as expected effect sizes.** Any MICROCORE experiment must tune the Transformer arm at least as carefully as the recurrent arms, or it will reproduce a foregone conclusion.

**(b) The real-world retrieval result consistently favours attention.** This is the single most decision-relevant number in the literature for MICROCORE, because MICROCORE's stated capabilities — exact identifiers, filenames, error messages, tool outputs, retrieved documentation — are *extraction* tasks.

| 6-task real-world extraction average (1.34B, 2K cut) | Source |
|---|---|
| Transformer **45.92** | Muir Table 6 |
| Muir 34.60 / GDN-2 32.08 | Muir Table 6 |
| Transformer **38.07** / GDN-2 recurrent-only 29.88 / GDN-2 hybrid **42.28** | GDN-2 Table 4 |

The pattern is unambiguous and consistent across both papers: **recurrent-only loses ~7–11 points; hybrid recovers and can exceed the Transformer baseline.** That is an argument for *hybrid*, and an argument against any layer mix that reduces the attention share below what the hybrid arms used (they used 2K sliding-window attention in a subset of layers).

**(c) Muir's "wide FFN" is a parameter-budget trick, not an architectural claim.** Muir's own framing is that dense gate matrices cost $2d^2$ per layer and low-rank fused gates cost $1024d$; the saving is 77.8% of the gate projection, which is worth +30.4% FFN width at iso-parameters. That is exactly the accounting MICROCORE should do — but it is an argument for *cheap gates*, not for *two memories*.

## 2.4 What the attention-only study actually says

*A Controlled Study of Attention-Only Transformers* is the only paper in this set that operates at MICROCORE's parameter scale (6M–87M), and its result is more nuanced than either side of the FFN debate would like:

- Deleting the FFN **in place** costs 0.47 nats (iso-depth).
- Matching **training FLOPs** still costs 0.26 nats.
- Matching **parameters** and reallocating into depth costs **0.006 nats** — essentially nothing, reproducible across seed pairs.
- But on **FineWeb-Edu**, the iso-parameter gap is **0.0398 nats in favour of the FFN**, and the residual deficit is localised to *parametric recall* — positions where the model must supply knowledge from weights rather than from context.

For MICROCORE this is a clean, direct answer to §3.6 of the brief: **keep the FFN** (MICROCORE trains on FineWeb-Edu and needs CS knowledge in weights), but there is no evidence that the FFN must be *wide* — the evidence says FFN capacity substitutes for depth at roughly 1:1 in parameters at this scale. A model with an FFN and fewer layers is not obviously better than a deeper FFN-free one; a model with a *narrow* FFN and lots of memory machinery is the worst of both.

---

# Part 3 — Mathematical Audit

## 3.1 Dimensional check of the proposed update

Adopting the stated convention $S_t\in\mathbb{R}^{d_k\times d_v}$, $k_t,q_t\in\mathbb{R}^{d_k}$, $v_t\in\mathbb{R}^{d_v}$:

| Object | Required shape | Proposed | Verdict |
|---|---|---|---|
| state | $d_k\times d_v$ | same | consistent |
| read $(S_{t-1}^\top k_t)^\top$ | $1\times d_v$ (row) | same | consistent, but the double transpose is redundant: $S^\top k_t$ is already a $d_v$-vector |
| outer product $k_t(\cdot)^\top$ | $d_k\times d_v$ | $k_t\big((S^\top k_t)^\top\big)$ | **dimensionally legal, semantically empty** |
| decay $\lambda_t$ | scalar or $\mathbb{R}^{d_k}$ | multiplied outside | ambiguous placement |
| write strength $\beta_t$ | scalar or gate | multiplied outside | ambiguous |

So the tensors close. The problem is not shape — it is that the equation is missing its content.

## 3.2 The central equation is degenerate as written

As printed, the update is

\[
S_t=\lambda_t S_{t-1}-\beta_t\,k_t\big(S_{t-1}^{\top}k_t\big)^{\!\top}
=\Big(\lambda_t I-\beta_t k_tk_t^{\top}\Big)S_{t-1}.
\]

There is **no $v_t$ anywhere**. Consequences, both immediate:

1. **Output is identically zero from a zero start.** With $S_0=0$, every $S_t=0$, hence the readout $(S_t)^\top q_t = 0$ for all $t$. A model built on this equation cannot emit anything.
2. **It is a linear operator with no input injection.** $S_t$ is a linear function of $S_0$ only. Whether or not one initialises $S_0\neq0$ (and the brief leaves that undefined), the layer cannot bind a key to a value: it can only *erase* projections of whatever it started with.

This is not a notation slip that a reader can silently repair — "read the prediction and subtract it" is half of the delta rule, and the half that carries the information is the write term. **The proposal's only stated mathematical content is non-functional.** Every claim in §3.3 of the brief ("retention and write behaviour should be learned") is therefore unverifiable against the equations as given.

Note also the missing decay in the correct place. In the published rules, decay multiplies the *state* before the erase read ($\bar S_t = D_t S_{t-1}$, $r_t=\bar S_t^\top e_t$), so that the read is taken from the decayed, pre-write state. Multiplying $\lambda$ outside the whole bracket, as sketched, would decay the freshly written value immediately.

## 3.3 The corrected rule (and whose it is)

The minimal correct form, with the write restored and the ordering fixed, is

\[
\bar S_t = D_t S_{t-1},\qquad
r_t = \bar S_t^{\top} e_t,\qquad
S_t = \bar S_t + k_t\big(z_t-r_t\big)^{\top},
\]
\[
D_t=\operatorname{Diag}(\alpha_t),\quad
e_t=b_t\odot k_t,\quad
z_t=w_t\odot v_t,\quad
o_t=S_t^{\top}q_t ,
\]

equivalently

\[
\boxed{\;S_t=\big(I-k_t\,(b_t\odot k_t)^{\top}\big)D_tS_{t-1}+k_t\,(w_t\odot v_t)^{\top}\;}
\]

with $\alpha_t=\exp(g_t)$, $g_t=-\exp(a)\odot\operatorname{softplus}(W_fx_t+\delta)$, $b_t\in(0,2)^{d_k}$, $w_t\in(0,1)^{d_v}$. This is **Gated Delta Rule-2** verbatim ([GDN-2](https://arxiv.org/html/2605.22791)). Setting $b_t=\beta_t\mathbf 1$ and $w_t=\beta_t\mathbf 1$ reduces it to KDA; further collapsing $\alpha_t$ to a scalar gives Gated DeltaNet.

**Two things follow.** First, the proposal, once repaired, *is* a published rule; the "candidate recurrent update" is not a starting point for novel derivation, it is a two-year-old line of work with three named variants. Second, because the read $o_t=S_t^\top q_t$ uses the post-write state, the current token's own write is visible at position $t$. This is correct and not a leak: $v_t$ is a function of $x_t$ only, and $t$'s output must be allowed to depend on $t$'s input. It does mean the "read before or after write" question in the brief has a determined answer — after, for retrieval; from the decayed pre-write state, for the erase correction.

## 3.4 Normalization is mandatory, not optional

Let $\lVert k_t\rVert_2=1$. The erase factor $I-\beta kk^\top$ has eigenvalues $\{1-\beta,\,1,\dots,1\}$, so it is non-expansive iff $\beta\in[0,2]$ (matching the paper's $b_t\in(0,2)^{d_k}$ range). Now drop the normalization. The effective write strength becomes $\beta_{\text{eff}}=\beta\lVert k_t\rVert_2^2$, and at initialisation with $k\sim\mathcal{N}(0,1/d_k)$ *un-normalized* one has $\lVert k\rVert_2^2\approx d_k$. With $d_k=128$ and a nominal $\beta=0.5$ this gives $\beta_{\text{eff}}\approx 64$, hence $\lvert 1-\beta_{\text{eff}}\rvert\approx 63$: the state multiplies by ~63 per token along that direction and overflows within two or three steps. **L2 normalization of $q$ and $k$ per head is a correctness requirement of this recurrence, and the brief does not specify it.** Both reference implementations do it.

## 3.5 One-step contraction does not imply stability

It is tempting to conclude from §3.4 that bounded gates suffice. They do not. Wang ([arXiv:2611.27109](https://arxiv.org/abs/2611.27109)) constructs a periodic token sequence for which **every one-step spectral radius is below 1 while the spectral radius of the period product exceeds 1**, and demonstrates the effect in a real checkpoint: a selected Qwen3.5-0.8B head's terminal gain over a 4,096-token repeated-text sequence rises from 0.99938 to 1.3977 with gates held fixed. The reason is that the product of non-normal, non-commuting erase operators is not controlled by its factors' spectra.

Practical consequence for MICROCORE: gate-range checks are necessary but not sufficient. Every recurrent arm must log the **state Frobenius norm per layer per step** and the worst-case windowed gain; a run that survives the first 100M tokens can still blow up at 2B. This is a concrete, cheap safeguard with a published justification, and it is missing from the brief.

## 3.6 Why "fast memory + slow memory" is not a mechanism

This is the decisive technical finding of the audit.

Let the fast branch have state $S^{(f)}\in\mathbb{R}^{d_k^f\times d_v}$ and the slow branch $S^{(s)}\in\mathbb{R}^{d_k^s\times d_v}$, each following the §3.3 rule with its own key $k^{(f)}_t,k^{(s)}_t$, its own decay $D^{(f)}_t,D^{(s)}_t$, its own gates. Suppose fusion is additive (the only fusion that costs no parameters):

\[
o_t=\big(S_t^{(f)}\big)^{\top}q_t^{(f)}+\big(S_t^{(s)}\big)^{\top}q_t^{(s)} .
\]

Define the stacked quantities

\[
S'_t=\begin{bmatrix}S^{(f)}_t\\[2pt]S^{(s)}_t\end{bmatrix}\in\mathbb{R}^{(d_k^f+d_k^s)\times d_v},\quad
k'_t=\begin{bmatrix}k^{(f)}_t\\k^{(s)}_t\end{bmatrix},\quad
q'_t=\begin{bmatrix}q^{(f)}_t\\q^{(s)}_t\end{bmatrix},\quad
D'_t=\operatorname{blkdiag}\big(D^{(f)}_t,D^{(s)}_t\big).
\]

Then $o_t=(S'_t)^\top q'_t$ **exactly**, and the two-branch recurrence is the one-branch recurrence with

\[
S'_t=\big(I-k'_t(e'_t)^\top\big)D'_tS'_{t-1}+k'_t(z'_t)^\top ,
\]

provided the erase direction is block-structured, $e'_t=[\,b^{(f)}_t\odot k^{(f)}_t;\; b^{(s)}_t\odot k^{(s)}_t\,]$.

**Therefore:** a dual-memory layer with additive fusion is *the same function class* as a single memory of key dimension $d_k^f+d_k^s$ whose erase matrix is constrained to be block-diagonal. It is not a new mechanism; it is a single memory with a restriction. And since a single memory of that width with a *full* (unrestricted) erase matrix costs the same and is strictly more expressive, **dual memory is dominated by a single memory of equal total width.**

The other fusion options do not rescue distinctness, because they are all linear recombinations of the same two reads:

- concatenation + projection: $W_o[\,\cdot\,;\cdot\,]$ — a linear map of $(S^{(f)\top}q^{(f)},\,S^{(s)\top}q^{(s)})$, i.e. a different readout of the same information, at $2d^2$ parameters per layer;
- input-dependent gating: $\sigma(g_t)\odot o^{(f)}+(1-\sigma(g_t))\odot o^{(s)}$ — an input-dependent recombination of the same information, at $d^2$ parameters per layer;
- separate output projections with residual combination: a special case of the above.

**No fusion scheme creates information the two states do not already jointly hold, and the joint content is exactly what one state of double width holds.** The dual decomposition buys: 2× recurrent state memory, 2× branch projections, plus a fusion matrix — in exchange for a block-diagonal constraint.

What the proposal is *actually* trying to achieve — protecting long-lived content from being overwritten by high-rate content — is a real problem, but it has a cheaper published solution. Muir characterises it as row-energy "glare": slow-decaying rows accumulate norm, and unweighted query readout lets them dominate (reported raw row-energy p90/p10 spread up to **100×** within a head). Muir's fix is a **readout gain** $\gamma_t$ on the query (rank-128, i.e. $128d$ parameters per layer) plus a static matched filter $\gamma_{\text{stat},j}\propto g_H(\lambda_j)/m_j^*$. That is one gate, not a second state, and it is 8× cheaper than a concatenation projection at $d=512$ ($128\times512=65{,}536$ vs. $2\times512^2=524{,}288$).

**The quantitative version:** at $d=512$, $L=16$, matched parameters, cl100k:

| Variant | memory+gating params | FFN width | FFN share |
|---|---|---|---|
| single memory, fused gates (candidate B) | 25.3M | 3,008 | 49.1% |
| dual memory, fused gates (candidate C) | 59.0M | 1,600 | 26.3% |
| dual + attention every 3rd (proposed D) | 40.6M | 2,240 | 36.6% |
| single memory + attention 3:1 (candidate F) | 19.0M | 3,136 | 51.4% |

The second memory costs **21.6M parameters** — 14.4% of the whole model, worth **880 FFN channels**, i.e. a 28% FFN reduction. The brief's requirement to "preserve a substantial wide FFN" and its requirement for two memories are arithmetically incompatible at 150M with a 100k vocabulary. One of them has to go; the evidence says the FFN should stay.

## 3.7 What $\lambda$ and $\beta$ should be

The brief leaves this open; the literature has settled it empirically.

- **Decay $\alpha$: per-channel, $d_k$-dimensional.** Scalar decay gives one memory horizon. Per-head gives $H$ horizons. Per-channel gives $H\cdot d_k$ horizons — at $d_k=128$ and 8 heads that is 1,024 distinct timescales per layer. KDA introduced per-channel decay explicitly "to enable multi-timescale memory within a single head" ([KDA discussion](https://openreview.net/pdf?id=FdXB4u27LD)). Since the *entire motivation* for two memories is multiple timescales, and per-channel decay already delivers them free, the second branch's raison d'être disappears.
- **Write strength $\beta$: split into a key-side erase gate $b_t\in(0,2)^{d_k}$ and a value-side write gate $w_t\in(0,1)^{d_v}$.** GDN-2's ablation is direct evidence: collapsing *both* gates to scalar costs 0.65 ppl (15.90 → 16.55); keeping only the erase gate channel-wise recovers most of it (16.12). A single scalar $\beta$ is the worst of the four configurations tested.
- **Init:** $\alpha$ near 1 for a long horizon ($\log\alpha=-\exp(a)\operatorname{softplus}(\cdot)$ with $a$ initialised so $\mathbb{E}[\alpha]\approx0.99$); $b$ near $0.05$–$0.1$ so the first writes are small; channel biases per gate (Muir adds $c_b,c_w,c_q$) so each channel has an independent operating point rather than all starting identical.

## 3.8 Chunking, state carry, and boundaries

Parallel training requires the WY/UT transform: within a chunk of size $C$, accumulate $T=\operatorname{tril}(\bar E\bar K^\top,-1)$, solve $A=(I+T)^{-1}$ by forward substitution, form $Y=A\bar E$, $U=AZ$, then $\mathbf S_C=\operatorname{Diag}(\gamma_C)\mathbf S_0+K_{\text{tail}}^\top(U-YS_0)$. GDN-2 uses $C=64$; Muir uses $C=256$ and notes the triangular-system condition number p90 matters for numerical stability (median p90 7.7 for Muir vs 11.1 for GDN-2), and that a naive unpivoted fp32 kernel produced NaNs on 25% of heads in their stress case. Muir's kernel adds boundary pivoting and reports bfloat16 forward error $7.6\times10^{-3}$ versus fp32 $7.0\times10^{-7}$.

State handling: carry $\mathbf S_C$ in fp32 between chunks; **reset to zero at every document boundary** using `cu_seqlens` for packed batches. The brief's "how recurrent states should be maintained between training chunks" has a clean answer for training (carry within a document, reset across documents). It has a *different* answer for inference on a long tool session, where the state must persist — and that is the one place the fixed-size state genuinely helps.

## 3.9 Errors and ambiguities to correct

1. **Missing write term** — fatal as written (§3.2).
2. **Missing decay placement** — decay must precede the erase read.
3. **No L2 normalization specified** — causes guaranteed divergence (§3.4).
4. **Scalar $\lambda,\beta$** — dominated by published per-channel variants (§3.7).
5. **No state initialisation, reset policy, or chunk-carry spec** — cannot be implemented unambiguously.
6. **No specification of read timing** — determined by the rule, but the brief must fix it.
7. **No gate-range constraint** ($\beta\in[0,2]$, $\alpha\in(0,1]$) — an omitted correctness condition.
8. **"Fast/slow" undefined operationally** — without a constraint tying branch identity to a timescale, nothing prevents the two branches from learning identical dynamics. There is no published evidence either way, because nobody publishes two-branch models.

---

# Part 4 — Parameter Audit

## 4.1 Validation of the ledger (this is why the numbers below are trustworthy)

The ledger was first run against published configurations. If it reproduces *their* counts, its conventions match theirs, and the candidate counts can be believed.

| Configuration | Computed | Published | Δ |
|---|---|---|---|
| Muir 166M (8L, d=1024, f=3584, 32k vocab, untied) | 166.34M | 166.20M | +0.08% |
| Muir 406M (11L, d=1536, f=5632) | 410.01M | 409.73M | +0.07% |
| Muir 834M (14L, d=2048, f=7680) | 836.18M | 835.72M | +0.05% |
| Muir 1.34B (24L, d=2048, f=7680) | 1,339.83M | 1,339.08M | +0.06% |
| GDN-2 1.3B (24L, d=2048, f=5888, dense gates) | 1,339.82M | 1,339.03M | +0.06% |

Systematic +0.05–0.08% drift is attributable to conv/norm parameters the papers fold into their per-layer budget accounting. **Conventions confirmed:** 2-matrix FFN (width $f$), vocab 32,000, untied input/output, no biases, $12d^2$ per-layer non-embedding budget, dense gates $=2d^2+512d$, fused gates $=1024d+512$.

Useful side-result: even the published 1.34B models are **not** at the $12d^2$ budget they claim once embeddings are included — the budget is an accounting device for the transformer block, not for the model.

## 4.2 The baseline is arithmetically close but structurally wrong

Recomputed with d=732, 6 heads × 122, f=2928, GELU, tied, cl100k (100,256):

\[
\underbrace{100{,}256\times732}_{\text{embedding}=73{,}387{,}392}
+12\times\underbrace{\Big(4\cdot732^2+2\cdot732\cdot2928+2\cdot732\Big)}_{\text{block}=6{,}431{,}352}
+\underbrace{732}_{\text{final norm}}
=150{,}564{,}348 .
\]

Stated: 150,580,452. **Difference: 16,104 = 22 × 732 exactly** — 22 unexplained width-732 vectors. The most likely explanation is an extra normalisation per layer plus an output norm, or a bias convention. It is immaterial to the conclusion; the statement "the figure is unverified" is correct, and the error is 0.011%.

The structural problems are much larger than the arithmetic error:

| Defect | Number | Consequence |
|---|---|---|
| Embeddings dominate | 73.39M = **48.7%** of the model | only 77.18M parameters do any computation |
| $d=732$ is not a multiple of 8 | $732 \bmod 8 = 4$ | every GEMM is misaligned for Turing's 16×8×16 HMMA tiles; cuBLAS pads to 736+ and wastes bandwidth |
| head dim 122 | $122 \bmod 8 = 2$ | same misalignment on every attention projection and on the KV cache layout |
| 6 heads of 122 | 122 is not a power of two | poor tensor-core utilisation, awkward for any fused kernel |
| GELU FFN at $4d$ | $f=2928=4\times732$ | 34.2% of parameters; the SAN result says this is defensible, the width is not especially wrong |
| tied embeddings + RoPE + RMSNorm | — | these choices are fine and should be kept |
| 12 layers | — | shallow for a 150M model; SAN's depth ladder put the optimum at 20 layers at d=512 |

**Verdict on the baseline:** sensible in spirit, inefficient in its numerics, and badly allocated in its parameter budget. The single highest-leverage change is not architectural at all — it is fixing $d$ to a multiple of 64 (and preferably 128) and cutting the embedding share.

## 4.3 Candidate ledgers (all computed, all at ~150M)

Conventions for all rows: cl100k vocab 100,256, **tied** embeddings, **no biases**, RoPE (0 params), 2 RMSNorm per block + 1 final, SwiGLU ($3df$) unless marked, GQA where a KV-head count is given, recurrent state excluded from parameter counts.

| # | Candidate | d | L | FFN w | A/R | Total | Dev | Embed | Mem+gate | Attn | FFN |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | baseline as proposed | 732 | 12 | 2,928 | 12/0 | 150,564,348 | +0.38% | 73.39M | 0 | 25.72M | 51.44M |
| A2 | repaired dense Transformer | 576 | 16 | 2,816 | 16/0 | 149,779,008 | −0.15% | 57.75M | 0 | 14.16M | 77.86M |
| A3 | deep dense Transformer | 512 | 20 | 2,816 | 20/0 | 150,966,784 | +0.64% | 51.33M | 0 | 13.11M | 86.51M |
| B | single memory + wide FFN | 512 | 16 | 3,008 | 0/16 | 150,561,280 | +0.37% | 51.33M | 25.29M | 0 | 73.92M |
| C | **dual memory** + FFN (no attn) | 512 | 16 | 1,600 | 0/16 | 149,651,968 | −0.23% | 51.33M | 59.00M | 0 | 39.32M |
| D | **dual + attn/3rd (proposed DMN)** | 512 | 16 | 2,240 | 5/11 | 150,225,408 | +0.15% | 51.33M | 40.56M | 3.28M | 55.05M |
| D2 | dual + attn/3, dense GDN-2 gates | 512 | 16 | 1,984 | 5/11 | 149,689,856 | −0.21% | 51.33M | 46.32M | 3.28M | 48.76M |
| E | Muir-faithful 166M (32k, untied) | 1,024 | 8 | 3,584 | 0/8 | 166,335,488 | +10.9%* | 65.54M | 42.06M | 0 | 58.72M |
| E2 | Muir recipe forced onto cl100k | 768 | 10 | 1,792 | 0/10 | 149,870,336 | −0.09% | 77.00M | 31.57M | 0 | 41.29M |
| F | **recommended hybrid** 3:1, single memory | 512 | 16 | 3,136 | 4/12 | 150,006,272 | **+0.00%** | 51.33M | 18.97M | 2.62M | 77.07M |

Rows D and D2 instantiate the brief's 2:1 arrangement (attention every third layer) at L=16 rather than the brief's L=12, so that they are directly comparable to A2/B/C/F; this gives 5 attention / 11 recurrent (31% attention) rather than 4/8 (33%). The change favours the proposal slightly by giving it more layers, and does not affect any conclusion.

\* Row E is the published 166.20M configuration reproduced at its own size, shown for reference — its +10.9% is deviation from the 150M target, not an error.

**Parameter-count equations used** (per layer, no biases):

- *Transformer / GQA:* $\;d^2+2d\,d_{kv}+d^2+3df+2d$, with $d_{kv}=d\,n_{kv}/n_h$.
- *Single memory, fused gates (Muir):* $\;4d^2+(2\cdot512d+512)+12d+2d+2d+3df$.
- *Single memory, dense gates (GDN-2):* $\;4d^2+(2d^2+512d)+12d+2d+2d+3df$.
- *Dual memory:* the single-memory expression twice (once per branch, own $d_k$), plus fusion $\big(2d^2$ concat / $d^2$ gated / $0$ additive$\big)$, plus **one** FFN.
- *Model total:* $V d\;[+\;Vd \text{ if untied}]+L\cdot(\text{block})+d$.

**Exact worked example, candidate A2** ($d=576$, 9 heads, 3 KV heads, $f=2816$):

$$W_q:576^2=331{,}776;\quad W_k,W_v:2\times576\times192=221{,}184;\quad W_o:331{,}776$$
$$\text{attn}=884{,}736;\quad \text{SwiGLU}=3\times576\times2816=4{,}866{,}048;\quad \text{norms}=1{,}152$$
$$\text{block}=5{,}751{,}936\;\Rightarrow\;16\times5{,}751{,}936=92{,}030{,}976$$
$$\text{total}=92{,}030{,}976+57{,}747{,}456+576=149{,}779{,}008\quad\checkmark$$

## 4.4 Required comparisons, read directly off the table

| Metric | B (single) | C (dual) | D (proposed) | F (recommended) |
|---|---|---|---|---|
| total trainable params | 150,561,280 | 149,651,968 | 150,225,408 | 150,006,272 |
| embedding params | 51,331,072 | 51,331,072 | 51,331,072 | 51,331,072 |
| recurrent-memory params (incl. per-branch norms) | 25,288,704 | 58,998,784 | 40,561,664 | 18,966,528 |
| attention params | 0 | 0 | 3,276,800 | 2,621,440 |
| FFN params | 73,924,608 | 39,321,600 | 55,050,240 | 77,070,336 |
| norm/other (outside memory bucket) | 16,896 | 512 | 5,632 | 16,896 |
| FFN width | 3,008 | 1,600 | 2,240 | 3,136 |
| hidden dim | 512 | 512 | 512 | 512 |
| layers | 16 | 16 | 16 | 16 |
| attention layers | 0 | 0 | 5 | 4 |
| recurrent layers | 16 | 16 | 11 | 12 |
| memory branches | 1 | 2 | 2 | 1 |
| heads × head dim | 8 × 64 | 8 × 64 | 8 × 64 | 8 × 64 |
| budget deviation | +0.37% | −0.23% | +0.15% | +0.00% |
| **runtime state (fp32, per sequence)** | 4.19 MB | 6.29 MB | 3.93 MB | 3.67 MB |

Column sums close exactly against §4.3 totals (e.g. C: 51,331,072 + 58,998,784 + 39,321,600 + 512 = 149,651,968). For the dual-memory rows the two per-branch RMSNorm vectors sit inside the memory bucket, which is why the `norm/other` column is small there.

## 4.5 Where the embedding budget goes, and why it matters more than the architecture

At cl100k's 100,256 tokens, the tied embedding costs $V\cdot d$: 51.3M at $d=512$, 57.7M at $d=576$, 73.4M at $d=732$. It is 34–49% of a 150M model. Meanwhile each embedding row is updated by roughly 30,000 tokens of evidence over the entire run (3B tokens ÷ 100,256 types), which is thin supervision for a 512-dimensional vector.

Three options, in order of preference:

1. **Keep cl100k, accept 34%, and buy depth instead of width.** $d=512$ or 576 with 16–20 layers. This is row F/A2/A3.
2. **Change the tokenizer to ~32k.** This frees ~34M parameters — about 5–6 extra layers — and matches the published recurrent recipes (both Muir and GDN-2 use 32k). Cost: a tokenizer must be trained, and the brief's "control tokenizer" requirement becomes a fixed *new* tokenizer rather than cl100k. For a technical-domain model this is likely worth it, but it changes an experimental variable.
3. **Factored embeddings** (vocab→256→d): saves ~44M at $d=576$, but ALBERT-style factorisation is known to cost quality and **must be ablated**, not assumed. Not recommended as a starting point.

The brief asks whether the 150M / 3B / 2048 constraints should be retained. My answer: **retain 150M and 3B; retain 2048; change $d$ and the layer count; consider changing the tokenizer.** A 150M model at 20 tokens/parameter on FineWeb-Edu is a reasonable, honest configuration — it will not be capable, but it will be trainable and comparable. Pretending 150M can be a competent coding model would be the larger error.

---

# Part 5 — Compute and Hardware Audit

## 5.1 The T4 is the binding constraint, and it is worse than "16 GB"

Verified specifications ([NVIDIA T4 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/tesla-t4/t4-tensor-core-datasheet.pdf), [Turing whitepaper](https://images.nvidia.com/aem-dam/Solutions/design-visualization/technologies/turing-architecture/NVIDIA-Turing-Architecture-Whitepaper.pdf)):

| Property | Tesla T4 | Consequence for MICROCORE |
|---|---|---|
| Architecture | Turing, **sm_75** | newest supported kernel families do not target it |
| **BF16** | **not supported at all** | all mixed precision must be FP16 with loss scaling; no BF16 fallback |
| FP16 tensor | 65 TFLOPS peak (FP32 accumulate) | 2 GPUs = 130 TFLOPS peak; realistic 20–30 TFLOPS aggregate |
| Memory | 16 GB GDDR6, 320 GB/s, 4 MB L2 | 6× lower bandwidth than A100; small L2 kills chunked-kernel reuse |
| Shared memory | 64 KB/SM | constrains Triton tile sizes for chunked recurrence |
| NVLink | none | 2 GPUs communicate over PCIe |

Three of these are disqualifying for the specific kernels the proposal needs:

**(a) Triton no longer emits tensor-core MMA below sm_80.** Since Triton 3.3, "Triton doesn't emit tensor-core MMA for compute capability < 8.0 and falls back to FMA", making the Triton attention path "up to 15× slower than FlashInfer" on T4 ([vLLM issue #60821 / PR #55380](https://github.com/vllm-project/vllm/pull/55380)). The fused chunkwise delta-rule kernels in both reference implementations are Triton (GDN-2: fused Triton, $C=64$; Muir: pure-JAX Pallas on TPU). **Neither paper reports any sm_75 number.** The only sm_75 delta-rule kernel found in this audit is an experimental forward-inference-only fork ([FlashQLA-SM70-SM75](https://github.com/weicj/FlashQLA-SM70-SM75)) — forward only, no backward, hence unusable for training.

**(b) FP16 has a 5-bit exponent.** Dynamic range 6.1e-5 to 65,504. A recurrent state with slow channels ($\alpha\to1$) accumulates writes and its row norms grow as $\sim 1/(1-\alpha_j)$; storing it in FP16 will overflow on some heads. Both reference implementations therefore keep the state in **fp32**. On T4 that state, plus fp32 accumulators, plus the WY triangular solve, runs at FP32/FMA rates (8.1 TFLOPS) rather than tensor-core rates for the state-update portion.

**(c) FlashAttention-2 does not support sm_75.** Attention must use PyTorch SDPA (memory-efficient backend), FlashInfer, or a Triton path that is 6–15× slower on prefill per the issue above. For a *dense Transformer* this is a real but manageable cost — the cuBLAS GEMMs still use tensor cores. For a *recurrent* model the mixer itself loses tensor cores.

**Honest summary:** there is no published evidence that a GDN-2/Muir-class chunkwise kernel trains at usable speed on a T4, and structural reasons (no MMA in Triton below sm_80, no bf16, 64 KB smem, 4 MB L2) to expect it to be much slower than the papers' H100/TPU7x measurements. **Any claim that DMN is "efficient" on T4 is unsupported.** This audit did not measure it; a 30-minute microbenchmark of one gated-delta layer versus one attention layer on a T4 should precede any further work.

## 5.2 Analytical compute comparison (not measured)

Forward MACs per token, causal average, $T=2048$; training FLOPs = $6\times$ forward; GPU-hours at 25% MFU on 2×T4 (130 TFLOPS peak):

| Candidate | GFLOP/token | 3B-token PFLOPs | KV @2K (fp16) | state | GPU-h @25% MFU |
|---|---|---|---|---|---|
| A baseline | 0.83 | 2,499 | 72.0 MB | 0 | 21.4 |
| A2 repaired | 0.79 | 2,380 | 26.7 MB | 0 | 20.3 |
| C dual, no attn | 0.54 | 1,635 | 0 | 6.3 MB | 14.0 |
| D proposed DMN | 0.68 | 2,030 | 4.2 MB | 3.9 MB | 17.4 |
| F recommended hybrid | 0.54 | 1,631 | 6.3 MB | 3.7 MB | 13.9 |

Two readings matter more than the arithmetic:

1. **The nominal FLOP saving is ~32% (0.79 → 0.54), and it is an illusion on this hardware.** It assumes the recurrent mixer costs the same per FLOP as a GEMM. On T4, per §5.1, it does not. The 25% MFU is also optimistic for a 150M model at batch 8–16; 15–20% is more likely, which puts a dense Transformer 3B run at **25–35 GPU-hours**.
2. **The memory saving is irrelevant at $T=2048$.** 26.7 MB → 6.3 MB of KV cache. Both fit in any GPU. The KV-cache argument for hybrids is decisive at 128K context; at 2,048 it is a rounding error. **MICROCORE's sequence length removes the main reason to build a hybrid at all.**

## 5.3 Will it fit in VRAM? Yes — for every candidate

$$\text{params: }150\text{M} \Rightarrow \underbrace{0.30\text{ GB}}_{\text{fp16 w}}+\underbrace{0.30}_{\text{fp16 g}}+\underbrace{1.20}_{\text{Adam }m,v\ \text{fp32}}+\underbrace{0.60}_{\text{fp32 master}}=2.40\text{ GB}$$

Activations for A2 at $B=8$, $T=2048$, gradient checkpointing on: one $B\times T\times d$ fp16 tensor is 18.9 MB; 17 checkpointed layer inputs ≈ 0.64 GB; the largest single attention buffer is $8\times9\times2048^2\times2\text{B}=604$ MB, live only inside one recomputed block. Total ≈ 3.5–4.5 GB of the 14.56 GiB usable. **Batch 8–16 fits comfortably; batch 32 needs care.** VRAM is not the constraint — kernel support and wall-clock are.

## 5.4 Kaggle is the second binding constraint

Kaggle provides **30 GPU-hours per week** (floating, resets weekly) and a **9–12 hour per-session limit** ([Kaggle GPU docs](https://www.kaggle.com/docs/efficient-gpu-usage), [session limits](https://www.kaggle.com/discussions/general/286404)).

Consequences, which the brief does not account for:

- One 3B-token run ≈ 20–35 GPU-hours ⇒ **a single full run consumes most or all of a week's quota**, and requires checkpoint/resume across at least two sessions.
- The brief's 6-arm experiment with 3 seeds = 18 full runs ≈ **360–630 GPU-hours ≈ 3–5 months** of Kaggle quota, before any learning-rate sweeps. That plan cannot be executed.
- The 12-hour session cap means the training loop *must* be resumable (optimizer state, data position, RNG state, LR schedule position, and — for recurrent arms — nothing else, since state resets per document). This is a real engineering requirement, not a footnote.

---

# Part 6 — Training Stability

## 6.1 Risks specific to this architecture, ranked

1. **Divergence from missing key normalization** (certain, if implemented as written). Fix: L2-normalize $q,k$ per head before the recurrence. Non-negotiable.
2. **Slow-channel overflow in FP16.** Fix: fp32 recurrent state, as both reference implementations do. On T4 with no bf16 this is the only safe choice, at a throughput cost.
3. **Windowed amplification despite contractive one-step maps** (§3.5). Fix: log per-layer state Frobenius norm every N steps; abort/restart on monotone growth over a 10M-token window; use a pivoted/boundary-stabilised triangular solve (Muir reports NaN on 25% of heads for a naive unpivoted fp32 kernel).
4. **Gate collapse.** SAN reports that at an extreme learning rate the FFN gates of their baseline collapsed to a mean of 0.07. For MICROCORE the analogous failure is *both* memory branches collapsing to identical dynamics, or the write gate collapsing to 0 (no learning) or 1 (pure overwrite). Fix: log $\mathbb{E}[b_t]$, $\mathbb{E}[w_t]$, $\mathbb{E}[\alpha_t]$ per layer; alert on drift toward the bounds.
5. **Branch redundancy (dual only).** Measure the cosine similarity between the fast and slow branch outputs on a fixed probe batch. If it exceeds ~0.9 by 1B tokens, the second branch is dead weight and the experiment has already answered the question. **This is the single most diagnostic measurement in the whole plan** and it is cheap.
6. **LR sensitivity of recurrent arms.** The SAN study found that the best learning rate differs by architecture and that *sharing* a rate "would bias the comparison" — they swept 0.5×/1×/2× per arm and locked interior minima. Any MICROCORE comparison that uses one LR for all arms is invalid.

## 6.2 Recommended safeguards with justification

| Safeguard | Justification |
|---|---|
| AdamW, $\beta=(0.9,0.999)$, wd 0.1 on matrices only | matches both reference trainings |
| peak LR $6\times10^{-4}$ (dense), sweep $\{3,6,12\}\times10^{-4}$ per arm | 150M is smaller than their 1.3B, so a higher rate than their $4\times10^{-4}$ is plausible; sweep, don't assume |
| warmup 1–2% of total steps (≈60M tokens) | 3B tokens is short; long warmup wastes budget |
| cosine decay to 10% of peak | standard, and cheap to verify |
| global grad-norm clip 1.0 | both references use 1.0 |
| **loss scaling for FP16** with dynamic scaling factor | mandatory without bf16; watch for skipped steps |
| fp32: state, decay computation, cumulative log-decay, master weights | GDN-2 computes decay in fp32 and keeps the state fp32 explicitly |
| zero-init output projections of memory branches | avoids a large initial perturbation to the residual stream |
| separate LR for gate parameters (×0.5) — *optional, ablation only* | plausible but unproven; do not adopt without evidence |
| checkpoint every 500M tokens with full optimizer state | Kaggle 12-hour cap |

**Do not** add: extra gating systems, per-branch learning rates, gradient surgery, or curriculum tricks. None has a published justification at this scale, and each adds a confound to a comparison that already has too few seeds to resolve small effects.

## 6.3 The honest uncertainty

There is **no published training run** of a 150M gated-delta model on 3B tokens at 2,048 context on FP16-only hardware. The nearest evidence — GDN-2 and Muir — is 1.3B parameters, 100B tokens, BF16, H100/TPU7x, 4K context. Extrapolating stability across a 9× parameter decrease, a 33× token decrease, and a precision change is not supported by anything in the literature. Treat stability as an open empirical question, and budget for at least one failed run per recurrent arm.

---

# Part 7 — Capability Assessment

Separating what is evidenced from what is hypothesised, per capability.

| Capability | Effect of the proposed architecture | Evidence class |
|---|---|---|
| **Exact retrieval of identifiers, filenames, error messages, tool output spans** | **Negative risk.** Recurrent-only loses 7–11 points on real-world extraction (GDN-2: 29.88 vs 38.07; Muir: 34.60 vs 45.92). Attention ablation in hybrids produces **0% retrieval** with no compensatory mechanism in recurrent layers. This is the capability most exposed by cutting attention to 4/12 layers. | **Evidenced** (two papers + ablation study) |
| **Long-context behaviour beyond 2,048** | Positive but irrelevant: constant-state extrapolation to 1M–10M tokens is real and well-demonstrated (Muir: passkey 90% at 1M with static readout; 10M-token PPL 7.95 vs GDN-2 8.13). MICROCORE trains and serves at 2,048. | **Evidenced, inapplicable** |
| **Parametric CS knowledge** (OS concepts, networking, security facts) | **Negative.** FFN removal/localisation of the deficit is *parametric recall*; on FineWeb-Edu the FFN is worth 0.0398 nats at iso-params. Narrowing the FFN from 3,136 to 2,240 to pay for a second memory moves in the wrong direction. | **Evidenced** (SAN) |
| **Multi-step reasoning / algorithmic problem solving** | Neutral to slightly positive: SAN finds the FFN deficit concentrates on low-context prediction and that attention-only models are *better* on context-grounded reasoning. Recurrence neither helps nor hurts this. | **Evidenced but not about recurrence** |
| **Code generation** | **Unknown.** No paper in this set evaluates HumanEval/MBPP. Claims in the brief about code are untested speculation. | **No evidence** |
| **Code debugging / multi-file reasoning** | **Unknown**, and plausibly *harmed*: debugging is exact-retrieval-heavy (read the error, find the identifier). See row 1. | **Inference** |
| **Following long instructions, tracking temporary task state** | Plausible small positive from a persistent state, but at 2,048 tokens the whole instruction is in context and attention sees it. The benefit appears at lengths MICROCORE does not use. | **Hypothesis** |
| **Fast/slow memory separation specifically** | **No evidence whatsoever** — in either direction. No published two-branch model. The mechanism is also provably redundant (§3.6) and its stated purpose is served more cheaply by a readout gain. | **No evidence** |
| **Perplexity** | Reported gains are 25–36 millinats (Muir, 1.34B/100B). For scale: the SAN study's seed-to-seed noise floor is 0.0015 nats and the FFN iso-param effect at 24M is 0.006 nats. A 25–36 millinat gain is *larger than these*, so not negligible — but it arrives with a 7–11 point retrieval regression, and it was measured against a baseline that looks under-tuned (§2.3a). | **Evidenced, with caveats** |

**Bottom line:** the architecture trades a capability MICROCORE needs (exact extraction) for a capability MICROCORE cannot use (unbounded context). The one clearly positive literature finding — that a *hybrid* recovers and slightly exceeds Transformer real-world retrieval (GDN-2 hybrid 42.28 vs Transformer 38.07) — argues for **hybrid**, not for **dual memory**, and it argues against the proposal's 4/12 attention share only insofar as it should be no *lower*.

---

# Part 8 — Experimental Plan

## 8.1 Budget reality first

The brief's plan (6 architectures × 3 seeds, 3B tokens each) is **not executable on Kaggle**: ≈360–630 GPU-hours against 30 h/week. The plan below is staged so that the decision is made with the cheapest experiments that can make it.

## 8.2 Stage 0 — prerequisite measurements (≈2 GPU-hours, 1 day)

1. **Microbenchmark on T4:** one gated-delta layer (chunkwise, C=64, fp32 state) vs. one GQA attention layer at $T=2048$, $d=512$, batch 8. Report tokens/s and peak VRAM. **If the gated-delta layer is more than ~1.5× slower than attention, the hybrid arm is dead on this hardware and Stage 1 shrinks to two arms.** This single measurement is worth more than any of the literature above, because it is the one number nobody has published.
2. **Verify FP16 stability** of the recurrent state at the chosen gate init over 20M tokens.

## 8.3 Stage 1 — screening at 1B tokens (≈4×8 GPU-h ≈ 32 GPU-h, ~1.5 weeks)

Four arms, 2 seeds, 1B tokens, all at iso-parameters (150M ±0.5%), seq 2048, same data order, same tokenizer, per-arm LR sweep at 200M tokens then locked:

| Arm | Config | Purpose |
|---|---|---|
| **A2** | repaired dense Transformer, d=576, 16L, f=2816, GQA 3:1, QK-norm | control |
| **B** | single memory (fused gates), d=512, 16L, f=3008 | does recurrence help at all? |
| **F** | single memory + attention 3:1, d=512, 16L, f=3136 | best-supported hybrid |
| **D** | **proposed DMN**, d=512, 16L, f=2240 | is the second memory worth anything? |

Drop candidate E (faithful Muir) from screening: at cl100k it forces $d=768$/10L and 51% embeddings (§4.3, row E2) — it is not a fair comparison at this vocabulary, and the honest conclusion is that **Muir's recipe does not transfer to a 100k vocabulary at 150M parameters without a tokenizer change.** That is a finding, not an experiment.

Metrics, all cheap and all diagnostic:

- validation loss on a held-out FineWeb-Edu shard (fixed 20M tokens, never trained on);
- **fast/slow branch output cosine similarity** (arm D only) — the decisive mechanism test;
- per-layer state norm and $\mathbb{E}[b],\mathbb{E}[w],\mathbb{E}[\alpha]$ trajectories;
- throughput (tokens/s) and peak VRAM, logged per arm;
- RULER-style passkey and variable-tracking at 1K and 2K (synthetic, uncontaminated);
- one code benchmark with execution-based scoring (HumanEval+ or MBPP+, both public and cleanly separated from FineWeb-Edu);
- a "tool-output comprehension" probe built in-house: a synthetic task where a fake terminal error message containing a random identifier must be quoted back and used to select a fix. This is the capability MICROCORE actually needs and no public benchmark measures it.

**Decision rule, fixed in advance:** proceed to Stage 2 only if an arm beats A2 by ≥0.01 nats validation loss *and* does not lose more than 2 points on passkey/tool-output probes. If arm D's branch cosine similarity exceeds 0.9, the dual-memory hypothesis is refuted regardless of loss.

## 8.4 Stage 2 — confirmation at 3B tokens (≈2 arms × 2 seeds × 25 GPU-h ≈ 100 GPU-h, ~4 weeks)

Only the winner of Stage 1 and A2, 2 seeds each, full 3B tokens, with a data-order-matched control. Report:

- validation loss / perplexity (primary);
- the capability suite above at final checkpoint;
- performance per parameter and per GPU-hour (both, since they differ);
- equal-token *and* equal-FLOP comparisons — if the hybrid uses 32% fewer FLOPs per token, a FLOP-matched comparison gives it ~1.5× more tokens for free, and that must be reported as a separate, clearly labelled result, not blended into the iso-token one.

## 8.5 Fairness controls (all mandatory)

| Control | Implementation |
|---|---|
| tokenizer | fixed; if changed, changed for all arms |
| data & order | one pre-tokenized, pre-shuffled token stream; each arm consumes the identical index range |
| tokens | equal for iso-token; FLOP-matched arm explicitly labelled |
| parameters | 150M ± 0.5%, reported exactly (table in §4.3) |
| sequence length | 2048 for all; any long-context eval is a separate, labelled extrapolation test |
| init | same scheme and seed mapping; report per-arm init std |
| LR | swept per arm (0.5×/1×/2×, extend if a boundary wins); locked minima reported |
| precision | FP16 + loss scaling for all arms (no bf16 on T4) — this is a *shared* handicap, not a per-arm choice |
| checkpoint selection | fixed rule (final checkpoint; no per-arm best-checkpoint cherry-picking) |
| seeds | 2 minimum; 3 if quota allows; report per-seed values, not just means |
| contamination | FineWeb-Edu overlaps HumanEval/MBPP-adjacent code; use decontaminated variants and report n-gram overlap statistics |

## 8.6 Tests designed specifically for fast/slow memory

The brief asks for tests that would *falsify* the dual-memory claim. Three, in increasing order of informativeness:

1. **Instruction-switch test.** Sequence: a task instruction $I_1$ with a target identifier $X$; 40K tokens of unrelated filler; a new instruction $I_2$ with target $Y$; then a query for $Y$, then a query for $X$. Predicted by the hypothesis: fast memory holds $Y$, slow holds $X$, both answered. Predicted by the copy-and-decay baseline: $X$ is lost. **If a single-memory model answers both equally well, the second branch is unnecessary.**
2. **Interference/overwrite test.** Repeated $k\!\to\!v$ bindings where the same key is rebound 20 times with different values; query the final value. Tests whether the erase mechanism (not the number of memories) controls interference. GDN-2's MK-NIAH numbers are the reference point.
3. **Branch-identity test (the decisive one).** After training, swap the fast and slow branch weights and re-evaluate; then zero one branch and re-evaluate. If performance is unchanged under swap, the branches learned the same function. If performance collapses when either is zeroed, both are load-bearing but possibly redundant; if zeroing either is harmless, one branch is dead.

---

# Part 9 — Recommended Architecture

The recommendation is **two configs**, one primary and one challenger, both fully specified and both computed exactly.

## 9.1 Primary: repaired dense Transformer (candidate A2)

Chosen because: it is the only architecture with evidence at MICROCORE's scale (SAN, 6–87M), it is the only one whose kernels are supported on sm_75 via cuBLAS/SDPA, it keeps 100% of the retrieval capability that MICROCORE's tasks depend on, and it needs no numerical special-casing beyond FP16 loss scaling.

| Parameter | Value | Rationale |
|---|---|---|
| layers | **16** | SAN's depth ladder: 20 optimal at d=512; 16 at d=576 is the iso-parameter equivalent |
| hidden dim $d$ | **576** | multiple of 64 (=9×64, =4.5×128); 576/8=72 ✓ tile-aligned |
| heads / head dim | **9 × 64** | 64 is the tensor-core-optimal head dim; 9 heads at d=576 |
| KV heads (GQA) | **3** | 3:1 grouping; cuts KV cache and $W_k,W_v$ by 3× |
| FFN | **SwiGLU, $f=2816$** | $4.89d$; SwiGLU at $f\approx4.9d$ ≈ GELU at $f\approx7.3d$ in capacity |
| positional | **RoPE**, $\theta=10{,}000$ | 0 parameters |
| norm | **RMSNorm**, pre-norm | |
| **QK-norm** | **yes**, per head | SAN: *required* for trainability of deep stacks in their setup; cheap insurance |
| embeddings | **tied**, cl100k 100,256 | |
| biases | **none** | |
| total | **149,779,008** (−0.15%) | |

Layer definition, with shapes:

\[
u=\mathrm{RMSNorm}(x),\quad
q=W_q u,\;k=W_k u,\;v=W_v u
\]
\[
(q,k)\leftarrow \mathrm{RoPE}\big(\mathrm{RMSNorm}_{h}(q),\mathrm{RMSNorm}_{h}(k)\big),\quad
A=\mathrm{softmax}\!\Big(\tfrac{qk^\top}{\sqrt{64}}+M\Big),\quad
y=x+W_o(Av)
\]
\[
z=\mathrm{RMSNorm}(y),\quad \mathrm{FFN}(z)=W_{\downarrow}\big(\mathrm{SiLU}(W_{g}z)\odot W_{u}z\big),\quad x'=y+\mathrm{FFN}(z)
\]

Shapes: $x,y,z,x'\in\mathbb{R}^{B\times T\times576}$; $q\in\mathbb{R}^{B\times 9\times T\times64}$; $k,v\in\mathbb{R}^{B\times3\times T\times64}$ (broadcast to 9 heads); $A\in\mathbb{R}^{B\times9\times T\times T}$; $W_q\in\mathbb{R}^{576\times576}$, $W_k,W_v\in\mathbb{R}^{576\times192}$, $W_o\in\mathbb{R}^{576\times576}$, $W_g,W_u\in\mathbb{R}^{2816\times576}$, $W_\downarrow\in\mathbb{R}^{576\times2816}$.

## 9.2 Challenger: single-memory 3:1 hybrid (candidate F)

Chosen over the proposed DMN because it is the arrangement the literature actually supports (GDN-2 hybrid 42.28 > Transformer 38.07 on real-world retrieval), it keeps a **wider** FFN than the DMN (3,136 vs 2,240), and it drops the branch that has no evidence.

| Parameter | Value |
|---|---|
| layers | **16**: 12 gated-delta-recurrent, 4 full attention at layers 4, 8, 12, 16 |
| hidden dim | **512** |
| heads / head dim | **8 × 64** (recurrent and attention) |
| GQA (attention layers) | **2 KV heads** |
| FFN | SwiGLU, $f=3136$, identical in both block types |
| memory | single state, $d_k=d_v=64$, per-head $S\in\mathbb{R}^{64\times64}$ |
| gates | **fused low-rank, $R_{\text{tot}}=512$** splits $(r_f,r_b,r_g,r_w,r_q)=(64,64,128,128,128)$; channel biases $c_b,c_w,c_q$ |
| readout | **matched-filter gain** $\gamma_t=\gamma_{\text{stat}}\odot2\sigma(z^q_t)$, $\gamma_{\text{stat}}$ init $\mathbf 1$ |
| conv | depthwise causal conv, kernel 4, over $q,k,v$ |
| chunk | $C=64$ |
| **attention share** | **4/16 = 25%** (3:1), the established ratio |
| total | **150,006,272** (+0.00%) |

Recurrent layer (per head, $\gamma$ readout as in Muir):

\[
g_t=-\exp(a)\odot\operatorname{softplus}(W_fx_t+\delta),\quad
\alpha_t=e^{g_t},\quad
b_t=2\sigma(z^b_t),\quad w_t=\sigma(z^w_t)
\]
\[
\bar S_t=\mathrm{Diag}(\alpha_t)S_{t-1},\quad
e_t=b_t\odot k_t,\quad r_t=\bar S_t^\top e_t,\quad
S_t=\bar S_t+k_t\big(w_t\odot v_t-r_t\big)^\top
\]
\[
o_t=(\gamma_t\odot q_t)^\top S_t,\qquad \gamma_t=\gamma_{\text{stat}}\odot 2\sigma(z^q_t)
\]
\[
\text{out}=W_o\Big[\mathrm{RMSNorm}_h(o_t)\odot\mathrm{SiLU}(g^{\text{out}}_t)\Big]
\]

Shapes: $S_t\in\mathbb{R}^{64\times64}$; $q_t,k_t\in\mathbb{R}^{64}$ with $\lVert\cdot\rVert_2=1$; $v_t\in\mathbb{R}^{64}$; gates $\alpha_t,b_t\in\mathbb{R}^{64}$, $w_t\in\mathbb{R}^{64}$; all five gate logits from one $W_\downarrow\in\mathbb{R}^{512\times512}$ then per-gate $W^\uparrow_m$.

**Do not** add a second memory branch. If the Stage-1 branch-identity test shows the fast/slow split is genuinely load-bearing (which §3.6 says it should not be), the correct response is a single memory with $d_k=128$ and a full erase matrix — strictly more expressive at the same parameter count — not two states.

## 9.3 Programmatic verification (executed)

`audit_v2.py` (attached) implements the ledger, validates it against the five published configurations in §4.1, enumerates candidate FFN widths to hit 150M ±0.5%, and asserts dimension divisibility. It was **executed**; the tables in §4.3 and §4.4 are its output. `compute_audit.py` produces §5.2. Both are pure Python and run without torch.

Shape/assertion checks to keep in the real implementation:

```python
# recurrent update
assert S.shape == (B, H, dk, dv)          # state, fp32
assert k.shape == (B, H, T, dk) and q.shape == k.shape
assert v.shape == (B, H, T, dv)
assert torch.allclose(k.norm(dim=-1), torch.ones_like(k.norm(dim=-1)), atol=1e-5)  # L2 normalized
assert b.min() >= 0 and b.max() <= 2      # erase range
assert w.min() >= 0 and w.max() <= 1      # write range
assert alpha.min() > 0 and alpha.max() <= 1
# delta-rule identity check against a tokenwise reference, fp64
S_ref = torch.zeros(dk, dv, dtype=torch.float64)
for t in range(T):
    S_ref = S_ref - torch.outer(k64[t], (S_ref.T @ (b64[t]*k64[t]))) + torch.outer(k64[t], w64[t]*v64[t])  # no decay
# must match the chunkwise kernel to <1e-9 in fp64
# fusion
assert out.shape == x.shape
assert fusion_w.shape == (2*d, d)          # if concat
```

Note explicitly: **the equations and calculator being correct does not mean the architecture has been tested.** No model was trained in this audit.

---

# Part 10 — Final Decision

## DECISION: **REPLACE**

(The dual-memory DMN as specified is, separately, **REJECT**ed.)

**Why REPLACE and not merely VALIDATE WITH MODIFICATIONS.** "Validate with modifications" would be right if the core idea survived contact with the evidence and needed tuning. It does not, for three independent reasons that would each be sufficient alone:

1. **The mechanism is not a mechanism.** A dual-memory layer with additive fusion is provably identical to a single memory of double key width with a block-diagonal erase constraint (§3.6). It cannot do anything a single memory of equal width cannot do, and a single memory of equal width with a full erase matrix does strictly more. The literature's actual solution to the problem the split was meant to solve — slow-channel dominance — is a readout gain costing $128d$ parameters, 8× less than the concat fusion it would replace (§3.6).
2. **It cannot be afforded at this parameter count.** At 150M with a 100,256-token vocabulary, the second branch costs 21.6M parameters = 880 FFN channels = 28% of the FFN. The brief simultaneously requires a wide FFN and two memories; at this scale those requirements are in arithmetic conflict, and the evidence (SAN, FineWeb-Edu 0.0398 nats) says the FFN is the one that earns its keep for a knowledge-oriented model.
3. **The advantage cannot materialise on this hardware at this sequence length.** At $T=2048$ the quadratic attention term is ~29% of block FLOPs and the KV cache is 27 MB — the entire motivation for sub-quadratic mixing is absent. Meanwhile the T4 lacks bf16, lacks tensor-core MMA in Triton below sm_80, and lacks FlashAttention-2, so the recurrent path — the one that needs custom kernels — is precisely the path that loses hardware acceleration. The published throughput advantage (Muir: 1.6×–2.7× over Splash at 16K–32K) is a *long-context* result; at 2K–4K Muir runs at **0.34×–0.45×** Transformer throughput.

**What replaces it.** A repaired dense Transformer (A2: 16L, $d=576$, 9×64 heads, GQA 3:1, SwiGLU 2816, QK-norm, 149,779,008 params) as the primary, with a single-memory 3:1 hybrid (F: 16L, $d=512$, 4 attention / 12 recurrent, fused low-rank gates with matched-filter readout, SwiGLU 3136, 150,006,272 params) as the one challenger worth a controlled run. Both are specified to the tensor shape in Part 9 and both are computed exactly.

**What should happen to the DMN.** Keep it as an *ablation arm* (candidate D) in Stage 1 — it is cheap to run once the single-memory path exists, and a negative result with the branch-similarity measurement attached is a genuine contribution. It should not be the plan of record, the paper, or the name of the model.

## What would change this verdict

Stated explicitly so the conclusion is falsifiable rather than merely assertive:

1. A T4 microbenchmark showing a chunkwise gated-delta layer within ~1.2× of a GQA attention layer at $T=2048$ (would remove objection 3).
2. A demonstration that MICROCORE's real workload needs sequences ≥32K (would make objection 3 moot and would make the hybrid the right answer).
3. A Stage-1 result where arm D beats A2 by ≥0.01 nats *and* the branch-similarity test shows the two branches are functionally distinct *and* the retrieval probes do not regress (would refute objection 1 empirically, though not the algebra).
4. A tokenizer change to ~32k, which would free ~34M parameters and make a wider-FFN dual-memory variant arithmetically possible (would soften objection 2, not 1).

Absent at least one of these, the proposal should not proceed as designed.

## Research-integrity statement

- All parameter counts in Part 4 are **computed by code that was executed**, and that code was **validated against five published configurations** before being used.
- All quoted results belong to the papers cited, on their hardware and their token budgets; **none are MICROCORE measurements**.
- **No GPU was used.** §5.2's GPU-hour figures are analytical estimates at an assumed 25% MFU and are labelled as such; §5.1's kernel claims are structural and cite the sources for each.
- The three named arXiv papers were located and read; their identifiers, authors, and dates are verified. Two claims in the brief that could not be verified against a primary source — the exact 150,580,452 parameter figure (recomputed to 150,564,348) and any claim that the stated baseline was tuned — are flagged rather than accepted.
- Where the literature is silent (code benchmarks for recurrent architectures; two-branch training dynamics; sm_75 kernel performance), this audit says so rather than inferring.

---

## Attached artefacts

- `audit_v2.py` — parameter ledger with published-configuration validation, candidate enumeration, executed.
- `compute_audit.py` — FLOPs, KV cache, recurrent-state and VRAM estimates, executed.
- `param_audit.py` — first-pass audit including the baseline discrepancy derivation, executed.

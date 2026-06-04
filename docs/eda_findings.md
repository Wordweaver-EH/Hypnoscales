# EDA Findings - Suggestibility Datasets

*W. Weaver, June 2026. Aside from main paper. Scripts: analysis/a09_eda.py, analysis/a10_eda2.py.*

This file keeps the empirical EDA results and follow-up questions separate from the speculative theory and scale-design notes. Mechanistic interpretation and proposed item design now live in [theory_and_scale_design_notes.md](theory_and_scale_design_notes.md).

---

## Part A: Empirical findings

### A1. VVIQ predicts taste, not visual items

**Dataset:** df2 (PCS-VVIQ, N=508)

VVIQ total correlates most strongly with taste hallucination (r=0.242), not with visual
items. Neg. visual hallucination r=−0.017 (ns). Music r=0.076 (ns). Arm rigidity r=0.146
(p<.01).

Sub-item check: sweet r=0.218, sour r=0.223 — nearly identical. The taste-VVIQ
relationship is not a reliability artefact from averaging two ratings; it is present in
both components equally.

VVIQ does not predict profile membership (Kruskal-Wallis p=0.11). High imagers are not
disproportionately in any response-profile group.

**Interpretation.** Taste hallucination has no competing ambient sensory signal — it is
already a "pure prior" context — and VVIQ predicts it strongly. Music and visual items
floor in a clear sensory environment: prior strength is irrelevant when sensory confidence
is high. Under sensory degradation the VVIQ correlations should emerge (see PP layer
section).

---

### A2. Response profiles: one dominant type, no distinct perceptual class

**Dataset:** df1 PCS (N=244), k-means k=4

| Profile | n   | %   | Signature |
|---------|-----|-----|-----------|
| P1      | 12  |  5% | High all items including music (3.67) — rare high-suggestible |
| P2      | 15  |  6% | Neg. visual = 4.73, music near-zero — specific visual responder |
| P3      | 138 | 57% | High motor + ideomotor, both perceptual floor items near-zero — **modal** |
| P4      | 79  | 32% | Low everything — low-suggestible |

Profile P2 (neg-visual spike) inspected at case level: 13/15 had neg-visual = 5/5. These
are not noise — mid-to-high overall responders who also maxed visual hallucination. Likely
a small high-responder subgroup, not a qualitatively distinct type.

**LCA (Bernoulli mixture EM) on binary pass/fail:**
BIC selects k=2. Two-class solution:

| Class | Weight | P(pass\|motor) | P(pass\|music) | P(pass\|neg.vis) |
|-------|--------|----------------|----------------|-----------------|
| High  | 73%    | ~0.99          | 0.185          | 0.121           |
| Low   | 27%    | ~0.77          | 0.000          | 0.039           |

No evidence for a qualitatively distinct perceptual-responder class. The structure is a
gradient. Consistent with GMM-BIC on HGSHS:A (see dimensionality section).

---

### A3. Item retest stability

**Dataset:** PCS norms retest (n=61 PCS, n=62 SWASH, embedded re-administration)

| Item               | Type       | r (PCS) | r (SWASH) | Floor T1 |
|--------------------|------------|---------|-----------|----------|
| Hand lowering      | motor      | 0.323   | 0.469     | 0%       |
| Hands together     | motor      | 0.318   | 0.490     | 2%       |
| Mosquito           | perceptual | 0.503   | 0.610     | 28%      |
| Taste              | perceptual | 0.449   | 0.639     | 18%      |
| Arm rigidity       | motor      | 0.217   | 0.558     | 0%       |
| Arm immobilisation | motor      | 0.411   | 0.420     | 5%       |
| Music              | perceptual | 0.645   | −0.013    | 84%      |
| Neg. visual        | perceptual | 0.216   | −0.025    | 95%      |
| Amnesia            | cognitive  | 0.337   | 0.382     | 23%      |
| Post-hypnotic      | cognitive  | 0.266   | 0.193     | 54%      |

Mean retest r by type (PCS): motor=0.317, perceptual=0.453, cognitive=0.301.

Motor items are *less* stable session-to-session than perceptual items in PCS despite
dominating the cross-sectional variance. Music hallucination (r=0.645 PCS) is the single
most stable item — when the experience fires it fires consistently (trait signal is real).
SWASH collapses music and neg-visual retest r to near-zero because floor rates climb to
~89%/~94%: too few non-zero cases to correlate.

---

### A4. HGSHS:A objective score is dimensional, not taxonic

**Dataset:** df4 (Terhune/Reshetnikov, N=584)

| k | BIC    | AIC    | Means               | Weights      |
|---|--------|--------|---------------------|--------------|
| 1 | 2740.8 | 2732.1 | [5.74]              | [1.0]        |
| 2 | 2754.4 | 2732.6 | [4.37, 7.87]        | [0.61, 0.39] |
| 3 | 2769.0 | 2734.1 | [4.16, 7.34, 1.41]  | [0.33, 0.58, 0.09] |

BIC favours k=1 (dimensional) by 13.6 points over k=2. MAMBAC curve (arm rigidity
indicator) is monotone. Score distribution roughly unimodal, centred ~5–6 out of 12.

Note: GMM-BIC is not identical to waveform-based taxometric methods (MAMBAC, MAXEIG,
L-Mode) used in the Terhune paper. Complementary, not contradictory. Full taxometric
replication is warranted.

---

### A5. Induction (SWASH) uniformly suppresses responding

**Dataset:** df1 randomised norms (PCS N=244 vs SWASH N=240)

All items decrease from PCS to SWASH. No amplification.

| Item type                                          | Mean change    |
|----------------------------------------------------|----------------|
| Perceptual (mosquito, taste, music, neg.visual)    | −36% to −48%  |
| Motor challenge (rigidity, immobilisation)         | −22% to −25%  |
| Motor ideomotor (hand lower, hands together)       | −13% to −17%  |
| Cognitive (amnesia, post-hypnotic)                 | −2% to −7%    |

Profile 4 (low-everything) grows from 23% (PCS) to 51% (SWASH) — whole-distribution
compression downward, not selective shift.

Two competing accounts:
1. **Relaxation mechanism:** perceptual items require active effortful imagination →
   suppressed most by relaxation. Ideomotor items involve passive kinesthetic experience
   → partially spared.
2. **Context/threshold effect (PP):** formal hypnosis framing raises the subjective
   threshold for what counts as a genuine experience. Participants demand more of
   themselves before rating, especially for imaginative/perceptual items that feel more
   voluntary. Cognitive items (amnesia, PHS) depend on compliance mechanisms → nearly
   unaffected.

---

---

## Part H: Open questions

1. Does VVIQ × taste replicate in df3 (SWASH paper has matched items)?
2. Does the Bernoulli k=2 LCA finding hold in df2, df3, df5?
3. Item-level retest in a standalone two-item context — embedded r=0.217 is a lower bound.
4. What mediates taste-VVIQ? Gustatory imagery vividness would clarify modality specificity.
5. Full MAMBAC/MAXEIG/L-Mode on df4 using proper taxometric methodology.
6. Is the neg-visual spike profile (P2) stable across sessions? 15 people, 13 at ceiling —
   a real phenotype if it replicates.
7. Why does SWASH induction reduce responding? In selected high-suggestibles the direction
   might reverse (relaxation facilitates rather than suppresses).
8. Does the cross-modal (Nair & Brang) item show stronger PsiQ/VVIQ correlation than the
   unimodal auditory item under equivalent deprivation?
9. Does the eigengrau item correlate with phosphene proneness and with the P2 profile?
10. Does PsiQ dissociate from VVIQ in predicting PP-layer items (noise paradigm) vs.
    GWT/CCT-layer items (motor, tingling)?
11. Run ASMR questionnaire (AEQ) × PCS item correlations — dataset was in the repo,
    correlations never computed.

---

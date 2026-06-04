# EDA notes — suggestibility datasets
*W. Weaver, June 2026. Aside from main paper. Scripts: analysis/a09_eda.py, analysis/a10_eda2.py.*

---

## 1. VVIQ does not predict visual items — it predicts taste

**Dataset:** df2 (PCS-VVIQ, N=508)

VVIQ total correlates most strongly with taste hallucination (r=0.242), not with visual items.
Neg. visual hallucination r=−0.017 (ns). Music r=0.076 (ns). Arm rigidity r=0.146 (p<.01).

Sub-item check: sweet r=0.218, sour r=0.223 — nearly identical. The taste-VVIQ
relationship is not a reliability artefact from averaging two ratings; it is present in
both components equally.

VVIQ does not predict profile membership (Kruskal-Wallis p=0.11). High imagers are
not disproportionately in any response-profile group.

**Interpretation.** VVIQ captures general phenomenological richness or imaginative
compliance, not visual-modality-specific imagery. The prediction that imagery vividness
would selectively elevate perceptual/visual items is not supported. The
visual hallucination items are near-floor in this sample, so floor effects may
suppress any true correlation there; but mosquito hallucination (which does not floor,
pass rate 69%) also sits below taste (r=0.092 vs 0.242). Taste hallucination may
genuinely require vivid cross-modal imagination in a way visual items do not.

**Follow-up questions.**
- Does VVIQ predict the taste sub-items equally across scales (SWASH has matched items)?
- Is the taste-VVIQ link replicated in df3 (SWASH paper)?
- Does vividness of olfactory/gustatory imagery (not measured by VVIQ, which is purely visual)
  mediate the taste finding?

---

## 2. Response profiles: one dominant type, no distinct perceptual class

**Dataset:** df1 PCS (N=244), k-means k=4

| Profile | n | % | Signature |
|---------|---|---|-----------|
| P1 | 12 | 5% | High all items including music (3.67) — rare high-suggestible |
| P2 | 15 | 6% | Neg. visual = 4.73, music near-zero — specific visual responder |
| P3 | 138 | 57% | High motor + ideomotor, both perceptual floor items near-zero — **modal** |
| P4 | 79 | 32% | Low everything — low-suggestible |

Profile P2 (neg-visual spike) was inspected at case level: 13/15 had neg-visual = 5/5
(ceiling). These are not noise. They are mid-to-high overall responders who also maxed
out on visual hallucination specifically; many have high motor scores as well. This is
probably a small high-responder subgroup, not a qualitatively distinct type.

No "motor-only" cluster emerges that is distinct from "motor + ideomotor." Motor challenge
and ideomotor items cluster naturally together in the modal profile.

**LCA (Bernoulli mixture EM) on binary pass/fail responses:**

BIC selects k=2 over k=3, 4, 5. The two-class solution:

| Class | Weight | P(pass\|motor) | P(pass\|music) | P(pass\|neg.vis) |
|-------|--------|---------------|----------------|-----------------|
| High  | 73%    | ~0.99          | 0.185           | 0.121            |
| Low   | 27%    | ~0.77          | 0.000           | 0.039            |

No evidence for a qualitatively distinct perceptual-responder class. The structure is
a gradient, not a taxonomy. Consistent with the GMM-BIC result on HGSHS:A (see §4).

---

## 3. Motor items are the least temporally stable

**Dataset:** PCS norms retest file (n=61 PCS, n=62 SWASH, embedded re-administration)

PCS item test-retest correlations:

| Item | Type | r (PCS) | r (SWASH) | Floor T1 |
|------|------|---------|-----------|----------|
| Hand lowering | motor | 0.323 | 0.469 | 0% |
| Hands together | motor | 0.318 | 0.490 | 2% |
| Mosquito | perceptual | 0.503 | 0.610 | 28% |
| Taste | perceptual | 0.449 | 0.639 | 18% |
| Arm rigidity | motor | 0.217 | 0.558 | 0% |
| Arm immobilisation | motor | 0.411 | 0.420 | 5% |
| Music | perceptual | 0.645 | −0.013 | 84% |
| Neg. visual | perceptual | 0.216 | −0.025 | 95% |
| Amnesia | cognitive | 0.337 | 0.382 | 23% |
| Post-hypnotic | cognitive | 0.266 | 0.193 | 54% |

Mean retest r by type (PCS): motor=0.317, perceptual=0.453, cognitive=0.301.

Motor items are less stable session-to-session than perceptual items in PCS.
Music hallucination (r=0.645 in PCS) is the single most stable item, despite being
84% floor. When a participant does experience music hallucination, they reliably
experience it again.

SWASH reverses the perceptual picture: music and neg-visual drop to near-zero retest
r under SWASH, where floor rates are ~89% and ~94%. Too few non-zero cases to
produce stable correlations.

**Implication for the screener.** The motor pair has good internal consistency
(inter-item r ~0.55 embedded), but modest individual item stability (arm rigidity
r=0.217 PCS). The perceptual items that look useless for cross-sectional variance
carry more trait-like signal when they do fire. This is a genuine tension if the
two-item form is ever tested as a standalone instrument — standalone administration
may show worse retest stability than expected from the embedded figures.

---

## 4. HGSHS:A objective score is dimensional, not taxonic

**Dataset:** df4 (Terhune/Reshetnikov, N=584)

Gaussian mixture model BIC comparison:

| k | BIC | AIC | Means | Weights |
|---|-----|-----|-------|---------|
| 1 | 2740.8 | 2732.1 | [5.74] | [1.0] |
| 2 | 2754.4 | 2732.6 | [4.37, 7.87] | [0.61, 0.39] |
| 3 | 2769.0 | 2734.1 | [4.16, 7.34, 1.41] | [0.33, 0.58, 0.09] |

BIC favours the single-component (dimensional) model by 13.6 points over k=2.
MAMBAC curve (arm rigidity indicator) is monotone, consistent with dimensionality.
Score distribution is roughly unimodal, centred around 5–6 out of 12.

**Note.** GMM-BIC is not identical to the waveform-based taxometric methods (MAMBAC,
MAXEIG, L-Mode) used in the Terhune paper. These results are complementary, not
directly contradictory. The published taxometric claim should be re-examined with
proper MAMBAC/MAXEIG on these data using the original item indicators.

---

## 5. Induction (SWASH) uniformly suppresses responding — no amplification

**Dataset:** df1 randomised norms (PCS N=244 vs SWASH N=240, same item pool)

All items decrease from PCS to SWASH. There is no amplification.

| Item type | Mean change |
|-----------|-------------|
| Perceptual (mosquito, taste, music, neg.visual) | −36% to −48% |
| Motor challenge (rigidity, immobilisation) | −22% to −25% |
| Motor ideomotor (hand lower, hands together) | −13% to −17% |
| Cognitive (amnesia, post-hypnotic) | −2% to −7% |

**Interpretation.** The higher motor-pair correlation under SWASH is not because
induction amplifies motor responding — it is because perceptual items are pushed
further toward floor, leaving the total variance even more dominated by motor items.

The differential suppression pattern is consistent with a relaxation/context mechanism:
- Perceptual items require active effortful imagination → suppressed most by relaxation
- Motor ideomotor items involve passive kinesthetic experience → partially facilitated by relaxation
- Cognitive items (amnesia, PHS) depend on compliance/expectation mechanisms → nearly unaffected
- Motor challenge items are intermediate

A competing context-effects account: the formal hypnosis framing raises the subjective
threshold for what counts as a genuine experience (participants demand more of
themselves before rating), particularly for imaginative/perceptual items that feel
more voluntary.

**Profile consequence.** Profile D joint fit shows Profile 4 (low-everything) growing
from 23% (PCS) to 51% (SWASH). This is a whole-distribution compression downward,
not a selective shift of low-suggestibles upward.

---

## 6. Open questions for future work

1. Does VVIQ × taste replicate in df3 (SWASH paper has matched items)?
2. Does the Bernoulli k=2 LCA finding hold in df2, df3, df5? Cross-dataset
   replication would strengthen the anti-taxon conclusion.
3. Item-level retest in a standalone two-item context — the embedded figures
   (arm rigidity r=0.217) are a lower bound; standalone may be worse or better.
4. What mediates the taste-VVIQ relationship? Olfactory/gustatory imagery
   vividness scales would clarify whether it is truly taste-specific or
   general imaginative compliance.
5. Full MAMBAC/MAXEIG/L-Mode on df4 using proper taxometric methodology.
6. The neg-visual spike profile (P2): is it stable across sessions? If those 15
   people have stable high neg-visual scores, they are a genuine phenotype worth
   characterising.
7. Why does the relaxation induction reduce responding when the classic literature
   expects induction to increase it? The norms sample is unselected undergraduates.
   In selected high-suggestibles the direction might be different.

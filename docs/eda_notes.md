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

## 6. Scale development idea: lift perceptual floors via sensory degradation

The persistent floor on music hallucination (~84%) and negative visual hallucination
(~92%) is not a defect in those items per se — they are valid perceptual suggestions
that carry domain-specific variance and high trait stability when they fire (music
retest r=0.645). The floor is a consequence of running the scale in a normal sensory
environment, where high sensory confidence means top-down suggestions can rarely
compete with bottom-up input.

**The mechanism (Reeder 2024; Clark 2013, 2015, 2023; Dijkstra):**

Under predictive processing, perception is a weighted competition between bottom-up
sensory evidence (precision-weighted) and top-down priors. In a quiet, well-lit
testing room, sensory confidence is high and suggestions lose. Reducing sensory
confidence — by introducing ambiguous background stimulation — shifts the balance
toward top-down priors, enabling more participants to experience the suggested
percept.

Two established laboratory demonstrations of this:

**Auditory — White Christmas paradigm**
- Barber & Calverley (1964): participants instructed to imagine "White Christmas";
  >50% reported hearing it clearly.
- Merckelbach & van de Ven (2001): signal-detection version with white noise
  background; participants reported the song embedded in static. Fantasy proneness
  modulated the effect.
- Directly applicable to music hallucination: presenting the suggestion against
  low-level broadband noise would reduce sensory confidence, lower the effective
  threshold, and convert a near-floor item into a variable one.

**Visual — Dijkstra paradigm (Dijkstra, Bosch & van Gerven)**
- Participants imagine a Gabor patch (tilted grating) while viewing dynamic visual
  noise. Vivid imagers show reality-monitoring failures — they report the imagined
  pattern as actually present.
- Neural mechanism: visual imagery activates V1/fusiform with sufficient signal to
  cross a reality threshold governed by frontal-visual networks; visual noise reduces
  the competing bottom-up signal so the threshold is crossed more easily.
- Applicable to negative visual hallucination: present the suggestion against a
  dynamic visual noise background (or a Gabor-family ambiguous stimulus) rather than
  in a clear field.

**Connection to Reeder's Divergent Predictive Perception Model (2024):**
Sensory confidence = Bayesian precision weight on incoming data.
Degraded input (white noise, visual static) forces sensory confidence toward zero,
making high-level priors (the suggestion) dominate.

```
Normal:   High sensory confidence + weak prior  → realistic perception
Degraded: Low sensory confidence  + strong prior → suggested hallucination
```

Reeder's model adds individual differences: position on the aphantasia–hyperphantasia
spectrum determines the strength of the mid-level imagery prior. Hyperphantasics
generate a large top-down signal that easily clears the reality threshold; aphantasics
generate none and would not hallucinate even under degraded conditions. This predicts
that the VVIQ × item correlation that currently disappears at floor (music r=0.076,
visual r=−0.017) would emerge strongly under sensory degradation.

**Our data make this prediction concrete:**

| Item | Retest r (trait stability when non-zero) | Floor rate | VVIQ r (current) |
|------|------------------------------------------|------------|-----------------|
| Music hallucination | 0.645 | 84% | 0.076 |
| Neg. visual hallucination | 0.216 (unreliable at floor) | 95% | −0.017 |
| Taste hallucination | 0.449 | 18% | **0.242** |

Taste hallucination has no ambient masking noise to overcome — it is already a "pure
imagery" context — and VVIQ predicts it strongly. Music and visual items are suppressed
by a clear sensory environment. If that environment were degraded, VVIQ should predict
them as strongly as it currently predicts taste, or more so (perceptual modality match).

**Three substrate approaches for perceptual items:**

**1. Degraded-environment versions (equipment-assisted)**
- *Auditory:* suggestion delivered against low-level broadband noise (~40 dB); rate
  intensity of heard music 0–5. Direct analogue of Merckelbach & van de Ven.
- *Visual:* suggestion delivered against dynamic pixelated noise or phase-scrambled
  grating (Dijkstra paradigm); rate intensity of seen pattern 0–5.

**2. Phosphene/eigengrau substrate (no equipment)**
Eyes closed in a moderately darkened room. The visual field is already a dynamic
noise field (eigengrau + phosphene activity) — sensory confidence is near-zero by
default. Two item variants:
- *Positive visual hallucination:* "Notice the visual field behind your eyes. As you
  watch, something begins to take shape — a light, a colour, a form." Rate vividness
  0–5. Natural gradient: phosphene flicker (1) → organised shapes (3) → stable 3D
  constructs (5).
- *Instruction principle:* discovery-oriented over volitional — "notice what appears"
  not "try to see X." Volitional instruction fails; undirected attention on the
  substrate succeeds. (Weaver, blog.phenomenal.ink/veil-of-perception, n.d.)
  Phenomenologically equivalent to passing an ideomotor suggestion — the experience
  arrives, it is not produced.

Phosphene-hallucination trait link supports this as a valid suggestibility probe:
respondents who have spontaneous hallucination experience show ~10× higher odds of
phosphene experience (chi-square p < 0.0025; Weaver, blog.phenomenal.ink/
something-about-phosphenes, n.d.). When the substrate is already active (phosphenes),
the suggestion has a real percept to work with rather than nothing.

**3. Cross-modal synesthesia item (Nair & Brang 2019)**
Nair & Brang demonstrated that brief visual deprivation is sufficient to induce
auditory-evoked visual percepts in non-synesthetes — cross-modal binding is latent
in the general population and released by reducing visual sensory confidence.

Applied item: eyes closed + brief tone or musical phrase → suggest colour or form
associated with the sound appears in the visual field. Combines:
- Eigengrau substrate (visual deprivation, sensory confidence → 0)
- Auditory input as the prior-driving signal
- Top-down imagery as the generative mechanism

This collapses the music hallucination and visual hallucination dimensions into a
single cross-modal item. Reeder's model predicts that hyperphantasics (strong
mid-level imagery prior) will show the strongest binding; aphantasics will not bind
even under deprivation, producing maximal individual-differences sensitivity.

The item also connects naturally to the existing scale structure: the music
hallucination item is already auditory; adding the cross-modal visual component
upgrades it from a pure auditory suggestion to a richer perceptual event without
requiring new equipment.

**Additional candidate items:**

**vEAR as a scale item (not just criterion)**
vEAR (visual evoked afterimage response) has been used here as an external criterion
(df5 correlations). But the afterimage itself is a natural suggestion substrate: show
a brief bright stimulus, then suggest the participant maintains, extends, and
elaborates the afterimage under suggestion. Real sensory persistence provides an
anchor — not purely imagined, not purely perceived. The suggestion rides a genuine
trace rather than generating from nothing.
- Substrate: veridical afterimage (high credibility, reduces demand characteristics)
- Direction: suggestion to shape/transform/extend what is already there
- Modality: visual, but distinct from both eigengrau (no prior stimulus) and
  Dijkstra noise (no structured percept). Closer to the morphic/figure-ground class.
- Individual differences: vEAR score itself predicts PCS performance (df5), so
  afterimage suggestibility may already be partially indexed by it.

**Chills/tingles (somatic/ASMR-adjacent)**
A somatosensory modality absent from PCS/SWASH entirely. ASMR-like tingling and
musical frissons (chills) share the feature of being:
- Involuntary (arrive rather than being produced — same phenomenology as ideomotor)
- Triggered top-down (specific sounds, expectations, or direct suggestion)
- Graded in intensity (0–5 is natural)
- Already widely experienced in the general population (ASMR prevalence ~20–30% in
  unselected samples; frissons higher)

As a suggestion item: auditory trigger (whispering, tapping, music) or direct
suggestion alone → rate tingling/chilling spreading from scalp or spine 0–5.
Near-floor problem is less acute than for visual items because the phenomenon is
common and the relevant sensory confidence (skin/proprioception) is lower than
external visual/auditory confidence.

The ASMR dataset (Autonomous Experiences Questionnaire) was briefly in the repo
(removed as unused). Its correlation with PCS items was not run — worth recovering.
Cross-modal angle: chills to music (frisson) involves an auditory→somatic pathway;
ASMR involves auditory/visual→somatic. Both are real cross-modal binding under
reduced threat of sensory contradiction.

**Proposed extended screener (exploratory):**

| Item | Modality | Substrate | Equipment |
|------|----------|-----------|-----------|
| Arm rigidity | Motor challenge | Normal | None |
| Arm immobilisation | Motor challenge | Normal | None |
| Eigengrau visual | Positive visual | Eyes-closed eigengrau | None |
| Cross-modal tone→colour | Auditory-visual | Eigengrau + tone | Speaker |
| vEAR elaboration | Visual-transformative | Afterimage | Brief flash stimulus |
| Chills/tingling | Somatic | Auditory trigger or direct | Optional speaker |

Would capture: general factor (motor pair) + visual perceptual (eigengrau/vEAR) +
cross-modal binding (Nair & Brang) + somatic/ASMR channel.
No floor issues anticipated for any item. All have a substrate that reduces reliance
on effortful generation.

**Key references:**
- Barber, T.X., & Calverley, D.S. (1964). *J. Abnorm. Soc. Psychol.*, 68(1), 13–20.
- Merckelbach, H., & van de Ven, V. (2001). *J. Behav. Ther. Exp. Psychiat.*, 32(3), 137–144.
- Nair, A., & Brang, D. (2019). Inducing synesthesia in non-synesthetes: Short-term
  visual deprivation facilitates auditory-evoked visual percepts. *Consciousness and
  Cognition*, 70, 70–79. https://doi.org/10.1016/j.concog.2019.02.006
- Dijkstra, N., Bosch, S.E., & van Gerven, M.A.J. (2021). Perceptual reality monitoring.
  *Trends Cogn. Sci.* (and related MEG/fMRI work).
- Reeder, R.R. (2024). A novel model of divergent predictive perception. *Neurosci.
  Biobehav. Rev.* https://doi.org/10.1093/nc/niae011 (verify journal/year).
- Clark, A. (2013). Whatever next? *Behav. Brain Sci.*, 36(3), 181–204.
- Clark, A. (2015). *Surfing Uncertainty.* Oxford University Press.
- Clark, A. (2023). *The Experience Machine.* W.W. Norton.
- Weaver, W. (n.d.). Something about phosphenes. blog.phenomenal.ink
- Weaver, W. (n.d.). Veil of perception. blog.phenomenal.ink

---

## 7. Individual differences measures: PsiQ as alternative/supplement to VVIQ

VVIQ (Marks 1973) has two limitations for this context:
1. **Volitional only** — measures deliberate imagery vividness; does not capture
   spontaneous/intrusive imagery, which is closer to what hallucination items require.
2. **Visual only** — single modality; misses auditory, somatic, gustatory imagery
   relevant to the items above.

**PsiQ (Phenomenological Sensitivity / Perceptual Sensitivity Questionnaire)** —
note: verify which specific scale is intended; candidates include:
- Reeder's **Perceptual Imagination Scale** / Phenomenological Imagery measures
  (multi-modal, includes spontaneous dimension)
- The **Psi-Q** (parapsychology; measures anomalous perceptual experiences,
  feelings of presence, etc. — correlates with hallucination proneness and
  reduced reality monitoring)
- The **Questionnaire on Mental Imagery (QMI)** / Betts — multi-modal including
  auditory, tactile, kinaesthetic, gustatory

For the revised scale's validation purposes, the ideal individual differences battery:

| Measure | What it adds over VVIQ |
|---------|------------------------|
| VVIQ | Baseline volitional visual imagery vividness |
| PsiQ / Perceptual Sensitivity | Spontaneous/anomalous perceptual experiences; non-volitional channel |
| OSIVQ or QMI | Multi-modal (auditory, somatic, gustatory) coverage |
| ASMR proneness (AEQ) | Somatic cross-modal sensitivity directly relevant to chills item |
| Aphantasia/hyperphantasia self-report | Extreme ends of Reeder spectrum; controls ceiling/floor in imagery measures |

**Prediction:** PsiQ should predict the new perceptual items more strongly than VVIQ
because it captures the involuntary/spontaneous dimension — the hallucination items
require passive discovery, not active generation. VVIQ will still predict the
deliberate imagination required by the White Christmas/noise paradigm versions.
The two measures might dissociate cleanly across item types.

---

## 8. Open questions for future work

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
8. Does the cross-modal (Nair & Brang) item show stronger PsiQ/VVIQ correlation than
   the unimodal auditory item under equivalent deprivation? Would distinguish
   imagery-vividness sensitivity from general hallucinability.
9. Does the eigengrau positive-visual item correlate with phosphene proneness
   (from blog survey) and with the neg-visual spike profile (P2)?
10. Does PsiQ dissociate from VVIQ in predicting volitional-substrate items
    (noise paradigm) vs. discovery-oriented items (eigengrau, chills)?
11. Run ASMR questionnaire (AEQ) × PCS item correlations — the dataset was in the
    repo but correlations were never computed. Recover and run.

---

## 9. Cognitive challenge item: naming inhibition as amnesia replacement/supplement

**The existing amnesia item:**
- Floor rate: ~27% (PCS/SWASH); moderate, not extreme.
- Requires post-procedure administration — cannot be embedded anywhere in a standalone
  short form. Participant must try to recall items from the earlier suggestions.
- The *experience* rated is trying-and-failing to remember, which is ambiguous
  (genuine blocking vs. simply forgetting vs. inattention).
- Practical problem (IME): a significant proportion of participants are simply confused
  by the instruction — they are unsure whether they are supposed to try to remember,
  not try, or report the experience of trying. The naming inhibition version removes
  this ambiguity: there is a single visible object, one unambiguous task (name it),
  and the experience is the felt resistance to doing so.

**Proposed replacement: naming inhibition (scissors paradigm)**
Suggestion: "When you look at this object [show scissors/picture], the word for it
will not come to mind. The more you try to name it, the more the word stays out of
reach." Rate blocking 0–5.

- No post-procedure dependency — testable immediately after suggestion
- Clear behavioral criterion (named it / hesitated / did not name it) + graded
  subjective experience of blocking
- Direct analogue of HGSHS:A item 8 (Communication inhibition / aphasia suggestion),
  which is also in our data (LABELS_HGSHS)
- Floor rates expected lower than amnesia: naming a highly familiar object is easy,
  so the *failure* to name it is a cleaner signal than failing to recall a list

**Mechanism under predictive processing:**
Naming inhibition is a top-down executive suppression of a motor/phonological output
pathway. The suggestion primes a "blocked" prior that competes with the automatic
retrieval pathway. Different from perceptual hallucination (adding signal) and motor
challenge (inhibiting movement completion) — a fourth modality adding
cognitive/executive variance.

This is the cognitive analogue of negative visual hallucination (suppressing a
perception rather than adding one). Both involve suggestion-driven inhibition rather
than generation.

---

## 10. Item-by-item problems and replacements

Floor rates across five datasets (mean across PCS norms, SWASH norms, PCS-VVIQ,
SWASH-val, vEAR PCS):

| Item | Type | Mean floor | Problem |
|------|------|-----------|---------|
| Neg. visual hallucination | perceptual | 90% | High sensory confidence; negative suggestion hard to detect |
| Music hallucination | perceptual | 85% | High sensory confidence; rare in normal acoustic env. |
| Post-hypnotic suggestion | cognitive | 65% | Two-stage structure; requires specific post-session event |
| Mosquito hallucination | perceptual | 43% | Multi-modal collapse (presence/touch/auditory); unclear criterion |
| Amnesia | cognitive | 29% | Post-procedure dependency; instruction routinely misunderstood |
| Taste hallucination | perceptual | 25% | Acceptable; already sub-rated (sweet/sour); VVIQ r=0.242 |

Items below 15% floor (motor items) are fine as-is.

---

### Neg. visual hallucination (90% floor)
Asks participant to fail to see something in a clear, structured visual field. Two
structural problems: (1) high sensory confidence — the external signal is real and
strong, so the suggestion must suppress a genuine percept; (2) the "pass" criterion
requires recording exactly two ball colours, which depends on attending to the test
rather than the experience. Replace with a **positive visual suggestion under reduced
sensory confidence** (eigengrau, see §6).

---

### Music hallucination (85% floor)
Pure auditory generative suggestion in a quiet room. Sensory confidence for "silence"
is high; there is nothing for the suggestion to ride. The objective criterion (raise
hand when you hear music) is actually clean — it's the environmental conditions that
fail. Fix: low-level acoustic substrate (broadband noise, or a tonally ambiguous drone)
delivered before the suggestion. Alternatively fold into the cross-modal item (§6,
Nair & Brang approach: eyes closed + substrate → music/colour experience).

---

### Post-hypnotic suggestion (65% floor)
Structurally broken for any standalone or short form. Requires: (1) a specific cue
(spacebar press) to be delivered after the session ends, (2) participant to recall that
they are supposed to do it, (3) the experimenter to trigger it. In online/remote
administration the logistics are even worse. The underlying construct (response to a
post-hoc cue) is valid but the delivery mechanism is fragile.

Replacement options:
- **Deferred naming task**: earlier in the session, suggest "later you will be asked a
  question and the word will come easily / not come at all." Test at session end.
  Simpler logistics than the spacebar paradigm, no external equipment needed.
- **Ideomotor cue response**: suggest that hearing a specific word or tone later will
  trigger an involuntary movement (finger lift, hand turn). Test within-session.
  Collapses latency with the motor items structurally.

---

### Mosquito hallucination (43% floor) — best replaced

**The multi-modal collapse problem.** The suggestion can produce three
qualitatively distinct experiences: (a) sense of presence near the skin, (b) tactile
sensation (itch, crawl, bite, tickle), (c) auditory hallucination (buzzing). The
objective criterion — "an outward acknowledgment of the effect" (any behavioural
response: swatting, flinching, scratching) — accepts all three equally. The subjective
0–5 rating is a single undifferentiated number with no modal decomposition.

Practically: participants who feel an itch but hear nothing wonder if it "counts."
Participants who get a strong presence without touch or sound don't know what to
rate. The 43% floor likely includes people who had a partial experience in one
modality but not the expected one.

The taste item handles this correctly: sweet and sour sub-rated separately, combined
as mean. The mosquito item gives no such guidance.

**Best replacement: a discrete, unambiguous unimodal tactile item.**

Candidate: **Localised itch/tingling suggestion** — suggest a specific, localised
sensation at a named body location (e.g., left forearm, tip of index finger). Single
modality (somatosensory), no ambiguity about what to attend to, no acoustic substrate
needed, naturally discrete.

- "As I count down, you will begin to notice a tingling sensation at the tip of your
  left index finger. The sensation will build with each count."
- Rate 0–5: no sensation → faint tingling → clear tingling → spreading/warming →
  strong persistent sensation.

This is phenomenologically cleaner than mosquito (no presence/auditory confusion),
has a natural 0–5 gradient, and as a somatic item adds a distinct modality not
covered by motor challenge (which is proprioceptive/kinaesthetic). The chills/ASMR
item (§6) is a related but autonomic/full-body version — this localised itch would
be a lower-intensity, more controllable variant suitable for unselected samples.

---

### Amnesia (29% floor)
Fixable via replacement with naming inhibition (§9). Instruction confusion alone
probably accounts for a meaningful fraction of the floor.

---

### Updated full screener (exploratory, revised PCS-style)

Proposed item set replacing or improving all floored items while preserving the
validated motor pair and taste:

| # | Item | Modality | Replaces | Floor expected | Equipment |
|---|------|----------|----------|----------------|-----------|
| 1 | Hand lowering | Motor ideomotor | — (keep) | ~4% | None |
| 2 | Moving hands together | Motor ideomotor | — (keep) | ~6% | None |
| 3 | Localised tingling (finger) | Tactile/somatic | Mosquito | Low | None |
| 4 | Taste hallucination | Gustatory | — (keep) | ~25% | None |
| 5 | Arm rigidity | Motor challenge | — (keep) | ~8% | None |
| 6 | Arm immobilisation | Motor challenge | — (keep) | ~13% | None |
| 7 | Eigengrau visual / cross-modal | Visual (+ auditory) | Music + Neg. visual | Low | Speaker optional |
| 8 | Naming inhibition | Cognitive executive | Amnesia | Low | Picture card |
| 9 | Chills/ASMR | Somatic autonomic | Post-hypnotic | Low | Optional |
| 10 | vEAR elaboration | Visual transformative | — (new) | Low | Brief flash |

Motor pair (#5, #6) preserved as the two-item short form. All floor items replaced
with lower-floor alternatives grounded in sensory-confidence framework. Three new
modalities added: tactile-localised, somatic-autonomic, visual-transformative.

Note: this is a theoretical proposal, not a validated scale. Ordering, phrasing,
and combination would need piloting before any psychometric claims.

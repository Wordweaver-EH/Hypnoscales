# GROUND_TRUTH.md — Verified Analysis Constants

Each entry is sourced; code and doc must stay in sync. If a value here conflicts with the
notebook, the notebook is wrong. Last verified: 2026-06-03.

---

## 1. Canonical scoring (PCS / SWASH)

Source: `osf/pcs_vviq/preprocdata.Rmd` (authors' preprocessing script) + PCS scoring guide.

```python
PHS_subjective   = sqrt(urge * amnesia)     # geometric mean, 2-item form
                                             # Use sqrt(), NOT log() — log(0) = -inf
                                             # sqrt(0 * x) = 0, which is correct:
                                             # PHS fails if either component is zero
Taste_subjective = mean(sweet, sour)
Total_subjective = mean([item1..item8, Taste_subjective, PHS_subjective])
                                             # 10-item mean; Taste and PHS each count once
```

**df1, df3, df5**: use author-precomputed totals (verified: r=1.000 / 0.999 with item mean).
**df2**: no precomputed total — recompute canonically above, then validate (see §5).
**df4**: no subjective-intensity ratings exist in HGSHS:A — never compute a "total" on the
         intensity model for df4.

---

## 2. Condition coding for df1

Source: matched against PCS-norms paper (Lush et al. 2021, *Collabra*) on three stats.

```
Condition 0 = PCS  : subj_mean=1.933, obj_mean=4.066, pct_low=4.1%   n=244
Condition 1 = SWASH: subj_mean=1.527, obj_mean=3.442, pct_low=14.2%  n=240
```

PROVEN — not inferred. Code must filter `df1[df1.Condition == 0]` for PCS,
`df1[df1.Condition == 1]` for SWASH. Never pool.

---

## 3. Exclusion flags

Source: column names verified in each raw file.

```
df1  exclude            == 1  → drop  (6 rows)
df2  (no exclusion column present)
df3  (no exclusion column present)
df4  Missing            == 1  → drop  (18 rows; n: 602 → 584)
df5  Incomplete_exclude == 1  → drop  (62 rows; n: ~514 → 452)
```

Apply exclusions before any computation, including the df2 recompute.

---

## 4. Motor-pair column mapping

Source: df2/df5 confirmed from `osf/pcs_vviq/readme.txt` (authors' item-order list);
        df4 from `HGSHSA_key` sheet.

```
df1  ArmRigiditySubjectiveRating   + ArmImmobilisationSubjectiveRating
df3  Q5RIGIDITYSUBJ                + Q6IMMOBILESUBJ
df2  StiffArm (rigidity, raw col 6) + HandAndArmHeavy (immobilisation, raw col 7)
df5  StiffArm                       + HandAndArmHeavy          [same as df2]
df4  INV.6 (rigidity)               + INV.4 (immobilisation)
     objective: HGSHS.A6            + HGSHS.A4
```

**WARNING**: `HandBecomesHeavy` = item 1 (hand lowering) ≠ `HandAndArmHeavy` (item 6,
immobilisation). Confirmed from readme item order:
  1=hand lowering, 2=hands together, 3=mosquito, 4=sweet, 5=sour,
  **6=arm rigidity (StiffArm), 7=arm immobilisation (HandAndArmHeavy)**,
  8=music, 9=neg-visual, 10=amnesia, 11=urge(PHS), 12=amnesia(PHS).

Scale positions (10-item): rigidity=item5, immobilisation=item6 (SWASH/PCS);
                            rigidity=item6, immobilisation=item4 (HGSHS:A).

---

## 5. df2 canonical recompute — validation requirement

Source: `osf/pcs_vviq/readme.txt` (item list + scoring note).

The notebook used a 12-column arithmetic mean, over-weighting Taste (2 raw cols) and PHS
(2 raw cols). Canonical is the 10-item mean with geometric-mean PHS.

After recomputing, **validate against authors' anchors before trusting the motor correlation**:
- The readme confirms item order; cross-check that your 10-item mean matches the scale's
  expected mean direction (PCS non-hypnotic sample; higher mean than SWASH is documented).
- Part-whole (corrected): target ≈ 0.778; part-rest: target ≈ 0.549.

If your recomputed total produces a wildly different motor-vs-total r, the scoring is wrong.

---

## 6. df4 — confirmed constraints

Source: `HGSHSA_key` sheet in `osf/terhune/raw_data.xlsx`.

**Involuntariness scale**: Bowers (1991) Involuntariness Scale (BIS).
  Anchor: `0 = no experience` (separate "nothing happened" category),
           `1 = voluntary, 2, 3, 4, 5 = involuntary` (agency gradient, conditional on response).

**Implication**: zero aligns with the others' floor ("did not experience") but 1–5 is the
agency dimension, not intensity. df4 cannot join the intensity story. Report on both its
dimensions (objective pass/fail, involuntariness) in separate labelled rows — never pooled
with df1/2/3/5.

**df4 columns**:
- Objective:        `HGSHS.A1`–`HGSHS.A12` (0=fail, 1=pass; binary)
- Involuntariness:  `INV.1`–`INV.12`        (0–5, Bowers BIS)
- Amnesia special:  `HGSHS.A12PRE` (items remembered pre-cancellation),
                    `HGSHS.A12POST` (post-cancellation); `HGSHS.A12` = final pass/fail

Motor pair (objective):        `HGSHS.A6` (rigidity) + `HGSHS.A4` (immobilisation)
Motor pair (involuntariness):  `INV.6`    (rigidity) + `INV.4`    (immobilisation)

---

## 7. Total provenance per dataset

Source: verified empirically (item-mean vs precomputed, r-check).

```
df1  Subjective_scale_score_first_test  : AUTHOR precomputed  (r=1.000 vs item mean)
df3  Subjectivescore                    : AUTHOR precomputed  (r=0.999 vs item mean)
df5  PCscore                            : AUTHOR precomputed  (= mean of 10 PCS suggestions,
                                          per vEAR codebook)
df2  (none)                             : RECOMPUTE canonically (§1 above)
df4  (none applicable for intensity)   : objective sum = sum(HGSHS.A1..A12);
                                          INV total = mean(INV.1..INV.12)
```

---

## 8. Procedure metadata (record, do not gate)

Sanger & Pietras (PC Workshop 2026) found the PCS rating procedure changed across
2019–2025; edge patterns shifted (arm immobilisation migrated clusters). Because every
analysis here is **within a single dataset**, this does not contaminate any estimate.
Record the era for each dataset for the one-sentence limitation:

```
df1  PCS/SWASH norms paper: collection ~2019  → pre-2023 (end-of-session ratings)
df2  PCS-VVIQ: ~2022–2023                     → confirm from OSF date / methods
df3  SWASH paper: collection ~2017–2018       → pre-2023
df4  Terhune/Reshetnikov: ~2020–2021          → pre-2023
df5  vEAR PCS: ~2022                          → pre-2023 (likely)
```

If any dataset straddles the 2023 boundary, stratify and check immobilisation stability
(§5.3 of handoff). Otherwise one limitation sentence citing Sanger suffices.

---

## 9. 2-item reliability — correct coefficient

Source: Eisinga, te Grotenhuis & Pelzer (2013).

For k=2 items, standardized Cronbach's α = Spearman-Brown = 2r/(1+r).
Report **inter-item r** and the **implied 2-item reliability (2r/(1+r))** once per dataset.
Do NOT present raw alpha and SB as independent corroboration — they are the same number.

---

## 10. Two metrics — report both

Source: Girard & Christensen (2008); Riegel (2021); Zech (2024).

**Full-scale r (part-whole)** — motor pair vs full total including the two motor items.
Inflated by construction but genre-standard: HGSHS-5:G (r=0.83, Riegel 2021), Zech (R²=0.69)
use the same design and passed peer review. Report with explicit overlap disclosure:
"The motor items are components of the full total."
Computed values: r=0.78–0.85, R²=0.60–0.72 across all five datasets.

**Part-rest r (overlap-free)** — motor pair vs 8-item rest score (total minus motor pair).
Conservative, non-circular estimate of shared variance. Cite Girard & Christensen (2008).
Computed values: r=0.55–0.69 across all five datasets.

Rest score = mean([all items] \ {rigidity, immobilisation})

The 8-item rest score is also the criterion for the primary classification analysis (§5.4),
so it must be emitted as a column by analysis.ipynb and any analysis.py.

---

*End of GROUND_TRUTH.md*

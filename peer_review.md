# Peer Review — "Two motor-challenge items as a cross-context suggestibility screener"

**Reviewer:** Computational re-analysis of all code and data  
**Date:** 2026-06-04  
**Status:** All issues addressed. See revision log below.

---

## Reproduction

The complete pipeline was re-executed independently. All primary statistics reproduce exactly. Bootstrap CIs were recomputed at the final setting of $n_{\text{boot}} = 5000$ (previously at draft setting of 2000; CIs shifted by ≤0.003 at the third decimal place).

---

## Issues identified and resolved

### 1. Selective reporting in all-pairs analysis ✅ Fixed

The original text reported the motor pair's $r_{\text{full}}$ rank for four of five datasets, omitting the SWASH validation sample (rank 13/45). The $r_{\text{rest}}$ sentence in the same paragraph listed all five. This asymmetry has been corrected: the all-pairs text now reads:

> "By $r_{\text{full}}$, the motor pair ranks first or second in all three PCS datasets and fourth in the Norms-SWASH dataset; in the SWASH validation dataset it ranks 13th, where the top pair is taste + arm rigidity ($r_{\text{full}} = 0.845$)."

### 2. Three unverifiable conference citations ✅ Fixed

References `sanger2026network`, `toussant2026interoceptive`, and `fine2026synaesthesia` were conference presentations from the date of writing, flagged in the `.bib` file as requiring verification before submission. They have been removed from both the paper and `references.bib`. The floor-mechanism sentences they supported have been rewritten to rely on the paper's own item descriptives (which fully establish the claim) and the published bifactor analysis \citep{zahedi2022bifactor}. Also removed: `reshetnikov2022hgshs` (not cited in text, contained unresolved verification flag) and `aslanov2026coldcontrol` (not cited in text, same conference).

### 3. Dataset labels were code variable names ✅ Fixed

All occurrences of `df1`, `df2`, `df3`, `df4`, `df5` have been replaced throughout the paper (prose, all three tables, Open Science Statement) with reader-facing names:

| Old label | New label |
|---|---|
| df1 PCS | Norms-PCS |
| df1 SWASH | Norms-SWASH |
| df2 | PCS-VVIQ |
| df3 | SWASH-val |
| df4 | HGSHS:A |
| df5 vEAR | vEAR-PCS |

### 4. Raw column names listed as code variable names ✅ Fixed

The Scoring section retained the column-name mapping (useful for reproducibility) but the header was changed from "Column names across files: df1, ..." to "Source column names: Norms sample: ..." using the new sample labels.

### 5. Exclusion flags written as code syntax ✅ Fixed

`df1 (\texttt{exclude=1}, n=6)` etc. rewritten as plain prose:  
"Dataset-provided exclusion variables were applied, removing $n = 6$ participants from the Norms sample, $n = 18$ from the HGSHS:A sample, and $n = 62$ from the vEAR-PCS sample."

### 6. Undocumented df3 exclusion ✅ Fixed

The SWASH validation sample drop (495→418) was filtered on missingness of the first-test score, not a named exclusion flag. This is now documented: "The SWASH validation sample was additionally restricted to participants with non-missing first-test scores ($n = 77$ excluded)."

### 7. "Documented in the robustness checks" ✅ Fixed

Changed to "documented in the Robustness subsection."

### 8. Bootstrap not at intended final setting ✅ Fixed

`lib_data.py`: `N_BOOT = 2000` (with draft comment) → `N_BOOT = 5000`. All analyses rerun. Table 2 CIs updated to reflect the new values (changes ≤0.003 at 3 d.p.). Methods text updated to $n_{\text{boot}} = 5000$.

### 9. df5 raw N reported as approximate ✅ Fixed

`\approx 514` → `514` (confirmed from raw data file: 514 rows).

### 10. [repository URL] placeholder ✅ Updated

Changed to "[GitHub/OSF repository; URL to be inserted before submission]" — more informative placeholder.

### 11. Open Science Statement used code labels ✅ Fixed

"df1 osf.io/et85n, df2 osf.io/aeyhw..." rewritten as:  
"Norms sample: osf.io/et85n; PCS-VVIQ sample: osf.io/aeyhw; ..."

---

## Remaining open items (require author action)

| Item | Status |
|---|---|
| `[GitHub/OSF repository; URL to be inserted before submission]` — code repository link | Author to add before submission |
| `[To be completed at submission.]` — CRediT authorship | Author to complete |
| Zech (2024) — cited as "In press"; verify $\kappa = 0.578$ comes from $N = 1{,}963$ (Riegel 2021) or $N = 2{,}529$ (Zech 2024 cross-study validation) and update table note accordingly | Author to verify |

---

## What was not changed

- All reported statistics are correct and exactly reproduced by the pipeline.
- The Discussion avoids overclaiming; limitations (embedded administration, unknown standalone retest, sample-dependence of floor effects) are appropriately acknowledged.
- The dual reporting of $r_{\text{full}}$ and $r_{\text{rest}}$ throughout is retained — this is the correct design for this application.

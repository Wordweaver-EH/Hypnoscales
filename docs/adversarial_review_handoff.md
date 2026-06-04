# Adversarial Review Handoff

**Date:** 2026-06-04

**Purpose:** Convert the adversarial review findings into an implementation-ready fix plan for the Hypnoscales analysis repo.

**Important constraint:** `osf/GROUND_TRUTH.md` was a development artifact. Do not reinstate it. Treat the current absence of that file as intentional, and fix stale references by moving only durable provenance into tracked source comments or public documentation.

---

## Current State

This repo is a script-and-artifact research analysis project. Core analysis scripts live in `analysis/`, generated tables live in `tables/`, figures live in `figures/`, and the manuscript plus public docs consume those outputs.

The adversarial review found no evidence that the loaded core datasets currently have missing motor-item rows after the existing exclusions. The main issues are reproducibility, classification semantics, stale provenance, and incomplete confidence interval handling in exploratory retest output.

## Fix Priorities

### 1. Fix classification semantics for tied, discrete scores

**Problem:** `analysis/a04_classification.py` describes tertiles and top-third screening, but the implementation uses percentile thresholds with strict `>` comparisons. Because the motor composite is a discrete 0-10 score, ties make the predicted high group much smaller than the named cutoff in several datasets. For example, generated output currently shows df2 PCS-VVIQ high motor count as 112/508 and df5 vEAR PCS as 104/452 for the three-group full-total rows.

**Files to modify:**
- `analysis/a04_classification.py`
- `analysis/a08_figures.py`
- `analysis.ipynb`
- `preprint.tex`
- `README.md`
- `docs/analysis_explainer.html`

**Implementation decision to make explicit:**
Use one of these policies and document it everywhere:

1. **Threshold policy:** Keep strict score thresholds and stop calling the groups exact tertiles/top-third. Report actual selected proportions beside every cutoff.
2. **Rank policy:** Force exactly the requested proportion by rank ordering, with deterministic tie handling. This is closer to "top third" but less clinically natural for a tied screening score.

**Recommended policy:** Threshold policy. It reflects how a two-item screener would actually be used: a score cutoff such as `> 7` or `> 8`, not random tie-breaking.

**Required code changes:**
- Rename helper language from `tertile_groups` to threshold-based grouping, or add docstrings that state ties are assigned below the boundary.
- Add columns to `tables/table_classification.csv` for actual motor and criterion proportions:
  - `pct_low_motor`
  - `pct_mid_motor`
  - `pct_high_motor`
  - `pct_low_crit`
  - `pct_mid_crit`
  - `pct_high_crit`
  - `n_pred_high` for binary rows
  - `pct_pred_high` for binary rows
- Update binary output so every cutoff row reports both requested cutoff and realized selected proportion.
- Update figure captions and manuscript copy to avoid implying exact top-third prediction where ties reduce the selected motor group.

**Acceptance checks:**
- `python analysis/a04_classification.py` exits 0.
- `tables/table_classification.csv` contains realized proportion columns.
- For df2 PCS-VVIQ and df5 vEAR PCS, the table makes clear that the motor high group is below one third under the threshold policy.
- `preprint.tex` no longer says "top-third" without a tie/threshold qualifier.

### 2. Fix root-level reproducibility commands

**Problem:** `README.md` instructs users to run `python a01_descriptives.py` from the repo root, but scripts are stored under `analysis/`. Running the command from `C:\Hypnoscales` fails because `a01_descriptives.py` is not at the root.

**Files to modify:**
- `README.md`
- Optional: create `run_pipeline.py` at repo root

**Recommended fix:**
Create a root-level `run_pipeline.py` that runs the pipeline in dependency order, then update README to offer both full-pipeline and individual-script commands.

**Pipeline order:**
1. `analysis/a01_descriptives.py`
2. `analysis/a02_convergence.py`
3. `analysis/a03_retest.py`
4. `analysis/a04_classification.py`
5. `analysis/a05_all_pairs.py`
6. `analysis/a06_external.py`
7. `analysis/a07_sensitivity.py`
8. `analysis/a08_figures.py`
9. Optional exploratory scripts: `analysis/a09_eda.py`, `analysis/a10_eda2.py`

**Acceptance checks:**
- `python run_pipeline.py` exits 0, if the runner is added.
- `python analysis/a01_descriptives.py` exits 0 from the repo root.
- README no longer lists root-missing commands such as `python a01_descriptives.py`.

### 3. Fix notebook import path

**Problem:** `analysis.ipynb` says its only external dependency is `analysis/lib_data.py`, but the setup cell imports `from lib_data import ...`. From the repo root, `import lib_data` fails.

**Files to modify:**
- `analysis.ipynb`

**Recommended fix:**
Add this before the `from lib_data import ...` statement in the setup cell:

```python
import sys
from pathlib import Path

ROOT = Path.cwd()
ANALYSIS_DIR = ROOT / "analysis"
if str(ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSIS_DIR))
```

If the notebook may be opened from inside `analysis/`, make the root detection robust:

```python
cwd = Path.cwd()
ROOT = cwd if (cwd / "analysis" / "lib_data.py").exists() else cwd.parent
ANALYSIS_DIR = ROOT / "analysis"
```

**Acceptance checks:**
- From repo root, `python -c "import sys; sys.path.insert(0, 'analysis'); import lib_data; print(lib_data.ROOT_DIR)"` exits 0.
- The first notebook code cell can be run from a Jupyter session launched at the repo root.

### 4. Fix bootstrap CI handling for constant resamples

**Problem:** `analysis/lib_data.py` bootstraps Pearson correlations directly. For low-variance items, some bootstrap resamples are constant, so `pearsonr` returns `nan`. Those NaNs propagate into blank CIs in `tables/table_eda2_retest.csv` for music and negative visual hallucination retest rows.

**Files to modify:**
- `analysis/lib_data.py`
- `analysis/a10_eda2.py`
- `docs/analysis_explainer.html`
- `docs/eda_notes.md`, if it cites those exploratory CIs

**Recommended fix:**
In `bootstrap_ci`, skip bootstrap draws where either resampled vector is constant. Track how many valid draws remain. If valid draws fall below a clear minimum, return `(np.nan, np.nan)` and let caller mark the CI as unavailable because the bootstrap distribution is degenerate.

**Reporting requirement:**
If a CI is unavailable, write `ci_note` or equivalent in exploratory tables rather than leaving empty CSV cells with no explanation.

**Acceptance checks:**
- `python analysis/a10_eda2.py` exits 0.
- `tables/table_eda2_retest.csv` does not contain unexplained blank `ci_lo`/`ci_hi` cells.
- Public docs explain that floor-heavy items can have degenerate bootstrap CIs.

### 5. Remove stale `GROUND_TRUTH.md` dependency without reinstating it

**Problem:** `analysis/lib_data.py` currently cites `osf/GROUND_TRUTH.md` as the motor-pair mapping source. That file is intentionally absent and should not be recreated.

**Files to modify:**
- `analysis/lib_data.py`
- Optional: `README.md`
- Optional: `docs/analysis_explainer.html`

**Required behavior:**
- Do not add `osf/GROUND_TRUTH.md`.
- Remove the stale citation from `analysis/lib_data.py`.
- Replace it with a short durable comment that explains the mapping in terms of the tracked source data and public scale item names.

**Suggested replacement comment:**

```python
# Motor-pair mapping uses the arm rigidity and arm immobilisation subjective
# items for PCS/SWASH-style datasets, and the corresponding rigidity/
# immobilisation items for HGSHS:A involuntariness/objective scoring.
```

If more detail is needed, put it in public-facing documentation, not in a resurrected dev artifact.

**Acceptance checks:**
- `rg -n "GROUND_TRUTH" .` returns no matches.
- `rg --files | rg "GROUND_TRUTH"` returns no matches.
- `git status --short` does not show a new `osf/GROUND_TRUTH.md`.

### 6. Regenerate and reconcile artifacts

**Problem:** Tables, figures, docs, notebook, and manuscript are tightly coupled. After code fixes, stale generated outputs can preserve old claims.

**Files likely to change:**
- `tables/table_classification.csv`
- `tables/table_eda2_retest.csv`
- `figures/fig4_roc_primary.png`
- `figures/fig_eda2.png`
- `preprint.tex`
- `preprint.pdf`, if compiling locally
- `docs/analysis_explainer.html`
- `README.md`
- `analysis.ipynb`

**Acceptance checks:**
- Run the full core pipeline from the repo root.
- Rebuild exploratory EDA only if the EDA tables/figures are kept in scope.
- Recompile `preprint.pdf` if manuscript text or tables change.
- Search for stale language:

```powershell
rg -n "top-third|tertile|GROUND_TRUTH|python a01_|python a02_|python a08_|blank CI|retained 71|80" README.md preprint.tex docs analysis.ipynb
```

Review every hit and confirm it is still accurate.

## Suggested Test Coverage

There is currently no test suite. Add small tests before changing classification and bootstrap behavior.

**Create:** `tests/test_classification_thresholds.py`

Test cases:
- A tied discrete motor vector produces realized high proportions that may differ from requested cutoff.
- The output helper reports `n_pred_high` and `pct_pred_high`.
- The full-total criterion and motor prediction use the same documented tie policy.

**Create:** `tests/test_bootstrap_ci.py`

Test cases:
- Normal continuous vectors return finite CI bounds.
- Low-variance vectors with some constant resamples do not crash.
- Fully constant vectors return unavailable CI bounds plus a clear note or sentinel.

**Acceptance command:**

```powershell
pytest tests -v
```

If adding pytest is too much for this repo, create `analysis/validation_checks.py` with explicit assertions and document:

```powershell
python analysis/validation_checks.py
```

## Final QA Checklist

- [ ] README commands work from `C:\Hypnoscales`.
- [ ] Notebook setup works from repo-root Jupyter.
- [ ] Classification tables report actual selected proportions under the chosen tie policy.
- [ ] Manuscript and docs no longer overstate exact top-third behavior.
- [ ] EDA retest CIs are either finite or explicitly marked unavailable with a reason.
- [ ] `GROUND_TRUTH.md` is not restored.
- [ ] `rg -n "GROUND_TRUTH" .` returns no matches.
- [ ] Generated tables and figures are updated after code changes.
- [ ] `git status --short` only shows intentional changes.

## Notes for the Implementer

The classification issue is the highest-risk scientific wording issue. Fix that before polishing docs. The `GROUND_TRUTH.md` issue is not a missing-file recovery task; it is a stale-reference cleanup task. Do not add private development notes back into `osf/` to make the old comment true.

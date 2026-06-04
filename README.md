# Two motor-challenge items as a candidate cross-context suggestibility screener

**W. Weaver**

Secondary reanalysis of five open datasets testing whether a two-item motor composite (arm rigidity + arm immobilisation) is a viable first-pass screener for hypnotic suggestibility across non-hypnotic (PCS), hypnotic (SWASH), and classic group-administered (HGSHS:A) contexts.

Preprint and full analysis pipeline: [github.com/Wordweaver-EH/Hypnoscales](https://github.com/Wordweaver-EH/Hypnoscales)

---

## Repository structure

```
├── preprint.tex / preprint.pdf   — manuscript (LaTeX source + compiled PDF)
├── references.bib                — bibliography
│
├── lib_data.py                   — shared data loading, scoring, and bootstrap CI functions
├── a01_descriptives.py           — item descriptives and floor rates
├── a02_convergence.py            — motor pair correlations (r_full, r_rest) across datasets
├── a03_retest.py                 — test-retest stability
├── a04_classification.py         — weighted κ, AUC, binary cutoff sweep
├── a05_all_pairs.py              — all 45 two-item combinations (PCS/SWASH samples)
├── a06_external.py               — external validity (vEAR, anomalous experiences, DES, flow)
├── a07_sensitivity.py            — sensitivity checks (z-scoring, listwise deletion)
├── a08_figures.py                — publication figures (Figures 1–5)
├── analysis.ipynb                — self-contained notebook reproducing the full pipeline
│
├── data/                         — raw dataset files (CSV/xlsx)
├── figures/                      — publication figures (PNG, 300 dpi)
├── tables/                       — computed output tables (CSV)
├── osf/                          — source OSF repositories (data + supplementary materials)
│
└── docs/                         — project web page and analysis explainer
```

## Reproducing the analysis

```bash
pip install numpy pandas scipy scikit-learn matplotlib openpyxl
python analysis/a01_descriptives.py
python analysis/a02_convergence.py
python analysis/a03_retest.py
python analysis/a04_classification.py
python analysis/a05_all_pairs.py
python analysis/a06_external.py
python analysis/a07_sensitivity.py
python analysis/a08_figures.py
```

Or open `analysis.ipynb` for the full inline narrative version.

## Source datasets

| Sample | Scale | OSF |
|--------|-------|-----|
| Norms (PCS + SWASH) | PCS / SWASH | [osf.io/et85n](https://osf.io/et85n) |
| PCS-VVIQ | PCS | [osf.io/aeyhw](https://osf.io/aeyhw) |
| SWASH validation | SWASH | [osf.io/wujk8](https://osf.io/wujk8) |
| HGSHS:A | HGSHS:A | [osf.io/jfmc4](https://osf.io/jfmc4) |
| vEAR-PCS | PCS | [osf.io/a2skp](https://osf.io/a2skp) |
| External criteria | — | [osf.io/u5wjy](https://osf.io/u5wjy) |

## Key findings

- Motor pair ranks first or second among all 45 two-item subsets in every PCS dataset; a motor item tops the best pair in every dataset including SWASH
- *r*_full = 0.78–0.85 (intensity and involuntariness scales), weighted κ = 0.50–0.65, AUC = 0.83–0.91
- Induction strengthens coupling: the randomised Norms split (same pool → PCS or SWASH) shows significantly higher motor-pair correlations under SWASH (*p* = .029, .018)
- Motor pair retains 71–80% of full-scale predictive signal against external criteria with no item overlap

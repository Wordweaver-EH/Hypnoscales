"""
a04_classification.py --  Classification / screening performance.

Design matches Zech et al. (2024) HGSHS-5:G benchmark:
  Three ordered groups (low / medium / high) using tertile boundaries
  on each scale independently. Weighted kappa (linear) across all three
  ordered categories. n=1,963 in Zech; our n=240-- 508.

Primary: criterion = full-scale total (genre-standard, directly comparable
         to HGSHS-5:G kappa=0.578).
Secondary (sensitivity): criterion = rest score (overlap-free per Girard &
         Christensen 2008) --  reported as conservative complement, NOT as
         the benchmark comparison.

Binary classification (top-% screen) retained as supplementary ROC/AUC.

Benchmark: HGSHS-5:G weighted kappa = 0.578 (Zech et al. 2024, N=1,963).

Outputs:
  tables/table_classification.csv
"""

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix, roc_curve, auc
from lib_data import (TABLES_DIR, FIGURES_DIR, load_all, MOTOR_COLS, make_tables_dir)


# ---------------------------------------------------------------------------
# Three-group threshold classification — matches Zech 2024 design
# ---------------------------------------------------------------------------
# Groups are defined by strict score thresholds at the 33rd/67th percentile
# boundaries (scores > threshold). For discrete motor composites this means
# the realised high group is often smaller than one third of the sample
# (e.g. 22–28% rather than 33%). Actual group sizes are reported alongside
# every κ estimate; do not describe the groups as exact tertiles.
# ---------------------------------------------------------------------------

def threshold_groups(scores):
    """Assign 0=low, 1=medium, 2=high using strict > thresholds at the
    33rd/67th percentile boundaries.  For discrete scores, the high group
    is typically smaller than one third of the sample.
    Returns (groups, lo_cut, hi_cut)."""
    lo = np.percentile(scores, 100 / 3)
    hi = np.percentile(scores, 200 / 3)
    groups = np.zeros(len(scores), dtype=int)
    groups[scores > lo] = 1
    groups[scores > hi] = 2
    return groups, lo, hi


# Keep old name as an alias so any external callers are not broken.
tertile_groups = threshold_groups


def three_group_kappa(motor, criterion):
    """Weighted (linear) and unweighted kappa for three-group threshold
    classification.  Reports actual group proportions alongside counts."""
    motor_g, m_lo, m_hi   = threshold_groups(motor)
    crit_g,  c_lo, c_hi   = threshold_groups(criterion)
    n = len(motor)
    kw = cohen_kappa_score(crit_g, motor_g, weights='linear')
    ku = cohen_kappa_score(crit_g, motor_g)
    cm = confusion_matrix(crit_g, motor_g, labels=[0, 1, 2])
    n_low  = int(np.sum(motor_g == 0))
    n_mid  = int(np.sum(motor_g == 1))
    n_high = int(np.sum(motor_g == 2))
    return {
        'kappa_weighted':   round(kw, 3),
        'kappa_unweighted': round(ku, 3),
        'confusion_matrix': cm,
        'motor_lo_cut':     round(m_lo, 3),
        'motor_hi_cut':     round(m_hi, 3),
        'crit_lo_cut':      round(c_lo, 3),
        'crit_hi_cut':      round(c_hi, 3),
        'n_low_motor':      n_low,
        'n_mid_motor':      n_mid,
        'n_high_motor':     n_high,
        'pct_low_motor':    round(n_low  / n, 3),
        'pct_mid_motor':    round(n_mid  / n, 3),
        'pct_high_motor':   round(n_high / n, 3),
        'n_low_crit':       int(np.sum(crit_g == 0)),
        'n_mid_crit':       int(np.sum(crit_g == 1)),
        'n_high_crit':      int(np.sum(crit_g == 2)),
        'pct_low_crit':     round(np.sum(crit_g == 0) / n, 3),
        'pct_mid_crit':     round(np.sum(crit_g == 1) / n, 3),
        'pct_high_crit':    round(np.sum(crit_g == 2) / n, 3),
    }


# ---------------------------------------------------------------------------
# Binary (top-%) classification --  for ROC/AUC and sensitivity/specificity
# ---------------------------------------------------------------------------

CUTOFFS = (0.08, 0.10, 0.12, 0.15, 0.20, 0.33)


def classify_binary(motor, criterion, pct):
    """Strictly-above threshold = high."""
    t_crit  = np.quantile(criterion, 1 - pct)
    t_motor = np.quantile(motor,     1 - pct)
    true_h  = (criterion > t_crit ).astype(int)
    pred_h  = (motor     > t_motor).astype(int)
    return true_h, pred_h


def binary_metrics(motor, criterion, label, criterion_label):
    rows = []
    for pct in CUTOFFS:
        th, ph = classify_binary(motor, criterion, pct)
        cm = confusion_matrix(th, ph)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
        else:
            tn = fp = fn = tp = np.nan
        kappa = cohen_kappa_score(th, ph)
        sens  = tp / (tp + fn) if (tp + fn) > 0 else np.nan
        spec  = tn / (tn + fp) if (tn + fp) > 0 else np.nan
        ppv   = tp / (tp + fp) if (tp + fp) > 0 else np.nan
        npv   = tn / (tn + fn) if (tn + fn) > 0 else np.nan
        n_pred_high = int(np.sum(ph))
        rows.append({
            'dataset':        label,
            'criterion':      criterion_label,
            'cutoff_pct':     f'{int(pct*100)}%',
            'n':              len(motor),
            'n_true_high':    int(np.sum(th)),
            'n_pred_high':    n_pred_high,
            'pct_pred_high':  round(n_pred_high / len(motor), 3),
            'kappa_binary':   round(kappa, 3),
            'sensitivity':    round(sens,  3),
            'specificity':    round(spec,  3),
            'PPV':            round(ppv,   3),
            'NPV':            round(npv,   3),
        })
    # ROC/AUC at top-33% (matches three-group high-group definition)
    th33, _ = classify_binary(motor, criterion, 0.33)
    fpr, tpr, _ = roc_curve(th33, motor)
    roc_auc = round(auc(fpr, tpr), 3)
    for r in rows:
        r['auc_top33'] = roc_auc
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    make_tables_dir()
    dfs = load_all()

    intensity_configs = [
        ('df1_pcs',   MOTOR_COLS['df1'],     'rest_score',     'Subjective_scale_score_first_test', 'df1 PCS'),
        ('df1_swash', MOTOR_COLS['df1'],     'rest_score',     'Subjective_scale_score_first_test', 'df1 SWASH'),
        ('df2',       MOTOR_COLS['df2'],     'rest_score',     'SubjectiveTotal',                   'df2 PCS-VVIQ'),
        ('df3',       MOTOR_COLS['df3'],     'rest_score',     'Subjectivescore',                   'df3 SWASH'),
        ('df5',       MOTOR_COLS['df5'],     'rest_score',     'PCscore',                           'df5 vEAR PCS'),
        # df4 HGSHS:A --  involuntariness dimension (Bowers 0-- 5 scale, same range as PCS/SWASH)
        ('df4',       MOTOR_COLS['df4_inv'], 'rest_score_inv', 'INV_total',                         'df4 HGSHS:A inv'),
        # df4 HGSHS:A --  objective binary (motor sum 0/1/2; coarser than inv)
        ('df4',       MOTOR_COLS['df4_obj'], 'rest_score_obj', 'OBJ_total',                         'df4 HGSHS:A obj'),
    ]

    # ---- Three-group weighted kappa (primary -- matches Zech 2024 design) ----
    print("PRIMARY CLASSIFICATION -- weighted kappa, three ordered groups")
    print("Matches Zech et al. (2024) HGSHS-5:G design: tertile low/medium/high")
    print("Benchmark: kappa_weighted = 0.578 (N=1,963)")
    print()

    main_rows = []
    for key, mc, rc, tc, label in intensity_configs:
        df    = dfs[key]
        motor = df[mc].sum(axis=1).dropna()
        total = df.loc[motor.index, tc].dropna()
        common = motor.index.intersection(total.index)
        m = motor.loc[common].values.astype(float)
        t = total.loc[common].values.astype(float)

        res = three_group_kappa(m, t)
        print(f"{label}  n={len(m)}")
        print(f"  kappa_weighted={res['kappa_weighted']}  kappa_unweighted={res['kappa_unweighted']}")
        print(f"  Motor thirds cut at {res['motor_lo_cut']:.1f} / {res['motor_hi_cut']:.1f}  "
              f"(n: {res['n_low_motor']} / {res['n_mid_motor']} / {res['n_high_motor']})")
        print(f"  Total thirds cut at {res['crit_lo_cut']:.2f} / {res['crit_hi_cut']:.2f}  "
              f"(n: {res['n_low_crit']} / {res['n_mid_crit']} / {res['n_high_crit']})")
        cm = res['confusion_matrix']
        print(f"  Confusion matrix (rows=true, cols=pred):")
        print(f"    {cm}")
        print()

        main_rows.append({
            'dataset':           label,
            'n':                 len(m),
            'criterion':         'full_total',
            'kappa_weighted':    res['kappa_weighted'],
            'kappa_unweighted':  res['kappa_unweighted'],
            'motor_lo_cut':      res['motor_lo_cut'],
            'motor_hi_cut':      res['motor_hi_cut'],
            'crit_lo_cut':       res['crit_lo_cut'],
            'crit_hi_cut':       res['crit_hi_cut'],
            'n_low_motor':       res['n_low_motor'],
            'n_mid_motor':       res['n_mid_motor'],
            'n_high_motor':      res['n_high_motor'],
            'pct_low_motor':     res['pct_low_motor'],
            'pct_mid_motor':     res['pct_mid_motor'],
            'pct_high_motor':    res['pct_high_motor'],
            'n_low_crit':        res['n_low_crit'],
            'n_mid_crit':        res['n_mid_crit'],
            'n_high_crit':       res['n_high_crit'],
            'pct_low_crit':      res['pct_low_crit'],
            'pct_mid_crit':      res['pct_mid_crit'],
            'pct_high_crit':     res['pct_high_crit'],
        })

    # ---- Secondary: rest-score criterion (overlap-free sensitivity check) ----
    print()
    print("SECONDARY --  rest-score criterion (overlap-free, sensitivity check)")
    print("Not directly comparable to HGSHS-5:G benchmark.")
    print()

    for key, mc, rc, tc, label in intensity_configs:
        df    = dfs[key]
        motor = df[mc].sum(axis=1).dropna()
        rest  = df.loc[motor.index, rc].dropna()
        common = motor.index.intersection(rest.index)
        m = motor.loc[common].values.astype(float)
        r = rest.loc[common].values.astype(float)

        res = three_group_kappa(m, r)
        print(f"{label}  kappa_weighted={res['kappa_weighted']}  kappa_unweighted={res['kappa_unweighted']}")

        main_rows.append({
            'dataset':           label,
            'n':                 len(m),
            'criterion':         'rest_score',
            'kappa_weighted':    res['kappa_weighted'],
            'kappa_unweighted':  res['kappa_unweighted'],
            'motor_lo_cut':      res['motor_lo_cut'],
            'motor_hi_cut':      res['motor_hi_cut'],
            'crit_lo_cut':       res['crit_lo_cut'],
            'crit_hi_cut':       res['crit_hi_cut'],
            'n_low_motor':       res['n_low_motor'],
            'n_mid_motor':       res['n_mid_motor'],
            'n_high_motor':      res['n_high_motor'],
            'pct_low_motor':     res['pct_low_motor'],
            'pct_mid_motor':     res['pct_mid_motor'],
            'pct_high_motor':    res['pct_high_motor'],
            'n_low_crit':        res['n_low_crit'],
            'n_mid_crit':        res['n_mid_crit'],
            'n_high_crit':       res['n_high_crit'],
            'pct_low_crit':      res['pct_low_crit'],
            'pct_mid_crit':      res['pct_mid_crit'],
            'pct_high_crit':     res['pct_high_crit'],
        })

    # ---- Binary classification for ROC/AUC (supplementary) ----
    print()
    print("SUPPLEMENTARY --  binary (top-33%) classification, ROC/AUC")
    print()

    binary_rows = []
    for key, mc, rc, tc, label in intensity_configs:
        df    = dfs[key]
        motor = df[mc].sum(axis=1).dropna()
        total = df.loc[motor.index, tc].dropna()
        common = motor.index.intersection(total.index)
        m = motor.loc[common].values.astype(float)
        t = total.loc[common].values.astype(float)
        br = binary_metrics(m, t, label, 'full_total')
        binary_rows.append(br)
        row33 = br[br['cutoff_pct'] == '33%'].iloc[0]
        print(f"{label}  AUC(top-33%)={row33['auc_top33']}  "
              f"kappa_binary={row33['kappa_binary']}  "
              f"sens={row33['sensitivity']}  spec={row33['specificity']}")

    # Save
    kappa_df  = pd.DataFrame(main_rows)
    binary_df = pd.concat(binary_rows, ignore_index=True)
    out = pd.concat([kappa_df.assign(analysis='three_group'),
                     binary_df.assign(analysis='binary')],
                    ignore_index=True)
    out.to_csv(f'{TABLES_DIR}/table_classification.csv', index=False)
    print()
    print("Saved: tables/table_classification.csv")


if __name__ == '__main__':
    main()

"""
a03_retest.py — Test-retest reliability analyses.

Two sources of retest data:
  1. PCS norms retest file (n=123, full T1+T2 item data, PCS+SWASH split)
  2. df3 SWASH: T1 items available, T2 total only (Subjectivereturnscore, n=66)

Key question: Is the 2-item motor score nearly as temporally stable as the full scale?

Outputs:
  tables/table_test_retest.csv
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from lib_data import (load_all, load_retest, MOTOR_COLS, ITEMS_DF1, ITEMS_DF3,
                      spearman_brown, bootstrap_ci, N_BOOT, make_tables_dir)

# PCS norms retest — T2 column name mapping
# T1 columns: standard names (ArmRigiditySubjectiveRating, etc.)
# T2 columns: suffix _69 (rigidity) _70 (immobilisation)
RETEST_MOTOR_T2 = ['ArmRigiditySubjectiveRating_69', 'ArmImmobilisationSubjectiveRating_70']
RETEST_TOTAL_T1 = 'TotalSubjectiveScore'   # sum of 10 items
RETEST_TOTAL_T2 = 'TotalSubjectiveScore_75'
# Convert to mean-per-item (same 0–5 scale as PCS items)
# TotalSubjectiveScore = sum of 10 items → divide by 10 for mean
# Equivalently: FIRSTSUBJECTIVE/5 and RTsubj/5 are already mean-per-item


def retest_row(x_t1, x_t2, label_x, label_y, dataset, n_boot=N_BOOT):
    """Single retest correlation row with Pearson, Spearman, bootstrap CI."""
    xa = np.asarray(x_t1, dtype=float)
    ya = np.asarray(x_t2, dtype=float)
    mask = np.isfinite(xa) & np.isfinite(ya)
    xa, ya = xa[mask], ya[mask]
    n = len(xa)
    if n < 10:
        return None
    rp, p  = pearsonr(xa, ya)
    rs, _  = spearmanr(xa, ya)
    ci_lo, ci_hi = bootstrap_ci(xa, ya, 'pearson', n_boot=n_boot)
    return {
        'dataset':    dataset,
        'T1_var':     label_x,
        'T2_var':     label_y,
        'n':          n,
        'pearson_r':  round(rp,    3),
        'p_value':    float(p),
        'spearman_r': round(rs,    3),
        'ci_lo':      round(ci_lo, 3),
        'ci_hi':      round(ci_hi, 3),
        'r2':         round(rp**2, 3),
    }


def main():
    make_tables_dir()
    dfs = load_all()
    rt_pcs, rt_swash = load_retest()

    rows = []

    # ── PCS norms retest ────────────────────────────────────
    for label, rt_df, cond in [('df1 PCS retest', rt_pcs, 'PCS'),
                                ('df1 SWASH retest', rt_swash, 'SWASH')]:
        # Motor pair sums
        t1_motor = rt_df[MOTOR_COLS['df1']].sum(axis=1)
        t2_motor = rt_df[RETEST_MOTOR_T2].sum(axis=1)
        # Full-scale total (mean per item)
        t1_total = rt_df[RETEST_TOTAL_T1] / 10
        t2_total = rt_df[RETEST_TOTAL_T2] / 10

        # Motor T1 vs Motor T2
        r = retest_row(t1_motor, t2_motor, 'motor_pair_T1', 'motor_pair_T2', label)
        if r: rows.append(r)

        # Full T1 vs Full T2
        r = retest_row(t1_total, t2_total, 'full_total_T1', 'full_total_T2', label)
        if r: rows.append(r)

        # Motor T1 vs Full T2 (cross-time screening utility)
        r = retest_row(t1_motor, t2_total, 'motor_pair_T1', 'full_total_T2', label)
        if r: rows.append(r)

        # Full T1 vs Motor T2
        r = retest_row(t1_total, t2_motor, 'full_total_T1', 'motor_pair_T2', label)
        if r: rows.append(r)

        # Rest T1 vs Rest T2 (compute rest scores for retest file)
        # T1 rest items — need to recompute (8 non-motor items in ITEMS_DF1)
        rest_items_t1 = [c for c in ITEMS_DF1 if c not in MOTOR_COLS['df1']]
        # T2 rest items — suffix mapping
        # T2 item columns: HandLoweringSubjectiveRating_65, ..., PostHypnoticSubjectiveRating_74
        # Suffix numbers: _65 to _74, minus motor pair (_69, _70)
        rest_items_t2 = [c for c in rt_df.columns
                         if c.endswith(('_65','_66','_67','_68','_71','_72','_73','_74'))]
        if rest_items_t1 and rest_items_t2 and len(rest_items_t2) >= 8:
            t1_rest = rt_df[rest_items_t1].mean(axis=1)
            t2_rest = rt_df[rest_items_t2].mean(axis=1)
            r = retest_row(t1_rest, t2_rest, 'rest_score_T1', 'rest_score_T2', label)
            if r: rows.append(r)

            # Motor T1 vs Rest T2 (screening → non-motor criterion)
            r = retest_row(t1_motor, t2_rest, 'motor_pair_T1', 'rest_score_T2', label)
            if r: rows.append(r)

    # ── df3 SWASH retest (T2 total only) ───────────────────
    df3 = dfs['df3']
    df3_retest = df3[df3['Subjectivereturnscore'].notna()].copy()
    t1_motor_df3 = df3_retest[MOTOR_COLS['df3']].sum(axis=1)
    t1_total_df3 = df3_retest['Subjectivescore']
    t2_total_df3 = df3_retest['Subjectivereturnscore']

    r = retest_row(t1_motor_df3, t2_total_df3,
                   'motor_pair_T1', 'full_total_T2', 'df3 SWASH retest')
    if r: rows.append(r)

    r = retest_row(t1_total_df3, t2_total_df3,
                   'full_total_T1', 'full_total_T2', 'df3 SWASH retest')
    if r: rows.append(r)

    # ── Compile and save ────────────────────────────────────
    rt_df_out = pd.DataFrame(rows)
    rt_df_out.to_csv('tables/table_test_retest.csv', index=False)
    print("Saved: tables/table_test_retest.csv")

    print("\nTEST-RETEST RESULTS")
    print("=" * 80)
    print(rt_df_out.to_string(index=False))

    # Key comparison: motor T1→T2 vs full T1→T2
    print("\nKey comparison — motor pair stability vs full scale stability:")
    for label in ['df1 PCS retest', 'df1 SWASH retest']:
        sub = rt_df_out[rt_df_out['dataset'] == label]
        mot = sub[sub['T1_var'] == 'motor_pair_T1'][sub['T2_var'] == 'motor_pair_T2']
        ful = sub[sub['T1_var'] == 'full_total_T1'][sub['T2_var'] == 'full_total_T2']
        if len(mot) and len(ful):
            r_mot = mot['pearson_r'].values[0]
            r_ful = ful['pearson_r'].values[0]
            print(f"  {label}: motor T1-T2 r={r_mot:.3f}  |  full T1-T2 r={r_ful:.3f}")


if __name__ == '__main__':
    main()

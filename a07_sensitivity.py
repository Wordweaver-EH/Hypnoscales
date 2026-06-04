"""
a07_sensitivity.py — Sensitivity analyses.

Checks:
  1. Sum vs mean scoring of the motor pair
  2. Pearson vs Spearman
  3. Raw item scores vs z-scored items
  4. Full total vs z-scored item total
  5. Pairwise deletion vs listwise deletion
  6. PCS only vs PCS+SWASH (pooled intensity datasets, noting heterogeneity)
  7. df2 canonical 10-item total vs the buggy 12-col mean

Outputs:
  tables/table_sensitivity.csv
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, zscore
from lib_data import (load_all, ITEMS_DF1, ITEMS_DF2, ITEMS_DF3, ITEMS_DF5,
                      MOTOR_COLS, bootstrap_ci, N_BOOT, make_tables_dir)


def sens_row(x, y, label, check, variant, n_boot=N_BOOT):
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    mask = np.isfinite(xa) & np.isfinite(ya)
    xa, ya = xa[mask], ya[mask]
    n = len(xa)
    rp, _ = pearsonr(xa, ya)
    rs, _ = spearmanr(xa, ya)
    ci_lo, ci_hi = bootstrap_ci(xa, ya, 'pearson', n_boot=n_boot)
    return {
        'sensitivity_check': check,
        'variant':           variant,
        'dataset':           label,
        'n':                 n,
        'pearson_r':         round(rp,    3),
        'spearman_r':        round(rs,    3),
        'ci_lo':             round(ci_lo, 3),
        'ci_hi':             round(ci_hi, 3),
        'r2':                round(rp**2, 3),
    }


def main():
    make_tables_dir()
    dfs = load_all()

    rows = []

    intensity_configs = [
        ('df1_pcs',   ITEMS_DF1, MOTOR_COLS['df1'], 'Subjective_scale_score_first_test', 'rest_score', 'df1 PCS'),
        ('df1_swash', ITEMS_DF1, MOTOR_COLS['df1'], 'Subjective_scale_score_first_test', 'rest_score', 'df1 SWASH'),
        ('df2',       ITEMS_DF2, MOTOR_COLS['df2'], 'SubjectiveTotal',                   'rest_score', 'df2 PCS-VVIQ'),
        ('df3',       ITEMS_DF3, MOTOR_COLS['df3'], 'Subjectivescore',                   'rest_score', 'df3 SWASH'),
        ('df5',       ITEMS_DF5, MOTOR_COLS['df5'], 'PCscore',                           'rest_score', 'df5 vEAR PCS'),
    ]

    for key, all_items, mc, tc, rc, label in intensity_configs:
        df = dfs[key]

        # 1. Sum scoring (baseline — also used in main analyses)
        motor_sum  = df[mc].sum(axis=1)
        motor_mean = df[mc].mean(axis=1)
        total      = df[tc]
        rest       = df[rc]

        rows.append(sens_row(motor_sum,  total, label, 'scoring', 'motor_sum_vs_total'))
        rows.append(sens_row(motor_mean, total, label, 'scoring', 'motor_mean_vs_total'))
        rows.append(sens_row(motor_sum,  rest,  label, 'scoring', 'motor_sum_vs_rest'))
        rows.append(sens_row(motor_mean, rest,  label, 'scoring', 'motor_mean_vs_rest'))

        # 2. Z-scored motor pair vs z-scored total
        valid = motor_sum.notna() & total.notna()
        if valid.sum() > 5:
            motor_z = zscore(motor_sum[valid])
            total_z = zscore(total[valid])
            rows.append(sens_row(motor_z, total_z, label, 'z_scored', 'motor_z_vs_total_z'))

        # 3. Z-scored motor vs z-scored rest
        valid2 = motor_sum.notna() & rest.notna()
        if valid2.sum() > 5:
            motor_z2 = zscore(motor_sum[valid2])
            rest_z2  = zscore(rest[valid2])
            rows.append(sens_row(motor_z2, rest_z2, label, 'z_scored', 'motor_z_vs_rest_z'))

        # 4. Listwise deletion (on all 10 items simultaneously)
        complete = df[all_items].notna().all(axis=1)
        if complete.sum() > 10:
            m_lw = df.loc[complete, mc].sum(axis=1)
            t_lw = df.loc[complete, tc]
            rows.append(sens_row(m_lw, t_lw, label, 'listwise_deletion', 'motor_sum_vs_total'))

    # 5. df2 canonical vs buggy 12-col mean (the documented bug)
    df2 = dfs['df2']
    buggy_cols = ['HandBecomesHeavy', 'MagneticHands', 'Mosquito',
                  'SweetSubRating', 'SourSubRating', 'StiffArm', 'HandAndArmHeavy',
                  'HappyBirthday', 'ColouredBalls', 'Amnesia',
                  'PostHypnoticSub1', 'PostHypnoticSub2']
    df2['BuggyTotal'] = df2[buggy_cols].mean(axis=1)
    motor2 = df2[MOTOR_COLS['df2']].sum(axis=1)
    rows.append(sens_row(motor2, df2['SubjectiveTotal'], 'df2 PCS-VVIQ', 'scoring_check', 'canonical_10item_total'))
    rows.append(sens_row(motor2, df2['BuggyTotal'],      'df2 PCS-VVIQ', 'scoring_check', 'buggy_12col_total'))

    # 6. df3 SWASH — first-test vs retest total (documents the original bug)
    df3 = dfs['df3']
    motor3 = df3[MOTOR_COLS['df3']].sum(axis=1)
    # First-test (correct)
    rows.append(sens_row(motor3, df3['Subjectivescore'],
                         'df3 SWASH', 'retest_check', 'vs_first_test_total_n418'))
    # Retest total (original bug — n≈66 only)
    df3_rt = df3[df3['Subjectivereturnscore'].notna()]
    motor3_rt = df3_rt[MOTOR_COLS['df3']].sum(axis=1)
    rows.append(sens_row(motor3_rt, df3_rt['Subjectivereturnscore'],
                         'df3 SWASH', 'retest_check', 'vs_retest_total_n66_original_bug'))

    sens_df = pd.DataFrame(rows)
    sens_df.to_csv('tables/table_sensitivity.csv', index=False)
    print("Saved: tables/table_sensitivity.csv")

    print("\nSENSITIVITY ANALYSIS RESULTS")
    print("=" * 80)
    print(sens_df.to_string(index=False))

    # Highlight the df2 scoring comparison
    print("\ndf2 scoring bug check:")
    sc = sens_df[sens_df['sensitivity_check'] == 'scoring_check']
    print(sc[['variant', 'n', 'pearson_r', 'spearman_r']].to_string(index=False))

    print("\ndf3 retest check (documents original notebook bug):")
    rc = sens_df[sens_df['sensitivity_check'] == 'retest_check']
    print(rc[['variant', 'n', 'pearson_r']].to_string(index=False))


if __name__ == '__main__':
    main()

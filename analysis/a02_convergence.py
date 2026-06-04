"""
a02_convergence.py â€” Main convergence analyses.

Section 5: Motor pair vs full-scale total (part-whole) and vs rest score (part-rest).
Section 6: Two-item reliability (Spearman-Brown, inter-item r).

Outputs:
  tables/table_main_convergence.csv
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, norm
from lib_data import (TABLES_DIR, FIGURES_DIR, load_all, ITEMS_DF1, ITEMS_DF2, ITEMS_DF3,
                      ITEMS_DF4_INV, ITEMS_DF4_OBJ, ITEMS_DF5,
                      MOTOR_COLS, spearman_brown, bootstrap_ci,
                      corr_row, N_BOOT, make_tables_dir)


def fishers_z_test(r1, n1, r2, n2):
    """Fisher's r-to-z test comparing two independent Pearson correlations.
    Returns (z_stat, p_two_tailed).
    """
    z1 = np.arctanh(r1)
    z2 = np.arctanh(r2)
    se = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
    z  = (z1 - z2) / se
    p  = 2 * (1 - norm.cdf(abs(z)))
    return float(z), float(p)


def fmt_p(p):
    """Format p-value for printing."""
    if p < .001:
        return "< .001"
    return f"= {p:.3f}"

# Expected part-rest r targets (from corrected analysis, verified)
PART_REST_TARGETS = {
    'df1 PCS (cond=0)':  0.565,
    'df1 SWASH (cond=1)': 0.694,
    'df2 PCS-VVIQ':       0.549,
    'df3 SWASH':          0.630,
    'df4 HGSHS inv.':     0.661,
    'df5 vEAR PCS':       0.579,
}
FULL_SCALE_TARGETS = {
    'df1 PCS (cond=0)':  0.783,
    'df1 SWASH (cond=1)': 0.849,
    'df2 PCS-VVIQ':       0.778,
    'df3 SWASH':          0.807,
    'df4 HGSHS inv.':     0.799,
    'df5 vEAR PCS':       0.785,
}


def convergence_row(df, motor_cols, total_col, rest_col, label,
                    scale, context, dimension, n_boot=N_BOOT):
    """Full row: part-whole r, part-rest r, reliability, all with CIs."""
    motor = df[motor_cols].sum(axis=1)
    total = df[total_col]
    rest  = df[rest_col]

    # Part-whole (full-scale r)
    mask_pw = motor.notna() & total.notna()
    m_pw, t_pw = motor[mask_pw].values, total[mask_pw].values
    r_pw, p_pw   = pearsonr(m_pw, t_pw)
    rs_pw, _     = spearmanr(m_pw, t_pw)
    ci_pw        = bootstrap_ci(m_pw, t_pw, 'pearson', n_boot=n_boot)

    # Part-rest (overlap-free)
    mask_pr = motor.notna() & rest.notna()
    m_pr, r_pr   = motor[mask_pr].values, rest[mask_pr].values
    r_rest, p_pr = pearsonr(m_pr, r_pr)
    rs_rest, _   = spearmanr(m_pr, r_pr)
    ci_pr        = bootstrap_ci(m_pr, r_pr, 'pearson', n_boot=n_boot)

    # Inter-item correlation and Spearman-Brown reliability
    i1 = df[motor_cols[0]].dropna()
    i2 = df[motor_cols[1]].dropna()
    common = i1.index.intersection(i2.index)
    r_ii, _ = pearsonr(i1.loc[common].values, i2.loc[common].values)
    sb = spearman_brown(r_ii)

    n_pw = int(mask_pw.sum())
    n_pr = int(mask_pr.sum())

    return {
        'dataset':          label,
        'scale':            scale,
        'context':          context,
        'dimension':        dimension,
        'n_full':           n_pw,
        'n_rest':           n_pr,
        # Part-whole
        'r_full':           round(r_pw,    3),
        'p_full':           float(p_pw),
        'r_full_spearman':  round(rs_pw,   3),
        'r_full_ci_lo':     round(ci_pw[0], 3),
        'r_full_ci_hi':     round(ci_pw[1], 3),
        'r_full_r2':        round(r_pw**2,  3),
        # Part-rest
        'r_rest':           round(r_rest,    3),
        'p_rest':           float(p_pr),
        'r_rest_spearman':  round(rs_rest,   3),
        'r_rest_ci_lo':     round(ci_pr[0],  3),
        'r_rest_ci_hi':     round(ci_pr[1],  3),
        # Reliability
        'interitem_r':      round(r_ii,  3),
        'sb_reliability':   round(sb,    3),
    }


def main():
    make_tables_dir()
    dfs = load_all()

    configs = [
        ('df1_pcs',   MOTOR_COLS['df1'],     'Subjective_scale_score_first_test', 'rest_score',
         'df1 PCS (cond=0)',  'PCS',    'Non-hypnotic', 'intensity'),
        ('df1_swash', MOTOR_COLS['df1'],     'Subjective_scale_score_first_test', 'rest_score',
         'df1 SWASH (cond=1)','SWASH',  'Hypnotic',     'intensity'),
        ('df2',       MOTOR_COLS['df2'],     'SubjectiveTotal', 'rest_score',
         'df2 PCS-VVIQ',      'PCS',    'Non-hypnotic', 'intensity'),
        ('df3',       MOTOR_COLS['df3'],     'Subjectivescore', 'rest_score',
         'df3 SWASH',         'SWASH',  'Hypnotic',     'intensity'),
        ('df5',       MOTOR_COLS['df5'],     'PCscore', 'rest_score',
         'df5 vEAR PCS',      'PCS',    'Non-hypnotic', 'intensity'),
        ('df4',       MOTOR_COLS['df4_inv'], 'INV_total', 'rest_score_inv',
         'df4 HGSHS inv.',    'HGSHS:A','Classic',      'involuntariness'),
        ('df4',       MOTOR_COLS['df4_obj'], 'OBJ_total', 'rest_score_obj',
         'df4 HGSHS obj.',    'HGSHS:A','Classic',      'objective'),
    ]

    rows = []
    for key, mc, tc, rc, label, scale, ctx, dim in configs:
        row = convergence_row(dfs[key], mc, tc, rc, label, scale, ctx, dim)
        rows.append(row)

    conv_df = pd.DataFrame(rows)

    # Add target comparison columns
    conv_df['target_r_full'] = conv_df['dataset'].map(FULL_SCALE_TARGETS)
    conv_df['target_r_rest'] = conv_df['dataset'].map(PART_REST_TARGETS)
    conv_df['delta_full'] = (conv_df['r_full'] - conv_df['target_r_full']).round(3)
    conv_df['delta_rest'] = (conv_df['r_rest'] - conv_df['target_r_rest']).round(3)
    conv_df['ok_full'] = conv_df['delta_full'].abs().le(0.02) | conv_df['target_r_full'].isna()
    conv_df['ok_rest'] = conv_df['delta_rest'].abs().le(0.02) | conv_df['target_r_rest'].isna()

    conv_df.to_csv(f'{TABLES_DIR}/table_main_convergence.csv', index=False)
    print("Saved: tables/table_main_convergence.csv")

    # Print results
    print("\nMAIN CONVERGENCE RESULTS")
    print("=" * 90)
    cols = ['dataset', 'n_full', 'r_full', 'r_full_r2', 'r_full_ci_lo', 'r_full_ci_hi',
            'r_rest', 'r_rest_ci_lo', 'r_rest_ci_hi', 'sb_reliability', 'interitem_r']
    print(conv_df[cols].to_string(index=False))

    print("\nBenchmark: HGSHS-5:G r_full=0.83, RÂ²=0.69 (Riegel 2021; Zech 2024 RÂ²=0.69)")

    # Validation check
    bad = conv_df[~conv_df['ok_full'] & conv_df['target_r_full'].notna()]
    if len(bad):
        print(f"\nWARNING: {len(bad)} row(s) differ from expected r_full by >0.02:")
        print(bad[['dataset', 'r_full', 'target_r_full', 'delta_full']].to_string(index=False))
    else:
        print("\nAll r_full values within 0.02 of expected targets. OK.")

    bad_r = conv_df[~conv_df['ok_rest'] & conv_df['target_r_rest'].notna()]
    if len(bad_r):
        print(f"\nWARNING: {len(bad_r)} row(s) differ from expected r_rest by >0.02:")
        print(bad_r[['dataset', 'r_rest', 'target_r_rest', 'delta_rest']].to_string(index=False))
    else:
        print("All r_rest values within 0.02 of expected targets. OK.")

    # p-value summary
    print("\nP-values (all should be < .001 at these n's):")
    for _, row in conv_df.iterrows():
        print(f"  {row['dataset']:25s}  p_full {fmt_p(row['p_full'])}  "
              f"p_rest {fmt_p(row['p_rest'])}")

    # Fisher's z-test: SWASH vs PCS
    print("\nFisher's r-to-z test: SWASH vs PCS (same conditions, df1)")
    pcs_row   = conv_df[conv_df['dataset'] == 'df1 PCS (cond=0)'].iloc[0]
    swash_row = conv_df[conv_df['dataset'] == 'df1 SWASH (cond=1)'].iloc[0]
    for metric, r_col, n_col in [
        ('r_full', 'r_full', 'n_full'),
        ('r_rest', 'r_rest', 'n_rest'),
    ]:
        z, p = fishers_z_test(pcs_row[r_col], pcs_row[n_col],
                               swash_row[r_col], swash_row[n_col])
        print(f"  {metric}: PCS={pcs_row[r_col]:.3f} (n={pcs_row[n_col]}) vs "
              f"SWASH={swash_row[r_col]:.3f} (n={swash_row[n_col]})  "
              f"z={z:.3f}, p {fmt_p(p)}")

    print("\nFisher's r-to-z test: SWASH vs PCS (cross-dataset pairs)")
    cross_pairs = [
        ('df2 PCS-VVIQ', 'df3 SWASH'),
        ('df5 vEAR PCS', 'df3 SWASH'),
    ]
    for pcs_lbl, swash_lbl in cross_pairs:
        pr = conv_df[conv_df['dataset'] == pcs_lbl].iloc[0]
        sr = conv_df[conv_df['dataset'] == swash_lbl].iloc[0]
        z, p = fishers_z_test(pr['r_full'], pr['n_full'], sr['r_full'], sr['n_full'])
        print(f"  r_full: {pcs_lbl} {pr['r_full']:.3f} vs {swash_lbl} {sr['r_full']:.3f}  "
              f"z={z:.3f}, p {fmt_p(p)}")

    # Summary of floor means
    print("\nFloor item mechanism check (music + neg.visual means):")
    from lib_data import FLOOR_COLS
    for key, (mc_col, vc_col) in FLOOR_COLS.items():
        df = dfs[key]
        print(f"  {key:14s}  music={df[mc_col].mean():.3f}  neg.vis={df[vc_col].mean():.3f}")


if __name__ == '__main__':
    main()

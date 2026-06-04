"""
a06_external.py â€” External validity analyses.

Tests whether the motor pair preserves the full PCS relationship
with external criteria outside the scale itself.

Datasets with individual PCS items + external criterion:
  - df5:       vEAR score (vEARscoreFromVideoRatings)
  - anomalous: Combined anomalous experience (comb exp), OBE, past-life, spirit-world
  - flow:      Flow_combined (and sub-scores by activity)
  - des:       DES_score (Dissociative Experiences Scale)

Datasets with SWASH/PCS TOTAL only (no individual items):
  - RHI (n=740):  SubjectiveSWASH â†’ cannot compute motor pair
  - MTS (n=154):  SWASH_subjective_score â†’ cannot compute motor pair
  - VP  (n=501):  SWASH_subjective_score â†’ cannot compute motor pair
  These are noted in the output but excluded from the main table.

For each external criterion, fit:
  1. criterion ~ full_score
  2. criterion ~ motor_pair
  3. criterion ~ rest_score
  And report r, rÂ², CIs.

Outputs:
  tables/table_external_validity.csv
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from lib_data import (TABLES_DIR, FIGURES_DIR, load_all, load_external_validity,
                      MOTOR_COLS, ITEMS_EXT_PCS,
                      bootstrap_ci, corr_row, N_BOOT, make_tables_dir)


def external_row(x, y, predictor_label, criterion_label, dataset, n_boot=N_BOOT):
    """Single external-validity regression row."""
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    mask = np.isfinite(xa) & np.isfinite(ya)
    xa, ya = xa[mask], ya[mask]
    n = len(xa)
    if n < 20:
        return None
    rp, p = pearsonr(xa, ya)
    ci_lo, ci_hi = bootstrap_ci(xa, ya, 'pearson', n_boot=n_boot)
    return {
        'dataset':    dataset,
        'predictor':  predictor_label,
        'criterion':  criterion_label,
        'n':          n,
        'pearson_r':  round(rp,    3),
        'p_value':    float(p),
        'r2':         round(rp**2, 3),
        'ci_lo':      round(ci_lo, 3),
        'ci_hi':      round(ci_hi, 3),
    }


def triad(df, motor_col, total_col, rest_col, criterion_col, criterion_label, dataset):
    """Run the three-predictor triad for one criterion."""
    rows = []
    for pred_col, pred_label in [
        (motor_col,  'motor_pair'),
        (total_col,  'full_scale'),
        (rest_col,   'rest_score'),
    ]:
        if pred_col not in df.columns and not isinstance(pred_col, pd.Series):
            continue
        x = df[pred_col] if isinstance(pred_col, str) else pred_col
        y = df[criterion_col]
        r = external_row(x, y, pred_label, criterion_label, dataset)
        if r:
            rows.append(r)
    return rows


def main():
    make_tables_dir()
    dfs = load_all()
    ext = load_external_validity()

    all_rows = []

    # â”€â”€ df5: vEAR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    df5 = dfs['df5']
    for crit_col, crit_label in [
        ('vEARscoreFromVideoRatings', 'vEAR_score'),
        ('AveVEAR',                   'vEAR_avg_self_report'),
    ]:
        if crit_col in df5.columns:
            rows = triad(df5, 'motor_pair_sum', 'PCscore', 'rest_score',
                         crit_col, crit_label, 'df5 vEAR PCS')
            all_rows.extend(rows)

    # â”€â”€ Unusual-experiences datasets â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # anomalous: past-life, OBE, spirit-world, combined
    anom = ext['anomalous']
    anom_criteria = [
        ('comb exp',               'anomalous_combined'),
        ('out_of_body_experience', 'OBE_experience'),
        ('past_life_experience',   'past_life_experience'),
        ('spirit_world_experience','spirit_world_experience'),
    ]
    for col, label in anom_criteria:
        if col in anom.columns:
            rows = triad(anom, 'motor_pair_sum', 'PCSscore', 'rest_score',
                         col, label, 'anomalous_PCS')
            all_rows.extend(rows)

    # flow
    flow = ext['flow']
    for col, label in [
        ('Flow_combined',    'flow_combined'),
        ('Flow_vacuuming',   'flow_vacuuming'),
        ('Flow_essay_writing','flow_essay_writing'),
        ('Flow_exercise',    'flow_exercise'),
    ]:
        if col in flow.columns:
            rows = triad(flow, 'motor_pair_sum', 'PCSscore', 'rest_score',
                         col, label, 'flow_PCS')
            all_rows.extend(rows)

    # DES
    des = ext['des']
    rows = triad(des, 'motor_pair_sum', 'PCSscore', 'rest_score',
                 'DES_score', 'DES_dissociation', 'DES_PCS')
    all_rows.extend(rows)

    # â”€â”€ Compile â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    out_df = pd.DataFrame(all_rows)
    out_df.to_csv(f'{TABLES_DIR}/table_external_validity.csv', index=False)
    print("Saved: tables/table_external_validity.csv")

    print("\nEXTERNAL VALIDITY RESULTS")
    print("=" * 90)
    print(out_df.to_string(index=False))

    print("\n--- RHI / MTS / VP note ---")
    print("RHI (n=740), mirror-touch synaesthesia (n=154), vicarious pain (n=501)")
    print("available from osf/rhi/ but contain only SWASH total scores â€” no individual items.")
    print("Cannot compute motor pair for these datasets. Full-scale SWASH correlates with")
    print("these criteria in the original publications but motor-pair isolation is not possible.")

    # Key result summary
    print("\nKey comparisons (motor_pair vs full_scale r for each criterion):")
    for crit in out_df['criterion'].unique():
        sub = out_df[out_df['criterion'] == crit]
        mot = sub[sub['predictor'] == 'motor_pair']
        ful = sub[sub['predictor'] == 'full_scale']
        if len(mot) and len(ful):
            rm = mot['pearson_r'].values[0]
            rf = ful['pearson_r'].values[0]
            ds = mot['dataset'].values[0]
            print(f"  {crit:<35} ({ds})  motor r={rm:.3f}  full r={rf:.3f}")


if __name__ == '__main__':
    main()

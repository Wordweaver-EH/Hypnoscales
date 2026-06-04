"""
a05_all_pairs.py â€” All 2-item pair comparison.

For each PCS/SWASH dataset:
  - Generate all C(10,2)=45 two-item combinations
  - Compute full-scale r (part-whole) and part-rest r
  - Rank by both metrics
  - Mark the pre-specified motor pair

Key question: Is the arm rigidity + immobilisation pair uniquely strong,
or just one of several effective pairs?

Outputs:
  tables/table_all_pairs.csv          (df1 PCS + df3 SWASH, all 45 pairs each)
  tables/table_all_pairs_summary.csv  (pre-specified pair rank across datasets)
"""

import numpy as np
import pandas as pd
from itertools import combinations
from scipy.stats import pearsonr
from lib_data import (TABLES_DIR, FIGURES_DIR, load_all, ITEMS_DF1, ITEMS_DF2, ITEMS_DF3, ITEMS_DF5,
                      MOTOR_COLS, LABELS_PCS, make_tables_dir)

# Human-readable item labels
ITEM_LABELS_PCS = dict(zip(
    ITEMS_DF1,
    ['Hand lowering', 'Hands together', 'Mosquito', 'Taste',
     'Arm rigidity', 'Arm immobilisation',
     'Music', 'Neg. visual', 'Amnesia', 'Post-hypnotic']
))
# For df2, df3, df5 â€” same logical items in different columns
ITEM_LABELS_DF2 = dict(zip(ITEMS_DF2,
    ['Hand lowering', 'Hands together', 'Mosquito', 'Taste',
     'Arm rigidity', 'Arm immobilisation',
     'Music', 'Neg. visual', 'Amnesia', 'Post-hypnotic']))
ITEM_LABELS_DF3 = dict(zip(ITEMS_DF3,
    ['Hand lowering', 'Hands together', 'Mosquito', 'Taste',
     'Arm rigidity', 'Arm immobilisation',
     'Music', 'Neg. visual', 'Amnesia', 'Post-hypnotic']))
ITEM_LABELS_DF5 = dict(zip(ITEMS_DF5,
    ['Hand lowering', 'Hands together', 'Mosquito', 'Taste',
     'Arm rigidity', 'Arm immobilisation',
     'Music', 'Neg. visual', 'Amnesia', 'Post-hypnotic']))


def all_pairs_analysis(df, all_items, item_labels, total_col, motor_cols, dataset_label):
    """Compute r_full and r_rest for all 45 two-item pairs."""
    motor_set = frozenset(motor_cols)
    rows = []
    for c1, c2 in combinations(all_items, 2):
        pair_sum = df[[c1, c2]].sum(axis=1)
        total    = df[total_col]
        mask_pw  = pair_sum.notna() & total.notna()
        r_full, _ = pearsonr(pair_sum[mask_pw].values, total[mask_pw].values)

        # Part-rest: vs mean of remaining 8 items
        rest_cols = [c for c in all_items if c not in (c1, c2)]
        rest      = df[rest_cols].mean(axis=1)
        mask_pr   = pair_sum.notna() & rest.notna()
        r_rest, _ = pearsonr(pair_sum[mask_pr].values, rest[mask_pr].values)

        # Inter-item r
        mask_ii = df[c1].notna() & df[c2].notna()
        r_ii, _ = pearsonr(df[c1][mask_ii].values, df[c2][mask_ii].values)
        from lib_data import TABLES_DIR, FIGURES_DIR, spearman_brown
        sb = spearman_brown(r_ii)

        # Item means
        mean1 = df[c1].mean()
        mean2 = df[c2].mean()

        rows.append({
            'dataset':     dataset_label,
            'c1':          c1,
            'c2':          c2,
            'item1':       item_labels.get(c1, c1),
            'item2':       item_labels.get(c2, c2),
            'pair_label':  f'{item_labels.get(c1,c1)} + {item_labels.get(c2,c2)}',
            'r_full':      round(r_full, 3),
            'r2_full':     round(r_full**2, 3),
            'r_rest':      round(r_rest, 3),
            'interitem_r': round(r_ii, 3),
            'sb':          round(sb, 3),
            'item1_mean':  round(mean1, 3),
            'item2_mean':  round(mean2, 3),
            'is_prespecified_motor_pair': frozenset([c1, c2]) == motor_set,
        })

    result = (pd.DataFrame(rows)
              .sort_values('r_full', ascending=False)
              .reset_index(drop=True))
    result['rank_by_r_full'] = result.index + 1
    result_rest = result.sort_values('r_rest', ascending=False).reset_index(drop=True)
    result_rest['rank_by_r_rest'] = result_rest.index + 1
    result = result.merge(result_rest[['c1','c2','rank_by_r_rest']], on=['c1','c2'])
    return result


def main():
    make_tables_dir()
    dfs = load_all()

    configs = [
        ('df1_pcs',   ITEMS_DF1, ITEM_LABELS_PCS, 'Subjective_scale_score_first_test',
         MOTOR_COLS['df1'], 'df1 PCS'),
        ('df1_swash', ITEMS_DF1, ITEM_LABELS_PCS, 'Subjective_scale_score_first_test',
         MOTOR_COLS['df1'], 'df1 SWASH'),
        ('df2',       ITEMS_DF2, ITEM_LABELS_DF2, 'SubjectiveTotal',
         MOTOR_COLS['df2'], 'df2 PCS-VVIQ'),
        ('df3',       ITEMS_DF3, ITEM_LABELS_DF3, 'Subjectivescore',
         MOTOR_COLS['df3'], 'df3 SWASH'),
        ('df5',       ITEMS_DF5, ITEM_LABELS_DF5, 'PCscore',
         MOTOR_COLS['df5'], 'df5 vEAR PCS'),
    ]

    all_dfs = []
    summary_rows = []

    for key, items, labels, total_col, mc, ds_label in configs:
        df = dfs[key]
        pairs_df = all_pairs_analysis(df, items, labels, total_col, mc, ds_label)
        all_dfs.append(pairs_df)

        # Summary for the pre-specified motor pair
        motor_row = pairs_df[pairs_df['is_prespecified_motor_pair']].iloc[0]
        n_pairs = len(pairs_df)
        print(f"\n{ds_label} (n={len(df)}): motor pair rank #{int(motor_row['rank_by_r_full'])}/{n_pairs} "
              f"r_full={motor_row['r_full']:.3f}  r_rest={motor_row['r_rest']:.3f}  "
              f"rank_rest=#{int(motor_row['rank_by_r_rest'])}")

        # Top 10 pairs
        print(f"  Top 5 pairs by r_full:")
        for _, row in pairs_df.head(5).iterrows():
            marker = ' <<< MOTOR' if row['is_prespecified_motor_pair'] else ''
            print(f"    #{int(row['rank_by_r_full']):2d}  {row['pair_label']:<45}  "
                  f"r_full={row['r_full']:.3f}  r_rest={row['r_rest']:.3f}{marker}")

        summary_rows.append({
            'dataset':           ds_label,
            'n_pairs_total':     n_pairs,
            'motor_rank_r_full': int(motor_row['rank_by_r_full']),
            'motor_rank_r_rest': int(motor_row['rank_by_r_rest']),
            'motor_r_full':      motor_row['r_full'],
            'motor_r_rest':      motor_row['r_rest'],
            'motor_sb':          motor_row['sb'],
            'top1_pair':         pairs_df.iloc[0]['pair_label'],
            'top1_r_full':       pairs_df.iloc[0]['r_full'],
        })

    # Save combined table
    combined = pd.concat(all_dfs, ignore_index=True)
    combined.drop(columns=['c1','c2'], inplace=True, errors='ignore')
    combined.to_csv(f'{TABLES_DIR}/table_all_pairs.csv', index=False)
    print("\nSaved: tables/table_all_pairs.csv")

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(f'{TABLES_DIR}/table_all_pairs_summary.csv', index=False)
    print("Saved: tables/table_all_pairs_summary.csv")

    print("\nSUMMARY â€” Motor pair rank across datasets")
    print(summary_df.to_string(index=False))


if __name__ == '__main__':
    main()

"""
a01_descriptives.py â€” Item descriptives with floor/ceiling rates.

Outputs:
  tables/table_item_descriptives.csv
  tables/table_dataset_summary.csv
"""

import numpy as np
import pandas as pd
from lib_data import (TABLES_DIR, FIGURES_DIR, load_all, ITEMS_DF1, ITEMS_DF2, ITEMS_DF3,
                      ITEMS_DF4_INV, ITEMS_DF4_OBJ, ITEMS_DF5,
                      LABELS_PCS, LABELS_HGSHS, TYPES_PCS, TYPES_HGSHS,
                      MOTOR_COLS, PROCEDURE_ERA, make_tables_dir)


def item_stats(df, item_cols, labels, item_types, dataset_label, scale, scale_max=5.0):
    """Compute per-item descriptives including floor/ceiling rates."""
    rows = []
    for i, col in enumerate(item_cols):
        x = df[col].dropna().values
        n = len(x)
        rows.append({
            'dataset':        dataset_label,
            'scale':          scale,
            'item_num':       i + 1,
            'item_col':       col,
            'item_label':     labels[i],
            'item_type':      item_types[i],
            'n_valid':        n,
            'mean':           round(float(np.mean(x)), 3),
            'sd':             round(float(np.std(x, ddof=1)), 3),
            'median':         round(float(np.median(x)), 3),
            'iqr':            round(float(np.percentile(x, 75) - np.percentile(x, 25)), 3),
            'min':            float(np.min(x)),
            'max':            float(np.max(x)),
            'pct_floor':      round(100 * float(np.mean(x == 0)), 1),
            'pct_ceiling':    round(100 * float(np.mean(x == scale_max)), 1),
            'pct_missing':    round(100 * float(df[col].isna().mean()), 1),
        })
    return rows


def main():
    make_tables_dir()
    dfs = load_all()

    configs = [
        ('df1_pcs',   ITEMS_DF1, LABELS_PCS,   TYPES_PCS,   'df1 PCS (cond=0)',    'PCS',    'intensity', 5.0),
        ('df1_swash', ITEMS_DF1, LABELS_PCS,   TYPES_PCS,   'df1 SWASH (cond=1)',  'SWASH',  'intensity', 5.0),
        ('df2',       ITEMS_DF2, LABELS_PCS,   TYPES_PCS,   'df2 PCS-VVIQ',        'PCS',    'intensity', 5.0),
        ('df3',       ITEMS_DF3, LABELS_PCS,   TYPES_PCS,   'df3 SWASH',           'SWASH',  'intensity', 5.0),
        ('df5',       ITEMS_DF5, LABELS_PCS,   TYPES_PCS,   'df5 vEAR PCS',        'PCS',    'intensity', 5.0),
        ('df4',       ITEMS_DF4_INV, LABELS_HGSHS, TYPES_HGSHS, 'df4 HGSHS inv.',  'HGSHS:A','involuntariness', 5.0),
        ('df4',       ITEMS_DF4_OBJ, LABELS_HGSHS, TYPES_HGSHS, 'df4 HGSHS obj.',  'HGSHS:A','objective', 1.0),
    ]

    all_rows = []
    for key, items, labels, types, label, scale, dim, smax in configs:
        rows = item_stats(dfs[key], items, labels, types, label, scale, scale_max=smax)
        for r in rows:
            r['dimension'] = dim
        all_rows.extend(rows)

    desc_df = pd.DataFrame(all_rows)
    desc_df.to_csv(f'{TABLES_DIR}/table_item_descriptives.csv', index=False)
    print("Saved: tables/table_item_descriptives.csv")

    # Dataset summary
    summary_rows = []
    for key, items, labels, types, label, scale, dim, smax in configs:
        df = dfs[key]
        n = len(df)
        # Full-scale total column
        totals = {
            'df1_pcs': 'Subjective_scale_score_first_test',
            'df1_swash': 'Subjective_scale_score_first_test',
            'df2': 'SubjectiveTotal',
            'df3': 'Subjectivescore',
            'df5': 'PCscore',
        }
        tc = totals.get(key)
        if tc:
            total_mean = round(df[tc].mean(), 3)
            total_sd   = round(df[tc].std(ddof=1), 3)
        else:
            tc_col = 'INV_total' if dim == 'involuntariness' else 'OBJ_total'
            total_mean = round(df[tc_col].mean(), 3) if tc_col in df.columns else float('nan')
            total_sd   = round(df[tc_col].std(ddof=1), 3) if tc_col in df.columns else float('nan')

        summary_rows.append({
            'dataset':     label,
            'scale':       scale,
            'dimension':   dim,
            'n':           n,
            'total_mean':  total_mean,
            'total_sd':    total_sd,
            'procedure':   PROCEDURE_ERA.get(key, ''),
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(f'{TABLES_DIR}/table_dataset_summary.csv', index=False)
    print("Saved: tables/table_dataset_summary.csv")

    # Print floor summary
    print("\nFloor item means (key mechanism check):")
    floor_mask = desc_df['item_type'].isin(['perceptual', 'cognitive'])
    floor_sub  = desc_df[floor_mask][['dataset', 'item_label', 'mean', 'pct_floor']].copy()
    print(floor_sub.to_string(index=False))

    # Motor vs perceptual mean comparison
    print("\nMean by item type (intensity datasets only):")
    intensity = desc_df[desc_df['dimension'] == 'intensity']
    type_means = intensity.groupby(['dataset', 'item_type'])['mean'].mean().round(3).unstack()
    print(type_means.to_string())


if __name__ == '__main__':
    main()

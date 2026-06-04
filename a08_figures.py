"""
a08_figures.py — Publication-quality figures.

Figure 1: Forest plot — motor pair vs full total and vs rest score across all datasets.
Figure 2: All-pairs rank plot — motor pair rank among all 45 pairs (all 5 datasets).
Figure 3: Item floor/variance plot — item means + floor % by type, all intensity datasets.
Figure 4: Classification ROC curves (primary: full-total criterion, top-33%, PCS only).
Figure 5: External validity — motor pair vs full scale r across external criteria.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os

from lib_data import (load_all, ITEMS_DF1, ITEMS_DF2, ITEMS_DF3, ITEMS_DF5,
                      MOTOR_COLS, LABELS_PCS, TYPES_PCS, COLOUR_MAP,
                      make_figures_dir)
from sklearn.metrics import roc_curve, auc


DPI = 300


def fig1_forest_plot():
    """Forest plot: motor pair correlations across datasets."""
    conv = pd.read_csv('tables/table_main_convergence.csv')
    intensity = conv[conv['dimension'].isin(['intensity', 'involuntariness'])].copy()

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)

    labels  = intensity['dataset'].tolist()
    n_ds    = len(labels)
    y_pos   = list(range(n_ds, 0, -1))
    colours = ['#e74c3c' if 'PCS' in l else '#3498db' if 'SWASH' in l else '#9b59b6'
               for l in labels]

    for ax, r_col, ci_lo, ci_hi, title, bench_r in [
        (axes[0], 'r_full', 'r_full_ci_lo', 'r_full_ci_hi',
         'Motor pair vs full scale total\n(part-whole; same design as HGSHS-5:G r=0.83)', 0.83),
        (axes[1], 'r_rest', 'r_rest_ci_lo', 'r_rest_ci_hi',
         'Motor pair vs rest score\n(part-rest, overlap-free)', None),
    ]:
        rs = intensity[r_col].values
        lo = intensity[ci_lo].values
        hi = intensity[ci_hi].values

        for y, r, l, h, c in zip(y_pos, rs, lo, hi, colours):
            ax.plot([l, h], [y, y], lw=2, color=c, alpha=0.7)
            ax.scatter([r], [y], color=c, s=70, zorder=5)

        ax.axvline(0, color='#555', lw=0.7, ls='--')
        if bench_r:
            ax.axvline(bench_r, color='#888', lw=1.2, ls=':', alpha=0.7,
                       label=f'HGSHS-5:G r={bench_r} (Riegel 2021)')
            ax.legend(fontsize=8, loc='lower right')

        ax.set_xlim(0, 1.0)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel('Pearson r  (95% bootstrap CI)', fontsize=10)
        ax.set_title(title, fontsize=10, pad=8)
        ax.grid(axis='x', alpha=0.3)

        for y, r in zip(y_pos, rs):
            ax.text(r + 0.01, y, f'{r:.3f}', va='center', fontsize=8)

    fig.suptitle('Two-item motor composite (arm rigidity + immobilisation)\n'
                 'correlations with full-scale and rest-score across datasets',
                 fontsize=11, y=1.02)
    plt.tight_layout()
    plt.savefig('figures/fig1_forest_plot.png', dpi=DPI, bbox_inches='tight')
    plt.close()
    print("Saved: figures/fig1_forest_plot.png")


def fig2_all_pairs_rank():
    """All-pairs rank: motor pair among 45 pairs, all PCS datasets."""
    pairs = pd.read_csv('tables/table_all_pairs.csv')

    # Show all PCS datasets (drop SWASH — incidental)
    pcs_datasets = [ds for ds in ['df1 PCS', 'df2 PCS-VVIQ', 'df5 vEAR PCS']
                    if ds in pairs['dataset'].unique()]
    n_panels = len(pcs_datasets)

    fig, axes = plt.subplots(1, n_panels, figsize=(5 * n_panels, 8))
    if n_panels == 1:
        axes = [axes]

    for ax, ds_label in zip(axes, pcs_datasets):
        sub = pairs[pairs['dataset'] == ds_label].copy()
        sub = sub.sort_values('r_full', ascending=True).reset_index(drop=True)
        y   = range(len(sub))

        colours = ['#e74c3c' if row['is_prespecified_motor_pair'] else '#bbb'
                   for _, row in sub.iterrows()]
        sizes   = [140 if row['is_prespecified_motor_pair'] else 30
                   for _, row in sub.iterrows()]

        ax.scatter(sub['r_full'], y, c=colours, s=sizes, zorder=5, alpha=0.85, label='r_full')
        ax.scatter(sub['r_rest'], y, c=colours, s=sizes, zorder=5, alpha=0.45,
                   marker='D', label='r_rest')

        motor_idx = sub[sub['is_prespecified_motor_pair']].index[0]
        motor_row = sub.loc[motor_idx]
        ax.annotate('Motor pair\n(rigidity+immob.)',
                    xy=(motor_row['r_full'], list(y)[motor_idx]),
                    xytext=(motor_row['r_full'] - 0.14, list(y)[motor_idx] + 3),
                    fontsize=8, color='#c0392b',
                    arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.2))

        ax.set_xlabel('Pearson r  (● = r_full,  ◆ = r_rest)', fontsize=9)
        ax.set_ylabel('Rank among 45 pairs  (higher = stronger correlation)', fontsize=9)
        ax.set_title(f'{ds_label}', fontsize=10)
        ax.grid(alpha=0.3)

    fig.suptitle('All-pairs analysis: pre-specified motor pair among all 45 two-item combinations\n'
                 'Highlighted in red', fontsize=10)
    plt.tight_layout()
    plt.savefig('figures/fig2_all_pairs_rank.png', dpi=DPI, bbox_inches='tight')
    plt.close()
    print("Saved: figures/fig2_all_pairs_rank.png")


def fig3_item_floor():
    """Item means + floor percentages, one panel per dataset."""
    desc = pd.read_csv('tables/table_item_descriptives.csv')
    intensity = desc[desc['dimension'] == 'intensity']
    datasets  = [('df1 PCS (cond=0)', 'df1 PCS'),
                 ('df1 SWASH (cond=1)', 'df1 SWASH'),
                 ('df2 PCS-VVIQ', 'df2 PCS'),
                 ('df3 SWASH', 'df3 SWASH'),
                 ('df5 vEAR PCS', 'df5 vEAR')]

    fig, axes = plt.subplots(2, 5, figsize=(18, 7))
    for col, (full_label, short_label) in enumerate(datasets):
        sub = intensity[intensity['dataset'] == full_label].copy()
        sub = sub.sort_values('item_num').reset_index(drop=True)
        bar_colours = [COLOUR_MAP.get(t, '#888') for t in sub['item_type']]
        x = range(len(sub))

        axes[0, col].bar(x, sub['mean'], color=bar_colours, alpha=0.85, edgecolor='white')
        axes[0, col].set_title(short_label, fontsize=9)
        axes[0, col].set_xticks(x)
        axes[0, col].set_xticklabels([f'i{i+1}' for i in range(len(sub))], fontsize=7)
        axes[0, col].set_ylim(0, 5)
        if col == 0:
            axes[0, col].set_ylabel('Mean (0–5)', fontsize=9)

        axes[1, col].bar(x, sub['pct_floor'], color=bar_colours, alpha=0.85, edgecolor='white')
        axes[1, col].set_xticks(x)
        axes[1, col].set_xticklabels([f'i{i+1}' for i in range(len(sub))], fontsize=7)
        axes[1, col].set_ylim(0, 100)
        if col == 0:
            axes[1, col].set_ylabel('% at floor (0)', fontsize=9)

    from matplotlib.patches import Patch
    legend_els = [Patch(color=COLOUR_MAP['motor'],      label='Motor/action  (i5–i6)'),
                  Patch(color=COLOUR_MAP['perceptual'], label='Perceptual'),
                  Patch(color=COLOUR_MAP['cognitive'],  label='Cognitive/amnesia')]
    fig.legend(handles=legend_els, loc='upper right', fontsize=9,
               title='Item type', title_fontsize=9,
               bbox_to_anchor=(0.99, 0.98))

    fig.suptitle('Item means (top) and floor rates (bottom) across PCS/SWASH datasets\n'
                 'Motor items (i5, i6) sit at mid-scale; perceptual items approach floor',
                 fontsize=10)
    plt.tight_layout(rect=[0, 0, 0.88, 1])
    plt.savefig('figures/fig3_item_floor.png', dpi=DPI, bbox_inches='tight')
    plt.close()
    print("Saved: figures/fig3_item_floor.png")


def fig4_roc_curves():
    """ROC curves — primary: full-total criterion, top-33%, PCS datasets only."""
    dfs = load_all()

    configs = [
        ('df1_pcs', MOTOR_COLS['df1'], 'Subjective_scale_score_first_test', 'df1 PCS'),
        ('df2',     MOTOR_COLS['df2'], 'SubjectiveTotal',                   'df2 PCS-VVIQ'),
        ('df5',     MOTOR_COLS['df5'], 'PCscore',                           'df5 vEAR PCS'),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    for ax, (key, mc, tc, label) in zip(axes, configs):
        df    = dfs[key]
        motor = df[mc].sum(axis=1).dropna()
        crit  = df.loc[motor.index, tc].dropna()
        common = motor.index.intersection(crit.index)
        m = motor.loc[common].values.astype(float)
        c = crit.loc[common].values.astype(float)

        # Top-33% (top tertile) on the criterion
        t_crit = np.quantile(c, 2/3)
        true_h = (c > t_crit).astype(int)
        fpr, tpr, _ = roc_curve(true_h, m)
        roc_auc = auc(fpr, tpr)

        ax.plot(fpr, tpr, color='#e74c3c', lw=2, label=f'AUC = {roc_auc:.3f}')
        ax.plot([0, 1], [0, 1], 'k--', lw=0.8)
        ax.set_xlabel('False positive rate', fontsize=9)
        if ax == axes[0]:
            ax.set_ylabel('True positive rate', fontsize=9)
        ax.set_title(f'{label}\n(top-33% criterion)', fontsize=9)
        ax.legend(fontsize=9, loc='lower right')
        ax.grid(alpha=0.25)

    fig.suptitle('ROC curves: motor composite classifying top-third on full scale total\n'
                 'Motor items are inside the total (part-whole; same design as HGSHS-5:G)',
                 fontsize=10)
    plt.tight_layout()
    plt.savefig('figures/fig4_roc_primary.png', dpi=DPI, bbox_inches='tight')
    plt.close()
    print("Saved: figures/fig4_roc_primary.png")


def fig5_external_validity():
    """Grouped bar chart: motor pair vs full scale r across external criteria."""
    ext = pd.read_csv('tables/table_external_validity.csv')

    # Select main criteria — one row per criterion, motor vs full_scale
    criteria_order = [
        ('vEAR_score',           'vEAR\n(video-rated)'),
        ('anomalous_combined',   'Anomalous\nexperiences'),
        ('past_life_experience', 'Past-life\nexperiences'),
        ('DES_dissociation',     'DES\n(dissociation)'),
        ('flow_combined',        'Flow\n(combined)'),
    ]

    motor_rs = []
    full_rs  = []
    motor_lo = []
    motor_hi = []
    full_lo  = []
    full_hi  = []
    labels   = []

    for crit_col, crit_label in criteria_order:
        sub = ext[ext['criterion'] == crit_col]
        if sub.empty:
            continue
        m = sub[sub['predictor'] == 'motor_pair'].iloc[0]
        f = sub[sub['predictor'] == 'full_scale'].iloc[0]
        motor_rs.append(m['pearson_r'])
        full_rs.append(f['pearson_r'])
        motor_lo.append(m['pearson_r'] - m['ci_lo'])
        motor_hi.append(m['ci_hi'] - m['pearson_r'])
        full_lo.append(f['pearson_r'] - f['ci_lo'])
        full_hi.append(f['ci_hi'] - f['pearson_r'])
        labels.append(crit_label)

    n = len(labels)
    x = np.arange(n)
    w = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))

    bars_m = ax.bar(x - w/2, motor_rs, w, label='Motor pair (rigidity + immob.)',
                    color='#e74c3c', alpha=0.85)
    bars_f = ax.bar(x + w/2, full_rs,  w, label='Full scale total',
                    color='#3498db', alpha=0.85)

    ax.errorbar(x - w/2, motor_rs,
                yerr=[motor_lo, motor_hi],
                fmt='none', color='#333', capsize=4, lw=1.2)
    ax.errorbar(x + w/2, full_rs,
                yerr=[full_lo, full_hi],
                fmt='none', color='#333', capsize=4, lw=1.2)

    # Annotate % signal retained only where both values are interpretable
    for xi, mr, fr in zip(x, motor_rs, full_rs):
        if fr > 0.15 and mr > 0.10:
            pct = int(round(100 * mr / fr))
            ax.text(xi, max(mr, fr) + 0.015, f'{pct}%',
                    ha='center', va='bottom', fontsize=7.5, color='#555')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel('Pearson r  (95% bootstrap CI)', fontsize=10)
    ax.set_ylim(0, 0.52)
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.set_title('External validity: motor pair vs full scale correlations\n'
                 'No item overlap between motor pair and any external criterion\n'
                 'Percentage labels show signal retained by motor pair relative to full scale',
                 fontsize=10)

    plt.tight_layout()
    plt.savefig('figures/fig5_external_validity.png', dpi=DPI, bbox_inches='tight')
    plt.close()
    print("Saved: figures/fig5_external_validity.png")


def main():
    make_figures_dir()
    fig1_forest_plot()
    fig2_all_pairs_rank()
    fig3_item_floor()
    fig4_roc_curves()
    fig5_external_validity()
    print("\nAll figures saved to figures/")


if __name__ == '__main__':
    main()

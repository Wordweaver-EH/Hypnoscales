"""
a09_eda.py — Exploratory analyses (not tied to the main paper claims).

Three questions:
  A. VVIQ × item-level: does imagery vividness predict perceptual items
     specifically, or is the relationship item-type-agnostic?
  B. Response profiles: do distinct responder types emerge from item
     response patterns in unselected PCS samples?
  C. Taxon vs dimension: is HGSHS:A suggestibility taxonic or continuous?

All outputs written to figures/ and tables/.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
from scipy.stats import pearsonr, norm
from scipy.special import gammaln
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture

from lib_data import (
    load_all, ITEMS_DF1, ITEMS_DF2, ITEMS_DF4_OBJ, ITEMS_DF4_INV,
    LABELS_PCS, LABELS_HGSHS, TYPES_PCS, COLOUR_MAP,
    MOTOR_COLS, FIGURES_DIR, TABLES_DIR,
    make_figures_dir, make_tables_dir, bootstrap_ci, RANDOM_SEED, N_BOOT
)

RNG = np.random.default_rng(RANDOM_SEED)

# ─────────────────────────────────────────────────────────────
# A.  VVIQ × item-level correlations
# ─────────────────────────────────────────────────────────────

def fishers_z_test(r1, n1, r2, n2):
    z1, z2 = np.arctanh(r1), np.arctanh(r2)
    se = np.sqrt(1/(n1-3) + 1/(n2-3))
    z = (z1 - z2) / se
    p = 2 * (1 - norm.cdf(abs(z)))
    return float(z), float(p)


def vviq_item_correlations(df2):
    """Correlate VVIQ_total with each PCS item; return DataFrame."""
    rows = []
    for item, label, itype in zip(ITEMS_DF2, LABELS_PCS, TYPES_PCS):
        sub = df2[[item, 'VVIQ_total']].dropna()
        r, p = pearsonr(sub[item].values, sub['VVIQ_total'].values)
        ci = bootstrap_ci(sub[item].values, sub['VVIQ_total'].values,
                          'pearson', n_boot=N_BOOT)
        rows.append({'item': item, 'label': label, 'type': itype,
                     'r': round(r, 3), 'p': round(p, 4),
                     'ci_lo': round(ci[0], 3), 'ci_hi': round(ci[1], 3),
                     'n': len(sub)})
    return pd.DataFrame(rows)


def plot_vviq(corr_df, ax):
    colours = [COLOUR_MAP[t] for t in corr_df['type']]
    x = np.arange(len(corr_df))
    bars = ax.bar(x, corr_df['r'], color=colours, alpha=0.85, zorder=3)
    # CI whiskers
    for i, row in corr_df.reset_index(drop=True).iterrows():
        ax.plot([i, i], [row['ci_lo'], row['ci_hi']], 'k-', lw=1.5, zorder=4)
    ax.axhline(0, color='#333', lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(corr_df['label'], rotation=40, ha='right', fontsize=8.5)
    ax.set_ylabel('Pearson r with VVIQ', fontsize=10)
    ax.set_title('A.  VVIQ × individual PCS items  (df2, N=508)', fontsize=11, pad=8)
    ax.set_ylim(-0.15, 0.35)
    ax.grid(axis='y', alpha=0.4, zorder=0)
    legend = [Patch(color=v, label=k) for k, v in COLOUR_MAP.items()]
    ax.legend(handles=legend, fontsize=8, loc='upper left')


# ─────────────────────────────────────────────────────────────
# B.  Response profiles — k-means on item ratings
# ─────────────────────────────────────────────────────────────

def elbow_ks(X_scaled, ks=range(2, 9), seed=RANDOM_SEED):
    inertias = []
    for k in ks:
        km = KMeans(n_clusters=k, random_state=seed, n_init=20)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
    return list(ks), inertias


def fit_profiles(X, k=4, seed=RANDOM_SEED):
    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)
    km = KMeans(n_clusters=k, random_state=seed, n_init=50)
    labels = km.fit_predict(X_sc)
    # Recover cluster centres in original scale
    centres = scaler.inverse_transform(km.cluster_centers_)
    return labels, centres, X_sc


def plot_profiles(centres, item_labels, item_types, ax):
    """Heatmap of cluster centres (rows=clusters, cols=items)."""
    k = centres.shape[0]
    n_items = centres.shape[1]
    # Sort clusters by total score descending
    order = np.argsort(centres.mean(axis=1))[::-1]
    centres = centres[order]

    vmin, vmax = 0, 5
    im = ax.imshow(centres, aspect='auto', cmap='YlOrRd',
                   vmin=vmin, vmax=vmax, interpolation='nearest')
    ax.set_xticks(range(n_items))
    ax.set_xticklabels(item_labels, rotation=40, ha='right', fontsize=8)
    ax.set_yticks(range(k))
    ax.set_yticklabels([f'Profile {i+1}' for i in range(k)], fontsize=9)
    ax.set_title('B.  Response profiles — cluster centres (k=4, df1 PCS)',
                 fontsize=11, pad=8)
    plt.colorbar(im, ax=ax, label='Mean rating (0–5)', shrink=0.8)
    # Mark motor items
    motor_idx = [i for i, t in enumerate(item_types) if t == 'motor']
    for mi in motor_idx:
        ax.axvline(mi - 0.5, color='#e74c3c', lw=1.2, alpha=0.6)
        ax.axvline(mi + 0.5, color='#e74c3c', lw=1.2, alpha=0.6)


def plot_elbow(ks, inertias, ax):
    ax.plot(ks, inertias, 'o-', color='#2c3e50', lw=2)
    ax.set_xlabel('k', fontsize=10)
    ax.set_ylabel('Inertia', fontsize=10)
    ax.set_title('Elbow (df1 PCS)', fontsize=10)
    ax.grid(alpha=0.4)


def plot_pca_scatter(X_sc, profile_labels, ax):
    pca = PCA(n_components=2, random_state=RANDOM_SEED)
    Z = pca.fit_transform(X_sc)
    colours_scatter = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
    k = len(np.unique(profile_labels))
    # Sort clusters by mean score (same as centres sort)
    # (label mapping already applied above — just plot)
    for c in range(k):
        mask = profile_labels == c
        ax.scatter(Z[mask, 0], Z[mask, 1],
                   color=colours_scatter[c % len(colours_scatter)],
                   alpha=0.5, s=18, label=f'Profile {c+1}')
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.0f}%)', fontsize=9)
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.0f}%)', fontsize=9)
    ax.set_title('PCA scatter by profile', fontsize=10)
    ax.legend(fontsize=8, markerscale=1.5)
    ax.grid(alpha=0.3)


# ─────────────────────────────────────────────────────────────
# C.  Taxon vs dimension — HGSHS:A objective total
# ─────────────────────────────────────────────────────────────

def fit_mixture_models(scores, max_k=3):
    """Fit 1- and 2-component Gaussian mixtures; return BIC table."""
    rows = []
    for k in range(1, max_k + 1):
        gm = GaussianMixture(n_components=k, random_state=RANDOM_SEED,
                             n_init=20, covariance_type='full')
        gm.fit(scores.reshape(-1, 1))
        rows.append({
            'components': k,
            'bic': round(gm.bic(scores.reshape(-1, 1)), 1),
            'aic': round(gm.aic(scores.reshape(-1, 1)), 1),
            'log_likelihood': round(gm.score(scores.reshape(-1, 1)) * len(scores), 1),
            'means': [round(m[0], 2) for m in gm.means_],
            'weights': [round(w, 3) for w in gm.weights_],
        })
    return pd.DataFrame(rows)


def mambac_curve(scores, indicator, n_cuts=50):
    """
    MAMBAC (Mean Above Minus Below A Cut).
    Sorts by `scores`, slides a cut, computes mean(indicator above) - mean(indicator below).
    Taxonic: curve is peaked/humped; dimensional: curve is flat or monotone.
    """
    sorted_idx = np.argsort(scores)
    x_sorted = scores[sorted_idx]
    y_sorted = indicator[sorted_idx]
    n = len(scores)
    # Cuts: exclude extreme 10%
    lo, hi = int(0.1 * n), int(0.9 * n)
    cut_positions = np.linspace(lo, hi, n_cuts, dtype=int)
    diffs = []
    cuts = []
    for c in cut_positions:
        above = y_sorted[c:]
        below = y_sorted[:c]
        if len(above) < 5 or len(below) < 5:
            continue
        diffs.append(above.mean() - below.mean())
        cuts.append(x_sorted[c])
    return np.array(cuts), np.array(diffs)


def plot_taxon(df4, ax_hist, ax_mambac, ax_bic):
    obj_scores = df4['OBJ_total'].dropna().values
    inv_scores = df4['INV_total'].dropna().values

    # --- Histogram with mixture overlay ---
    n, bins, _ = ax_hist.hist(obj_scores, bins=13, color='#5d8aa8',
                               alpha=0.7, density=True, label='Observed')
    x_range = np.linspace(0, 12, 300)
    for k, colour, ls in [(1, '#e74c3c', '--'), (2, '#2ecc71', '-')]:
        gm = GaussianMixture(n_components=k, random_state=RANDOM_SEED,
                             n_init=20, covariance_type='full')
        gm.fit(obj_scores.reshape(-1, 1))
        log_prob = gm.score_samples(x_range.reshape(-1, 1))
        ax_hist.plot(x_range, np.exp(log_prob), color=colour, lw=2, ls=ls,
                     label=f'{k}-component GMM')
    ax_hist.set_xlabel('HGSHS:A objective total (0–12)', fontsize=10)
    ax_hist.set_ylabel('Density', fontsize=10)
    ax_hist.set_title('C.  HGSHS:A score distribution', fontsize=11, pad=8)
    ax_hist.legend(fontsize=8)
    ax_hist.grid(alpha=0.3)

    # --- BIC table as text ---
    bic_df = fit_mixture_models(obj_scores)
    ax_bic.axis('off')
    col_labels = ['k', 'BIC', 'AIC', 'Means', 'Weights']
    table_data = []
    for _, row in bic_df.iterrows():
        table_data.append([
            int(row['components']),
            f"{row['bic']:.0f}",
            f"{row['aic']:.0f}",
            str(row['means']),
            str(row['weights']),
        ])
    tbl = ax_bic.table(cellText=table_data, colLabels=col_labels,
                       loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    tbl.scale(1.2, 1.6)
    ax_bic.set_title('GMM model comparison (HGSHS:A obj.)', fontsize=10)

    # --- MAMBAC ---
    # Use OBJ_total as input, a single item as indicator (item 6 = arm rigidity,
    # highest-loading in our analysis)
    common = df4[['OBJ_total', 'HGSHS.A6']].dropna()
    cuts, diffs = mambac_curve(common['OBJ_total'].values,
                                common['HGSHS.A6'].values)
    ax_mambac.plot(cuts, diffs, 'o-', color='#2c3e50', lw=2, ms=5)
    ax_mambac.axhline(0, color='#aaa', lw=0.8, ls='--')
    ax_mambac.set_xlabel('Cut point (HGSHS:A objective total)', fontsize=10)
    ax_mambac.set_ylabel('Mean(above) − Mean(below)\nArm rigidity', fontsize=9)
    ax_mambac.set_title('MAMBAC curve (arm rigidity indicator)', fontsize=10)
    ax_mambac.grid(alpha=0.3)
    # Taxonic expectation: peaked hump; dimensional: monotone / flat
    ax_mambac.annotate('Taxonic → peak/hump\nDimensional → monotone',
                       xy=(0.98, 0.97), xycoords='axes fraction',
                       ha='right', va='top', fontsize=7.5,
                       bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    make_figures_dir()
    make_tables_dir()
    dfs = load_all()
    df1_pcs = dfs['df1_pcs']
    df2     = dfs['df2']
    df4     = dfs['df4']

    # ── A. VVIQ ──────────────────────────────────────────────
    print("=" * 60)
    print("A. VVIQ × item-level correlations (df2, N=508)")
    print("=" * 60)
    corr_df = vviq_item_correlations(df2)
    print(corr_df[['label', 'type', 'r', 'ci_lo', 'ci_hi', 'p']].to_string(index=False))

    motor_r    = corr_df[corr_df['type'] == 'motor']['r'].values
    percept_r  = corr_df[corr_df['type'] == 'perceptual']['r'].values
    n = corr_df['n'].iloc[0]
    print(f"\nMotor mean r={motor_r.mean():.3f}  Perceptual mean r={percept_r.mean():.3f}")

    # Fisher test: motor pair vs near-floor visual items
    taste_r = corr_df[corr_df['label'] == 'Taste hallucination']['r'].values[0]
    vis_r   = corr_df[corr_df['label'] == 'Neg. visual hallucination']['r'].values[0]
    z, p = fishers_z_test(taste_r, n, vis_r, n)
    print(f"Fisher z: Taste vs Neg.visual  z={z:.3f}  p={p:.4f}")

    corr_df.to_csv(f'{TABLES_DIR}/table_eda_vviq.csv', index=False)

    # ── B. Response profiles ──────────────────────────────────
    print("\n" + "=" * 60)
    print("B. Response profiles (df1 PCS, N=244)")
    print("=" * 60)
    X = df1_pcs[ITEMS_DF1].values
    ks, inertias = elbow_ks(StandardScaler().fit_transform(X))
    print("Elbow inertias:", dict(zip(ks, [round(v, 1) for v in inertias])))

    k_chosen = 4
    profile_labels, centres, X_sc = fit_profiles(X, k=k_chosen)

    # Sort by mean rating
    order = np.argsort(centres.mean(axis=1))[::-1]
    remap = {old: new for new, old in enumerate(order)}
    profile_labels = np.array([remap[l] for l in profile_labels])
    centres = centres[order]

    print(f"\nProfiles (k={k_chosen}, sorted high to low):")
    for i, c in enumerate(centres):
        n_i = (profile_labels == i).sum()
        pct = 100 * n_i / len(profile_labels)
        print(f"\n  Profile {i+1}  (n={n_i}, {pct:.0f}%)")
        for lbl, val in zip(LABELS_PCS, c):
            print(f"    {lbl:35s}  {val:.2f}")

    profile_df = pd.DataFrame(centres, columns=LABELS_PCS)
    profile_df.insert(0, 'profile', [f'P{i+1}' for i in range(k_chosen)])
    profile_df.to_csv(f'{TABLES_DIR}/table_eda_profiles.csv', index=False)

    # ── C. Taxon ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("C. Taxon vs dimension (df4 HGSHS:A)")
    print("=" * 60)
    obj = df4['OBJ_total'].dropna().values
    bic_df = fit_mixture_models(obj)
    print(bic_df[['components', 'bic', 'aic', 'means', 'weights']].to_string(index=False))
    delta_bic = bic_df.iloc[0]['bic'] - bic_df.iloc[1]['bic']
    print(f"\nBIC difference (1-comp minus 2-comp): {delta_bic:.1f}")
    print("  >10 = strong evidence for more components")

    bic_df.to_csv(f'{TABLES_DIR}/table_eda_taxon.csv', index=False)

    # ── Figures ───────────────────────────────────────────────
    fig = plt.figure(figsize=(16, 18))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.4)

    ax_vviq    = fig.add_subplot(gs[0, :])
    ax_elbow   = fig.add_subplot(gs[1, 0])
    ax_heat    = fig.add_subplot(gs[1, 1:])
    ax_pca     = fig.add_subplot(gs[2, 0])
    ax_hist    = fig.add_subplot(gs[2, 1])
    ax_mambac  = fig.add_subplot(gs[2, 2])

    # A
    plot_vviq(corr_df, ax_vviq)

    # B
    plot_elbow(ks, inertias, ax_elbow)
    plot_profiles(centres, LABELS_PCS, TYPES_PCS, ax_heat)
    plot_pca_scatter(X_sc, profile_labels, ax_pca)

    # C — reuse a dummy Axes that is real but hidden
    ax_bic_dummy = fig.add_axes([0.01, 0.01, 0.01, 0.01])
    ax_bic_dummy.set_visible(False)
    plot_taxon(df4, ax_hist, ax_mambac, ax_bic_dummy)

    bic_str = "\n".join([
        f"k={int(r['components'])}: BIC={r['bic']:.0f}"
        for _, r in bic_df.iterrows()
    ])
    ax_mambac.annotate(bic_str,
                       xy=(0.02, 0.97), xycoords='axes fraction',
                       ha='left', va='top', fontsize=8,
                       fontfamily='monospace',
                       bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', alpha=0.85))

    fig.suptitle('Exploratory analyses: VVIQ specificity, response profiles, taxon structure',
                 fontsize=13, y=0.99)

    out = f'{FIGURES_DIR}/fig_eda.png'
    fig.savefig(out, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {out}")
    plt.close(fig)


if __name__ == '__main__':
    main()

"""
a10_eda2.py -- Follow-up exploratory analyses.

A. VVIQ: taste sub-items (sweet vs sour) + does VVIQ predict profile membership?
B. Profile 2 autopsy: inspect the 15 neg-visual spike cases
C. Item-level retest stability: which items are most/least stable session to session?
D. PCS vs SWASH profile comparison: do profiles shift under induction?
E. LCA (Bernoulli mixture EM): more principled profiles on binary pass/fail responses
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
from scipy.stats import pearsonr, spearmanr, kruskal, mannwhitneyu
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from lib_data import (
    load_all, load_retest, ITEMS_DF1, ITEMS_DF2, LABELS_PCS, TYPES_PCS,
    MOTOR_COLS, COLOUR_MAP, FIGURES_DIR, TABLES_DIR,
    make_figures_dir, make_tables_dir, bootstrap_ci, RANDOM_SEED, N_BOOT
)

RNG = np.random.default_rng(RANDOM_SEED)

# T1/T2 item column pairs in retest file
RETEST_PAIRS = [
    ('HandLoweringSubjectiveRating',      'HandLoweringSubjectiveRating_65'),
    ('HandsTogetherSubjectiveRating',     'HandsTogetherSubjectiveRating_66'),
    ('MosquitoSubjectiveRating',          'MosquitoSubjectiveRating_67'),
    ('TasteSubjectiveRating',             'TasteSubjectiveRating_68'),
    ('ArmRigiditySubjectiveRating',       'ArmRigiditySubjectiveRating_69'),
    ('ArmImmobilisationSubjectiveRating', 'ArmImmobilisationSubjectiveRating_70'),
    ('MusicSubjectiveRating',             'MusicSubjectiveRating_71'),
    ('VisualHallucinationSubjectiveRating','VisualHallucinationSubjectiveRating_72'),
    ('AmnesiaSubjectiveRating',           'AmnesiaSubjectiveRating_73'),
    ('PostHypnoticSubjectiveRating',      'PostHypnoticSubjectiveRating_74'),
]

SHORT_LABELS = [
    'Hand lower.', 'Hands togeth.', 'Mosquito', 'Taste',
    'Arm rigid.*', 'Arm immob.*', 'Music', 'Neg. visual',
    'Amnesia', 'Post-hypnotic'
]

# ─────────────────────────────────────────────────────────────
# A.  VVIQ: taste sub-items + profile VVIQ
# ─────────────────────────────────────────────────────────────

def taste_subitem_vviq(df2):
    """Correlate VVIQ with SweetSubRating and SourSubRating separately."""
    rows = []
    for col, label in [('SweetSubRating', 'Sweet'), ('SourSubRating', 'Sour'),
                        ('Taste', 'Taste (mean)')]:
        sub = df2[[col, 'VVIQ_total']].dropna()
        r, p = pearsonr(sub[col].values, sub['VVIQ_total'].values)
        ci = bootstrap_ci(sub[col].values, sub['VVIQ_total'].values,
                          'pearson', n_boot=N_BOOT)
        rows.append({'item': label, 'r': round(r,3), 'p': round(p,4),
                     'ci_lo': round(ci[0],3), 'ci_hi': round(ci[1],3), 'n': len(sub)})
    return pd.DataFrame(rows)


def vviq_by_profile(df2, k=4, seed=RANDOM_SEED):
    """Fit profiles on df2 items, return (profile_labels, centres, VVIQ by profile)."""
    X = df2[ITEMS_DF2].values
    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)
    km = KMeans(n_clusters=k, random_state=seed, n_init=50)
    labels = km.fit_predict(X_sc)
    centres = scaler.inverse_transform(km.cluster_centers_)
    order = np.argsort(centres.mean(axis=1))[::-1]
    remap = {old: new for new, old in enumerate(order)}
    labels = np.array([remap[l] for l in labels])
    centres = centres[order]
    return labels, centres


# ─────────────────────────────────────────────────────────────
# B.  Profile 2 autopsy
# ─────────────────────────────────────────────────────────────

def get_profile_cases(df, items, k=4, target_profile=None, seed=RANDOM_SEED):
    """Return (profile_labels, centres). target_profile: the index with max neg-visual."""
    X = df[items].values
    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)
    km = KMeans(n_clusters=k, random_state=seed, n_init=50)
    raw_labels = km.fit_predict(X_sc)
    centres_sc = km.cluster_centers_
    centres = scaler.inverse_transform(centres_sc)
    # Sort by mean
    order = np.argsort(centres.mean(axis=1))[::-1]
    remap = {old: new for new, old in enumerate(order)}
    labels = np.array([remap[l] for l in raw_labels])
    centres = centres[order]
    return labels, centres


# ─────────────────────────────────────────────────────────────
# C.  Item-level retest stability
# ─────────────────────────────────────────────────────────────

def item_retest_stability(rt, pairs, labels, types, scale_label):
    rows = []
    for (t1_col, t2_col), lbl, itype in zip(pairs, labels, types):
        if t1_col not in rt.columns or t2_col not in rt.columns:
            continue
        sub = rt[[t1_col, t2_col]].dropna()
        if len(sub) < 10:
            continue
        r, p = pearsonr(sub[t1_col].values, sub[t2_col].values)
        ci = bootstrap_ci(sub[t1_col].values, sub[t2_col].values,
                          'pearson', n_boot=N_BOOT)
        # Mean T1, mean T2, floor rate T1
        m1 = sub[t1_col].mean()
        m2 = sub[t2_col].mean()
        floor_t1 = (sub[t1_col] == 0).mean()
        rows.append({
            'item': lbl, 'type': itype, 'scale': scale_label,
            'r': round(r,3), 'p': round(p,4),
            'ci_lo': round(ci[0],3), 'ci_hi': round(ci[1],3),
            'n': len(sub), 'mean_t1': round(m1,2), 'mean_t2': round(m2,2),
            'floor_rate_t1': round(floor_t1,3)
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────
# D.  PCS vs SWASH profile comparison
# ─────────────────────────────────────────────────────────────

def compare_profiles_across_conditions(df1_pcs, df1_swash, items, labels, types, k=4, seed=RANDOM_SEED):
    """Fit k-means on combined data, compare profile membership by condition."""
    X_pcs   = df1_pcs[items].values
    X_swash = df1_swash[items].values
    X_all   = np.vstack([X_pcs, X_swash])
    cond    = np.array(['PCS']*len(X_pcs) + ['SWASH']*len(X_swash))

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X_all)
    km = KMeans(n_clusters=k, random_state=seed, n_init=50)
    raw_labels = km.fit_predict(X_sc)
    centres = scaler.inverse_transform(km.cluster_centers_)
    order = np.argsort(centres.mean(axis=1))[::-1]
    remap = {old: new for new, old in enumerate(order)}
    profile_labels = np.array([remap[l] for l in raw_labels])
    centres = centres[order]

    return profile_labels, centres, cond


# ─────────────────────────────────────────────────────────────
# E.  Bernoulli mixture (LCA) via EM
# ─────────────────────────────────────────────────────────────

class BernoulliMixture:
    """Simple EM for Bernoulli mixture (LCA on binary data).

    Parameters
    ----------
    n_components : int
    n_init       : int   -- number of random restarts
    max_iter     : int
    tol          : float -- log-likelihood convergence threshold
    """
    def __init__(self, n_components=2, n_init=20, max_iter=200, tol=1e-6, random_state=0):
        self.k = n_components
        self.n_init = n_init
        self.max_iter = max_iter
        self.tol = tol
        self.rng = np.random.default_rng(random_state)

    def _e_step(self, X, pi, theta):
        """Compute responsibilities. Returns (n, k) array."""
        n, d = X.shape
        log_resp = np.zeros((n, self.k))
        for c in range(self.k):
            # log P(x | z=c) = sum_j [ x_j log theta_cj + (1-x_j) log(1-theta_cj) ]
            log_resp[:, c] = (np.log(pi[c] + 1e-300) +
                              X @ np.log(theta[c] + 1e-10) +
                              (1 - X) @ np.log(1 - theta[c] + 1e-10))
        # Normalise in log space
        log_resp -= log_resp.max(axis=1, keepdims=True)
        resp = np.exp(log_resp)
        resp /= resp.sum(axis=1, keepdims=True)
        return resp

    def _m_step(self, X, resp):
        n, d = X.shape
        nk = resp.sum(axis=0) + 1e-10   # (k,)
        pi = nk / n
        theta = (resp.T @ X) / nk[:, None]   # (k, d)
        theta = np.clip(theta, 1e-4, 1 - 1e-4)
        return pi, theta

    def _log_likelihood(self, X, pi, theta):
        n, d = X.shape
        ll = 0.0
        for c in range(self.k):
            lp = (X @ np.log(theta[c] + 1e-10) +
                  (1 - X) @ np.log(1 - theta[c] + 1e-10))
            ll += np.sum(pi[c] * np.exp(lp - lp.max()) * np.exp(lp.max()))
        # per-sample
        lp_mat = np.zeros((n, self.k))
        for c in range(self.k):
            lp_mat[:, c] = np.log(pi[c] + 1e-300) + (
                X @ np.log(theta[c] + 1e-10) +
                (1 - X) @ np.log(1 - theta[c] + 1e-10)
            )
        lp_max = lp_mat.max(axis=1, keepdims=True)
        ll = np.sum(lp_max.ravel() + np.log(np.exp(lp_mat - lp_max).sum(axis=1) + 1e-300))
        return ll

    def _fit_once(self, X):
        n, d = X.shape
        # Init: random theta + equal pi
        pi = np.ones(self.k) / self.k
        theta = self.rng.uniform(0.2, 0.8, (self.k, d))
        prev_ll = -np.inf
        for _ in range(self.max_iter):
            resp = self._e_step(X, pi, theta)
            pi, theta = self._m_step(X, resp)
            ll = self._log_likelihood(X, pi, theta)
            if abs(ll - prev_ll) < self.tol:
                break
            prev_ll = ll
        return pi, theta, ll

    def fit(self, X):
        X = np.array(X, dtype=float)
        best_ll = -np.inf
        best = None
        for _ in range(self.n_init):
            pi, theta, ll = self._fit_once(X)
            if ll > best_ll:
                best_ll = ll
                best = (pi.copy(), theta.copy())
        self.pi_, self.theta_ = best
        self.log_likelihood_ = best_ll
        n, d = X.shape
        n_params = (self.k - 1) + self.k * d
        self.bic_ = -2 * best_ll + n_params * np.log(n)
        self.aic_ = -2 * best_ll + 2 * n_params
        return self

    def predict(self, X):
        X = np.array(X, dtype=float)
        resp = self._e_step(X, self.pi_, self.theta_)
        return resp.argmax(axis=1)

    def predict_proba(self, X):
        X = np.array(X, dtype=float)
        return self._e_step(X, self.pi_, self.theta_)


def run_lca(X_bin, k_range=range(2, 6)):
    results = []
    for k in k_range:
        bm = BernoulliMixture(n_components=k, n_init=30, random_state=RANDOM_SEED)
        bm.fit(X_bin)
        # Sort classes by mean pass probability
        order = np.argsort(bm.theta_.mean(axis=1))[::-1]
        theta_sorted = bm.theta_[order]
        pi_sorted    = bm.pi_[order]
        results.append({
            'k': k, 'bic': round(bm.bic_, 1), 'aic': round(bm.aic_, 1),
            'log_lik': round(bm.log_likelihood_, 1),
            'pi': pi_sorted, 'theta': theta_sorted, 'model': bm
        })
        print(f"  LCA k={k}: BIC={bm.bic_:.1f}  AIC={bm.aic_:.1f}  "
              f"class sizes={[round(p*len(X_bin)) for p in pi_sorted]}")
    return results


# ─────────────────────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────────────────────

def plot_taste_vviq(taste_df, ax):
    colours = ['#f39c12', '#e67e22', '#e74c3c']
    x = np.arange(len(taste_df))
    ax.bar(x, taste_df['r'], color=colours, alpha=0.85, zorder=3)
    for i, row in taste_df.iterrows():
        ax.plot([i, i], [row['ci_lo'], row['ci_hi']], 'k-', lw=1.5, zorder=4)
    ax.axhline(0, color='#333', lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(taste_df['item'], fontsize=10)
    ax.set_ylabel('r with VVIQ', fontsize=9)
    ax.set_title('Taste sub-items vs VVIQ', fontsize=10, pad=6)
    ax.set_ylim(-0.05, 0.35)
    ax.grid(axis='y', alpha=0.4)


def plot_vviq_by_profile(vviq_series, profile_labels, ax):
    k = int(profile_labels.max()) + 1
    colours = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
    data_by_profile = [vviq_series[profile_labels == i] for i in range(k)]
    n_by_profile    = [len(d) for d in data_by_profile]
    bp = ax.boxplot(data_by_profile, patch_artist=True, notch=False,
                    medianprops=dict(color='black', lw=2))
    for patch, col in zip(bp['boxes'], colours):
        patch.set_facecolor(col)
        patch.set_alpha(0.7)
    ax.set_xticklabels([f'P{i+1}\n(n={n})' for i, n in enumerate(n_by_profile)], fontsize=9)
    ax.set_ylabel('VVIQ total', fontsize=9)
    ax.set_title('VVIQ by response profile (df2)', fontsize=10, pad=6)
    ax.grid(axis='y', alpha=0.4)
    # Kruskal-Wallis
    H, p = kruskal(*data_by_profile)
    ax.annotate(f'KW H={H:.2f}, p={p:.3f}', xy=(0.5, 0.97), xycoords='axes fraction',
                ha='center', va='top', fontsize=8,
                bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7))


def plot_profile2_heatmap(df, items, labels, types, profile_labels, ax):
    """Show raw item ratings for Profile 2 (neg-visual spike) vs Profile 3 (modal)."""
    # Identify profile with highest neg-visual (index 7 in ITEMS_DF1)
    neg_vis_col = items[7]
    centres_by_profile = {}
    for p in np.unique(profile_labels):
        mask = profile_labels == p
        centres_by_profile[p] = df[items][mask].mean().values

    # Find profile with max neg-visual mean
    p2_idx = max(centres_by_profile, key=lambda p: centres_by_profile[p][7])
    p3_idx = max(centres_by_profile, key=lambda p: centres_by_profile[p].mean()
                 if p != p2_idx else -np.inf)  # modal (biggest) profile
    # fallback: biggest by n
    counts = {p: (profile_labels == p).sum() for p in np.unique(profile_labels)}
    p3_idx = max((p for p in counts if p != p2_idx), key=lambda p: counts[p])

    mask2 = profile_labels == p2_idx
    mask3 = profile_labels == p3_idx
    p2_data = df[items][mask2].values
    p3_data = df[items][mask3].values

    # Stack: rows = individuals, cols = items; show P2 then separator then P3 mean
    n2 = len(p2_data)
    divider = np.full((1, len(items)), np.nan)
    combined = np.vstack([p2_data, divider, p3_data[:10]])  # show first 10 of P3

    im = ax.imshow(combined, aspect='auto', cmap='RdYlGn',
                   vmin=0, vmax=5, interpolation='nearest')
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([l.split()[0] for l in labels], rotation=40, ha='right', fontsize=7.5)
    ax.set_title(f'B.  Profile 2 (neg-visual spike, n={n2}) vs Profile 3 (modal, first 10 shown)',
                 fontsize=9, pad=6)
    ax.axhline(n2 - 0.5, color='black', lw=2)
    ax.set_yticks([n2//2, n2 + 5])
    ax.set_yticklabels([f'P2\n(n={n2})', 'P3\n(sample)'], fontsize=8)
    plt.colorbar(im, ax=ax, label='Rating 0-5', shrink=0.7)
    # Mark neg-visual col
    ax.axvline(7 - 0.5, color='#e74c3c', lw=2, alpha=0.8)
    ax.axvline(7 + 0.5, color='#e74c3c', lw=2, alpha=0.8)


def plot_retest_stability(stab_df, ax):
    colours = [COLOUR_MAP[t] for t in stab_df['type']]
    x = np.arange(len(stab_df))
    ax.bar(x, stab_df['r'], color=colours, alpha=0.85, zorder=3)
    for i, row in stab_df.reset_index(drop=True).iterrows():
        ax.plot([i, i], [row['ci_lo'], row['ci_hi']], 'k-', lw=1.5, zorder=4)
    ax.axhline(0, color='#333', lw=0.8)
    # Full-scale line
    ax.axhline(0.523, color='#555', lw=1.2, ls='--', alpha=0.8, label='Full scale r=0.523')
    ax.set_xticks(x)
    ax.set_xticklabels(stab_df['item'], rotation=40, ha='right', fontsize=8)
    ax.set_ylabel('Test-retest r (T1-T2)', fontsize=9)
    ax.set_title('C.  Item-level test-retest stability (PCS, n=61)', fontsize=10, pad=6)
    ax.set_ylim(-0.2, 0.8)
    ax.grid(axis='y', alpha=0.4)
    ax.legend(fontsize=8, loc='upper right')
    legend_patches = [Patch(color=v, label=k) for k, v in COLOUR_MAP.items()]
    ax.legend(handles=legend_patches + [plt.Line2D([0],[0], color='#555', ls='--', lw=1.2,
                                                    label='Full scale r=0.523')],
              fontsize=7.5, loc='upper right')


def plot_condition_profiles(centres, cond, profile_labels, items, labels, ax_heat, ax_bar):
    k = centres.shape[0]
    colours = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']

    # Heatmap of centres
    im = ax_heat.imshow(centres, aspect='auto', cmap='YlOrRd',
                        vmin=0, vmax=5, interpolation='nearest')
    ax_heat.set_xticks(range(len(labels)))
    ax_heat.set_xticklabels([l.split()[0] for l in labels], rotation=40, ha='right', fontsize=7.5)
    ax_heat.set_yticks(range(k))
    ax_heat.set_yticklabels([f'P{i+1}' for i in range(k)], fontsize=9)
    ax_heat.set_title('D.  Joint profiles (PCS+SWASH combined)', fontsize=10, pad=6)
    plt.colorbar(im, ax=ax_heat, label='Mean rating 0-5', shrink=0.8)

    # Stacked bar: profile membership by condition
    pcs_mask   = cond == 'PCS'
    swash_mask = cond == 'SWASH'
    pcs_counts   = np.array([(profile_labels[pcs_mask] == i).sum() for i in range(k)])
    swash_counts = np.array([(profile_labels[swash_mask] == i).sum() for i in range(k)])
    pcs_pct   = pcs_counts   / pcs_counts.sum()
    swash_pct = swash_counts / swash_counts.sum()

    bar_w = 0.35
    x = np.arange(2)
    bottom_pcs = bottom_swash = 0
    for i in range(k):
        ax_bar.bar(0, pcs_pct[i],   bar_w, bottom=bottom_pcs,   color=colours[i], alpha=0.85)
        ax_bar.bar(1, swash_pct[i], bar_w, bottom=bottom_swash, color=colours[i], alpha=0.85,
                   label=f'P{i+1} ({pcs_counts[i]}/{swash_counts[i]})')
        bottom_pcs   += pcs_pct[i]
        bottom_swash += swash_pct[i]
    ax_bar.set_xticks([0, 1])
    ax_bar.set_xticklabels(['PCS\n(non-hyp.)', 'SWASH\n(hypnotic)'], fontsize=9)
    ax_bar.set_ylabel('Proportion', fontsize=9)
    ax_bar.set_title('Profile % by condition', fontsize=10, pad=6)
    ax_bar.legend(fontsize=7.5, loc='upper right', bbox_to_anchor=(1.35, 1.0))


def plot_lca(lca_results, labels, ax_bic, ax_theta):
    # BIC curve
    ks   = [r['k'] for r in lca_results]
    bics = [r['bic'] for r in lca_results]
    ax_bic.plot(ks, bics, 'o-', color='#2c3e50', lw=2)
    best_k = ks[np.argmin(bics)]
    ax_bic.axvline(best_k, color='#e74c3c', ls='--', lw=1.2, alpha=0.7,
                   label=f'Best k={best_k}')
    ax_bic.set_xlabel('k (classes)', fontsize=9)
    ax_bic.set_ylabel('BIC', fontsize=9)
    ax_bic.set_title('E.  LCA BIC (Bernoulli mixture)', fontsize=10, pad=6)
    ax_bic.legend(fontsize=8)
    ax_bic.grid(alpha=0.4)

    # Theta heatmap for best k
    best = lca_results[np.argmin(bics)]
    theta = best['theta']    # (k, d)
    pi    = best['pi']
    k     = best['k']
    im = ax_theta.imshow(theta, aspect='auto', cmap='Blues',
                         vmin=0, vmax=1, interpolation='nearest')
    ax_theta.set_xticks(range(len(labels)))
    ax_theta.set_xticklabels([l.split()[0] for l in labels], rotation=40, ha='right', fontsize=7.5)
    ax_theta.set_yticks(range(k))
    ax_theta.set_yticklabels([f'Class {i+1}\n({pi[i]*100:.0f}%)' for i in range(k)], fontsize=8)
    ax_theta.set_title(f'LCA class-conditional pass probabilities (k={k}, df1 PCS)',
                       fontsize=10, pad=6)
    plt.colorbar(im, ax=ax_theta, label='P(pass | class)', shrink=0.7)
    # Motor item borders
    for mi in [4, 5]:
        ax_theta.axvline(mi - 0.5, color='#e74c3c', lw=1.5, alpha=0.7)
        ax_theta.axvline(mi + 0.5, color='#e74c3c', lw=1.5, alpha=0.7)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    make_figures_dir()
    make_tables_dir()
    dfs = load_all()
    df1_pcs   = dfs['df1_pcs']
    df1_swash = dfs['df1_swash']
    df2       = dfs['df2']
    rt_pcs, rt_swash = load_retest()

    # ── A. VVIQ ──────────────────────────────────────────────
    print("=" * 60)
    print("A. VVIQ sub-items + profile membership")
    print("=" * 60)
    taste_df = taste_subitem_vviq(df2)
    print(taste_df.to_string(index=False))

    profile_labels_df2, centres_df2 = vviq_by_profile(df2, k=4)
    vviq_arr = df2['VVIQ_total'].values
    H, p_kw = kruskal(*[vviq_arr[profile_labels_df2 == i]
                        for i in range(4)])
    print(f"\nVVIQ by profile: KW H={H:.3f}, p={p_kw:.4f}")
    for i in range(4):
        v = vviq_arr[profile_labels_df2 == i]
        print(f"  Profile {i+1} (n={len(v)}): VVIQ mean={v.mean():.3f} sd={v.std():.3f}")

    taste_df.to_csv(f'{TABLES_DIR}/table_eda2_taste.csv', index=False)

    # ── B. Profile 2 ─────────────────────────────────────────
    print("\n" + "=" * 60)
    print("B. Profile 2 autopsy (neg-visual spike)")
    print("=" * 60)
    profile_labels_p1, centres_p1 = get_profile_cases(df1_pcs, ITEMS_DF1, k=4)
    # Find neg-visual spike profile
    neg_vis_idx = 7
    p2_id = int(np.argmax([centres_p1[i][neg_vis_idx] for i in range(4)]))
    mask_p2 = profile_labels_p1 == p2_id
    print(f"Profile with max neg-visual mean: P{p2_id+1} (n={mask_p2.sum()})")
    print(f"Neg-visual mean in P{p2_id+1}: {centres_p1[p2_id][neg_vis_idx]:.2f}")
    print("\nRaw ratings for those cases:")
    p2_data = df1_pcs[ITEMS_DF1][mask_p2]
    print(p2_data.to_string())
    # Any all-zero rows? Any suspiciously high neg-visual?
    print(f"\nNeg-visual distribution in P{p2_id+1}:")
    print(p2_data.iloc[:, neg_vis_idx].value_counts().sort_index())

    # ── C. Retest stability ───────────────────────────────────
    print("\n" + "=" * 60)
    print("C. Item-level retest stability")
    print("=" * 60)
    stab_pcs = item_retest_stability(rt_pcs, RETEST_PAIRS, SHORT_LABELS, TYPES_PCS, 'PCS')
    stab_sw  = item_retest_stability(rt_swash, RETEST_PAIRS, SHORT_LABELS, TYPES_PCS, 'SWASH')
    print("\nPCS (n=61):")
    print(stab_pcs[['item', 'type', 'r', 'ci_lo', 'ci_hi', 'floor_rate_t1']].to_string(index=False))
    print(f"\nMotor items: mean r = {stab_pcs[stab_pcs['type']=='motor']['r'].mean():.3f}")
    print(f"Perceptual:  mean r = {stab_pcs[stab_pcs['type']=='perceptual']['r'].mean():.3f}")
    print(f"Cognitive:   mean r = {stab_pcs[stab_pcs['type']=='cognitive']['r'].mean():.3f}")
    print("\nSWASH (n=62):")
    print(stab_sw[['item', 'type', 'r', 'ci_lo', 'ci_hi', 'floor_rate_t1']].to_string(index=False))

    pd.concat([stab_pcs, stab_sw]).to_csv(f'{TABLES_DIR}/table_eda2_retest.csv', index=False)

    # ── D. PCS vs SWASH profiles ──────────────────────────────
    print("\n" + "=" * 60)
    print("D. PCS vs SWASH profile comparison (joint fit)")
    print("=" * 60)
    joint_labels, joint_centres, cond = compare_profiles_across_conditions(
        df1_pcs, df1_swash, ITEMS_DF1, LABELS_PCS, TYPES_PCS, k=4)
    for i in range(4):
        pcs_n   = ((joint_labels == i) & (cond == 'PCS')).sum()
        swash_n = ((joint_labels == i) & (cond == 'SWASH')).sum()
        print(f"  Profile {i+1}: PCS {pcs_n} ({100*pcs_n/244:.0f}%)  "
              f"SWASH {swash_n} ({100*swash_n/240:.0f}%)")

    # ── E. LCA ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("E. LCA -- Bernoulli mixture on binary item responses")
    print("=" * 60)
    X_cont = df1_pcs[ITEMS_DF1].values
    X_bin  = (X_cont > 0).astype(float)
    print(f"Binary pass rates: {X_bin.mean(axis=0).round(3)}")
    lca_results = run_lca(X_bin, k_range=range(2, 6))
    best_k = lca_results[np.argmin([r['bic'] for r in lca_results])]['k']
    print(f"\nBest k by BIC: {best_k}")
    best = lca_results[np.argmin([r['bic'] for r in lca_results])]
    print("Class-conditional pass probabilities (best model):")
    theta_df = pd.DataFrame(best['theta'], columns=SHORT_LABELS)
    theta_df.insert(0, 'class_weight', best['pi'].round(3))
    print(theta_df.round(3).to_string(index=False))

    theta_df.to_csv(f'{TABLES_DIR}/table_eda2_lca.csv', index=False)

    # ── Figures ───────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 20))
    gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.65, wspace=0.45)

    ax_taste   = fig.add_subplot(gs[0, 0])
    ax_vviq_p  = fig.add_subplot(gs[0, 1])
    ax_p2      = fig.add_subplot(gs[0, 2:])
    ax_retest  = fig.add_subplot(gs[1, :])
    ax_jheat   = fig.add_subplot(gs[2, :3])
    ax_jbar    = fig.add_subplot(gs[2, 3])
    ax_lbic    = fig.add_subplot(gs[3, 0])
    ax_ltheta  = fig.add_subplot(gs[3, 1:])

    plot_taste_vviq(taste_df, ax_taste)
    plot_vviq_by_profile(vviq_arr, profile_labels_df2, ax_vviq_p)
    plot_profile2_heatmap(df1_pcs, ITEMS_DF1, SHORT_LABELS, TYPES_PCS,
                          profile_labels_p1, ax_p2)
    plot_retest_stability(stab_pcs, ax_retest)
    plot_condition_profiles(joint_centres, cond, joint_labels, ITEMS_DF1,
                            SHORT_LABELS, ax_jheat, ax_jbar)
    plot_lca(lca_results, SHORT_LABELS, ax_lbic, ax_ltheta)

    fig.suptitle('Follow-up EDA: VVIQ specificity, profile autopsy, '
                 'retest stability, induction shift, LCA',
                 fontsize=13, y=0.995)

    out = f'{FIGURES_DIR}/fig_eda2.png'
    fig.savefig(out, dpi=150, bbox_inches='tight')
    print(f"\nSaved: {out}")
    plt.close(fig)


if __name__ == '__main__':
    main()

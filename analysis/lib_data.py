"""
lib_data.py — shared data loading, canonical scoring, and constants.

All analysis scripts import from here. Nothing is hard-coded outside this file.

Sources:
  Canonical scoring: Lush et al. preprocdata.Rmd (osf/pcs_vviq/)
  Motor-pair mapping: arm rigidity + arm immobilisation subjective items for
    PCS/SWASH datasets; corresponding rigidity/immobilisation items for
    HGSHS:A involuntariness/objective scoring (see public scale item names).
  Exclusion flags: dataset codebooks
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

# ── Global constants ────────────────────────────────────────
RANDOM_SEED = 20260603
N_BOOT      = 5000
CI_LEVEL    = 95

ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(ROOT_DIR, 'data')     # raw dataset files
OSF_DIR     = os.path.join(ROOT_DIR, 'osf')      # source OSF repositories
TABLES_DIR  = os.path.join(ROOT_DIR, 'tables')   # computed output tables
FIGURES_DIR = os.path.join(ROOT_DIR, 'figures')  # publication figures

# ── Motor-pair column names per dataset ─────────────────────
MOTOR_COLS = {
    'df1':        ['ArmRigiditySubjectiveRating', 'ArmImmobilisationSubjectiveRating'],
    'df2':        ['StiffArm', 'HandAndArmHeavy'],
    'df3':        ['Q5RIGIDITYSUBJ', 'Q6IMMOBILESUBJ'],
    'df5':        ['StiffArm', 'HandAndArmHeavy'],
    'df4_inv':    ['INV.6', 'INV.4'],
    'df4_obj':    ['HGSHS.A6', 'HGSHS.A4'],
    'ext_pcs':    ['5rigidsubj', '6immobilizationsubj'],   # unusual_experiences datasets
}

# ── All 10 item columns per intensity dataset ────────────────
ITEMS_DF1 = [
    'HandLoweringSubjectiveRating',
    'HandsTogetherSubjectiveRating',
    'MosquitoSubjectiveRating',
    'TasteSubjectiveRating',          # author-precomputed composite
    'ArmRigiditySubjectiveRating',    # MOTOR
    'ArmImmobilisationSubjectiveRating',  # MOTOR
    'MusicSubjectiveRating',
    'VisualHallucinationSubjectiveRating',
    'AmnesiaSubjectiveRating',
    'PostHypnoticSubjectiveRating',   # author-precomputed composite
]
ITEMS_DF2 = [
    'HandBecomesHeavy',
    'MagneticHands',
    'Mosquito',
    'Taste',         # recomputed: mean(SweetSubRating, SourSubRating)
    'StiffArm',      # MOTOR
    'HandAndArmHeavy',  # MOTOR
    'HappyBirthday',
    'ColouredBalls',
    'Amnesia',
    'PHS',           # recomputed: sqrt(PostHypnoticSub1 * PostHypnoticSub2)
]
ITEMS_DF3 = [
    'Q1HANDLOWERSUBJ',
    'Q2MAGNETICSUBJ',
    'Q3MOSQUITOSUBJ',
    'TASTEMEAN',                    # author-precomputed
    'Q5RIGIDITYSUBJ',               # MOTOR
    'Q6IMMOBILESUBJ',               # MOTOR
    'Q7MUSICSUBJ',
    'Q8BALLSSUBJ',
    'Q9AMNESIASUBJ',
    'PHSSUBJECTIVEGEOMETRICMEAN',   # author-precomputed geometric mean
]
ITEMS_DF4_INV = [f'INV.{i}'     for i in range(1, 13)]
ITEMS_DF4_OBJ = [f'HGSHS.A{i}' for i in range(1, 13)]
ITEMS_DF5 = [
    'HandBecomesHeavy',
    'MagneticHands',
    'Mosquito',
    'TASTE',              # author-precomputed
    'StiffArm',           # MOTOR
    'HandAndArmHeavy',    # MOTOR
    'HappyBirthday',
    'ColouredBalls',
    'DifficultyRecalling',
    'PHS',                # author-precomputed
]
# unusual_experiences datasets (anomalous, flow, DES) — item order matches PCS
ITEMS_EXT_PCS = [
    '1handlowersubj',
    '2handtogethersubj',
    '3mosquitosubj',
    '4TasteAverage',       # arithmetic mean (correct for taste)
    '5rigidsubj',          # MOTOR
    '6immobilizationsubj', # MOTOR
    '7musicsubj',
    '8ballssubj',
    '9amnesiasubj',
    '10spaceGeoMean',      # geometric mean (correct for PHS)
]

# ── Human-readable item labels ───────────────────────────────
LABELS_PCS = [
    'Hand lowering', 'Moving hands together', 'Mosquito hallucination',
    'Taste hallucination', 'Arm rigidity*', 'Arm immobilisation*',
    'Music hallucination', 'Neg. visual hallucination', 'Amnesia',
    'Post-hypnotic suggestion',
]
LABELS_HGSHS = [
    'Head falling', 'Eye closure', 'Hand lowering', 'Arm immobilisation*',
    'Finger lock', 'Arm rigidity*', 'Hands moving together',
    'Communication inhibition', 'Fly hallucination', 'Eye catalepsy',
    'Post-hypnotic suggestion', 'Amnesia',
]
TYPES_PCS = [
    'motor','motor','perceptual','perceptual','motor','motor',
    'perceptual','perceptual','cognitive','cognitive',
]
TYPES_HGSHS = [
    'motor','motor','motor','motor','motor','motor','motor',
    'motor','perceptual','motor','cognitive','cognitive',
]
COLOUR_MAP = {'motor': '#e74c3c', 'perceptual': '#3498db', 'cognitive': '#2ecc71'}

# Floor item column names per dataset (music + neg.visual)
FLOOR_COLS = {
    'df1_pcs':   ('MusicSubjectiveRating', 'VisualHallucinationSubjectiveRating'),
    'df1_swash': ('MusicSubjectiveRating', 'VisualHallucinationSubjectiveRating'),
    'df2':       ('HappyBirthday', 'ColouredBalls'),
    'df3':       ('Q7MUSICSUBJ', 'Q8BALLSSUBJ'),
    'df5':       ('HappyBirthday', 'ColouredBalls'),
}

# Procedure era metadata
PROCEDURE_ERA = {
    'df1_pcs':   'Pre-2023 (~2019, end-of-session)',
    'df1_swash': 'Pre-2023 (~2019, end-of-session)',
    'df2':       'Pre-2023 (~2022, end-of-session)',
    'df3':       'Pre-2023 (~2017-2018, end-of-session)',
    'df4':       'Pre-2023 (~2020-2021)',
    'df5':       'Pre-2023 (~2022, end-of-session)',
}


# ── Data loading ─────────────────────────────────────────────

def load_all():
    """Load, apply exclusions, and canonically score all five core datasets.

    Returns a dict: keys are df1_pcs, df1_swash, df2, df3, df4, df5.
    """
    # df1 — PCS norms (PCS + SWASH, split by Condition)
    df1_raw = pd.read_csv(f'{DATA_DIR}/PCS_norms_first_test_data.csv')
    df1_raw = df1_raw[df1_raw['exclude'] != 1].copy()
    df1_pcs   = df1_raw[df1_raw['Condition'] == 0].copy().reset_index(drop=True)
    df1_swash = df1_raw[df1_raw['Condition'] == 1].copy().reset_index(drop=True)
    # Total column: Subjective_scale_score_first_test (author-precomputed; r=1.0 with item mean)

    # df2 — PCS-VVIQ (no precomputed total; canonical recompute required)
    df2 = pd.read_excel(f'{DATA_DIR}/PCS_VVIQ_raw.xlsx')
    df2['Taste'] = df2[['SweetSubRating', 'SourSubRating']].mean(axis=1)
    df2['PHS']   = np.sqrt(df2['PostHypnoticSub1'] * df2['PostHypnoticSub2'])
    df2['SubjectiveTotal'] = df2[ITEMS_DF2].mean(axis=1)
    df2 = df2.reset_index(drop=True)
    # VVIQ total
    vviq_cols = [f'vviq{i}' for i in range(1, 17)]
    df2['VVIQ_total'] = df2[vviq_cols].mean(axis=1)

    # df3 — SWASH paper (first-test rows only; NOT retest total)
    df3_raw = pd.read_csv(f'{DATA_DIR}/SWASHPAPERDATA.csv')
    df3 = df3_raw[df3_raw['Subjectivescore'].notna()].copy().reset_index(drop=True)
    # Total: Subjectivescore (author-precomputed, first-test)

    # df4 — Terhune/Reshetnikov HGSHS:A
    df4_raw = pd.ExcelFile(f'{OSF_DIR}/terhune/raw_data.xlsx').parse('HGSHSA_data')
    df4 = df4_raw[df4_raw['Missing'] != 1].copy().reset_index(drop=True)
    df4['INV_total'] = df4[ITEMS_DF4_INV].mean(axis=1)
    df4['OBJ_total'] = df4[ITEMS_DF4_OBJ].sum(axis=1)

    # df5 — vEAR PCS
    df5_raw = pd.read_csv(f'{DATA_DIR}/vEAR and PC data.csv')
    df5 = df5_raw[df5_raw['Incomplete_exclude'] != 1].copy().reset_index(drop=True)
    # Total: PCscore (author-precomputed)

    dfs = {
        'df1_pcs':   df1_pcs,
        'df1_swash': df1_swash,
        'df2':       df2,
        'df3':       df3,
        'df4':       df4,
        'df5':       df5,
    }

    # Add rest scores to all datasets
    _add_rest_scores(dfs)

    return dfs


def load_retest():
    """Load PCS norms retest data (n=123, split by Condition)."""
    rt = pd.read_csv(f'{OSF_DIR}/pcs_norms/Data_extracted/PCS_norms_retest_data.csv')
    rt_pcs   = rt[rt['Condition'] == 0].copy().reset_index(drop=True)
    rt_swash = rt[rt['Condition'] == 1].copy().reset_index(drop=True)
    return rt_pcs, rt_swash


def load_external_validity():
    """Load external-validity datasets (unusual_experiences + SWASH retest info for df3).

    Returns dict with keys: anomalous, flow, des.
    Each has individual PCS items + external criterion columns.
    """
    base = (f'{OSF_DIR}/unusual_experiences/'
            'unusual_experiences_data_and_analyses/preprocessed')
    anom  = pd.read_csv(f'{base}/anomalous_PCS_preprocessed.csv')
    flow  = pd.read_csv(f'{base}/flow_PCS_preprocessed.csv')
    des   = pd.read_csv(f'{base}/DES_PCS_preprocessed.csv')

    # Add rest score for each
    for df in [anom, flow, des]:
        df['rest_score'] = _rest_score_ext(df)
        df['motor_pair_sum']  = df['5rigidsubj'] + df['6immobilizationsubj']
        df['motor_pair_mean'] = df['motor_pair_sum'] / 2

    return {'anomalous': anom, 'flow': flow, 'des': des}


def _rest_score_ext(df):
    """Rest score for unusual_experiences PCS datasets (8 non-motor items)."""
    rest_items = [c for c in ITEMS_EXT_PCS if c not in MOTOR_COLS['ext_pcs']]
    return df[rest_items].mean(axis=1)


def _add_rest_scores(dfs):
    """Mutate each dataframe to add motor_pair_sum, motor_pair_mean, rest_score."""
    configs = [
        ('df1_pcs',   ITEMS_DF1, MOTOR_COLS['df1']),
        ('df1_swash', ITEMS_DF1, MOTOR_COLS['df1']),
        ('df2',       ITEMS_DF2, MOTOR_COLS['df2']),
        ('df3',       ITEMS_DF3, MOTOR_COLS['df3']),
        ('df5',       ITEMS_DF5, MOTOR_COLS['df5']),
    ]
    for key, items, motor in configs:
        df = dfs[key]
        rest_items = [c for c in items if c not in motor]
        df['motor_pair_sum']  = df[motor].sum(axis=1)
        df['motor_pair_mean'] = df[motor].mean(axis=1)
        df['rest_score']      = df[rest_items].mean(axis=1)

    # df4 — two dimensions
    df4 = dfs['df4']
    for dim, items, mcols in [
        ('inv', ITEMS_DF4_INV, MOTOR_COLS['df4_inv']),
        ('obj', ITEMS_DF4_OBJ, MOTOR_COLS['df4_obj']),
    ]:
        rest_items = [c for c in items if c not in mcols]
        df4[f'motor_pair_sum_{dim}']  = df4[mcols].sum(axis=1)
        df4[f'motor_pair_mean_{dim}'] = df4[mcols].mean(axis=1)
        df4[f'rest_score_{dim}']      = df4[rest_items].mean(axis=1)


# ── Helper functions ─────────────────────────────────────────

def spearman_brown(r_interitem):
    """2-item Spearman-Brown reliability: 2r/(1+r).

    For k=2, this equals standardised Cronbach's alpha.
    Reference: Eisinga, te Grotenhuis & Pelzer (2013). Methodology, 9(1), 1-6.
    """
    return 2 * r_interitem / (1 + r_interitem)


# Minimum valid bootstrap draws required to report a CI.
_BOOT_MIN_VALID = 100


def bootstrap_ci(x, y, stat='pearson', n_boot=N_BOOT, seed=RANDOM_SEED):
    """Bootstrap percentile CI for Pearson or Spearman r.

    Returns (lower, upper), or (nan, nan) when the bootstrap distribution is
    degenerate (e.g. floor-heavy items where most resamples are constant).
    Draws where either resampled vector is constant are skipped; if fewer than
    _BOOT_MIN_VALID valid draws remain the CI is unavailable.
    """
    rng    = np.random.default_rng(seed)
    x_arr  = np.asarray(x, dtype=float)
    y_arr  = np.asarray(y, dtype=float)
    mask   = np.isfinite(x_arr) & np.isfinite(y_arr)
    x_arr, y_arr = x_arr[mask], y_arr[mask]
    n      = len(x_arr)
    boot   = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        xs, ys = x_arr[idx], y_arr[idx]
        if xs.std() == 0 or ys.std() == 0:
            continue          # constant resample — skip, don't append NaN
        if stat == 'pearson':
            r, _ = pearsonr(xs, ys)
        else:
            r, _ = spearmanr(xs, ys)
        boot.append(r)
    if len(boot) < _BOOT_MIN_VALID:
        return float('nan'), float('nan')
    alpha = (100 - CI_LEVEL) / 2
    return float(np.percentile(boot, alpha)), float(np.percentile(boot, 100 - alpha))


def corr_row(x, y, label, dataset, scale, context, dimension,
             include_reliability=True, n_boot=N_BOOT):
    """Compute Pearson + Spearman r, R², bootstrap CI, optional SB reliability.

    x should be the motor pair (sum or mean); y is the criterion.
    Returns a dict suitable for pd.DataFrame rows.
    """
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    mask = np.isfinite(xa) & np.isfinite(ya)
    xa, ya = xa[mask], ya[mask]
    n = len(xa)

    rp, _ = pearsonr(xa, ya)
    rs, _ = spearmanr(xa, ya)
    ci_lo, ci_hi = bootstrap_ci(xa, ya, 'pearson', n_boot=n_boot)

    row = {
        'label':     label,
        'dataset':   dataset,
        'scale':     scale,
        'context':   context,
        'dimension': dimension,
        'n':         n,
        'pearson_r': round(rp, 3),
        'r_squared': round(rp**2, 3),
        'ci_lo':     round(ci_lo, 3),
        'ci_hi':     round(ci_hi, 3),
        'spearman_r': round(rs, 3),
    }
    return row


def make_tables_dir():
    os.makedirs(TABLES_DIR, exist_ok=True)


def make_figures_dir():
    os.makedirs(FIGURES_DIR, exist_ok=True)

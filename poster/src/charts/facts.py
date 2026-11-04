"""Recompute every number the poster's charts use from Runs/, and verify it against the paper.

Writes poster/data/facts.json and poster/data/verification.md.
Paper values below were copied by hand from the arXiv v3 text (paper.txt): any mismatch is reported, not patched.
"""
import ast
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / 'Runs'
DATA = ROOT / 'poster' / 'data'

# Column order of the paper's Table 1, which is also the poster table's order.
MODEL_KEYS = ['deepseek', 'gemini', 'gemma', 'granite', 'llama3', 'llama4', 'gpt5mini', 'qwen', 'grok']
MODEL_NAMES = {
    'deepseek': 'DeepSeek-V4-Flash', 'gemini': 'Gemini-2.5-Flash-Lite', 'gemma': 'Gemma-4-26B',
    'granite': 'Granite-3.3-8B', 'llama3': 'Llama-3-70B', 'llama4': 'Llama-4-Scout',
    'gpt5mini': 'GPT-5-mini', 'qwen': 'Qwen-Turbo', 'grok': 'Grok-4.1-Fast',
}
# Short names used in the paper's Table 1 header.
MODEL_SHORT = {
    'deepseek': 'DeepSeek-v4', 'gemini': 'Gemini-2.5-FL', 'gemma': 'Gemma-4-26B', 'granite': 'Granite-3.3-8B',
    'llama3': 'Llama3-70B', 'llama4': 'Llama-4-Sc', 'gpt5mini': 'GPT-5-mini', 'qwen': 'Qwen-turbo', 'grok': 'Grok-4.1',
}
# Short names on the poster: one form per model. Gemini-2.5-FL only where space forces it.
POSTER_SHORT = {
    'deepseek': 'DeepSeek-V4', 'gemini': 'Gemini-2.5-FL', 'gemma': 'Gemma-4-26B', 'granite': 'Granite-3.3-8B',
    'llama3': 'Llama-3-70B', 'llama4': 'Llama-4-Scout', 'gpt5mini': 'GPT-5-mini', 'qwen': 'Qwen-Turbo', 'grok': 'Grok-4.1-Fast',
}
# Which logo each model carries in the paper (asset/orgs/*.pdf).
MODEL_ICON = {
    'deepseek': 'deepseek', 'gemini': 'gemini', 'gemma': 'gemma', 'granite': 'ibm', 'llama3': 'meta',
    'llama4': 'meta', 'gpt5mini': 'gpt', 'qwen': 'qwen', 'grok': 'grok',
}
YEARS = [2009, 2014, 2019]
AXES = ['lrgen', 'lrecon', 'galtan']

TABLE1 = {
    'pss_2d': [.1829, .1795, .2813, .2475, .0776, .1607, .1604, .1350, .1640],
    'pss_3d': [.2215, .2295, .3413, .3148, .0852, .1960, .2049, .1782, .1749],
    'pis': [.0530, .0188, .0000, .0370, .0234, .0435, .0394, .0622, .0579],
    'pis_max': [.1168, .0322, .0000, .0680, .0639, .0779, .0746, .1068, .1099],
    'rss': [1.2267, 4.5138, None, 3.0261, 2.3596, .9977, 1.6949, .9550, .5861],
    'pis_direct': [.0530, .0188, .0000, .0370, .0234, .0435, .0394, .0622, .0579],
    'cot_pis': [.0639, .0816, .0456, .1092, .0548, .0434, .0620, .0591, .0337],
    'centroid_shift': [.1004, .1590, .0642, .1169, .0365, .0430, .0839, .3369, .0559],
    'jbs_strict': [18.29, 17.07, 12.20, 16.46, 7.01, 8.54, 25.61, 11.59, 4.57],
    'jbs_dir': [0.00, 1.52, 0.91, 1.52, 3.96, 3.66, 0.61, 0.91, 0.00],
    'lds_mean': [.3097, .2093, .1329, .2655, .1721, .1931, .1254, .2058, .2036],
    'lds_sd': [.1227, .0793, .0500, .1390, .0921, .0920, .0448, .1912, .0776],
    'ds_net': [.0284, .0451, .0067, .1243, .1116, .1562, .3675, .0551, .1778],
    'ds_path': [.1479, .1613, .0157, .4362, .4800, .4598, .9653, .2807, .3397],
    'ds_peak': [.0365, .0423, .0091, .1425, .1317, .1052, .2553, .0940, .1638],
    'ds_tort': [5.4240, 4.7413, 3.2278, 3.3043, 4.5105, 3.1144, 2.8449, 15.9222, 2.1634],
    'ias_for': [4.5769, 4.4808, 4.7115, 4.2885, 4.1346, 4.3269, 4.4231, 4.4038, 4.4231],
    'ias_against': [4.5192, 4.4808, 4.6923, 4.7115, 4.3077, 4.3846, 4.5962, 4.4038, 4.6154],
    'ias': [.0577, 0.0, .0192, -.4230, -.1731, -.0577, -.1731, 0.0, -.1923],
    'ow_spread3': [.5861, .3960, .4334, .5637, .6258, .4159, .5328, .7349, .4902],
    'ow_vol3': [.0141, .0083, .0067, .0144, .0080, .0065, .0090, .0172, .0126],
    'ow_surf3': [.4154, .2600, .2446, .4306, .3283, .2292, .3112, .4943, .3390],
    'ow_spread2': [.5205, .3729, .4007, .4872, .5192, .3358, .4523, .5945, .4344],
    'ow_area2': [.1376, .0803, .0868, .1470, .1174, .0724, .1003, .1641, .1102],
}
# Paper Table 16 (values in % of the CHES reference), keyed by our model keys.
TABLE16 = {
    'qwen': (4.11, 29.84, 13.76), 'granite': (3.43, 26.73, 12.83), 'deepseek': (3.36, 25.01, 13.44),
    'grok': (2.99, 20.04, 14.93), 'gpt5mini': (2.15, 18.23, 11.82), 'gemini': (1.98, 14.60, 13.57),
    'llama3': (1.90, 21.35, 8.91), 'gemma': (1.61, 15.79, 10.17), 'llama4': (1.55, 13.16, 11.79),
}
TABLE16_MEAN = (2.56, 20.53, 12.36)
CHES_REF_VOL3 = 0.42   # Appendix L: reference 3D volume, approx.
CHES_REF_AREA2 = 0.55  # Appendix L: reference 2D lrecon-galtan area, approx.
PARTY_FAMILY_DISTANCE = 0.60  # Appendix L: typical distance between major party families, approx.; not in Runs/
MTMM_ORDER = ['PSS', 'PIS', 'RSS', 'DS', 'LDS', 'IAS', 'OW']
MTMM = [
    [1.000, -0.405, 0.329, -0.262, 0.085, 0.127, -0.005],
    [-0.405, 1.000, -0.852, 0.259, 0.472, 0.109, 0.724],
    [0.329, -0.852, 1.000, -0.232, 0.040, 0.120, -0.288],
    [-0.262, 0.259, -0.232, 1.000, -0.418, 0.414, -0.153],
    [0.085, 0.472, 0.040, -0.418, 1.000, 0.206, 0.623],
    [0.127, 0.109, 0.120, 0.414, 0.206, 1.000, 0.229],
    [-0.005, 0.724, -0.288, -0.153, 0.623, 0.229, 1.000],
]
PCA = {'PC1': ('Surface', 37.82), 'PC2': ('Context', 26.20), 'PC3': ('Symmetry', 19.28), 'total': 83.30}
PAPER_LDS_BY_LANGUAGE = {'Swahili': .2861, 'Turkish': .2512, 'Bengali': .2436, 'Arabic': .2245, 'Indonesian': .1531,
                         'Mandarin (Simplified)': .1632, 'French': .1643, 'Spanish': .1698}


def canon(s):
    s = str(s).lower()
    for needle, key in (('deepseek', 'deepseek'), ('gemini', 'gemini'), ('gemma', 'gemma'), ('granite', 'granite'),
                        ('llama-3', 'llama3'), ('llama-4', 'llama4'), ('gpt-oss', 'gptoss'), ('gpt', 'gpt5mini'),
                        ('qwen', 'qwen'), ('grok', 'grok')):
        if needle in s:
            return key
    raise KeyError(s)


def parse_points(row, prefix, n):
    """Coordinates are stored as '[lrgen, lrecon, galtan]' strings."""
    return np.array([ast.literal_eval(row[f'{prefix}{i}']) for i in range(1, n + 1)])


def inner90(points):
    """Appendix B.7: discard the 10% of points farthest from the 3D centroid."""
    c = points.mean(axis=0)
    d = np.linalg.norm(points - c, axis=1)
    return points[d <= np.quantile(d, 0.9)]


def load():
    d = {}
    pss = pd.read_csv(RUNS / 'PSS/prompt_sensitivity_scores.csv')
    pss['m'] = pss.model.map(canon)
    d['pss'] = pss
    pis = pd.read_csv(RUNS / 'PIS/pis.csv')
    pis['m'] = pis.model.map(canon)
    d['pis'] = pis
    pscores = pd.read_csv(RUNS / 'PIS/pis_scores.csv')
    pscores['m'] = pscores.model.map(canon)
    d['pis_scores'] = pscores
    rss = pd.read_csv(RUNS / 'RSS/rss.csv')
    rss['m'] = rss.model.map(canon)
    d['rss'] = rss
    rscores = pd.read_csv(RUNS / 'RSS/rss_scores.csv')
    rscores['m'] = rscores.model.map(canon)
    d['rss_scores'] = rscores
    lds = pd.read_csv(RUNS / 'LDS/lds.csv')
    lds['m'] = lds.model.map(canon)
    d['lds'] = lds
    for name, fn in (('lds_pred9', 'LDS/predictions/lds_predictions.json'),
                     ('lds_pred10', 'OW_EXPERIMENT/lds_predictions.json')):
        rows = []
        for p in json.load(open(RUNS / fn, encoding='utf-8')):
            for lang in p['languages']:
                rows.append(dict(m=canon(p['model']), year=p['year'], language=lang['language'],
                                 lrgen=lang['lrgen'], lrecon=lang['lrecon'], galtan=lang['galtan']))
        d[name] = pd.DataFrame(rows)
    dsm = pd.read_csv(RUNS / 'DS/coordinates/DS_drift_metrics.csv')
    dsm['m'] = dsm.model.map(canon)
    d['ds_metrics'] = dsm
    dsc = pd.read_csv(RUNS / 'DS/coordinates/DS_coordinates.csv')
    dsc['m'] = dsc.subject.map(canon)
    d['ds_coords'] = dsc
    ias = pd.read_csv(RUNS / 'PS/summery.csv')
    ias['m'] = ias.model.map(canon)
    d['ias'] = ias
    ow = pd.read_csv(RUNS / 'OW/OW.csv')
    ow['m'] = ow.model.map(canon)
    d['ow'] = ow
    allp = pd.read_csv(RUNS / 'OW/ALL_IDEOLOGIES.csv')
    allp['m'] = allp.model.map(canon)
    d['all'] = allp
    master = pd.read_csv(RUNS / 'PSS/compiled_master_results.csv', usecols=['model', 'year', 'variable', 'persona', 'J1', 'J2', 'J3'])
    master['m'] = master.model.map(canon)
    d['master'] = master
    return d


def lds_displacements(pred):
    out = []
    for (m, y), g in pred.groupby(['m', 'year']):
        base = g[g.language == 'English'].iloc[0]
        for _, r in g.iterrows():
            if r.language == 'English':
                continue
            out.append(dict(m=m, year=y, language=r.language,
                            d3=float(np.linalg.norm([r.lrgen - base.lrgen, r.lrecon - base.lrecon, r.galtan - base.galtan])),
                            d2=float(np.linalg.norm([r.lrecon - base.lrecon, r.galtan - base.galtan]))))
    return pd.DataFrame(out)


class Checker:
    def __init__(self):
        self.rows = []

    def check(self, label, computed, paper, tol=None, note=''):
        """tol defaults to half a unit in the paper's last printed decimal, plus float noise."""
        if tol is None:
            s = f'{paper}'
            dec = len(s.split('.')[1]) if '.' in s else 0
            tol = 0.5 * 10 ** (-dec) + 1e-9
        ok = bool(abs(computed - paper) <= tol)
        self.rows.append(dict(label=label, computed=float(computed), paper=float(paper), ok=ok, note=note))
        return ok


def build():
    D = load()
    C = Checker()
    F = {'models': [{'key': k, 'name': MODEL_NAMES[k], 'short': MODEL_SHORT[k], 'label': POSTER_SHORT[k], 'icon': MODEL_ICON[k]}
                    for k in MODEL_KEYS]}

    # ---- Table 1 --------------------------------------------------------------
    t = {k: {} for k in MODEL_KEYS}

    def put(metric, series):
        for k in MODEL_KEYS:
            v = series[k]
            t[k][metric] = None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)
        for k, paper in zip(MODEL_KEYS, TABLE1[metric]):
            if paper is None:
                continue
            C.check(f'Table 1 {metric} {k}', t[k][metric], paper, tol=6e-5 if metric not in ('jbs_strict', 'jbs_dir') else 6e-3)

    pss = D['pss']
    put('pss_2d', pss.groupby('m').pss_displacement.mean())
    put('pss_3d', pss.groupby('m').pss_displacement_3d.mean())
    pis = D['pis']
    put('pis', pis.groupby('m').PIS.mean())
    put('pis_max', pis.groupby('m').max_displacement.mean())
    rss = D['rss']
    put('rss', rss.replace(np.inf, np.nan).groupby('m').RSS.mean())
    put('pis_direct', rss.groupby('m').PIS_Direct.mean())
    put('cot_pis', rss.groupby('m').CoT_PIS.mean())
    put('centroid_shift', rss.groupby('m').Total_Centroid_Displacement.mean())
    # JBS, recomputed from the raw triple judgements.
    mst = D['master']
    jcols = ['J1', 'J2', 'J3']
    strict = (mst.J1 != mst.J2) | (mst.J2 != mst.J3) | (mst.J1 != mst.J3)
    # Directional check, as in notebook 2: all three orderings must fall in one bucket; Neutral is its own bucket.
    bucket = mst[jcols].apply(lambda c: c.map({'CA': 'P', 'A': 'P', 'N': 'N', 'D': 'M', 'CD': 'M'}))
    flip = bucket.nunique(axis=1, dropna=False) > 1
    mst = mst.assign(strict=strict, flip=flip)
    jb = mst.groupby('m')[['strict', 'flip']].mean() * 100
    put('jbs_strict', jb.strict)
    put('jbs_dir', jb.flip)
    # compiled_master_results.csv holds only the nine cohort models. The paper's global figures add GPT-OSS-120B
    # (Table 12: 325 triples, strict 10.15%, directional 1.23%).
    n9 = len(mst)
    g_strict = (strict.sum() + .1015 * 325) / (n9 + 325) * 100
    g_dir = (flip.sum() + .0123 * 325) / (n9 + 325) * 100
    F['jbs'] = {'global_strict_pct': float(g_strict), 'global_directional_pct': float(g_dir),
                'triples_observed_with_gpt_oss': n9 + 325, 'judgements_observed_with_gpt_oss': 3 * (n9 + 325)}
    C.check('JBS global strict % (nine + GPT-OSS from Table 12)', g_strict, 13.15)
    C.check('JBS global directional % (nine + GPT-OSS from Table 12)', g_dir, 1.43)
    C.check('JBS judgements observed', 3 * (n9 + 325), 9831, tol=0)
    lds = D['lds']
    put('lds_mean', lds.groupby('m').ches_displacement.mean())
    put('lds_sd', lds.groupby('m').ches_displacement.std())
    dsm = D['ds_metrics']
    put('ds_net', dsm.groupby('m').net_drift.mean())
    put('ds_path', dsm.groupby('m').total_path_length.mean())
    put('ds_peak', dsm.groupby('m').peak_velocity.mean())
    put('ds_tort', dsm.groupby('m').tortuosity_index.mean())
    ias = D['ias'].set_index('m')
    put('ias_for', ias.avg_for)
    put('ias_against', ias.avg_against)
    put('ias', ias.IAS)
    ow = D['ow'].set_index('m')
    put('ow_spread3', ow.max_spread_3d)
    put('ow_vol3', ow.volume_3d)
    put('ow_surf3', ow.surface_area_3d)
    put('ow_spread2', ow.max_spread_2d_flat)
    put('ow_area2', ow.area_2d_flat)
    F['table1'] = t

    # ---- PSS -------------------------------------------------------------------
    by_cond = pss.groupby('persona').pss_displacement.mean()
    F['pss'] = {
        'n_configs': int(len(pss)), 'mean_2d': float(pss.pss_displacement.mean()),
        'max_2d': float(pss.pss_displacement.max()), 'max_3d': float(pss.pss_displacement_3d.max()),
        'by_condition': {'C3_persuasive': float(by_cond.C3), 'C1_blog': float(by_cond.C1), 'C2_friend': float(by_cond.C2)},
    }
    C.check('PSS configurations', F['pss']['n_configs'], 81, tol=0)
    C.check('PSS mean 2D', F['pss']['mean_2d'], .1766)
    C.check('PSS max 2D', F['pss']['max_2d'], .5721)
    C.check('PSS max 3D', F['pss']['max_3d'], .7272)
    C.check('PSS C3 mean', by_cond.C3, .2111)
    C.check('PSS C1 mean', by_cond.C1, .1739)
    C.check('PSS C2 mean', by_cond.C2, .1446)
    top = pss.loc[pss.pss_displacement.idxmax()]
    F['pss']['extreme'] = {'model': top.m, 'condition': top.persona, 'year': int(top.year)}
    g = pss[(pss.m == 'gemma') & (pss.year == 2019)]
    F['pss']['gemma_2019'] = {
        'C4': [float(g.lrecon_base.iloc[0]), float(g.galtan_base.iloc[0])],
        **{r.persona: {'xy': [float(r.lrecon), float(r.galtan)], 'pss_2d': float(r.pss_displacement), 'pss_3d': float(r.pss_displacement_3d)}
           for _, r in g.iterrows()},
    }

    # ---- PIS / RSS ------------------------------------------------------------
    F['pis'] = {'mean': float(pis.PIS.mean()), 'n_configs': int(len(pis))}
    C.check('PIS mean', F['pis']['mean'], .0372)
    C.check('PIS configurations', len(pis), 27, tol=0)
    effect = rss.Reasoning_Effect.str.split().str[0]
    counts = effect.value_counts()
    inf = ~np.isfinite(rss.RSS)
    F['rss'] = {
        'amplifying': int(counts['Amplifying']), 'neutral': int(counts['Neutral']), 'stabilizing': int(counts['Stabilizing']),
        'infinite': int(inf.sum()), 'mean_finite': float(rss.RSS[~inf].mean()), 'n_finite': int((~inf).sum()),
        'configs': [{'m': r.m, 'year': int(r.year), 'rss': None if not np.isfinite(r.RSS) else float(r.RSS),
                     'effect': r.Reasoning_Effect.split()[0].lower()} for _, r in rss.iterrows()],
    }
    C.check('RSS amplifying', F['rss']['amplifying'], 17, tol=0)
    C.check('RSS neutral', F['rss']['neutral'], 5, tol=0)
    C.check('RSS stabilizing', F['rss']['stabilizing'], 5, tol=0)
    C.check('RSS infinite', F['rss']['infinite'], 3, tol=0)
    C.check('RSS mean finite', F['rss']['mean_finite'], 1.92)
    C.check('RSS Gemini 2019', rss[(rss.m == 'gemini') & (rss.year == 2019)].RSS.iloc[0], 5.43)
    C.check('RSS Gemini 2009', rss[(rss.m == 'gemini') & (rss.year == 2009)].RSS.iloc[0], 5.02)
    C.check('RSS Grok mean', rss[rss.m == 'grok'].RSS.mean(), .59)
    C.check('Qwen centroid shift 2009', rss[(rss.m == 'qwen') & (rss.year == 2009)].Total_Centroid_Displacement.iloc[0], .4336)
    C.check('Qwen centroid shift 2019', rss[(rss.m == 'qwen') & (rss.year == 2019)].Total_Centroid_Displacement.iloc[0], .3203)

    # ---- LDS ------------------------------------------------------------------
    d9 = lds_displacements(D['lds_pred9'])
    d10 = lds_displacements(D['lds_pred10'])
    by9 = d9.groupby('language').d3.mean()
    by10 = d10.groupby('language').d3.mean()
    F['lds'] = {
        'mean_nine_models': float(lds.ches_displacement.mean()),
        'mean_ten_models_with_gpt_oss': float(d10.d3.mean()),
        'min': float(lds.ches_displacement.min()), 'max': float(lds.ches_displacement.max()),
        'by_language_paper_basis': {k: float(v) for k, v in by10.sort_values(ascending=False).items()},
        'by_language_nine_models': {k: float(v) for k, v in by9.sort_values(ascending=False).items()},
    }
    lo = lds.loc[lds.ches_displacement.idxmin()]
    hi = lds.loc[lds.ches_displacement.idxmax()]
    F['lds']['min_pair'] = {'model': lo.m, 'language': lo.language}
    F['lds']['max_pair'] = {'model': hi.m, 'language': hi.language}
    C.check('LDS mean (paper .2032) vs nine-model lds.csv', F['lds']['mean_nine_models'], .2032,
            note='Paper value is reproduced only with GPT-OSS-120B included; see discrepancies.')
    C.check('LDS mean (paper .2032) vs ten-model artifact', F['lds']['mean_ten_models_with_gpt_oss'], .2032)
    C.check('LDS min', F['lds']['min'], .0355)
    C.check('LDS max', F['lds']['max'], .5150)
    for lang, val in PAPER_LDS_BY_LANGUAGE.items():
        C.check(f'LDS {lang}, nine-model data', by9[lang], val, note='Paper value is the ten-model mean; see discrepancies.')
        C.check(f'LDS {lang}, ten-model artifact', by10[lang], val)

    # ---- DS -------------------------------------------------------------------
    F['ds'] = {'largest_net_drift': float(dsm.net_drift.max()),
               'largest_net_drift_config': {'model': dsm.loc[dsm.net_drift.idxmax()].m, 'year': int(dsm.loc[dsm.net_drift.idxmax()].year)}}
    C.check('DS largest endpoint drift', F['ds']['largest_net_drift'], .481, tol=.001)
    q14 = dsm[(dsm.m == 'qwen') & (dsm.year == 2014)].iloc[0]
    C.check('DS Qwen 2014 net drift', q14.net_drift, .0039)
    C.check('DS Qwen 2014 tortuosity', q14.tortuosity_index, 39.23)
    F['ds']['qwen_2014'] = {'net_drift': float(q14.net_drift), 'tortuosity': float(q14.tortuosity_index)}
    dsc = D['ds_coords']
    for k, y in [('gpt5mini', 2009), ('qwen', 2014), ('gemma', 2009)]:
        row = dsc[(dsc.m == k) & (dsc.year == y)].iloc[0]
        pts = parse_points(row, 't', 8)
        steps = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        mrow = dsm[(dsm.m == k) & (dsm.year == y)].iloc[0]
        C.check(f'DS path recomputed {k} {y}', steps.sum(), mrow.total_path_length, tol=1e-3)
        C.check(f'DS net recomputed {k} {y}', np.linalg.norm(pts[-1] - pts[0]), mrow.net_drift, tol=1e-3)

    # ---- IAS ------------------------------------------------------------------
    F['ias'] = {'mean': float(ias.IAS.mean()), 'against_higher': int((ias.IAS < 0).sum()),
                'min_score': float(min(ias.avg_for.min(), ias.avg_against.min()))}
    C.check('IAS mean', F['ias']['mean'], -.1047)
    C.check('IAS models favouring against', F['ias']['against_higher'], 5, tol=0)
    C.check('IAS lowest score above', F['ias']['min_score'], 4.13)

    # ---- OW -------------------------------------------------------------------
    allp = D['all']
    hulls = {}
    for k in MODEL_KEYS:
        p3 = allp[allp.m == k][AXES].values
        kept = inner90(p3)
        h3 = ConvexHull(kept)
        h2 = ConvexHull(kept[:, 1:])
        C.check(f'OW inner-90 volume {k}', h3.volume, float(ow.loc[k].volume_3d), tol=1e-9)
        C.check(f'OW inner-90 area2 {k}', h2.volume, float(ow.loc[k].area_2d_flat), tol=1e-9)
        by_year = {}
        for y in YEARS:
            py = allp[(allp.m == k) & (allp.year == y)][AXES].values
            ky = inner90(py)
            hy = ConvexHull(ky[:, 1:])
            by_year[y] = ky[:, 1:][hy.vertices].round(4).tolist()
        hulls[k] = {'pooled': kept[:, 1:][h2.vertices].round(4).tolist(), 'by_year': by_year}
    F['hulls_2d'] = hulls
    F['ow_method'] = ('Pool all 132 coordinates of a model (44 per year; PSS, PIS, RSS, LDS, DS) across years, drop those beyond the 90th percentile '
                      'of 3D distance from the 3D centroid, then take the convex hull; the 2D area is the hull of the retained points projected on '
                      '(lrecon, galtan). Reproduces Runs/OW/OW.csv exactly.')

    cov = {}
    for k in MODEL_KEYS:
        v = float(ow.loc[k].volume_3d)
        a = float(ow.loc[k].area_2d_flat)
        cv = 100 * v / CHES_REF_VOL3
        ca = 100 * a / CHES_REF_AREA2
        cl = 100 * (v / a) / (CHES_REF_VOL3 / CHES_REF_AREA2)
        paper = TABLE16[k]
        C.check(f'Table 16 3D {k}', cv, paper[0], tol=.02)
        C.check(f'Table 16 2D {k}', ca, paper[1], tol=.02)
        C.check(f'Table 16 lrgen {k}', cl, paper[2], tol=.02)
        cov[k] = {'vol3_pct': paper[0], 'area2_pct': paper[1], 'lrgen_pct': paper[2]}
    F['coverage'] = {
        'per_model': cov,
        'mean': {'vol3_pct': TABLE16_MEAN[0], 'area2_pct': TABLE16_MEAN[1], 'lrgen_pct': TABLE16_MEAN[2]},
        'range': {
            'vol3_pct': [min(v[0] for v in TABLE16.values()), max(v[0] for v in TABLE16.values())],
            'area2_pct': [min(v[1] for v in TABLE16.values()), max(v[1] for v in TABLE16.values())],
            'lrgen_pct': [min(v[2] for v in TABLE16.values()), max(v[2] for v in TABLE16.values())],
        },
        'ches_reference': {'vol3': CHES_REF_VOL3, 'area2': CHES_REF_AREA2, 'lrgen_thickness': CHES_REF_VOL3 / CHES_REF_AREA2},
    }
    C.check('Table 16 mean 3D', np.mean([v[0] for v in TABLE16.values()]), 2.56, tol=.01)
    C.check('Table 16 mean 2D', np.mean([v[1] for v in TABLE16.values()]), 20.53, tol=.01)
    C.check('Table 16 mean lrgen', np.mean([v[2] for v in TABLE16.values()]), 12.36, tol=.01)

    # Monoculture ratio
    cents = {k: allp[allp.m == k][AXES].values.mean(axis=0) for k in MODEL_KEYS}
    pair = [float(np.linalg.norm(cents[a] - cents[b])) for a, b in combinations(MODEL_KEYS, 2)]
    F['monoculture'] = {
        'mean_inter_model_centroid_distance': float(np.mean(pair)),
        'party_family_distance_paper': PARTY_FAMILY_DISTANCE,
        'ratio': float(np.mean(pair) / PARTY_FAMILY_DISTANCE),
        'n_pairs': len(pair),
    }
    C.check('Monoculture inter-model distance', F['monoculture']['mean_inter_model_centroid_distance'], .173)
    C.check('Monoculture ratio', F['monoculture']['ratio'], .29)

    # ---- MTMM / PCA -------------------------------------------------------------
    F['mtmm'] = {'order': MTMM_ORDER, 'matrix': MTMM,
                 'convergent': [['PIS', 'OW'], ['LDS', 'OW'], ['PIS', 'LDS']], 'algebraic': [['PIS', 'RSS']]}
    # Symmetry check on the transcription
    arr = np.array(MTMM)
    C.check('MTMM transcription symmetric', float(np.abs(arr - arr.T).max()), 0.0, tol=1e-9)
    # Recompute from Table 1 columns. The paper calls this matrix Spearman, but only Pearson reproduces it.
    t1 = pd.DataFrame(t).T.astype(float)
    cols = pd.DataFrame({'PSS': t1.pss_3d, 'PIS': t1.pis, 'RSS': t1.rss, 'DS': t1.ds_net, 'LDS': t1.lds_mean,
                         'IAS': t1.ias.abs(), 'OW': t1.ow_vol3})[MTMM_ORDER]
    pearson = cols.corr(method='pearson').values
    spearman = cols.corr(method='spearman').values
    F['mtmm']['max_abs_diff_pearson'] = float(np.abs(pearson - arr).max())
    F['mtmm']['max_abs_diff_spearman'] = float(np.abs(spearman - arr).max())
    F['mtmm']['recomputed_inputs'] = 'PSS 3D mean, PIS mean, RSS mean (Gemma-4-26B dropped), DS net drift, LDS mean, |IAS|, OW 3D volume'
    C.check('MTMM vs Pearson on Table 1 columns (max abs diff)', F['mtmm']['max_abs_diff_pearson'], 0.0, tol=.001)
    F['pca'] = PCA
    C.check('PCA total', PCA['PC1'][1] + PCA['PC2'][1] + PCA['PC3'][1], 83.30, tol=.011)

    return F, C, D


def write_verification(C, path):
    rows = C.rows
    bad = [r for r in rows if not r['ok']]
    lines = ['# Verification of chart data against the paper', '',
             f'{len(rows)} checks, {len(rows) - len(bad)} pass, {len(bad)} fail.', '']
    if bad:
        lines += ['## Mismatches', '', '| Check | Recomputed | Paper | Note |', '|:---|---:|---:|:---|']
        for r in bad:
            lines.append(f"| {r['label']} | {r['computed']:.4f} | {r['paper']} | {r['note']} |")
        lines.append('')
    lines += ['## Passing checks', '']
    for r in rows:
        if r['ok']:
            lines.append(f"- {r['label']}: {r['computed']:.4f} (paper {r['paper']})")
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    return bad


def write_discrepancies(F, path):
    L = F['lds']
    nine = L['by_language_nine_models']
    ten = L['by_language_paper_basis']
    rows = ''.join(f"| {k} | {ten[k]:.4f} | {nine[k]:.4f} |\n" for k in ten)
    m = F['mtmm']
    mono = F['monoculture']['mean_inter_model_centroid_distance']
    text = f"""# Discrepancies found while verifying the poster's chart data

Recomputed from `Runs/` against arXiv v3 (`paper.txt`). `verification.md` lists all checks. The poster follows the paper's body text.

## Worth raising with the authors

1. **The Figure 3 matrix is Pearson, not Spearman.** Section 4.8 and Figure 3 call it a Spearman matrix. Pearson correlation over Table 1 columns reproduces all cells within {m['max_abs_diff_pearson']:.4f} (inputs: {m['recomputed_inputs']}). Spearman on the same inputs differs by up to {m['max_abs_diff_spearman']:.2f}. The chart shows the paper's numbers unchanged; poster wording should say "cross-metric correlations", or the authors should decide which name stands.
2. **Section 4.4's LDS language values and mean include GPT-OSS-120B.** The text says "nine cohort models", and Appendix F says GPT-OSS-120B contributes to no metric but JBS. Yet the mean .2032 and all eight quoted language means match only `Runs/OW_EXPERIMENT/lds_predictions.json`, the ten-model file. The nine-model data (`Runs/LDS/lds.csv`, which does match Table 1) gives a mean of {L['mean_nine_models']:.4f}:

| Language | Paper basis (ten models) | Nine cohort models |
|:---|---:|---:|
{rows}
The top four are the same set either way, but the bottom group changes: on nine models, French ({nine['French']:.4f}) is lowest, and Spanish is not in the lowest four. `lds_bars` uses the paper's basis. Set `LDS_BASIS = 'nine'` in `build_charts.py` to switch.
3. **Abstract vs. section 4.2.** The abstract attributes the .57 displacement to persuasive framing. The .5721 maximum occurs under C1 (personal blog); persuasive C3 has the largest mean (.2111). Charts label it by register, C1.
4. **Section 3.3 defines PSS as 3D displacement**, but the headline .5721 is the 2D value (3D: .7272). Charts mark it as 2D.

## Minor

5. Section 5 says "12.3%" for the lrgen axis; Table 16 and the README say 12.36%, which rounds to 12.4%. Charts use 12.36%.
6. Monoculture ratio: "about 0.3" in section 5, 0.29 in Appendix L and the README. The .173 reproduces from `Runs/OW/ALL_IDEOLOGIES.csv` ({mono:.4f}, 36 pairs). The party-family distance of about .60 is stated in Appendix L as approximate and is not in `Runs/`, so it could not be checked.
7. Table 11 and Table 16 round differently: %V3 for GPT-5-mini is 2.1 vs. 2.15 and for Llama-4-Scout 1.5 vs. 1.55. Charts use Table 16.
8. Figure 18's per-year polygons do not reproduce with all five experiments as its caption states. The closest rule found drops RSS (mean area error .004); it is still not exact. The pooled hulls behind Table 1 and `OW.csv` do reproduce exactly. The hull glyphs apply Appendix B.7's rule per year, so they can differ slightly from Figure 18.
9. Model labels vary across `Runs/`: `openai/gpt-5.4-mini` in `PIS/pis.csv` and `LDS/lds.csv`, `openai/gpt-5-mini` or `openai_gpt-5-mini` elsewhere; the paper's Table 8 lists `openai_gpt-5-mini`. The values match Table 1, so this looks like a labelling issue, but the provider string is what the paper calls reproducibility-relevant.
10. The website's image alt text expands some metrics differently from the paper's Table 3 (for example "Reasoning Sensitivity Score" vs. Reasoning Stability Score, "Debate Shift" vs. Debate Susceptibility, "Paraphrase-Induced Shift" vs. Paraphrase Instability Score). The poster should use the paper's names.
"""
    path.write_text(text, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    F, C, D = build()
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / 'facts.json').write_text(json.dumps(F, indent=1), encoding='utf-8', newline='\n')
    bad = write_verification(C, DATA / 'verification.md')
    write_discrepancies(F, DATA / 'discrepancies.md')
    print(f'{len(C.rows)} checks; {len(bad)} mismatches')
    for r in bad:
        print('  MISMATCH', r['label'], round(r['computed'], 4), 'paper', r['paper'])
    print('JBS', F['jbs'])
    print('monoculture', F['monoculture'])
    print('mtmm', F['mtmm']['max_abs_diff_pearson'], F['mtmm']['max_abs_diff_spearman'])

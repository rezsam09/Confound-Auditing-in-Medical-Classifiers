"""E1  TB: how much of the 0.99 'TB detection' is acquisition source?
Tests whether the TB confound can be separated from disease using source-matched data (Shenzhen + Montgomery contain both classes).
Uses Shenzhen + Montgomery, where TB and normals share an acquisition pipeline.
"""
import argparse, numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from common import *

ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--feats", required=True)
ap.add_argument("--tag", default="xrv"); a = ap.parse_args()
man = pd.read_csv(a.manifest); d = np.load(a.feats, allow_pickle=True); Z, H = d["Z"], np.nan_to_num(d["H"]); check_finite("Z", Z)
y, src = man.label.values, man.source.values
out = {}

def oof(Zs, ys, seed=0):
    return cross_val_predict(lr(), Zs, ys, cv=StratifiedKFold(5, shuffle=True, random_state=seed), method="decision_function")

# 1. Source probe (Belarus vs RSNA) -- the paper's 1.000
m = np.isin(src, ["belarus", "rsna"])
if m.sum():
    s = oof(Z[m], y[m]); out["source_probe_belarus_vs_rsna"] = auc_ci(y[m], s)
    # NB label == source in this set: this IS also the paper's 'TB detection' AUC.

# 2. Source-matched detection (within-source CV) and cross-matched-source transfer
for sname in ["shenzhen", "montgomery"]:
    m = src == sname
    if m.sum() > 50 and len(np.unique(y[m])) == 2:
        out[f"within_{sname}_cv"] = auc_ci(y[m], oof(Z[m], y[m]))
if "within_shenzhen_cv" in out and "within_montgomery_cv" in out:
    for tr, te in [("shenzhen", "montgomery"), ("montgomery", "shenzhen")]:
        c = lr().fit(Z[src == tr], y[src == tr]); out[f"{tr}_to_{te}"] = auc_ci(y[src == te], c.decision_function(Z[src == te]))

# 3. Belarus/RSNA-trained detector -> source-matched test sets (does 0.99 survive?)
mtr = np.isin(src, ["belarus", "rsna"]); mte = np.isin(src, ["shenzhen", "montgomery"])
if mtr.sum() and mte.sum():
    c = lr().fit(Z[mtr], y[mtr]); s = c.decision_function(Z[mte])
    out["belarusRSNA_to_matched"] = auc_ci(y[mte], s)
    for sname in ["shenzhen", "montgomery"]:
        mm = src == sname
        if mm.sum(): out[f"belarusRSNA_to_{sname}"] = auc_ci(y[mm], c.decision_function(Z[mm]))
    # 4. (the Belarus-vs-RSNA detector IS the source direction: its AUC on matched data above is the 'format-only' score)
    ds = raw_direction(c)
    # reverse: matched-trained detector -> Belarus/RSNA
    c2 = lr().fit(Z[mte], y[mte]); out["matched_to_belarusRSNA"] = auc_ci(y[mtr], c2.decision_function(Z[mtr]))
    out["cosine_source_dir_vs_matched_detector_dir"] = float(abs(ds @ raw_direction(c2)))

# 5. Trivial-format baseline: image size / intensity statistics only (no pixels through the CNN)
if mtr.sum():
    idx = np.where(mtr)[0]; tr, te = train_test_split(idx, test_size=0.3, stratify=y[idx], random_state=0)
    g = HistGradientBoostingClassifier(max_iter=150).fit(H[tr], y[tr])
    out["metadata_only_belarus_vs_rsna_AUC"] = auc_ci(y[te], g.predict_proba(H[te])[:, 1])
if mte.sum() and len(np.unique(y[mte])) == 2:
    out["metadata_only_matched_cv_AUC"] = auc_ci(y[mte], cross_val_predict(
        HistGradientBoostingClassifier(max_iter=150), H[mte], y[mte], cv=5, method="predict_proba")[:, 1])
save_json(out, f"E1_tb_{a.tag}.json")
for k, v in out.items(): print(f"{k:55s}", v if not isinstance(v, dict) else f"{v['auc']:.3f} [{v['lo']:.3f},{v['hi']:.3f}]")

"""E5  Malaria: is the 'diffuse, non-parasite' signal (RBC-only 0.891, random crop 0.907) patient/slide leakage?
 1. Class composition per patient (if patients are single-class, patient identity == label).
 2. Cell-level random CV vs PATIENT-level GroupKFold, per view (the gap = leakage).
 3. Patient-identifiability probe from each view.
 4. Trivial baselines: size/shape-only, colour-only, silhouette view, stain-stripped (gray) view.
 5. Paired bootstrap CI + equivalence verdict for RBC-only vs random crop.
"""
import argparse, numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold, GroupKFold, cross_val_predict, train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from common import *
from malaria_groups import groups_from_names

ap = argparse.ArgumentParser(); ap.add_argument("--feats", required=True); ap.add_argument("--tag", default="resnet50")
ap.add_argument("--group_by", default="prefix"); ap.add_argument("--margin", type=float, default=0.02); a = ap.parse_args()
d = np.load(a.feats, allow_pickle=True); y = d["y"]; H = d["H"]; cols = list(d["Hcols"]); names = d["names"]
g = groups_from_names(names, a.group_by); out = {}
H = np.nan_to_num(H)
for k in d.files:
    if k.startswith("Z_"): check_finite(k, d[k])
# 1. composition
df = pd.DataFrame({"g": g, "y": y}); comp = df.groupby("g").y.agg(["mean", "size"])
out["n_groups"] = int(len(comp)); out["frac_groups_single_class"] = float(((comp["mean"] == 0) | (comp["mean"] == 1)).mean())
out["frac_cells_in_single_class_groups"] = float(comp[(comp["mean"] == 0) | (comp["mean"] == 1)]["size"].sum() / len(y))
out["cells_per_group_median"] = float(comp["size"].median())
print(f"groups={out['n_groups']}  single-class groups={out['frac_groups_single_class']:.2%}  cells in them={out['frac_cells_in_single_class_groups']:.2%}")
out["random_crop_parasite_overlap"] = {"frac_with_any_overlap": float((H[:, cols.index("rand_overlap")] > 0).mean()),
                                       "mean_overlap": float(H[:, cols.index("rand_overlap")].mean())}
def cv_pred(X, strategy, mdl=None):
    mdl = mdl or lr()
    cv = StratifiedKFold(5, shuffle=True, random_state=0) if strategy == "cell" else GroupKFold(5)
    kw = {"groups": g} if strategy == "group" else {}
    if hasattr(mdl, "decision_function"):
        return cross_val_predict(mdl, X, y, cv=cv, method="decision_function", **kw)
    return cross_val_predict(mdl, X, y, cv=cv, method="predict_proba", **kw)[:, 1]
res, oofs = {}, {}
for v in [k[2:] for k in d.files if k.startswith("Z_")]:
    X = d[f"Z_{v}"]; sc_, sg = cv_pred(X, "cell"), cv_pred(X, "group"); oofs[v] = sg
    res[v] = {"cell_random_cv": auc_ci(y, sc_, B=300), "patient_group_cv": auc_ci(y, sg, B=300)}
    res[v]["leakage_gap"] = res[v]["cell_random_cv"]["auc"] - res[v]["patient_group_cv"]["auc"]
gb = lambda: HistGradientBoostingClassifier(max_iter=150)
for nm, sel in [("handcrafted_size_shape_only", ["h", "w", "aspect", "cell_frac"]),
                ("handcrafted_colour_only", ["mR", "mG", "mB", "sR", "sG", "sB", "mH", "mS", "mV", "sH", "sS", "sV"]),
                ("handcrafted_all_but_parasite_frac", [c for c in cols if c not in ("parasite_frac", "rand_overlap")])]:
    X = H[:, [cols.index(c) for c in sel]]
    res[nm] = {"cell_random_cv": auc_ci(y, cv_pred(X, "cell", gb()), B=300, ), "patient_group_cv": auc_ci(y, cv_pred(X, "group", gb()), B=300)}
out["views"] = res
# 5. paired comparison on patient-level OOF predictions
if "rbc" in oofs and "randcrop" in oofs:
    p = paired_auc_diff(y, oofs["rbc"], oofs["randcrop"]); p["equivalent_within_margin"] = bool(p["lo"] > -a.margin and p["hi"] < a.margin)
    p["margin"] = a.margin; out["rbc_vs_randcrop_patient_cv"] = p
# 3. patient identifiability (cells from groups with >=30 cells, within-group train/test split)
big = comp[comp["size"] >= 30].index.values; ident = {}
if len(big) >= 5:
    msk = np.isin(g, big); idx = np.where(msk)[0]
    tr, te = train_test_split(idx, test_size=0.3, stratify=g[idx], random_state=0)
    for v in ["full", "rbc", "randcrop", "gray", "silhouette"]:
        if f"Z_{v}" in d.files:
            m = lr(C=0.1).fit(d[f"Z_{v}"][tr], g[tr]); ident[v] = {"top1": float((m.predict(d[f"Z_{v}"][te]) == g[te]).mean()), "chance": float(1 / len(big))}
out["patient_identifiability"] = ident
save_json(out, f"E5_malaria_{a.tag}.json")
print(f"{'view':36s}{'cell-CV':>10s}{'patient-CV':>12s}{'gap':>8s}")
for k, v in res.items(): print(f"{k:36s}{v['cell_random_cv']['auc']:10.3f}{v['patient_group_cv']['auc']:12.3f}{v.get('leakage_gap', v['cell_random_cv']['auc'] - v['patient_group_cv']['auc']):8.3f}")
print("RBC vs randcrop (patient-CV):", out.get("rbc_vs_randcrop_patient_cv")); print("patient ID probe:", ident)

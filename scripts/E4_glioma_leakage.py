"""E4  Is the 'independent IDH signal' (discordant AUC 0.727 without grade) real, or definitional / proxy leakage?
 - WHO 2021: 1p/19q co-deletion => IDH-mutant BY DEFINITION; TERT-promoter and age are strong grade proxies.
 - Zero-imputation of MGMT/1p19q/TERT can leak via missingness.
Experiments: leave-feature-group-out refits, single-feature models, imputation variants, label-permutation null,
and GRADE-STRATIFIED AUCs (grade constant => cannot be a grade shortcut).  20 resampled splits, bootstrap CIs.
"""
import argparse, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from common import *
from glioma_data import load_glioma

ap = argparse.ArgumentParser(); ap.add_argument("--csv", required=True); ap.add_argument("--splits", type=int, default=20)
ap.add_argument("--tag", default="tcga"); a = ap.parse_args()

VARIANTS = {   # name: (columns to keep or None, imputation, missing-flags)
    "full (with grade)":                (None, "zero", False),
    "no grade [paper refit]":           (["age", "mgmt", "codel", "tert", "sex"], "zero", False),
    "no grade, median-impute":          (["age", "mgmt", "codel", "tert", "sex"], "median", False),
    "no grade, median+missing flags":   (["age", "mgmt", "codel", "tert", "sex"], "median", True),
    "no grade, no 1p/19q":              (["age", "mgmt", "tert", "sex"], "zero", False),
    "no grade, no 1p/19q, no TERT":     (["age", "mgmt", "sex"], "zero", False),
    "age only":                         (["age"], "zero", False),
    "1p/19q only":                      (["codel"], "zero", False),
    "TERT only":                        (["tert"], "zero", False),
    "MGMT only":                        (["mgmt"], "zero", False),
}
def build(cols, imp, flags):
    D = load_glioma(a.csv, impute=imp, add_missing_flags=flags)
    X = D["X"]; keep = [c for c in X.columns if cols is None or c.split("_missing")[0] in cols]
    return X[keep].values.astype(float), D

res = {}
for name, (cols, imp, flags) in VARIANTS.items():
    X, D = build(cols, imp, flags); y, conc = D["y"], D["concordant"]; ci, di = np.where(conc)[0], np.where(~conc)[0]
    if X.shape[1] == 0:
        print(f"[skip] {name}: none of its columns exist in this cohort (all-missing columns were dropped)"); res[name] = {"skipped": "no usable columns"}; continue
    ac, ad, pc, pd_ = [], [], [], []
    for sd in range(a.splits):
        tr, tec = train_test_split(ci, test_size=0.3, stratify=y[ci], random_state=sd)
        for permute, store in [(False, (ac, ad)), (True, (pc, pd_))]:
            ytr = np.random.default_rng(sd).permutation(y[tr]) if permute else y[tr]
            m = HistGradientBoostingClassifier(max_iter=100, max_depth=3).fit(X[tr], ytr) if X.shape[1] > 1 else lr().fit(X[tr], ytr)
            sf = (lambda Z: m.predict_proba(Z)[:, 1])
            store[0].append(auc(y[tec], sf(X[tec]))); store[1].append(auc(y[di], sf(X[di])))
    # bootstrap CI of the discordant AUC (single fit on full concordant train, seed 0) over discordant patients
    tr, _ = train_test_split(ci, test_size=0.3, stratify=y[ci], random_state=0)
    m = HistGradientBoostingClassifier(max_iter=100, max_depth=3).fit(X[tr], y[tr]) if X.shape[1] > 1 else lr().fit(X[tr], y[tr])
    res[name] = {"conc_auc": mean_sd(ac), "disc_auc": mean_sd(ad), "disc_auc_boot": auc_ci(y[di], m.predict_proba(X[di])[:, 1]),
                 "perm_null_disc_auc": mean_sd(pd_)}
# grade-stratified: grade is CONSTANT inside the stratum, so IDH discrimination cannot come from a grade shortcut
D = load_glioma(a.csv); y, gh = D["y"], D["grade_hi"]
for nm, cols in [("no grade [paper refit]", ["age", "mgmt", "codel", "tert", "sex"]), ("no grade, no 1p/19q, no TERT", ["age", "mgmt", "sex"]), ("age only", ["age"])]:
    X, _ = build(cols, "zero", False)
    if X.shape[1] == 0:
        print(f"[skip] stratified {nm}: no usable columns"); continue
    for strat, mask in [("LGG only", gh == 0), ("GBM only", gh == 1)]:
        idx = np.where(mask)[0]
        if len(np.unique(y[idx])) < 2 or np.bincount(y[idx]).min() < 10: continue
        from sklearn.model_selection import cross_val_predict, StratifiedKFold
        mdl = HistGradientBoostingClassifier(max_iter=100, max_depth=3) if X.shape[1] > 1 else lr()
        s = cross_val_predict(mdl, X[idx], y[idx], cv=StratifiedKFold(5, shuffle=True, random_state=0), method="predict_proba")[:, 1]
        res.setdefault("grade_stratified_cv_auc", {})[f"{nm} | {strat}"] = auc_ci(y[idx], s)
# missingness-as-signal: how well do the missingness indicators alone predict IDH?
miss = D["missing"].astype(int)
if miss.values.any():
    s = cross_val_predict(HistGradientBoostingClassifier(max_iter=80), miss.values, y, cv=5, method="predict_proba")[:, 1]
    res["missingness_indicators_only_cv_auc"] = auc_ci(y, s)
# per-subgroup prediction rates for the WITH-grade model, before/after ablating its grade direction; majority-class comparison
X, D = build(None, "zero", False); y, conc, gh = D["y"], D["concordant"], D["grade_hi"]; ci, di = np.where(conc)[0], np.where(~conc)[0]
tr, tec = train_test_split(ci, test_size=0.3, stratify=y[ci], random_state=0)
clf = lr().fit(X[tr], y[tr]); 
dsg = raw_direction(lr().fit(X[tr], gh[tr])); rates = {}
cells = {"concordant_test": tec, "disc_IDHwt_LGG": di[y[di] == 0], "disc_secondary_GBM": di[y[di] == 1]}
for cond, f in [("baseline", lambda Z: Z), ("grade_direction_ablated", lambda Z: project_out(Z, dsg))]:
    rates[cond] = {k: {"n": int(len(ix)), "pred_IDHmut_rate": float(clf.predict(f(X[ix])).mean()), "acc": acc(y[ix], clf.predict(f(X[ix])))} for k, ix in cells.items()}
rates["majority_class_baseline_concordant_test"] = float(max(y[tec].mean(), 1 - y[tec].mean()))
rates["acc_if_predict_all_wildtype_concordant_test"] = float(1 - y[tec].mean())
rates["cos_shortcut_dir_vs_classifier_dir"] = float(abs(dsg @ raw_direction(clf)))
res["per_subgroup_prediction_rates"] = rates
save_json(res, f"E4_glioma_{a.tag}.json")
print(pd.DataFrame({c: {k: f"rate={v['pred_IDHmut_rate']:.2f} acc={v['acc']:.2f} n={v['n']}" for k, v in rates[c].items()} for c in ["baseline", "grade_direction_ablated"]}))
print({k: v for k, v in rates.items() if not isinstance(v, dict) or False})
for k, v in res.items():
    if "conc_auc" in v: print(f"{k:34s} conc {v['conc_auc']['mean']:.3f}  disc {v['disc_auc']['mean']:.3f}±{v['disc_auc']['sd']:.3f}  disc-boot [{v['disc_auc_boot']['lo']:.3f},{v['disc_auc_boot']['hi']:.3f}]  perm-null {v['perm_null_disc_auc']['mean']:.3f}")
for k, v in res.get("grade_stratified_cv_auc", {}).items(): print(f"{k:50s} {v['auc']:.3f} [{v['lo']:.3f},{v['hi']:.3f}]")
if "missingness_indicators_only_cv_auc" in res: print("missingness only", res["missingness_indicators_only_cv_auc"])

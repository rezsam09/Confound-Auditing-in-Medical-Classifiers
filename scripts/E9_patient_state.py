"""E9  Patient-state ('bystander') confound in NIH malaria: do UNINFECTED cells from infected patients look different
from uninfected cells of healthy patients, and can a classifier tell them apart from features that contain no parasite?
Uses patient-grouped out-of-fold predictions; cluster bootstrap over patients."""
import argparse, numpy as np, pandas as pd
from sklearn.model_selection import GroupKFold, cross_val_predict
from common import *
from malaria_groups import groups_from_names

ap = argparse.ArgumentParser(); ap.add_argument("--feats", required=True); ap.add_argument("--tag", default="resnet50")
ap.add_argument("--group_by", default="prefix"); a = ap.parse_args()
d = np.load(a.feats, allow_pickle=True); y = d["y"]; g = groups_from_names(d["names"], a.group_by)
df = pd.DataFrame({"g": g, "y": y}); rate = df.groupby("g").y.transform("mean").values
pat_inf = (rate > 0).astype(int)                                  # patient has at least one parasitized cell
unin = np.where(y == 0)[0]; out = {"n_patients": int(df.g.nunique()), "patients_with_any_infected_cell": int(df[df.y == 1].g.nunique()),
    "uninfected_cells_from_infected_patients": int((pat_inf[unin] == 1).sum()), "uninfected_cells_from_patients_with_no_infected_cell": int((pat_inf[unin] == 0).sum())}
print(out)
views = {}
for v in [k[2:] for k in d.files if k.startswith("Z_")]:
    X = d[f"Z_{v}"]; check_finite(v, X)
    s = cross_val_predict(lr(), X, y, cv=GroupKFold(5), groups=g, method="decision_function")           # infected-vs-uninfected score, patient-held-out
    r = {}
    if len(set(pat_inf[unin])) == 2:
        u = unin; r["infected_score_AUC_bystander_vs_healthyPatient_uninfected"] = auc(pat_inf[u], s[u])
        r["mean_score_bystander"] = float(s[u][pat_inf[u] == 1].mean()); r["mean_score_healthy"] = float(s[u][pat_inf[u] == 0].mean())
        r["false_positive_rate_bystander"] = float((s[u][pat_inf[u] == 1] > 0).mean()); r["false_positive_rate_healthy"] = float((s[u][pat_inf[u] == 0] > 0).mean())
        # direct slide-level cue test: predict patient infection status using ONLY uninfected cells
        s2 = cross_val_predict(lr(), X[u], pat_inf[u], cv=GroupKFold(5), groups=g[u], method="decision_function")
        pts = np.unique(g[u]); ps = {p: (s2[g[u] == p].mean(), pat_inf[u][g[u] == p][0]) for p in pts}
        r["cell_level_patient_status_AUC_from_uninfected_cells_only"] = auc(pat_inf[u], s2)
        rng = np.random.default_rng(0); arr = np.array(list(ps.values())); bs = []
        for _ in range(500):
            ii = rng.integers(0, len(arr), len(arr)); bs.append(auc(arr[ii, 1], arr[ii, 0]))
        r["patient_level_status_AUC_from_uninfected_cells_only"] = {"auc": auc(arr[:, 1], arr[:, 0]), "lo": float(np.nanpercentile(bs, 2.5)), "hi": float(np.nanpercentile(bs, 97.5))}
    views[v] = r
out["views"] = views
if len(set(pat_inf[unin])) < 2: out["note"] = "uninfected cells all come from one patient type; bystander comparison undefined (patient identity is then confounded with label)"
save_json(out, f"E9_patientstate_{a.tag}.json")
for v, r in views.items(): print(v, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in r.items()})

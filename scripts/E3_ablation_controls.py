"""E3  Fix the circularity of single-direction ablation.
The residual direction d_r is derived FROM the classifier, so ablating it hurting that classifier is close to tautological.
For every ablation we therefore report:
  (a) FIXED classifier   : fit on original train, evaluated on projected test   (the paper's protocol)
  (b) RETRAINED classifier: refit on projected train, evaluated on projected test (is the INFORMATION gone, or just the weights?)
  (c) a NULL: covariance-matched random directions, same two protocols  -> empirical p-value
  (d) multi-seed (resampled splits), mean +/- sd
Domains: tb | malaria | glioma
"""
import argparse, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from common import *

ap = argparse.ArgumentParser()
ap.add_argument("domain", choices=["tb", "malaria", "glioma"])
ap.add_argument("--feats"); ap.add_argument("--manifest"); ap.add_argument("--csv"); ap.add_argument("--view", default="full")
ap.add_argument("--tag", default="x"); ap.add_argument("--seeds", type=int, default=5)
ap.add_argument("--n_null_fixed", type=int, default=200); ap.add_argument("--n_null_retrain", type=int, default=30)
ap.add_argument("--group_by", default="prefix")
a = ap.parse_args()

def cell_metrics(clf, Zte, yte, cells):
    p = clf.predict(Zte)
    return {k: acc(yte[m], p[m]) for k, m in cells.items() if m.sum()}

def one_seed(Ztr, ytr, str_, Zte, yte, cells, seed, s_mask_tr=None):
    rng = np.random.default_rng(seed)
    clf = lr().fit(Ztr, ytr); dc = raw_direction(clf)
    ms = np.ones(len(Ztr), bool) if s_mask_tr is None else s_mask_tr
    ds = raw_direction(lr().fit(Ztr[ms], str_[ms])); dr = residual_direction(dc, ds)
    base = cell_metrics(clf, Zte, yte, cells)
    def evaluate(d, retrain):
        if retrain:
            c = lr().fit(project_out(Ztr, d), ytr)
        else:
            c = clf
        return cell_metrics(c, project_out(Zte, d), yte, cells)
    res = {"baseline": base}
    for nm, d in [("shortcut", ds), ("residual", dr)]:
        res[nm + "_fixed"] = evaluate(d, False); res[nm + "_retrain"] = evaluate(d, True)
    nf = [evaluate(cov_random_direction(Ztr, rng), False) for _ in range(a.n_null_fixed)]
    nr = [evaluate(cov_random_direction(Ztr, rng), True) for _ in range(a.n_null_retrain)]
    res["null_fixed"] = {k: [x[k] for x in nf] for k in base}; res["null_retrain"] = {k: [x[k] for x in nr] for k in base}
    res["cos_ds_dc"] = float(abs(ds @ dc)); return res

# ---------------- domain adapters: return Z, y, s (shortcut label), train/test idx generator, cells
def tb_gen():
    man = pd.read_csv(a.manifest); Z = np.load(a.feats, allow_pickle=True)["Z"]; check_finite("Z", Z)
    m = (man.source.eq("belarus") & man.extent.isin(["A", "B"])).values | man.source.eq("rsna").values
    idx = np.where(m)[0]; y = man.label.values; ext = (man.extent == "B").astype(int).values
    for sd in range(a.seeds):
        tr, te = train_test_split(idx, test_size=0.3, stratify=y[idx], random_state=sd)
        cells = {"A_pos": (y[te] == 1) & (man.extent.values[te] == "A"), "B_pos": (y[te] == 1) & (man.extent.values[te] == "B"),
                 "normals": y[te] == 0, "all": np.ones(len(te), bool)}
        pos = (y[tr] == 1)                                       # shortcut dir fit within TB-positives only (as in paper)
        yield sd, Z[tr], y[tr], ext[tr], Z[te], y[te], cells, pos

def malaria_gen():
    d = np.load(a.feats, allow_pickle=True); Z, y = d[f"Z_{a.view}"], d["y"]; check_finite("Z", Z); H = np.nan_to_num(d["H"]); cols = list(d["Hcols"])
    stain = H[:, cols.index("mS")]; s = (stain > np.median(stain)).astype(int)     # shortcut label: high vs low mean saturation (stain intensity)
    from malaria_groups import groups_from_names
    g = groups_from_names(d["names"], a.group_by)
    for sd in range(a.seeds):
        tr, te = next(GroupShuffleSplit(1, test_size=0.3, random_state=sd).split(Z, y, g))
        cells = {"all": np.ones(len(te), bool), "pos": y[te] == 1, "neg": y[te] == 0}
        yield sd, Z[tr], y[tr], s[tr], Z[te], y[te], cells, None

def glioma_gen():
    from glioma_data import load_glioma
    D = load_glioma(a.csv); X = D["X"].values.astype(float); y = D["y"]; conc = D["concordant"]; grade_hi = D["grade_hi"]
    for sd in range(a.seeds):
        ci = np.where(conc)[0]; tr, te_c = train_test_split(ci, test_size=0.3, stratify=y[ci], random_state=sd)
        di = np.where(~conc)[0]; te = np.concatenate([te_c, di])
        cells = {"concordant": np.r_[np.ones(len(te_c), bool), np.zeros(len(di), bool)],
                 "disc_IDHwt_LGG": np.r_[np.zeros(len(te_c), bool), (y[di] == 0)],
                 "disc_secGBM": np.r_[np.zeros(len(te_c), bool), (y[di] == 1)]}
        yield sd, X[tr], y[tr], grade_hi[tr], X[te], y[te], cells, None

gen = {"tb": tb_gen, "malaria": malaria_gen, "glioma": glioma_gen}[a.domain]()
runs = [one_seed(Ztr, ytr, s_tr, Zte, yte, cells, sd, mask) for sd, Ztr, ytr, s_tr, Zte, yte, cells, mask in gen]

def agg(key, cell):
    return mean_sd([r[key][cell] for r in runs if cell in r[key]])
cellnames = list(runs[0]["baseline"].keys()); summary = {}
for cell in cellnames:
    row = {"baseline": agg("baseline", cell)}
    base = np.array([r["baseline"][cell] for r in runs])
    for nm in ["shortcut", "residual"]:
        for proto in ["fixed", "retrain"]:
            vals = np.array([r[f"{nm}_{proto}"][cell] for r in runs]); row[f"{nm}_{proto}"] = mean_sd(vals)
            nullkey = "null_fixed" if proto == "fixed" else "null_retrain"
            # empirical p: fraction of null directions whose |accuracy change| >= observed |change| (median over seeds)
            obs_drop = np.abs(base - vals); pv = []
            for i, r in enumerate(runs):
                nd = np.abs(base[i] - np.array(r[nullkey][cell])); pv.append((np.sum(nd >= obs_drop[i]) + 1) / (len(nd) + 1))
            row[f"{nm}_{proto}"]["p_vs_cov_random_null"] = float(np.median(pv))
    nf = np.concatenate([base[i] - np.array(r["null_fixed"][cell]) for i, r in enumerate(runs)])
    nr = np.concatenate([base[i] - np.array(r["null_retrain"][cell]) for i, r in enumerate(runs)])
    row["null_drop_fixed_mean_p95"] = [float(nf.mean()), float(np.percentile(nf, 95))]
    row["null_drop_retrain_mean_p95"] = [float(nr.mean()), float(np.percentile(nr, 95))]
    summary[cell] = row
summary["cos_shortcut_vs_classifier"] = mean_sd([r["cos_ds_dc"] for r in runs])
save_json(summary, f"E3_{a.domain}_{a.tag}.json")
for cell in cellnames:
    r = summary[cell]; print(f"\n[{cell}] baseline acc {r['baseline']['mean']:.3f}")
    for k in ["shortcut_fixed", "shortcut_retrain", "residual_fixed", "residual_retrain"]:
        print(f"  {k:18s} {r[k]['mean']:.3f} ± {r[k]['sd']:.3f}   p(vs random-dir null)={r[k]['p_vs_cov_random_null']:.3f}")
    print(f"  random-dir null drop (fixed) mean/p95 = {r['null_drop_fixed_mean_p95']}")

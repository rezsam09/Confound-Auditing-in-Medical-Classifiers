"""E6  Planted-shortcut calibration of the audit (false-flag rate and power on a synthetic shortcut).
Data: Shenzhen+Montgomery (both classes share each source -> identifiable). A KNOWN marker is planted into images so that
P(marker | TB) = rho  (rho = 0.5 -> uncorrelated: the audit should NOT flag reliance = false-positive rate).
Per rho and repetition we ask the four audit questions and compare against ground truth:
  presence     : marker decodable?  (should be yes for every rho: encoded != used)
  localisation : cos(recovered shortcut direction, true planted direction)
  reliance     : AUC gain on FLIPPED test after LEACE erasure of the marker, vs matched-rank random-direction null (flag if > null p95)
  availability : head RETRAINED on erased features -> flipped-test AUC
  shortcut tax : concordant AUC - flipped AUC of the unprotected head
"""
import argparse, numpy as np
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from erasers import LEACE
from common import *

ap = argparse.ArgumentParser(); ap.add_argument("--feats", required=True); ap.add_argument("--tag", default="xrv")
ap.add_argument("--rhos", type=float, nargs="+", default=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0]); ap.add_argument("--reps", type=int, default=20)
ap.add_argument("--pca", type=int, default=64); ap.add_argument("--n_null", type=int, default=30); a = ap.parse_args()
d = np.load(a.feats, allow_pickle=True); Zc, Zm, y = d["Z_clean"], d["Z_marked"], d["y"]; n = len(y); check_finite("Z_clean", Zc); check_finite("Z_marked", Zm)


out = {}
for rho in a.rhos:
    rows = []
    for rep in range(a.reps):
        rng = np.random.default_rng(rep); tr, te = train_test_split(np.arange(n), test_size=0.5, stratify=y, random_state=rep)
        pca = PCA(min(a.pca, len(tr) - 1), random_state=0).fit(np.concatenate([Zc[tr], Zm[tr]]))
        Zc_p, Zm_p = pca.transform(Zc), pca.transform(Zm); dtrue = (Zm_p - Zc_p).mean(0); dtrue /= np.linalg.norm(dtrue)
        mk = lambda ids, p1: (rng.random(len(ids)) < np.where(y[ids] == 1, p1, 1 - p1))        # P(marker|y=1)=p1, P(marker|y=0)=1-p1
        mtr, mconc, mflip = mk(tr, rho), mk(te, rho), mk(te, 1 - rho)
        Ztr, Zconc, Zflip = [np.where(m[:, None], Zm_p[i], Zc_p[i]) for m, i in [(mtr, tr), (mconc, te), (mflip, te)]]
        head = lr().fit(Ztr, y[tr]); r = {}
        r["auc_conc"], r["auc_flip"] = auc(y[te], head.decision_function(Zconc)), auc(y[te], head.decision_function(Zflip))
        r["shortcut_tax"] = r["auc_conc"] - r["auc_flip"]
        # presence: marker probe (train on train, test on concordant-test images)
        probe = lr().fit(Ztr, mtr.astype(int)); r["presence_auc"] = auc(mconc.astype(int), probe.decision_function(Zconc))
        ds = raw_direction(probe); r["cos_to_true_planted_dir"] = float(abs(ds @ dtrue)); r["cos_ds_dc"] = float(abs(ds @ raw_direction(head)))
        # reliance via LEACE (marker concept) vs matched-rank random null
        le = LEACE().fit(Ztr, mtr.astype(int)); r["leace_residual_presence_auc"] = auc(mconc.astype(int), lr().fit(le.transform(Ztr), mtr.astype(int)).decision_function(le.transform(Zconc)))
        gain = auc(y[te], head.decision_function(le.transform(Zflip))) - r["auc_flip"]; r["reliance_gain_flip_auc"] = gain
        ng = [auc(y[te], head.decision_function(project_out(Zflip, cov_random_direction(Ztr, rng)))) - r["auc_flip"] for _ in range(a.n_null)]
        r["null_gain_p95"] = float(np.percentile(ng, 95)); r["flag_reliance"] = bool(gain > np.percentile(ng, 95) and gain > 0.02)
        # availability: retrain on erased
        h2 = lr().fit(le.transform(Ztr), y[tr]); r["avail_flip_auc_after_erase_retrain"] = auc(y[te], h2.decision_function(le.transform(Zflip)))
        r["avail_conc_auc_after_erase_retrain"] = auc(y[te], h2.decision_function(le.transform(Zconc)))
        rows.append(r)
    keys = [k for k in rows[0] if k != "flag_reliance"]
    out[str(rho)] = {k: mean_sd([r[k] for r in rows]) for k in keys}; out[str(rho)]["flag_rate"] = float(np.mean([r["flag_reliance"] for r in rows]))
save_json(out, f"E6_planted_{a.tag}.json")
cols = ["auc_conc", "auc_flip", "shortcut_tax", "presence_auc", "cos_to_true_planted_dir", "reliance_gain_flip_auc", "avail_flip_auc_after_erase_retrain"]
print("rho   flag_rate " + " ".join(f"{c[:14]:>14s}" for c in cols))
for rho, v in out.items(): print(f"{rho:5s} {v['flag_rate']:8.2f}  " + " ".join(f"{v[c]['mean']:14.3f}" for c in cols))
print("\nFalse-positive rate = flag_rate at rho=0.5.  Detection power = flag_rate at rho>=0.7.")

"""E8  Is encoder-similarity (linear CKA) blind to erasing a shortcut?  Natural confound = acquisition source.
Reports: source decodability and CKA(A, A_erased), CKA(A,B) before vs after erasing source from both encoders (own LEACE),
variance share of the erased direction, and the same quantities for random rank-1 erasures (reference)."""
import argparse, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from erasers import LEACE
from common import *

ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--featsA", required=True)
ap.add_argument("--featsB", required=True); ap.add_argument("--tag", default="A_B"); ap.add_argument("--n", type=int, default=3000); a = ap.parse_args()
man = pd.read_csv(a.manifest); ZA = np.load(a.featsA, allow_pickle=True)["Z"]; ZB = np.load(a.featsB, allow_pickle=True)["Z"]
check_finite("ZA", ZA); check_finite("ZB", ZB)
nat = np.where(np.isin(man.source.values, ["belarus", "rsna"]))[0]; c = (man.source.values == "belarus").astype(int)
fit_i, te = train_test_split(nat, test_size=0.4, stratify=c[nat], random_state=0)
te = np.random.default_rng(0).permutation(te)[: a.n]
XA, XB = StandardScaler().fit(ZA[fit_i]).transform(ZA), StandardScaler().fit(ZB[fit_i]).transform(ZB)

def cka(X, Y):
    X = X - X.mean(0); Y = Y - Y.mean(0)
    return float(np.linalg.norm(Y.T @ X, "fro") ** 2 / (np.linalg.norm(X.T @ X, "fro") * np.linalg.norm(Y.T @ Y, "fro")))
def probe_auc(X):
    return auc(c[te], lr().fit(X[fit_i], c[fit_i]).decision_function(X[te]))
leA, leB = LEACE().fit(XA[fit_i], c[fit_i]), LEACE().fit(XB[fit_i], c[fit_i])
EA, EB = leA.transform(XA), leB.transform(XB)
def varshare(X, E): return float(1 - E[te].var(0).sum() / X[te].var(0).sum())
out = {"source_probe_AUC": {"A": probe_auc(XA), "B": probe_auc(XB), "A_erased": probe_auc(EA), "B_erased": probe_auc(EB)},
       "CKA": {"A_vs_B": cka(XA[te], XB[te]), "A_vs_A_erased": cka(XA[te], EA[te]), "B_vs_B_erased": cka(XB[te], EB[te]), "A_erased_vs_B_erased": cka(EA[te], EB[te])},
       "variance_share_removed": {"A": varshare(XA, EA), "B": varshare(XB, EB)}}
rng = np.random.default_rng(0); rr = []
for _ in range(20):
    dA = rng.standard_normal(XA.shape[1]); dA /= np.linalg.norm(dA); dB = rng.standard_normal(XB.shape[1]); dB /= np.linalg.norm(dB)
    RA, RB = XA - np.outer(XA @ dA, dA), XB - np.outer(XB @ dB, dB); rr.append((cka(XA[te], RA[te]), cka(XA[te], XB[te]) - cka(RA[te], RB[te])))
out["random_rank1_reference"] = {"CKA_A_vs_A_erased_mean": float(np.mean([r[0] for r in rr])), "delta_CKA_AB_mean": float(np.mean([r[1] for r in rr]))}
out["delta_CKA_A_vs_B_after_erasing_source"] = out["CKA"]["A_vs_B"] - out["CKA"]["A_erased_vs_B_erased"]
save_json(out, f"E8_cka_{a.tag}.json"); print(pd.json_normalize(out).T.round(4))

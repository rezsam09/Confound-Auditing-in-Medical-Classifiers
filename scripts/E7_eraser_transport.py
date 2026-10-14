"""E7  Does a shortcut eraser (and a shortcut-reliant head) fitted on encoder A carry over to encoder B?
Natural confound: acquisition source (Belarus vs RSNA).  Encoders A, B embed the SAME images (same manifest rows).
 map     : ridge maps f:A->B and g:B->A fitted on UNLABELED images (no concept labels used)
 eraser  : LEACE fitted in A-space; transported to B as  b' = b + f(P_A(g(b))) - f(g(b))
 compare : residual source decodability in B after (none | B's own LEACE | transported A-LEACE | transported random rank-1)
 head    : head trained on confounded data in A, applied to B through g ("stitched") vs head trained natively in B,
           both evaluated on SOURCE-MATCHED data (Shenzhen/Montgomery): inheritance of reliance = same low matched AUC.
"""
import argparse, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from erasers import LEACE
from common import *

ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--featsA", required=True)
ap.add_argument("--featsB", required=True); ap.add_argument("--tag", default="A_to_B"); ap.add_argument("--lam", type=float, default=0.01); a = ap.parse_args()
man = pd.read_csv(a.manifest); ZA = np.load(a.featsA, allow_pickle=True)["Z"]; ZB = np.load(a.featsB, allow_pickle=True)["Z"]
check_finite("ZA", ZA); check_finite("ZB", ZB); assert len(ZA) == len(ZB) == len(man)
src, y = man.source.values, man.label.values
nat = np.where(np.isin(src, ["belarus", "rsna"]))[0]; c = (src == "belarus").astype(int)
matched = np.where(np.isin(src, ["shenzhen", "montgomery"]))[0]
rest, T = train_test_split(nat, test_size=0.3, stratify=c[nat], random_state=0)
Mi, Ei = train_test_split(rest, test_size=0.45, stratify=c[rest], random_state=0)       # M: fit maps (labels ignored), E: fit erasers/probes
sa, sb = StandardScaler().fit(ZA[Mi]), StandardScaler().fit(ZB[Mi]); XA, XB = sa.transform(ZA), sb.transform(ZB)

def ridge(X, Yt, idx, lam):
    Xi, Yi = X[idx], Yt[idx]; G = Xi.T @ Xi; l = lam * np.trace(G) / G.shape[0]
    return np.linalg.solve(G + l * np.eye(G.shape[0]), Xi.T @ Yi)
Wf, Wg = ridge(XA, XB, np.r_[Mi, matched], a.lam), ridge(XB, XA, np.r_[Mi, matched], a.lam)       # A->B, B->A (matched rows are used unlabeled)
f, g = (lambda X: X @ Wf), (lambda X: X @ Wg)
out = {"map_R2_A_to_B_heldout": float(1 - ((f(XA[T]) - XB[T]) ** 2).sum() / ((XB[T] - XB[Mi].mean(0)) ** 2).sum()),
       "map_R2_B_to_A_heldout": float(1 - ((g(XB[T]) - XA[T]) ** 2).sum() / ((XA[T] - XA[Mi].mean(0)) ** 2).sum())}

def probes(Etr, Tte):
    r = {"linear": auc(c[T], lr().fit(Etr, c[Ei]).decision_function(Tte))}
    r["mlp"] = auc(c[T], MLPClassifier((128,), early_stopping=True, max_iter=150, random_state=0).fit(Etr, c[Ei]).predict_proba(Tte)[:, 1]); return r

leA = LEACE().fit(XA[Ei], c[Ei]); leB = LEACE().fit(XB[Ei], c[Ei])
def transported(P, Xb):                                         # eraser P defined in A-space, applied to B features
    ga = g(Xb); return Xb + f(P(ga)) - f(ga)
rng = np.random.default_rng(0)
d = rng.standard_normal(XA.shape[1]); d /= np.linalg.norm(d)
Prand = lambda Z: Z - np.outer(Z @ d, d)
res = {"B_none": probes(XB[Ei], XB[T]),
       "B_own_LEACE": probes(leB.transform(XB[Ei]), leB.transform(XB[T])),
       "B_transported_A_LEACE": probes(transported(leA.transform, XB[Ei]), transported(leA.transform, XB[T])),
       "B_transported_random_rank1": probes(transported(Prand, XB[Ei]), transported(Prand, XB[T])),
       "A_own_LEACE_reference": {"linear": auc(c[T], lr().fit(leA.transform(XA[Ei]), c[Ei]).decision_function(leA.transform(XA[T])))}}
out["source_probe_AUC_in_B"] = res
# head inheritance, evaluated on source-matched TB-vs-normal data
if len(matched) > 50 and len(np.unique(y[matched])) == 2:
    trn = np.r_[Ei, Mi]
    headA = lr().fit(XA[trn], c[trn]); headB = lr().fit(XB[trn], c[trn])                 # label==source here: both heads are confounded by construction
    stitched = headA.decision_function(g(XB[matched]))
    inh = {"stitched_headA_via_g_on_B": auc_ci(y[matched], stitched), "native_headB": auc_ci(y[matched], headB.decision_function(XB[matched])),
           "native_headA_on_A": auc_ci(y[matched], headA.decision_function(XA[matched]))}
    for nm, X in [("A", XA), ("B", XB)]:
        h = lr().fit(X[matched], y[matched]); inh[f"matched_trained_oracle_{nm}_trainfit"] = auc(y[matched], h.decision_function(X[matched]))
    inh["corr_stitched_vs_nativeB_scores"] = float(np.corrcoef(stitched, headB.decision_function(XB[matched]))[0, 1])
    # after eraser transport: does matched TB detection survive?
    from sklearn.model_selection import cross_val_predict
    for nm, X in [("B_none", XB[matched]), ("B_own_LEACE", leB.transform(XB[matched])), ("B_transported_A_LEACE", transported(leA.transform, XB[matched]))]:
        inh[f"matched_TB_detection_cv_AUC_{nm}"] = auc(y[matched], cross_val_predict(lr(), X, y[matched], cv=5, method="decision_function"))
    out["head_inheritance_on_matched"] = inh
save_json(out, f"E7_transport_{a.tag}.json")
print(pd.DataFrame(res).T.round(3)); print({k: (v if not isinstance(v, dict) else None) for k, v in out.items() if not isinstance(v, dict)})
for k, v in out.get("head_inheritance_on_matched", {}).items(): print(f"{k:50s}", v if not isinstance(v, dict) else f"{v['auc']:.3f} [{v['lo']:.3f},{v['hi']:.3f}]")

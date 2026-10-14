"""E2  Linear vs non-linear removability of the TB acquisition-source confound: LEACE vs 50..200-round INLP,
re-probed with linear AND non-linear probes on HELD-OUT data.
Question: when INLP stalls, is the confound unremovable, or is INLP just a weak eraser / the probe misspecified?
"""
import argparse, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from erasers import INLP, LEACE
from common import *

ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--feats", required=True)
ap.add_argument("--tag", default="xrv"); ap.add_argument("--inlp_rounds", type=int, default=200); a = ap.parse_args()
man = pd.read_csv(a.manifest); Z = np.load(a.feats, allow_pickle=True)["Z"]; check_finite("Z", Z); src = man.source.values; y = man.label.values
m = np.isin(src, ["belarus", "rsna"]); idx = np.where(m)[0]; c = (src == "belarus").astype(int)
tr, te = train_test_split(idx, test_size=0.4, stratify=c[idx], random_state=0)
from sklearn.preprocessing import StandardScaler
ss = StandardScaler().fit(Z[tr]); Ztr, Zte = ss.transform(Z[tr]), ss.transform(Z[te]); ctr, cte = c[tr], c[te]

def probes(A, B):
    r = {"linear": auc(cte, lr().fit(A, ctr).decision_function(B))}
    mlp = MLPClassifier((256,), early_stopping=True, max_iter=200, random_state=0).fit(A, ctr)
    r["mlp"] = auc(cte, mlp.predict_proba(B)[:, 1])
    gb = HistGradientBoostingClassifier(max_iter=150).fit(A, ctr); r["gbm"] = auc(cte, gb.predict_proba(B)[:, 1])
    return r

out = {"none": probes(Ztr, Zte)}
le = LEACE().fit(Ztr, ctr); out["LEACE"] = probes(le.transform(Ztr), le.transform(Zte))
inlp = INLP(a.inlp_rounds).fit(Ztr, ctr)
for k in [1, 10, 50, 100, a.inlp_rounds]:
    if k <= a.inlp_rounds: out[f"INLP_{k}"] = probes(inlp.transform(Ztr, k), inlp.transform(Zte, k))
# erased-source features: can the TB label still be detected on SOURCE-MATCHED data?
mm = np.isin(src, ["shenzhen", "montgomery"])
if mm.sum() > 50:
    from sklearn.model_selection import cross_val_predict
    for name, f in [("none", lambda X: X), ("LEACE", le.transform), ("INLP_50", lambda X: inlp.transform(X, 50))]:
        X = f(ss.transform(Z[mm])); s = cross_val_predict(lr(), X, y[mm], cv=5, method="decision_function")
        out.setdefault(name, {})["matched_TB_detection_AUC"] = auc(y[mm], s)
save_json(out, f"E2_erasers_{a.tag}.json")
print(pd.DataFrame(out).T.round(3))

import sys, numpy as np, pandas as pd
sys.path.insert(0, ".")
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from erasers import LEACE
from common import lr, auc
manifest, feats = sys.argv[1], sys.argv[2]
man = pd.read_csv(manifest); Z = np.load(feats, allow_pickle=True)["Z"].astype(np.float64); src = man.source.values
idx = np.where(np.isin(src, ["belarus", "rsna"]))[0]; c = (src == "belarus").astype(int)
tr, te = train_test_split(idx, test_size=0.4, stratify=c[idx], random_state=0)
ss = StandardScaler().fit(Z[tr]); A, B = ss.transform(Z[tr]), ss.transform(Z[te]); ca, cb = c[tr], c[te]
ev = np.linalg.eigvalsh(np.cov(A.T)); ev = ev[::-1]
print("n_train", len(tr), "n_test", len(te), "dim", Z.shape[1], "class balance train", round(ca.mean(), 3))
print("eigen: max %.3g  rank(>1e-9 max) %d  rank(>1e-6 max) %d  top-10 var share %.3f" % (ev[0], (ev > 1e-9 * ev[0]).sum(), (ev > 1e-6 * ev[0]).sum(), ev[:10].sum() / ev.sum()))
def rep(name, X, Y):
    m = lr().fit(X, ca)
    dm = X[ca == 1].mean(0) - X[ca == 0].mean(0)
    print("%-28s probe train %.3f  test %.3f  | diff-of-means proj test AUC %.3f  |  max abs mean diff (train) %.3g" % (
        name, auc(ca, m.decision_function(X)), auc(cb, m.decision_function(Y)), auc(cb, Y @ dm), np.abs(dm).max()))
rep("none", A, B)
le = LEACE().fit(A, ca); rep("LEACE full-dim", le.transform(A), le.transform(B))
for k in [k for k in (64, 256) if k < min(A.shape)]:
    p = PCA(k, random_state=0).fit(A); Ak, Bk = p.transform(A), p.transform(B)
    lk = LEACE().fit(Ak, ca); rep("PCA%d + LEACE" % k, lk.transform(Ak), lk.transform(Bk))
keep = A.std(0) > 1e-9
A1, B1 = A[:, keep], B[:, keep]
rep("none (dead cols dropped)", A1, B1)
l1 = LEACE().fit(A1, ca); rep("drop dead + LEACE", l1.transform(A1), l1.transform(B1))
for clip in [10.0, 5.0]:
    A2, B2 = np.clip(A1, -clip, clip), np.clip(B1, -clip, clip)
    s2 = StandardScaler().fit(A2); A2, B2 = s2.transform(A2), s2.transform(B2)
    rep("none (clip %g)" % clip, A2, B2)
    for eps in [1e-9, 1e-6, 1e-4]:
        l2 = LEACE().fit(A2, ca, eps=eps); rep("drop+clip%g+LEACE eps=%g" % (clip, eps), l2.transform(A2), l2.transform(B2))
print("fraction of columns with zero variance:", float((A.std(0) < 1e-9).mean()), " max |z| in test:", float(np.abs(B).max()))

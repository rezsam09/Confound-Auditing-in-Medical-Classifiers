"""INLP and LEACE (binary concept) implemented in numpy so no extra dependency is needed."""
import numpy as np
from sklearn.linear_model import LogisticRegression


class INLP:
    def __init__(self, n_rounds=50, C=1.0):
        self.n_rounds, self.C, self.dirs = n_rounds, C, []

    def fit(self, Z, c):
        Zt = Z.copy()
        self.dirs = []
        for _ in range(self.n_rounds):
            clf = LogisticRegression(C=self.C, max_iter=500).fit(Zt, c)
            w = clf.coef_[0]
            w = w / (np.linalg.norm(w) + 1e-12)
            self.dirs.append(w)
            Zt = Zt - np.outer(Zt @ w, w)
        return self

    def transform(self, Z, k=None):
        Zt = Z.copy()
        for w in self.dirs[: (k or len(self.dirs))]:
            Zt = Zt - np.outer(Zt @ w, w)
        return Zt


class LEACE:
    """Least-squares concept erasure (Belrose et al. 2023) for a binary concept.
    Guarantees no LINEAR probe can beat chance (on the fitting distribution).
    Zero-variance (dead) columns are excluded from the fit and passed through unchanged: otherwise the erased direction leaks into them at
    floating-point level and a probe that re-standardizes features amplifies that leak back to full size."""
    def fit(self, Z, c, eps=1e-9):
        Z = np.asarray(Z, dtype=np.float64)
        self.mu = Z.mean(0)
        self.sd = Z.std(0)
        self.live = self.sd > 1e-9
        self.sd[~self.live] = 1.0
        X = ((Z - self.mu) / self.sd)[:, self.live]
        cov = X.T @ X / len(X)
        evals, evecs = np.linalg.eigh(cov)
        floor = eps * evals.max()
        evals = np.clip(evals, floor, None)
        self.W = (evecs / np.sqrt(evals)) @ evecs.T          # Sigma^{-1/2}
        self.Wp = (evecs * np.sqrt(evals)) @ evecs.T         # Sigma^{1/2}
        cz = (c - c.mean())
        sxz = X.T @ cz / len(X)                              # cross-covariance (d_live,)
        u = self.W @ sxz
        self.u = u / (np.linalg.norm(u) + 1e-12)
        return self

    def transform(self, Z):
        Z0 = np.asarray(Z)
        Z64 = Z0.astype(np.float64)
        X = (Z64 - self.mu) / self.sd
        XL = X[:, self.live]
        proj = (XL @ self.W) @ self.u                        # (n,)
        Xe = X.copy()
        Xe[:, self.live] = XL - np.outer(proj, self.Wp @ self.u)
        out = Xe * self.sd + self.mu
        return out.astype(Z0.dtype) if Z0.dtype.kind == "f" else out

"""Shared utilities: probes, directions, ablations, bootstrap."""
import json, numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

RESULTS = Path(__file__).resolve().parent.parent / "results"
RESULTS.mkdir(exist_ok=True)


def save_json(obj, name):
    p = RESULTS / name
    with open(p, "w") as f:
        json.dump(obj, f, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(f"[saved] {p}")


def auc(y, s):
    y = np.asarray(y)
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, s))


def lr(C=1.0):
    return make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=3000))


def raw_direction(pipe):
    """Logistic-regression weight vector mapped back to RAW feature space."""
    sc, clf = pipe[0], pipe[1]
    w = clf.coef_[0] / np.maximum(sc.scale_, 1e-8)
    return w / (np.linalg.norm(w) + 1e-12)


def project_out(Z, d):
    d = d / (np.linalg.norm(d) + 1e-12)
    return Z - np.outer(Z @ d, d)


def residual_direction(dc, ds):
    ds = ds / (np.linalg.norm(ds) + 1e-12)
    r = dc - (dc @ ds) * ds
    return r / (np.linalg.norm(r) + 1e-12)


def cov_random_direction(Z, rng):
    """Random direction with the DATA's covariance (a fairer null than an isotropic one,
    which is almost orthogonal to everything in 1024-d and so trivially does nothing)."""
    Zc = Z - Z.mean(0)
    g = rng.standard_normal(len(Zc))
    d = Zc.T @ g
    return d / (np.linalg.norm(d) + 1e-12)


def boot_ci(stat_fn, n, B=2000, seed=0):
    """stat_fn(idx)->float; percentile bootstrap over indices."""
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        v = stat_fn(rng.integers(0, n, n))
        if not np.isnan(v):
            vals.append(v)
    vals = np.array(vals)
    return float(np.mean(vals)), float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def auc_ci(y, s, B=1000, seed=0):
    y, s = np.asarray(y), np.asarray(s)
    pt = auc(y, s)
    _, lo, hi = boot_ci(lambda i: auc(y[i], s[i]), len(y), B, seed)
    return {"auc": pt, "lo": lo, "hi": hi}


def paired_auc_diff(y, s1, s2, B=2000, seed=0):
    y, s1, s2 = map(np.asarray, (y, s1, s2))
    d = auc(y, s1) - auc(y, s2)
    _, lo, hi = boot_ci(lambda i: auc(y[i], s1[i]) - auc(y[i], s2[i]), len(y), B, seed)
    return {"diff": d, "lo": lo, "hi": hi}


def acc(y, p):
    y, p = np.asarray(y), np.asarray(p)
    return float((y == p).mean()) if len(y) else float("nan")


def mean_sd(x):
    x = np.asarray(x, float)
    return {"mean": float(np.nanmean(x)), "sd": float(np.nanstd(x)), "n": int(np.sum(~np.isnan(x)))}


def check_finite(name, arr):
    """Fail early with a readable message instead of inside sklearn's StandardScaler."""
    arr = np.asarray(arr, dtype=float)
    bad = ~np.isfinite(arr).reshape(len(arr), -1).all(1)
    if bad.any():
        raise ValueError(f"{name}: {bad.sum()}/{len(arr)} rows contain NaN/inf (first: {np.where(bad)[0][:10]}). Re-extract in fp32 or drop them.")

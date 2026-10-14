"""Glioma loader for the TCGA pan-glioma cohort.csv (string-coded columns). Prints which columns it used."""
import sys, numpy as np, pandas as pd
_PRINTED = [False]

def _first(df, names):
    return [c for c in names if c in df.columns]

def _coalesce(df, names, fn):
    out = pd.Series(np.nan, index=df.index, dtype=float)
    for c in _first(df, names):
        out = out.fillna(df[c].map(fn).astype(float))
    return out

def _num(v):
    try: return float(v)
    except Exception: return np.nan

def _idh(v):
    if pd.isna(v): return np.nan
    s = str(v).lower()
    if "mut" in s: return 1.0
    if "wt" in s or "wild" in s: return 0.0
    return np.nan

def _meth(v):
    if pd.isna(v): return np.nan
    s = str(v).lower()
    if "unmeth" in s: return 0.0
    if "meth" in s: return 1.0
    return np.nan

def _codel(v):
    if pd.isna(v): return np.nan
    s = str(v).lower().replace(" ", "")
    if "non" in s: return 0.0
    if "codel" in s: return 1.0
    return np.nan

def _tert(v):
    if pd.isna(v): return np.nan
    s = str(v).lower()
    if "mut" in s: return 1.0
    if "wt" in s or "wild" in s: return 0.0
    return np.nan

def _sex(v):
    if pd.isna(v): return np.nan
    s = str(v).lower()
    if s.startswith("m"): return 1.0
    if s.startswith("f"): return 0.0
    return np.nan

def _gbm(v):
    if pd.isna(v): return np.nan
    s = str(v).upper()
    return 1.0 if ("G4" in s or "IV" in s or s.strip() == "4" or "GBM" in s or "GLIOBLASTOMA" in s) else 0.0

def load_glioma(path, impute="zero", add_missing_flags=False, drop=()):
    df = pd.read_csv(path)
    y_raw = _coalesce(df, ["idh_status", "idh_mut", "idh"], _idh)
    df = df[y_raw.notna()].reset_index(drop=True)
    y = _coalesce(df, ["idh_status", "idh_mut", "idh"], _idh).astype(int).values
    g = _coalesce(df, ["who_grade_raw", "grade"], _gbm)
    grade_hi = g.fillna(0.0).astype(int).values
    conc = ((y == 1) & (grade_hi == 0)) | ((y == 0) & (grade_hi == 1))
    cols = {
        "grade": pd.Series(grade_hi, index=df.index).astype(float),
        "age": _coalesce(df, ["age_at_diagnosis", "age"], _num),
        "mgmt": _coalesce(df, ["mgmt_methylation_status", "mgmt_promoter_status", "mgmt"], _meth),
        "codel": _coalesce(df, ["idh_1p19q_subtype", "codel_1p19q"], _codel),
        "tert": _coalesce(df, ["tert_promoter_status", "tert_mutation", "tert"], _tert),
        "sex": _coalesce(df, ["sex", "gender"], _sex),
    }
    X = pd.DataFrame({k: v for k, v in cols.items() if k not in drop})
    frac = X.isna().mean()
    dead = [k for k in X.columns if k != "grade" and frac[k] >= 0.999]
    if not _PRINTED[0]:
        _PRINTED[0] = True
        print("[glioma_data] rows=%d  IDH-mut frac=%.3f  grade_hi frac=%.3f  concordant frac=%.3f" % (len(df), y.mean(), grade_hi.mean(), conc.mean()), file=sys.stderr)
        print("[glioma_data] missing fraction per feature:", {k: round(float(v), 3) for k, v in frac.items()}, file=sys.stderr)
        if dead: print("[glioma_data] WARNING: dropped all-missing features:", dead, file=sys.stderr)
    X = X.drop(columns=dead)
    miss = X.isna()
    if "age" in X: X["age"] = (X["age"] - X["age"].mean()) / (X["age"].std() + 1e-9)
    X = X.fillna(0.0) if impute == "zero" else X.fillna(X.median())
    if add_missing_flags:
        for c in miss.columns[miss.any()]: X[c + "_missing"] = miss[c].astype(int)
    return dict(X=X, y=y, concordant=conc, grade_hi=grade_hi, df=df, missing=miss)

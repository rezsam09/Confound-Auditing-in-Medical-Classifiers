"""Synthetic stand-ins with the SAME file formats the real pipeline produces (for smoke-testing only)."""
import numpy as np, pandas as pd, sys
from pathlib import Path
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); rng = np.random.default_rng(0); D = 64
# TB
rows = [("b%d.dcm" % i, 1, "belarus", "A" if i % 2 else "B") for i in range(800)] + [("r%d.png" % i, 0, "rsna", "") for i in range(2400)] \
     + [("s%d.png" % i, i % 2, "shenzhen", "") for i in range(300)] + [("m%d.png" % i, i % 2, "montgomery", "") for i in range(120)]
man = pd.DataFrame(rows, columns=["path", "label", "source", "extent"]); man.to_csv(out / "tb_manifest.csv", index=False)
fmt = np.zeros(D); fmt[:5] = 3.0; dis = np.zeros(D); dis[10:14] = 0.6; ext = np.zeros(D); ext[20:23] = 0.8
Z = rng.standard_normal((len(man), D))
isfmt = man.source.isin(["belarus"]).values
Z += np.outer(isfmt, fmt) + np.outer(man.label.values, dis) + np.outer((man.extent == "B").values, ext)
Z[:, 30:] += rng.standard_normal((len(man), 1)) * 0.0
H = np.c_[np.where(isfmt, 2500, 1024) + rng.integers(0, 3, len(man)), np.where(isfmt, 2000, 1024) + rng.integers(0, 3, len(man)), rng.random(len(man)), rng.random(len(man)), rng.random(len(man)), rng.random(len(man))]
np.savez(out / "tb_feats.npz", Z=Z.astype(np.float32), H=H.astype(np.float32), Hcols=np.array(list("abcdef")))
# Malaria: 40 patients, slide signature per patient, label partly by patient
n = 6000; pat = rng.integers(0, 40, n); pinf = rng.random(40) * 0.9 + 0.05; y = (rng.random(n) < pinf[pat]).astype(int)
sig = rng.standard_normal((40, D)) * 0.8; true = np.zeros(D); true[:6] = 0.7
names = np.array([f"C{p+1}P{p+1}ThinF_IMG_2015_{i}_cell_{i}.png" for i, p in enumerate(pat)])
d = {"y": y, "names": names}
for v, (ps, ts) in {"full": (1, 1), "parasite": (0.5, 1.5), "rbc": (1, 0.3), "randcrop": (1, 0.3), "gray": (0.4, 0.2), "silhouette": (0.2, 0.0)}.items():
    d[f"Z_{v}"] = (rng.standard_normal((n, D)) + ps * sig[pat] + ts * np.outer(y, true)).astype(np.float32)
cols = ["h", "w", "aspect", "cell_frac", "parasite_frac", "rand_overlap", "mR", "mG", "mB", "sR", "sG", "sB", "mH", "mS", "mV", "sH", "sS", "sV"]
Hm = rng.random((n, len(cols))); Hm[:, 0] = 100 + 5 * pat + y * 3 + rng.integers(0, 4, n); Hm[:, 5] = (rng.random(n) < 0.1) * 0.05; Hm[:, 13] += 0.1 * pat / 40
d["H"] = Hm.astype(np.float32); d["Hcols"] = np.array(cols); np.savez(out / "mal_feats.npz", **d)
# Glioma
m = 1100; grade = rng.choice([2, 3, 4], m, p=[.3, .2, .5]); idh = ((grade < 4) & (rng.random(m) < .85) | (grade == 4) & (rng.random(m) < .07)).astype(int)
age = 55 - 15 * idh + 5 * (grade == 4) + rng.normal(0, 9, m); codel = ((idh == 1) & (grade < 4) & (rng.random(m) < .4)).astype(float)
tert = ((codel == 1) | ((idh == 0) & (rng.random(m) < .6))).astype(float); mgmt = ((rng.random(m) < .4 + .3 * idh)).astype(float)
df = pd.DataFrame(dict(idh_mut=idh, grade=grade, age=age, mgmt=mgmt, codel_1p19q=codel, tert=tert, sex=rng.integers(0, 2, m)))
df.loc[rng.random(m) < .2, "mgmt"] = np.nan; df.loc[rng.random(m) < .3, "tert"] = np.nan; df.to_csv(out / "glioma.csv", index=False)
print("synthetic written to", out)

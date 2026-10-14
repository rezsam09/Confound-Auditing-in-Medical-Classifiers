"""Build tb_manifest.csv: path,label,source,extent
  belarus   : TB cases (label 1)  -- extent from --extent_csv (columns: basename,extent in {A,B})
  rsna      : normals  (label 0)
  shenzhen  : CHNCXR_xxxx_{0|1}.png  (label from suffix)   <- source-matched TB vs normal
  montgomery: MCUCXR_xxxx_{0|1}.png                        <- source-matched TB vs normal
Pass only the dirs you have."""
import argparse, pandas as pd
from pathlib import Path
ap = argparse.ArgumentParser()
for k in ["belarus", "rsna", "shenzhen", "montgomery"]: ap.add_argument(f"--{k}_dir")
ap.add_argument("--extent_csv"); ap.add_argument("--out", default="tb_manifest.csv")
a = ap.parse_args(); rows = []
ext = {}
if a.extent_csv:
    e = pd.read_csv(a.extent_csv); ext = dict(zip(e.basename.astype(str), e.extent))
def files(d):
    """Recursive image list; skips segmentation masks (Montgomery ships leftMask/rightMask/ManualMask copies with identical file names)
    and de-duplicates by file stem."""
    out, seen = [], set()
    for p in sorted(Path(d).rglob("*")):
        if p.suffix.lower() not in (".dcm", ".png", ".jpg", ".jpeg"): continue
        if any("mask" in part.lower() for part in p.parts[len(Path(d).parts):]): continue
        if p.stem in seen: continue
        seen.add(p.stem); out.append(p)
    return out
if a.belarus_dir:
    for p in files(a.belarus_dir): rows.append((p, 1, "belarus", ext.get(p.stem, ext.get(p.name, ""))))
if a.rsna_dir:
    for p in files(a.rsna_dir): rows.append((p, 0, "rsna", ""))
for src in ["shenzhen", "montgomery"]:
    d = getattr(a, f"{src}_dir")
    if d:
        for p in files(d):
            if p.stem.endswith("_1"): rows.append((p, 1, src, ""))
            elif p.stem.endswith("_0"): rows.append((p, 0, src, ""))
pd.DataFrame(rows, columns=["path", "label", "source", "extent"]).to_csv(a.out, index=False)
m = pd.DataFrame(rows, columns=["path", "label", "source", "extent"]); print(m.groupby(["source", "label"]).size())
print("expected: shenzhen 326/336, montgomery 80/58 (normal/TB). Belarus extent filled:", (m[m.source == "belarus"].extent.astype(str).isin(["A", "B"])).mean())

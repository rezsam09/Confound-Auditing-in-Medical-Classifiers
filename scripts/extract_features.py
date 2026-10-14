"""Frozen-backbone feature extraction (the ONLY GPU step).
TB:      python extract_features.py tb --manifest tb_manifest.csv --backbone xrv_densenet121 --out feats/tb_xrv.npz [--harmonize]
Malaria: python extract_features.py malaria --root cell_images --backbone resnet50 --out feats/mal_resnet50.npz
Backbones: xrv_densenet121 (paper, TB) | resnet50 | densenet121 | dinov2_small
"""
import argparse, importlib.util, re, numpy as np
from pathlib import Path
import torch
from PIL import Image, ImageOps
from tqdm import tqdm

dev = "cuda" if torch.cuda.is_available() else "cpu"
IMN_M, IMN_S = np.array([0.485, 0.456, 0.406], np.float32), np.array([0.229, 0.224, 0.225], np.float32)


# ------------------------------------------------------------------ backbones
def get_backbone(name):
    torch.backends.cudnn.enabled = False   # cuDNN 9 sublibrary bug on the CV instance (same fix as the original paper run)
    if name == "xrv_densenet121":
        import torchxrayvision as xrv
        m = xrv.models.DenseNet(weights="densenet121-res224-all").eval().to(dev)
        return m, lambda x: m.features2(x), "xrv"
    import torchvision.models as tvm
    if name == "resnet50":
        m = tvm.resnet50(weights=tvm.ResNet50_Weights.IMAGENET1K_V1); m.fc = torch.nn.Identity()
        return m.eval().to(dev), lambda x: m(x), "imn"
    if name == "densenet121":
        m = tvm.densenet121(weights=tvm.DenseNet121_Weights.IMAGENET1K_V1)
        m.classifier = torch.nn.Identity()
        return m.eval().to(dev), lambda x: m(x), "imn"
    if name == "dinov2_small":
        from transformers import AutoModel
        m = AutoModel.from_pretrained("facebook/dinov2-small").eval().to(dev)
        return m, lambda x: m(pixel_values=x).last_hidden_state[:, 0], "imn"
    raise ValueError(name)


@torch.no_grad()
def run_batches(fn, tensors, bs=128):
    out = []
    for i in range(0, len(tensors), bs):
        x = torch.from_numpy(np.stack(tensors[i:i + bs])).to(dev)
        o = fn(x).float().cpu().numpy()            # fp32 on purpose: fp16 autocast can overflow to inf in DenseNet features
        if not np.isfinite(o).all():
            print(f"[warn] non-finite features in batch {i}; zeroing them (inspect those images)")
            o = np.nan_to_num(o, nan=0.0, posinf=0.0, neginf=0.0)
        out.append(o)
    return np.concatenate(out)


def to_tensor(img_u8, kind):
    """img_u8: HxW or HxWx3 uint8, already 224x224."""
    a = img_u8 if img_u8.ndim == 3 else np.stack([img_u8] * 3, 2)
    a = (a.astype(np.float32) / 255.0 - IMN_M) / IMN_S
    return a.transpose(2, 0, 1)


# ------------------------------------------------------------------ TB
def load_tb_image(path, harmonize):
    p = str(path)
    if p.lower().endswith(".dcm"):
        import pydicom
        ds = pydicom.dcmread(p); a = ds.pixel_array.astype(np.float32)
        if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
            a = a.max() - a
    else:
        im = Image.open(p)
        a = np.asarray(im.convert("L") if im.mode not in ("I;16", "I") else im).astype(np.float32)
    meta = dict(h=a.shape[0], w=a.shape[1], mean=float(a.mean()), std=float(a.std()),
                maxv=float(a.max()), minv=float(a.min()))
    lo, hi = np.percentile(a, [0.5, 99.5])
    a8 = np.clip((a - lo) / max(hi - lo, 1e-6), 0, 1) * 255
    im8 = Image.fromarray(a8.astype(np.uint8))
    if harmonize:  # identical pipeline for every source: equalize + JPEG round-trip erases container/compression traces
        import io
        im8 = ImageOps.equalize(im8)
        buf = io.BytesIO(); im8.save(buf, "JPEG", quality=90); buf.seek(0); im8 = Image.open(buf).convert("L")
    return np.asarray(im8.resize((224, 224), Image.BILINEAR)), meta


def extract_tb(args):
    import pandas as pd
    man = pd.read_csv(args.manifest)
    model, fn, kind = get_backbone(args.backbone)
    feats, metas = [], []
    for i in tqdm(range(0, len(man), 512)):
        ts = []
        for p in man.path.iloc[i:i + 512]:
            img, meta = load_tb_image(p, args.harmonize); metas.append(meta)
            if kind == "xrv":
                t = ((img.astype(np.float32) / 255.0) * 2048 - 1024)[None]       # xrv expects [-1024, 1024]
                ts.append(t)
            else:
                ts.append(to_tensor(img, kind))
        feats.append(run_batches(fn, ts))
    H = pd.DataFrame(metas).values.astype(np.float32)
    np.savez(args.out, Z=np.concatenate(feats), H=H, Hcols=np.array(list(metas[0].keys())))


# ------------------------------------------------------------------ TB planted shortcut (for E6)
def plant_marker(img8, strength=1.0):
    """Known synthetic shortcut: small bright block + soft corner gradient, applied BEFORE resize (uint8 HxW)."""
    a = img8.astype(np.float32).copy(); h, w = a.shape
    a[int(.03*h):int(.09*h), int(.03*w):int(.09*w)] = 255 * strength + a[int(.03*h):int(.09*h), int(.03*w):int(.09*w)] * (1 - strength)
    yy, xx = np.mgrid[:h, :w]; a += 25 * strength * np.clip(1 - (yy + xx) / (0.6 * (h + w)), 0, 1)
    return np.clip(a, 0, 255).astype(np.uint8)


def extract_tb_planted(args):
    """Features for CLEAN and MARKED versions of every manifest row (E6 resamples which version each image gets)."""
    import pandas as pd
    man = pd.read_csv(args.manifest); man = man[man.source.isin(args.planted_sources.split(","))].reset_index(drop=True)
    man.to_csv(Path(args.out).with_suffix(".manifest.csv"), index=False)
    model, fn, kind = get_backbone(args.backbone); Zc, Zm = [], []
    for i in tqdm(range(0, len(man), 256)):
        tc, tm = [], []
        for p in man.path.iloc[i:i + 256]:
            raw, _ = load_tb_image(p, args.harmonize); full = np.asarray(Image.fromarray(raw).resize((512, 512)))
            for arr, lst in [(full, tc), (plant_marker(full), tm)]:
                im = np.asarray(Image.fromarray(arr).resize((224, 224), Image.BILINEAR))
                lst.append(((im.astype(np.float32) / 255.0) * 2048 - 1024)[None] if kind == "xrv" else to_tensor(im, kind))
        Zc.append(run_batches(fn, tc)); Zm.append(run_batches(fn, tm))
    np.savez(args.out, Z_clean=np.concatenate(Zc), Z_marked=np.concatenate(Zm), y=man.label.values, source=man.source.values)


# ------------------------------------------------------------------ Malaria
def default_parasite_mask(rgb):
    """PLACEHOLDER Giemsa-HSV parasite mask. Replace with your own mask:
    pass --views-module your_file.py defining parasite_mask(rgb_uint8)->bool array."""
    from skimage.color import rgb2hsv
    hsv = rgb2hsv(rgb); cell = rgb.sum(2) > 30
    return cell & (hsv[..., 1] > 0.45) & (hsv[..., 2] < 0.70) & (hsv[..., 0] > 0.60)


def adaptive_parasite_mask(rgb):
    """Fallback mask (used for the reported results, --mask adaptive): per-cell robust threshold on the dark, purple-ish (low-green) tail.
    Choose with --mask adaptive. Sanity-check that parasite_frac is clearly higher for Parasitized than Uninfected cells."""
    from scipy.ndimage import binary_opening
    cell = rgb.sum(2) > 30
    if cell.sum() < 50: return np.zeros(cell.shape, bool)
    g = rgb[..., 1].astype(float); gc = g[cell]
    rstd = 1.4826 * np.median(np.abs(gc - np.median(gc))) + 1e-6
    pm = cell & (g < np.median(gc) - 2.5 * rstd) & (rgb[..., 2] > rgb[..., 1])
    return binary_opening(pm, iterations=1)


def make_views(rgb, rng, pmask_fn):
    h, w, _ = rgb.shape
    cell = rgb.sum(2) > 30
    pm = pmask_fn(rgb)
    from scipy.ndimage import binary_dilation
    pmd = binary_dilation(pm, iterations=2)
    views = {"full": rgb}
    # parasite region + centre crop
    par = rgb.copy(); par[~pmd] = 0
    cy, cx, r = h // 2, w // 2, int(0.35 * min(h, w))
    views["parasite"] = par[max(cy - r, 0):cy + r, max(cx - r, 0):cx + r]
    # RBC-only: parasite pixels replaced by median colour of remaining cell pixels
    rbc = rgb.copy(); rest = cell & ~pmd
    med = np.median(rgb[rest], axis=0) if rest.sum() > 10 else np.array([0, 0, 0])
    rbc[pmd] = med.astype(np.uint8); views["rbc"] = rbc
    # random off-centre circular crop (r=35% of cell), seeded; choose the candidate with least parasite overlap
    best, best_ov = None, 2.0
    R = int(0.35 * min(h, w)); yy, xx = np.mgrid[:h, :w]
    for _ in range(50):
        y0, x0 = rng.integers(R, max(h - R, R + 1)), rng.integers(R, max(w - R, R + 1))
        if abs(y0 - cy) + abs(x0 - cx) < R // 2: continue          # off-centre
        circ = (yy - y0) ** 2 + (xx - x0) ** 2 <= R ** 2
        ov = float((circ & pmd).sum()) / max(circ.sum(), 1)
        if ov < best_ov: best, best_ov = circ, ov
        if ov == 0: break
    if best is None: best, best_ov = ((yy - cy) ** 2 + (xx - cx) ** 2 <= R ** 2), 1.0
    rc = rgb.copy(); rc[~best] = 0; views["randcrop"] = rc
    # stain-stripped: grayscale + per-image standardisation within the cell
    g = rgb.mean(2); gz = np.zeros_like(g)
    if cell.sum() > 10: gz[cell] = (g[cell] - g[cell].mean()) / (g[cell].std() + 1e-6) * 40 + 128
    views["gray"] = np.stack([np.clip(gz, 0, 255).astype(np.uint8)] * 3, 2)
    # silhouette only (shape / size, no texture or colour)
    views["silhouette"] = np.stack([(cell * 255).astype(np.uint8)] * 3, 2)
    # handcrafted baselines
    from skimage.color import rgb2hsv
    hsv = rgb2hsv(rgb)
    px = rgb[cell] if cell.sum() else rgb.reshape(-1, 3)
    hp = hsv[cell] if cell.sum() else hsv.reshape(-1, 3)
    hand = [h, w, h / w, cell.mean(), pm.sum() / max(cell.sum(), 1), best_ov,
            *px.mean(0), *px.std(0), *hp.mean(0), *hp.std(0)]
    return views, np.array(hand, np.float32)


HAND_COLS = ["h", "w", "aspect", "cell_frac", "parasite_frac", "rand_overlap",
             "mR", "mG", "mB", "sR", "sG", "sB", "mH", "mS", "mV", "sH", "sS", "sV"]
VIEWS = ["full", "parasite", "rbc", "randcrop", "gray", "silhouette"]


def extract_malaria(args):
    root = Path(args.root)
    files = sorted(list((root / "Parasitized").glob("*.png")) + list((root / "Uninfected").glob("*.png")))
    y = np.array([1 if f.parent.name == "Parasitized" else 0 for f in files])
    pfn = adaptive_parasite_mask if args.mask == "adaptive" else default_parasite_mask
    if args.views_module:
        spec = importlib.util.spec_from_file_location("v", args.views_module); m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m); pfn = m.parasite_mask
    model, fn, kind = get_backbone(args.backbone)
    Z = {v: [] for v in VIEWS}; hand = []; buf = {v: [] for v in VIEWS}
    def flush():
        for v in VIEWS:
            if buf[v]: Z[v].append(run_batches(fn, buf[v])); buf[v] = []
    for k, f in enumerate(tqdm(files)):
        rgb = np.asarray(Image.open(f).convert("RGB"))
        rng = np.random.default_rng(1000 + k)                        # seeded per cell
        views, hv = make_views(rgb, rng, pfn); hand.append(hv)
        for v in VIEWS:
            im = Image.fromarray(views[v]).resize((224, 224), Image.BILINEAR)
            buf[v].append(to_tensor(np.asarray(im), kind if kind != "xrv" else "imn"))
        if (k + 1) % 512 == 0: flush()
    flush()
    np.savez(args.out, y=y, names=np.array([f.name for f in files]), H=np.stack(hand),
             Hcols=np.array(HAND_COLS), **{f"Z_{v}": np.concatenate(Z[v]) for v in VIEWS})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("task", choices=["tb", "malaria", "tb_planted"])
    ap.add_argument("--manifest"); ap.add_argument("--root"); ap.add_argument("--backbone", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--harmonize", action="store_true")
    ap.add_argument("--views-module", default=None); ap.add_argument("--mask", default="hsv", choices=["hsv", "adaptive"]); ap.add_argument("--planted_sources", default="shenzhen,montgomery")
    a = ap.parse_args(); Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    {'tb': extract_tb, 'malaria': extract_malaria, 'tb_planted': extract_tb_planted}[a.task](a)

# Confound Auditing in Medical Classifiers

Code and result files for **"Confound Auditing in Medical Classifiers: Evidence from TB, Glioma, and Malaria"** (ML4H 2026, Findings Track).

The paper proposes an *iterative falsification audit* for frozen-feature medical classifiers. A stratified shortcut test ablates shortcut and residual directions under random-direction and retrained-head controls. Decision rules map each verdict to a follow-up test. A planted-marker calibration estimates the audit's false-flag rate and power. We apply the loop to three public datasets.

Everything runs on **frozen features**. Only feature extraction needs a GPU. All analyses are numpy/scikit-learn on CPU.

## Headline results

| Domain | Finding |
|---|---|
| Planted marker (TB) | 0 of 20 splits flagged at no association (rho = 0.5). Marker prevalence of 0.7 or higher was flagged in at least 85% of splits for DINOv2 and ResNet-50. Sensitivity is lower for the xrv encoder. |
| TB | Source is decodable at AUC 0.999 to 1.000. A Belarus/RSNA-trained detector scores 0.455 to 0.542 on source-matched data. After LEACE or INLP erasure, MLP probes still decode source (up to 0.998). |
| Glioma | Ablating WHO grade collapses predictions to one class. The grade-excluded refit reaches discordant AUC 0.738, which depends on imputation (0.563 to 0.812). |
| Malaria | Parasite-replaced views stay predictive (AUC 0.952 to 0.977). Uninfected cells carry patient infection status (AUC 0.946 to 0.954). |

All numbers behind the paper are in [`results/SUMMARY.md`](results/SUMMARY.md) (generated) and the per-experiment JSON files in [`results/`](results/). A prose walkthrough, including the known xrv-LEACE bug and its fix, is in [`docs/RESULTS.md`](docs/RESULTS.md).

## Repository layout

```
scripts/      analysis and feature-extraction code (one script per experiment)
results/      per-experiment JSON outputs and SUMMARY.md
docs/         RESULTS.md, results notes and known issues
tests/        synthetic data generator for smoke tests (no real data needed)
reproduce_all.sh   end-to-end driver (extract | analyze | addons | all)
paths.sh.example   dataset locations to edit
```

| Script | What it does |
|---|---|
| `extract_features.py` | Frozen features from xrv DenseNet-121, ResNet-50, DINOv2-small, DenseNet-121 (malaria); malaria views; planted-marker TB images |
| `E1_tb_source_matched.py` | Source decodability, within-source detection, Belarus/RSNA detector on source-matched data |
| `E2_leace_vs_inlp.py` | LEACE vs INLP (1 to 200 rounds) with linear, MLP and GBM probes |
| `E3_ablation_controls.py` | Shortcut/residual ablations with fixed head, retrained head and random-direction nulls |
| `E4_glioma_leakage.py` | Glioma grade ablation, leave-one-feature-out refits, imputation sensitivity |
| `E5_malaria_patient_split.py` | Cell-level vs patient-grouped CV across views, size/colour baselines |
| `E6_planted_shortcut_calibration.py` | Planted-marker calibration: false-flag rate and power |
| `E7_eraser_transport.py` | Transport of an eraser fit in one encoder into another |
| `E8_cka_blindness.py` | CKA before and after erasure |
| `E9_patient_state.py` | Patient infection status from uninfected malaria cells |
| `erasers.py`, `common.py`, `*_data.py`, `make_*` | LEACE/INLP, shared utilities, data loaders, report builder |

## Data

Datasets are public and are **not redistributed** here. Download them and point `paths.sh` at them.

- TB: Belarus TB Portals (Rosenthal et al., 2017), RSNA pneumonia normals (Shih et al., 2019), Shenzhen and Montgomery (Jaeger et al., 2014). The disease-extent (A/B) labels for Belarus cases go in a CSV with columns `basename,extent`.
- Glioma: TCGA LGG/GBM molecular cohort (Ceccarelli et al., 2016). Edit `COLS` in `scripts/glioma_data.py` to match your column names. Age and sex are entirely missing in the cohort file we used.
- Malaria: NIH thin-smear cell images (Rajaraman et al., 2018). Patient groups are parsed from file names (`C100P61ThinF_...png`), giving 201 groups.

## Setup and reproduction

```bash
pip install -r requirements.txt
cp paths.sh.example paths.sh      # edit the dataset paths
nohup bash reproduce_all.sh extract > extract.log 2>&1 &   # GPU, about 2-3 h on a T4
bash reproduce_all.sh analyze                              # CPU, several hours
bash reproduce_all.sh addons                               # E7, E8, E9
```

Outputs land in `results/*.json` and `results/SUMMARY.md`. A T4 (16 GB) is enough for extraction. `extract_features.py` disables cuDNN (a cuDNN 9 sublibrary bug on our setup) and runs in fp32 (fp16 overflowed to inf in DenseNet features).

Smoke test without any data:

```bash
python tests/make_synthetic.py /tmp/syn
cd scripts
python E1_tb_source_matched.py --manifest /tmp/syn/tb_manifest.csv --feats /tmp/syn/tb_feats.npz --tag syn
python E5_malaria_patient_split.py --feats /tmp/syn/mal_feats.npz --tag syn
```

Settings behind the reported numbers: E3 malaria and glioma use the script defaults (5 seeds, 200 fixed-head and 30 retrained-head random-direction nulls; glioma `--seeds 10`). E3 TB uses 3 seeds on xrv and 2 on DINOv2. E4 uses 20 splits.

## Known issues

- Preprocessing in `extract_features.py` (percentile window, 8-bit, 224 px) and the default malaria parasite mask are re-implementations. Use `--mask adaptive` (as for the reported results) or pass your own mask with `--views-module`.
- LEACE originally failed on the 1024-d xrv features because 108 zero-variance columns leaked the erased direction back (`scripts/diagnose_leace.py`). `erasers.py` now excludes dead columns, and all reported xrv results use the fixed version.
- Per-seed standard deviations of about 0 in E4 reflect discrete features. Use the bootstrap intervals.
- Intervals reflect resampling of test samples, not training variance. Seed counts are small (see `docs/RESULTS.md`, Limitations).

## License

MIT, see [`LICENSE`](LICENSE).

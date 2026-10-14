# Confound Auditing in Medical Classifiers

> **Note:** *This paper is under review as a Findings paper in ML4H.*

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

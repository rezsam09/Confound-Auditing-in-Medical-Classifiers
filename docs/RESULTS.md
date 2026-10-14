# Results notes

Source of all numbers: `results/SUMMARY.md` (included). All planned experiments have finished, including the rerun with the fixed LEACE eraser. Section 7 lists limitations.

## 0. Status at a glance

| Component | Status |
|---|---|
| TB source identifiability and transfer (E1), 3 encoders + harmonized | Final |
| TB eraser comparison (E2): DINOv2, ResNet50 | Final |
| TB eraser comparison (E2): xrv_densenet121 and harmonized | Final after the LEACE fix (section 6). |
| Ablation controls (E3): TB (xrv, DINOv2), malaria (ResNet50), glioma | Final. Metric is accuracy, not AUC, except the "all" cell where noted. |
| Glioma leakage (E4) | Final with the corrected loader. Age and sex are missing from the cohort file. |
| Malaria patient-grouped analysis (E5), 3 encoders | Final |
| Malaria bystander / patient-state (E9), 3 encoders | Final |
| Planted-shortcut calibration (E6) | Final. It runs LEACE inside a 64-dim PCA space, so the xrv bug never affected it. |
| Eraser transport (E7) and CKA (E8) | Final for the ResNet50 <-> DINOv2 and xrv <-> DINOv2 pairs. |

## 1. TB: source is perfectly identifiable and the confounded detector does not transfer

- Source (Belarus vs RSNA) is decodable from features at AUC 1.000 (DINOv2, ResNet50) and 0.999 (xrv). Metadata alone also gives 1.000.
- A TB detector trained on Belarus-TB vs RSNA-normals is at chance on source-matched data (Shenzhen + Montgomery): DINOv2 0.455 [0.417, 0.499], ResNet50 0.511 [0.471, 0.552], xrv 0.542 [0.503, 0.584]. On Shenzhen alone: 0.395, 0.465, 0.501.
- Within-source detection is strong (Shenzhen CV 0.893 / 0.897 / 0.903; Montgomery CV 0.844 / 0.870 / 0.903), so the failure to transfer is not an absence of disease signal.
- Matched-to-matched transfer is partial and encoder dependent: Shenzhen -> Montgomery 0.736 / 0.718 / 0.628; Montgomery -> Shenzhen 0.787 / 0.821 / 0.356 (xrv is BELOW chance, CI [0.318, 0.398]; unexplained, do not hide it).
- Format harmonization (xrv): the Belarus/RSNA detector transfers better, 0.752 [0.715, 0.785] on matched data (vs 0.542 unharmonized), while source stays identifiable (0.999). Matched-to-matched transfer gets worse (Shenzhen -> Montgomery 0.548). Mixed result; report both.
- The source direction is nearly orthogonal to the matched TB-detector direction (cosine 0.002 to 0.045).

### Erasers (E2)
- DINOv2 / ResNet50: LEACE drives the linear source probe to chance in one step (0.494 / 0.470) but an MLP (0.998 / 0.997) and GBM (0.985 / 0.995) still decode the source. INLP needs about 100 (DINOv2) to 200 (ResNet50) rounds to reach linear chance (0.496 / 0.484), and non-linear probes still decode the source (MLP 0.941 / 0.994 at 200 rounds).
- TB detection on matched data is unchanged by erasure (DINOv2 0.839 -> 0.844; ResNet50 0.850 -> 0.847).
- xrv (the paper's main encoder): LEACE reaches linear chance in one step (0.484; harmonized 0.481) while the MLP (0.989 / 0.998) and GBM (1.000 / 1.000) still decode the source. INLP at 200 rounds reaches 0.501 (harmonized 0.503) with MLP 0.990 and GBM 0.999. Matched-data TB detection after LEACE does not drop (0.808 -> 0.825; harmonized 0.812 -> 0.827). An earlier xrv LEACE value of 0.997 was a bug (section 6).
- Reading: linear erasure removes the linear source signal but not the source; stalled INLP is a weak-eraser effect, and a linear-only audit understates the confound.

### Ablation controls (E3, accuracy)
- Removing the source direction with the head fixed does not change positive-class accuracy for DINOv2 (A_pos 1.000 -> 1.000; B_pos 0.991 -> 0.991). For xrv positives are unchanged (0.991, 0.986 -> 0.990) but normals drop 0.998 -> 0.835 (sd 0.081, p = 0.01 vs the random-direction null); a retrained head restores 0.998.
- Removing the residual (disease) direction with the head fixed collapses accuracy (DINOv2 A_pos 0.000, B_pos 0.000; xrv 0.108, 0.236) and a retrained head recovers it (0.986 / 0.976 DINOv2, 0.989 / 0.986 xrv): the disease information is redundantly available.

### Planted-shortcut calibration (E6)
A marker was planted in Shenzhen/Montgomery images with P(marker | TB) = rho; rho = 0.5 is the null.
- False positives: flag rate 0.00 at rho = 0.5 for all three encoders.
- Detection (flag rate): DINOv2 0.40 / 0.85 / 1.00 / 1.00 / 0.90 at rho 0.6 / 0.7 / 0.8 / 0.9 / 1.0; ResNet50 0.25 / 0.85 / 1.00 / 1.00 / 1.00; xrv 0.00 / 0.30 / 0.75 / 0.70 / 0.00. xrv (the paper's main encoder) is the least sensitive and misses the strongest shortcut (rho = 1.0).
- Shortcut tax (concordant AUC minus flipped AUC) grows with rho: DINOv2 0.058 at rho 0.7, 0.312 at 0.9; ResNet50 0.064, 0.327; xrv 0.044, 0.210.
- Recovered-direction cosine to the planted direction is about 0.65 to 0.72 for DINOv2 / ResNet50 and about 0.25 for xrv.
- The "LEACE gain on flipped" column is valid for all three encoders (E6 applies LEACE after a 64-dim PCA): xrv 0.078 at rho 0.9 and -0.182 at 1.0 (negative at 1.0: erasing the marker hurts because the head has no other signal); DINOv2 0.250 and 0.142; ResNet50 0.258 and 0.203.

## 2. Malaria

- Patient-grouped CV barely differs from cell-level CV: full image 0.977 vs 0.982 (ResNet50), 0.981 vs 0.986 (densenet121), 0.991 vs 0.993 (DINOv2). 24.9% of the 201 patient groups are single-class (12.4% of cells).
- Parasite-masked view: 0.899 / 0.917 / 0.928 (ResNet50 / densenet121 / DINOv2) patient-grouped. Random crops reach 0.811 / 0.828 / 0.848 (mean parasite overlap 1.2%, 29% of crops overlap any parasite).
- RBC view minus random crop: 0.142 [0.137, 0.146] ResNet50, 0.136 [0.131, 0.140] densenet121, 0.129 [0.124, 0.133] DINOv2. The pre-specified +/-0.02 equivalence test FAILS for all three. Do not claim the views are equivalent; the supportable statement is that non-parasite regions carry substantial signal (0.81 to 0.85) but less than the RBC view.
- Colour-only handcrafted features reach 0.967 to 0.969 patient-grouped (all but parasite fraction: 0.970 to 0.972); size/shape only 0.572 to 0.577; silhouette 0.716 to 0.742.
- Patient identifiability: a probe on the full-image features picks the correct patient among 201 at top-1 0.50 to 0.58 (chance 0.005); random crops 0.32 to 0.43; silhouette 0.07 to 0.10.
- Bystander test (E9): uninfected cells from infected patients vs uninfected cells from patients with no infected cell: AUC 0.612 to 0.675 on the full-image features, 0.505 to 0.512 on the parasite view (no effect). Patient infection status is predictable from uninfected cells alone at AUC 0.946 to 0.954 (full), 0.796 to 0.886 (parasite view). Extra false positives on bystander cells, e.g. ResNet50 FPR 0.068 vs 0.040 (full) and 0.246 vs 0.111 (random crop).
- Ablation (E3, ResNet50, shortcut = high vs low mean saturation): removing the shortcut direction leaves accuracy at 0.927 vs 0.928 baseline (fixed head) and 0.928 (retrained), p = 0.95 and 0.45. Removing the residual direction collapses it to 0.506. RBC view: 0.890 baseline, 0.886 fixed. The "pos" and "neg" rows are single-class cells with 5 seeds, so their +/-0.4 SDs are an artifact of few binary outcomes; use the "all" row.

## 3. Glioma (corrected loader; n = 995 patients with IDH status)

The first run was invalid (all non-grade features were silently parsed as NaN, so every model saw constants). The loader now parses the text-coded columns. Age and sex are 100% missing in the cohort file and are dropped; TERT is 67% missing, MGMT 11.6%, 1p/19q 2.1%.
- With grade the model is a pure grade shortcut: concordant AUC 1.000, discordant AUC 0.000; the grade direction has cosine 1.00 with the classifier, and removing it collapses predictions to a constant.
- Without grade (paper refit), discordant AUC is 0.738 [0.649, 0.823] (the paper reported 0.727). It depends strongly on preprocessing: median imputation 0.812 [0.736, 0.888]; median plus missingness flags 0.563 [0.394, 0.596].
- Without 1p/19q: 0.624 [0.544, 0.716]. 1p/19q alone: 0.527; TERT alone: 0.336 [0.284, 0.387] (below chance); MGMT alone: 0.638. 1p/19q co-deletion implies IDH-mutant by definition, so part of the signal is definitional.
- Missingness indicators alone predict IDH at CV AUC 0.666 [0.631, 0.699].
- Within grade: low-grade only 0.891 [0.855, 0.925]; glioblastoma only 0.606 [0.509, 0.704]. Without 1p/19q and TERT (MGMT only): 0.750 and 0.604.
- Discordant set: 104 IDH-wildtype low-grade and 37 IDH-mutant glioblastoma, so intervals are wide.
- E3 glioma (accuracy; single-class cells): ablating the grade direction takes concordant accuracy 1.000 -> 0.490; a retrained head gets 0.815.
- Caveats: the old loader had 1,122 rows and an IDH-mutant fraction of 0.407; the new one has 995 rows and 0.459 (127 rows lack IDH status and were probably counted as wildtype before). Check which n the paper reports. "Age only" and any age-based argument cannot be run on this file.

## 4. Eraser transport and CKA

- Own-encoder LEACE removes the linear source signal (0.529 in ResNet50, 0.511 in DINOv2). Transporting the DINOv2 eraser into ResNet50 through a ridge map removes only part of it (0.931; a random rank-1 control stays at 1.000); the reverse direction removes almost nothing (0.997). Non-linear (MLP) probes decode the source at 0.99 or above under every condition. Held-out map R2 is 0.357 (A to B) and 0.323 (B to A).
- xrv <-> DINOv2 (valid after the fix): own-encoder LEACE reaches 0.524 in xrv and 0.511 in DINOv2; a transported eraser leaves 0.987 (DINOv2 -> xrv) and 0.991 (xrv -> DINOv2); a random rank-1 control leaves 0.998 and 1.000. Map R2 is 0.273 / 0.140. MLP probes decode the source at 0.987 or above in every condition.
- Summary: erasers do not transfer across encoders. The only partial transfer is DINOv2 -> ResNet50 (0.931). Source-matched TB detection is unaffected by any of these erasures (xrv 0.808 -> 0.815 own, 0.813 transported).
- Head inheritance on source-matched data: stitched heads are indistinguishable from native heads (ResNet50 <-> DINOv2: 0.467 [0.428, 0.509] vs 0.464 / 0.471; xrv <-> DINOv2: 0.499 [0.461, 0.540] and 0.541 [0.503, 0.582] vs 0.570 / 0.471). Their scores correlate 0.76 to 0.90, and all are near chance, as in section 1.
- CKA, xrv vs DINOv2: CKA(A,B) = 0.202; erasing the source (3.2% / 4.3% of variance) gives CKA(xrv, xrv_erased) = 0.978 and CKA(DINOv2, DINOv2_erased) = 0.930, and the cross-encoder CKA changes by -0.045 (random rank-1: 0.0002), while the xrv source probe falls from 1.000 to 0.481.
- CKA, ResNet50 vs DINOv2: CKA(A,B) = 0.408. After erasing the source direction (about 4.3 to 4.5% of variance), CKA(A, A_erased) = 0.890 and CKA(B, B_erased) = 0.930, and the cross-encoder CKA changes by -0.055, while the linear source probe falls from 1.0 to about 0.47. A random rank-1 removal changes cross-encoder CKA by 0.0002. So CKA moves about 300x more than for a random direction, but in absolute terms it stays large (0.89 to 0.93) while source decodability collapses. Phrase this as "CKA changes little in absolute terms relative to the change in decodability", not as "CKA is blind".

## 5. Claims: supported and not supported

Supported by current numbers: source is perfectly identifiable in TB features and metadata; the confounded detector is at chance on matched data; linear erasure (LEACE or INLP) leaves non-linear source information on all three encoders; source-direction ablation leaves disease detection intact; the planted-shortcut audit has no false positives at rho 0.5 and high power from rho 0.7 for DINOv2 / ResNet50; the glioma "independent signal" reproduces (0.738) but is fragile to imputation and partly definitional; slide-level patient state is encoded in uninfected cells.

Not supported by the data: RBC view equivalent to random crops (equivalence test fails); the audit works equally well on xrv (it does not at rho 1.0 and is weaker overall); CKA "blindness" in absolute terms; erasers transferring across encoders (they mostly do not); anything about age in glioma.

## 6. The xrv LEACE bug and the fix (resolved)

Symptom: on the 1024-d xrv features LEACE left the linear source probe at 0.997 (0.999 harmonized) while DINOv2 and ResNet50 reached chance. `scripts/diagnose_leace.py` showed 108 of 1024 columns have zero variance (covariance rank 916) and the largest standardized test value was 931 sd; LEACE on the full space left a linear probe at train AUC 1.000 although all class means were equal to 1e-11. Dropping the dead columns before LEACE gave train 0.509 / test 0.524; clipping outliers made no difference. The fixed `erasers.py` excludes dead columns from the fit and passes them through. After the rerun the xrv linear probe is at 0.484 (0.481 harmonized), and E7 / E8 with xrv are valid. A consistency check: the xrv CKA values and variance share removed are identical before and after the fix (CKA 0.9776, 3.2%), so the leak was confined to near-zero-variance columns. The mechanism (the erased direction leaking into dead columns at floating-point level and re-amplified by the probe's standardization) is our best explanation, supported by the diagnostic but not independently proven. E6 was never affected because it applies LEACE after a 64-dim PCA.

## 7. Limitations

1. Single splits and small seed counts throughout (E3: 2 to 5 seeds). Intervals reflect resampling of test cells, not training variance.
2. Coverage gaps: E3 on TB with ResNet50; E3 on malaria with DINOv2 / densenet121; harmonization for DINOv2 / ResNet50; planted-marker calibration only on TB.
3. The malaria patient grouping is parsed from file names (201 groups vs the 200 patients the dataset describes).
4. The glioma cohort has 995 patients with IDH status (1,122 rows minus 127 without IDH); age and sex are fully missing in the cohort file.

## 8. Reproduce

See the top-level README and `reproduce_all.sh`. Features are not included (they come from the extraction stage).

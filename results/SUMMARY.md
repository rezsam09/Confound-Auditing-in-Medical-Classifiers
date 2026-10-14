## E1_tb_dinov2_small.json
| test | AUC [95% CI] |
|---|---|
| source_probe_belarus_vs_rsna | 1.000 [1.000, 1.000] |
| within_shenzhen_cv | 0.893 [0.869, 0.916] |
| within_montgomery_cv | 0.844 [0.775, 0.906] |
| shenzhen_to_montgomery | 0.736 [0.652, 0.820] |
| montgomery_to_shenzhen | 0.787 [0.753, 0.820] |
| belarusRSNA_to_matched | 0.455 [0.417, 0.499] |
| belarusRSNA_to_shenzhen | 0.395 [0.350, 0.436] |
| belarusRSNA_to_montgomery | 0.569 [0.466, 0.670] |
| matched_to_belarusRSNA | 0.515 [0.496, 0.535] |
| cosine_source_dir_vs_matched_detector_dir | 0.045 |
| metadata_only_belarus_vs_rsna_AUC | 1.000 [1.000, 1.000] |
| metadata_only_matched_cv_AUC | 0.748 [0.713, 0.780] |
## E1_tb_resnet50.json
| test | AUC [95% CI] |
|---|---|
| source_probe_belarus_vs_rsna | 1.000 [1.000, 1.000] |
| within_shenzhen_cv | 0.897 [0.873, 0.920] |
| within_montgomery_cv | 0.870 [0.809, 0.922] |
| shenzhen_to_montgomery | 0.718 [0.624, 0.802] |
| montgomery_to_shenzhen | 0.821 [0.791, 0.851] |
| belarusRSNA_to_matched | 0.511 [0.471, 0.552] |
| belarusRSNA_to_shenzhen | 0.465 [0.418, 0.507] |
| belarusRSNA_to_montgomery | 0.690 [0.598, 0.779] |
| matched_to_belarusRSNA | 0.496 [0.477, 0.515] |
| cosine_source_dir_vs_matched_detector_dir | 0.031 |
| metadata_only_belarus_vs_rsna_AUC | 1.000 [1.000, 1.000] |
| metadata_only_matched_cv_AUC | 0.748 [0.713, 0.780] |
## E1_tb_xrv_densenet121.json
| test | AUC [95% CI] |
|---|---|
| source_probe_belarus_vs_rsna | 0.999 [0.999, 1.000] |
| within_shenzhen_cv | 0.903 [0.879, 0.925] |
| within_montgomery_cv | 0.903 [0.840, 0.954] |
| shenzhen_to_montgomery | 0.628 [0.528, 0.722] |
| montgomery_to_shenzhen | 0.356 [0.318, 0.398] |
| belarusRSNA_to_matched | 0.542 [0.503, 0.584] |
| belarusRSNA_to_shenzhen | 0.501 [0.455, 0.545] |
| belarusRSNA_to_montgomery | 0.673 [0.573, 0.762] |
| matched_to_belarusRSNA | 0.643 [0.622, 0.664] |
| cosine_source_dir_vs_matched_detector_dir | 0.002 |
| metadata_only_belarus_vs_rsna_AUC | 1.000 [1.000, 1.000] |
| metadata_only_matched_cv_AUC | 0.748 [0.713, 0.780] |
## E1_tb_xrv_harmonized.json
| test | AUC [95% CI] |
|---|---|
| source_probe_belarus_vs_rsna | 0.999 [0.999, 1.000] |
| within_shenzhen_cv | 0.930 [0.910, 0.948] |
| within_montgomery_cv | 0.898 [0.829, 0.951] |
| shenzhen_to_montgomery | 0.548 [0.446, 0.645] |
| montgomery_to_shenzhen | 0.608 [0.567, 0.650] |
| belarusRSNA_to_matched | 0.752 [0.715, 0.785] |
| belarusRSNA_to_shenzhen | 0.802 [0.767, 0.835] |
| belarusRSNA_to_montgomery | 0.705 [0.609, 0.792] |
| matched_to_belarusRSNA | 0.844 [0.830, 0.858] |
| cosine_source_dir_vs_matched_detector_dir | 0.001 |
| metadata_only_belarus_vs_rsna_AUC | 1.000 [1.000, 1.000] |
| metadata_only_matched_cv_AUC | 0.748 [0.713, 0.780] |
## E2_erasers_dinov2_small.json  (held-out source-probe AUC after erasure)
| eraser | linear | MLP | GBM | matched-TB-detection AUC |
|---|---|---|---|---|
| none | 1.000 | 1.000 | 1.000 | 0.839 |
| LEACE | 0.494 | 0.998 | 0.985 | 0.844 |
| INLP_1 | 0.999 | 0.999 | 0.999 | nan |
| INLP_10 | 0.967 | 0.998 | 0.990 | nan |
| INLP_50 | 0.671 | 0.996 | 0.977 | 0.831 |
| INLP_100 | 0.496 | 0.989 | 0.953 | nan |
| INLP_200 | 0.472 | 0.941 | 0.831 | nan |
## E2_erasers_resnet50.json  (held-out source-probe AUC after erasure)
| eraser | linear | MLP | GBM | matched-TB-detection AUC |
|---|---|---|---|---|
| none | 1.000 | 1.000 | 0.999 | 0.850 |
| LEACE | 0.470 | 0.997 | 0.995 | 0.847 |
| INLP_1 | 0.999 | 1.000 | 0.999 | nan |
| INLP_10 | 0.994 | 0.999 | 0.999 | nan |
| INLP_50 | 0.905 | 0.999 | 0.998 | 0.854 |
| INLP_100 | 0.788 | 0.999 | 0.997 | nan |
| INLP_200 | 0.484 | 0.994 | 0.991 | nan |
## E2_erasers_xrv_densenet121.json  (held-out source-probe AUC after erasure)
| eraser | linear | MLP | GBM | matched-TB-detection AUC |
|---|---|---|---|---|
| none | 0.999 | 0.999 | 1.000 | 0.808 |
| LEACE | 0.484 | 0.989 | 1.000 | 0.825 |
| INLP_1 | 0.999 | 0.994 | 0.990 | nan |
| INLP_10 | 0.988 | 0.991 | 1.000 | nan |
| INLP_50 | 0.882 | 0.996 | 1.000 | 0.825 |
| INLP_100 | 0.684 | 0.999 | 1.000 | nan |
| INLP_200 | 0.501 | 0.990 | 0.999 | nan |
## E2_erasers_xrv_harmonized.json  (held-out source-probe AUC after erasure)
| eraser | linear | MLP | GBM | matched-TB-detection AUC |
|---|---|---|---|---|
| none | 0.999 | 0.999 | 1.000 | 0.812 |
| LEACE | 0.481 | 0.998 | 1.000 | 0.827 |
| INLP_1 | 0.999 | 0.999 | 0.992 | nan |
| INLP_10 | 0.988 | 0.999 | 1.000 | nan |
| INLP_50 | 0.901 | 0.999 | 1.000 | 0.831 |
| INLP_100 | 0.658 | 0.999 | 0.999 | nan |
| INLP_200 | 0.503 | 0.991 | 0.995 | nan |
## E3_glioma_tcga.json
| cell | baseline | shortcut fixed | shortcut retrain | residual fixed | residual retrain | random-dir null drop (mean, p95) |
|---|---|---|---|---|---|---|
| concordant | 1.000 | 0.490±0.000 (p=0.12) | 0.815±0.021 (p=0.11) | 0.490±0.000 (p=0.12) | 0.815±0.021 (p=0.11) | 0.150, 0.510 |
| disc_IDHwt_LGG | 0.000 | 0.000±0.000 (p=1.00) | 0.654±0.000 (p=0.06) | 0.000±0.000 (p=1.00) | 0.654±0.000 (p=0.06) | -0.047, 0.000 |
| disc_secGBM | 0.000 | 1.000±0.000 (p=0.06) | 0.622±0.000 (p=0.03) | 1.000±0.000 (p=0.06) | 0.622±0.000 (p=0.03) | -0.177, 0.000 |
## E3_malaria_resnet50_full.json
| cell | baseline | shortcut fixed | shortcut retrain | residual fixed | residual retrain | random-dir null drop (mean, p95) |
|---|---|---|---|---|---|---|
| all | 0.928 | 0.927±0.006 (p=0.95) | 0.928±0.006 (p=0.45) | 0.506±0.059 (p=0.01) | 0.931±0.006 (p=0.03) | 0.115, 0.415 |
| pos | 0.922 | 0.922±0.013 (p=0.95) | 0.923±0.012 (p=0.65) | 0.200±0.400 (p=0.00) | 0.924±0.011 (p=0.03) | 0.072, 0.569 |
| neg | 0.934 | 0.934±0.012 (p=0.93) | 0.935±0.007 (p=0.58) | 0.800±0.400 (p=0.38) | 0.939±0.007 (p=0.03) | 0.159, 0.898 |
## E3_malaria_resnet50_rbc.json
| cell | baseline | shortcut fixed | shortcut retrain | residual fixed | residual retrain | random-dir null drop (mean, p95) |
|---|---|---|---|---|---|---|
| all | 0.890 | 0.886±0.007 (p=0.81) | 0.890±0.009 (p=0.74) | 0.504±0.056 (p=0.00) | 0.893±0.010 (p=0.03) | 0.103, 0.364 |
| pos | 0.879 | 0.880±0.022 (p=0.93) | 0.879±0.020 (p=0.87) | 0.328±0.417 (p=0.00) | 0.879±0.021 (p=0.03) | 0.071, 0.597 |
| neg | 0.902 | 0.893±0.010 (p=0.91) | 0.902±0.007 (p=0.84) | 0.703±0.398 (p=0.28) | 0.908±0.009 (p=0.06) | 0.136, 0.837 |
## E3_tb_dinov2_small.json
| cell | baseline | shortcut fixed | shortcut retrain | residual fixed | residual retrain | random-dir null drop (mean, p95) |
|---|---|---|---|---|---|---|
| A_pos | 1.000 | 1.000±0.000 (p=1.00) | 1.000±0.000 (p=1.00) | 0.000±0.000 (p=0.00) | 0.986±0.007 (p=0.05) | 0.019, 0.096 |
| B_pos | 0.991 | 0.991±0.009 (p=1.00) | 0.991±0.009 (p=1.00) | 0.000±0.000 (p=0.00) | 0.976±0.006 (p=0.10) | 0.026, 0.138 |
| normals | 0.999 | 0.999±0.001 (p=0.79) | 0.999±0.001 (p=1.00) | 1.000±0.000 (p=0.60) | 0.997±0.001 (p=0.03) | 0.006, 0.014 |
| all | 0.999 | 0.998±0.001 (p=0.92) | 0.999±0.001 (p=1.00) | 0.894±0.000 (p=0.02) | 0.995±0.001 (p=0.03) | 0.007, 0.025 |
## E3_tb_xrv_densenet121.json
| cell | baseline | shortcut fixed | shortcut retrain | residual fixed | residual retrain | random-dir null drop (mean, p95) |
|---|---|---|---|---|---|---|
| A_pos | 0.991 | 0.991±0.003 (p=0.79) | 0.989±0.003 (p=1.00) | 0.108±0.097 (p=0.00) | 0.989±0.003 (p=1.00) | 0.060, 0.357 |
| B_pos | 0.986 | 0.990±0.003 (p=0.56) | 0.988±0.005 (p=1.00) | 0.236±0.278 (p=0.00) | 0.986±0.007 (p=0.74) | 0.045, 0.269 |
| normals | 0.998 | 0.835±0.081 (p=0.01) | 0.998±0.000 (p=1.00) | 0.290±0.104 (p=0.00) | 0.998±0.001 (p=0.74) | 0.011, 0.057 |
| all | 0.997 | 0.851±0.073 (p=0.01) | 0.997±0.001 (p=0.97) | 0.278±0.108 (p=0.00) | 0.997±0.001 (p=1.00) | 0.016, 0.060 |
## E4_glioma_tcga.json
| variant | concordant AUC | discordant AUC (20 splits) | discordant bootstrap CI | label-permutation null |
|---|---|---|---|---|
| full (with grade) | 1.000 | 0.000±0.000 | [0.000, 0.000] | 0.476 |
| no grade [paper refit] | 0.877 | 0.738±0.000 | [0.649, 0.823] | 0.452 |
| no grade, median-impute | 0.806 | 0.812±0.000 | [0.736, 0.888] | 0.428 |
| no grade, median+missing flags | 0.948 | 0.563±0.036 | [0.394, 0.596] | 0.422 |
| no grade, no 1p/19q | 0.834 | 0.624±0.016 | [0.544, 0.716] | 0.464 |
| no grade, no 1p/19q, no TERT | 0.809 | 0.638±0.000 | [0.548, 0.723] | 0.528 |
| 1p/19q only | 0.698 | 0.527±0.000 | [0.500, 0.566] | 0.500 |
| TERT only | 0.581 | 0.336±0.000 | [0.284, 0.387] | 0.484 |
| MGMT only | 0.809 | 0.638±0.000 | [0.548, 0.723] | 0.528 |

Grade-stratified CV AUC (grade constant within stratum):
- no grade [paper refit] | LGG only: 0.891 [0.855, 0.925]
- no grade [paper refit] | GBM only: 0.606 [0.509, 0.704]
- no grade, no 1p/19q, no TERT | LGG only: 0.750 [0.686, 0.808]
- no grade, no 1p/19q, no TERT | GBM only: 0.604 [0.510, 0.703]
- missingness indicators only: 0.666 [0.631, 0.699]

Per-subgroup prediction rates: {"baseline": {"concordant_test": {"n": 257, "pred_IDHmut_rate": 0.490272373540856, "acc": 1.0}, "disc_IDHwt_LGG": {"n": 104, "pred_IDHmut_rate": 1.0, "acc": 0.0}, "disc_secondary_GBM": {"n": 37, "pred_IDHmut_rate": 0.0, "acc": 0.0}}, "grade_direction_ablated": {"concordant_test": {"n": 257, "pred_IDHmut_rate": 1.0, "acc": 0.490272373540856}, "disc_IDHwt_LGG": {"n": 104, "pred_IDHmut_rate": 1.0, "acc": 0.0}, "disc_secondary_GBM": {"n": 37, "pred_IDHmut_rate": 1.0, "acc": 1.0}}, "majority_class_baseline_concordant_test": 0.5097276264591439, "acc_if_predict_all_wildtype_concordant_test": 0.5097276264591439, "cos_shortcut_dir_vs_classifier_dir": 0.9999999999997812}
## E5_malaria_densenet121.json
groups=201, single-class groups=24.9%, cells in them=12.4%
random-crop parasite overlap: {'frac_with_any_overlap': 0.2895347993323173, 'mean_overlap': 0.012475116178393364}
| view | cell-level CV | patient-grouped CV |
|---|---|---|
| full | 0.986 [0.985, 0.987] | 0.981 [0.980, 0.982] |
| parasite | 0.926 [0.923, 0.929] | 0.917 [0.914, 0.921] |
| rbc | 0.974 [0.972, 0.975] | 0.964 [0.962, 0.966] |
| randcrop | 0.860 [0.855, 0.864] | 0.828 [0.823, 0.833] |
| gray | 0.984 [0.983, 0.985] | 0.980 [0.979, 0.981] |
| silhouette | 0.737 [0.731, 0.743] | 0.727 [0.721, 0.732] |
| handcrafted_size_shape_only | 0.585 [0.578, 0.591] | 0.576 [0.569, 0.583] |
| handcrafted_colour_only | 0.983 [0.982, 0.984] | 0.969 [0.967, 0.970] |
| handcrafted_all_but_parasite_frac | 0.985 [0.984, 0.986] | 0.972 [0.970, 0.973] |
RBC vs random crop (patient-grouped, paired bootstrap): {'diff': 0.1358424299827049, 'lo': 0.13127766869277238, 'hi': 0.1402145313992199, 'equivalent_within_margin': False, 'margin': 0.02}
Patient-identifiability probe: {'full': {'top1': 0.5820029027576198, 'chance': 0.004975124378109453}, 'rbc': {'top1': 0.5817610062893082, 'chance': 0.004975124378109453}, 'randcrop': {'top1': 0.3665940977261732, 'chance': 0.004975124378109453}, 'gray': {'top1': 0.4020319303338171, 'chance': 0.004975124378109453}, 'silhouette': {'top1': 0.07426221577164974, 'chance': 0.004975124378109453}}
## E5_malaria_dinov2_small.json
groups=201, single-class groups=24.9%, cells in them=12.4%
random-crop parasite overlap: {'frac_with_any_overlap': 0.2895347993323173, 'mean_overlap': 0.012475116178393364}
| view | cell-level CV | patient-grouped CV |
|---|---|---|
| full | 0.993 [0.992, 0.993] | 0.991 [0.990, 0.992] |
| parasite | 0.936 [0.934, 0.940] | 0.928 [0.925, 0.931] |
| rbc | 0.982 [0.980, 0.983] | 0.977 [0.975, 0.978] |
| randcrop | 0.874 [0.870, 0.877] | 0.848 [0.844, 0.852] |
| gray | 0.991 [0.990, 0.992] | 0.989 [0.988, 0.990] |
| silhouette | 0.751 [0.745, 0.756] | 0.742 [0.737, 0.747] |
| handcrafted_size_shape_only | 0.588 [0.581, 0.595] | 0.577 [0.570, 0.583] |
| handcrafted_colour_only | 0.983 [0.982, 0.984] | 0.967 [0.965, 0.969] |
| handcrafted_all_but_parasite_frac | 0.985 [0.983, 0.986] | 0.971 [0.969, 0.973] |
RBC vs random crop (patient-grouped, paired bootstrap): {'diff': 0.12862563902790247, 'lo': 0.12445996820502303, 'hi': 0.13275004187680164, 'equivalent_within_margin': False, 'margin': 0.02}
Patient-identifiability probe: {'full': {'top1': 0.5673681664247702, 'chance': 0.004975124378109453}, 'rbc': {'top1': 0.5667634252539913, 'chance': 0.004975124378109453}, 'randcrop': {'top1': 0.4276729559748428, 'chance': 0.004975124378109453}, 'gray': {'top1': 0.3950169327527818, 'chance': 0.004975124378109453}, 'silhouette': {'top1': 0.09772617319787132, 'chance': 0.004975124378109453}}
## E5_malaria_resnet50.json
groups=201, single-class groups=24.9%, cells in them=12.4%
random-crop parasite overlap: {'frac_with_any_overlap': 0.2895347993323173, 'mean_overlap': 0.012475116178393364}
| view | cell-level CV | patient-grouped CV |
|---|---|---|
| full | 0.982 [0.980, 0.983] | 0.977 [0.975, 0.978] |
| parasite | 0.907 [0.903, 0.911] | 0.899 [0.895, 0.904] |
| rbc | 0.964 [0.963, 0.966] | 0.952 [0.950, 0.954] |
| randcrop | 0.844 [0.839, 0.849] | 0.811 [0.805, 0.815] |
| gray | 0.978 [0.977, 0.980] | 0.975 [0.973, 0.976] |
| silhouette | 0.726 [0.721, 0.731] | 0.718 [0.713, 0.723] |
| handcrafted_size_shape_only | 0.586 [0.579, 0.593] | 0.575 [0.568, 0.582] |
| handcrafted_colour_only | 0.982 [0.981, 0.984] | 0.968 [0.966, 0.970] |
| handcrafted_all_but_parasite_frac | 0.985 [0.984, 0.986] | 0.971 [0.969, 0.973] |
RBC vs random crop (patient-grouped, paired bootstrap): {'diff': 0.14169553267700952, 'lo': 0.1368136936308295, 'hi': 0.14626391996747715, 'equivalent_within_margin': False, 'margin': 0.02}
Patient-identifiability probe: {'full': {'top1': 0.49927431059506533, 'chance': 0.004975124378109453}, 'rbc': {'top1': 0.49117077890662797, 'chance': 0.004975124378109453}, 'randcrop': {'top1': 0.3299467827769715, 'chance': 0.004975124378109453}, 'gray': {'top1': 0.3362360909530721, 'chance': 0.004975124378109453}, 'silhouette': {'top1': 0.06833575229801644, 'chance': 0.004975124378109453}}
## E5_malaria_resnet50_pnum.json
groups=201, single-class groups=24.9%, cells in them=12.4%
random-crop parasite overlap: {'frac_with_any_overlap': 0.2895347993323173, 'mean_overlap': 0.012475116178393364}
| view | cell-level CV | patient-grouped CV |
|---|---|---|
| full | 0.982 [0.980, 0.983] | 0.977 [0.976, 0.979] |
| parasite | 0.907 [0.903, 0.911] | 0.899 [0.895, 0.903] |
| rbc | 0.964 [0.963, 0.966] | 0.952 [0.949, 0.954] |
| randcrop | 0.844 [0.839, 0.849] | 0.810 [0.804, 0.815] |
| gray | 0.978 [0.977, 0.980] | 0.974 [0.972, 0.975] |
| silhouette | 0.726 [0.721, 0.731] | 0.716 [0.710, 0.721] |
| handcrafted_size_shape_only | 0.587 [0.580, 0.593] | 0.572 [0.565, 0.578] |
| handcrafted_colour_only | 0.983 [0.981, 0.984] | 0.967 [0.965, 0.969] |
| handcrafted_all_but_parasite_frac | 0.985 [0.984, 0.986] | 0.970 [0.968, 0.972] |
RBC vs random crop (patient-grouped, paired bootstrap): {'diff': 0.14224253857592484, 'lo': 0.13737378246131096, 'hi': 0.1471195379412165, 'equivalent_within_margin': False, 'margin': 0.02}
Patient-identifiability probe: {'full': {'top1': 0.49528301886792453, 'chance': 0.004975124378109453}, 'rbc': {'top1': 0.4910498306724722, 'chance': 0.004975124378109453}, 'randcrop': {'top1': 0.3220851475568457, 'chance': 0.004975124378109453}, 'gray': {'top1': 0.3297048863086599, 'chance': 0.004975124378109453}, 'silhouette': {'top1': 0.06966618287373004, 'chance': 0.004975124378109453}}
## E6_planted_dinov2_small.json
| rho | flag rate | AUC concordant | AUC flipped | shortcut tax | cos(recovered, planted) | LEACE gain on flipped | avail. (retrain) |
|---|---|---|---|---|---|---|---|
| 0.5 | 0.00 | 0.868 | 0.867 | 0.001 | 0.68 | -0.000 | 0.867 |
| 0.6 | 0.40 | 0.872 | 0.857 | 0.016 | 0.69 | 0.013 | 0.869 |
| 0.7 | 0.85 | 0.885 | 0.827 | 0.058 | 0.69 | 0.049 | 0.878 |
| 0.8 | 1.00 | 0.901 | 0.757 | 0.144 | 0.69 | 0.123 | 0.889 |
| 0.9 | 1.00 | 0.928 | 0.616 | 0.312 | 0.67 | 0.250 | 0.895 |
| 1.0 | 0.90 | 0.967 | 0.301 | 0.666 | 0.64 | 0.142 | 0.517 |
## E6_planted_resnet50.json
| rho | flag rate | AUC concordant | AUC flipped | shortcut tax | cos(recovered, planted) | LEACE gain on flipped | avail. (retrain) |
|---|---|---|---|---|---|---|---|
| 0.5 | 0.00 | 0.884 | 0.883 | 0.001 | 0.72 | -0.002 | 0.881 |
| 0.6 | 0.25 | 0.891 | 0.871 | 0.020 | 0.72 | 0.009 | 0.882 |
| 0.7 | 0.85 | 0.904 | 0.840 | 0.064 | 0.71 | 0.045 | 0.890 |
| 0.8 | 1.00 | 0.923 | 0.768 | 0.155 | 0.70 | 0.122 | 0.901 |
| 0.9 | 1.00 | 0.949 | 0.622 | 0.327 | 0.69 | 0.258 | 0.913 |
| 1.0 | 1.00 | 0.985 | 0.295 | 0.691 | 0.66 | 0.203 | 0.507 |
## E6_planted_xrv_densenet121.json
| rho | flag rate | AUC concordant | AUC flipped | shortcut tax | cos(recovered, planted) | LEACE gain on flipped | avail. (retrain) |
|---|---|---|---|---|---|---|---|
| 0.5 | 0.00 | 0.896 | 0.896 | -0.001 | 0.26 | -0.002 | 0.895 |
| 0.6 | 0.00 | 0.901 | 0.887 | 0.014 | 0.27 | -0.003 | 0.887 |
| 0.7 | 0.30 | 0.911 | 0.867 | 0.044 | 0.26 | 0.011 | 0.887 |
| 0.8 | 0.75 | 0.925 | 0.824 | 0.101 | 0.26 | 0.043 | 0.884 |
| 0.9 | 0.70 | 0.943 | 0.733 | 0.210 | 0.25 | 0.078 | 0.864 |
| 1.0 | 0.00 | 0.969 | 0.538 | 0.431 | 0.25 | -0.182 | 0.540 |
## E7_transport_dinov2_to_resnet50.json  (eraser transport A->B; held-out source-probe AUC in B)
| condition | linear | MLP |
|---|---|---|
| B_none | 1.000 | 1.000 |
| B_own_LEACE | 0.529 | 0.986 |
| B_transported_A_LEACE | 0.931 | 0.997 |
| B_transported_random_rank1 | 1.000 | 0.999 |
| A_own_LEACE_reference | 0.511 | nan |
map R2 A->B 0.357, B->A 0.323

Head inheritance on source-matched data:
- stitched_headA_via_g_on_B: 0.467 [0.428, 0.509]
- native_headB: 0.464 [0.424, 0.504]
- native_headA_on_A: 0.471 [0.433, 0.514]
- matched_trained_oracle_A_trainfit: 0.999
- matched_trained_oracle_B_trainfit: 1.0
- corr_stitched_vs_nativeB_scores: 0.782
- matched_TB_detection_cv_AUC_B_none: 0.85
- matched_TB_detection_cv_AUC_B_own_LEACE: 0.848
- matched_TB_detection_cv_AUC_B_transported_A_LEACE: 0.844
## E7_transport_dinov2_to_xrv.json  (eraser transport A->B; held-out source-probe AUC in B)
| condition | linear | MLP |
|---|---|---|
| B_none | 0.999 | 0.999 |
| B_own_LEACE | 0.524 | 0.987 |
| B_transported_A_LEACE | 0.987 | 0.991 |
| B_transported_random_rank1 | 0.998 | 0.999 |
| A_own_LEACE_reference | 0.511 | nan |
map R2 A->B 0.273, B->A 0.140

Head inheritance on source-matched data:
- stitched_headA_via_g_on_B: 0.499 [0.461, 0.540]
- native_headB: 0.570 [0.531, 0.611]
- native_headA_on_A: 0.471 [0.433, 0.514]
- matched_trained_oracle_A_trainfit: 0.999
- matched_trained_oracle_B_trainfit: 1.0
- corr_stitched_vs_nativeB_scores: 0.757
- matched_TB_detection_cv_AUC_B_none: 0.808
- matched_TB_detection_cv_AUC_B_own_LEACE: 0.815
- matched_TB_detection_cv_AUC_B_transported_A_LEACE: 0.813
## E7_transport_resnet50_to_dinov2.json  (eraser transport A->B; held-out source-probe AUC in B)
| condition | linear | MLP |
|---|---|---|
| B_none | 1.000 | 0.999 |
| B_own_LEACE | 0.511 | 0.991 |
| B_transported_A_LEACE | 0.997 | 0.994 |
| B_transported_random_rank1 | 1.000 | 0.999 |
| A_own_LEACE_reference | 0.529 | nan |
map R2 A->B 0.323, B->A 0.357

Head inheritance on source-matched data:
- stitched_headA_via_g_on_B: 0.463 [0.426, 0.503]
- native_headB: 0.471 [0.433, 0.514]
- native_headA_on_A: 0.464 [0.424, 0.504]
- matched_trained_oracle_A_trainfit: 1.0
- matched_trained_oracle_B_trainfit: 0.999
- corr_stitched_vs_nativeB_scores: 0.897
- matched_TB_detection_cv_AUC_B_none: 0.839
- matched_TB_detection_cv_AUC_B_own_LEACE: 0.843
- matched_TB_detection_cv_AUC_B_transported_A_LEACE: 0.836
## E7_transport_xrv_to_dinov2.json  (eraser transport A->B; held-out source-probe AUC in B)
| condition | linear | MLP |
|---|---|---|
| B_none | 1.000 | 0.999 |
| B_own_LEACE | 0.511 | 0.991 |
| B_transported_A_LEACE | 0.991 | 0.993 |
| B_transported_random_rank1 | 1.000 | 0.999 |
| A_own_LEACE_reference | 0.524 | nan |
map R2 A->B 0.140, B->A 0.273

Head inheritance on source-matched data:
- stitched_headA_via_g_on_B: 0.541 [0.503, 0.582]
- native_headB: 0.471 [0.433, 0.514]
- native_headA_on_A: 0.570 [0.531, 0.611]
- matched_trained_oracle_A_trainfit: 1.0
- matched_trained_oracle_B_trainfit: 0.999
- corr_stitched_vs_nativeB_scores: 0.845
- matched_TB_detection_cv_AUC_B_none: 0.839
- matched_TB_detection_cv_AUC_B_own_LEACE: 0.843
- matched_TB_detection_cv_AUC_B_transported_A_LEACE: 0.847
## E8_cka_resnet50_dinov2.json  (CKA blindness)
{
 "source_probe_AUC": {
  "A": 0.99998758066359,
  "B": 0.999986338729949,
  "A_erased": 0.4709946398144054,
  "B_erased": 0.4932289777892588
 },
 "CKA": {
  "A_vs_B": 0.40762490034103394,
  "A_vs_A_erased": 0.8901606798171997,
  "B_vs_B_erased": 0.9301667213439941,
  "A_erased_vs_B_erased": 0.3525296449661255
 },
 "variance_share_removed": {
  "A": 0.04467892646789551,
  "B": 0.043262779712677
 },
 "random_rank1_reference": {
  "CKA_A_vs_A_erased_mean": 0.999999144491537,
  "delta_CKA_AB_mean": 0.00017469089348152444
 },
 "delta_CKA_A_vs_B_after_erasing_source": 0.05509525537490845
}
## E8_cka_xrv_dinov2.json  (CKA blindness)
{
 "source_probe_AUC": {
  "A": 0.9995591135574443,
  "B": 0.999986338729949,
  "A_erased": 0.48149146294815176,
  "B_erased": 0.4932277358556178
 },
 "CKA": {
  "A_vs_B": 0.20198340713977814,
  "A_vs_A_erased": 0.9776376485824585,
  "B_vs_B_erased": 0.9301667213439941,
  "A_erased_vs_B_erased": 0.15675796568393707
 },
 "variance_share_removed": {
  "A": 0.03222900629043579,
  "B": 0.043262779712677
 },
 "random_rank1_reference": {
  "CKA_A_vs_A_erased_mean": 0.9999949746194362,
  "delta_CKA_AB_mean": 0.00017224728701514675
 },
 "delta_CKA_A_vs_B_after_erasing_source": 0.045225441455841064
}
## E9_patientstate_densenet121.json  (patient state)
{"n_patients": 201, "patients_with_any_infected_cell": 151, "uninfected_cells_from_infected_patients": 10364, "uninfected_cells_from_patients_with_no_infected_cell": 3415}
| view | AUC bystander vs healthy-patient uninfected | FPR bystander | FPR healthy | patient-status AUC from uninfected cells only |
|---|---|---|---|---|
| full | 0.675 | 0.056 | 0.034 | 0.949 [0.904, 0.982] |
| parasite | 0.505 | 0.067 | 0.060 | 0.875 [0.821, 0.922] |
| rbc | 0.678 | 0.083 | 0.044 | 0.948 [0.902, 0.980] |
| randcrop | 0.690 | 0.227 | 0.097 | 0.930 [0.881, 0.969] |
| gray | 0.592 | 0.060 | 0.043 | 0.948 [0.909, 0.978] |
| silhouette | 0.662 | 0.364 | 0.164 | 0.874 [0.812, 0.928] |
## E9_patientstate_dinov2_small.json  (patient state)
{"n_patients": 201, "patients_with_any_infected_cell": 151, "uninfected_cells_from_infected_patients": 10364, "uninfected_cells_from_patients_with_no_infected_cell": 3415}
| view | AUC bystander vs healthy-patient uninfected | FPR bystander | FPR healthy | patient-status AUC from uninfected cells only |
|---|---|---|---|---|
| full | 0.612 | 0.040 | 0.028 | 0.946 [0.903, 0.981] |
| parasite | 0.512 | 0.059 | 0.050 | 0.886 [0.825, 0.938] |
| rbc | 0.651 | 0.073 | 0.039 | 0.949 [0.904, 0.981] |
| randcrop | 0.699 | 0.192 | 0.088 | 0.941 [0.894, 0.977] |
| gray | 0.608 | 0.044 | 0.029 | 0.909 [0.846, 0.952] |
| silhouette | 0.660 | 0.352 | 0.158 | 0.854 [0.788, 0.909] |
## E9_patientstate_resnet50.json  (patient state)
{"n_patients": 201, "patients_with_any_infected_cell": 151, "uninfected_cells_from_infected_patients": 10364, "uninfected_cells_from_patients_with_no_infected_cell": 3415}
| view | AUC bystander vs healthy-patient uninfected | FPR bystander | FPR healthy | patient-status AUC from uninfected cells only |
|---|---|---|---|---|
| full | 0.644 | 0.068 | 0.040 | 0.954 [0.909, 0.987] |
| parasite | 0.505 | 0.075 | 0.073 | 0.796 [0.721, 0.857] |
| rbc | 0.669 | 0.108 | 0.052 | 0.953 [0.910, 0.988] |
| randcrop | 0.665 | 0.246 | 0.111 | 0.911 [0.861, 0.954] |
| gray | 0.568 | 0.079 | 0.048 | 0.934 [0.883, 0.967] |
| silhouette | 0.645 | 0.364 | 0.187 | 0.886 [0.830, 0.935] |
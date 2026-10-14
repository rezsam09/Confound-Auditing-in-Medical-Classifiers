"""Collect results/*.json into results/SUMMARY.md ."""
import json, glob
from pathlib import Path
R = Path(__file__).resolve().parent.parent / "results"; L = []
f = lambda v: f"{v['auc']:.3f} [{v['lo']:.3f}, {v['hi']:.3f}]"
for p in sorted(R.glob("E1_*.json")):
    d = json.load(open(p)); L += [f"## {p.name}", "| test | AUC [95% CI] |", "|---|---|"]
    L += [f"| {k} | {f(v) if isinstance(v, dict) else round(v, 3)} |" for k, v in d.items()]
for p in sorted(R.glob("E2_*.json")):
    d = json.load(open(p)); L += [f"## {p.name}  (held-out source-probe AUC after erasure)", "| eraser | linear | MLP | GBM | matched-TB-detection AUC |", "|---|---|---|---|---|"]
    L += [f"| {k} | {v.get('linear', float('nan')):.3f} | {v.get('mlp', float('nan')):.3f} | {v.get('gbm', float('nan')):.3f} | {v.get('matched_TB_detection_AUC', float('nan')):.3f} |" for k, v in d.items()]
for p in sorted(R.glob("E3_*.json")):
    d = json.load(open(p)); L += [f"## {p.name}", "| cell | baseline | shortcut fixed | shortcut retrain | residual fixed | residual retrain | random-dir null drop (mean, p95) |", "|---|---|---|---|---|---|---|"]
    for c, v in d.items():
        if not isinstance(v, dict) or "baseline" not in v: continue
        g = lambda k: f"{v[k]['mean']:.3f}±{v[k]['sd']:.3f} (p={v[k]['p_vs_cov_random_null']:.2f})"
        L.append(f"| {c} | {v['baseline']['mean']:.3f} | {g('shortcut_fixed')} | {g('shortcut_retrain')} | {g('residual_fixed')} | {g('residual_retrain')} | {v['null_drop_fixed_mean_p95'][0]:.3f}, {v['null_drop_fixed_mean_p95'][1]:.3f} |")
for p in sorted(R.glob("E4_*.json")):
    d = json.load(open(p)); L += [f"## {p.name}", "| variant | concordant AUC | discordant AUC (20 splits) | discordant bootstrap CI | label-permutation null |", "|---|---|---|---|---|"]
    for k, v in d.items():
        if isinstance(v, dict) and "conc_auc" in v:
            L.append(f"| {k} | {v['conc_auc']['mean']:.3f} | {v['disc_auc']['mean']:.3f}±{v['disc_auc']['sd']:.3f} | [{v['disc_auc_boot']['lo']:.3f}, {v['disc_auc_boot']['hi']:.3f}] | {v['perm_null_disc_auc']['mean']:.3f} |")
    L += ["", "Grade-stratified CV AUC (grade constant within stratum):"] + [f"- {k}: {f(v)}" for k, v in d.get("grade_stratified_cv_auc", {}).items()]
    if "missingness_indicators_only_cv_auc" in d: L.append(f"- missingness indicators only: {f(d['missingness_indicators_only_cv_auc'])}")
    L += ["", "Per-subgroup prediction rates: " + json.dumps(d.get("per_subgroup_prediction_rates"))]
for p in sorted(R.glob("E5_*.json")):
    d = json.load(open(p)); L += [f"## {p.name}", f"groups={d['n_groups']}, single-class groups={d['frac_groups_single_class']:.1%}, cells in them={d['frac_cells_in_single_class_groups']:.1%}",
        f"random-crop parasite overlap: {d['random_crop_parasite_overlap']}", "| view | cell-level CV | patient-grouped CV |", "|---|---|---|"]
    L += [f"| {k} | {f(v['cell_random_cv'])} | {f(v['patient_group_cv'])} |" for k, v in d["views"].items()]
    L += [f"RBC vs random crop (patient-grouped, paired bootstrap): {d.get('rbc_vs_randcrop_patient_cv')}", f"Patient-identifiability probe: {d.get('patient_identifiability')}"]
for p in sorted(R.glob("E6_*.json")):
    d = json.load(open(p)); L += [f"## {p.name}", "| rho | flag rate | AUC concordant | AUC flipped | shortcut tax | cos(recovered, planted) | LEACE gain on flipped | avail. (retrain) |", "|---|---|---|---|---|---|---|---|"]
    L += [f"| {r} | {v['flag_rate']:.2f} | {v['auc_conc']['mean']:.3f} | {v['auc_flip']['mean']:.3f} | {v['shortcut_tax']['mean']:.3f} | {v['cos_to_true_planted_dir']['mean']:.2f} | {v['reliance_gain_flip_auc']['mean']:.3f} | {v['avail_flip_auc_after_erase_retrain']['mean']:.3f} |" for r, v in d.items()]
for p in sorted(R.glob("E7_*.json")):
    d = json.load(open(p)); L += [f"## {p.name}  (eraser transport A->B; held-out source-probe AUC in B)", "| condition | linear | MLP |", "|---|---|---|"]
    L += [f"| {k} | {v.get('linear', float('nan')):.3f} | {v.get('mlp', float('nan')):.3f} |" for k, v in d["source_probe_AUC_in_B"].items()]
    L += [f"map R2 A->B {d['map_R2_A_to_B_heldout']:.3f}, B->A {d['map_R2_B_to_A_heldout']:.3f}", "", "Head inheritance on source-matched data:"]
    L += [f"- {k}: {(f(v) if isinstance(v, dict) else round(v, 3))}" for k, v in d.get("head_inheritance_on_matched", {}).items()]
for p in sorted(R.glob("E8_*.json")):
    d = json.load(open(p)); L += [f"## {p.name}  (CKA blindness)", json.dumps(d, indent=1)]
for p in sorted(R.glob("E9_*.json")):
    d = json.load(open(p)); L += [f"## {p.name}  (patient state)", json.dumps({k: v for k, v in d.items() if k != "views"}), "| view | AUC bystander vs healthy-patient uninfected | FPR bystander | FPR healthy | patient-status AUC from uninfected cells only |", "|---|---|---|---|---|"]
    for k, v in d["views"].items():
        ps = v.get("patient_level_status_AUC_from_uninfected_cells_only", {})
        L.append(f"| {k} | {v.get('infected_score_AUC_bystander_vs_healthyPatient_uninfected', float('nan')):.3f} | {v.get('false_positive_rate_bystander', float('nan')):.3f} | {v.get('false_positive_rate_healthy', float('nan')):.3f} | {ps.get('auc', float('nan')):.3f} [{ps.get('lo', float('nan')):.3f}, {ps.get('hi', float('nan')):.3f}] |")
(R / "SUMMARY.md").write_text("\n".join(L)); print("\n".join(L)[:6000]); print("\n[written]", R / "SUMMARY.md")

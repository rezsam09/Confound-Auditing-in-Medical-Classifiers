#!/usr/bin/env bash
# Usage: cp paths.sh.example paths.sh ; edit it ; bash reproduce_all.sh [extract|analyze|addons|all]
# extract needs a GPU (about 2-3 h with cuDNN off); everything else is CPU.
STEP=${1:-all}
cd "$(dirname "$0")/scripts"
source ../paths.sh
mkdir -p ../feats ../results
M=../feats/tb_manifest.csv
run(){ echo "=== $1 $2 $3 $4"; "$@" || echo "!!! FAILED: $1 $2 $3 $4"; }

if [[ $STEP == extract || $STEP == all ]]; then
  run python make_tb_manifest.py --belarus_dir $BELARUS --rsna_dir $RSNA --shenzhen_dir $SHENZHEN --montgomery_dir $MONTGOMERY --extent_csv $EXTENT_CSV --out $M
  for B in xrv_densenet121 dinov2_small resnet50; do
    run python extract_features.py tb --manifest $M --backbone $B --out ../feats/tb_$B.npz
    run python extract_features.py tb_planted --manifest $M --backbone $B --out ../feats/tbplanted_$B.npz
  done
  run python extract_features.py tb --manifest $M --backbone xrv_densenet121 --harmonize --out ../feats/tb_xrv_densenet121_harmonized.npz
  for B in resnet50 densenet121 dinov2_small; do
    run python extract_features.py malaria --root $MALARIA --backbone $B --mask adaptive --out ../feats/mal_$B.npz
  done
fi

if [[ $STEP == analyze || $STEP == all ]]; then
  for B in resnet50 densenet121 dinov2_small; do run python E5_malaria_patient_split.py --feats ../feats/mal_$B.npz --tag $B; done
  run python E5_malaria_patient_split.py --feats ../feats/mal_resnet50.npz --tag resnet50_pnum --group_by pnum
  for B in xrv_densenet121 dinov2_small resnet50; do
    run python E1_tb_source_matched.py --manifest $M --feats ../feats/tb_$B.npz --tag $B
    run python E2_leace_vs_inlp.py --manifest $M --feats ../feats/tb_$B.npz --tag $B
    run python E6_planted_shortcut_calibration.py --feats ../feats/tbplanted_$B.npz --tag $B
  done
  run python E1_tb_source_matched.py --manifest $M --feats ../feats/tb_xrv_densenet121_harmonized.npz --tag xrv_harmonized
  run python E2_leace_vs_inlp.py --manifest $M --feats ../feats/tb_xrv_densenet121_harmonized.npz --tag xrv_harmonized
  run python E4_glioma_leakage.py --csv $GLIOMA_CSV --tag tcga
  run python E3_ablation_controls.py glioma --csv $GLIOMA_CSV --tag tcga --seeds 10
  run python E3_ablation_controls.py malaria --feats ../feats/mal_resnet50.npz --view full --tag resnet50_full
  run python E3_ablation_controls.py malaria --feats ../feats/mal_resnet50.npz --view rbc --tag resnet50_rbc
  run python E3_ablation_controls.py tb --manifest $M --feats ../feats/tb_xrv_densenet121.npz --tag xrv_densenet121 --seeds 3
  run python E3_ablation_controls.py tb --manifest $M --feats ../feats/tb_dinov2_small.npz --tag dinov2_small --seeds 2
fi

if [[ $STEP == addons || $STEP == all ]]; then
  for B in resnet50 densenet121 dinov2_small; do run python E9_patient_state.py --feats ../feats/mal_$B.npz --tag $B; done
  run python E7_eraser_transport.py --manifest $M --featsA ../feats/tb_xrv_densenet121.npz --featsB ../feats/tb_dinov2_small.npz --tag xrv_to_dinov2
  run python E7_eraser_transport.py --manifest $M --featsA ../feats/tb_dinov2_small.npz --featsB ../feats/tb_xrv_densenet121.npz --tag dinov2_to_xrv
  run python E7_eraser_transport.py --manifest $M --featsA ../feats/tb_resnet50.npz --featsB ../feats/tb_dinov2_small.npz --tag resnet50_to_dinov2
  run python E7_eraser_transport.py --manifest $M --featsA ../feats/tb_dinov2_small.npz --featsB ../feats/tb_resnet50.npz --tag dinov2_to_resnet50
  run python E8_cka_blindness.py --manifest $M --featsA ../feats/tb_xrv_densenet121.npz --featsB ../feats/tb_dinov2_small.npz --tag xrv_dinov2
  run python E8_cka_blindness.py --manifest $M --featsA ../feats/tb_resnet50.npz --featsB ../feats/tb_dinov2_small.npz --tag resnet50_dinov2
fi

run python make_report.py
echo REPRODUCE_DONE

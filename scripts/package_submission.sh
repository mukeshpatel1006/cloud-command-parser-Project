#!/usr/bin/env bash
# usage: scripts/package_submission.sh 230101006   (put the scanned notes as ./<roll>.pdf and report/report.pdf first)
set -euo pipefail
R=$1
[ -f "$R.pdf" ] || { echo "missing $R.pdf (scanned handwritten notes)"; exit 1; }
[ -f report/report.pdf ] || { echo "missing report/report.pdf"; exit 1; }
rm -f "$R.zip"
zip -r "$R.zip" . -x '.git/*' 'models_local/*' 'release/*' '*.safetensors' '__pycache__/*' '.pytest_cache/*' '.ruff_cache/*' "$R.zip"
unzip -l "$R.zip" | tail -1

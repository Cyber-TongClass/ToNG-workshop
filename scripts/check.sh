#!/usr/bin/env bash
set -euo pipefail
mode="${1:-project}"
[[ "$mode" == project || "$mode" == final ]] || { echo 'usage: bash scripts/check.sh [project|final]'; exit 2; }
python -m hybridml.environment
python .course/local_check.py protected
python .course/local_check.py hygiene
python .course/local_check.py native
bash scripts/build.sh
python -m pytest -q tests/public
if [[ "$mode" == final ]]; then
    python .course/local_check.py history
    bash scripts/train.sh
    python -m hybridml.evaluate
fi
echo 'Checks passed.'

#!/usr/bin/env bash
# Task 4.5: rolling update v1->v2 under load, then rollback. Run the load test separately for >= 3 min:
#   locust -f tools/locustfile.py --headless --users 4 --spawn-rate 4 --run-time 4m --host http://localhost:8080 --csv results/rolling
# then run this script ~30 s after Locust started.
set -euo pipefail
mkdir -p results
{
 kubectl -n app set env deploy/parser MODEL_VERSION=v2 MODEL_URI=s3://models/v2/
 kubectl -n app rollout status deploy/parser --timeout=300s
 sleep 20
 kubectl -n app rollout undo deploy/parser
 kubectl -n app rollout status deploy/parser --timeout=300s
 kubectl -n app get deploy parser -o jsonpath='{.spec.template.spec.containers[0].env}'; echo
 for i in 1 2 3 4 5; do curl -si -X POST localhost:8080/parse -H 'content-type: application/json' -d '{"text":"what time is it"}' | grep -i x-model-version; done
} 2>&1 | tee results/rolling_update.log

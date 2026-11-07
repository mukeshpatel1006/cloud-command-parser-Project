#!/usr/bin/env bash
# Task 4.6: delete one pod while Locust runs (start Locust first, ~3 min run).
set -euo pipefail
mkdir -p results
{
 kubectl -n app get pods -l app=parser
 P=$(kubectl -n app get pods -l app=parser -o jsonpath='{.items[0].metadata.name}')
 echo "deleting $P"; kubectl -n app delete pod $P --wait=false
 for i in $(seq 1 30); do sleep 4; date +%T; kubectl -n app get deploy parser; done
 kubectl -n app get pods -l app=parser
} 2>&1 | tee results/recovery.log

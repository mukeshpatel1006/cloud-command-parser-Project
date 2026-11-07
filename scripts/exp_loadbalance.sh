#!/usr/bin/env bash
# Task 4.8: exactly two Ready replicas, standard Locust command through the Ingress.
# The HPA would scale back to 1 when idle, so pin it to 2 for this run, then restore.
set -euo pipefail
mkdir -p results
kubectl -n app patch hpa parser -p '{"spec":{"minReplicas":2}}'
kubectl -n app scale deploy parser --replicas=2
kubectl -n app wait --for=condition=Ready pod -l app=parser --timeout=300s
kubectl -n app get pods -l app=parser -o wide | tee results/loadbalance_pods.txt
locust -f tools/locustfile.py --headless --users 4 --spawn-rate 4 --run-time 2m \
  --host http://localhost:8080 --csv results/loadtest 2>&1 | tee results/loadtest_console.txt || true
kubectl -n app patch hpa parser -p '{"spec":{"minReplicas":1}}'
cat results/loadtest_headers.json

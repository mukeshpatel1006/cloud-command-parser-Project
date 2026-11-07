#!/usr/bin/env bash
# Task 4.4: evidence of scale 1->2 under load and back to 1 (run Locust for ~6 min in another terminal with --users 8).
mkdir -p results
for i in $(seq 1 90); do date +%T; kubectl -n app get hpa parser --no-headers; kubectl -n app top pods --no-headers; sleep 10; done | tee results/hpa.log

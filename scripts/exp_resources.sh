#!/usr/bin/env bash
# Task 7: sample `kubectl top pods` every 10 s while the standard Locust test runs in another terminal.
mkdir -p results
for i in $(seq 1 14); do date +%T; kubectl -n app top pods --no-headers; sleep 10; done | tee results/kubectl_top.log

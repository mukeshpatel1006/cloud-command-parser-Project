#!/usr/bin/env bash
# Task 3: 50 sequential requests against the container at 1 CPU / 1 GiB; records peak memory + OOM flag.
# Needs a model in object storage: run `make up` first (uses the port-forward to SeaweedFS). Output -> results/mem_test.txt
set -euo pipefail
. scripts/s3env.sh
mkdir -p results; docker rm -f cc-memtest >/dev/null 2>&1 || true
docker run -d --name cc-memtest --network host --cpus 1 --memory 1g \
  -e MODEL_URI=s3://models/v1/ -e MODEL_VERSION=v1 -e S3_ENDPOINT=$S3_ENDPOINT \
  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e HOSTNAME=memtest cc-parser:1 >/dev/null
for i in $(seq 1 120); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:8000/readyz)" = 200 ] && break; sleep 2; done
( while true; do docker stats --no-stream --format '{{.MemUsage}}' cc-memtest >> results/mem_samples.txt; sleep 1; done ) & SP=$!
ok=0
for i in $(seq 1 50); do
  t=$(python3 -c "import json;print(json.loads(open('data/validation.jsonl').readlines()[$i-1])['text'])")
  c=$(curl -s -o /dev/null -w '%{http_code}' -X POST localhost:8000/parse -H 'content-type: application/json' -d "{\"text\":\"$t\"}")
  [ "$c" = 200 ] && ok=$((ok+1))
done
kill $SP 2>/dev/null || true
{ echo "requests_ok=$ok/50"; echo "OOMKilled=$(docker inspect -f '{{.State.OOMKilled}}' cc-memtest)";
  echo "memory samples (docker stats MemUsage / limit):"; sort -u results/mem_samples.txt | sort -h | tail -3; } | tee results/mem_test.txt
docker rm -f cc-memtest >/dev/null

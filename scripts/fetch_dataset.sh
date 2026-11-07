#!/usr/bin/env bash
# Download teacher shards from object storage, run clean.py, upload train.jsonl + train.sha256 to datasets/v1/.
set -euo pipefail
. scripts/s3env.sh
python3 - <<'PY'
import os, sys
sys.path.insert(0, "worker")
import s3util
s3 = s3util.client()
os.makedirs("data/shards", exist_ok=True)
for o in s3.list_objects_v2(Bucket="datasets", Prefix="teacher/").get("Contents", []):
    s3.download_file("datasets", o["Key"], "data/shards/" + os.path.basename(o["Key"]))
    print("downloaded", o["Key"])
PY
mkdir -p data/v1 results
python3 worker/clean.py --shards data/shards --out-dir data/v1 | tee results/clean_counts.txt
cp data/v1/clean_counts.json results/clean_counts.json
python3 - <<'PY'
import sys
sys.path.insert(0, "worker")
import s3util
s3 = s3util.client()
for f in ("train.jsonl", "train.sha256"):
    s3.upload_file("data/v1/" + f, "datasets", "v1/" + f)
print("uploaded datasets/v1/*")
PY
cp data/v1/train.sha256 results/train.sha256

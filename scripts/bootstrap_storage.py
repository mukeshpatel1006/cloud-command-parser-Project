"""Create buckets datasets + models; upload commands_pool.jsonl to datasets (idempotent)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "worker"))
import s3util  # noqa: E402

s3 = s3util.client()
for b in ("datasets", "models"):
    try:
        s3.create_bucket(Bucket=b)
        print("created bucket", b)
    except Exception as e:  # noqa: BLE001
        print("bucket", b, "->", type(e).__name__)
s3.upload_file("data/commands_pool.jsonl", "datasets", "commands_pool.jsonl")
print("uploaded datasets/commands_pool.jsonl")

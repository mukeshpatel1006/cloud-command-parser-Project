"""Upload a model dir to s3://models/<version>/ together with model.sha256 (checksum of the Release tarball).
python training/upload_model.py models_local/v1 v1 release/model-v1.sha256"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "worker"))
import s3util  # noqa: E402

d, ver, sha = sys.argv[1:4]
s3 = s3util.client()
for name in os.listdir(d):
    p = os.path.join(d, name)
    if os.path.isfile(p):
        s3.upload_file(p, "models", f"{ver}/{name}")
        print("uploaded", f"models/{ver}/{name}")
s3.upload_file(sha, "models", f"{ver}/model.sha256")
print("uploaded", f"models/{ver}/model.sha256")

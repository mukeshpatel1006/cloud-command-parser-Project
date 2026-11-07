"""Tiny S3 helper (SeaweedFS S3 gateway). Credentials come from the standard AWS_* env vars
(injected from a Kubernetes Secret); nothing is stored in the repository."""
import os

import boto3
from botocore.config import Config


def client(endpoint=None):
    return boto3.client(
        "s3",
        endpoint_url=endpoint or os.environ["S3_ENDPOINT"],
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}, retries={"max_attempts": 5}),
    )


def get_text(s3, bucket, key):
    return s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")


def put_text(s3, bucket, key, text):
    s3.put_object(Bucket=bucket, Key=key, Body=text.encode("utf-8"))


def exists(s3, bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except Exception:
        return False

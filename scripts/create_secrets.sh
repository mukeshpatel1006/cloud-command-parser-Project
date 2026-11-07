#!/usr/bin/env bash
# Generates random S3 credentials at deploy time and stores them ONLY as Kubernetes Secrets (never in Git).
set -euo pipefail
for ns in data pipeline app; do kubectl get ns $ns >/dev/null 2>&1 || kubectl create ns $ns; done
if kubectl -n data get secret s3-credentials >/dev/null 2>&1; then echo "secrets exist"; exit 0; fi
AK=$(openssl rand -hex 8); SK=$(openssl rand -hex 16)
for ns in data pipeline app; do
  kubectl -n $ns create secret generic s3-credentials \
    --from-literal=AWS_ACCESS_KEY_ID=$AK --from-literal=AWS_SECRET_ACCESS_KEY=$SK
done
cat > /tmp/s3.json <<JSON
{"identities":[{"name":"admin","credentials":[{"accessKey":"$AK","secretKey":"$SK"}],"actions":["Admin","Read","Write","List","Tagging"]}]}
JSON
kubectl -n data create secret generic seaweedfs-s3-config --from-file=s3.json=/tmp/s3.json
rm -f /tmp/s3.json

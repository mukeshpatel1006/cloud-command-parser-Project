#!/usr/bin/env bash
# Fetch model v1/v2 from the GitHub Release and put them in object storage (fresh-clone path of `make up`).
# usage: scripts/seed_models.sh <github-user/repo> <release-tag>
set -euo pipefail
REPO=$1; TAG=$2
mkdir -p release
for v in v1 v2; do
  for f in model-$v.tar.gz model-$v.sha256; do
    [ -f release/$f ] || curl -fsSL -o release/$f "https://github.com/$REPO/releases/download/$TAG/$f"
  done
  ( cd release && sha256sum -c model-$v.sha256 )
  rm -rf models_local/$v && mkdir -p models_local/$v && tar -xzf release/model-$v.tar.gz -C models_local/$v
done
. scripts/s3env.sh
for v in v1 v2; do python3 training/upload_model.py models_local/$v $v release/model-$v.sha256; done

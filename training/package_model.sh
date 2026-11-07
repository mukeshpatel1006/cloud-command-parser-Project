#!/usr/bin/env bash
# Package a trained model dir for the GitHub Release: model-<ver>.tar.gz + model-<ver>.sha256
# usage: training/package_model.sh models_local/v1 v1
set -euo pipefail
DIR=$1; VER=$2; OUT=release; mkdir -p "$OUT"
tar --sort=name --mtime='2026-01-01 00:00:00' --owner=0 --group=0 -cf - -C "$DIR" . | gzip -n > "$OUT/model-$VER.tar.gz"
( cd "$OUT" && sha256sum "model-$VER.tar.gz" > "model-$VER.sha256" )
cp "$DIR/VERSION" "$OUT/VERSION-$VER.txt"
cat "$OUT/model-$VER.sha256"

"""Run the TEACHER (same prompt + settings as Task 1) on validation.jsonl -> predictions for score.py.
python training/teacher_validation.py --out results/teacher_predictions.jsonl   (needs Ollama on localhost)"""
import argparse
import json
import os
import sys

import requests

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="data/validation.jsonl")
ap.add_argument("--out", required=True)
ap.add_argument("--prompt", default="prompts/teacher_prompt.txt")
ap.add_argument("--url", default=os.environ.get("OLLAMA_URL", "http://localhost:11434"))
a = ap.parse_args()
tpl = open(a.prompt, encoding="utf-8").read()
json_mode = os.environ.get("TEACHER_JSON_MODE", "1") == "1"
with open(a.input, encoding="utf-8") as f, open(a.out, "w", encoding="utf-8") as o:
    for line in f:
        if not line.strip():
            continue
        r = json.loads(line)
        body = {"model": "phi3.5", "prompt": tpl.replace("{command}", r["text"]), "stream": False,
                "options": {"temperature": 0, "seed": 42}}
        if json_mode:
            body["format"] = "json"
        resp = requests.post(f"{a.url}/api/generate", json=body, timeout=600).json()["response"]
        o.write(json.dumps({"id": r["id"], "prediction": resp}, ensure_ascii=False) + "\n")
        print(r["id"], file=sys.stderr)

"""Teacher-labelling worker.

Env: SHARD_INDEX, SHARD_COUNT, S3_ENDPOINT, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
     OLLAMA_URL (default http://host.k3d.internal:11434), TEACHER_MODEL (default phi3.5),
     TEACHER_JSON_MODE (default 1: asks Ollama for syntactically valid JSON)
Reads  s3://datasets/commands_pool.jsonl
Writes s3://datasets/teacher/shard-<SHARD_INDEX>.jsonl   (re-uploaded every 50 records; resumable)
Each output line: {"id", "text", "teacher_raw"}  - teacher_raw is the exact reply, never edited.
"""
import json
import os
import sys
import time

import requests
import s3util
from sharding import select_shard

PROMPT_FILE = os.environ.get("PROMPT_FILE", "/app/prompts/teacher_prompt.txt")


def ask_teacher(prompt, url, model, json_mode):
    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "seed": 42,
            "repeat_penalty": 1.1,
            "repeat_last_n": 64,
            "num_predict": 128
}
    }

    if json_mode:
        body["format"] = "json"

    for attempt in range(15):
        try:
            r = requests.post(
                f"{url}/api/generate",
                json=body,
                timeout=(30, 600)
            )

            if r.status_code >= 500:
                print(
                    f"Ollama server error {r.status_code}: {r.text[:500]}",
                    file=sys.stderr,
                    flush=True
                )
                raise requests.exceptions.HTTPError(
                    f"HTTP {r.status_code}"
                )

            r.raise_for_status()
            result = r.json()

            if "response" not in result:
                raise ValueError(f"Missing response: {result}")

            return result["response"]

        except Exception as e:
            wait = min(10 * (attempt + 1), 60)

            print(
                f"Teacher error (attempt {attempt + 1}/15): {e}. "
                f"Retrying in {wait} seconds...",
                file=sys.stderr,
                flush=True
            )

            time.sleep(wait)

    raise RuntimeError("Teacher unreachable after 15 attempts")

def main():
    idx = int(os.environ["SHARD_INDEX"])
    cnt = int(os.environ["SHARD_COUNT"])
    url = os.environ.get("OLLAMA_URL", "http://host.k3d.internal:11434")
    model = os.environ.get("TEACHER_MODEL", "phi3.5")
    json_mode = os.environ.get("TEACHER_JSON_MODE", "1") == "1"
    template = open(PROMPT_FILE, encoding="utf-8").read()

    s3 = s3util.client()
    lines = [l for l in s3util.get_text(s3, "datasets", "commands_pool.jsonl").splitlines() if l.strip()]
    mine = [json.loads(l) for l in select_shard(lines, idx, cnt)]
    key = f"teacher/shard-{idx}.jsonl"

    done = {}
    if s3util.exists(s3, "datasets", key):  # resume after a crash
        for l in s3util.get_text(s3, "datasets", key).splitlines():
            if l.strip():
                r = json.loads(l)
                done[r["id"]] = r
    print(f"shard {idx}/{cnt}: {len(mine)} commands, {len(done)} already done", flush=True)

    out = dict(done)
    for n, rec in enumerate(mine, 1):
        if rec["id"] in out:
            continue
        prompt = template.replace("{command}", rec["text"])
        raw = ask_teacher(prompt, url, model, json_mode)
        out[rec["id"]] = {"id": rec["id"], "text": rec["text"], "teacher_raw": raw}
        if n % 50 == 0 or n == len(mine):
            body = "\n".join(json.dumps(out[r["id"]], ensure_ascii=False) for r in mine if r["id"] in out)
            s3util.put_text(s3, "datasets", key, body + "\n")
            print(f"  {len(out)}/{len(mine)} done", flush=True)
    print("finished", flush=True)


if __name__ == "__main__":
    main()

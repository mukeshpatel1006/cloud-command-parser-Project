"""Command-parser inference service. Port 8000.
Env: MODEL_URI (s3://models/v1/), MODEL_VERSION, S3_ENDPOINT, MAX_NEW_TOKENS, FAULT_INJECT.
Credentials: AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY from a Kubernetes Secret."""
import os
import tempfile
import threading

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from validation import validate_output

MODEL_URI = os.environ.get("MODEL_URI", "")
MODEL_VERSION = os.environ.get("MODEL_VERSION", "unknown")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "")
MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", "96"))
REPETITION_PENALTY = 1.01
NO_REPEAT_NGRAM_SIZE = 3
POD = os.environ.get("HOSTNAME", "local")
PROMPT_INSTRUCTIONS = (
    "Output exactly one JSON object with exactly four keys: intent, date, time, place. "
    "Use null for absent slots. Copy date, time, and place exactly from the command; "
    "do not convert digits to words. Place must be the shortest meaningful phrase. No extra text."
)

app = FastAPI()
state = {"model": None, "tok": None, "error": None}
_lock = threading.Lock()


class Req(BaseModel):
    text: str


def download_model(uri, endpoint, dest):
    import boto3
    from botocore.config import Config
    bucket, _, prefix = uri[len("s3://"):].partition("/")
    s3 = boto3.client("s3", endpoint_url=endpoint, region_name="us-east-1",
                      config=Config(s3={"addressing_style": "path"}))
    n = 0
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for o in page.get("Contents", []):
            name = o["Key"][len(prefix):].lstrip("/")
            if not name or name == "model.sha256":
                continue
            s3.download_file(bucket, o["Key"], os.path.join(dest, name))
            n += 1
    print(f"downloaded {n} files from {uri} ({endpoint})", flush=True)


def load_model():
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        dest = tempfile.mkdtemp(prefix="model-")
        download_model(MODEL_URI, S3_ENDPOINT, dest)
        tok = AutoTokenizer.from_pretrained(dest)
        tok.pad_token = tok.eos_token
        model = AutoModelForCausalLM.from_pretrained(dest).eval()
        state.update(tok=tok, model=model)
        print(f"model {MODEL_VERSION} loaded", flush=True)
    except Exception as e:  # noqa: BLE001
        state["error"] = str(e)
        print("model load failed:", e, flush=True)


@app.on_event("startup")
def _startup():
    threading.Thread(target=load_model, daemon=True).start()


def generate(text):
    import torch
    prompt = f"Command: {text.lower()}\nJSON: "
    tok, model = state["tok"], state["model"]
    enc = tok(prompt, return_tensors="pt")
    with _lock, torch.inference_mode():
        out = model.generate(**enc, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                             pad_token_id=tok.eos_token_id,
                             repetition_penalty=REPETITION_PENALTY,
                             no_repeat_ngram_size=NO_REPEAT_NGRAM_SIZE)
    return tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def _headers():
    return {"X-Model-Version": MODEL_VERSION, "X-Served-By": POD}


@app.get("/healthz")
def healthz():
    return JSONResponse({"status": "alive"})


@app.get("/readyz")
def readyz():
    if state["model"] is None:
        return JSONResponse({"status": "loading"}, status_code=503)
    return JSONResponse({"status": "ready"})


@app.post("/parse")
def parse(req: Req):
    if state["model"] is None:
        return JSONResponse(
            {"error": "model_not_ready"},
            status_code=503,
            headers=_headers()
        )

    raw = "not json" if os.environ.get("FAULT_INJECT") == "1" else generate(req.text)

    print("DEBUG INPUT:", req.text, flush=True)
    print("DEBUG RAW MODEL OUTPUT:", repr(raw), flush=True)

    obj = validate_output(raw)

    if obj is None:
        print("DEBUG VALIDATION FAILED", flush=True)
        return JSONResponse(
            {"error": "invalid_model_output"},
            status_code=500,
            headers=_headers()
        )

    return JSONResponse(obj, headers=_headers())
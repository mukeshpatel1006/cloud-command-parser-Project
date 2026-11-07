"""Generate raw predictions for score.py with a local HF model dir (or a hub id such as
EleutherAI/pythia-70m for the untrained baseline).
python training/predict.py --model DIR --input data/validation.jsonl --out results/student_v1_predictions.jsonl"""
import argparse
import json

import torch
from common import build_prompt
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--input", default="data/validation.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-new-tokens", type=int, default=64)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model).eval()
    with open(a.input, encoding="utf-8") as f, open(a.out, "w", encoding="utf-8") as o:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            enc = tok(build_prompt(r["text"]), return_tensors="pt")
            with torch.inference_mode():
                out = model.generate(**enc, max_new_tokens=a.max_new_tokens, do_sample=False,
                                     pad_token_id=tok.eos_token_id)
            text = tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()
            o.write(json.dumps({"id": r["id"], "prediction": text}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()

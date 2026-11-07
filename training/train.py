"""Sequence-level distillation: fine-tune Pythia-70M on the teacher's JSON replies (CPU).
Usage: python training/train.py --config training/config.yaml [--subset 50]"""
import argparse
import csv
import json
import os
import random

import numpy as np
import torch
import yaml
from common import build_prompt
from transformers import AutoModelForCausalLM, AutoTokenizer


def set_seed(s):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)


def compact(raw):
    """Teacher reply -> one-line JSON (same content, whitespace removed)."""
    return json.dumps(json.loads(raw), ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="training/config.yaml")
    ap.add_argument("--subset", type=int, default=0)
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    set_seed(cfg["seed"])
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    rows = [json.loads(l) for l in open(cfg["train_file"], encoding="utf-8") if l.strip()]
    rows = rows[: cfg["max_train_examples"]]
    if a.subset:
        rows = rows[: a.subset]
    print(f"training on {len(rows)} examples")

    tok = AutoTokenizer.from_pretrained(cfg["base_model"])
    tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(cfg["base_model"])
    model.train()

    examples = []
    for r in rows:
        p = tok(build_prompt(r["text"]))["input_ids"]
        t = tok(compact(r["teacher_raw"]))["input_ids"] + [tok.eos_token_id]
        ids = (p + t)[: cfg["max_seq_len"]]
        labels = ([-100] * len(p) + t)[: cfg["max_seq_len"]]   # loss only on the JSON part
        examples.append((ids, labels))

    opt = torch.optim.AdamW(model.parameters(), lr=cfg["learning_rate"])
    g = torch.Generator().manual_seed(cfg["seed"])
    bs = cfg["batch_size"]
    losses = []
    for epoch in range(1, cfg["epochs"] + 1):
        order = torch.randperm(len(examples), generator=g).tolist()
        total, n = 0.0, 0
        for i in range(0, len(order), bs):
            batch = [examples[j] for j in order[i:i + bs]]
            m = max(len(x[0]) for x in batch)
            ids = torch.tensor([x[0] + [tok.pad_token_id] * (m - len(x[0])) for x in batch])
            lab = torch.tensor([x[1] + [-100] * (m - len(x[1])) for x in batch])
            att = torch.tensor([[1] * len(x[0]) + [0] * (m - len(x[0])) for x in batch])
            loss = model(input_ids=ids, attention_mask=att, labels=lab).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            opt.zero_grad()
            total += loss.item() * len(batch)
            n += len(batch)
        losses.append((epoch, total / n))
        print(f"epoch {epoch}: loss {total / n:.4f}", flush=True)

    os.makedirs(os.path.dirname(cfg["loss_csv"]) or ".", exist_ok=True)
    with open(cfg["loss_csv"], "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["epoch", "loss"])
        w.writerows(losses)
    out = cfg["output_dir"] + ("_subset" if a.subset else "")
    os.makedirs(out, exist_ok=True)
    model.save_pretrained(out)
    tok.save_pretrained(out)
    with open(os.path.join(out, "VERSION"), "w") as f:
        f.write(f"{cfg['version']}\nbase={cfg['base_model']}\nseed={cfg['seed']}\n"
                f"epochs={cfg['epochs']}\ntorch={torch.__version__}\n")
    print("saved to", out)


if __name__ == "__main__":
    main()

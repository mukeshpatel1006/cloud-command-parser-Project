"""Clean the teacher shard outputs.

  python worker/clean.py --shards DIR_OR_FILES... --out-dir OUT [--schema data/schema.json]

Reads every *.jsonl in the shard directory, drops bad records and writes
  OUT/train.jsonl    {"id","text","teacher_raw"} in id order
  OUT/train.sha256   SHA-256 of train.jsonl (sha256sum format)
  OUT/clean_counts.json
Each rejected record is counted once, in the FIRST rule it breaks (a) > (b) > (c) > (d);
duplicate commands are then removed among the surviving records (smallest id kept).
"""
import argparse
import glob
import hashlib
import json
import os

KEYS = {"intent", "date", "time", "place"}


def check(rec, intents):
    """Return None if OK, else 'a' / 'b' / 'c' / 'd'."""
    try:
        obj = json.loads(rec["teacher_raw"])
    except (ValueError, TypeError):
        return "a"
    if not isinstance(obj, dict):
        return "a"
    if set(obj.keys()) != KEYS:
        return "b"
    if obj["intent"] not in intents:
        return "c"
    text = rec["text"]
    for k in ("date", "time", "place"):
        v = obj[k]
        if v is None:
            continue
        if not isinstance(v, str) or v.strip() == "" or v not in text:
            return "d"
    return None


def id_key(i):
    return (len(i), i)  # C0001 < C0010 < C0100 ; fixed width ids sort the same either way


def clean(records, intents):
    counts = {"input": len(records), "a_invalid_json": 0, "b_bad_keys": 0,
              "c_bad_intent": 0, "d_bad_slot": 0, "duplicates": 0, "kept": 0}
    name = {"a": "a_invalid_json", "b": "b_bad_keys", "c": "c_bad_intent", "d": "d_bad_slot"}
    good = []
    for r in records:
        bad = check(r, intents)
        if bad:
            counts[name[bad]] += 1
        else:
            good.append(r)
    good.sort(key=lambda r: id_key(r["id"]))
    seen, kept = set(), []
    for r in good:
        if r["text"] in seen:
            counts["duplicates"] += 1
            continue
        seen.add(r["text"])
        kept.append(r)
    counts["kept"] = len(kept)
    return kept, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", nargs="+", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--schema", default="data/schema.json")
    a = ap.parse_args()

    files = []
    for p in a.shards:
        files += sorted(glob.glob(os.path.join(p, "*.jsonl"))) if os.path.isdir(p) else [p]
    records = []
    for f in sorted(files):
        with open(f, encoding="utf-8") as fh:
            records += [json.loads(l) for l in fh if l.strip()]
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids)), "an id appears in more than one shard output"

    intents = set(json.load(open(a.schema, encoding="utf-8"))["intents"])
    kept, counts = clean(records, intents)

    os.makedirs(a.out_dir, exist_ok=True)
    body = "".join(json.dumps({"id": r["id"], "text": r["text"], "teacher_raw": r["teacher_raw"]},
                              ensure_ascii=False) + "\n" for r in kept)
    data = body.encode("utf-8")
    with open(os.path.join(a.out_dir, "train.jsonl"), "wb") as f:
        f.write(data)
    digest = hashlib.sha256(data).hexdigest()
    with open(os.path.join(a.out_dir, "train.sha256"), "w") as f:
        f.write(f"{digest}  train.jsonl\n")
    with open(os.path.join(a.out_dir, "clean_counts.json"), "w") as f:
        json.dump(counts, f, indent=2)
    print(json.dumps(counts, indent=2))
    assert counts["input"] == sum(counts[k] for k in counts if k not in ("input", "kept")) + counts["kept"]


if __name__ == "__main__":
    main()

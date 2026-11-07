# Order of work (do this in order; ~25 h left at start)
1. `git init`, create GitHub repo, push this folder. Edit placeholders (`<YOUR ...>`, Makefile GITHUB_REPO, ci.yml RELEASE_TAG).
2. `ollama pull phi3.5`; run `OLLAMA_HOST=0.0.0.0 ollama serve`. Test the prompt on 5 commands first.
3. `make cluster storage images` (k3d, SeaweedFS, buckets, images).            -> screenshot/log to results/
4. `kubectl apply -f k8s/pipeline/worker-job.yaml`  (START EARLY - hours on CPU).  Meanwhile do steps 7-9.
5. `scripts/fetch_dataset.sh` -> data/v1/train.jsonl + train.sha256 (commit data/shards, data/v1, results/clean_counts.*).
6. `make train SUBSET=50` (smoke test) then `make train`; `make train CONFIG=training/config_v2.yaml`.
   Package both (`training/package_model.sh`), upload models to S3 (`training/upload_model.py`) and to a GitHub Release.
7. (parallel, no model needed) Task 5 is done: `make nacl`; Task 6: push to GitHub and watch CI.
8. Scores: `python training/predict.py --model models_local/v1 --out results/student_predictions.jsonl`,
   `--model EleutherAI/pythia-70m` for the base, `training/teacher_validation.py` for the teacher; run tools/score.py each
   (save results/*_score.json, results/teacher_validation.json).
9. Task 3/4 experiments with scripts/*.sh (see README). Task 7: standard Locust, `kubectl top`, `scripts/cost.py`.
10. CI: deliberately failing run (workflow_dispatch -> model_source=base); copy the run link into the report.
11. Fill report/report.md -> `report/build.sh`. Handwrite notes (notes/ draft) -> scan -> <roll>.pdf.
12. `git tag final && git push --tags`; zip: see scripts/package_submission.sh <roll_number>.

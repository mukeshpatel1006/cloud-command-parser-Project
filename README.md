# Cloud Computing Mini Project — Distilled command parser on a local Kubernetes cloud

Name:< Mukesh Kumar Verma > Roll number:<230101006>
GitHub repository: https://github.com/mukeshpatel1006/cloud-command-parser-Project/(final commit tagged `final`)
GitHub Release (model, tokenizer, version, checksums): https://github.com/mukeshpatel1006/cloud-command-parser-Project/ /releases/tag/model-release**

Teacher: phi3.5 via Ollama (temperature 0, seed 42) -> sequence-level distillation -> student EleutherAI/pythia-70m -> FastAPI service
on k3d (Traefik ingress, HPA) with SeaweedFS object storage.

## Layout
| path | purpose |
|---|---|
| `cluster/k3d.yaml` | k3d cluster (host port 8080 -> ingress) |
| `k8s/data` `k8s/pipeline` `k8s/app` | SeaweedFS, labelling Job, parser Deployment/Service/Ingress/HPA |
| `prompts/teacher_prompt.txt` | teacher prompt |
| `worker/` | sharded teacher worker, `clean.py`, Dockerfile |
| `training/` | `config.yaml` (+`config_v2.yaml`), `train.py`, `predict.py`, packaging/upload |
| `service/` | FastAPI service + Dockerfile (no weights in image) |
| `network/` | `subnets.md`, `nacl.json` |
| `tests/`, `.github/workflows/ci.yml` | unit tests, CI/CD |
| `results/` | all logs, score reports, Locust output |
| `AI_USE.md`, `report/report.pdf` | AI-use statement, report |

## Prerequisites
Docker, k3d, kubectl, Python 3.11+, make, Ollama (with `ollama pull phi3.5`), `pip install -r requirements-dev.txt`.

## Build and deploy (fresh clone)
```bash
git clone https://github.com/<YOUR_USER>/<YOUR_REPO> && cd <YOUR_REPO>
make up GITHUB_REPO=<YOUR_USER>/<YOUR_REPO>      # cluster, SeaweedFS, images, models from the Release, app (1 command)
curl -X POST localhost:8080/parse -H 'content-type: application/json' -d '{"text":"what is the weather in london"}'
```

## Pipeline (how the artefacts were produced)
```bash
# Task 1 - labelling (Ollama must listen on 0.0.0.0:  OLLAMA_HOST=0.0.0.0 ollama serve)
kubectl apply -f k8s/pipeline/worker-job.yaml            # two workers, SHARD_INDEX 0 and 1
kubectl -n pipeline logs -f -l job-name=teacher-labelling --prefix
scripts/fetch_dataset.sh                                  # download shards, worker/clean.py, upload datasets/v1/
# Task 2 - training
make train                                                # reads training/config.yaml; make train SUBSET=50 = smoke test
make train CONFIG=training/config_v2.yaml                 # version v2
training/package_model.sh models_local/v1 v1              # -> release/model-v1.tar.gz + .sha256   (same for v2)
```
Upload `release/*` as assets of the GitHub Release (never `git add` model files).

## Test
```bash
make test        # unit tests          make lint     # ruff
make nacl        # NACL simulator      python tools/score.py <preds> data/validation.jsonl --min-validity 95
locust -f tools/locustfile.py --headless --users 4 --spawn-rate 4 --run-time 2m --host http://localhost:8080 --csv results/loadtest
```
Experiments (each writes into `results/`): `scripts/mem_test.sh`, `exp_hpa.sh`, `exp_rolling_update.sh`, `exp_recovery.sh`,
`exp_coldstart.sh`, `exp_loadbalance.sh`, `exp_resources.sh`, `python scripts/cost.py ...`.

## Shut down
```bash
make down        # deletes the k3d cluster (and all data in it)
```

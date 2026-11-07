# Usage: see README.md.  `make up` = whole system from a fresh clone; `make down` = delete the cluster.
# edit GITHUB_REPO below
GITHUB_REPO ?= YOUR_USER/YOUR_REPO
RELEASE_TAG ?= final
CONFIG ?= training/config.yaml
SUBSET ?= 0

.PHONY: up down cluster storage images deploy train test lint nacl

up: cluster storage images
	scripts/seed_models.sh $(GITHUB_REPO) $(RELEASE_TAG)
	kubectl apply -f k8s/app/app.yaml
	kubectl -n app rollout status deploy/parser --timeout=300s
	@echo "Service ready: curl -X POST localhost:8080/parse -H 'content-type: application/json' -d '{\"text\":\"what is the weather in london\"}'"

cluster:
	k3d cluster create --config cluster/k3d.yaml || true
	scripts/create_secrets.sh

storage:
	kubectl apply -f k8s/data/seaweedfs.yaml
	kubectl -n data rollout status statefulset/seaweedfs --timeout=300s
	bash -c '. scripts/s3env.sh && python3 scripts/bootstrap_storage.py'

images:
	docker build -t cc-parser:3 -f service/Dockerfile .
	docker build -t cc-worker:1 -f worker/Dockerfile .
	k3d image import cc-parser:3 cc-worker:1 -c cc

down:
	k3d cluster delete cc

train:
	python3 training/train.py --config $(CONFIG) $(if $(filter-out 0,$(SUBSET)),--subset $(SUBSET),)

test:
	python3 -m pytest -q tests

lint:
	ruff check .

nacl:
	python3 tools/nacl_sim.py network/nacl.json network/packets_sample.jsonl --check



GITHUB_REPO ?= mukeshpatel1006/cloud-command-parser-Project
RELEASE_TAG ?= final
CONFIG ?= training/config.yaml
SUBSET ?= 0

.PHONY: up down cluster storage images models deploy train test lint nacl

up: cluster storage images models deploy

cluster:
	k3d cluster create --config cluster/k3d.yaml || true
	bash scripts/create_secrets.sh

storage:
	kubectl apply -f k8s/data/seaweedfs.yaml
	kubectl -n data rollout status statefulset/seaweedfs --timeout=300s
	bash -c '. scripts/s3env.sh && python3 scripts/bootstrap_storage.py'

images:
	docker build -t cc-parser:3 -f service/Dockerfile .
	docker build -t cc-worker:1 -f worker/Dockerfile .
	k3d image import cc-parser:3 cc-worker:1 -c cc

models:
	bash scripts/seed_models.sh $(GITHUB_REPO) $(RELEASE_TAG)

deploy:
	kubectl apply -f k8s/app/app.yaml
	kubectl -n app rollout status deploy/parser --timeout=300s
	@echo "Service ready: http://localhost:8080"
	@echo "Test command:"
	@echo "curl -X POST http://localhost:8080/parse -H 'Content-Type: application/json' -d '{\"text\":\"what is the weather in london\"}'"

train:
	python3 training/train.py --config $(CONFIG) $(if $(filter-out 0,$(SUBSET)),--subset $(SUBSET),)

test:
	python3 -m pytest -q tests

lint:
	ruff check .

nacl:
	python3 tools/nacl_sim.py network/nacl.json network/packets_sample.jsonl --check

down:
	k3d cluster delete cc

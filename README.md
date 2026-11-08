# Cloud Computing Mini Project
## Knowledge Distillation and Deployment of a Lightweight Command-Parsing Language Model on a Local Kubernetes Cloud

**Student Name:** Mukesh Kumar Verma  
**Roll Number:** 230101006  
**Department:** Computer Science and Engineering  
**Institute:** Indian Institute of Information Technology, Manipur  
**Course:** CS3081 – Cloud Computing

**Repository:** https://github.com/mukeshpatel1006/cloud-command-parser-Project

---

## 1. Project Overview

This project implements an end-to-end cloud-native Natural Language Command Parsing System using Knowledge Distillation, Object Storage, Containerization, Kubernetes, and automated testing.

The primary objective is to develop a lightweight language model capable of converting natural-language commands into structured JSON objects containing an intent and relevant slots.

A larger teacher language model, Phi-3.5-mini-instruct, is used to generate labelled training examples. These examples are cleaned and used to train a smaller student model based on EleutherAI/Pythia-70M.

The trained student model is integrated with a FastAPI inference service and deployed in a local Kubernetes environment using k3d. SeaweedFS provides S3-compatible object storage for datasets and model artefacts.

The project demonstrates the complete machine learning lifecycle, from data generation and model training to containerized inference, Kubernetes deployment, network security, testing, and performance evaluation.

## 2. Project Objectives

- Implement S3-compatible object storage using SeaweedFS.
- Generate labelled command datasets using a teacher language model.
- Perform parallel teacher labelling using multiple workers.
- Apply data cleaning and schema validation.
- Train a lightweight student model using sequence-level distillation.
- Develop a REST-based inference service using FastAPI.
- Containerize the inference service using Docker.
- Deploy and manage the application using Kubernetes.
- Configure ingress, replicas, resource limits, health checks, and autoscaling.
- Design subnetting and stateless Network Access Control List rules.
- Implement automated testing, linting, secret scanning, and CI/CD.
- Evaluate model accuracy, reliability, resource consumption, and deployment performance.

## 3. System Architecture

The system follows a multi-stage architecture in which data generation, model training, model packaging, deployment, and inference are connected through a cloud-native workflow.

### 3.1 End-to-End Architecture

```text
              USER COMMAND
                    |
                    v
           NATURAL LANGUAGE INPUT
                    |
                    v
             DATASET GENERATION
                    |
                    v
             SEAWEEDFS STORAGE
                    |
                    v
          PARALLEL TEACHER LABELLING
                 /       \
                v         v
           WORKER 0    WORKER 1
                \         /
                 v       v
              DATA CLEANING
                    |
                    v
            CLEANED DATASET
                    |
                    v
             STUDENT TRAINING
              PYTHIA-70M
                    |
                    v
             MODEL EVALUATION
                    |
                    v
            MODEL PACKAGING
                    |
                    v
             SEAWEEDFS STORAGE
                    |
                    v
             FASTAPI SERVICE
                    |
                    v
              DOCKER IMAGE
                    |
                    v
             KUBERNETES
                    |
             TRAEFIK INGRESS
                    |
                    v
             USER REQUEST
                    |
                    v
             MODEL INFERENCE
                    |
                    v
             JSON VALIDATION
                    |
                    v
           STRUCTURED JSON OUTPUT
```

### 3.2 Architecture Components

| Component | Technology | Responsibility |
|---|---|---|
| Teacher model | Phi-3.5-mini-instruct | Generate labelled command examples |
| Teacher runtime | Ollama | Run the teacher model locally |
| Parallel processing | Kubernetes Jobs | Execute independent labelling workers |
| Object storage | SeaweedFS | Store datasets and model artefacts |
| Data processing | Python | Clean and validate generated data |
| Student model | EleutherAI/Pythia-70M | Perform lightweight command parsing |
| Model framework | PyTorch, Transformers | Train and execute the student model |
| API framework | FastAPI | Expose the inference endpoint |
| Containerization | Docker | Package the inference application |
| Orchestration | k3d, Kubernetes | Deploy and manage application containers |
| Ingress | Traefik | Route incoming HTTP requests |
| Autoscaling | Kubernetes HPA | Manage application replica scaling |
| Testing | Pytest, Ruff | Verify functionality and code quality |
| CI/CD | GitHub Actions | Automate testing and quality checks |

## 4. Command Parsing Specification

The application converts one natural-language command into one JSON object containing exactly four keys:

- `intent`
- `date`
- `time`
- `place`

### Supported Intents

| Intent | Description |
|---|---|
| `alarm_set` | Set an alarm |
| `alarm_query` | Query an alarm |
| `calendar_set` | Create a calendar event |
| `calendar_query` | Query calendar events |
| `calendar_remove` | Remove a calendar event |
| `weather_query` | Request weather information |
| `datetime_query` | Request date or time information |
| `recommendation_events` | Request event recommendations |

### Input and Output Example 1: Weather Query

**Input:**

```text
what is the weather in london
```

**Expected JSON Output:**

```json
{
  "intent": "weather_query",
  "date": null,
  "time": null,
  "place": "london"
}
```

### Input and Output Example 2: Alarm Setting

**Input:**

```text
set an alarm for seven thirty am tomorrow
```

**Expected JSON Output:**

```json
{
  "intent": "alarm_set",
  "date": "tomorrow",
  "time": "seven thirty am",
  "place": null
}
```

### Output Validation Rules

1. Every output must be a valid JSON object.
2. Exactly four keys must be present.
3. The intent must belong to the supported intent list.
4. Date, time, and place must contain strings or null values.
5. Slot values must be copied from the original command.
6. Missing slots must be represented using null.
7. Additional keys and explanatory text are not allowed.

## 5. Task 1: Object Storage and Parallel Teacher Labelling

### Objective

Generate a labelled command dataset using a teacher language model and store the resulting artefacts in S3-compatible object storage.

### Implementation

SeaweedFS is deployed in the local Kubernetes cluster and configured to provide S3-compatible object storage.

The initial command dataset contains 3,000 natural-language commands. Two independent teacher workers process separate dataset shards.

The teacher model used is Phi-3.5-mini-instruct through Ollama with deterministic generation settings.

**Teacher configuration:**

| Parameter | Configuration |
|---|---|
| Teacher model | Phi-3.5-mini-instruct |
| Runtime | Ollama |
| Temperature | 0 |
| Seed | 42 |
| Workers | 2 |
| Initial commands | 3,000 |

### Data Cleaning

The generated teacher outputs are processed through a cleaning and validation script.

| Data processing result | Count |
|---|---:|
| Initial records | 3,000 |
| Invalid JSON | 2 |
| Invalid keys | 14 |
| Invalid intent | 7 |
| Invalid slot values | 165 |
| Duplicate records | 47 |
| Final cleaned records | 2,765 |

The cleaned dataset is stored in SeaweedFS for subsequent student model training.

## 6. Task 2: Student Model Training and Sequence-Level Distillation

### Objective

Train a lightweight student language model using labelled examples generated by the teacher model.

### Teacher–Student Architecture

```text
       NATURAL LANGUAGE COMMAND
                  |
                  v
        TEACHER LANGUAGE MODEL
          PHI-3.5-MINI-INSTRUCT
                  |
                  v
          LABELLED EXAMPLES
                  |
                  v
           DATA CLEANING
                  |
                  v
          TRAINING DATASET
                  |
                  v
          STUDENT LANGUAGE MODEL
             PYTHIA-70M
                  |
                  v
          TRAINED STUDENT MODEL
```

### Student Model Configuration

| Parameter | Configuration |
|---|---|
| Student model | EleutherAI/Pythia-70M |
| Framework | PyTorch |
| Model library | Hugging Face Transformers |
| Optimizer | AdamW |
| Learning rate | 0.00001 |
| Batch size | 2 |
| Epochs | 10 |
| Gradient clipping | 0.5 |
| Training precision | FP32 |

The student model learns to generate structured JSON outputs from natural-language commands.

### Training Loss

The training loss decreased over the ten epochs:

| Epoch | Training Loss |
|---|---:|
| 1 | 0.1946 |
| 2 | 0.0923 |
| 3 | 0.0640 |
| 4 | 0.0456 |
| 5 | 0.0364 |
| 6 | 0.0287 |
| 7 | 0.0258 |
| 8 | 0.0188 |
| 9 | 0.0166 |
| 10 | 0.0110 |

### Model Evaluation

| Evaluation Metric | Teacher | Student |
|---|---:|---:|
| JSON validity | 100% | 100% |
| Intent accuracy | 80% | 78% |
| Date accuracy | 79% | 81% |
| Time accuracy | 87% | 89% |
| Place accuracy | 87% | 82% |
| Full-frame accuracy | 49% | 48% |

The evaluation results show that the smaller student model achieves performance close to the teacher on several individual slot metrics.

## 7. Task 3: Containerised Inference Service

### Objective

Develop a REST API that accepts natural-language commands and returns validated structured JSON responses.

### FastAPI Implementation

The inference service is developed using FastAPI and provides the following endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/parse` | POST | Parse a natural-language command |
| `/healthz` | GET | Check application health |
| `/readyz` | GET | Check model readiness |

### Inference Workflow

```text
         USER REQUEST
               |
               v
          FASTAPI API
               |
               v
        REQUEST VALIDATION
               |
               v
         STUDENT MODEL
               |
               v
         TEXT GENERATION
               |
               v
          JSON PARSING
               |
               v
         SCHEMA VALIDATION
               |
          /         \
         v           v
      VALID        INVALID
         |           |
         v           v
    JSON OUTPUT   ERROR RESPONSE
```

### API Request Example

```http
POST /parse
Content-Type: application/json
```

Request body:

```json
{
  "text": "what is the weather in london"
}
```

Successful response:

```json
{
  "intent": "weather_query",
  "date": null,
  "time": null,
  "place": "london"
}
```

The service also includes health checking, readiness checking, model version headers, and invalid-output handling.

The Docker image contains the application and its inference dependencies rather than embedding the model weights.

## 8. Task 4: Kubernetes Deployment, Scaling and Reliability

### Objective

Deploy the containerized inference service using Kubernetes and evaluate its operational reliability.

### Deployment Architecture

```text
             USER REQUEST
                   |
                   v
             TRAEFIK INGRESS
                   |
                   v
             KUBERNETES SERVICE
                   |
              /         \
             v           v
         POD 1          POD 2
             |           |
             v           v
          FASTAPI     FASTAPI
             \           /
              \         /
               v       v
             STUDENT MODEL
```

### Kubernetes Components

| Component | Purpose |
|---|---|
| k3d cluster | Local Kubernetes environment |
| Deployment | Manage parser application pods |
| Service | Provide internal application networking |
| Ingress | Route external requests through Traefik |
| HPA | Configure horizontal pod autoscaling |
| ConfigMap | Store application configuration |
| Secret | Store sensitive credentials |
| Readiness probe | Verify model and application readiness |
| Liveness probe | Check application health |

### Resource Configuration

| Resource | Request | Limit |
|---|---:|---:|
| CPU | 250m | 1 CPU |
| Memory | 512Mi | 1Gi |

The application uses Kubernetes health probes and controlled resource allocation to support reliable inference.

Deployment restart, pod readiness, and rollback procedures are included in the project workflow.

## 9. Task 5: Subnetting and Network Access Control Lists

### Objective

Design a subnet allocation scheme and implement stateless network access control rules.

### Subnet Configuration

| Subnet | Network | Usable Host Range | Hosts |
|---|---|---|---:|
| Application | 10.20.0.0/22 | 10.20.0.1 – 10.20.3.254 | 1022 |
| Public | 10.20.4.0/24 | 10.20.4.1 – 10.20.4.254 | 254 |
| Data | 10.20.5.0/25 | 10.20.5.1 – 10.20.5.126 | 126 |
| Management | 10.20.5.128/27 | 10.20.5.129 – 10.20.5.158 | 30 |

### Network ACL Design

The Network ACL configuration includes:

- Deny rules for the specified abusive IP range.
- HTTP and HTTPS inbound access.
- Restricted SSH access from the management subnet.
- Application subnet ephemeral reply traffic.
- Outbound application communication on TCP port 8000.
- Client reply traffic using the configured ephemeral port range.

The rules are evaluated in numerical order. Since Network ACLs are stateless, inbound and outbound traffic must be explicitly configured.

### Packet Simulation

The NACL simulator was executed against six sample packet scenarios.

**Observed result: 6/6 test cases passed.**

The project includes the NACL configuration and packet simulation script.

## 10. Task 6: Reproducibility, Testing and CI/CD

### Objective

Establish a reproducible development and deployment workflow with automated quality checks.

### Testing Tools

| Tool | Purpose |
|---|---|
| Pytest | Unit and application testing |
| Ruff | Python linting |
| Gitleaks | Secret scanning |
| GitHub Actions | Continuous integration |

### Test Execution

Run unit tests:

```bash
python -m pytest tests/ -v
```

Observed result:

```text
8 passed
```

Run linting:

```bash
ruff check .
```

Run secret scanning:

```bash
gitleaks dir . --config .gitleaks.toml --redact
```

Run the NACL simulator:

```bash
python tools/nacl_sim.py
```

### CI/CD Pipeline

```text
          GITHUB PUSH
                |
                v
          GITHUB ACTIONS
                |
       +--------+--------+
       |        |        |
       v        v        v
   SECRET     LINT    UNIT TESTS
   SCAN
       |        |        |
       +--------+--------+
                |
                v
           EVALUATION
                |
                v
         PIPELINE RESULT
```

The GitHub Actions workflow executes secret scanning, linting, unit tests, and model evaluation.

Model weights and sensitive credentials are excluded from the Git repository. Model artefacts are distributed through GitHub Releases.

## 11. Task 7: Performance, Cost and Review

### Objective

Evaluate the performance, resource consumption, reliability, and operational cost of the deployed command-parsing service.

### Evaluation Areas

| Area | Evaluation |
|---|---|
| Model performance | Intent, slot, and JSON validity |
| API performance | Request processing latency |
| Resource utilisation | CPU and memory usage |
| Reliability | Health, readiness, restart, and recovery |
| Scaling | HPA behaviour under load |
| Load balancing | Request distribution across replicas |
| Deployment | Rollout and rollback behaviour |
| Cost | Estimated compute and storage consumption |

### Performance Testing Tools

Locust is used for load testing the API.

```bash
locust -f tools/locustfile.py --headless --users 4 --spawn-rate 4 --run-time 2m --host http://localhost:8080 --csv results/loadtest
```

Additional experiment scripts are available for memory testing, autoscaling, rolling updates, recovery, cold starts, load balancing, and resource measurements.

Performance values should be taken from the generated experiment logs and reports.

## 12. Repository Structure

```text
cloud-command-parser-Project/
│
├── cluster/
│   └── k3d.yaml
│
├── config/
│   ├── s3.example.json
│   └── schema.json
│
├── data/
├── datasets/
│
├── k8s/
│   ├── data/
│   ├── pipeline/
│   └── app/
│
├── prompts/
│   └── teacher_prompt.txt
│
├── worker/
│   ├── Dockerfile
│   ├── clean.py
│   └── worker.py
│
├── training/
│   ├── config.yaml
│   ├── config_v2.yaml
│   ├── train.py
│   └── predict.py
│
├── service/
│   ├── app.py
│   ├── validation.py
│   ├── schema.json
│   └── Dockerfile
│
├── network/
│   ├── subnets.md
│   └── nacl.json
│
├── tests/
├── tools/
├── scripts/
├── results/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── AI_USE.md
├── README.md
├── RUNBOOK.md
└── Makefile
```

## 13. Installation and Deployment

### Prerequisites

Install the following tools before running the project:

- Python 3.11 or later
- Docker
- k3d
- kubectl
- Make
- Ollama

Install the required Python dependencies:

```bash
pip install -r requirements-dev.txt
```

Download the teacher model:

```bash
ollama pull phi3.5
```

### Clone the Repository

```bash
git clone https://github.com/mukeshpatel1006/cloud-command-parser-Project.git
cd cloud-command-parser-Project
```

### Start the Local Cloud Environment

```bash
make up
```

The Makefile coordinates the configured cluster, storage, images, model artefacts, and application deployment.

Check the Kubernetes resources:

```bash
kubectl get nodes
kubectl get pods -A
kubectl get services -A
```

### Send an Inference Request

```bash
curl -X POST http://localhost:8080/parse \
-H "Content-Type: application/json" \
-d '{"text":"what is the weather in london"}'
```

### Expected Response

```json
{
  "intent": "weather_query",
  "date": null,
  "time": null,
  "place": "london"
}
```

## 14. Reproducing the Machine Learning Pipeline

### Task 1: Teacher Labelling

Start Ollama:

```bash
OLLAMA_HOST=0.0.0.0 ollama serve
```

Deploy the teacher labelling workers:

```bash
kubectl apply -f k8s/pipeline/worker-job.yaml
```

Check worker logs:

```bash
kubectl -n pipeline logs -f -l job-name=teacher-labelling --prefix
```

Fetch and clean the generated dataset:

```bash
scripts/fetch_dataset.sh
```

### Task 2: Student Training

Train the student model using the configured training settings:

```bash
make train
```

Run a small smoke test:

```bash
make train SUBSET=50
```

Train using the second configuration:

```bash
make train CONFIG=training/config_v2.yaml
```

### Model Packaging

Package the trained model and generate its checksum:

```bash
training/package_model.sh models_local/v1 v1
```

The generated archive and checksum are stored in the `release/` directory.

Upload model archives and checksum files as GitHub Release assets rather than committing model weights to Git.

## 15. Verification and Testing Commands

Run unit tests:

```bash
make test
```

Run lint checks:

```bash
make lint
```

Run the NACL simulator:

```bash
make nacl
```

Evaluate model predictions:

```bash
python tools/score.py <predictions-file> data/validation.jsonl --min-validity 95
```

Run load testing:

```bash
locust -f tools/locustfile.py --headless --users 4 --spawn-rate 4 --run-time 2m --host http://localhost:8080 --csv results/loadtest
```

Additional experiments:

```bash
scripts/mem_test.sh
bash scripts/exp_hpa.sh
bash scripts/exp_rolling_update.sh
bash scripts/exp_recovery.sh
bash scripts/exp_coldstart.sh
bash scripts/exp_loadbalance.sh
bash scripts/exp_resources.sh
python scripts/cost.py
```

Experiment results are stored in the `results/` directory.

## 16. Model Release and Versioning

The project uses GitHub Releases to distribute trained model artefacts independently of the source code repository.

Each model release should contain:

- Model archive.
- Tokenizer files.
- Model configuration.
- Model version information.
- SHA-256 checksum.

**Release page:**

https://github.com/mukeshpatel1006/cloud-command-parser-Project/releases/tag/final

Verify the downloaded archive using its SHA-256 checksum before deployment.

## 17. Challenges and Limitations

The project involves several practical engineering challenges:

- Teacher-generated data may contain invalid JSON and incorrect slot values.
- Smaller language models may generate malformed JSON.
- Model loading and storage configuration require correct environment variables.
- Kubernetes resource allocation must be balanced against available hardware.
- Stateless network ACLs require explicit reply traffic rules.
- Autoscaling and load balancing need controlled experiments for reliable evaluation.
- Local k3d deployments cannot fully reproduce the behaviour of a production multi-node cloud environment.

The project results should be interpreted within the constraints of the actual experimental environment. Any incomplete experiment or deviation from the assignment configuration should be documented transparently.

## 18. Future Improvements

- Improve JSON generation reliability using structured decoding.
- Increase student model accuracy through additional training experiments.
- Optimize inference latency and memory usage.
- Complete and validate HPA scaling experiments.
- Evaluate deployment on a multi-node Kubernetes cluster.
- Add enhanced monitoring and application metrics.
- Improve model versioning and automated release management.
- Expand the command dataset with additional natural-language variations.

## 19. Conclusion

This project demonstrates the design and implementation of a cloud-native lightweight natural-language command-parsing system using knowledge distillation and Kubernetes.

The teacher model generates labelled command examples, which are cleaned and used to train a smaller student model. The trained model is integrated into a FastAPI inference service, containerized using Docker, and deployed in a local Kubernetes environment.

SeaweedFS provides object storage, Kubernetes manages the application lifecycle, and network ACL rules provide stateless traffic filtering. Automated testing and GitHub Actions support reproducibility and software quality.

The project brings together machine learning, cloud infrastructure, containerization, orchestration, networking, and CI/CD into a single end-to-end implementation.

## 20. References

1. Hugging Face Transformers Documentation — https://huggingface.co/docs/transformers
2. PyTorch Documentation — https://pytorch.org/docs/stable/
3. FastAPI Documentation — https://fastapi.tiangolo.com/
4. Kubernetes Documentation — https://kubernetes.io/docs/
5. k3d Documentation — https://k3d.io/
6. SeaweedFS Documentation — https://github.com/seaweedfs/seaweedfs
7. Ollama Documentation — https://ollama.com/
8. Docker Documentation — https://docs.docker.com/
9. GitHub Actions Documentation — https://docs.github.com/en/actions

---

**Author:** Mukesh Kumar Verma  
**Roll Number:** 230101006  
**Project:** Cloud Computing Mini Project – CS3081  
**Institute:** IIIT Manipur

<<<<<<< HEAD
**Repository:** https://github.com/mukeshpatel1006/cloud-command-parser-Project
=======
**Repository:** https://github.com/mukeshpatel1006/cloud-command-parser-Project
>>>>>>> 2c63500 (Update project pipeline and documentation)

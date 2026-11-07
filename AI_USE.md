# AI use statement

**Tool:** Claude (Anthropic) via the Claude app / Claude Code.
**Used for:** scaffolding the repository (Makefile, Kubernetes manifests, Dockerfiles, service/worker/training code, CI workflow),
drafting the teacher prompt, computing the subnet table, and drafting report/notes outlines.
**How I checked it:** <EDIT - write what you actually did, e.g.>
- read and understood every file before committing; ran `pytest`, `ruff`, `nacl_sim.py --check` (6/6) and `clean.py` myself;
- ran the real pipeline (Ollama, k3d, training, Locust) on my own laptop; every number in the report comes from files in `results/`;
- verified the subnet arithmetic by hand (2^(32-p)-2);
- teacher outputs were stored unedited; validation.jsonl was never used for training.
**Things the AI got wrong / I had to fix:** <EDIT - list real issues you hit>

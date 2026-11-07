#!/usr/bin/env bash
# Task 4.7: delete all pods 3 times; time from Pod creation to Ready; keep the model-download log lines.
set -euo pipefail
mkdir -p results; : > results/coldstart.log
for run in 1 2 3; do
  kubectl -n app delete pods -l app=parser --wait=true >/dev/null
  kubectl -n app wait --for=condition=Ready pod -l app=parser --timeout=300s >/dev/null
  kubectl -n app get pods -l app=parser -o json | python3 -c "
import json,sys,datetime as d
p=lambda s:d.datetime.strptime(s,'%Y-%m-%dT%H:%M:%SZ')
for it in json.load(sys.stdin)['items']:
    c=p(it['metadata']['creationTimestamp'])
    r=[x for x in it['status']['conditions'] if x['type']=='Ready'][0]['lastTransitionTime']
    print('run $run', it['metadata']['name'], (p(r)-c).total_seconds(), 's')" | tee -a results/coldstart.log
  for pod in $(kubectl -n app get pods -l app=parser -o name); do kubectl -n app logs $pod | grep -E 'downloaded|loaded' | sed "s|^|$pod: |" >> results/coldstart.log; done
done
echo "(median per run = median of the Pod times above; compute over the 3 runs for your report)"

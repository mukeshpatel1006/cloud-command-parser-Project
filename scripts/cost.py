"""Task 7 cost: python scripts/cost.py REPLICAS CPU_LIMIT MEM_LIMIT_GIB REQUESTS_PER_SECOND"""
import json
import sys

rc = json.load(open("data/rate_card.json"))
rep, cpu, mem, rps = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
hourly = rep * (cpu * rc["vcpu_hour"] + mem * rc["gib_memory_hour"])
per_hour = rps * 3600
print(f"hourly cost = {rep} x ({cpu} x {rc['vcpu_hour']} + {mem} x {rc['gib_memory_hour']}) = {hourly:.4f} INR")
print(f"requests/hour = {rps} x 3600 = {per_hour:.0f}")
print(f"cost per 1000 requests = ({hourly:.4f} / {per_hour:.0f}) x 1000 = {hourly / per_hour * 1000:.4f} INR")

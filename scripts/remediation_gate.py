#!/usr/bin/env python3
import json, sys, os

# Trivy JSON path
TRIVY = os.environ.get("TRIVY_JSON", "trivy-report.json")
crit = 0
try:
    with open(TRIVY) as f:
        data = json.load(f)
    for r in data.get("Results", []):
        for v in r.get("Vulnerabilities") or []:
            if v.get("Severity","").upper() == "CRITICAL":
                crit += 1
except FileNotFoundError:
    print("Trivy result not found:", TRIVY)
    # We choose to not fail if no report; change as desired
    sys.exit(0)

print(f"Critical vulnerabilities found: {crit}")
if crit > 0:
    print("Failing pipeline due to critical vulnerabilities.")
    sys.exit(1)
else:
    print("No critical vulnerabilities found.")
    sys.exit(0)

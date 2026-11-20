"""Verify a NEURAX evidence file, in two ways.

1. with NEURAX (POST /v1/evidence/verify)
2. independently, with the public key and the `cryptography` library:
   the signature is ECDSA P-256 over SHA-256 of the "evidence" field in compact JSON form.

Usage:  python verify_evidence.py neurax-fascicolo-job_xxx.json
"""
import base64, json, sys
from neurax import Client, compact_evidence

text = open(sys.argv[1], encoding="utf-8").read()
doc = json.loads(text)
nx = Client()

print("Check with NEURAX:", "AUTHENTIC" if nx.verify_evidence(text) else "NOT AUTHENTIC")

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
except ImportError:
    sys.exit("for the independent check: pip install cryptography")
key = serialization.load_pem_public_key(nx.evidence_key().encode())
try:
    key.verify(base64.b64decode(doc["signature"]), compact_evidence(text), ec.ECDSA(hashes.SHA256()))
    print("Independent check: AUTHENTIC")
except Exception:
    print("Independent check: NOT AUTHENTIC")

ev = doc["evidence"]
print("Job:", ev["job"]["id"], "| boundaries:", ev["boundaries"].get("description"),
      "| all inside boundaries:", ev["compliance"].get("all_executions_inside_boundaries"))
for x in ev.get("executions", []):
    print("  node %s, partner %s, country %s, city %s, role %s" % (
        x.get("worker_name"), x.get("partner_name", "-"), x.get("ip_country"), x.get("city"), x.get("role")))

# Evidence files

Every job has a signed evidence file: `GET /v1/jobs/{id}/evidence`.

```json
{
  "evidence": {
    "format": "neurax-evidence/1",
    "issued": "…", "issuer": "NEURAX Compute — Swiss Group Network SNC",
    "job": { "id": "job_…", "workload": "…", "status": "succeeded", "output_sha256": "…" },
    "boundaries": { "region": "EUROPE", "sovereign": true, "description": "…" },
    "executions": [ { "worker_name": "…", "partner_name": "…", "partner_verified": true,
                      "ip_country": "IT", "city": "…", "output_hash": "…", "role": "result", "t": 0 } ],
    "verification": { … }, "billing": { … }, "events": [ … ], "ledger_entries": [ … ],
    "compliance": { "all_executions_inside_boundaries": true }
  },
  "algorithm": "ECDSA-P256-SHA256",
  "key_sha256": "…",
  "signature": "…"
}
```

Executions are recorded when they happen, not reconstructed afterwards. `ip_country` is the country of
the node's IP address as detected by Cloudflare, not declared by the partner.

## Verification

- **On the website**: https://neuraxcopute.it/verifica — drag and drop the file.
- **Through the API** (public): `POST /v1/evidence/verify` with the file exactly as downloaded → `{"authentic": true}`.
- **Independently of NEURAX**: PEM public key at `GET /v1/evidence/key`. The signature is ECDSA P-256
  (DER, base64) over SHA-256 of the value of `evidence` in **compact JSON form**: the downloaded file is
  indented, so first remove whitespace outside strings (`neurax.compact_evidence` does it).
  Example: [`examples/python/verify_evidence.py`](../examples/python/verify_evidence.py).

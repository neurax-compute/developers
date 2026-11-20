# Fascicolo di prova

Ogni lavoro ha un fascicolo firmato: `GET /v1/jobs/{id}/evidence`.

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

Le esecuzioni sono registrate nel momento in cui avvengono. `ip_country` è il paese dell'indirizzo
internet del nodo rilevato da Cloudflare, non dichiarato dal partner.

## Verifica

- **Sul sito**: https://neuraxcopute.it/verifica — trascini il file.
- **Via API** (pubblico): `POST /v1/evidence/verify` con il file così com'è → `{"authentic": true}`.
- **In modo indipendente**: chiave pubblica PEM su `GET /v1/evidence/key`. La firma è ECDSA P-256
  (DER, base64) su SHA-256 del valore di `evidence` in **forma JSON compatta**: il file scaricato è
  indentato, quindi prima si tolgono gli spazi fuori dalle stringhe (`neurax.compact_evidence`).
  Esempio: [`examples/python/verify_evidence.py`](../../examples/python/verify_evidence.py).

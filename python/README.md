# neurax — Python client for NEURAX Compute

```bash
pip install "git+https://github.com/neurax-compute/developers.git#subdirectory=python"
export NEURAX_KEY="nxk_your_key"
```

```python
from neurax import Client
nx = Client()
r = nx.run("bs-mc-european@1", {"spot": 100, "strike": 105, "rate": 0.03, "volatility": 0.2,
                                 "maturity_years": 1, "option_type": "call", "paths": 20_000_000},
           region="EUROPE")
print(r["price"], r["black_scholes_exact"])
```

| Method | What it does |
|---|---|
| `quote`, `submit`, `wait`, `run` | quote, submit, wait for the verified result |
| `job`, `jobs`, `cancel`, `result` | job status, list, cancellation, result |
| `evidence`, `verify_evidence`, `evidence_key` | signed evidence file and its verification |
| `edge`, `edge_functions` | NEURAX Edge instant calls |
| `workloads`, `network_stats`, `me`, `billing` | catalogue, live network, account |
| `prices_from_csv`, `compact_evidence` | helpers for historical VaR and independent verification |

No dependencies: only the Python 3.8+ standard library. Temporary errors (rate limit, switch-over to the
standby server, network) are retried automatically. For independent verification of evidence files also
install `cryptography` (`pip install "neurax[verify]"`).

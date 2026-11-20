# Getting started

1. Sign up as a company at https://clienti.neuraxcopute.it and top up your credit.
2. In the **Accesso API** (API access) menu, create a key. It starts with `nxk_` and is shown **only once**.
3. Store it as an environment variable: `export NEURAX_KEY="nxk_…"` — never in the code of web pages or apps.

## The lifecycle of a job

| Step | Call | Notes |
|---|---|---|
| Quote | `POST /v1/quote` | no charge |
| Submit | `POST /v1/jobs` | the cost is **reserved**; use `Idempotency-Key` |
| Status | `GET /v1/jobs/{id}` | `queued` → `running` → `succeeded` / `failed` / `canceled` |
| Result | `GET /v1/jobs/{id}/result` | `?full=1` for every block |
| Evidence | `GET /v1/jobs/{id}/evidence` | signed evidence file |
| Cancel | `DELETE /v1/jobs/{id}` | reservation refunded |

The cost is **charged only once the result has been verified**.

## Conventions

- Amounts: `*_eur` (string, 6 decimals) and `*_micro_eur` (integer; 1 EUR = 1,000,000).
- Errors: `{"error": {"code": "…", "message": "…"}}` with stable codes (`invalid`, `unauthorized`,
  `insufficient_funds`, `not_ready`, `no_nodes_in_region`, `rate_limited`, …). The message is currently in Italian.
- Duplicate submissions: send an `Idempotency-Key` header (for example your order number); repeating
  the same request returns the job already created instead of creating and charging a second one.
- Rate limits: 10 requests per second on average, bursts of 40; above that, `429` with `Retry-After`.

## Available computations

`GET /v1/workloads` (public) returns the current list with an example of parameters:

| Name | What it computes |
|---|---|
| `bs-mc-european@1` | European option, compared with the exact Black-Scholes formula |
| `mc-exotic@1` | Asian and barrier options |
| `mc-var@1` | Value-at-Risk and Expected Shortfall from volatilities and correlations (Monte Carlo) |
| `hist-var@1` | Value-at-Risk and Expected Shortfall from real historical prices |
| `matmul@1` | matrix multiplication, verified with Freivalds' algorithm |

NEURAX Edge instant functions: `GET /v1/edge/functions`, called with `POST /v1/edge/run`.
The response includes `path`: which nodes answered, with city, role, outcome and milliseconds.
If the predicted fastest node is late, the NEURAX Bounce algorithm forwards the request to the next one:
the first valid answer wins and is the only one paid.

## Boundaries

On every job and Edge call: `"region": "EUROPE"` (EU/EEA and Switzerland) or `"CH"`,
`"sovereign": true` (identity-verified partners only), `"confidential": true` (certified nodes only).
The country of a node is the country of its IP address as detected by Cloudflare — the partner cannot declare it.
If there is no active node inside the boundary the job is rejected immediately with `409 no_nodes_in_region`, with no charge.

## How results are verified

| Computation | Check before charging |
|---|---|
| Options, Monte Carlo VaR | random blocks recomputed after delivery with the same random generator, plus mathematical checks |
| Historical VaR | full recomputation of every scenario |
| Matrices | Freivalds' algorithm |
| Containers and rendering | double execution on two different partners; images accepted at PSNR ≥ 35 dB |
| NEURAX Edge | all of a new node's first 10 answers, then a sample that grows when the node's reputation drops |

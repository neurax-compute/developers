# Portfolio risk: Bitcoin and other assets

Question: *"I hold EUR 100,000 in Bitcoin and EUR 200,000 in a stock: how much can I lose, in 99% of cases?"*

## Two methods

| | `hist-var@1` — historical | `mc-var@1` — parametric |
|---|---|---|
| What you send | real past prices | volatilities and correlations |
| Assumptions | none: real moves are used | log-normal returns |
| Sudden crashes (Bitcoin) | included | tend to be underestimated |
| NEURAX verification | full recomputation | random blocks recomputed |
| When to use it | crypto, volatile assets, audit | when you already have risk parameters |

## Historical: `hist-var@1`

```json
{
  "workload": "hist-var@1",
  "params": {
    "positions": [ {"name": "BTC", "value_eur": 100000}, {"name": "Stock XY", "value_eur": 200000} ],
    "dates":  ["2024-01-02", "2024-01-03", "…"],
    "prices": [[41250.0, 52.10], [42010.5, 52.35], "…"],
    "horizon_days": 1,
    "periods_per_year": 365
  }
}
```

- `prices`: one row per date, oldest first, one column per position, all in the **same currency**
  (preferably euro; if Bitcoin is in dollars, currency risk is not included).
- Every past window of `horizon_days` periods becomes a scenario applied to today's portfolio.
- `periods_per_year`: 365 for prices of every day (crypto), 252 for trading days; used only for the annual volatility.
- Limits: 50 positions, 10,000 dates, 300,000 prices in total, at least 20 scenarios.
- Convention: with N scenarios, VaR at level q is the k-th worst loss with k = ⌈N·(1−q)⌉;
  Expected Shortfall is the average of the k worst losses.

Result: `var_95_eur`, `var_99_eur`, `es_95_eur`, `es_99_eur`, `worst_loss_eur` with `worst_from` and
`worst_to`, the observed `correlation` and, for each position, `annual_volatility`, `standalone_var_99_eur`
and `es_99_contribution_eur` — how much the position weighs in the losses of the worst 1% of cases.
A low or negative contribution means the asset **offsets** Bitcoin's falls.

Full example: [`examples/python/risk_btc_historical.py`](../examples/python/risk_btc_historical.py).
In the customer portal you can simply upload a CSV exported from Excel (`date;BTC;Stock XY`).

## Parametric: `mc-var@1`

```json
{
  "workload": "mc-var@1",
  "params": {
    "positions": [ {"name": "BTC", "value_eur": 100000, "volatility": 0.60},
                   {"name": "Stock XY", "value_eur": 200000, "volatility": 0.25} ],
    "correlation": [[1, 0.3], [0.3, 1]],
    "horizon_days": 10,
    "scenarios": 2000000
  }
}
```

The volatility and correlation values are a format example, not market data.
Up to 100 positions; optional `drift` per position.

## Limits to know

- NEURAX computes on the data you send: it does not download market prices.
- The historical method only sees what happened in the period you send: more history, sturdier estimates.

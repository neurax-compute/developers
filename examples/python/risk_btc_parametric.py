"""Risk of a Bitcoin + stock portfolio with the parametric method (mc-var@1).
You provide volatility and correlation: the numbers below are only a format example."""
from neurax import Client

nx = Client()
r = nx.run("mc-var@1", {
    "positions": [{"name": "BTC", "value_eur": 100_000, "volatility": 0.60},
                  {"name": "Stock XY", "value_eur": 200_000, "volatility": 0.25}],
    "correlation": [[1, 0.3], [0.3, 1]],
    "horizon_days": 10,
    "scenarios": 2_000_000,
}, region="EUROPE")
print("VaR 99%%: %.0f EUR   ES 99%%: %.0f EUR" % (r["var_99_eur"], r["es_99_eur"]))

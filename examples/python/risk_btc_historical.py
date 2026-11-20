"""Risk of a Bitcoin + stock portfolio on real past prices (hist-var@1).

Prepare a prices.csv file (an Excel export works) like this:
    date;BTC;Stock XY
    2024-01-02;41250.50;52.10
    2024-01-03;42010.00;52.35
    ...
with all prices in the same currency (preferably euro), oldest date first.
Separators ";" "," or tab and the decimal comma are accepted.

Usage:  python risk_btc_historical.py prices.csv 100000 200000
"""
import sys
from neurax import Client, prices_from_csv

path, values = sys.argv[1], [float(v) for v in sys.argv[2:]]
names, dates, prices = prices_from_csv(path)
if len(values) != len(names):
    sys.exit("give one euro value for each column: %s" % ", ".join(names))

nx = Client()
r = nx.run("hist-var@1", {
    "positions": [{"name": n, "value_eur": v} for n, v in zip(names, values)],
    "dates": dates, "prices": prices,
    "horizon_days": 1,
    "periods_per_year": 365,          # 365 for daily prices of every day (crypto), 252 for trading days
}, region="EUROPE")

print("Real scenarios used: %d" % r["scenarios"])
print("VaR 99%%: %.0f EUR   ES 99%%: %.0f EUR" % (r["var_99_eur"], r["es_99_eur"]))
print("Worst loss: %.0f EUR (%s -> %s)" % (r["worst_loss_eur"], r.get("worst_from"), r.get("worst_to")))
for p in r["positions"]:
    print("  %-12s annual vol %5.1f%%  standalone VaR99 %10.0f  ES99 contribution %10.0f" % (
        p["name"], p["annual_volatility"] * 100, p["standalone_var_99_eur"], p["es_99_contribution_eur"]))

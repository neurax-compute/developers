# Rischio di portafoglio: BTC e altri titoli

Domanda: *"Ho 100.000 € in BTC e 200.000 € in un'azione: quanto posso perdere, nel 99% dei casi?"*

## Due metodi

| | `hist-var@1` — storico | `mc-var@1` — parametrico |
|---|---|---|
| Che cosa invii | i prezzi reali del passato | volatilità e correlazioni |
| Ipotesi | nessuna: si usano i movimenti veri | rendimenti log-normali |
| Crolli improvvisi (BTC) | inclusi | tendono a essere sottostimati |
| Verifica NEURAX | ricalcolo completo | ricalcolo di blocchi a caso |
| Quando usarlo | criptovalute, titoli volatili, revisione | quando hai già i parametri di rischio |

## Storico: `hist-var@1`

```json
{
  "workload": "hist-var@1",
  "params": {
    "positions": [ {"name": "BTC", "value_eur": 100000}, {"name": "Azione XY", "value_eur": 200000} ],
    "dates":  ["2024-01-02", "2024-01-03", "…"],
    "prices": [[41250.0, 52.10], [42010.5, 52.35], "…"],
    "horizon_days": 1,
    "periods_per_year": 365
  }
}
```

- `prices`: una riga per data, dalla più vecchia alla più recente, una colonna per posizione; tutti
  nella **stessa valuta** (meglio euro).
- Ogni finestra di `horizon_days` periodi del passato diventa uno scenario applicato al portafoglio di oggi.
- Limiti: 50 posizioni, 10.000 date, 300.000 prezzi in tutto, almeno 20 scenari.
- Convenzione: con N scenari, il VaR al livello q è la k-esima perdita peggiore con k = ⌈N·(1−q)⌉;
  l'Expected Shortfall è la media delle k perdite peggiori.

Risultato: `var_95_eur`, `var_99_eur`, `es_95_eur`, `es_99_eur`, `worst_loss_eur` con `worst_from` e
`worst_to`, `correlation` osservata e, per ogni posizione, `annual_volatility`, `standalone_var_99_eur` e
`es_99_contribution_eur` — quanto la posizione pesa nelle perdite dell'1% dei casi peggiori.
Un contributo basso o negativo indica che il titolo **compensa** le cadute di BTC.

Esempio completo: [`examples/python/risk_btc_historical.py`](../../examples/python/risk_btc_historical.py).
Dal portale clienti basta caricare il CSV esportato da Excel (`data;BTC;Azione XY`).

## Parametrico: `mc-var@1`

```json
{
  "workload": "mc-var@1",
  "params": {
    "positions": [ {"name": "BTC", "value_eur": 100000, "volatility": 0.60},
                   {"name": "Azione XY", "value_eur": 200000, "volatility": 0.25} ],
    "correlation": [[1, 0.3], [0.3, 1]],
    "horizon_days": 10,
    "scenarios": 2000000
  }
}
```

I valori di volatilità e correlazione sono un esempio di formato, non dati di mercato.
Fino a 100 posizioni; `drift` facoltativo per posizione.

## Limiti da conoscere

- NEURAX calcola sui dati che invii: non scarica prezzi di mercato.
- Il metodo storico vede solo ciò che è successo nel periodo inviato: più storia, stime più solide.
- Per una posizione in BTC quotata in dollari, il rischio di cambio è incluso solo se i prezzi sono in euro.

# Primi passi

1. Registrati come azienda su https://clienti.neuraxcopute.it e ricarica il credito.
2. Nel menu **Accesso API** crea una chiave. Inizia con `nxk_` e si vede **una sola volta**.
3. Salvala come variabile d'ambiente: `export NEURAX_KEY="nxk_…"` (mai nel codice di pagine web o app).

## Il ciclo di un lavoro

| Passo | Chiamata | Note |
|---|---|---|
| Preventivo | `POST /v1/quote` | nessun addebito |
| Invio | `POST /v1/jobs` | il costo viene **riservato**; usa `Idempotency-Key` |
| Stato | `GET /v1/jobs/{id}` | `queued` → `running` → `succeeded` / `failed` / `canceled` |
| Risultato | `GET /v1/jobs/{id}/result` | `?full=1` per tutti i blocchi |
| Prova | `GET /v1/jobs/{id}/evidence` | fascicolo firmato |
| Annullo | `DELETE /v1/jobs/{id}` | rimborso della riserva |

Il costo viene **addebitato solo quando il risultato è stato verificato**.

## Convenzioni

- Importi: `*_eur` (stringa, 6 decimali) e `*_micro_eur` (intero; 1 € = 1.000.000).
- Errori: `{"error": {"code": "…", "message": "…"}}` con codici stabili (`invalid`, `unauthorized`,
  `insufficient_funds`, `not_ready`, `no_nodes_in_region`, `rate_limited`, …).
- Limiti: 10 richieste al secondo in media, picchi di 40; oltre, `429` con `Retry-After`.

## Calcoli disponibili

`GET /v1/workloads` (pubblico) restituisce l'elenco aggiornato con un esempio di parametri:

| Nome | Che cosa calcola |
|---|---|
| `bs-mc-european@1` | opzione europea, confrontata con la formula esatta di Black-Scholes |
| `mc-exotic@1` | opzioni asiatiche e con barriera |
| `mc-var@1` | VaR ed Expected Shortfall con volatilità e correlazioni (Monte Carlo) |
| `hist-var@1` | VaR ed Expected Shortfall sui prezzi reali del passato |
| `matmul@1` | moltiplicazione di matrici, verificata con Freivalds |

Funzioni istantanee NEURAX Edge: `GET /v1/edge/functions`, chiamata con `POST /v1/edge/run`.

## Confini

Su ogni lavoro e chiamata Edge: `"region": "EUROPE"` o `"CH"`, `"sovereign": true` (solo partner
verificati), `"confidential": true` (solo nodi certificati). Il paese di un nodo è quello del suo
indirizzo internet, rilevato da Cloudflare.

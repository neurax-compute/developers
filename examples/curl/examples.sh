#!/usr/bin/env bash
# curl examples. First: export NEURAX_KEY="nxk_your_key"
set -euo pipefail
API=https://api.neuraxcopute.it
AUTH="Authorization: Bearer $NEURAX_KEY"

# 1. available computations (public)
curl -s $API/v1/workloads

# 2. quote (no charge)
curl -s -X POST $API/v1/quote -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"workload":"bs-mc-european@1","params":{"spot":100,"strike":105,"rate":0.03,"volatility":0.2,"maturity_years":1,"option_type":"call","paths":20000000}}'

# 3. submit: Europe only, identity-verified partners only (Sovereign Tier)
ID=$(curl -s -X POST $API/v1/jobs -H "$AUTH" -H "Content-Type: application/json" -H "Idempotency-Key: example-$(date +%s)" \
  -d '{"workload":"bs-mc-european@1","region":"EUROPE","sovereign":true,"params":{"spot":100,"strike":105,"rate":0.03,"volatility":0.2,"maturity_years":1,"option_type":"call","paths":20000000}}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
echo "job $ID"

# 4. wait and fetch the verified result
until curl -s $API/v1/jobs/$ID -H "$AUTH" | grep -q '"status": "succeeded"'; do sleep 2; done
curl -s $API/v1/jobs/$ID/result -H "$AUTH"

# 5. evidence file and authenticity check (public)
curl -s $API/v1/jobs/$ID/evidence -H "$AUTH" -o evidence.json
curl -s -X POST $API/v1/evidence/verify -H "Content-Type: application/json" --data-binary @evidence.json

# 6. NEURAX Edge instant call
curl -s -X POST $API/v1/edge/run -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"function":"option.price@1","input":{"spot":100,"strike":105,"rate":0.03,"volatility":0.2,"years":1,"type":"call"},"region":"EUROPE"}'

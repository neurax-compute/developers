// NEURAX Edge from Node.js 18+:  NEURAX_KEY=nxk_... node edge.mjs
const API = "https://api.neuraxcopute.it";
const H = { Authorization: "Bearer " + process.env.NEURAX_KEY, "Content-Type": "application/json" };

const res = await fetch(API + "/v1/edge/run", {
  method: "POST", headers: H,
  body: JSON.stringify({
    function: "option.price@1",
    input: { spot: 100, strike: 105, rate: 0.03, volatility: 0.2, years: 1, type: "call" },
    region: "EUROPE",
  }),
});
if (!res.ok) throw new Error((await res.json()).error.code);
const out = await res.json();
console.log("result:", out.output);
console.log(`time: ${out.latency_ms.toFixed(1)} ms, price: ${out.price_eur} EUR, bounced: ${out.bounced}`);
for (const h of out.path) console.log(`  ${h.role} ${h.city || h.node} -> ${h.outcome} in ${h.ms.toFixed(1)} ms`);

// Submit a job and wait for the verified result (Node.js 18+)
const API = "https://api.neuraxcopute.it";
const H = { Authorization: "Bearer " + process.env.NEURAX_KEY, "Content-Type": "application/json" };
const call = async (method, path, body, extra = {}) => {
  const r = await fetch(API + path, { method, headers: { ...H, ...extra }, body: body && JSON.stringify(body) });
  const j = await r.json();
  if (!r.ok) throw new Error(`${r.status} ${j.error.code}: ${j.error.message}`);
  return j;
};
const job = await call("POST", "/v1/jobs", {
  workload: "mc-exotic@1", region: "EUROPE",
  params: { spot: 100, strike: 100, rate: 0.03, volatility: 0.25, maturity_years: 1, option_type: "call", style: "asian", steps: 252, paths: 2000000 },
}, { "Idempotency-Key": "js-" + Date.now() });
let j;
do { await new Promise((r) => setTimeout(r, 2000)); j = await call("GET", "/v1/jobs/" + job.id); } while (!["succeeded", "failed", "canceled"].includes(j.status));
console.log(j.status === "succeeded" ? await call("GET", `/v1/jobs/${job.id}/result`) : j);

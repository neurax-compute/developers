"""Official Python client for the NEURAX Compute API.

Uses only the Python standard library (3.8 or later): no dependencies.

    from neurax import Client
    nx = Client()                       # reads the key from NEURAX_KEY
    job = nx.submit("mc-var@1", {...}, region="EUROPE")
    result = nx.wait(job["id"])

Copyright (c) 2026 Swiss Group Network SNC. MIT License (see LICENSE).
"""

import csv
import io
import json
import os
import time
import urllib.error
import urllib.request
import uuid

__all__ = ["Client", "NeuraxError", "prices_from_csv", "compact_evidence"]
__version__ = "1.0.0"

DEFAULT_BASE = "https://api.neuraxcopute.it"


class NeuraxError(Exception):
    """Error returned by the API: .status (HTTP), .code (stable), .message (currently in Italian)."""

    def __init__(self, status, code, message, retry_after=None):
        super().__init__("%s %s: %s" % (status, code, message))
        self.status, self.code, self.message, self.retry_after = status, code, message, retry_after


class Client:
    def __init__(self, key=None, base_url=DEFAULT_BASE, timeout=60, retries=3):
        self.key = key or os.environ.get("NEURAX_KEY", "")
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries

    # ------------------------------------------------------------ transport
    def request(self, method, path, body=None, headers=None, raw=False, auth=True):
        data = None
        h = {"Accept": "application/json", "User-Agent": "neurax-python/" + __version__}
        if auth and self.key:
            h["Authorization"] = "Bearer " + self.key
        if body is not None:
            data = body if isinstance(body, (bytes, bytearray)) else json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        h.update(headers or {})
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(self.base + path, data=data, method=method, headers=h)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    b = r.read()
                    return b if raw else (json.loads(b) if b else None)
            except urllib.error.HTTPError as e:
                b = e.read()
                try:
                    err = json.loads(b).get("error", {})
                except ValueError:
                    err = {}
                ra = e.headers.get("Retry-After")
                # temporary conditions: rate limit, switch-over to the standby server
                if attempt < self.retries and (e.code == 429 and err.get("code") == "rate_limited" or e.code in (502, 503)):
                    time.sleep(float(ra) if ra and ra.isdigit() else 2 ** attempt)
                    continue
                raise NeuraxError(e.code, err.get("code", "http_%d" % e.code), err.get("message", b.decode("utf-8", "replace")[:300]), ra)
            except urllib.error.URLError:
                if attempt < self.retries:
                    time.sleep(2 ** attempt)
                    continue
                raise

    # ------------------------------------------------------------ public
    def info(self):
        return self.request("GET", "/v1/info", auth=False)

    def workloads(self):
        return self.request("GET", "/v1/workloads", auth=False)

    def network_stats(self):
        return self.request("GET", "/v1/network/stats", auth=False)

    # ------------------------------------------------------------ jobs
    @staticmethod
    def _job(workload, params, region=None, sovereign=False, confidential=False):
        j = {"workload": workload, "params": params}
        if region:
            j["region"] = region
        if sovereign:
            j["sovereign"] = True
        if confidential:
            j["confidential"] = True
        return j

    def quote(self, workload, params, **bounds):
        """Quote: no charge."""
        return self.request("POST", "/v1/quote", self._job(workload, params, **bounds))

    def submit(self, workload, params, idempotency_key=None, **bounds):
        """Submit a job. The cost is reserved and charged only once the result is verified.
        bounds: region="EUROPE"|"CH", sovereign=True, confidential=True."""
        key = idempotency_key or "py-" + uuid.uuid4().hex
        return self.request("POST", "/v1/jobs", self._job(workload, params, **bounds), headers={"Idempotency-Key": key})

    def job(self, job_id):
        return self.request("GET", "/v1/jobs/" + job_id)

    def jobs(self):
        return self.request("GET", "/v1/jobs")

    def cancel(self, job_id):
        return self.request("DELETE", "/v1/jobs/" + job_id)

    def result(self, job_id, full=False):
        return self.request("GET", "/v1/jobs/%s/result%s" % (job_id, "?full=1" if full else ""))

    def wait(self, job_id, timeout=3600, poll=2.0):
        """Wait for the job to finish and return the verified result."""
        end = time.time() + timeout
        while True:
            j = self.job(job_id)
            if j["status"] == "succeeded":
                return self.result(job_id)
            if j["status"] in ("failed", "canceled"):
                raise NeuraxError(409, "job_" + j["status"], j.get("fail_reason") or j["status"])
            if time.time() > end:
                raise TimeoutError("job %s still %s" % (job_id, j["status"]))
            time.sleep(poll)

    def run(self, workload, params, **kw):
        """Submit and wait: returns the verified result."""
        timeout = kw.pop("timeout", 3600)
        return self.wait(self.submit(workload, params, **kw)["id"], timeout=timeout)

    # ------------------------------------------------------------ evidence
    def evidence(self, job_id, path=None):
        """Download the signed evidence file; if path is given, save it to disk."""
        b = self.request("GET", "/v1/jobs/%s/evidence" % job_id, raw=True)
        if path:
            with open(path, "wb") as f:
                f.write(b)
        return json.loads(b)

    def verify_evidence(self, file_bytes):
        """Authenticity check with NEURAX: posts the file exactly as it is."""
        if isinstance(file_bytes, str):
            file_bytes = file_bytes.encode()
        return self.request("POST", "/v1/evidence/verify", file_bytes, auth=False)["authentic"]

    def evidence_key(self):
        """PEM public key NEURAX uses to sign evidence files."""
        return self.request("GET", "/v1/evidence/key", raw=True, auth=False).decode()

    # ------------------------------------------------------------ edge
    def edge_functions(self):
        return self.request("GET", "/v1/edge/functions", auth=False)

    def edge(self, function, input, region=None, near=None, timeout_ms=None):
        """NEURAX Edge instant call. near=(lat, lon) of the end user, optional."""
        q = {"function": function, "input": input}
        if region:
            q["region"] = region
        if near:
            q["near"] = {"lat": near[0], "lon": near[1]}
        if timeout_ms:
            q["timeout_ms"] = timeout_ms
        return self.request("POST", "/v1/edge/run", q)

    # ------------------------------------------------------------ account
    def me(self):
        return self.request("GET", "/v1/me")

    def billing(self):
        return self.request("GET", "/v1/billing")


def prices_from_csv(path_or_text, delimiter=None):
    """Read a CSV of historical prices: first row "date;NAME1;NAME2", then one row per date.
    Accepts ";" "," or tab separators and the decimal comma. Returns (names, dates, prices)."""
    text = path_or_text
    if "\n" not in path_or_text and os.path.exists(path_or_text):
        with open(path_or_text, encoding="utf-8-sig") as f:
            text = f.read()
    first = text.lstrip("﻿").splitlines()[0]
    sep = delimiter or (";" if ";" in first else "\t" if "\t" in first else ",")
    rows = [r for r in csv.reader(io.StringIO(text.lstrip("﻿")), delimiter=sep) if any(c.strip() for c in r)]
    names = [c.strip() for c in rows[0][1:]]

    def num(x):
        x = x.strip().replace("'", "")
        if sep != "," and "," in x:
            x = x.replace(".", "").replace(",", ".")
        return float(x)

    dates, prices = [], []
    for i, r in enumerate(rows[1:], start=2):
        vals = [num(x) for x in r[1:]]
        if len(vals) != len(names) or any(v <= 0 for v in vals):
            raise ValueError("row %d: %d positive prices expected" % (i, len(names)))
        dates.append(r[0].strip())
        prices.append(vals)
    return names, dates, prices


def compact_evidence(file_text):
    """Return the signed bytes of an evidence file: the value of "evidence" in compact JSON form,
    exactly as NEURAX signed it (needed for independent verification)."""
    s = file_text.decode() if isinstance(file_text, bytes) else file_text
    i = s.index('"evidence"') + len('"evidence"')
    i = s.index(":", i) + 1
    while s[i] in " \t\r\n":
        i += 1
    depth, j, in_str, esc = 0, i, False, False
    out = []
    while True:
        c = s[j]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
                out.append(c)
            elif c in " \t\r\n":
                pass
            else:
                out.append(c)
                if c in "{[":
                    depth += 1
                elif c in "}]":
                    depth -= 1
                    if depth == 0:
                        break
        j += 1
    return "".join(out).encode()

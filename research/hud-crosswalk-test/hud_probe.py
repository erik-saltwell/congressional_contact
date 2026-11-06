"""Probe the HUD USPS crosswalk API. Reads HUD_API_TOKEN from the repo .env; never prints it.
Usage: python3 -I hud_probe.py ENV_FILE OUT_JSON type=5 query=10003 [year=2025 quarter=2]
Prints only HTTP status, top-level metadata and result count."""
import json, sys, urllib.request, urllib.parse, urllib.error, pathlib

def token(env):
    for line in pathlib.Path(env).read_text().splitlines():
        if line.startswith("HUD_API_TOKEN="):
            v = line.split("=", 1)[1].strip().strip('"').strip("'")
            if v: return v
    sys.exit("HUD_API_TOKEN missing or empty in .env")

env, out, *kv = sys.argv[1:]
params = dict(a.split("=", 1) for a in kv)
url = "https://www.huduser.gov/hudapi/public/usps?" + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token(env),
                                           "Accept": "application/json",
                                           "User-Agent": "congressional-contact-data-tool"})
try:
    with urllib.request.urlopen(req, timeout=600) as r:
        body = r.read(); status = r.status
except urllib.error.HTTPError as e:
    body = e.read(); status = e.code
pathlib.Path(out).write_bytes(body)
print("params", params, "HTTP", status, "bytes", len(body))
try:
    d = json.loads(body)
except Exception:
    print("non-JSON body start:", body[:200]); sys.exit(0)
data = d.get("data", d) if isinstance(d, dict) else d
if isinstance(data, list): data = data[0] if data else {}
if isinstance(data, dict):
    print({k: v for k, v in data.items() if k != "results"})
    res = data.get("results")
    if isinstance(res, list):
        print("results", len(res)); print(json.dumps(res[:5]))
else:
    print(str(d)[:300])

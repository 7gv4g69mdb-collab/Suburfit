"""Fetch the two newest SA Private Rent Report files (Consumer and Business Services bond data, CC BY 4.0) into rent/."""
import json, os, re, urllib.request
API = "https://data.sa.gov.au/data/api/3/action/package_show?id=private-rent-report"
OUT = os.path.join(os.path.dirname(__file__), "rent")

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "suburb-fit-data-fetch"})
    with urllib.request.urlopen(req, timeout=120) as r: return r.read()

found = []
for res in json.loads(get(API))["result"]["resources"]:
    m = re.search(r"private-rental-report-(20\d\d-\d\d)\.xlsx$", res.get("url", ""), re.I)
    if m: found.append((m.group(1), res["url"]))
os.makedirs(OUT, exist_ok=True)
keep = sorted(found)[-2:]
for when, url in keep:
    path = os.path.join(OUT, f"private-rental-report-{when}.xlsx")
    if not os.path.exists(path): open(path, "wb").write(get(url)); print("new", when)
for f in os.listdir(OUT):
    if f.endswith(".xlsx") and f not in {f"private-rental-report-{w}.xlsx" for w, _ in keep}: os.remove(os.path.join(OUT, f))

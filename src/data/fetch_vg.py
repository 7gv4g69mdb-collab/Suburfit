"""Fetch the latest Metropolitan Median House Sales quarters from data.sa.gov.au and save each sheet as CSV."""
import csv, io, json, os, re, urllib.request

API = "https://data.sa.gov.au/data/api/3/action/package_show?id=metro-median-house-sales"
OUT = os.path.join(os.path.dirname(__file__), "raw")
KEEP = 6  # newest quarters to keep

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "suburb-fit-data-fetch"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

pkg = json.loads(get(API))["result"]
found = []
for res in pkg["resources"]:
    text = f'{res.get("name","")} {res.get("url","")}'
    m = re.search(r"Q([1-4])\D{0,3}(20\d\d)", text, re.I) or re.search(r"(20\d\d)[_\- ]?([1-4])q", text, re.I)
    if not m: continue
    q, y = (int(m.group(1)), int(m.group(2))) if m.re.pattern.startswith("Q") else (int(m.group(2)), int(m.group(1)))
    found.append((y, q, res))
found.sort(key=lambda t: (t[0], t[1]), reverse=True)
os.makedirs(OUT, exist_ok=True)
index = []
for y, q, res in found[:KEEP]:
    url = res["url"]; data = get(url)
    stem = f"{y}-Q{q}"
    rows_by_sheet = {}
    if url.lower().endswith(".xls"):
        import xlrd
        wb = xlrd.open_workbook(file_contents=data)
        for sh in wb.sheets():
            rows_by_sheet[sh.name] = [sh.row_values(i) for i in range(sh.nrows)]
    else:
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True, read_only=True)
        for ws in wb.worksheets:
            rows_by_sheet[ws.title] = [list(r) for r in ws.iter_rows(values_only=True)]
    for i, (name, rows) in enumerate(rows_by_sheet.items()):
        path = os.path.join(OUT, f"{stem}-sheet{i + 1}.csv")
        with open(path, "w", newline="") as f:
            csv.writer(f).writerows([["" if v is None else v for v in r] for r in rows])
    index.append({"quarter": stem, "name": res.get("name"), "url": url, "sheets": list(rows_by_sheet)})
    print(stem, url, list(rows_by_sheet))
with open(os.path.join(OUT, "index.json"), "w") as f:
    json.dump(index, f, indent=1)

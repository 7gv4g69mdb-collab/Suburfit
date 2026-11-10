"""Build the `const RENTS = {...}` line from the SA Private Rent Report (CBS bond data, CC BY 4.0) in rent/ (fetched by fetch_rents.py).

Combines the two latest quarters, so suburbs with few new leases still get a figure. Medians are averaged,
weighted by the number of bonds ("*" means 1 to 5 bonds; counted as 3). Metropolitan suburbs only.
"""
import glob, json, os, re
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__))
COLS = {"house": (19, 20), "house3": (15, 16), "house2": (13, 14), "house4": (17, 18), "unit": (9, 10), "unit2": (3, 4), "unit1": (1, 2)}
MIN = 5  # fewer bonds than this across both quarters: leave that figure out

def num(v): return 3 if v == "*" else (v or 0)

def read(path):
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Suburb"]
    rows = list(ws.iter_rows(values_only=True))
    title = next(str(r[0]) for r in rows if r[0] and str(r[0]).startswith("Suburbs by dwelling type"))
    a, b = re.search(r"1 (\w+) - \d+ (\w+ \d{4})", title).groups()  # e.g. "1 April - 30 June 2026"
    period = f"{a[:3]}-{b[:3]} {b[-4:]}"
    out, metro = {}, False
    for r in rows:
        if r[0] == "Metro": metro = True; continue
        if r[0] in ("Non-Metro", "Country", "Grand Total") or (metro and r[0] and str(r[0]).endswith("Total")): metro = False; continue
        if not metro or not r[0] or not isinstance(r[0], str): continue
        out[r[0].strip().upper()] = {k: (num(r[c]), r[m]) for k, (c, m) in COLS.items() if r[m]}
    return period, out

def main():
    files = sorted(glob.glob(os.path.join(HERE, "rent", "private-rental-report-*.xlsx")), key=lambda f: f[-12:])[-2:]
    periods, data = [], {}
    for f in files:
        p, d = read(f); periods.append(p)
        for sub, v in d.items():
            for k, (c, m) in v.items(): data.setdefault(sub, {}).setdefault(k, []).append((c, m))
    rents = {}
    for sub, v in data.items():
        e = {}
        for k, xs in v.items():
            n = sum(c for c, _ in xs)
            if n >= MIN: e[k] = [round(sum(c * m for c, m in xs) / n / 5) * 5, n]
        if e: rents[sub] = e
    span = f"{periods[0][:3]} {periods[0][-4:]} to {periods[-1][4:]}"  # "Jan 2026 to Jun 2026"
    js = "  const RENTS = " + json.dumps(rents, separators=(",", ":")) + ";\n  const RENT_PERIOD = " + json.dumps(span) + ";"
    open(os.path.join(HERE, "rents.js"), "w").write(js)
    print(len(rents), "suburbs with rents,", span)

if __name__ == "__main__":
    main()

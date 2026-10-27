"""Read the Valuer-General quarterly CSVs in raw/ (saved by the fetch job).
load() returns (quarter labels, {(COUNCIL, SUBURB): [(sales, median) per quarter, oldest first]}) for the latest 4 quarters."""
import csv, glob, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
def load(n=4):
    files = sorted(glob.glob(os.path.join(HERE, "raw", "*-Q*-sheet1.csv")))[-n:]
    quarters, per = [], []
    for f in files:
        y, q = re.search(r"(\d{4})-Q(\d)", f).groups(); quarters.append(f"Q{q} {y}")
        rows = list(csv.reader(open(f))); hdr = rows[0]
        si = max(i for i, h in enumerate(hdr) if h.startswith("Sales"))
        mi = max(i for i, h in enumerate(hdr) if h.startswith("Median") and "Change" not in h)
        assert y in hdr[si] and q in hdr[si], (f, hdr)
        d = {}
        for r in rows[1:]:
            if len(r) > mi and r[1]:
                d[(r[0].strip().upper(), r[1].strip().upper())] = (int(float(r[si])) if r[si] else 0, int(float(r[mi])) if r[mi] else 0)
        per.append(d)
    keys = set().union(*per)
    return quarters, {k: [p.get(k, (0, 0)) for p in per] for k in keys}
def year(q):
    n = sum(s for s, _ in q); return (n, round(sum(s * m for s, m in q) / n / 1000) * 1000 if n else None)

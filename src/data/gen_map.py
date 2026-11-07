"""Write mapdata.js: every metropolitan Adelaide suburb the Valuer-General lists that isn't in the budget tool,
with its median house price (same method as gen.py) and simplified ABS boundary, for the price map only."""
import json, os
from parse_vg import load, year
import gen
HERE = os.path.dirname(os.path.abspath(__file__))
shapes = json.load(open(os.path.join(HERE, "abs_sal_sa_shapes.json")))
pts = json.load(open(os.path.join(HERE, "abs_sal_sa.json")))
s = open(os.path.join(HERE, "suburbs.js")).read(); inapp = {x["name"].upper() for x in json.loads(s[s.index("["):s.rindex("]") + 1])}
from gen_shapes import simplify
quarters, data = load()
out, seen = [], set()
for (council, name), q in sorted(data.items()):
    if name in inapp or name in seen or name not in shapes: continue
    seen.add(name)
    sales, med = year(q)
    meds = [m for sl, m in q if sl]
    varies = len(meds) >= 3 and max(meds) / min(meds) >= gen.VARY
    if med and varies and len(meds) >= 4:
        keep = sorted((m, sl) for sl, m in q if sl)[1:-1]
        med = round(sum(m * sl for m, sl in keep) / sum(sl for _, sl in keep) / 1000) * 1000
    d = {"n": gen.title(name), "c": gen.title(council), "s": sales, "m": med if sales >= gen.MIN_SALES else None,
         "lat": pts[name]["lat"], "lng": pts[name]["lng"], "r": [simplify(r) for r in shapes[name]]}
    if varies and sales >= gen.MIN_SALES: d["v"] = [min(meds), max(meds)]
    out.append(d)
js = "  const MAP_EXTRA = " + json.dumps(out, separators=(",", ":")) + ";"
open(os.path.join(HERE, "mapdata.js"), "w").write(js)
print(len(out), "extra suburbs,", sum(1 for d in out if d["m"]), "with a price,", round(len(js) / 1024), "KB")

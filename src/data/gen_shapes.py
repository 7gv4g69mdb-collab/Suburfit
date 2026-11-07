"""Write shapes.js: simplified ABS boundaries for the suburbs in suburbs.js, keyed by suburb id (for the price map)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
shapes = json.load(open(os.path.join(HERE, "abs_sal_sa_shapes.json")))
s = open(os.path.join(HERE, "suburbs.js")).read(); subs = json.loads(s[s.index("["):s.rindex("]") + 1])
def simplify(ring, tol=0.0004):
    # drop points closer than tol to the last kept point (about 40 m), keep the ring closed
    out = [ring[0]]
    for p in ring[1:-1]:
        if abs(p[0] - out[-1][0]) > tol or abs(p[1] - out[-1][1]) > tol: out.append(p)
    out.append(ring[-1]); return out if len(out) >= 4 else ring
out, missing = {}, []
for x in subs:
    rings = shapes.get(x["name"].upper())
    if not rings: missing.append(x["name"]); continue
    out[x["id"]] = [simplify(r) for r in rings]
js = "  const SHAPES = " + json.dumps(out, separators=(",", ":")) + ";"
open(os.path.join(HERE, "shapes.js"), "w").write(js)
print(len(out), "shapes,", round(len(js) / 1024), "KB; no boundary:", missing)

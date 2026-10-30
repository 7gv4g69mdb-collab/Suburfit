"""Download ABS ASGS 2021 Suburbs and Localities (SAL) boundaries for SA and save each suburb's centre point.
Source: Australian Bureau of Statistics, ASGS Edition 3 (CC BY 4.0). Output: src/data/abs_sal_sa.json {"SEATON": {"lat":..,"lng":..}}"""
import json, os, re, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
BASES = ["https://geo.abs.gov.au/arcgis/rest/services/ASGS2021/SAL/MapServer/0",
         "https://geo.abs.gov.au/arcgis/rest/services/ASGS2021/SAL/FeatureServer/0"]
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "suburb-fit-data-fetch"})
    return json.loads(urllib.request.urlopen(req, timeout=180).read())
def centroid(rings):
    A = cx = cy = 0.0
    for ring in rings:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
            c = x1 * y2 - x2 * y1; A += c; cx += (x1 + x2) * c; cy += (y1 + y2) * c
    if abs(A) < 1e-12:
        pts = [p for r in rings for p in r]; return sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts)
    return cy / (3 * A), cx / (3 * A)
for base in BASES:
    try:
        meta = get(base + "?f=json"); fields = [f["name"] for f in meta.get("fields", [])]
        print("layer", base, meta.get("name"), fields)
        name_f = next(f for f in fields if f.upper().startswith("SAL_NAME"))
        state_f = next(f for f in fields if f.upper().startswith("STATE_CODE") or f.upper().startswith("STE_CODE"))
        out, off = {}, 0
        while True:
            q = urllib.parse.urlencode({"where": f"{state_f}='4'", "outFields": name_f, "returnGeometry": "true", "outSR": "4326",
                                        "geometryPrecision": "5", "maxAllowableOffset": "0.0005", "resultOffset": off, "resultRecordCount": 200, "f": "json"})
            d = get(base + "/query?" + q); feats = d.get("features", [])
            for f in feats:
                g = f.get("geometry") or {}
                if not g.get("rings"): continue
                lat, lng = centroid(g["rings"])
                name = re.sub(r"\s*\(SA\)$", "", f["attributes"][name_f]).upper()
                out[name] = {"lat": round(lat, 5), "lng": round(lng, 5)}
            print("got", off, len(feats))
            if not feats or not d.get("exceededTransferLimit") and len(feats) < 200: break
            off += len(feats)
        json.dump(out, open(os.path.join(HERE, "abs_sal_sa.json"), "w"), indent=0, sort_keys=True)
        print("saved", len(out)); break
    except Exception as e:
        print("FAIL", base, repr(e))

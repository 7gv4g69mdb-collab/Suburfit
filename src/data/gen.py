import json, re
from vg import CS, WT, year
coords = json.load(open('coords.json'))
# Existing hand-checked data for the original ten (nearest petrol station, bedroom medians from property.com.au)
orig = {
 "FULHAM GARDENS": dict(id="fulham", petrol=2.419, station="Ampol Fulham Gardens", salesMedian=1375000, bed=[817000,960000,1250000,1450000,1680000]),
 "LOCKLEYS": dict(id="lockleys", petrol=2.389, station="BP Brooklyn Park / Shell Underdale", salesMedian=1555000, bed=[790000,929000,1310000,1690000,1930000]),
 "WEST BEACH": dict(id="westbeach", petrol=2.414, station="Shell OTR West Beach", salesMedian=1764000, bed=[969000,1140000,1480000,1890000,2100000]),
 "SEATON": dict(id="seaton", petrol=2.369, station="United Seaton", salesMedian=1070000, bed=[796000,936000,1040000,1210000,1530000]),
 "ROYAL PARK": dict(id="royalpark", petrol=2.295, station="United Woodville (Hanson Rd)", salesMedian=862500, bed=[615000,723000,850000,930000,1070000]),
 "FLINDERS PARK": dict(id="flinderspark", petrol=2.389, station="Shell OTR Underdale", salesMedian=1298500, bed=[859000,1010000,1200000,1450000,1620000]),
 "FINDON": dict(id="findon", petrol=2.369, station="United Findon", salesMedian=1040000, bed=[619000,728000,1040000,1190000,1500000]),
 "HENLEY BEACH": dict(id="henleybeach", petrol=2.414, station="Shell OTR West Beach", salesMedian=1672500, bed=[1122000,1320000,1550000,1850000,2250000]),
 "HENDON": dict(id="hendon", petrol=2.404, station="OTR Shell Hendon", salesMedian=962500, bed=[762000,897000,997000,1117000,1280000]),
 "WOODVILLE WEST": dict(id="woodvillewest", petrol=2.295, station="United Woodville (Hanson Rd)", salesMedian=1056250, bed=[626000,737000,1050000,1200000,1360000]),
}
coastal = {"WEST BEACH","HENLEY BEACH","HENLEY BEACH SOUTH","TENNYSON","GRANGE","SEMAPHORE PARK","WEST LAKES SHORE","GLENELG NORTH"}
flood = {"LOCKLEYS","FULHAM","WEST LAKES"}
river = {"FULHAM GARDENS","FLINDERS PARK","KIDMAN PARK","UNDERDALE","TORRENSVILLE","THEBARTON","ALLENBY GARDENS","WEST HINDMARSH","BOWDEN","NOVAR GARDENS"}
inner = {"BROMPTON","RIDLEYTON","RENOWN PARK","OVINGHAM","CROYDON","WELLAND","THEBARTON","TORRENSVILLE","MILE END","HILTON","KESWICK","COWANDILLA","WEST HINDMARSH","KILKENNY","RICHMOND","MARLESTON"}
def title(n): return " ".join(w.capitalize() if w != "ST" else "St" for w in n.split())
out = []
for council, src in (("Charles Sturt", CS), ("West Torrens", WT)):
    for n, q in src.items():
        if n == "WEST BEACH": council_n = "West Torrens"   # the Valuer-General lists West Beach under both councils; it is in West Torrens
        else: council_n = council
        sales, med = year(q)
        c = coords[n]
        o = orig.get(n, {})
        if n in coastal: ins, note = 1.15, "coastal and low-lying"
        elif n in flood: ins, note = 1.10, "parts sit on a floodplain"
        elif n in river: ins, note = 1.05, "it's near the River Torrens or Patawalonga"
        else: ins, note = 1.00, "no major flood or coastal loading"
        land = 250 if n == "BOWDEN" else 450 if n in inner else 550 if n in coastal else 600
        if o.get("id") in ("lockleys",): land = 650
        if o.get("id") in ("royalpark","hendon","henleybeach"): land = 500
        if o.get("id") in ("westbeach","woodvillewest"): land = 550
        d = dict(id=o.get("id") or re.sub(r"[^a-z0-9]+","",n.lower()), name=title(n), council=council_n, median=med, sales=sales,
                 lat=c["lat"], lng=c["lng"], postcode=c["pc"], insFactor=ins, insNote=note,
                 petrol=o.get("petrol", 2.388), station=o.get("station", "Adelaide average price"), typLand=land)
        if o: d["salesMedian"] = o["salesMedian"]; d["bed"] = {str(i+1): v for i, v in enumerate(o["bed"])}
        if any(x["id"] == d["id"] for x in out) or (not o and d["id"] in {v["id"] for v in orig.values()}): d["id"] += "-" + council_n.split()[0].lower()
        out.append(d)
out.sort(key=lambda d: (d["council"], d["name"]))
js = "  const SUBURBS = " + json.dumps(out, separators=(",", ":")).replace('},{', '},\n    {') + ".map(s => ({ ...s, region: \"City of \" + s.council }));"
open("suburbs.js","w").write(js)
print(len(out), "suburbs")

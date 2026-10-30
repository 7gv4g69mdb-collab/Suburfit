"""Build suburbs.js (the `const SUBURBS = [...]` line in the app) from the Valuer-General files in raw/.

Run after the fetch job adds a new quarter: python3 src/data/gen.py
Prices are the sales-weighted median of the latest four quarters. Suburbs with fewer than MIN_SALES
house sales in 12 months are left out; the app flags 15 or fewer as "Few sales".
"""
import csv, json, os, re
from parse_vg import load, year

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_SALES = 5
VARY = 1.5  # flag a suburb when its highest quarterly median is 1.5x its lowest
COUNCILS = ["CHARLES STURT", "WEST TORRENS", "PORT ADELAIDE ENFIELD", "SALISBURY", "PLAYFORD", "ONKAPARINGA"]

# Suburbs the Valuer-General lists under more than one council: keep each once, under this council
HOME_COUNCIL = {"WEST BEACH": "WEST TORRENS", "DEVON PARK": "CHARLES STURT", "VALLEY VIEW": "PORT ADELAIDE ENFIELD",
                "WALKLEY HEIGHTS": "PORT ADELAIDE ENFIELD", "ELIZABETH VALE": "PLAYFORD"}
SKIP = {"GILLMAN", "DRY CREEK", "GEPPS CROSS", "WINGFIELD", "HINDMARSH"}  # mostly industrial, or too few homes

# Hand-checked details for the original ten suburbs: nearest petrol station and bedroom medians (property.com.au)
ORIG = {
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

# Insurance loadings (estimates): coastal and low-lying, floodplain, bushfire-prone, near the coast, near a river
LOAD = [
 (1.15, "coastal and low-lying", {"WEST BEACH","HENLEY BEACH","HENLEY BEACH SOUTH","TENNYSON","GRANGE","SEMAPHORE PARK","WEST LAKES SHORE","GLENELG NORTH",
        "NORTH HAVEN","LARGS BAY","LARGS NORTH","SEMAPHORE","SEMAPHORE SOUTH","TAPEROO","OSBORNE","PETERHEAD","EXETER","BIRKENHEAD","GLANVILLE"}),
 (1.10, "parts sit on a floodplain", {"LOCKLEYS","FULHAM","WEST LAKES","PORT ADELAIDE","ETHELTON","ALBERTON","QUEENSTOWN","ROSEWATER","OTTOWAY",
        "VIRGINIA","ANGLE VALE","SMITHFIELD PLAINS","BURTON","PARALOWIE"}),
 (1.10, "it's in a bushfire-prone area", {"COROMANDEL VALLEY","CHANDLERS HILL","ONKAPARINGA HILLS","CRAIGBURN FARM","MCLAREN FLAT","WILLUNGA",
        "OLD NOARLUNGA","ONE TREE HILL","HILLIER","GULFVIEW HEIGHTS","SALISBURY HEIGHTS","HILLBANK","FLAGSTAFF HILL","ABERFOYLE PARK","HAPPY VALLEY"}),
 (1.05, "it's near the coast", {"CHRISTIES BEACH","MOANA","PORT NOARLUNGA","PORT NOARLUNGA SOUTH","ALDINGA BEACH","SELLICKS BEACH","MASLIN BEACH","PORT WILLUNGA",
        "O'SULLIVAN BEACH","SEAFORD","HALLETT COVE"}),
 (1.05, "it's near the River Torrens or Patawalonga", {"FULHAM GARDENS","FLINDERS PARK","KIDMAN PARK","UNDERDALE","TORRENSVILLE","THEBARTON","ALLENBY GARDENS",
        "WEST HINDMARSH","BOWDEN","NOVAR GARDENS","KLEMZIG","WINDSOR GARDENS","DERNANCOURT","NORTHFIELD"}),
]
# Typical block size (m2), used only when the buyer enters a land size
LAND = {**{k: 450 for k in ["BROMPTON","RIDLEYTON","RENOWN PARK","OVINGHAM","CROYDON","WELLAND","THEBARTON","TORRENSVILLE","MILE END","HILTON","KESWICK",
                            "COWANDILLA","WEST HINDMARSH","KILKENNY","RICHMOND","MARLESTON","ANDREWS FARM","MUNNO PARA WEST","SEAFORD MEADOWS","SEAFORD HEIGHTS",
                            "NORTHGATE","OAKDEN"]},
        **{k: 400 for k in ["MAWSON LAKES","RIVERLEA PARK","BLAKEVIEW","EYRE"]},
        "BOWDEN": 250, "LIGHTSVIEW": 300, "LOCKLEYS": 650, "ROYAL PARK": 500, "HENDON": 500, "HENLEY BEACH": 500, "WEST BEACH": 550, "WOODVILLE WEST": 550,
        **{k: 1000 for k in ["ONE TREE HILL","CHANDLERS HILL","ONKAPARINGA HILLS","HILLIER","VIRGINIA","MCLAREN FLAT","COROMANDEL VALLEY","CRAIGBURN FARM"]},
        **{k: 800 for k in ["WILLUNGA","OLD NOARLUNGA","MCLAREN VALE","ANGLE VALE","HILLBANK","GULFVIEW HEIGHTS","SALISBURY HEIGHTS"]}}
COASTAL_LAND = 550

def title(n):
    t = " ".join(w.capitalize() for w in n.split()).replace("Mclaren", "McLaren")
    return re.sub(r"O'(\w)", lambda m: "O'" + m.group(1).upper(), t)

def main():
    # Suburb centre points: ABS ASGS 2021 Suburbs and Localities (CC BY 4.0), fetched by the "Fetch ABS suburb centres" job
    abs_pts = json.load(open(os.path.join(HERE, "abs_sal_sa.json")))
    # Suburbs created after the ABS 2021 boundaries: approximate centre points
    abs_pts.setdefault("RIVERLEA PARK", {"lat": -34.6458, "lng": 138.5103})
    abs_pts.setdefault("ONKAPARINGA HEIGHTS", {"lat": -35.1623, "lng": 138.5222})
    postcodes = json.load(open(os.path.join(HERE, "postcodes.json")))
    quarters, data = load()
    out, seen = [], set()
    for council in COUNCILS:
        for (c, n), q in sorted(data.items()):
            if c != council or n in SKIP or n in seen or HOME_COUNCIL.get(n, council) != council: continue
            sales, med = year(q)
            meds = [m for s, m in q if s]
            varies = len(meds) >= 3 and max(meds) / min(meds) >= VARY
            if varies and len(meds) >= 4:
                # Prices swing a lot between quarters (a few very large or very small sales): leave out the highest and lowest quarter
                keep = sorted((m, s) for s, m in q if s)[1:-1]
                med = round(sum(m * s for m, s in keep) / sum(s for _, s in keep) / 1000) * 1000
            if sales < MIN_SALES: continue
            seen.add(n)
            o = ORIG.get(n, {})
            pos = {**abs_pts[n], "pc": postcodes[n]}
            ins, note = next(((f, t) for f, t, s in LOAD if n in s), (1.00, "no major flood, fire or coastal loading"))
            land = LAND.get(n, COASTAL_LAND if ins == 1.15 else 600)
            cname = title(council)
            d = dict(id=o.get("id") or re.sub(r"[^a-z0-9]+", "", n.lower()), name=title(n), council=cname, median=med, sales=sales,
                     lat=round(pos["lat"], 6), lng=round(pos["lng"], 6), postcode=pos["pc"], insFactor=ins, insNote=note,
                     petrol=o.get("petrol", 2.388), station=o.get("station", "Adelaide average price"), typLand=land)
            if varies: d["varies"] = [min(meds), max(meds)]
            if o: d["salesMedian"] = o["salesMedian"]; d["bed"] = {str(i + 1): v for i, v in enumerate(o["bed"])}
            if n == "FULHAM": d["id"] = "fulham-west"  # "fulham" is Fulham Gardens, kept for saved clients
            if any(x["id"] == d["id"] for x in out): d["id"] += "-" + cname.split()[0].lower()
            out.append(d)
    out.sort(key=lambda d: (COUNCILS.index(d["council"].upper()), d["name"]))
    js = "  const SUBURBS = " + json.dumps(out, separators=(",", ":")).replace('},{', '},\n    {') + ".map(s => ({ ...s, region: \"City of \" + s.council }));"
    open(os.path.join(HERE, "suburbs.js"), "w").write(js)
    json.dump({"quarters": quarters, "count": len(out)}, open(os.path.join(HERE, "suburbs_meta.json"), "w"))
    print(len(out), "suburbs,", quarters[0], "to", quarters[-1])

if __name__ == "__main__":
    main()

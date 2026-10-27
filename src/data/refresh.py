"""Regenerate suburb prices from raw/ and put them into src/artifact.html (the SUBURBS line and the price dates)."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); APP = os.path.join(HERE, "..", "artifact.html")
subprocess.run([sys.executable, os.path.join(HERE, "gen.py")], check=True)
new = open(os.path.join(HERE, "suburbs.js")).read(); meta = json.load(open(os.path.join(HERE, "suburbs_meta.json")))
s = open(APP).read()
m = re.search(r'  const SUBURBS = \[.*?\]\.map\(s => \(\{ \.\.\.s, region: "City of " \+ s\.council \}\)\);', s, re.S)
s = s[:m.start()] + new + s[m.end():]
first, last = meta["quarters"][0], meta["quarters"][-1]
months = {"1": "March", "2": "June", "3": "September", "4": "December"}
q, y = last[1], last.split()[1]
s = re.sub(r"(\d+) Adelaide suburbs across six councils", f"{meta['count']} Adelaide suburbs across six councils", s)
s = re.sub(r"in \d+ suburbs, how much", f"in {meta['count']} suburbs, how much", s)
s = re.sub(r'placeholder="Search \d+ suburbs', f'placeholder="Search {meta["count"]} suburbs', s)
s = re.sub(r"12 months to (March|June|September|December) 20\d\d", f"12 months to {months[q]} {y}", s)
s = re.sub(r"sales to (March|June|September|December) 20\d\d, SA Valuer-General", f"sales to {months[q]} {y}, SA Valuer-General", s)
s = re.sub(r"Valuer-General sales to (March|June|September|December) 20\d\d", f"Valuer-General sales to {months[q]} {y}", s)
s = re.sub(r"Q[1-4] 20\d\d to Q[1-4] 20\d\d", f"{first} to {last}", s)
open(APP, "w").write(s)
print("Updated app:", meta)

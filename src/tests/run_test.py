"""Upload the fake statements through the prototype page and compare its figures with the truth."""
import json, sys
from playwright.sync_api import sync_playwright

truth = json.load(open("truth.json"))
files = ["everyday_account_CBA.csv", "credit_card_NAB.csv", "savings_account_Westpac.csv"]

with sync_playwright() as pw:
    b = pw.chromium.launch()
    p = b.new_page(viewport={"width": 1280, "height": 1000})
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto("file:///home/claude/suburb-fit/index.html")
    p.wait_for_timeout(600)
    p.click('#landExample')     # past the front page
    p.click('#toggleEntries')   # and open all the entries so the tables are visible
    p.set_input_files("#file", files)
    p.wait_for_timeout(800)
    status = p.inner_text("#importStatus")
    hint = p.inner_text("#incomeHint")
    cats = p.evaluate("""() => {
      const out = {};
      document.querySelectorAll('#expBody tr').forEach(tr => {
        const id = tr.querySelector('input').id.replace('amt-','');
        out[id] = parseFloat(tr.querySelector('td.mo').innerText.replace(/[^0-9.\\-]/g,'')) || 0;
      });
      return out;
    }""")
    merch = p.evaluate("""() => [...document.querySelectorAll('#merchBody tr')].map(tr => [tr.cells[0].innerText, tr.cells[1].innerText, tr.querySelector('select').value])""")
    total = p.inner_text("#expTotal")
    if len(sys.argv) > 1:
        p.set_viewport_size({"width": 1280, "height": 2400})
        p.evaluate("document.getElementById('review').open = true")
        p.wait_for_timeout(200)
        p.screenshot(path=sys.argv[1], full_page=False)
    b.close()

print("STATUS:", status)
print("INCOME HINT:", hint)
print("TOTAL:", total, " truth:", truth["_total_spend_per_month"])
print(f"{'category':<14}{'tool':>10}{'truth':>10}{'diff':>10}")
keys = sorted(set(cats) | {k for k in truth if not k.startswith('_')})
bad = 0
for k in keys:
    t, c = truth.get(k, 0), cats.get(k, 0)
    flag = "  <--" if abs(c - t) > max(5, 0.05 * t) else ""
    bad += bool(flag)
    if t or c:
        print(f"{k:<14}{c:>10.0f}{t:>10.0f}{c - t:>10.0f}{flag}")
print("categories off by >5%:", bad)
print("\nPAYEES:")
for m in merch:
    print("  ", m)
print("errors:", errs)

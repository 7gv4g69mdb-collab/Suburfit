"""Generate 8 months (Feb-Sep 2026) of fake bank statements for a made-up couple,
in three different Australian bank CSV layouts, plus the true monthly figures per category."""
import csv, json, random
from datetime import date, timedelta
from collections import defaultdict

random.seed(42)
START, END = date(2026, 2, 1), date(2026, 9, 30)
truth = defaultdict(float)      # category -> total real spending
income_total = 0.0

everyday, card, savings = [], [], []   # (date, desc, amount) ; negative = money out
bal = {"everyday": 4200.0, "card": -850.0, "savings": 18500.0}

def spend(acct, d, desc, amt, cat):
    acct.append((d, desc, -round(amt, 2)))
    if cat:
        truth[cat] += round(amt, 2)

def credit(acct, d, desc, amt):
    acct.append((d, desc, round(amt, 2)))

d = START
fortnight_anchor = date(2026, 2, 5)
card_month_spend = defaultdict(float)
while d <= END:
    dow, dom, mon = d.weekday(), d.day, d.month   # Mon=0
    # ---- Income ----
    if (d - fortnight_anchor).days % 14 == 0 and d >= fortnight_anchor:
        credit(everyday, d, "DIRECT CREDIT 402211 ACME LOGISTICS PAYROLL", 3180.00); income_total += 3180
    if dom == 15:
        credit(everyday, d, "SALARY SA HEALTH NET PAY", 4950.00); income_total += 4950
    # ---- Everyday account ----
    if dow == 3:
        spend(everyday, d, "RENT HARCOURTS GRANGE REF 7781", 590, "rent")
    if dom == 3:
        spend(everyday, d, "TELSTRA CORPORATION BPAY", 89, "phone")
    if dom == 9:
        spend(everyday, d, "MEDIBANK PRIVATE LTD DD 33190", 268.40, "healthins")
    if dom == 11:
        spend(everyday, d, "AAMI INSURANCE DD CAR POLICY", 104.55, "carins")
    if dom == 12:
        spend(everyday, d, "YOUI CONTENTS INSURANCE", 31.20, "homeins")
    if dom == 14:
        spend(everyday, d, "PLENTI CAR LOAN REPAYMENT", 486, "debt")
    if dom == 20:
        spend(everyday, d, "JETTS FITNESS SEATON", 69.80, "entertainment")
    if dom == 1:
        spend(everyday, d, "TRANSFER TO XX5521 SAVINGS", 1000, None)          # own account
        credit(savings, d, "TRANSFER FROM XX8834 EVERYDAY", 1000)
    if dom == 25 and mon % 2 == 0:
        spend(everyday, d, "AFTERPAY AUSTRALIA PTY", round(random.uniform(60, 140), 2), "debt")
    if dom == 6 and mon in (3, 6, 9):
        spend(everyday, d, "AGL SALES PTY LTD ELECTRICITY", round(random.uniform(420, 610), 2), "power")
    if dom == 18 and mon in (2, 5, 8):
        spend(everyday, d, "ORIGIN ENERGY GAS BPAY", round(random.uniform(150, 260), 2), "gas")
    if dom == 22 and mon in (3, 6, 9):
        spend(everyday, d, "SA WATER CORPORATION BPAY", round(random.uniform(95, 135), 2), "water")
    if dom == 8 and mon == 4:
        spend(everyday, d, "SERVICE SA REGO RENEWAL", 1012.00, "car")
    if dom == 17 and mon in (3, 8):
        spend(everyday, d, "ULTRA TUNE WOODVILLE SERVICE", round(random.uniform(290, 420), 2), "car")
    if dow == 5 and random.random() < 0.25:
        spend(everyday, d, "ATM WITHDRAWAL CBA SEATON", 100, "other")
    if dom == 27 and random.random() < 0.6:
        spend(everyday, d, "OSKO PAYMENT TO S NGUYEN BIRTHDAY GIFT", 50, "other")
    if dom == 28 and random.random() < 0.5:
        credit(everyday, d, "DIRECT CREDIT M PATEL DINNER SPLIT", 45)        # friend paying back, not income
    # ---- Credit card (most day-to-day spending) ----
    if dow == 5:
        spend(card, d, "WOOLWORTHS 3342 FINDON SA", round(random.uniform(145, 215), 2), "groceries")
    if dow == 2:
        spend(card, d, "COLES 0821 WEST LAKES", round(random.uniform(40, 90), 2), "groceries")
    if dow == 0 and random.random() < 0.5:
        spend(card, d, "ALDI STORES SEATON", round(random.uniform(30, 70), 2), "groceries")
    if dow in (1, 4):
        spend(card, d, "BP HENLEY BEACH RD", round(random.uniform(50, 78), 2), "fuel")
    if dow == 4 and random.random() < 0.7:
        spend(card, d, "UBER *EATS HELP.UBER.COM", round(random.uniform(30, 62), 2), "dining")
    if dow == 6 and random.random() < 0.6:
        spend(card, d, "CAFE BRUNELLO GRANGE", round(random.uniform(16, 38), 2), "dining")
    if dom == 5:
        spend(card, d, "NETFLIX.COM MELBOURNE", 18.99, "entertainment")
    if dom == 7:
        spend(card, d, "SPOTIFY P1A2B3C SYDNEY", 13.99, "entertainment")
    if dom == 21 and random.random() < 0.7:
        spend(card, d, "KMART 1123 WEST LAKES", round(random.uniform(40, 120), 2), "shopping")
    if dom == 26 and random.random() < 0.5:
        spend(card, d, "BUNNINGS 6610 MILE END", round(random.uniform(35, 110), 2), "shopping")
    if dom == 13 and random.random() < 0.5:
        spend(card, d, "TERRY WHITE CHEMMART FINDON", round(random.uniform(20, 55), 2), "health")
    if dom == 2 and mon == 5:
        spend(card, d, "SPECSAVERS WEST LAKES", 289.00, "health")
    if dom == 10 and mon == 6:
        spend(card, d, "JB HI-FI ADELAIDE CITY", 1899.00, "shopping")          # one-off TV
    if dom == 24 and mon == 6:
        credit(card, d, "KMART 1123 WEST LAKES REFUND", 45.00)                 # refund
        truth["shopping"] -= 45.00
    if dom == 19 and random.random() < 0.5:
        spend(card, d, "HOTEL HENLEY BISTRO", round(random.uniform(70, 140), 2), "dining")
    d += timedelta(days=1)

# Credit card repaid in full from everyday account each month (an internal transfer, not spending)
for m in range(2, 10):
    pay_day = date(2026, m, 16)
    month_card = sum(-a for (dd, desc, a) in card if a < 0 and dd.month == m - 1) if m > 2 else 850.0
    month_card = round(month_card, 2)
    spend(everyday, pay_day, "PAYMENT TO ANZ CREDIT CARD 4564", month_card, None)
    credit(card, pay_day, "PAYMENT RECEIVED - THANK YOU", month_card)
# Savings interest
for m in range(2, 10):
    credit(savings, date(2026, m, 28), "INTEREST PAID", round(random.uniform(55, 70), 2))

def write_cba(rows, path):
    # Commonwealth Bank style: no header. Date, Amount, Description, Balance
    rows = sorted(rows, key=lambda r: r[0]); b = bal["everyday"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        for dd, desc, a in rows:
            b += a
            w.writerow([dd.strftime("%d/%m/%Y"), f"{a:+.2f}", desc, f"{b:+.2f}"])

def write_nab(rows, path):
    # NAB style with header; dates like 05 Feb 26
    rows = sorted(rows, key=lambda r: r[0]); b = bal["card"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Amount", "Account Number", "", "Transaction Type", "Transaction Details", "Balance", "Category", "Merchant Name"])
        for dd, desc, a in rows:
            b += a
            ttype = "CREDIT CARD PURCHASE" if a < 0 else "PAYMENT"
            w.writerow([dd.strftime("%d %b %y"), f"{a:.2f}", "4564-XXXX-XXXX-2231", "", ttype, desc, f"{b:.2f}", "", desc.split(" ")[0].title()])

def write_westpac(rows, path):
    # Westpac style: separate Debit Amount / Credit Amount columns
    rows = sorted(rows, key=lambda r: r[0]); b = bal["savings"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Bank Account", "Date", "Narrative", "Debit Amount", "Credit Amount", "Balance", "Categories", "Serial"])
        for dd, desc, a in rows:
            b += a
            w.writerow(["732-156 445521", dd.strftime("%d/%m/%Y"), desc, f"{-a:.2f}" if a < 0 else "", f"{a:.2f}" if a > 0 else "", f"{b:.2f}", "DEP" if a > 0 else "PAYMENT", ""])

write_cba(everyday, "everyday_account_CBA.csv")
write_nab(card, "credit_card_NAB.csv")
write_westpac(savings, "savings_account_Westpac.csv")

all_dates = [r[0] for r in everyday + card + savings]
months = ((max(all_dates) - min(all_dates)).days) / 30.4375
out = {k: round(v / months, 2) for k, v in truth.items()}
out["_income_per_month"] = round(income_total / months, 2)
out["_months"] = round(months, 2)
out["_total_spend_per_month"] = round(sum(truth.values()) / months, 2)
json.dump(out, open("truth.json", "w"), indent=2)
print(json.dumps(out, indent=2))
print("rows:", len(everyday), len(card), len(savings))

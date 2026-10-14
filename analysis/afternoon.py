"""Afternoon (12:00+) departures: who flies them, since when, how often, what they cost, and
whether the routes carrying them pay. Writes tables/afternoon_inventory.csv and
tables/afternoon_monthly.csv. Revenue can't be split AM/PM (transactions carry route + purchase
date, not flight time), so route-level contribution is the test.
"""
import collections
import csv
import sqlite3
import statistics
from pathlib import Path

HERE = Path(__file__).parent
db = sqlite3.connect(HERE / "airline_analysis.sqlite")
PRE = ("2024-09", "2025-02")  # before the spring-2025 schedule change
NEW = {"YOW-YUL", "YUL-YOW", "YXU-YYZ", "YYZ-YXU", "YQM-YHZ", "YHZ-YQM"}
PEAK = {"06", "07", "08", "12"}

fl = collections.defaultdict(list)  # route -> [(month, period, hhmm, cents)]
for date, month, period, route, cents in db.execute(
        "select date, month, period, route, amount_cents from cost_events where category_count = 4"):
    fl[route].append((month, period, date[11:16], cents))
rev, tix = collections.Counter(), collections.Counter()
for route, period, ttype, cents in db.execute("select route, period, type, amount_cents from transactions"):
    rev[route, period] += cents
    tix[route, period] += ttype == "Ticket"

pm = lambda t: t >= "12:00"
rows, monthly = [], []
for route, f in sorted(fl.items()):
    pm_times = sorted({t for _, _, t, _ in f if pm(t)})
    if not pm_times:
        continue
    pre_pm = {t for m, _, t, _ in f if pm(t) and PRE[0] <= m <= PRE[1]}
    # ponytail: <100 flights/yr = peak-day extra (YVR-YYC flies 17:20 twice each July), not a rotation
    added = [t for t in pm_times if t not in pre_pm and sum(x[2] == t and x[1] == 2 for x in f) >= 100]
    cls = ("new market" if route in NEW else "2025 added rotation" if added and not pre_pm
           else "legacy + 2025 added" if added else "legacy flex")
    p2 = [x for x in f if x[1] == 2]
    by_month = collections.Counter(m for m, _, t, _ in p2 if pm(t))
    months = sorted({m for m, *_ in p2})
    counts = [by_month[m] for m in months]
    am_cost = [c for _, _, t, c in p2 if not pm(t)]
    pm_cost = [c for _, _, t, c in p2 if pm(t)]
    n_pm = len(pm_cost)
    rows.append(dict(
        route=route, cls=cls, pm_times=" ".join(pm_times), added_times=" ".join(added),
        p2_flights=len(p2), p2_pm_flights=n_pm, pm_share=round(n_pm / len(p2), 3),
        peak_month_share=round(sum(by_month[m] for m in months if m[5:] in PEAK) / n_pm, 2),
        monthly_cv=round(statistics.pstdev(counts) / statistics.mean(counts), 2),
        am_cost_per_flight=round(statistics.mean(am_cost) / 100),
        pm_cost_per_flight=round(statistics.mean(pm_cost) / 100),
        pm_cost_musd=round(sum(pm_cost) / 1e8, 2),
        p2_contribution_musd=round((rev[route, 2] - sum(c for *_, c in p2)) / 1e8, 2),
        tickets_per_flight_p1=round(tix[route, 1] / sum(x[1] == 1 for x in f), 1),
        tickets_per_flight_p2=round(tix[route, 2] / len(p2), 1)))
    all_pm = collections.Counter(m for m, _, t, _ in f if pm(t))
    all_n = collections.Counter(m for m, *_ in f)
    monthly += [dict(route=route, cls=cls, month=m, pm_flights=all_pm[m], flights=all_n[m]) for m in sorted(all_n)]

for name, data in (("afternoon_inventory", rows), ("afternoon_monthly", monthly)):
    with open(HERE / "tables" / f"{name}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0]))
        w.writeheader()
        w.writerows(data)

by_cls = collections.defaultdict(list)
for r in rows:
    by_cls[r["cls"]].append(r)
print(f"{'class':22} dirs  PM flts  PM cost $M  contrib $M  peak-share  CV   tix/flt P1->P2")
for cls, rs in by_cls.items():
    n = sum(r["p2_pm_flights"] for r in rs)
    print(f"{cls:22} {len(rs):4} {n:8} {sum(r['pm_cost_musd'] for r in rs):11.2f} "
          f"{sum(r['p2_contribution_musd'] for r in rs):11.2f} "
          f"{sum(r['peak_month_share'] * r['p2_pm_flights'] for r in rs) / n:11.2f} "
          f"{statistics.mean(r['monthly_cv'] for r in rs):5.2f} "
          f"{sum(tix[r['route'], 1] for r in rs) / sum(sum(x[1] == 1 for x in fl[r['route']]) for r in rs):6.1f} -> "
          f"{sum(tix[r['route'], 2] for r in rs) / sum(r['p2_flights'] for r in rs):.1f}")

# chart: afternoon share of each class's monthly flights
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
series = collections.defaultdict(collections.Counter)
tot = collections.defaultdict(collections.Counter)
for r in monthly:
    series[r["cls"]][r["month"]] += r["pm_flights"]
    tot[r["cls"]][r["month"]] += r["flights"]
ms = sorted({r["month"] for r in monthly})
fig, ax = plt.subplots(figsize=(10, 4.5))
for cls in ("2025 added rotation", "legacy + 2025 added", "new market", "legacy flex"):
    ax.plot(ms, [100 * series[cls][m] / tot[cls][m] if tot[cls][m] else None for m in ms], marker="o", ms=3, label=cls)
ax.axvline(ms.index("2025-03"), color="grey", ls="--", lw=1)
ax.set_xticks(range(0, len(ms), 2), ms[::2], rotation=35, ha="right")
ax.set_ylabel("Afternoon share of flights, %")
ax.set_title("Legacy afternoon flights are added on peak days; the 2025 adds shadow every morning flight")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(HERE / "charts" / "11_afternoon_flights.png", dpi=200)

# self-check: every PM flight is classified exactly once, and the 2025 adds are the 10 trunk directions
assert sum(r["p2_pm_flights"] for r in rows) == sum(1 for f in fl.values() for x in f if x[1] == 2 and pm(x[2]))
assert {r["route"] for r in rows if "2025" in r["cls"]} == {
    "YUL-YVR", "YVR-YUL", "YHZ-YYZ", "YYZ-YHZ", "YUL-YYZ", "YYZ-YUL", "YOW-YYZ", "YYZ-YOW", "YHZ-YUL", "YUL-YHZ"}

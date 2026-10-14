"""Reproduce cost-event and gate-charge analyses from the cleaned source CSVs.

Run from any directory: python3 analysis/costs_gates.py
All money is parsed and aggregated in integer cents. Output tables live beside this
script in analysis/tables. Period-to-gate-year mapping is illustrative only.
"""

from collections import Counter, defaultdict
from csv import DictReader, DictWriter
from datetime import datetime
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "tables"
OUT.mkdir(exist_ok=True)
CATEGORIES = ("Crew", "Food", "Fuel", "Maintenance")
PERIODS = {"2024-2025": "P1", "2025-2026": "P2"}


def rows(name):
    with (ROOT / name).open(newline="", encoding="utf-8-sig") as f:
        return list(DictReader(f))


def cents(s):
    s = s.replace(",", "").replace("$", "").strip()
    assert re.fullmatch(r"-?\d+(?:\.\d{1,2})?", s), s
    sign = -1 if s.startswith("-") else 1
    s = s.lstrip("-")
    whole, _, frac = s.partition(".")
    return sign * (int(whole) * 100 + int(frac.ljust(2, "0")))


def money(v):
    sign = "-" if v < 0 else ""
    v = abs(v)
    return f"{sign}{v // 100}.{v % 100:02d}"


def ratio(num, den):
    return round(num / den, 4) if den else ""


def write(name, data, fields):
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = DictWriter(f, fields)
        w.writeheader()
        w.writerows(data)


costs = rows("costs.csv")
events = defaultdict(dict)
cost_ids = set()
route_city = defaultdict(set)
for row in costs:
    assert row["Cost_ID"] not in cost_ids, row["Cost_ID"]
    cost_ids.add(row["Cost_ID"])
    dt = datetime.strptime(row["Cost_Date"], "%Y-%m-%d %H:%M")
    assert row["Cost_Type"] in CATEGORIES
    assert re.fullmatch(r"[A-Z]{3}-[A-Z]{3}", row["Route_ID"])
    p = "P1" if datetime(2024, 9, 1) <= dt < datetime(2025, 9, 1) else "P2" if datetime(2025, 9, 1) <= dt < datetime(2026, 9, 1) else None
    assert p, dt
    key = (row["Cost_Date"], row["Route_ID"])
    assert row["Cost_Type"] not in events[key], key
    events[key][row["Cost_Type"]] = cents(row["Amount"])
    route_city[row["Route_ID"]].add((row["From"], row["To"]))

assert all(set(v) == set(CATEGORIES) for v in events.values())
assert all(len(v) == 1 for v in route_city.values())

period = defaultdict(lambda: {"events": 0, **{c: 0 for c in CATEGORIES}})
monthly = defaultdict(lambda: {"events": 0, **{c: 0 for c in CATEGORIES}})
route = defaultdict(lambda: {"events": 0, **{c: 0 for c in CATEGORIES}})
event_totals = []
for (date, code), cat in events.items():
    dt = datetime.strptime(date, "%Y-%m-%d %H:%M")
    p = "P1" if dt < datetime(2025, 9, 1) else "P2"
    total = sum(cat.values())
    event_totals.append((total, date, code, cat))
    for agg in (period[p], monthly[(p, date[:7])], route[(p, code)]):
        agg["events"] += 1
        for c in CATEGORIES:
            agg[c] += cat[c]

def summary(p, key=None, a=None):
    a = a if a is not None else period[p]
    n = a["events"]
    total = sum(a[c] for c in CATEGORIES)
    return {"period": p, **({"route_id": key} if key else {}), "cost_events": n,
            **{f"{c.lower()}_cost": money(a[c]) for c in CATEGORIES},
            "total_cost": money(total), "cost_per_event": money(round(total / n)) if n else ""}

cost_period = [summary(p) for p in ("P1", "P2")]
write("costs_period.csv", cost_period, list(cost_period[0]))
cost_month = []
for p, month in sorted(monthly):
    cost_month.append({"month": month, **summary(p, a=monthly[(p, month)])})
write("costs_monthly.csv", cost_month, list(cost_month[0]))

# Physical gate-year is the charge grain. Route rows are gate assignments, not
# independent annual charges. An unlisted route leaves the entire charge unallocated.
gate = defaultdict(lambda: {"cost": None, "routes": set()})
for row in rows("gates.csv"):
    assert row["Year"] in PERIODS
    k = (row["Year"], row["City"], row["Gate_Number"])
    val = cents(row["Annual_Gate_Cost"])
    if gate[k]["cost"] is None:
        gate[k]["cost"] = val
    assert gate[k]["cost"] == val, k
    if row["Route_ID"]:
        assert row["Route_ID"] in route_city
        assert row["City"] == next(iter(route_city[row["Route_ID"]]))[0], row
        gate[k]["routes"].add(row["Route_ID"])

allocated = defaultdict(int)
gate_detail = []
for (year, city, number), value in sorted(gate.items()):
    charge = value["cost"]
    routes = sorted(value["routes"])
    p = PERIODS[year]
    if routes:
        q, rem = divmod(charge, len(routes))
        for i, code in enumerate(routes):
            allocated[(p, code)] += q + (i < rem)
    gate_detail.append({"period": p, "gate_year": year, "city": city,
                        "gate_number": number, "listed_routes": len(routes),
                        "route_ids": ";".join(routes), "annual_charge": money(charge),
                        "unallocated_charge": money(charge if not routes else 0)})
write("gate_charges.csv", gate_detail, list(gate_detail[0]))

gate_period = []
for p in ("P1", "P2"):
    recs = [g for g in gate_detail if g["period"] == p]
    total = sum(cents(g["annual_charge"]) for g in recs)
    unalloc = sum(cents(g["unallocated_charge"]) for g in recs)
    assert sum(v for (pp, _), v in allocated.items() if pp == p) + unalloc == total
    gate_period.append({"period": p, "physical_gates": len(recs),
                        "listed_route_assignments": sum(g["listed_routes"] for g in recs),
                        "unassigned_gates": sum(g["listed_routes"] == 0 for g in recs),
                        "network_gate_charge": money(total),
                        "allocated_gate_charge": money(total - unalloc),
                        "unallocated_gate_charge": money(unalloc)})
write("gate_period.csv", gate_period, list(gate_period[0]))

route_rows = []
for p in ("P1", "P2"):
    for code in sorted(route_city):
        a = route[(p, code)]
        operating = sum(a[c] for c in CATEGORIES)
        gate_cost = allocated[(p, code)]
        route_rows.append({**summary(p, code, a), "allocated_gate_charge": money(gate_cost),
                           "cost_plus_allocated_gate": money(operating + gate_cost),
                           "allocation_per_event": money(round(gate_cost / a["events"])) if a["events"] else ""})
write("costs_routes.csv", route_rows, list(route_rows[0]))

change_rows = []
for code in sorted(route_city):
    a, b = route[("P1", code)], route[("P2", code)]
    n1, n2 = a["events"], b["events"]
    t1, t2 = (sum(x[c] for c in CATEGORIES) for x in (a, b))
    # Exact total-change decomposition in cents: event-count effect is rounded;
    # per-event amount is the residual and the two sum exactly to Δtotal.
    count_effect = round((n2 - n1) * t1 / n1) if n1 else 0
    change_rows.append({"route_id": code, "p1_events": n1, "p2_events": n2,
                        "event_change_pct": ratio(100 * (n2 - n1), n1),
                        "p1_cost": money(t1), "p2_cost": money(t2),
                        "cost_change": money(t2 - t1),
                        "cost_change_pct": ratio(100 * (t2 - t1), t1),
                        "p1_cost_per_event": money(round(t1 / n1)) if n1 else "",
                        "p2_cost_per_event": money(round(t2 / n2)) if n2 else "",
                        "per_event_change_pct": ratio(100 * (t2 / n2 - t1 / n1), t1 / n1) if n1 and n2 else "",
                        "event_count_effect": money(count_effect),
                        "cost_per_event_effect": money(t2 - t1 - count_effect),
                        "gate_change": money(allocated[("P2", code)] - allocated[("P1", code)])})
write("costs_route_changes.csv", change_rows, list(change_rows[0]))

decomp = []
for c in (*CATEGORIES, "Total"):
    t1 = sum(period["P1"][x] for x in CATEGORIES) if c == "Total" else period["P1"][c]
    t2 = sum(period["P2"][x] for x in CATEGORIES) if c == "Total" else period["P2"][c]
    n1, n2 = period["P1"]["events"], period["P2"]["events"]
    count_effect = round((n2 - n1) * t1 / n1)
    decomp.append({"category": c, "p1_cost": money(t1), "p2_cost": money(t2),
                   "change": money(t2 - t1), "change_pct": ratio(100 * (t2 - t1), t1),
                   "event_count_effect": money(count_effect),
                   "cost_per_event_effect": money(t2 - t1 - count_effect),
                   "p1_per_event": money(round(t1 / n1)),
                   "p2_per_event": money(round(t2 / n2))})
write("costs_decomposition.csv", decomp, list(decomp[0]))

anomaly = []
for total, date, code, cat in sorted(event_totals, reverse=True)[:20]:
    anomaly.append({"timestamp": date, "route_id": code, "total_cost": money(total),
                    **{c.lower(): money(cat[c]) for c in CATEGORIES}})
write("costs_top_events.csv", anomaly, list(anomaly[0]))

print(f"Cost rows={len(costs)}; complete events={len(events)}; routes={len(route_city)}")
print("Period totals:", cost_period)
print("Gate period:", gate_period)
print("Decomposition:", decomp)
print("Monthly cost event range:", min(x["cost_events"] for x in cost_month), max(x["cost_events"] for x in cost_month))

"""Size the four strategic alternatives on one consistent FY25-26 basis.

Contribution = revenue - (fuel + crew + maintenance + food), before gates.
Low case = revenue on removed flights is lost in proportion (0% recapture);
high case = it moves onto the remaining flights (100% recapture). Exits lose
their own revenue plus the other leg of any hub connection that uses them.
Writes tables/alternatives_matrix.csv.
"""
import collections
import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
db = sqlite3.connect(HERE / "airline_analysis.sqlite")

TRUNK = {"YUL-YVR", "YVR-YUL", "YHZ-YYZ", "YYZ-YHZ", "YUL-YYZ", "YYZ-YUL",
         "YOW-YYZ", "YYZ-YOW", "YHZ-YUL", "YUL-YHZ"}
MTL_YVR = {"YUL-YVR", "YVR-YUL"}
NEW = {"YOW-YUL", "YUL-YOW", "YXU-YYZ", "YYZ-YXU", "YQM-YHZ", "YHZ-YQM"}
ALL_SEASON_LOSS = {  # negative contribution in all four FY25-26 seasons
    "YEG-YZF", "YHZ-YQM", "YHZ-YUL", "YHZ-YYZ", "YOW-YUL", "YOW-YYZ", "YQM-YHZ",
    "YUL-YHZ", "YUL-YOW", "YUL-YVR", "YUL-YYZ", "YVR-YUL", "YVR-YXS", "YXS-YVR",
    "YXU-YYZ", "YXX-YYC", "YYC-YXX", "YYZ-YHZ", "YYZ-YOW", "YYZ-YUL", "YYZ-YXU", "YZF-YEG"}
PRE = {"2024-09", "2024-10", "2024-11", "2024-12", "2025-01", "2025-02"}

# ---- flights (cost events) and revenue, FY25-26
flights = collections.defaultdict(list)          # route -> [(month, hh:mm, cost_cents)]
pre_times = collections.defaultdict(set)         # route -> departure clock times flown Sep24-Feb25
for date, month, period, route, cents in db.execute(
        "select date, month, period, route, amount_cents from cost_events"):
    if month in PRE:
        pre_times[route].add(date[11:16])
    if period == 2:
        flights[route].append((month, date[11:16], cents))
rev = collections.Counter()
legs = collections.defaultdict(lambda: collections.Counter())  # booking -> route -> cents
ticket_routes = collections.defaultdict(set)
for booking, route, month, ttype, cents in db.execute(
        "select booking_id, route, month, type, amount_cents from transactions where period = 2"):
    rev[route] += cents
    legs[booking][route] += cents
    if ttype == "Ticket":
        ticket_routes[booking].add(route)

cost = {r: sum(c for *_, c in f) for r, f in flights.items()}
base_contrib = sum(rev.values()) - sum(cost.values())


def connecting_loss(exited):
    """Other-leg revenue of hub connections that use an exited route."""
    lost = 0
    for booking, routes in ticket_routes.items():
        if len(routes) == 2 and routes & exited and not routes <= exited:
            a, b = (r.split("-") for r in routes)
            if a != b[::-1]:  # not a return trip
                lost += sum(legs[booking][r] for r in routes - exited)
    return lost


def trim(routes, keep):
    """Remove flights where keep(month, time) is False. Returns (cost_saved, rev_at_risk, n_removed).
    Revenue at risk = removed share of the route's flights."""
    saved = risk = n = 0
    for r in routes:
        gone = [c for m, t, c in flights[r] if not keep(r, m, t)]
        saved += sum(gone)
        risk += rev[r] * len(gone) / len(flights[r])
        n += len(gone)
    return saved, risk, n


def exit_(routes):
    lost_conn = connecting_loss(set(routes))
    return (sum(cost[r] for r in routes), sum(rev[r] for r in routes) + lost_conn,
            sum(len(flights[r]) for r in routes), lost_conn)


rows = []


def add(alt, component, saved, at_risk, n, recapture=(0, 0, 0), conn=0):
    """recapture = share of at-risk revenue kept in the (low, central, high) case."""
    lo, mid, hi = ((saved - at_risk * (1 - rc)) / 1e8 for rc in recapture)
    rows.append(dict(alternative=alt, component=component, flights_removed=n, low_musd=round(lo, 2),
                     central_musd=round(mid, 2), high_musd=round(hi, 2),
                     connecting_revenue_lost_musd=round(conn / 1e8, 2)))


RS, SH = "Right-Size & Recover", "Shrink to Core"
# Trunk central = full recapture: doubling these flights added ~0 revenue (+3.1% vs +4.0% on unchanged routes).
s, r, n = trim(TRUNK - MTL_YVR, lambda rt, m, t: t in pre_times[rt])
add(RS, "Remove 2025 added rotations, 8 trunk directions", s, r, n, (0, 1, 1))
s, r, n, conn = exit_(MTL_YVR)
add(RS, "Exit Montreal-Vancouver (0 connecting bookings)", s, r, n, conn=conn)
alt_half = collections.Counter()
half = lambda rt: (alt_half.update([rt]) or alt_half[rt]) % 2 == 1  # keep every other flight
s, r, n = trim(NEW, lambda rt, m, t: half(rt))
add(RS, "Halve frequency on 3 spring-2025 markets", s, r, n, (0, .5, 1))  # no pre-expansion history
# Winter halving on Whitehorse & St. John's dropped (team, 2026-10-15): ~$0.9M, hurts communities, rebook-first covers refunds.
s, r, n, conn = exit_(ALL_SEASON_LOSS)
add(SH, "Exit 22 directions negative in every season", s, r, n, conn=conn)

# Gate leases: the same rule for every option. Leases run Jan-Jan, so FY25-26 (Sep-Aug) = 4/12 of the
# calendar-2025 lease + 8/12 of calendar 2026, whose records are missing: each gate repeats its 2024->25
# % increase (Q5). Gives $10.096M for 2026 and $10.023M for FY25-26 (teammate repo agrees to the cent).
# Steady state (from the Jan 2027 renewal), a gate is released only when no remaining route departs from it.
gate_routes = collections.defaultdict(set)
gate_cost = {}  # (city, gate) -> {lease year: cents}; the file repeats a gate's cost on every route row
for city, gate, year, route, cents in db.execute("select city, gate, year, route, amount_cents from gates"):
    gate_routes[(city, gate)].add(route or "")
    gate_cost.setdefault((city, gate), {})[year] = cents
L25 = {g: c["2025-2026"] for g, c in gate_cost.items()}
L26 = {g: c["2025-2026"] ** 2 / c["2024-2025"] for g, c in gate_cost.items()}
GATES = (sum(L25.values()) * 4 / 12 + sum(L26.values()) * 8 / 12) / 100  # FY25-26 accrual, dollars
assert round(sum(L25.values())) == 987_770_000 and abs(GATES - 10_023_129) < 1, GATES


def gates_released(exited):
    return sum(c for g, c in L26.items() if "" not in gate_routes[g] and gate_routes[g] <= exited) / 1e8


# A. Fill the Planes: verified revenue-lever stack (low, central, ceiling), excluding ~$7.6M organic
# growth that every option gets. Ceiling assumes doubled connections and -10% fares at e=-1.5.
FILL = (2.5, 5.3, 30.1)
# Right-Size also carries the short-term revenue levers that only work once the schedule is fixed:
# trunk yield repair 0.3-1.8, St John's rebook-first 0.44-1.06, OTA->direct 0.15-0.8, hub connection
# marketing 0.66-2.6, community-route fares 0.36-1.2, all-in fare bundles 0.3-0.8 ($M; overlap, so
# the high end is not additive). Recapture is NOT a lever: B's trunk saving already assumes it.
RS_LEVERS = (2.2, 5.2, 8.3)
rows.append(dict(alternative=RS, component="Revenue recovery levers (short term)", flights_removed=0,
                 low_musd=RS_LEVERS[0], central_musd=RS_LEVERS[1], high_musd=RS_LEVERS[2],
                 connecting_revenue_lost_musd=0))

served = lambda removed: len({a for rt in flights if rt not in removed for a in rt.split("-")})
base, after = base_contrib / 1e8, base_contrib / 1e8 - GATES / 1e6
summary = []
for alt, removed, extra in (("Stay the Course", set(), (0, 0, 0)), ("Fill the Planes", set(), FILL),
                            (RS, MTL_YVR, None), (SH, ALL_SEASON_LOSS, None)):
    part = [x for x in rows if x["alternative"] == alt]
    gain = extra or tuple(sum(x[k] for x in part) for k in ("low_musd", "central_musd", "high_musd"))
    freed = gates_released(removed)
    summary.append(dict(alternative=alt, component="TOTAL", flights_removed=sum(x["flights_removed"] for x in part),
                        low_musd=round(gain[0], 2), central_musd=round(gain[1], 2), high_musd=round(gain[2], 2),
                        connecting_revenue_lost_musd=round(sum(x["connecting_revenue_lost_musd"] for x in part), 2),
                        airports_served=served(removed), gates_released_musd=round(freed, 2),
                        before_gates_central=round(base + gain[1], 2),
                        after_gates_low=round(after + freed + gain[0], 2),
                        after_gates_central=round(after + freed + gain[1], 2),
                        after_gates_high=round(after + freed + gain[2], 2)))
S = {x["alternative"]: x for x in summary}

# Recapture (on all trimmed flights) at which Right-Size matches Shrink after gates.
rs_at = lambda rc: (after + S[RS]["gates_released_musd"] + sum(x["low_musd"] + rc * (x["high_musd"] - x["low_musd"])
                    for x in rows if x["alternative"] == RS))
breakeven_rc = next((rc / 100 for rc in range(101) if rs_at(rc / 100) >= S[SH]["after_gates_central"]), 0.0)

# ---- decision matrix. Financial is linear in central after-gates result: Stay = 1, break-even = 5.
fin = lambda x: max(1, min(5, 1 + 4 * (x - after) / -after))
WEIGHTS = dict(financial=30, evidence=15, speed=10, communities=15, customers=15, employees=15)
SCORES = {  # judgment scores 1-5; anchors in slides/OUTLINE.md
    "Stay the Course":  dict(evidence=1, speed=1, communities=3, customers=3, employees=3),
    "Fill the Planes":  dict(evidence=2, speed=2, communities=3, customers=2, employees=3),
    RS:                 dict(evidence=5, speed=4, communities=4, customers=4, employees=3),
    SH:                 dict(evidence=3, speed=3, communities=1, customers=2, employees=1),
}
for alt, sc in SCORES.items():
    sc["financial"] = round(fin(S[alt]["after_gates_central"]), 2)


def total(alt, w_fin=WEIGHTS["financial"], fin_of=lambda a: SCORES[a]["financial"]):
    rest = 100 - WEIGHTS["financial"]
    return (w_fin * fin_of(alt) + sum((100 - w_fin) * WEIGHTS[k] / rest * v
            for k, v in SCORES[alt].items() if k != "financial")) / 100


# Financial weight at which Shrink overtakes Right-Size, if Right-Size only hits its 0%-recapture low case.
low_fin = {RS: fin(S[RS]["after_gates_low"]), SH: SCORES[SH]["financial"]}
flip = next((w for w in range(101) if total(SH, w, low_fin.get) > total(RS, w, low_fin.get)), None)

out = HERE / "tables" / "alternatives_matrix.csv"
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(summary[0]))
    w.writeheader()
    w.writerows(rows + summary)
with open(HERE / "tables" / "decision_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["criterion", "weight_pct", *SCORES])
    for k in WEIGHTS:
        w.writerow([k, WEIGHTS[k], *(SCORES[a][k] for a in SCORES)])
    w.writerow(["weighted_total", 100, *(round(total(a), 2) for a in SCORES)])

assert abs(base - -48.38) < 0.01, base  # reconciles to network_period
assert served(set()) == 20 and sum(WEIGHTS.values()) == 100
for x in rows + summary:
    print({k: v for k, v in x.items() if v not in ("", None)})
print({a: round(total(a), 2) for a in SCORES}, "| fin scores", {a: SCORES[a]["financial"] for a in SCORES})
print(f"Right-Size matches Shrink after gates at {breakeven_rc:.0%} recapture; "
      f"Shrink overtakes Right-Size (RS at 0% recapture) only if financial weight >= {flip}%")

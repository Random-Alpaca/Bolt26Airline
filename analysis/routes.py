"""Reproduce route contribution and trend tables from airline_analysis.sqlite.

Run from the repository root: python3 analysis/routes.py
Amounts in the SQLite database are integer cents; CSV outputs use dollars.
"""

from __future__ import annotations

import csv
import sqlite3
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DB = ROOT / "airline_analysis.sqlite"
TABLES = ROOT / "tables"
PERIODS = (1, 2)
COST_TYPES = ("Crew", "Food", "Fuel", "Maintenance")


def dollars(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    return f"{sign}{abs(cents) // 100}.{abs(cents) % 100:02d}"


def pct(numerator: int, denominator: int) -> str:
    return f"{100 * numerator / denominator:.2f}" if denominator else ""


def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
    TABLES.mkdir(exist_ok=True)
    with (TABLES / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def assert_periods(connection: sqlite3.Connection) -> None:
    for table in ("transactions", "costs"):
        periods = connection.execute(
            f"SELECT period, MIN(month), MAX(month), COUNT(*) FROM {table} GROUP BY period ORDER BY period"
        ).fetchall()
        if [p[0] for p in periods] != [1, 2]:
            raise ValueError(f"Unexpected {table} periods: {periods}")
        for period, first, last, _ in periods:
            expected = ("2024-09", "2025-08") if period == 1 else ("2025-09", "2026-08")
            if (first, last) != expected:
                raise ValueError(f"Unexpected {table} coverage: {periods}")


def load_rollups(connection: sqlite3.Connection):
    data = defaultdict(lambda: {"revenue": 0, "cost": 0, "tx": 0, "ticket_tx": 0,
                                "refund": 0, "cost_events": 0, **{t: 0 for t in COST_TYPES}})
    for period, route, revenue, tx, ticket_tx, refund in connection.execute("""
        SELECT period, route, SUM(amount_cents), COUNT(*),
               SUM(CASE WHEN type='Ticket' THEN 1 ELSE 0 END),
               SUM(CASE WHEN type='Refund' THEN amount_cents ELSE 0 END)
        FROM transactions GROUP BY period, route
    """):
        d = data[(period, route)]
        d.update(revenue=revenue, tx=tx, ticket_tx=ticket_tx, refund=refund)
    event_counts = defaultdict(set)
    observed_types = defaultdict(set)
    for period, route, cost_type, cost, events in connection.execute("""
        SELECT period, route, type, SUM(amount_cents), COUNT(*)
        FROM costs GROUP BY period, route, type
    """):
        d = data[(period, route)]
        if cost_type not in COST_TYPES:
            raise ValueError(f"Unexpected cost type: {cost_type}")
        d[cost_type] = cost
        d["cost"] += cost
        event_counts[(period, route)].add(events)
        observed_types[(period, route)].add(cost_type)
        if cost_type == "Crew":
            d["cost_events"] = events
    for (period, route), counts in event_counts.items():
        if (len(counts) != 1 or observed_types[(period, route)] != set(COST_TYPES)
                or not data[(period, route)]["cost_events"]):
            raise ValueError(f"Unbalanced cost categories for {period} {route}")
    return data


def main() -> None:
    if not DB.exists():
        raise FileNotFoundError(DB)
    connection = sqlite3.connect(DB)
    assert_periods(connection)
    data = load_rollups(connection)
    routes = sorted({route for _, route in data})
    period_rows = []
    for period in PERIODS:
        for route in routes:
            d = data.get((period, route))
            if d is None or (not d["tx"] and not d["cost_events"]):
                continue
            contribution = d["revenue"] - d["cost"]
            period_rows.append({
                "period": period, "route": route,
                "revenue": dollars(d["revenue"]), "cost": dollars(d["cost"]),
                "contribution_before_gates": dollars(contribution),
                "contribution_margin_pct": pct(contribution, d["revenue"]),
                "transaction_count": d["tx"], "ticket_transaction_count": d["ticket_tx"],
                "cost_event_count": d["cost_events"],
                "revenue_per_cost_event": dollars(round(d["revenue"] / d["cost_events"])) if d["cost_events"] else "",
                "cost_per_cost_event": dollars(round(d["cost"] / d["cost_events"])) if d["cost_events"] else "",
                **{f"{t.lower()}_cost": dollars(d[t]) for t in COST_TYPES},
                "refund_amount": dollars(d["refund"]),
            })
    write_csv("routes_period.csv", list(period_rows[0]), period_rows)

    growth_rows = []
    for route in routes:
        a = data.get((1, route)); b = data.get((2, route))
        # Presence is measured using transactions or cost events, rather than a zero net balance.
        exists1 = bool(a and (a["tx"] or a["cost_events"]))
        exists2 = bool(b and (b["tx"] or b["cost_events"]))
        status = "existing" if exists1 and exists2 else "new" if exists2 else "ceased"
        a = a or defaultdict(int); b = b or defaultdict(int)
        ca = a["revenue"] - a["cost"]; cb = b["revenue"] - b["cost"]
        growth_rows.append({
            "route": route, "status": status,
            "p1_revenue": dollars(a["revenue"]), "p2_revenue": dollars(b["revenue"]),
            "revenue_change": dollars(b["revenue"] - a["revenue"]),
            "revenue_growth_pct": pct(b["revenue"] - a["revenue"], a["revenue"]) if exists1 else "",
            "p1_cost": dollars(a["cost"]), "p2_cost": dollars(b["cost"]),
            "cost_change": dollars(b["cost"] - a["cost"]),
            "p1_contribution": dollars(ca), "p2_contribution": dollars(cb),
            "contribution_change": dollars(cb - ca),
            "p1_cost_events": a["cost_events"], "p2_cost_events": b["cost_events"],
            "cost_event_change": b["cost_events"] - a["cost_events"],
        })
    write_csv("routes_growth.csv", list(growth_rows[0]), growth_rows)

    direction_rows = []
    for period in PERIODS:
        for route in routes:
            origin, destination = route.split("-")
            reverse = f"{destination}-{origin}"
            if route >= reverse or (period, route) not in data or (period, reverse) not in data:
                continue
            a = data[(period, route)]; b = data[(period, reverse)]
            ac = a["revenue"] - a["cost"]; bc = b["revenue"] - b["cost"]
            direction_rows.append({
                "period": period, "market": "/".join(sorted((origin, destination))),
                "route_a": route, "route_b": reverse,
                "a_revenue": dollars(a["revenue"]), "b_revenue": dollars(b["revenue"]),
                "a_cost": dollars(a["cost"]), "b_cost": dollars(b["cost"]),
                "a_contribution": dollars(ac), "b_contribution": dollars(bc),
                "a_minus_b_contribution": dollars(ac - bc),
                "a_margin_pct": pct(ac, a["revenue"]), "b_margin_pct": pct(bc, b["revenue"]),
                "a_cost_events": a["cost_events"], "b_cost_events": b["cost_events"],
            })
    write_csv("routes_direction.csv", list(direction_rows[0]), direction_rows)

    monthly = defaultdict(lambda: {"revenue": 0, "cost": 0, "tx": 0, "cost_events": 0})
    for month, period, route, revenue, tx in connection.execute("""
        SELECT month, period, route, SUM(amount_cents), COUNT(*)
        FROM transactions GROUP BY month, period, route
    """):
        d = monthly[(month, period, route)]; d["revenue"] = revenue; d["tx"] = tx
    for month, period, route, cost, events in connection.execute("""
        SELECT month, period, route, SUM(amount_cents), COUNT(*) / 4
        FROM costs GROUP BY month, period, route
    """):
        d = monthly[(month, period, route)]; d["cost"] = cost; d["cost_events"] = events
    monthly_rows = []
    for (month, period, route), d in sorted(monthly.items()):
        monthly_rows.append({
            "month": month, "period": period, "route": route,
            "revenue": dollars(d["revenue"]), "cost": dollars(d["cost"]),
            "contribution_before_gates": dollars(d["revenue"] - d["cost"]),
            "transaction_count": d["tx"], "cost_event_count": d["cost_events"],
        })
    write_csv("routes_monthly.csv", list(monthly_rows[0]), monthly_rows)

    comparable_rows = []
    for route in routes:
        matched = []
        unmatched_p2 = []
        for (month, period, monthly_route), second in monthly.items():
            if period != 2 or monthly_route != route or not second["cost_events"]:
                continue
            prior_month = f"{int(month[:4]) - 1}{month[4:]}"
            first = monthly.get((prior_month, 1, route))
            if first and first["cost_events"]:
                matched.append((first, second))
            else:
                unmatched_p2.append(second)
        a_revenue = sum(a["revenue"] for a, _ in matched)
        b_revenue = sum(b["revenue"] for _, b in matched)
        a_cost = sum(a["cost"] for a, _ in matched)
        b_cost = sum(b["cost"] for _, b in matched)
        unmatched_revenue = sum(d["revenue"] for d in unmatched_p2)
        unmatched_cost = sum(d["cost"] for d in unmatched_p2)
        comparable_rows.append({
            "route": route, "matched_calendar_months": len(matched),
            "p1_matched_revenue": dollars(a_revenue),
            "p2_matched_revenue": dollars(b_revenue),
            "matched_revenue_change": dollars(b_revenue - a_revenue),
            "matched_revenue_growth_pct": pct(b_revenue - a_revenue, a_revenue),
            "p1_matched_cost": dollars(a_cost), "p2_matched_cost": dollars(b_cost),
            "matched_cost_change": dollars(b_cost - a_cost),
            "p1_matched_contribution": dollars(a_revenue - a_cost),
            "p2_matched_contribution": dollars(b_revenue - b_cost),
            "matched_contribution_change": dollars((b_revenue - b_cost) - (a_revenue - a_cost)),
            "p2_unmatched_months": len(unmatched_p2),
            "p2_unmatched_revenue": dollars(unmatched_revenue),
            "p2_unmatched_cost": dollars(unmatched_cost),
            "p2_unmatched_contribution": dollars(unmatched_revenue - unmatched_cost),
        })
    write_csv("routes_comparable_months.csv", list(comparable_rows[0]), comparable_rows)
    connection.close()


if __name__ == "__main__":
    main()

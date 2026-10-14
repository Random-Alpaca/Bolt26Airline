"""Build monthly route revenue and compare ambiguous date interpretations.

Outputs an Excel workbook with current, all M/D/Y, and all D/M/Y route sheets,
plus monthly impact sheets. TX9900561's confirmed September date is kept in
every scenario. Requires openpyxl for the Excel workbook.
"""

import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

from TransAnalysis import TRANSACTION_TYPES


ROOT = Path(__file__).parent
SOURCE = ROOT / "transactions.csv"
DECISIONS = ROOT / "transaction_date_decisions.csv"
WORKBOOK = ROOT / "monthly_revenue_scenarios.xlsx"
CURRENT_CSV = ROOT / "monthly_route_revenue.csv"
IMPACT_CSV = ROOT / "monthly_revenue_impact.csv"
TYPE_NAMES = {name.casefold(): name for name in TRANSACTION_TYPES}
ZERO = Decimal("0.00")


def load_decisions():
    with DECISIONS.open(newline="", encoding="utf-8-sig") as source:
        return {int(row["Excel_Row"]): row for row in csv.DictReader(source)}


def date_choices(value):
    """Return possible dates for an input date without guessing its order."""
    day = value.split(" ", 1)[0]
    if "-" in day:
        parsed = date.fromisoformat(day)
        return parsed, parsed
    parts = day.split("/")
    if len(parts[0]) == 4:  # YYYY/MM/DD
        parsed = date(*(int(part) for part in parts))
        return parsed, parsed
    first, second, year = map(int, parts)
    try:
        month_first = date(year, first, second)
    except ValueError:
        month_first = None
    try:
        day_first = date(year, second, first)
    except ValueError:
        day_first = None
    if month_first is None and day_first is None:
        raise ValueError(f"Invalid transaction date {value!r}")
    return month_first, day_first


def empty_categories():
    return {kind: ZERO for kind in TRANSACTION_TYPES}


def aggregate():
    decisions = load_decisions()
    scenarios = {
        "Current": defaultdict(empty_categories),
        "All MDY": defaultdict(empty_categories),
        "All DMY": defaultdict(empty_categories),
    }
    counts = {"transactions": 0, "ambiguous": 0, "id_resolved": 0,
              "fallback": 0, "ambiguous_amount": ZERO}

    with SOURCE.open(newline="", encoding="utf-8-sig") as source:
        for excel_row, row in enumerate(csv.DictReader(source), start=2):
            counts["transactions"] += 1
            raw_date = row["Transaction_Date"].strip()
            month_first, day_first = date_choices(raw_date)
            ambiguous = month_first is not None and day_first is not None and month_first != day_first
            if ambiguous:
                decision = decisions.get(excel_row)
                if decision is None or decision["Original_Date"] != raw_date:
                    raise ValueError(f"Missing date decision for CSV row {excel_row}")
                current = date.fromisoformat(decision["Converted_Date"][:10])
                if current not in (month_first, day_first):
                    raise ValueError(f"Date decision does not match CSV row {excel_row}")
                counts["ambiguous"] += 1
                if "from ID order" in decision["Interpretation"]:
                    counts["id_resolved"] += 1
                elif "fallback" in decision["Interpretation"]:
                    counts["fallback"] += 1
                else:
                    raise ValueError(f"Unexpected date decision at CSV row {excel_row}")
            else:
                current = month_first or day_first
            chosen_dates = {
                "Current": current,
                "All MDY": month_first or day_first,
                "All DMY": day_first or month_first,
            }

            route = row["Route_ID"].strip().upper()
            kind = TYPE_NAMES.get(row["Transaction_Type"].strip().casefold())
            if not route or kind is None:
                raise ValueError(f"Invalid route or transaction type at CSV row {excel_row}")
            amount = Decimal(row["Amount"].strip().replace("$", "").replace(",", ""))
            if ambiguous:
                counts["ambiguous_amount"] += abs(amount)
            for scenario, chosen in chosen_dates.items():
                month = f"{chosen.year:04d}-{chosen.month:02d}"
                scenarios[scenario][(month, route)][kind] += amount

    if counts["ambiguous"] != counts["id_resolved"] + counts["fallback"]:
        raise ValueError(f"Unexpected ambiguous date counts: {counts}")
    return scenarios, counts


def total(amounts):
    return sum(amounts.values(), ZERO) if amounts else ZERO


def route_rows(scenario):
    return [
        (month, route, *(amounts[kind] for kind in TRANSACTION_TYPES), total(amounts))
        for (month, route), amounts in sorted(scenario.items())
    ]


def impact_rows(scenarios):
    keys = sorted(set().union(*(scenario.keys() for scenario in scenarios.values())))
    rows = []
    for month, route in keys:
        current = total(scenarios["Current"].get((month, route)))
        mdy = total(scenarios["All MDY"].get((month, route)))
        dmy = total(scenarios["All DMY"].get((month, route)))
        rows.append((month, route, current, mdy, dmy, dmy - mdy, current - mdy))
    return rows


def monthly_impact_rows(route_impact):
    by_month = defaultdict(lambda: [ZERO, ZERO, ZERO])
    for month, _, current, mdy, dmy, _, _ in route_impact:
        amounts = by_month[month]
        amounts[0] += current
        amounts[1] += mdy
        amounts[2] += dmy
    return [
        (month, *amounts, amounts[2] - amounts[1], amounts[0] - amounts[1])
        for month, amounts in sorted(by_month.items())
    ]


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.writer(destination, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow(str(value) if isinstance(value, Decimal) else value for value in row)


def add_table(workbook, name, header, rows):
    from openpyxl.styles import Alignment, Font, PatternFill

    sheet = workbook.create_sheet(name)
    sheet.append(header)
    for row in rows:
        sheet.append([float(value) if isinstance(value, Decimal) else value for value in row])
    sheet.freeze_panes = "C2" if "Route" in header or "Route_ID" in header else "B2"
    sheet.auto_filter.ref = sheet.dimensions
    for cell in sheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.alignment = Alignment(wrap_text=True)
    sheet.row_dimensions[1].height = 30
    for column in sheet.columns:
        letter = column[0].column_letter
        label = str(column[0].value)
        sheet.column_dimensions[letter].width = max(13, min(22, len(label) + 3))
        if label not in ("Month", "Route_ID"):
            for cell in column[1:]:
                cell.number_format = '#,##0.00;[Red](#,##0.00)'
    return sheet


def write_workbook(scenarios, counts, route_impact, monthly_impact):
    from openpyxl import Workbook

    workbook = Workbook()
    summary = workbook.active
    summary.title = "Summary"
    summary.append(("Measure", "Value"))
    summary.append(("Transactions", counts["transactions"]))
    summary.append(("Ambiguous dates compared", counts["ambiguous"]))
    summary.append(("Resolved by transaction ID", counts["id_resolved"]))
    summary.append(("M/D/Y fallbacks", counts["fallback"]))
    summary.append(("Gross amount on ambiguous dates", float(counts["ambiguous_amount"])))
    biggest = max(monthly_impact, key=lambda row: abs(row[4]))
    summary.append(("Largest monthly D/M/Y minus M/D/Y difference", float(biggest[4])))
    summary.append(("Month of largest difference", biggest[0]))
    active_months = [row for row in monthly_impact if "2024-09" <= row[0] <= "2026-08"]
    biggest_active = max(active_months, key=lambda row: abs(row[4]))
    summary.append(("Largest difference within Sep 2024–Aug 2026", float(biggest_active[4])))
    summary.append(("Month of largest within-span difference", biggest_active[0]))
    outside = [row for row in monthly_impact if row not in active_months]
    summary.append(("All M/D/Y revenue outside Sep 2024–Aug 2026",
                    float(sum((row[2] for row in outside), ZERO))))
    summary.append(("All D/M/Y revenue outside Sep 2024–Aug 2026",
                    float(sum((row[3] for row in outside), ZERO))))
    summary.append(("Annual revenue difference across scenarios", 0))
    summary.append(("Confirmed TX9900561", "2024-09-04 in every scenario"))
    summary.append(("Date rule", "Current uses ID evidence; all M/D/Y and all D/M/Y are counterfactuals"))
    summary.column_dimensions["A"].width = 48
    summary.column_dimensions["B"].width = 65
    summary.freeze_panes = "A2"

    route_header = ("Month", "Route_ID", *TRANSACTION_TYPES, "Total_Revenue")
    for name, scenario in (("Current by Route", "Current"),
                           ("All MDY by Route", "All MDY"),
                           ("All DMY by Route", "All DMY")):
        add_table(workbook, name, route_header, route_rows(scenarios[scenario]))
    add_table(workbook, "Monthly Impact",
              ("Month", "Current_Revenue", "All_MDY_Revenue", "All_DMY_Revenue",
               "DMY_minus_MDY", "Current_minus_MDY"), monthly_impact)
    add_table(workbook, "Route Impact",
              ("Month", "Route_ID", "Current_Revenue", "All_MDY_Revenue",
               "All_DMY_Revenue", "DMY_minus_MDY", "Current_minus_MDY"), route_impact)
    workbook.save(WORKBOOK)


def main():
    scenarios, counts = aggregate()
    route_impact = impact_rows(scenarios)
    monthly_impact = monthly_impact_rows(route_impact)
    write_csv(CURRENT_CSV, ("Month", "Route_ID", *TRANSACTION_TYPES, "Total_Revenue"),
              route_rows(scenarios["Current"]))
    write_csv(IMPACT_CSV,
              ("Month", "Current_Revenue", "All_MDY_Revenue", "All_DMY_Revenue",
               "DMY_minus_MDY", "Current_minus_MDY"), monthly_impact)
    write_workbook(scenarios, counts, route_impact, monthly_impact)
    print(f"Wrote {WORKBOOK.name}, {CURRENT_CSV.name}, and {IMPACT_CSV.name}")
    print(f"Compared {counts['ambiguous']} ambiguous dates: "
          f"{counts['id_resolved']} ID resolved, {counts['fallback']} fallbacks")
    biggest = max(monthly_impact, key=lambda row: abs(row[4]))
    print(f"Largest monthly D/M/Y minus M/D/Y difference: {biggest[4]:,.2f} in {biggest[0]}")


if __name__ == "__main__":
    main()

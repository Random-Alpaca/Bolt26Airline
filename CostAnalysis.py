"""Show annual costs by route and cost type from costs.csv.

Run ``python3 CostAnalysis.py`` for every route and year. Use ``--route`` and
``--year`` to narrow the report, or ``--output FILE`` to save it as CSV.
"""

import argparse
import csv
from collections import defaultdict
from datetime import date as calendar_date
from decimal import Decimal, InvalidOperation
from pathlib import Path


COST_TYPES = ("Crew", "Food", "Fuel", "Maintenance")
DEFAULT_COSTS_FILE = Path(__file__).with_name("costs.csv")


def annual_costs(path):
    """Return costs keyed by (calendar year, route), then cost type."""
    totals = defaultdict(lambda: {cost_type: Decimal("0") for cost_type in COST_TYPES})

    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"Cost_Date", "Route_ID", "Cost_Type", "Amount"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path} must contain columns: {', '.join(sorted(required))}")

        for line_number, row in enumerate(reader, start=2):
            date = row["Cost_Date"].strip()
            route = row["Route_ID"].strip().upper()
            cost_type = row["Cost_Type"].strip()
            try:
                year = calendar_date.fromisoformat(date[:10]).year
            except ValueError as error:
                raise ValueError(f"{path}:{line_number}: invalid Cost_Date {date!r}")
            if not route or cost_type not in COST_TYPES:
                raise ValueError(f"{path}:{line_number}: invalid route or cost type")
            try:
                amount = Decimal(row["Amount"].strip())
            except InvalidOperation as error:
                raise ValueError(f"{path}:{line_number}: invalid Amount {row['Amount']!r}") from error
            totals[(year, route)][cost_type] += amount

    return totals


def selected_rows(totals, route=None, year=None):
    return [
        (annual_year, route_id, amounts)
        for (annual_year, route_id), amounts in sorted(totals.items())
        if (route is None or route_id == route) and (year is None or annual_year == year)
    ]


def print_report(rows):
    if not rows:
        print("No costs found for the selected route and year.")
        return

    headers = ("Year", "Route", *COST_TYPES, "Total")
    formatted = []
    for annual_year, route_id, amounts in rows:
        total = sum(amounts.values())
        formatted.append((
            str(annual_year), route_id,
            *(f"{amounts[cost_type]:,.2f}" for cost_type in COST_TYPES),
            f"{total:,.2f}",
        ))

    widths = [max(len(str(value)) for value in column) for column in zip(headers, *formatted)]
    print("  ".join(f"{header:<{width}}" for header, width in zip(headers, widths)))
    print("  ".join("-" * width for width in widths))
    for row in formatted:
        print("  ".join(
            f"{value:<{width}}" if index < 2 else f"{value:>{width}}"
            for index, (value, width) in enumerate(zip(row, widths))
        ))


def write_csv(rows, path):
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.writer(destination, lineterminator="\n")
        writer.writerow(("Year", "Route_ID", *COST_TYPES, "Total"))
        for year, route, amounts in rows:
            writer.writerow((year, route, *(f"{amounts[kind]:.2f}" for kind in COST_TYPES),
                             f"{sum(amounts.values()):.2f}"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route", help="Show one route, for example YVR-YLW")
    parser.add_argument("--year", type=int, help="Show one calendar year")
    parser.add_argument("--costs-file", type=Path, default=DEFAULT_COSTS_FILE,
                        help="Input CSV (default: costs.csv beside this script)")
    parser.add_argument("--output", type=Path, help="Write the selected rows to a CSV file")
    args = parser.parse_args()

    try:
        totals = annual_costs(args.costs_file)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    rows = selected_rows(totals, route=args.route.strip().upper() if args.route else None,
                         year=args.year)
    if args.output:
        if args.output.resolve() == args.costs_file.resolve():
            parser.error("output file must differ from the input costs file")
        try:
            write_csv(rows, args.output)
        except OSError as error:
            parser.error(str(error))
        print(f"Wrote {len(rows)} rows to {args.output}")
    else:
        print_report(rows)


if __name__ == "__main__":
    main()

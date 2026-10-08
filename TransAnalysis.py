"""Show annual revenue by route and transaction type from transactions.csv.

Run ``python3 TransAnalysis.py`` to view the report. Use ``--route`` and
``--year`` to narrow it, or ``--output FILE`` to save it as CSV.
Refunds are negative amounts and reduce total revenue.
"""

import argparse
import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


TRANSACTION_TYPES = (
    "Ticket", "Extra Baggage", "Food & Onboard", "Seat Upgrade",
    "Change Fee", "Refund",
)
TYPE_NAMES = {name.casefold(): name for name in TRANSACTION_TYPES}
DEFAULT_TRANSACTIONS_FILE = Path(__file__).with_name("transactions.csv")


def transaction_year(value):
    """Read the calendar year from ISO and slash dates in the source CSV."""
    day = value.split(" ", 1)[0]
    if "-" in day:
        return date.fromisoformat(day).year
    first, second, third = day.split("/")
    if len(first) == 4:  # YYYY/MM/DD
        return date(int(first), int(second), int(third)).year
    if len(third) == 4:  # MM/DD/YYYY or DD/MM/YYYY; either gives the same year
        year, left, right = int(third), int(first), int(second)
        if not any(
            is_valid_date(year, month, day)
            for month, day in ((left, right), (right, left))
        ):
            raise ValueError(f"invalid transaction date {value!r}")
        return year
    raise ValueError(f"invalid transaction date {value!r}")


def is_valid_date(year, month, day):
    try:
        date(year, month, day)
    except ValueError:
        return False
    return True


def annual_revenue(path):
    """Return revenue keyed by (calendar year, route), then transaction type."""
    totals = defaultdict(lambda: {kind: Decimal("0") for kind in TRANSACTION_TYPES})

    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"Transaction_Date", "Route_ID", "Transaction_Type", "Amount"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path} must contain columns: {', '.join(sorted(required))}")

        for line_number, row in enumerate(reader, start=2):
            route = row["Route_ID"].strip().upper()
            kind = TYPE_NAMES.get(row["Transaction_Type"].strip().casefold())
            if not route or kind is None:
                raise ValueError(f"{path}:{line_number}: invalid route or transaction type")
            try:
                year = transaction_year(row["Transaction_Date"].strip())
            except (ValueError, TypeError) as error:
                raise ValueError(
                    f"{path}:{line_number}: invalid Transaction_Date {row['Transaction_Date']!r}"
                ) from error
            try:
                amount = Decimal(row["Amount"].strip().replace("$", "").replace(",", ""))
            except InvalidOperation as error:
                raise ValueError(f"{path}:{line_number}: invalid Amount {row['Amount']!r}") from error
            totals[(year, route)][kind] += amount

    return totals


def selected_rows(totals, route=None, year=None):
    return [
        (annual_year, route_id, amounts)
        for (annual_year, route_id), amounts in sorted(totals.items())
        if (route is None or route_id == route) and (year is None or annual_year == year)
    ]


def print_report(rows):
    if not rows:
        print("No transactions found for the selected route and year.")
        return

    headers = ("Year", "Route", *TRANSACTION_TYPES, "Total_Revenue")
    formatted = [
        (str(year), route,
         *(f"{amounts[kind]:,.2f}" for kind in TRANSACTION_TYPES),
         f"{sum(amounts.values()):,.2f}")
        for year, route, amounts in rows
    ]
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
        writer.writerow(("Year", "Route_ID", *TRANSACTION_TYPES, "Total_Revenue"))
        for year, route, amounts in rows:
            writer.writerow((year, route, *(f"{amounts[kind]:.2f}" for kind in TRANSACTION_TYPES),
                             f"{sum(amounts.values()):.2f}"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route", help="Show one route, for example YVR-YLW")
    parser.add_argument("--year", type=int, help="Show one calendar year")
    parser.add_argument("--transactions-file", type=Path, default=DEFAULT_TRANSACTIONS_FILE,
                        help="Input CSV (default: transactions.csv beside this script)")
    parser.add_argument("--output", type=Path, help="Write the selected rows to a CSV file")
    args = parser.parse_args()

    try:
        totals = annual_revenue(args.transactions_file)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    rows = selected_rows(totals, route=args.route.strip().upper() if args.route else None,
                         year=args.year)
    if args.output:
        if args.output.resolve() == args.transactions_file.resolve():
            parser.error("output file must differ from the input transactions file")
        try:
            write_csv(rows, args.output)
        except OSError as error:
            parser.error(str(error))
        print(f"Wrote {len(rows)} rows to {args.output}")
    else:
        print_report(rows)


if __name__ == "__main__":
    main()

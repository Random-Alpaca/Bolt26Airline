"""Combine annual route revenue and costs into a profit CSV.

Run ``python3 ProfitAnalysis.py`` to regenerate annual_route_profits.csv.
Profit is total revenue, including refunds, minus total cost.
"""

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path


DIRECTORY = Path(__file__).parent


def read_totals(path, amount_column):
    """Read one annual total per (year, route) from a summary CSV."""
    totals = {}
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        required = {"Year", "Route_ID", amount_column}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path} must contain columns: {', '.join(sorted(required))}")

        for line_number, row in enumerate(reader, start=2):
            try:
                key = (int(row["Year"]), row["Route_ID"].strip().upper())
                amount = Decimal(row[amount_column].strip())
            except (ValueError, InvalidOperation, AttributeError) as error:
                raise ValueError(f"{path}:{line_number}: invalid year, route, or amount") from error
            if not key[1] or not amount.is_finite():
                raise ValueError(f"{path}:{line_number}: invalid route or amount")
            if key in totals:
                raise ValueError(f"{path}:{line_number}: duplicate year and route {key}")
            totals[key] = amount
    return totals


def write_profits(revenue, costs, path):
    revenue_only = revenue.keys() - costs.keys()
    costs_only = costs.keys() - revenue.keys()
    if revenue_only or costs_only:
        raise ValueError(
            f"Revenue and cost rows do not match: {len(revenue_only)} without costs, "
            f"{len(costs_only)} without revenue"
        )

    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.writer(destination, lineterminator="\n")
        writer.writerow(("Year", "Route_ID", "Total_Revenue", "Total_Cost", "Profit"))
        for year, route in sorted(revenue):
            total_revenue = revenue[(year, route)]
            total_cost = costs[(year, route)]
            writer.writerow((year, route, f"{total_revenue:.2f}", f"{total_cost:.2f}",
                             f"{total_revenue - total_cost:.2f}"))
    return len(revenue)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revenue-file", type=Path,
                        default=DIRECTORY / "annual_route_revenue.csv")
    parser.add_argument("--costs-file", type=Path,
                        default=DIRECTORY / "annual_route_costs.csv")
    parser.add_argument("--output", type=Path,
                        default=DIRECTORY / "annual_route_profits.csv")
    args = parser.parse_args()
    if args.output.resolve() in {args.revenue_file.resolve(), args.costs_file.resolve()}:
        parser.error("output file must differ from both input files")

    try:
        revenue = read_totals(args.revenue_file, "Total_Revenue")
        costs = read_totals(args.costs_file, "Total")
        count = write_profits(revenue, costs, args.output)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Wrote {count} rows to {args.output}")


if __name__ == "__main__":
    main()

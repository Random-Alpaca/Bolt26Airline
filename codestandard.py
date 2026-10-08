"""Normalize Route_ID to AAA-AAA (upper case, no spaces) in the working CSVs."""
import csv
import re

for name in ("costs", "gates", "transactions"):
    path = f"{name}.csv"
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0])
    bad = 0
    for r in rows:
        letters = re.sub(r"[^A-Za-z]", "", r["Route_ID"]).upper()
        if len(letters) == 6:
            r["Route_ID"] = f"{letters[:3]}-{letters[3:]}"
        else:
            bad += 1  # left untouched for manual review
            print(f"{path}: unfixable Route_ID {r['Route_ID']!r}")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{path}: {len(rows)} rows, {bad} unfixable")

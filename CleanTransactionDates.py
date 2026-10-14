"""Normalize slash-format text dates in transactions.xlsx to Excel date cells.

For dates valid in both month/day/year and day/month/year, use neighboring
Transaction_ID values when they place exactly one interpretation in order.
Fall back to month/day/year if IDs cannot resolve the date. Record every
decision in a CSV and preserve the workbook's other content.
"""

import csv
import bisect
import os
import re
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from posixpath import normpath
from xml.etree import ElementTree
from zipfile import ZipFile


ROOT = Path(__file__).parent
SOURCE = ROOT / "transactions.xlsx"
TRANSACTIONS_CSV = ROOT / "transactions.csv"
OUTPUT = ROOT / "transactions_cleaned.xlsx"
DECISIONS = ROOT / "transaction_date_decisions.csv"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
ROW_PATTERN = re.compile(rb"<row\b[^>]*>.*?</row>", re.DOTALL)
DATE_CELL = re.compile(rb'<c r="C(\d+)" t="s"><v>(\d+)</v></c>')
NATIVE_DATE_CELL = re.compile(rb'<c r="C(\d+)" s="(\d+)"><v>([\d.]+)</v></c>')
SLASH_DATE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4}) (\d{2}):(\d{2})$")
EXCEL_EPOCH = datetime(1899, 12, 30)
CONFIRMED_CORRECTIONS = {
    9900561: ("04/09/2024 07:59", datetime(2024, 9, 4, 7, 59)),
}


def shared_dates(archive):
    """Map shared-string indexes used for slash dates to their text."""
    dates = {}
    with archive.open("xl/sharedStrings.xml") as source:
        for index, (_, element) in enumerate(
            (event, element)
            for event, element in ElementTree.iterparse(source, events=("end",))
            if element.tag == NS + "si"
        ):
            value = "".join(part.text or "" for part in element.iter(NS + "t"))
            if SLASH_DATE.fullmatch(value):
                dates[index] = value
            element.clear()
    return dates


def transaction_sheet(archive):
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    sheet = next((item for item in workbook.iter(NS + "sheet")
                  if item.get("name") == "transactions"), None)
    if sheet is None:
        raise ValueError("No transactions sheet found")
    relationship_id = sheet.get(REL_NS + "id")
    relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    relationship = next((item for item in relationships.iter(PKG_NS + "Relationship")
                         if item.get("Id") == relationship_id), None)
    if relationship is None:
        raise ValueError("Transactions sheet relationship is missing")
    return normpath("xl/" + relationship.get("Target").lstrip("/"))


def possible_dates(value):
    first, second, year, hour, minute = map(int, SLASH_DATE.fullmatch(value).groups())
    choices = []
    for month, day in ((first, second), (second, first)):
        try:
            choices.append(datetime(year, month, day, hour, minute))
        except ValueError:
            choices.append(None)
    return choices


def load_id_evidence():
    """Read known dates and IDs from the CSV, which shares the workbook row order."""
    known = []
    source_text_dates = {}
    ambiguous_ids = {}
    confirmed_by_row = {}
    with TRANSACTIONS_CSV.open(newline="", encoding="utf-8-sig") as source:
        for excel_row, row in enumerate(csv.DictReader(source), start=2):
            transaction_id = int(row["Transaction_ID"].strip().removeprefix("TX"))
            value = row["Transaction_Date"].strip()
            if transaction_id in CONFIRMED_CORRECTIONS:
                original, confirmed = CONFIRMED_CORRECTIONS[transaction_id]
                if value != confirmed.strftime("%Y-%m-%d %H:%M"):
                    raise ValueError(f"Confirmed date does not match CSV row {excel_row}")
                source_text_dates[excel_row] = original
                confirmed_by_row[excel_row] = confirmed
                known.append((transaction_id, confirmed))
                continue
            if SLASH_DATE.fullmatch(value):
                source_text_dates[excel_row] = value
                month_first, day_first = possible_dates(value)
                if month_first and day_first and month_first != day_first:
                    ambiguous_ids[excel_row] = transaction_id
                    continue
                parsed = month_first or day_first
            else:
                day = value.split(" ", 1)[0]
                if "-" in day:
                    parsed = datetime.strptime(value, "%Y-%m-%d %H:%M")
                else:
                    parsed = datetime.strptime(value, "%Y/%m/%d %H:%M")
            if parsed is None:
                raise ValueError(f"Invalid source date at CSV row {excel_row}")
            known.append((transaction_id, parsed))
    known.sort(key=lambda item: item[0])
    return ([item[0] for item in known], known, source_text_dates,
            ambiguous_ids, confirmed_by_row)


def infer_from_id(transaction_id, month_first, day_first, known_ids, known):
    """Use tight chronological neighbors in the main sequential ID range."""
    if not 1_000_000 <= transaction_id < 2_000_000:
        return None
    left = bisect.bisect_left(known_ids, transaction_id)
    right = bisect.bisect_right(known_ids, transaction_id)
    if left == 0 or right == len(known):
        return None
    lower_id, lower_date = known[left - 1]
    upper_id, upper_date = known[right]
    if max(transaction_id - lower_id, upper_id - transaction_id) > 3:
        return None
    month_fits = lower_date <= month_first <= upper_date
    day_fits = lower_date <= day_first <= upper_date
    if month_fits == day_fits:
        return None
    return (month_first if month_fits else day_first,
            lower_id, lower_date, upper_id, upper_date)


def clean_row(row, dates, decision_writer, counts, date_style, id_evidence):
    cell = DATE_CELL.search(row)
    if not cell:
        numeric_cell = NATIVE_DATE_CELL.search(row)
        if not numeric_cell:
            return row
        excel_row = int(numeric_cell.group(1))
        known_ids, known, source_text_dates, ambiguous_ids, _ = id_evidence
        if excel_row not in ambiguous_ids:
            return row
        original = source_text_dates[excel_row]
        month_first, day_first = possible_dates(original)
        existing = EXCEL_EPOCH + timedelta(days=float(numeric_cell.group(3)))
        if existing.strftime("%Y-%m-%d %H:%M") not in (
            month_first.strftime("%Y-%m-%d %H:%M"),
            day_first.strftime("%Y-%m-%d %H:%M"),
        ):
            raise ValueError(f"C{excel_row} does not match either source date interpretation")
        inference = infer_from_id(ambiguous_ids[excel_row], month_first, day_first,
                                  known_ids, known)
        if inference:
            parsed, lower_id, lower_date, upper_id, upper_date = inference
            decision = "M/D/Y from ID order" if parsed == month_first else "D/M/Y from ID order"
            neighbor_evidence = (
                f"TX{lower_id} {lower_date:%Y-%m-%d %H:%M}; "
                f"TX{upper_id} {upper_date:%Y-%m-%d %H:%M}"
            )
            counts["id_resolved"] += 1
        else:
            parsed = month_first
            decision = "M/D/Y fallback; ID order inconclusive"
            neighbor_evidence = ""
            counts["fallback"] += 1
        decision_writer.writerow((excel_row, original, decision,
                                  parsed.strftime("%Y-%m-%d %H:%M"), neighbor_evidence))
        counts["native_ambiguous"] += 1
        if parsed.strftime("%Y-%m-%d %H:%M") == existing.strftime("%Y-%m-%d %H:%M"):
            return row
        serial = (parsed - EXCEL_EPOCH).total_seconds() / 86400
        replacement = (f'<c r="C{excel_row}" s="{numeric_cell.group(2).decode()}">'
                       f'<v>{serial:.12f}</v></c>').encode()
        counts["native_corrected"] += 1
        return row[:numeric_cell.start()] + replacement + row[numeric_cell.end():]

    excel_row = int(cell.group(1))
    value = dates.get(int(cell.group(2)))
    if value is None:
        if excel_row != 1:
            raise ValueError(f"C{excel_row} has an unexpected text date")
        return row
    known_ids, known, source_text_dates, ambiguous_ids, confirmed_by_row = id_evidence
    if source_text_dates.get(excel_row) != value:
        raise ValueError(f"C{excel_row} does not match transactions.csv")

    counts["text_dates"] += 1
    month_first, day_first = possible_dates(value)
    parsed = month_first or day_first
    if parsed is None:
        raise ValueError(f"C{excel_row} has an invalid date: {value}")
    neighbor_evidence = ""
    if excel_row in confirmed_by_row:
        parsed = confirmed_by_row[excel_row]
        decision = "D/M/Y confirmed; moved to September 2024"
        counts["confirmed"] += 1
    elif month_first and day_first and month_first != day_first:
        transaction_id = ambiguous_ids[excel_row]
        inference = infer_from_id(transaction_id, month_first, day_first,
                                  known_ids, known)
        if inference:
            parsed, lower_id, lower_date, upper_id, upper_date = inference
            decision = "M/D/Y from ID order" if parsed == month_first else "D/M/Y from ID order"
            neighbor_evidence = (
                f"TX{lower_id} {lower_date:%Y-%m-%d %H:%M}; "
                f"TX{upper_id} {upper_date:%Y-%m-%d %H:%M}"
            )
            counts["id_resolved"] += 1
        else:
            decision = "M/D/Y fallback; ID order inconclusive"
            counts["fallback"] += 1
    elif month_first:
        decision = "M/D/Y"
    else:
        decision = "D/M/Y required; first component exceeds 12"
        counts["forced_day_first"] += 1
    decision_writer.writerow((excel_row, value, decision,
                              parsed.strftime("%Y-%m-%d %H:%M"), neighbor_evidence))

    serial = (parsed - EXCEL_EPOCH).total_seconds() / 86400
    replacement = f'<c r="C{excel_row}" s="{date_style}"><v>{serial:.12f}</v></c>'.encode()
    counts["converted"] += 1
    return row[:cell.start()] + replacement + row[cell.end():]


def clean_sheet(source, destination, dates, decision_writer, counts, date_style,
                id_evidence):
    buffer = b""
    while chunk := source.read(1024 * 1024):
        buffer += chunk
        while match := ROW_PATTERN.search(buffer):
            destination.write(buffer[:match.start()])
            destination.write(clean_row(match.group(), dates, decision_writer, counts,
                                        date_style, id_evidence))
            buffer = buffer[match.end():]
    destination.write(buffer)


def main():
    if OUTPUT.resolve() == SOURCE.resolve():
        raise ValueError("output workbook must differ from source workbook")

    temporary_workbook = None
    temporary_decisions = None
    try:
        with tempfile.NamedTemporaryFile(dir=ROOT, suffix=".xlsx", delete=False) as file:
            temporary_workbook = Path(file.name)
        with tempfile.NamedTemporaryFile(dir=ROOT, suffix=".csv", delete=False) as file:
            temporary_decisions = Path(file.name)

        counts = {"text_dates": 0, "converted": 0, "id_resolved": 0,
                  "fallback": 0, "forced_day_first": 0, "confirmed": 0,
                  "native_ambiguous": 0, "native_corrected": 0}
        id_evidence = load_id_evidence()
        with ZipFile(SOURCE) as original, \
             ZipFile(temporary_workbook, "w") as cleaned, \
             temporary_decisions.open("w", newline="", encoding="utf-8") as decisions:
            dates = shared_dates(original)
            sheet = transaction_sheet(original)
            with original.open(sheet) as source:
                first_bytes = source.read(8192)
            style_match = re.search(rb'<c r="C2" s="(\d+)"><v>', first_bytes)
            if not style_match:
                raise ValueError("Could not identify the Excel date style in C2")
            date_style = style_match.group(1).decode()
            writer = csv.writer(decisions, lineterminator="\n")
            writer.writerow(("Excel_Row", "Original_Date", "Interpretation",
                             "Converted_Date", "ID_Neighbors"))
            for item in original.infolist():
                with original.open(item) as entry, cleaned.open(item, "w") as output:
                    if item.filename == sheet:
                        clean_sheet(entry, output, dates, writer, counts,
                                    date_style, id_evidence)
                    else:
                        while chunk := entry.read(1024 * 1024):
                            output.write(chunk)

        if counts["text_dates"] == 0 or counts["text_dates"] != counts["converted"]:
            raise ValueError(f"unexpected date counts: {counts}")
        os.replace(temporary_workbook, OUTPUT)
        os.replace(temporary_decisions, DECISIONS)
        print(f"Converted {counts['converted']} dates in {OUTPUT.name}")
        print(f"Resolved {counts['id_resolved']} ambiguous dates from Transaction_ID order")
        print(f"Used M/D/Y fallback for {counts['fallback']} inconclusive dates")
        print(f"Used D/M/Y for {counts['forced_day_first']} dates where M/D/Y is invalid")
        print(f"Applied {counts['confirmed']} confirmed date correction")
        print(f"Corrected {counts['native_corrected']} pre-existing Excel dates")
        print(f"Recorded decisions in {DECISIONS.name}")
    finally:
        for path in (temporary_workbook, temporary_decisions):
            if path is not None:
                path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

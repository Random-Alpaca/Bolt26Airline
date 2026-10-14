"""Prepare exact-cent, normalized analysis inputs without changing source files."""
import csv
import hashlib
import json
import os
import re
import sqlite3
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TABLES = HERE / 'tables'
DB = HERE / 'airline_analysis.sqlite'
TYPE_MAP = {x.casefold(): x for x in ['Ticket', 'Extra Baggage', 'Food & Onboard', 'Seat Upgrade', 'Change Fee', 'Refund']}
CHANNEL_MAP = {alias: canonical for canonical, aliases in {
    'Direct Web': ['direct web', 'website', 'web'],
    'Online Travel Agency': ['online travel agency', 'online travel agcy', 'ota'],
    'Mobile App': ['mobile app', 'app', 'mobile'],
    'Corporate Portal': ['corporate portal', 'corp portal', 'corporate'],
}.items() for alias in aliases}
TIER_MAP = {x.casefold(): x for x in ['Non-Member', 'Blue', 'Silver', 'Gold', 'Platinum']}
TIER_MAP.update({x: 'Unknown' for x in ['', 'none', 'n/a', 'unknown']})
PAYMENT_MAP = {x.casefold(): x for x in ['Credit Card', 'Points + Cash', 'Debit', 'Travel Voucher']}
PAYMENT_MAP[''] = 'Unknown'


def cents(value):
    amount = Decimal(value.strip().replace('$', '').replace(',', ''))
    assert amount.is_finite() and amount * 100 == (amount * 100).to_integral_value(), value
    return int(amount * 100)


def period(value):
    assert '2024-09-01' <= value[:10] <= '2026-08-31', value
    return 1 if value < '2025-09-01' else 2


def write_csv(name, rows, fields=None):
    TABLES.mkdir(exist_ok=True)
    with (TABLES / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    TABLES.mkdir(exist_ok=True)
    audit = {'source_files': {}, 'date_decisions_used': 0}
    for name in ['transactions.csv', 'costs.csv', 'gates.csv', 'transaction_date_decisions.csv']:
        path = ROOT / name
        audit['source_files'][name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
    with (ROOT / 'transaction_date_decisions.csv').open(newline='') as f:
        decision_rows = list(csv.DictReader(f))
    decisions = {int(r['Excel_Row']): r for r in decision_rows}
    assert len(decisions) == len(decision_rows)
    temp = HERE / 'airline_analysis.building.sqlite'
    if temp.exists():
        temp.unlink()
    con = sqlite3.connect(temp)
    con.execute('PRAGMA cache_size=-262144')
    con.execute('PRAGMA temp_store=MEMORY')
    con.executescript('''
        CREATE TABLE transactions(tx_id TEXT PRIMARY KEY,booking_id TEXT,date TEXT,month TEXT,period INTEGER,
          route TEXT,type TEXT,tier TEXT,channel TEXT,payment TEXT,amount_cents INTEGER,source_row INTEGER);
        CREATE TABLE costs(cost_id TEXT PRIMARY KEY,date TEXT,month TEXT,period INTEGER,route TEXT,type TEXT,
          origin TEXT,destination TEXT,amount_cents INTEGER);
        CREATE TABLE gates(city TEXT,gate TEXT,year TEXT,route TEXT,amount_cents INTEGER,source_row INTEGER);
    ''')
    removed = []
    fallbacks = []
    category_changes = Counter()
    raw_sum = 0
    with (ROOT / 'transactions.csv').open(newline='', encoding='utf-8-sig') as f:
        for rownum, row in enumerate(csv.DictReader(f), start=2):
            raw_date = row['Transaction_Date'].strip()
            decision = decisions.get(rownum)
            if decision:
                # The workbook log preserves the pre-correction text for this confirmed row.
                assert decision['Original_Date'] == raw_date or (
                    row['Transaction_ID'] == 'TX9900561' and raw_date == decision['Converted_Date'])
                date = decision['Converted_Date']
                audit['date_decisions_used'] += 1
            else:
                date = raw_date
                if '/' in date:
                    parts = date.split(' ')[0].split('/')
                    fmt = '%Y/%m/%d %H:%M' if len(parts[0]) == 4 else '%m/%d/%Y %H:%M'
                    date = datetime.strptime(date, fmt).strftime('%Y-%m-%d %H:%M')
            date = datetime.fromisoformat(date).strftime('%Y-%m-%d %H:%M')
            route = row['Route_ID'].strip().upper()
            assert re.fullmatch('[A-Z]{3}-[A-Z]{3}', route)
            kind = TYPE_MAP[row['Transaction_Type'].strip().casefold()]
            tier = TIER_MAP[row['Membership_Tier'].strip().casefold()]
            channel = CHANNEL_MAP[row['Booking_Channel'].strip().casefold()]
            payment = PAYMENT_MAP[row['Payment_Method'].strip().casefold()]
            for col, value in [('Transaction_Type', kind), ('Membership_Tier', tier), ('Booking_Channel', channel), ('Payment_Method', payment)]:
                category_changes[(col, row[col], value)] += 1
            amount = cents(row['Amount'])
            assert (amount < 0) == (kind == 'Refund')
            values = (row['Transaction_ID'].strip(), row['Booking_ID'].strip(), date, date[:7], period(date), route, kind, tier, channel, payment, amount, rownum)
            raw_sum += amount
            try:
                con.execute('INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', values)
            except sqlite3.IntegrityError:
                existing = con.execute('SELECT * FROM transactions WHERE tx_id=?', (values[0],)).fetchone()
                assert existing[:-1] == values[:-1], ('Conflicting duplicate', values[0], existing, values)
                removed.append({'Transaction_ID': values[0], 'Kept_Source_Row': existing[-1], 'Removed_Source_Row': rownum, 'Amount_Cents': amount, 'Route_ID': route, 'Month': date[:7]})
            if decision and 'fallback' in decision['Interpretation']:
                alt = datetime.strptime(raw_date, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M')
                fallbacks.append({'Transaction_ID': values[0], 'Source_Row': rownum, 'Route_ID': route, 'Type': kind, 'Amount_Cents': amount, 'Current_Date': date, 'Alternative_Date': alt})
    audit['raw_transaction_rows'] = rownum - 1
    audit['raw_revenue_cents'] = raw_sum
    audit['removed_duplicate_rows'] = len(removed)
    audit['removed_duplicate_revenue_cents'] = sum(r['Amount_Cents'] for r in removed)
    audit['date_fallback_rows'] = len(fallbacks)
    audit['date_fallback_gross_cents'] = sum(abs(r['Amount_Cents']) for r in fallbacks)
    with (ROOT / 'costs.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            date = datetime.fromisoformat(row['Cost_Date']).strftime('%Y-%m-%d %H:%M')
            amount = cents(row['Amount'])
            assert amount > 0
            con.execute('INSERT INTO costs VALUES (?,?,?,?,?,?,?,?,?)',
                (row['Cost_ID'], date, date[:7], period(date), row['Route_ID'], row['Cost_Type'], row['From'], row['To'], amount))
    with (ROOT / 'gates.csv').open(newline='') as f:
        for rownum, row in enumerate(csv.DictReader(f), start=2):
            con.execute('INSERT INTO gates VALUES (?,?,?,?,?,?)',
                (row['City'], row['Gate_Number'], row['Year'], row['Route_ID'].strip(), cents(row['Annual_Gate_Cost']), rownum))
    con.executescript('''
        CREATE INDEX tx_booking ON transactions(booking_id);
        CREATE INDEX tx_route_period ON transactions(route,period);
        CREATE INDEX tx_month ON transactions(month);
        CREATE INDEX cost_route_period ON costs(route,period);
        CREATE INDEX cost_month ON costs(month);
        CREATE VIEW cost_events AS SELECT date,month,period,route,SUM(amount_cents) AS amount_cents,
          COUNT(*) AS category_count FROM costs GROUP BY date,route;
    ''')
    audit['deduplicated_transaction_rows'], audit['deduplicated_revenue_cents'] = con.execute('SELECT COUNT(*),SUM(amount_cents) FROM transactions').fetchone()
    audit['cost_rows'], audit['cost_cents'] = con.execute('SELECT COUNT(*),SUM(amount_cents) FROM costs').fetchone()
    audit['booking_count'] = con.execute('SELECT COUNT(DISTINCT booking_id) FROM transactions').fetchone()[0]
    audit['gate_rows'] = con.execute('SELECT COUNT(*) FROM gates').fetchone()[0]
    assert audit['raw_revenue_cents'] - audit['removed_duplicate_revenue_cents'] == audit['deduplicated_revenue_cents']
    assert audit['raw_transaction_rows'] - audit['removed_duplicate_rows'] == audit['deduplicated_transaction_rows']
    assert con.execute('SELECT COUNT(*) FROM cost_events WHERE category_count!=4').fetchone()[0] == 0
    assert audit['date_decisions_used'] == len(decisions)
    con.commit()
    assert con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    con.close()
    os.replace(temp, DB)
    write_csv('duplicate_transactions_removed.csv', removed)
    write_csv('uncertain_dates.csv', fallbacks)
    write_csv('category_mapping.csv', [{'Field': c, 'Raw_Value': raw, 'Normalized_Value': value, 'Source_Rows': n}
        for (c, raw, value), n in sorted(category_changes.items())])
    (HERE / 'preparation_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps({k: v for k,v in audit.items() if k != 'source_files'}, indent=2))


if __name__ == '__main__':
    main()

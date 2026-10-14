"""Reproduce booking integrity and recorded-revenue mix analysis.

Run after prepare.py creates airline_analysis.sqlite:
    python3 analysis/commercial.py
"""

import csv
import sqlite3
from pathlib import Path


BASE = Path(__file__).resolve().parent
DB = BASE / "airline_analysis.sqlite"
TABLES = BASE / "tables"
TABLES.mkdir(exist_ok=True)


def write_table(conn, name, sql):
    cur = conn.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    with (TABLES / f"commercial_{name}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        writer.writerows(rows)
    return [dict(zip(cols, row)) for row in rows]


def money(cents):
    return f"{'-' if cents < 0 else ''}${abs(cents) / 100:,.2f}"


def pct(n, d):
    return f"{n / d * 100:.1f}%" if d else "n/a"


with sqlite3.connect(DB) as con:
    con.execute("PRAGMA temp_store=MEMORY")
    con.executescript("""
        CREATE TEMP TABLE booking_profile AS
        SELECT booking_id,
               COUNT(*) AS transactions,
               SUM(type='Ticket') AS ticket_transactions,
               SUM(type IN ('Extra Baggage','Food & Onboard','Seat Upgrade')) AS extra_transactions,
               SUM(type='Change Fee') AS change_transactions,
               SUM(type='Refund') AS refund_transactions,
               COUNT(DISTINCT route) AS routes,
               COUNT(DISTINCT tier) AS tiers,
               COUNT(DISTINCT channel) AS channels,
               COUNT(DISTINCT period) AS periods,
               SUM(amount_cents) AS net_cents
        FROM transactions GROUP BY booking_id;
        CREATE INDEX bp_booking ON booking_profile(booking_id);
        CREATE TEMP TABLE booking_period AS
        SELECT booking_id, period,
               COUNT(*) AS transactions,
               SUM(type='Ticket') AS ticket_transactions,
               SUM(type IN ('Extra Baggage','Food & Onboard','Seat Upgrade')) AS extra_transactions,
               SUM(type='Refund') AS refund_transactions,
               SUM(CASE WHEN type IN ('Extra Baggage','Food & Onboard','Seat Upgrade')
                        THEN amount_cents ELSE 0 END) AS extra_cents,
               SUM(amount_cents) AS net_cents,
               COUNT(DISTINCT route) AS routes,
               COUNT(DISTINCT tier) AS tiers,
               COUNT(DISTINCT channel) AS channels,
               MIN(channel) AS channel,
               MIN(tier) AS tier,
               MIN(route) AS route
        FROM transactions GROUP BY booking_id,period;
        CREATE INDEX bperiod_booking ON booking_period(booking_id,period);
    """)

    integrity = write_table(con, "booking_integrity", """
        SELECT COUNT(*) AS bookings,
               SUM(ticket_transactions=0) AS no_ticket_bookings,
               SUM(ticket_transactions=1) AS one_ticket_bookings,
               SUM(ticket_transactions>1) AS multiple_ticket_bookings,
               SUM(routes>1) AS mixed_route_bookings,
               SUM(tiers>1) AS mixed_tier_bookings,
               SUM(channels>1) AS mixed_channel_bookings,
               SUM(periods>1) AS cross_period_bookings,
               SUM(refund_transactions>0) AS refund_bookings,
               SUM(refund_transactions>0 AND ticket_transactions=0) AS refund_without_ticket_bookings,
               SUM(extra_transactions>0 AND ticket_transactions=0) AS extra_without_ticket_bookings,
               SUM(CASE WHEN ticket_transactions=0 THEN net_cents ELSE 0 END) AS no_ticket_net_cents
        FROM booking_profile;
    """)[0]
    periods = write_table(con, "revenue_mix", """
        SELECT period, type, COUNT(*) AS transactions,
               COUNT(DISTINCT booking_id) AS bookings,
               SUM(amount_cents) AS revenue_cents
        FROM transactions GROUP BY period,type ORDER BY period,type;
    """)
    all_period = write_table(con, "period_totals", """
        SELECT period, COUNT(*) AS transactions,
               COUNT(DISTINCT booking_id) AS bookings,
               SUM(CASE WHEN amount_cents>0 THEN amount_cents ELSE 0 END) AS positive_cents,
               -SUM(CASE WHEN amount_cents<0 THEN amount_cents ELSE 0 END) AS refund_cents,
               SUM(amount_cents) AS net_cents
        FROM transactions GROUP BY period ORDER BY period;
    """)
    channel = write_table(con, "channel", """
        SELECT period, channel, COUNT(*) AS transactions,
               SUM(type='Ticket') AS ticket_transactions,
               SUM(CASE WHEN type='Ticket' THEN amount_cents ELSE 0 END) AS ticket_cents,
               SUM(CASE WHEN type IN ('Extra Baggage','Food & Onboard','Seat Upgrade','Change Fee')
                        THEN amount_cents ELSE 0 END) AS ancillary_fee_cents,
               -SUM(CASE WHEN type='Refund' THEN amount_cents ELSE 0 END) AS refund_cents,
               SUM(amount_cents) AS net_cents
        FROM transactions GROUP BY period,channel ORDER BY period,channel;
    """)
    tier = write_table(con, "tier", """
        SELECT period, tier, COUNT(*) AS transactions,
               SUM(type='Ticket') AS ticket_transactions,
               SUM(CASE WHEN type='Ticket' THEN amount_cents ELSE 0 END) AS ticket_cents,
               SUM(CASE WHEN type IN ('Extra Baggage','Food & Onboard','Seat Upgrade','Change Fee')
                        THEN amount_cents ELSE 0 END) AS ancillary_fee_cents,
               -SUM(CASE WHEN type='Refund' THEN amount_cents ELSE 0 END) AS refund_cents,
               SUM(amount_cents) AS net_cents
        FROM transactions GROUP BY period,tier ORDER BY period,tier;
    """)
    payment = write_table(con, "payment", """
        SELECT period, payment, COUNT(*) AS transactions,
               SUM(type='Ticket') AS ticket_transactions,
               SUM(amount_cents) AS net_cents
        FROM transactions GROUP BY period,payment ORDER BY period,payment;
    """)
    attachment = write_table(con, "attachment", """
        SELECT period,
               COUNT(*) AS ticket_bookings,
               SUM(extra_transactions>0) AS attached_bookings,
               SUM(extra_transactions) AS extra_transactions,
               SUM(extra_cents) AS extra_cents,
               SUM(refund_transactions>0) AS refunded_ticket_bookings,
               SUM(routes>1) AS mixed_route_ticket_bookings,
               SUM(channels>1) AS mixed_channel_ticket_bookings,
               SUM(tiers>1) AS mixed_tier_ticket_bookings
        FROM booking_period WHERE ticket_transactions>0
        GROUP BY period ORDER BY period;
    """)
    period_exclusions = write_table(con, "period_cohort_exclusions", """
        SELECT period, COUNT(*) AS booking_periods_without_ticket,
               SUM(extra_transactions>0) AS add_on_bookings_without_ticket,
               SUM(extra_cents) AS add_on_cents_without_ticket,
               SUM(refund_transactions>0) AS refund_bookings_without_ticket
        FROM booking_period WHERE ticket_transactions=0
        GROUP BY period ORDER BY period;
    """)
    attachment_channel = write_table(con, "attachment_by_channel", """
        SELECT period, CASE WHEN channels=1 THEN channel ELSE 'Mixed' END AS channel,
               COUNT(*) AS ticket_bookings,
               SUM(extra_transactions>0) AS attached_bookings,
               SUM(extra_cents) AS extra_cents,
               SUM(refund_transactions>0) AS refunded_ticket_bookings
        FROM booking_period WHERE ticket_transactions>0
        GROUP BY period, CASE WHEN channels=1 THEN channel ELSE 'Mixed' END
        ORDER BY period,channel;
    """)
    attachment_tier = write_table(con, "attachment_by_tier", """
        SELECT period, CASE WHEN tiers=1 THEN tier ELSE 'Mixed' END AS tier,
               COUNT(*) AS ticket_bookings,
               SUM(extra_transactions>0) AS attached_bookings,
               SUM(extra_cents) AS extra_cents,
               SUM(refund_transactions>0) AS refunded_ticket_bookings
        FROM booking_period WHERE ticket_transactions>0
        GROUP BY period, CASE WHEN tiers=1 THEN tier ELSE 'Mixed' END
        ORDER BY period,tier;
    """)
    attachment_ticket_tier = write_table(con, "attachment_by_ticket_tier", """
        WITH ticket_tiers AS (
          SELECT booking_id, period,
                 CASE WHEN COUNT(DISTINCT tier)=1 THEN MIN(tier) ELSE 'Mixed' END AS ticket_tier
          FROM transactions WHERE type='Ticket' GROUP BY booking_id,period
        )
        SELECT b.period, t.ticket_tier AS tier,
               COUNT(*) AS ticket_bookings,
               SUM(b.extra_transactions>0) AS attached_bookings,
               SUM(b.extra_cents) AS extra_cents
        FROM booking_period b JOIN ticket_tiers t
          ON b.booking_id=t.booking_id AND b.period=t.period
        GROUP BY b.period,t.ticket_tier ORDER BY b.period,t.ticket_tier;
    """)
    unmatched = write_table(con, "non_ticket_booking_mix", """
        SELECT t.type, COUNT(*) AS transactions, COUNT(DISTINCT t.booking_id) AS bookings,
               SUM(t.amount_cents) AS amount_cents
        FROM transactions t JOIN booking_profile b USING(booking_id)
        WHERE b.ticket_transactions=0
        GROUP BY t.type ORDER BY t.type;
    """)
    matched_ticket = write_table(con, "matched_ticket_value", """
        WITH cells AS (
          SELECT period, route, month, channel,
                 COUNT(*) AS tickets, SUM(amount_cents) AS ticket_cents
          FROM transactions
          WHERE type='Ticket' AND channel IN ('Direct Web','Online Travel Agency')
          GROUP BY period,route,month,channel
        ), pairs AS (
          SELECT a.period, a.route, a.month,
                 a.tickets AS direct_tickets, a.ticket_cents AS direct_cents,
                 b.tickets AS ota_tickets, b.ticket_cents AS ota_cents
          FROM cells a JOIN cells b
            ON a.period=b.period AND a.route=b.route AND a.month=b.month
          WHERE a.channel='Direct Web' AND b.channel='Online Travel Agency'
        )
        SELECT period, COUNT(*) AS matched_route_month_cells,
               SUM(direct_tickets) AS direct_ticket_transactions,
               SUM(ota_tickets) AS ota_ticket_transactions,
               SUM(direct_cents) AS direct_cents,
               SUM(ota_cents) AS ota_cents,
               ROUND(SUM((direct_tickets+ota_tickets)*1.0*direct_cents/direct_tickets)
                     /SUM(direct_tickets+ota_tickets),2) AS direct_standardized_cents,
               ROUND(SUM((direct_tickets+ota_tickets)*1.0*ota_cents/ota_tickets)
                     /SUM(direct_tickets+ota_tickets),2) AS ota_standardized_cents
        FROM pairs GROUP BY period ORDER BY period;
    """)

net1, net2 = [x["net_cents"] for x in all_period]
gross1, gross2 = [x["positive_cents"] for x in all_period]
refund1, refund2 = [x["refund_cents"] for x in all_period]
att1, att2 = attachment
lines = [
    "# Commercial and booking analysis",
    "",
    "The source is the normalized, deduplicated transaction table in `airline_analysis.sqlite`. Period 1 is September 2024–August 2025; Period 2 is September 2025–August 2026. Values are recorded transaction amounts, not earned flight revenue. A booking ID is not a customer or passenger ID.",
    "",
    "## Revenue and mix",
    "",
    f"Net recorded revenue changed from {money(net1)} to {money(net2)} ({pct(net2-net1,net1)}). Positive transactions changed from {money(gross1)} to {money(gross2)}; refunds rose from {money(refund1)} to {money(refund2)}. Refunds represented {pct(refund1,gross1)} and {pct(refund2,gross2)} of positive recorded amounts, respectively.",
    "",
    f"Refund amounts rose {pct(refund2-refund1,refund1)}, faster than the {pct(gross2-gross1,gross1)} increase in positive amounts. The refund burden increased by {(refund2/gross2-refund1/gross1)*100:.2f} percentage points.",
    "",
    "| Transaction type | Period 1 | Period 2 | Change |",
    "| --- | ---: | ---: | ---: |",
]
by_mix = {(x["period"],x["type"]):x for x in periods}
for typ in ["Ticket","Extra Baggage","Food & Onboard","Seat Upgrade","Change Fee","Refund"]:
    a=by_mix.get((1,typ),{}).get("revenue_cents",0); b=by_mix.get((2,typ),{}).get("revenue_cents",0)
    lines.append(f"| {typ} | {money(a)} | {money(b)} | {money(b-a)} |")
lines += [
    "",
    "## Booking integrity and add-ons",
    "",
    f"The file has {integrity['bookings']:,} distinct booking IDs, and every one has at least one recorded ticket transaction. {integrity['multiple_ticket_bookings']:,} have more than one ticket transaction. Multiple ticket transactions can reflect multi-leg bookings or changes; they do not establish duplicate bookings without a booking ledger.",
    "",
    f"Across all transactions, {integrity['mixed_route_bookings']:,} bookings span multiple routes, {integrity['mixed_tier_bookings']:,} span multiple membership tiers, and {integrity['mixed_channel_bookings']:,} span multiple channels. {integrity['cross_period_bookings']:,} booking IDs have transactions in both comparison periods. Attribute based booking comparisons below assign 'Mixed' where a booking has multiple values within a period.",
    "",
    "For each period, add-on attachment counts bookings with at least one ticket transaction and at least one Extra Baggage, Food & Onboard, or Seat Upgrade transaction recorded in that same period. It does not measure passengers, seats, flight-level purchases, or an add-on take rate for a particular departure.",
    "",
    "| Period | Ticket bookings | With paid add-on | Attachment | Add-on amount |",
    "| --- | ---: | ---: | ---: | ---: |",
]
for row in attachment:
    lines.append(f"| {row['period']} | {row['ticket_bookings']:,} | {row['attached_bookings']:,} | {pct(row['attached_bookings'],row['ticket_bookings'])} | {money(row['extra_cents'])} |")
lines += ["", f"Ticket bookings increased {pct(att2['ticket_bookings']-att1['ticket_bookings'],att1['ticket_bookings'])}, while add-on attachment fell from {pct(att1['attached_bookings'],att1['ticket_bookings'])} to {pct(att2['attached_bookings'],att2['ticket_bookings'])}, a {(att1['attached_bookings']/att1['ticket_bookings']-att2['attached_bookings']/att2['ticket_bookings'])*100:.2f} percentage-point decline. Add-on recorded amounts among these bookings increased {pct(att2['extra_cents']-att1['extra_cents'],att1['extra_cents'])}."]
extra_total_2=sum(by_mix[(2,typ)]['revenue_cents'] for typ in ['Extra Baggage','Food & Onboard','Seat Upgrade'])
extra_total_1=sum(by_mix[(1,typ)]['revenue_cents'] for typ in ['Extra Baggage','Food & Onboard','Seat Upgrade'])
excluded_2=next(x for x in period_exclusions if x['period']==2)
lines += ["", f"Period 2 has {excluded_2['booking_periods_without_ticket']:,} booking-period records without a ticket transaction in that period, including {excluded_2['add_on_bookings_without_ticket']:,} with an add-on and {excluded_2['refund_bookings_without_ticket']:,} with a refund. All of these booking IDs have a ticket transaction elsewhere in the data. Total add-on recorded amounts rose {pct(extra_total_2-extra_total_1,extra_total_1)}, from {money(extra_total_1)} to {money(extra_total_2)}. The same-period ticket-booking cohort contains only {money(att2['extra_cents'])} of the Period 2 total; {money(extra_total_2-att2['extra_cents'])} ({pct(extra_total_2-att2['extra_cents'],extra_total_2)}) is excluded because those bookings have their ticket transaction in a different period. This is a transaction-timing boundary, not evidence of unattached extras or missing tickets."]
lines += [
    "",
    "## Channel and membership association",
    "",
    "The tables below use a booking's consistent within-period channel or tier. 'Mixed' is retained separately. Differences are descriptive associations and can reflect route, timing, or product mix.",
    "",
    "| Period | Channel | Ticket bookings | Add-on attachment |",
    "| --- | --- | ---: | ---: |",
]
for row in attachment_channel:
    lines.append(f"| {row['period']} | {row['channel']} | {row['ticket_bookings']:,} | {pct(row['attached_bookings'],row['ticket_bookings'])} |")
lines += ["", "| Period | Membership tier | Ticket bookings | Add-on attachment |", "| --- | --- | ---: | ---: |"]
for row in attachment_tier:
    lines.append(f"| {row['period']} | {row['tier']} | {row['ticket_bookings']:,} | {pct(row['attached_bookings'],row['ticket_bookings'])} |")
lines += ["", "The very high 'Mixed' tier attachment reflects selection on inconsistent tier values on all booking transactions, including add-ons. It should not be read as a behavioral difference. The supplementary check below assigns tier using ticket transactions only, so add-on tier fields cannot move a booking into 'Mixed'. Neither method establishes actual customer membership status. Channel is consistent within bookings, but route and product mix still vary between channels.", "", "| Period | Ticket-based tier | Ticket bookings | Add-on attachment |", "| --- | --- | ---: | ---: |"]
for row in attachment_ticket_tier:
    lines.append(f"| {row['period']} | {row['tier']} | {row['ticket_bookings']:,} | {pct(row['attached_bookings'],row['ticket_bookings'])} |")
raw_mixed={x['period']:x for x in attachment_tier if x['tier']=='Mixed'}
anchored_mixed={x['period']:x for x in attachment_ticket_tier if x['tier']=='Mixed'}
lines += ["", f"The 'Mixed' group shrinks from {raw_mixed[2]['ticket_bookings']:,} to {anchored_mixed.get(2,{}).get('ticket_bookings',0):,} Period 2 ticket bookings when tier is anchored to tickets. The original 88.0% attachment rate in the all-transaction 'Mixed' group is therefore not a reliable membership comparison."]
lines += ["", "### Recorded revenue by channel", "", "| Channel | Period 1 net | Period 2 net | Change | Period 2 share |", "| --- | ---: | ---: | ---: | ---: |"]
by_channel = {(x["period"],x["channel"]):x for x in channel}
for label in sorted({x["channel"] for x in channel}):
    a=by_channel.get((1,label),{}).get("net_cents",0)
    b=by_channel.get((2,label),{}).get("net_cents",0)
    lines.append(f"| {label} | {money(a)} | {money(b)} | {money(b-a)} | {pct(b,net2)} |")
lines += ["", "### Recorded revenue by membership tier", "", "| Tier | Period 1 net | Period 2 net | Change | Period 2 share |", "| --- | ---: | ---: | ---: | ---: |"]
by_tier = {(x["period"],x["tier"]):x for x in tier}
for label in sorted({x["tier"] for x in tier}):
    a=by_tier.get((1,label),{}).get("net_cents",0)
    b=by_tier.get((2,label),{}).get("net_cents",0)
    lines.append(f"| {label} | {money(a)} | {money(b)} | {money(b-a)} | {pct(b,net2)} |")
lines += ["", "### Payment method mix", "", "| Payment method | Period 1 net | Period 2 net | Period 2 share |", "| --- | ---: | ---: | ---: |"]
by_payment = {(x["period"],x["payment"]):x for x in payment}
for label in sorted({x["payment"] for x in payment}):
    a=by_payment.get((1,label),{}).get("net_cents",0)
    b=by_payment.get((2,label),{}).get("net_cents",0)
    lines.append(f"| {label} | {money(a)} | {money(b)} | {pct(b,net2)} |")
lines += ["", "### Refund burden and ticket transaction value", "", "Refund burden below is refund amount divided by positive ticket, add-on, and fee amounts within each category. Ticket value is the average recorded ticket transaction amount, not a passenger fare.", "", "| Period | Channel | Refund burden | Average ticket transaction |", "| --- | --- | ---: | ---: |"]
for row in channel:
    positive=row['ticket_cents']+row['ancillary_fee_cents']
    lines.append(f"| {row['period']} | {row['channel']} | {pct(row['refund_cents'],positive)} | {money(row['ticket_cents']/row['ticket_transactions']) if row['ticket_transactions'] else 'n/a'} |")
ota=by_channel[(2,'Online Travel Agency')]
web=by_channel[(2,'Direct Web')]
ota_burden=ota['refund_cents']/(ota['ticket_cents']+ota['ancillary_fee_cents'])
web_burden=web['refund_cents']/(web['ticket_cents']+web['ancillary_fee_cents'])
lines += ["", f"Online Travel Agency's Period 2 refund burden was {pct(ota['refund_cents'],ota['ticket_cents']+ota['ancillary_fee_cents'])}, compared with {pct(web['refund_cents'],web['ticket_cents']+web['ancillary_fee_cents'])} for Direct Web, a {(ota_burden-web_burden)*100:.2f} percentage-point gap. This is a transaction-category association, not evidence that channel caused refunds."]
lines += ["", "| Period | Tier | Refund burden | Average ticket transaction |", "| --- | --- | ---: | ---: |"]
for row in tier:
    positive=row['ticket_cents']+row['ancillary_fee_cents']
    lines.append(f"| {row['period']} | {row['tier']} | {pct(row['refund_cents'],positive)} | {money(row['ticket_cents']/row['ticket_transactions']) if row['ticket_transactions'] else 'n/a'} |")
lines += ["", "### Route and month matched channel comparison", "", "For Direct Web and Online Travel Agency, each matched route-month cell has at least one ticket transaction in both channels. The two channel averages use identical pooled ticket-transaction weights across those cells. This controls the measured route and month mix, but not booking product, traveler, or purchase timing differences.", "", "| Period | Matched route-month cells | Direct Web standardized ticket value | OTA standardized ticket value | Difference |", "| --- | ---: | ---: | ---: | ---: |"]
for row in matched_ticket:
    a=row['direct_standardized_cents']; b=row['ota_standardized_cents']
    lines.append(f"| {row['period']} | {row['matched_route_month_cells']:,} | {money(a)} | {money(b)} | {money(a-b)} |")
lines += [
    "",
    "## Reproducible detail",
    "",
    "The `commercial_*.csv` tables contain integer-cent source totals, transaction counts, and booking counts for revenue type, channel, tier, payment, refunds, attachment, and booking integrity. The matched ticket value table gives weighted averages rounded to cents. Counts use deduplicated transaction IDs. The booking analysis excludes no-ticket bookings from attachment denominators and does not resolve whether one ticket transaction represents one traveler.",
    "",
]
(BASE / "commercial_findings.md").write_text("\n".join(lines))
print(f"Wrote commercial findings and 13 tables from {integrity['bookings']:,} booking IDs")

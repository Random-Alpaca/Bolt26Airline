"""Network totals, reconciliations, gate allocation and arithmetic sensitivities."""
import csv
import json
import sqlite3
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
TABLES = HERE / 'tables'


def read(name):
    with (TABLES / name).open(newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (TABLES / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def dollars(c):
    return f'{Decimal(c)/100:.2f}'


def money(s):
    return int(Decimal(s) * 100)


def main():
    con = sqlite3.connect(f'file:{HERE / "airline_analysis.sqlite"}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    gate = {int(r['period'][1]): money(r['network_gate_charge']) for r in read('gate_period.csv')}
    net = []
    pstats = {}
    for p in [1, 2]:
        t = dict(con.execute('''SELECT COUNT(*) tx,COUNT(DISTINCT booking_id) bookings,SUM(amount_cents) revenue,
          SUM(CASE WHEN type='Ticket' THEN 1 ELSE 0 END) ticket_transactions,
          SUM(CASE WHEN type='Ticket' THEN amount_cents ELSE 0 END) tickets,
          -SUM(CASE WHEN type='Refund' THEN amount_cents ELSE 0 END) refunds,
          SUM(CASE WHEN type IN ('Extra Baggage','Food & Onboard','Seat Upgrade') THEN amount_cents ELSE 0 END) extras,
          SUM(CASE WHEN type='Change Fee' THEN amount_cents ELSE 0 END) change_fees
          FROM transactions WHERE period=?''', (p,)).fetchone())
        costs = dict(con.execute('SELECT type,SUM(amount_cents) FROM costs WHERE period=? GROUP BY type', (p,)))
        t.update(cost=sum(costs.values()), fuel=costs['Fuel'])
        t['events'] = con.execute('SELECT COUNT(*) FROM cost_events WHERE period=?', (p,)).fetchone()[0]
        t['contribution'] = t['revenue'] - t['cost']
        pstats[p] = t
        net.append({'period': p, 'start': '2024-09' if p==1 else '2025-09', 'end':'2025-08' if p==1 else '2026-08',
          'net_revenue': dollars(t['revenue']), 'ticket_revenue': dollars(t['tickets']),
          'paid_extras': dollars(t['extras']), 'change_fees': dollars(t['change_fees']), 'refunds': dollars(t['refunds']),
          'recorded_cost': dollars(t['cost']), 'contribution_before_gates': dollars(t['contribution']),
          'margin_pct': f"{100*t['contribution']/t['revenue']:.4f}", 'unique_gate_charge_scenario': dollars(gate[p]),
          'contribution_after_gates_scenario': dollars(t['contribution']-gate[p]),
          'transactions': t['tx'], 'bookings':t['bookings'], 'ticket_transactions':t['ticket_transactions'], 'cost_events':t['events'],
          'revenue_per_cost_event': dollars(Decimal(t['revenue'])/t['events']),
          'cost_per_cost_event': dollars(Decimal(t['cost'])/t['events']),
          'ticket_transactions_per_cost_event': f"{t['ticket_transactions']/t['events']:.4f}",
          'revenue_uplift_for_recorded_breakeven_pct': f"{100*max(0,-t['contribution'])/t['revenue']:.4f}",
          'cost_reduction_for_recorded_breakeven_pct': f"{100*max(0,-t['contribution'])/t['cost']:.4f}"})
    write('network_period.csv', net)
    months = []
    for r in con.execute('SELECT month,period,SUM(amount_cents) revenue,COUNT(*) transactions FROM transactions GROUP BY month ORDER BY month'):
        cost, events = con.execute('SELECT SUM(amount_cents),COUNT(*)/4 FROM costs WHERE month=?',(r['month'],)).fetchone()
        months.append({'month':r['month'],'period':r['period'],'revenue':dollars(r['revenue']),'cost':dollars(cost),
          'contribution':dollars(r['revenue']-cost),'margin_pct':f"{100*(r['revenue']-cost)/r['revenue']:.4f}",
          'transactions':r['transactions'],'cost_events':events})
    write('network_monthly.csv', months)
    dup_by_year = defaultdict(int)
    dup_by_period = defaultdict(int)
    dup_count = defaultdict(int)
    for r in read('duplicate_transactions_removed.csv'):
        dup_by_year[r['Month'][:4]] += int(r['Amount_Cents'])
        p = 1 if r['Month'] < '2025-09' else 2
        dup_by_period[p] += int(r['Amount_Cents']); dup_count[p] += 1
    original = defaultdict(int)
    with (HERE.parent/'annual_route_revenue.csv').open(newline='') as f:
        for r in csv.DictReader(f):original[r['Year']] += money(r['Total_Revenue'])
    reconciliation = []
    for yr, total in con.execute('SELECT SUBSTR(date,1,4),SUM(amount_cents) FROM transactions GROUP BY 1'):
        assert original[yr]-dup_by_year[yr] == total
        reconciliation.append({'calendar_year':yr,'original_report_revenue':dollars(original[yr]),
          'duplicate_revenue_removed':dollars(dup_by_year[yr]),'analysis_revenue':dollars(total),'reconciles':True})
    write('source_reconciliation.csv', reconciliation)
    write('duplicate_effect_by_period.csv', [{'period':p,'rows_removed':dup_count[p],'net_revenue_removed':dollars(dup_by_period[p])} for p in [1,2]])

    # Match the cost agent's already documented equal gate allocations to route contribution.
    allocation = {(int(r['period'][1]),r['route_id']):money(r['allocated_gate_charge']) for r in read('costs_routes.csv')}
    route_gate = []
    for p, route, rev in con.execute('SELECT period,route,SUM(amount_cents) FROM transactions GROUP BY period,route'):
        cost = con.execute('SELECT SUM(amount_cents) FROM costs WHERE period=? AND route=?',(p,route)).fetchone()[0]
        charge = allocation[(p,route)]
        route_gate.append({'period':p,'route':route,'net_revenue':dollars(rev),'recorded_cost':dollars(cost),
            'contribution_before_gates':dollars(rev-cost),'equal_gate_allocation_scenario':dollars(charge),
            'contribution_after_allocated_gates_scenario':dollars(rev-cost-charge),
            'became_negative_with_gate_scenario':rev-cost >= 0 and rev-cost-charge < 0})
    write('gate_route_contribution_scenario.csv',route_gate)

    s=pstats[2]; base=s['contribution']; sens=[]
    effects=[('Baseline',0),('Net revenue +5%',s['revenue']*Decimal('.05')),
      ('Net revenue -5%',-s['revenue']*Decimal('.05')),('Recorded operating cost -5%',s['cost']*Decimal('.05')),
      ('Fuel cost +10%',-s['fuel']*Decimal('.10')),('Refund outflow -10%',s['refunds']*Decimal('.10')),
      ('Paid extras +10%',s['extras']*Decimal('.10')),
      ('Revenue +5% and recorded operating cost -5%',s['revenue']*Decimal('.05')+s['cost']*Decimal('.05'))]
    for label,effect in effects:
        sens.append({'period':2,'scenario':label,'contribution_change':dollars(effect),
          'contribution_before_gates':dollars(base+effect),
          'contribution_after_network_gates_scenario':dollars(base+effect-gate[2])})
    write('network_sensitivity.csv',sens)

    def bucket(d):
        if '2024-09-01' <= d[:10] <= '2025-08-31':return '1'
        if '2025-09-01' <= d[:10] <= '2026-08-31':return '2'
        return 'outside_observed_window'
    delta=defaultdict(int); monthly_delta=defaultdict(int)
    for r in read('uncertain_dates.csv'):
        amount=int(r['Amount_Cents'])
        assert con.execute('SELECT COUNT(*) FROM transactions WHERE tx_id=?',(r['Transaction_ID'],)).fetchone()[0]==1
        delta[bucket(r['Current_Date'])]-=amount
        delta[bucket(r['Alternative_Date'])]+=amount
        monthly_delta[r['Current_Date'][:7]]-=amount
        monthly_delta[r['Alternative_Date'][:7]]+=amount
    assert sum(delta.values())==0 and sum(monthly_delta.values())==0
    write('uncertain_dates_period_impact.csv',[{'period_bucket':k,'alternative_minus_baseline_revenue':dollars(v)} for k,v in sorted(delta.items())])
    write('uncertain_dates_month_impact.csv',[{'month':k,'alternative_minus_baseline_revenue':dollars(v)} for k,v in sorted(monthly_delta.items())])
    # Sanity checks bridge network, costs, gate and individual source aggregates.
    assert sum(x['revenue'] for x in pstats.values()) == con.execute('SELECT SUM(amount_cents) FROM transactions').fetchone()[0]
    assert sum(x['cost'] for x in pstats.values()) == con.execute('SELECT SUM(amount_cents) FROM costs').fetchone()[0]
    (HERE/'network_metrics.json').write_text(json.dumps(pstats,indent=2)+'\n')
    print('Network totals and scenarios reconcile. Wrote 9 tables.')


if __name__=='__main__':main()

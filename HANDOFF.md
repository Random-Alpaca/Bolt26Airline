# Handoff: NorthByte / BOLT UBC FirstByte 2026

Updated 2026-10-14. **The deck PDF is due Thu Oct 15, 11:59 PM.** Name it `[TeamName]_FirstByte2026.pdf`, PDF only, one upload, and no edits after submission. Presentation day is Sat Oct 17: 10 min plus 5 min Q&A.

Judging: Data Analysis 35% · Recommendation 35% · Presentation 30%.

Sources (outside this repo):
- `~/Downloads/FirstByte 2026 Case Package.pdf`
- `~/Downloads/FirstByte 2026 Data Dictionary.pdf`

## Where things are

| What | Where |
|---|---|
| Cleaned data, as SQLite | `analysis/airline_analysis.sqlite` (built by `analysis/prepare.py`) |
| Original analysis report (partly superseded, see "Corrections") | `analysis/REPORT.md` |
| Four-alternative sizing + decision matrix | `analysis/alternatives.py` → `analysis/tables/alternatives_matrix.csv`, `decision_matrix.csv` |
| Deck template (27 slides, Google Slides-importable) | `slides/NorthByte_FirstByte2026_template.pptx` |
| Slide outline + timing + analysis TODOs | `slides/OUTLINE.md` |
| Draft charts | `analysis/charts/*.png` |
| Afternoon-flight deep dive (flex vs paired PM flights, YOW↔YYZ midday) | `analysis/afternoon.py` → `analysis/afternoon_findings.md`, `charts/11_afternoon_flights.png` |

Nothing from this session is committed yet. `slides/`, `HANDOFF.md`, `analysis/alternatives.py` and the two new tables are untracked.

## Data rules that matter

- Fiscal year runs Sep–Aug. P1 = FY24-25, P2 = FY25-26.
- **Transaction_Date is the purchase date. Cost_Date is the flight date.** Use seasons rather than months for revenue timing.
- **One flight** = a route + timestamp with exactly 4 cost rows.
- **A ticket transaction is one passenger on one flight**, so tickets per flight works as a load proxy. There is no seat count.
- **The gate file repeats each gate's cost on every route row.** Count each physical gate once: $9.66M for the 2024-25 lease year and $9.88M for 2025-26.
- **Gate rule from the case:** split each airport's gate total across all flights departing that airport. Leases run Jan–Jan, and the 2026-27 records are missing.
- **Duplicates:** 1,856 duplicate transactions were removed (−$1.23M).
- **Connections:** 12,644 bookings are hub connections, and 268 are return trips.

## The story (verified)

1. **What happened.**
   - Revenue $180.6M → $190.0M (+5.2%). Flight costs $193.0M → $238.4M (+23.5%).
   - Contribution before gates went from −$12.4M to **−$48.4M**, and is about −$58.3M after gates.
   - The case's "~$40M" figure is our number with refunds excluded (−$40.5M).
   - Monthly margin was positive through Feb 2025 and negative every month from Mar 2025.
2. **Root cause.** Since Mar 2025 a **second rotation per operating day** has been flown on 10 trunk directions: YUL↔YVR, YHZ↔YYZ, YUL↔YYZ, YOW↔YYZ and YHZ↔YUL.
   - Over Sep–Feb, flights rose +101% while revenue rose only +3.1%. Unchanged routes grew revenue +4.0%.
   - Tickets per flight fell 44%. Fares fell about 8% across every channel.
   - There was no maturation in year 2: Apr–Aug tickets rose 0.1% on an identical schedule.
   - On one rotation these directions made +$1.15M (Sep 24–Feb 25). On two they lost −$23.8M in the same months a year later.
3. **Cost growth.** Of the +$45.4M, **about ⅔ is volume and mix ($30.1M)** and **⅓ is like-for-like cost per flight +7.1% ($15.3M)**.
   - Like-for-like means the same route and the same calendar month.
   - Fuel +8.7% and crew +8.5% like-for-like. The case's 3%/4% are network averages diluted by the cheap new routes.
   - The inflation was a one-time step and has been flat for about 12 months.
4. **The 3 new markets** (YOW↔YUL, YXU↔YYZ, YQM↔YHZ): revenue $5.0M against cost $15.2M. Cost coverage has been stuck at 32–34% for 12 months.
5. **Network.**
   - Montréal–Vancouver loses −$19.7M with 0 connecting passengers.
   - 22 directions lose money in all 4 seasons.
   - The network loss is flat across seasons, so the problem is not seasonal.
6. **Revenue side.**
   - Ancillaries are about 2% of revenue; +10% ≈ $0.4M.
   - Refunds rose from $6.7M to $7.8M.
   - OTA refund burden is 5.9% vs about 3.8% for direct channels.
   - **St. John's** routes refund 37–39% of revenue in winter. This is a disruption problem, not weak demand, and it is not an "Atlantic" problem.
   - Rewards tiers show no revenue premium.

## Alternatives & decision matrix (from `analysis/alternatives.py`)

| | Stay the Course | Fill the Planes | **Right-Size & Recover** | Shrink to Core |
|---|:-:|:-:|:-:|:-:|
| Gain, central | $0 | +$5.3M | **+$60.7M** | +$52.1M |
| After gates, central (range) | −$58.3M | −$53.0M (−$55.8 to −$28.2) | **+$2.4M** (−$16.1 to +$7.0) | −$3.3M |
| Airports / connecting revenue lost | 20 / $0 | 20 / $0 | **20 / $0** | 14 / $8.1M |
| Flights removed | 0 | 0 | 4,352 (28%) | 8,748 (56%) |
| Weighted score | 1.9 | 2.1 | **4.3** | 2.8 |

- **Weights:** Financial 30 (linear: −$58.3M = 1, break-even = 5), Evidence & reversibility 15, Speed 10, Communities 15, Customers 15, Employees 15. **Safety is a pass/fail screen.**
- **Shrink only wins if Financial is weighted at 71% or more**, and only if Right-Size gets 0% recapture.
- **Right-Size & Recover, schedule part:**
  - Remove the added rotations on 8 trunk directions: +$28.5M central.
  - Exit Montréal–Vancouver: +$19.7M.
  - Halve the 3 new markets: +$6.4M.
  - Halve Dec–Feb flights on Whitehorse/St. John's: +$0.9M (see decision 1 below).
- **Right-Size & Recover, revenue recovery levers** ($2.2M–8.3M, central about $5.2M, not additive at the high end):
  - restore trunk yield ($0.3–1.8M);
  - rebook-first for St. John's disruptions ($0.4–1.1M);
  - shift OTA bookings to direct ($0.2–0.8M);
  - hub connection marketing ($0.7–2.6M);
  - community-route fares ($0.4–1.2M);
  - transparent all-in fare bundles ($0.3–0.8M).
- **No-Regret layer (applies to every option):** release the 2 unassigned gates (Halifax A3, Ottawa A2, $0.43M) at the Jan 2027 renewal. Also restates the OTA and reliability items.
- **How to reject Fill the Planes:**
  1. Break-even needs **+25.5% revenue (+30.7% after gates)**: 4.5–5 years at record growth, with about **$130M more losses** along the way.
  2. The trunk already ran this experiment: more flights did not fill.
  3. Every revenue lever combined covers only a fraction of the gap: about $5M central, $30M at the ceiling.
  4. Raising fares 26% would break the "Everyday Value" value.
- **Framing:** "Fill the planes we keep, not the planes we added." Q&A rebuttals to the devil's-advocate arguments (maturation, business travellers, competition, fixed costs, connections, loyalty, inflation, "shrinking story") are below.

## Corrections: do NOT use these older claims

- "86% of cost growth is volume" (from `REPORT.md`) → use the ⅔ volume / ⅓ like-for-like split.
- "Atlantic winter refunds" → it's **St. John's**.
- "$190M further losses" → **about $130M**.
- "−0.9 price elasticity" → describe it as the observed ratio: fares −11% and tickets +11% vs the control routes, so revenue was flat.
- "$24–47M saving, $47M central" → $47M is the top of the range. With spill it is $43–46M. The $24M is a separate risk: 0% recapture, or partly fixed costs.
- "Keeping the PM flight protects $4M of connections" → not supported. Those flows existed before the PM flight.
- Ancillary ceiling: if every passenger bought a bag, seat and food, it covers **39%** of the gap, not 38%.
- Fare drop was "uniform across tiers and payment methods" → only true **across channels** (−7.6% to −9.7%).
- Ancillaries +10% = **$0.40M**, not $0.34M.

## Open decisions (team)

1. **Drop the Whitehorse/St. John's winter halving?** Recommended: yes.
   - It's worth only about $0.9M.
   - St. John's winter flights are among the fullest.
   - It hurts "Connecting Communities".
   - Rebook-first addresses the refunds instead.
   - Without it, the Right-Size central case is about +$1.5M after gates.
2. **Re-add trigger.** A direction earns back its second rotation at about **2× its one-rotation load** sustained for 6 months, at control-trend fares. The draft "18–19 tickets per flight" trigger would fire immediately.
3. **Kill trigger for the halved new markets**, e.g. exit if revenue/cost stays below 0.8 by Q4 FY26-27. Full exit is worth $10.3M vs $5.1–7.6M for halving.
4. Issues / Recs / Implementation / Risks slides: the user asked to leave these as placeholders until told otherwise. The alternatives work was explicitly requested.

## Still to do before submission

- [ ] **Gates (Q5):**
  - estimate the 2026-27 leases by airport;
  - pro-rate the calendar-year leases onto fiscal years;
  - allocate per the case rule (airport total ÷ departing flights).
  - Then replace the `GATES` placeholder in `alternatives.py`; currently it's the 2025-26 lease total.
- [ ] **Update the deck:**
  - slide 8 headline → ⅔ volume / ⅓ cost per flight;
  - slide 11 → trunk before/after chart, the key evidence;
  - Alternatives slide → the decision matrix;
  - Recommendation → bridge from −$58.3M through Right-Size, the levers and gates, to positive.
- [ ] **Rejection slide for Fill the Planes:** chart of each revenue lever's ceiling vs the gap.
- [ ] **Commit** this session's files.
- [ ] Optional appendix: Rewards cost via outside benchmarks. This is allowed if cited and labelled as an assumption; the organizers' contact is developer@boltubc.com.

## Q&A prep (verified answers)

- **"New flights take years to mature."**
  - Apr–Aug ran an identical schedule in both years, and tickets moved +0.1%.
  - The new markets plateaued at 32–34% cost coverage.
  - Concede that 18 months is short. The re-add trigger covers that.
- **"Costs are partly fixed."**
  - Recorded trunk cost per flight moved exactly with the control routes when frequency doubled.
  - Quote the range. Even the downside (~$25M) dwarfs any revenue lever.
- **"Business travellers need the PM flight."**
  - Corporate share of trunk tickets stayed flat (19.3%).
  - Corporate fares fell the most (−9.7%).
  - The data can't see contracts; concede that.
- **"Shrink has the more certain number."**
  - The financial results are within about $6M.
  - Shrink costs 6 airports, $8M of connecting revenue, and 56% of flights.
  - "Shrink cuts markets; the data says the problem was frequency."
- **"Does it meet 'sustainable profit'?"**
  - Right-Size alone is about −$3M after gates. With the recovery levers it is about +$2.4M.
  - Quote the range honestly.

## Agent outputs (raw, for reference)

These are session-temporary paths and may disappear:
- `/private/tmp/claude-501/-Users-jxue-Bolt26Airline/8954611d-2211-4024-8593-d2c6e409e531/tasks/w82oqnkx8.output`: the rebuttals, revenue levers and 56-claim verification.
- `.../tasks/wnmof5e9e.output`: the matrix critique and judge Q&A.
- `.../scratchpad/ftp_partial.json`: the Fill the Planes evidence tests 1–11.

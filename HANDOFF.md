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
| Slide builders (deck is generated, rerun after analysis changes) | `slides/build_*.py`, shared helpers `slides/deckkit.py`, `slides/finalize.py`, fit check `slides/check_fit.py`; how to rerun: `slides/OUTLINE.md` |
| Cross-check vs teammate repo (vvictort/firstByte-2026) | `analysis/teammate_crosscheck.md` |
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
   - Contribution before gates went from −$12.4M to **−$48.4M**, and is **−$58.4M after gates** (fiscal-year gate accrual $10.02M, see Q5 below).
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
   - Unit costs rose ~13–14% in monthly steps Jan–Jul 2025 on every route, then flat (not a single step). Like-for-like: fuel +$6.5M (+8.7%), crew +$5.7M (+8.5%), maintenance +$3.1M (+4.7%), food ~0; total $15.25M (shown as $15.3M so the ⅔ + ⅓ split adds to $45.4M).
4. **The 3 new markets** (YOW↔YUL, YXU↔YYZ, YQM↔YHZ): revenue $5.0M against cost $15.2M. Cost coverage has been stuck at 32–34% for 12 months.
5. **Network.**
   - Montréal–Vancouver loses −$19.7M with 0 connecting passengers.
   - 22 directions lose money in all 4 seasons.
   - The network loss is flat across seasons, so the problem is not seasonal.
6. **Revenue side.**
   - Ancillaries are about 2% of revenue; +10% ≈ $0.4M.
   - Refunds rose from $6.7M to $7.8M.
   - OTA refund burden is 5.8% vs 3.7% for direct channels (on gross revenue).
   - **St. John's** routes refund about 37% of revenue in winter (Dec–Feb, 36–39% depending on the measure). This is a disruption problem, not weak demand, and it is not an "Atlantic" problem.
   - Rewards tiers show no revenue premium.

## Alternatives & decision matrix (from `analysis/alternatives.py`)

| | Stay the Course | Fill the Planes | **Right-Size & Recover** | Shrink to Core |
|---|:-:|:-:|:-:|:-:|
| Gain, central | $0 | +$5.3M | **+$59.8M** | +$52.1M |
| After gates, central (range) | −$58.4M | −$53.1M (−$55.9 to −$28.3) | **+$1.4M** (−$16.9 to +$5.7) | −$3.4M |
| Airports / connecting revenue lost | 20 / $0 | 20 / $0 | **20 / $0** | 14 / $8.1M |
| Flights removed | 0 | 0 | 4,296 (27%) | 8,748 (56%) |
| Weighted score | 1.9 | 2.1 | **4.3** | 2.8 |

- **Weights:** Financial 30 (linear: −$58.4M = 1, break-even = 5), Evidence & reversibility 15, Speed 10, Communities 15, Customers 15, Employees 15. **Safety is a pass/fail screen.**
- **Shrink only wins if Financial is weighted at 70% or more**, and only if Right-Size gets 0% recapture. Right-Size beats Shrink after gates once ≥60% of the trunk revenue moves to the kept flights.
- **Right-Size & Recover, schedule part:**
  - Remove the added rotations on 8 trunk directions: +$28.5M central.
  - Exit Montréal–Vancouver: +$19.7M.
  - Halve the 3 new markets: +$6.4M.
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
- Ancillary ceiling: if every ticket bought a bag, seat and food, the gain is **+$19.8M**: 34% of the −$58.4M gap after gates, or 41% before gates. The older "39%" mixed bases (gross $23.1M vs the after-gates gap). See `slides/OUTLINE.md`, "Rejecting Fill the Planes: ancillary evidence".
- Fare drop was "uniform across tiers and payment methods" → only true **across channels** (−7.6% to −9.7%).
- Ancillaries +10% = **$0.40M**, not $0.34M.

## Key-issues re-verification (2026-10-14)

All Slide 17 numbers were re-verified. Corrections and the non-overlapping Theme 1 table are in `slides/OUTLINE.md`, "Verification notes". The main points:
- the −$29.0M covers 4 markets (Montréal–Toronto, Halifax–Toronto, Halifax–Montréal, Ottawa–Toronto). It is not the 8-direction set in `afternoon_findings.md`;
- the fare drop is trunk-only, Sep–Feb;
- the cost rise was a ramp from Jan to Jul 2025, not a single step;
- **halving the new markets still loses about −$2.6M at 0.65 coverage**, so the 0.8 kill trigger in decision 3 fires immediately.

## Open decisions (team)

1. ~~Drop the Whitehorse/St. John's winter halving?~~ **Decided 2026-10-15: dropped.** Removed from `alternatives.py`; Right-Size central is now +$1.52M after gates. Slides 17–18 are rebuilt by `slides/build_issues_alternatives.py`.
2. **Re-add trigger.** A direction earns back its second rotation at about **2× its one-rotation load** sustained for 6 months, at control-trend fares. The draft "18–19 tickets per flight" trigger would fire immediately.
3. **Kill trigger for the halved new markets**, e.g. exit if revenue/cost stays below 0.8 by Q4 FY26-27. Full exit is worth $10.3M vs $5.1–7.6M for halving.
4. Issues slide is drafted in `slides/OUTLINE.md` ("Slide 17: Key issues"). Recs / Implementation / Risks slides: the user asked to leave these as placeholders until told otherwise. The alternatives work was explicitly requested.

## Still to do before submission

- [x] **Gates (Q5), done 2026-10-15** (`analysis/alternatives.py`; matches the teammate repo to the cent):
  - Lease years: $9.664M (2024) → $9.878M (2025), +2.2%. Calendar 2026 estimated at **$10.096M** (each gate repeats its 2024→25 % increase; flat-rate floor $9.878M).
  - Fiscal-year accrual: FY24-25 $9.807M, **FY25-26 $10.023M** (4/12 of the 2025 lease + 8/12 of the 2026 estimate). After gates: **−$58.4M**.
  - Per-airport allocation (airport total ÷ departing flights) is on the gates slide (`slides/build_gates.py`).
- [ ] **Update the deck:**
  - slide 8 headline → ⅔ volume / ⅓ cost per flight;
  - slide 11 → trunk before/after chart, the key evidence;
  - Alternatives slide → the decision matrix;
  - Recommendation → bridge from −$58.4M through Right-Size, the levers and gates, to positive.
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
  - Corporate trunk fares fell in line with the other channels (−8.2% like-for-like). The raw −9.7% comes from route mix, so don't say "fell the most".
  - The data can't see contracts; concede that.
- **"Shrink has the more certain number."**
  - The financial results are within about $6M.
  - Shrink costs 6 airports, $8M of connecting revenue, and 56% of flights.
  - "Shrink cuts markets; the data says the problem was frequency."
- **"Does it meet 'sustainable profit'?"**
  - The schedule changes alone get to about −$3.8M after gates. With the recovery levers (~$5.2M central) it is about +$1.4M, i.e. break-even, not a margin.
  - It is contribution after gates: aircraft ownership and overhead are not in the data.
  - Quote the range honestly.

## Agent outputs (raw, for reference)

These are session-temporary paths and may disappear:
- `/private/tmp/claude-501/-Users-jxue-Bolt26Airline/8954611d-2211-4024-8593-d2c6e409e531/tasks/w82oqnkx8.output`: the rebuttals, revenue levers and 56-claim verification.
- `.../tasks/wnmof5e9e.output`: the matrix critique and judge Q&A.
- `.../scratchpad/ftp_partial.json`: the Fill the Planes evidence tests 1–11.

# FirstByte 2026 deck outline: NorthByte Airlines

**Due:** Thu Oct 15, 11:59 PM · PDF only · `[TeamName]_FirstByte2026.pdf` · one upload, no edits after.
**Talk:** 10 min + 5 min Q&A. **Scoring:** Data Analysis 35% · Recommendation 35% · Presentation 30%.

Template: [NorthByte_FirstByte2026_template.pptx](NorthByte_FirstByte2026_template.pptx). In Google Slides: *File → Import slides* or upload to Drive → *Open with Google Slides*. Each slide's speaker notes say what goes there, the timing, and open TODOs. Dashed grey boxes are placeholders. Embedded charts are drafts from `analysis/charts/`.

## Storyline (Pyramid: answer first)

> NorthByte's losses come mainly from **flying ~20% more flights after the spring 2025 expansion without matching revenue**. The losses are concentrated in a few hub-to-hub markets. Fuel and crew prices, refunds and Rewards are real costs, but each is an order of magnitude smaller.

| # | Slide | Guiding Q | Time | Status |
|---|---|---|---|---|
| 1 | Title | | 0:15 | Team name |
| 2 | Executive summary | all | 0:45 | Findings drafted; recs box empty |
| 3 | Situation & key question | | 0:40 | Drafted |
| 4 | Data & approach | | 0:40 | Drafted; gate step needs redo |
| 5 | *Divider: What happened* | | | Optional |
| 6 | What changed: revenue vs cost bridge | Q1 | 0:50 | Drafted |
| 7 | When it turned: monthly margin | Q1 | 0:50 | Drafted |
| 8 | Why costs rose: volume vs price | Q1, Q3 | 1:00 | Drafted (key insight) |
| 9 | *Divider: Where money is lost* | | | Optional |
| 10 | Network: route/market P&L | Q2 | 1:00 | Drafted; redo after gates |
| 11 | The expansion: new routes vs added frequency | Q1, Q2 | 0:45 | **Analysis needed** |
| 12 | *Divider: What else matters* | | | Optional |
| 13 | Refunds, Rewards, ancillaries, connections | Q3, Q4 | 1:00 | Partial; **analysis needed** |
| 14 | Gate leases + 2026-27 estimate | Q5 | 0:45 | **Analysis needed** |
| 15 | Root-cause synthesis (driver ranking) | Q3 | 0:30 | Placeholder |
| 16 | *Divider: What NorthByte should do* | | | Optional |
| 17 | Key issues | | 0:40 | **Built** (`build_issues_alternatives.py`); not yet visually checked |
| 18 | Alternatives (scoring matrix) | | 0:45 | **Built** (`build_issues_alternatives.py`); not yet visually checked |
| 19 | Recommendation: short/long term + stakeholder effects | Q6 | 1:15 | **Placeholder** |
| 20 | Implementation roadmap + KPIs | | 0:45 | **Placeholder** |
| 21 | Risks & mitigation | | 0:30 | **Placeholder** |
| 22 | Thank you | | | |
| 23–27 | Appendix: cleaning, heatmap, sensitivity, channels | | Q&A | Drafted |
| 28 | Appendix: Strategic lens (Five Forces + SWOT) | | Q&A | **Built**; not yet visually checked |

That's about 12:45 as drafted, roughly 3 minutes over. Delete the dividers, merge slides 3 and 4, and fold slide 15 into slide 17 to land at 10.

## Slide 17: Key issues (draft, absorbs slide 15)

**What "issues" means here.** The case asks for a deck of *"analysis of the issues, possible alternatives, and final recommendation(s)"*. So an issue is a problem NorthByte must solve, and it sits between the analysis and the alternatives:

- **The loss is a symptom, not an issue.** The issues are the causes behind it that management can act on.
- **Each issue is sized in $** and ranked. Guiding question 3 asks "which factors matter most", so the order is part of the answer.
- **Issues should be MECE** (no overlaps, nothing missing), and each one maps to a later recommendation. An issue with no fix, or a fix with no issue, means something is wrong.
- **State the non-issues too.** The case plants likely suspects: fuel/crew, refunds, Rewards, loyalty spending. Saying with numbers that they are small is itself an insight.
- **NorthByte's values are decision criteria, not issues.** They belong on the Alternatives slide (safety screen, communities, Everyday Value).

**Problem statement (top of slide).** NorthByte added capacity faster than demand. On record revenue ($190.0M, +5.2%) it lost −$48.4M before gates (−$58.3M after), nearly four times the prior year (−$12.4M). Flights +20.3%, tickets +5.2%.

Three themes, which split cleanly into: **what NorthByte flies**, **what each flight earns and costs**, and **how those decisions get made**.

| Theme | What's behind it | Size (FY25-26) | → Fix |
|---|---|---:|---|
| **1. Capacity outran demand** | **Added afternoon flights on 4 trunk markets** (Montréal–Toronto, Halifax–Toronto, Halifax–Montréal, Ottawa–Toronto). From Mar/Apr 2025, each got one afternoon flight paired with every morning flight on every day it operates. Ottawa–Toronto also got a midday flight. Trunk Sep–Feb year over year: flights +101%, revenue +3.1% (unchanged routes +4.0%), tickets per flight −44%. The 2,265 added flights cost $28.5M and brought in about $0 of extra revenue. Before 2025, afternoon flights were added selectively (about 15% of days, weighted to summer and December), and those routes make +$4.3M.<br>**Montréal–Vancouver.** Loses money in every season and every month of FY25-26, with 0 connecting passengers.<br>**The 3 new markets.** About 3 tickets per flight against about 10 needed to break even. They recover a third of their cost every month (32.7%). | −$29.0M<br><br><br><br>−$19.7M<br><br>−$10.3M<br><br>**≈ −$59M**<br>(rest of network +$10.6M) | Remove the added rotations (flex re-add trigger); exit Montréal–Vancouver; halve the new markets, with a kill trigger. **Check:** halving still loses about −$2.6M (coverage 0.65), so a 0.8 kill trigger fires on day one. See open decision 3 |
| **2. Each flight earns less and costs more** | **Cost per flight rose about 13–14%** on every route in monthly steps, Jan–Jul 2025, and has been flat since (Jul–Aug 2026 −0.6% YoY). In the fiscal-year bridge that shows as +7.1% like-for-like (fuel +8.7%, crew +8.5%). The case's 3%/4% are network averages diluted by the cheap new routes; excluding them it is +9.2% / +9.6%.<br>**Trunk fares fell about 8%** in every channel (−7.6% to −9.7%, Sep–Feb YoY), in the same month each market's flights doubled. Other routes rose about 3%. The extra seats sold only at lower fares.<br>**Revenue lost after the sale.** Refunds $6.7M → $7.8M (like-for-like +8–10%, about 4% of revenue). St. John's refunds about 37% of its winter revenue. OTA refunds 5.8% of revenue vs 3.7% for direct channels. | $15.3M (⅓ of cost growth; about $6.5M of it sits inside theme 1)<br><br>part of theme 1<br><br>about $2M addressable (St. John's ~$1.9M, OTA ~$0.8M; overlapping) | Cost: absorbed once capacity is right-sized, not a lever on its own. Revenue: restore trunk fares; rebook-first for disruptions; shift OTA bookings to direct |
| **3. Decisions made without route-level visibility** | Case p.10: finance "reviewed costs at the company level, by category, rather than route by route". Case p.8: company-wide reports "have not made it clear where the money is being lost". The company-level indicators looked benign: fuel per flight +3.1%, crew per flight +4.1%. *Our inference, supported by data:* the routes that were doubled already had weaker margins before (5.4% vs 12.3%), and Ottawa–Toronto ranked 46th of 50 on tickets per flight yet got the largest increase. The Mar–Aug 2026 schedule repeats 2025 almost flight for flight (8,051 of 8,183) after 17–19 straight loss-making months. | Root cause of theme 1: the 16 added directions lose about −$4.9M a month, −$86M cumulative to Aug 2026 | Route-level P&L; capacity add/remove triggers |

**Not the problem (one line at the bottom):**
- **Rewards:** no fare premium. Every tier is within 0.3% of $1,031 per ticket. The program's cost isn't visible in the data.
- **Ancillaries:** about 2% of revenue. Even world-class add-on revenue would cover about a quarter of the gap (see "Rejecting Fill the Planes").
- **Gates:** $9.66M → $9.88M (+2.2%, lease years), mostly fixed. Only $0.43M sits idle.
- **Seasonality:** every season loses $11–13M; even summer loses $11.1M.

**Headline:** *"The losses come from flights NorthByte added, not the routes it already flew. Prices, refunds and Rewards are an order of magnitude smaller."*

Numbers were re-verified on 2026-10-14 (independent recompute plus a skeptic pass; see "Verification notes" below). Theme 1 adds up to −$58.95M, which is more than the network loss. That works because the other 38 directions make +$10.6M (about +$5M after gates) and were profitable in all 24 months. Say this aloud, since Q2 asks whether some parts are carrying others. **Do not add theme 1 and theme 2 together:** about $6.5M of the cost step is already inside theme 1's route losses.

### Verification notes (re-check 2026-10-14)

Every number on Slide 17 was recomputed independently from `analysis/airline_analysis.sqlite` and the raw CSVs, then re-checked by a skeptic using different definitions. Scripts are in the session scratchpad and are not committed. FY25-26, before gates unless stated.

**Theme 1, non-overlapping breakdown (sums to the network loss):**

| Component | Directions | Contribution | of which added flights | Base schedule |
|---|---:|---:|---:|---:|
| Added PM rotations: Montréal–Toronto, Halifax–Toronto, Halifax–Montréal, Ottawa–Toronto | 8 | −$28.99M | −$28.49M (2,265 flights) | −$0.51M |
| Montréal–Vancouver | 2 | −$19.71M | −$18.77M (310 flights) | −$0.93M |
| 3 new markets | 6 | −$10.25M | — | — |
| **Theme 1** | 16 | **−$58.95M** | | |
| Rest of network | 38 | +$10.57M | | |
| **Network** | 54 | **−$48.38M** | | |

After gates (case rule, 2025-26 leases): the 4 markets −$31.4M, Montréal–Vancouver −$20.1M, new markets −$11.6M, rest +$4.9M, network −$58.25M. Keep issue sizes **before** gates, because gate costs don't fall when flights are cut.

**Traps a judge could catch:**
- **Two different "8 directions" sets are in circulation.** `afternoon_findings.md`'s "2025 added rotation" set (−$41.5M) includes Montréal–Vancouver and leaves out Ottawa–Toronto. Adding −$41.5M + −$19.7M + −$10.3M would count Montréal–Vancouver twice (−$71.5M). Always name the markets.
- **"Daily" is wrong.** These routes operate 112–361 days a year. The added PM flight runs on every operating day, not every calendar day.
- **"Fares −8%" holds only for the trunk, Sep–Feb year over year.** On the full fiscal year the trunk is −3.3% and the network is +0.35%.
- **The cost increase was not one step.** Cost per flight rose about 13–14% in six monthly increments, Jan–Jul 2025, on every route (spread under 1 point). It began before the expansion. Only Jul–Aug is directly observed as flat.
- **Like-for-like cost depends on the basis.** It is $15.3M at FY25-26 route-month weights, $12.3M on identical flights, and $26–28M at run-rate against fall-2024 unit costs. Footnote the basis.
- **The case's two loss figures don't agree with each other.** "~$40M" matches only the loss excluding refunds (−$40.5M, which would be 7× the prior year). "Four times" matches only with refunds included (3.9×).
- **The case says "spring 2025",** but London–Toronto launched Feb 1, 2025. The Feb→Mar jump is mostly added frequency on existing routes.

**Additional data worth using:**
- *Main slide or speaker notes:*
  1. **The staggered rollout works as a natural experiment.** Each group's fare fell about 10% against control in the exact month its flights doubled. The March group (Montréal–Toronto, Ottawa–Toronto) went 1.007 → 0.909. The April group stayed at 1.021 in March, then fell to 0.913 in April. This is the causal link between the added flights and the lower fares.
  2. **Each added trunk flight carried about 1.9 extra tickets; break-even is about 19.** Sep–Feb incremental revenue was −$0.20M against $23.1M of incremental cost.
  3. **The route data pointed the other way before the decision** (Sep 24–Feb 25). The routes later doubled had a 5.4% margin vs 12.3% for the rest. Ottawa–Toronto carried 9.5–10 tickets per flight, 46th–48th of 50, and got the largest increase.
  4. **The not-the-problem items are small against the −$36.0M decline:**
     - refunds −$1.15M;
     - Points + Cash at most +$1.33M;
     - ancillaries +$0.29M (they improved);
     - gates +$0.21M.
- *Q&A backup:*
  - **Reverting does not restore the old profit.** On one rotation the trunk would be −$0.80M in Sep–Feb FY25-26, vs +$1.15M a year earlier.
  - **Montréal–Vancouver: exit vs revert differs by only about $0.9M** ($19.7M vs $18.8M). The route is 9.4% of network revenue and 50.6% of Montréal's.
  - **Connection revenue at risk from the trunk cuts is about $0.18M a year.** The 268 return trips are all Ottawa–Toronto.
  - **Rewards:** Gold and Platinum members buy about 2× the seat upgrades, the only tier difference in the data.
  - **The data can't show** which departure a passenger took, booking lead time, or whether passengers shifted from AM to PM flights. Concede this.

## Issues: frameworks (SWOT, Porter's Five Forces)

**How the frameworks fit in.** A framework is a way to *find* and *check* the issues. It is not a slide of its own.
- **Five Forces** is the outside-in view. It explains *why* the market punished the expansion.
- **SWOT** is the bridge from the issues to the alternatives. Weaknesses and threats become the issues; strengths and opportunities become what the alternatives must protect or use.
- With 10 minutes and the deck already about 3 minutes over, neither gets a full slide.
  - Five Forces goes in as a strip on slide 17.
  - SWOT goes in as the 2×2 that opens slide 18 (Alternatives).
  - The full versions go in the appendix for Q&A.

**Rule:** use only the case package and our data. Assumption 11 says no outside market claims. Every force below cites the case text or one of our numbers. Points marked *(inference)* must be said as inference.

### Porter's Five Forces: Canadian domestic air (case p.7–10)

| Force | Strength | Evidence (case text / our data) | So what for NorthByte |
|---|:-:|---|---|
| **Rivalry** | High | "Dominated by two large national carriers," plus "a rotating group of smaller and low-cost airlines". Our data: trunk fares fell about 8% in every channel once frequency doubled. | The trunk (Montréal, Toronto, Vancouver, Ottawa, Halifax) is where a small carrier has the least pricing power *(inference: the large carriers fight hardest between big cities)*. Extra frequency there was met with lower fares, not new passengers. |
| **Buyer power** | High | "Price-sensitive travellers." OTAs sell 20% of ticket revenue ($38.9M) and carry the highest refund burden (5.8% vs 3.7% direct). On the trunk, corporate fares fell in line with other channels (−8.2% like-for-like). | Customers took the extra seats only at lower fares. Revenue +3.1% on +101% flights. |
| **Supplier power** | High | Fuel prices "volatile"; "a national pilot shortage has pushed up crew wages"; airport fees "among the highest in the world"; gates leased "whether or not those gates are busy". Our data: fuel +8.7% and crew +8.5% like-for-like, a one-time step. | Cost per flight is set outside NorthByte's control. **The only cost lever NorthByte holds is how many flights it flies.** |
| **Threat of new entrants** | Medium | Entry happens, but "several newer carriers … ambitious expansion plans, only to scale back or shut down within a few years". | **This is the warning story for the deck.** NorthByte's 2025 expansion follows the same pattern. Use it as the hook on slide 17 or 3. |
| **Substitutes** | Low | "Distances between cities are long"; flying "keeps smaller and northern communities linked". | Demand on community routes is captive and is NorthByte's strength. Driving and rail are realistic substitutes only on short corridors like Ottawa–Montréal *(inference)*, the new market with 2–3 tickets per flight. |

**One-line takeaway (the slide 17 strip):** *"In a market with strong rivals, price-sensitive buyers and powerful suppliers, a small carrier wins on network coverage, not on frequency. The 2025 expansion bet on frequency."*

### SWOT: NorthByte (internal = our data; external = case text)

| | Helpful | Harmful |
|---|---|---|
| **Internal** | **Strengths**<br>• The legacy network earns about +$10M outside the expansion. Legacy peak-day afternoon flights are profitable (+$4.3M).<br>• 12,644 hub connections: the network is worth more than the sum of its routes.<br>• Community routes larger airlines "overlook": captive demand. St. John's winter flights are among the fullest.<br>• Revenue at a record $190.0M (+5.2%), so demand exists. | **Weaknesses → issues**<br>• Capacity planned without route-level P&L (case p.10) → **Issue 3**<br>• Frequency added faster than demand: tickets per flight −44% on the trunk → **Issue 1**<br>• New markets cover only 32–34% of their cost → **Issue 1**<br>• Revenue lost after the sale: refunds $7.8M, St. John's winter, OTA → **Issue 2** |
| **External** | **Opportunities**<br>• Passenger numbers "at record highs" (case p.7).<br>• Release idle gates at the Jan 2027 renewal ($0.43M).<br>• Move bookings from OTAs to direct channels; grow connections.<br>• Peak-day flex flying (Jun–Aug, Dec): a proven model already in the data. | **Threats**<br>• Two dominant rivals plus low-cost carriers → fare pressure.<br>• Fuel volatility, the pilot shortage, airport fees: cost per flight keeps rising.<br>• Passenger protection rules and winter disruption → refunds in St. John's and the North.<br>• Rivals' loyalty spending (case p.8). Our data: tiers show no revenue premium, so matching them is not the fix. |

**How SWOT feeds the rest of the deck:**
- **Weaknesses** = the issues on slide 17. Each one is already sized there.
- **Strengths** = what every alternative must keep: hubs, connections, communities. This is why Shrink to Core scores low: it gives up 6 airports and $8.1M of connecting revenue.
- **Opportunities** = the revenue recovery levers and the flex re-add trigger in Right-Size & Recover.
- **Threats** = slide 21 (Risks): fuel, crew, and rival fare responses when NorthByte cuts frequency.

### Check: does each issue survive both frameworks?

| Issue (slide 17) | SWOT | Five Forces | Fix (slide 19) |
|---|---|---|---|
| 1. Capacity outran demand | Weakness | Rivalry + buyer power: extra frequency was met with lower fares | Right-size + flex re-add |
| 2. Each flight earns less and costs more | Weakness + Threat | Supplier power (cost); buyer power (fares, OTA) | Fare repair, rebook-first, OTA → direct. Cost: accept it, and fly fewer flights. |
| 3. Decisions made without route visibility | Weakness | — (internal) | Route-level P&L + triggers |
| *Not an issue:* Rewards, ancillaries, gates, seasonality | — | Rivals' loyalty spending is a threat, but the data shows no premium | No investment; say so |

No issue lacks a fix, and no fix lacks an issue, so the set is MECE.

## Rejecting Fill the Planes: ancillary evidence

One bar on the "each lever's ceiling vs the gap" chart, plus a Q&A answer. Benchmarks and sources are in `analysis/ASSUMPTIONS.md` #17. Outside figures are US$; we treat them one-for-one as an assumption.

**Headline:** "To close the gap with add-ons alone, every passenger would have to spend $329 on extras. That's 3× the best airline in the world."

| Scenario (FY25-26 ticket base, 187,718) | Per ticket | Gain vs today | Share of −$58.3M gap after gates |
|---|---|---|---|
| Today | $17.91 | — | — |
| Air Canada level (the North American laggard) | $28.54 | +$2.0M | 3% |
| Our take-rate targets (bags 35%, seats 15%, food 25%) | $29.63 | +$2.2M | 4% |
| Jet2.com, best in the world | $100.73 | +$15.5M | 27% |
| Every ticket buys a bag, seat and food at today's prices | $123.24 | +$19.8M | 34% (41% before gates) |
| **Needed to break even from add-ons alone** | **$328.50** | **+$58.3M** | 100%: 3.3× Jet2, 11.5× Air Canada |

**Why ancillaries don't rescue Fill the Planes:**
1. **They scale with passengers, not flights.** Doubling trunk frequency cut tickets per flight by 44%: it did not add passengers. More flights do not add add-on buyers, so this lever is just as available under Right-Size.
2. **Even a world-class result is a fraction of the gap.** Catching up to Air Canada is worth about $2M. Matching Jet2 is still only about a quarter of the gap.
3. **The size needed breaks the brand.** $329 of fees on a ~$1,033 ticket is low-cost-carrier unbundling, which conflicts with "Everyday Value."
4. **So we keep it, but under Right-Size:** take-rate improvements and transparent 3-tier bundles (already in the $2.2–8.3M recovery levers) on the planes we keep.

**Q&A, "airlines make 15–20% of revenue from add-ons, why not you?"**
- That share includes loyalty and co-brand credit-card revenue. Our Rewards tiers show no revenue premium, and there's no card in the data.
- Our three paid extras are directly comparable only to à la carte fees. On those, the realistic target is raising per-ticket spend about 60% to the Air Canada level, which is worth about $2M.

## Analysis still needed before the deck is final

1. **Gate allocation per case rule.** Split each airport's total evenly across **all flights departing that airport**. `analysis/costs_gates.py` currently splits equally across listed routes.
2. **Gate fiscal pro-rating.** Leases run Jan–Jan, but the fiscal year runs Sep–Aug. FY24-25 = ⅓ of lease 2024-25 + ⅔ of lease 2025-26. FY25-26 = ⅓ of lease 2025-26 + ⅔ of **estimated** 2026-27.
3. **Estimate 2026-27 gate costs** by airport. State the method on the slide.
4. **Reconcile with the case's numbers.**
   - The case says FY25-26 lost "about $40M" on flights; we get −$48.4M.
   - The case says losses started in Feb 2025; our Feb 2025 shows a +4.5% margin and the first loss is in March.
   - Explain these differences or adopt the case's figures. Don't silently contradict the client.
5. **Check per-flight fuel and crew costs against the case.** The case says fuel per flight rose about 3% and crew per flight about 4%; check this against our cost per flight by category.
6. **Expansion split:** the 3 new connections versus added frequency on existing routes (slide 11).
7. **Refunds by region × winter months.** The case hints at Atlantic Canada and the North.
8. **Size the cost of the Rewards program.** Points + Cash is 10.6% of revenue; look at the tier mix.
9. **Connecting passengers.** Find out which bookings span multiple routes, what share of revenue they are, and which hubs they connect through.
10. **Driver ranking** in dollars against the $36M decline, for slide 15.

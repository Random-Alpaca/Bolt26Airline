# Key Issues number check: final synthesis (FirstByte 2026, NorthByte)

All figures are FY25-26 and before gates unless stated. I ran my own spot-checks against `analysis/airline_analysis.sqlite` (read-only); the scripts are in `/private/tmp/claude-501/-Users-jxue-Bolt26Airline/7a52eac9-5db7-4a51-997e-3d7b9b2f380f/scratchpad/synth/` (`spot.py`, `spot2.py`). No repo files were modified.

## 1. Claim table

### Problem statement
| Claim | Slide | Verified | Verdict | Fix |
|---|---|---|---|---|
| Record revenue | $190.0M, +5.2% | $189.999M vs $180.630M, +5.19% (raw rebuild $190.001M) | Confirmed | none |
| Loss before gates | −$48.4M | −$48.377M (raw −$48.375M) | Confirmed | none |
| Loss after gates | −$58.3M | −$58.25M if lease labels are matched to fiscal years. Pro-rated by fiscal year with a 2026-27 trend estimate (+2.2%): −$58.40M | Depends on definition | If the deck estimates 2026-27 leases at about $10.1M, use "≈ −$58.4M" and footnote the pro-rating |
| "Four times the prior year" | 4× | 3.92× (−$12.36M → −$48.38M). After gates: 2.64× | Confirmed (rounded) | Say "nearly 4×". Call it a step change at the spring-2025 expansion: Sep–Feb accounts for 94% of the −$36.0M change, Mar–Aug only −$2.2M |
| About 20% more flights | ~20% | 13,072 → 15,729 flights (+20.3%) | Confirmed | none |

### Theme 1: capacity outran demand
| Claim | Slide | Verified | Verdict | Fix |
|---|---|---|---|---|
| "From Mar 2025" | Mar 2025 | 4 directions started in Mar 2025 (YUL↔YYZ, YOW↔YYZ); 6 started in Apr 2025 | Wrong detail | "From Mar/Apr 2025" |
| "8 trunk directions" | 8 | The −$29.0M covers YUL↔YYZ, YHZ↔YYZ, YHZ↔YUL and YOW↔YYZ. afternoon_findings' "8" is a different set: it swaps YOW↔YYZ for YUL↔YVR | Wrong label | Name the 4 markets |
| "Daily afternoon flight paired with every morning flight" | daily | Exactly 1 PM flight per AM flight on every day the route operates. Operating days per direction: 112–361 a year. Only YOW↔YYZ is near-daily, and it also gained a 12:00 midday flight | Wrong wording | "an afternoon flight on every day the route operates" |
| Flights +101%, revenue +3.1%, unchanged routes +4.0%, tickets per flight −44% | as shown | Exact for the **10** trunk directions (+100.8% / +3.07% / +3.99% / −43.7%). On the 4-market set: +100.9% / +3.7% / −43.7% | Confirmed, but wrong set | Label as "10 trunk directions", or switch to the 4-market figures |
| Pre-2025 afternoon flights "only on peak days" and "profitable" | +$4.3M | +$4.29M is whole-route contribution. These flights run on 15.4% of operating days, 52.7% of them in Jun–Aug/Dec, with no holiday or weekday pattern. 58% of the profit is Vancouver–Calgary, which has about 10 PM flights a year | Wrong | "selective, summer- and December-weighted afternoon flights; those routes make +$4.3M, mostly Vancouver–Calgary" |
| Size of the added-rotation issue | −$29.0M | −$28.99M = whole-route loss of the 4 markets | Number right, label wrong | See §2 |
| Montréal–Vancouver loss | −$19.7M | −$19.71M | Confirmed | none |
| Montréal–Vancouver loses in every season | every season | All 4 seasons and all 12 months negative in FY25-26. In FY24-25 it was positive in fall and winter | Confirmed | Add "in FY25-26" |
| Montréal–Vancouver connecting passengers | 0 | 0 | Confirmed | none |
| New markets: tickets per flight | "2–3" | 3.20 in FY25-26 (2.38 was the launch-ramp year); break-even is about 9.8 | Depends on definition | "about 3 per flight; break-even needs about 10" |
| New markets: cost coverage | 32–34%, 12 months | 31.6–33.6% by month; 32.7% for the year, identical in each market | Confirmed | Optionally "about one-third every month" |
| New markets loss | −$10.2M | −$10.25M | Minor difference | −$10.3M |
| Theme 1 total | ≈ −$59M | −$58.95M (raw −$58.97M) | Confirmed | Label "before gates" |
| Rest of network | +$10M | +$10.57M (raw +$10.55M) across 38 directions; about +$4.9M after gates. 12 of the 38 lose money | Depends on definition | "+$10M before gates (~+$5M after)" |
| Fix: "halve new markets, kill trigger at 0.8" | — | Halving at 100% recapture still loses −$2.64M, at 0.65 coverage, so the trigger fires on day one | Contradicted | Recommend a full exit (see §3) |

### Theme 2: each flight earns less and costs more
| Claim | Slide | Verified | Verdict | Fix |
|---|---|---|---|---|
| Cost per flight "stepped up once… then flat ~12 months" | one-time step | The rise was about +13.5% in 6 monthly increments, Jan–Jul 2025. Uniform across routes (SD under 1pp); began before the expansion. Jul–Aug 2026 is −0.6% YoY | Minor difference | "rose ~13–14% between Jan and Jul 2025 on every route; flat since" |
| Fuel and crew per flight, like-for-like | +8.7% / +8.5% | Exact at FY25-26 route-month weights. On identical flights: +8.0% / +7.9% | Depends on definition | Name the basis |
| Case's 3%/4% diluted by new routes | — | +3.09% / +4.05%. Excluding the new markets: +9.24% / +9.60% | Confirmed | none |
| Like-for-like cost share | $15.3M (⅓ of growth) | $15.25M (+7.07%) at FY25-26 weights. Same flights in both years: $12.34M (27%). Run-rate burden vs fall-2024 unit costs: $26–28M | Depends on definition | Footnote the basis |
| Fares −8% "in every channel" | −7.6% to −9.7% | Trunk only, Sep–Feb YoY: −8.17%. On the full year the trunk is −3.3%; the network is +0.35%; legacy routes are +3.3% | Depends on definition | "on the trunk, Sep–Feb year over year (~11% below other routes)" |
| "As more seats chased the same demand" | — | Trunk tickets rose +13% (control +1.4%), but revenue relative to control was flat (−1.3%) | Wrong wording | "extra seats sold only at lower fares; revenue no higher than on unchanged routes" |
| Refunds | $6.7M → $7.8M | $6.685M → $7.834M exact. About half the rise is a data-window artefact; like-for-like is +8–10% | Depends on definition | Add "like-for-like +8–9%, about 4% of revenue in both years" |
| St. John's winter refunds | 37–39% | 36.0–39.2% by measure; 37.1% pooled for Dec–Feb FY25-26 | Minor difference | "about 37%" |
| OTA refund burden | 5.9% vs 3.8% | 5.79% vs 3.68% on gross revenue (the repo table says 5.8% / 3.7%). 5.91% vs 3.76% on ticket revenue. Flat year over year | Depends on definition | 5.8% vs 3.7% |
| "About $1–2M" revenue lost after the sale | $1–2M | **No verifier checked this.** My spot-check below | Unverified | Define the figure (§4) |

### Theme 3: decisions made without route-level visibility
| Claim | Slide | Verified | Verdict | Fix |
|---|---|---|---|---|
| Finance reviewed costs at company level | quote | Exact, case p.10 | Confirmed | Restore "by category" |
| Nothing triggered a review | — | Our inference. Supporting data: 8,051 of the 8,183 Mar–Aug 2026 flights match 2025 exactly (route, date and time), after 17–19 straight red months on every added direction | Inference, supported | Label it as inference |
| "Root cause of theme 1" | unsized | Optional size: the 16 added directions lose −$4.91M a month; −$86.4M cumulative to Aug 2026 | n/a | Optional |

### Not the problem
| Claim | Slide | Verified | Verdict | Fix |
|---|---|---|---|---|
| Rewards tiers show no revenue premium | — | All tiers within 0.3% of $1,031 per ticket. Gold and Platinum buy about 2× the seat upgrades | Confirmed | Say "no fare premium" |
| Programme cost not visible | — | Confirmed: Non-Members pay with Points + Cash on 9.93% of tickets, and Points + Cash records the full fare | Confirmed | none |
| Ancillaries about 2%; +10% ≈ $0.4M | — | $0.40M uses the case's 4-stream base ($3.97M, 2.09%). The 3-type $3.36M base gives 1.77% and +$0.34M | Depends on definition | Use 4 streams throughout |
| Gates | $9.66M → $9.88M (+2.3%) | $9,664,400 → $9,877,700 = +2.21% | Minor difference | +2.2%, and label these as lease years (calendar 2024 / 2025) |
| Idle gates | $0.43M | $433,500 (Halifax A3 + Ottawa A2) | Confirmed | none |
| Seasonality flat | — | Seasons range −$11.1M to −$13.3M. Per flight, winter (−$3,572) is about 40% worse than summer (−$2,560) | Depends on definition | "every season loses $11–13M; even summer loses $11.1M" |

## 2. Afternoon-rotation size and Theme 1 double counting

**What each figure measures:**
| Figure | What it is | Use it? |
|---|---|---|
| −$28.99M | Whole-route loss of the 4 markets (YUL↔YYZ, YHZ↔YYZ, YHZ↔YUL, YOW↔YYZ): revenue $27.99M − cost $56.98M | Yes, labelled "these 4 markets lose" |
| −$28.49M | Cost of the 2,265 added flights in those markets. Revenue there grew +3.7% vs +3.3–4.0% on control routes, so these flights brought in about $0 of extra revenue. Ties exactly to the +$28.5M removal fix | **Most defensible issue size** |
| −$41.52M | Whole-route loss of the paired-8 set, which includes YUL↔YVR | Not an issue size; double counts YUL↔YVR |
| −$48.70M | Whole-route loss of all 10 trunk directions, morning flights included | Same problem |

**Recommendation:** size the issue at −$28.5M (cost of the added flights), or keep −$29.0M as the markets' total loss. In both cases, name the 4 markets.

**Double counting:** the ≈ −$59M does **not** double count Montréal–Vancouver, because the −$29.0M set excludes YUL↔YVR. The slide creates the risk by (a) using the "8 trunk directions… paired with every morning flight" label, which describes the set that includes YUL↔YVR, and (b) the −$41.5M in afternoon_findings. Adding −$41.5M + −$19.7M + −$10.3M would give −$71.5M, counting YUL↔YVR twice.

Theme 1 and Theme 2 also overlap by about **$6.5M**: $3.76M + $2.58M + $0.19M of the $15.25M cost step sits inside Theme 1's route losses. Do not add the two themes together.

**Non-overlapping Theme 1, before gates (my spot-check, SQLite):**
| Component | Directions | Total | Added flights | Base schedule |
|---|---|---|---|---|
| Added rotations: Montréal–Toronto, Halifax–Toronto, Halifax–Montréal, Ottawa–Toronto | 8 | −$28.99M | −$28.49M (2,265 flights) | −$0.51M |
| Montréal–Vancouver | 2 | −$19.71M | −$18.77M (310 flights) | −$0.93M |
| 3 new markets | 6 | −$10.25M | — | — |
| **Theme 1** | **16** | **−$58.95M** | | |
| Rest of network | 38 | **+$10.57M** (+$10.55M raw) | | |
| **Network** | 54 | **−$48.38M** | | |

A by-cause version that sums to the same total: all trunk added flights −$47.26M (2,575 flights) + trunk base schedules −$1.44M + new markets −$10.25M = −$58.95M.

After gates (case rule, 2025-26 leases): 4 markets −$31.4M, Montréal–Vancouver −$20.1M, new markets −$11.6M, rest +$4.9M, network −$58.25M. Keep issue sizes before gates, because gate costs don't fall when flights are cut.

The 38 "rest" directions were profitable in all 24 months (spot-checked).

## 3. Additional data points

**Main slide**
1. **The staggered rollout acts as a natural experiment.** Each group's fare fell about 10% against control in the exact month its capacity doubled. March group (YUL↔YYZ, YOW↔YYZ): fare index 1.007 → 0.909. April group: unchanged in March (1.021), then 0.913 in April. This is the causal link between the added flights and the fare cut.
2. **The added flights recovered about 0% of their cost.** Sep–Feb, 10 trunk directions: incremental revenue −$0.20M against incremental cost $23.13M. Each added flight brought about 1.9 extra tickets; break-even is about 19. This backs the 100%-recapture assumption and "keep none".
3. **Route data before the decision already pointed the other way.** In Sep 2024–Feb 2025, the directions that were later doubled ran a 5.4% margin vs 12.3% for the rest, and 16.46 vs 17.06 tickets per flight. Ottawa–Toronto carried 9.5–10.2 tickets per flight (ranked 46th and 48th of 50) and got the largest increase. This is the strongest Theme 3 evidence.
4. **Company-level indicators looked benign.** Fuel per flight +3.1%, crew per flight +4.1%, network cost per flight +2.6%. Meanwhile flights rose 20.3% and tickets only 5.2%. This explains why nothing triggered a review.
5. **The 16 added directions lose −$4.9M a month.** They were red from their first month (−$86.4M cumulative), while the rest of the network was profitable in every one of 24 months. Sizes Theme 3.
6. **Not-the-problem items sized against the −$36.0M decline:**
   - refunds: −$1.15M (3.2%);
   - Points + Cash: at most +$1.33M (3.7%);
   - ancillaries: +$0.29M, an improvement;
   - gates: +$0.21M.
7. **Exit the new markets rather than halving them.** Halving reaches only 0.65 coverage and still loses −$2.64M. A full exit gains +$10.25M and frees $0.69M of dedicated gates (London B1, Moncton B1, Montréal D3). Trade-off: airports served go from 20 to 18.

**Q&A backup**
- **Reverting does not restore the old profit.** On one rotation, Sep–Feb FY25-26 would be −$0.80M (vs +$1.15M a year earlier). For the full year: 4 markets −$0.51M, Montréal–Vancouver −$0.93M.
- **Montréal–Vancouver: exit vs revert is worth only about $0.9M** ($19.71M vs $18.77M), but the route is 9.4% of network revenue and 50.6% of Montréal's.
- **Connection revenue at risk is about $0.18M a year.** The 268 return trips are all Ottawa–Toronto (about $0.13M a year), against $6.98M a year of added Ottawa–Toronto flights.
- **The refund rise is partly a data-window artefact.** Sep 2024 refunds were $74k vs $528k in Sep 2025, so like-for-like growth is +8–10%.
  - Excess over the network refund rate: St. John's $1.87M; OTA $0.84M. These overlap, so do not add them.
- **The fare cut bought volume, not revenue.** Against control: fare −11.4%, tickets +11.4%, revenue −1.3%.
- **The cost step at run-rate is $26–28M**, compared with $15.3M in the year-over-year bridge.
- **The case's two loss figures are inconsistent.** "~$40M" matches only the refund-excluded loss (−$40.5M, which is 7.1× the prior year). "4×" matches only with refunds included (3.9×).
- **Calgary routes raised fares about 6% with no volume loss.** This supports the community-fare lever, but it is a correlation only.
- **Concede in Q&A:** the data cannot show the departure a passenger took, lead time, or whether passengers shifted from morning to afternoon flights.

## 4. Completeness and unresolved points

**Slide claims no verifier checked:**
- **"About $1–2M" (revenue lost after the sale).** Spot-check:
  - year-over-year refund rise: $1.15M recorded, about $0.6M like-for-like;
  - excess refunds vs network rates: St. John's $1.87M ($2.20M vs a 3.0% non-St. John's rate on $11.04M gross); OTA $0.84M (5.79% vs 3.68% on $39.7M).

  The range fits only as "addressable excess" (St. John's plus OTA, which overlap), not as change. Suggested label: "about $2M addressable (St. John's ~$1.9M, OTA ~$0.8M, overlapping)".
- **"Root cause of theme 1" and "nothing triggered a review"** are qualitative. Data supports them (item 5 in §3) but they must be presented as inference.

**Disagreements between verifiers:**
| Issue | Resolution |
|---|---|
| One-rotation trunk, Sep–Feb FY25-26: −$0.80M (A4) vs −$0.64M (capacity sweep) | **Spot-check: −$0.80M.** Revenue $22.15M − actual cost of base-time flights $22.95M. Use −$0.80M. I did not find how the −$0.64M was derived |
| Corporate fare, like-for-like: −8.0% (A7) vs −8.1% (unit sweep) | **Spot-check: −8.15%**, mid-pack (Web −7.68%, OTA −8.49%, Mobile −8.58%). Raw "fell the most (−9.7%)" is true only as a simple average driven by route mix. Drop "fell the most" from Buyer power |
| Calendar-2024 lease cost with no flights behind it: $675.5k (X3b) vs $319.1k (governance) | **Spot-check:** Montréal D3 2024-25 lease = $356.4k (YUL-YOW only). $319.1k is London + Moncton, the airports with zero departures (case airport rule); $675.5k adds D3 (gate-route view). Both are valid; the same static gate mapping repeats in both years, so do not claim gates were leased early |
| Feb 2025 margin after gates, case per-flight rule: +0.5% vs +0.7% | Not resolved. The gap comes from different lease bases for Feb (2024 lease scaled vs 2025 lease). Both are positive and the difference is immaterial; with flat monthly gates Feb is −1.5% |
| Like-for-like refund growth: +8.2%, +8.5%, +9.1%, +9.7% | Consistent; the window definitions differ. Use "+8–10%" |
| HANDOFF's "fare drop uniform only across channels" | The unit sweep finds it equally uniform across tiers (−7.6% to −9.0%) and payment methods. Not spot-checked; it does not affect the slide |

Two "8 directions" sets are in circulation across HANDOFF, afternoon_findings and alternatives_matrix. Every slide that says "8 directions" must name its markets.
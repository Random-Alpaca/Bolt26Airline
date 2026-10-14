# Route contribution and trend analysis

Run `python3 analysis/routes.py` from the repository root to reproduce the five `analysis/tables/routes_*.csv` tables from `analysis/airline_analysis.sqlite`. All amounts are in the source's unspecified currency. Period 1 is September 2024–August 2025; Period 2 is September 2025–August 2026. Contribution is net recorded transaction revenue less recorded Crew, Food, Fuel, and Maintenance costs, **before gates and all other unobserved costs**. The dates of transactions and costs do not establish flight-level profitability.

## Network result

| Measure | Period 1 | Period 2 | Change |
| --- | ---: | ---: | ---: |
| Net recorded revenue | 180,629,746.30 | 189,999,278.55 | +9,369,532.25 (+5.19%) |
| Four recorded cost types | 192,985,563.99 | 238,376,476.25 | +45,390,912.26 (+23.52%) |
| Contribution before gates | -12,355,817.69 | -48,377,197.70 | -36,021,380.01 |
| Contribution margin | -6.84% | -25.46% | -18.62 percentage points |
| Cost events (departure proxy) | 13,072 | 15,729 | +2,657 (+20.33%) |
| Directional routes below zero contribution | 24 of 54 | 28 of 54 | +4 |

The cost increase is the dominant arithmetic driver: fuel rose 16,121,247.14, crew 15,049,420.86, maintenance 13,003,356.24, and food 1,216,888.02. Cost per event rose from 14,763.28 to 15,155.22 (+2.65%), while revenue per event fell from 13,818.07 to 12,079.55 (-12.58%). These are descriptive ratios using a cost-event proxy, not fares, yields, passenger counts, or load factors. Growth in event count and route mix can move both ratios.

## Comparable route-months and expansion

All 54 directional routes appear in both full periods, but recorded cost-event coverage for six begins during Period 1: YXU–YYZ and its reverse in February 2025, YUL–YOW and its reverse in March, and YQM–YHZ and its reverse in April. The data do not establish actual route launch dates. Thus a full-period comparison overstates like-for-like exposure for these routes. Matching a route and calendar month only where cost events occur in both periods gives 612 route-month pairs. Matched revenue rose 6,995,337.98 (+3.87%), matched cost rose 38,102,040.68 (+19.74%), and matched contribution deteriorated 31,106,702.70. The 36 Period 2 route-months lacking a Period 1 cost-event counterpart contributed another -4,914,677.31 (revenue 2,374,194.27; cost 7,288,871.58), completing the -36,021,380.01 total change. The matched comparison controls route-month presence, not event intensity, aircraft, or timing between bookings and flights. [Detailed comparable-month table](tables/routes_comparable_months.csv).

## Where contribution deteriorated

| Directional route | Period 2 contribution | Change from Period 1 | Cost-event change |
| --- | ---: | ---: | ---: |
| YUL–YVR | -10,311,653.30 | -6,082,696.63 | 221 → 306 |
| YVR–YUL | -9,394,093.56 | -5,556,177.00 | 226 → 314 |
| YHZ–YYZ | -4,995,940.78 | -3,028,997.69 | 265 → 372 |
| YYZ–YHZ | -4,152,634.94 | -2,534,819.62 | 245 → 344 |
| YUL–YYZ | -4,364,368.14 | -2,438,209.96 | 476 → 628 |
| YYZ–YUL | -4,060,326.26 | -2,220,968.30 | 481 → 634 |

The two Vancouver–Montreal directions alone generated -19,705,746.86, or 32.3% of the gross losses on Period 2 loss-making routes. Their combined contribution deteriorated 11,638,873.63: combined revenue grew 403,325.52 while combined cost rose 12,042,199.15. The eight worst route deteriorations account for 25,700,555.34, or 71.3% of the network's 36,021,380.01 decline. [Route-period detail](tables/routes_period.csv) and [route changes](tables/routes_growth.csv) show the full distribution.

Twenty-six Period 2 routes had positive contribution totaling 12,557,385.03; the 28 negative routes lost 60,934,582.73. The leading positive routes were YYZ–YYC (+1,506,102.71), YYC–YVR (+1,248,195.19), YVR–YYC (+1,233,187.14), and YYC–YYZ (+1,197,785.45). The five largest routes by revenue represented 33.3% of Period 2 revenue (33.9% in Period 1), so revenue is concentrated but the deterioration is more concentrated in specific loss-making routes.

Both directions had the same contribution sign in all 27 reverse-direction pairs in Period 2 (25 of 27 in Period 1). The largest direction gap was YUL–YVR versus YVR–YUL at 917,559.74, much smaller than their combined 19,705,746.86 loss. This points to reviewing that two-way market's recorded economics before drawing conclusions about direction-specific pricing. Directional differences may still reflect booking timing, route mix, or data limits. [Direction table](tables/routes_direction.csv).

## Monthly pattern

The first six months of Period 1 (September 2024–February 2025) had positive monthly contribution; every month from March 2025 through August 2026 was negative, including all twelve Period 2 months. Period 2 monthly losses ranged from 3,460,012.25 (September 2025) to 4,583,812.83 (January 2026). Relative to the same month one year earlier, cost grew 27.1%–57.0% in September–March, while revenue grew 5.1%–10.3%; the cost comparison eased from April onward and was slightly negative by July–August 2026. The coverage ramp in Period 1 matters to these comparisons. Two years of records do not establish recurring seasonality. [Monthly route table](tables/routes_monthly.csv).

## Review priorities

1. Review Vancouver–Montreal, Toronto–Halifax, and Toronto–Montreal at the **two-way market** level. Reconcile cost-event growth, cost per event, schedule changes, and any omitted revenue timing before reducing or reallocating service.
2. Investigate the six routes whose recorded cost-event coverage begins during Period 1 separately. Their 36 unmatched Period 2 route-months contributed -4,914,677.31; do not evaluate them solely against a partial Period 1 baseline.
3. Investigate why event activity rose 20.33% while recorded revenue rose 5.19%, especially on the largest deteriorating routes. This is a review lead; the data do not provide passengers, capacity, flight IDs, or revenue-recognition dates needed to diagnose cause.
4. Use the separate gate scenario and any verified overhead before an investment or service decision. The primary contribution measure omits them and is not net profit.

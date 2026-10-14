# Cost activity and gate charges

Reproduce every table with `python3 analysis/costs_gates.py`. Source data: `costs.csv` and `gates.csv`. Assumptions, especially the meaning of a cost event and the illustrative gate-year mapping, are in `analysis/ASSUMPTIONS.md`. All amounts are in the source's unspecified currency.

## Operating costs grew mainly with recorded activity

| Measure | Sep 2024–Aug 2025 | Sep 2025–Aug 2026 | Change |
|---|---:|---:|---:|
| Complete cost events | 13,072 | 15,729 | +2,657 (+20.33%) |
| Crew, food, fuel, maintenance | 192,985,563.99 | 238,376,476.25 | +45,390,912.26 (+23.52%) |
| Cost per event | 14,763.28 | 15,155.22 | +391.94 (+2.65%) |

All 115,204 cost rows have unique `Cost_ID`s and form 28,801 `(Cost_Date, Route_ID)` events, each containing exactly one of each of the four categories. The cost file covers 54 directional routes. These events are an activity proxy, not confirmed flights or passenger counts.

Holding Period 1 cost per event fixed, 2,657 additional events explain **39,226,028.42 (86.4%)** of the total increase. The remaining **6,164,883.84 (13.6%)** reflects higher average cost per event, including any change in the mix of routes. This is an exact arithmetic decomposition with the first component rounded to cents; it does not isolate price inflation.

Fuel increased 16,121,247.14 (+24.04%), crew 15,049,420.86 (+25.20%), maintenance 13,003,356.24 (+22.27%), and food 1,216,888.02 (+15.56%). Food cost per event **fell** from 598.43 to 574.70; its total still rose because there were more events. [Category decomposition](tables/costs_decomposition.csv) gives the count and per-event components for every category.

## Growth is concentrated in a few directions

The four largest cost increases are YUL–YVR (+6,292,788.16), YVR–YUL (+5,749,410.99), YHZ–YYZ (+3,197,416.33), and YYZ–YHZ (+2,693,140.73). Together they account for **17,932,756.21, or 39.5%** of the network increase. The Montréal–Vancouver pair alone accounts for 12,042,199.15 (26.5%). For YUL–YVR, event count increased from 221 to 306; 5,129,444.15 of its 6,292,788.16 increase is attributable to event count under the same decomposition.

Several shorter routes had much larger *percentage* activity changes: Moncton–Halifax went from 144 to 336 events (+133.3%), Halifax–Moncton from 144 to 332 (+130.6%), Montréal–Ottawa from 280 to 546 (+95.0%), and Ottawa–Montréal from 284 to 544 (+91.5%). Those are material network mix changes and review leads, but the source cannot explain whether schedules, aircraft, reporting, or other conditions changed. [Route changes](tables/costs_route_changes.csv) and [route costs](tables/costs_routes.csv) contain every direction.

Monthly event counts range from 792 (February 2025) to 1,478 (July 2025 and July 2026). A month with fewer events can still have high cost per event: February 2026 had 1,103 events and 17,062.27 per event, the highest month in the file. Its counterpart in February 2025 had 792 events and 16,469.44 per event. These two years are too short to establish a recurring seasonal pattern. [Monthly costs](tables/costs_monthly.csv) shows all 24 months. [Largest individual events](tables/costs_top_events.csv) are listed for review; a large absolute event is not itself evidence of an error because routes have very different typical costs.

## Gate cost is charged by physical gate, with two unassigned gates

Each gate-year charge is repeated on every listed route using that city and gate. Deduplicating by `(City, Gate_Number, Year)` yields **34 physical gates** and 54 route assignments per period. Charges for all repeated rows agree. A simple sum of the 56 rows in each gate-year would count shared charges more than once: 17,423,300 versus the deduplicated 9,664,400 in 2024–2025, and 17,819,600 versus 9,877,700 in 2025–2026.

| Illustrative gate-period mapping | 2024–2025 → Period 1 | 2025–2026 → Period 2 |
|---|---:|---:|
| Network charge, unique gates | 9,664,400.00 | 9,877,700.00 |
| Equal allocation to listed routes | 9,238,700.00 | 9,444,200.00 |
| Unallocated: Halifax A3, Ottawa A2 | 425,700.00 | 433,500.00 |

Network gate charges increased **213,300 (+2.21%)**. The unallocated amounts remain network costs; a blank `Route_ID` does not imply a free gate. For each assigned gate, the illustrative route allocation divides its annual charge equally among distinct listed routes, distributing any leftover cents in route-code order. [Physical gate charges](tables/gate_charges.csv), [gate totals](tables/gate_period.csv), and the allocation in [route costs](tables/costs_routes.csv) permit reconciliation.

The gate labels are year ranges with no stated start or end dates. Mapping them to the two 12-month cost windows is therefore an **assumption**, and the equal allocation is a scenario rather than measured route use. Gate charges are excluded from the primary operating cost figures above. No revenue is analyzed here, and cost per event is not cost per passenger or per flight.

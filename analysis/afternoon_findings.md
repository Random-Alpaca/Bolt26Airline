# Afternoon flights

Reproduce with `uv run --with matplotlib python analysis/afternoon.py`; the chart is the only part that needs matplotlib. Outputs: [inventory](tables/afternoon_inventory.csv), [monthly](tables/afternoon_monthly.csv), and [chart](charts/11_afternoon_flights.png). An afternoon flight departs at 12:00 or later. Every departure in the data is at 06:30–08:00 or at 12:00–18:10. Contribution is before gates. **Revenue cannot be split between the AM and PM flights.** Transactions carry the route and the purchase date, not the flight. So each route's contribution is the test.

## Size

| | FY24-25 | FY25-26 |
|---|---:|---:|
| Afternoon flights | 2,784 of 13,072 (21%) | 4,756 of 15,729 (30%) |
| Afternoon flight cost | $29.4M | $59.5M |

The afternoon schedule grew by 1,972 flights, which is **74% of all flights added** (+2,657). Its cost rose by $30.1M.

## Four kinds of afternoon flight (FY25-26)

| Class | Directions | PM flights | PM cost | Route contribution | Share in peak months* | Tickets per flight, P1 → P2 |
|---|---:|---:|---:|---:|---:|---:|
| **Legacy flex**: pre-2025 peak-day extras | 8 | 433 | $2.4M | **+$4.3M** | 53% | 13.6 → 13.7 |
| **2025 added rotation**: one PM flight paired with every AM flight | 8 | 1,525 | $40.3M | **−$41.5M** | 37% | 14.8 → 11.6 |
| **YOW↔YYZ**: legacy flex plus a 2025 daily PM and a midday flight | 2 | 1,387 | $9.2M | −$7.2M | 37% | 6.7 → 5.4 |
| **New markets** (YOW↔YUL, YXU↔YYZ, YQM↔YHZ) | 6 | 1,411 | $7.6M | −$10.2M | 36% | 2.4 → 3.2 |

\*Peak months are Jun, Jul, Aug and Dec, which are 4 of 12 months (33%) of a flat schedule. The P1 → P2 tickets-per-flight values are full-year figures. The Sep–Feb same-window drop on the trunk is −44% (see HANDOFF).

- **Legacy flex.** These are YVR↔YYJ, YVR↔YLW, YEG↔YYC and YVR↔YYC/YYC↔YVR. Taken together, they are **6–21% of these routes' flights** depending on the month. The share follows demand: it is highest in Jul–Aug and in Dec. The monthly count varies a lot (CV 0.93). Tickets per flight held steady. Every one of these routes makes money.
- **2025 added rotations.** These are the other 8 trunk directions. From Mar/Apr 2025, each route got **exactly one PM flight for every AM flight**, so the afternoon share is 50.0% in every month and the monthly CV is 0.10. They flew regardless of season. All 8 directions lose money.
- **YOW↔YYZ** was a flex route before Mar 2025, with a 17:20 / 18:00 PM flight on 30–55% of days.
  - It then got a daily 16:20 / 17:00 flight.
  - It also got a **12:00 / 12:40 midday flight** that runs on exactly the same days as the legacy evening flight (equal monthly counts).
  - So on peak days it now flies 4 times. Two-thirds of its flights are in the afternoon.
- **New markets** launched with AM+PM from day one, a fixed 50/50 split. They carry 2–3 tickets per flight.

**PM flights cost the same as AM flights.** Average cost per flight on the same route is within 1% for every 2025-added direction. There is no off-peak discount, crew or otherwise. Each added flight costs a full flight.

## What it means for the story

1. **NorthByte already knew how to schedule afternoon flights. The 2025 change dropped that method.** On legacy routes a PM flight is added on peak days and those routes are profitable. In 2025 a PM flight was paired with every trunk AM flight all year, and those routes lose $48.7M (10 directions including YOW↔YYZ).
2. **This gives the re-add trigger (open decision 2) a ready model.** Give PM flights back first as **peak-day flex** (Jun–Aug, Dec, holiday weekends), not daily. Return to daily only at about 2× the one-rotation load. Slide line: *"Fly the afternoon when the afternoon flies."*
3. **YOW↔YYZ's midday flight is a third rotation that HANDOFF doesn't mention.**
   - `alternatives.py` already removes it, because it keeps only the times flown in Sep 24–Feb 25.
   - So the 8-direction trunk saving already includes it. **No number changes.**
   - The slide wording should say "added PM and midday flights", not "second rotation", for this pair.
4. **Q&A: "Afternoon flights serve business travellers."**
   - The legacy flex routes show an evening flight can work.
   - But the corporate share on the trunk is flat at 19.3%. The 2025 PM flights did not attract corporate demand; they spread the existing demand across more flights.

## Limits

- No seat counts and no flight-level revenue. AM and PM loads cannot be compared directly.
- The flex-schedule upside is not sized. Sizing it needs a peak-day demand estimate we don't have. Present it as a lower-risk way back, not as a dollar figure.

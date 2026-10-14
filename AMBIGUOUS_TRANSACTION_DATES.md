# Transaction dates requiring review

These 11 `TX99...` records have slash dates for which both M/D/Y and D/M/Y are valid. Their transaction IDs do not provide reliable date order. `transactions_cleaned.xlsx` currently uses the M/D/Y interpretation as the documented fallback. The Excel row numbers refer to the `transactions` sheet in `transactions.xlsx`.

| Excel row | Transaction ID | Route | Type | Amount | Original | Current M/D/Y date | Possible D/M/Y date |
| ---: | --- | --- | --- | ---: | --- | --- | --- |
| 40924 | TX9900426 | YYC-YWG | Ticket | $1,124.11 | 03/10/2026 09:41 | 2026-03-10 09:41 | 2026-10-03 09:41 |
| 41830 | TX9900250 | YUL-YYZ | Extra Baggage | $41.98 | 02/01/2025 17:22 | 2025-02-01 17:22 | 2025-01-02 17:22 |
| 79533 | TX9900416 | YYC-YQR | Ticket | $828.77 | 01/06/2025 22:29 | 2025-01-06 22:29 | 2025-06-01 22:29 |
| 81972 | TX9900256 | YXU-YYZ | Ticket | $451.42 | 08/11/2025 19:04 | 2025-08-11 19:04 | 2025-11-08 19:04 |
| 302498 | TX9900223 | YVR-YYJ | Ticket | $638.87 | 07/10/2025 03:59 | 2025-07-10 03:59 | 2025-10-07 03:59 |
| 364440 | TX9900811 | YYC-YWG | Ticket | $1,197.45 | 11/10/2024 08:06 | 2024-11-10 08:06 | 2024-10-11 08:06 |
| 371736 | TX9900353 | YYZ-YYC | Ticket | $1,375.65 | 05/07/2025 00:51 | 2025-05-07 00:51 | 2025-07-05 00:51 |
| 442334 | TX9900812 | YUL-YHZ | Ticket | $729.74 | 10/06/2025 06:01 | 2025-10-06 06:01 | 2025-06-10 06:01 |
| 490642 | TX9900257 | YOW-YYZ | Extra Baggage | $36.00 | 10/11/2024 23:08 | 2024-10-11 23:08 | 2024-11-10 23:08 |
| 503087 | TX9900181 | YUL-YYZ | Ticket | $721.45 | 02/11/2025 08:57 | 2025-02-11 08:57 | 2025-11-02 08:57 |
| 548264 | TX9900315 | YEG-YVR | Extra Baggage | $49.98 | 03/11/2025 10:18 | 2025-03-11 10:18 | 2025-11-03 10:18 |

## Effect on the current reports

- **Annual route revenue and profit:** No change. Each alternative has the same year, route, category, and amount, so changing the day/month interpretation has a $0 effect on `annual_route_revenue.csv` and `annual_route_profits.csv`. Costs are unaffected.
- **Monthly or daily reports:** The remaining dates could move $7,195.42 of recorded revenue between months. The largest single item is $1,375.65. This matters if a future report groups or filters by month or day.
- **Date-range check:** Unambiguous transaction dates run from 2024-09-01 through 2026-08-31. For TX9900426, the D/M/Y reading is 2026-10-03, after that range, while the current M/D/Y reading is inside it. This is a clue, not confirmation of the source format.

## Resolved

TX9900561 ($2,157.41, YYZ-YVR) was changed from 2024-04-09 to **2024-09-04 07:59** as requested. It is no longer counted among the unresolved dates. The change does not affect annual revenue or profit because the year remains 2024.

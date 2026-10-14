# Analysis assumptions

## Dates and reporting years

- **Annual reports use calendar years (January 1 through December 31).** The year comes from `Cost_Date` for costs and `Transaction_Date` for revenue. Profit joins those summaries by calendar year and `Route_ID`. The reports show only recorded data; they do not annualize partial years. The cost data spans September 2024 through August 2026.
- **Cost dates:** Every `Cost_Date` in `costs.csv` uses `YYYY-MM-DD HH:MM`. The cost report reads the year from that date.
- **Transaction dates:** `transactions.csv` contains `YYYY-MM-DD HH:MM`, `YYYY/MM/DD HH:MM`, and slash dates with the year last (`XX/XX/YYYY HH:MM`). `YYYY/MM/DD` is read as year/month/day. When both month/day/year and day/month/year are valid, the cleaner sorts known dates by `Transaction_ID` and selects the interpretation that falls between its nearest known ID neighbors, provided both neighbors are within three ID numbers. This resolves 7,972 ambiguous dates in the current workbook, including one that Excel had already stored as a date. For 11 records with inconclusive ID order, the fallback assumption is month/day/year. TX9900561 was explicitly corrected to 2024-09-04 07:59. If the first component exceeds 12, month/day/year is impossible, so the date is read as day/month/year (7,941 current workbook dates; for example, `26/08/2025`). `transactions_cleaned.xlsx` converts all text dates to Excel dates; `transaction_date_decisions.csv` records each interpretation and the ID neighbors used. The annual revenue report uses only the year, which is unaffected by the day/month choice.
- **Unresolved dates:** The 11 M/D/Y fallback records and their alternative dates are listed in `AMBIGUOUS_TRANSACTION_DATES.md`. Their date choice does not change the existing annual reports.
- **Monthly scenarios:** `monthly_revenue_scenarios.xlsx` compares the current ID-informed dates with two counterfactuals: every remaining ambiguous year-last slash date read as M/D/Y or as D/M/Y. Dates for which only one order is valid, ISO dates, and the confirmed TX9900561 correction stay fixed. Month is the calendar month of `Transaction_Date`; revenue categories and refund signs follow the annual revenue report. Every scenario retains the same route-year revenue totals.
- **Gate years:** `gates.csv` uses range labels such as `2024-2025`, not a single transaction date. We do not assume which calendar year or months each range covers. Gate costs are not included in the current annual cost or profit CSVs.

## Amounts

- Revenue includes all transaction categories. Refund amounts are negative and reduce `Total_Revenue`.
- `Profit` is `Total_Revenue` minus `Total_Cost`, where `Total_Cost` includes Crew, Food, Fuel, and Maintenance from `costs.csv`.

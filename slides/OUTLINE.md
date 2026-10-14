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
| 17 | Key issues | | 0:30 | **Placeholder (do not fill yet)** |
| 18 | Alternatives (scoring matrix) | | 0:45 | **Placeholder** |
| 19 | Recommendation: short/long term + stakeholder effects | Q6 | 1:15 | **Placeholder** |
| 20 | Implementation roadmap + KPIs | | 0:45 | **Placeholder** |
| 21 | Risks & mitigation | | 0:30 | **Placeholder** |
| 22 | Thank you | | | |
| 23–27 | Appendix: cleaning, heatmap, sensitivity, channels | | Q&A | Drafted |

That's about 12:45 as drafted, roughly 3 minutes over. Delete the dividers, merge slides 3 and 4, and fold slide 15 into slide 17 to land at 10.

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

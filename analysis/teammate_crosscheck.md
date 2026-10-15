# Cross-check against the teammate repo (vvictort/firstByte-2026), 2026-10-15

86 numbers on the Key issues, Alternatives and Strategic lens slides were compared with the teammate's `outputs/` tables and report. Every mismatch was then recomputed from both datasets.

**Result: no number on our slides is wrong on its stated basis.** Every gap traces to one of two definitional choices:

| Difference | Effect | What we did |
|---|---|---|
| **Dates.** The teammate reads all 7,902 ambiguous NN/NN/YYYY transaction dates day-first and drops 759 out-of-window rows. We use the ID-informed decisions (ASSUMPTIONS.md #2). | FY25-26 revenue −$0.29M on their side: $189.71M vs our $190.00M; −$48.67M vs −$48.38M before gates. Costs match to the cent. | Kept ours. Every route-group figure rounds the same on both sides (−$29.0M, −$19.7M, −$10.3M, −$59M). |
| **Gates.** The teammate accrues by fiscal year: Sep–Dec 2025 lease + Jan–Aug 2026 estimate = $10.02M. We had charged the calendar-2025 lease total of $9.88M. | −$0.15M after gates | **Adopted theirs:** it answers the case's 2026-27 question. `alternatives.py` now computes it, reproducing their $10.096M 2026 estimate and $10.023M FY25-26 accrual to the cent. After gates is **−$58.4M**; Right-Size is **+$1.4M** (−$16.9M to +$5.7M). |

Story-level differences to be ready for. Their report frames these differently; ours is not wrong, but say it this way:
- **Fuel and crew.** Their report says fuel and crew are 90% of the decline. That is by cost line. By cause, $19.0M of fuel+crew is flying more and $12.2M is higher cost per flight (same route and month). Both are true.
- **Route losses vs savings.** They say route losses are not closure savings. Our savings assume the four flight costs on removed flights are avoidable (case p.10). The slide 17 source line and notes disclose this: each 10% that proves fixed costs ~$7.4M.
- **Rewards.** Its cost is not in the data, so we now say "not measurable", not "not the problem".
- **Connections.** These are connection-compatible bookings (two chained tickets), inferred, not proven itineraries.
- **"Already loss-making."** Their "the doubled routes were already negative in FY24-25" holds only for the full year. All of that loss came after the Mar/Apr 2025 doubling; Sep–Feb they made +$1.15M.

**Thin central case** (Codex review plus our recompute): Right-Size breaks even only at about 90% trunk recapture. It beats Shrink above about ⅔ recapture. About 1% more cost per flight would erase it. Exiting the new markets instead of halving them would add about +$3.9M of buffer. That is an open team decision.

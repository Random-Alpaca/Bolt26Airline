# Commercial and booking analysis

The source is the normalized, deduplicated transaction table in `airline_analysis.sqlite`. Period 1 is September 2024–August 2025; Period 2 is September 2025–August 2026. Values are recorded transaction amounts, not earned flight revenue. A booking ID is not a customer or passenger ID.

## Revenue and mix

Net recorded revenue changed from $180,629,746.30 to $189,999,278.55 (5.2%). Positive transactions changed from $187,314,667.48 to $197,833,331.06; refunds rose from $6,684,921.18 to $7,834,052.51. Refunds represented 3.6% and 4.0% of positive recorded amounts, respectively.

Refund amounts rose 17.2%, faster than the 5.6% increase in positive amounts. The refund burden increased by 0.39 percentage points.

| Transaction type | Period 1 | Period 2 | Change |
| --- | ---: | ---: | ---: |
| Ticket | $183,640,795.69 | $193,866,920.15 | $10,226,124.46 |
| Extra Baggage | $2,001,639.26 | $2,139,239.17 | $137,599.91 |
| Food & Onboard | $435,546.30 | $493,660.50 | $58,114.20 |
| Seat Upgrade | $678,561.23 | $729,536.24 | $50,975.01 |
| Change Fee | $558,125.00 | $603,975.00 | $45,850.00 |
| Refund | -$6,684,921.18 | -$7,834,052.51 | -$1,149,131.33 |

## Booking integrity and add-ons

The file has 353,002 distinct booking IDs, and every one has at least one recorded ticket transaction. 13,149 have more than one ticket transaction. Multiple ticket transactions can reflect multi-leg bookings or changes; they do not establish duplicate bookings without a booking ledger.

Across all transactions, 12,912 bookings span multiple routes, 5,386 span multiple membership tiers, and 0 span multiple channels. 3,865 booking IDs have transactions in both comparison periods. Attribute based booking comparisons below assign 'Mixed' where a booking has multiple values within a period.

For each period, add-on attachment counts bookings with at least one ticket transaction and at least one Extra Baggage, Food & Onboard, or Seat Upgrade transaction recorded in that same period. It does not measure passengers, seats, flight-level purchases, or an add-on take rate for a particular departure.

| Period | Ticket bookings | With paid add-on | Attachment | Add-on amount |
| --- | ---: | ---: | ---: | ---: |
| 1 | 171,963 | 68,064 | 39.6% | $3,115,746.79 |
| 2 | 181,040 | 70,801 | 39.1% | $3,243,546.22 |

Ticket bookings increased 5.3%, while add-on attachment fell from 39.6% to 39.1%, a 0.47 percentage-point decline. Add-on recorded amounts among these bookings increased 4.1%.

Period 2 has 3,864 booking-period records without a ticket transaction in that period, including 3,317 with an add-on and 499 with a refund. All of these booking IDs have a ticket transaction elsewhere in the data. Total add-on recorded amounts rose 7.9%, from $3,115,746.79 to $3,362,435.91. The same-period ticket-booking cohort contains only $3,243,546.22 of the Period 2 total; $118,889.69 (3.5%) is excluded because those bookings have their ticket transaction in a different period. This is a transaction-timing boundary, not evidence of unattached extras or missing tickets.

## Channel and membership association

The tables below use a booking's consistent within-period channel or tier. 'Mixed' is retained separately. Differences are descriptive associations and can reflect route, timing, or product mix.

| Period | Channel | Ticket bookings | Add-on attachment |
| --- | --- | ---: | ---: |
| 1 | Corporate Portal | 30,614 | 39.0% |
| 1 | Direct Web | 69,333 | 39.5% |
| 1 | Mobile App | 37,442 | 39.9% |
| 1 | Online Travel Agency | 34,574 | 39.9% |
| 2 | Corporate Portal | 32,046 | 38.4% |
| 2 | Direct Web | 72,549 | 39.2% |
| 2 | Mobile App | 39,755 | 39.7% |
| 2 | Online Travel Agency | 36,690 | 39.0% |

| Period | Membership tier | Ticket bookings | Add-on attachment |
| --- | --- | ---: | ---: |
| 1 | Blue | 41,791 | 39.2% |
| 1 | Gold | 13,618 | 41.8% |
| 1 | Mixed | 2,603 | 87.3% |
| 1 | Non-Member | 84,365 | 38.7% |
| 1 | Platinum | 4,979 | 43.2% |
| 1 | Silver | 23,193 | 38.4% |
| 1 | Unknown | 1,414 | 0.9% |
| 2 | Blue | 44,112 | 38.3% |
| 2 | Gold | 14,225 | 41.7% |
| 2 | Mixed | 2,660 | 88.0% |
| 2 | Non-Member | 88,488 | 38.4% |
| 2 | Platinum | 5,288 | 42.9% |
| 2 | Silver | 24,724 | 38.0% |
| 2 | Unknown | 1,543 | 0.6% |

The very high 'Mixed' tier attachment reflects selection on inconsistent tier values on all booking transactions, including add-ons. It should not be read as a behavioral difference. The supplementary check below assigns tier using ticket transactions only, so add-on tier fields cannot move a booking into 'Mixed'. Neither method establishes actual customer membership status. Channel is consistent within bookings, but route and product mix still vary between channels.

| Period | Ticket-based tier | Ticket bookings | Add-on attachment |
| --- | --- | ---: | ---: |
| 1 | Blue | 42,108 | 39.6% |
| 1 | Gold | 13,763 | 42.4% |
| 1 | Mixed | 223 | 48.9% |
| 1 | Non-Member | 85,075 | 39.1% |
| 1 | Platinum | 5,023 | 43.6% |
| 1 | Silver | 23,360 | 38.8% |
| 1 | Unknown | 2,411 | 38.2% |
| 2 | Blue | 44,440 | 38.7% |
| 2 | Gold | 14,346 | 42.2% |
| 2 | Mixed | 219 | 49.8% |
| 2 | Non-Member | 89,237 | 38.8% |
| 2 | Platinum | 5,329 | 43.2% |
| 2 | Silver | 24,896 | 38.4% |
| 2 | Unknown | 2,573 | 37.0% |

The 'Mixed' group shrinks from 2,660 to 219 Period 2 ticket bookings when tier is anchored to tickets. The original 88.0% attachment rate in the all-transaction 'Mixed' group is therefore not a reliable membership comparison.

### Recorded revenue by channel

| Channel | Period 1 net | Period 2 net | Change | Period 2 share |
| --- | ---: | ---: | ---: | ---: |
| Corporate Portal | $32,909,409.77 | $34,680,822.14 | $1,771,412.37 | 18.3% |
| Direct Web | $72,994,983.52 | $76,277,709.49 | $3,282,725.97 | 40.1% |
| Mobile App | $39,187,753.35 | $41,631,925.45 | $2,444,172.10 | 21.9% |
| Online Travel Agency | $35,537,599.66 | $37,408,821.47 | $1,871,221.81 | 19.7% |

### Recorded revenue by membership tier

| Tier | Period 1 net | Period 2 net | Change | Period 2 share |
| --- | ---: | ---: | ---: | ---: |
| Blue | $44,089,824.79 | $46,539,527.97 | $2,449,703.18 | 24.5% |
| Gold | $14,576,177.99 | $15,155,761.20 | $579,583.21 | 8.0% |
| Non-Member | $89,541,768.74 | $93,715,001.97 | $4,173,233.23 | 49.3% |
| Platinum | $5,274,494.39 | $5,687,004.07 | $412,509.68 | 3.0% |
| Silver | $24,496,184.69 | $26,074,441.52 | $1,578,256.83 | 13.7% |
| Unknown | $2,651,295.70 | $2,827,541.82 | $176,246.12 | 1.5% |

### Payment method mix

| Payment method | Period 1 net | Period 2 net | Period 2 share |
| --- | ---: | ---: | ---: |
| Credit Card | $115,967,822.55 | $121,618,043.59 | 64.0% |
| Debit | $36,966,320.36 | $39,011,183.96 | 20.5% |
| Points + Cash | $18,833,062.05 | $20,195,648.07 | 10.6% |
| Travel Voucher | $7,359,595.97 | $7,644,971.62 | 4.0% |
| Unknown | $1,502,945.37 | $1,529,431.31 | 0.8% |

### Refund burden and ticket transaction value

Refund burden below is refund amount divided by positive ticket, add-on, and fee amounts within each category. Ticket value is the average recorded ticket transaction amount, not a passenger fare.

| Period | Channel | Refund burden | Average ticket transaction |
| --- | --- | ---: | ---: |
| 1 | Corporate Portal | 2.8% | $1,031.12 |
| 1 | Direct Web | 3.3% | $1,028.68 |
| 1 | Mobile App | 3.3% | $1,025.70 |
| 1 | Online Travel Agency | 5.1% | $1,032.26 |
| 2 | Corporate Portal | 2.9% | $1,037.30 |
| 2 | Direct Web | 3.7% | $1,031.38 |
| 2 | Mobile App | 3.7% | $1,031.81 |
| 2 | Online Travel Agency | 5.8% | $1,032.47 |

Online Travel Agency's Period 2 refund burden was 5.8%, compared with 3.7% for Direct Web, a 2.10 percentage-point gap. This is a transaction-category association, not evidence that channel caused refunds.

| Period | Tier | Refund burden | Average ticket transaction |
| --- | --- | ---: | ---: |
| 1 | Blue | 3.6% | $1,026.76 |
| 1 | Gold | 3.4% | $1,032.76 |
| 1 | Non-Member | 3.5% | $1,029.91 |
| 1 | Platinum | 3.7% | $1,025.72 |
| 1 | Silver | 3.6% | $1,029.73 |
| 1 | Unknown | 4.1% | $1,027.62 |
| 2 | Blue | 4.1% | $1,032.89 |
| 2 | Gold | 3.8% | $1,034.51 |
| 2 | Non-Member | 3.9% | $1,031.60 |
| 2 | Platinum | 3.6% | $1,039.08 |
| 2 | Silver | 4.0% | $1,033.84 |
| 2 | Unknown | 4.4% | $1,036.97 |

### Route and month matched channel comparison

For Direct Web and Online Travel Agency, each matched route-month cell has at least one ticket transaction in both channels. The two channel averages use identical pooled ticket-transaction weights across those cells. This controls the measured route and month mix, but not booking product, traveler, or purchase timing differences.

| Period | Matched route-month cells | Direct Web standardized ticket value | OTA standardized ticket value | Difference |
| --- | ---: | ---: | ---: | ---: |
| 1 | 612 | $1,028.26 | $1,033.20 | -$4.95 |
| 2 | 648 | $1,030.21 | $1,034.94 | -$4.73 |

## Reproducible detail

The `commercial_*.csv` tables contain integer-cent source totals, transaction counts, and booking counts for revenue type, channel, tier, payment, refunds, attachment, and booking integrity. The matched ticket value table gives weighted averages rounded to cents. Counts use deduplicated transaction IDs. The booking analysis excludes no-ticket bookings from attachment denominators and does not resolve whether one ticket transaction represents one traveler.

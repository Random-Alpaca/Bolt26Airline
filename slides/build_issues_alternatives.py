"""Fill deck slides 17 (Key issues) and 18 (Alternatives) and add an appendix slide (Strategic lens).

Run from the repo root:  uv run --no-project --with python-pptx python slides/build_issues_alternatives.py
Edits the deck (slides/deckkit.py: DECK, or NB_DECK) in place and is safe to rerun: each built slide is
reset to its frame (top bar, kicker, title, footer) before content is added. Numbers come from
analysis/tables/*.csv and the SQLite database, so rerun after alternatives.py changes.
"""
import copy
import csv
import sqlite3

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION, XL_TICK_MARK
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from deckkit import (BODY, DECK, FRAME, GREEN, HEAD, INK, LINE, MINUS, MUTED, NAVY, ORANGE, PANEL, ROOT, WHITE,
                     box, find_slide, money, reset, rule, text)

LENS_KICKER = "APPENDIX · STRATEGIC LENS"


def usd(x):
    """-58.4 -> '−$58.4M'"""
    m = money(x)
    return (m[0] + "$" + m[1:] if m[0] in "+" + MINUS else "$" + m) + "M"


# ---------- data
rows = list(csv.DictReader(open(ROOT / "analysis/tables/alternatives_matrix.csv")))
TOT = {r["alternative"]: r for r in rows if r["component"] == "TOTAL"}
DM = {r["criterion"]: r for r in csv.DictReader(open(ROOT / "analysis/tables/decision_matrix.csv"))}
ALTS = ["Stay the Course", "Fill the Planes", "Right-Size & Recover", "Shrink to Core"]
REC = "Right-Size & Recover"
# Trunk-only recapture thresholds (other assumptions central): trunk saving runs linearly from low (0%) to central (100%)
_trunk = next(r for r in rows if r["component"].startswith("Remove 2025 added"))
_span = float(_trunk["central_musd"]) - float(_trunk["low_musd"])
_rs, _sh = (float(TOT[a]["after_gates_central"]) for a in (REC, "Shrink to Core"))
CROSS = 1 - (_rs - _sh) / _span   # trunk recapture at which Right-Size matches Shrink (~66%)
BREAK_EVEN = 1 - _rs / _span       # trunk recapture at which Right-Size breaks even (~90%)

db = sqlite3.connect(ROOT / "analysis/airline_analysis.sqlite")
GROUPS = {
    "trunk": {"YHZ-YYZ", "YYZ-YHZ", "YUL-YYZ", "YYZ-YUL", "YOW-YYZ", "YYZ-YOW", "YHZ-YUL", "YUL-YHZ"},
    "mtl": {"YUL-YVR", "YVR-YUL"},
    "new": {"YOW-YUL", "YUL-YOW", "YXU-YYZ", "YYZ-YXU", "YQM-YHZ", "YHZ-YQM"},
}
contrib = {}
for route, cents in db.execute(
        "select route, sum(c) from (select route, amount_cents c from transactions where period = 2 "
        "union all select route, -amount_cents from costs where period = 2) group by route"):
    contrib[route] = cents / 1e8
grp = {k: sum(contrib[r] for r in v) for k, v in GROUPS.items()}
grp["rest"] = sum(contrib.values()) - sum(grp.values())
total = sum(contrib.values())
n_rest = len(contrib) - sum(len(v) for v in GROUPS.values())
assert abs(total - -48.38) < 0.01, total


# ---------- slide 17: key issues
def build_issues(s):
    reset(s, "KEY ISSUES",
          "The loss comes from flights NorthByte added in 2025, not the network it already flew",
          "Source: NorthByte transactions & costs, FY24-25 vs FY25-26; team analysis. "
          "Contribution = revenue − fuel, crew, maintenance, food (before gates).",
          NOTES_17)
    text(s, 0.6, 1.62, 12.1, 0.3, [[
        ("On record revenue ($190.0M, +5.2%), NorthByte lost ", {}),
        (f"{MINUS}$48.4M before gates ({usd(float(TOT['Stay the Course']['after_gates_central']))} after)", {"bold": True, "color": NAVY}),
        (", nearly 4× the year before.", {})]], size=14)

    # left: where the loss sits
    box(s, 0.6, 2.08, 4.55, 3.7, fill=PANEL)
    text(s, 0.8, 2.18, 4.2, 0.5, [[("Where FY25-26 contribution comes from", {"bold": True, "color": NAVY})],
                                  [("$M before gates, by route group", {"size": 10, "color": MUTED})]], size=12)
    cats = [f"Rest of network ({n_rest} directions)", "4 doubled trunk markets (8 directions)",
            "Montréal–Vancouver (2)", "3 new markets (6)", "Network total"]
    vals = [grp["rest"], grp["trunk"], grp["mtl"], grp["new"], total]
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series("Contribution", [round(v, 1) for v in vals])
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.7), Inches(2.72), Inches(4.35), Inches(3.0), cd)
    ch = gf.chart
    ch.has_legend = False
    ch.font.name, ch.font.size, ch.font.color.rgb = BODY, Pt(10), INK
    plot = ch.plots[0]
    plot.gap_width = 45
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format, dl.number_format_is_linked = '"+"0.0;"−"0.0', False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size, dl.font.bold = Pt(11), True
    ser = plot.series[0]
    ser.invert_if_negative = False
    for i, c in enumerate([GREEN, ORANGE, ORANGE, ORANGE, NAVY]):
        pt = ser.points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = c
    ca = ch.category_axis
    ca.reverse_order = True
    ca.tick_label_position = XL_TICK_LABEL_POSITION.LOW
    ca.format.line.color.rgb = LINE
    ca.major_tick_mark = XL_TICK_MARK.NONE
    ca.tick_labels.font.size = Pt(10)
    va = ch.value_axis
    va.visible = False
    va.has_major_gridlines = False
    va.minimum_scale, va.maximum_scale = -62, 18

    # right: three issues
    issues = [
        ("1", "Capacity outran demand", f"{MINUS}$59M", "contribution of the routes involved",
         "10 trunk directions, Sep–Feb: flights +101%, revenue +3.1% (other routes +4.0%), tickets/flight −44%. "
         "Montréal–Vancouver lost money all year. New markets cover a third of cost.",
         "→ Fix: right-size the schedule; re-add flights only on proven demand"),
        ("2", "Each flight earns less and costs more", "$15.2M", "cost rise, same route & month (⅓ of growth)",
         "Per flight, same route & month: fuel +8.7%, crew +8.5%, rising Jan–Jul 2025. Trunk fares −8% "
         "(Sep–Feb): extra seats sold only at lower fares. Refunds $6.7M → $7.8M.",
         "→ Fix: restore trunk fares, rebook-first for disruptions, shift OTA bookings to direct"),
        ("3", "Decisions without route-level numbers", f"{MINUS}$4.9M/mo", "lost by the 16 added directions",
         "Finance “reviewed costs at the company level, by category, rather than route by route” (case). "
         "Doubled routes already earned less (5.4% vs 12.3% margin); 2026 repeated the schedule.",
         "→ Fix: a route-level P&L with add/remove triggers"),
    ]
    y, h, gap = 2.08, 1.18, 0.08
    for num, head, stat, cap, body, fix in issues:
        box(s, 5.4, y, 7.33, h, fill=WHITE, line=LINE)
        circ = box(s, 5.55, y + 0.12, 0.42, 0.42, fill=ORANGE, shape=MSO_SHAPE.OVAL)
        circ.text_frame.text = num
        r = circ.text_frame.paragraphs[0].runs[0]
        r.font.name, r.font.size, r.font.bold, r.font.color.rgb = HEAD, Pt(14), True, WHITE
        circ.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        circ.text_frame.margin_left = circ.text_frame.margin_right = 0
        text(s, 6.12, y + 0.08, 4.7, 0.3, [head], size=14, bold=True, color=NAVY, font=HEAD)
        text(s, 6.12, y + 0.37, 4.75, 0.55, [body], size=10.5)
        text(s, 6.12, y + 0.9, 6.5, 0.24, [fix], size=10, bold=True, color=ORANGE)
        text(s, 10.95, y + 0.08, 1.68, 0.4, [stat], size=18, bold=True, color=NAVY, font=HEAD, align=PP_ALIGN.RIGHT)
        text(s, 10.95, y + 0.48, 1.68, 0.36, [cap], size=9, color=MUTED, align=PP_ALIGN.RIGHT)
        y += h + gap
    # strip: why the market punished it + what is not the problem
    box(s, 0.6, 5.86, 12.13, 0.5, fill=PANEL)
    text(s, 0.78, 5.9, 11.8, 0.44, [[
        ("Why the market punished it (Porter's Five Forces): ", {"bold": True, "color": NAVY}),
        ("among strong rivals and price-sensitive buyers (case), NorthByte's extra frequency sold only at lower fares; "
         "powerful suppliers set the cost of each flight. A small carrier wins on coverage, not frequency (our inference).", {})]],
        size=11, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.6, 6.48, 12.13, 0.4, [[
        ("Not the problem:  ", {"bold": True, "color": ORANGE}),
        ("Ancillaries (2% of revenue; +10% ≈ $0.4M)  ·  Gates (+2.2%, mostly fixed)  ·  Seasonality (every season "
         "loses $11–13M).   ", {}), ("Not measurable: ", {"bold": True, "color": ORANGE}),
        ("Rewards program cost (not in the data; no fare premium by tier)", {})]], size=11)
    return issues


NOTES_17 = """KEY ISSUES. ~40 sec.
Say: "Record revenue, but a loss nearly four times last year's. Three issues explain it, and they are not the ones leadership suspected."
1. Capacity outran demand. The chart is the whole story: the 16 directions NorthByte added or doubled in 2025 lose about $59M; the other 38 still make +$10.6M (about +$5M after gates) and were profitable in all 24 months. That answers Q2: the rest of the network still earns, but covers only about a fifth of the expansion's −$59M.
   The 4 doubled trunk markets are Montréal–Toronto, Halifax–Toronto, Halifax–Montréal and Ottawa–Toronto. Name them; do not say "8 directions" without naming them (afternoon_findings uses a different 8).
   The staggered rollout is strongly consistent with cause and effect: each group's fare fell ~10% against control routes in the exact month its flights doubled (purchase-month revenue, so say "consistent with", not "proves").
2. Each flight earns less and costs more. Per flight on the same route and month, fuel +8.7% and crew +8.5% ($12.2M together); with maintenance (+4.7%, $3.1M) all cost lines rose $15.2M on that basis ($12.3M on identical flights), rising Jan–Jul 2025 on every route, then flat. If asked "what about maintenance +$13.0M?": mostly volume; only $3.1M is per-flight, and it falls with the flights Right-Size removes. By cost line fuel+crew are $31.2M of the decline; by cause, $19.0M of that is flying more and $12.2M is higher cost per flight. Trunk fares fell ~8% Sep–Feb. Do NOT add issue 2 to issue 1: about $6.5M of the cost rise is already inside issue 1's route losses.
3. Root cause: costs were reviewed company-wide, by category (case p.10). The routes later doubled already had a 5.4% margin vs 12.3% elsewhere, and 8,051 of 8,183 Mar–Aug 2026 flights repeat 2025 exactly. "Nobody reviewed it" is our inference from that; say so if asked.
Close with the strip: Five Forces explains why frequency was the wrong bet (competitor response is our inference; the data only shows NorthByte's own fares). Ancillaries, gates and seasonality are each an order of magnitude smaller; Rewards' cost isn't in the data, so we don't size it.
If asked "is it ALL the expansion?": no. The 16 added directions explain ~90% of the decline (the 10 doubled trunk directions alone 78%); the other 38 directions also slipped $3.4M (+$14.0M → +$10.6M) on the per-flight cost step, and 12 of them lose money individually.
The case's "~$40M" is our −$48.4M with refunds excluded (−$40.5M). Refunds $6.7M → $7.8M is about +9% like-for-like (Sep 2024 is a low data month).
Sources: analysis/airline_analysis.sqlite; slides/OUTLINE.md "Verification notes"; cross-checked against the teammate repo (differences are only date parsing, ≤ $0.3M)."""


# ---------- slide 18: alternatives
DESC = {
    "Stay the Course": "Keep the 2025 schedule and absorb the loss",
    "Fill the Planes": "Keep every flight; grow revenue to fill the seats",
    REC: "Undo 2025 trunk add-ons, exit Montréal–Vancouver, halve 3 new markets, add revenue levers",
    "Shrink to Core": "Exit all 22 directions that lose money in every season",
}
CRIT = [("financial", "Financial", "30%"), ("evidence", "Evidence", "15%"),
        ("speed", "Speed", "10%"), ("communities", "Communities", "15%"),
        ("customers", "Customers", "15%"), ("employees", "Employees", "15%")]
SCALE = {1: "EEF1F5", 2: "D5DCE6", 3: "A9B6C9", 4: "4F6A8F", 5: "0B1F3A"}


def build_alternatives(s):
    reset(s, "ALTERNATIVES",
          "Right-Size & Recover is the only option whose central case breaks even, and it keeps all 20 airports",
          "Source: analysis/alternatives.py, FY25-26; gates accrued by fiscal year ($10.0M); flight costs "
          "avoidable (case p.10). Range: 0–100% recapture, levers low–high.",
          NOTES_18)
    widths = [2.95, 0.95, 0.95, 0.85, 0.98, 0.95, 0.95, 0.85, 2.7]  # = 12.13
    x0, y0, hh, rh = 0.6, 1.72, 0.6, 0.84
    tbl_gf = s.shapes.add_table(5, len(widths), Inches(x0), Inches(y0), Inches(sum(widths)), Inches(hh + 4 * rh))
    tbl = tbl_gf.table
    tbl.first_row = tbl.horz_banding = False
    for i, w in enumerate(widths):
        tbl.columns[i].width = Inches(w)
    tbl.rows[0].height = Inches(hh)
    for i in range(1, 5):
        tbl.rows[i].height = Inches(rh)

    def cell(r, c, paras, fill, size=11, color=INK, bold=False, align=PP_ALIGN.CENTER, font=BODY):
        ce = tbl.cell(r, c)
        ce.fill.solid()
        ce.fill.fore_color.rgb = fill
        ce.margin_left = ce.margin_right = Inches(0.06)
        ce.margin_top = ce.margin_bottom = Inches(0.04)
        ce.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = ce.text_frame
        tf.word_wrap = True
        for i, para in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            for t, o in ([(para, {})] if isinstance(para, str) else para):
                rr = p.add_run()
                rr.text = t
                f = rr.font
                f.name, f.size = o.get("font", font), Pt(o.get("size", size))
                f.bold, f.color.rgb = o.get("bold", bold), o.get("color", color)

    hdr = [("Alternative", None)] + [(lab, w) for _, lab, w in CRIT] + [("Weighted\nscore", None),
                                                                        ("After gates, $M", "central (range)")]
    for c, (lab, sub) in enumerate(hdr):
        hf = HEAD if c in (0, len(hdr) - 1) else BODY  # Lato is narrower: criteria names fit on one line
        paras = [[(l, {"bold": True, "color": WHITE, "font": hf, "size": 10})] for l in lab.split("\n")]
        if sub:
            paras.append([(sub, {"color": RGBColor.from_string("C9D2DF"), "size": 9})])
        cell(0, c, paras, NAVY, align=PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER)

    lo_v, hi_v = -62.0, 12.0
    rx = x0 + sum(widths[:-1])
    pad = 0.18
    to_x = lambda v: rx + pad + (v - lo_v) / (hi_v - lo_v) * (widths[-1] - 2 * pad)
    for i, alt in enumerate(ALTS, start=1):
        rec = alt == REC
        base = RGBColor.from_string("FFF4EE") if rec else (PANEL if i % 2 else WHITE)
        cell(i, 0, [[(alt, {"bold": True, "color": NAVY, "font": HEAD, "size": 12})],
                    [(DESC[alt], {"size": 10, "color": INK})]], base, align=PP_ALIGN.LEFT)
        for c, (key, _, _) in enumerate(CRIT, start=1):
            v = float(DM[key][alt])
            fill = RGBColor.from_string(SCALE[max(1, min(5, round(v)))])
            cell(i, c, [f"{v:.1f}" if key == "financial" else f"{v:.0f}"], fill, size=13, bold=True,
                 color=WHITE if round(v) >= 4 else INK)
        cell(i, 7, [f"{float(DM['weighted_total'][alt]):.1f}"], base, size=16, bold=True,
             color=ORANGE if rec else NAVY, font=HEAD)
        t = TOT[alt]
        lo, mid, hi = (float(t[k]) for k in ("after_gates_low", "after_gates_central", "after_gates_high"))
        label = money(mid) + (f"  ({money(lo)} to {money(hi)})" if hi - lo > 0.05 else "")
        cell(i, 8, [[(label, {"size": 10, "bold": True, "color": NAVY})]], base, align=PP_ALIGN.LEFT)
        # whisker: drawn over the cell, on a shared -62..+12 axis
        yc = y0 + hh + (i - 1) * rh + rh * 0.68
        if hi - lo > 0.05:
            rule(s, to_x(lo), yc, to_x(hi), yc, color=RGBColor.from_string("9AAAC0"), width=3)
        d = 0.15
        box(s, to_x(mid) - d / 2, yc - d / 2, d, d, fill=ORANGE if rec else NAVY, shape=MSO_SHAPE.OVAL)
        tbl.cell(i, 8).vertical_anchor = MSO_ANCHOR.TOP
    # break-even line across the result column
    zx = to_x(0)
    y_top, y_bot = y0 + hh, y0 + hh + 4 * rh
    rule(s, zx, y_top + 0.05, zx, y_bot + 0.02, color=ORANGE, width=1.25, dash=MSO_LINE.DASH)
    text(s, zx - 0.8, y_top + 0.05, 0.75, 0.2, ["break-even"], size=8, color=ORANGE, align=PP_ALIGN.RIGHT)
    # recommended outline + tag
    yr = y0 + hh + 2 * rh
    box(s, x0, yr, sum(widths), rh, fill=None, line=ORANGE, line_w=2.25)
    tag = box(s, x0 + 0.08, yr - 0.11, 1.22, 0.22, fill=ORANGE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    tag.text_frame.text = "RECOMMENDED"
    tf = tag.text_frame
    tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    r = tf.paragraphs[0].runs[0]
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = HEAD, Pt(8), True, WHITE

    rs, sh = TOT[REC], TOT["Shrink to Core"]
    stay = float(TOT["Stay the Course"]["after_gates_central"])
    calls = [
        ("Why not Fill the Planes?",
         "Break-even needs +25.5% revenue (+30.7% after gates): ~5 years at this year's +5% growth. Levers "
         "≈ $5M central; even a $30M ceiling leaves it negative. More trunk flights did not fill."),
        ("Why not Shrink to Core?",
         f"Its {money(float(sh['after_gates_central']))} is more certain, but it drops 6 airports, "
         f"${float(sh['connecting_revenue_lost_musd']):.1f}M of connecting revenue and 56% of flights. Right-Size "
         f"leads once ≥{CROSS:.0%} of the trunk's cut-flight revenue moves to kept flights."),
        ("How we scored",
         f"Safety First is a pass/fail screen: all pass. Financial is linear ({usd(stay)} = 1, break-even = 5); "
         "the rest is team judgement. Even at Right-Size's 0%-recapture low, Shrink needs ≥70% Financial weight."),
    ]
    cw, gap, cy, chh = (12.13 - 2 * 0.2) / 3, 0.2, 5.8, 1.1
    for k, (head, body) in enumerate(calls):
        cx = 0.6 + k * (cw + gap)
        box(s, cx, cy, cw, chh, fill=PANEL)
        text(s, cx + 0.15, cy + 0.1, cw - 0.3, chh - 0.15,
             [[(head, {"bold": True, "color": NAVY, "font": HEAD, "size": 11, "space_after": 3})], body], size=10.5)


NOTES_18 = """ALTERNATIVES. ~45 sec.
Say: "We tested four ways out, on one consistent FY25-26 basis, against NorthByte's own values."
- Stay the Course: the baseline, about −$58M after gates.
- Fill the Planes: keep every flight and sell more. It needs +25.5% revenue just to break even before gates (+30.7% after), roughly 5 years of record growth with ~$130M more losses on the way, and every lever we sized adds only ~$5M. The trunk already ran this experiment.
- Right-Size & Recover: remove the 2025 trunk add-ons, exit Montréal–Vancouver, halve the 3 new markets, then use the revenue levers. Central case about +$1.4M after gates with all 20 airports kept; range about −$17M to +$6M (0–100% recapture plus lever low–high). Be upfront that the central case is thin: it breaks even only if ~90% of the trunk's cut-flight revenue moves to the kept flights (it beats Shrink above ~⅔), and ~1% more cost per flight or ~1% less retained revenue would erase it. Why we still expect high recapture: the added flights brought in almost no extra revenue (+3.7% vs +3.3–4.0% on unchanged routes), and 10 of 10 doubled directions cut fares while 0 of 38 unchanged directions did. Each added trunk flight brought ~1.9 extra tickets against ~19 needed to break even, so most of it should.
- Shrink to Core: exit the 22 directions that lost money in every FY25-26 season. Similar money, more certain, but 6 airports, $8M of connecting revenue and 56% of flights gone. It only wins if money is weighted 70%+ AND Right-Size recaptures nothing.
If asked "is +$1.4M a profit?": it is contribution after gates, i.e. break-even on the costs the data shows (fuel, crew, maintenance, food, gates). It excludes aircraft ownership and overhead, which the case does not give. The schedule changes alone get to about −$3.8M; the revenue levers (~$5.2M central) close the gap.
Assumption to disclose: fuel, crew, maintenance and food on removed flights are avoidable (case p.10: these costs "depend on the number of flights"). About $73.6M of flight cost is removed; each 10% that proves fixed costs ~$7.4M.
Gates: after-gates figures accrue leases by fiscal year: Sep–Dec 2025 at 2025 rates + Jan–Aug 2026 with each gate repeating its 2024→25 increase = $10.02M (teammate's gate analysis agrees to the cent).
If asked "why exit Montréal–Vancouver rather than go back to one flight?": the difference is only ~$0.9M ($19.7M vs $18.8M); even the one-rotation base schedule still loses ~$0.9M after the cost step, it has 0 connecting passengers, and the exit saving doesn't depend on recapture. Fallback: revert to one rotation and exit if it stays negative for two quarters.
Fill the Planes' −$28M ceiling assumes a −1.5 fare elasticity that our trunk evidence contradicts (fares −11%, tickets +11% vs control, revenue flat), so it is generous.
Safety is a pass/fail screen, not a score. Weights: financial 30%; communities, customers, employees 15% each.
OPEN TEAM DECISION: halved, the new markets still lose about −$3.9M at central recapture (revenue covers 49% of cost; −$2.6M and 65% even at full recapture), and reaching the 0.8 trigger needs ~63% more revenue. None of the 12,644 connection-compatible bookings uses them. A full exit adds ~+$3.9M more and frees $0.69M of gates (a real buffer for the thin central case), but London and Moncton lose service (20 → 18 airports) and the headline changes."""


# ---------- appendix: strategic lens (Five Forces + SWOT)
def build_lens(s):
    reset(s, LENS_KICKER,
          "Five Forces explains why extra frequency failed; SWOT shows what any fix must protect",
          "Source: Case package p.6–10 (market context) and team analysis of FY25-26 data. "
          "* = inference, not stated in the case.",
          NOTES_LENS)
    text(s, 0.6, 1.62, 6.0, 0.3, [[("Porter's Five Forces: Canadian domestic air", {"bold": True, "color": NAVY})]],
         size=13, font=HEAD)
    forces = [
        ("Rivalry", "High", "Two national carriers plus low-cost airlines (case). Trunk fares fell ~8% when frequency doubled."),
        ("Buyer power", "High", "Price-sensitive travellers (case); OTAs sell 20% of ticket revenue. Extra seats sold only at lower fares."),
        ("Supplier power", "High", "Volatile fuel, pilot shortage, high airport fees (case). Same route & month: fuel +8.7%, crew +8.5%."),
        ("New entrants", "Medium", "Newer carriers expanded, then scaled back or shut down (case): the path NorthByte took in 2025.*"),
        ("Substitutes", "Low", "Long distances and small communities: demand on community routes is captive.*"),
    ]
    y = 2.0
    for force, lvl, why in forces:
        box(s, 0.6, y, 6.0, 0.86, fill=PANEL)
        text(s, 0.75, y + 0.1, 1.6, 0.3, [force], size=12, bold=True, color=NAVY, font=HEAD)
        pill = box(s, 0.75, y + 0.45, 0.85, 0.26, fill=ORANGE if lvl == "High" else
                   (RGBColor.from_string("F4A97F") if lvl == "Medium" else LINE), shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        pill.text_frame.text = lvl
        pf = pill.text_frame
        pf.margin_top = pf.margin_bottom = pf.margin_left = pf.margin_right = 0
        pf.paragraphs[0].alignment = PP_ALIGN.CENTER
        rr = pf.paragraphs[0].runs[0]
        rr.font.name, rr.font.size, rr.font.bold = BODY, Pt(9), True
        rr.font.color.rgb = WHITE if lvl != "Low" else INK
        text(s, 2.45, y + 0.08, 4.05, 0.72, [why], size=10.5, anchor=MSO_ANCHOR.MIDDLE)
        y += 0.96

    text(s, 6.95, 1.62, 5.8, 0.3, [[("SWOT: NorthByte", {"bold": True, "color": NAVY})]], size=13, font=HEAD)
    quads = [
        ("Strengths", GREEN, ["Rest of network earns +$10.6M before gates",
                              "12,644 connection-compatible bookings", "Community routes the mission is built on (case)"]),
        ("Weaknesses → issues", ORANGE, ["No route-level P&L (case p.10)",
                                         "Frequency added faster than demand: trunk tickets/flight −44% (Sep–Feb)",
                                         "New markets cover only a third of their cost"]),
        ("Opportunities", NAVY, ["Record passenger demand (case p.7)", "Seasonal flex flying (summer, December); OTA → direct",
                                 "Release 2 unassigned gates at the Jan 2027 renewal (≥$0.43M/yr)"]),
        ("Threats", MUTED, ["Two dominant rivals plus low-cost carriers", "Fuel, pilot wages, airport fees",
                            "Winter disruption + refund rules (St. John's)"]),
    ]
    qw, qh, g = 2.84, 2.32, 0.12
    for k, (head, col, items) in enumerate(quads):
        qx, qy = 6.95 + (k % 2) * (qw + g), 2.0 + (k // 2) * (qh + g)
        box(s, qx, qy, qw, qh, fill=WHITE, line=LINE)
        paras = [[(head, {"bold": True, "color": col, "font": HEAD, "size": 12, "space_after": 4})]]
        paras += [[("•  " + it, {"space_after": 4})] for it in items]
        text(s, qx + 0.14, qy + 0.12, qw - 0.28, qh - 0.2, paras, size=10.5)


NOTES_LENS = """APPENDIX: STRATEGIC LENS. Q&A only.
Use if a judge asks "what about competitors / the market?"
Five Forces: every force cites the case text or our data. Rivalry and buyer power explain why doubling the trunk cut fares: the extra passengers came only at lower fares, so revenue grew no faster than on unchanged routes. Supplier power explains why the largest cost lever NorthByte controls is how many flights it flies (fuel efficiency and maintenance purchasing are smaller, secondary levers). The case's own story of newer carriers that expanded and then shrank is the warning.
SWOT: weaknesses are the three issues; strengths are what Right-Size keeps (hubs, connections, communities) and Shrink gives up; opportunities are the recovery levers; threats feed the risk slide.
Do not claim outside market facts: assumption 11 (analysis/ASSUMPTIONS.md)."""


def main():
    prs = Presentation(DECK)
    build_issues(find_slide(prs, "KEY ISSUES"))
    build_alternatives(find_slide(prs, "ALTERNATIVES"))
    try:
        lens = find_slide(prs, LENS_KICKER)
    except KeyError:  # new slide at the end: same layout, frame shapes copied from the issues slide
        src = find_slide(prs, "KEY ISSUES")
        lens = prs.slides.add_slide(src.slide_layout)
        for sh in src.shapes:
            if sh.name in FRAME:
                lens.shapes._spTree.append(copy.deepcopy(sh._element))
    build_lens(lens)
    prs.save(DECK)
    print("built Key issues, Alternatives, Strategic lens: route groups "
          + ", ".join(f"{k} {v:+.2f}" for k, v in grp.items()) + f", total {total:+.2f}")


if __name__ == "__main__":
    main()

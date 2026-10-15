"""Flag text that likely overflows its box or table cell (no renderer needed).

uv run --no-project --with python-pptx --with pillow python slides/check_fit.py [deck.pptx] [slide numbers, e.g. 17,18]
ponytail: real Lato metrics (font files from the local R install), average glyph widths for Montserrat (~0.63 em
bold), so it is a heuristic with ~5-10% error; anything within 10% of the limit is reported as TIGHT. A real render is still the final check.
"""
import math
import sys

from pptx import Presentation
from pptx.util import Emu

from deckkit import DECK

EM = {("Montserrat", True): 0.63, ("Montserrat", False): 0.58, ("Lato", True): 0.53, ("Lato", False): 0.50}
# Real Lato metrics when the font files exist (Montserrat is not installed here, so it keeps the estimate)
LATO_DIR = "/Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/library/rmarkdown/rmd/h/bootstrap/css/fonts"
try:
    from PIL import ImageFont
    FONTS = {("Lato", False): ImageFont.truetype(f"{LATO_DIR}/Lato.ttf", 1000),
             ("Lato", True): ImageFont.truetype(f"{LATO_DIR}/LatoBold.ttf", 1000)}
except Exception:
    FONTS = {}


def width(txt, font, bold, pt):
    f = FONTS.get((font or "Lato", bool(bold)))
    if f:
        return f.getlength(txt) / 1000 * pt / 72
    return len(txt) * EM.get((font or "Lato", bool(bold)), 0.52) * pt / 72


def need_height(tf, width_in):
    """Estimated height (in) of a text frame's paragraphs wrapped at width_in."""
    total = 0.0
    paras = list(tf.paragraphs)
    for idx, p in enumerate(paras):
        runs = p.runs
        size = max((r.font.size.pt for r in runs if r.font.size), default=12)
        if not "".join(r.text for r in runs).strip():
            total += size * 1.2 / 72
            continue
        line_w, lines = 0.0, 1
        for r in runs:
            pt = r.font.size.pt if r.font.size else size
            for i, word in enumerate(r.text.split(" ")):
                w = width((" " if i or line_w else "") + word, r.font.name, r.font.bold, pt)
                if line_w + w > width_in and line_w > 0:
                    lines += 1 + math.floor(w / width_in)
                    line_w = w % width_in
                else:
                    line_w += w
        total += lines * size * 1.2 / 72 + (p.space_after.pt / 72 if p.space_after and idx < len(paras) - 1 else 0)
    return total


def margins(tf):
    get = lambda v, d: Emu(v).inches if v is not None else d
    return (get(tf.margin_left, 0.1) + get(tf.margin_right, 0.1), get(tf.margin_top, 0.05) + get(tf.margin_bottom, 0.05))


def check(deck, only=None):
    prs = Presentation(deck)
    bad = 0
    for n, s in enumerate(prs.slides, 1):
        if only and n not in only:
            continue
        for sh in s.shapes:
            frames = []
            if sh.has_text_frame and sh.text_frame.text.strip() and sh.text_frame.word_wrap is not False:
                frames.append((sh.name, sh.text_frame, Emu(sh.width).inches, Emu(sh.height).inches))
            if sh.has_table:
                t = sh.table
                for ri, row in enumerate(t.rows):
                    for ci, c in enumerate(row.cells):
                        if c.text.strip():
                            frames.append((f"{sh.name}[{ri},{ci}]", c.text_frame, Emu(t.columns[ci].width).inches,
                                           Emu(row.height).inches))
            for name, tf, w, h in frames:
                mw, mh = margins(tf)
                need, have = need_height(tf, w - mw) + mh, h
                if name in ("TextBox 2", "TextBox 6"):  # template kicker and page number grow to fit; one short line
                    continue
                if name in ("TextBox 3", "TextBox 5"):  # title <= 2 lines; source line 1 line (+6pt space-after)
                    have = {"TextBox 3": 1.05, "TextBox 5": 0.33}[name]
                if need > have * 1.1:
                    status = "OVERFLOW"
                elif need > have * 0.95:
                    status = "TIGHT"
                else:
                    continue
                bad += status == "OVERFLOW"
                print(f"slide {n:2} {status:8} {name:22} need {need:.2f}in, box {have:.2f}in  {tf.text[:60]!r}")
    return bad


if __name__ == "__main__":
    deck = sys.argv[1] if len(sys.argv) > 1 else DECK
    only = {int(x) for x in sys.argv[2].split(",")} if len(sys.argv) > 2 else None
    sys.exit(1 if check(deck, only) else 0)

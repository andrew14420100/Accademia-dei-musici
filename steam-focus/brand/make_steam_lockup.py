"""STEAM FOCUS lockup requested by the owner: the official Steam logo + the word FOCUS.

    python brand/make_steam_lockup.py STEAM_LOGO.svg FONT.ttf OUT_DIR [focus_colour]

STEAM_LOGO.svg is the official vector logo (symbol + STEAM wordmark + (R)) as served in
the Steam store header (fetched by scripts/fetch_assets.sh, not committed: it is Valve
artwork). Its shapes are copied unchanged; only the fill colour is set (white for the
inverse/dark version, ink for the light version, as in Valve's own logo variants).
FOCUS is set as outlines, with the wordmark's cap height (32.5 units), baseline and
letter spacing.

NOTE: Valve's brand guidelines do not allow combining the Steam logo with other words
or logos without permission (https://partner.steamgames.com/doc/marketing/branding).
This lockup is the owner's choice for the private preview; see REVISIONE_V3.md.
"""
import re
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

CAP = 32.5  # cap height of the STEAM wordmark, logo units
BASE = 60.6  # baseline of the wordmark
GAP = 6.5  # letter spacing in the wordmark (S-T 6, T-E 9, E-A 8, A-M 9 units, optically ~6.5)
X0 = 303.0  # FOCUS starts one word space after the (R)

SKY = '#66C0F4'
INK = '#0B1626'


def focus_path(font_file, x0=X0):
    f = TTFont(font_file)
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    ch = f['OS/2'].sCapHeight or 0.7 * f['head'].unitsPerEm
    k = CAP / ch
    pen = SVGPathPen(gs)
    x = x0
    for c in 'FOCUS':
        g = gs[cmap[ord(c)]]
        # remove side bearings so the visible gap equals GAP
        from fontTools.pens.boundsPen import BoundsPen
        bp = BoundsPen(gs)
        g.draw(bp)
        xmin, _, xmax, _ = bp.bounds
        g.draw(TransformPen(pen, (k, 0, 0, -k, x - xmin * k, BASE)))
        x += (xmax - xmin) * k + GAP
    return pen.getCommands(), x - GAP


def official_shapes(svg_file):
    """Every <path>/<polygon> of the official logo, unchanged apart from the fill."""
    s = Path(svg_file).read_text()
    shapes = re.findall(r'<(?:path|polygon)\b[^>]*?/>', s, flags=re.S)
    return [re.sub(r'\sfill="[^"]*"', '', sh) for sh in shapes]


def lockup(svg_file, font_file, logo_fill, focus_fill):
    shapes = official_shapes(svg_file)
    d, right = focus_path(font_file)
    w, h = right + 1, 89.4
    body = f'<g fill="{logo_fill}">' + ''.join(shapes) + '</g>'
    body += f'<path fill="{focus_fill}" d="{d}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {w + 4:.1f} {h + 4:.1f}" '
            f'width="{(w + 4) * 8:.0f}" height="{(h + 4) * 8:.0f}">{body}</svg>\n')


def main():
    svg_file, font_file, out = sys.argv[1:4]
    focus = sys.argv[4] if len(sys.argv) > 4 else SKY
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    (o / 'steam_focus_dark.svg').write_text(lockup(svg_file, font_file, '#FFFFFF', focus))
    (o / 'steam_focus_light.svg').write_text(lockup(svg_file, font_file, INK, '#1F6FA3'))
    (o / 'steam_focus_mono_white.svg').write_text(lockup(svg_file, font_file, '#FFFFFF', '#FFFFFF'))
    (o / 'steam_focus_mono_dark.svg').write_text(lockup(svg_file, font_file, INK, INK))
    print('wrote', o)


if __name__ == '__main__':
    main()

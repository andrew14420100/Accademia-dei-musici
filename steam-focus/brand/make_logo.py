"""STEAM FOCUS editorial identity — two original logo concepts, as self-contained SVG.

    python brand/make_logo.py          (needs fontTools; fonts from public/fonts)

Writes brand/<concept>/*.svg. Text is converted to outlines (Saira, SIL OFL), so the
files render identically everywhere. Neither symbol uses or imitates the Steam logo:
concept A is a camera focus frame, concept B an aperture of four inward chevrons.

Variants per concept:
  symbol            symbol only, colour (for dark backgrounds)
  stacked_dark      symbol + two-line wordmark, colour, for dark backgrounds
  stacked_light     same for light backgrounds
  horizontal_dark   symbol + one-line wordmark (compact badge / lower third)
  horizontal_light
  mono_white        single colour, white
  mono_dark         single colour, ink
"""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONT = TTFont(HERE.parent / 'public/fonts/Saira-600.ttf')

# Design tokens (mirrored in src/theme.ts)
INK = '#0B1626'
NIGHT = '#13283F'
PETROL = '#1B3B56'
SKY = '#66C0F4'
SKY_DEEP = '#1F6FA3'  # Steam-blue family, dark enough for text on white (4.9:1)
PAPER = '#F3F5F7'


def text_path(s, size, x, y, tracking=0.06):
    """Outline of `s` (caps) at baseline (x, y); returns (svg path d, advance width)."""
    gs = FONT.getGlyphSet()
    cmap = FONT.getBestCmap()
    upm = FONT['head'].unitsPerEm
    k = size / upm
    pen = SVGPathPen(gs)
    cx = 0.0
    for ch in s:
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (k, 0, 0, -k, x + cx, y))
        gs[g].draw(tp)
        cx += gs[g].width * k + tracking * size
    return pen.getCommands(), cx - tracking * size


def cap_height(size):
    return FONT['OS/2'].sCapHeight / FONT['head'].unitsPerEm * size


# ---------------------------------------------------------------- symbols (100 x 100)

def symbol_a(c1, c2, c3, tile=True):
    """Focus frame: a rounded tile, four corner brackets and a centred diamond."""
    out = []
    if tile:
        out.append(
            '<defs><linearGradient id="ga" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{PETROL}"/><stop offset="1" stop-color="{INK}"/></linearGradient></defs>'
            '<rect x="0" y="0" width="100" height="100" rx="22" fill="url(#ga)"/>'
            f'<rect x="1" y="1" width="98" height="98" rx="21" fill="none" stroke="{SKY}" stroke-opacity="0.35" stroke-width="2"/>'
        )
    i, L, w = 20, 19, 7.5  # inset, arm length, stroke
    pts = [
        f'M{i},{i + L} V{i} H{i + L}',
        f'M{100 - i - L},{i} H{100 - i} V{i + L}',
        f'M{100 - i},{100 - i - L} V{100 - i} H{100 - i - L}',
        f'M{i + L},{100 - i} H{i} V{100 - i - L}',
    ]
    out.append(f'<path d="{" ".join(pts)}" fill="none" stroke="{c1}" stroke-width="{w}" stroke-linecap="square"/>')
    out.append(f'<path d="M50,36 L64,50 L50,64 L36,50 Z" fill="{c2}"/>')
    return ''.join(out)


def symbol_b(c1, c2, c3, tile=False):
    """Aperture: four chevrons pointing inwards (focus), a diamond core (the subject)."""
    # top chevron; the other three are rotations of it
    v = 'M24,8 L50,34 L76,8 L64,8 L50,22 L36,8 Z'
    cols = [c1, c2, c2, c1]  # top, right, bottom, left: light comes from the top-left
    parts = [f'<path d="{v}" fill="{col}" transform="rotate({rot} 50 50)"/>' for rot, col in zip((0, 90, 180, 270), cols)]
    parts.append(f'<path d="M50,40 L60,50 L50,60 L40,50 Z" fill="{c3}"/>')
    return ''.join(parts)


SYMBOLS = {'a_focusframe': symbol_a, 'b_aperture': symbol_b}


def palette(variant):
    # (symbol c1, c2, c3, word STEAM, word FOCUS, tile?)
    return {
        'dark': (SKY, PAPER, SKY, PAPER, SKY, True),
        'light': (SKY_DEEP, INK, SKY_DEEP, INK, SKY_DEEP, True),  # tile keeps dark colours
        'mono_white': (PAPER, PAPER, PAPER, PAPER, PAPER, False),
        'mono_dark': (INK, INK, INK, INK, INK, False),
    }[variant]


def compose(concept, layout, variant):
    sym = SYMBOLS[concept]
    c1, c2, c3, w1, w2, tile = palette(variant)
    # mono variants of the tile concept: brackets + diamond only (no gradient tile)
    has_tile = tile and concept == 'a_focusframe'
    if has_tile:  # the tile is always dark inside, whatever the page colour
        c1, c2, c3 = SKY, PAPER, SKY
    elif variant == 'light':
        c1, c2, c3 = SKY_DEEP, INK, SKY_DEEP
    body = sym(c1, c2, c3, tile=has_tile)
    if layout == 'symbol':
        return 100, 100, f'<g>{body}</g>'
    if layout == 'stacked':
        # two lines of caps, 34 units each with a 0.36 cap gap, centred on the symbol
        size = 34 / cap_height(1)
        ch = 34
        top = (100 - (2 * ch + 0.36 * ch)) / 2
        x0 = 126
        d1, a1 = text_path('STEAM', size, x0, top + ch, tracking=0.1)
        d2, a2 = text_path('FOCUS', size, x0, top + 2 * ch + 0.36 * ch, tracking=0.1)
        width = x0 + max(a1, a2) + 2
        return width, 100, f'<g>{body}</g><path d="{d1}" fill="{w1}"/><path d="{d2}" fill="{w2}"/>'
    if layout == 'horizontal':
        size = 70
        ch = cap_height(size)
        y = 50 + ch / 2
        x0 = 124
        d1, a1 = text_path('STEAM', size, x0, y)
        d2, a2 = text_path('FOCUS', size, x0 + a1 + 0.32 * size, y)
        width = x0 + a1 + 0.32 * size + a2 + 2
        return width, 100, f'<g>{body}</g><path d="{d1}" fill="{w1}"/><path d="{d2}" fill="{w2}"/>'
    raise ValueError(layout)


def svg(w, h, inner, pad=0):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w + 2 * pad:.1f} {h + 2 * pad:.1f}" '
        f'width="{(w + 2 * pad) * 4:.0f}" height="{(h + 2 * pad) * 4:.0f}">{inner}</svg>\n'
    )


def main():
    for concept in SYMBOLS:
        d = HERE / concept
        d.mkdir(exist_ok=True)
        jobs = {
            'symbol': ('symbol', 'dark'),
            'stacked_dark': ('stacked', 'dark'),
            'stacked_light': ('stacked', 'light'),
            'horizontal_dark': ('horizontal', 'dark'),
            'horizontal_light': ('horizontal', 'light'),
            'mono_white': ('stacked', 'mono_white'),
            'mono_dark': ('stacked', 'mono_dark'),
        }
        for name, (layout, variant) in jobs.items():
            w, h, inner = compose(concept, layout, variant)
            (d / f'{name}.svg').write_text(svg(w, h, inner, pad=4))
        print('wrote', d)


if __name__ == '__main__':
    main()

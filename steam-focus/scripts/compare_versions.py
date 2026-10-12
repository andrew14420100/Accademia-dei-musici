"""Side-by-side stills, v1 (1080p30) vs v2 (4K60 master), at matching story moments.

    python3 scripts/compare_versions.py out/v1_1080p30_steam_focus_ecc_redline_full.mp4 \
        out/steam_focus_ecc_redline_full_4K_60fps.mp4 out/qc/compare

Moments are located in each version's own EDL (by shot, section or spoken word),
so the pairs show the same beat even though the two edits are timed differently.
"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

v1, v2, outdir = sys.argv[1:4]
out = Path(outdir)
out.mkdir(parents=True, exist_ok=True)
E1 = json.load(open('public/full_edl_v1.json'))
E2 = json.load(open('public/full_edl.json'))


def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    return re.sub(r'[^a-z0-9]', '', s)


def word(e, w, after=0, line_id=None):
    for line in e['lines']:
        if line_id and line['id'] != line_id:
            continue
        for a, _b, t in line['words']:
            if norm(t) == w:
                return line['from'] + a * e['fps'] + after
    raise KeyError(w)


def shot(e, sid, after=0):
    s = next(s for s in e['shots'] if s['id'] == sid)
    return s['from'] + after


MOMENTS = [
    ('01_apertura', 'Titolo d\'apertura sul gameplay',
     lambda e: shot(e, 'h_heli', 45 if e is E2 else 40)),
    ('02_capitolo', 'Cartello di capitolo (Movimento)',
     lambda e: e['sections']['movement'][0] + 24),
    ('03_sottotitoli', 'Sottotitoli e area sicura TikTok',
     lambda e: word(e, 'quattro', 8, 'sq1') if e is E2 else e['sections']['squad'][0] + 40),
    ('04_negozio', 'Prezzi del negozio (nessun pannello sopra)',
     lambda e: word(e, 'siringa', 24)),
    ('05_analisi', 'Analisi editoriale separata dai dati ufficiali',
     lambda e: shot(e, 'e_after', 30)),
    ('06_steam', 'Pagina Steam reale: stato di uscita',
     lambda e: word(e, 'arrivo', 30)),
    ('07_lingue', 'Pagina Steam reale: lingue',
     lambda e: word(e, 'lingue', 20)),
    ('08_chiusura', 'Chiusura',
     lambda e: e['frames'] - 14),
]

rows = []
for key, label, at in MOMENTS:
    pair = []
    for tag, e, src in (('v1', E1, v1), ('v2', E2, v2)):
        try:
            t = at(e) / e['fps']
        except (KeyError, StopIteration):
            t = None
        f = out / f'_{key}_{tag}.png'
        if t is None:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=0x222222:s=1080x1920',
                            '-frames:v', '1', str(f)], check=True)
        else:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', src, '-frames:v', '1',
                            '-vf', 'scale=1080:1920:flags=lanczos', str(f)], check=True)
        pair.append((f, t))
    dst = out / f'{key}.jpg'
    title = f"{label}  |  v1 {pair[0][1] or 0:.2f}s  vs  v2 {pair[1][1] or 0:.2f}s"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(pair[0][0]), '-i', str(pair[1][0]), '-filter_complex',
                    '[0][1]hstack=inputs=2,pad=iw:ih+90:0:90:color=black,'
                    f"drawtext=text='{title.replace(chr(39), '')}':x=24:y=26:fontsize=40:fontcolor=white,"
                    "drawtext=text='v1':x=24:y=110:fontsize=56:fontcolor=white:box=1:boxcolor=black@0.6,"
                    "drawtext=text='v2':x=1104:y=110:fontsize=56:fontcolor=white:box=1:boxcolor=black@0.6,"
                    'scale=1080:-2', '-q:v', '3', str(dst)], check=True)
    for f, _ in pair:
        f.unlink()
    rows.append((key, label, pair[0][1], pair[1][1]))
    print(key, label, pair[0][1], pair[1][1])

"""Pick the best take of each sentence (best-of-N) and assemble a voice sample.

    python narration/pick_takes.py CAND_DIR VOICE SENTENCES.json OUT.wav [pauses...]

Takes are named <VOICE>_<sentence>_<seed>.wav. Each take is transcribed with
faster-whisper and scored on: word match to the script (accent- and case-folded),
presence of the hard words (ECC, REDLINE, NetEase, Steam, ruolo, ottiche...), and
a plausible speaking rate (rejects truncated or runaway generations). The ASR
score only screens for wrong or missing words; it says nothing about how
natural a take sounds, which needs a human listen.
"""
import difflib
import glob
import json
import re
import sys
import unicodedata

import librosa
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

SR = 24000
KEY = {
    'ecc': ('ecc', 'ec c', 'e c c', 'eccredline'),
    'redline': ('redline', 'redlain', 'red line'),
    'netease': ('netease', 'net ease'),
    'steam': ('steam',),
    'ruolo': ('ruolo',),
    'ottiche': ('ottiche',),
    'movimento': ('movimento',),
    'squadra': ('squadra',),
}


def fold(s):
    s = unicodedata.normalize('NFKD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.replace('-', ' ').replace('.', ' ')
    return re.sub(r'[^a-z0-9 ]', ' ', s)


def words(s):
    return fold(s).split()


def score(asr, target):
    t = words(target.replace('E-C-C Rèdlain', 'ECC Redline'))
    a = words(asr)
    ratio = difflib.SequenceMatcher(None, t, a).ratio()
    flat = ' '.join(a)
    need = [k for k in KEY if any(v in fold(target.replace('E-C-C Rèdlain', 'ECC Redline')) for v in KEY[k][:1])]
    miss = [k for k in need if not any(v in flat for v in KEY[k])]
    return ratio - 0.15 * len(miss), miss


def main():
    cand, voice, sentences, out = sys.argv[1:5]
    pauses = [float(p) for p in sys.argv[5:]] or [0.3]
    S = json.load(open(sentences))
    model = WhisperModel('medium', device='cpu', compute_type='int8')
    parts, report = [], []
    for i, target in enumerate(S):
        best = None
        for f in sorted(glob.glob(f'{cand}/{voice}_{i}_*.wav')):
            y, sr = librosa.load(f, sr=SR)
            y, _ = librosa.effects.trim(y, top_db=38)
            dur = len(y) / SR
            exp = len(fold(target).replace(' ', '')) / 13.5  # ~13.5 letters/s for Italian news reading
            segs, _ = model.transcribe(librosa.resample(y, orig_sr=SR, target_sr=16000), language='it', beam_size=5)
            asr = ' '.join(s.text.strip() for s in segs)
            sc, miss = score(asr, target)
            rate_ok = 0.65 < dur / exp < 1.45
            total = sc - (0 if rate_ok else 0.5)
            report.append(dict(take=f, score=round(total, 3), dur=round(dur, 2), expected=round(exp, 2), missing=miss, asr=asr))
            if best is None or total > best[0]:
                best = (total, y, f)
        parts.append(best[1])
        print(f'sentence {i}: {best[2]} score {best[0]:.3f}')
    fade = int(0.012 * SR)
    out_audio = []
    for i, y in enumerate(parts):
        y = y.copy()
        y[:fade] *= np.linspace(0, 1, fade)
        y[-fade:] *= np.linspace(1, 0, fade)
        out_audio.append(y)
        if i < len(parts) - 1:
            out_audio.append(np.zeros(int(pauses[min(i, len(pauses) - 1)] * SR)))
    sf.write(out, np.concatenate(out_audio), SR)
    json.dump(report, open(out.replace('.wav', '_takes.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

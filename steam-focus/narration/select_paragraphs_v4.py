"""V4 narration: one paragraph per chapter, natural speed. Pick the best take of each chapter
and cut it into the script's lines at the natural pauses, so the edit keeps every line as an
anchor (subtitles, graphics) while the chapter plays back exactly as it was spoken.

    python narration/select_paragraphs_v4.py narration/ecc_redline_it_v4.json TAKES_DIR OUT_DIR public/vo_timing.json

TAKES_DIR holds <section>_<seed>.wav (narration/chatterbox_batch.py). Each take is trimmed,
transcribed with faster-whisper (word timestamps) and scored against the chapter text
(narration/pick_takes.py: word match, hard words present, plausible speaking rate). The
chosen take is split at the midpoint of the silence between two lines; every line gets
"gap_before": 0 except the first of a chapter, so edit/plan_full.py reassembles the chapter
seamlessly. No time-stretching. The score screens wrong or missing words only: it says
nothing about how natural the reading sounds.
"""
import difflib
import glob
import json
import os
import sys

import librosa
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

sys.path.insert(0, os.path.dirname(__file__))
from pick_takes import fold, score  # noqa: E402

SR = 24000


def trim(y, top_db=38, pad=0.06):
    _, (a, b) = librosa.effects.trim(y, top_db=top_db)
    return y[max(0, a - int(pad * SR)): min(len(y), b + int(pad * SR))]


def main():
    script_path, takes, out_dir, timing_path = sys.argv[1:5]
    script = json.load(open(script_path))
    os.makedirs(out_dir, exist_ok=True)
    model = WhisperModel('medium', device='cpu', compute_type='int8')
    sections = []
    for l in script['lines']:
        if not sections or sections[-1][0] != l['section']:
            sections.append((l['section'], []))
        sections[-1][1].append(l)
    timing, report = [], []
    for sec, lines in sections:
        target = ' '.join(l['text'] for l in lines).replace('ECC: REDLINE', 'E-C-C Rèdlain')
        say = ' '.join(l.get('say', l['text']) for l in lines)
        best = None
        for f in sorted(glob.glob(f'{takes}/{sec}_*.wav')):
            y, _ = librosa.load(f, sr=SR)
            y = trim(y)
            segs, _ = model.transcribe(librosa.resample(y, orig_sr=SR, target_sr=16000), language='it',
                                       beam_size=5, word_timestamps=True)
            words = [w for s in segs for w in s.words]
            asr = ' '.join(w.word.strip() for w in words)
            sc, miss = score(asr, target)
            rate = (len(y) / SR) / (len(fold(say).replace(' ', '')) / 13.5)
            total = sc - (0 if 0.65 < rate < 1.5 else 0.5)
            report.append(dict(section=sec, take=os.path.basename(f), score=round(total, 3), dur=round(len(y) / SR, 2),
                               rate=round(rate, 2), missing=miss, asr=asr))
            if best is None or total > best[0]:
                best = (total, y, f, words, asr)
        total, y, f, words, asr = best
        print(f'{sec:9s} {os.path.basename(f):14s} {total:5.2f}  {asr}')
        # map each line's first word onto the ASR word sequence
        tw, owner = [], []
        for i, l in enumerate(lines):
            for w in fold(l['text'].replace('ECC: REDLINE', 'ECC Redline')).split():
                tw.append(w)
                owner.append(i)
        aw = [' '.join(fold(w.word).split()) for w in words]
        sm = difflib.SequenceMatcher(None, tw, aw, autojunk=False)
        t2a = {}
        for a0, b0, n in sm.get_matching_blocks():
            for k in range(n):
                t2a[a0 + k] = b0 + k
        cuts = [0]
        for i in range(1, len(lines)):
            first_t = owner.index(i)
            # nearest matched text word at/after the line start, else proportional
            ai = next((t2a[k] for k in range(first_t, len(tw)) if k in t2a and owner[k] == i), None)
            if ai is None or ai == 0:
                ai = round(first_t / len(tw) * len(words))
            prev_end, next_start = words[ai - 1].end, words[ai].start
            cuts.append(int((prev_end + next_start) / 2 * SR))
        cuts.append(len(y))
        for i, l in enumerate(lines):
            a, b = cuts[i], cuts[i + 1]
            clip = y[a:b].copy()
            n = int(0.008 * SR)
            if i > 0:
                clip[:n] *= np.linspace(0, 1, n)
            if i < len(lines) - 1:
                clip[-n:] *= np.linspace(1, 0, n)
            sf.write(f"{out_dir}/{l['id']}.wav", clip, SR)
            t0 = a / SR
            lw = [[round(w.start - t0, 3), round(w.end - t0, 3), w.word.strip()] for w in words if a / SR <= w.start < b / SR]
            entry = dict(id=l['id'], section=sec, text=l['text'], dur=round(len(clip) / SR, 3), words=lw,
                         take=os.path.basename(f), score=round(total, 3))
            if i > 0:
                entry['gap_before'] = 0.0
            timing.append(entry)
    json.dump(timing, open(timing_path, 'w'), ensure_ascii=False, indent=1)
    json.dump(report, open(f'{out_dir}/takes_report.json', 'w'), ensure_ascii=False, indent=1)
    print('total voice', round(sum(t['dur'] for t in timing), 2), 's')


if __name__ == '__main__':
    main()

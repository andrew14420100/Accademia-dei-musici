"""V3 narration: choose one take per line and write the timing file for the edit.

    python narration/select_takes_v3.py narration/ecc_redline_it_v3.json TAKES_DIR OUT_DIR public/vo_timing.json [TEMPO]

TAKES_DIR holds <line>_<seed>.wav from narration/chatterbox_batch.py. For each line every
take is trimmed, transcribed with faster-whisper (word timestamps) and scored against the
script (narration/pick_takes.py: word match, hard words present, plausible speaking rate).
The best take is written to OUT_DIR/<line>.wav (24 kHz) and its words go into the timing
file, in the same format synth_voice.py produced for v1/v2. A report of every take is
saved as OUT_DIR/takes_report.json. The score screens wrong or missing words only.

TEMPO (default 1.0) speeds the chosen takes up with Rubberband (ffmpeg, pitch and
formants preserved); word timestamps are scaled by the same factor.
"""
import glob
import json
import os
import subprocess
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
    a = max(0, a - int(pad * SR))
    b = min(len(y), b + int(pad * SR))
    return y[a:b]


def main():
    script_path, takes, out_dir, timing_path = sys.argv[1:5]
    tempo = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    script = json.load(open(script_path))
    os.makedirs(out_dir, exist_ok=True)
    model = WhisperModel('medium', device='cpu', compute_type='int8')
    timing, report = [], []
    for line in script['lines']:
        target = line['text'].replace('ECC: REDLINE', 'E-C-C Rèdlain')
        best = None
        for f in sorted(glob.glob(f"{takes}/{line['id']}_*.wav")):
            y, _ = librosa.load(f, sr=SR)
            y = trim(y)
            dur = len(y) / SR
            exp = len(fold(line.get('say', line['text'])).replace(' ', '')) / 13.5
            segs, _ = model.transcribe(librosa.resample(y, orig_sr=SR, target_sr=16000), language='it',
                                       beam_size=5, word_timestamps=True)
            words = [w for s in segs for w in s.words]
            asr = ' '.join(w.word.strip() for w in words)
            sc, miss = score(asr, target)
            rate = dur / exp
            total = sc - (0 if 0.65 < rate < 1.45 else 0.5)
            report.append(dict(line=line['id'], take=os.path.basename(f), score=round(total, 3), dur=round(dur, 2),
                               rate=round(rate, 2), missing=miss, asr=asr))
            if best is None or total > best[0]:
                best = (total, y, f, words, asr)
        total, y, f, words, asr = best
        dst = f"{out_dir}/{line['id']}.wav"
        sf.write(dst, y, SR)
        t_line = line.get('tempo', tempo)  # per-line override (e.g. a line the stretch blurs)
        if t_line != 1.0:
            tmp = dst.replace('.wav', '_rt.wav')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', dst, '-af',
                            f'rubberband=tempo={t_line}:formant=preserved:transients=mixed:window=standard',
                            '-ar', str(SR), '-c:a', 'pcm_s16le', tmp], check=True)
            os.replace(tmp, dst)
            y, _ = librosa.load(dst, sr=SR)
        timing.append(dict(id=line['id'], section=line['section'], text=line['text'], dur=round(len(y) / SR, 3),
                           words=[[round(w.start / t_line, 3), round(w.end / t_line, 3), w.word.strip()] for w in words],
                           take=os.path.basename(f), score=round(total, 3)))
        print(f"{line['id']:6s} {os.path.basename(f):12s} {total:5.2f}  {asr}")
    json.dump(timing, open(timing_path, 'w'), ensure_ascii=False, indent=1)
    json.dump(report, open(f'{out_dir}/takes_report.json', 'w'), ensure_ascii=False, indent=1)
    print('total voice', round(sum(t['dur'] for t in timing), 2), 's')


if __name__ == '__main__':
    main()

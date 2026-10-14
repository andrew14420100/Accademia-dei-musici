"""Italian narration with Kokoro-82M (Apache-2.0, stock voice, no cloning).

Writes one WAV per line (24 kHz mono, edges trimmed) into <out_dir>, a
timing file for Remotion/audio, and an ASR round-trip report: each line is
transcribed back with faster-whisper so mispronunciations show up as text.

usage (Python 3.12 venv with kokoro, faster-whisper):
  python synth_voice.py narration/ecc_redline_it.json <out_dir> public/vo_timing.json
"""
import json
import re
import sys
import unicodedata

import numpy as np
import soundfile as sf
from kokoro import KPipeline

SR = 24000
script_path, out_dir, timing_path = sys.argv[1:4]
script = json.load(open(script_path))
pipe = KPipeline(lang_code="i", repo_id="hexgrad/Kokoro-82M")


def trim(a, thr=0.004, pad=0.08):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(pad * SR))
    e = min(len(a), idx[-1] + int(pad * SR))
    return a[s:e]


timing = []
for line in script["lines"]:
    say = line.get("say", line["text"])
    chunks = [a.numpy() for _, _, a in pipe(say, voice=script["voice"], speed=script.get("speed", 1.0))]
    audio = trim(np.concatenate(chunks))
    path = f"{out_dir}/{line['id']}.wav"
    sf.write(path, audio, SR)
    timing.append({"id": line["id"], "section": line["section"], "text": line["text"], "dur": round(len(audio) / SR, 3)})
    print(f"{line['id']:6s} {len(audio) / SR:5.2f}s  {line['text']}")

# ASR round trip (16 kHz) to catch mispronunciations.
from faster_whisper import WhisperModel  # noqa: E402

asr = WhisperModel("medium", device="cpu", compute_type="int8")


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


report = []
for t in timing:
    a, _ = sf.read(f"{out_dir}/{t['id']}.wav")
    a16 = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
    segs, _ = asr.transcribe(a16, language="it", word_timestamps=True)
    words = [w for s in segs for w in s.words]
    heard = " ".join(w.word.strip() for w in words)
    ref, hyp = norm(t["text"]), norm(heard)
    # word error rate (Levenshtein on words)
    d = np.arange(len(hyp) + 1)
    for i, r in enumerate(ref, 1):
        prev, d[0] = d.copy(), i
        for j, h in enumerate(hyp, 1):
            d[j] = min(prev[j] + 1, d[j - 1] + 1, prev[j - 1] + (r != h))
    wer = d[-1] / max(1, len(ref))
    t["words"] = [[round(w.start, 3), round(w.end, 3), w.word.strip()] for w in words]
    report.append({"id": t["id"], "wer": round(float(wer), 3), "heard": heard})
    print(f"{t['id']:6s} WER {wer:4.2f} | {heard}")

json.dump(timing, open(timing_path, "w"), ensure_ascii=False, indent=1)
json.dump(report, open(f"{out_dir}/asr_report.json", "w"), ensure_ascii=False, indent=1)
print("total voice", round(sum(t["dur"] for t in timing), 2), "s")

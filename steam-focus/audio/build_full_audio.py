"""STEAM FOCUS — ECC: REDLINE full report (v2): voice + original score + design.

No third-party audio: the trailer's music and effects (NetEase) are not used
(rights not cleared). Narration (Kokoro TTS) on top, the original procedural
score (audio/score.py) ducked under the voice, synthesized design on the cuts
and graphics. Output is pre-master (loudness is normalised at mux time).
v1 (with trailer audio) is kept as build_full_audio_v1.py.

usage: python3 build_full_audio.py public/full_edl.json <work> <out.wav> [vo_dir]
"""
import json
import os
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, resample_poly, sosfilt, sosfiltfilt

sys.path.insert(0, os.path.dirname(__file__))
import build_audio as d  # noqa: E402  (shared synth elements)
import score  # noqa: E402

SR = 48000
edl = json.load(open(sys.argv[1]))
work, out_path = sys.argv[2], sys.argv[3]
VO = sys.argv[4] if len(sys.argv) > 4 else f"{work}/vo"
FPS = edl["fps"]
N = int(edl["frames"] / FPS * SR) + SR // 2


def at(frame):
    return int(round(frame / FPS * SR))


def load(path):
    sr, x = wavfile.read(path)
    x = x.astype(np.float32) / 32768.0
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    if sr != SR:
        x = resample_poly(x, SR, sr, axis=0).astype(np.float32)
    return x


def put(bus, sig, start, gain_db=0.0, pan=0.0):
    g = 10 ** (gain_db / 20)
    if sig.ndim == 1:
        lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * lg * 1.414, sig * rg * 1.414], 1)
    e = min(len(bus), start + len(sig))
    if e > start:
        bus[start:e] += g * sig[: e - start]


def fades(x, ms=8):
    n = int(ms / 1000 * SR)
    r = np.linspace(0, 1, n)[:, None]
    x = x.copy()
    x[:n] *= r
    x[-n:] *= r[::-1]
    return x


def word(line_id, prefix):
    import re
    import unicodedata

    def norm(s):
        s = unicodedata.normalize("NFKD", s.lower())
        return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if not unicodedata.combining(c)))

    line = next(l for l in edl["lines"] if l["id"] == line_id)
    w = next(w for w in line["words"] if norm(w[2]).startswith(norm(prefix)))
    return line["from"] + round(w[0] * FPS)


# --- voice ------------------------------------------------------------------
voice = np.zeros((N, 2), np.float32)
hp = butter(2, 85, "highpass", fs=SR, output="sos")
presence = butter(2, [2500, 6000], "bandpass", fs=SR, output="sos")
for v in edl["voice"]:
    x = load(f"{VO}/{v['id']}.wav")[:, 0]
    x = sosfilt(hp, x)
    x = x + 0.18 * sosfilt(presence, x)            # a little presence for phone speakers
    rms = np.sqrt(np.mean(x[np.abs(x) > 0.01] ** 2)) if np.any(np.abs(x) > 0.01) else 1
    x = x * (0.11 / rms)                           # consistent level line to line
    # gentle compression (2:1 above -18 dBFS, smoothed envelope)
    envl = np.sqrt(np.convolve(x ** 2, np.ones(480) / 480, mode="same")) + 1e-6
    thr = 10 ** (-18 / 20)
    gain = np.where(envl > thr, (thr * (envl / thr) ** 0.5) / envl, 1.0)
    x = (x * gain).astype(np.float32)
    put(voice, fades(np.stack([x, x], 1), 15), at(v["from"]))

# Ducking envelope from voice activity (fast attack, slow release).
act = np.abs(voice[:, 0]) > 0.004
act = np.convolve(act.astype(np.float32), np.ones(int(0.25 * SR)), mode="same") > 0
duck = np.where(act, 10 ** (-18 / 20), 10 ** (-4 / 20)).astype(np.float32)
a_att, a_rel = np.exp(-1 / (0.06 * SR)), np.exp(-1 / (0.35 * SR))
sm = np.empty_like(duck)
y = duck[0]
for i in range(0, len(duck), 64):           # block-wise one-pole (fast enough)
    t_ = duck[i]
    c = a_att if t_ < y else a_rel
    y = t_ + (y - t_) * c ** 64
    sm[i:i + 64] = y

# --- original score, ducked under the voice ----------------------------------
total_s = edl["frames"] / FPS
music = score.build(total_s + 0.5, edl["sections"], edl["signature"]["from"] / FPS, FPS)
music = np.concatenate([music, np.zeros((max(0, N - len(music)), 2), np.float32)])[:N]
duck_m = np.where(sm < 0.5, 10 ** (-12 / 20), 1.0).astype(np.float32)  # sm is low while speaking
# smooth the music duck
kern = np.ones(int(0.12 * SR)) / int(0.12 * SR)
duck_m = np.convolve(duck_m, kern, mode="same").astype(np.float32)
bed = music * duck_m[:, None] * 10 ** (-4 / 20)

# --- design -----------------------------------------------------------------
fx = np.zeros((N, 2), np.float32)
put(fx, d.reverse_swell(0.4), at(0), -10)
put(fx, d.sub_hit(), at(8), -6)                                   # title lands
for name, (a, b) in edl["sections"].items():
    if name in ("hook", "steam", "outro"):
        continue
    put(fx, d.whoosh(0.6, 500, 3800), at(a - 6), -10)             # chapter swing
ticks = [("id1", "galaxy"), ("id1", "netease"), ("id2", "free"), ("id2", "pc"), ("id2", "data"), ("id3", "zona"),
         ("mov2", "sprint"), ("mov2", "scivolata"), ("mov2", "mira"), ("mov2", "fuoco"),
         ("mov3", "rampino"), ("mov3", "rimbalzi"), ("mov4", "lettura"), ("sq1", "quattro"), ("sq2", "assorbe"),
         ("sq2", "tiene"), ("sq2", "entra"), ("re3", "roaming"), ("ec1", "crediti"), ("ec2", "mina"),
         ("ec2", "siringa"), ("ec3", "piu"), ("wp1", "balistica"), ("wp1", "rinculo"), ("wp1", "maneggevolezza"),
         ("wp2", "parti"), ("wp2", "ottiche"), ("wp2", "impugnatura"),
         ("st1", "arrivo"), ("st2", "aperta"), ("st2", "italiano")]
for lid, wd in ticks:
    put(fx, d.ui_tick(), at(word(lid, wd)), -14, pan=-0.25)
# Blender bridge: blast reinforcement, pull-back whoosh, plate landing.
s3 = edl["s3"]
put(fx, d.sub_hit(48, 28, 1.0), at(s3["from"] + 4), -9)
put(fx, d.whoosh(2.4, 280, 2400), at(s3["from"] + 34), -9)
put(fx, d.landing(), at(s3["from"] + 149), -6)
put(fx, d.whoosh(0.8, 300, 2000), at(s3["from"] + s3["bridge"] - 14), -11)   # page recedes

mix = voice + bed + fx
peak = np.abs(mix).max()
if peak > 0.98:                                  # transparent safety only
    mix *= 0.98 / peak
tail = int(0.4 * SR)
mix[-tail:] *= np.linspace(1, 0, tail)[:, None]
mix = mix[: int(edl["frames"] / FPS * SR)]
wavfile.write(out_path, SR, (mix * 32767).astype(np.int16))
wavfile.write(out_path.replace(".wav", "_voice.wav"), SR, (voice[: len(mix)] * 32767).astype(np.int16))
print("wrote", out_path, f"{len(mix) / SR:.2f}s, peak {20 * np.log10(peak + 1e-9):.1f} dBFS pre-limit")

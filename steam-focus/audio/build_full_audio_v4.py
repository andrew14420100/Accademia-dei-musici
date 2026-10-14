"""STEAM FOCUS — ECC: REDLINE v4 mix: voice B (Chatterbox, natural speed) + v4 score (audio/score_v4.py) + design.

    python3 audio/build_full_audio_v4.py public/full_edl.json VO_DIR OUT_DIR

Writes to OUT_DIR:
  mix.wav        pre-master stereo mix (loudness is normalised at mux time)
  narration.wav  processed voice alone, on the timeline
  music.wav      score alone (stems summed, before ducking)
  stems/         drums, bass, music, fx (score) + design, as placed in the mix

Ducking is per stem: under the voice the melodic stem drops most and also loses
energy in the 1.2-4.5 kHz band where speech consonants live; drums drop less so
the rhythm keeps pushing; the bass drops a little. Fast attack, ~0.35 s release.
No third-party audio is used.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, resample_poly, sosfilt

sys.path.insert(0, os.path.dirname(__file__))
import build_audio as d  # noqa: E402  (shared synth elements: ticks, whooshes, hits)
import score_v4  # noqa: E402

SR = 48000
edl = json.load(open(sys.argv[1]))
VO, OUT = sys.argv[2], sys.argv[3]
os.makedirs(f'{OUT}/stems', exist_ok=True)
FPS = edl['fps']
TOTAL = edl['frames'] / FPS
N = int(TOTAL * SR) + SR // 2


def at(frame):
    return int(round(frame / FPS * SR))


def load_mono(path):
    x, sr = sf.read(path, dtype='float32')
    if x.ndim > 1:
        x = x.mean(1)
    if sr != SR:
        x = resample_poly(x, SR, sr).astype(np.float32)
    return x


def put(bus, sig, start, gain_db=0.0, pan=0.0):
    g = 10 ** (gain_db / 20)
    if sig.ndim == 1:
        lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * lg * 1.414, sig * rg * 1.414], 1)
    e = min(len(bus), start + len(sig))
    if e > start:
        bus[start:e] += g * sig[: e - start]


def word(line_id, prefix):
    import re
    import unicodedata

    def norm(s):
        s = unicodedata.normalize('NFKD', s.lower())
        return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if not unicodedata.combining(c)))

    line = next(l for l in edl['lines'] if l['id'] == line_id)
    w = next(w for w in line['words'] if norm(w[2]).startswith(norm(prefix)))
    return line['from'] + round(w[0] * FPS)


def smooth_env(target, att=0.04, rel=0.35, block=64):
    out = np.empty_like(target)
    y = target[0]
    a_att, a_rel = np.exp(-block / (att * SR)), np.exp(-block / (rel * SR))
    for i in range(0, len(target), block):
        t = target[i]
        y = t + (y - t) * (a_att if t < y else a_rel)
        out[i:i + block] = y
    return out


# --- voice ------------------------------------------------------------------
voice = np.zeros((N, 2), np.float32)
hp = butter(2, 80, 'highpass', fs=SR, output='sos')
presence = butter(2, [2500, 6000], 'bandpass', fs=SR, output='sos')
deess = butter(2, [5500, 9000], 'bandpass', fs=SR, output='sos')
for v in edl['voice']:
    x = load_mono(f"{VO}/{v['id']}.wav")
    x = sosfilt(hp, x)
    x = x + 0.15 * sosfilt(presence, x)
    s = sosfilt(deess, x)  # tame sibilance a little where it is strong
    se = np.sqrt(np.convolve(s ** 2, np.ones(240) / 240, mode='same'))
    x = x - s * np.clip((se - 0.02) / 0.04, 0, 0.5)
    act = np.abs(x) > 0.01
    rms = np.sqrt(np.mean(x[act] ** 2)) if act.any() else 1
    x = x * (0.11 / rms)
    envl = np.sqrt(np.convolve(x ** 2, np.ones(480) / 480, mode='same')) + 1e-6
    thr = 10 ** (-18 / 20)
    x = (x * np.where(envl > thr, (thr * (envl / thr) ** 0.5) / envl, 1.0)).astype(np.float32)
    n = int(0.012 * SR)
    x[:n] *= np.linspace(0, 1, n)
    x[-n:] *= np.linspace(1, 0, n)
    put(voice, np.stack([x, x], 1), at(v['from']))

# voice activity -> 0 (silent) .. 1 (speaking), smoothed
act = (np.abs(voice[:, 0]) > 0.006).astype(np.float32)
act = (np.convolve(act, np.ones(int(0.18 * SR)), mode='same') > 0).astype(np.float32)
speak = 1 - smooth_env(1 - act, att=0.03, rel=0.35)  # rises in ~30 ms, releases over ~0.35 s

# --- score ------------------------------------------------------------------
sig_at = edl['signature']['from'] / FPS
hook2 = next(l for l in edl['lines'] if l['id'] == 'hook2')['from'] / FPS
stems = score_v4.build(TOTAL + 0.3, edl["sections"], sig_at, FPS, drop_at=hook2 - 0.05)
stems = {k: np.concatenate([v, np.zeros((max(0, N - len(v)), 2))])[:N].astype(np.float32) for k, v in stems.items()}
music_raw = sum(stems.values())

BUS = 10 ** (-19 / 20)  # v4: score sits closer to the voice between phrases (-19: voice >= 12 dB over score while speaking)
DUCK_DB = {'music': -15, 'drums': -9, 'bass': -8, 'fx': -11}  # v4: drums keep pushing under the voice
band = butter(2, [1200, 4500], 'bandpass', fs=SR, output='sos')
bed = np.zeros((N, 2), np.float32)
for k, x in stems.items():
    g = 10 ** (DUCK_DB[k] * speak / 20)
    y = x * g[:, None]
    # presence-band carve while speaking (consonants live at 1.2-4.5 kHz)
    y = y - (0.6 if k == 'music' else 0.45) * sosfilt(band, y, axis=0) * speak[:, None]
    stems[k] = (y * BUS).astype(np.float32)
    bed += stems[k]

# --- design (shared with v2, levels re-balanced under the busier score) -----
fx = np.zeros((N, 2), np.float32)
for name, (a, b) in edl['sections'].items():
    if name in ('hook', 'steam', 'outro'):
        continue
    put(fx, d.whoosh(0.6, 500, 3800), at(a - 6), -12)  # chapter swing
ticks = [('id1', 'galaxy'), ('id1', 'netease'), ('id2', 'free'), ('id2', 'pc'), ('id2', 'data'), ('id3', 'zona'),
         ('mov2', 'sprint'), ('mov2', 'scivolata'), ('mov2', 'mira'), ('mov2', 'fuoco'),
         ('mov3', 'rampino'), ('mov3', 'rimbalzi'), ('mov4', 'lettura'), ('sq1', 'quattro'), ('sq2', 'assorbe'),
         ('sq2', 'tiene'), ('sq2', 'entra'), ('re3', 'roaming'), ('ec1', 'crediti'), ('ec2', 'mina'),
         ('ec2', 'siringa'), ('ec3', 'piu'), ('wp1', 'balistica'), ('wp1', 'rinculo'), ('wp1', 'maneggevolezza'),
         ('wp2', 'parti'), ('wp2', 'ottiche'), ('wp2', 'impugnatura'),
         ('st1', 'arrivo'), ('st2', 'aperta'), ('st2', 'italiano')]
for lid, wd in ticks:
    try:
        put(fx, d.ui_tick(), at(word(lid, wd)), -15, pan=-0.25)
    except StopIteration:
        print('tick: word not found', lid, wd)
s3 = edl['s3']
put(fx, d.whoosh(2.4, 280, 2400), at(s3['from'] + 34), -19)  # under the last weapons line
put(fx, d.landing(), at(s3['from'] + 149), -8)
put(fx, d.whoosh(0.8, 300, 2000), at(s3['from'] + s3['bridge'] - 14), -12)
# v4 opening banner (src/full/Banner.tsx BANNER_T): fly-in whoosh, soft landing on beat 1,
# exit swell + whoosh accelerating out, small punch on beat 18 as Identita swings in
BEAT = 60 / 128
put(fx, d.whoosh(0.5, 450, 4200), at(0), -13, pan=0.3)
put(fx, d.landing(), int(round(1 * BEAT * SR)), -15)
put(fx, d.reverse_swell(0.55), int(round((18 * BEAT - 0.55) * SR)), -16)
put(fx, d.whoosh(0.8, 350, 3600), at(226), -14, pan=-0.3)
put(fx, d.punch(0.4), int(round(18 * BEAT * SR)), -17)
fx = fx * (10 ** (-8 * speak / 20))[:, None]  # design ducks under the voice too
stems['design'] = fx

mix = voice + bed + fx
peak = np.abs(mix).max()
if peak > 0.98:
    mix *= 0.98 / peak
L = int(TOTAL * SR)
mix, voice, music_raw = mix[:L], voice[:L], music_raw[:L]
sf.write(f'{OUT}/mix.wav', mix, SR, subtype='PCM_24')
sf.write(f'{OUT}/narration.wav', voice, SR, subtype='PCM_24')
sf.write(f'{OUT}/music.wav', music_raw / max(1e-9, np.abs(music_raw).max()) * 0.89, SR, subtype='PCM_24')
for k, v in stems.items():
    sf.write(f'{OUT}/stems/{k}.wav', v[:L], SR, subtype='PCM_24')


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)


sp = speak[:L] > 0.9
print(f'wrote {OUT}/mix.wav {L / SR:.2f}s, peak {20 * np.log10(peak + 1e-9):.1f} dBFS pre-limit')
print(f'voice vs score while speaking: {rms_db(voice[sp]) - rms_db((bed[:L])[sp]):.1f} dB; '
      f'score between phrases {rms_db((bed[:L])[~sp]) - rms_db(voice[sp]):.1f} dB rel. voice')

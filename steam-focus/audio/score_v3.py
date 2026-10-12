"""STEAM FOCUS v3 — original score: electronic cinematic / hybrid trailer, 124 BPM, D minor.

Everything is synthesized here (no samples, no third-party audio), so the track is
original and reproducible. The arrangement follows the edit's chapters:

  hook      instant impact, full groove (drop) under the title
  identity  driving beat, arp filter opening = build
  movement  fastest, densest section: rolling 16th bass, 16th arp, fills
  squad     driving but with room for the voice (no lead chords)
  reentry   same energy, darker harmony, half-bar breaks
  economy   tech percussion (ticks, rims) on a pulsing bass
  weapons   metallic accents, chords back, snare build at the end
  steam     density drops: no kick, pad + soft arp, so the page can be read
  outro     two-bar rebuild, riser, final impact on the sign-off, short tail

    python audio/score_v3.py public/full_edl.json out.wav

Stems (drums, bass, music, fx) are written next to the mix as *_stem_*.wav so the
mix stage can duck and EQ them separately.
"""
import json
import sys

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
BPM = 124
BEAT = 60 / BPM
BAR = 4 * BEAT
S16 = BEAT / 4
rng = np.random.default_rng(7)

# D minor. Roots in Hz (bass octave) and chord tones as semitones above D3.
D2 = 73.42
PROG_MAIN = [(0, [0, 3, 7]), (-4, [-4, 0, 3]), (3, [3, 7, 10]), (-2, [-2, 2, 5])]  # Dm Bb F C
PROG_DARK = [(0, [0, 3, 7]), (-4, [-4, 0, 3]), (-7, [-7, -4, 0]), (-5, [-5, -1, 2])]  # Dm Bb Gm A


def hz(semi, base=D2):
    return base * 2 ** (semi / 12)


# ------------------------------------------------------------------ DSP helpers

def lp(x, f, order=2):
    return sosfilt(butter(order, min(f, SR / 2.2), 'lowpass', fs=SR, output='sos'), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'highpass', fs=SR, output='sos'), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, min(hi, SR / 2.2)], 'bandpass', fs=SR, output='sos'), x, axis=0)


def env(n, a, d, s=0.0, r=None):
    """Attack / exponential decay to sustain level s."""
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-5), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-5)))
    if r:
        rn = int(r * SR)
        if rn < n:
            e[-rn:] *= np.linspace(1, 0, rn)
    return e


def polyblep(t, dt):
    y = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    y[m] = 2 * x - x * x - 1
    m2 = t > 1 - dt
    x2 = (t[m2] - 1) / dt[m2]
    y[m2] = x2 * x2 + 2 * x2 + 1
    return y


def saw(f, n, phase=0.0):
    """Band-limited sawtooth; f may be a scalar or an array of length n."""
    f = np.broadcast_to(np.asarray(f, float), (n,))
    dt = f / SR
    ph = (phase + np.cumsum(dt)) % 1.0
    return 2 * ph - 1 - polyblep(ph, dt)


def square(f, n, width=0.5):
    return 0.5 * (saw(f, n) - saw(f, n, phase=width))


def supersaw(f, n, voices=7, spread=0.012):
    out = np.zeros((n, 2))
    for i in range(voices):
        d = (i - (voices - 1) / 2) / ((voices - 1) / 2)
        s = saw(f * (1 + spread * d), n, phase=rng.random())
        pan = 0.5 + 0.45 * d
        out[:, 0] += s * np.cos(pan * np.pi / 2)
        out[:, 1] += s * np.sin(pan * np.pi / 2)
    return out / voices


def stereo(x, pan=0.0):
    a = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)


def reverb_ir(seconds=2.2, damp=4500, seed=3):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal((n, 2)) * np.exp(-t * 6.9 / seconds)[:, None]
    ir = lp(ir, damp)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))[:, None]
    return ir / np.sqrt((ir ** 2).sum(0))


IR_HALL = reverb_ir(2.4)
IR_ROOM = reverb_ir(0.7, 7000, seed=5)


def reverb(x, ir, wet):
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x + wet * y


def delay(x, t, fb=0.35, wet=0.3, pingpong=True):
    d = int(t * SR)
    y = np.zeros_like(x)
    tap = x.copy()
    g = wet
    for k in range(1, 6):
        tap = np.roll(tap, d, axis=0)
        tap[:d] = 0
        if pingpong:
            tap = tap[:, ::-1]
        y += g * tap
        g *= fb
    return x + lp(y, 5000)


def put(buf, sig, t, g=1.0):
    s = int(round(t * SR))
    if s >= len(buf):
        return
    if s < 0:
        sig = sig[-s:]
        s = 0
    e = min(len(buf), s + len(sig))
    if sig.ndim == 1 and buf.ndim == 2:
        sig = np.stack([sig, sig], 1)
    buf[s:e] += g * sig[: e - s]


# ------------------------------------------------------------------ instruments

def kick(punch=1.0):
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 46 + 130 * np.exp(-t * 32) + 30 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.22)
    click = hp(rng.standard_normal(n), 2500) * env(n, 0.0003, 0.005) * 0.35
    return np.tanh(2.2 * punch * (body + click)) * 0.95


def snare():
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(185 + 60 * np.exp(-t * 40)) / SR) * env(n, 0.001, 0.07) * 0.6
    noise = bp(rng.standard_normal(n), 1200, 9000) * env(n, 0.001, 0.13) * 0.75
    clapn = bp(rng.standard_normal(n), 900, 3500)
    ce = env(n, 0.001, 0.05)
    for dd in (0.011, 0.022):
        k = int(dd * SR)
        ce[k:] += 0.7 * env(n - k, 0.001, 0.045)
    return np.tanh(1.5 * (body + noise + 0.5 * clapn * ce)) * 0.7


def hat(open_=False):
    n = int((0.26 if open_ else 0.06) * SR)
    x = hp(rng.standard_normal(n), 8000, 4) + 0.3 * hp(square(6200, n), 7000)
    return x * env(n, 0.0005, 0.09 if open_ else 0.018) * 0.22


def rim():
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1650 * t) * 0.6 + bp(rng.standard_normal(n), 2000, 7000) * 0.5) * env(n, 0.0005, 0.012) * 0.5


def tick():
    """Metallic UI tick (FM), for HUD/economy accents."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    mod = np.sin(2 * np.pi * 2310 * t) * 3.0 * env(n, 0.0005, 0.02)
    return np.sin(2 * np.pi * 3300 * t + mod) * env(n, 0.0005, 0.03) * 0.35


def tom(f0=110):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f0 + 80 * np.exp(-t * 25)) / SR) * env(n, 0.001, 0.15) * 0.8


def bass_note(semi, dur, style='roll'):
    n = int(dur * SR)
    f = hz(semi - 12)  # D1 octave sub
    sub = np.sin(2 * np.pi * f * np.arange(n) / SR)
    mid = saw(f * 2, n) + 0.6 * saw(f * 2 * 1.006, n)
    cut = 380 + 1700 * env(n, 0.002, 0.07 if style == 'roll' else 0.16)
    # filter in 4 blocks (cutoff envelope), enough for short notes
    out = np.zeros(n)
    bl = max(1, n // 4)
    for i in range(0, n, bl):
        c = float(cut[i])
        out[i:i + bl] = lp(mid[i:i + bl], c, 2)
    amp = env(n, 0.003, 0.25 if style == 'roll' else 0.5, 0.35, r=0.01)
    return np.tanh(1.6 * (0.9 * sub + 0.45 * out)) * amp * 0.7


def pluck(semi, dur, bright=0.5):
    n = int(dur * SR)
    f = hz(semi + 24)
    x = square(f, n, 0.3) + 0.5 * saw(f * 1.003, n)
    x = lp(x, 900 + 4200 * bright) * env(n, 0.002, 0.09 + 0.08 * bright)
    return x * 0.28


def chord_stab(semis, dur, bright=0.6):
    n = int(dur * SR)
    out = np.zeros((n, 2))
    for s in semis:
        out += supersaw(hz(s + 12), n)
    out = lp(out, 1500 + 3500 * bright) * env(n, 0.01, dur * 0.9, 0.6, r=0.05)[:, None]
    return hp(out, 180) * 0.22


def pad(semis, dur):
    n = int(dur * SR)
    out = np.zeros((n, 2))
    for s in semis:
        out += supersaw(hz(s + 12), n, voices=5, spread=0.006)
    a = np.minimum(1, np.arange(n) / (0.6 * SR))
    rel = np.minimum(1, (n - np.arange(n)) / (0.4 * SR))
    return hp(lp(out, 2200), 200) * (a * rel)[:, None] * 0.16


def impact(size=1.0):
    n = int(2.8 * SR)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(32 + 90 * np.exp(-t * 7)) / SR) * env(n, 0.002, 0.9)
    braam = sum(saw(hz(s - 12), n) for s in (0, 7, 12)) / 3
    braam = lp(braam, 700) * env(n, 0.01, 1.1)
    noise = lp(rng.standard_normal(n), 3000) * env(n, 0.001, 0.25) * 0.5
    x = np.tanh(1.8 * (sub + 0.55 * braam + noise)) * 0.8 * size
    return reverb(stereo(x), IR_HALL, 0.35)


def riser(dur):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    bl = n // 32 or 1
    for i in range(0, n, bl):
        c = 400 + 9000 * t[i] ** 2
        out[i:i + bl] = bp(noise[i:i + bl], c * 0.7, c * 1.3, 1)
    tone = saw(110 * 2 ** (2 * t), n) * 0.15
    return stereo((out * 0.5 + lp(tone, 3000)) * t ** 2.2 * 0.6)


def reverse_cymbal(dur=1.2):
    n = int(dur * SR)
    x = hp(rng.standard_normal(n), 5000) * np.linspace(0, 1, n) ** 3 * 0.35
    return stereo(x)


# ------------------------------------------------------------------ arrangement

LAYERS = {
    #            kick  snare hats  bass    arp   chords pad  perc   prog
    'hook':     (1,    1,    1,   'roll', 0.8,  1,     0,   0,     'main'),
    'identity': (1,    0.5,  1,   'eight', 0.5, 0,     1,   0,     'main'),
    'movement': (1,    1,    1,   'roll', 1.0,  1,     0,   1,     'main'),
    'squad':    (1,    1,    1,   'eight', 0.6, 0,     1,   0,     'main'),
    'reentry':  (1,    1,    1,   'eight', 0.6, 0,     1,   0,     'dark'),
    'economy':  (1,    1,    1,   'pulse', 0.5, 0,     1,   2,     'main'),
    'weapons':  (1,    1,    1,   'roll', 0.7,  1,     0,   2,     'dark'),
    'steam':    (0,    0,    0.5, 'none', 0.35, 0,     1,   0,     'main'),
    'outro':    (1,    1,    1,   'roll', 0.9,  1,     0,   1,     'main'),
}


def build(total_s, sections, signature_at, fps, cue_hits=()):
    N = int((total_s + 0.1) * SR)
    drums = np.zeros((N, 2))
    bass = np.zeros((N, 2))
    music = np.zeros((N, 2))
    fx = np.zeros((N, 2))
    secs = {k: (a / fps, b / fps) for k, (a, b) in sections.items()}

    def section_of(t):
        for k, (a, b) in secs.items():
            if a <= t < b:
                return k
        return 'outro'

    def sec_progress(t):
        a, b = secs[section_of(t)]
        return (t - a) / max(b - a, 1e-3)

    K, SN = kick(), snare()
    HC, HO, RM, TK = hat(), hat(True), rim(), tick()
    n16 = int(signature_at / S16) + 1
    for i in range(n16):
        t = i * S16
        sec = section_of(t)
        kick_on, snare_on, hats_on, bass_style, arp_lvl, chords_on, pad_on, perc, prog = LAYERS[sec]
        P = PROG_DARK if prog == 'dark' else PROG_MAIN
        bar, rem = divmod(i, 16)
        beat, sub = divmod(rem, 4)
        root, tones = P[(bar // 2) % 4]
        a, b = secs.get(sec, (0, total_s))
        # a short rhythmic stop (drums + bass) in the last half-beat before each new chapter
        nxt = b
        stop = (nxt - t) < BEAT / 2 and sec not in ('outro',) and t > 1
        # identity: half the snares until halfway (build); hook: first beat is the impact
        if kick_on and not stop:
            if sub == 0:
                put(drums, K, t, 1.0 if beat in (0, 2) else 0.85)
            if sec in ('movement', 'outro') and beat == 3 and sub == 2 and bar % 2:
                put(drums, K, t, 0.6)
        if snare_on and not stop and sub == 0 and beat in (1, 3):
            if snare_on >= 1 or sec_progress(t) > 0.5:
                put(drums, stereo(SN, 0.05), t, 0.9)
        if hats_on and not stop:
            vel = (0.35, 0.18, 0.75, 0.2)[sub] * hats_on
            h = HO if (sub == 2 and beat == 3 and bar % 2 == 1) else HC
            put(drums, stereo(h, 0.35 if sub % 2 else -0.25), t + (0.012 if sub % 2 else 0), vel)
        if perc == 1 and not stop and bar % 4 == 3 and beat == 3:  # fill
            put(drums, stereo(tom(150 - 20 * sub), -0.3 + 0.2 * sub), t, 0.55)
        if perc == 2 and not stop:
            if sub in (1, 3) and (beat + sub) % 3 == 0:
                put(drums, stereo(RM, 0.4), t, 0.5)
            if sub == 3:
                put(drums, stereo(TK, -0.5 if beat % 2 else 0.5), t, 0.45)
        # bass
        if bass_style != 'none' and not stop:
            if bass_style == 'roll' and sub != 0:
                put(bass, stereo(bass_note(root, S16 * 0.95)), t, 0.8)
            elif bass_style == 'eight' and sub == 2:
                put(bass, stereo(bass_note(root, BEAT / 2 * 0.95, 'eight')), t, 0.9)
            elif bass_style == 'pulse' and sub in (0, 2, 3):
                put(bass, stereo(bass_note(root + (12 if sub == 3 else 0), S16 * 0.9)), t, 0.75)
        # arpeggio: chord tones over two octaves, filter opens through each section
        if arp_lvl > 0:
            seq = [tones[0], tones[1], tones[2], tones[0] + 12, tones[2], tones[1] + 12, tones[2] + 12, tones[1]]
            note = seq[(i % 8)]
            fast = sec in ('movement', 'hook', 'outro', 'weapons')
            if fast or sub % 2 == 0:
                bright = 0.25 + 0.7 * sec_progress(t) if sec == 'identity' else 0.55
                pan = 0.45 if (i % 2) else -0.45
                put(music, stereo(pluck(note, S16 * (1 if fast else 2) * 0.9, bright), pan), t, arp_lvl)
        # chords / pad on bar starts (2 bars per chord)
        if rem == 0 and bar % 2 == 0:
            if chords_on:
                for k in range(4):  # rhythmic stabs: 1, 1-and-a, 3, 4-and
                    st = (0, 0.75, 2, 3.5)[k] * BEAT
                    if t + st < signature_at:
                        put(music, chord_stab(tones, BEAT * 0.7), t + st, 0.8)
                        put(music, chord_stab(tones, BEAT * 0.7), t + BAR + st, 0.8)
            if pad_on:
                put(music, pad(tones, 2 * BAR), t, 1.0)

    # chapter transitions: riser into an impact on the cut; hook starts on an impact
    put(fx, impact(1.1), 0.0)
    for name in ('identity', 'movement', 'squad', 'reentry', 'economy', 'weapons', 'steam', 'outro'):
        if name not in secs:
            continue
        t = secs[name][0]
        put(fx, riser(BAR), t - BAR, 0.55)
        put(fx, reverse_cymbal(1.0), t - 1.0, 0.8)
        put(fx, impact(0.7 if name == 'steam' else 0.9), t)
    # editorial accents (e.g. the movement chain), a light tick on each
    for t in cue_hits:
        put(fx, stereo(tick(), 0.2), t, 0.6)
    # sign-off: final hit, short tail, hard stop (no long fade)
    put(fx, riser(BAR), signature_at - BAR, 0.7)
    put(fx, impact(1.2), signature_at)
    put(music, chord_stab(PROG_MAIN[0][1], 1.2, 0.9), signature_at, 1.2)

    # sidechain on the kick for bass and music
    duck = np.ones(N)
    for i in range(int(signature_at / BEAT)):
        t = i * BEAT
        if LAYERS[section_of(t)][0]:
            s = int(t * SR)
            m = min(N - s, int(0.22 * SR))
            duck[s:s + m] = np.minimum(duck[s:s + m], 1 - 0.6 * np.exp(-np.arange(m) / (0.06 * SR)))
    bass *= duck[:, None]
    music = delay(music, BEAT * 0.75, 0.32, 0.22) * duck[:, None]
    music = reverb(music, IR_HALL, 0.18)
    drums = reverb(drums, IR_ROOM, 0.12)

    # tail: everything ends 1.4 s after the sign-off hit
    end = int((signature_at + 1.4) * SR)
    for x in (drums, bass, music, fx):
        x[end:] = 0
        k = int(0.25 * SR)
        x[end - k:end] *= np.linspace(1, 0, k)[:, None]
    # chapter intensity (dB): identity builds, movement peaks, explanations sit lower
    gain_db = {'hook': 0, 'identity': (-5, -1), 'movement': 0, 'squad': -3, 'reentry': -3.5,
               'economy': -2.5, 'weapons': -1.5, 'steam': 0, 'outro': 0}
    g = np.zeros(N)
    for name, (a, b) in secs.items():
        v = gain_db.get(name, 0)
        lo, hi = (v, v) if np.isscalar(v) else v
        ia, ib = int(a * SR), min(N, int(b * SR))
        g[ia:ib] = np.linspace(lo, hi, max(ib - ia, 1))
    g[int(secs['outro'][1] * SR):] = 0
    k = int(0.25 * SR)
    g = np.convolve(g, np.ones(k) / k, mode='same')
    lin = (10 ** (g / 20))[:, None]
    return {'drums': drums * lin, 'bass': lp(bass, 4000) * lin * 0.85, 'music': music * lin, 'fx': fx}


def glue(stems):
    mix = stems['drums'] + stems['bass'] + 0.85 * stems['music'] + 0.9 * stems['fx']
    return np.tanh(mix * 1.1) / 1.1


def main():
    import soundfile as sf
    edl = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    fps = edl['fps']
    sig = edl['signature']['from'] / fps if 'signature' in edl else edl['frames'] / fps - 1.6
    total = edl['frames'] / fps
    stems = build(total, edl['sections'], sig, fps)
    mix = glue(stems)
    peak = np.abs(mix).max()
    for k, v in stems.items():
        sf.write(out.replace('.wav', f'_stem_{k}.wav'), (v / peak * 0.89).astype(np.float32), SR)
    sf.write(out, (mix / peak * 0.89).astype(np.float32), SR)
    print('wrote', out, f'{len(mix) / SR:.1f}s')


if __name__ == '__main__':
    main()

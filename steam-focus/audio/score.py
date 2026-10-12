"""Original procedural score for the STEAM FOCUS report (no third-party audio).

100 BPM, A minor, i–VI–III–VII (Am–F–C–G), two bars per chord. The arrangement
follows the edit: a rising hook, a groove under the chapters with downbeat
accents on each chapter start, a lighter texture on the Steam page, and a
sting under the 1.6 s sign-off. All sounds are synthesized here.
"""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
BPM = 100
BEAT = 60 / BPM
rng = np.random.default_rng(23)

# chord roots (Hz, bass octave) and triads (Hz, pad octave)
CHORDS = [
    (110.00, [220.00, 261.63, 329.63]),   # Am
    (87.31, [174.61, 220.00, 261.63]),    # F
    (130.81, [261.63, 329.63, 392.00]),   # C
    (98.00, [196.00, 246.94, 293.66]),    # G
]


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "lowpass", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "highpass", fs=SR, output="sos"), x)


def env(n, a, r):
    t = np.arange(n) / SR
    return np.clip(t / max(a, 1e-4), 0, 1) * np.exp(-np.clip(t - a, 0, None) / max(r, 1e-4))


def saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    ph = (f * (1 + detune)) * t
    return 2 * (ph % 1) - 1


def kick():
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.16)
    click = hp(rng.standard_normal(n), 3000) * env(n, 0.0005, 0.004) * 0.15
    return np.tanh(1.6 * (x + click)) * 0.9


def clap():
    n = int(0.25 * SR)
    x = sosfilt(butter(2, [900, 4500], "bandpass", fs=SR, output="sos"), rng.standard_normal(n))
    e = env(n, 0.001, 0.07)
    for d in (0.012, 0.024):  # flam
        k = int(d * SR)
        e[k:] += 0.6 * env(n - k, 0.001, 0.05)
    return x * e * 0.35


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.0005, 0.06 if open_ else 0.015) * 0.12


def build(total_s, sections, signature_at, fps):
    """sections: {name: (start_frame, end_frame)} at `fps` base frames."""
    N = int(total_s * SR)
    drums = np.zeros(N)
    bass = np.zeros(N)
    pad = np.zeros((N, 2))
    fx = np.zeros(N)
    sec_at = lambda name: sections[name][0] / fps  # noqa: E731

    def section_of(t):
        for k, (a, b) in sections.items():
            if a / fps <= t < b / fps:
                return k
        return "outro"

    def put(buf, sig, t, g=1.0):
        s = int(t * SR)
        e = min(len(buf), s + len(sig))
        if e > s:
            buf[s:e] += g * sig[: e - s]

    K, C = kick(), clap()
    n_beats = int(total_s / BEAT) + 1
    for b in range(n_beats):
        t = b * BEAT
        sec = section_of(t)
        bar, beat = divmod(b, 4)
        root, triad = CHORDS[(bar // 2) % 4]
        if t >= signature_at:
            break
        quiet = sec in ("steam",)
        hook = sec == "hook"
        # drums
        if not quiet and not (hook and t < 2.4):
            put(drums, K, t, 0.9 if beat in (0, 2) else (0.0 if hook else 0.55))
            if beat in (1, 3) and not hook:
                put(drums, C, t, 0.8)
        for s16 in range(4):
            if not hook or t > 2.4:
                put(drums, hat(open_=(s16 == 2 and beat == 3)), t + s16 * BEAT / 4, 0.9 if s16 % 2 else 0.55)
        # bass: 8th notes on the chord root, octave jump on the last 8th
        for e8 in range(2):
            n = int(BEAT / 2 * SR * 0.92)
            f = root * (2 if (beat == 3 and e8 == 1) else 1)
            tone = np.sin(2 * np.pi * f * np.arange(n) / SR) + 0.35 * np.sin(4 * np.pi * f * np.arange(n) / SR)
            put(bass, np.tanh(1.4 * tone) * env(n, 0.004, 0.18) * (0.42 if quiet else 0.6), t + e8 * BEAT / 2)
    # pad: one chord per 2 bars, slow attack, detuned saws through a low-pass
    bar_s = 4 * BEAT
    for i in range(int(total_s / (2 * bar_s)) + 1):
        t = i * 2 * bar_s
        if t >= signature_at:
            break
        _, triad = CHORDS[i % 4]
        n = int(2 * bar_s * SR)
        x = np.zeros(n)
        for f in triad:
            for d in (-0.004, 0.0, 0.004):
                x += saw(f, n, d)
        x = hp(lp(x, 1400), 150) * env(n, 0.9, 6.0) * 0.06
        left, right = x * 0.9, np.roll(x, int(0.011 * SR)) * 0.9
        s = int(t * SR)
        e = min(N, s + n)
        pad[s:e, 0] += left[: e - s]
        pad[s:e, 1] += right[: e - s]

    # chapter accents: reverse swell into a sub hit on each chapter start
    for name in ("identity", "movement", "squad", "reentry", "economy", "weapons", "steam"):
        t = sec_at(name)
        n = int(0.9 * SR)
        swell = hp(rng.standard_normal(n), 1500) * (np.arange(n) / n) ** 3 * 0.12
        put(fx, swell, t - 0.9)
        m = int(1.2 * SR)
        tt = np.arange(m) / SR
        sub = np.sin(2 * np.pi * np.cumsum(40 + 50 * np.exp(-tt * 9)) / SR) * env(m, 0.003, 0.5) * 0.5
        put(fx, sub, t)
    # hook: rising filtered pulse until the title, then an impact
    n = int(2.4 * SR)
    rise = lp(saw(55, n), 300) * (np.arange(n) / n) ** 2 * 0.25
    put(fx, rise, 0.0)
    # sign-off sting: Am add9 chord + sub, 1.6 s
    n = int(1.8 * SR)
    st = np.zeros(n)
    for f in (220.0, 261.63, 329.63, 493.88):
        st += saw(f, n, 0.003) + saw(f, n, -0.003)
    st = lp(st, 2200) * env(n, 0.01, 0.7) * 0.07
    tt = np.arange(n) / SR
    st += np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-tt * 8)) / SR) * env(n, 0.002, 0.6) * 0.55
    put(fx, st, signature_at)

    # sidechain: pad and bass duck on each kick
    duck = np.ones(N)
    for b in range(n_beats):
        t = b * BEAT
        if t >= signature_at or section_of(t) == "steam":
            continue
        s = int(t * SR)
        m = min(N - s, int(0.3 * SR))
        if m > 0:
            duck[s:s + m] = np.minimum(duck[s:s + m], 1 - 0.55 * np.exp(-np.arange(m) / (0.08 * SR)))
    bass = lp(bass * duck, 900)
    pad = pad * duck[:, None]

    mono = drums + bass + fx
    out = np.stack([mono, mono], 1) + pad
    # gentle bus glue
    out = np.tanh(out * 1.2) / 1.2
    return out.astype(np.float32)

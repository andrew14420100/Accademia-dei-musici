"""STEAM FOCUS — ECC: REDLINE demo sound design (48 kHz stereo, 15 s).

Bed: the official trailer audio of each shot. On top: synthesized design
elements placed on exact video frames (30 fps), so picture and sound share
one timeline. Loudness normalisation happens at mux time (ffmpeg loudnorm).

usage: python3 build_audio.py <dir with audio_s1/2/3.wav> <out.wav>
"""
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt, sosfiltfilt

SR = 48000
FPS = 30
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(11)


def at(frame):
    return int(round(frame / FPS * SR))


def load(path):
    sr, x = wavfile.read(path)
    assert sr == SR, path
    x = x.astype(np.float32) / 32768.0
    return x if x.ndim == 2 else np.stack([x, x], 1)


def env(n, attack, release, shape=4.0):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    r = np.exp(-shape * np.clip(t - attack, 0, None) / max(release, 1e-4))
    return a * r


def band(x, lo, hi, order=4):
    return sosfilt(butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, "highpass", fs=SR, output="sos"), x)


def lp(x, f):
    return sosfilt(butter(2, f, "lowpass", fs=SR, output="sos"), x)


def sweep_sine(f0, f1, dur, curve=3.0):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    f = f1 + (f0 - f1) * np.exp(-curve * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def reverb(x, seconds=1.4, mix=0.25):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-6.0 * np.arange(n) / n)
    ir = lp(ir, 6000)
    ir /= np.sqrt((ir ** 2).sum())
    wet = fftconvolve(x, ir)[: len(x)]
    return (1 - mix) * x + mix * wet


def place(bus, sig, frame, gain_db=0.0, pan=0.0):
    """Mono or stereo signal into the stereo bus at a video frame."""
    g = 10 ** (gain_db / 20)
    if sig.ndim == 1:
        lgain, rgain = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * lgain * 1.414, sig * rgain * 1.414], 1)
    s = at(frame)
    e = min(N, s + len(sig))
    if e > s:
        bus[s:e] += g * sig[: e - s]


def pad(n):
    return np.zeros(n, np.float32)


# --- design elements --------------------------------------------------------
def sub_hit(f0=58, f1=30, dur=1.6):
    s = sweep_sine(f0, f1, dur) * env(int(dur * SR), 0.004, dur * 0.55)
    click = hp(rng.standard_normal(int(0.03 * SR)), 2500) * env(int(0.03 * SR), 0.0005, 0.012) * 0.5
    s[: len(click)] += click
    return s


def reverse_swell(dur=0.7):
    n = int(dur * SR)
    x = band(rng.standard_normal(n), 300, 5000)
    e = (np.arange(n) / n) ** 3
    return x * e * 0.5


def punch(dur=0.45):
    n = int(dur * SR)
    s = sweep_sine(110, 45, dur, 6) * env(n, 0.002, dur * 0.35)
    crack = band(rng.standard_normal(n), 900, 7000) * env(n, 0.0008, 0.05)
    return s + 0.35 * crack


def ui_tick():
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    a = np.sin(2 * np.pi * 1760 * t) * env(n, 0.001, 0.025)
    b = np.zeros(n)
    k = int(0.045 * SR)
    b[k:] = np.sin(2 * np.pi * 2637 * t[: n - k]) * env(n - k, 0.001, 0.03)
    return reverb((a + 0.8 * b) * 0.32, 0.6, 0.2)


def whoosh(dur, f_lo, f_hi):
    """Noise swept through a resonant band; bell envelope; stereo travel."""
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    hop = 1024
    t = np.arange(0, n, hop)
    for i, s in enumerate(t):
        u = s / n
        fc = f_lo + (f_hi - f_lo) * np.sin(np.pi * u) ** 1.5
        seg = noise[max(0, s - 4096): s + hop]
        y = band(seg, fc * 0.6, min(fc * 1.6, 20000), 2)[-(min(hop, n - s)):]
        out[s: s + len(y)] = y
    u = np.linspace(0, 1, n)
    e = np.sin(np.pi * u) ** 2.2
    mono = out * e * 0.7
    pan = np.linspace(-0.7, 0.7, n)
    return np.stack([mono * np.cos((pan + 1) * np.pi / 4), mono * np.sin((pan + 1) * np.pi / 4)], 1) * 1.414


def drone(dur, rise=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f, a in [(55.0, 0.55), (82.41, 0.28), (110.0, 0.22), (164.81, 0.08)]:
        for det in (-0.12, 0.12):
            ph = 2 * np.pi * (f + det) * t
            x += a * (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.5   # saw
    cutoff = np.linspace(180, 900, n) if rise else np.full(n, 300.0)
    y = np.zeros(n)
    hop = 2048
    for s in range(0, n, hop):
        y[s: s + hop] = lp(x[max(0, s - 8192): s + hop], cutoff[s])[-len(x[s: s + hop]):]
    fade = np.minimum(1, np.minimum(t / 0.8, (dur - t) / 0.8))
    return y * np.clip(fade, 0, 1) * 0.35


def landing():
    n = int(0.9 * SR)
    body = sweep_sine(95, 48, 0.9, 8) * env(n, 0.002, 0.28)
    knock = np.sin(2 * np.pi * 230 * np.arange(n) / SR) * env(n, 0.001, 0.05) * 0.4
    glass = band(rng.standard_normal(n), 3500, 9000) * env(n, 0.0005, 0.02) * 0.35
    return reverb(body + knock + glass, 1.1, 0.22)


def end_tail(dur=1.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    pad_ = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(220, 0.25), (329.6, 0.18), (440.6, 0.08)])
    air = band(rng.standard_normal(n), 2000, 9000) * 0.06
    e = env(n, 0.05, dur * 0.5, 3)
    return reverb((pad_ + air) * e * 0.5 + 0.8 * sub_hit(52, 28, dur)[:n], 1.8, 0.35)


def main(src, out):
    bus = np.zeros((N, 2), np.float32)

    # Game audio beds, cut on picture (S1 0-103, S2 104-157, S3 158-449).
    s1, s2, s3 = load(f"{src}/audio_s1.wav"), load(f"{src}/audio_s2.wav"), load(f"{src}/audio_s3.wav")
    fade = int(0.006 * SR)

    def bed(x, f_from, f_len, gain_db=0.0):
        n = min(len(x), at(f_len))
        x = x[:n].copy()
        r = np.linspace(0, 1, fade)[:, None]
        x[:fade] *= r
        x[-fade:] *= r[::-1]
        place(bus, x, f_from, gain_db)

    s1 = s1.copy()
    s1[: int(0.35 * SR)] *= np.linspace(0, 1, int(0.35 * SR))[:, None]
    bed(s1, 0, 104, -2)
    bed(s2, 104, 54, -1)

    # S3: full until the pull-back, then the trailer recedes into the page:
    # low-pass sweep + level drop, as if it now plays inside the store's player.
    x = s3[: at(292)].copy()
    n = len(x)
    i0, i1 = at(200 - 158), at(262 - 158)
    lo = np.zeros_like(x)
    for c in range(2):
        lo[:, c] = sosfiltfilt(butter(2, 900, "lowpass", fs=SR, output="sos"), x[:, c])
    m = np.clip((np.arange(n) - i0) / (i1 - i0), 0, 1)[:, None]
    gain = 10 ** ((-14 * m) / 20)
    x = ((1 - m) * x + m * lo) * gain
    x[at(262 - 158):] *= np.clip(1 - (np.arange(n - at(262 - 158)) / at(160)), 0, 1)[:, None]
    x[:fade] *= np.linspace(0, 1, fade)[:, None]
    place(bus, x, 158)

    # Design layer.
    place(bus, band(rng.standard_normal(at(30)), 400, 3000) * env(at(30), 0.6, 0.4) * 0.12, 0)  # air in
    place(bus, reverse_swell(0.6), 52 - 18, -6)
    place(bus, sub_hit(), 52, -3)                       # title lands
    place(bus, punch(), 104, -4)                        # cut to combat
    place(bus, ui_tick(), 107, -6, pan=-0.3)            # runner callout
    place(bus, sub_hit(48, 28, 1.0), 158, -6)           # reinforce the scope blast
    place(bus, whoosh(2.4, 280, 2400), 192, -5)         # camera pull-back
    place(bus, drone(7.9), 200, -8)                     # bed under the page
    place(bus, landing(), 158 + 149, -3)                # plate seats in the player
    place(bus, ui_tick(), 158 + 168, -6, pan=-0.2)      # release callout
    place(bus, ui_tick(), 158 + 214, -6, pan=-0.2)      # italian callout
    place(bus, end_tail(), 158 + 264, -4)               # Steam end card

    # Gentle bus glue: soft clip only above -1 dBFS peaks.
    peak = np.abs(bus).max()
    bus = np.tanh(bus / max(peak, 1e-6) * 1.2) / np.tanh(1.2) * 0.89
    tail = int(0.25 * SR)
    bus[-tail:] *= np.linspace(1, 0, tail)[:, None]
    wavfile.write(out, SR, (bus * 32767).astype(np.int16))
    print("wrote", out, f"{len(bus) / SR:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

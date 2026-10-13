"""STEAM FOCUS v4 — original score: electronic cinematic / futuristic action, 128 BPM, D minor.

Same instruments as v3 (audio/score_v3.py, all synthesized here: no samples, no
third-party audio) but a real arrangement instead of one groove with layers switched
on and off. Each chapter has its own drum pattern, bass figure and lead texture; every
4 bars there is a fill, every 8 bars the hats, chord voicing and arpeggio order change,
so no two minutes of the same loop:

  hook      impact, then a 2-bar build (sub, rising arp) into a full drop
  identity  four-on-the-floor, offbeat open hats, filter opening = build
  movement  fastest: syncopated kicks, 16th hats, ghost snares, rolling bass, stabs
  squad     half-time snare (tension), toms, pulsing bass, dark pads
  reentry   breath bar (no kick) + riser, then driving groove on the dark progression
  economy   tech: rims/ticks in shuffle, staccato plucks, bass pulse
  weapons   heavy: distorted reese bass, metallic hits on beat 4, stabs
  steam     breakdown: pads, soft arp, sub pulses only (the page must be read)
  outro     two-bar drop, final impact on the sign-off, 1.4 s tail

    python audio/score_v4.py public/full_edl.json out.wav   (also writes *_stem_*.wav)
"""
import json
import sys

import numpy as np

import score_v3 as s3
from score_v3 import (IR_HALL, IR_ROOM, PROG_DARK, PROG_MAIN, SR, bass_note, chord_stab, delay, hat, impact, kick,
                      lp, hp, pad, pluck, put, reverb, reverse_cymbal, rim, riser, saw, snare, stereo, supersaw, tick,
                      tom, env, hz)

BPM = 128
BEAT = 60 / BPM
BAR = 4 * BEAT
S16 = BEAT / 4
rng = np.random.default_rng(11)


def reese(semi, dur):
    """Detuned, distorted low saw pair (weapons chapter)."""
    n = int(dur * SR)
    f = hz(semi - 12)
    x = saw(f, n) + saw(f * 1.012, n, 0.3) + 0.6 * np.sin(2 * np.pi * f / 2 * np.arange(n) / SR)
    x = np.tanh(2.2 * lp(x, 420)) * env(n, 0.004, dur * 0.7, 0.4, r=0.02)
    return x * 0.55


def metal_hit():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t + 2 * np.sin(2 * np.pi * f * 1.41 * t)) for f in (520, 787, 1210))
    return hp(x / 3, 300) * env(n, 0.001, 0.12) * 0.4


def snare_roll(beats=1.0, start_vel=0.25, end_vel=0.9):
    n16 = int(beats * 4)
    out = []
    for i in range(n16):
        out.append((i * S16, start_vel + (end_vel - start_vel) * i / max(1, n16 - 1)))
    return out


# drum pattern per chapter: per 16th step -> instrument velocities
#            0     1     2     3     4     5     6     7     8     9     10    11    12    13    14    15
PATTERNS = {
    'four':   dict(kick=[1, 0, 0, 0, .9, 0, 0, 0, 1, 0, 0, 0, .9, 0, 0, 0],
                   clap=[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                   hat=[0, 0, .7, 0, 0, 0, .7, 0, 0, 0, .7, 0, 0, 0, .7, 0], open=[2, 6, 10, 14]),
    'drive':  dict(kick=[1, 0, 0, .5, .9, 0, 0, 0, 1, 0, .6, 0, .9, 0, 0, .4],
                   clap=[0, 0, 0, 0, 1, 0, 0, .2, 0, 0, 0, 0, 1, 0, .25, 0],
                   hat=[.5, .25, .8, .25, .5, .25, .8, .3, .5, .25, .8, .25, .5, .3, .8, .35], open=[14]),
    'half':   dict(kick=[1, 0, 0, 0, 0, 0, .6, 0, 0, 0, .8, 0, 0, 0, 0, 0],
                   clap=[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                   hat=[.6, .2, .4, .2, .6, .2, .4, .2, .6, .2, .4, .2, .6, .2, .4, .3], open=[]),
    'tech':   dict(kick=[1, 0, 0, 0, .9, 0, 0, 0, 1, 0, 0, 0, .9, 0, 0, 0],
                   clap=[0, 0, 0, 0, .9, 0, 0, 0, 0, 0, 0, 0, .9, 0, 0, 0],
                   hat=[.4, 0, .6, .2, .4, 0, .6, .2, .4, 0, .6, .2, .4, 0, .6, .25], open=[]),
    'heavy':  dict(kick=[1, 0, 0, 0, 0, 0, .8, 0, 1, 0, 0, .5, 0, 0, .8, 0],
                   clap=[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                   hat=[.5, 0, .7, 0, .5, 0, .7, 0, .5, 0, .7, 0, .5, 0, .7, .3], open=[10]),
}

STYLE = {
    #            pattern  bass     arp   lead     prog    fill
    'hook':     ('drive', 'roll',  .8,  'stabs',  'main', 'snare'),
    'identity': ('four',  'off',   .5,  'pad',    'main', 'snare'),
    'movement': ('drive', 'roll',  1.0, 'stabs',  'main', 'snare'),
    'squad':    ('half',  'pulse', .6,  'pad',    'main', 'tom'),
    'reentry':  ('drive', 'off',   .6,  'pad',    'dark', 'tom'),
    'economy':  ('tech',  'pulse', .55, 'pluck8', 'main', 'tick'),
    'weapons':  ('heavy', 'reese', .6,  'stabs',  'dark', 'snare'),
    'steam':    (None,    'sub',   .35, 'pad',    'main', None),
    'outro':    ('drive', 'roll',  .9,  'stabs',  'main', 'snare'),
}


def build(total_s, sections, signature_at, fps, drop_at=None, accents=()):
    N = int((total_s + 0.1) * SR)
    drums, bass, music, fx = (np.zeros((N, 2)) for _ in range(4))
    secs = {k: (a / fps, b / fps) for k, (a, b) in sections.items()}

    def section_of(t):
        for k, (a, b) in secs.items():
            if a <= t < b:
                return k
        return 'outro'

    def progress(t):
        a, b = secs[section_of(t)]
        return (t - a) / max(b - a, 1e-3)

    K, SN, HC, HO, RM, TK = kick(), snare(), hat(), hat(True), rim(), tick()
    MH = metal_hit()
    n16 = int(signature_at / S16) + 1
    for i in range(n16):
        t = i * S16
        sec = section_of(t)
        pat_name, bass_style, arp_lvl, lead, prog, fill = STYLE[sec]
        P = PROG_DARK if prog == 'dark' else PROG_MAIN
        bar, step = divmod(i, 16)
        beat = step // 4
        root, tones = P[(bar // 2) % 4]
        var = (bar // 8) % 2  # 8-bar variation
        a, b = secs.get(sec, (0, total_s))
        stop = (b - t) < BEAT / 2 and sec != 'outro' and t > 1  # rhythmic break before each chapter
        pre_drop = drop_at is not None and sec == 'hook' and t < drop_at
        breath = sec == 'reentry' and t - a < BAR  # first bar of reentry: no kick
        fill_now = fill and bar % 4 == 3 and beat == 3 and not stop
        # drums
        if pat_name and not stop and not pre_drop:
            p = PATTERNS[pat_name]
            if p['kick'][step] and not breath and not (fill_now and fill == 'snare' and step > 12):
                put(drums, K, t, p['kick'][step])
            if p['clap'][step]:
                put(drums, stereo(SN, 0.05), t, 0.85 * p['clap'][step])
            hv = p['hat'][step]
            if var and pat_name in ('four', 'drive') and step % 2:  # variation: busier hats
                hv = max(hv, 0.3)
            if hv:
                h = HO if (step in p['open'] and (var or pat_name == 'four')) else HC
                put(drums, stereo(h, 0.35 if step % 2 else -0.25), t + (0.01 if step % 2 else 0), hv * 0.9)
            if pat_name == 'tech' and step in (3, 7, 11, 14, 15):
                put(drums, stereo(RM if step % 2 else TK, 0.45 if step % 2 else -0.45), t, 0.35)
            if pat_name == 'heavy' and step == 15:
                put(drums, stereo(MH, -0.2), t, 0.6)
        if fill_now and step == 12:
            if fill == 'snare':
                for dt, v in snare_roll(1.0):
                    put(drums, stereo(SN, 0.1), t + dt, 0.55 * v)
            elif fill == 'tom':
                for k, f0 in enumerate((180, 150, 120, 95)):
                    put(drums, stereo(tom(f0), -0.4 + 0.25 * k), t + k * S16, 0.6)
            elif fill == 'tick':
                for k in range(4):
                    put(drums, stereo(TK, 0.5 - 0.3 * k), t + k * S16, 0.4)
        # bass
        if not stop:
            if bass_style == 'roll' and step % 4 and not pre_drop:
                put(bass, stereo(bass_note(root, S16 * 0.95)), t, 0.8)
            elif bass_style == 'off' and step % 4 == 2:
                put(bass, stereo(bass_note(root, BEAT / 2 * 0.95, 'eight')), t, 0.9)
            elif bass_style == 'pulse' and step in (0, 3, 6, 8, 11, 14):
                put(bass, stereo(bass_note(root + (12 if step == 14 else 0), S16 * 1.6)), t, 0.75)
            elif bass_style == 'reese' and step % 8 == 0:
                put(bass, stereo(reese(root, BEAT * 1.9)), t, 0.8)
            elif bass_style == 'sub' and step == 0 and bar % 2 == 0:
                put(bass, stereo(np.sin(2 * np.pi * hz(root - 12) * np.arange(int(BAR * SR)) / SR)
                                 * env(int(BAR * SR), 0.05, 1.2)), t, 0.45)
            if pre_drop and step == 0:  # hook build: sustained sub under the title
                put(bass, stereo(np.sin(2 * np.pi * hz(root - 12) * np.arange(int(BAR * SR)) / SR)
                                 * env(int(BAR * SR), 0.02, 2.0)), t, 0.5)
        # arpeggio (order rotates every 8 bars; filter opens through identity and hook build)
        if arp_lvl:
            seqA = [0, 1, 2, 3, 2, 4, 5, 1]
            seqB = [0, 2, 1, 3, 5, 2, 4, 3]
            pool = [tones[0], tones[1], tones[2], tones[0] + 12, tones[1] + 12, tones[2] + 12]
            note = pool[(seqB if var else seqA)[i % 8]]
            fast = sec in ('movement', 'hook', 'outro', 'weapons')
            if lead == 'pluck8' and step % 2 == 0:
                put(music, stereo(pluck(note, S16 * 0.8, 0.7), 0.4 if step % 4 else -0.4), t, arp_lvl)
            elif lead != 'pluck8' and (fast or step % 2 == 0):
                bright = 0.25 + 0.7 * progress(t) if sec in ('identity',) or pre_drop else 0.6
                put(music, stereo(pluck(note, S16 * (1 if fast else 2) * 0.9, bright), 0.45 if i % 2 else -0.45), t, arp_lvl)
        # chords / pads on bar starts (2 bars per chord); top voice up an octave on variation
        if step == 0 and bar % 2 == 0:
            voicing = tones if not var else [tones[0], tones[1], tones[2] + 12]
            if lead == 'stabs' and not pre_drop:
                for k, st in enumerate((0, 0.75, 2, 3.5, 4, 4.75, 6, 7.5)):
                    if t + st * BEAT < signature_at:
                        put(music, chord_stab(voicing, BEAT * 0.6, 0.65), t + st * BEAT, 0.7)
            if lead in ('pad',) or pre_drop or sec == 'steam':
                put(music, pad(voicing, 2 * BAR), t, 1.0)

    # chapter transitions: reverse cymbal + riser into an impact on the cut
    put(fx, impact(1.15), 0.0)
    if drop_at:
        put(fx, riser(min(BAR, drop_at)), drop_at - min(BAR, drop_at), 0.5)
        put(fx, impact(0.8), drop_at)
    for name in ('identity', 'movement', 'squad', 'reentry', 'economy', 'weapons', 'steam', 'outro'):
        if name not in secs:
            continue
        t = secs[name][0]
        put(fx, riser(BAR), t - BAR, 0.55)
        put(fx, reverse_cymbal(1.0), t - 1.0, 0.8)
        put(fx, impact(0.65 if name == 'steam' else 0.9), t)
    for t in accents:  # optional sync points from the edit (e.g. shop prices, chain steps)
        put(fx, stereo(tick(), 0.25), t, 0.55)
    put(fx, riser(BAR), signature_at - BAR, 0.7)
    put(fx, impact(1.25), signature_at)
    put(music, chord_stab(PROG_MAIN[0][1], 1.2, 0.9), signature_at, 1.2)

    # sidechain pumping from the kick (bass, music): energy without loudness
    duck = np.ones(N)
    for i in range(n16):
        t = i * S16
        sec = section_of(t)
        pat = STYLE[sec][0]
        if pat and PATTERNS[pat]['kick'][i % 16] >= 0.9 and t < signature_at:
            s = int(t * SR)
            m = min(N - s, int(0.2 * SR))
            if m > 0:
                duck[s:s + m] = np.minimum(duck[s:s + m], 1 - 0.55 * np.exp(-np.arange(m) / (0.055 * SR)))
    bass *= duck[:, None]
    music = delay(music, BEAT * 0.75, 0.3, 0.2) * duck[:, None]
    music = reverb(music, IR_HALL, 0.16)
    drums = reverb(drums, IR_ROOM, 0.1)

    # chapter intensity (dB)
    gain_db = {'hook': 0, 'identity': (-4, -0.5), 'movement': 0.5, 'squad': -1.5, 'reentry': -2,
               'economy': -1.5, 'weapons': 0, 'steam': 0, 'outro': 0.5}
    g = np.zeros(N)
    for name, (a, b) in secs.items():
        v = gain_db.get(name, 0)
        lo, hi = (v, v) if np.isscalar(v) else v
        ia, ib = int(a * SR), min(N, int(b * SR))
        g[ia:ib] = np.linspace(lo, hi, max(ib - ia, 1))
    k = int(0.25 * SR)
    g = np.convolve(g, np.ones(k) / k, mode='same')
    lin = (10 ** (g / 20))[:, None]
    end = int((signature_at + 1.4) * SR)
    out = {'drums': drums * lin, 'bass': lp(bass, 4000) * lin * 0.85, 'music': music * lin, 'fx': fx}
    for x in out.values():
        x[end:] = 0
        kk = int(0.25 * SR)
        x[end - kk:end] *= np.linspace(1, 0, kk)[:, None]
    return out


def main():
    import soundfile as sf
    edl = json.load(open(sys.argv[1]))
    outp = sys.argv[2]
    fps = edl['fps']
    sig = edl['signature']['from'] / fps
    hook2 = next((l['from'] / fps for l in edl['lines'] if l['id'] == 'hook2'), None)
    stems = build(edl['frames'] / fps, edl['sections'], sig, fps, drop_at=hook2 and hook2 - 0.05)
    mix = sum(stems.values())
    mix = np.tanh(mix * 1.1) / 1.1
    peak = np.abs(mix).max()
    for k, v in stems.items():
        sf.write(outp.replace('.wav', f'_stem_{k}.wav'), (v / peak * 0.89).astype(np.float32), SR)
    sf.write(outp, (mix / peak * 0.89).astype(np.float32), SR)
    print('wrote', outp, f'{len(mix) / SR:.1f}s')


if __name__ == '__main__':
    main()

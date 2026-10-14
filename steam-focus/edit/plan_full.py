"""Edit decision list for the full STEAM FOCUS report on ECC: REDLINE.

The narration drives the cut. Voice lines are laid out first (fixed pauses),
then each section's shots fill the span between section starts. Shots that
illustrate a specific word in the hook cut exactly on that word.

Sources:  G = official "Gameplay Footage" trailer (Steam, 1080p30)
          S3 = Blender shot (blender/redline_steam_page.py), 292 frames

usage: python3 plan_full.py public/vo_timing.json public/full_edl.json
"""
import json
import re
import sys
import unicodedata

FPS = 30
timing = json.load(open(sys.argv[1]))
OUT = sys.argv[2]

GAP_LINE, GAP_SECTION, START = 0.27, 0.75, 0.9  # v3: tighter pace (v2: 0.32, 1.0)
LEAD = 0.35            # picture changes slightly before the voice of a new section
S3_FRAMES = 292
S3_BRIDGE = 165        # Blender frames used: scope blast -> pull-back -> plate lands
SIGNATURE = 1.6        # STEAM FOCUS sign-off after the last line

# --- voice layout -----------------------------------------------------------
lines, cur, prev = [], START, None
for t in timing:
    if prev:
        # v4: lines cut from one chapter paragraph carry their own natural pause
        # ("gap_before": 0), so the chapter plays back exactly as it was spoken
        cur += GAP_SECTION if t["section"] != prev else t.get("gap_before", GAP_LINE)
    lines.append({**t, "start": round(cur, 3), "end": round(cur + t["dur"], 3)})
    cur += t["dur"]
    prev = t["section"]
L = {l["id"]: l for l in lines}


def word_time(line_id, word):
    """Start time of the first ASR word that begins with `word`."""
    line = L[line_id]
    for s, _, w in line["words"]:
        if norm(w).startswith(norm(word)):
            return line["start"] + s
    raise KeyError((line_id, word))


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if not unicodedata.combining(c)))


def first(section):
    return min(l["start"] for l in lines if l["section"] == section)


def last(section):
    return max(l["end"] for l in lines if l["section"] == section)


# The Blender shot starts so its release callout lands on the first Steam line;
# its first seconds (scope blast, pull-back) close the weapons section.
# The Blender bridge (the approved hero shot) runs until the plate lands in the
# store page; real page details take over 0.3 s before the first Steam line.
s3_start = L["st1"]["start"] - 0.3 - S3_BRIDGE / FPS
outro_start = first("outro") - LEAD
total = last("outro") + 0.25 + SIGNATURE

sections = [
    ("hook", 0.0),
    ("identity", first("identity") - 0.8),
    ("movement", first("movement") - LEAD),
    ("squad", first("squad") - LEAD),
    ("reentry", first("reentry") - LEAD),
    ("economy", first("economy") - LEAD),
    ("weapons", first("weapons") - LEAD),
    ("steam", s3_start),
    ("outro", outro_start),
]
bounds = {name: (a, sections[i + 1][1] if i + 1 < len(sections) else total) for i, (name, a) in enumerate(sections)}

# --- shots ------------------------------------------------------------------
# src, source in (s), crop centre keys [[t_rel_s, source_x]], nominal duration
# (None = takes the rest of the section), optional cut-on-word.
SHOTS = {
    "hook": [
        # same reframe as the approved demo; zoom + raised centre hide the
        # trailer's burned-in caption. The title lands on it within 0.5 s.
        dict(id="h_heli", src="G", sin=62.86, until=("hook2", "squadre"), allow_cuts=[65.73], zoom=[1.08, 1.13], cy=505,
             cx=[[0, 1150], [0.39, 1150], [0.69, 1090], [0.86, 1480], [0.96, 1400], [1.06, 1160], [1.19, 470], [1.32, 340], [1.46, 420], [1.59, 880], [1.72, 960], [2.12, 1010], [2.86, 990], [2.89, 960], [3.82, 965]]),  # v4: starts 0.39 s earlier (keys shifted) so the longer hook ends before the 66.73 cut
        dict(id="h_squad", src="G", sin=60.12, cx=[[0, 960]], until=("hook2", "scivolate")),
        dict(id="h_slide", src="G", sin=264.1, cx=[[0, 1000]], until=("hook2", "rampino")),
        dict(id="h_grapple", src="G", sin=329.25, cx=[[0, 960]], until=("hook2", "crediti")),
        dict(id="h_credits", src="G", sin=152.99, cx=[[0, 900]], dur=None, freeze_after=2.36),  # v3: hold the last frame before the 155.40 cut
    ],
    "identity": [
        dict(id="i_arena", src="G", sin=217.24, cx=[[0, 900], [2, 960]], dur=2.05),
        dict(id="i_hall", src="G", sin=219.42, cx=[[0, 960]], dur=2.0),
        dict(id="i_descent", src="G", sin=66.8, cx=[[0, 900], [3, 1000]], until=("id3", "si")),
        dict(id="i_map", src="G", sin=72.5, cx=[[0, 1010], [6, 980]], dur=None),
    ],
    "movement": [
        dict(id="m_slide", src="G", sin=253.3, cx=[[0, 1000]], dur=3.2),
        dict(id="m_aim", src="G", sin=257.5, cx=[[0, 900], [2, 960]], dur=3.0),
        dict(id="m_grapple_tp", src="G", sin=111.15, cx=[[0, 700], [1.4, 640], [2.7, 900]], dur=2.75),
        dict(id="m_wall", src="G", sin=114.0, cx=[[0, 1000]], dur=1.55),
        dict(id="m_grapple_fp", src="G", sin=336.5, cx=[[0, 900], [3, 1000]], dur=3.0, allow_cuts=[337.4]),
        # analysis line: shooting while airborne / on the move
        dict(id="m_air", src="G", sin=117.3, cx=[[0, 960]], dur=1.8),
        dict(id="m_air2", src="G", sin=261.05, cx=[[0, 960]], dur=None),
    ],
    "squad": [
        dict(id="s_hud", src="G", sin=349.567, cx=[[0, 900], [1.8, 990]], dur=1.8, allow_cuts=[350.43]),
        dict(id="s_push", src="G", sin=344.06, cx=[[0, 960]], dur=2.74),
        dict(id="s_fight", src="G", sin=346.87, cx=[[0, 960]], dur=2.66),
        dict(id="s_cover", src="G", sin=163.93, cx=[[0, 900], [5, 1000]], dur=None),
    ],
    "reentry": [
        dict(id="r_down", src="G", sin=170.3, cx=[[0, 900]], dur=2.7),
        dict(id="r_revive", src="G", sin=325.55, cx=[[0, 700], [1.2, 760], [2.6, 960]], dur=2.75),
        dict(id="r_roam", src="G", sin=306.45, cx=[[0, 960]], dur=2.5),
        dict(id="r_roof", src="G", sin=309.1, cx=[[0, 960]], dur=None),
    ],
    "economy": [
        dict(id="e_kill", src="G", sin=167.32, cx=[[0, 1000]], dur=1.45),
        dict(id="e_hud", src="G", sin=146.99, cx=[[0, 960], [5.9, 1000]], until=("ec2", "nel")),
        # Shop UI is static: play the opening, then hold an annotated freeze.
        dict(id="e_shop", src="G", sin=96.6, cx=[[0, 580]], zoom=[1.06, 1.12], cy=600, freeze_after=1.1, until=("ec3", "piu")),
        dict(id="e_funds", src="G", sin=98.45, cx=[[0, 420]], zoom=[1.38, 1.44], cy=720, dur=3.22),
        dict(id="e_after", src="G", sin=101.88, cx=[[0, 960]], dur=None),
    ],
    "weapons": [
        dict(id="w_range", src="G", sin=28.7, cx=[[0, 960]], dur=2.2),
        dict(id="w_scope", src="G", sin=32.7, cx=[[0, 900]], dur=3.3),
        # the trailer dips to black around 6.7 s: two pieces around the fade
        dict(id="w_inspect", src="G", sin=5.3, cx=[[0, 900], [2.4, 960]], dur=2.4),
        dict(id="w_inspect2", src="G", sin=17.25, cx=[[0, 960], [3, 1000]], dur=None),
    ],
    "steam": [dict(id="s3", src="S3", sin=0, cx=None, dur=None)],  # bridge + store-page details
    # zoom past the trailer's letterbox bars
    "outro": [dict(id="o_ecc", src="G", sin=379.78, cx=[[0, 960]], zoom=[1.24, 1.3], dur=None)],
}

edl = []
for name, (a, b) in bounds.items():
    t = a
    shots = SHOTS[name]
    for i, s in enumerate(shots):
        if "until" in s:
            end = word_time(*s["until"]) - 0.05
        elif s.get("dur"):
            end = t + s["dur"]
        else:
            end = b
        if i == len(shots) - 1:
            end = b
        f0, f1 = round(t * FPS), round(end * FPS)
        edl.append({
            "id": s["id"], "section": name, "src": s["src"], "sin": s["sin"],
            "from": f0, "frames": f1 - f0, "cx": s["cx"], "zoom": s.get("zoom"), "cy": s.get("cy"), "freezeAfter": s.get("freeze_after"),
            "allow_cuts": s.get("allow_cuts", []),
        })
        t = end

# --- validation: no shot crosses a cut of the source trailer, no reuse ----------
cuts = {"G": [float(x) for x in open(sys.argv[3]).read().split()]} if len(sys.argv) > 3 else {}
used, problems = [], []
for e in edl:
    if e["src"] != "G":
        continue
    a = e["sin"]
    b = a + (e["freezeAfter"] if e["freezeAfter"] else e["frames"] / FPS)
    for c in cuts.get("G", []):
        if a + 0.02 < c < b - 0.02 and not any(abs(c - x) < 0.05 for x in e["allow_cuts"]):
            problems.append(f"{e['id']}: crosses source cut at {c:.2f}s ({a:.2f}-{b:.2f})")
    for uid, ua, ub in used:
        if a < ub - 0.02 and ua < b - 0.02:
            problems.append(f"{e['id']}: reuses source {max(a, ua):.2f}-{min(b, ub):.2f}s already used by {uid}")
    used.append((e["id"], a, b))
for p_ in problems:
    print("WARN", p_)

subs = []
for l in lines:
    subs.append({"id": l["id"], "text": l["text"], "from": round(l["start"] * FPS), "to": round(l["end"] * FPS),
                 "words": l["words"]})

# --- subtitles: <= 2 lines x ~26 chars, timed on the spoken words -----------
MAXC = 44


def chunks_of(text):
    """Split a sentence into balanced cues of at most MAXC characters,
    breaking after punctuation when possible and never inside a name."""
    words = text.replace("ECC: REDLINE", "ECC:\u00a0REDLINE").split()
    n = -(-len(text) // MAXC)
    best = None
    # brute-force all split points for n cues (sentences are short)
    import itertools
    for cut in itertools.combinations(range(1, len(words)), n - 1):
        parts = [words[i:j] for i, j in zip((0,) + cut, cut + (len(words),))]
        lens = [len(" ".join(p_)) for p_ in parts]
        if max(lens) > MAXC + 4:
            continue
        cost = max(lens) - min(lens)
        cost -= sum(8 for p_ in parts[:-1] if p_[-1][-1] in ",.:;?")
        if best is None or cost < best[0]:
            best = (cost, parts)
    parts = best[1] if best else [words]
    return [[w.replace("\u00a0", " ") for w in p_] for p_ in parts]


def word_starts(line, words):
    """Start time (s, line-relative) of each text word, aligned on characters
    to the ASR tokens, so apostrophes, numbers and acronyms still line up."""
    asr = line["words"]
    if len(asr) == len(words):
        return [w[0] for w in asr]
    tn = [norm(w) for w in words]
    an = [norm(w[2]) for w in asr]
    t_total, a_total = sum(map(len, tn)) or 1, sum(map(len, an)) or 1
    a_cum, c = [], 0
    for x in an:
        a_cum.append(c)
        c += len(x)
    out_, c = [], 0
    for x in tn:
        target = c * a_total / t_total
        k = max(i for i, v in enumerate(a_cum) if v <= target + 1e-6)
        # interpolate inside the ASR token
        seg = max(1, len(an[k]))
        frac = min(1.0, (target - a_cum[k]) / seg)
        st, en = asr[k][0], asr[k][1]
        out_.append(st + (en - st) * frac)
        c += len(x)
    return out_


cues = []
for l in lines:
    groups = chunks_of(l["text"])
    tw = [w for g in groups for w in g]
    starts = word_starts(l, tw)
    idx = 0
    for gi, g in enumerate(groups):
        st = l["start"] + starts[idx]
        idx += len(g)
        en = l["start"] + starts[idx] if gi + 1 < len(groups) else l["end"] + 0.15
        cues.append({"from": round(max(st - 0.05, l["start"]) * FPS), "to": round(en * FPS), "text": " ".join(g)})
for a_, b_ in zip(cues, cues[1:]):
    a_["to"] = min(a_["to"], b_["from"])


def srt_time(f):
    ms = round(f / FPS * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


with open(OUT.replace("full_edl.json", "steam_focus_ecc_redline.srt"), "w") as fh:
    for i, c in enumerate(cues, 1):
        fh.write(f"{i}\n{srt_time(c['from'])} --> {srt_time(c['to'])}\n{c['text']}\n\n")

out = {
    "cues": cues,
    "fps": FPS,
    "frames": round(total * FPS),
    "voice": [{"id": l["id"], "from": round(l["start"] * FPS), "dur": l["dur"], "section": l["section"]} for l in lines],
    "sections": {k: [round(v[0] * FPS), round(v[1] * FPS)] for k, v in bounds.items()},
    "s3": {"from": round(s3_start * FPS), "bridge": S3_BRIDGE},
    "signature": {"from": round((last("outro") + 0.25) * FPS), "frames": round(SIGNATURE * FPS)},
    "shots": edl,
    "lines": subs,
}
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
for e in edl:
    print(f"{e['id']:14s} {e['section']:9s} {e['from'] / FPS:7.2f}s  {e['frames'] / FPS:5.2f}s  {e['src']} {e['sin']}")
print("total", round(total, 2), "s", out["frames"], "frames")

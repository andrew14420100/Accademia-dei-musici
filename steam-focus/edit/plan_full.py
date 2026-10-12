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

GAP_LINE, GAP_SECTION, START = 0.28, 0.85, 0.9
LEAD = 0.35            # picture changes slightly before the voice of a new section
S3_FRAMES = 292
S3_RELEASE = 168       # S3 frame where the "release date" callout appears
LOGO_CARD = 1.4        # standalone Steam logo before the outro
OUTRO_TAIL = 2.6

# --- voice layout -----------------------------------------------------------
lines, cur, prev = [], START, None
for t in timing:
    if prev:
        cur += GAP_SECTION if t["section"] != prev else GAP_LINE
    if t["id"] == "end1":
        cur += LOGO_CARD
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
s3_start = L["st1"]["start"] + 0.15 - S3_RELEASE / FPS
s3_hold_end = L["st2"]["end"] + 0.45
logo_end = s3_hold_end + LOGO_CARD - 0.45
total = last("outro") + OUTRO_TAIL

sections = [
    ("hook", 0.0),
    ("identity", first("identity") - LEAD),
    ("movement", first("movement") - LEAD),
    ("squad", first("squad") - LEAD),
    ("reentry", first("reentry") - LEAD),
    ("economy", first("economy") - LEAD),
    ("weapons", first("weapons") - LEAD),
    ("steam", s3_start),
    ("outro", logo_end),
]
bounds = {name: (a, sections[i + 1][1] if i + 1 < len(sections) else total) for i, (name, a) in enumerate(sections)}

# --- shots ------------------------------------------------------------------
# src, source in (s), crop centre keys [[t_rel_s, source_x]], nominal duration
# (None = takes the rest of the section), optional cut-on-word.
SHOTS = {
    "hook": [
        dict(id="h_squad", src="G", sin=60.12, cx=[[0, 960]], until=("hook1", "scivolate")),
        dict(id="h_slide", src="G", sin=264.1, cx=[[0, 1000]], until=("hook1", "rampino")),
        dict(id="h_grapple", src="G", sin=329.25, cx=[[0, 960]], until=("hook1", "crediti")),
        dict(id="h_credits", src="G", sin=153.05, cx=[[0, 900]], until=("hook2", "il")),
        # same reframe as the approved demo; zoom + raised centre hide the
        # trailer's burned-in caption
        dict(id="h_heli", src="G", sin=63.25, dur=None, allow_cuts=[65.73], zoom=[1.08, 1.13], cy=505,
             cx=[[0, 1150], [0.3, 1090], [0.47, 1480], [0.57, 1400], [0.67, 1160], [0.8, 470], [0.93, 340],
                 [1.07, 420], [1.2, 880], [1.33, 960], [1.73, 1010], [2.47, 990], [2.5, 960], [3.43, 965]]),
    ],
    "identity": [
        dict(id="i_arena", src="G", sin=217.24, cx=[[0, 900], [2, 960]], dur=2.05),
        dict(id="i_hall", src="G", sin=219.42, cx=[[0, 960]], until=("id2", "sara")),
        dict(id="i_descent", src="G", sin=66.8, cx=[[0, 900], [3, 1000]], until=("id3", "si")),
        dict(id="i_map", src="G", sin=70.7, cx=[[0, 1010], [6, 980]], dur=None),
    ],
    "movement": [
        dict(id="m_slide", src="G", sin=253.3, cx=[[0, 1000]], dur=3.9),
        dict(id="m_aim", src="G", sin=257.5, cx=[[0, 900], [2, 960]], dur=3.5),
        dict(id="m_grapple_tp", src="G", sin=111.15, cx=[[0, 700], [1.4, 640], [2.7, 900]], dur=2.75),
        dict(id="m_wall", src="G", sin=114.0, cx=[[0, 1000]], dur=1.55),
        dict(id="m_grapple_fp", src="G", sin=336.5, cx=[[0, 900], [3, 1000]], dur=None, allow_cuts=[337.4]),
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
        dict(id="e_kill", src="G", sin=167.15, cx=[[0, 1000]], dur=1.15),
        dict(id="e_hud", src="G", sin=147.0, cx=[[0, 960], [5.9, 1000]], until=("ec2", "nel")),
        # Shop UI is static: play the opening, then hold an annotated freeze.
        dict(id="e_shop", src="G", sin=96.6, cx=[[0, 580]], zoom=[1.0, 1.06], freeze_after=1.1, until=("ec3", "in")),
        dict(id="e_funds", src="G", sin=98.45, cx=[[0, 520]], zoom=[1.2, 1.25], cy=630, dur=2.1),
        dict(id="e_after", src="G", sin=101.9, cx=[[0, 960]], dur=2.6),
        dict(id="e_after2", src="G", sin=104.6, cx=[[0, 960]], dur=None),
    ],
    "weapons": [
        dict(id="w_range", src="G", sin=28.7, cx=[[0, 960]], dur=2.2),
        dict(id="w_scope", src="G", sin=32.7, cx=[[0, 900]], dur=3.3),
        dict(id="w_inspect", src="G", sin=4.2, cx=[[0, 900], [4, 1000]], dur=None),
    ],
    "steam": [dict(id="s3", src="S3", sin=0, cx=None, dur=None)],
    "outro": [dict(id="o_ecc", src="G", sin=379.78, cx=[[0, 960]], dur=None)],
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


cues = []
for l in lines:
    tw = [w for g in chunks_of(l["text"]) for w in g]
    tw = " ".join(tw).split()
    asr = l["words"]
    same = len(asr) == len(tw)
    total_c = sum(len(w) + 1 for w in tw)
    idx = 0
    groups = chunks_of(l["text"])
    for gi, g in enumerate(groups):
        if same:
            st = l["start"] + asr[idx][0]
        else:
            st = l["start"] + l["dur"] * sum(len(w) + 1 for w in tw[:idx]) / total_c
        idx += len(g)
        if gi + 1 < len(groups):
            en = (l["start"] + asr[idx][0]) if same else l["start"] + l["dur"] * sum(len(w) + 1 for w in tw[:idx]) / total_c
        else:
            en = l["end"] + 0.15
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
    "s3": {"from": round(s3_start * FPS), "holdUntil": round(s3_hold_end * FPS),
           "italianAt": round((word_time("st2", "italiano") - s3_start) * FPS),
           "logoAt": round((s3_hold_end - s3_start) * FPS)},
    "shots": edl,
    "lines": subs,
}
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
for e in edl:
    print(f"{e['id']:14s} {e['section']:9s} {e['from'] / FPS:7.2f}s  {e['frames'] / FPS:5.2f}s  {e['src']} {e['sin']}")
print("total", round(total, 2), "s", out["frames"], "frames")

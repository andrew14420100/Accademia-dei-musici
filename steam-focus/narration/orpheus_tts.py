"""Italian narration with Orpheus 3B (Canopy Labs, Italian/Spanish fine-tune, Apache-2.0)
on CPU through llama.cpp, decoded with SNAC 24 kHz (MIT).

    python narration/orpheus_tts.py MODEL.gguf JOBS.json

JOBS.json: [{"text": ..., "voice": "pietro"|"carlo", "out": "x.wav", "seed": 1,
             "temperature": 0.6, "top_p": 0.9}, ...]

Voices are the model's own built-in Italian voices (no voice cloning). Prompt format and
token -> SNAC code mapping follow Orpheus-FastAPI (github.com/Lex-au/Orpheus-FastAPI).
"""
import json
import re
import sys
import time

import numpy as np
import soundfile as sf
import torch
from llama_cpp import Llama
from snac import SNAC

SR = 24000
TOKEN_RE = re.compile(r'<custom_token_(\d+)>')


def codes_from_text(text):
    ids = []
    for n in TOKEN_RE.findall(text):
        idx = len(ids)
        code = int(n) - 10 - ((idx % 7) * 4096)
        if 0 <= code < 4096:
            ids.append(code)
        # tokens outside the expected range (e.g. the start-of-audio marker) are skipped
    return ids


def decode(snac, ids):
    n = len(ids) // 7
    ids = ids[: n * 7]
    c0, c1, c2 = [], [], []
    for j in range(n):
        f = ids[7 * j: 7 * j + 7]
        c0.append(f[0])
        c1 += [f[1], f[4]]
        c2 += [f[2], f[3], f[5], f[6]]
    codes = [torch.tensor(c, dtype=torch.int32)[None] for c in (c0, c1, c2)]
    with torch.inference_mode():
        audio = snac.decode(codes)
    return audio.squeeze().cpu().numpy()


def main():
    model_path, jobs_path = sys.argv[1:3]
    jobs = json.load(open(jobs_path))
    llm = Llama(model_path=model_path, n_ctx=8192, n_threads=4, verbose=False, seed=1)
    snac = SNAC.from_pretrained('hubertsiuzdak/snac_24khz').eval()
    for j in jobs:
        prompt = f"<|audio|>{j['voice']}: {j['text']}<|eot_id|>"
        t = time.time()
        llm.set_seed(j.get('seed', 1))
        out = llm.create_completion(prompt, max_tokens=j.get('max_tokens', 6000), temperature=j.get('temperature', 0.6),
                                    top_p=j.get('top_p', 0.9), repeat_penalty=j.get('repeat_penalty', 1.1))
        text = out['choices'][0]['text']
        ids = codes_from_text(text)
        audio = decode(snac, ids)
        peak = np.abs(audio).max() or 1
        sf.write(j['out'], (audio / peak * 0.9).astype(np.float32), SR)
        print(f"{j['out']} tokens {len(ids)} dur {len(audio) / SR:.1f}s gen {time.time() - t:.0f}s", flush=True)


if __name__ == '__main__':
    main()

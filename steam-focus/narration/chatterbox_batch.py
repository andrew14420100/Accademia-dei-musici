import sys, json, time, torch, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
torch.set_num_threads(4)
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
jobs = json.load(open(sys.argv[1]))
for j in jobs:
    torch.manual_seed(j.get('seed', 0))
    t = time.time()
    wav = m.generate(j['text'], language_id="it", audio_prompt_path=j.get('prompt'),
                     exaggeration=j.get('ex', 0.5), cfg_weight=j.get('cfg', 0.5), temperature=j.get('temp', 0.8))
    torchaudio.save(j['out'], wav, m.sr)
    print(j['out'], "sec %.0f dur %.1f" % (time.time() - t, wav.shape[-1] / m.sr), flush=True)

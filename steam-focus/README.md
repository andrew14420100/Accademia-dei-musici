# STEAM FOCUS — nuova pipeline audiovisiva (demo ECC: REDLINE, 9:16)

Sequenza dimostrativa verticale (1080×1920, 30 fps, 15 s) prodotta solo con strumenti
gratuiti: **Blender 4.2 LTS** (Cycles), **Remotion 4** (licenza gratuita), **FFmpeg**,
Python (NumPy/SciPy/OpenCV). Tutto il materiale di gioco è ufficiale: trailer
"Gameplay Footage" e pagina Steam di ECC: REDLINE (app 5268340, NetEase Games).

## Direzione artistica

**Principio:** il gameplay è il protagonista. È sempre a tutto schermo e le informazioni
vivono *dentro* l'immagine, non sopra pannelli neri.

| Elemento | Scelta |
|---|---|
| Formato | 9:16. Il 16:9 ufficiale viene ritagliato in verticale con un reframe animato che segue il soggetto (elicottero, giocatore, mirino). |
| Tipografia | **Barlow Condensed** (titoli, maiuscolo, compatto), **Inter Tight** (testo), **JetBrains Mono** (dati tecnici, kicker). Tutte OFL. |
| Colore | Inchiostro `#0A0D12` e carta `#F3F5F7`. Due soli accenti con significato: **rosso REDLINE** `#E3262E` per i dati sul gioco, **blu Steam** `#66C0F4` per i dati della pagina Steam. |
| Tipo sul gameplay | Nessun box. Sui cieli chiari il titolo è in inchiostro scuro; sulle scene scure il testo è bianco con un'ombra morbida locale. |
| Didascalie | Agganciate al mondo: in S2 seguono il giocatore (tracking OpenCV); in S3 seguono gli elementi della pagina proiettati dalla camera di Blender. |
| Movimento | Un solo linguaggio: attacco rapido e assestamento lungo (`bezier(0.16,1,0.3,1)`), testo che emerge dalla propria linea di base. Niente transizioni da template: i tagli sono netti, a ritmo, o motivati nello spazio 3D. |
| 3D | Usato dove migliora davvero: la lastra di gameplay con spessore e ombra reale sopra la pagina Steam, la profondità di campo, il motion blur, la luce emissiva. Eliminata la polvere in bokeh: in prova creava macchie e non aggiungeva nulla. |
| Aree sicure | Testo entro x 72–1008 e y 120–1540, per non finire sotto l'interfaccia di Shorts/Reels/TikTok. |

### Logo Steam (linee guida Valve)

Il logo Steam si usa solo nella versione *inverse* ufficiale, presa dal PDF di Valve:
bianco puro, con ®, almeno 50 px di altezza. È **isolato**: nessun lockup con
"STEAM FOCUS", nessun oggetto nello spazio di rispetto, nessuna estrusione 3D o effetto.
La nota legale ufficiale in italiano sta fuori dallo spazio di rispetto. Il bug
"STEAM FOCUS" scompare prima che il logo entri.

## Struttura della demo

| Frame | Shot | Contenuto |
|---|---|---|
| 0–103 | S1 · inserimento in elicottero (trailer 63.25 s) | Titolo "ECC: REDLINE" in inchiostro sulle nuvole, NetEase · Galaxy Studio, free-to-play su PC |
| 104–157 | S2 · scontro ed esplosione (349.57 s) | Didascalia tracciata sul giocatore: "Movimento a catena — sprint · scivolata · rampino" |
| 158–449 | S3 · Blender | Il mirino esplode a tutto schermo; la camera arretra e rivela la lastra di gameplay sopra la vera pagina Steam; la lastra si posa nel player della pagina; la camera scende lungo la colonna informazioni: "Uscita da annunciare / wishlist dal 9 ottobre", "Italiano non supportato" (riga evidenziata sulla tabella lingue reale); chiusura con il logo Steam isolato. |

## Sound design

`audio/build_audio.py` usa l'audio originale di ogni shot e aggiunge elementi
sintetizzati posizionati sui frame:
- sub-drop sul titolo, punch sul taglio, rinforzo sull'esplosione;
- whoosh stereo sull'arretramento della camera;
- quando il gameplay "entra" nella pagina, il suo audio passa in passa-basso e scende di livello;
- impatto all'aggancio della lastra, tick sulle didascalie, coda sul logo.

Master a −14 LUFS, −1 dBTP.

## Pipeline

```bash
npm install
WORK=/percorso/lavoro ./scripts/fetch_assets.sh     # trailer, pagina Steam, logo, Blender
python3 scripts/track_point.py public/s2_combat.mp4 868 590 90 180 54 public/track_runner.json
$WORK/blender-4.2.23-linux-x64/blender -b --factory-startup \
  --python blender/redline_steam_page.py -- --assets $WORK/assets --plate $WORK/plate \
  --out $WORK/render_s3 --anchors public/s3_anchors.json --samples 16
WORK=/percorso/lavoro ./scripts/build_demo.sh       # -> out/redline_demo_9x16.mp4
```

- Blender gira su CPU con Cycles: senza GPU, EEVEE non parte. Ogni frame richiede
  circa 30 s su 4 core. Il render si può riprendere: i frame già su disco vengono saltati.
- `public/s3_anchors.json` contiene, frame per frame, le coordinate 2D dei punti della
  pagina proiettati dalla camera di Blender. Remotion lo usa per agganciare le didascalie.
- `npm run studio` apre l'anteprima interattiva di Remotion.

## Reportage completo (issue #2) — 9:16, ~118 s

| File | Ruolo |
|---|---|
| `narration/ecc_redline_it.json` | Testo della narrazione: `text` per i sottotitoli, `say` con la fonetica dei nomi inglesi |
| `narration/synth_voice.py` | Voce con Kokoro-82M (Apache-2.0, voce di serie `im_nicola`, nessuna clonazione) e verifica automatica: ogni frase viene ritrascritta con faster-whisper (WER per riga) e i tempi delle parole servono per i sottotitoli |
| `edit/plan_full.py` | Montaggio guidato dalla voce. Calcola posizione delle frasi, sezioni, inquadrature (tagli sulle parole del gancio iniziale), sottotitoli bilanciati e SRT. Controlla che nessuna inquadratura attraversi un taglio del trailer o riusi immagini già mostrate |
| `edit/extract_clips.py` | Clip frame-accurate di ogni inquadratura (video per Remotion, audio per il mix) |
| `scripts/track_point.py` | Tracking OpenCV, usato solo dove è affidabile (rianimazione, giocatore in corsa) |
| `src/full/` | Composizione `RedlineFull`: reframe 9:16, frusta tra i capitoli, titoli di capitolo, grafiche legate alle parole (catena di movimento, ruoli, dati, zona sicura *illustrativa*), lente sull'HUD (crediti e squadra stanno nella fascia bassa coperta dalle app), traduzioni ancorate al negozio, scena Blender della pagina Steam con "hold" 2D, firma STEAM FOCUS |
| `audio/build_full_audio.py` | Voce (passa-alto, presenza, compressione 2:1, livello uniforme) + audio dei trailer con ducking −18 dB sotto la voce + design sincronizzato |
| `scripts/build_full.sh` | Pipeline completa → `out/steam_focus_ecc_redline_full.mp4`, `_cover.png`, `.srt`, `_sources.txt`, `_narrazione.txt`, `_mix.wav` |

Capitoli: gancio · 01 Identità · 02 Movimento · 03 Squadre · 04 Rientro ·
05 Economia · 06 Armi e tattica · 07 Su Steam · firma.

Note di metodo:
- **Mostrato o descritto.** Le meccaniche visibili nel filmato (rianimazione, rampino, negozio, HUD) sono annotate sull'immagine. Quelle solo descritte dalla pagina Steam (stato di roaming) sono dichiarate come tali a schermo. La zona sicura è etichettata "schema illustrativo".
- **Blender.** Un solo hero shot, riusato come ponte editoriale verso la pagina Steam (~15 s su ~118). Il container non ha GPU e Cycles su CPU impiega ~30 s/frame, quindi niente nuovi render pesanti: il tratto finale, con la pagina frontale, prosegue con un push 2D sull'ultimo frame, visivamente equivalente.
- **Voce.** Non posso ascoltarla. È verificata con la trascrizione automatica del mix finale (WER sull'intero testo) e va comunque ascoltata da una persona prima della pubblicazione.
- **Diritti.** Vedi `narration/steam_focus_ecc_redline_sources.txt`. Il video resta un'**anteprima privata** finché l'uso delle clip e dell'audio NetEase non è verificato.

## Revisione v2 — master 2160×3840, 60 FPS (issue #2, aggiornata)

La v1 (1080p/30) resta in `out/v1_1080p30_*`, nei file `*_v1.json`/`.srt` e nel commit `dea4b07`.

**Render 4K/60 reale**
- La composizione `RedlineFull4K` è 2160×3840 a 60 fps. Il layout è scritto in unità 1080×1920 e impaginato con `zoom: 2` CSS: testi, tracciati SVG e ritagli della pagina Steam vengono rasterizzati a 4K, non ingranditi.
- Tutte le animazioni usano `useBaseFrame()`, cioè il frame frazionario a 30 fps. A 60 fps sono quindi calcolate davvero a 60 fps; `Sequence`, `Freeze` e tracking vengono convertiti o interpolati.
- **Footage:** la sorgente ufficiale è 1080p/30, quindi l'output è 4K ma il gameplay non è 4K nativo. L'interpolazione 30→60 (FFmpeg `minterpolate` a compensazione di moto) è applicata solo alle inquadrature con movimento di camera regolare (`public/full60/list.json`). Le inquadrature con armi in primo piano, esplosioni o panoramiche rapide restano a cadenza 30, perché l'interpolazione vi produce "fantasmi" (verificato su fotogrammi campione).
- **Scena Blender:** a 4K su CPU servono ~98 s/frame (~16 h per la versione a 60 fps), quindi si usa il render 1080p con il movimento di camera interpolato. I primi 42 frame (esplosione nel mirino) restano a 30. Per il 4K nativo su GPU: `scripts/blender_gpu_4k.sh`.
- **Render a segmenti riprendibile:** `scripts/render_4k60.sh` (`SMOKE=1` per il test di 8 s). Ogni segmento è verificato con ffprobe; le giunzioni sono senza ricodifica.

**Montaggio, grafica e testo**
- **Gancio:** "Questo è il nuovo ECC: REDLINE" e titolo a schermo entro 0,3 s.
- **Analisi editoriali:** movimento/copertura e il rapporto 4.500 ÷ 400 ≈ 11 mine. Compaiono in schede tratteggiate "Analisi STEAM FOCUS · non verificata in partita", distinte dai dati ufficiali.
- **Capitolo 07:** ponte Blender, poi ritagli autentici a densità 3× della pagina Steam del 12/10/2026 (titolo, data, sviluppatore/editore, wishlist, tabella lingue), mostrati in schede 3D con le parti rilevanti evidenziate. La pagina non resta più ferma per 15 s.
- **Grafica:**
  - rotazioni 3D di camera tra i capitoli al posto della "frusta";
  - targhe di capitolo compatte;
  - firma STEAM FOCUS di 1,6 s, senza loghi di terzi;
  - il logo Steam compare solo nella vera intestazione della pagina.
- **Safe area TikTok:** testi entro x 64–940 e y 170–1440. Sottotitoli 48 px sopra la fascia della didascalia; la scheda di analisi sul negozio è spostata dopo la chiusura del negozio, così non copre i prezzi.

**Voce e audio**
- **Pronuncia:** varianti fonetiche scelte per confidenza della trascrizione: "Stìiim" 0,98 contro 0,63, "Nèt Iis" trascritto esattamente come NetEase, "Questo è il nuovo E C C Rèdlain". Analisi acustica di intonazione e ritmo (librosa). La voce resta **da ascoltare da una persona**.
- **Nessun audio dei trailer:** colonna sonora originale procedurale (`audio/score.py`, 100 BPM, La minore) più design sintetizzato, con la musica a −12 dB sotto la voce. Sul mix completo la trascrizione automatica coincide con il testo. Lo script v1 è conservato in `audio/build_full_audio_v1.py`.

## Licenze e scelte di strumenti

- **Remotion:** gratuito per privati, aziende con al massimo 3 dipendenti e non profit,
  anche per uso commerciale (`node_modules/remotion/LICENSE.md`). Sopra queste soglie
  serve la Company License.
- **Blender, FFmpeg, font:** GPL/LGPL/OFL.
- **DaVinci Resolve Fusion:** non usato. La versione gratuita richiede GPU e interfaccia
  grafica e non si automatizza da riga di comando (lo scripting esterno è riservato a
  Studio). Non porterebbe miglioramenti concreti senza montaggio manuale.
- I media (clip del trailer, catture Steam, artwork Valve) non sono nel repository:
  si rigenerano con `fetch_assets.sh`.

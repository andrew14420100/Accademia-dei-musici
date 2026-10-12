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
python3 scripts/track_runner.py public/s2_combat.mp4 public/s2_track.json
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

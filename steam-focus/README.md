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

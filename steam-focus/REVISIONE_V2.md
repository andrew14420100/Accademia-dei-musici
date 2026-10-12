# STEAM FOCUS — ECC: REDLINE · Revisione v2 (master 2160×3840, 60 fps)

Questa relazione accompagna il master v2 e il confronto con la v1 (1080×1920, 30 fps).
La v1 resta conservata (commit `dea4b07`, file `out/v1_1080p30_*`). Il progetto resta in
questo repository; JARVIS non è stato toccato.

## File consegnati (cartella `out/`, non versionata)

| File | Contenuto |
| --- | --- |
| `steam_focus_ecc_redline_full_4K_60fps.mp4` | master H.264 High, 2160×3840, 60 fps CFR, AAC 320k |
| `steam_focus_ecc_redline_review_720p.mp4` | copia leggera di revisione (720×1280, 60 fps) |
| `steam_focus_ecc_redline_cover.png` | copertina 2160×3840 (fotogramma del master, senza sottotitoli) |
| `steam_focus_ecc_redline.srt` | sottotitoli italiani allineati alla voce |
| `steam_focus_ecc_redline_mix.wav` | mix finale normalizzato (−14 LUFS, true peak ≤ −1 dBTP) |
| `steam_focus_ecc_redline_narrazione.txt` | testo della voce, con le righe di analisi marcate |
| `steam_focus_ecc_redline_sources.txt` | fonti, licenze e limiti |
| `qc/` | ffprobe, rilevamento neri/fermi/duplicati, loudness, provini per capitolo, confronti v1/v2 |

## Come è fatto il 4K60

- Remotion renderizza la composizione `RedlineFull4K` a 2160×3840 e 60 fps: testi, grafica,
  ritagli della pagina Steam e trasformazioni 3D sono rasterizzati nativamente in 4K
  (`zoom: 2`), non ingranditi.
- Tutti i tempi sono scritti in fotogrammi base a 30 fps; a 60 fps animazioni, transizioni,
  tracking e sottotitoli vengono campionati ogni mezzo fotogramma (moto realmente a 60).
- Il filmato di gioco è il trailer ufficiale a 1920×1080, 30 fps: in 4K è ingrandito
  (non esiste una sorgente a risoluzione più alta). L'interpolazione 30→60 è applicata **solo**
  alle inquadrature con movimento di camera regolare (8 su 34) dove non produce artefatti;
  armi, esplosioni, HUD in movimento restano a 30 fps nativi (ogni fotogramma ripetuto due
  volte) perché l'interpolazione li sdoppiava.
- La ripresa Blender (pagina Steam in 3D) è a 1080×1920 30 fps interpolata a 60:
  un render 4K in Cycles su CPU richiede ~98 s/fotogramma (≈ 16 ore). Con una GPU si usa
  `scripts/blender_gpu_4k.sh`.
- Render a segmenti da 600 fotogrammi, ripristinabile (`scripts/render_4k60.sh`), poi unione
  senza ricodifica e mux dell'audio.

## Errori corretti rispetto alla v1

<!-- QC_TABLE -->

## Verifiche sul master

<!-- QC_RESULTS -->

## Limiti e diritti (il video NON è pronto per la pubblicazione)

- **Filmato di gioco**: trailer ufficiali ECC: REDLINE di NetEase/Galaxy Studio. Nessuna licenza
  di riuso è stata ottenuta; l'uso a scopo di commento/informazione va valutato caso per caso
  e preferibilmente autorizzato dall'editore prima della pubblicazione.
- **Pagina Steam e logo Steam**: catture reali della pagina (12/10/2026). Il logo è quello
  presente nell'intestazione della pagina, non è affiancato al marchio STEAM FOCUS; STEAM FOCUS
  è presentato come format indipendente, non affiliato a Valve o NetEase. L'uso del nome
  "STEAM" nel nome del format va verificato con le linee guida di Valve.
- **Voce**: sintetica (Kokoro-82M, Apache-2.0), dichiarata nella chiusura. Ho verificato la
  pronuncia con trascrizione automatica (faster-whisper) e analisi di intonazione e pause, ma
  **non posso ascoltarla**: serve un ascolto umano prima della pubblicazione.
- **Musica ed effetti**: generati proceduralmente in `audio/score.py` e
  `audio/build_full_audio.py`; nessun audio di terzi nel mix v2.
- **Font**: Barlow Condensed, Inter Tight, JetBrains Mono (SIL OFL).
- Anteprima da tenere privata finché i diritti non sono chiariti.

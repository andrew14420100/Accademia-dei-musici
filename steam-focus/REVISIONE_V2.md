# STEAM FOCUS — ECC: REDLINE · Revisione v2 (master 2160×3840, 60 fps)

Questa relazione accompagna il master v2 e il confronto con la v1 (1080×1920, 30 fps).
La v1 resta conservata (commit `dea4b07`, file `out/v1_1080p30_*`). Il progetto resta in
questo repository; JARVIS non è stato toccato.

## File consegnati (cartella `out/`, non versionata)

| File | Contenuto |
| --- | --- |
| `steam_focus_ecc_redline_full_4K_60fps.mp4` | master H.264 High, 2160×3840, 60 fps CFR, AAC 320k |
| `steam_focus_ecc_redline_review_720p60.mp4` | copia leggera di revisione (720×1280, 60 fps, 23 MB) |
| `steam_focus_ecc_redline_cover.png` | copertina 2160×3840 (stesso fotogramma del master a 2,5 s, renderizzato senza sottotitoli) |
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

Confronti affiancati v1/v2 negli stessi momenti del racconto: [`docs/revisione_v2/0*.jpg`](docs/revisione_v2) (provini per capitolo e log delle verifiche nella stessa cartella).

| # | Problema nella v1 | Correzione nella v2 |
| --- | --- | --- |
| 1 | 1080×1920, 30 fps | 2160×3840, 60 fps CFR; grafica, testi e ritagli Steam renderizzati nativamente in 4K, animazioni campionate a 60 |
| 2 | Il gioco veniva nominato solo dopo ~7 s | Titolo ECC: REDLINE sul gameplay entro 0,3 s; voce «Questo è il nuovo ECC: REDLINE» |
| 3 | «ECC» poco intelligibile, «Steam» e «NetEase» pronunciati male | Testo fonetico per il sintetizzatore («E C C Rèdlain», «Stìiim», «Nèt Iis»); verifica con trascrizione automatica: 0 errori sulle singole frasi |
| 4 | Musica e letti audio presi dal trailer | Colonna sonora originale procedurale (100 BPM, La minore) + effetti sincronizzati; nessun audio di terzi |
| 5 | Nel mix, «ruolo»/«interruzioni» capiti male dal riconoscimento vocale | Musica abbassata di 12 dB sotto la voce, bassi ridotti, pad filtrato sotto 150 Hz: parole riconosciute correttamente |
| 6 | Picco +3 dBFS dopo la normalizzazione | Limitatore true peak: −14 LUFS integrati, picco ≤ −1,5 dBTP |
| 7 | Transizioni a stacco secco tra capitoli, un fade dal nero nel trailer (0,5 s) | Transizioni 3D «swing» (rotazione in profondità, sfocatura, banda di luce) solo ai cambi di capitolo; nessun fotogramma nero |
| 8 | Cartelli di capitolo grandi, lunghi da leggere | Targhe compatte (2 s) con rotazione e riflesso |
| 9 | Pannelli dati sovrapposti tra loro; pannello analisi sopra i prezzi del negozio | Ogni pannello ha la sua finestra temporale; l'analisi «1 siringa ≈ 11 mine» arriva dopo la chiusura del negozio |
| 10 | Informazioni ufficiali e opinioni non distinte | Dati ufficiali etichettati «pagina Steam»; le letture editoriali in riquadro tratteggiato «Analisi STEAM FOCUS · non verificata in partita» e annunciate dalla voce («La nostra lettura…») |
| 11 | Pagina Steam: ritagli con testo minuscolo illeggibile | Catture reali a densità 3× del 12/10/2026, ritagli leggibili (stato «In arrivo», pulsante lista desideri, tabella lingue), evidenziazioni sincronizzate alla voce |
| 12 | Chiusura lunga con logo Steam affiancato | Firma STEAM FOCUS di 1,6 s, solo marchio del format, dichiarazione «non affiliato a Valve o NetEase», «voce sintetica (IA)», fonte delle immagini |
| 13 | Area sicura generica | Area sicura TikTok (64–940 × 170–1440): titoli, pannelli e sottotitoli all'interno |
| 14 | Render unico, non riprendibile | Render a segmenti verificati con ffprobe, ripresa automatica, unione senza ricodifica |

Difetti trovati durante il controllo del primo master v2 e corretti prima della consegna:

| Difetto | Correzione |
| --- | --- |
| La riga «Voce sintetica (IA)…» della chiusura mancava e la riga sopra usciva dall'area sicura | Tre righe brevi dentro l'area sicura; segmento finale rirenderizzato |
| Nel negozio il sottotitolo copriva parte del saldo «6,000» | Per le frasi che iniziano sull'inquadratura del negozio il sottotitolo sale nella fascia vuota sopra il saldo |
| Il cartellino «Saldo» copriva la cifra reale e riportava 6.000 → 3.207 (valore intermedio, letto male già nella v1) | Inquadratura stretta sul saldo, cartellino a fianco della cifra; valore corretto 6.000 → 1.813 (ultima cifra leggibile prima che il negozio si chiuda) e uscita del cartellino prima della chiusura |
| Nel capitolo Armi la sequenza Parti/Ottiche/Impugnatura era etichettata «Catena di movimento» | Etichetta «Modifica dell'arma» |

## Verifiche sul master

Risultati sul file finale (dettagli in `out/qc/`):

| Verifica | Risultato |
| --- | --- |
| ffprobe | H.264, **2160×3840**, `avg_frame_rate=60/1`, `r_frame_rate=60/1`, **6974 fotogrammi**, 116,23 s, AAC 48 kHz stereo, 558 MB |
| Fotogrammi neri (blackdetect) | nessuno |
| Fermi immagine ≥ 0,5 s (freezedetect) | solo nel capitolo Steam (101–109 s): sono le schede della pagina ferme per la lettura (0,5–0,9 s) |
| Duplicati (mpdecimate, sul video prima del mux) | 6274 fotogrammi distinti su 6974 (90%); fuori dal capitolo Steam nessuna pausa oltre 4 fotogrammi (0,067 s). Le inquadrature non interpolate sono a 30 fps nativi, ma grafica e reinquadrature si muovono a 60 |
| Loudness (EBU R128) | −14,3 LUFS integrati, true peak −1,8 dBTP, LRA 2,2 LU |
| Sincronia voce/sottotitoli | trascrizione automatica del mix finale: 47 battute su 50 agganciate; la prima parola parte in media 0,05 s (mediana 0,07 s) dopo l'inizio del sottotitolo |
| Testo riconosciuto | coincide con il copione, salvo «vicoli» → «vicoglie», «col» → «con» e «dieci» trascritto «10» (da far verificare all'ascolto) |
| Area sicura TikTok | provini per capitolo `out/qc/sheet_*.jpg` con l'area disegnata: titoli, pannelli e sottotitoli all'interno |
| Gameplay visibile | nessun pannello pieno sopra il filmato; i pannelli dati occupano la fascia alta e restano sotto i 2–3 s per voce |

Tempi di render (CPU, nessuna GPU disponibile): ~4,5 min per segmento da 10 s, ~53 min l'intero master;
dopo il controllo sono stati rifatti solo i 4 segmenti toccati dalle correzioni.

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

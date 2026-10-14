# STEAM FOCUS — ECC: REDLINE · EXPORT REPORT (V4 finale)

Data: 14 ottobre 2026. Progetto nel repository `Accademia-dei-musici` (cartella `steam-focus/`), branch
`claude/kind-wozniak-6stu1j`. JARVIS non è stato toccato. Le versioni V1, V2 e V3 sono conservate
(`out/`, `public/*_v1|_v2|_v3.*`, cronologia git).

**Stato:** video completo renderizzato e verificato. È una **bozza privata, non pronta per la
pubblicazione** (vedi "Diritti").

## File consegnati (`out/`, non versionata)

| File | Contenuto |
| --- | --- |
| `STEAM_FOCUS_ECC_REDLINE_FINAL_4K60.mp4` | master completo, 2160×3840, 60 fps |
| `STEAM_FOCUS_ECC_REDLINE_FINAL_REVIEW_1080p60.mp4` | reportage completo 1080×1920, 60 fps (copia leggera, non un estratto) |
| `STEAM_FOCUS_BANNER_TRANSPARENT.png` | banner approvato, RGBA 1976×642, trasparente fuori dalla cornice |
| `STEAM_FOCUS_ECC_REDLINE_FINAL_SUBTITLES.srt` | sottotitoli italiani (48 battute) |
| `STEAM_FOCUS_V4_NARRATION_FINAL.wav`, `STEAM_FOCUS_V4_MUSIC_FINAL.wav`, `STEAM_FOCUS_V4_MIX_PREMASTER.wav` | voce, musica, mix prima della normalizzazione |
| `STEAM_FOCUS_ECC_REDLINE_COVER_V4_4K.png` | copertina cinematica 2160×3840 |
| `qc_v4/` | ffprobe, neri/fermi, loudness, provini per capitolo con area sicura |
| `banner_test/` | test tecnico del banner (primi 10 s dal render 4K reale) e fotogrammi |

## Verifica FFprobe — master `STEAM_FOCUS_ECC_REDLINE_FINAL_4K60.mp4`

| Voce | Valore misurato |
| --- | --- |
| Container | MP4 (faststart) |
| Video | H.264, profilo High, livello 5.2 |
| Risoluzione | **2160 × 3840** (9:16 verticale) |
| Frame rate | `r_frame_rate=60/1`, `avg_frame_rate=60/1` (**60 fps costanti**) |
| Fotogrammi | **6814** contati (`-count_frames`) = 113,567 s × 60 |
| Durata | **113,57 s** (1:53,6) |
| Pixel format | yuv420p |
| Colore | Rec.709 SDR: `color_space/primaries/transfer = bt709`, range `tv` (limited) |
| Bitrate video | 36,2 Mbit/s (CRF 17, preset slow, GOP 120) |
| Audio | AAC-LC, stereo, 48 kHz, 303 kbit/s |
| Dimensione | 517,7 MB (517 700 050 byte) |

Copia di revisione: H.264 1080×1920, 60/1 fps, 6814 fotogrammi, 113,57 s, 9,8 Mbit/s, 143,1 MB, stesso audio.

## Controlli eseguiti

| Controllo | Risultato |
| --- | --- |
| Fotogrammi neri (blackdetect su tutto il master) | **nessuno** |
| Fotogrammi fermi ≥ 0,5 s (freezedetect) | solo 96,7–107,0 s: schede della pagina Steam tenute ferme per la lettura (voluto, come in V3) |
| Loudness EBU R128 | **−14,1 LUFS** integrati, LRA 3,0 LU, true peak **−1,8 dBTP** |
| Voce/musica | durante il parlato la voce sta 12,8 dB sopra la musica; tra le frasi la musica risale a −7 dB dalla voce |
| Testo riconosciuto (trascrizione automatica del master) | 97,0% delle parole dei sottotitoli ritrovate nell'audio |
| Sincronia sottotitoli | 47 battute su 48 agganciate alla voce, scarto mediano +0,04 s, massimo 0,33 s |
| Area sicura TikTok | provini per capitolo `qc_v4/sheet_*.jpg`: banner, logo, titoli, pannelli e sottotitoli dentro l'area |
| Logo duplicato | il piccolo logo STEAM FOCUS in alto a sinistra è nascosto mentre il banner è visibile e ricompare a 8,4 s |
| Render a segmenti | 12 segmenti da 10 s, ciascuno verificato con ffprobe (600 fotogrammi), uniti senza ricodifica |

## Banner (nuova entrata e uscita)

- File: il banner approvato, reso trasparente solo fuori dalla cornice arrotondata (`scripts/banner_cutout.py`).
  Dentro, sfondo blu, logo e testi sono invariati; nessun ricampionamento. I pixel completamente
  trasparenti hanno colore azzerato (niente aloni negli editor).
- Nel video: renderizzato direttamente nella composizione 4K/60 (`src/full/Banner.tsx`), largo 1490 px
  (15% in meno della prima anteprima), centrato nell'area sicura, sopra l'azione e sopra i sottotitoli.
- **Entrata 0–0,8 s:** arriva dalla profondità in 3D (prospettiva, rotazione, parallasse con il piano
  d'ombra), maschera diagonale animata, scie di luce, passaggio di luce sul banner, motion blur reale
  (7 campioni temporali per fotogramma mentre si muove); si assesta sul primo battito (0,47 s, 128 BPM)
  con whoosh e un colpo morbido. Il gameplay è visibile dal primo fotogramma.
- **Tenuta 0,8–7,4 s:** lenta orbita di camera e fluttuazione.
- **Uscita 7,4–8,43 s:** accelera verso la camera e verso l'alto, ruota in profondità, maschera
  inclinata che si chiude, motion blur; finisce sul battito 18 mentre entra il capitolo Identità con la
  sua rotazione di camera. Suono: swell + whoosh + colpo sul battito. Nessuna schermata nera.
- Durata totale sullo schermo: circa 8,4 s.

## Sorgenti e qualità 4K (dichiarazione)

- Gameplay: trailer ufficiale ECC: REDLINE, **1920×1080 a 30 fps nativi**. Non è 4K nativo.
- Upscaling: Lanczos 2× a 3840×2160 con leggero unsharp sulla luminanza (`scripts/upscale_clips.sh`),
  poi scalato nella composizione 4K. È interpolazione: aumenta la nitidezza percepita, non aggiunge
  dettaglio reale. La super-risoluzione con IA (Real-ESRGAN) era stata provata in V3 e scartata perché
  alterava il testo dell'HUD e le texture.
- 60 fps: 8 inquadrature con movimento di camera regolare sono interpolate a 60 fps (minterpolate); le
  altre sono a 30 fps nativi con fotogrammi raddoppiati nella timeline a 60 fps. Grafica, testi,
  sottotitoli e banner sono renderizzati nativamente a 60 fps e in 4K.
- Ponte Blender (pagina Steam): renderizzato a 1080×1920 (nessuna GPU nel server) e scalato.

## Errori corretti in questa fase

- Il primo mix V4 teneva la musica troppo vicina alla voce (7,9 dB): bus musica a −19 dB e ducking
  più profondo, ora 12,8 dB.
- Una ripresa della voce diceva «righieci» invece di «più di dieci»: esclusa e sostituita.
- Inquadrature che attraversavano tagli del trailer (h_heli, i_map, e_after) e una durata negativa
  (m_air2) dopo il nuovo ritmo della voce: corrette.
- La prima uscita del banner accelerava troppo tardi (movimento concentrato in 0,3 s): curva più
  morbida su 1 s.
- Il render si è fermato al limite di 2 ore del processo durante l'11° segmento: ripreso dai segmenti
  già verificati, nessun fotogramma rifatto a mano.

## Limiti residui

- Il banner copre per circa mezzo secondo (7,4–7,9 s) una medaglia di eliminazione del trailer;
  l'HUD fisso (bussola, soldi, munizioni) resta libero.
- In alcune inquadrature i sottotitoli passano sopra scritte cinesi dell'HUD del trailer in basso
  (come in V3).
- Voce sintetica (Chatterbox, timbro sintetico, filigrana Perth): le verifiche sono misure e
  trascrizione automatica, serve l'ascolto del proprietario.

## Diritti — non pronto per la pubblicazione

- **Marchi Valve:** il banner (logo Steam con ®) e il lockup STEAM FOCUS combinano il logo Steam con
  altre parole; il banner contiene anche il logo Windows (Microsoft). Le linee guida Valve lo vietano
  senza autorizzazione scritta. Il canale non è affiliato a Valve né a NetEase.
- **Filmato:** trailer ufficiali NetEase, nessuna licenza di riuso ottenuta.
- **Banner:** grafica generata con ChatGPT e fornita dal proprietario.
- Musica: originale, generata dal codice (`audio/score_v4.py`). Fonti e licenze:
  `narration/STEAM_FOCUS_SOURCES_AND_RIGHTS.txt`.

# STEAM FOCUS — ECC: REDLINE · Revisione V3 (master 2160×3840, 60 fps)

V3 parte dalla V2 (stessa pipeline Blender + Remotion + FFmpeg, stessi fatti verificati) e
cambia identità, voce, musica e ritmo. V1 e V2 restano conservate: file `out/v1_1080p30_*` e
`out/steam_focus_ecc_redline_*`, commit `dea4b07` (V1) e `2d3ae6f` (V2); EDL, tempi e
sottotitoli V2 in `public/*_v2.*`. Il progetto resta in questo repository; JARVIS non è stato
toccato.

**Stato: anteprima privata, non pronta alla pubblicazione** (diritti NetEase sulle immagini,
marchio Valve nel logo: vedi in fondo).

## File consegnati (`out/`, non versionata)

| File | Contenuto |
| --- | --- |
| `STEAM_FOCUS_ECC_REDLINE_V3_4K60.mp4` | master H.264, 2160×3840, 60 fps CFR, AAC 320k |
| `STEAM_FOCUS_ECC_REDLINE_V3_REVIEW.mp4` | copia leggera di revisione (720×1280, 60 fps) |
| `STEAM_FOCUS_ECC_REDLINE_V3_COVER.png` | copertina 2160×3840 senza sottotitoli |
| `STEAM_FOCUS_LOGO.svg`, `STEAM_FOCUS_LOGO_TRANSPARENT.png`, `STEAM_FOCUS_LOGO_varianti/` | marchio scelto (scuro, chiaro, mono bianco, mono scuro; SVG + PNG trasparente 3840 px) |
| `STEAM_FOCUS_VOICE_A/B/C.wav` | i tre campioni di voce sottoposti alla scelta |
| `STEAM_FOCUS_NARRATION_FINAL.wav` | voce B finale, sulla timeline |
| `STEAM_FOCUS_MUSIC_FINAL.wav` | colonna sonora originale, traccia separata (prima del ducking) |
| `STEAM_FOCUS_MIX_FINAL.wav` | mix finale masterizzato (−14 LUFS, limitatore true peak) |
| `STEAM_FOCUS_SUBTITLES.srt` | sottotitoli italiani allineati alla voce V3 |
| `STEAM_FOCUS_SOURCES_AND_RIGHTS.txt` | fonti, licenze, rischi |
| `qc_v3/` | ffprobe, neri/fermi/duplicati, loudness, provini per capitolo, confronti V2/V3 (copia in `docs/revisione_v3/`) |

## Cosa cambia rispetto alla V2

| Area | V2 | V3 |
| --- | --- | --- |
| Marchio | scritta STEAM FOCUS con rombo rosso | **lockup scelto dal proprietario: logo Steam ufficiale (invariato) + «FOCUS»** (Montserrat 700 tarato sulla scritta STEAM); fisso in alto a sinistra con velo blu-notte di intensità calcolata per ogni inquadratura (`scripts/bug_contrast.py`), in copertina e nella firma |
| Identità grafica | nero + rosso + blu | design token centralizzati (`src/theme.ts`): blu notte `#0B1626`/`#13283F`/`#1B3B56`, blu Steam `#66C0F4`, bianco, grigi freddi; rosso solo per il titolo ECC: REDLINE e le informazioni negative (italiano assente, zona fuori dalla zona sicura) |
| Tipografia | Barlow Condensed | Saira Condensed (titoli, valori), Inter Tight (sottotitoli), JetBrains Mono (etichette), Montserrat (solo «FOCUS»); tutti SIL OFL, nessuno dichiarato font Valve |
| Titolo d'apertura | inchiostro scuro, illeggibile sulle parti scure | bianco su velo blu-notte, leggibile su nebbia e interni |
| Sottotitoli | bianchi | parole chiave in blu Steam, max 2 righe, area sicura TikTok |
| Voce | Kokoro `im_nicola` (giudicata meccanica) | **voce B** scelta tra tre campioni: Chatterbox Multilingual (MIT), timbro sintetico; ogni frase scelta tra 3–5 tentativi; +12% di velocità con Rubberband |
| Musica | procedurale calma, 100 BPM | **originale energica 124 BPM** (`audio/score_v3.py`): impatto in apertura, drop della batteria dopo il titolo, crescita in Identità, picco in Movimento, percussioni «tech» in Economia/Armi, riduzione sulla pagina Steam, colpo finale secco; traccia separata |
| Mix | ducking unico | ducking per stem + taglio 1,2–4,5 kHz sotto la voce; effetti anch'essi attenuati sotto la voce |
| Durata | 116,2 s | 119,9 s (pause più strette per restare entro 120 s con la voce nuova) |
| Firma | 1,6 s, testo | 1,6 s, lockup che entra in profondità con passaggio di luce, tre righe di dichiarazioni |

## Scelte e prove documentate

- **Logo.** Ho preparato due marchi originali (`brand/a_focusframe`, `brand/b_aperture`, con anteprime in `brand/previews/`). Il proprietario ha chiesto invece il logo Steam con FOCUS: realizzato così, senza modificare le forme del logo Valve. Vedi il rischio marchio in fondo.
- **Voce.** Tre campioni (`STEAM_FOCUS_VOICE_A/B/C.wav`) più la voce V2 come riferimento; scelta del proprietario: B. Correzioni fatte durante la produzione:
  - «NetEase» letto come «Netis»: nuova grafia fonetica, poi riconosciuto «NetEase»;
  - «dieci mine» capito «diecimila»: frase riscritta in «Più di dieci mine adesive» e letta con una pausa dopo «dieci», senza velocizzazione (la velocizzazione la rendeva ambigua);
  - «ECC» coperto dalla batteria in apertura: la batteria entra dopo il titolo;
  - «vicoli» coperto da un effetto del ponte Blender: effetto abbassato, effetti attenuati sotto la voce.
- **Upscaling del gameplay.** Real-ESRGAN `realesr-general-x4v3` (BSD-3) provato su fotogrammi con HUD: bordi più netti ma texture appiattite e testo piccolo alterato («ITEM» illeggibile), circa 16 s/fotogramma su CPU (≈15 h). Scartato. Il gameplay resta la sorgente 1080p/30 scalata in composizione: **non è 4K nativo**.
- **Interpolazione 60 fps.** Stessa scelta della V2: 8 inquadrature con camera regolare interpolate (`scripts/interp_clips.sh`), le altre a 30 nativi raddoppiati.
- **Tracking.** Ho provato a estendere il tracciamento della rianimazione a tutta l'inquadratura: dopo il fotogramma 30 la camera passa al primo piano e il punto va nel vuoto, quindi l'etichetta resta agganciata solo per il tratto affidabile (1 s).
- **Blender.** Nessuna GPU nel server: ponte 3D a 1080p con movimento interpolato a 60 fps; per il 4K nativo su GPU (es. RTX 5070 Ti in locale) c'è `scripts/blender_gpu_4k.sh`.

## Verifiche sul master V3

| Verifica | Risultato |
| --- | --- |
| ffprobe | H.264, **2160×3840**, `avg_frame_rate=60/1`, `r_frame_rate=60/1`, **7194 fotogrammi**, 119,90 s, AAC 48 kHz stereo, 573 MB |
| Fotogrammi neri | nessuno |
| Fermi immagine ≥ 0,5 s | solo nel capitolo Steam (104,9–113,8 s): schede della pagina ferme per la lettura (0,5–0,95 s) |
| Duplicati (video prima del mux) | 6291 fotogrammi distinti su 7194 (87%); fuori dal capitolo Steam nessuna pausa oltre 4 fotogrammi (0,067 s) |
| Loudness (EBU R128) | −13,9 LUFS integrati, true peak −1,9 dBTP, LRA 2,9 LU |
| Voce e musica | durante il parlato la voce sta 14,5 dB sopra la musica; tra una frase e l'altra la musica risale a −8 dB dalla voce |
| Testo riconosciuto (mix completo) | 98,2% di parole coincidenti; differenze solo di grafia («4» per «quattro», «10» per «dieci», «ballistica») e «mina» capito «mine» |
| Sincronia sottotitoli | 50 battute su 50 agganciate, mediana +0,05 s |
| Area sicura TikTok | provini per capitolo in `docs/revisione_v3/sheet_*.jpg`: logo, titoli, pannelli e sottotitoli dentro l'area |
| Prezzi e saldo | non coperti (sottotitoli rialzati nel negozio, cartellino del saldo a fianco della cifra) |

Durata del render: CPU a 4 thread, ~4,5 min per segmento da 10 s, ~55 min in tutto; smoke test di 8 s eseguito prima (2 fps).
Durante il lavoro il disco del server si è riempito: ho eliminato solo file intermedi riproducibili e cache (modello Parler, segmenti V2 già assemblati); i master V1 e V2 sono intatti.

## Limiti e diritti — il video NON è pronto per la pubblicazione

- **Marchio Steam nel logo.** Le linee guida Valve vietano di combinare il logo Steam con altre parole o loghi e di usarlo come elemento principale di contenuti non Valve senza autorizzazione. Il lockup «STEAM FOCUS» richiesto rientra in questo divieto: per pubblicare serve un'autorizzazione scritta di Valve, altrimenti va usato uno dei due marchi originali già pronti. La firma dichiara «non affiliato a Valve o NetEase» e «Steam e il logo Steam sono marchi di Valve Corporation», ma questo non sostituisce l'autorizzazione.
- **Filmato di gioco.** Trailer ufficiali NetEase, nessuna licenza di riuso ottenuta.
- **Voce.** Sintetica, dichiarata nella firma; filigrana Perth di Chatterbox nell'audio. **Non ho potuto ascoltarla**: le verifiche sono trascrizione automatica e misure. Serve l'ascolto del proprietario.
- **Musica.** Originale, generata dal codice; nessun audio di terzi.
- Fonti e licenze: `STEAM_FOCUS_SOURCES_AND_RIGHTS.txt`.


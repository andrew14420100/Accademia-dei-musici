# STEAM FOCUS — identità editoriale (v3)

Due concept originali, generati da `brand/make_logo.py` (SVG con testo convertito in tracciati,
font Saira, SIL OFL). Nessuno dei due usa, combina o imita il logo Steam di Valve: il marchio
Steam compare nel video solo separatamente, nel contesto della pagina Steam, invariato.

| Concept | Simbolo | Idea |
| --- | --- | --- |
| `a_focusframe/` | riquadro arrotondato, quattro angoli di messa a fuoco, rombo centrale | il mirino/inquadratura con cui "mettiamo a fuoco" un gioco; il riquadro funziona da badge su qualsiasi sfondo |
| `b_aperture/` | quattro frecce che convergono su un rombo | messa a fuoco, scoperta, direzione; senza riquadro, più leggero |

Varianti per concept: `symbol`, `stacked_dark|light` (due righe), `horizontal_dark|light`
(una riga, compatta), `mono_white`, `mono_dark`. PNG trasparenti in `png/` (2160 px di base).
Anteprime sopra il gameplay: `previews/` (`scripts/logo_preview.mjs`).

Colori: token in `src/theme.ts` (`#0B1626`, `#13283F`, `#1B3B56`, `#66C0F4`, `#F3F5F7`;
`#1F6FA3` per il blu su fondo chiaro).

Prima di pubblicare: verificare l'uso della parola "STEAM" nel nome del format rispetto ai
marchi Valve (vedi `REVISIONE_V2.md` e le linee guida https://partner.steamgames.com/doc/marketing/branding).

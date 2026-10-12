/**
 * STEAM FOCUS v3 design tokens — the single source for colour, type, spacing,
 * radii and motion. The same values drive brand/make_logo.py (keep in sync).
 *
 * Palette: night blues from the Steam ecosystem, Steam blue for platform data,
 * white and cold greys for text. REDLINE red is an accent reserved for facts
 * about the game itself (never decorative, never dominant). No orange.
 */
export const palette = {
  ink: '#0B1626', // deepest background
  night: '#13283F', // panels
  petrol: '#1B3B56', // raised panels, tile gradient
  sky: '#66C0F4', // Steam blue: platform data, focus, highlights
  skyDeep: '#1F6FA3', // Steam-blue text on light backgrounds
  paper: '#F3F5F7', // primary text
  frost: '#A9B8C8', // secondary text (cold grey)
  slate: '#5B6B7C', // tertiary, rules
  redline: '#E3262E', // ECC: REDLINE accent, narrative use only
} as const;

export const alpha = {
  glass: 'rgba(11,22,38,0.78)', // translucent panel over gameplay
  glassStrong: 'rgba(11,22,38,0.90)',
  hairline: 'rgba(102,192,244,0.28)',
  shadow: '0 18px 48px rgba(0,0,0,0.45)',
  textShadow: '0 2px 10px rgba(0,0,0,0.65)',
} as const;

/** Free fonts (SIL OFL), chosen for affinity with the Steam store look. Not Valve fonts. */
export const type = {
  display: 'Saira', // titles, chapter plates, wordmark, numbers
  text: 'Inter Tight', // subtitles, body copy
  mono: 'JetBrains Mono', // labels, HUD-style kickers
  // sizes in 1080x1920 design pixels (x2 in the 4K master)
  size: {kicker: 22, label: 26, body: 34, subtitle: 46, value: 52, title: 88, hero: 132},
  tracking: {kicker: '0.14em', label: '0.08em', display: '0.02em'},
} as const;

export const space = {xs: 8, s: 14, m: 22, l: 36, xl: 56} as const;
export const radius = {s: 6, m: 12, l: 22, tile: 0.22} as const;

/** Motion: one curve family; durations in 30 fps base frames. */
export const motion = {
  in: 12,
  out: 9,
  stagger: 4,
  hold: 45,
  bezierOut: [0.16, 1, 0.3, 1],
  bezierInOut: [0.65, 0, 0.35, 1],
} as const;

import {loadFont} from '@remotion/fonts';
import {Easing, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {alpha, palette, type} from './theme';

// STEAM FOCUS — vertical news format.
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

// Keep type inside the area social players leave uncovered
// (top status bar, bottom caption/UI band, right action rail).
// TikTok 9:16 safe area (top tabs, right action rail, bottom caption band).
export const SAFE = {left: 64, right: 940, top: 170, bottom: 1440};

// v3: values come from the central tokens in theme.ts.
export const color = {
  ink: palette.ink,
  night: palette.night,
  petrol: palette.petrol,
  paper: palette.paper,
  frost: palette.frost,
  dim: 'rgba(243,245,247,0.74)',
  // Accent for data that comes from the Steam store page.
  steam: palette.sky,
  // Accent for facts about the game itself (ECC: REDLINE brand red), used sparingly.
  redline: palette.redline,
  glass: alpha.glass,
  hairline: alpha.hairline,
};

export const font = {
  display: type.display,
  text: type.text,
  mono: type.mono,
};

export const fontsReady = Promise.all([
  loadFont({family: font.display, url: staticFile('fonts/SairaCondensed-500.ttf'), weight: '500'}),
  loadFont({family: font.display, url: staticFile('fonts/SairaCondensed-600.ttf'), weight: '600'}),
  loadFont({family: font.display, url: staticFile('fonts/SairaCondensed-700.ttf'), weight: '700'}),
  loadFont({family: font.text, url: staticFile('fonts/InterTight.ttf'), weight: '100 900'}),
  loadFont({family: font.mono, url: staticFile('fonts/JetBrainsMono.ttf'), weight: '100 800'}),
]);

// One motion language for the whole show: fast attack, long settle.
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

/**
 * All timing in this project is authored at 30 fps ("base frames"). Components
 * read a fractional base frame, so the same animation renders natively smooth
 * in a 60 fps composition and unchanged at 30 fps.
 */
export const BASE_FPS = 30;
export const useBaseFrame = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (frame * BASE_FPS) / fps;
};
/** Composition frames per base frame (2 at 60 fps). */
export const useFrameScale = () => useVideoConfig().fps / BASE_FPS;

/** Sample a per-base-frame track ([x, y, ...] rows) at a fractional frame. */
export const sampleTrack = (rows: number[][], f: number) => {
  const i = Math.max(0, Math.min(rows.length - 1, f));
  const a = Math.floor(i);
  const b = Math.min(rows.length - 1, a + 1);
  const t = i - a;
  return rows[a].map((v, k) => v + (rows[b][k] - v) * t);
};

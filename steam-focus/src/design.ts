import {loadFont} from '@remotion/fonts';
import {Easing, staticFile} from 'remotion';

// STEAM FOCUS — vertical news format.
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;

// Keep type inside the area social players leave uncovered
// (top status bar, bottom caption/UI band, right action rail).
export const SAFE = {left: 72, right: 1008, top: 120, bottom: 1540};

export const color = {
  ink: '#0A0D12',
  paper: '#F3F5F7',
  dim: 'rgba(243,245,247,0.72)',
  // Accent for data that comes from the Steam store page.
  steam: '#66C0F4',
  // Accent for data about the game itself (ECC: REDLINE brand red).
  redline: '#E3262E',
  glass: 'rgba(9,12,17,0.90)',
  hairline: 'rgba(255,255,255,0.16)',
};

export const font = {
  display: 'Barlow Condensed',
  text: 'Inter Tight',
  mono: 'JetBrains Mono',
};

export const fontsReady = Promise.all([
  loadFont({family: font.display, url: staticFile('fonts/BarlowCondensed-SemiBold.ttf'), weight: '600'}),
  loadFont({family: font.display, url: staticFile('fonts/BarlowCondensed-Bold.ttf'), weight: '700'}),
  loadFont({family: font.text, url: staticFile('fonts/InterTight.ttf'), weight: '100 900'}),
  loadFont({family: font.mono, url: staticFile('fonts/JetBrainsMono.ttf'), weight: '100 800'}),
]);

// One motion language for the whole show: fast attack, long settle.
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

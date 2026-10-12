import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {color, easeOut, font, HEIGHT, WIDTH} from '../design';

const LOGO_W = 4748; // steam_logo_inverse.png, Valve "inverse" artwork
const LOGO_H = 1433;

/**
 * Valve-approved inverse logo (pure white, with ®) on its own: nothing else
 * inside its clear space, no lockup with the show name, no alteration.
 * Valve's legal attribution sits well outside the clear space.
 */
export const SteamEndCard: React.FC<{at: number}> = ({at}) => {
  const frame = useCurrentFrame();
  if (frame < at) return null;
  const dim = interpolate(frame, [at, at + 12], [0, 0.9], {easing: easeOut, extrapolateRight: 'clamp'});
  const show = interpolate(frame, [at + 4, at + 16], [0, 1], {easing: easeOut, extrapolateRight: 'clamp'});
  const w = 560;
  const h = (w * LOGO_H) / LOGO_W;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{backgroundColor: color.ink, opacity: dim}} />
      <Img
        src={staticFile('brand/steam_logo_inverse.png')}
        style={{
          position: 'absolute',
          width: w,
          height: h,
          left: (WIDTH - w) / 2,
          top: (HEIGHT - h) / 2 - 120,
          opacity: show,
          transform: `scale(${0.985 + 0.015 * show})`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 96,
          right: 96,
          top: 1400,
          textAlign: 'center',
          fontFamily: font.text,
          fontSize: 19,
          lineHeight: 1.45,
          color: 'rgba(243,245,247,0.55)',
          opacity: show,
        }}
      >
        ©2026 Valve Corporation. Steam e il logo Steam sono marchi e/o marchi registrati appartenenti a Valve
        Corporation negli Stati Uniti e/o in altri Paesi.
      </div>
    </AbsoluteFill>
  );
};

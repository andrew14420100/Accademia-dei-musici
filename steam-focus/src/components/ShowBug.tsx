import {interpolate, useCurrentFrame} from 'remotion';
import {color, font, SAFE} from '../design';
import {Kicker, MaskLine, Rule} from './Type';

/** Programme identity, top-left. Never shares the screen with the Steam logo. */
export const ShowBug: React.FC<{inAt: number; outAt: number; episode: string}> = ({inAt, outAt, episode}) => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [outAt, outAt + 10], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left,
        top: SAFE.top + 14,
        opacity: out,
        textShadow: '0 1px 14px rgba(0,0,0,0.45)',
        filter: 'drop-shadow(0 1px 8px rgba(0,0,0,0.25))',
      }}
    >
      <MaskLine at={inAt}>
        <div
          style={{
            fontFamily: font.display,
            fontWeight: 600,
            fontSize: 34,
            letterSpacing: '0.30em',
            color: color.paper,
          }}
        >
          STEAM FOCUS
        </div>
      </MaskLine>
      <div style={{marginTop: 10, marginBottom: 10}}>
        <Rule at={inAt + 4} width={232} thickness={2} />
      </div>
      <MaskLine at={inAt + 8}>
        <Kicker style={{fontSize: 18, color: color.dim}}>{episode}</Kicker>
      </MaskLine>
    </div>
  );
};

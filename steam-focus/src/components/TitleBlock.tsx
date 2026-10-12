import {interpolate } from 'remotion';
import {color, font, SAFE, useBaseFrame} from '../design';
import {Kicker, MaskLine, Rule} from './Type';

/**
 * Game title in white over a soft night-blue scrim (no panel): readable on the
 * bright cloud layer and on the dark cabin of the helicopter insertion.
 * It drifts slower than the footage push-in, which reads as depth.
 */
export const TitleBlock: React.FC<{at: number}> = ({at}) => {
  const frame = useBaseFrame();
  const drift = interpolate(frame, [at, at + 60], [10, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scrim = interpolate(frame, [at - 2, at + 8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <>
    {/* night-blue scrim behind the title block: readable on fog and on dark interiors */}
    <div style={{position: 'absolute', inset: 0, opacity: scrim, background: 'radial-gradient(900px 560px at 330px 470px, rgba(11,22,38,0.62), rgba(11,22,38,0) 100%)'}} />
    <div style={{position: 'absolute', left: SAFE.left, top: 318 + drift, width: SAFE.right - SAFE.left}}>
      <MaskLine at={at}>
        <Kicker tint={color.steam} style={{fontWeight: 700, textShadow: '0 1px 10px rgba(0,0,0,0.6)'}}>
          NetEase Games · Galaxy Studio
        </Kicker>
      </MaskLine>
      <MaskLine at={at + 3} len={18}>
        <div
          style={{
            fontFamily: font.display,
            fontWeight: 700,
            fontSize: 176,
            lineHeight: 0.92,
            letterSpacing: '-0.005em',
            color: color.paper,
            marginTop: 8,
            textShadow: '0 4px 30px rgba(11,22,38,0.75), 0 1px 3px rgba(0,0,0,0.5)',
          }}
        >
          ECC: REDLINE
        </div>
      </MaskLine>
      <div style={{marginTop: 18, marginBottom: 18}}>
        <Rule at={at + 9} width={120} thickness={4} color={color.redline} />
      </div>
      <MaskLine at={at + 11}>
        <div
          style={{
            fontFamily: font.text,
            fontWeight: 600,
            fontSize: 40,
            lineHeight: 1.18,
            color: color.paper,
            maxWidth: 820,
            textShadow: '0 2px 14px rgba(11,22,38,0.85)',
          }}
        >
          Sparatutto tattico + sport estremi.
        </div>
      </MaskLine>
      <MaskLine at={at + 14}>
        <div style={{fontFamily: font.text, fontWeight: 600, fontSize: 40, lineHeight: 1.18, color: color.paper, textShadow: '0 2px 14px rgba(11,22,38,0.85)'}}>
          Free-to-play su PC.
        </div>
      </MaskLine>
    </div>
    </>
  );
};

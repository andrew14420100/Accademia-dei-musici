import {interpolate, useCurrentFrame} from 'remotion';
import {color, font, SAFE} from '../design';
import {Kicker, MaskLine, Rule} from './Type';

/**
 * Game title set in ink directly on the bright cloud layer of the
 * helicopter insertion: the plate stays visible, no panel behind the type.
 * It drifts slower than the footage push-in, which reads as depth.
 */
export const TitleBlock: React.FC<{at: number}> = ({at}) => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [at, at + 60], [10, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: SAFE.left, top: 318 + drift, width: SAFE.right - SAFE.left}}>
      <MaskLine at={at}>
        <Kicker tint={color.redline} style={{fontWeight: 700}}>
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
            color: color.ink,
            marginTop: 8,
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
            color: color.ink,
            maxWidth: 820,
          }}
        >
          Sparatutto tattico + sport estremi.
        </div>
      </MaskLine>
      <MaskLine at={at + 14}>
        <div style={{fontFamily: font.text, fontWeight: 600, fontSize: 40, lineHeight: 1.18, color: color.ink}}>
          Free-to-play su PC.
        </div>
      </MaskLine>
    </div>
  );
};

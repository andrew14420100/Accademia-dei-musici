import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {color, font, HEIGHT, WIDTH} from '../design';
import {Kicker, MaskLine, progress} from './Type';

type Pt = {x: number; y: number};

/**
 * Data label attached to a point that moves with the image (a tracked
 * player, or a page element projected from the Blender camera).
 *
 * `glass` sits on the store page; `open` sits on gameplay with only a soft
 * shadow behind the type, so the action is never boxed out.
 */
export const Callout: React.FC<{
  anchor: Pt;
  /** Where the leader meets the label (label's left edge, at this y). */
  dock: Pt;
  labelSide: 'above' | 'below';
  at: number;
  until: number;
  tint: string;
  kicker: string;
  title: string;
  sub?: string;
  variant: 'open' | 'glass';
  width?: number;
}> = ({anchor, dock, labelSide, at, until, tint, kicker, title, sub, variant, width = 720}) => {
  const frame = useCurrentFrame();
  if (frame < at || frame > until + 8) return null;
  const ring = progress(frame, at, 10);
  const line = progress(frame, at + 3, 12);
  const out = interpolate(frame, [until, until + 6], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  // Leader: anchor -> elbow (vertical first) -> dock.
  const elbow = {x: anchor.x, y: dock.y};
  const seg1 = Math.abs(dock.y - anchor.y);
  const seg2 = Math.abs(dock.x - anchor.x);
  const total = seg1 + seg2 || 1;
  const pulse = interpolate(frame - at, [0, 18], [0, 1], {extrapolateRight: 'clamp'});

  const label = (
    <div
      style={{
        position: 'absolute',
        left: dock.x,
        ...(labelSide === 'above' ? {bottom: HEIGHT - dock.y + 14} : {top: dock.y + 14}),
        ...(variant === 'glass'
          ? {
              backgroundColor: color.glass,
              backdropFilter: 'blur(12px)',
              borderLeft: `4px solid ${tint}`,
              padding: '18px 24px 20px',
              borderRadius: 4,
              maxWidth: width,
              clipPath: `inset(0 ${(1 - line) * 100}% 0 0)`,
            }
          : {width, textShadow: '0 2px 18px rgba(0,0,0,0.65), 0 0 2px rgba(0,0,0,0.4)'}),
      }}
    >
      <MaskLine at={at + 6}>
        <Kicker tint={tint}>{kicker}</Kicker>
      </MaskLine>
      <MaskLine at={at + 8} len={16}>
        <div
          style={{
            fontFamily: font.display,
            fontWeight: 700,
            fontSize: variant === 'glass' ? 58 : 84,
            lineHeight: 0.98,
            color: color.paper,
            marginTop: 6,
            textTransform: 'uppercase',
          }}
        >
          {title}
        </div>
      </MaskLine>
      {sub ? (
        <MaskLine at={at + 11}>
          <div
            style={{
              fontFamily: variant === 'glass' ? font.text : font.mono,
              fontWeight: variant === 'glass' ? 500 : 600,
              fontSize: variant === 'glass' ? 30 : 28,
              letterSpacing: variant === 'glass' ? 0 : '0.08em',
              textTransform: variant === 'glass' ? 'none' : 'uppercase',
              color: color.dim,
              marginTop: 8,
            }}
          >
            {sub}
          </div>
        </MaskLine>
      ) : null}
    </div>
  );

  return (
    <AbsoluteFill style={{opacity: out}}>
      {variant === 'open' ? (
        // Soft local shadow so white type holds on bright sky; not a panel.
        <div
          style={{
            position: 'absolute',
            left: dock.x - 160,
            top: dock.y - (labelSide === 'above' ? 300 : -20),
            width: width + 320,
            height: 300,
            background: 'radial-gradient(closest-side, rgba(0,0,0,0.42), rgba(0,0,0,0))',
            opacity: line,
          }}
        />
      ) : null}
      <svg width={WIDTH} height={HEIGHT} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        <polyline
          points={`${anchor.x},${anchor.y} ${elbow.x},${elbow.y} ${dock.x},${dock.y}`}
          fill="none"
          stroke={color.paper}
          strokeOpacity={0.9}
          strokeWidth={2}
          strokeDasharray={total}
          strokeDashoffset={total * (1 - line)}
          style={{filter: 'drop-shadow(0 0 3px rgba(0,0,0,0.6))'}}
        />
        <circle cx={anchor.x} cy={anchor.y} r={5 * ring} fill={tint} />
        <circle
          cx={anchor.x}
          cy={anchor.y}
          r={14 * ring}
          fill="none"
          stroke={color.paper}
          strokeWidth={2}
          style={{filter: 'drop-shadow(0 0 3px rgba(0,0,0,0.6))'}}
        />
        <circle
          cx={anchor.x}
          cy={anchor.y}
          r={14 + 30 * pulse}
          fill="none"
          stroke={tint}
          strokeWidth={2}
          strokeOpacity={1 - pulse}
        />
      </svg>
      {label}
    </AbsoluteFill>
  );
};

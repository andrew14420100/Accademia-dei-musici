import {interpolate } from 'remotion';
import {color, easeOut, font, useBaseFrame} from '../design';

const p = (frame: number, start: number, len: number) =>
  interpolate(frame, [start, start + len], [0, 1], {
    easing: easeOut,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

/** Line that rises out of its own baseline mask. */
export const MaskLine: React.FC<{
  at: number;
  len?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({at, len = 16, style, children}) => {
  const frame = useBaseFrame();
  const t = p(frame, at, len);
  return (
    <div style={{overflow: 'hidden', paddingBottom: '0.08em', marginBottom: '-0.08em'}}>
      <div style={{transform: `translateY(${(1 - t) * 105}%)`, ...style}}>{children}</div>
    </div>
  );
};

/** Hairline that draws from the left. */
export const Rule: React.FC<{at: number; width: number; len?: number; color?: string; thickness?: number}> = ({
  at,
  width,
  len = 14,
  color: c = color.paper,
  thickness = 2,
}) => {
  const frame = useBaseFrame();
  return <div style={{height: thickness, width: width * p(frame, at, len), backgroundColor: c}} />;
};

export const Kicker: React.FC<{children: React.ReactNode; tint?: string; style?: React.CSSProperties}> = ({
  children,
  tint = color.paper,
  style,
}) => (
  <div
    style={{
      fontFamily: font.mono,
      fontWeight: 600,
      fontSize: 26,
      letterSpacing: '0.12em',
      textTransform: 'uppercase',
      color: tint,
      ...style,
    }}
  >
    {children}
  </div>
);

export const progress = p;

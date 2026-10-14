import {AbsoluteFill, interpolate, OffthreadVideo, staticFile } from 'remotion';
import {Kicker} from '../components/Type';
import {color, easeOut, HEIGHT, WIDTH, useBaseFrame} from '../design';
import {project, Shot} from './edl';

/**
 * Magnifier for HUD elements that sit in the bottom band of the source frame
 * (covered by social-app UI in 9:16): the region is lifted, enlarged, into
 * the safe area with a leader to where it really is.
 */
export const Loupe: React.FC<{
  s: Shot;
  region: {x: number; y: number; w: number; h: number};
  at: number;
  until: number;
  box: {x: number; y: number; w: number};
  kicker: string;
  tint?: string;
}> = ({s, region, at, until, box, kicker, tint = color.steam}) => {
  const frame = useBaseFrame();
  if (frame < at || frame > until + 10) return null;
  const p = interpolate(frame, [at, at + 12], [0, 1], {easing: easeOut, extrapolateRight: 'clamp'});
  const out = interpolate(frame, [until, until + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const k = box.w / region.w;
  const h = region.h * k;
  const src = project(s, frame, region.x + region.w / 2, region.y + region.h / 2);
  const target = {x: Math.min(Math.max(src.x, 40), WIDTH - 40), y: Math.min(src.y, HEIGHT - 40)};
  return (
    <AbsoluteFill style={{opacity: out}}>
      <svg width={WIDTH} height={HEIGHT} style={{position: 'absolute', inset: 0}}>
        <line
          x1={box.x + box.w / 2}
          y1={box.y + h}
          x2={target.x}
          y2={box.y + h + (target.y - box.y - h) * p}
          stroke={color.paper}
          strokeOpacity={0.8}
          strokeWidth={2}
          strokeDasharray="6 8"
        />
      </svg>
      <div
        style={{
          position: 'absolute',
          left: box.x,
          top: box.y - 44,
          opacity: p,
        }}
      >
        <Kicker tint={tint} style={{fontSize: 22, textShadow: '0 2px 12px rgba(0,0,0,0.7)'}}>
          {kicker}
        </Kicker>
      </div>
      <div
        style={{
          position: 'absolute',
          left: box.x,
          top: box.y,
          width: box.w,
          height: h,
          overflow: 'hidden',
          borderRadius: 10,
          border: `3px solid ${color.paper}`,
          boxShadow: '0 24px 60px rgba(0,0,0,0.55)',
          transform: `perspective(1200px) rotateX(${(1 - p) * 25}deg) scale(${0.9 + 0.1 * p})`,
          transformOrigin: 'bottom center',
          opacity: p,
        }}
      >
        <OffthreadVideo
          src={staticFile(`full/${s.id}.mp4`)}
          muted
          style={{position: 'absolute', width: 1920 * k, height: 1080 * k, left: -region.x * k, top: -region.y * k}}
        />
      </div>
    </AbsoluteFill>
  );
};

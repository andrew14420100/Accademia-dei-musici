import {AbsoluteFill, Freeze, interpolate, OffthreadVideo, staticFile} from 'remotion';
import {easeInOut, easeOut, HEIGHT, useBaseFrame, useFrameScale, WIDTH} from '../design';
import {cropOf, EDL, Shot} from './edl';

const SWING_IN = 9; // base frames
const SWING_OUT = 6;

/**
 * One official trailer shot, full-bleed 9:16, reframed on the action.
 * Chapter boundaries use a camera "swing": the outgoing plate turns away in
 * depth, the incoming one turns in from the other side and settles, with a
 * short light band. Cuts inside a chapter stay hard.
 */
export const FullShot: React.FC<{s: Shot; swingIn: boolean; swingOut: boolean; src?: string}> = ({s, swingIn, swingOut, src}) => {
  const frame = useBaseFrame();
  const k = useFrameScale();
  const {cx, cy, scale} = cropOf(s, frame);
  const freezeAt = s.freezeAfter ? Math.round(s.freezeAfter * EDL.fps * k) : null;

  let rot = 0;
  let depth = 1;
  let blur = 0;
  let light = 0;
  if (swingIn && frame < SWING_IN) {
    const p = interpolate(frame, [0, SWING_IN], [1, 0], {easing: easeOut, extrapolateRight: 'clamp'});
    rot = 16 * p;
    depth = 1 + 0.1 * p;
    blur = 8 * p;
    light = 0.35 * p;
  }
  if (swingOut && frame > s.frames - SWING_OUT) {
    const p = interpolate(frame, [s.frames - SWING_OUT, s.frames], [0, 1], {easing: easeInOut, extrapolateRight: 'clamp'});
    rot = -14 * p;
    depth = 1 - 0.06 * p;
    blur = 6 * p;
    light = 0.25 * p;
  }

  const video = (
    <OffthreadVideo
      src={staticFile(src ?? `full/${s.id}.mp4`)}
      muted
      style={{
        position: 'absolute',
        width: 1920 * scale,
        height: 1080 * scale,
        left: WIDTH / 2 - cx * scale,
        top: HEIGHT / 2 - cy * scale,
        filter: 'contrast(1.05) saturate(1.06)',
      }}
    />
  );

  return (
    <AbsoluteFill style={{backgroundColor: '#000', perspective: 1800, overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          overflow: 'hidden',
          transform: `rotateY(${rot}deg) scale(${depth * (1 + Math.abs(rot) * 0.012)})`,
          filter: blur > 0.2 ? `blur(${blur}px)` : undefined,
        }}
      >
        {freezeAt !== null ? (
          <Freeze frame={freezeAt} active={(f) => f >= freezeAt}>
            {video}
          </Freeze>
        ) : (
          video
        )}
        {light > 0.01 ? (
          <AbsoluteFill
            style={{
              background: 'linear-gradient(100deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.9) 50%, rgba(255,255,255,0) 70%)',
              opacity: light,
              mixBlendMode: 'screen',
            }}
          />
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

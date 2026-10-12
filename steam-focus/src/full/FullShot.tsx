import {AbsoluteFill, Freeze, interpolate, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {easeOut, HEIGHT, WIDTH} from '../design';
import {cropOf, EDL, Shot} from './edl';

const WHIP = 6; // frames

/**
 * One official trailer shot, full-bleed 9:16, reframed on the action.
 * Section boundaries use a short horizontal whip (motion blur + travel)
 * instead of a template wipe; cuts inside a section stay hard.
 */
export const FullShot: React.FC<{s: Shot; whipIn: boolean; whipOut: boolean}> = ({s, whipIn, whipOut}) => {
  const frame = useCurrentFrame();
  const {cx, cy, scale} = cropOf(s, frame);
  const freezeAt = s.freezeAfter ? Math.round(s.freezeAfter * EDL.fps) : null;

  let dx = 0;
  let blur = 0;
  if (whipIn && frame < WHIP) {
    const p = interpolate(frame, [0, WHIP], [1, 0], {easing: easeOut});
    dx = 220 * p;
    blur = 14 * p;
  }
  if (whipOut && frame > s.frames - WHIP) {
    const p = interpolate(frame, [s.frames - WHIP, s.frames], [0, 1], {extrapolateRight: 'clamp'});
    dx = -220 * p * p;
    blur = 14 * p;
  }

  const video = (
    <OffthreadVideo
      src={staticFile(`full/${s.id}.mp4`)}
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
    <AbsoluteFill
      style={{
        overflow: 'hidden',
        backgroundColor: '#000',
        transform: `translateX(${dx}px) scale(${1 + blur * 0.004})`,
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
    </AbsoluteFill>
  );
};

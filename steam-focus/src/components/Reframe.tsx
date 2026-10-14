import {AbsoluteFill, interpolate, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import {easeInOut, HEIGHT, WIDTH} from '../design';

const SRC_W = 1920;
const SRC_H = 1080;

/** [frame, source x of the crop centre] — repeat a frame number for a hard jump. */
export type CropKeys = Array<[number, number]>;

export type Reframing = {
  keys: CropKeys;
  /** Slow virtual push-in over the shot: [startZoom, endZoom]. */
  push: [number, number];
  duration: number;
  /** Source y kept at screen centre (default: frame centre). */
  cy?: number;
};

export const cropAt = (r: Reframing, frame: number) => {
  const frames = r.keys.map((k) => k[0]);
  const xs = r.keys.map((k) => k[1]);
  const cx = interpolate(frame, frames, xs, {
    easing: easeInOut,
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const zoom = interpolate(frame, [0, r.duration], r.push, {extrapolateRight: 'clamp'});
  const scale = (HEIGHT / SRC_H) * zoom;
  // Never let the crop reveal past the source edges.
  const half = WIDTH / 2 / scale;
  const x = Math.min(SRC_W - half, Math.max(half, cx));
  const halfH = HEIGHT / 2 / scale;
  const y = Math.min(SRC_H - halfH, Math.max(halfH, r.cy ?? SRC_H / 2));
  return {cx: x, cy: y, scale};
};

/** Source-pixel position -> screen position for overlays on a reframed shot. */
export const toScreen = (r: Reframing, frame: number, x: number, y: number) => {
  const {cx, cy, scale} = cropAt(r, frame);
  return {x: WIDTH / 2 + (x - cx) * scale, y: HEIGHT / 2 + (y - cy) * scale};
};

/** 16:9 official footage shown full-bleed in 9:16, following the action. */
export const Reframe: React.FC<{src: string; r: Reframing}> = ({src, r}) => {
  const frame = useCurrentFrame();
  const {cx, cy, scale} = cropAt(r, frame);
  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: '#000'}}>
      <OffthreadVideo
        src={staticFile(src)}
        muted
        style={{
          position: 'absolute',
          width: SRC_W * scale,
          height: SRC_H * scale,
          left: WIDTH / 2 - cx * scale,
          top: HEIGHT / 2 - cy * scale,
          filter: 'contrast(1.05) saturate(1.06)',
        }}
      />
    </AbsoluteFill>
  );
};

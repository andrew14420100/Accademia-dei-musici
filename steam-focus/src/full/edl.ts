import edlJson from '../../public/full_edl.json';
import {HEIGHT, WIDTH} from '../design';

export type Shot = {
  id: string;
  section: string;
  src: 'G' | 'S3';
  sin: number;
  from: number;
  frames: number;
  cx: Array<[number, number]> | null;
  zoom: [number, number] | null;
  cy: number | null;
  freezeAfter: number | null;
};

type Line = {id: string; text: string; from: number; to: number; words: Array<[number, number, string]>};

export const EDL = edlJson as unknown as {
  fps: number;
  frames: number;
  sections: Record<string, [number, number]>;
  s3: {from: number; holdUntil: number; italianAt: number; logoAt: number};
  shots: Shot[];
  lines: Line[];
  cues: Array<{from: number; to: number; text: string}>;
  voice: Array<{id: string; from: number; dur: number; section: string}>;
};

const FPS = EDL.fps;
const SRC_W = 1920;
const SRC_H = 1080;

const norm = (s: string) =>
  s
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]/g, '');

/** Absolute frame where a spoken word starts (first ASR word with that prefix). */
export const wordAt = (lineId: string, prefix: string): number => {
  const line = EDL.lines.find((l) => l.id === lineId);
  if (!line) throw new Error(`no line ${lineId}`);
  const w = line.words.find((x) => norm(x[2]).startsWith(norm(prefix)));
  if (!w) throw new Error(`no word ${prefix} in ${lineId}`);
  return line.from + Math.round(w[0] * FPS);
};

export const shot = (id: string) => {
  const s = EDL.shots.find((x) => x.id === id);
  if (!s) throw new Error(`no shot ${id}`);
  return s;
};

const lerpKeys = (keys: Array<[number, number]>, t: number) => {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const [t0, v0] = keys[i - 1];
      const [t1, v1] = keys[i];
      const u = (t - t0) / (t1 - t0);
      const e = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; // ease in-out cubic
      return v0 + (v1 - v0) * e;
    }
  }
  return keys[keys.length - 1][1];
};

/** Crop of a 16:9 trailer shot into 9:16 at a local frame. */
export const cropOf = (s: Shot, localFrame: number) => {
  const t = localFrame / FPS;
  const z = s.zoom ? s.zoom[0] + (s.zoom[1] - s.zoom[0]) * Math.min(1, localFrame / Math.max(1, s.frames)) : 1.03;
  const scale = (HEIGHT / SRC_H) * z;
  const halfW = WIDTH / 2 / scale;
  const halfH = HEIGHT / 2 / scale;
  const cx = s.cx ? lerpKeys(s.cx, t) : SRC_W / 2;
  return {
    cx: Math.min(SRC_W - halfW, Math.max(halfW, cx)),
    cy: Math.min(SRC_H - halfH, Math.max(halfH, s.cy ?? SRC_H / 2)),
    scale,
  };
};

/** Source pixel -> screen pixel on a reframed shot. */
export const project = (s: Shot, localFrame: number, x: number, y: number) => {
  const {cx, cy, scale} = cropOf(s, localFrame);
  return {x: WIDTH / 2 + (x - cx) * scale, y: HEIGHT / 2 + (y - cy) * scale};
};

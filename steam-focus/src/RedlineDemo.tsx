import {useEffect, useState} from 'react';
import {
  AbsoluteFill,
  continueRender,
  delayRender,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import anchors from '../public/s3_anchors.json';
import track from '../public/s2_track.json';
import {Callout} from './components/Callout';
import {Reframe, Reframing, toScreen} from './components/Reframe';
import {ShowBug} from './components/ShowBug';
import {SteamEndCard} from './components/SteamEndCard';
import {TitleBlock} from './components/TitleBlock';
import {progress} from './components/Type';
import {color, fontsReady, SAFE} from './design';

// Timeline (30 fps). Every shot is official ECC: REDLINE footage from its
// Steam store trailer; S3 is the Blender shot built on the real store page.
const S1 = {from: 0, len: 104}; // helicopter insertion, gameplay 63.25 s
const S2 = {from: 104, len: 54}; // combat + explosion, gameplay 349.57 s
const S3 = {from: 158, len: 292}; // scope blast -> Steam page (Blender)
export const DEMO_FRAMES = S3.from + S3.len; // 450 = 15 s

// Crop centre (source px) follows the subject; S1 cuts hard at frame 75.
const R1: Reframing = {
  duration: S1.len,
  // Zoom + raised centre keep the trailer's burned-in caption out of frame.
  push: [1.08, 1.13],
  cy: 505,
  keys: [
    [0, 1150],
    [9, 1090],
    [14, 1480],
    [17, 1400],
    [20, 1160],
    [24, 470],
    [28, 340],
    [32, 420],
    [36, 880],
    [40, 960],
    [52, 1010],
    [74, 990],
    [75, 960],
    [103, 965],
  ],
};
const R2: Reframing = {duration: S2.len, push: [1.02, 1.08], keys: [[0, 900], [53, 990]]};

type P = [number, number, number];
const pt = (name: keyof typeof anchors.points, i: number) => {
  const arr = anchors.points[name] as P[];
  const v = arr[Math.max(0, Math.min(arr.length - 1, i))];
  return {x: v[0], y: v[1]};
};

const RunnerCallout: React.FC = () => {
  const frame = useCurrentFrame();
  const runner = track.runner[Math.min(track.runner.length - 1, frame)];
  // Chest height of the tracked player.
  const a = toScreen(R2, frame, runner[0], runner[1] - 45);
  return (
    <Callout
      anchor={a}
      dock={{x: SAFE.left, y: 610}}
      labelSide="above"
      at={3}
      until={S2.len + 20}
      tint={color.redline}
      kicker="Gameplay · movimento"
      title="Movimento a catena"
      sub="Sprint · scivolata · rampino"
      variant="open"
      width={860}
    />
  );
};

const PageCallouts: React.FC = () => {
  const frame = useCurrentFrame(); // 0-based Blender frame index
  const rel = pt('release', frame);
  const ita = pt('italian', frame);
  const itaNa = pt('italian_na', frame);
  // Page px -> screen px at the current camera distance.
  const k = (itaNa.x - ita.x) / (2860 - 2372);
  const hi = progress(frame, 238, 14);
  const hiOut = interpolate(frame, [262, 270], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rowW = 760 * k;
  const rowH = 54 * k;
  return (
    <AbsoluteFill>
      <Callout
        anchor={{x: rel.x - 10, y: rel.y}}
        dock={{x: SAFE.left, y: rel.y - 74}}
        labelSide="above"
        at={168}
        until={220}
        tint={color.steam}
        kicker="Pagina Steam · stato"
        title="Uscita da annunciare"
        sub="Wishlist aperta dal 9 ottobre"
        variant="glass"
      />
      {/* "Italiano — Non disponibile" row, outlined on the real table. */}
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: hiOut}}>
        <rect
          x={ita.x - 22 * k}
          y={ita.y - rowH / 2}
          width={rowW}
          height={rowH}
          rx={4}
          fill="rgba(227,38,46,0.10)"
          stroke={color.redline}
          strokeWidth={3}
          strokeDasharray={2 * (rowW + rowH)}
          strokeDashoffset={2 * (rowW + rowH) * (1 - hi)}
        />
      </svg>
      <Callout
        anchor={{x: ita.x - 22 * k, y: ita.y}}
        // The row enters from below the safe area: hold the label inside it.
        dock={{x: SAFE.left, y: Math.min(ita.y - 96, 1420)}}
        labelSide="above"
        at={236}
        until={262}
        tint={color.redline}
        kicker="Localizzazione"
        title="Italiano non supportato"
        sub="Né interfaccia, né audio, né sottotitoli"
        variant="glass"
      />
    </AbsoluteFill>
  );
};

/** Keeps the programme bug legible once the store page fills the frame. */
const PageTopScrim: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [60, 90], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill
      style={{
        opacity: o,
        background: 'linear-gradient(180deg, rgba(7,9,12,0.82) 0px, rgba(7,9,12,0.55) 200px, rgba(7,9,12,0) 360px)',
      }}
    />
  );
};

const Finish: React.FC = () => (
  <AbsoluteFill
    style={{
      background: 'radial-gradient(120% 75% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.30) 100%)',
      pointerEvents: 'none',
    }}
  />
);

export const RedlineDemo: React.FC = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    fontsReady.then(() => continueRender(handle));
  }, [handle]);

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <Sequence from={S1.from} durationInFrames={S1.len} name="S1 heli">
        <Reframe src="s1_heli.mp4" r={R1} />
        <TitleBlock at={52} />
      </Sequence>
      <Sequence from={S2.from} durationInFrames={S2.len} name="S2 combat">
        <Reframe src="s2_combat.mp4" r={R2} />
        <RunnerCallout />
      </Sequence>
      <Sequence from={S3.from} durationInFrames={S3.len} name="S3 Steam page (Blender)">
        <OffthreadVideo src={staticFile('s3_blender.mp4')} muted />
        <PageTopScrim />
        <PageCallouts />
        <SteamEndCard at={264} />
      </Sequence>
      <Finish />
      <ShowBug inAt={6} outAt={S3.from + 250} episode="Nº 01 · Anteprima" />
    </AbsoluteFill>
  );
};

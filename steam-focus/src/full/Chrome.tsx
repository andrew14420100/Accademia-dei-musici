import {AbsoluteFill, getInputProps, interpolate} from 'remotion';
import {progress} from '../components/Type';
import {color, easeOut, font, SAFE, useBaseFrame} from '../design';
import {Lockup} from '../brand/Lockup';
import {EDL} from './edl';
import bugContrast from '../../public/bug_contrast.json';

const BUG_H = 50;

/** Scrim strength behind the lockup per shot (from scripts/bug_contrast.py: bright shots get more). */
const bugScrim = (frame: number) => {
  const s = EDL.shots.find((x) => frame >= x.from && frame < x.from + x.frames);
  return s ? ((bugContrast as Record<string, number>)[s.id] ?? 0.6) : 0.6;
};

export const CHAPTERS: Record<string, {n: string; title: string}> = {
  identity: {n: '01', title: 'Identità'},
  movement: {n: '02', title: 'Movimento'},
  squad: {n: '03', title: 'Squadre'},
  reentry: {n: '04', title: 'Rientro'},
  economy: {n: '05', title: 'Economia'},
  weapons: {n: '06', title: 'Armi e tattica'},
  steam: {n: '07', title: 'Su Steam'},
};

const sectionAt = (frame: number) => {
  for (const [k, [a, b]] of Object.entries(EDL.sections)) if (frame >= a && frame < b) return k;
  return 'outro';
};

/** Programme bug with the running chapter, top-left (below TikTok's top tabs). */
export const Bug: React.FC = () => {
  const frame = useBaseFrame();
  const sec = sectionAt(frame);
  const ch = CHAPTERS[sec];
  const steam = EDL.sections.steam;
  const sig = EDL.signature.from;
  const out = interpolate(frame, [sig - 8, sig], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const chStart = ch ? EDL.sections[sec][0] : 0;
  const chIn = ch ? progress(frame, chStart + 2, 12) : 0;
  const reveal = interpolate(frame, [3, 15], [0, 1], {easing: easeOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const scrim = bugScrim(frame);
  const pageScrim = interpolate(frame, [steam[0] + EDL.s3.bridge - 70, steam[0] + EDL.s3.bridge - 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{opacity: out}}>
      <AbsoluteFill
        style={{
          opacity: pageScrim,
          background: 'linear-gradient(180deg, rgba(11,22,38,0.82) 0px, rgba(11,22,38,0.5) 240px, rgba(11,22,38,0) 400px)',
        }}
      />
      {/* soft local scrim: keeps the lockup readable on bright shots without a panel */}
      <AbsoluteFill
        style={{
          opacity: scrim,
          background: 'radial-gradient(520px 260px at 170px 205px, rgba(11,22,38,0.62), rgba(11,22,38,0) 100%)',
        }}
      />
      <div style={{position: 'absolute', left: SAFE.left, top: SAFE.top}}>
        <div
          style={{
            clipPath: `inset(0 ${(1 - reveal) * 100}% 0 0)`,
            filter: 'drop-shadow(0 2px 10px rgba(0,0,0,0.55))',
            position: 'relative',
          }}
        >
          <Lockup height={BUG_H} />
        </div>
        <div
          style={{
            marginTop: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            fontFamily: font.mono,
            fontWeight: 600,
            fontSize: 20,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: color.dim,
            textShadow: '0 1px 10px rgba(0,0,0,0.7)',
            opacity: ch ? chIn : reveal,
            transform: `translateY(${(1 - (ch ? chIn : 1)) * 8}px)`,
          }}
        >
          <div style={{width: 18, height: 2, backgroundColor: color.steam}} />
          {ch ? `${ch.n} · ${ch.title}` : 'ECC: REDLINE'}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * Chapter plate: swings in on a hinge in perspective, a light band sweeps
 * across it, then it folds away. Short (≈1.4 s) and sits under the bug.
 */
export const ChapterTitle: React.FC<{section: string; hold?: number}> = ({section, hold = 40}) => {
  const frame = useBaseFrame();
  const ch = CHAPTERS[section];
  if (frame > hold + 14) return null;
  const inP = interpolate(frame, [0, 14], [0, 1], {easing: easeOut, extrapolateRight: 'clamp'});
  const outP = interpolate(frame, [hold, hold + 12], [0, 1], {easing: easeOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sweep = interpolate(frame, [6, 30], [-30, 130], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rot = -62 * (1 - inP) + 70 * outP;
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left,
        top: 320,
        perspective: 1100,
        opacity: 1 - outP,
      }}
    >
      <div
        style={{
          transformOrigin: 'left center',
          transform: `rotateY(${rot}deg)`,
          padding: '16px 28px 18px 22px',
          borderLeft: `6px solid ${color.steam}`,
          background: 'linear-gradient(90deg, rgba(11,22,38,0.78), rgba(19,40,63,0.35) 70%, rgba(19,40,63,0))',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div style={{fontFamily: font.mono, fontWeight: 700, fontSize: 22, letterSpacing: '0.18em', color: color.steam}}>
          CAPITOLO {ch.n}
        </div>
        <div
          style={{
            fontFamily: font.display,
            fontWeight: 700,
            fontSize: 96,
            lineHeight: 0.95,
            color: color.paper,
            textTransform: 'uppercase',
            marginTop: 4,
            textShadow: '0 2px 20px rgba(0,0,0,0.5)',
          }}
        >
          {ch.title}
        </div>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: `linear-gradient(105deg, rgba(255,255,255,0) ${sweep - 12}%, rgba(255,255,255,0.22) ${sweep}%, rgba(255,255,255,0) ${sweep + 12}%)`,
            mixBlendMode: 'screen',
          }}
        />
      </div>
    </div>
  );
};

/**
 * Burned-in subtitles inside TikTok's safe area: above the caption band and
 * clear of the right action rail; 2 lines max, high contrast.
 */
/** Shots whose HUD (shop balance) sits on the subtitle line: cues that start
 *  inside them are lifted into the empty band above it (bottom edge, px). */
const RAISED: Record<string, number> = {e_shop: 1290};
const raisedBottom = (from: number) => {
  const s = EDL.shots.find((x) => RAISED[x.id] && from >= x.from && from < x.from + x.frames);
  return s ? RAISED[s.id] : SAFE.bottom;
};

/** Key terms in Steam blue (discreet: same weight and size, colour only). */
const KEY = /(ECC: REDLINE|NetEase Games|NetEase|Galaxy Studio|Steam|free-to-play|quattro|ruolo|scivolat[ae]|rampino|rimbalzi|crediti|400|4\.500|balistica|rinculo|maneggevolezza|ottiche|roaming|movimento|lista dei desideri|italiano)/gi;
const highlight = (text: string) =>
  text.split(KEY).map((part, i) =>
    i % 2 ? (
      <span key={i} style={{color: color.steam}}>
        {part}
      </span>
    ) : (
      part
    ),
  );

export const Subtitles: React.FC = () => {
  const frame = useBaseFrame();
  // `--props='{"noSubs":true}'` renders clean stills (cover); the video always has them.
  if ((getInputProps() as {noSubs?: boolean}).noSubs) return null;
  const cue = EDL.cues.find((c) => frame >= c.from && frame < c.to);
  if (!cue) return null;
  const t = progress(frame, cue.from, 4);
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left + 30,
        width: SAFE.right - SAFE.left - 30,
        bottom: 1920 - raisedBottom(cue.from),
        display: 'flex',
        justifyContent: 'center',
        opacity: t,
        transform: `translateY(${(1 - t) * 8}px)`,
      }}
    >
      <div
        style={{
          fontFamily: font.text,
          fontWeight: 700,
          fontSize: 48,
          lineHeight: 1.18,
          color: '#FFFFFF',
          textAlign: 'center',
          padding: '12px 22px 14px',
          borderRadius: 10,
          backgroundColor: 'rgba(11,22,38,0.6)',
          textShadow: '0 2px 6px rgba(0,0,0,0.6)',
        }}
      >
        {highlight(cue.text)}
      </div>
    </div>
  );
};

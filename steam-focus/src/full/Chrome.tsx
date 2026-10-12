import {AbsoluteFill, interpolate} from 'remotion';
import {MaskLine, progress, Rule} from '../components/Type';
import {color, easeOut, font, SAFE, useBaseFrame} from '../design';
import {EDL} from './edl';

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
  const pageScrim = interpolate(frame, [steam[0] + EDL.s3.bridge - 70, steam[0] + EDL.s3.bridge - 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{opacity: out}}>
      <AbsoluteFill
        style={{
          opacity: pageScrim,
          background: 'linear-gradient(180deg, rgba(7,9,12,0.82) 0px, rgba(7,9,12,0.5) 240px, rgba(7,9,12,0) 400px)',
        }}
      />
      <div style={{position: 'absolute', left: SAFE.left, top: SAFE.top, textShadow: '0 1px 14px rgba(0,0,0,0.5)'}}>
        <MaskLine at={4}>
          <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
            <div style={{width: 14, height: 14, backgroundColor: color.redline, transform: 'rotate(45deg)'}} />
            <div style={{fontFamily: font.display, fontWeight: 700, fontSize: 36, letterSpacing: '0.26em', color: color.paper}}>
              STEAM FOCUS
            </div>
          </div>
        </MaskLine>
        <div style={{marginTop: 10, marginBottom: 10}}>
          <Rule at={8} width={250} thickness={2} />
        </div>
        <div
          style={{
            fontFamily: font.mono,
            fontWeight: 600,
            fontSize: 22,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: color.dim,
            opacity: ch ? chIn : 1,
            transform: `translateY(${(1 - (ch ? chIn : 1)) * 8}px)`,
          }}
        >
          {ch ? `${ch.n} · ${ch.title}` : 'Nº 01 · ECC: REDLINE'}
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
          borderLeft: `6px solid ${color.redline}`,
          background: 'linear-gradient(90deg, rgba(8,10,14,0.72), rgba(8,10,14,0.0))',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div style={{fontFamily: font.mono, fontWeight: 700, fontSize: 24, letterSpacing: '0.18em', color: color.redline}}>
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
export const Subtitles: React.FC = () => {
  const frame = useBaseFrame();
  const cue = EDL.cues.find((c) => frame >= c.from && frame < c.to);
  if (!cue) return null;
  const t = progress(frame, cue.from, 4);
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left + 30,
        width: SAFE.right - SAFE.left - 30,
        bottom: 1920 - SAFE.bottom,
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
          backgroundColor: 'rgba(8,10,14,0.6)',
          textShadow: '0 2px 6px rgba(0,0,0,0.6)',
        }}
      >
        {cue.text}
      </div>
    </div>
  );
};

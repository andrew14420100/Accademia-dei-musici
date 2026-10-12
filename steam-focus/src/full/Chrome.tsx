import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {MaskLine, progress, Rule} from '../components/Type';
import {color, easeOut, font, SAFE} from '../design';
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

/** Programme bug with the running chapter, top-left. */
export const Bug: React.FC = () => {
  const frame = useCurrentFrame();
  const sec = sectionAt(frame);
  const ch = CHAPTERS[sec];
  const steam = EDL.sections.steam;
  // Hidden while the standalone Steam logo is on screen and in the outro.
  const logoFrom = EDL.s3.from + EDL.s3.logoAt;
  const out = interpolate(frame, [logoFrom - 12, logoFrom - 2], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const chStart = ch ? EDL.sections[sec][0] : 0;
  const chIn = ch ? progress(frame, chStart + 2, 12) : 0;
  const pageScrim = interpolate(frame, [steam[0] + 60, steam[0] + 90], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: out}}>
      <AbsoluteFill
        style={{
          opacity: pageScrim,
          background: 'linear-gradient(180deg, rgba(7,9,12,0.82) 0px, rgba(7,9,12,0.55) 200px, rgba(7,9,12,0) 360px)',
        }}
      />
      <div style={{position: 'absolute', left: SAFE.left, top: SAFE.top + 14, textShadow: '0 1px 14px rgba(0,0,0,0.5)'}}>
        <MaskLine at={4}>
          <div style={{fontFamily: font.display, fontWeight: 600, fontSize: 34, letterSpacing: '0.30em', color: color.paper}}>
            STEAM FOCUS
          </div>
        </MaskLine>
        <div style={{marginTop: 10, marginBottom: 10}}>
          <Rule at={8} width={232} thickness={2} />
        </div>
        <div
          style={{
            fontFamily: font.mono,
            fontWeight: 600,
            fontSize: 20,
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

/** Large chapter title set into the picture at the start of a section. */
export const ChapterTitle: React.FC<{section: string; hold?: number}> = ({section, hold = 46}) => {
  const frame = useCurrentFrame();
  const ch = CHAPTERS[section];
  const out = interpolate(frame, [hold, hold + 10], [0, 1], {easing: easeOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (frame > hold + 12) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left,
        top: 300,
        opacity: 1 - out,
        transform: `translateY(${-24 * out}px)`,
        textShadow: '0 2px 24px rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.4)',
      }}
    >
      <MaskLine at={4}>
        <div style={{fontFamily: font.mono, fontWeight: 700, fontSize: 26, letterSpacing: '0.16em', color: color.redline}}>
          CAPITOLO {ch.n}
        </div>
      </MaskLine>
      <MaskLine at={7} len={18}>
        <div
          style={{
            fontFamily: font.display,
            fontWeight: 700,
            fontSize: 138,
            lineHeight: 0.92,
            color: color.paper,
            textTransform: 'uppercase',
            marginTop: 6,
          }}
        >
          {ch.title}
        </div>
      </MaskLine>
    </div>
  );
};

/** Burned-in subtitles: bottom of the safe area, 2 lines max, high contrast. */
export const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = EDL.cues.find((c) => frame >= c.from && frame < c.to);
  if (!cue) return null;
  const t = progress(frame, cue.from, 5);
  return (
    <div
      style={{
        position: 'absolute',
        left: 64,
        right: 64,
        bottom: HEIGHT_BOTTOM,
        display: 'flex',
        justifyContent: 'center',
        opacity: t,
        transform: `translateY(${(1 - t) * 10}px)`,
      }}
    >
      <div
        style={{
          fontFamily: font.text,
          fontWeight: 700,
          fontSize: 50,
          lineHeight: 1.18,
          color: '#FFFFFF',
          textAlign: 'center',
          padding: '12px 22px 14px',
          borderRadius: 10,
          backgroundColor: 'rgba(8,10,14,0.58)',
          textShadow: '0 2px 6px rgba(0,0,0,0.6)',
          maxWidth: 900,
        }}
      >
        {cue.text}
      </div>
    </div>
  );
};

// Subtitle block sits above the band social apps cover with their UI.
const HEIGHT_BOTTOM = 1920 - 1530;

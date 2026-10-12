import {AbsoluteFill, Freeze, Img, interpolate, OffthreadVideo, staticFile} from 'remotion';
import {Kicker} from '../components/Type';
import {color, easeOut, font, SAFE, useBaseFrame, useFrameScale} from '../design';
import {EDL, wordAt} from './edl';

// Real store-page crops, captured at 3x density (scripts/capture_steam_details.mjs).
const CROPS = {
  steambar: {w: 1960, h: 195},
  title: {w: 1740, h: 200},
  facts: {w: 1160, h: 650},
  wishlist: {w: 2340, h: 420},
  arrivo: {w: 1100, h: 190},
  button: {w: 740, h: 175},
  italian: {w: 2340, h: 276},
  languages: {w: 1170, h: 560},
} as const;
type CropName = keyof typeof CROPS;
type Box = [number, number, number, number]; // x, y, w, h in crop pixels

/** One authentic crop, with highlight boxes drawn on its own pixels. */
const Crop: React.FC<{name: CropName; width: number; marks?: Array<{box: Box; at: number; tint: string}>}> = ({name, width, marks = []}) => {
  const frame = useBaseFrame();
  const c = CROPS[name];
  const k = width / c.w;
  return (
    <div style={{position: 'relative', width, height: c.h * k, borderRadius: 8, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.14)'}}>
      <Img src={staticFile(`steam/crop_${name}.png`)} style={{width, height: c.h * k, display: 'block'}} />
      {marks.map((m, i) => {
        const p = interpolate(frame, [m.at, m.at + 10], [0, 1], {easing: easeOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const [x, y, w, h] = m.box;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x * k - 6,
              top: y * k - 4,
              width: (w * k + 12) * p,
              height: h * k + 8,
              border: `3px solid ${m.tint}`,
              borderRadius: 6,
              backgroundColor: `${m.tint}22`,
              opacity: p,
            }}
          />
        );
      })}
    </div>
  );
};

/** A group of crops that tips in from depth, holds, then folds away. */
const CardGroup: React.FC<{at: number; until: number; top: number; children: React.ReactNode; kicker: string}> = ({
  at,
  until,
  top,
  children,
  kicker,
}) => {
  const frame = useBaseFrame();
  if (frame < at - 2 || frame > until + 14) return null;
  const inP = interpolate(frame, [at, at + 14], [0, 1], {easing: easeOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const outP = interpolate(frame, [until, until + 12], [0, 1], {easing: easeOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sweep = interpolate(frame, [at + 4, at + 34], [-40, 140], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: SAFE.left, width: SAFE.right - SAFE.left, top, perspective: 1600}}>
      <div
        style={{
          transformOrigin: '50% 0%',
          transform: `translateY(${(1 - inP) * 140 - outP * 120}px) rotateX(${-32 * (1 - inP) + 26 * outP}deg) scale(${0.92 + 0.08 * inP})`,
          opacity: inP * (1 - outP),
          filter: `drop-shadow(0 40px 60px rgba(0,0,0,0.6))`,
        }}
      >
        <Kicker tint={color.steam} style={{fontSize: 24, marginBottom: 14, textShadow: '0 2px 12px rgba(0,0,0,0.7)'}}>
          {kicker}
        </Kicker>
        <div style={{position: 'relative', display: 'flex', flexDirection: 'column', gap: 18, alignItems: 'flex-start'}}>
          {children}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              pointerEvents: 'none',
              background: `linear-gradient(110deg, rgba(255,255,255,0) ${sweep - 14}%, rgba(255,255,255,0.18) ${sweep}%, rgba(255,255,255,0) ${sweep + 14}%)`,
              mixBlendMode: 'screen',
            }}
          />
        </div>
      </div>
    </div>
  );
};

const Caption: React.FC<{at: number; text: string; tint: string}> = ({at, text, tint}) => {
  const frame = useBaseFrame();
  const p = interpolate(frame, [at, at + 10], [0, 1], {easing: easeOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div
      style={{
        fontFamily: font.display,
        fontWeight: 700,
        fontSize: 64,
        lineHeight: 1,
        color: color.paper,
        textTransform: 'uppercase',
        borderLeft: `6px solid ${tint}`,
        paddingLeft: 18,
        opacity: p,
        transform: `translateX(${(1 - p) * -24}px)`,
        textShadow: '0 2px 18px rgba(0,0,0,0.7)',
      }}
    >
      {text}
    </div>
  );
};

/**
 * Chapter 07. The approved Blender hero shot is the bridge (gameplay plate
 * lands inside the real store page); then the page recedes into depth and
 * legible crops of the real page carry each fact as it is spoken.
 */
export const SteamBlock: React.FC = () => {
  const frame = useBaseFrame();
  const k = useFrameScale();
  const B = EDL.s3.bridge;
  const from = EDL.s3.from;
  const tA = EDL.lines.find((l) => l.id === 'st1')!.from - from - 9;
  const tArr = wordAt('st1', 'arrivo') - from;
  const tB = wordAt('st2', 'lista') - from - 4;
  const tOpen = wordAt('st2', 'aperta') - from;
  const tC = wordAt('st2', 'italiano') - from - 6;
  const tLang = wordAt('st2', 'lingue') - from;
  const end = EDL.sections.steam[1] - from;

  // Page recedes into a blurred, darkened backdrop after the plate lands.
  const back = interpolate(frame, [B - 16, B + 6], [0, 1], {easing: easeOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const drift = interpolate(frame, [B, end], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const s3src = staticFile(k === 2 ? 's3_blender_60.mp4' : 's3_blender.mp4');
  return (
    <AbsoluteFill style={{backgroundColor: '#000', overflow: 'hidden'}}>
      <AbsoluteFill
        style={{
          transform: `scale(${1 + 0.08 * back + 0.04 * drift}) translateY(${-30 * drift}px)`,
          filter: back > 0.01 ? `blur(${18 * back}px) brightness(${1 - 0.5 * back})` : undefined,
        }}
      >
        <Freeze frame={B * k} active={(f) => f >= B * k}>
          <OffthreadVideo src={s3src} muted />
        </Freeze>
      </AbsoluteFill>

      <CardGroup at={tA} until={tB - 6} top={330} kicker="Pagina Steam ufficiale · 12/10/2026">
        <Crop name="steambar" width={760} />
        <Crop name="title" width={760} />
        <Crop
          name="facts"
          width={860}
          marks={[
            {box: [440, 425, 160, 66], at: tArr, tint: color.steam},
            {box: [440, 522, 300, 110], at: tArr + 14, tint: color.steam},
          ]}
        />
        <Caption at={tArr + 4} text="Uscita: da annunciare" tint={color.steam} />
      </CardGroup>

      <CardGroup at={tB} until={tC - 6} top={470} kicker="Pagina Steam · stato">
        <Crop name="arrivo" width={860} marks={[{box: [44, 100, 290, 80], at: tB + 8, tint: color.steam}]} />
        <Crop name="button" width={640} marks={[{box: [50, 40, 660, 118], at: tOpen, tint: color.steam}]} />
        <Caption at={tOpen} text="Wishlist già aperta" tint={color.steam} />
      </CardGroup>

      <CardGroup at={tC} until={end - 4} top={360} kicker="Pagina Steam · lingue">
        <Crop
          name="languages"
          width={876}
          marks={[
            {box: [18, 176, 1110, 58], at: tC + 8, tint: color.redline},
            {box: [24, 496, 586, 58], at: tLang, tint: color.steam},
          ]}
        />
        <Caption at={tC + 10} text="Italiano: non ancora" tint={color.redline} />
      </CardGroup>
    </AbsoluteFill>
  );
};


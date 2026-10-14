import {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, Easing, Img, interpolate, staticFile} from 'remotion';
import {Lockup} from '../brand/Lockup';
import {MaskLine, progress, Rule} from '../components/Type';
import {color, easeInOut, easeOut, font, fontsReady, SAFE, useBaseFrame, useFrameScale} from '../design';

/**
 * STEAM FOCUS / ECC: REDLINE banner. Built in vector (approved lockup SVG + text), so it has
 * real transparency around the card and renders natively at any resolution. A translucent
 * night-blue card with a hairline Steam-blue border carries the text over gameplay; no glow,
 * no neon. Used as the opening title card (overlay on h_heli) and exported as a transparent PNG
 * (composition BannerPNG).
 */
export const BANNER_W = 876;

const chips = ['Free-to-play', 'PC', 'In arrivo su Steam'];

export const BannerCard: React.FC<{at?: number; out?: number; solid?: boolean}> = ({at = -200, out, solid = false}) => {
  const a = solid ? 1 : 0.9;
  const frame = useBaseFrame();
  const enter = progress(frame, at, 16);
  const exit = out === undefined ? 0 : interpolate(frame, [out - 8, out], [0, 1], {easing: easeInOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div
      style={{
        width: BANNER_W,
        boxSizing: 'border-box',
        padding: '30px 36px 32px',
        borderRadius: 20,
        background: `linear-gradient(135deg, rgba(27,59,86,${a - 0.02}) 0%, rgba(19,40,63,${a}) 45%, rgba(11,22,38,${Math.min(1, a + 0.02)}) 100%)`,
        border: '1.5px solid rgba(102,192,244,0.55)',
        boxShadow: '0 18px 50px rgba(0,0,0,0.42), inset 0 1px 0 rgba(243,245,247,0.12)',
        opacity: enter * (1 - exit),
        transform: `translateY(${(1 - enter) * 24 - exit * 12}px) scale(${0.97 + enter * 0.03})`,
        transformOrigin: 'left top',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* fine diagonal hatch on the right, Steam blue at low opacity (texture, not decoration) */}
      <div
        style={{
          position: 'absolute',
          right: 0,
          top: 0,
          bottom: 0,
          width: 300,
          backgroundImage: 'repeating-linear-gradient(120deg, rgba(102,192,244,0.07) 0 2px, transparent 2px 14px)',
          WebkitMaskImage: 'linear-gradient(90deg, transparent, #000)',
          maskImage: 'linear-gradient(90deg, transparent, #000)',
        }}
      />
      <MaskLine at={at + 2}>
        <Lockup height={56} />
      </MaskLine>
      <div style={{display: 'flex', gap: 0, marginTop: 16}}>
        <Rule at={at + 5} width={70} thickness={4} color={color.redline} />
        <Rule at={at + 7} width={BANNER_W - 72 - 70} thickness={2} color="rgba(102,192,244,0.6)" />
      </div>
      <MaskLine at={at + 6} len={18}>
        <div
          style={{
            fontFamily: font.display,
            fontWeight: 700,
            fontSize: 158,
            lineHeight: 0.9,
            letterSpacing: '0.005em',
            whiteSpace: 'nowrap',
            color: '#FFFFFF',
            marginTop: 14,
            textShadow: '0 4px 18px rgba(0,0,0,0.35)',
          }}
        >
          ECC: REDLINE
        </div>
      </MaskLine>
      <MaskLine at={at + 10}>
        <div style={{fontFamily: font.text, fontWeight: 650, fontSize: 33, lineHeight: 1.15, color: color.paper, marginTop: 10}}>
          Sparatutto competitivo con movimento acrobatico
        </div>
      </MaskLine>
      <MaskLine at={at + 12}>
        <div style={{fontFamily: font.mono, fontWeight: 600, fontSize: 19, letterSpacing: '0.2em', color: color.steam, marginTop: 14, textTransform: 'uppercase'}}>
          NetEase Games · Galaxy Studio
        </div>
      </MaskLine>
      <div style={{display: 'flex', gap: 12, marginTop: 20}}>
        {chips.map((c, i) => {
          const t = progress(frame, at + 14 + i * 2, 12);
          return (
            <div
              key={c}
              style={{
                opacity: t,
                transform: `translateY(${(1 - t) * 10}px)`,
                fontFamily: font.text,
                fontWeight: 800,
                fontSize: 23,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                color: '#FFFFFF',
                padding: '9px 18px',
                borderRadius: 999,
                border: `2px solid ${color.steam}`,
                backgroundColor: 'rgba(102,192,244,0.12)',
              }}
            >
              {c}
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** In-video placement: upper third, inside the TikTok safe area, over sky/fog of the opening shot. */
export const BannerOverlay: React.FC<{at: number; out: number}> = ({at, out}) => (
  <div style={{position: 'absolute', left: (1080 - BANNER_W) / 2 - 6, top: SAFE.top + 120}}>
    <BannerCard at={at} out={out} />
  </div>
);

/** Transparent PNG export: 1000 x 640 layout units (cropped to the card + shadow afterwards), rendered at 3.84x (3840 px wide). */
export const BANNER_PNG = {w: 1000, h: 640, zoom: 3.84};
export const BannerPNG: React.FC = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    fontsReady.then(() => continueRender(handle));
  }, [handle]);
  return (
    <AbsoluteFill>
      <div style={{width: BANNER_PNG.w, height: BANNER_PNG.h, zoom: BANNER_PNG.zoom, position: 'relative'}}>
        <div style={{position: 'absolute', left: (BANNER_PNG.w - BANNER_W) / 2, top: 40}}>
          <BannerCard solid />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/**
 * The approved banner (ChatGPT artwork supplied by the owner), cut out with
 * scripts/banner_cutout.py: transparent outside the rounded frame, unchanged inside.
 * Source 1976x642 px, shown 745 units wide (1490 px in the 4K master: downscaled, never enlarged),
 * i.e. 15% smaller than the first preview, centred inside the TikTok safe area.
 *
 * Motion (base frames, 30 fps grid, rendered natively at 60):
 *   entry  0 -> 24  3D fly-in from depth (z -1400, yaw -42, pitch 16) with a diagonal mask
 *                   reveal, leading light streaks and a light sweep; visually settles on beat 1 (0.47 s, 128 BPM)
 *   hold  24 -> 222 slow camera orbit (yaw -3 -> +3, pitch 1.5 -> -1.5) and float: depth and
 *                   parallax against its own shadow plane
 *   exit 222 -> 253 accelerates past the camera (z +900, pitch -22, up 420) behind a closing
 *                   slanted mask, ending on beat 18 (8.44 s) as the Identita chapter swings in
 * Motion blur: 7 time samples across the frame interval while it moves fast (averaged).
 */
export const BANNER_T = {in0: 0, land: 24, out0: 222, end: 253};
const BW = 745;
const BH = (BW * 642) / 1976;
const BLEFT = (1080 - BW) / 2;
const BTOP = 200;
const easeLand = Easing.bezier(0.33, 0.9, 0.25, 1);
const easeAway = Easing.bezier(0.45, 0, 0.75, 0.1);
const cl = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

type Pose = {x: number; y: number; z: number; rx: number; ry: number; o: number; reveal: number; close: number};
const pose = (f: number): Pose => {
  const p = interpolate(f, [BANNER_T.in0, BANNER_T.land], [0, 1], {...cl, easing: easeLand});
  const u = interpolate(f, [BANNER_T.land, BANNER_T.out0], [0, 1], cl);
  const e = interpolate(f, [BANNER_T.out0, BANNER_T.end], [0, 1], {...cl, easing: easeAway});
  return {
    x: 260 * (1 - p),
    y: 60 * (1 - p) + Math.sin(f / 38) * 2.5 * p - 420 * e,
    z: -1400 * (1 - p) + 24 * u + 900 * e,
    rx: 16 * (1 - p) + (1.5 - 3 * u) * p - 22 * e,
    ry: -42 * (1 - p) + (-3 + 6 * u) * p + 8 * e,
    o: interpolate(p, [0, 0.35], [0, 1], cl) * interpolate(e, [0.5, 1], [1, 0], cl),
    reveal: interpolate(f, [BANNER_T.in0 + 1, BANNER_T.land - 3], [0, 1], {...cl, easing: easeOut}),
    close: e,
  };
};
const tf = (q: Pose, dz = 0) =>
  `translate3d(${q.x}px, ${q.y}px, ${q.z + dz}px) rotateX(${q.rx}deg) rotateY(${q.ry}deg)`;

/** 0..1: how much of the banner is on screen (the small corner lockup hides meanwhile). */
export const bannerPresence = (f: number) =>
  interpolate(f, [BANNER_T.in0, BANNER_T.in0 + 6, BANNER_T.end - 6, BANNER_T.end], [0, 1, 1, 0], cl);

const BannerFace: React.FC<{q: Pose; sweep: number}> = ({q, sweep}) => {
  // entry: diagonal reveal left -> right; exit: slanted shutter closing from the bottom
  const r = q.reveal * 135;
  const c = q.close * 125;
  const clip = `polygon(0% ${c}%, ${r}% ${Math.max(0, c - 25)}%, ${r - 35}% 100%, 0% 100%)`;
  return (
    <div style={{position: 'absolute', inset: 0, clipPath: q.close > 0 ? `polygon(0% 0%, 100% 0%, 100% ${100 - c}%, 0% ${100 - c + 25}%)` : clip}}>
      <Img src={staticFile('banner_steam_focus.png')} style={{width: BW, height: BH, display: 'block'}} />
      {sweep > 0 && sweep < 1 ? (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            WebkitMaskImage: `url(${staticFile('banner_steam_focus.png')})`,
            WebkitMaskSize: '100% 100%',
            maskImage: `url(${staticFile('banner_steam_focus.png')})`,
            maskSize: '100% 100%',
            background: `linear-gradient(105deg, rgba(255,255,255,0) ${sweep * 160 - 40}%, rgba(200,235,255,0.42) ${sweep * 160 - 25}%, rgba(255,255,255,0) ${sweep * 160 - 10}%)`,
          }}
        />
      ) : null}
    </div>
  );
};

export const ApprovedBanner: React.FC = () => {
  const frame = useBaseFrame();
  const k = useFrameScale();
  const q = pose(frame);
  if (q.o <= 0.001) return null;
  const moving = frame < BANNER_T.land + 2 || frame > BANNER_T.out0;
  // shutter-angle style motion blur: samples spread over the last 0.8 composition frame
  const N = moving ? 7 : 1;
  const span = (0.8 / k);
  const sweep = interpolate(frame, [BANNER_T.land - 6, BANNER_T.land + 16], [0, 1], cl);
  const streak = interpolate(frame, [BANNER_T.in0, BANNER_T.land - 2], [0, 1], {...cl, easing: easeOut});
  const ox = 1080 / 2 + (frame - BANNER_T.land) * 0.15;
  return (
    <div style={{position: 'absolute', inset: 0, perspective: 1300, perspectiveOrigin: `${ox}px ${BTOP + BH / 2}px`, pointerEvents: 'none'}}>
      <div style={{position: 'absolute', left: BLEFT, top: BTOP, width: BW, height: BH, opacity: q.o}}>
        {/* shadow plane behind the banner: parallax/depth cue and readability over bright fog */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            transform: `${tf(q, -90)} translateY(16px)`,
            borderRadius: 26,
            backgroundColor: 'rgba(6,14,28,0.42)',
            filter: 'blur(26px)',
          }}
        />
        {Array.from({length: N}).map((_, i) => {
          const qi = pose(frame - (span * i) / Math.max(1, N - 1));
          return (
            <div key={i} style={{position: 'absolute', inset: 0, transform: tf(qi), opacity: 1 / (N - i), backfaceVisibility: 'hidden'}}>
              <BannerFace q={qi} sweep={sweep} />
            </div>
          );
        })}
      </div>
      {/* entry light streaks (Steam blue), leading the banner in along its top and bottom edges */}
      {streak > 0 && streak < 1
        ? [BTOP - 6, BTOP + BH + 4].map((y, i) => (
            <div
              key={y}
              style={{
                position: 'absolute',
                top: y,
                left: BLEFT - 220 + streak * (BW + 420) * (i ? 0.92 : 1),
                width: 260,
                height: 2,
                opacity: Math.sin(streak * Math.PI) * 0.85,
                background: 'linear-gradient(90deg, rgba(102,192,244,0), rgba(160,220,255,0.95), rgba(102,192,244,0))',
              }}
            />
          ))
        : null}
    </div>
  );
};

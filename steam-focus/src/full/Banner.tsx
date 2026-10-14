import {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, Img, interpolate, staticFile} from 'remotion';
import {Lockup} from '../brand/Lockup';
import {MaskLine, progress, Rule} from '../components/Type';
import {color, easeInOut, font, fontsReady, SAFE, useBaseFrame} from '../design';

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
 * Source 1976x642 px; shown 876 units wide (1752 px in the 4K master: downscaled, never enlarged).
 * Entry: rises 18 px, settles from 96% scale and reveals left to right; exit: short fade.
 * No drop shadow (it would read as a dark halo around the frame).
 */
export const APPROVED_BANNER = {w: 1976, h: 642, top: 262};
export const ApprovedBanner: React.FC<{at: number; out: number}> = ({at, out}) => {
  const frame = useBaseFrame();
  const t = progress(frame, at, 18);
  const wipe = progress(frame, at, 22);
  const exit = interpolate(frame, [out - 10, out], [0, 1], {easing: easeInOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const w = SAFE.right - SAFE.left;
  const h = (w * APPROVED_BANNER.h) / APPROVED_BANNER.w;
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left,
        top: APPROVED_BANNER.top,
        width: w,
        height: h,
        opacity: Math.min(1, t * 1.4) * (1 - exit),
        transform: `translateY(${(1 - t) * 18 - exit * 6}px) scale(${0.96 + 0.04 * t + 0.015 * exit})`,
        clipPath: `inset(0 ${(1 - wipe) * 100}% 0 0 round 22px)`,
      }}
    >
      <Img src={staticFile('banner_steam_focus.png')} style={{width: w, height: h, display: 'block'}} />
    </div>
  );
};

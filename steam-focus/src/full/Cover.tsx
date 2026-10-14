import {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, Img, staticFile} from 'remotion';
import {Lockup, LOCKUP_RATIO} from '../brand/Lockup';
import {color, font, fontsReady, HEIGHT, SAFE, WIDTH} from '../design';

/**
 * V4 cover: a composed frame, not a still from the edit. Authentic gameplay (grapple onto a
 * rooftop, official trailer) under a night-blue grade, the approved STEAM FOCUS lockup,
 * title, tagline and three verified facts as chips. Laid out in 1080x1920 units and
 * rendered at 2160x3840 through zoom: 2 (vectors and text rasterize natively in 4K).
 */
const CoverLayout: React.FC = () => {
  const chips = ['Free-to-play', 'PC', 'In arrivo su Steam'];
  return (
    <AbsoluteFill style={{backgroundColor: color.ink}}>
      <Img src={staticFile('cover_bg.png')} style={{width: WIDTH, height: HEIGHT, objectFit: 'cover', transform: 'translateY(-430px)', filter: 'contrast(1.06) saturate(1.05)'}} />
      {/* grade: night blue at the top (lockup) and bottom (title), gameplay clear in the middle */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, rgba(11,22,38,0.78) 0%, rgba(11,22,38,0.15) 22%, rgba(11,22,38,0) 40%, rgba(11,22,38,0.25) 55%, rgba(11,22,38,0.9) 70%, ${color.ink} 76%)`,
        }}
      />
      <div style={{position: 'absolute', left: SAFE.left, top: SAFE.top, filter: 'drop-shadow(0 2px 10px rgba(0,0,0,0.5))'}}>
        <Lockup height={58} />
      </div>
      <div style={{position: 'absolute', left: SAFE.left, top: 1250, width: SAFE.right - SAFE.left}}>
        <div style={{fontFamily: font.mono, fontWeight: 700, fontSize: 24, letterSpacing: '0.16em', color: color.steam, textTransform: 'uppercase'}}>
          NetEase Games · Galaxy Studio
        </div>
        <div
          style={{
            fontFamily: font.display,
            fontWeight: 700,
            fontSize: 158,
            whiteSpace: 'nowrap',
            lineHeight: 0.9,
            color: color.paper,
            marginTop: 10,
            textShadow: '0 6px 40px rgba(11,22,38,0.8)',
          }}
        >
          ECC: REDLINE
        </div>
        <div style={{width: 140, height: 6, backgroundColor: color.redline, marginTop: 20}} />
        <div style={{fontFamily: font.text, fontWeight: 600, fontSize: 46, lineHeight: 1.18, color: color.paper, marginTop: 22, maxWidth: 820}}>
          Sparatutto competitivo con movimento acrobatico
        </div>
        <div style={{display: 'flex', gap: 14, marginTop: 30, flexWrap: 'wrap'}}>
          {chips.map((c) => (
            <div
              key={c}
              style={{
                fontFamily: font.mono,
                fontWeight: 600,
                fontSize: 22,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                color: color.paper,
                padding: '10px 16px',
                border: `2px solid ${color.steam}`,
                borderRadius: 6,
                backgroundColor: 'rgba(19,40,63,0.6)',
              }}
            >
              {c}
            </div>
          ))}
        </div>
        <div style={{fontFamily: font.mono, fontSize: 15, letterSpacing: '0.08em', color: 'rgba(243,245,247,0.6)', textTransform: 'uppercase', marginTop: 34}}>
          Immagini: trailer ufficiale · format indipendente, non affiliato a Valve o NetEase
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const CoverV4: React.FC = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    fontsReady.then(() => continueRender(handle));
  }, [handle]);
  return (
    <AbsoluteFill style={{backgroundColor: color.ink}}>
      <div style={{width: WIDTH, height: HEIGHT, zoom: 2, overflow: 'hidden', position: 'relative'}}>
        <CoverLayout />
      </div>
    </AbsoluteFill>
  );
};

export const COVER_RATIO = LOCKUP_RATIO;

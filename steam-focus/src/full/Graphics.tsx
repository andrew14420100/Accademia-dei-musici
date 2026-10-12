import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Kicker, MaskLine, progress} from '../components/Type';
import {color, easeOut, font, HEIGHT, SAFE, WIDTH} from '../design';

const shadow = '0 2px 18px rgba(0,0,0,0.65), 0 0 2px rgba(0,0,0,0.45)';

/** Stack of data facts that appear on the words that say them. */
export const DataStack: React.FC<{
  top: number;
  items: Array<{at: number; k: string; v: string; tint: string}>;
  until: number;
}> = ({top, items, until}) => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [until, until + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: SAFE.left, top, opacity: out, textShadow: shadow}}>
      {items.map((it) => {
        const p = progress(frame, it.at, 12);
        return (
          <div key={it.k} style={{display: 'flex', alignItems: 'stretch', marginBottom: 18, opacity: p}}>
            <div style={{width: 5, backgroundColor: it.tint, transform: `scaleY(${p})`, transformOrigin: 'top', marginRight: 18}} />
            <div style={{transform: `translateX(${(1 - p) * -18}px)`}}>
              <Kicker tint={it.tint} style={{fontSize: 22}}>
                {it.k}
              </Kicker>
              <div style={{fontFamily: font.display, fontWeight: 700, fontSize: 66, lineHeight: 1, color: color.paper, textTransform: 'uppercase'}}>
                {it.v}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

/** Sprint → slide → aim → fire: each step lights on its spoken word. */
export const Chain: React.FC<{steps: Array<{at: number; label: string}>; top: number; until: number}> = ({steps, top, until}) => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [until, until + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const appear = progress(frame, steps[0].at - 6, 10);
  return (
    <div style={{position: 'absolute', left: SAFE.left, right: WIDTH - SAFE.right, top, opacity: out * appear}}>
      <Kicker tint={color.redline} style={{marginBottom: 14, textShadow: shadow}}>
        Catena di movimento
      </Kicker>
      <div style={{display: 'flex', gap: 10}}>
        {steps.map((s, i) => {
          const on = progress(frame, s.at, 8);
          return (
            <div key={s.label} style={{flex: 1}}>
              <div style={{height: 6, backgroundColor: 'rgba(255,255,255,0.25)', borderRadius: 3, overflow: 'hidden'}}>
                <div style={{height: '100%', width: `${on * 100}%`, backgroundColor: i === steps.length - 1 ? color.redline : color.paper}} />
              </div>
              <div
                style={{
                  marginTop: 12,
                  fontFamily: font.display,
                  fontWeight: 700,
                  fontSize: 46,
                  textTransform: 'uppercase',
                  color: color.paper,
                  opacity: 0.35 + 0.65 * on,
                  textShadow: shadow,
                }}
              >
                {s.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** Three squad roles, introduced on the words that describe them. */
export const Roles: React.FC<{roles: Array<{at: number; k: string; v: string}>; top: number; until: number}> = ({roles, top, until}) => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [until, until + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: SAFE.left, right: WIDTH - SAFE.right, top, opacity: out, display: 'flex', gap: 16}}>
      {roles.map((r) => {
        const p = progress(frame, r.at, 12);
        return (
          <div
            key={r.k}
            style={{
              flex: 1,
              padding: '16px 18px 18px',
              borderTop: `4px solid ${color.redline}`,
              background: 'linear-gradient(180deg, rgba(8,10,14,0.62), rgba(8,10,14,0.0))',
              opacity: p,
              transform: `perspective(900px) rotateX(${(1 - p) * 35}deg) translateY(${(1 - p) * 20}px)`,
              transformOrigin: 'top',
            }}
          >
            <Kicker tint={color.redline} style={{fontSize: 20}}>
              {r.k}
            </Kicker>
            <div style={{fontFamily: font.display, fontWeight: 700, fontSize: 44, lineHeight: 1, color: color.paper, marginTop: 6, textShadow: shadow}}>
              {r.v}
            </div>
          </div>
        );
      })}
    </div>
  );
};

/**
 * Illustrative shrinking safe zone over the official aerial map shot.
 * Labelled as a diagram: the real zone position is not shown in the footage.
 */
export const SafeZone: React.FC<{at: number; until: number; cx: number; cy: number}> = ({at, until, cx, cy}) => {
  const frame = useCurrentFrame();
  const p = progress(frame, at, 14);
  const shrink = interpolate(frame, [at + 10, until], [0, 1], {easing: easeOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const out = interpolate(frame, [until, until + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const r0 = 470;
  const r = r0 - 250 * shrink;
  return (
    <AbsoluteFill style={{opacity: p * out}}>
      <svg width={WIDTH} height={HEIGHT} style={{position: 'absolute', inset: 0}}>
        <defs>
          <mask id="zone">
            <rect width={WIDTH} height={HEIGHT} fill="white" />
            <circle cx={cx} cy={cy} r={r} fill="black" />
          </mask>
        </defs>
        <rect width={WIDTH} height={HEIGHT} fill="rgba(227,38,46,0.22)" mask="url(#zone)" />
        <circle cx={cx} cy={cy} r={r0} fill="none" stroke="rgba(255,255,255,0.35)" strokeWidth={2} strokeDasharray="10 12" />
        <circle cx={cx} cy={cy} r={r} fill="none" stroke={color.paper} strokeWidth={4} />
      </svg>
      <div style={{position: 'absolute', left: SAFE.left, top: cy - r0 - 120, textShadow: shadow}}>
        <Kicker tint={color.redline}>Schema illustrativo</Kicker>
        <div style={{fontFamily: font.display, fontWeight: 700, fontSize: 64, color: color.paper, textTransform: 'uppercase'}}>
          La zona sicura si stringe
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Italian translation tag pinned to a static in-game UI element. */
export const UiTag: React.FC<{x: number; y: number; at: number; until: number; label: string; value?: string; tint?: string; side?: 'left' | 'right'}> = ({
  x,
  y,
  at,
  until,
  label,
  value,
  tint = color.redline,
  side = 'right',
}) => {
  const frame = useCurrentFrame();
  if (frame < at || frame > until + 10) return null;
  const p = progress(frame, at, 10);
  const out = interpolate(frame, [until, until + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const pulse = interpolate(frame - at, [0, 18], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: out}}>
      <svg width={WIDTH} height={HEIGHT} style={{position: 'absolute', inset: 0}}>
        <circle cx={x} cy={y} r={7 * p} fill={tint} />
        <circle cx={x} cy={y} r={16 * p} fill="none" stroke={color.paper} strokeWidth={2} />
        <circle cx={x} cy={y} r={16 + 26 * pulse} fill="none" stroke={tint} strokeWidth={2} strokeOpacity={1 - pulse} />
      </svg>
      <div
        style={{
          position: 'absolute',
          top: y - 34,
          ...(side === 'right' ? {left: x + 28} : {right: WIDTH - x + 28}),
          backgroundColor: color.glass,
          borderLeft: `4px solid ${tint}`,
          padding: '10px 16px 12px',
          borderRadius: 4,
          clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`,
          whiteSpace: 'nowrap',
        }}
      >
        <Kicker tint={tint} style={{fontSize: 20}}>
          {label}
        </Kicker>
        {value ? (
          <div style={{fontFamily: font.display, fontWeight: 700, fontSize: 48, lineHeight: 1, color: color.paper, marginTop: 4}}>{value}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Short honest note on a claim the footage does not show. */
export const Note: React.FC<{at: number; until: number; kicker: string; title: string; sub: string; top: number}> = ({at, until, kicker, title, sub, top}) => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [until, until + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (frame < at) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: SAFE.left,
        top,
        maxWidth: 860,
        opacity: out,
        backgroundColor: color.glass,
        borderLeft: `4px solid ${color.steam}`,
        padding: '18px 24px 20px',
        borderRadius: 4,
        clipPath: `inset(0 ${(1 - progress(frame, at, 12)) * 100}% 0 0)`,
      }}
    >
      <MaskLine at={at + 4}>
        <Kicker tint={color.steam}>{kicker}</Kicker>
      </MaskLine>
      <MaskLine at={at + 6}>
        <div style={{fontFamily: font.display, fontWeight: 700, fontSize: 58, lineHeight: 1, color: color.paper, marginTop: 6, textTransform: 'uppercase'}}>
          {title}
        </div>
      </MaskLine>
      <MaskLine at={at + 9}>
        <div style={{fontFamily: font.text, fontWeight: 500, fontSize: 28, color: color.dim, marginTop: 8}}>{sub}</div>
      </MaskLine>
    </div>
  );
};

/** Programme sign-off: independent STEAM FOCUS branding, no third-party logos. */
export const Outro: React.FC<{questionAt: number}> = ({questionAt}) => {
  const frame = useCurrentFrame();
  const dim = interpolate(frame, [0, 14], [0, 0.72], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{backgroundColor: color.ink, opacity: dim}} />
      <div style={{position: 'absolute', left: SAFE.left, right: WIDTH - SAFE.right, top: 520}}>
        <MaskLine at={6} len={18}>
          <div style={{fontFamily: font.display, fontWeight: 700, fontSize: 150, lineHeight: 0.9, letterSpacing: '0.02em', color: color.paper}}>
            STEAM
          </div>
        </MaskLine>
        <MaskLine at={9} len={18}>
          <div style={{fontFamily: font.display, fontWeight: 700, fontSize: 150, lineHeight: 0.9, letterSpacing: '0.02em', color: color.redline}}>
            FOCUS
          </div>
        </MaskLine>
        <div style={{height: 34}} />
        <MaskLine at={questionAt}>
          <div style={{fontFamily: font.text, fontWeight: 700, fontSize: 48, lineHeight: 1.18, color: color.paper, maxWidth: 880}}>
            Il movimento basterà a distinguerlo dagli altri tattici?
          </div>
        </MaskLine>
        <div style={{height: 26}} />
        <MaskLine at={questionAt + 6}>
          <Kicker tint={color.dim} style={{fontSize: 23, lineHeight: 1.5, letterSpacing: '0.08em'}}>
            Format editoriale indipendente · non affiliato a Valve o NetEase
          </Kicker>
        </MaskLine>
        <MaskLine at={questionAt + 9}>
          <Kicker tint={color.dim} style={{fontSize: 23, lineHeight: 1.5, letterSpacing: '0.08em'}}>
            Immagini: trailer ufficiali e pagina Steam di ECC: REDLINE
          </Kicker>
        </MaskLine>
        <MaskLine at={questionAt + 12}>
          <Kicker tint={color.dim} style={{fontSize: 23, lineHeight: 1.5, letterSpacing: '0.08em'}}>
            Voce sintetica (Kokoro TTS)
          </Kicker>
        </MaskLine>
      </div>
    </AbsoluteFill>
  );
};

import {AbsoluteFill, Freeze, interpolate, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import anchors from '../../public/s3_anchors.json';
import {Callout} from '../components/Callout';
import {SteamEndCard} from '../components/SteamEndCard';
import {progress} from '../components/Type';
import {color, HEIGHT, SAFE, WIDTH} from '../design';
import {EDL} from './edl';

const LAST = 291; // last rendered Blender frame (0-based)

type P = [number, number, number];

/**
 * The approved Blender hero shot, used once as the editorial bridge to the
 * real store page. Once the camera settles the page is flat and frontal, so
 * the hold continues as a slow 2D push on the last frame.
 */
export const SteamBlock: React.FC = () => {
  const frame = useCurrentFrame();
  const hold = Math.max(0, frame - LAST);
  const holdLen = EDL.s3.holdUntil - EDL.s3.from - LAST;
  const push = 1 + 0.035 * Math.min(1, hold / Math.max(1, holdLen));

  const pt = (name: keyof typeof anchors.points) => {
    const arr = anchors.points[name] as P[];
    const v = arr[Math.min(arr.length - 1, frame)];
    return {x: WIDTH / 2 + (v[0] - WIDTH / 2) * push, y: HEIGHT / 2 + (v[1] - HEIGHT / 2) * push};
  };
  const rel = pt('release');
  const ita = pt('italian');
  const itaNa = pt('italian_na');
  const k = (itaNa.x - ita.x) / (2860 - 2372);
  const italianAt = EDL.s3.italianAt;
  const hi = progress(frame, italianAt + 2, 14);
  const logoAt = EDL.s3.logoAt;
  const hiOut = interpolate(frame, [logoAt - 6, logoAt + 2], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rowW = 760 * k;
  const rowH = 54 * k;

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <AbsoluteFill style={{transform: `scale(${push})`}}>
        <Freeze frame={LAST} active={(f) => f >= LAST}>
          <OffthreadVideo src={staticFile('s3_blender.mp4')} muted />
        </Freeze>
      </AbsoluteFill>
      <Callout
        anchor={{x: rel.x - 10, y: rel.y}}
        dock={{x: SAFE.left, y: rel.y - 74}}
        labelSide="above"
        at={168}
        until={222}
        tint={color.steam}
        kicker="Pagina Steam · stato"
        title="Uscita da annunciare"
        sub="Senza data · wishlist già aperta"
        variant="glass"
      />
      <svg width={WIDTH} height={HEIGHT} style={{position: 'absolute', inset: 0, opacity: hiOut}}>
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
        dock={{x: SAFE.left, y: Math.min(ita.y - 96, 1240)}}
        labelSide="above"
        at={italianAt - 4}
        until={logoAt - 8}
        tint={color.redline}
        kicker="Localizzazione · oggi"
        title="Italiano non supportato"
        sub="7 lingue elencate, l'italiano non c'è"
        variant="glass"
      />
      <SteamEndCard at={logoAt} />
    </AbsoluteFill>
  );
};

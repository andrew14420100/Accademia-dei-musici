import {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, Sequence, useVideoConfig} from 'remotion';
import interp60 from '../../public/full60/list.json';
import revive from '../../public/track_revive.json';
import {Callout} from '../components/Callout';
import {TitleBlock} from '../components/TitleBlock';
import {color, fontsReady, SAFE, sampleTrack, useBaseFrame, useFrameScale} from '../design';
import {Bug, ChapterTitle, Subtitles} from './Chrome';
import {EDL, project, shot, Shot, wordAt} from './edl';
import {FullShot} from './FullShot';
import {AnalysisCard, Chain, DataStack, Note, Roles, SafeZone, Signature, UiTag} from './Graphics';
import {Loupe} from './Loupe';
import {SteamBlock} from './SteamBlock';

/** Duration in composition frames (EDL is authored in 30 fps base frames). */
export const fullFrames = (fps: number) => (EDL.frames * fps) / EDL.fps;

/** Local base frame (inside a shot) of a spoken word. */
const w = (s: Shot, line: string, word: string) => wordAt(line, word) - s.from;
const endOf = (s: Shot) => s.frames;

const RevivePin: React.FC<{s: Shot}> = ({s}) => {
  const f = useBaseFrame();
  const [x, y] = sampleTrack(revive.points, f);
  const a = project(s, f, x, y - 40);
  return (
    <Callout
      anchor={a}
      dock={{x: SAFE.left, y: 600}}
      labelSide="above"
      at={2}
      until={revive.points.length - 4}
      tint={color.steam}
      kicker="Visto nel filmato"
      title="Rianimazione"
      sub="Un compagno lo rimette in piedi"
      variant="open"
      width={820}
    />
  );
};

const OVERLAYS: Record<string, (s: Shot) => React.ReactNode> = {
  // Hook: the game is named on screen within the first half second.
  h_heli: () => <TitleBlock at={8} />,
  h_credits: (s) => (
    <Loupe s={s} region={{x: 0, y: 950, w: 420, h: 95}} at={2} until={endOf(s)} box={{x: 120, y: 760, w: 760}} kicker="Crediti in partita" />
  ),

  i_arena: (s) => (
    <DataStack
      top={620}
      until={endOf(s) + shot('i_hall').frames - 6}
      items={[
        {at: w(s, 'id1', 'galaxy'), k: 'Sviluppo · pagina Steam', v: 'Galaxy Studio', tint: color.steam},
        {at: w(s, 'id1', 'netease'), k: 'Sviluppatore ed editore', v: 'NetEase Games', tint: color.steam},
      ]}
    />
  ),
  i_descent: (s) => (
    <DataStack
      top={360}
      until={endOf(s) - 6}
      items={[
        {at: w(s, 'id2', 'free'), k: 'Modello · pagina Steam', v: 'Free-to-play', tint: color.steam},
        {at: w(s, 'id2', 'pc'), k: 'Piattaforma', v: 'PC · Windows 10/11', tint: color.steam},
        {at: w(s, 'id2', 'data'), k: 'Uscita', v: 'Da annunciare', tint: color.steam},
      ]}
    />
  ),
  i_map: (s) => <SafeZone at={w(s, 'id3', 'zona') - 6} until={endOf(s) - 10} cx={500} cy={930} />,

  m_slide: (s) => (
    <Chain
      top={340}
      until={endOf(s) + shot('m_aim').frames - 8}
      steps={[
        {at: w(s, 'mov2', 'sprint'), label: 'Sprint'},
        {at: w(s, 'mov2', 'scivolata'), label: 'Scivolata'},
        {at: w(s, 'mov2', 'mira'), label: 'Mira'},
        {at: w(s, 'mov2', 'fuoco'), label: 'Fuoco'},
      ]}
    />
  ),
  m_grapple_tp: (s) => (
    <DataStack
      top={360}
      until={endOf(s) + shot('m_wall').frames + shot('m_grapple_fp').frames - 10}
      items={[
        {at: w(s, 'mov3', 'rampino'), k: 'Estende la catena', v: 'Rampino', tint: color.steam},
        {at: w(s, 'mov3', 'rimbalzi'), k: 'Estende la catena', v: 'Rimbalzi a parete', tint: color.steam},
      ]}
    />
  ),
  m_air: (s) => (
    <AnalysisCard
      at={w(s, 'mov4', 'lettura')}
      until={endOf(s) + shot('m_air2').frames - 8}
      top={340}
      title="Tempismo > copertura?"
      sub="Se si spara in movimento, la posizione cambia di continuo."
    />
  ),

  s_hud: (s) => (
    <Loupe
      s={s}
      region={{x: 20, y: 715, w: 330, h: 330}}
      at={w(s, 'sq1', 'quattro') - 2}
      until={endOf(s) + 40}
      box={{x: 300, y: 560, w: 480}}
      kicker="HUD · squadra da 4"
    />
  ),
  s_push: (s) => (
    <Roles
      top={340}
      until={endOf(s) + shot('s_fight').frames + shot('s_cover').frames - 8}
      roles={[
        {at: w(s, 'sq2', 'assorbe'), k: 'Scudo', v: 'Assorbe il fuoco'},
        {at: w(s, 'sq2', 'tiene'), k: 'Supporto', v: 'Tiene in vita'},
        {at: w(s, 'sq2', 'entra'), k: 'Ingresso', v: 'Entra col rampino'},
      ]}
    />
  ),

  r_revive: (s) => <RevivePin s={s} />,
  r_roam: (s) => (
    <Note
      at={w(s, 're3', 'roaming') - 4}
      until={endOf(s) + shot('r_roof').frames - 8}
      top={340}
      kicker="Descritto dalla pagina Steam"
      title="Stato di roaming"
      sub="Non visibile in questo filmato"
    />
  ),

  e_hud: (s) => (
    <Loupe s={s} region={{x: 0, y: 950, w: 420, h: 95}} at={w(s, 'ec1', 'crediti') - 4} until={endOf(s) - 6} box={{x: 120, y: 760, w: 760}} kicker="Crediti del giocatore" />
  ),
  e_shop: (s) => {
    const mine = project(s, 40, 597, 560);
    const syr = project(s, 40, 787, 285);
    return (
      <AbsoluteFill>
        <UiTag x={mine.x} y={mine.y} at={w(s, 'ec2', 'mina')} until={endOf(s)} label="粘雷 · mina adesiva" value="400" />
        <UiTag x={syr.x} y={syr.y} at={w(s, 'ec2', 'siringa')} until={endOf(s)} label="自救针 · auto-rianimazione" value="4.500" side="left" />
      </AbsoluteFill>
    );
  },
  e_funds: (s) => {
    // pin sits just right of the in-game figure, so the real balance stays readable
    const funds = project(s, 20, 445, 793);
    return (
      <AbsoluteFill>
        {/* the counter is still falling when the shop closes (clip frame ~33):
            last legible figure 1.813; the tag leaves before the shop does */}
        <UiTag x={funds.x} y={funds.y} at={4} until={26} label="Saldo durante gli acquisti" value="6.000 → 1.813" tint={color.paper} />
      </AbsoluteFill>
    );
  },

  // after the shop closes, so the card never covers prices or the balance
  e_after: (s) => (
    <AnalysisCard
      at={2}
      until={endOf(s) - 6}
      top={340}
      title="1 siringa ≈ 11 mine"
      sub="4.500 ÷ 400: rialzarsi da soli o mettere pressione."
    />
  ),

  w_range: (s) => (
    <DataStack
      top={360}
      until={endOf(s) + shot('w_scope').frames - 8}
      items={[
        {at: w(s, 'wp1', 'balistica'), k: 'Taratura dichiarata', v: 'Balistica', tint: color.steam},
        {at: w(s, 'wp1', 'rinculo'), k: 'Taratura dichiarata', v: 'Rinculo', tint: color.steam},
        {at: w(s, 'wp1', 'maneggevolezza'), k: 'Taratura dichiarata', v: 'Maneggevolezza', tint: color.steam},
      ]}
    />
  ),
  w_inspect: (s) => (
    <Chain
      kicker="Modifica dell'arma"
      top={340}
      until={endOf(s) + shot('w_inspect2').frames - 4}
      steps={[
        {at: w(s, 'wp2', 'parti'), label: 'Parti'},
        {at: w(s, 'wp2', 'ottiche'), label: 'Ottiche'},
        {at: w(s, 'wp2', 'impugnatura'), label: 'Impugnatura'},
      ]}
    />
  ),
};

/** Overlays that must not outlive their own shot. */
const SHOT_ONLY = new Set(['h_heli', 'h_credits']);

const firstOfSection = new Set<string>();
const lastOfSection = new Set<string>();
for (const sec of Object.keys(EDL.sections)) {
  const list = EDL.shots.filter((s) => s.section === sec);
  if (list.length) {
    firstOfSection.add(list[0].id);
    lastOfSection.add(list[list.length - 1].id);
  }
}

const INTERP = new Set<string>((interp60 as {ids: string[]}).ids);

export const RedlineFull: React.FC = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    fontsReady.then(() => continueRender(handle));
  }, [handle]);
  const k = useFrameScale();
  const {fps} = useVideoConfig();
  // Base frames -> composition frames.
  const F = (n: number) => Math.round(n * k);
  const sig = EDL.signature;

  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {EDL.shots.map((s) => {
        if (s.src === 'S3') {
          const [a, b] = EDL.sections.steam;
          return (
            <Sequence key={s.id} from={F(a)} durationInFrames={F(b - a)} name="07 · Steam (Blender bridge + page)">
              <SteamBlock />
            </Sequence>
          );
        }
        const swingIn = firstOfSection.has(s.id) && !['hook', 'outro'].includes(s.section);
        const swingOut = lastOfSection.has(s.id) && !['weapons', 'outro', 'hook'].includes(s.section);
        const src = fps === 60 && INTERP.has(s.id) ? `full60/${s.id}.mp4` : undefined;
        return (
          <Sequence key={s.id} from={F(s.from)} durationInFrames={F(s.frames)} name={s.id}>
            <FullShot s={s} swingIn={swingIn} swingOut={swingOut} src={src} />
          </Sequence>
        );
      })}

      {/* Overlays live on their own layer: they may outlast the shot that
          starts them (local frames still count from that shot's first frame). */}
      {EDL.shots
        .filter((s) => OVERLAYS[s.id])
        .map((s) => (
          <Sequence key={`ov-${s.id}`} from={F(s.from)} durationInFrames={F(SHOT_ONLY.has(s.id) ? s.frames : EDL.sections[s.section][1] - s.from)} name={`overlay ${s.id}`}>
            {OVERLAYS[s.id](s)}
          </Sequence>
        ))}

      {Object.keys(EDL.sections)
        .filter((sec) => !['hook', 'steam', 'outro'].includes(sec))
        .map((sec) => (
          <Sequence key={sec} from={F(EDL.sections[sec][0])} durationInFrames={F(60)} name={`chapter ${sec}`}>
            <ChapterTitle section={sec} />
          </Sequence>
        ))}

      <AbsoluteFill
        style={{background: 'radial-gradient(120% 75% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.30) 100%)', pointerEvents: 'none'}}
      />
      <Sequence from={0} durationInFrames={F(sig.from)} name="bug">
        <Bug />
      </Sequence>
      <Subtitles />
      <Sequence from={F(sig.from)} durationInFrames={F(EDL.frames - sig.from)} name="signature">
        <Signature frames={EDL.frames - sig.from} />
      </Sequence>
    </AbsoluteFill>
  );
};

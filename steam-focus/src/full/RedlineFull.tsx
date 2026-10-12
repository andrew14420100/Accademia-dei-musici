import {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, Sequence, useCurrentFrame} from 'remotion';
import revive from '../../public/track_revive.json';
import {Callout} from '../components/Callout';
import {TitleBlock} from '../components/TitleBlock';
import {color, fontsReady, SAFE} from '../design';
import {Bug, ChapterTitle, Subtitles} from './Chrome';
import {EDL, project, shot, Shot, wordAt} from './edl';
import {FullShot} from './FullShot';
import {Chain, DataStack, Note, Outro, Roles, SafeZone, UiTag} from './Graphics';
import {Loupe} from './Loupe';
import {SteamBlock} from './SteamBlock';

export const FULL_FRAMES = EDL.frames;

/** Local frame (inside a shot) of a spoken word. */
const w = (s: Shot, line: string, word: string) => wordAt(line, word) - s.from;
const endOf = (s: Shot) => s.frames;

const OVERLAYS: Record<string, (s: Shot) => React.ReactNode> = {
  h_credits: (s) => (
    <Loupe s={s} region={{x: 0, y: 950, w: 420, h: 95}} at={2} until={endOf(s)} box={{x: 120, y: 760, w: 840}} kicker="Crediti in partita" />
  ),
  h_heli: (s) => <TitleBlock at={w(s, 'hook2', 'chiama') + 6} />,

  i_arena: (s) => (
    <DataStack
      top={620}
      until={endOf(s) + shot('i_hall').frames - 6}
      items={[
        {at: w(s, 'id1', 'galaxy'), k: 'Sviluppo', v: 'Galaxy Studio', tint: color.redline},
        {at: w(s, 'id1', 'netis'), k: 'Sviluppatore ed editore su Steam', v: 'NetEase Games', tint: color.steam},
      ]}
    />
  ),
  i_descent: (s) => (
    <DataStack
      top={360}
      until={endOf(s) - 6}
      items={[
        {at: w(s, 'id2', 'free'), k: 'Modello', v: 'Free-to-play', tint: color.steam},
        {at: w(s, 'id2', 'pc'), k: 'Piattaforma', v: 'PC · Windows 10/11', tint: color.steam},
        {at: w(s, 'id2', 'data'), k: 'Uscita', v: 'Da annunciare', tint: color.steam},
      ]}
    />
  ),
  i_map: (s) => <SafeZone at={w(s, 'id3', 'zona') - 6} until={endOf(s) - 10} cx={540} cy={930} />,

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
        {at: w(s, 'mov3', 'rampino'), k: 'Estende la catena', v: 'Rampino', tint: color.redline},
        {at: w(s, 'mov3', 'rimbalzi'), k: 'Estende la catena', v: 'Rimbalzi a parete', tint: color.redline},
      ]}
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

  r_revive: (s) => {
    const RevivePin: React.FC = () => {
      const f = useCurrentFrame();
      const p = revive.points[Math.min(revive.points.length - 1, f)];
      const a = project(s, f, p[0], p[1] - 40);
      return (
        <Callout
          anchor={a}
          dock={{x: SAFE.left, y: 560}}
          labelSide="above"
          at={2}
          until={revive.points.length - 4}
          tint={color.redline}
          kicker="Visto nel filmato"
          title="Rianimazione"
          sub="Un compagno lo rimette in piedi"
          variant="open"
          width={860}
        />
      );
    };
    return <RevivePin />;
  },
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
    <Loupe s={s} region={{x: 0, y: 950, w: 420, h: 95}} at={w(s, 'ec1', 'crediti') - 4} until={endOf(s) - 6} box={{x: 120, y: 760, w: 840}} kicker="Crediti del giocatore" />
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
    const funds = project(s, 30, 300, 793);
    return <UiTag x={funds.x} y={funds.y} at={w(s, 'ec3', 'saldo')} until={endOf(s)} label="Saldo dopo gli acquisti" value="6.000 → 3.207" tint={color.paper} />;
  },

  w_range: (s) => (
    <DataStack
      top={360}
      until={endOf(s) + shot('w_scope').frames - 8}
      items={[
        {at: w(s, 'wp1', 'balistica'), k: 'Taratura dichiarata', v: 'Balistica', tint: color.redline},
        {at: w(s, 'wp1', 'rinculo'), k: 'Taratura dichiarata', v: 'Rinculo', tint: color.redline},
        {at: w(s, 'wp1', 'maneggevolezza'), k: 'Taratura dichiarata', v: 'Maneggevolezza', tint: color.redline},
      ]}
    />
  ),
  w_inspect: (s) => (
    <Chain
      top={340}
      until={endOf(s) - 4}
      steps={[
        {at: w(s, 'wp2', 'parti'), label: 'Parti'},
        {at: w(s, 'wp2', 'ottiche'), label: 'Ottiche'},
        {at: w(s, 'wp2', 'impugnatura'), label: 'Impugnatura'},
      ]}
    />
  ),
};

const firstOfSection = new Set<string>();
const lastOfSection = new Set<string>();
for (const sec of Object.keys(EDL.sections)) {
  const list = EDL.shots.filter((s) => s.section === sec);
  if (list.length) {
    firstOfSection.add(list[0].id);
    lastOfSection.add(list[list.length - 1].id);
  }
}

export const RedlineFull: React.FC = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    fontsReady.then(() => continueRender(handle));
  }, [handle]);

  const outro = EDL.sections.outro;
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {EDL.shots.map((s) => {
        if (s.src === 'S3') {
          const [a, b] = EDL.sections.steam;
          return (
            <Sequence key={s.id} from={a} durationInFrames={b - a} name="S3 · Steam page (Blender)">
              <SteamBlock />
            </Sequence>
          );
        }
        const whipIn = firstOfSection.has(s.id) && !['hook', 'outro'].includes(s.section);
        const whipOut = lastOfSection.has(s.id) && !['weapons', 'outro'].includes(s.section);
        return (
          <Sequence key={s.id} from={s.from} durationInFrames={s.frames} name={s.id}>
            <FullShot s={s} whipIn={whipIn} whipOut={whipOut} />
          </Sequence>
        );
      })}

      {/* Overlays live on their own layer: they may outlast the shot that
          starts them (local frames still count from that shot's first frame). */}
      {EDL.shots
        .filter((s) => OVERLAYS[s.id])
        .map((s) => (
          <Sequence key={`ov-${s.id}`} from={s.from} durationInFrames={EDL.sections[s.section][1] - s.from} name={`overlay ${s.id}`}>
            {OVERLAYS[s.id](s)}
          </Sequence>
        ))}

      {Object.keys(EDL.sections)
        .filter((k) => !['hook', 'steam', 'outro'].includes(k))
        .map((k) => (
          <Sequence key={k} from={EDL.sections[k][0]} durationInFrames={70} name={`chapter ${k}`}>
            <ChapterTitle section={k} />
          </Sequence>
        ))}

      <Sequence from={outro[0]} durationInFrames={outro[1] - outro[0]} name="outro card">
        <Outro questionAt={wordAt('end2', 'secondo') - outro[0]} />
      </Sequence>

      <AbsoluteFill
        style={{background: 'radial-gradient(120% 75% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.30) 100%)', pointerEvents: 'none'}}
      />
      <Sequence from={0} durationInFrames={outro[0]} name="bug">
        <Bug />
      </Sequence>
      <Subtitles />
    </AbsoluteFill>
  );
};

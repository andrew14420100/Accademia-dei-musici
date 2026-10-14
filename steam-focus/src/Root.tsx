import {Composition} from 'remotion';
import {RedlineDemo, DEMO_FRAMES} from './RedlineDemo';
import {FPS, HEIGHT, WIDTH} from './design';
import {fullFrames, RedlineFull} from './full/RedlineFull';
import {RedlineFull4K} from './full/RedlineFull4K';
import {CoverV4, CoverV4Draft} from './full/Cover';

export const Root: React.FC = () => (
  <>
  <Composition
    id="RedlineDemo"
    component={RedlineDemo}
    durationInFrames={DEMO_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
  <Composition
    id="RedlineFull"
    component={RedlineFull}
    durationInFrames={fullFrames(FPS)}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
  {/* Final master: 2160x3840, 60 fps CFR. Layout is authored in 1080x1920
      units and laid out at 2x zoom, so text and vector graphics rasterize
      natively at 4K; animations are evaluated on 60 fps frames. */}
  <Composition
    id="RedlineFull4K"
    component={RedlineFull4K}
    durationInFrames={fullFrames(60)}
    fps={60}
    width={WIDTH * 2}
    height={HEIGHT * 2}
  />
    <Composition id="CoverV4" component={CoverV4} durationInFrames={1} fps={60} width={WIDTH * 2} height={HEIGHT * 2} />
    <Composition id="CoverV4Draft" component={CoverV4Draft} durationInFrames={1} fps={60} width={WIDTH * 2} height={HEIGHT * 2} />
    </>
);

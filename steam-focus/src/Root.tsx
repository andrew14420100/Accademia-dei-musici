import {Composition} from 'remotion';
import {RedlineDemo, DEMO_FRAMES} from './RedlineDemo';
import {FPS, HEIGHT, WIDTH} from './design';
import {FULL_FRAMES, RedlineFull} from './full/RedlineFull';

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
    durationInFrames={FULL_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
  </>
);

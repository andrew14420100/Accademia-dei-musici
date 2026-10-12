import {Composition} from 'remotion';
import {RedlineDemo, DEMO_FRAMES} from './RedlineDemo';
import {FPS, HEIGHT, WIDTH} from './design';

export const Root: React.FC = () => (
  <Composition
    id="RedlineDemo"
    component={RedlineDemo}
    durationInFrames={DEMO_FRAMES}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);

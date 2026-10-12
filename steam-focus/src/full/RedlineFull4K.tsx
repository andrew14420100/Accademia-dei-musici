import {AbsoluteFill} from 'remotion';
import {HEIGHT, WIDTH} from '../design';
import {RedlineFull} from './RedlineFull';

/**
 * 4K wrapper. CSS zoom changes layout size (not a bitmap scale), so every
 * text glyph, SVG stroke and image is rasterized at 2160x3840.
 */
export const RedlineFull4K: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: '#000'}}>
    <div style={{position: 'absolute', left: 0, top: 0, width: WIDTH, height: HEIGHT, zoom: 2, overflow: 'hidden'}}>
      <RedlineFull />
    </div>
  </AbsoluteFill>
);

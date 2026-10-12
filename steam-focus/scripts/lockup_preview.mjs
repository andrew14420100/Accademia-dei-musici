// Lockup previews top-left over clean gameplay frames: node lockup_preview.mjs SVG OUTPREFIX BG...
import {chromium} from 'playwright';
import fs from 'fs';
const [svgFile, outPrefix, ...bgs] = process.argv.slice(2);
const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const p = await b.newPage({viewport: {width: 2160, height: 3840}});
const svg = fs.readFileSync(svgFile, 'utf8').replace(/width="[\d.]+" height="[\d.]+"/, 'height="124"');
for (const [i, f] of bgs.entries()) {
  const bg = fs.readFileSync(f).toString('base64');
  // x 128 / top 340 = TikTok safe area (64, 170) x2; height 124 = 62 design px
  await p.setContent(`<html><body style="margin:0;width:2160px;height:3840px;background:url(data:image/png;base64,${bg});background-size:cover">
    <div style="position:absolute;left:0;top:0;width:1500px;height:700px;background:radial-gradient(60% 55% at 18% 14%, rgba(11,22,38,0.55), rgba(11,22,38,0) 70%)"></div>
    <div style="position:absolute;left:128px;top:340px;filter:drop-shadow(0 4px 14px rgba(0,0,0,0.6))">${svg}</div></body></html>`);
  await p.screenshot({path: `${outPrefix}_${i}.png`});
}
await b.close();

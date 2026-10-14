import {chromium} from 'playwright';
import fs from 'fs';
const S = process.argv[2], root = process.argv[3];
const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const p = await b.newPage({viewport: {width: 2160, height: 3840}});
for (const c of ['a_focusframe', 'b_aperture']) {
  const svg = fs.readFileSync(`${root}/brand/${c}/stacked_dark.svg`, 'utf8').replace(/width="[\d.]+" height="[\d.]+"/, 'height="168"');
  for (const i of [0, 1, 2]) {
    const bg = fs.readFileSync(`${S}/bg${i}.png`).toString('base64');
    // 4K units: x 128 (= SAFE.left 64 x 2), top 340 (= 170 x 2), height 168 (= 84 design px)
    await p.setContent(`<html><body style="margin:0;width:2160px;height:3840px;background:url(data:image/png;base64,${bg});background-size:cover">
      <div style="position:absolute;left:0;top:0;width:1400px;height:760px;background:radial-gradient(70% 60% at 10% 12%, rgba(11,22,38,0.55), rgba(11,22,38,0) 70%)"></div>
      <div style="position:absolute;left:128px;top:340px;filter:drop-shadow(0 6px 18px rgba(0,0,0,0.55))">${svg}</div></body></html>`);
    await p.screenshot({path: `${S}/pv_${c}_${i}.png`});
  }
}
await b.close();

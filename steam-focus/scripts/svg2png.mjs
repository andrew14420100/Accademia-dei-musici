// usage: node svg2png.mjs out.png width file.svg [bg]
import {chromium} from 'playwright';
import fs from 'fs';
const [out, width, file, bg] = process.argv.slice(2);
const svg = fs.readFileSync(file, 'utf8');
const m = svg.match(/viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"/);
const w = +width, h = Math.round(w * (+m[4]) / (+m[3]));
const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const p = await b.newPage({viewport: {width: w, height: h}});
await p.setContent(`<html><body style="margin:0;background:${bg || 'transparent'}">${svg.replace(/width="[\d.]+" height="[\d.]+"/, `width="${w}" height="${h}"`)}</body></html>`);
await p.screenshot({path: out, omitBackground: !bg});
await b.close();

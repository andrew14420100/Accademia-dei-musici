// Capture the real ECC: REDLINE Steam page (Italian) at 3x density and save
// legible crops of the facts the report cites, with DOM-measured boxes.
// usage: node capture_steam_details.mjs <outDir> <chromeExecutable>
import fs from 'node:fs';
import {chromium} from 'playwright';

const [out, exe] = process.argv.slice(2);
const DSF = 3;
const browser = await chromium.launch({executablePath: exe, args: ['--headless=new']});
const ctx = await browser.newContext({viewport: {width: 1600, height: 1000}, deviceScaleFactor: DSF, locale: 'it-IT'});
await ctx.addCookies([
  {name: 'birthtime', value: '0', domain: 'store.steampowered.com', path: '/'},
  {name: 'wants_mature_content', value: '1', domain: 'store.steampowered.com', path: '/'},
  {
    name: 'cookieSettings',
    value: '%7B%22version%22%3A1%2C%22preference_state%22%3A2%2C%22content_customization%22%3Anull%2C%22valve_analytics%22%3Anull%2C%22third_party_analytics%22%3Anull%2C%22third_party_content%22%3Anull%2C%22utm_enabled%22%3Atrue%7D',
    domain: 'store.steampowered.com',
    path: '/',
  },
]);
const page = await ctx.newPage();
await page.goto('https://store.steampowered.com/app/5268340/ECC_REDLINE/?l=italian', {waitUntil: 'networkidle', timeout: 90000});
await page.addStyleTag({content: '#cookiePrefPopup,.cookiepreferences_popup{display:none!important}'});
await page.waitForTimeout(2500);

// Union box of the elements matched by each text, expanded by a margin (CSS px).
const boxOf = async (texts, margin = 18) => {
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (const t of texts) {
    const loc = page.locator(`text=${t} >> visible=true`).first();
    const b = await loc.boundingBox();
    if (!b) throw new Error(`not found: ${t}`);
    x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y);
    x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height);
  }
  return {x: x0 - margin, y: y0 - margin, width: x1 - x0 + 2 * margin, height: y1 - y0 + 2 * margin};
};

const scrollY = async () => page.evaluate(() => window.scrollY);
const crops = {
  header: ['NEGOZIO', 'ECC: REDLINE'],
  facts: ['DATA DI RILASCIO', 'In arrivo', 'SVILUPPATORE', 'EDITORE'],
  wishlist: ['Questo gioco non è ancora disponibile su Steam', 'Aggiungi alla Lista dei desideri'],
  languages: ['Lingue:', 'Mostra tutte le lingue supportate'],
  about: ['Galaxy Studio under NetEase Games'],
};
const meta = {captured: new Date().toISOString(), url: page.url(), dsf: DSF, crops: {}};
for (const [name, texts] of Object.entries(crops)) {
  // Bring the region into view, then measure in viewport coordinates.
  await page.locator(`text=${texts[0]} >> visible=true`).first().scrollIntoViewIfNeeded({timeout: 15000});
  await page.waitForTimeout(600);
  let box = await boxOf(texts);
  if (name === 'header') {
    // include the Steam logo (left of the NEGOZIO tab) and the title row
    const logo = await page.locator('a[href*="store.steampowered.com"] img, .logo img, #logo_holder img').first().boundingBox().catch(() => null);
    if (logo) {
      const x0 = Math.min(box.x, logo.x - 18);
      const y0 = Math.min(box.y, logo.y - 18);
      box = {x: x0, y: y0, width: box.x + box.width - x0, height: box.y + box.height - y0};
    }
  }
  await page.screenshot({path: `${out}/steam_${name}.png`, clip: box});
  meta.crops[name] = {...box, scrollY: await scrollY()};
}
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(500);
await page.screenshot({path: `${out}/steam_full_3x.png`, fullPage: true});
fs.writeFileSync(`${out}/steam_details.json`, JSON.stringify(meta, null, 1));
await browser.close();
console.log(JSON.stringify(meta.crops));

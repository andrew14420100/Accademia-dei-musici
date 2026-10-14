// Capture the real ECC: REDLINE Steam store page (Italian, 2x) for the Blender shot.
// usage: node capture_steam_page.mjs <outDir> <chromeExecutable>
import { chromium } from 'playwright';
const out = process.argv[2];
const exe = process.argv[3];
const browser = await chromium.launch({ executablePath: exe, args: ['--headless=new'] });
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2, locale: 'it-IT' });
await ctx.addCookies([
  { name: 'birthtime', value: '0', domain: 'store.steampowered.com', path: '/' },
  { name: 'wants_mature_content', value: '1', domain: 'store.steampowered.com', path: '/' },
  { name: 'cookieSettings', value: '%7B%22version%22%3A1%2C%22preference_state%22%3A2%2C%22content_customization%22%3Anull%2C%22valve_analytics%22%3Anull%2C%22third_party_analytics%22%3Anull%2C%22third_party_content%22%3Anull%2C%22utm_enabled%22%3Atrue%7D', domain: 'store.steampowered.com', path: '/' },
]);
const page = await ctx.newPage();
await page.goto('https://store.steampowered.com/app/5268340/ECC_REDLINE/?l=italian', { waitUntil: 'networkidle', timeout: 90000 });
await page.addStyleTag({ content: '#cookiePrefPopup,.cookiepreferences_popup{display:none!important}' });
await page.waitForTimeout(2000);
// Select the third media thumbnail so the player shows a screenshot, not a loading video.
await page.mouse.click(658, 782);
await page.waitForTimeout(2500);
await page.screenshot({ path: `${out}/steam_page_view.png` });
await page.screenshot({ path: `${out}/steam_page_full.png`, fullPage: true });
await browser.close();

// cut3d frame renderer (headless Chromium + SwiftShader WebGL), serving the repo root.
//   node tools/cut3d/render.js videos/<slug> out.mp4 [--cover] [--fps 30] [--t0 0] [--t1 <end>]
//   node tools/cut3d/render.js videos/<slug> --stills 0.5,3,12 <prefix> [--cover]     -> <prefix>_<t>.jpg
// env RS = internal 3D resolution scale (default 0.6667; DOM overlays stay full 1080x1920)
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path'), { spawn } = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.woff2': 'font/woff2', '.jpg': 'image/jpeg' };
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const ep = argv[0].replace(/\/$/, '');
const PORT = 8700 + Math.floor(Math.random() * 200);
const srv = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!p.startsWith(ROOT)) { r.writeHead(403); r.end(); return; }
  fs.readFile(p, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(d); }); });
(async () => {
  await new Promise(r => srv.listen(PORT, r));
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => { const s = m.text(); if (!/already non-indexed/.test(s)) console.log('[page]', s); });
  page.on('pageerror', e => console.log('[page error]', e.message));
  await page.goto(`http://localhost:${PORT}/tools/cut3d/engine.html?ep=${encodeURIComponent(ep)}&rs=${process.env.RS || '0.6667'}`);
  await page.waitForFunction('window.__ready === true || window.__error', null, { timeout: 180000 });
  const err = await page.evaluate('window.__error'); if (err) { console.error('engine failed:', err); process.exit(2); }
  const fn = argv.includes('--cover') ? '__cover' : '__frame';
  const tl = JSON.parse(fs.readFileSync(path.join(ROOT, ep, '.work', 'timeline.json')));
  if (argv[1] === '--stills') {
    for (const t of argv[2].split(',').map(Number)) {
      await page.evaluate(([f, t]) => window[f](t), [fn, t]);
      await page.screenshot({ path: `${argv[3]}_${t.toFixed(2)}.jpg`, type: 'jpeg', quality: 85 });
    }
  } else {
    const out = argv[1], fps = +opt('--fps', 30), t0 = +opt('--t0', 0), t1 = +opt('--t1', tl.total);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round((t1 - t0) * fps); const st = Date.now();
    for (let i = 0; i < n; i++) {
      await page.evaluate(([f, t]) => window[f](t), [fn, t0 + i / fps]);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`${path.basename(out)} frame ${i}/${n}  ${((Date.now() - st) / 1000 / (i + 1)).toFixed(2)} s/frame`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close(); srv.close();
})().catch(e => { console.error(e); process.exit(1); });

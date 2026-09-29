// Chrome DevTools Protocol로 앱 화면을 고해상도로 찍는다 (Node 22+ 내장 WebSocket 사용)
// node capture.mjs <url> <outDir>
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';

const [url = 'http://localhost:8766/', out = 'D:/voca-mkt/shots'] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 9333;
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, '--user-data-dir=D:/voca-mkt/profile', '--hide-scrollbars', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));

let ws, id = 0; const pending = new Map();
async function connect() {
  for (let i = 0; i < 50; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
      const page = list.find(t => t.type === 'page');
      if (page) { ws = new WebSocket(page.webSocketDebuggerUrl); break; }
    } catch { }
    await sleep(200);
  }
  await new Promise(r => ws.addEventListener('open', r, { once: true }));
  ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
}
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const js = async code => { const r = await send('Runtime.evaluate', { expression: `(async()=>{${code}})()`, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) console.error(r.result.exceptionDetails.text, r.result.exceptionDetails.exception?.description); return r.result?.result?.value; };

async function device(w, h, scale, dark) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: scale, mobile: w < 640 });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: dark ? 'dark' : 'light' }] });
}
async function shot(name) {
  await sleep(700);
  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
  writeFileSync(`${out}/${name}.png`, Buffer.from(r.result.data, 'base64'));
  console.log('saved', name);
}
async function load(prep = '') {
  await send('Page.navigate', { url });
  await sleep(1500);
  await js(`localStorage.clear();${prep}`);
  await send('Page.reload', {});
  await sleep(2200);
  // 화면에 보이는 그림이 다 불러와질 때까지 기다린다
  await js(`const t=Date.now();while(Date.now()-t<6000){const im=[...document.querySelectorAll('img')].filter(i=>{const r=i.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight&&i.getAttribute('src')});if(im.every(i=>i.complete))break;await new Promise(r=>setTimeout(r,200));}`);
}

await connect();
await send('Page.enable'); await send('Runtime.enable');

const scenes = JSON.parse(process.env.SCENES || '[]');
for (const s of scenes) {
  await device(s.w || 390, s.h || 844, s.scale || 3, s.dark !== false);
  await load(s.prep || '');
  if (s.run) { await js(s.run); await sleep(s.wait || 900); }
  await shot(s.name);
}
ws.close(); chrome.kill();
process.exit(0);

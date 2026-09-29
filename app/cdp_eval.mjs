// 에뮬레이터 WebView에 붙어 식 하나를 실행한다: node cdp_eval.mjs "<js>"
const port = 9444, expr = process.argv[2];
const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
const page = list.find(t => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
ws.send(JSON.stringify({ id: 1, method: 'Runtime.evaluate', params: { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true } }));
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id === 1) { console.log(JSON.stringify(m.result.result?.value ?? m.result)); process.exit(0); } });
setTimeout(() => { console.log('timeout'); process.exit(1); }, 20000);

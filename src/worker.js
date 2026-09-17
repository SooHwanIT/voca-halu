// Static site + /api/tts (Cloudflare Workers AI, English only)
const SPEAKERS = ['luna','asteria','stella','athena','hera','orion','arcas','perseus','angus','orpheus','helios','zeus'];
const MODELS = [
  { id: '@cf/deepgram/aura-1', input: (t, s) => ({ text: t, speaker: s }), type: 'audio/mpeg' },
  { id: '@cf/myshell-ai/melotts', input: t => ({ prompt: t, lang: 'en' }), type: 'audio/mpeg' },
];

async function tts(env, text, speaker) {
  let lastErr;
  for (const m of MODELS) {
    try {
      const res = await env.AI.run(m.id, m.input(text, speaker));
      if (res instanceof ReadableStream || res instanceof ArrayBuffer || res instanceof Uint8Array) {
        return new Response(res, { headers: { 'content-type': m.type } });
      }
      if (res && res.audio) { // base64
        const bin = Uint8Array.from(atob(res.audio), c => c.charCodeAt(0));
        return new Response(bin, { headers: { 'content-type': m.type } });
      }
      if (res instanceof Response) return new Response(res.body, { headers: { 'content-type': m.type } });
      lastErr = new Error('unexpected response from ' + m.id);
    } catch (e) { lastErr = e; }
  }
  throw lastErr || new Error('tts failed');
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/api/tts') {
      const text = (url.searchParams.get('t') || '').trim().slice(0, 300);
      if (!text) return new Response('missing t', { status: 400 });
      if (!env.AI) return new Response('AI binding missing', { status: 503 });
      const sp = url.searchParams.get('s') || 'luna';
      const speaker = SPEAKERS.includes(sp) ? sp : 'luna';
      const cache = caches.default;
      const key = new Request(new URL('/api/tts?v=1&s=' + speaker + '&t=' + encodeURIComponent(text.toLowerCase()), url.origin).toString());
      const hit = await cache.match(key);
      if (hit) return hit;
      try {
        const r = await tts(env, text, speaker);
        const buf = await r.arrayBuffer();
        const out = new Response(buf, { headers: { 'content-type': r.headers.get('content-type') || 'audio/mpeg', 'cache-control': 'public, max-age=2592000', 'access-control-allow-origin': '*' } });
        ctx.waitUntil(cache.put(key, out.clone()));
        return out;
      } catch (e) {
        return new Response('tts error: ' + (e && e.message), { status: 502 });
      }
    }
    return env.ASSETS.fetch(request);
  },
};

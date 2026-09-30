// 포카보카 서비스 워커 — 한 번 연 화면과 본 그림은 오프라인에서도 뜬다.
// 앱 본체: 네트워크 우선(새 버전 반영), 실패하면 캐시.
// 그림(img/): 캐시 우선 — 본 적 있는 포카만 저장한다(전체 1만 7천 장을 미리 받지 않는다).
// 글꼴 등 외부 정적 파일: 캐시를 먼저 쓰고 뒤에서 갱신.
// 음성(/api/tts): 캐시하지 않는다. 앱에 넣은 음성(tts/)은 같은 곳 파일이라 본 것만 저장된다.
const SHELL = 'pv-shell-10', IMG = 'pv-img-1';
const CORE = ['./', './index.html', './manifest.json', './icon.svg', './icon-192.png', './icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== SHELL && k !== IMG).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

// 알림을 누르면 열려 있는 창을 앞으로, 없으면 새로 연다
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => cs.length ? cs[0].focus() : self.clients.openWindow('./')));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.pathname.includes('/api/')) return;

  if (url.origin === location.origin && url.pathname.includes('/img/')) {
    e.respondWith(caches.open(IMG).then(async c => {
      const hit = await c.match(req);
      if (hit) return hit;
      const res = await fetch(req);
      if (res.ok) c.put(req, res.clone());
      return res;
    }));
    return;
  }
  if (req.mode === 'navigate' || (url.origin === location.origin && /\/$|\.html$/.test(url.pathname))) {
    e.respondWith(fetch(req).then(res => {
      if (res.ok) caches.open(SHELL).then(c => c.put(req, res.clone()));
      return res;
    }).catch(() => caches.match(req).then(r => r || caches.match('./index.html'))));
    return;
  }
  if (url.origin === location.origin || /(jsdelivr\.net|googleapis\.com|gstatic\.com)$/.test(url.hostname)) {
    e.respondWith(caches.open(SHELL).then(async c => {
      const hit = await c.match(req);
      const net = fetch(req).then(res => { if (res.ok || res.type === 'opaque') c.put(req, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    }));
  }
});

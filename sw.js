/* Vāk offline helper. Page: network first (so updates arrive), stored copy when offline.
   Recordings: stored copy first, served in byte ranges as audio players (Safari) require. */
const CACHE = "vak-v3-1";
const PAGE = ["./", "./index.html", "./manifest.webmanifest", "./icon-180.png", "./icon-192.png", "./icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(PAGE)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith("vak-") && k !== CACHE && k !== "vak-audio").map(k => caches.delete(k)))).then(() => self.clients.claim())); });
const bufs = {};
async function audioBuf(url) {
  if (bufs[url]) return bufs[url];
  const hit = await (await caches.open("vak-audio")).match(url);
  if (!hit) return null;
  bufs[url] = { buf: await hit.arrayBuffer(), type: hit.headers.get("Content-Type") || "audio/mpeg" };
  return bufs[url];
}
self.addEventListener("fetch", e => {
  const req = e.request, u = new URL(req.url);
  if (req.method !== "GET" || u.origin !== location.origin) return;
  if (/\.(mp3|m4a|ogg|wav)$/i.test(u.pathname)) {
    e.respondWith((async () => {
      const a = await audioBuf(u.origin + u.pathname);
      if (!a) return fetch(req);
      const size = a.buf.byteLength, range = req.headers.get("range");
      if (!range) return new Response(a.buf, { status: 200, headers: { "Content-Type": a.type, "Content-Length": String(size), "Accept-Ranges": "bytes" } });
      const m = /bytes=(\d*)-(\d*)/.exec(range) || [];
      let start = m[1] ? +m[1] : 0, end = m[2] ? +m[2] : size - 1;
      if (!m[1] && m[2]) { start = size - +m[2]; end = size - 1; }
      end = Math.min(end, size - 1);
      return new Response(a.buf.slice(start, end + 1), { status: 206, headers: {
        "Content-Type": a.type, "Content-Length": String(end - start + 1), "Content-Range": `bytes ${start}-${end}/${size}`, "Accept-Ranges": "bytes" } });
    })());
    return;
  }
  e.respondWith((async () => {
    const c = await caches.open(CACHE);
    try {
      const r = await fetch(req);
      if (r.ok && (req.mode === "navigate" || PAGE.some(p => u.pathname.endsWith(p.slice(1))))) c.put(req, r.clone());
      return r;
    } catch (err) {
      return (await c.match(req, { ignoreSearch: true })) || (await c.match("./")) || Response.error();
    }
  })());
});

"""Build an installable, offline-capable website from packs (for GitHub Pages or any static host).

  site/
    index.html             the Reader (first pack opens first)
    <pack>.mp3             recordings, only for packs whose licence is "public"
    sw.js                  service worker: keeps the page and recordings on the device
    manifest.webmanifest   lets phones and iPads "Add to Home Screen" as an app
    icon-180.png icon-192.png icon-512.png

How offline works, plainly: on the first visit with internet, the page saves itself and the recording
into the browser's storage, showing "Saving for offline use… 40%". Afterwards the service worker answers
from that storage, so the page opens and plays with no internet. Audio players ask for the file in pieces
("byte ranges"); the service worker serves those pieces from storage too, which iPhone/iPad Safari needs.
"""
import copy, json, os, shutil

from . import htmlbuild

SW = r"""/* Vāk offline helper. Page: network first (so updates arrive), stored copy when offline.
   Recordings: stored copy first, served in byte ranges as audio players (Safari) require. */
const CACHE = "vak-__VERSION__";
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
"""

# Added to the page: register the helper, save recordings with visible progress, report "ready offline".
OFFLINE_JS = r"""<script>
(function(){
  if(!("serviceWorker" in navigator) || !window.caches || (location.protocol!=="https:" && location.hostname!=="localhost")) return;
  navigator.serviceWorker.register("sw.js").catch(function(){});
  var files = __AUDIO_FILES__;
  function say(t,ms){ try{ toast(t,ms||3000); }catch(e){} }
  async function saveAll(){
    var c = await caches.open("vak-audio"), fresh = 0;
    for (var i=0;i<files.length;i++){
      var url = new URL(files[i], location.href).href;
      if (await c.match(url)) continue;
      fresh++;
      var r = await fetch(url, {cache:"no-store"}); if(!r.ok || !r.body) return;
      var total = +r.headers.get("Content-Length") || 0, got = 0, chunks = [], rd = r.body.getReader(), last = 0;
      for(;;){ var x = await rd.read(); if(x.done) break; chunks.push(x.value); got += x.value.length;
        if (total && Date.now()-last > 1500){ last = Date.now(); say("Saving for offline use… " + Math.round(got*100/total) + "%", 1800); } }
      await c.put(url, new Response(new Blob(chunks, {type: r.headers.get("Content-Type")||"audio/mpeg"}), {headers:{"Content-Type": r.headers.get("Content-Type")||"audio/mpeg"}}));
    }
    if (fresh) say("Ready. This prayer now works without internet.", 4500);
    try{ if(navigator.storage && navigator.storage.persist) navigator.storage.persist(); }catch(e){}
  }
  if (document.readyState === "complete") setTimeout(saveAll, 1500); else addEventListener("load", function(){ setTimeout(saveAll, 1500); });
})();
</script>"""

HEAD_EXTRA = ('<link rel="manifest" href="manifest.webmanifest">'
              '<meta name="apple-mobile-web-app-capable" content="yes">'
              '<meta name="mobile-web-app-capable" content="yes">'
              '<meta name="apple-mobile-web-app-title" content="Vāk">'
              '<meta name="theme-color" content="#1a120e">'
              '<link rel="apple-touch-icon" href="icon-180.png">')


def icons(out):
    from PIL import Image, ImageDraw
    for n in (180, 192, 512):
        im = Image.new("RGB", (n, n), (26, 18, 14))
        d = ImageDraw.Draw(im)
        r = n * 0.30                                    # a lamp's glow: gold disc with a sindoor flame
        d.ellipse([n/2 - r, n*0.56 - r*0.55, n/2 + r, n*0.56 + r*0.55], fill=(242, 180, 64))
        f = n * 0.11
        d.polygon([(n/2, n*0.22), (n/2 - f, n*0.44), (n/2, n*0.52), (n/2 + f, n*0.44)], fill=(224, 83, 47))
        im.save(os.path.join(out, f"icon-{n}.png"))


def build(packs, out, audio_paths=None, version="1"):
    """packs: pack dicts. audio_paths: {pack_id: path} for packs whose recording may be published."""
    os.makedirs(out, exist_ok=True)
    packs = copy.deepcopy(packs)
    files = []
    for p in packs:
        src = (audio_paths or {}).get(p["id"])
        if src and p.get("recording"):
            name = f"{p['id']}.mp3"
            shutil.copyfile(src, os.path.join(out, name))
            p["recording"]["src"] = name
            files.append(name)
    html, warns = htmlbuild.render(packs)
    html = html.replace("</head>", HEAD_EXTRA + "</head>", 1)
    html = html.replace("</body></html>", OFFLINE_JS.replace("__AUDIO_FILES__", json.dumps(files)) + "</body></html>")
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
    open(os.path.join(out, "sw.js"), "w").write(SW.replace("__VERSION__", str(version)))
    json.dump({"name": "Vāk Puja Reader", "short_name": "Vāk", "start_url": "./", "scope": "./",
               "display": "standalone", "background_color": "#1a120e", "theme_color": "#1a120e",
               "icons": [{"src": f"icon-{n}.png", "sizes": f"{n}x{n}", "type": "image/png"} for n in (192, 512)]},
              open(os.path.join(out, "manifest.webmanifest"), "w"), ensure_ascii=False)
    icons(out)
    open(os.path.join(out, ".nojekyll"), "w").close()
    return {"out": out, "audio": files, "warnings": warns}

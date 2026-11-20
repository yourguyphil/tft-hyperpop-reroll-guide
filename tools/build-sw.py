"""Write sw.js with a precache list of every site file (run after changing assets)."""
import sys, os, hashlib, json
root = sys.argv[1]
files = ["./", "index.html", "manifest.json", "favicon.ico"]
files += sorted(f for f in os.listdir(root) if f.endswith(".pdf"))
for d, _, fs in os.walk(os.path.join(root, "assets")):
    for f in sorted(fs):
        files.append(os.path.relpath(os.path.join(d, f), root).replace("\\", "/"))
h = hashlib.sha1()
for f in files[1:]:
    h.update(open(os.path.join(root, f), "rb").read())
version = h.hexdigest()[:10]
sw = f"""// Auto-generated. Caches the whole site so it works offline once installed.
const CACHE = "{os.path.basename(os.path.abspath(root))}-{version}";
const PRECACHE = {json.dumps(files, indent=0)};

self.addEventListener("install", e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
}});

self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
}});

self.addEventListener("fetch", e => {{
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // Page: network first (fresh content), fall back to cache offline.
  if (req.mode === "navigate") {{
    e.respondWith(fetch(req).then(r => {{ caches.open(CACHE).then(c => c.put("index.html", r.clone())); return r; }})
      .catch(() => caches.match("index.html")));
    return;
  }}
  // Everything else (images, fonts): cache first, then network + store.
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {{
    if (r.ok || r.type === "opaque") {{ const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }}
    return r;
  }})));
}});
"""
open(os.path.join(root, "sw.js"), "w", encoding="utf8", newline="\n").write(sw)
print(len(files), "files, version", version)

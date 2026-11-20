"""Build a single self-contained HTML file with every image embedded (data URIs).

Usage:
    python tools/build-standalone.py [site_dir]   # -> <site-folder-name>.html

Use it when the separate asset files can't load: opening the file from a viewer that
blocks local files, emailing it, or putting it on a USB stick. index.html (with the
assets/ folder) is still the version to host.
"""
import base64, json, os, re

import sys
ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
SRC = os.path.join(ROOT, "index.html")
OUT = os.path.join(ROOT, os.path.basename(os.path.normpath(ROOT)) + ".html")
MIME = {".png": "image/png", ".webp": "image/webp", ".svg": "image/svg+xml", ".ico": "image/x-icon"}

def data_uri(rel):
    path = os.path.join(ROOT, rel.replace("/", os.sep))
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as f:
        return f"data:{MIME[ext]};base64," + base64.b64encode(f.read()).decode("ascii")

h = open(SRC, encoding="utf8").read()

# every asset file in the site (JS builds some paths at runtime, so embed them all)
assets = {}
for d, _, files in os.walk(os.path.join(ROOT, "assets")):
    for fn in files:
        if os.path.splitext(fn)[1].lower() in MIME:
            rel = os.path.relpath(os.path.join(d, fn), ROOT).replace("\\", "/")
            assets[rel] = data_uri(rel)

# 1) static references in HTML attributes
h = re.sub(r'(src|href)="(assets/[^"]+)"', lambda m: f'{m.group(1)}="{assets.get(m.group(2), m.group(2))}"', h)
if os.path.exists(os.path.join(ROOT, "favicon.ico")):
    h = h.replace('href="favicon.ico"', f'href="{data_uri("favicon.ico")}"')
# drop PWA bits that need a server
h = re.sub(r'<link rel="manifest"[^>]*>\n?', "", h)

# 2) runtime: rewrite any <img> whose src starts with assets/ to the embedded copy
shim = """<script>
window.__ASSETS__ = %s;
(function(){
  const A = window.__ASSETS__;
  const fix = img => { const s = img.getAttribute("src"); if (s && A[s]) img.setAttribute("src", A[s]); };
  const scan = root => { if (root.tagName === "IMG") fix(root); root.querySelectorAll && root.querySelectorAll("img[src^='assets/']").forEach(fix); };
  new MutationObserver(ms => ms.forEach(m => {
    if (m.type === "attributes") fix(m.target); else m.addedNodes.forEach(n => n.nodeType === 1 && scan(n));
  })).observe(document.documentElement, {subtree: true, childList: true, attributes: true, attributeFilter: ["src"]});
})();
</script>
""" % json.dumps(assets)
h = h.replace("<body>", "<body>\n" + shim, 1)

with open(OUT, "w", encoding="utf8", newline="\n") as f:
    f.write(h)
print(f"wrote {os.path.relpath(OUT, ROOT)}  ({len(h)/1e6:.1f} MB, {len(assets)} images embedded)")

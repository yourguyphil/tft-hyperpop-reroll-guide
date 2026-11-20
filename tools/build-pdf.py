"""Build a printable PDF from print/outline.md.

Run from the site folder:  python tools/build-pdf.py   (output: <site-folder-name>.pdf)
Unit names/costs come from print/units.json:  {"malzahar": ["Malzahar", 3], ...}

Usage:
    python tools/build-pdf.py                 # -> <site-folder-name>.pdf
    python tools/build-pdf.py --html-only     # just write print/_build.html (open it to preview)
    python tools/build-pdf.py --a4            # A4 instead of US Letter

Needs Microsoft Edge or Google Chrome installed (used headless to print). No pip installs.
"""
import html, os, re, shutil, subprocess, sys

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.getcwd()
SRC = os.path.join(ROOT, "print", "outline.md")
OUT_HTML = os.path.join(ROOT, "print", "_build.html")
OUT_PDF = os.path.join(ROOT, os.path.basename(os.path.normpath(ROOT)) + ".pdf")
A = "../assets"  # asset path relative to print/_build.html

# ---------------------------------------------------------------- data
UNITS = {}  # filled from print/units.json
_uj = os.path.join(ROOT, "print", "units.json")
if os.path.exists(_uj):
    import json as _json
    UNITS = {k: tuple(v) for k, v in _json.load(open(_uj, encoding="utf8")).items()}
COMP = {  # key: (short name, file)
    "sword": ("Sword", "bfsword"), "bow": ("Bow", "recurvebow"), "rod": ("Rod", "needlesslylargerod"),
    "tear": ("Tear", "tearofthegoddess"), "vest": ("Vest", "chainvest"), "cloak": ("Cloak", "negatroncloak"),
    "belt": ("Belt", "giantsbelt"), "gloves": ("Gloves", "sparringgloves"),
}
ITEMS = {  # key: (name, file, compA, compB)  Set 18 recipes
    "deathblade": ("Deathblade", "deathblade", "sword", "sword"),
    "giantslayer": ("Giant Slayer", "madredsbloodrazor", "sword", "bow"),
    "gunblade": ("Hextech Gunblade", "hextechgunblade", "sword", "rod"),
    "shojin": ("Spear of Shojin", "spearofshojin", "sword", "tear"),
    "eon": ("Edge of Night", "guardianangel", "sword", "vest"),
    "bt": ("Bloodthirster", "bloodthirster", "sword", "cloak"),
    "sterak": ("Sterak's Gage", "steraksgage", "sword", "belt"),
    "ie": ("Infinity Edge", "infinityedge", "sword", "gloves"),
    "redbuff": ("Red Buff", "rapidfirecannon", "bow", "bow"),
    "guinsoo": ("Guinsoo's Rageblade", "guinsoosrageblade", "bow", "rod"),
    "voidstaff": ("Void Staff", "voidstaff", "bow", "tear"),
    "titans": ("Titan's Resolve", "titansresolve", "bow", "vest"),
    "kraken": ("Kraken's Fury", "krakenslayer", "bow", "cloak"),
    "nashor": ("Nashor's Tooth", "leviathan", "bow", "belt"),
    "lw": ("Last Whisper", "lastwhisper", "bow", "gloves"),
    "rabadon": ("Rabadon's Deathcap", "rabadonsdeathcap", "rod", "rod"),
    "archangel": ("Archangel's Staff", "archangelsstaff", "rod", "tear"),
    "crownguard": ("Crownguard", "crownguard", "rod", "vest"),
    "ionic": ("Ionic Spark", "ionicspark", "rod", "cloak"),
    "morello": ("Morellonomicon", "morellonomicon", "rod", "belt"),
    "jg": ("Jeweled Gauntlet", "jeweledgauntlet", "rod", "gloves"),
    "bluebuff": ("Blue Buff", "bluebuff", "tear", "tear"),
    "vow": ("Protector's Vow", "frozenheart", "tear", "vest"),
    "helm": ("Adaptive Helm", "adaptivehelm", "tear", "cloak"),
    "visage": ("Spirit Visage", "spiritvisagerr", "tear", "belt"),
    "hoj": ("Hand of Justice", "unstableconcoction", "tear", "gloves"),
    "bramble": ("Bramble Vest", "bramblevest", "vest", "vest"),
    "gargoyle": ("Gargoyle Stoneplate", "gargoylestoneplate", "vest", "cloak"),
    "sunfire": ("Sunfire Cape", "redbuff", "vest", "belt"),
    "steadfast": ("Steadfast Heart", "nightharvester", "vest", "gloves"),
    "dclaw": ("Dragon's Claw", "dragonsclaw", "cloak", "cloak"),
    "evenshroud": ("Evenshroud", "spectralgauntlet", "cloak", "belt"),
    "qss": ("Quicksilver", "quicksilver", "cloak", "gloves"),
    "warmog": ("Warmog's Armor", "warmogsarmor", "belt", "belt"),
    "flail": ("Striker's Flail", "powergauntlet", "belt", "gloves"),
    "thief": ("Thief's Gloves", "thiefsgloves", "gloves", "gloves"),
}
COST_COLORS = {1: "#8a94a3", 2: "#1fa85a", 3: "#2f7fe6", 4: "#a63ee0", 5: "#e09a10", 6: "#e8364f", 7: "#e8364f", 8: "#e8364f"}

# ---------------------------------------------------------------- shortcodes
def warn(msg):
    print("  ! " + msg, file=sys.stderr)

def cost_chip(c):
    return f'<span class="cc" style="background:{COST_COLORS[int(c)]}">{c}g</span>'

def unit_img(k, cls="up"):
    if k not in UNITS:
        warn(f"unknown unit '{k}'"); return f"[{k}?]"
    n, c = UNITS[k]
    return f'<img class="{cls}" src="{A}/units-sq/{k}.png" alt="{n}" style="border-color:{COST_COLORS[c]}">'

def comp_img(k):
    if k not in COMP:
        warn(f"unknown component '{k}'"); return f"[{k}?]"
    return f'<img class="ic" src="{A}/items/{COMP[k][1]}.png" alt="{COMP[k][0]}">'

def shortcode(m):
    kind, arg = m.group(1), m.group(2)
    if kind == "u":
        if arg not in UNITS: return unit_img(arg)
        n, c = UNITS[arg]
        return f'<span class="u">{unit_img(arg)}<b>{n}</b>{cost_chip(c)}</span>'
    if kind == "units":
        return '<span class="urow">' + "".join(unit_img(k.strip()) for k in arg.split(",")) + "</span>"
    if kind == "big":
        if arg not in UNITS: return unit_img(arg)
        return f'<img class="big" src="{A}/units-sq/{arg}.png" alt="" style="border-color:{COST_COLORS[UNITS[arg][1]]}">'
    if kind == "c":
        return f'<span class="cp">{comp_img(arg)}{COMP.get(arg, (arg,))[0]}</span>'
    if kind == "ci":
        return comp_img(arg)
    if kind == "ii":
        if arg not in ITEMS: warn(f"unknown item '{arg}'"); return f"[{arg}?]"
        return f'<img class="ic" src="{A}/items/{ITEMS[arg][1]}.png" alt="{ITEMS[arg][0]}">'
    if kind == "i":
        if arg not in ITEMS: warn(f"unknown item '{arg}'"); return f"[{arg}?]"
        n, f, *_ = ITEMS[arg]
        return f'<span class="it"><img class="ic" src="{A}/items/{f}.png" alt="">{n}</span>'
    if kind == "r":
        if arg not in ITEMS: warn(f"unknown item '{arg}'"); return f"[{arg}?]"
        n, f, a, b = ITEMS[arg]
        return (f'<span class="rec">{comp_img(a)}{COMP[a][0]}<i>+</i>{comp_img(b)}{COMP[b][0]}'
                f'<i>=</i><img class="ic" src="{A}/items/{f}.png" alt=""><b>{n}</b></span>')
    if kind == "t":
        return (f'<img class="ic tr" src="{A}/traits/{arg}.svg" alt="">' if os.path.exists(os.path.join(ROOT, "assets", "traits", arg + ".svg")) else f'<img class="ic tr" src="{A}/traits/{arg}.png" alt="">')
    if kind == "a":
        f, _, n = arg.partition("|")
        tr = " tr" if "traits/" in f else ""
        return f'<span class="it"><img class="ic{tr}" src="{A}/augments/{f}.png" alt="">{n}</span>'
    if kind == "cost":
        return cost_chip(arg)
    warn(f"unknown shortcode {{{kind}:{arg}}}")
    return m.group(0)

def inline(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"\{(\w+):([^}]+)\}", shortcode, t)
    t = t.replace("{br}", "<br>")
    return t

# ---------------------------------------------------------------- block parser
def parse(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    # stack of containers: each = {"kind", "cls", "cols": [[html,...], ...]}
    root = {"kind": "root", "cls": "", "cols": [[]]}
    stack = [root]
    para, items = [], []

    def out(s):
        stack[-1]["cols"][-1].append(s)

    def flush():
        nonlocal para, items
        if para:
            out("<p>" + inline(" ".join(para)) + "</p>"); para = []
        if items:
            out("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>"); items = []

    def render(c):
        cols = ["".join(col) for col in c["cols"]]
        if c["kind"] in ("cols", "cols3"):
            return f'<div class="{c["kind"]}">' + "".join(f"<div>{x}</div>" for x in cols) + "</div>"
        return f'<div class="box {c["cls"]}">' + "".join(cols) + "</div>"

    for raw in md.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if s.startswith(":::"):
            flush()
            arg = s[3:].strip()
            if arg:
                kind, _, cls = arg.partition(" ")
                stack.append({"kind": kind, "cls": cls or "plain", "cols": [[]]})
            else:
                if len(stack) == 1: warn("stray ':::'"); continue
                c = stack.pop(); out(render(c))
            continue
        if s == "|||":
            flush()
            for c in reversed(stack):
                if c["kind"] in ("cols", "cols3"):
                    c["cols"].append([]); break
            continue
        if s == "---page---":
            flush(); out('<div class="pb"></div>'); continue
        if not s:
            flush(); continue
        m = re.match(r"(#{1,3})\s+(.*)", s)
        if m:
            flush(); n = len(m.group(1)); out(f"<h{n}>{inline(m.group(2))}</h{n}>"); continue
        if s.startswith("- "):
            if para: flush()
            items.append(s[2:]); continue
        if s.startswith("> "):
            flush(); out(f'<p class="note">{inline(s[2:])}</p>'); continue
        if items:  # continuation of previous bullet
            items[-1] += " " + s; continue
        para.append(s)
    flush()
    while len(stack) > 1:
        warn("unclosed ':::' block"); c = stack.pop(); out(render(c))
    return "".join(root["cols"][0])

# ---------------------------------------------------------------- page
CSS = """
@page { size: %(size)s; margin: 0.42in 0.45in; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 10.5pt/1.4 Inter, "Segoe UI", system-ui, sans-serif; color: #18202e; }
h1, h2, h3 { font-family: Cinzel, Georgia, serif; margin: 0; line-height: 1.15; }
h1 { font-size: 22pt; margin: 2px 0 2px; display: flex; align-items: center; gap: 10px;
     background: linear-gradient(90deg, #7c3aed, #db2777); -webkit-background-clip: text; background-clip: text; color: transparent; }
h1 img { -webkit-text-fill-color: initial; }
h2 { font-size: 13pt; margin: 14px 0 6px; padding-bottom: 3px; border-bottom: 2px solid #e4e8ef; display: flex; align-items: center; gap: 6px; }
h3 { font-size: 11pt; margin: 8px 0 5px; display: flex; align-items: center; gap: 5px; flex-wrap: wrap; }
p { margin: 4px 0; }
p.note { color: #667185; font-size: 9.5pt; margin: 0 0 8px; }
ul { list-style: none; margin: 4px 0; padding: 0; display: grid; gap: 5px; }
li { padding: 5px 9px; background: #f4f6fa; border-radius: 7px; break-inside: avoid; line-height: 1.75; }
li img, li .u, li .urow, li .rec, li .cp, li .it { vertical-align: middle; }
.u, .urow, .cp, .it { margin-right: 2px; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.cols3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
.cols > div, .cols3 > div { min-width: 0; }
.box { border-radius: 10px; padding: 8px 12px; margin: 6px 0; border: 1.5px solid #dfe3ea; break-inside: avoid; }
.box.teal { border-color: #8b5cf6; background: #f4efff; }
.box.red  { border-color: #db2777; background: #fdeef6; }
.box.tank { border-color: #6a8ff0; background: #eef2fe; }
.box.gold { border-color: #e0aa2c; background: #fdf7e6; }
.box li { background: rgba(255,255,255,.75); }
.box h3 { margin-top: 2px; }
img.ic { width: 18px; height: 18px; border-radius: 4px; vertical-align: middle; }
img.tr { filter: brightness(0); }
h2 img.tr, h1 img.tr { width: 20px; height: 20px; }
img.up { width: 22px; height: 22px; border-radius: 5px; border: 2px solid; vertical-align: middle; }
img.big { width: 46px; height: 46px; border-radius: 9px; border: 2px solid; object-fit: cover; }
h1 img.big { width: 40px; height: 40px; }
.u { display: inline-flex; align-items: center; gap: 5px; }
.u b { font-weight: 700; }
.urow { display: inline-flex; gap: 3px; }
.cc { display: inline-block; font: 800 8pt Inter, sans-serif; color: #fff; padding: 0 5px; border-radius: 4px; line-height: 14px; }
.cp, .it { display: inline-flex; align-items: center; gap: 4px; }
.rec { display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; }
.rec i { font-style: normal; color: #99a1b0; font-weight: 800; }
.rec b { font-weight: 700; }
.pb { break-after: page; height: 0; }
.box.items li { line-height: 1.35; padding: 4px 8px; font-size: 9pt; }
.box.items ul { gap: 4px; }
.box.items h2 { font-size: 11.5pt; margin: 8px 0 5px; }
.box.items li .rec { margin-bottom: 2px; }
.box.items { border: 0; padding: 0; background: none; margin: 0; }
.why { color: #0b6f74; font-weight: 700; } .does { color: #5b6476; font-weight: 700; }
.foot { margin-top: 14px; color: #99a1b0; font-size: 8pt; }
"""

TITLE = os.path.basename(ROOT).replace("-", " ").title()

def build(size):
    with open(SRC, encoding="utf8") as f:
        body = parse(f.read())
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>{TITLE}</title>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800&family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>{CSS % {"size": size}}</style></head><body>{body}
<div class="foot">{TITLE} · data from Riot game files via CommunityDragon · not endorsed by Riot Games.</div>
</body></html>"""
    with open(OUT_HTML, "w", encoding="utf8") as f:
        f.write(page)
    print("wrote", os.path.relpath(OUT_HTML, ROOT))

def find_browser():
    cands = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for c in cands:
        if os.path.exists(c): return c
    for name in ("msedge", "google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p: return p
    return None

def to_pdf():
    b = find_browser()
    if not b:
        sys.exit("No Edge/Chrome found. Open print/_build.html in a browser and use Print → Save as PDF.")
    url = "file:///" + OUT_HTML.replace("\\", "/").lstrip("/")
    cmd = [b, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=6000",
           f"--print-to-pdf={OUT_PDF}", url]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("wrote", os.path.relpath(OUT_PDF, ROOT))

if __name__ == "__main__":
    build("A4" if "--a4" in sys.argv else "Letter")
    if "--html-only" not in sys.argv:
        to_pdf()

"""Baixa as páginas do espaço webPosto do Confluence (HTML renderizado + anexos de imagem)."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, unquote

BASE = "https://qualityautomacao.atlassian.net"
SPACE_ID = "1179672"
OUT = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(f"{OUT}/pages", exist_ok=True)
os.makedirs(f"{OUT}/assets", exist_ok=True)

def get(url, dest=None):
    args = ["curl", "-sS", "-L", "--fail", "--retry", "3", url]
    if dest:
        args += ["-o", dest]
        return subprocess.run(args).returncode == 0
    return subprocess.check_output(args)

# 1. lista de páginas
pages, url = [], f"{BASE}/wiki/api/v2/spaces/{SPACE_ID}/pages?limit=250&status=current"
while url:
    r = json.loads(get(url)); pages += r["results"]
    n = r.get("_links", {}).get("next"); url = BASE + n if n else None
json.dump(pages, open(f"{OUT}/pages.json", "w"), ensure_ascii=False)
print("páginas:", len(pages))

# 2. corpo de cada página (pula se versão não mudou)
def fetch_page(p):
    f = f"{OUT}/pages/{p['id']}.json"
    ver = p.get("version", {}).get("number")
    if os.path.exists(f):
        old = json.load(open(f))
        if old.get("version", {}).get("number") == ver: return old
    d = json.loads(get(f"{BASE}/wiki/rest/api/content/{p['id']}?expand=body.export_view,version"))
    json.dump(d, open(f, "w"), ensure_ascii=False)
    return d
with ThreadPoolExecutor(12) as ex:
    bodies = list(ex.map(fetch_page, pages))
print("corpos baixados")

# 3. imagens/anexos referenciados
srcs = set()
for d in bodies:
    for m in re.finditer(r'(?:src|href)="(https://qualityautomacao\.atlassian\.net/wiki/download/[^"]+)"', d["body"]["export_view"]["value"]):
        srcs.add(m.group(1).replace("&amp;", "&"))
    v = d["body"]["export_view"]["value"]
    for m in re.finditer(r'preview=%2F(\d+)%2F\d+%2F([^"&]+)', v):
        srcs.add(f"{BASE}/wiki/download/attachments/{m.group(1)}/{m.group(2).replace('+', '%20')}")
    for tag in re.findall(r'<img[^>]+(?:api\.media|media-cdn)\.atlassian\.com[^>]*>', v):
        nm = re.search(r'[?&;]name=([^"&]+)', tag) or re.search(r'alt="([^"]+\.(?:png|jpe?g|gif|webp))"', tag)
        if nm:
            srcs.add(f"{BASE}/wiki/download/attachments/{d['id']}/{nm.group(1)}")
def asset_path(u):
    path = unquote(urlparse(u).path).split("/wiki/download/")[1]
    path = re.sub(r"[^\w./-]+", "_", path)
    return path
def fetch_asset(u):
    dest = f"{OUT}/assets/{asset_path(u)}"
    if os.path.exists(dest): return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    return get(u, dest)
with ThreadPoolExecutor(12) as ex:
    ok = list(ex.map(fetch_asset, sorted(srcs)))
print("anexos:", len(srcs), "falhas:", ok.count(False))

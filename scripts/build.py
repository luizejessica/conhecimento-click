"""Gera o portal estático conhecimento.click a partir do cache do Confluence.

Uso:
    python3 scripts/build.py                # gera _site/ (vídeos apontam para VIDEO_BASE)
    VIDEO_BASE=https://videos.conhecimento.click python3 scripts/build.py
    python3 scripts/build.py --with-videos  # copia os vídeos para _site/videos (servidor próprio)
"""
import hashlib, html, json, os, re, shutil, sys, unicodedata
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, Comment, NavigableString

sys.path.insert(0, os.path.dirname(__file__))
import config as C

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE = f"{ROOT}/cache"
OUT = f"{ROOT}/_site"
WITH_VIDEOS = "--with-videos" in sys.argv
VIDEO_BASE = os.environ.get("VIDEO_BASE", C.VIDEO_BASE).rstrip("/")

IMG_EXT = {"png", "jpg", "jpeg", "gif", "webp", "bmp", "svg"}
VID_EXT = {"mp4", "webm", "mkv", "mov", "avi"}
EMOJI = {"information": "ℹ️", "info": "ℹ️", "plus": "➕", "minus": "➖", "tick": "✅", "cross": "❌",
         "warning": "⚠️", "error": "⚠️", "light-on": "💡", "light-off": "💡", "question": "❓",
         "star": "⭐", "blue-star": "⭐", "smile": "🙂", "thumbs-up": "👍", "cog": "⚙️"}


# ---------------------------------------------------------------- dados
def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70] or "pagina"


pages = json.load(open(f"{CACHE}/pages.json"))
byid = {p["id"]: p for p in pages}
children = {}
for p in pages:
    children.setdefault(p.get("parentId"), []).append(p)
for v in children.values():
    v.sort(key=lambda x: (x.get("position") or 0, x["title"]))

excluded = set()
def exclude_tree(pid):
    excluded.add(pid)
    for c in children.get(pid, []):
        exclude_tree(c["id"])
for pid in C.EXCLUDE_IDS:
    if pid in byid:
        exclude_tree(pid)

HOME = C.HOME_ID
included = [p for p in pages if p["id"] not in excluded and p["id"] != HOME]
inc_ids = {p["id"] for p in included}

def url_of(pid):
    return f"/artigo/{pid}-{slugify(byid[pid]['title'])}/"

def ancestors(pid):
    out, cur = [], byid[pid].get("parentId")
    while cur and cur in byid and cur != HOME:
        out.insert(0, cur)
        cur = byid[cur].get("parentId")
    return out

def kids(pid):
    return [c for c in children.get(pid, []) if c["id"] in inc_ids]

def count_desc(pid):
    return sum(1 + count_desc(c["id"]) for c in kids(pid))

categories = kids(HOME)

def meta(pid):
    d = json.load(open(f"{CACHE}/pages/{pid}.json"))
    return d


# ---------------------------------------------------------------- mídia
def asset_rel(u):
    path = unquote(urlparse(u).path).split("/wiki/download/")[1]
    return re.sub(r"[^\w./-]+", "_", path)

def ext_of(rel):
    name = rel.rsplit("/", 1)[-1].lower()
    exts = re.findall(r"\.([a-z0-9]{2,4})(?=_|$)", name)
    known = [e for e in exts if e in IMG_EXT | VID_EXT | {"pdf", "zip", "rar", "exe", "msi", "xlsx", "xls", "docx", "doc", "csv", "txt", "xml", "sql", "bat", "ini"}]
    return known[-1] if known else (exts[-1] if exts else "")

images_needed = {}   # rel -> out name
videos_needed = set()
files_needed = {}

def image_url(rel):
    h = hashlib.sha1(rel.encode()).hexdigest()[:16]
    ext = ext_of(rel)
    if ext == "gif":
        src = f"{CACHE}/assets/{rel}"
        big = os.path.exists(src) and os.path.getsize(src) > 4_000_000
        name = f"{h}.mp4" if big else f"{h}.gif"
    else:
        name = f"{h}.webp"
    images_needed[rel] = name
    return f"/midia/{name}"

def video_url(rel):
    videos_needed.add(rel)
    return f"{VIDEO_BASE}/{rel}"

def file_url(rel):
    name = re.sub(r"[^\w.-]+", "_", rel.replace("attachments/", "").replace("/", "_"))
    files_needed[rel] = name
    return f"/arquivos/{name}"


# ---------------------------------------------------------------- limpeza do HTML
def clean(body_html, pid):
    s = BeautifulSoup(body_html, "html.parser")
    for t in s.find_all(["style", "script", "form", "colgroup"]):
        t.decompose()
    for c in s.find_all(string=lambda x: isinstance(x, Comment)):
        c.extract()
    for t in s.select(".confluence-jim-macro, .search-macro, .aui-icon, .expand-control-icon, .expand-control-image"):
        t.decompose()

    # emoticons
    for img in s.select("img.emoticon"):
        fb = img.get("data-emoji-fallback", "")
        if fb.startswith(":") or not fb:
            fb = EMOJI.get(img.get("data-emoticon-name", ""), "")
        img.replace_with(fb)

    # imagens e vídeos incorporados
    for img in s.find_all("img"):
        src = img.get("src", "")
        if "/wiki/download/" in src:
            rel = asset_rel(src)
            ext = ext_of(rel)
            alt = img.get("alt", "")
            if ext in VID_EXT:
                v = s.new_tag("video", controls="", preload="none", playsinline="")
                v["src"] = video_url(rel)
                fig = s.new_tag("figure", attrs={"class": "media-video"})
                fig.append(v)
                cap = s.new_tag("figcaption")
                a = s.new_tag("a", href=video_url(rel), download="")
                a.string = "Baixar vídeo"
                cap.append(a)
                fig.append(cap)
                (img.find_parent("span", class_="confluence-embedded-file-wrapper") or img).replace_with(fig)
                continue
            iu = image_url(rel)
            if iu.endswith(".mp4"):
                v = s.new_tag("video", src=iu, autoplay="", muted="", loop="", playsinline="", preload="metadata")
                v["title"] = alt
                (img.find_parent("span", class_="confluence-embedded-file-wrapper") or img).replace_with(v)
                continue
            new = s.new_tag("img", src=iu, alt=alt if not re.search(r"\.(png|jpe?g|gif)$", alt, re.I) else "",
                            loading="lazy", decoding="async")
            if img.get("width"):
                new["style"] = f"max-width:min(100%,{img['width']}px)"
            wrap = img.find_parent("span", class_="confluence-embedded-file-wrapper")
            if wrap and wrap.find_parent("a") is None:
                a = s.new_tag("a", href=new["src"], attrs={"class": "zoom"})
                a.append(new)
                new = a
            img.replace_with(new)
        elif re.search(r"(api\.media|media-cdn)\.atlassian\.com", src):
            nm = re.search(r"[?&]name=([^&]+)", src.replace("&amp;", "&")) or re.fullmatch(r"(.+\.(?:png|jpe?g|gif|webp))", img.get("alt", ""), re.I)
            if nm and not nm.group(1).lower().endswith(".pdf"):
                rel = asset_rel(f"https://x.atlassian.net/wiki/download/attachments/{pid}/{nm.group(1)}")
                if os.path.exists(f"{CACHE}/assets/{rel}"):
                    img.replace_with(s.new_tag("img", src=image_url(rel), alt="", loading="lazy", decoding="async"))
                    continue
            img.decompose()
        elif src.startswith("http") and "atlassian.net" in src:
            img.decompose()

    # links
    for a in s.find_all("a"):
        href = a.get("href", "")
        lid = a.get("data-linked-resource-id")
        m = re.search(r"atlassian\.net/wiki/(?:spaces/[^/]+/pages|pages/viewpage\.action\?pageId=)/?(\d+)", href)
        target = lid if (lid and a.get("data-linked-resource-type") == "page") else (m.group(1) if m else None)
        if "user-mention" in (a.get("class") or []) or "confluence-userlink" in (a.get("class") or []):
            a.unwrap(); continue
        if target:
            if target in inc_ids:
                frag = href.split("#", 1)[1] if "#" in href else ""
                a.attrs = {"href": url_of(target) + (f"#{frag}" if frag else "")}
            else:
                a.unwrap()
            continue
        pv = re.search(r"preview=%2F(\d+)%2F\d+%2F([^&]+)", href)
        if pv:
            href = f"https://x.atlassian.net/wiki/download/attachments/{pv.group(1)}/{pv.group(2).replace('+', '%20')}"
        if "/wiki/download/" in href:
            rel = asset_rel(href)
            ext = ext_of(rel)
            if ext in VID_EXT:
                a.attrs = {"href": video_url(rel)}
            elif ext in IMG_EXT:
                a.attrs = {"href": image_url(rel), "class": "zoom"}
            elif os.path.exists(f"{CACHE}/assets/{rel}") and os.path.getsize(f"{CACHE}/assets/{rel}") > 24_000_000:
                a.attrs = {"href": video_url(rel), "download": ""}   # grande demais para o Pages: vai junto com os vídeos
            elif os.path.exists(f"{CACHE}/assets/{rel}"):
                a.attrs = {"href": file_url(rel), "download": ""}
            else:
                a.unwrap()
            continue
        if "atlassian.net" in href or "localhost" in href:
            a.unwrap(); continue
        if href.startswith("http"):
            a.attrs = {"href": href, "target": "_blank", "rel": "noopener"}

    # URLs internas (Jira/Confluence) escritas como texto
    ATL = re.compile(r"https?://[\w.-]*atlassian\.(?:net|com)\S*")
    for tr in s.find_all("tr"):
        cells = tr.find_all(["td", "th"], recursive=False)
        if len(cells) == 2 and ATL.fullmatch(cells[1].get_text(strip=True) or "-"):
            tr.decompose()
    for t in s.find_all(string=ATL):
        t.replace_with(ATL.sub("", str(t)))

    # caixas de informação
    kinds = {"information": "info", "info": "info", "note": "note", "warning": "warning", "tip": "tip"}
    for d in s.select("div.confluence-information-macro"):
        k = next((kinds[c.split("-")[-1]] for c in d["class"] if c.startswith("confluence-information-macro-") and c.split("-")[-1] in kinds), "info")
        body = d.select_one(".confluence-information-macro-body") or d
        new = s.new_tag("aside", attrs={"class": f"callout callout-{k}"})
        for ch in list(body.contents):
            new.append(ch.extract())
        d.replace_with(new)
    for d in s.select("div.panel"):
        body = d.select_one(".panelContent") or d
        new = s.new_tag("aside", attrs={"class": "callout callout-panel"})
        hdr = d.select_one(".panelHeader")
        if hdr:
            b = s.new_tag("p"); st = s.new_tag("strong"); st.string = hdr.get_text(" ", strip=True); b.append(st); new.append(b)
        for ch in list(body.contents):
            new.append(ch.extract())
        d.replace_with(new)

    # expandir
    for d in s.select("div.expand-container"):
        det = s.new_tag("details", attrs={"class": "expand"})
        sm = s.new_tag("summary")
        sm.string = (d.select_one(".expand-control-text") or d).get_text(" ", strip=True)[:200] or "Mostrar mais"
        det.append(sm)
        content = d.select_one(".expand-content")
        if content:
            for ch in list(content.contents):
                det.append(ch.extract())
        d.replace_with(det)

    # código
    for pre in s.select("pre.syntaxhighlighter-pre"):
        pre.attrs = {}
        code = s.new_tag("code")
        code.string = pre.get_text()
        pre.clear(); pre.append(code)
    for d in s.select("div.code, div.codeContent"):
        d.unwrap()

    # tabelas
    for t in s.find_all("table"):
        t.attrs = {}
        parent = t.parent
        if not (parent and parent.name == "div" and "table-wrap" in (parent.get("class") or [])):
            w = s.new_tag("div", attrs={"class": "table-wrap"})
            t.wrap(w)
    for d in s.select("div.table-wrap"):
        d.attrs = {"class": "table-wrap"}

    # iframes (YouTube)
    for f in s.find_all("iframe"):
        src = f.get("src", "")
        if not src.startswith("https://"):
            f.decompose(); continue
        f.attrs = {"src": src, "loading": "lazy", "allowfullscreen": "", "title": "Vídeo"}
        w = s.new_tag("div", attrs={"class": "embed"})
        f.wrap(w)

    for t in s.select(".inline-comment-marker, .confluence-embedded-file-wrapper, .innerCell"):
        t.unwrap()

    # atributos
    keep = {"href", "src", "alt", "id", "class", "colspan", "rowspan", "controls", "preload", "playsinline", "autoplay", "muted", "loop",
            "loading", "decoding", "title", "target", "rel", "download", "allowfullscreen", "style", "open", "start"}
    ok_class = re.compile(r"^(callout.*|expand|table-wrap|embed|zoom|media-video|columnLayout|cell|two-equal|three-equal|"
                          r"two-left-sidebar|two-right-sidebar|three-with-sidebars|fixed-width|full-width|toc-macro|toc-indentation|aside|numberingColumn)$")
    for t in s.find_all(True):
        for k in list(t.attrs):
            if k not in keep:
                del t[k]
        if "class" in t.attrs:
            cls = [c for c in t["class"] if ok_class.match(c)]
            if cls: t["class"] = cls
            else: del t["class"]
        if "style" in t.attrs and t.name != "img":
            del t["style"]
    for t in s.find_all("span"):
        if not t.attrs:
            t.unwrap()
    # parágrafos vazios
    for p in s.find_all("p"):
        if not p.get_text(strip=True) and not p.find(["img", "video", "iframe", "br"]):
            p.decompose()
    return str(s)


# ---------------------------------------------------------------- layout
CSS_VER = "1"

def esc(x):
    return html.escape(x, quote=True)

def fmt_date(iso):
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return d.strftime("%d/%m/%Y")
    except Exception:
        return ""

LOGO = ('<svg class="logo" viewBox="0 0 64 40" aria-hidden="true"><rect width="64" height="40" rx="8" fill="var(--navy)"/>'
        '<text x="9" y="29" font-family="Inter,Arial Black,sans-serif" font-weight="900" font-size="24" fill="#E30A0A">W</text>'
        '<text x="35" y="29" font-family="Inter,Arial Black,sans-serif" font-weight="900" font-size="24" fill="#fff">P</text></svg>')

def layout(title, body, description="", canonical="/", search_body=False, extra_head=""):
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{C.BASE_URL}{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#000B3D">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/pagefind/pagefind-ui.css">
<link rel="stylesheet" href="/assets/site.css?v={CSS_VER}">
<script>try{{var t=localStorage.getItem('tema');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
{extra_head}
</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="topbar">
  <div class="topbar-in">
    <a class="brand" href="/">{LOGO}<span><strong>{esc(C.BRAND)}</strong><small>Central de Ajuda</small></span></a>
    <button class="search-trigger" type="button" data-open-search aria-label="Buscar">
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M16.4 15l4 4-1.4 1.4-4-4A7.5 7.5 0 1 1 16.4 15zM10.5 16a5.5 5.5 0 1 0 0-11 5.5 5.5 0 0 0 0 11z"/></svg>
      <span>Buscar artigos…</span><kbd>/</kbd>
    </button>
    <button class="theme-toggle" type="button" aria-label="Alternar tema claro/escuro" data-theme-toggle>
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 3a9 9 0 1 0 9 9c0-.5 0-.9-.1-1.4A5.5 5.5 0 0 1 13.4 3.1L12 3z"/></svg>
    </button>
  </div>
</header>
<div class="search-modal" hidden data-search-modal>
  <div class="search-backdrop" data-close-search></div>
  <div class="search-panel" role="dialog" aria-label="Buscar na central de ajuda">
    <div id="busca"></div>
    <button class="search-close" type="button" data-close-search aria-label="Fechar">Esc</button>
  </div>
</div>
<main id="conteudo"{' data-pagefind-body' if search_body else ''}>
{body}
</main>
<footer class="footer">
  <div class="footer-in">
    <span>{LOGO}</span>
    <p>{esc(C.FOOTER_TEXT)}</p>
    <p class="muted">© {datetime.now().year} {esc(C.BRAND)} · {esc(C.DOMAIN)}</p>
  </div>
</footer>
<div class="lightbox" hidden data-lightbox><img alt=""></div>
<script src="/pagefind/pagefind-ui.js"></script>
<script src="/assets/site.js?v={CSS_VER}"></script>
</body>
</html>"""


def card_icon(title):
    t = title.lower()
    icons = [("pdv", "🖥️"), ("retaguarda", "🏢"), ("pay", "💳"), ("tef", "💳"), ("conveni", "🏪"), ("restaurante", "🍽️"),
             ("mobile", "📱"), ("android", "📱"), ("alerta", "🔔"), ("cota", "📊"), ("ia", "🤖"), ("oil", "🛢️"),
             ("frota", "🚚"), ("promo", "🏷️"), ("abastece", "⛽"), ("api", "🔌"), ("bi", "📈"), ("contábil", "🧾"),
             ("pagamentos", "💠"), ("integra", "🔗"), ("agendamento", "🗓️"), ("autoatendimento", "🙋")]
    for k, i in icons:
        if re.search(rf"\b{k}", t):
            return i
    return "📘"


def nav_tree(pid_root, current, path_ids):
    def rec(pid, depth):
        items = []
        for c in kids(pid):
            sub = kids(c["id"])
            cls = ' class="active"' if c["id"] == current else ""
            link = f'<a href="{url_of(c["id"])}"{cls}{" aria-current=\"page\"" if c["id"] == current else ""}>{esc(c["title"])}</a>'
            if sub:
                op = " open" if c["id"] in path_ids or c["id"] == current else ""
                items.append(f'<li><details{op}><summary>{link}</summary>{rec(c["id"], depth+1)}</details></li>')
            else:
                items.append(f"<li>{link}</li>")
        return f'<ul>{"".join(items)}</ul>'
    return rec(pid_root, 0)


def breadcrumb(pid):
    parts = ['<a href="/">Início</a>'] + [f'<a href="{url_of(a)}">{esc(byid[a]["title"])}</a>' for a in ancestors(pid)]
    return f'<nav class="crumbs" aria-label="Você está em" data-pagefind-ignore="all">{" <span>›</span> ".join(parts)}</nav>'


def text_excerpt(h, n=160):
    t = re.sub(r"\s+", " ", BeautifulSoup(h, "html.parser").get_text(" ")).strip()
    return (t[:n].rsplit(" ", 1)[0] + "…") if len(t) > n else t


def render_page(pid):
    d = meta(pid)
    p = byid[pid]
    body = clean(d["body"]["export_view"]["value"], pid)
    anc = ancestors(pid)
    cat = anc[0] if anc else pid
    path_ids = set(anc)
    updated = fmt_date(d.get("version", {}).get("when", ""))
    sub = kids(pid)
    sub_html = ""
    if sub:
        cards = "".join(
            f'<a class="sub-card" href="{url_of(c["id"])}"><span>{esc(c["title"])}</span>'
            f'{f"<small>{count_desc(c["id"])} artigos</small>" if kids(c["id"]) else ""}</a>' for c in sub)
        sub_html = f'<section class="subpages" data-pagefind-ignore="all"><h2>Nesta seção</h2><div class="sub-grid">{cards}</div></section>'
    is_empty = not BeautifulSoup(body, "html.parser").get_text(strip=True) and "<img" not in body and "<video" not in body
    side = (f'<aside class="sidebar" aria-label="Navegação da seção" data-pagefind-ignore="all"><details class="side-mobile" open>'
            f'<summary>{esc(byid[cat]["title"])}</summary>'
            f'<a class="side-root{" active" if pid == cat else ""}" href="{url_of(cat)}">{esc(byid[cat]["title"])}</a>'
            f'{nav_tree(cat, pid, path_ids)}</details></aside>')
    article = f"""
<div class="doc">
{side}
<article class="article">
  {breadcrumb(pid)}
  <h1 data-pagefind-meta="title">{esc(p['title'])}</h1>
  <p class="meta" data-pagefind-ignore>Atualizado em {updated}</p>
  <span hidden data-pagefind-filter="Produto">{esc(byid[cat]['title'])}</span>
  <div class="prose">{'' if is_empty else body}</div>
  {sub_html}
  <div class="feedback" data-pagefind-ignore>
    <p>Não encontrou o que precisava?</p>
    <a class="btn" href="{esc(C.SUPPORT_URL)}" target="_blank" rel="noopener">Falar com o suporte</a>
  </div>
</article>
</div>"""
    desc = text_excerpt(body) or f"{p['title']} — Central de Ajuda {C.BRAND}"
    out = layout(f"{p['title']} · Central de Ajuda {C.BRAND}", article, desc, url_of(pid), search_body=True)
    dest = f"{OUT}{url_of(pid)}index.html"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w").write(out)
    return pid, d.get("version", {}).get("when", ""), dict(images=dict(images_needed), videos=set(videos_needed), files=dict(files_needed))


def render_home(recent):
    cards = []
    for c in categories:
        n = count_desc(c["id"])
        top = kids(c["id"])[:4]
        links = "".join(f'<li><a href="{url_of(t["id"])}">{esc(t["title"])}</a></li>' for t in top)
        cards.append(f'''<div class="cat-card">
  <a class="cat-head" href="{url_of(c["id"])}"><span class="cat-ico" aria-hidden="true">{card_icon(c["title"])}</span>
  <span><strong>{esc(c["title"])}</strong><small>{n} artigo{"s" if n != 1 else ""}</small></span></a>
  {f"<ul>{links}</ul>" if links else ""}
</div>''')
    rec = "".join(f'<li><a href="{url_of(pid)}">{esc(byid[pid]["title"])}</a><small>{fmt_date(w)} · {esc(byid[ancestors(pid)[0]]["title"] if ancestors(pid) else "")}</small></li>' for pid, w in recent)
    body = f"""
<section class="hero">
  <div class="hero-in">
    <h1>Como podemos ajudar?</h1>
    <p>Tutoriais, configurações e soluções para todos os produtos {esc(C.BRAND)}.</p>
    <button class="hero-search" type="button" data-open-search>
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M16.4 15l4 4-1.4 1.4-4-4A7.5 7.5 0 1 1 16.4 15zM10.5 16a5.5 5.5 0 1 0 0-11 5.5 5.5 0 0 0 0 11z"/></svg>
      <span>Busque por “NFC-e”, “sangria”, “TEF”, “impressora”…</span>
    </button>
    <p class="hero-stats">{len(included)} artigos · {len(categories)} produtos e módulos</p>
  </div>
</section>
<section class="wrap">
  <h2 class="section-title">Navegue por produto</h2>
  <div class="cat-grid">{"".join(cards)}</div>
</section>
<section class="wrap recent">
  <h2 class="section-title">Atualizados recentemente</h2>
  <ul class="recent-list">{rec}</ul>
</section>"""
    open(f"{OUT}/index.html", "w").write(layout(f"Central de Ajuda {C.BRAND}", body,
        f"Base de conhecimento {C.BRAND}: tutoriais, configurações e solução de problemas.", "/"))


def render_404():
    body = '<section class="wrap notfound"><h1>Página não encontrada</h1><p>O artigo pode ter sido movido. Tente a busca ou volte para o início.</p><p><a class="btn" href="/">Ir para o início</a> <button class="btn btn-ghost" data-open-search>Buscar</button></p></section>'
    open(f"{OUT}/404.html", "w").write(layout("Página não encontrada", body, "", "/404.html"))


# ---------------------------------------------------------------- mídia (conversão)
def convert_image(args):
    rel, name = args
    src, dst = f"{CACHE}/assets/{rel}", f"{OUT}/midia/{name}"
    if os.path.exists(dst) or not os.path.exists(src):
        return os.path.exists(dst)
    from PIL import Image
    try:
        if name.endswith(".gif"):
            shutil.copyfile(src, dst); return True
        if name.endswith(".mp4"):
            import subprocess
            r = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-movflags", "faststart", "-pix_fmt", "yuv420p",
                                "-vf", "scale='min(1600,trunc(iw/2)*2)':-2", "-c:v", "libx264", "-crf", "26", "-an", dst])
            return r.returncode == 0
        im = Image.open(src)
        im = im.convert("RGBA") if im.mode in ("P", "LA", "RGBA") else im.convert("RGB")
        if im.width > 1600:
            im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        im.save(dst, "WEBP", quality=82, method=4)
        return True
    except Exception as e:
        print("imagem falhou:", rel, e)
        return False


def main():
    os.makedirs(OUT, exist_ok=True)
    for sub in ("artigo",):
        shutil.rmtree(f"{OUT}/{sub}", ignore_errors=True)
    os.makedirs(f"{OUT}/midia", exist_ok=True)
    os.makedirs(f"{OUT}/arquivos", exist_ok=True)
    os.makedirs(f"{OUT}/assets", exist_ok=True)
    for f in os.listdir(f"{ROOT}/static"):
        dst = f"{OUT}/assets/{f}" if f not in ("favicon.svg", "_headers", "_redirects", "robots.txt", "CNAME") else f"{OUT}/{f}"
        shutil.copyfile(f"{ROOT}/static/{f}", dst)

    with ProcessPoolExecutor() as ex:
        results = list(ex.map(render_page, [p["id"] for p in included], chunksize=8))
    imgs, vids, files = {}, set(), {}
    for _, _, m in results:
        imgs.update(m["images"]); vids |= m["videos"]; files.update(m["files"])
    recent = sorted(((pid, w) for pid, w, _ in results), key=lambda x: x[1], reverse=True)[:12]
    render_home(recent)
    render_404()

    with ProcessPoolExecutor() as ex:
        ok = list(ex.map(convert_image, imgs.items(), chunksize=16))
    for rel, name in files.items():
        if os.path.exists(f"{CACHE}/assets/{rel}"):
            shutil.copyfile(f"{CACHE}/assets/{rel}", f"{OUT}/arquivos/{name}")
    with open(f"{ROOT}/videos-para-upload.txt", "w") as f:
        f.write("\n".join(sorted(vids)))
    if WITH_VIDEOS:
        for rel in vids:
            src, dst = f"{CACHE}/assets/{rel}", f"{OUT}/videos/{rel}"
            if os.path.exists(src) and not os.path.exists(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                os.link(src, dst)

    urls = ["/"] + [url_of(p["id"]) for p in included]
    with open(f"{OUT}/sitemap.xml", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.writelines(f"  <url><loc>{C.BASE_URL}{u}</loc></url>\n" for u in urls)
        f.write("</urlset>\n")
    print(f"artigos: {len(included)} (excluídos: {len(excluded)}) · imagens: {ok.count(True)}/{len(imgs)} · "
          f"vídeos referenciados: {len(vids)} · arquivos: {len(files)}")


if __name__ == "__main__":
    main()

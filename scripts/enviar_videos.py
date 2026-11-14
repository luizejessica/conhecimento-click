"""Envia os vídeos (e anexos grandes) da central de ajuda para um bucket Cloudflare R2.

Rode no SEU computador. Ele baixa cada arquivo do Confluence e envia para o R2, um por vez,
apagando a cópia local em seguida (não precisa de 16 GB livres).

Pré-requisitos:
  1. ~/.netrc com seu acesso ao Confluence:
       machine qualityautomacao.atlassian.net login SEU_EMAIL password SEU_TOKEN_ATLASSIAN
  2. Wrangler logado na Cloudflare:  npx wrangler login
  3. Bucket criado:                  npx wrangler r2 bucket create conhecimento-videos
  4. Domínio ligado ao bucket (painel R2 → bucket → Settings → Custom Domains → videos.conhecimento.click)

Uso:
  python3 scripts/enviar_videos.py [nome-do-bucket]

Pode interromper e rodar de novo: o progresso fica salvo em scripts/.videos-enviados.txt.
"""
import os, subprocess, sys, tempfile
from urllib.parse import quote

BUCKET = sys.argv[1] if len(sys.argv) > 1 else "conhecimento-videos"
BASE = "https://qualityautomacao.atlassian.net/wiki/download/"
HERE = os.path.dirname(os.path.abspath(__file__))
LISTA = os.path.join(HERE, "videos.txt")
FEITOS = os.path.join(HERE, ".videos-enviados.txt")
NPX = "npx.cmd" if os.name == "nt" else "npx"

CONTENT_TYPES = {"mp4": "video/mp4", "webm": "video/webm", "mkv": "video/x-matroska", "mov": "video/quicktime",
                 "exe": "application/octet-stream", "zip": "application/zip", "pdf": "application/pdf"}

def main():
    todos = [l.strip() for l in open(LISTA, encoding="utf-8") if l.strip()]
    feitos = set(l.strip() for l in open(FEITOS, encoding="utf-8")) if os.path.exists(FEITOS) else set()
    pend = [r for r in todos if r not in feitos]
    print(f"{len(todos)} arquivos, {len(feitos)} já enviados, {len(pend)} pendentes → bucket '{BUCKET}'")
    falhas = []
    for i, rel in enumerate(pend, 1):
        # rel: attachments/<pageId>/<nome com _ no lugar de espaços/símbolos>
        _, page_id, nome = rel.split("/", 2)
        print(f"[{i}/{len(pend)}] {rel}")
        with tempfile.TemporaryDirectory() as tmp:
            dest = os.path.join(tmp, "arquivo")
            ok = baixar(page_id, nome, dest)
            if not ok:
                print("   ✗ não encontrado no Confluence"); falhas.append(rel); continue
            ext = nome.rsplit(".", 1)[-1].lower()
            cmd = [NPX, "wrangler", "r2", "object", "put", f"{BUCKET}/{rel}", "--file", dest, "--remote",
                   "--content-type", CONTENT_TYPES.get(ext, "application/octet-stream")]
            if subprocess.run(cmd, stdout=subprocess.DEVNULL).returncode != 0:
                print("   ✗ falha no envio"); falhas.append(rel); continue
        with open(FEITOS, "a", encoding="utf-8") as f:
            f.write(rel + "\n")
    print(f"Concluído. Falhas: {len(falhas)}")
    for r in falhas:
        print("  -", r)

def baixar(page_id, nome, dest):
    """O nome salvo trocou espaços/símbolos por '_'; busca o nome original na lista de anexos da página."""
    import json
    url = f"https://qualityautomacao.atlassian.net/wiki/rest/api/content/{page_id}/child/attachment?limit=500"
    try:
        r = json.loads(subprocess.check_output(["curl", "-sS", "--netrc", "--fail", url]))
    except Exception:
        return False
    import re
    norm = lambda s: re.sub(r"[^\w./-]+", "_", s)
    for a in r.get("results", []):
        if norm(a["title"]) == nome:
            link = "https://qualityautomacao.atlassian.net/wiki" + a["_links"]["download"]
            return subprocess.run(["curl", "-sS", "--netrc", "-L", "--fail", "-o", dest, link]).returncode == 0
    return False

if __name__ == "__main__":
    main()

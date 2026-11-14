# conhecimento.click — Central de Ajuda webPosto

Portal estático de ajuda para clientes, gerado a partir do espaço **webPosto** do Confluence.

- 951 artigos organizados por produto (Retaguarda, PDV, Pay, TEF…)
- Busca instantânea em português com [Pagefind](https://pagefind.app). Roda no navegador, sem servidor.
- Tema claro/escuro, layout para celular, zoom de imagens e sitemap para o Google
- Seções internas removidas (veja `EXCLUDE_IDS` em `scripts/config.py`)

## Como funciona

```
Confluence ──fetch.py──▶ cache/ (HTML + anexos) ──build.py──▶ _site/ ──pagefind──▶ índice de busca
```

| Arquivo | Função |
|---|---|
| `scripts/config.py` | Domínio, links, endereço dos vídeos e páginas excluídas |
| `scripts/fetch.py` | Baixa páginas e anexos do Confluence. É incremental: só baixa o que mudou. |
| `scripts/build.py` | Limpa o HTML do Confluence e gera o site em `_site/` |
| `static/` | CSS, JS, favicon, robots.txt e `_headers` |

## Atualizar o conteúdo

Requisitos: Python 3.10+, `pip install beautifulsoup4 pillow`, Node 18+ e `ffmpeg`.

O `fetch.py` usa o `curl` para acessar `qualityautomacao.atlassian.net`. Fora do ambiente em que o
site foi gerado, configure a autenticação (seu e-mail Atlassian + um token de API) no `~/.netrc`:

```
machine qualityautomacao.atlassian.net login SEU_EMAIL password SEU_TOKEN
```

Depois, acrescente `--netrc` ao comando curl na função `get()` de `scripts/fetch.py`.

```bash
npm install
npm run fetch      # baixa/atualiza a partir do Confluence
npm run build      # gera _site/ e o índice de busca
npm run serve      # abre em http://localhost:8080
```

## Publicar em conhecimento.click

O site em `_site/` é estático (cerca de 250 MB e 7 mil arquivos) e funciona em qualquer hospedagem.
Recomendação: **Cloudflare Pages**, que é gratuito e já inclui CDN e HTTPS.

```bash
npx wrangler pages deploy _site --project-name conhecimento-click
```

Depois, no painel da Cloudflare: Pages → conhecimento-click → *Custom domains* → `conhecimento.click`.

### Vídeos (16 GB)

Os cerca de 1.100 vídeos não cabem no Pages, que aceita no máximo 25 MB por arquivo. Por isso o site
os busca em `https://videos.conhecimento.click/attachments/...`. Esse endereço é configurado em
`VIDEO_BASE`.

- **Opção A, Cloudflare R2** (sem custo de tráfego): crie um bucket, conecte a ele o domínio
  `videos.conhecimento.click` e envie a pasta `cache/assets/attachments` mantendo a estrutura de
  pastas. A lista exata de arquivos está em `videos-para-upload.txt`. Dá para enviar com `rclone copy`.
- **Opção B, servidor próprio** (VPS com nginx): gere o site com os vídeos incluídos e sirva tudo
  do mesmo lugar:

```bash
VIDEO_BASE=/videos python3 scripts/build.py --with-videos && npx pagefind --site _site
```

## Excluir mais páginas

Adicione o ID da página em `EXCLUDE_IDS`, no `scripts/config.py`. O ID aparece na URL do
Confluence, em `/pages/<ID>/...`. A página e todas as suas subpáginas deixam de ser publicadas.

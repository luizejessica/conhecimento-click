# Notas do projeto — Central de Ajuda webPosto (conhecimento.click)

Portal estático de ajuda para clientes, gerado a partir do espaço **webPosto** do Confluence
(`qualityautomacao.atlassian.net`, space id `1179672`, página inicial `1179907`). Como funciona: veja o README.

## Estado atual (14/11/2026)

- [x] Gerador pronto (`scripts/fetch.py`, `scripts/build.py`, `scripts/config.py`)
- [x] Site gerado e versionado em `_site/`: 951 artigos, ~5.150 imagens em WebP e busca Pagefind
- [x] Repositório no GitHub: `luizejessica/conhecimento-click` (privado)
- [ ] Publicar `_site/` no Cloudflare Pages (Connect to Git, sem comando de build, diretório de saída `_site`)
- [ ] Ligar o domínio `conhecimento.click` ao projeto do Pages
- [ ] Enviar os vídeos ao R2 com `scripts/enviar_videos.py` (1.095 arquivos, ~16 GB), rodando no computador do usuário
- [ ] Ligar `videos.conhecimento.click` ao bucket R2 `conhecimento-videos`

## Decisões tomadas

- Páginas excluídas (`EXCLUDE_IDS`): Parceiros, Migração, "criação de usuário para acesso ao banco local"
  e "Procedimento para habilitar o Horus BI" (internas).
- Links do Jira e do Confluence removidos; referências `QP-xxxx` ficam só em nomes de arquivos de vídeo.
- GIFs acima de 4 MB viram MP4 em loop. Anexos acima de 24 MB vão para o host de vídeos (limite de 25 MB do Pages).
- O usuário **não quis** fornecer um token da Cloudflare para a sessão. O envio ao R2 fica com ele.

## Pendências para revisar com o usuário

- Link do botão "Falar com o suporte" (`SUPPORT_URL`): hoje aponta para qualityautomacao.com.br.
- Decidir se as páginas de PgAdmin/backup de banco (dentro de WP PDV → Instalação) e
  "Manutenção no Banco de Dados" devem continuar públicas.
- 25 imagens de 6 notas de versão (26.4.1 a 26.9.1) não foram encontradas como anexo e ficaram de fora.

## Como atualizar o conteúdo

```bash
npm install && pip install beautifulsoup4 pillow
npm run fetch && npm run build
```

Em seguida, faça commit de `_site/` e push. O Pages republica sozinho.
O `fetch` precisa de acesso autenticado ao Confluence: na nuvem, por credencial salva no ambiente;
localmente, pelo `~/.netrc`.

# Notas do projeto — materiais de suporte webPosto

## Conteúdo do repositório

- `prompts/assistente-suporte.md`: prompt do assistente de IA do sistema de suporte. A base de
  conhecimento oficial fica em https://conhecimento.click/knowledge-base (mantida pelo usuário).
- `guia/guia-autoajuda-webposto.pdf`: Guia Rápido de Autoajuda (11 páginas), gerado por `scripts/guia_pdf.py`
  (reportlab). O texto do guia está no próprio script.

## Decisões

- 15/11/2026: o usuário pediu para **excluir por completo** o site estático gerado a partir do Confluence
  (gerador, `_site/`, scripts de vídeos). Não recrie esse site nem republique conteúdo do Confluence
  sem um pedido explícito.
- O assistente de suporte não deve inventar endereços: só https://conhecimento.click/knowledge-base
  ou links exatos vindos da base de conhecimento.

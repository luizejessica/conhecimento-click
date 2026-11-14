"""Configuração do portal. Ajuste aqui sem mexer no gerador."""

BRAND = "webPosto"
DOMAIN = "conhecimento.click"
BASE_URL = "https://conhecimento.click"

# Página inicial do espaço webPosto no Confluence
HOME_ID = "1179907"

# Endereço de onde os vídeos serão servidos (ver README). Pode ser sobrescrito com a variável VIDEO_BASE.
VIDEO_BASE = "https://videos.conhecimento.click"

# Link do botão "Falar com o suporte"
SUPPORT_URL = "https://qualityautomacao.com.br"
FOOTER_TEXT = "Central de Ajuda webPosto — tutoriais e respostas para o dia a dia do seu posto."

# Páginas (e todas as subpáginas) que NÃO serão publicadas para clientes
EXCLUDE_IDS = [
    "76546087",    # Parceiros (inclui "Login Rápido com o usuário de suporte")
    "520552475",   # Migração (backup, restauração de banco, migrador)
    "742227969",   # Como solicitar a criação de usuário para acesso ao banco local
    "1650688010",  # Procedimento de como habilitar o Horus BI para novos clientes (interno)
]

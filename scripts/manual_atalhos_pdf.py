"""Manual de atalhos do WP PDV para o usuário final (frentista / operador de caixa).

Fonte: Confluence webPosto > "Atalhos do WP PDV" (página 66289752, versão de 22/09/2026).
Uso: python3 scripts/manual_atalhos_pdf.py  ->  guia/manual-atalhos-wp-pdv.pdf
"""
import os
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = f"{ROOT}/guia/manual-atalhos-wp-pdv.pdf"

NAVY = colors.HexColor("#000B3D"); NAVY2 = colors.HexColor("#001350"); RED = colors.HexColor("#E30A0A")
GREY = colors.HexColor("#5A6382"); LIGHT = colors.HexColor("#F3F5FA"); BORDER = colors.HexColor("#DDE2EE")
INFO_BG = colors.HexColor("#EAF1FF"); WARN_BG = colors.HexColor("#FFF3E0")
W, H = A4
M = 16 * mm
CW = W - 2 * M

S = {
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=19, leading=23, textColor=NAVY, spaceAfter=2),
    "lead": ParagraphStyle("lead", fontName="Helvetica", fontSize=10.5, leading=14.5, textColor=GREY, spaceAfter=8),
    "p": ParagraphStyle("p", fontName="Helvetica", fontSize=10, leading=14.5, spaceAfter=4),
    "li": ParagraphStyle("li", fontName="Helvetica", fontSize=10, leading=15, leftIndent=16, bulletIndent=4, spaceAfter=3),
    "act": ParagraphStyle("act", fontName="Helvetica", fontSize=10, leading=13),
    "key": ParagraphStyle("key", fontName="Helvetica", fontSize=10, leading=13, alignment=2),
    "note": ParagraphStyle("note", fontName="Helvetica", fontSize=9.5, leading=13.5),
    "card_t": ParagraphStyle("ct", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=NAVY),
    "card_k": ParagraphStyle("ck", fontName="Helvetica", fontSize=11, leading=15),
    "toc": ParagraphStyle("toc", fontName="Helvetica", fontSize=11, leading=19),
}

NAMES = {"ctrl": "Ctrl", "alt": "Alt", "shift": "Shift", "space": "Espaço", "esc": "Esc", "enter": "Enter"}


def key(k):
    k = NAMES.get(k.lower(), k)
    return (f'<font name="Courier-Bold" size="10" color="#000B3D" backColor="#E4E9F5">&nbsp;{k}&nbsp;</font>')


def keys(spec):
    """'[Ctrl] + [Alt] + [C]' ou 'Shift + CTRL + T' -> teclas desenhadas."""
    parts = [x.strip(" []") for x in spec.split("+")]
    return ' <font color="#5A6382">+</font> '.join(key(x) for x in parts if x)


# ------------------------------------------------------------------ conteúdo (reorganizado por tarefa)
ESSENCIAIS = [
    ("Confirmar / OK", "F10"), ("Cancelar / Voltar", "Esc"),
    ("Ver abastecimentos", "A  (no campo de atalhos)"), ("Marcar abastecimento", "Space"),
    ("Fechar a venda", "F10"), ("Incluir produto", "F11"),
    ("Identificar cliente", "F12"), ("Mais de uma forma de pagamento", "F2"),
    ("Consultar NFC-e", "Ctrl + E"), ("Sangria", "Alt + N"),
    ("Fechar caixa", "F7"), ("Fechar turno", "Ctrl + F7"),
]

SECOES = [
    ("Na tela de abastecimentos",
     "Depois de digitar A (ou B + número do bico) no campo de atalhos e pressionar Enter.",
     [("Marcar / desmarcar um abastecimento", "Space"),
      ("Marcar todos", "M"),
      ("Marcar e já finalizar", "Ctrl + Enter"),
      ("Fracionar o abastecimento", "F"),
      ("Filtrar por operador", "Alt + O"),
      ("Lançar como aferição", "A"),
      ("Finalizar em Dinheiro", "D"),
      ("Finalizar em Cartão (POS)", "P"),
      ("Finalizar em TEF", "T"),
      ("Finalizar em Notas", "N"),
      ("Finalizar em Cheque", "C"),
      ("Finalizar em Cheque-Pré", "H"),
      ("Finalizar em Carta Frete", "R"),
      ("Finalizar em Créditos (Vale)", "V"),
      ("Finalizar em Pré-Pago", "G")]),
    ("Na tela de pagamento",
     "Aparece quando você fecha a venda com F10.",
     [("Dinheiro", "D"), ("Cartão (POS)", "P"), ("TEF", "T"), ("Notas", "N"),
      ("Cheque", "C"), ("Cheque-Pré", "H"), ("Carta Frete", "R"), ("Créditos (Vale)", "V"), ("Pré-Pago", "G"),
      ("Usar várias formas de pagamento (Diversos)", "F2"),
      ("Informar valores por forma de pagamento", "Alt + V"),
      ("Limpar as formas escolhidas", "F9"),
      ("Dar desconto", "F4"),
      ("Lançar acréscimo", "F5"),
      ("Troco em Vale", "F8"),
      ("Cheque troco", "Shift + Ctrl + T")]),
    ("Montando a venda",
     "Na tela principal do PDV.",
     [("Abrir a venda", "F2"),
      ("Incluir produto", "F11"),
      ("Incluir abastecimento", "Ctrl + F4"),
      ("Lançar abastecimento manual", "Ctrl + I"),
      ("Identificar cliente", "F12"),
      ("Selecionar cliente cadastrado", "Ctrl + F12"),
      ("Excluir item da venda", "Shift + Ctrl + E"),
      ("Fechar a venda", "F10"),
      ("Ir para os pagamentos", "Alt + F10"),
      ("Cancelar a venda", "Alt + C"),
      ("Pré-venda", "Shift + Ctrl + P"),
      ("Incluir pré-venda", "Ctrl + Alt + P")]),
    ("Finalizar direto na tela principal",
     "Atalhos rápidos para fechar a venda já na forma de pagamento certa.",
     [("Finalizar em Cartão (POS)", "Shift + P"),
      ("Finalizar em TEF", "Shift + T"),
      ("Finalizar em Notas", "Shift + N"),
      ("Finalizar em Cheque", "Shift + C"),
      ("Finalizar em Cheque-Pré", "Shift + H"),
      ("Finalizar em Carta Frete", "Shift + R"),
      ("Finalizar em Créditos (Vale)", "Shift + V"),
      ("Finalizar em Pré-Pago", "Shift + G")]),
    ("Caixa e turno",
     "Abertura, fechamento e movimentação de dinheiro.",
     [("Abrir o turno", "Ctrl + Alt + F7"),
      ("Abrir o caixa", "Alt + F7"),
      ("Fechar o caixa", "F7"),
      ("Fechar o turno", "Ctrl + F7"),
      ("Sangria (retirar dinheiro)", "Alt + N"),
      ("Suprimento (colocar troco)", "Ctrl + S"),
      ("Abrir a gaveta", "Alt + G"),
      ("Troca de valores", "Ctrl + Alt + T"),
      ("Totais por operador", "Ctrl + T"),
      ("Movimentação", "Ctrl + F2")]),
    ("Lançamentos",
     "Despesas, recebimentos, vales e serviços.",
     [("Menu de lançamentos", "Ctrl + F3"),
      ("Despesas", "F9"),
      ("Empréstimo", "F8"),
      ("Recebimento de clientes", "Ctrl + W"),
      ("Vale funcionário", "Shift + Ctrl + F"),
      ("Vale cliente", "Shift + Ctrl + V"),
      ("Pré-pago", "Ctrl + G"),
      ("Serviço", "Ctrl + O"),
      ("Recarga de celular", "Shift + Ctrl + R")]),
    ("Notas fiscais e impressão",
     "",
     [("Consultar NFC-e/SAT (corrigir, cancelar, reimprimir)", "Ctrl + E"),
      ("NF-e", "Ctrl + F"),
      ("Reimprimir o último cupom", "Alt + Y")]),
    ("Consultas e relatórios",
     "",
     [("Tabela de produtos", "Ctrl + F6"),
      ("Tabela de clientes", "Ctrl + F5"),
      ("Encerrantes", "Ctrl + Alt + E"),
      ("Relatório de reposição", "Alt + L"),
      ("Relatório de posição de estoque", "Alt + E"),
      ("Grupo / Produto", "Ctrl + Alt + L"),
      ("Troca de preço", "Ctrl + P")]),
    ("Menus e navegação",
     "",
     [("Menu principal", "F1"),
      ("Venda", "F2"),
      ("Lançar", "F3"),
      ("Caixa / Turno", "F4"),
      ("Consultas", "F5"),
      ("Outros", "F6"),
      ("Menu", "Ctrl + A"),
      ("Menu principal - Opções", "Shift + Ctrl + F1"),
      ("Confirmar (em qualquer tela)", "F10"),
      ("Cancelar / Voltar (em qualquer tela)", "Esc"),
      ("Trocar de usuário (novo login)", "Alt + F5"),
      ("Encerrar o PDV", "Ctrl + F12")]),
    ("Abastecimentos: correções",
     "",
     [("Estornar aferição", "Alt + R"),
      ("Excluir abastecimento", "Ctrl + Alt + A")]),
    ("Integrações",
     "Use apenas se o seu posto trabalha com essas integrações.",
     [("Funções TEF", "Alt + A"),
      ("OS webOil", "Alt + W"),
      ("OS JetOil", "Ctrl + J"),
      ("Resgate KMV", "Ctrl + Alt + K"),
      ("Importar / Excluir Inforlub", "Shift + I"),
      ("Exportar Inforlub", "Shift + E")]),
]

AVANCADOS = [
    ("Ativar / desativar contingência", "Ctrl + Alt + C"),
    ("Modo contingência", "Alt + O"),
    ("Ativar / desativar NF-e", "Ctrl + Alt + N"),
    ("Bloquear leitura do Concentrador", "Ctrl + B"),
    ("Configurações do PDV", "Alt + P"),
    ("Alterar PDV", "Ctrl + F1  ou  Alt + F1"),
]


# ------------------------------------------------------------------ helpers de layout
def kspec(spec):
    if "  ou  " in spec:
        return '  <font color="#5A6382">ou</font>  '.join(keys(x) for x in spec.split("  ou  "))
    if "(" in spec:
        k, rest = spec.split("(", 1)
        return keys(k) + f' <font size="8.5" color="#5A6382">({rest}</font>'
    return keys(spec)


def shortcut_table(rows, warn=False):
    data = [[Paragraph(a, S["act"]), Paragraph(kspec(k), S["key"])] for a, k in rows]
    t = Table(data, colWidths=[CW * .6, CW * .4])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, BORDER),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#E8A000") if warn else BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def box(text, kind="info"):
    bg, bar = (INFO_BG, colors.HexColor("#3D6BFF")) if kind == "info" else (WARN_BG, colors.HexColor("#E8A000"))
    t = Table([["", Paragraph(text, S["note"])]], colWidths=[1.6 * mm, CW - 1.6 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), bar), ("BACKGROUND", (1, 0), (1, 0), bg),
                           ("LEFTPADDING", (1, 0), (1, 0), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def section_title(n, title):
    t = Table([[Paragraph(f'<font color="white"><b>{n}</b></font>', ParagraphStyle("n", fontName="Helvetica-Bold", fontSize=11, alignment=1, leading=14)),
                Paragraph(title, ParagraphStyle("st", fontName="Helvetica-Bold", fontSize=13.5, leading=17, textColor=NAVY))]],
              colWidths=[10 * mm, CW - 10 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), RED), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LEFTPADDING", (1, 0), (1, 0), 8), ("TOPPADDING", (0, 0), (-1, -1), 3),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def cards(items, cols=3):
    cells = []
    for a, k in items:
        cells.append([Paragraph(a, S["card_t"]), Spacer(1, 3), Paragraph(kspec(k), S["card_k"])])
    rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
    while len(rows[-1]) < cols:
        rows[-1].append("")
    t = Table(rows, colWidths=[CW / cols] * cols, rowHeights=19 * mm)
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, NAVY), ("INNERGRID", (0, 0), (-1, -1), 0.6, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ------------------------------------------------------------------ páginas
def cover(c, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(NAVY2); c.rect(0, 0, W, H * 0.36, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 60)
    c.setFillColor(RED); c.drawString(M, H - 68 * mm, "W")
    c.setFillColor(colors.white); c.drawString(M + c.stringWidth("W", "Helvetica-Bold", 60), H - 68 * mm, "P")
    c.setFont("Helvetica-Bold", 32); c.drawString(M, H - 100 * mm, "Atalhos do WP PDV")
    c.setFont("Helvetica", 15); c.drawString(M, H - 111 * mm, "Manual rápido para frentistas e operadores de caixa")
    c.setFillColor(RED); c.rect(M, H - 119 * mm, 40 * mm, 1.6 * mm, stroke=0, fill=1)
    # teclas decorativas
    x = M
    for k in ["F2", "F10", "F11", "F12", "Esc"]:
        w = max(16 * mm, c.stringWidth(k, "Helvetica-Bold", 16) + 10 * mm)
        c.setFillColor(colors.HexColor("#1B2A66")); c.roundRect(x, H - 150 * mm, w, 14 * mm, 3 * mm, stroke=0, fill=1)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(x + w / 2, H - 145 * mm, k)
        x += w + 4 * mm
    c.setFillColor(colors.HexColor("#C9D1F0")); c.setFont("Helvetica", 11)
    for i, t in enumerate(["Encontre o atalho pelo que você quer fazer.",
                           "Página 2: cartão de bolso para imprimir e deixar ao lado do caixa.",
                           "Versão: novembro de 2026"]):
        c.drawString(M, 62 * mm - i * 7 * mm, t)
    c.restoreState()


def page(c, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, H - 11 * mm, W, 11 * mm, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 9); c.setFillColor(RED); c.drawString(M, H - 7 * mm, "W")
    c.setFillColor(colors.white); c.drawString(M + 7, H - 7 * mm, "P")
    c.setFont("Helvetica", 9); c.drawString(M + 18, H - 7 * mm, "Atalhos do WP PDV")
    c.setFillColor(GREY); c.setFont("Helvetica", 8.5)
    c.drawRightString(W - M, 9 * mm, str(d.page))
    c.drawString(M, 9 * mm, "Dica: digite ? no campo de atalhos do PDV para ver a lista na tela.")
    c.restoreState()


def build():
    story = [NextPageTemplate("conteudo"), PageBreak()]

    # Cartão de bolso
    story += [Paragraph("Cartão de bolso: os 12 atalhos mais usados", S["h1"]),
              Paragraph("Imprima esta página e deixe ao lado do caixa.", S["lead"]),
              cards(ESSENCIAIS), Spacer(1, 10),
              box('<b>Regra de ouro:</b> ' + keys("F10") + ' confirma e ' + keys("Esc") +
                  ' cancela ou volta, em qualquer tela do PDV.'),
              Spacer(1, 8),
              box('<b>Esqueceu um atalho?</b> Digite <b>?</b> no campo de atalhos (canto inferior esquerdo da tela '
                  'principal) e o PDV mostra a lista de comandos.'),
              Spacer(1, 12),
              Paragraph("<b>Como usar este manual</b>", S["p"])]
    for t in ["Os atalhos estão agrupados pelo <b>que você quer fazer</b>: vender, receber, fechar o caixa…",
              "Quando aparecer " + keys("Ctrl + E") + ", segure a primeira tecla e pressione a segunda.",
              "Uma <b>letra sozinha</b> (como " + keys("D") + ") funciona dentro da tela indicada no título da seção. "
              "A mesma tecla pode fazer coisas diferentes em telas diferentes.",
              "Os atalhos do seu PDV podem ter sido personalizados. Veja como na última página."]:
        story.append(Paragraph(t, S["li"], bulletText="•"))
    story.append(PageBreak())

    # Seções
    story += [Paragraph("Todos os atalhos, por tarefa", S["h1"]), Spacer(1, 6)]
    for i, (title, sub, rows) in enumerate(SECOES, 1):
        block = [section_title(i, title)]
        if sub:
            block.append(Paragraph(sub, ParagraphStyle("sub", parent=S["lead"], spaceBefore=3, spaceAfter=4)))
        else:
            block.append(Spacer(1, 4))
        block.append(shortcut_table(rows))
        story += [KeepTogether(block), Spacer(1, 12)]

    n = len(SECOES) + 1
    story += [KeepTogether([section_title(n, "Funções avançadas (use só com orientação)"),
                            Spacer(1, 4),
                            box("Estes atalhos mudam o funcionamento do PDV ou a emissão de notas fiscais. "
                                "Use apenas quando o suporte ou o gerente pedir.", "warn"),
                            Spacer(1, 4), shortcut_table(AVANCADOS, warn=True)]), Spacer(1, 12)]

    # Personalizar
    story += [KeepTogether([section_title(n + 1, "Personalizar os atalhos"), Spacer(1, 6)] +
              [Paragraph(t, S["li"], bulletText=f"{j}.") for j, t in enumerate([
                  "Na tela principal do PDV, clique com o <b>botão direito do mouse</b>.",
                  "Vá em <b>Funções &gt; Configurar Atalhos do PDV</b>.",
                  "No campo <b>Atalho Configurado</b>, digite a nova combinação de teclas e confirme.",
                  "Não repita um atalho que já está em uso."], 1)] +
              [Spacer(1, 6), box("Se os atalhos do seu PDV foram personalizados, alguns podem ser diferentes deste manual. "
                                 "Digite <b>?</b> no campo de atalhos para conferir os atalhos atuais.")])]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=18 * mm, bottomMargin=16 * mm,
                          title="Atalhos do WP PDV", author="webPosto", subject="Manual de atalhos para o usuário final")
    doc.addPageTemplates([PageTemplate("capa", frames=[Frame(0, 0, W, H)], onPage=cover),
                          PageTemplate("conteudo", frames=[Frame(M, 16 * mm, CW, H - 34 * mm)], onPage=page)])
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()

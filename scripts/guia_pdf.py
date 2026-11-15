"""Gera o Guia Rápido de Autoajuda webPosto em PDF (resumo da base de conhecimento do Confluence).

Uso: python3 scripts/guia_pdf.py  ->  guia/guia-autoajuda-webposto.pdf
"""
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = f"{ROOT}/guia/guia-autoajuda-webposto.pdf"

NAVY = colors.HexColor("#000B3D")
NAVY2 = colors.HexColor("#001350")
RED = colors.HexColor("#E30A0A")
GREY = colors.HexColor("#5A6382")
LIGHT = colors.HexColor("#EEF1F8")
BORDER = colors.HexColor("#DDE2EE")
INFO_BG = colors.HexColor("#EAF1FF")
WARN_BG = colors.HexColor("#FFF3E0")

W, H = A4
M = 18 * mm

S = {
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=NAVY, spaceAfter=4),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=NAVY, spaceBefore=12, spaceAfter=4),
    "lead": ParagraphStyle("lead", fontName="Helvetica", fontSize=10.5, leading=15, textColor=GREY, spaceAfter=8),
    "p": ParagraphStyle("p", fontName="Helvetica", fontSize=10, leading=14.5, spaceAfter=4),
    "li": ParagraphStyle("li", fontName="Helvetica", fontSize=10, leading=14.5, leftIndent=16, bulletIndent=4, spaceAfter=2),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=9, leading=12),
    "cellb": ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.white),
    "note": ParagraphStyle("note", fontName="Helvetica", fontSize=9.5, leading=13.5),
    "toc1": ParagraphStyle("toc1", fontName="Helvetica", fontSize=11, leading=20),
}

K = lambda k: f'<font name="Courier-Bold" color="#000B3D" backColor="#EEF1F8"> {k} </font>'  # tecla


class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name == "h1":
            key = "h" + str(abs(hash(f.getPlainText())))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(f.getPlainText(), key, 0)
            self.notify("TOCEntry", (0, f.getPlainText(), self.page, key))


def cover(c, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(NAVY2); c.rect(0, 0, W, H * 0.38, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 64)
    c.setFillColor(RED); c.drawString(M, H - 70 * mm, "W")
    c.setFillColor(colors.white); c.drawString(M + c.stringWidth("W", "Helvetica-Bold", 64), H - 70 * mm, "P")
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 30); c.drawString(M, H - 105 * mm, "Guia Rápido de Autoajuda")
    c.setFont("Helvetica", 16); c.drawString(M, H - 116 * mm, "webPosto: PDV, WP Pay, NFC-e, Caixa e Retaguarda")
    c.setFillColor(RED); c.rect(M, H - 124 * mm, 40 * mm, 1.6 * mm, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#C9D1F0")); c.setFont("Helvetica", 11)
    for i, t in enumerate(["Respostas rápidas para as dúvidas mais comuns do dia a dia.",
                           "Resumo da Base de Conhecimento webPosto.",
                           "Versão: novembro de 2026"]):
        c.drawString(M, 70 * mm - i * 7 * mm, t)
    c.restoreState()


def page(c, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, H - 12 * mm, W, 12 * mm, stroke=0, fill=1)
    c.setFont("Helvetica-Bold", 9); c.setFillColor(RED); c.drawString(M, H - 7.6 * mm, "W")
    c.setFillColor(colors.white); c.drawString(M + 7, H - 7.6 * mm, "P")
    c.setFont("Helvetica", 9); c.drawString(M + 18, H - 7.6 * mm, "Guia Rápido de Autoajuda webPosto")
    c.setFillColor(GREY); c.setFont("Helvetica", 8.5)
    c.drawRightString(W - M, 10 * mm, f"{d.page}")
    c.drawString(M, 10 * mm, "Em caso de dúvida, fale com o suporte webPosto.")
    c.restoreState()


# ---------------------------------------------------------------- blocos
def h1(t): return Paragraph(t, S["h1"])
def h2(t): return Paragraph(t, S["h2"])
def p(t): return Paragraph(t, S["p"])
def lead(t): return Paragraph(t, S["lead"])

def steps(items, numbered=True):
    out = []
    for i, t in enumerate(items, 1):
        out.append(Paragraph(t, S["li"], bulletText=f"{i}." if numbered else "•"))
    return out

def bullets(items): return steps(items, numbered=False)

def table(head, rows, widths):
    data = [[Paragraph(h, S["cellb"]) for h in head]] + [[Paragraph(c, S["cell"]) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 6)]

def box(text, kind="info"):
    bg, bar = (INFO_BG, colors.HexColor("#3D6BFF")) if kind == "info" else (WARN_BG, colors.HexColor("#E8A000"))
    t = Table([["", Paragraph(text, S["note"])]], colWidths=[1.6 * mm, W - 2 * M - 1.6 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), bar), ("BACKGROUND", (1, 0), (1, 0), bg),
        ("LEFTPADDING", (1, 0), (1, 0), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 6)]

def section(title, *parts):
    """Mantém o título junto do primeiro bloco."""
    flat = []
    for x in parts:
        flat.extend(x if isinstance(x, list) else [x])
    return [KeepTogether([h2(title)] + flat[:2])] + flat[2:]


# ---------------------------------------------------------------- conteúdo
CW = W - 2 * M
story = [NextPageTemplate("conteudo"), PageBreak()]

toc = TableOfContents(); toc.levelStyles = [S["toc1"]]
story += [Paragraph("Sumário", ParagraphStyle("toct", parent=S["h1"])), Spacer(1, 6), toc, Spacer(1, 14)]
story += box("<b>Como usar este guia:</b> procure o assunto no sumário e siga os passos. As teclas aparecem assim: "
             f"{K('F10')}. Se o problema continuar depois de seguir as orientações, consulte a seção "
             "<b>Quando chamar o suporte</b> no final do guia.")
story.append(PageBreak())

# 1
story += [h1("1. Primeiros passos no WP PDV"),
          lead("Login, abertura de turno e caixa, e como ler a tela principal.")]
story += section("Entrar e abrir o turno",
    steps([f"Faça login com <b>código de usuário e senha</b> ou pela <b>biometria</b>.",
           f"Abra o turno pressionando {K('F10')} e confirme. O turno é definido por funcionário.",
           f"Confirme a abertura do caixa com {K('F10')}. Todo usuário que acessa o PDV pela primeira vez precisa abrir o caixa."]))
story += section("Tela principal",
    bullets(["<b>Parte superior:</b> data, turno aberto e operador.",
             "<b>Bicos:</b> número do bico, combustível, quantidade de abastecimentos no turno e valor do último abastecimento.",
             "<b>Canto inferior esquerdo:</b> campo para digitar atalhos (bicos e outras funções).",
             "<b>Canto inferior direito:</b> menus Venda, Lançamento, Caixa/Turno, Consulta e Outros."]))
story += section("Ícones de serviço (Concentrador, Impressora e Integra)",
    p("Os três ícones abaixo da imagem do PDV mostram, da esquerda para a direita, o estado do Concentrador, "
      "da Impressora e do Integra:"),
    table(["Cor", "Significado"],
          [["<font color='#1E9E55'><b>Verde</b></font>", "Serviço funcionando normalmente."],
           ["<font color='#B07800'><b>Amarelo</b></font>", "Algum erro está ocorrendo."],
           ["<font color='#E30A0A'><b>Vermelho</b></font>", "Erro grave ou serviço parado."]], [30 * mm, CW - 30 * mm]),
    box("Se o ícone da <b>direita (Integra)</b> estiver amarelo ou vermelho, as vendas do PDV podem não estar chegando ao "
        "Retaguarda. Ícone amarelo ou vermelho: <b>chame o suporte</b>.", "warn"))

# 2
story += [PageBreak(), h1("2. Vendas no WP PDV"),
          lead("Selecionar abastecimentos, receber e identificar o cliente.")]
story += section("Selecionar abastecimentos pendentes",
    table(["Digite no campo de atalhos", "Resultado"],
          [[f"{K('A')} ou {K('B')} + {K('ENTER')}", "Mostra todos os abastecimentos pendentes."],
           [f"{K('B')} + número do bico + {K('ENTER')}", "Mostra só os abastecimentos daquele bico (ou clique 2x no bico)."],
           [f"{K('A')} + valor + {K('ENTER')}", "Busca pelo valor. Se só houver um, já abre o fechamento da venda."],
           [f"{K('Espaço')} ou clique duplo", "Seleciona o abastecimento para a venda."]], [60 * mm, CW - 60 * mm]))
story += section("Fechar a venda (sem identificar o cliente)",
    steps([f"Com os abastecimentos selecionados, pressione {K('F10')} (ou clique em Fechar Venda).",
           "Escolha a forma de pagamento pelo atalho (tabela abaixo).",
           f"Confirme com {K('F10')}. O sistema abre a tela de impressão da NFC-e."]),
    table(["Atalho", "Forma de pagamento", "Atalho", "Forma de pagamento"],
          [[K("D"), "Dinheiro", K("T"), "TEF"],
           [K("P"), "Cartão", K("R"), "Carta"],
           [K("N"), "Notas", K("V"), "Vale"],
           [K("C"), "Cheque", K("G"), "Pré-pago"],
           [K("H"), "Cheque pré", "", ""]], [20 * mm, CW / 2 - 20 * mm, 20 * mm, CW / 2 - 20 * mm]),
    box(f"<b>Mais de uma forma de pagamento:</b> pressione {K('F2')} para liberar todas as formas e combine-as. "
        f"Para limpar e escolher de novo, use {K('F9')}."))
story += section("Venda com cliente identificado",
    steps([f"Pressione {K('F12')}, na tela principal ou já na tela de fechamento da venda.",
           f"{K('F4')} seleciona um cliente <b>já cadastrado</b>. {K('F5')} identifica um cliente <b>não cadastrado</b>.",
           f"Selecione os abastecimentos. Para incluir produtos na venda, use {K('F11')}.",
           f"Escolha a forma de pagamento e finalize com {K('F10')}."]))
story += section("Classificar o pagamento na tela de abastecimentos",
    p("Permite marcar a forma de pagamento antes de fechar a venda. Precisa estar ativado na chave "
      "<b>PDV-Classifica Pgtos na Tela de Venda</b> (Cadastro do PDV). Peça ao responsável pelo sistema, se ainda não estiver ativa."),
    table(["Classificar", "Atalho", "Filtrar", "Atalho"],
          [["Dinheiro", K("1"), "Dinheiro", K("Alt") + "+" + K("1")],
           ["Cartão", K("2"), "Cartão", K("Alt") + "+" + K("2")],
           ["Notas", K("3"), "Notas", K("Alt") + "+" + K("3")],
           ["Não classificado", K("0"), "Não classificado", K("Alt") + "+" + K("0")]],
          [CW * .3, CW * .2, CW * .3, CW * .2]),
    p(f"Exemplo: pressione {K('3')}, marque os abastecimentos com {K('Espaço')} e pressione {K('3')} novamente."))
story += section("Baixar abastecimento como aferição",
    steps([f"Digite {K('A')} ou {K('B')} para listar os abastecimentos.",
           f"Pressione {K('A')}. Aparece a mensagem \"Selecione os abastecimentos para aferição\".",
           f"Marque os abastecimentos com {K('Espaço')}.",
           f"Pressione {K('A')} de novo e confirme em <b>Sim</b>."]))

# 3
story += [PageBreak(), h1("3. NFC-e: consultar, corrigir e cancelar"),
          lead("Tudo começa na consulta de notas do PDV.")]
story += section(f"Abrir a consulta de NFC-e: {K('CTRL')} + {K('E')}",
    table(["Tecla", "Mostra", "O que dá para fazer"],
          [[K("F1"), "Autorizadas", "Cancelar, reimprimir, visualizar ou enviar por e-mail."],
           [K("F2"), "Contingência", "Corrigir, Corrigir Cliente ou Inutilizar."],
           [K("F3"), "Com Erro", "Corrigir, Corrigir Cliente ou Inutilizar (o motivo aparece na coluna \"Motivo\")."],
           [K("F4"), "Canceladas", "Consulta."],
           [K("F5"), "Inutilizadas", "Consulta."],
           [K("F6"), "Todas", "Consulta."]], [18 * mm, 32 * mm, CW - 50 * mm]))
story += section("Corrigir NFC-e em contingência ou com erro",
    steps([f"Na consulta ({K('CTRL')} + {K('E')}), escolha <b>Contingência</b> {K('F2')} ou <b>Com Erro</b> {K('F3')}.",
           "Selecione o período nas datas e clique na lupa.",
           "Se aparecerem notas, selecione e clique em <b>Corrigir</b>, ou em <b>Corrigir Todas</b>.",
           "Nas notas com erro, leia o motivo exibido. Se precisar ajustar algo no Retaguarda (cadastro do produto ou do cliente), "
           "faça o ajuste, aguarde alguns minutos até o Integra atualizar o PDV e clique em <b>Corrigir</b> de novo.",
           "Se a busca não trouxer nenhuma nota, não há pendências. Confira também se o PDV não está em <b>Modo Contingência</b>."]),
    box("NFC-e com erro ou em contingência pode <b>impedir que o fechamento do caixa/turno chegue ao Retaguarda</b>. "
        "Corrija antes de fechar o turno.", "warn"))
story += section("Cancelar um cupom (NFC-e)",
    steps([f"Pressione {K('CTRL')} + {K('E')} e escolha <b>Autorizadas</b> {K('F1')}.",
           "Selecione o cupom e clique em <b>Cancelar NFCe</b>.",
           "Informe o motivo do cancelamento."]),
    box("O cancelamento deve ser feito em até <b>30 minutos</b> após a emissão.", "warn"))
story += section("Inutilizar uma NFC-e",
    p("Disponível para notas em <b>Contingência</b> ou <b>Com Erro</b>: selecione a nota e clique em <b>Inutilizar</b>."))

# 4
story += [PageBreak(), h1("4. Caixa e turno no WP PDV"),
          lead("Fechamento de turno, coleta de sangrias e troca de valores.")]
story += section(f"Fechar o turno: {K('CTRL')} + {K('F7')}",
    steps(["A primeira tela mostra as <b>NFC-e pendentes</b>. Corrija-as para que o caixa feche no Retaguarda.",
           "Confira o resumo do turno: Apurado (valor disponível), Encerrantes, Aferições, Produtos, Vendas, Cartões, Notas e Despesas.",
           "Na aba Caixas, use <b>Fechar Caixa Selecionado</b> ou <b>Fechar Todos os Caixas</b>.",
           f"Confirme com {K('F10')}, escolha os relatórios que deseja imprimir e pressione {K('F10')} de novo."]),
    p(f"Para fechar só o caixa do operador, use {K('F7')} na tela principal."))
story += section("Coleta de valores (sangrias)",
    steps([f"Acesse <b>Lançamentos</b> {K('F3')} &gt; <b>Coleta de valores</b>.",
           f"Clique em <b>Confirmar</b> {K('F10')}. Todas as sangrias listadas entram na coleta.",
           "Em <b>Coletas realizadas</b> aparecem a data/hora, a quantidade de registros e o valor total."]))
story += section("Troca de valores",
    p(f"Menu <b>Outros</b> {K('F6')} &gt; Troca de Valores. Selecione o cliente, a entrada e a saída pelos atalhos:"),
    table(["Entrada", "Atalho", "Saída", "Atalho"],
          [["Cheque", K("F1"), "Serviço", K("F5")],
           ["Dinheiro", K("F2"), "Cheque troco", K("F6")],
           ["Carta frete", K("F3"), "Vale", K("F7")],
           ["Vale", K("F4"), "Dinheiro", K("F8")],
           ["Cartão", K("F9"), "Transferência bancária", K("F12")],
           ["TEF", K("F11"), "", ""],
           ["Transferência bancária", K("Shift") + "+" + K("F12"), "", ""]],
          [CW * .32, CW * .18, CW * .32, CW * .18]),
    p("No final, são impressos os comprovantes. O campo <b>Taxa</b> mostra o valor descontado do total devolvido ao cliente."))

# 5
story += [PageBreak(), h1("5. WP Pay (maquininha)"),
          lead("Vendas, pagamentos e operações de caixa no smartPOS.")]
story += section("Login",
    p("Digite o <b>código do funcionário</b> e a <b>senha</b>. O WP Pay só aceita <b>senhas numéricas</b>."))
story += section("Receber um abastecimento",
    steps(["Toque em <b>Abastecimento</b> e no bico desejado.",
           "Toque no abastecimento a receber.",
           "Escolha a forma: <b>Dinheiro</b>, <b>Crédito</b>, <b>Débito</b> ou <b>QR Code</b> (carteiras digitais).",
           "Confirme o valor e toque em <b>Confirmar</b>.",
           "Em \"Vincular Funcionário ao Produto\", toque em <b>Atualizar</b> e depois em <b>Finalizar</b>."]),
    box("<b>Pagar com duas formas:</b> escolha a primeira forma e digite um valor <b>menor que o total</b>. "
        "O sistema libera a escolha da segunda forma para o restante."))
story += section("Abastecimento + produtos",
    steps(["Selecione o abastecimento e toque no ícone do <b>carrinho</b> no alto da tela.",
           "Encontre o produto pelos grupos ou pela pesquisa, informe a quantidade e toque em <b>Confirmar</b>.",
           "Use <b>Adicionar produtos</b> para incluir mais itens.",
           "Toque em <b>Finalizar compra</b> e escolha a forma de pagamento."]),
    p("Para vender <b>só produtos</b>, toque em <b>Produtos</b> na tela inicial e siga os mesmos passos."))
story += section("Venda a prazo (cliente identificado)",
    steps(["Toque em <b>Abastecimento</b> e no ícone de pessoa com lupa (canto superior direito).",
           "Pesquise por Razão Social, Nome Fantasia, Placa ou CPF, ou leia o QR Code do cliente com a câmera.",
           "Selecione o cliente, o motorista e a placa (se necessário) e confirme o endereço.",
           "Selecione o abastecimento, escolha a forma <b>a prazo</b> e confirme.",
           "Finalize e, se quiser, imprima a <b>promissória</b>."]))
story += section("Preset (pagamento antes de abastecer)",
    steps(["Menu <b>Abastecimentos</b> &gt; <b>Presets</b>.",
           "Escolha o bico.",
           "Selecione o valor ou a litragem (pré-definido ou digitado) e confirme.",
           "A bomba libera o abastecimento até o valor pago."]),
    p("Se a opção não aparecer, o Preset precisa ser ativado no cadastro do PDV. Fale com o responsável pelo sistema."))
story += section("Sangria, suprimento e relatório de fechamento",
    table(["Operação", "Caminho", "Para que serve"],
          [["Sangria", "Tela inicial &gt; Operações &gt; Sangria", "Retirar valores do caixa. Imprime comprovante."],
           ["Suprimento", "Tela inicial &gt; Operações &gt; Suprimento", "Colocar valores no caixa (troco). Imprime comprovante."],
           ["Fechamento", "Tela inicial &gt; Operações &gt; Relatório de Fechamento de caixa",
            "Escolha as datas inicial e final e imprima o relatório."]], [26 * mm, 70 * mm, CW - 96 * mm]))

# 6
story += [h1("6. Conveniência (PDV Android)")]
story += table(["Operação", "Como fazer"],
               [["Sangria", "Aba <b>Operações</b> &gt; Sangria. Confira o resumo de créditos e débitos, deslize para o lado, "
                            "informe os valores e confirme. Imprime comprovante."],
                ["Fechar caixa", "Aba <b>Operações</b> &gt; Fechar caixa. Ao entrar de novo no aplicativo, outro caixa é aberto automaticamente."],
                ["Fechar turno", "Aba <b>Operações</b> &gt; Fechar turno. O app avisa sobre caixas abertos. "
                                 "Ao fechar todos, o turno é encerrado e você é desconectado."]], [30 * mm, CW - 30 * mm])

# 7
story += [PageBreak(), h1("7. WP Retaguarda"),
          lead("Senhas, vendas, preços e descontos.")]
story += section("Alterar a própria senha",
    steps(["Acesse <b>webPosto &gt; Administração &gt; Alterar Senha</b>.",
           "Digite a senha atual, a nova senha e repita a nova senha.",
           "Clique em <b>Salvar</b>."]),
    box("<b>Esqueceu a senha?</b> Por segurança, o sistema não tem recuperação automática. Peça a um usuário com permissão "
        "de cadastro de usuários para definir uma nova senha em <b>webPosto &gt; Administração &gt; Usuário</b> "
        "(buscar o usuário, Alterar, nova senha, Salvar)."))
story += section("Consultar vendas e trocar o cliente de um cupom",
    steps(["Acesse <b>webPosto &gt; Movimentos &gt; Visualizar Vendas</b>.",
           "Informe o número do cupom em \"Consultar por\", confira se as datas incluem a emissão e clique em Consultar.",
           "Dê um clique duplo na venda.",
           "No campo Cliente, clique nos três pontinhos, escolha o cliente correto e salve. "
           "O mesmo vale para Funcionário, Placa, KM e Ordem de Abastecimento."]),
    box("Essas alterações <b>não modificam a NFC-e/NF-e</b> já emitida. Não é possível alterar um cupom já acobertado por NF-e. "
        "Para saber se o cupom está vinculado a uma nota, veja a coluna <b>NF</b> ou o campo \"Nota de Saída\".", "warn"))
story += section("Trocar preço",
    p("Acesse <b>Movimentos &gt; Operações &gt; Troca de Preço</b>."),
    bullets(["<b>Combustível:</b> escolha \"início do turno\" ou \"programado\", selecione a filial, os combustíveis e o novo preço, e salve.",
             "<b>Produtos:</b> escolha \"início do turno\", \"programado\" ou \"imediato\", selecione a filial e os grupos ou produtos, "
             "informe o novo preço e salve. Na pesquisa de produtos, digite <b>%</b> e Enter para listar todos."]))
story += section("Liberar desconto no PDV",
    steps(["Dê ao funcionário a permissão <b>Efetuar Descontos</b>: em <b>Cadastros &gt; Funcionários</b> (aba Config. PDV) "
           "ou no <b>Cadastro de Funções</b> da função dele.",
           "Em <b>Cadastros &gt; Desconto</b>, inclua os produtos e o percentual máximo de desconto. "
           "Use <b>Modificar em Lote</b> para aplicar o mesmo percentual a um grupo.",
           "Salve, aguarde alguns minutos e <b>reinicie o PDV</b>."]),
    p("Para permitir desconto no total do cupom (e não só item a item), a chave <b>PDV - Permite desconto no fim do cupom</b> "
      "do cadastro do PDV precisa estar como SIM."))
story += section("Autorizar operações pelo celular (WP Mobile)",
    p("Quando o funcionário tenta uma operação sem permissão no PDV, ele pode clicar em <b>Solicitar Aprovação</b>. "
      "O PDV fica aguardando até que um usuário autorize o pedido no aplicativo <b>WP Mobile</b>, em Autorizações PDV."))

# 8
story += [PageBreak(), h1("8. Problemas comuns e soluções rápidas")]
story += table(["Sintoma", "O que fazer"],
    [["Ícone do Concentrador, da Impressora ou do Integra <b>amarelo/vermelho</b> no PDV", "Chame o suporte. Com o Integra em alerta, as vendas podem não chegar ao Retaguarda."],
     ["NFC-e em contingência ou com erro", f"{K('CTRL')}+{K('E')} &gt; {K('F2')} ou {K('F3')} &gt; Corrigir (seção 3)."],
     ["Caixa/turno não aparece fechado no Retaguarda", "Verifique se há NFC-e pendente (contingência ou erro) e corrija."],
     ["Preciso cancelar um cupom", f"{K('CTRL')}+{K('E')} &gt; Autorizadas {K('F1')} &gt; Cancelar NFCe. Prazo: até 30 minutos após a emissão."],
     ["Mensagem \"Este produto é do tipo USO CONSUMO não pode ser Vendido!\"",
      "No Retaguarda: Cadastros &gt; Produtos &gt; selecione o produto &gt; aba Estoque &gt; marque <b>Controle de Estoque</b>."],
     ["Funcionário não consegue dar desconto", "Confira a permissão \"Efetuar Descontos\" e o cadastro de desconto do produto. Depois reinicie o PDV (seção 7)."],
     ["Esqueci minha senha do Retaguarda", "Peça a um usuário com permissão para definir uma nova senha (seção 7)."],
     ["Senha não funciona no WP Pay", "O WP Pay aceita apenas senhas numéricas."],
     ["Venda saiu com o cliente errado", "Visualizar Vendas &gt; abrir a venda &gt; trocar o cliente (não altera a nota já emitida)."],
     ["Erro \"Element ... infRespTec is unexpected\" ao emitir NFC-e", "Chame o suporte. É preciso ajustar a atualização automática do PDV."],
     ["WP Pay mostra \"Erro ao iniciar operadora, verifique a configuração do PDV\"", "Chame o suporte. O ajuste é feito pela equipe técnica."]],
    [CW * .42, CW * .58])

# 9
story += [h1("9. Quando chamar o suporte")]
story += [p("Fale com o suporte webPosto <b>imediatamente</b> quando:")]
story += bullets(["O PDV não abre ou nenhuma venda sai.",
                  "As bombas estão sem comunicação, ou o TEF/Pix está fora do ar em todos os caixas.",
                  "Notas continuam rejeitadas depois de seguir a seção 3, ou há muitas notas em contingência.",
                  "Algum ícone de serviço do PDV está amarelo ou vermelho.",
                  "Há valores divergentes no caixa ou no financeiro, ou suspeita de perda de dados."])
story += [Spacer(1, 6), p("<b>Para agilizar o atendimento, tenha em mãos:</b>")]
story += bullets(["Nome do posto e filial.",
                  "Sistema afetado: Retaguarda, PDV, WP Pay, PDV Android ou Mobile.",
                  "A mensagem de erro exata, ou um print da tela.",
                  "O que você já tentou fazer.",
                  "Desde quando o problema acontece, e se começou depois de alguma atualização."])
story += box("<b>Segurança:</b> o suporte nunca vai pedir a senha do seu certificado digital ou os dados completos de cartões. "
             "Não compartilhe senhas por mensagem.", "warn")


def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = Doc(OUT, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=20 * mm, bottomMargin=18 * mm,
              title="Guia Rápido de Autoajuda webPosto", author="webPosto", subject="Autoajuda para clientes webPosto")
    fr = Frame(M, 18 * mm, W - 2 * M, H - 38 * mm, id="f")
    doc.addPageTemplates([PageTemplate("capa", frames=[Frame(0, 0, W, H, id="c")], onPage=cover),
                          PageTemplate("conteudo", frames=[fr], onPage=page)])
    doc.multiBuild(story)
    print(OUT)


if __name__ == "__main__":
    build()

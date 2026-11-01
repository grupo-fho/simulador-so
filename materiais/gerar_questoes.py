"""Gera material de estudo em Markdown e DOCX usando somente a biblioteca padrão.

Uso na raiz: python -B materiais/gerar_questoes.py
Este utilitário de documentação escreve os dois materiais em docs/.
Ele é independente da aplicação: main.py não o importa nem grava resultados.
"""

from collections import Counter
from pathlib import Path
import random
import re
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from banco_questoes import QUESTOES


RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "docs"
NOME = "QUESTOES_ESTUDO"
TITULO = "120 questões para defender e modificar o simulador de SO"
INTRODUCAO = [
    "Material de preparação para a apresentação: 120 questões autorais, com cinco alternativas (A–E), uma única resposta correta e gabarito comentado.",
    "O conteúdo está vinculado à implementação deste repositório. Os pedidos atribuídos ao professor são possibilidades de treino, e não uma previsão das perguntas reais.",
    "As questões distinguem o comportamento atual das extensões propostas. Trechos são recortes ou propostas localizadas, não programas completos; nomes como thread, pcb, fila e config pressupõem o contexto informado. Nenhuma mudança proposta foi aplicada ao simulador por este material.",
    "Convenções: uma CPU lógica; prioridades não preemptivas; menor número indica maior prioridade; empates seguem a fila, salvo pedido explícito; cada despacho conta como troca, inclusive o primeiro; contexto padrão zero. Referências, submissões de E/S e chamadas de arquivos são instantâneas; somente cpu consome CPU útil. Tempos de serviço são lógicos, sem espera real.",
    "Salvo indicação contrária, cenários numéricos não possuem outros eventos, usam os processos na ordem de admissão indicada e consideram todo o horizonte até a drenagem de E/S. Intervalos [a,b) incluem o início e excluem o fim.",
    "Todos os arquivos e dispositivos mencionados nas questões são virtuais, exceto quando o enunciado fala expressamente do código-fonte, da entrada JSON ou do sistema hospedeiro.",
]
ROTEIRO = [
    "Primeira rodada: responda sem consultar o gabarito. Para cálculos, desenhe a linha do tempo de CPU e dispositivos.",
    "Segunda rodada: consulte a explicação e localize o método indicado. Explique oralmente por que a resposta está correta e por que as demais não atendem ao enunciado.",
    "Terceira rodada: pratique as alterações em uma cópia do projeto, primeiro prevendo a saída de uma carga pequena e depois executando os testes relevantes.",
    "Nas extensões, identifique todas as camadas envolvidas: formato da carga, validação, modelo, núcleo, eventos, interface, testes e documentação. Uma mudança em um único trecho nem sempre completa a funcionalidade.",
    "Use python main.py --cenario verificacao para conferir escalonamento e python -B -m unittest discover -s testes -v para executar a suíte original.",
    "Fonte: código deste repositório, README, guia de apresentação, relatório e especificacoes.pdf. Material elaborado com assistência de OpenAI Codex; revise as respostas junto com a versão do código usada na avaliação.",
]


def preparar_questoes():
    """Mantém 24 respostas por letra sem padrão cíclico na sequência final."""
    assert len(QUESTOES) == 120
    assert len({q.titulo for q in QUESTOES}) == 120
    assert all(len(q.distratores) == 4 for q in QUESTOES)
    assert all(len(set((q.correta, *q.distratores))) == 5 for q in QUESTOES)
    assert len(Counter(q.secao for q in QUESTOES)) == 12
    assert set(Counter(q.secao for q in QUESTOES).values()) == {10}
    sorteio = random.Random(20261031)
    posicoes = list(range(5)) * 24
    sorteio.shuffle(posicoes)
    saida = []
    for numero, (questao, posicao) in enumerate(zip(QUESTOES, posicoes), 1):
        alternativas = list(questao.distratores)
        sorteio.shuffle(alternativas)
        alternativas.insert(posicao, questao.correta)
        saida.append((numero, questao, alternativas, "ABCDE"[posicao]))
    assert Counter(item[3] for item in saida) == Counter({letra: 24 for letra in "ABCDE"})
    return saida


def gerar_markdown(questoes):
    conteudo = [f"# {TITULO}", "", "## Como usar", ""]
    for paragrafo in INTRODUCAO:
        conteudo += [paragrafo, ""]
    conteudo += ["## Roteiro de preparação", ""]
    for indice, paragrafo in enumerate(ROTEIRO, 1):
        conteudo += [f"{indice}. {paragrafo}", ""]
    conteudo += ["## Distribuição do conteúdo", "", "| Questões | Tema |", "|---|---|"]
    for secao, quantidade in Counter(q.secao for q in QUESTOES).items():
        primeiro = next(n for n, q, _, _ in questoes if q.secao == secao)
        conteudo += [f"| {primeiro:03d}–{primeiro + quantidade - 1:03d} | {secao} |"]
    conteudo += ["", "As alternativas aparecem antes do gabarito para permitir autoavaliação. Cada questão vale um ponto; total de 120 pontos.", ""]
    anterior = None
    for numero, questao, alternativas, letra in questoes:
        if questao.secao != anterior:
            conteudo += [f"## {questao.secao}", ""]
            anterior = questao.secao
        conteudo += [f"### Questão {numero:03d} — {questao.titulo}", "",
                     f"**Tipo:** {questao.tipo}", "", questao.enunciado, ""]
        if questao.codigo:
            conteudo += ["```python", questao.codigo, "```", ""]
        for rotulo, alternativa in zip("ABCDE", alternativas):
            conteudo += [f"**{rotulo})** {alternativa}", ""]
    conteudo += ["---", "", "## Gabarito rápido", "",
                 "| " + " | ".join(f"Coluna {i}" for i in range(1, 11)) + " |",
                 "| " + " | ".join("---" for _ in range(10)) + " |"]
    for inicio in range(0, 120, 10):
        conteudo += ["| " + " | ".join(f"{n:03d}: **{letra}**" for n, _, _, letra in questoes[inicio:inicio+10]) + " |"]
    conteudo += ["", "As colunas organizam dez questões por linha; o número dentro da célula identifica a questão.", "",
                 "## Gabarito comentado e pontos de alteração", ""]
    anterior = None
    for numero, questao, _, letra in questoes:
        if questao.secao != anterior:
            conteudo += [f"### {questao.secao}", ""]
            anterior = questao.secao
        conteudo += [f"#### Questão {numero:03d} — {letra}", "",
                     f"**Resposta:** {questao.correta}", "",
                     f"**Comentário:** {questao.explicacao}", "",
                     f"**Onde estudar/alterar:** {questao.referencia}", ""]
        if questao.pratica:
            conteudo += [f"**Treino adicional:** {questao.pratica}", ""]
    conteudo += ["## Conferência final antes da apresentação", "",
                 "- Consigo explicar quem possui os recursos e quem disputa a CPU?",
                 "- Consigo prever a ordem e os tempos de uma carga pequena?",
                 "- Sei quais alterações exigem invalidar um evento já agendado?",
                 "- Sei distinguir arquivo virtual em RAM de arquivo de entrada da aplicação?",
                 "- Consigo alterar uma regra sem contornar validação, log ou máquina de estados?",
                 "- Consigo indicar um teste que falha antes e passa depois da alteração solicitada?", ""]
    return "\n".join(conteudo)


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
ET.register_namespace("w", W)
ET.register_namespace("r", R)


def elemento(pai, nome, atributos=None):
    return ET.SubElement(pai, f"{{{W}}}{nome}",
                         {f"{{{W}}}{chave}": str(valor) for chave, valor in (atributos or {}).items()})


def paragrafo(pai, texto="", estilo="Normal", manter=False, nova_pagina=False):
    p = elemento(pai, "p")
    props = elemento(p, "pPr")
    elemento(props, "pStyle", {"val": estilo})
    if manter:
        elemento(props, "keepNext")
    if nova_pagina:
        elemento(props, "pageBreakBefore")
    elemento(props, "keepLines")
    for indice, parte in enumerate(texto.split("\n")):
        if indice:
            elemento(elemento(p, "r"), "br")
        run = elemento(p, "r")
        texto_xml = elemento(run, "t")
        texto_xml.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        texto_xml.text = parte
    return p


def tabela_gabarito(pai, questoes):
    tabela = elemento(pai, "tbl")
    props = elemento(tabela, "tblPr")
    elemento(props, "tblW", {"w": 9638, "type": "dxa"})
    elemento(props, "tblLayout", {"type": "fixed"})
    bordas = elemento(props, "tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        elemento(bordas, lado, {"val": "single", "sz": 4, "color": "B9C9D6"})
    grade = elemento(tabela, "tblGrid")
    for _ in range(10):
        elemento(grade, "gridCol", {"w": 963})
    for inicio in range(0, 120, 10):
        linha = elemento(tabela, "tr")
        elemento(elemento(linha, "trPr"), "cantSplit")
        for numero, _, _, letra in questoes[inicio:inicio+10]:
            celula = elemento(linha, "tc")
            propriedades = elemento(celula, "tcPr")
            elemento(propriedades, "tcW", {"w": 963, "type": "dxa"})
            if inicio % 20 == 0:
                elemento(propriedades, "shd", {"fill": "EDF3F7"})
            paragrafo(celula, f"{numero:03d}: {letra}", "TableText")


def criar_estilos():
    styles = ET.Element(f"{{{W}}}styles")
    defaults = elemento(styles, "docDefaults")
    rpr = elemento(elemento(defaults, "rPrDefault"), "rPr")
    elemento(rpr, "rFonts", {"ascii": "Calibri", "hAnsi": "Calibri"})
    elemento(rpr, "sz", {"val": 22})
    elemento(rpr, "lang", {"val": "pt-BR"})
    ppr = elemento(elemento(defaults, "pPrDefault"), "pPr")
    elemento(ppr, "spacing", {"after": 100, "line": 264, "lineRule": "auto"})
    elemento(ppr, "widowControl")
    definicoes = [
        ("Normal", "Normal", 22, False, None),
        ("Title", "Título", 40, True, "17364D"),
        ("Subtitle", "Subtítulo", 25, False, "536B7D"),
        ("Heading1", "Título 1", 30, True, "17364D"),
        ("Heading2", "Título 2", 25, True, "234F6A"),
        ("Question", "Questão", 24, True, "17364D"),
        ("Option", "Alternativa", 21, False, None),
        ("Code", "Código", 18, False, "163747"),
        ("Small", "Referência", 19, False, "526572"),
        ("TableText", "Gabarito em tabela", 19, True, "17364D"),
    ]
    for identificador, nome, tamanho, negrito, cor in definicoes:
        style = elemento(styles, "style", {"type": "paragraph", "styleId": identificador})
        if identificador == "Normal":
            style.set(f"{{{W}}}default", "1")
        elemento(style, "name", {"val": nome})
        if identificador != "Normal":
            elemento(style, "basedOn", {"val": "Normal"})
        ppr = elemento(style, "pPr")
        if identificador in {"Heading1", "Heading2", "Question"}:
            elemento(ppr, "keepNext")
            elemento(ppr, "spacing", {"before": 200, "after": 120})
        if identificador == "Heading1":
            elemento(ppr, "outlineLvl", {"val": 0})
        elif identificador in {"Heading2", "Question"}:
            elemento(ppr, "outlineLvl", {"val": 1})
        if identificador == "Option":
            elemento(ppr, "ind", {"left": 220, "hanging": 220})
            elemento(ppr, "spacing", {"after": 65})
        if identificador == "Code":
            elemento(ppr, "shd", {"fill": "F0F4F7"})
            elemento(ppr, "ind", {"left": 160, "right": 100})
            elemento(ppr, "spacing", {"before": 90, "after": 90, "line": 240, "lineRule": "auto"})
        if identificador == "TableText":
            elemento(ppr, "jc", {"val": "center"})
            elemento(ppr, "spacing", {"before": 70, "after": 70})
        rpr = elemento(style, "rPr")
        elemento(rpr, "sz", {"val": tamanho})
        if negrito:
            elemento(rpr, "b")
        if cor:
            elemento(rpr, "color", {"val": cor})
        if identificador == "Code":
            elemento(rpr, "rFonts", {"ascii": "Consolas", "hAnsi": "Consolas"})
    return styles


def xml_bytes(raiz):
    return ET.tostring(raiz, encoding="utf-8", xml_declaration=True)


def gerar_docx(questoes, destino):
    document = ET.Element(f"{{{W}}}document")
    body = elemento(document, "body")
    paragrafo(body, "SIMULADOR DE SISTEMAS OPERACIONAIS", "Subtitle")
    paragrafo(body, TITULO, "Title")
    paragrafo(body, "Caderno de questões com alternativas A–E\nGabarito rápido e comentários ao final", "Subtitle")
    paragrafo(body, "Nome: __________________________________________\nData: ____/____/________    Acertos: ______ / 120")
    paragrafo(body, "12 temas • conceitos • rastreamento • depuração • alterações de código", "Small")
    paragrafo(body, "Baseado na versão do simulador deste repositório.\nElaborado em 31/10/2026 para estudo e preparação da apresentação.", "Small")
    paragrafo(body, "Como estudar", "Heading1", nova_pagina=True)
    for texto in INTRODUCAO:
        paragrafo(body, texto)
    for indice, texto in enumerate(ROTEIRO, 1):
        paragrafo(body, f"{indice}. {texto}")
    paragrafo(body, "Mapa das questões", "Heading1", nova_pagina=True)
    for secao, quantidade in Counter(q.secao for q in QUESTOES).items():
        primeiro = next(n for n, q, _, _ in questoes if q.secao == secao)
        paragrafo(body, f"{primeiro:03d}–{primeiro + quantidade - 1:03d}  |  {secao}")
    paragrafo(body, "Use os títulos no painel de navegação do Word para localizar temas e questões.", "Small")
    anterior = None
    for numero, questao, alternativas, _ in questoes:
        if anterior != questao.secao:
            paragrafo(body, questao.secao, "Heading1", nova_pagina=True)
            anterior = questao.secao
        paragrafo(body, f"Questão {numero:03d} — {questao.titulo}", "Question", manter=True)
        paragrafo(body, f"Tipo: {questao.tipo}", "Small", manter=True)
        paragrafo(body, questao.enunciado, manter=True)
        if questao.codigo:
            paragrafo(body, questao.codigo, "Code", manter=True)
        for indice, (rotulo, alternativa) in enumerate(zip("ABCDE", alternativas)):
            paragrafo(body, f"{rotulo}) {alternativa}", "Option", manter=indice < 4)
    paragrafo(body, "Gabarito rápido", "Heading1", nova_pagina=True)
    paragrafo(body, "Cada célula informa o número da questão e a alternativa correta.")
    tabela_gabarito(body, questoes)
    paragrafo(body, "Pontuação: um ponto por questão, máximo de 120. Para dominar uma alteração, explique também a razão e a verificação necessária.")
    paragrafo(body, "Gabarito comentado e pontos de alteração", "Heading1", nova_pagina=True)
    anterior = None
    for numero, questao, _, letra in questoes:
        if anterior != questao.secao:
            paragrafo(body, questao.secao, "Heading2")
            anterior = questao.secao
        paragrafo(body, f"Questão {numero:03d} — resposta {letra}", "Question", manter=True)
        paragrafo(body, "Resposta: " + questao.correta, manter=True)
        paragrafo(body, "Comentário: " + questao.explicacao)
        paragrafo(body, "Onde estudar/alterar: " + questao.referencia, "Small")
        if questao.pratica:
            paragrafo(body, "Treino adicional: " + questao.pratica)
    paragrafo(body, "Conferência final antes da apresentação", "Heading1", nova_pagina=True)
    for texto in [
        "Consigo explicar quem possui os recursos e quem disputa a CPU?",
        "Consigo prever a ordem e os tempos de uma carga pequena?",
        "Sei quais alterações exigem invalidar um evento já agendado?",
        "Sei distinguir arquivo virtual em RAM de arquivo de entrada da aplicação?",
        "Consigo alterar uma regra sem contornar validação, log ou máquina de estados?",
        "Consigo indicar um teste que falha antes e passa depois da alteração solicitada?",
    ]:
        paragrafo(body, "[  ] " + texto)
    sect = elemento(body, "sectPr")
    elemento(sect, "footerReference", {"type": "default"}).set(f"{{{R}}}id", "rIdFooter")
    elemento(sect, "pgSz", {"w": 11906, "h": 16838})
    elemento(sect, "pgMar", {"top": 1134, "right": 1134, "bottom": 1134,
                             "left": 1134, "header": 567, "footer": 567, "gutter": 0})
    footer = ET.Element(f"{{{W}}}ftr")
    p = paragrafo(footer, "Simulador de SO • Caderno de estudo • Página ", "Small")
    campo = elemento(p, "fldSimple", {"instr": "PAGE"})
    elemento(elemento(campo, "r"), "t").text = "1"
    settings = ET.Element(f"{{{W}}}settings")
    elemento(settings, "updateFields", {"val": "true"})
    conteudos = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>'''
    raiz_rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rIdDocument" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rIdCore" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>'''
    document_rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
<Relationship Id="rIdFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>'''
    propriedades = '''<?xml version="1.0" encoding="UTF-8"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <dc:title>120 questões — Simulador de SO</dc:title><dc:language>pt-BR</dc:language>
 <dc:creator>Material de estudo do projeto, com assistência de OpenAI Codex</dc:creator>
 <dc:description>Questões A–E, análise de código e gabarito comentado.</dc:description>
 <dcterms:created xsi:type="dcterms:W3CDTF">2026-10-31T00:00:00Z</dcterms:created>
</cp:coreProperties>'''
    with ZipFile(destino, "w", compression=ZIP_DEFLATED) as pacote:
        for caminho, conteudo in {
            "[Content_Types].xml": conteudos.encode("utf-8"),
            "_rels/.rels": raiz_rels.encode("utf-8"),
            "word/document.xml": xml_bytes(document),
            "word/_rels/document.xml.rels": document_rels.encode("utf-8"),
            "word/styles.xml": xml_bytes(criar_estilos()),
            "word/settings.xml": xml_bytes(settings),
            "word/footer1.xml": xml_bytes(footer),
            "docProps/core.xml": propriedades.encode("utf-8"),
        }.items():
            pacote.writestr(caminho, conteudo)


def verificar_artefatos(questoes):
    markdown = (PASTA / f"{NOME}.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^### Questão \d{3} —", markdown, re.M)) == 120
    assert len(re.findall(r"^#### Questão \d{3} — [A-E]$", markdown, re.M)) == 120
    for letra in "ABCDE":
        assert len(re.findall(rf"^\*\*{letra}\)\*\* ", markdown, re.M)) == 120
    with ZipFile(PASTA / f"{NOME}.docx") as pacote:
        assert pacote.testzip() is None
        for caminho in pacote.namelist():
            ET.fromstring(pacote.read(caminho))
        document = ET.fromstring(pacote.read("word/document.xml"))
        textos = [t.text for t in document.iter(f"{{{W}}}t") if t.text]
        assert sum(bool(re.match(r"Questão \d{3} — (?!resposta)", t)) for t in textos) == 120
        assert sum(bool(re.match(r"Questão \d{3} — resposta [A-E]$", t)) for t in textos) == 120
        for letra in "ABCDE":
            assert sum(t.startswith(letra + ") ") for t in textos) == 120
        # Todo enunciado e alternativa deve aparecer no Word, sem perda de acentos.
        for numero, questao, alternativas, letra in questoes:
            assert questao.enunciado in textos
            assert all(f"{rotulo}) {texto}" in textos for rotulo, texto in zip("ABCDE", alternativas))
            assert f"Questão {numero:03d} — resposta {letra}" in textos


def main():
    questoes = preparar_questoes()
    PASTA.mkdir(exist_ok=True)
    (PASTA / f"{NOME}.md").write_text(gerar_markdown(questoes), encoding="utf-8")
    gerar_docx(questoes, PASTA / f"{NOME}.docx")
    verificar_artefatos(questoes)
    print("Gerados e verificados: 120 questões, 600 alternativas e 120 respostas comentadas em MD e DOCX.")
    print("Tipos:", dict(Counter(q.tipo for q in QUESTOES)))
    print("Questões com código:", sum(bool(q.codigo) for q in QUESTOES))
    print("Gabarito:", dict(sorted(Counter(q[3] for q in questoes).items())))


if __name__ == "__main__":
    main()

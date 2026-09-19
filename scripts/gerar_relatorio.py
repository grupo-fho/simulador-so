#!/usr/bin/env python3
"""Gerador opcional do PDF: Python 3 + reportlab. Não participa do simulador."""
from pathlib import Path
import csv
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

RAIZ = Path(__file__).resolve().parents[1]
with (RAIZ/'resultados/experimentos/comparacoes.csv').open(encoding='utf-8') as arquivo:
    cenarios = {linha['cenario']: linha for linha in csv.DictReader(arquivo)}
FONTES = Path(os.environ.get('SO_FONT_DIR', '/usr/share/fonts/truetype/dejavu'))
if (FONTES / 'DejaVuSans.ttf').exists():
    pdfmetrics.registerFont(TTFont('Helvetica', str(FONTES / 'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('Helvetica-Bold', str(FONTES / 'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFontFamily('Helvetica', normal='Helvetica', bold='Helvetica-Bold')
AZUL = colors.HexColor('#163650')
VERDE = colors.HexColor('#087F8C')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TituloRelatorio', fontName='Helvetica-Bold', fontSize=25, leading=30, textColor=AZUL, spaceAfter=18))
styles.add(ParagraphStyle(name='SubtituloRelatorio', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=AZUL, spaceAfter=12))
styles.add(ParagraphStyle(name='TextoRelatorio', fontName='Helvetica', fontSize=10, leading=15, spaceAfter=10))
styles.add(ParagraphStyle(name='PequenoRelatorio', fontName='Helvetica', fontSize=8, leading=11, spaceAfter=7))
styles.add(ParagraphStyle(name='CelulaRelatorio', fontName='Helvetica', fontSize=8, leading=11))
historia=[]
def texto(conteudo, estilo='TextoRelatorio'):
    historia.append(Paragraph(conteudo, styles[estilo]))
def titulo(numero, nome):
    texto(f'{numero} / {nome}', 'SubtituloRelatorio')
def pagina():
    historia.append(PageBreak())
def tabela(cabecalho, linhas, larguras):
    dados = [[Paragraph(escape(str(c)), styles['CelulaRelatorio']) for c in linha] for linha in [cabecalho]+linhas]
    tab=Table(dados, colWidths=larguras, repeatRows=1, hAlign='LEFT')
    tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E3EEF3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),1,VERDE),('LINEBELOW',(0,1),(-1,-1),0.3,colors.HexColor('#D4DEE4')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    historia.extend([tab, Spacer(1,14)])
def numero(cenario, campo, casas=2):
    return f'{float(cenarios[cenario][campo]):.{casas}f}'.replace('.',',')
def arquitetura():
    desenho=Drawing(495,190)
    caixas=[(135,148,225,32,'Main / Configuracao / Carga'),(170,91,155,32,'Simulador + Evento'),(0,22,115,32,'Escalonador'),(126,22,115,32,'Memoria'),(252,22,115,32,'Dispositivo'),(378,22,115,32,'Arquivos')]
    for x,y,w,h,rotulo in caixas:
        desenho.add(Rect(x,y,w,h,rx=4,fillColor=colors.HexColor('#EAF1F5'),strokeColor=AZUL,strokeWidth=.7))
        desenho.add(String(x+w/2,y+12,rotulo,fontName='Helvetica',fontSize=9,textAnchor='middle',fillColor=AZUL))
    desenho.add(Line(247,148,247,123,strokeColor=VERDE))
    for centro in [57,183,309,435]:
        desenho.add(Line(247,91,centro,54,strokeColor=VERDE))
    desenho.add(String(247,4,'Processo (PCB), ThreadSimulada (TCB) e Metricas integram os mecanismos.',fontSize=8,textAnchor='middle',fillColor=AZUL))
    historia.append(desenho)

texto('SIMULADOR DIDÁTICO<br/>DE SISTEMAS OPERACIONAIS','TituloRelatorio')
texto('Relatório técnico • implementação CLI com alvo Java 27<br/>16 de setembro de 2026','PequenoRelatorio')
titulo('01','Objetivo e escopo')
texto('O projeto reproduz uma CPU, processos com múltiplas threads, paginação, dispositivos e um sistema de arquivos hierárquico. O tempo é lógico: a velocidade do computador hospedeiro não interfere nas métricas. A carga é externa ao código e os eventos permitem reconstruir a execução.')
texto('Foram implementados os mecanismos obrigatórios do enunciado Trabalho SO.pdf. A prioridade é não preemptiva; o menor número representa maior prioridade. A interface gráfica foi acrescentada como extensão de apresentação; seu escopo está no adendo final. O projeto usa somente a biblioteca padrão de Java e não cria threads reais para simular concorrência.')
arquitetura()
texto('O núcleo coordena os mecanismos; cada mecanismo concentra sua própria regra. Processo e ThreadSimulada exercem os papéis de PCB e TCB. O diagrama completo de classes está em docs/diagrama-classes.mmd e as convenções detalhadas em docs/arquitetura.md.')
texto('<b>Clareza do código.</b> Nomes de domínio em português, loops explícitos, ausência de camadas artificiais e dependências dispensáveis seguem o Markdown fornecido. As entidades são internas ao pacote; estados e filas têm acesso controlado. Não foi usada herança sem relação de domínio.')
texto('<b>Autoria e apoio.</b> Esta implementação e este relatório foram produzidos com assistência do ChatGPT/Codex, declarada no README. O grupo deve revisar e compreender integralmente o material. Não foram criados nomes de autores, participação fictícia ou histórico artificial de commits.','PequenoRelatorio')
pagina()
titulo('02','Clock, estados e escalonamento')
texto('O próximo evento determina o avanço do clock. No mesmo instante, a ordem é: conclusões de E/S e paginação; chegadas; término de unidade da CPU; fim da troca de contexto. Dentro do mesmo tipo vale a sequência de inserção. Na ausência de trabalho, o clock salta diretamente ao próximo evento.')
tabela(['Unidade','Informações e regra'],[
['PCB / Processo','ID, prioridade, chegada, estado agregado, contexto da última thread, espaço lógico, threads e descritores locais.'],
['TCB / ThreadSimulada','ID, processo dono, estado, PC, restante do surto, acumulador, pilha, caixa de entrada e tempos.'],
['Estados de thread','NOVO → PRONTO → EXECUTANDO; da execução pode ir a PRONTO, BLOQUEADO ou FINALIZADO; BLOQUEADO retorna a PRONTO.'],
['Estado de processo','Derivado das threads. Finaliza somente quando todas terminam e não resta E/S pendente. Cada alteração registra causa.']], [100,395])
texto('FCFS escolhe a primeira entrada na fila. RR usa a mesma ordem e devolve a thread ao final da fila ao esgotar o quantum. Prioridade acrescenta o valor numérico antes da ordem de entrada. Empates seguem entrada e, por último, nome completo. Uma chegada com prioridade maior não interrompe a thread atual.')
texto('Cada despacho, inclusive o primeiro ou para a mesma thread, cobra o custo de contexto. A escolha ocorre ao fim desse intervalo e considera chegadas ocorridas durante a troca. Não se executa carga útil na troca. Bloqueio e término têm precedência sobre preempção quando coincidem com o limite do quantum.')
texto('CPU N executa N unidades; cada outra instrução custa uma unidade para emitir a operação. Faltas e E/S têm tempo de serviço adicional. Se a última instrução bloquear, a thread retorna à fila e encerra no próximo despacho, sem nova unidade útil. Essa última troca também é contabilizada.')
titulo('03','Definições das métricas')
texto('Retorno = finalização − chegada. Resposta = início da primeira instrução − chegada. Espera soma intervalos PRONTO, incluindo a espera por contexto. Por processo, a resposta é a primeira das threads e a espera informada é a soma das esperas das threads, não o tempo de permanência do PCB em PRONTO.')
texto('Utilização da CPU = unidades úteis / clock final. Sobrecarga é apresentada separadamente; ociosidade = total − útil − sobrecarga. Utilização de cada dispositivo = serviço ocupado / clock final. Throughput = processos finalizados / clock final. Taxa de faltas = faltas / referências. O horizonte começa em zero e inclui a drenagem das requisições assíncronas.')
pagina()
titulo('04','Memória, dispositivos e arquivos')
texto('<b>Paginação.</b> O endereço lógico é dividido em página e deslocamento. Cada processo tem tabela própria, que guarda presença e moldura. A tradução usa moldura × tamanho da página + deslocamento. Acertos não alteram a ordem FIFO global. Na falta, a thread bloqueia e entra na fila serial do paginador.')
texto('Ao concluir o serviço, usa-se moldura livre ou a vítima mais antiga. A tabela da vítima é invalidada e a nova página é instalada. A referência é concluída pelo evento do paginador, sem recontagem ou repetição ao retomar a thread. Pedidos simultâneos à mesma página mantêm seus atendimentos, mas reutilizam a página se ela já estiver residente. Finalizar um processo libera suas molduras.')
texto('<b>E/S.</b> Disco (bloco) e terminal (caractere) têm filas FCFS e tempos independentes. B bloqueia; NB permite prosseguir. A conclusão produz interrupção e entrega dispositivo:id:OK à caixa de entrada do TCB. Não há polling. Se todas as threads já terminaram, o processo aguarda os pedidos assíncronos antes de liberar recursos.')
texto('<b>Arquivos.</b> A raiz contém nós de diretório e arquivo, com nome, tipo, permissões, tamanho e instantes lógicos. Há criação, abertura, leitura, escrita, fechamento, remoção e listagem. Cada abertura associa descritor local a entrada global com nó, modo e cursor. Threads compartilham os descritores do processo; processos diferentes têm espaços locais independentes.')
texto('O volume usa 128 blocos encadeados de 16 unidades UTF-16. Cada bloco aponta para o próximo; o nó aponta para o primeiro. A estratégia evita exigir blocos contíguos, mas impõe percorrer a cadeia para acessar dados. A escrita verifica capacidade antes da alteração, mantendo o conteúdo anterior se faltar espaço. O tamanho é lógico, não bytes UTF-8.')
texto('Permissões r/w são verificadas na abertura e nas operações. Remoção de arquivo aberto e de diretório não vazio é rejeitada. Fechar ou encerrar o processo remove a associação local/global. As operações de arquivos são síncronas de uma unidade, sem gerar pedidos no dispositivo disco; o dispositivo é exercitado explicitamente pelas instruções IO. O volume não persiste entre execuções.')
titulo('05','Desenho dos experimentos')
texto('Os sete cenários são executados por scripts/experimentos.py. Mantêm-se troca = 1, página = 16, falta = 5, disco = 4, terminal = 2 e semente = 42. As comparações de política e quantum usam a mesma carga mista, com quatro molduras. A comparação de memória usa uma carga específica e FCFS. Não há geração aleatória; a semente é registrada para explicitar a configuração.')
texto('Os números seguintes foram obtidos na execução de referência em JDK 17, anterior à migração do alvo para Java 27. A lógica foi preservada, mas esses números ainda não foram reproduzidos em JDK 27. Tempos estão em unidades lógicas; médias de espera/resposta são por thread, retorno médio é por processo. As utilizações aparecem como porcentagem apenas neste relatório; o CSV usa proporções.','PequenoRelatorio')
pagina()
titulo('06','Experimento 1: políticas de CPU')
texto('Carga mista idêntica, quatro molduras, quantum 3 (aplicável somente ao RR). O programa contém quatro threads em três processos; executa 54 unidades úteis e seis referências à memória em todas as políticas.')
linhas=[]
for chave,rotulo in [('politica-fcfs','FCFS'),('politica-rr','RR, q=3'),('politica-prioridade','Prioridade')]:
    c=cenarios[chave]
    linhas.append([rotulo,c['tempo_total'],c['trocas'],numero(chave,'media_resposta_threads'),numero(chave,'media_espera_threads'),numero(chave,'media_retorno_processos')])
tabela(['Política','Total','Trocas','Resposta média','Espera média','Retorno médio'],linhas,[95,50,55,95,95,105])
linhas=[]
for chave,rotulo in [('politica-fcfs','FCFS'),('politica-rr','RR, q=3'),('politica-prioridade','Prioridade')]:
    c=cenarios[chave]
    linhas.append([rotulo,f"{100*float(c['utilizacao_cpu']):.2f}%",c['sobrecarga'],c['ocioso'],c['faltas'],numero(chave,'throughput',4)])
tabela(['Política','CPU útil','Sobrecarga','Ocioso','Faltas','Throughput'],linhas,[95,80,80,70,70,100])
texto('<b>Interpretação.</b> FCFS encerra o conjunto em 70 unidades, contra 87 do RR. O RR, porém, reduz a resposta média de 17,75 para 6,25: as primeiras oportunidades de CPU chegam antes. O custo é realizar 24 trocas contra 13, além de uma distribuição diferente dos bloqueios e da ociosidade.')
texto('Prioridade obtém o menor retorno médio de processos (50,33), mas não o menor tempo total (75). Ela favorece as tarefas com prioridades mais altas; o término de toda a carga ainda depende da tarefa restante. Retorno médio e duração total medem propriedades diferentes e não devem ser confundidos.')
texto('Mesmo mantendo os parâmetros de memória constantes, FCFS apresenta seis faltas e as demais políticas cinco. O escalonamento altera a ordem global das referências e a permanência das páginas na memória. Essa interação é resultado do modelo integrado, não uma mudança na configuração experimental.')
texto('Neste cenário, RR melhora a resposta inicial e reduz a eficiência total; não se conclui que uma política seja sempre superior. Cargas, custos e prioridades diferentes podem mudar o resultado. Sem envelhecimento, prioridade também pode adiar threads menos prioritárias diante de um fluxo contínuo, embora a carga finita deste experimento termine.')
pagina()
titulo('07','Experimento 2: tamanho do quantum')
texto('Mesma carga mista, política RR, quatro molduras. Somente o quantum muda; o cenário q=3 do experimento anterior é incluído como referência intermediária.')
linhas=[]
for chave in ['quantum-1','politica-rr','quantum-6']:
    c=cenarios[chave]
    linhas.append([c['quantum'],c['tempo_total'],c['trocas'],numero(chave,'media_resposta_threads'),f"{100*float(c['utilizacao_cpu']):.2f}%",numero(chave,'media_retorno_processos')])
tabela(['Quantum','Total','Trocas','Resposta média','CPU útil','Retorno médio'],linhas,[65,55,60,110,85,120])
texto('Reduzir q de 6 para 1 melhora a resposta média de 10,00 para 3,25, mas aumenta o total de 76 para 122 e as trocas de 15 para 54. Com custo de contexto 1, q=1 faz a sobrecarga igualar as 54 unidades úteis. A utilização útil cai de 71,05% para 44,26%.')
texto('As três execuções têm cinco faltas, de modo que esse indicador não explica a diferença principal. A maior frequência de trocas pesa diretamente; a sobreposição de bloqueios também muda o tempo ocioso (7, 9 e 14 unidades para q=6, 3 e 1). Um quantum deve equilibrar resposta e custo de despacho, não ser escolhido apenas pelo menor tempo de resposta.')
titulo('08','Experimento 3: número de molduras')
texto('FCFS, páginas de tamanho 16, uma thread e a sequência 0,1,2,0,1,2,0,1,2. Somente a quantidade de molduras muda; nove referências mais CPU 1 somam dez unidades úteis.')
linhas=[]
for chave in ['memoria-2','memoria-3']:
    c=cenarios[chave]
    linhas.append([c['molduras'],c['faltas'],f"{100*float(c['taxa_faltas']):.2f}%",c['tempo_total'],c['sobrecarga'],c['ocioso']])
tabela(['Molduras','Faltas','Taxa','Total','Sobrecarga','Ocioso'],linhas,[75,65,85,70,100,100])
texto('Com duas molduras, cada referência precisa de carregamento: a página necessária foi expulsa pelo ciclo anterior. Com três, as três primeiras referências faltam e as seis restantes acertam. O total cai de 65 para 29 unidades, redução de 55,38%.')
texto('A diferença de 36 unidades é explicável: seis faltas a menos economizam 30 unidades de atendimento e seis despachos de retomada economizam outras seis. Mais memória reduz tanto o bloqueio quanto a sobrecarga de retomada nesta carga. Esse resultado específico não prova monotonicidade geral de FIFO; a análise se restringe à sequência fornecida.')
pagina()
titulo('09','Validação e reprodução')
texto('A versão anterior passou em 191 verificações com JDK 17 e -Xlint:all. O alvo agora é --release 27; a compilação e os testes com JDK 27 ainda não foram executados neste ambiente. Inclui testes de transições, ordenação, quantum, métricas exatas, tradução, FIFO, isolamento, faltas simultâneas, E/S B/NB, permissões, descritores, blocos, escrita sem espaço e validação de entrada. Integração executa sete cargas nas três políticas e compara duas execuções de cada configuração.')
texto('A carga manual verifica P1 com CPU 3 e chegada 0, P2 com CPU 2 e chegada 1, sem custo de contexto. FCFS termina P1 em 3 e P2 em 5; RR q=2 termina P2 em 4 e P1 em 5. Ambas usam cinco unidades úteis. Os valores de espera e resposta estão no README e são comparados nos testes.')
texto('<b>Comandos principais.</b> Em Linux/macOS: sh scripts/testar.sh. Em Windows: powershell -ExecutionPolicy Bypass -File scripts/testar.ps1. Para reproduzir as comparações: python3 scripts/experimentos.py resultados/nova-comparacao (python ou py -3 no Windows). A pasta de destino deve ser nova.')
texto('O ZIP contém os logs completos em resultados/experimentos. O código não sobrescreve uma pasta não vazia. Resultados gerados e arquivos binários estão ignorados pelo Git. O README explica a compilação, as opções, a linguagem da carga e os cálculos.')
titulo('10','Limitações e próximos passos')
texto('A simulação tem uma CPU, tempos fixos e ausência de instruções condicionais. O paginador é independente do disco genérico. Arquivos ficam em memória, sem persistência física e sem custo de E/S associado. Não há usuários, TLB, páginas sujas, multiprocessamento, aging, cache, journaling ou escalonamento avançado de disco. São simplificações declaradas, não funcionalidades parcialmente implementadas.')
texto('A cobertura verifica cenários relevantes, mas não constitui prova formal de correção. Os tempos são unidades abstratas: não podem ser interpretados como desempenho de hardware real. Os resultados se referem às cargas entregues; generalizações exigiriam novos experimentos controlados.')
texto('A publicação do repositório GitHub acessível ao professor, os nomes dos integrantes e o histórico real de participação devem ser providenciados pelo grupo. Não foi criado histórico artificial nem simulada uma entrega intermediária. Antes da submissão, o grupo deve executar o projeto em seu próprio ambiente e preparar a explicação de cada decisão.')
titulo('11','Fontes e ferramentas')
texto('Requisitos: Trabalho SO.pdf, disciplina de Sistemas Operacionais, Prof. Maurício Acconcia Dias, fornecido pelo usuário. Estilo: Markdown.md colado, fornecido pelo usuário. Ferramenta de apoio: ChatGPT/Codex, declarada para revisão acadêmica. Java padrão implementa o simulador; Python padrão automatiza experimentos. ReportLab é usado somente no gerador opcional deste PDF e não é dependência de execução do simulador.','PequenoRelatorio')


pagina()
titulo('12','Adendo: desktop gráfico')
texto('Foi acrescentada uma interface Swing, usando o módulo padrão java.desktop. O visual adota fundo verde-petróleo, títulos azul-marinho, painéis cinza e bordas em relevo, com organização em janelas internas e barra de tarefas. A inspiração combina desktops como KDE Plasma com a estética clássica do Windows 98; nenhum componente desses sistemas foi incorporado.')
texto('InterfaceGrafica reúne seleção e prévia de cargas, política de CPU, quantum, custos, memória, dispositivos, semente e pasta de saída. Após executar, o monitor apresenta métricas, processos, threads, linha do tempo da CPU e registro completo. Cada execução gera uma pasta própria com os mesmos logs e CSVs da CLI.')
texto('O fluxo Main.executar é compartilhado por CLI e GUI. A simulação é executada por SwingWorker para manter a janela responsiva; o núcleo continua sequencial, orientado a eventos e clock lógico. O botão de execução fica desabilitado durante o trabalho. Não há execução real de processos do sistema hospedeiro.')
texto('LinhaTempo projeta eventos concluídos: INSTRUCAO representa [clock-1, clock] e os eventos de troca delimitam a sobrecarga. A visualização não é uma reprodução em tempo real nem depuração passo a passo. O log conserva o detalhe exato; a escala gráfica comprime cargas longas.')
texto('O pacote Windows passa a oferecer SimuladorSO.exe para a GUI, SimuladorCLI.exe para automação e Testar.exe para a suíte. INICIAR.bat abre a GUI; MENU-CLI.bat preserva o menu textual. O runtime embutido inclui java.base e java.desktop. É preciso regenerar o pacote no Windows para obter esses executáveis.')
texto('<b>Validação.</b> A compilação de compatibilidade com JDK 17 passou nas 191 verificações do núcleo. Um teste offscreen acionou a interface real, verificou o bloqueio de execução duplicada e comparou os três CSVs de métricas com o fluxo da CLI. As capturas da interface em docs foram produzidas nesse teste. O alvo entregue permanece Java 27; a abertura e interação nativa no Windows/JDK 27 ainda precisam de conferência.')
texto('O diagrama de classes foi atualizado com InterfaceGrafica e LinhaTempo. Instruções completas e limitações estão em docs/interface-grafica.md. O pacote contém fontes e gerador; o executável Windows não foi produzido neste ambiente Linux.')

def rodape(canvas, documento):
    canvas.setStrokeColor(VERDE)
    canvas.line(50,43,545,43)
    canvas.setFillColor(AZUL)
    canvas.setFont('Helvetica',8)
    canvas.drawString(50,29,'SIMULADOR DE SO | Relatório técnico | 16/09/2026')
    canvas.drawRightString(545,29,str(documento.page))

destino=RAIZ/'docs/relatorio-tecnico.pdf'
SimpleDocTemplate(str(destino),pagesize=A4,rightMargin=50,leftMargin=50,topMargin=43,bottomMargin=60,title='Simulador de SO - Relatório técnico',author='Produzido com assistência do ChatGPT/Codex').build(historia,onFirstPage=rodape,onLaterPages=rodape)
print(destino)

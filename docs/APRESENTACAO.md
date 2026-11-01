# Guia para estudar, apresentar e alterar

## Demonstração sugerida

1. Execute `python main.py --cenario verificacao --algoritmo fcfs`. Explique os intervalos 0–3 e 3–5; confira retorno e espera.
2. Execute `python main.py --cenario verificacao --algoritmo rr --quantum 2`. Mostre a preempção em 2, a CPU restante salva e a retomada em 4.
3. Execute `python main.py --cenario verificacao --algoritmo prioridades`. P2 entra primeiro por ter prioridade numérica 0.
4. Execute `python main.py --cenario mista --custo-contexto 1`. Mostre threads do mesmo processo e diferencie CPU útil da sobrecarga.
5. Execute `python main.py --cenario memoria --numero-molduras 2`. Localize FALTA_PAGINA, bloqueio, CARREGAMENTO_PAGINA, TRADUCAO_ENDERECO e SUBSTITUICAO_FIFO.
6. Execute `python main.py --cenario es`. Mostre E/S assíncrona e interrupções; outra thread pode usar a CPU durante um bloqueio.
7. Execute `python main.py --cenario arquivos`. Mostre criação, descritor, escrita, fechamento, reabertura e leitura. Os três ERRO_ARQUIVO são intencionais. Nenhum `/aula` foi criado em C:.
8. Execute `python main.py --experimentos` e, ao final, `python -B -m unittest discover -s testes -v`.

## Onde alterar quando o professor pedir

| Pedido | Local ou comando | O que observar |
|---|---|---|
| Trocar quantum | `--quantum 4` | Mudança das preempções e da resposta |
| Aumentar custo de contexto | `--custo-contexto 2` | CPU útil igual, maior sobrecarga |
| Mudar chegada, prioridade ou surto | `cargas/verificacao.json` | Entrada independente das classes |
| Adicionar thread | Lista `threads` do JSON | Mesmo PCB, TCB próprio, CPU disputada por thread |
| Inverter prioridade numérica | `Prioridades.selecionar`, em escalonamento.py | Trocar min por max e ajustar o teste/documentação |
| Mudar empate | Políticas em escalonamento.py; admissão em nucleo.py | Preservar regra determinística |
| Mais molduras | `--numero-molduras 4` | Menos faltas nesta sequência; FIFO pode ter anomalias em outras |
| Mudar tamanho de página | `--tamanho-pagina 32` | Mesmos endereços passam a compartilhar outras páginas |
| Mudar serviço de dispositivo | `--tempo-disco 8` | Mais bloqueio e espera no dispositivo |
| Tornar uma E/S assíncrona | `"bloqueante": false` na carga | Thread prossegue e recebe notificação |
| Simular disco cheio | `--numero-blocos 1 --tamanho-bloco 4` na carga arquivos | Escrita recusada sem corrupção |
| Alterar permissões | `"permissoes":"r"` na criação de arquivo | Abrir para escrita passa a falhar |
| Adicionar métrica | `Simulador.metricas` e `apresentar_metricas` | Derivar do clock lógico, com teste verificável |

Os métodos privados têm `_` para sinalizar operações internas de cada mecanismo. Evite mudar o estado diretamente pelo campo: use `_mudar_estado` no núcleo para manter fila e log consistentes. Nos testes, esse método é chamado diretamente apenas para conferir rejeição de uma transição inválida.

## Perguntas que o grupo deve conseguir responder

- **Processo e thread:** processo é dono do espaço lógico e descritores; a thread possui PC, registradores, pilha lógica e estado escalonável.
- **Eventos discretos:** o clock avança ao próximo evento, sem aguardar tempo real. Um intervalo de 100 unidades não demora 100 segundos.
- **Memória:** página = endereço // tamanho da página; deslocamento = endereço % tamanho; físico = moldura × tamanho + deslocamento.
- **FIFO:** substitui a página carregada há mais tempo. Um acerto não atualiza a ordem, diferentemente de LRU.
- **E/S bloqueante:** a CPU é liberada até a interrupção. Assíncrona: o resultado é entregue por notificação sem espera ativa.
- **Arquivo:** nome e metadados ficam no FCB; diretório relaciona nomes a objetos; conteúdo é armazenado em blocos encadeados. Descritor local aponta para uma abertura global com cursor e modo.
- **Sem persistência física:** blocos são objetos Python e desaparecem ao fechar a aplicação. O JSON lido é apenas uma descrição da carga.
- **Limitação dos arquivos:** uma chamada é instantânea; latência de disco deve ser representada por uma instrução es explícita.
- **Troca de contexto:** cada despacho tem custo, inclusive o primeiro. A espera de fila termina no despacho; a resposta só ocorre na primeira CPU útil.
- **Reprodutibilidade:** não há aleatoriedade; empates têm ordem explícita. A semente é registrada para futuras cargas geradas, sem alterar artificialmente as atuais.

Estude as convenções e os testes antes da apresentação. O documento de requisitos exige domínio da solução e identificação das ferramentas usadas no desenvolvimento.

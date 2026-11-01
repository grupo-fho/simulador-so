# 120 questões para defender e modificar o simulador de SO

## Como usar

Material de preparação para a apresentação: 120 questões autorais, com cinco alternativas (A–E), uma única resposta correta e gabarito comentado.

O conteúdo está vinculado à implementação deste repositório. Os pedidos atribuídos ao professor são possibilidades de treino, e não uma previsão das perguntas reais.

As questões distinguem o comportamento atual das extensões propostas. Trechos são recortes ou propostas localizadas, não programas completos; nomes como thread, pcb, fila e config pressupõem o contexto informado. Nenhuma mudança proposta foi aplicada ao simulador por este material.

Convenções: uma CPU lógica; prioridades não preemptivas; menor número indica maior prioridade; empates seguem a fila, salvo pedido explícito; cada despacho conta como troca, inclusive o primeiro; contexto padrão zero. Referências, submissões de E/S e chamadas de arquivos são instantâneas; somente cpu consome CPU útil. Tempos de serviço são lógicos, sem espera real.

Salvo indicação contrária, cenários numéricos não possuem outros eventos, usam os processos na ordem de admissão indicada e consideram todo o horizonte até a drenagem de E/S. Intervalos [a,b) incluem o início e excluem o fim.

Todos os arquivos e dispositivos mencionados nas questões são virtuais, exceto quando o enunciado fala expressamente do código-fonte, da entrada JSON ou do sistema hospedeiro.

## Roteiro de preparação

1. Primeira rodada: responda sem consultar o gabarito. Para cálculos, desenhe a linha do tempo de CPU e dispositivos.

2. Segunda rodada: consulte a explicação e localize o método indicado. Explique oralmente por que a resposta está correta e por que as demais não atendem ao enunciado.

3. Terceira rodada: pratique as alterações em uma cópia do projeto, primeiro prevendo a saída de uma carga pequena e depois executando os testes relevantes.

4. Nas extensões, identifique todas as camadas envolvidas: formato da carga, validação, modelo, núcleo, eventos, interface, testes e documentação. Uma mudança em um único trecho nem sempre completa a funcionalidade.

5. Use python main.py --cenario verificacao para conferir escalonamento e python -B -m unittest discover -s testes -v para executar a suíte original.

6. Fonte: código deste repositório, README, guia de apresentação, relatório e especificacoes.pdf. Material elaborado com assistência de OpenAI Codex; revise as respostas junto com a versão do código usada na avaliação.

## Distribuição do conteúdo

| Questões | Tema |
|---|---|
| 001–010 | 1. Orientação a objetos e arquitetura |
| 011–020 | 2. Estados, processos e contexto |
| 021–030 | 3. Eventos discretos e determinismo |
| 031–040 | 4. Escalonamento e mudanças de política |
| 041–050 | 5. Cálculos de CPU, espera e resposta |
| 051–060 | 6. Paginação, tradução e substituição FIFO |
| 061–070 | 7. Dispositivos, bloqueios e notificações |
| 071–080 | 8. Arquivos, diretórios e descritores |
| 081–090 | 9. Modificações e defeitos no sistema de arquivos |
| 091–100 | 10. Cargas, validação e testes |
| 101–110 | 11. Pedidos práticos de alteração durante a apresentação |
| 111–120 | 12. Diagnóstico integrado e defesa das decisões |

As alternativas aparecem antes do gabarito para permitir autoavaliação. Cada questão vale um ponto; total de 120 pontos.

## 1. Orientação a objetos e arquitetura

### Questão 001 — Unidade escalonável

**Tipo:** Conceito

Qual entidade efetivamente entra na fila de prontos para disputar a CPU nesta implementação?

**A)** Processo, com todas as threads executadas como um bloco indivisível.

**B)** Thread, com contexto individual no TCB.

**C)** Evento, tratado como uma thread de usuário.

**D)** ArquivoAberto, selecionado pela prioridade do arquivo.

**E)** PCB, usado como uma instrução CPU.

### Questão 002 — Composição no núcleo

**Tipo:** Conceito

Simulador cria objetos de memória, arquivos e escalonamento. Qual relação orientada a objetos isso exemplifica?

**A)** Variável global: todos os recursos pertencem ao módulo json.

**B)** Recursão: todos os métodos chamam a si mesmos.

**C)** Herança múltipla: o núcleo é simultaneamente todos os dispositivos.

**D)** Sobrecarga de operadores: os recursos são somados ao clock.

**E)** Composição: o núcleo coordena objetos com responsabilidades próprias.

### Questão 003 — Contrato da política

**Tipo:** Conceito

Qual é o contrato de PoliticaEscalonamento.selecionar?

**A)** Retornar sempre o identificador do processo como texto.

**B)** Devolver o instante do próximo evento CPU.

**C)** Remover todas as threads bloqueadas e retornar None.

**D)** Devolver o índice da thread escolhida sem remover elementos da fila.

**E)** Executar as instruções da thread antes de devolver a fila.

### Questão 004 — Fila com valor padrão

**Tipo:** Depuração

Por que field(default_factory=list) é apropriado para notificacoes no TCB?

```python
notificacoes: list[str] = field(default_factory=list)
```

**A)** Gera automaticamente uma thread real para cada item.

**B)** Cria uma lista independente para cada TCB.

**C)** Converte a lista em uma tupla imutável.

**D)** Persiste a lista quando a aplicação termina.

**E)** Faz todas as threads compartilharem a mesma lista deliberadamente.

### Questão 005 — Configuração imutável

**Tipo:** Modificação

Após criar config, o professor pede uma configuração igual com quantum 4, preservando a original. Qual expressão é adequada?

```python
from dataclasses import replace
nova = replace(config, quantum=4)
```

**A)** config.quantum = 4, pois frozen=True permite esse ajuste.

**B)** config.append(quantum=4).

**C)** dataclasses.replace(config, quantum=4).

**D)** config['quantum'] = 4, pois a dataclass é um dicionário.

**E)** del config.quantum, para ativar o padrão 4.

### Questão 006 — RR e seleção FCFS

**Tipo:** Conceito

RoundRobin herda FCFS e não redefine selecionar. Onde o comportamento temporal de RR é implementado?

**A)** No contador de eventos, ao reordenar todas as chegadas.

**B)** No núcleo, ao limitar o intervalo pela quota restante e devolver a thread ao fim da fila.

**C)** No sistema operacional hospedeiro, usando threads reais.

**D)** Em Configuracao, que executa instruções no __post_init__.

**E)** No FCB, ao fechar o arquivo depois de cada quantum.

### Questão 007 — PC de quem executa

**Tipo:** Conceito

Duas threads do mesmo processo estão em instruções diferentes. Qual campo determina a próxima instrução de cada uma?

**A)** O PCB.contador_programa como único contexto de todas as threads.

**B)** O número de descritores abertos do processo.

**C)** O contador_programa do TCB de cada thread.

**D)** Um único contador compartilhado no FCB do processo.

**E)** A posição da thread na tabela de páginas.

### Questão 008 — Novo algoritmo substituível

**Tipo:** Modificação

O professor pede uma política de seleção nova. Qual plano preserva a arquitetura?

**A)** Acrescentar um if de prioridade em cada operação de arquivos.

**B)** Modificar somente a descrição no README.

**C)** Substituir todos os TCBs por threads do módulo threading.

**D)** Implementar o contrato da política, registrá-la na fábrica e nas validações/CLI, e testar sua ordenação.

**E)** Colocar a política na função que codifica texto UTF-8.

### Questão 009 — Recurso compartilhado

**Tipo:** Conceito

Qual dado é compartilhado pelas threads de um mesmo processo, segundo o modelo?

**A)** A pilha lógica individual de uma thread.

**B)** O quantum_restante de todos os processos como um único campo.

**C)** A tabela de arquivos abertos do PCB.

**D)** O contador_programa de todos os TCBs como um único inteiro.

**E)** A lista de notificações de todas as threads.

### Questão 010 — Responsabilidade da interface

**Tipo:** Modificação

Para apresentar uma métrica adicional sem misturar impressão com o núcleo, onde devem ficar cálculo e exibição?

**A)** Impressão dentro de cada comparação da política FCFS.

**B)** Ambos em SistemaArquivos._partes.

**C)** Ambos no construtor de RegistroEvento.

**D)** Cálculo no argparse e exibição na tabela de páginas.

**E)** Cálculo em Simulador.metricas; exibição em apresentar_metricas.

## 2. Estados, processos e contexto

### Questão 011 — Admissão

**Tipo:** Conceito

Qual transição de thread representa a admissão de uma tarefa recém-chegada?

**A)** FINALIZADO para EXECUTANDO.

**B)** BLOQUEADO para NOVO.

**C)** PRONTO para BLOQUEADO sem despacho.

**D)** NOVO para PRONTO.

**E)** NOVO para FINALIZADO.

### Questão 012 — Estado alterado diretamente

**Tipo:** Depuração

Qual problema pode ocorrer se uma modificação substituir a chamada abaixo apenas por thread.tcb.estado = Estado.PRONTO?

```python
self._mudar_estado(thread, Estado.PRONTO, 'interrupção de E/S')
```

**A)** O Python sempre lançará SyntaxError ao atribuir um Enum.

**B)** A thread pode ficar pronta sem entrar na fila e sem registrar a causa ou atualizar o processo.

**C)** A memória física será automaticamente duplicada.

**D)** A thread terminará obrigatoriamente no mesmo instante.

**E)** A chamada direta equivale integralmente ao método original.

### Questão 013 — Uma bloqueada e outra pronta

**Tipo:** Rastreamento

Um processo tem T1 bloqueada e T2 pronta, sem outra thread. Qual é o estado agregado do processo?

**A)** PRONTO.

**B)** EXECUTANDO, mesmo sem thread na CPU.

**C)** NOVO.

**D)** FINALIZADO.

**E)** BLOQUEADO, pois qualquer bloqueio bloqueia todas as threads.

### Questão 014 — Fim de apenas uma thread

**Tipo:** Rastreamento

T1 finaliza, mas T2 do mesmo processo ainda está bloqueada. O que deve ocorrer com os descritores compartilhados?

**A)** Devem ser removidos juntamente com a raiz do sistema de arquivos.

**B)** Devem permanecer disponíveis até todas as threads finalizarem ou até fechamento explícito.

**C)** Devem ser convertidos em arquivos físicos.

**D)** Devem ser fechados obrigatoriamente por qualquer finalização de thread.

**E)** Devem passar ao PCB de um processo aleatório.

### Questão 015 — Contexto após preempção

**Tipo:** Depuração

Uma thread executou 2 de um surto de 5 e sofreu preempção. Qual ação mantém o contexto correto?

```python
if tcb.cpu_restante == 0:
    tcb.cpu_restante = duracao
```

**A)** Preservar cpu_restante=3 e o PC na instrução CPU ainda incompleta.

**B)** Avançar o PC para a próxima instrução a cada preempção.

**C)** Apagar todos os registradores ao entrar na fila.

**D)** Reiniciar cpu_restante=5 em todo despacho.

**E)** Marcar finalizacao para impedir retorno à CPU.

### Questão 016 — Espera acumulada

**Tipo:** Rastreamento

Uma thread esperou de 1 a 4 e depois de 7 a 9 na fila de prontos. Qual o tempo de espera acumulado?

**A)** 9 unidades.

**B)** 3 unidades.

**C)** 8 unidades.

**D)** 5 unidades.

**E)** 2 unidades.

### Questão 017 — Espera que se perde

**Tipo:** Depuração

Qual correção é necessária para o trecho proposto acumular todas as passagens pela fila?

```python
thread.tcb.tempo_espera = self.clock - thread.tcb.entrada_prontos
```

**A)** Trocar = por += na atualização de tempo_espera.

**B)** Calcular tempo_espera pelo número de páginas.

**C)** Trocar a diferença por self.clock + entrada_prontos.

**D)** Subtrair o total anterior para remover esperas repetidas.

**E)** Zerar entrada_prontos no final de cada simulação apenas.

### Questão 018 — Pilha após erro de arquivo

**Tipo:** Conceito

Por que a remoção do quadro de chamada de arquivo está em finally?

```python
finally:
    thread.tcb.pilha_logica.pop()
```

**A)** Para garantir que o arquivo seja salvo fisicamente.

**B)** Para finalizar todas as threads assim que houver uma leitura.

**C)** Para ignorar todas as exceções sem registrar nada.

**D)** Para executar a operação de arquivo uma segunda vez.

**E)** Para retirar o quadro tanto no sucesso quanto quando ocorre ErroSimulacao.

### Questão 019 — Chave da thread

**Tipo:** Rastreamento

Para processo_id='P2' e identificador='T3', qual o resultado da propriedade chave?

```python
return f'{self.tcb.processo_id}/{self.tcb.identificador}'
```

**A)** O endereço da tabela de páginas.

**B)** Um inteiro gerado pelo sistema operacional.

**C)** P2T3 sem separador.

**D)** T3/P2.

**E)** P2/T3.

### Questão 020 — Reexecutar a mesma instância

**Tipo:** Conceito

Depois de executar sim.executar(), o que acontece ao chamá-lo novamente sobre o mesmo objeto?

**A)** A segunda execução reutiliza os resultados como se a carga não tivesse sido consumida.

**B)** O clock e todos os recursos são reiniciados automaticamente.

**C)** É levantado ErroSimulacao; deve-se construir outra instância para uma nova rodada.

**D)** O algoritmo muda automaticamente para FCFS.

**E)** A segunda execução acrescenta um processo vazio.

## 3. Eventos discretos e determinismo

### Questão 021 — Clock lógico

**Tipo:** Conceito

Uma instrução CPU tem duração 100. Como esse tempo é tratado?

**A)** Cada unidade exige que o usuário aperte Enter.

**B)** O tempo é determinado pela velocidade do processador hospedeiro.

**C)** Um evento de conclusão é agendado 100 unidades lógicas à frente, sem sleep real.

**D)** A aplicação espera obrigatoriamente 100 segundos.

**E)** É criado um processo do Windows para medir a duração.

### Questão 022 — Ordenação da agenda

**Tipo:** Conceito

Quais campos ordenam os objetos Evento no heap?

```python
@dataclass(order=True)
class Evento:
    instante: int
    ordem: int
    tipo: str = field(compare=False)
```

**A)** A ordem alfabética do endereço de memória da função.

**B)** tipo e depois nome da função callback.

**C)** A duração dos arquivos abertos.

**D)** instante e depois ordem; tipo e acao não participam da comparação.

**E)** Somente a prioridade do processo.

### Questão 023 — Empate de eventos

**Tipo:** Rastreamento

São inseridos B em t=2, A em t=1 e C em t=2, nessa ordem. Qual é a ordem de remoção?

**A)** A, B, C.

**B)** B, C, A.

**C)** A, C, B.

**D)** C, B, A.

**E)** B, A, C.

### Questão 024 — Remover o critério de desempate

**Tipo:** Depuração

Se acao passasse a participar da comparação e dois eventos empatassem em todos os campos anteriores, qual risco surgiria?

```python
acao: Callable[[], None] = field(compare=False, repr=False)
```

**A)** A fila de arquivos corrigiria o empate automaticamente.

**B)** O clock passaria a medir segundos.

**C)** O Python converteria os callbacks em prioridades de processo.

**D)** As funções seriam automaticamente ordenadas por duração de CPU.

**E)** O heap poderia tentar ordenar funções, causando TypeError.

### Questão 025 — Captura da variável no callback

**Tipo:** Depuração

Por que a chegada é agendada usando lambda p=processo, em vez de capturar apenas o nome processo?

```python
lambda p=processo: self._admitir(p)
```

**A)** Para executar a chegada no momento de criação da lambda.

**B)** Para copiar integralmente todos os blocos do processo.

**C)** Para impedir que eventos tenham o mesmo clock.

**D)** Para guardar o processo daquela iteração e evitar que os callbacks usem o último valor do laço.

**E)** Para tornar o processo uma variável global compartilhada.

### Questão 026 — Custo de contexto zero

**Tipo:** Conceito

Se custo_contexto=0, por que ainda se agenda FIM_CONTEXTO no clock atual?

**A)** Para aumentar CPU útil sem executar instrução.

**B)** Para manter o mesmo fluxo de eventos e a ordem registrada, mesmo sem avanço temporal.

**C)** Para indicar que a thread já terminou.

**D)** Para produzir uma espera real de um segundo.

**E)** Para bloquear indefinidamente o primeiro despacho.

### Questão 027 — Chegada durante CPU

**Tipo:** Rastreamento

Em FCFS, P1 inicia CPU de 0 a 8. P2 chega em 3. O que o núcleo faz em t=3?

**A)** Interrompe P1 obrigatoriamente porque todo evento causa preempção.

**B)** Admite P2 e o coloca na fila; P1 conserva a CPU até terminar ou bloquear.

**C)** Finaliza P1 para liberar o recurso.

**D)** Ignora a chegada e a altera para t=8.

**E)** Executa P1 e P2 simultaneamente em duas CPUs do modelo.

### Questão 028 — Despacho antes de esvaziar o instante

**Tipo:** Depuração

Por que não se deve inserir um novo despacho dentro de cada callback de chegada, antes de processar os outros eventos do mesmo instante?

```python
while self.agenda and self.agenda.proximo_instante == self.clock:
    self.agenda.proximo().acao()
```

**A)** Porque a agenda só aceita um evento por instante.

**B)** Porque uma chegada não pode inserir threads na fila.

**C)** Porque prioridades só funciona com relógio real.

**D)** Porque todos os eventos do instante têm necessariamente o mesmo processo.

**E)** Isso pode selecionar antes de conhecer todas as threads recém-prontas e mudar a regra documentada de empate.

### Questão 029 — Semente e carga determinística

**Tipo:** Conceito

Ao alterar apenas --semente em uma carga fornecida, sem acrescentar sorteios ao modelo, qual resultado se espera?

**A)** Toda prioridade passa a ser sorteada.

**B)** O programa deixa de aceitar cargas externas.

**C)** Mesmas métricas e eventos de execução; a linha de configuração registra a semente diferente.

**D)** O quantum varia a cada rodada.

**E)** As durações de disco mudam automaticamente.

### Questão 030 — Limite defensivo do laço

**Tipo:** Depuração

O que significa a detecção de thread_atual não nula, mas sem evento futuro na agenda?

```python
elif self.thread_atual is not None and not self.agenda:
    raise RuntimeError('CPU ocupada sem evento de conclusão.')
```

**A)** A execução normal deve esperar um arquivo .txt aparecer.

**B)** O algoritmo passou automaticamente para prioridades preemptivas.

**C)** Há uma inconsistência interna: faltou agendar a conclusão da atividade que mantém a CPU ocupada.

**D)** A CPU está livre porque há uma thread atual.

**E)** Toda thread CPU-bound termina sem evento de conclusão.

## 4. Escalonamento e mudanças de política

### Questão 031 — FCFS escolhe a cabeça

**Tipo:** Rastreamento

Com fila_prontos=[T1,T2,T3], o que ocorre na seleção FCFS?

**A)** Retorna o inteiro 0 ao núcleo sem remover a thread.

**B)** Retorna T3 e a fila passa a [T1,T2].

**C)** Retorna as três threads para execução simultânea.

**D)** Retorna T1 e a fila passa a [T2,T3].

**E)** Retorna T2 e ordena a fila por ID.

### Questão 032 — Ordem de prioridades

**Tipo:** Rastreamento

A fila contém T1/P1 prioridade 5, T2/P2 prioridade 0 e T3/P3 prioridade 2. Quem sai primeiro em prioridades?

**A)** As três, porque prioridade não determina uma seleção.

**B)** T1/P1, pois 5 é o maior número.

**C)** T3/P3, por estar no meio da fila.

**D)** T2/P2, por ter o menor valor numérico de prioridade.

**E)** T1/P1 em qualquer caso, pois prioridades ignora os valores.

### Questão 033 — Inverter a convenção numérica

**Tipo:** Modificação

O professor pede que maior número signifique maior prioridade, mantendo o desempate pela primeira posição da fila. Qual alteração atende ao pedido?

```python
return max(range(len(fila)),
           key=lambda i: prioridades[fila[i].tcb.processo_id])
```

**A)** Trocar min por max na seleção, conservando a chave de prioridade.

**B)** Trocar fila.pop(indice) por fila.pop() em todas as políticas.

**C)** Inverter apenas o texto do README.

**D)** Alterar o tempo de falta de página para um número negativo.

**E)** Remover a chave e calcular min diretamente sobre objetos Thread.

### Questão 034 — Prioridade empatada

**Tipo:** Rastreamento

A fila já está na ordem [P2/T1,P1/T1], ambos com prioridade 3. Qual sai primeiro em prioridades?

**A)** P1/T1 obrigatoriamente, porque a política reordena IDs em toda seleção.

**B)** P2/T1, pois o empate mantém a ordem da fila existente.

**C)** O que tiver mais memória.

**D)** O que tiver menos descritores abertos.

**E)** Uma thread sorteada com a semente.

### Questão 035 — Prioridades não preemptivas

**Tipo:** Rastreamento

P1 de prioridade 5 executa CPU de 0 a 5. P2 de prioridade 0 chega em 1. Sem custo de contexto ou outros eventos, quando P2 começa CPU?

**A)** Somente após uma falta de página obrigatória.

**B)** Em 5.

**C)** Em 2, independentemente da configuração.

**D)** Em 0.

**E)** Em 1.

### Questão 036 — Tornar prioridades preemptivas

**Tipo:** Modificação

Qual plano é necessário para acrescentar preempção por prioridade durante um intervalo de CPU já agendado?

**A)** Adicionar a thread atual à fila e manter inalterado o evento CPU antigo.

**B)** Somente mudar min para max.

**C)** Fechar os arquivos de P1 para forçar a liberação de CPU.

**D)** Contabilizar o trecho executado, salvar CPU restante, invalidar a conclusão antiga e reencaminhar a thread ao estado pronto.

**E)** Somente imprimir PREEMPCAO sem tocar em contexto nem eventos.

### Questão 037 — RR em uma carga mínima

**Tipo:** Rastreamento

P1 e P2 chegam em 0, nessa ordem de admissão, com CPU 3 e 2. RR q=2, contexto 0. Qual sequência de CPU é correta?

**A)** P2 [0,2), P1 [2,5).

**B)** P1 [0,2), P2 [2,4), P1 [4,5).

**C)** P1 [0,1), P2 [1,2), P1 [2,4), P2 [4,5).

**D)** P1 [0,2), P1 [2,3), P2 [3,5).

**E)** P1 [0,3), P2 [3,5).

### Questão 038 — Quantum entre surtos adjacentes

**Tipo:** Rastreamento

P1 tem cpu(1), cpu(2); P2 tem cpu(1); ambos chegam em 0 e P1 entra primeiro. RR q=2, contexto 0. Quando P2 começa?

**A)** Em 0, por ter o menor surto.

**B)** Em 2, pois o quantum de P1 acumula nos dois surtos adjacentes.

**C)** Em 3, porque cada surto renova o quantum automaticamente.

**D)** Em 4, pois a preempção tem custo obrigatório de uma unidade.

**E)** Em 1, pois toda instrução CPU força troca.

### Questão 039 — Inserção na cabeça após quantum

**Tipo:** Depuração

Se adicionar passasse a usar insert(0, thread), qual risco apareceria no RR?

```python
self.fila_prontos.insert(0, thread)
```

**A)** As interrupções deixariam de ser eventos.

**B)** A thread preemptada voltaria à cabeça e poderia impedir a rotação esperada.

**C)** O quantum passaria a valer zero.

**D)** A alteração seria equivalente a append para qualquer fila.

**E)** O algoritmo se tornaria automaticamente LRU.

### Questão 040 — Nova política LIFO experimental

**Tipo:** Modificação

Como implementar somente a seleção da última thread pronta, preservando o contrato da política e supondo fila não vazia?

```python
def selecionar(self, fila, prioridades):
    return len(fila) - 1
```

**A)** Retornar fila[-1], pois o contrato exige um objeto Thread.

**B)** Retornar len(fila), pois os índices começam em 1.

**C)** Retornar len(fila) - 1.

**D)** Executar fila.clear() antes de retornar 0.

**E)** Retornar sempre None.

## 5. Cálculos de CPU, espera e resposta

### Questão 041 — Retorno versus instante absoluto

**Tipo:** Rastreamento

Uma thread chega em 4 e finaliza em 11. Qual é seu tempo de retorno?

**A)** 11 unidades.

**B)** 4 unidades.

**C)** 44 unidades.

**D)** 7 unidades.

**E)** 15 unidades.

### Questão 042 — Resposta com sobrecarga inicial

**Tipo:** Rastreamento

Uma única thread chega em 0 e tem CPU 2; custo_contexto=3. Sem outros eventos, quais são resposta, retorno e CPU útil?

**A)** Resposta 3, retorno 5, CPU útil 2.

**B)** Resposta 0, retorno 2, CPU útil 5.

**C)** Resposta 0, retorno 5, CPU útil 5.

**D)** Resposta 3, retorno 3, CPU útil 2.

**E)** Resposta 5, retorno 5, CPU útil 3.

### Questão 043 — Utilização da CPU

**Tipo:** Rastreamento

O horizonte é 20, CPU útil 12 e contexto 3. Quais são utilização útil, sobrecarga proporcional e ociosidade?

**A)** 80%, 20% e zero unidade.

**B)** 60%, 25% e 3 unidades.

**C)** 75%, 15% e 8 unidades.

**D)** 12%, 3% e 5 unidades.

**E)** 60%, 15% e 5 unidades.

### Questão 044 — Throughput

**Tipo:** Rastreamento

Quatro processos concluem em um horizonte global de 10 unidades. Qual é o throughput do modelo?

**A)** 0,4 processo por unidade de tempo.

**B)** 10 processos por unidade de tempo.

**C)** 2,5 processos por unidade de tempo.

**D)** 4 processos por thread.

**E)** 40 processos por unidade de tempo.

### Questão 045 — Contagem de despachos RR

**Tipo:** Rastreamento

Uma thread tem apenas CPU 5, chega em 0 e usa RR q=2, com contexto 1 em cada despacho. Qual horizonte e quantidade de despachos são esperados?

**A)** Horizonte 6 e um despacho.

**B)** Horizonte 5 e um despacho.

**C)** Horizonte 7 e dois despachos.

**D)** Horizonte 10 e cinco despachos.

**E)** Horizonte 8 e três despachos.

### Questão 046 — Preservar primeira resposta

**Tipo:** Depuração

Qual problema surgiria se primeira_cpu fosse atribuída em todo intervalo, removendo a condição abaixo?

```python
if tcb.primeira_cpu is None:
    tcb.primeira_cpu = self.clock
```

**A)** A thread deixaria de retornar à fila.

**B)** A métrica de resposta passaria a usar uma execução posterior, em vez da primeira utilização útil.

**C)** Os descritores perderiam o vínculo com o PCB.

**D)** A duração do primeiro surto seria necessariamente zero.

**E)** O throughput passaria a ser calculado em bytes.

### Questão 047 — Thread sem instrução CPU

**Tipo:** Rastreamento

Uma thread executa somente chamadas instantâneas de arquivos e nunca tem instrução cpu. Como sua resposta aparece?

**A)** Como o número de blocos usados.

**B)** Como None nos dados e n/a na apresentação textual.

**C)** Como um valor sorteado.

**D)** Como o instante da última abertura obrigatoriamente.

**E)** Sempre como zero, mesmo sem CPU.

### Questão 048 — Média com respostas indefinidas

**Tipo:** Modificação

Ao acrescentar resposta média por thread, qual cálculo evita tratar None como número e explicita o caso sem amostras?

```python
valores = [t['resposta'] for t in threads if t['resposta'] is not None]
media = sum(valores) / len(valores) if valores else None
```

**A)** Trocar todos os None por tempo_total e calcular a média.

**B)** Somar None diretamente para aproveitar a conversão automática em zero.

**C)** Dividir a soma pelo número de blocos do disco.

**D)** Eliminar as threads sem CPU de todos os relatórios, inclusive retorno.

**E)** Filtrar respostas não None e calcular sum(valores)/len(valores), retornando None se a lista ficar vazia.

### Questão 049 — Erro de denominador

**Tipo:** Depuração

Por que trocar o denominador da utilização útil por cpu_util, no trecho proposto, está errado para a métrica original?

```python
utilizacao = self.tempo_cpu / self.tempo_cpu if self.tempo_cpu else 0
```

**A)** Porque uso de CPU deve ser medido pelo tamanho dos arquivos.

**B)** Porque divisões com inteiros são proibidas em Python.

**C)** Porque todas as métricas devem usar apenas a semente.

**D)** Porque a utilização correta é sempre acima de 100%.

**E)** Porque eliminaria o horizonte e produziria 100% sempre que houvesse CPU útil, ocultando contexto e ociosidade.

### Questão 050 — Espera agregada do processo

**Tipo:** Conceito

Por que espera_threads de um processo pode superar seu tempo de retorno?

**A)** Porque o clock volta no tempo durante uma preempção.

**B)** Porque soma esperas de threads que podem estar simultaneamente na fila.

**C)** Porque a métrica inclui obrigatoriamente tempo de parede.

**D)** Porque o modelo tem obrigatoriamente uma CPU física por thread.

**E)** Porque cada arquivo duplica o instante de chegada.

## 6. Paginação, tradução e substituição FIFO

### Questão 051 — Página e deslocamento

**Tipo:** Rastreamento

Com tamanho_pagina=16 e endereço lógico válido 35, qual é a página e qual o deslocamento?

```python
return divmod(endereco, self.tamanho_pagina)
```

**A)** Página 35, deslocamento zero.

**B)** Página 16, deslocamento 35.

**C)** Página 2, deslocamento 3.

**D)** Página 2, deslocamento 19.

**E)** Página 3, deslocamento 2.

### Questão 052 — Endereço físico

**Tipo:** Rastreamento

A página do endereço lógico 35 está na moldura 4 e a página tem 16 bytes. Qual é o endereço físico?

**A)** 80.

**B)** 67.

**C)** 19.

**D)** 35.

**E)** 64.

### Questão 053 — Presença na tabela

**Tipo:** Conceito

Qual informação mínima EntradaPagina guarda para a tradução?

**A)** Se a página está presente e o índice da moldura correspondente.

**B)** O caminho físico de um arquivo .txt hospedeiro.

**C)** A prioridade do dispositivo e o quantum da thread.

**D)** O número de descritores livres do PCB.

**E)** A lista de todas as instruções da thread.

### Questão 054 — Físico zero é acerto

**Tipo:** Depuração

Por que substituir if fisico is not None por if fisico no acesso do núcleo causaria um erro?

```python
fisico = self.memoria.acessar(processo_id, endereco)
if fisico is not None:
    ...
```

**A)** A nova condição contaria dois acertos em qualquer acesso.

**B)** O endereço físico zero é válido, mas seria interpretado como falso e confundido com falta.

**C)** Todo endereço físico deve ser positivo e zero é proibido pelo modelo.

**D)** O quantum passaria a ser calculado pela moldura.

**E)** None é sempre um endereço residente.

### Questão 055 — FIFO não é LRU

**Tipo:** Rastreamento

Duas molduras recebem páginas 0 e 1, nessa ordem. Há um acerto em 0 e depois deve entrar a página 2. Qual é a vítima FIFO?

**A)** Nenhuma: um acerto cria uma terceira moldura.

**B)** Página 1, por ter o acesso menos recente.

**C)** A página de menor prioridade do arquivo.

**D)** Página 0.

**E)** Página 2 antes de entrar.

### Questão 056 — Invalidar a vítima

**Tipo:** Depuração

Que falha ocorreria se o carregamento substituísse a moldura sem invalidar a entrada da página vítima?

```python
entrada_vitima.presente = False
entrada_vitima.moldura = None
```

**A)** A fila de prontos eliminaria sozinha a associação antiga.

**B)** A FIFO se converteria automaticamente em FCFS de CPU.

**C)** Um acesso posterior à vítima poderia ser contado como acerto e traduzido para dados de outra página.

**D)** O Python impediria qualquer acesso à lista de molduras.

**E)** A thread antiga terminaria sempre de imediato.

### Questão 057 — Falta compartilhada

**Tipo:** Rastreamento

T1 e T2 do mesmo processo acessam a mesma página ausente antes de terminar o primeiro atendimento. Quantas faltas e carregamentos são registrados?

**A)** Uma falta e dois carregamentos.

**B)** Uma falta e zero carregamento.

**C)** Duas faltas e um carregamento.

**D)** Duas faltas e dois carregamentos obrigatoriamente.

**E)** Zero falta e um carregamento.

### Questão 058 — Espaços independentes

**Tipo:** Conceito

P1 e P2 acessam a página lógica 0. Por que não se pode usar somente o número da página como chave global de faltas pendentes?

```python
chave = (processo_id, pagina)
```

**A)** Porque a paginação funciona apenas com nomes de arquivos.

**B)** Porque a prioridade substitui o identificador de processo.

**C)** Porque todos os processos devem compartilhar a mesma página 0.

**D)** Porque a página 0 de P1 e a página 0 de P2 pertencem a espaços lógicos independentes.

**E)** Porque Python proíbe inteiros como chaves de dicionário.

### Questão 059 — Referência concluída na carga

**Tipo:** Conceito

Depois de atender uma falta, por que o modelo não repete a referência automaticamente no próximo despacho?

**A)** Porque a tabela de páginas é substituída pela tabela de arquivos.

**B)** Porque uma falta finaliza obrigatoriamente o processo.

**C)** Porque a referência pendente se completa no carregamento, que já grava a tradução e desbloqueia a thread.

**D)** Porque o endereço lógico deixa de existir.

**E)** Porque CPU restante vira igual ao endereço físico.

### Questão 060 — Acrescentar LRU de verdade

**Tipo:** Modificação

Qual alteração conceitual é necessária para oferecer LRU, sem apenas renomear FIFO?

**A)** Manter informação de último uso, atualizá-la nos acessos e escolher a página residente menos recentemente usada.

**B)** Somente trocar o nome ordem_fifo por ordem_lru.

**C)** Usar first fit entre molduras de mesmo tamanho como sinônimo de LRU.

**D)** Diminuir o quantum da CPU sem modificar o gerenciador de memória.

**E)** Escolher a página com maior endereço, ignorando acessos.

## 7. Dispositivos, bloqueios e notificações

### Questão 061 — Tipos de dispositivo

**Tipo:** Conceito

Quais dispositivos mínimos o projeto instancia?

**A)** Uma impressora e uma GPU reais controladas pelo simulador.

**B)** Apenas a CPU como dispositivo de E/S.

**C)** Dois discos de bloco, sem caractere.

**D)** Um arquivo real do Windows por thread.

**E)** disco de bloco e terminal de caractere.

### Questão 062 — E/S bloqueante e CPU

**Tipo:** Rastreamento

P1 executa CPU 1, disco bloqueante 4 e CPU 1. P2 chega em 0 com CPU 2; FCFS, P1 admitido primeiro, contexto 0. Quando P1 termina?

**A)** Em 3.

**B)** Em 8.

**C)** Em 6.

**D)** Em 4.

**E)** Em 5.

### Questão 063 — Fila FCFS do disco

**Tipo:** Rastreamento

Duas requisições de disco de duração 4 são submetidas em t=0 a um disco livre, primeiro R1 e depois R2. Quando R2 termina?

**A)** Em 6.

**B)** Em 2.

**C)** Em 0.

**D)** Em 8.

**E)** Em 4, pois ambas usam o mesmo disco simultaneamente.

### Questão 064 — Filas independentes

**Tipo:** Rastreamento

Em t=0 são iniciadas uma requisição de disco de 4 e uma de terminal de 2, ambos livres. Quando terminam?

**A)** Ambos em 6.

**B)** Terminal em 2 e disco em 4.

**C)** Terminal em 6 e disco em 4, pois compartilham uma única fila.

**D)** Ambos somente depois de uma thread CPU-bound terminar.

**E)** Disco em 2 e terminal em 4.

### Questão 065 — Duração específica da requisição

**Tipo:** Rastreamento

Com --tempo-disco 4, uma instrução es informa duracao=7. Qual duração ela usa?

```python
instrucao.get('duracao', dispositivo.tempo_servico)
```

**A)** Zero, por ser uma operação de controle.

**B)** 7 unidades, pois a duração explícita substitui o padrão dessa requisição.

**C)** 4 unidades, porque o campo da carga é ignorado.

**D)** 11 unidades, por somar sempre os dois valores.

**E)** 3 unidades, por subtrair configuração e carga.

### Questão 066 — E/S assíncrona após o fim da thread

**Tipo:** Rastreamento

Uma thread chega em 0, solicita disco não bloqueante de 4 e executa CPU 2; contexto 0. Qual é o retorno da thread e o horizonte global?

**A)** Retorno 4 e horizonte 4.

**B)** Retorno 6 e horizonte 6.

**C)** Retorno 2 e horizonte 2.

**D)** Retorno zero e horizonte 2.

**E)** Retorno 2 e horizonte 4.

### Questão 067 — Evitar espera ativa

**Tipo:** Modificação

Qual abordagem mantém a operação não bloqueante sem espera ativa?

**A)** Agendar a conclusão e entregar notificação no callback, deixando a thread prosseguir.

**B)** Executar CPU fictícia repetidamente para consultar o disco.

**C)** Manter while not concluida: pass dentro da instrução.

**D)** Obrigar o usuário a digitar o resultado da requisição.

**E)** Consultar o relógio real em um laço até passar a duração.

### Questão 068 — Desbloquear somente quem bloqueou

**Tipo:** Depuração

Se o callback de toda requisição mudasse a thread para PRONTO, mesmo nas não bloqueantes, qual falha poderia ocorrer?

```python
if bloqueante:
    self._mudar_estado(thread, Estado.PRONTO, 'interrupção de E/S')
```

**A)** Poderia tentar EXECUTANDO→PRONTO sem a liberação coordenada da CPU ou FINALIZADO→PRONTO, quebrando estados e filas.

**B)** Faria o arquivo virtual ganhar permissões rw.

**C)** Converteria automaticamente a política de disco em SCAN.

**D)** Aumentaria somente o tamanho dos blocos.

**E)** Melhoraria a notificação sem qualquer efeito nos estados.

### Questão 069 — Adicionar terceiro dispositivo

**Tipo:** Modificação

Para aceitar instruções es para uma impressora lógica com tempo configurável, qual conjunto de mudanças é coerente?

**A)** Reutilizar a mesma fila de disco e ignorar o nome solicitado.

**B)** Instalar um driver real e remover os eventos lógicos.

**C)** Criar o dispositivo, aceitar seu nome no validador, adicionar parâmetro de configuração/CLI e testar sua fila e interrupções.

**D)** Alterar apenas a apresentação da tabela de páginas.

**E)** Somente escrever impressora no JSON, pois qualquer nome já é aceito.

### Questão 070 — Utilização de dispositivo

**Tipo:** Rastreamento

Um dispositivo atende 6 unidades em uma execução com horizonte 10, e sua fila acumulou 3 unidades de espera. Qual utilização é mostrada?

**A)** 6%.

**B)** 30%.

**C)** 60%.

**D)** 90%.

**E)** 150%.

## 8. Arquivos, diretórios e descritores

### Questão 071 — FCB e conteúdo

**Tipo:** Conceito

Qual afirmação descreve corretamente a separação entre FCB e Bloco?

**A)** FCB guarda metadados e o primeiro bloco; Bloco guarda bytes e o elo para o próximo.

**B)** FCB e Bloco são caminhos reais em C:.

**C)** Cada Bloco cria um arquivo .txt no hospedeiro.

**D)** FCB guarda somente prioridade de CPU e Bloco guarda o PCB.

**E)** FCB é o cursor de cada abertura e Bloco é a fila de prontos.

### Questão 072 — Descritor local repetido

**Tipo:** Rastreamento

P1 e P2 abrem o mesmo arquivo como sua primeira abertura. Ambos recebem fd=0. Isso é um erro?

**A)** Sim; P2 deveria receber o número da página 0 de P1.

**B)** Não, porque a tabela global contém somente strings sem referência ao arquivo.

**C)** Não, porque toda abertura compartilha obrigatoriamente o mesmo cursor global.

**D)** Sim; fd precisa ser único em todos os processos do sistema.

**E)** Não; os descritores são locais aos PCBs e apontam para entradas globais distintas.

### Questão 073 — Cursores independentes

**Tipo:** Rastreamento

Um arquivo contém b'abcdef'. Duas aberturas r independentes começam na posição zero. A primeira lê 2 bytes e a segunda lê 3. O que a segunda recebe?

**A)** b'def'.

**B)** b'ef'.

**C)** b'', pois a primeira leitura consumiu o arquivo inteiro.

**D)** b'cde'.

**E)** b'abc'.

### Questão 074 — Abrir em modo w

**Tipo:** Rastreamento

Um arquivo existente contém 10 bytes e está fechado. O que acontece ao abri-lo em modo w com permissão de escrita?

**A)** O conteúdo é truncado para vazio, seus blocos são liberados e o cursor começa em zero.

**B)** O arquivo ganha automaticamente permissão de leitura.

**C)** São criados 10 blocos vazios para reservar o tamanho anterior.

**D)** O conteúdo é preservado e o cursor vai obrigatoriamente ao final.

**E)** A abertura falha sempre que o arquivo já existe.

### Questão 075 — Metadados em bytes

**Tipo:** Rastreamento

Após escrever o texto 'á' em um arquivo vazio, codificado em UTF-8, qual tamanho fica no FCB?

```python
dados = texto.encode('utf-8')
arquivo.fcb.tamanho = len(dados)
```

**A)** 4 bytes sempre, por ser Unicode.

**B)** O tamanho inteiro de um bloco mesmo que parte esteja vazia.

**C)** 2 bytes.

**D)** Zero, porque metadados não contam texto.

**E)** 1 byte, pois há um caractere.

### Questão 076 — Arredondamento de blocos

**Tipo:** Rastreamento

Com blocos de 4 bytes, quantos blocos são necessários para armazenar 10 bytes?

```python
necessarios = (len(dados) + self.tamanho_bloco - 1) // self.tamanho_bloco
```

**A)** 2 blocos.

**B)** 10 blocos.

**C)** 4 blocos.

**D)** 1 bloco.

**E)** 3 blocos.

### Questão 077 — Permissão incompatível

**Tipo:** Rastreamento

Um arquivo tem permissões 'r'. O programa simulado tenta abri-lo em modo 'w'. O que ocorre na execução pelo núcleo?

**A)** A abertura trunca o arquivo antes de verificar a permissão.

**B)** O processo recebe acesso de administrador do Windows.

**C)** A aplicação inteira precisa salvar um relatório para continuar.

**D)** O arquivo passa automaticamente a ter rw.

**E)** A abertura é recusada, ERRO_ARQUIVO é registrado e a thread pode continuar.

### Questão 078 — Remoção de diretório

**Tipo:** Rastreamento

O diretório /aula contém o arquivo /aula/notas. O que faz remover('/aula', clock) no modelo atual?

**A)** Remove somente o nome, deixando os blocos sem possibilidade de localização.

**B)** Fecha todos os processos que já listaram o diretório.

**C)** Remove recursivamente todas as entradas sem validação.

**D)** Recusa a operação porque o diretório não está vazio.

**E)** Move notas automaticamente para a raiz.

### Questão 079 — Leitura no fim

**Tipo:** Rastreamento

Após uma abertura r ter lido todos os bytes do arquivo, uma nova leitura sem quantidade retorna o quê?

```python
resultado = dados[abertura.posicao:fim]
abertura.posicao += len(resultado)
```

**A)** O arquivo inteiro outra vez, reiniciando automaticamente o cursor.

**B)** None como sinal de arquivo removido.

**C)** b'', sem mover o cursor além do que já foi efetivamente lido.

**D)** Bytes zero até completar um bloco inteiro.

**E)** Uma exceção obrigatória de permissão.

### Questão 080 — Persistência dos arquivos virtuais

**Tipo:** Conceito

Depois de finalizar todos os processos, o objeto Simulador ainda existe em uma sessão Python. O que acontece com um arquivo virtual que não foi removido?

**A)** É salvo automaticamente em C:/aula/notas.

**B)** Permanece disponível entre execuções independentes do programa sem armazenamento.

**C)** É obrigatoriamente removido quando qualquer descritor é fechado.

**D)** Seu conteúdo pode continuar no SistemaArquivos em RAM, mas não é persistido fisicamente e desaparece com o descarte da aplicação.

**E)** É convertido em um arquivo de carga JSON automaticamente.

## 9. Modificações e defeitos no sistema de arquivos

### Questão 081 — Escrita além da capacidade

**Tipo:** Depuração

Por que o teste de capacidade precisa acontecer antes de apagar os blocos antigos?

```python
if necessarios > len(antigos) + len(livres):
    raise ErroSimulacao('Disco virtual cheio.')
# Só depois: remover/reconstruir blocos.
```

**A)** Porque o tamanho de um arquivo nunca pode diminuir.

**B)** Porque apagar blocos exige aumentar o quantum.

**C)** Para uma escrita recusada preservar o conteúdo anterior e permitir recuperação sem corrupção.

**D)** Porque a soma de blocos livres não pode incluir blocos reutilizáveis do próprio arquivo.

**E)** Porque todo erro deve reiniciar o sistema de arquivos.

### Questão 082 — Fechar enquanto percorre a tabela

**Tipo:** Depuração

Por que fechar_todos percorre list(pcb.arquivos_abertos) em vez do próprio dicionário?

```python
for descritor in list(pcb.arquivos_abertos):
    self.fechar(pcb, descritor, clock)
```

**A)** Porque os descritores precisam ser convertidos em bytes.

**B)** Porque a cópia fecha também as aberturas de todos os outros processos.

**C)** Porque dicionários não podem ter chaves inteiras.

**D)** Porque fechar remove entradas, e uma cópia das chaves evita alterar o dicionário durante sua iteração.

**E)** Porque list ordena os descritores pela prioridade da thread.

### Questão 083 — Remover somente vínculo local

**Tipo:** Depuração

Se fechar apagasse apenas pcb.arquivos_abertos[descritor], sem apagar a entrada global, qual defeito surgiria?

```python
del self.tabela_global[abertura.identificador]
del pcb.arquivos_abertos[descritor]
```

**A)** A thread passaria para BLOQUEADO sem evento.

**B)** O Python fecharia automaticamente a entrada global pela igualdade dos IDs.

**C)** Vazamento de abertura global, que pode inclusive fazer o arquivo parecer ainda aberto para remoção.

**D)** A posição de todas as outras aberturas seria reiniciada.

**E)** O conteúdo do arquivo seria sempre perdido imediatamente.

### Questão 084 — Cursor depois de erro

**Tipo:** Depuração

Por que abertura.posicao só deve ser atualizada depois de _substituir_conteudo retornar com sucesso?

```python
self._substituir_conteudo(abertura.arquivo, novos, clock)
abertura.posicao = posicao + len(dados)
```

**A)** Para dispensar o teste de capacidade.

**B)** Para uma falha por disco cheio não avançar o cursor de uma escrita que não aconteceu.

**C)** Para o cursor ser sempre igual ao número do descritor.

**D)** Para o modo r ganhar permissão de escrita.

**E)** Para converter automaticamente o arquivo em diretório.

### Questão 085 — Acrescentar seek

**Tipo:** Modificação

Para implementar seek absoluto em bytes como nova instrução, aceitando somente 0 <= posicao <= tamanho, qual plano é completo?

```python
abertura = self._abertura(pcb, descritor)
if type(posicao) is not int or not 0 <= posicao <= abertura.arquivo.fcb.tamanho:
    raise ErroSimulacao('Posição inválida.')
abertura.posicao = posicao
```

**A)** Atualizar o cursor no FCB, fazendo todas as aberturas obrigatoriamente compartilhá-lo.

**B)** Usar seek de um arquivo real para representar o cursor virtual.

**C)** Modificar primeiro_bloco para o número da posição desejada.

**D)** Alterar apenas o nome de um registrador na carga.

**E)** Validar a instrução, resolver o descritor, verificar o limite, atualizar o cursor da abertura e registrar a operação.

### Questão 086 — Acrescentar chmod simplificado

**Tipo:** Modificação

Sem introduzir usuários ou grupos, como acrescentar uma operação que altere permissões básicas de um objeto?

**A)** Criar uma nova moldura para cada letra r ou w.

**B)** Chamar a permissão real do Windows para um caminho virtual.

**C)** Validar o novo valor, localizar o objeto, alterar fcb.permissoes e modificacao e registrar o evento; integrar a nova instrução ao parser da carga.

**D)** Trocar o ID global de todas as aberturas pelo texto das permissões.

**E)** Mudar somente a cor de exibição no terminal.

### Questão 087 — Detecção de ciclo nos blocos

**Tipo:** Modificação

Para detectar corrupção que ligue o último bloco de volta a um bloco anterior, que proteção pode ser acrescentada ao percurso?

```python
visitados = set()
while indice is not None:
    if indice in visitados:
        raise ErroSimulacao('Ciclo na cadeia de blocos.')
    visitados.add(indice)
    indice = self.blocos[indice].proximo
```

**A)** Manter um conjunto de índices visitados e recusar um índice repetido.

**B)** Parar ao encontrar dados b'', pois qualquer bloco vazio indica ciclo.

**C)** Aumentar o tempo do disco para que o ciclo termine sozinho.

**D)** Somar o número da página ao próximo bloco.

**E)** Retirar a atualização indice = proximo do laço.

### Questão 088 — Reutilização de descritor

**Tipo:** Rastreamento

P1 tem apenas fd=0 aberto. Fecha esse fd e depois abre outro arquivo. Que descritor local a implementação tende a devolver?

```python
descritor = 0
while descritor in pcb.arquivos_abertos:
    descritor += 1
```

**A)** O ID do FCB do novo arquivo.

**B)** O mesmo ID global da abertura anterior.

**C)** -1 para indicar que já houve um fechamento.

**D)** 0 novamente, pois escolhe o menor inteiro não utilizado.

**E)** 1 obrigatoriamente, porque o descritor local nunca é reutilizado.

### Questão 089 — Append com concorrência lógica

**Tipo:** Depuração

Por que o modo a recalcula len(anteriores) em cada escrita, em vez de confiar apenas no cursor definido na abertura?

```python
posicao = len(anteriores) if abertura.modo == 'a' else abertura.posicao
```

**A)** Porque posicao não pode ser armazenada em dataclass.

**B)** Porque o modo a também deve permitir leitura independentemente da permissão.

**C)** Porque o comprimento mede quantos processos existem.

**D)** Porque outra abertura pode ter alterado o tamanho e append deve continuar escrevendo no final atual.

**E)** Porque append sempre apaga o conteúdo anterior.

### Questão 090 — Contar blocos ocupados

**Tipo:** Modificação

Qual expressão fornece a ocupação proporcional dos blocos de dados virtuais, supondo numero_blocos positivo?

```python
ocupacao = len(self.blocos) / self.numero_blocos
```

**A)** len(self.blocos) / len(self.tabela_global), sem proteção de zero.

**B)** len(self.blocos) / self.numero_blocos.

**C)** len(self.tabela_global) / self.numero_blocos.

**D)** self.numero_blocos / self.tamanho_bloco.

**E)** self.raiz.fcb.tamanho / self.numero_blocos.

## 10. Cargas, validação e testes

### Questão 091 — Booleano como duração

**Tipo:** Depuração

Por que inteiro usa type(valor) is int em vez de apenas isinstance(valor, int)?

```python
if type(valor) is not int or valor < minimo:
    raise ErroSimulacao('Inteiro inválido.')
```

**A)** Porque bool é subclasse de int em Python, mas true não deve ser aceito como uma duração inteira da carga.

**B)** Porque o JSON não permite booleanos em nenhum campo.

**C)** Porque type converte automaticamente strings em inteiros.

**D)** Porque isinstance sempre retorna False para números positivos.

**E)** Porque a comparação remove todos os números negativos sozinha.

### Questão 092 — Campo escrito errado

**Tipo:** Rastreamento

Uma instrução informa op='cpu', duracao=2 e também durcao=7. Como o validador atual a trata?

```python
desconhecidos = set(instrucao) - campos[operacao] - {'op'}
```

**A)** Recusa a instrução por conter um campo desconhecido.

**B)** Ignora silenciosamente o erro para favorecer a execução.

**C)** Transforma durcao em nome de thread.

**D)** Usa automaticamente durcao por ser o último campo.

**E)** Soma os dois campos e executa 9.

### Questão 093 — Limite do endereço lógico

**Tipo:** Rastreamento

Um processo tem memoria=128 bytes. Qual conjunto expressa os endereços lógicos válidos?

**A)** Apenas múltiplos de 16.

**B)** Inteiros de 1 a 128.

**C)** Qualquer inteiro não negativo, pois há paginação.

**D)** Inteiros de 0 a 127.

**E)** Inteiros de 0 a 128, inclusive.

### Questão 094 — Identificador repetido

**Tipo:** Rastreamento

É permitido usar thread id='T1' em P1 e também em P2?

**A)** Sim, mas as threads se tornam o mesmo objeto TCB.

**B)** Não; toda thread precisa usar o mesmo ID do processo.

**C)** Sim, desde que seus arquivos estejam em C:.

**D)** Não; IDs de threads são obrigatoriamente únicos no projeto inteiro.

**E)** Sim; a unicidade do ID da thread é exigida dentro do processo, e a chave completa distingue os donos.

### Questão 095 — Entrada sem criar arquivo

**Tipo:** Modificação

Para fornecer uma carga textual completa sem criar um novo arquivo JSON em disco, qual opção já existe?

```python
if opcoes.carga == '-':
    processos = carregar_texto(sys.stdin.read())
```

**A)** Usar --sem-log como substituto do conteúdo da carga.

**B)** Salvar obrigatoriamente um arquivo .txt temporário.

**C)** Usar --carga - e enviar o JSON pela entrada padrão.

**D)** Usar --carga - para ativar aleatoriedade sem JSON.

**E)** Modificar a classe PCB para inserir cada instrução.

### Questão 096 — Mudar o valor padrão do quantum

**Tipo:** Modificação

O professor quer quantum padrão 4 tanto na API quanto na CLI, sem afetar valores explícitos. O que deve ser atualizado?

**A)** O campo tamanho_pagina, porque ele determina o quantum.

**B)** O padrão em Configuracao e o padrão de quantum no mapa do parser, além da documentação e verificações afetadas.

**C)** Todas as durações CPU nas cargas para valor 4.

**D)** Somente a ajuda textual, mantendo os defaults numéricos.

**E)** Somente Configuracao, pois argparse sempre usa os valores da dataclass automaticamente.

### Questão 097 — Teste de não persistência

**Tipo:** Conceito

O teste que bloqueia builtins.open e io.open durante a execução da carga de arquivos verifica principalmente o quê?

**A)** Que as operações do sistema de arquivos simulado não dependem de abrir arquivos hospedeiros durante a simulação.

**B)** Que a aplicação jamais leu os JSON de entrada em momento algum.

**C)** Que todos os objetos Python são imutáveis.

**D)** Que o Windows não permite mais nenhum acesso ao disco em outros programas.

**E)** Que o algoritmo RR é sempre mais rápido que FCFS.

### Questão 098 — Teste de troca de prioridades

**Tipo:** Modificação

Após inverter a convenção de prioridade para maior número primeiro, qual teste fornece evidência mais direta?

**A)** Executar testes de UTF-8 sem observar os despachos.

**B)** Verificar apenas se o README contém a palavra prioridade.

**C)** Usar uma única thread e comparar somente o tempo CPU total.

**D)** Aumentar o número de blocos do disco até não ocorrer erro.

**E)** Criar threads prontas com prioridades conhecidas, conferir a ordem e incluir um empate para validar a estabilidade.

### Questão 099 — JSON malformado e código de saída

**Tipo:** Rastreamento

Uma carga tem um erro de sintaxe JSON. Qual comportamento a CLI implementa?

**A)** Cria automaticamente um arquivo corrigido.

**B)** Ignora a sintaxe e procura somente números no texto.

**C)** Substitui toda a carga por um sorteio de processos.

**D)** Retorna código 0 e executa uma carga vazia.

**E)** Informa erro objetivo, incluindo localização do problema JSON, e retorna código 2.

### Questão 100 — Adicionar campo novo à carga

**Tipo:** Modificação

Deseja-se acrescentar um campo opcional etiqueta no processo e mantê-lo no PCB. Qual mudança é necessária além de usar o campo no JSON?

**A)** Nenhuma; todos os campos desconhecidos já são guardados automaticamente no PCB.

**B)** Gravar a etiqueta num arquivo real para evitar alterar o modelo.

**C)** Somente substituir json.loads por eval.

**D)** Remover a validação de todos os campos e ignorar o armazenamento.

**E)** Aceitar e validar o campo em construir_processos, acrescentar seu armazenamento no modelo e repassá-lo ao construir o PCB.

## 11. Pedidos práticos de alteração durante a apresentação

### Questão 101 — Contador de preempções

**Tipo:** Modificação

O professor pede a quantidade de preempções RR nos resultados. Que cálculo usa o log existente sem confundir despachos com preempções?

```python
preempcoes = sum(r.tipo == 'PREEMPCAO' for r in self.log.registros)
```

**A)** Contar somente os registros cujo tipo é PREEMPCAO.

**B)** Usar trocas_contexto, pois toda troca resulta de fim de quantum.

**C)** Contar todos os eventos ESTADO_THREAD.

**D)** Subtrair o número de arquivos do horizonte.

**E)** Contar todas as interrupções de E/S como preempções.

### Questão 102 — Somente eventos de uma thread

**Tipo:** Modificação

Para exibir eventos diretamente atribuídos a P1/T1, sem alterar o log original, qual filtro é correto?

```python
filtrados = [r for r in simulador.log.registros if r.objeto == 'P1/T1']
```

**A)** Trocar o processo_id das outras threads antes de imprimir.

**B)** Apagar todos os outros registros de self.log.registros.

**C)** Selecionar os registros cujo objeto é igual a 'P1/T1'.

**D)** Selecionar todos os registros cujo tipo é P1.

**E)** Escolher somente registros com clock igual a 1.

### Questão 103 — Métrica de throughput por thread

**Tipo:** Modificação

Além do throughput por processo, deseja-se medir threads concluídas por unidade do horizonte. Como calcular na execução finalizada?

```python
concluidas = sum(len(p.threads) for p in self.processos.values())
throughput_threads = concluidas / total if total else 0
```

**A)** Dividir o número de processos pelo tamanho da página.

**B)** Dividir o clock pela CPU restante da thread atual.

**C)** Somar len(p.threads) dos processos e dividir por tempo_total, protegendo horizonte zero.

**D)** Usar referencias_memoria como número de threads.

**E)** Somar esperas e dividir por quantidade de arquivos.

### Questão 104 — Novo estado SUSPENSO

**Tipo:** Modificação

Por que acrescentar apenas SUSPENSO ao Enum não basta para criar suporte funcional a suspensão?

**A)** Porque suspender é sempre idêntico a finalizar.

**B)** Porque todo estado precisa ser um arquivo físico.

**C)** Porque Enum não permite novos nomes.

**D)** Faltariam transições, eventos de suspensão/retorno, tratamento nas filas e regra de estado agregado do processo.

**E)** Porque a tipagem cria automaticamente todos os eventos e métricas de estados.

### Questão 105 — Renovar quantum após bloqueio

**Tipo:** Rastreamento

Uma thread RR q=4 executa CPU 1, bloqueia por E/S e depois é despachada novamente. Qual quantum_restante recebe no novo despacho?

```python
thread.tcb.quantum_restante = self.configuracao.quantum
```

**A)** O número de requisições concluídas do dispositivo.

**B)** 1, igual ao primeiro surto.

**C)** Zero, para forçar uma preempção imediata.

**D)** 3, pois o modelo sempre conserva o quantum através de bloqueios.

**E)** 4, pois cada despacho inicia uma nova rodada.

### Questão 106 — Limitar intervalo de RR

**Tipo:** Depuração

Qual seria o efeito de trocar min por max no cálculo do intervalo de CPU do RR?

```python
intervalo = min(tcb.cpu_restante, tcb.quantum_restante)
```

**A)** Converteria o tempo de serviço em bytes.

**B)** Apenas inverteria a prioridade numérica, sem mudar a CPU.

**C)** Seria equivalente porque ambos os valores sempre são iguais.

**D)** Poderia executar além do quantum ou além do surto restante, violando o limite e gerando contadores incorretos.

**E)** Reduziria sempre o intervalo para zero.

### Questão 107 — Tempo de página apenas por configuração

**Tipo:** Modificação

Quer-se elevar a latência padrão de falta para 8 em uma demonstração, sem mudar as classes. Qual opção atende?

**A)** Usar --tempo-falta-pagina 8.

**B)** Usar --tamanho-pagina 8, que controla apenas o tempo.

**C)** Usar --tempo-disco 8, pois o paginador sempre é a mesma fila do disco.

**D)** Usar --numero-molduras 8 como sinônimo de duração.

**E)** Usar --semente 8 para multiplicar a latência.

### Questão 108 — Desempate por ID na prioridade

**Tipo:** Modificação

O professor pede que, somente em empate de prioridade, prevaleçam processo_id e identificador, em ordem lexicográfica, em vez da fila. Qual chave implementa essa regra?

```python
return min(range(len(fila)), key=lambda i: (
    prioridades[fila[i].tcb.processo_id],
    fila[i].tcb.processo_id, fila[i].tcb.identificador))
```

**A)** (prioridade_do_processo, processo_id, identificador_da_thread).

**B)** (-prioridade_do_processo,), invertendo também a convenção da prioridade.

**C)** (len(fila),), que é igual para todas as candidatas.

**D)** (identificador_da_thread, prioridade_do_processo), deixando o ID como critério principal.

**E)** (clock, tamanho_bloco), ignorando os IDs e a prioridade.

### Questão 109 — Adicionar operação ao interpretador

**Tipo:** Modificação

Deseja-se criar op='marcar' que apenas grave uma mensagem no log, sem CPU útil. Qual integração evita que a nova operação caia indevidamente no tratamento de arquivos?

```python
elif operacao == 'marcar':
    self._registrar('MARCADOR', thread.chave, instrucao['mensagem'])
    self._avancar_programa(thread)
```

**A)** Colocar mensagem em Configuracao e deixar o PC parado.

**B)** Criar um arquivo real com o nome da mensagem.

**C)** Contabilizar mensagem como endereço físico sem alterar o interpretador.

**D)** Aceitar e validar mensagem em carga.py e acrescentar um ramo explícito em _executar_instrucoes que registre e avance o PC.

**E)** Somente usar op='marcar' no JSON, pois o validador aceita qualquer operação.

### Questão 110 — Validar faixa da nova operação

**Tipo:** Modificação

Ao implementar seek, o professor pede que posicao=True seja recusado. Qual condição aplica a mesma política de tipos do restante do projeto?

```python
if type(posicao) is not int or posicao < 0:
    raise ErroSimulacao('Posição deve ser inteira não negativa.')
```

**A)** type(posicao) is not int or posicao < 0.

**B)** posicao < 0, suficiente para rejeitar todo booleano.

**C)** posicao is None, única condição necessária.

**D)** not isinstance(posicao, int), que sempre recusa True.

**E)** str(posicao).isdigit(), que mantém o contrato de entrada inteira sem conversões.

## 12. Diagnóstico integrado e defesa das decisões

### Questão 111 — Aumentar molduras e concluir demais

**Tipo:** Conceito

Na carga memoria, quatro molduras reduzem as faltas em relação a duas. Que conclusão é sustentada pelo experimento?

**A)** FIFO não pode apresentar anomalia em nenhuma sequência.

**B)** A redução ocorreu nessa sequência; não demonstra que FIFO sempre melhora ao adicionar molduras em qualquer carga.

**C)** A política de CPU foi convertida em LRU pelo número de molduras.

**D)** A CPU útil da carga passou necessariamente de 11 para 44.

**E)** Quatro molduras eliminam até as primeiras faltas de páginas ainda não carregadas.

### Questão 112 — Comparação sem controle

**Tipo:** Depuração

Alguém compara FCFS com contexto 0 e RR com contexto 3 e atribui toda diferença de horizonte ao algoritmo. Qual é o problema?

**A)** Comparar métricas é impossível em um relógio lógico.

**B)** Foram alteradas duas variáveis; é preciso manter o custo de contexto igual para isolar a política.

**C)** RR só funciona com contexto zero.

**D)** FCFS sempre precisa obrigatoriamente de contexto 3.

**E)** O custo não afeta o horizonte, então a comparação está isolada.

### Questão 113 — Erro simulado versus falha da CLI

**Tipo:** Conceito

Qual é a diferença entre --quantum 0 e uma instrução ler com descritor fechado em uma carga válida?

**A)** O parâmetro inválido encerra a CLI com código 2; a leitura inválida gera ERRO_ARQUIVO e a thread continua.

**B)** Ambos são corrigidos silenciosamente sem log.

**C)** Ambos precisam gerar um arquivo de erro em C:.

**D)** O parâmetro inválido executa normalmente com CPU negativa.

**E)** A leitura inválida altera o algoritmo para FCFS.

### Questão 114 — Evitar bytecode em disco

**Tipo:** Conceito

Por que main.py define sys.dont_write_bytecode antes de importar os módulos do simulador?

```python
import sys
sys.dont_write_bytecode = True
from simulador.terminal import main
```

**A)** Para evitar a gravação dos arquivos de cache .pyc durante os imports da aplicação.

**B)** Para impedir que os módulos sejam lidos do disco.

**C)** Para fazer o sistema operacional não usar memória virtual.

**D)** Para desativar a compilação das instruções Python em memória.

**E)** Para transformar todos os arquivos virtuais em arquivos de texto reais.

### Questão 115 — Copiar registradores para o PCB

**Tipo:** Depuração

O que o .copy() evita ao guardar no PCB o último contexto observado, em comparação com atribuir diretamente o dicionário do TCB?

```python
pcb.registradores = thread.tcb.registradores.copy()
```

**A)** Zera os registradores da thread de origem.

**B)** Copia os registradores de todas as threads do sistema.

**C)** Cria automaticamente uma cópia profunda de qualquer objeto aninhado.

**D)** Salva o dicionário no disco hospedeiro.

**E)** Evita que os dois campos referenciem o mesmo dicionário externo, embora a cópia seja rasa.

### Questão 116 — Perigo de reusar processos consumidos

**Tipo:** Depuração

Por que não basta criar dois Simulador diferentes usando a mesma lista de objetos Processo já executados no primeiro?

```python
a = Simulador(carregar_arquivo(caminho), config_a)
b = Simulador(carregar_arquivo(caminho), config_b)
```

**A)** Porque duas instâncias de uma classe são proibidas em Python.

**B)** Porque toda carga precisa de uma semente diferente para ser comparável.

**C)** Porque o código sempre faz deepcopy automaticamente no construtor.

**D)** Os PCBs e TCBs foram modificados; é preciso reconstruir os processos da carga para comparar execuções limpas.

**E)** Porque registros de eventos são arquivos de uso exclusivo do Windows.

### Questão 117 — Reciclar moldura e FIFO

**Tipo:** Depuração

Por que liberar(processo_id) também precisa retirar da ordem_fifo os índices das molduras liberadas?

```python
self.molduras[indice] = None
self.ordem_fifo.remove(indice)
```

**A)** Porque a fila de prontos contém os mesmos inteiros das molduras.

**B)** Para impedir que qualquer moldura livre seja utilizada novamente.

**C)** Para mudar a prioridade numérica dos processos restantes.

**D)** Para evitar índices obsoletos e duplicados na ordem de substituição quando essas molduras forem reutilizadas.

**E)** Para converter o conteúdo das páginas em arquivos.

### Questão 118 — Conservação de tempos

**Tipo:** Depuração

Uma alteração produz tempo_total=10, cpu_util=8 e tempo_contexto=5. Qual diagnóstico é mais adequado?

```python
cpu_ociosa = total - self.tempo_cpu - self.tempo_contexto
```

**A)** É normal: uma CPU lógica sempre tem utilização maior que 100%.

**B)** A diferença negativa deve ser escondida com abs sem investigar.

**C)** Há inconsistência na contabilização ou sobreposição indevida de CPU/contexto, pois ociosidade resultaria negativa.

**D)** Isso prova que o disco virtual está cheio.

**E)** O throughput corrige automaticamente todos os contadores.

### Questão 119 — Substituição em qual instante

**Tipo:** Rastreamento

Na implementação atual, em que momento é escolhida a moldura livre ou a vítima de uma falta de página?

```python
moldura, vitima = self.memoria.carregar(*chave)
```

**A)** Na conclusão do atendimento do paginador, quando _concluir_paginacao chama memoria.carregar.

**B)** Na criação da configuração da CLI.

**C)** Sempre na chegada inicial do processo, antes de qualquer referência.

**D)** No primeiro fechamento de arquivo da thread.

**E)** Somente após todos os processos já terem finalizado.

### Questão 120 — Mudança segura na frente do professor

**Tipo:** Modificação

O professor pede uma mudança curta na regra de seleção. Qual sequência demonstra melhor compreensão e reduz regressões?

**A)** Reescrever o núcleo inteiro antes de ler o pedido.

**B)** Usar uma carga enorme sem conhecer a ordem esperada e concluir que está correto porque terminou.

**C)** Modificar várias classes sem prever o efeito e observar apenas se a aplicação abre.

**D)** Ajustar apenas o gabarito do material para coincidir com qualquer saída.

**E)** Explicar a regra atual, localizar a política, alterar o menor trecho coerente e conferir um cenário pequeno com resultado esperado e os testes relevantes.

---

## Gabarito rápido

| Coluna 1 | Coluna 2 | Coluna 3 | Coluna 4 | Coluna 5 | Coluna 6 | Coluna 7 | Coluna 8 | Coluna 9 | Coluna 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 001: **B** | 002: **E** | 003: **D** | 004: **B** | 005: **C** | 006: **B** | 007: **C** | 008: **D** | 009: **C** | 010: **E** |
| 011: **D** | 012: **B** | 013: **A** | 014: **B** | 015: **A** | 016: **D** | 017: **A** | 018: **E** | 019: **E** | 020: **C** |
| 021: **C** | 022: **D** | 023: **A** | 024: **E** | 025: **D** | 026: **B** | 027: **B** | 028: **E** | 029: **C** | 030: **C** |
| 031: **D** | 032: **D** | 033: **A** | 034: **B** | 035: **B** | 036: **D** | 037: **B** | 038: **B** | 039: **B** | 040: **C** |
| 041: **D** | 042: **A** | 043: **E** | 044: **A** | 045: **E** | 046: **B** | 047: **B** | 048: **E** | 049: **E** | 050: **B** |
| 051: **C** | 052: **B** | 053: **A** | 054: **B** | 055: **D** | 056: **C** | 057: **C** | 058: **D** | 059: **C** | 060: **A** |
| 061: **E** | 062: **C** | 063: **D** | 064: **B** | 065: **B** | 066: **E** | 067: **A** | 068: **A** | 069: **C** | 070: **C** |
| 071: **A** | 072: **E** | 073: **E** | 074: **A** | 075: **C** | 076: **E** | 077: **E** | 078: **D** | 079: **C** | 080: **D** |
| 081: **C** | 082: **D** | 083: **C** | 084: **B** | 085: **E** | 086: **C** | 087: **A** | 088: **D** | 089: **D** | 090: **B** |
| 091: **A** | 092: **A** | 093: **D** | 094: **E** | 095: **C** | 096: **B** | 097: **A** | 098: **E** | 099: **E** | 100: **E** |
| 101: **A** | 102: **C** | 103: **C** | 104: **D** | 105: **E** | 106: **D** | 107: **A** | 108: **A** | 109: **D** | 110: **A** |
| 111: **B** | 112: **B** | 113: **A** | 114: **A** | 115: **E** | 116: **D** | 117: **D** | 118: **C** | 119: **A** | 120: **E** |

As colunas organizam dez questões por linha; o número dentro da célula identifica a questão.

## Gabarito comentado e pontos de alteração

### 1. Orientação a objetos e arquitetura

#### Questão 001 — B

**Resposta:** Thread, com contexto individual no TCB.

**Comentário:** Escalonador.fila_prontos contém objetos Thread. O processo agrupa recursos, mas não é a unidade selecionada pela política.

**Onde estudar/alterar:** simulador/escalonamento.py: Escalonador; simulador/modelo.py: Thread e TCB

#### Questão 002 — E

**Resposta:** Composição: o núcleo coordena objetos com responsabilidades próprias.

**Comentário:** O construtor mantém componentes em atributos. Alterar uma política não exige transformar o núcleo em um subtipo de sistema de arquivos.

**Onde estudar/alterar:** simulador/nucleo.py: Simulador.__init__

#### Questão 003 — D

**Resposta:** Devolver o índice da thread escolhida sem remover elementos da fila.

**Comentário:** A política escolhe um índice; Escalonador.selecionar realiza pop(indice). Separar escolha e remoção evita remover a mesma thread duas vezes.

**Onde estudar/alterar:** simulador/escalonamento.py: PoliticaEscalonamento.selecionar

#### Questão 004 — B

**Resposta:** Cria uma lista independente para cada TCB.

**Comentário:** Cada contexto precisa da própria coleção. Uma coleção compartilhada produziria notificações e contexto misturados entre threads.

**Onde estudar/alterar:** simulador/modelo.py: TCB

#### Questão 005 — C

**Resposta:** dataclasses.replace(config, quantum=4).

**Comentário:** Configuracao é frozen. replace cria outra instância e executa sua validação, como já fazem os experimentos.

**Onde estudar/alterar:** simulador/configuracao.py: Configuracao; simulador/terminal.py: executar_experimentos

#### Questão 006 — B

**Resposta:** No núcleo, ao limitar o intervalo pela quota restante e devolver a thread ao fim da fila.

**Comentário:** A ordem da seleção é FCFS nas duas políticas. _iniciar_cpu e _concluir_cpu aplicam o limite e a preempção RR.

**Onde estudar/alterar:** simulador/escalonamento.py: RoundRobin; simulador/nucleo.py: _iniciar_cpu e _concluir_cpu

#### Questão 007 — C

**Resposta:** O contador_programa do TCB de cada thread.

**Comentário:** O núcleo consulta thread.tcb.contador_programa. O PCB recebe o último PC observado, mas não substitui o contexto individual.

**Onde estudar/alterar:** simulador/nucleo.py: _executar_instrucoes e _avancar_programa

#### Questão 008 — D

**Resposta:** Implementar o contrato da política, registrá-la na fábrica e nas validações/CLI, e testar sua ordenação.

**Comentário:** A classe concreta deve devolver um índice. A nova opção precisa ser aceita também em Configuracao e argparse; sem isso, não será selecionável.

**Onde estudar/alterar:** simulador/escalonamento.py; simulador/configuracao.py; simulador/terminal.py

**Treino adicional:** Localize o mapa de classes em Escalonador.__init__ e as opções de --algoritmo.

#### Questão 009 — C

**Resposta:** A tabela de arquivos abertos do PCB.

**Comentário:** Os descritores pertencem ao processo. PC, registradores, notificações e pilha pertencem ao TCB, mesmo quando uma thread guarda um número de descritor em seu registrador.

**Onde estudar/alterar:** simulador/modelo.py: PCB.arquivos_abertos e TCB

#### Questão 010 — E

**Resposta:** Cálculo em Simulador.metricas; exibição em apresentar_metricas.

**Comentário:** O núcleo devolve dados; a interface decide como representá-los. A saída JSON também aproveita o dicionário de métricas.

**Onde estudar/alterar:** simulador/nucleo.py: metricas; simulador/terminal.py: apresentar_metricas

### 2. Estados, processos e contexto

#### Questão 011 — D

**Resposta:** NOVO para PRONTO.

**Comentário:** _admitir registra CHEGADA e chama _mudar_estado com PRONTO. Isso registra a causa e insere a thread na fila.

**Onde estudar/alterar:** simulador/nucleo.py: _admitir e TRANSICOES

#### Questão 012 — B

**Resposta:** A thread pode ficar pronta sem entrar na fila e sem registrar a causa ou atualizar o processo.

**Comentário:** _mudar_estado centraliza validação, log, instante de entrada na fila, inserção e atualização agregada do PCB. Atribuir o campo ignora esses efeitos.

**Onde estudar/alterar:** simulador/nucleo.py: _mudar_estado

#### Questão 013 — A

**Resposta:** PRONTO.

**Comentário:** _atualizar_processo dá preferência a EXECUTANDO e depois a PRONTO. Uma thread pronta permite que o processo continue elegível à CPU.

**Onde estudar/alterar:** simulador/nucleo.py: _atualizar_processo

#### Questão 014 — B

**Resposta:** Devem permanecer disponíveis até todas as threads finalizarem ou até fechamento explícito.

**Comentário:** A liberação automática de recursos está condicionada ao estado agregado FINALIZADO. Fechar ao terminar uma única thread prejudicaria as demais.

**Onde estudar/alterar:** simulador/nucleo.py: _atualizar_processo

#### Questão 015 — A

**Resposta:** Preservar cpu_restante=3 e o PC na instrução CPU ainda incompleta.

**Comentário:** O PC avança somente quando o surto termina. _iniciar_cpu inicializa a duração apenas se cpu_restante é zero, permitindo a retomada.

**Onde estudar/alterar:** simulador/nucleo.py: _iniciar_cpu e _concluir_cpu

#### Questão 016 — D

**Resposta:** 5 unidades.

**Comentário:** Somam-se os intervalos de fila: (4-1)+(9-7)=5. Bloqueios e CPU não entram nessa soma.

**Onde estudar/alterar:** simulador/nucleo.py: _despachar; TCB.tempo_espera

#### Questão 017 — A

**Resposta:** Trocar = por += na atualização de tempo_espera.

**Comentário:** A atribuição simples sobrescreveria as esperas anteriores. O código original usa += para somar os intervalos de cada despacho.

**Onde estudar/alterar:** simulador/nucleo.py: _despachar

#### Questão 018 — E

**Resposta:** Para retirar o quadro tanto no sucesso quanto quando ocorre ErroSimulacao.

**Comentário:** O bloco finally restaura a pilha lógica. O except trata o erro da chamada; a limpeza do quadro precisa ocorrer em ambos os caminhos.

**Onde estudar/alterar:** simulador/nucleo.py: _executar_arquivo

#### Questão 019 — E

**Resposta:** P2/T3.

**Comentário:** A propriedade combina o dono e o ID local. O separador / é proibido nos IDs de entrada para não tornar essa identificação ambígua.

**Onde estudar/alterar:** simulador/modelo.py: Thread.chave; simulador/carga.py: construir_processos

#### Questão 020 — C

**Resposta:** É levantado ErroSimulacao; deve-se construir outra instância para uma nova rodada.

**Comentário:** _executado protege contra repetição sobre estado consumido. Os experimentos recarregam processos e constroem outro Simulador.

**Onde estudar/alterar:** simulador/nucleo.py: executar; simulador/terminal.py: executar_experimentos

### 3. Eventos discretos e determinismo

#### Questão 021 — C

**Resposta:** Um evento de conclusão é agendado 100 unidades lógicas à frente, sem sleep real.

**Comentário:** O modelo progride por eventos e não por tempo de parede. Isso permite reproduzir a mesma execução em máquinas diferentes.

**Onde estudar/alterar:** simulador/nucleo.py: _iniciar_cpu; simulador/eventos.py: AgendaEventos

#### Questão 022 — D

**Resposta:** instante e depois ordem; tipo e acao não participam da comparação.

**Comentário:** Evento tem order=True, enquanto tipo e acao usam compare=False. ordem vem de um contador e resolve empates de forma estável.

**Onde estudar/alterar:** simulador/eventos.py: Evento e AgendaEventos.agendar

#### Questão 023 — A

**Resposta:** A, B, C.

**Comentário:** A tem o menor instante. B e C empatam no instante e seguem a ordem de inserção, pois B recebeu ordem menor.

**Onde estudar/alterar:** simulador/eventos.py: AgendaEventos; testes/test_simulador.py: test_agenda_estavel

#### Questão 024 — E

**Resposta:** O heap poderia tentar ordenar funções, causando TypeError.

**Comentário:** Funções não têm ordenação natural com <. compare=False e o contador único evitam depender da comparação de callbacks.

**Onde estudar/alterar:** simulador/eventos.py: Evento.acao

#### Questão 025 — D

**Resposta:** Para guardar o processo daquela iteração e evitar que os callbacks usem o último valor do laço.

**Comentário:** O argumento padrão é avaliado ao construir a função. A captura tardia do nome do laço poderia admitir repetidamente o processo errado.

**Onde estudar/alterar:** simulador/nucleo.py: executar

#### Questão 026 — B

**Resposta:** Para manter o mesmo fluxo de eventos e a ordem registrada, mesmo sem avanço temporal.

**Comentário:** Eventos de duração zero são válidos para contexto e são consumidos no instante atual. O algoritmo não precisa de um caminho especial para executar instruções.

**Onde estudar/alterar:** simulador/nucleo.py: _despachar e executar

#### Questão 027 — B

**Resposta:** Admite P2 e o coloca na fila; P1 conserva a CPU até terminar ou bloquear.

**Comentário:** A agenda processa a chegada no meio do intervalo já reservado. FCFS não preempta a thread atual; a conclusão CPU continua agendada para 8.

**Onde estudar/alterar:** simulador/nucleo.py: executar, _admitir e _iniciar_cpu

#### Questão 028 — E

**Resposta:** Isso pode selecionar antes de conhecer todas as threads recém-prontas e mudar a regra documentada de empate.

**Comentário:** O laço central processa os eventos do instante antes da seleção. Despachar cedo pode favorecer a primeira chegada até quando outra tem maior prioridade.

**Onde estudar/alterar:** simulador/nucleo.py: executar

#### Questão 029 — C

**Resposta:** Mesmas métricas e eventos de execução; a linha de configuração registra a semente diferente.

**Comentário:** A semente é registrada, mas não há geração aleatória nas cargas. Não se deve afirmar que logs integrais são idênticos quando o próprio registro de configuração muda.

**Onde estudar/alterar:** simulador/configuracao.py: semente; simulador/nucleo.py: executar

#### Questão 030 — C

**Resposta:** Há uma inconsistência interna: faltou agendar a conclusão da atividade que mantém a CPU ocupada.

**Comentário:** Uma thread atual deve ter um evento de fim de contexto ou CPU. O RuntimeError expõe a quebra da invariável em vez de esconder um travamento.

**Onde estudar/alterar:** simulador/nucleo.py: executar

### 4. Escalonamento e mudanças de política

#### Questão 031 — D

**Resposta:** Retorna T1 e a fila passa a [T2,T3].

**Comentário:** FCFS.selecionar devolve índice zero. O mecanismo usa pop(0) e devolve o objeto escolhido.

**Onde estudar/alterar:** simulador/escalonamento.py: FCFS.selecionar e Escalonador.selecionar

#### Questão 032 — D

**Resposta:** T2/P2, por ter o menor valor numérico de prioridade.

**Comentário:** A política aplica min à prioridade do processo dono. O ID serve para identificar a thread, sem substituir o critério da política.

**Onde estudar/alterar:** simulador/escalonamento.py: Prioridades.selecionar

#### Questão 033 — A

**Resposta:** Trocar min por max na seleção, conservando a chave de prioridade.

**Comentário:** max retorna o primeiro máximo entre os índices percorridos, preservando o desempate da fila. Também devem mudar os testes e a convenção documentada.

**Onde estudar/alterar:** simulador/escalonamento.py: Prioridades.selecionar

**Treino adicional:** Crie uma fila com prioridades 1, 7 e 7; confira seleção da primeira thread de prioridade 7.

#### Questão 034 — B

**Resposta:** P2/T1, pois o empate mantém a ordem da fila existente.

**Comentário:** min percorre os índices em ordem e mantém a primeira ocorrência do menor valor. A ordenação por ID acontece nas admissões, não em toda seleção de prioridades.

**Onde estudar/alterar:** simulador/escalonamento.py: Prioridades.selecionar

#### Questão 035 — B

**Resposta:** Em 5.

**Comentário:** Prioridades nesta implementação não preempta uma thread atual. P2 espera quatro unidades, até a conclusão de P1.

**Onde estudar/alterar:** simulador/nucleo.py: _admitir e _concluir_cpu

#### Questão 036 — D

**Resposta:** Contabilizar o trecho executado, salvar CPU restante, invalidar a conclusão antiga e reencaminhar a thread ao estado pronto.

**Comentário:** O intervalo atual já tem callback futuro. Uma implementação segura precisa cancelar ou tornar obsoleto esse callback e evitar dupla contabilização; também deve preservar a máquina de estados.

**Onde estudar/alterar:** simulador/nucleo.py: _iniciar_cpu, _concluir_cpu, _admitir; simulador/eventos.py

**Treino adicional:** Use um identificador de geração do despacho e teste a chegada de uma prioridade maior no meio do surto.

#### Questão 037 — B

**Resposta:** P1 [0,2), P2 [2,4), P1 [4,5).

**Comentário:** P1 usa um quantum e volta ao fim. P2 conclui dentro do seu quantum; P1 então executa a unidade restante.

**Onde estudar/alterar:** cargas/verificacao.json; simulador/nucleo.py: _concluir_cpu

#### Questão 038 — B

**Resposta:** Em 2, pois o quantum de P1 acumula nos dois surtos adjacentes.

**Comentário:** P1 executa uma unidade da primeira CPU e uma da segunda, esgotando a rodada. O quantum só é reiniciado em novo despacho.

**Onde estudar/alterar:** simulador/nucleo.py: _despachar, _iniciar_cpu e _concluir_cpu

#### Questão 039 — B

**Resposta:** A thread preemptada voltaria à cabeça e poderia impedir a rotação esperada.

**Comentário:** RR exige retorno ao fim da fila. Inserir na cabeça pode reeleger a mesma thread antes das que já aguardavam.

**Onde estudar/alterar:** simulador/escalonamento.py: Escalonador.adicionar

#### Questão 040 — C

**Resposta:** Retornar len(fila) - 1.

**Comentário:** O mecanismo espera um índice válido. len(fila)-1 aponta para o último elemento; registrar uma nova política evita alterar o significado de FCFS.

**Onde estudar/alterar:** simulador/escalonamento.py: PoliticaEscalonamento e Escalonador.selecionar

### 5. Cálculos de CPU, espera e resposta

#### Questão 041 — D

**Resposta:** 7 unidades.

**Comentário:** Retorno é finalização menos chegada, portanto 11-4=7. Não é o clock absoluto de finalização.

**Onde estudar/alterar:** simulador/nucleo.py: metricas

#### Questão 042 — A

**Resposta:** Resposta 3, retorno 5, CPU útil 2.

**Comentário:** O despacho começa em 0, mas a primeira CPU só começa em 3 e termina em 5. O custo de contexto não é CPU útil.

**Onde estudar/alterar:** simulador/nucleo.py: _despachar, _concluir_contexto e _iniciar_cpu

#### Questão 043 — E

**Resposta:** 60%, 15% e 5 unidades.

**Comentário:** Utilização=12/20; sobrecarga=3/20; ociosidade=20-12-3. Somar útil e contexto como utilização útil perderia a distinção pedida.

**Onde estudar/alterar:** simulador/nucleo.py: metricas

#### Questão 044 — A

**Resposta:** 0,4 processo por unidade de tempo.

**Comentário:** Throughput divide processos concluídos pelo horizonte: 4/10=0,4. O inverso mede tempo médio por conclusão, outra grandeza.

**Onde estudar/alterar:** simulador/nucleo.py: metricas, campo throughput

#### Questão 045 — E

**Resposta:** Horizonte 8 e três despachos.

**Comentário:** Há parcelas CPU 2, 2 e 1, com três custos de uma unidade. Mesmo sem concorrente, a convenção conta a reeleição como despacho.

**Onde estudar/alterar:** simulador/nucleo.py: _despachar e _concluir_cpu

#### Questão 046 — B

**Resposta:** A métrica de resposta passaria a usar uma execução posterior, em vez da primeira utilização útil.

**Comentário:** O campo é um marco único. Atualizá-lo na retomada de um quantum destruiria a definição operacional de resposta.

**Onde estudar/alterar:** simulador/nucleo.py: _iniciar_cpu

#### Questão 047 — B

**Resposta:** Como None nos dados e n/a na apresentação textual.

**Comentário:** Não existe primeira utilização útil para medir. O núcleo preserva None e a interface apresenta n/a, distinguindo ausência de execução de resposta imediata.

**Onde estudar/alterar:** simulador/nucleo.py: metricas; simulador/terminal.py: apresentar_metricas

#### Questão 048 — E

**Resposta:** Filtrar respostas não None e calcular sum(valores)/len(valores), retornando None se a lista ficar vazia.

**Comentário:** A política de amostragem precisa ser explícita. Usar apenas respostas definidas impede erros de tipo e evita fabricar resposta zero para quem nunca executou CPU.

**Onde estudar/alterar:** simulador/nucleo.py: metricas

#### Questão 049 — E

**Resposta:** Porque eliminaria o horizonte e produziria 100% sempre que houvesse CPU útil, ocultando contexto e ociosidade.

**Comentário:** Utilização compara serviço útil com todo o tempo observado. A proteção contra denominador zero também deve permanecer.

**Onde estudar/alterar:** simulador/nucleo.py: metricas

#### Questão 050 — B

**Resposta:** Porque soma esperas de threads que podem estar simultaneamente na fila.

**Comentário:** É uma soma por unidade escalonável, e não a duração de um estado agregado único. A sobreposição das esperas torna a soma maior sem inconsistência.

**Onde estudar/alterar:** simulador/nucleo.py: metricas, espera_threads

### 6. Paginação, tradução e substituição FIFO

#### Questão 051 — C

**Resposta:** Página 2, deslocamento 3.

**Comentário:** divmod(35,16) produz (2,3). O deslocamento deve ser menor que o tamanho da página.

**Onde estudar/alterar:** simulador/memoria.py: decompor_endereco

#### Questão 052 — B

**Resposta:** 67.

**Comentário:** O deslocamento é 3. A base da moldura 4 é 4x16=64, então o físico é 67. Número de página e de moldura não são intercambiáveis.

**Onde estudar/alterar:** simulador/memoria.py: acessar

#### Questão 053 — A

**Resposta:** Se a página está presente e o índice da moldura correspondente.

**Comentário:** Uma entrada não residente tem presente=False e moldura=None. A tabela permite traduzir quando há associação física válida.

**Onde estudar/alterar:** simulador/modelo.py: EntradaPagina

#### Questão 054 — B

**Resposta:** O endereço físico zero é válido, mas seria interpretado como falso e confundido com falta.

**Comentário:** acessar usa None como sentinela de falta. Uma checagem de verdade mistura esse sentinela com o inteiro zero, que pode representar moldura 0 e deslocamento 0.

**Onde estudar/alterar:** simulador/nucleo.py: _acessar_memoria

#### Questão 055 — D

**Resposta:** Página 0.

**Comentário:** FIFO usa a idade de carregamento, não o último acesso. O acerto em 0 não altera ordem_fifo, então 0 continua sendo a mais antiga.

**Onde estudar/alterar:** simulador/memoria.py: acessar e carregar

#### Questão 056 — C

**Resposta:** Um acesso posterior à vítima poderia ser contado como acerto e traduzido para dados de outra página.

**Comentário:** A correspondência tabela-moldura precisa ser consistente nos dois sentidos. A entrada antiga deve ficar ausente e sem moldura.

**Onde estudar/alterar:** simulador/memoria.py: carregar

#### Questão 057 — C

**Resposta:** Duas faltas e um carregamento.

**Comentário:** Cada referência ausente conta uma falta; _faltas_pendentes agrupa as threads pela chave (processo,página). O atendimento é compartilhado.

**Onde estudar/alterar:** simulador/nucleo.py: _acessar_memoria e _concluir_paginacao

#### Questão 058 — D

**Resposta:** Porque a página 0 de P1 e a página 0 de P2 pertencem a espaços lógicos independentes.

**Comentário:** A tupla (processo_id,pagina) distingue donos. Remover processo_id agruparia atendimentos que não representam a mesma página lógica.

**Onde estudar/alterar:** simulador/nucleo.py: _acessar_memoria

#### Questão 059 — C

**Resposta:** Porque a referência pendente se completa no carregamento, que já grava a tradução e desbloqueia a thread.

**Comentário:** O PC da referência já foi avançado. Essa convenção evita contagens artificiais e tentativas intermináveis se a página for removida antes do novo despacho.

**Onde estudar/alterar:** simulador/nucleo.py: _executar_instrucoes e _concluir_paginacao

#### Questão 060 — A

**Resposta:** Manter informação de último uso, atualizá-la nos acessos e escolher a página residente menos recentemente usada.

**Comentário:** LRU precisa distinguir a ordem de uso da ordem de carregamento. A extensão também deve preservar invalidadores, liberação e comparação com a mesma sequência de referências.

**Onde estudar/alterar:** simulador/memoria.py: acessar, carregar e liberar

**Treino adicional:** Reutilize a sequência 0,1,0,2 com duas molduras: FIFO remove 0; LRU deve remover 1.

### 7. Dispositivos, bloqueios e notificações

#### Questão 061 — E

**Resposta:** disco de bloco e terminal de caractere.

**Comentário:** O núcleo constrói dois objetos Dispositivo com tipos distintos. Cada um tem fila, atendimento e tempo padrão próprios.

**Onde estudar/alterar:** simulador/nucleo.py: Simulador.__init__

#### Questão 062 — C

**Resposta:** Em 6.

**Comentário:** P1 usa CPU [0,1), disco [1,5) e CPU [5,6). P2 usa CPU [1,3), sobrepondo-se ao serviço do disco.

**Onde estudar/alterar:** simulador/nucleo.py: _solicitar_es; simulador/entrada_saida.py: Dispositivo

#### Questão 063 — D

**Resposta:** Em 8.

**Comentário:** Um dispositivo atende uma requisição de cada vez. R1 ocupa [0,4) e R2 ocupa [4,8); tempo de fila não é tempo de serviço simultâneo.

**Onde estudar/alterar:** simulador/entrada_saida.py: solicitar, _iniciar_proxima e _concluir

#### Questão 064 — B

**Resposta:** Terminal em 2 e disco em 4.

**Comentário:** Dispositivos têm atendimentos independentes e eventos próprios. O paralelismo é lógico, sem threads hospedeiras.

**Onde estudar/alterar:** simulador/entrada_saida.py: Dispositivo; simulador/nucleo.py: dispositivos

#### Questão 065 — B

**Resposta:** 7 unidades, pois a duração explícita substitui o padrão dessa requisição.

**Comentário:** dict.get retorna a duração informada quando ela existe. A submissão é instantânea, mas o atendimento do dispositivo consome as sete unidades lógicas.

**Onde estudar/alterar:** simulador/nucleo.py: _solicitar_es

#### Questão 066 — E

**Resposta:** Retorno 2 e horizonte 4.

**Comentário:** A thread termina em 2, mas a agenda drena a requisição até 4. A conclusão fica registrada na notificação sem reabrir a thread finalizada.

**Onde estudar/alterar:** simulador/nucleo.py: executar e _solicitar_es

#### Questão 067 — A

**Resposta:** Agendar a conclusão e entregar notificação no callback, deixando a thread prosseguir.

**Comentário:** O núcleo já usa callback que atualiza notificacoes e es_N. Um laço de consulta bloquearia o avanço da própria simulação ou consumiria CPU sem trabalho útil.

**Onde estudar/alterar:** simulador/nucleo.py: _solicitar_es; simulador/entrada_saida.py: _concluir

#### Questão 068 — A

**Resposta:** Poderia tentar EXECUTANDO→PRONTO sem a liberação coordenada da CPU ou FINALIZADO→PRONTO, quebrando estados e filas.

**Comentário:** A requisição assíncrona não retirou a thread da execução. Só a solicitação bloqueante autoriza o retorno de BLOQUEADO para PRONTO no callback.

**Onde estudar/alterar:** simulador/nucleo.py: _solicitar_es

#### Questão 069 — C

**Resposta:** Criar o dispositivo, aceitar seu nome no validador, adicionar parâmetro de configuração/CLI e testar sua fila e interrupções.

**Comentário:** O nome é validado em carga.py e resolvido no mapa do núcleo. Para ser configurável, o tempo também precisa existir em Configuracao e no parser.

**Onde estudar/alterar:** simulador/carga.py: validar_instrucao; simulador/nucleo.py: dispositivos; simulador/configuracao.py; simulador/terminal.py

#### Questão 070 — C

**Resposta:** 60%.

**Comentário:** Utilização considera atendimento/horizonte: 6/10. A espera na fila não ocupa adicionalmente o dispositivo e não deve ser somada ao numerador.

**Onde estudar/alterar:** simulador/nucleo.py: metricas; simulador/entrada_saida.py: tempo_ocupado

### 8. Arquivos, diretórios e descritores

#### Questão 071 — A

**Resposta:** FCB guarda metadados e o primeiro bloco; Bloco guarda bytes e o elo para o próximo.

**Comentário:** O arquivo referencia um FCB com tamanho, permissões e tempos. O conteúdo é reconstruído percorrendo a cadeia de blocos armazenados no dicionário em RAM.

**Onde estudar/alterar:** simulador/arquivos.py: FCB, Arquivo e Bloco

#### Questão 072 — E

**Resposta:** Não; os descritores são locais aos PCBs e apontam para entradas globais distintas.

**Comentário:** A resolução usa pcb.arquivos_abertos[fd]. A tabela global tem uma entrada por abertura, com modo e posição próprios.

**Onde estudar/alterar:** simulador/arquivos.py: abrir e _abertura

#### Questão 073 — E

**Resposta:** b'abc'.

**Comentário:** O conteúdo é compartilhado, mas cada ArquivoAberto possui sua própria posicao. Ler por uma abertura não desloca o cursor da outra.

**Onde estudar/alterar:** simulador/arquivos.py: ArquivoAberto e ler

#### Questão 074 — A

**Resposta:** O conteúdo é truncado para vazio, seus blocos são liberados e o cursor começa em zero.

**Comentário:** abrir chama _substituir_conteudo com b'' para o modo w. Preservar conteúdo é o comportamento de rw, e escrever no fim é o de a.

**Onde estudar/alterar:** simulador/arquivos.py: abrir

#### Questão 075 — C

**Resposta:** 2 bytes.

**Comentário:** 'á'.encode('utf-8') tem dois bytes. O tamanho registra o conteúdo real, enquanto a alocação arredonda a quantidade de blocos.

**Onde estudar/alterar:** simulador/arquivos.py: escrever e _substituir_conteudo

#### Questão 076 — E

**Resposta:** 3 blocos.

**Comentário:** (10+4-1)//4 = 3. O último bloco usa somente dois bytes; não é possível armazenar os 10 bytes em dois blocos de capacidade 4.

**Onde estudar/alterar:** simulador/arquivos.py: _substituir_conteudo

#### Questão 077 — E

**Resposta:** A abertura é recusada, ERRO_ARQUIVO é registrado e a thread pode continuar.

**Comentário:** abrir verifica permissões antes de truncar ou criar descritor. _executar_arquivo captura ErroSimulacao e guarda a mensagem em erro_arquivo.

**Onde estudar/alterar:** simulador/arquivos.py: abrir; simulador/nucleo.py: _executar_arquivo

#### Questão 078 — D

**Resposta:** Recusa a operação porque o diretório não está vazio.

**Comentário:** A remoção recursiva não foi implementada. É preciso remover o conteúdo antes, respeitando também a restrição de arquivo aberto.

**Onde estudar/alterar:** simulador/arquivos.py: remover

#### Questão 079 — C

**Resposta:** b'', sem mover o cursor além do que já foi efetivamente lido.

**Comentário:** O fatiamento a partir do fim resulta vazio. posicao avança por len(resultado), portanto permanece no fim.

**Onde estudar/alterar:** simulador/arquivos.py: ler

#### Questão 080 — D

**Resposta:** Seu conteúdo pode continuar no SistemaArquivos em RAM, mas não é persistido fisicamente e desaparece com o descarte da aplicação.

**Comentário:** A finalização fecha descritores e libera molduras; não apaga os arquivos virtuais. O estado permanece apenas enquanto o objeto que o mantém estiver vivo.

**Onde estudar/alterar:** simulador/nucleo.py: _atualizar_processo; simulador/arquivos.py: SistemaArquivos

### 9. Modificações e defeitos no sistema de arquivos

#### Questão 081 — C

**Resposta:** Para uma escrita recusada preservar o conteúdo anterior e permitir recuperação sem corrupção.

**Comentário:** O arquivo pode reutilizar seus blocos antigos. A capacidade é conferida antes de qualquer mutação; somente depois são reconstruídos os elos e atualizados os metadados.

**Onde estudar/alterar:** simulador/arquivos.py: _substituir_conteudo

#### Questão 082 — D

**Resposta:** Porque fechar remove entradas, e uma cópia das chaves evita alterar o dicionário durante sua iteração.

**Comentário:** A iteração direta pode produzir RuntimeError quando o tamanho muda. A lista representa as chaves iniciais e permite removê-las com segurança.

**Onde estudar/alterar:** simulador/arquivos.py: fechar_todos

#### Questão 083 — C

**Resposta:** Vazamento de abertura global, que pode inclusive fazer o arquivo parecer ainda aberto para remoção.

**Comentário:** As duas tabelas devem perder a associação. remover consulta a tabela global para detectar arquivo aberto, então uma entrada órfã tem efeito funcional.

**Onde estudar/alterar:** simulador/arquivos.py: fechar e remover

#### Questão 084 — B

**Resposta:** Para uma falha por disco cheio não avançar o cursor de uma escrita que não aconteceu.

**Comentário:** A operação deve preservar dados e cursor quando recusada. Antecipar a posição introduziria uma alteração parcial observável pelo processo.

**Onde estudar/alterar:** simulador/arquivos.py: escrever

#### Questão 085 — E

**Resposta:** Validar a instrução, resolver o descritor, verificar o limite, atualizar o cursor da abertura e registrar a operação.

**Comentário:** O cursor pertence a ArquivoAberto. É preciso acrescentar o formato em carga.py e o despacho em _executar_arquivo, além do método do sistema de arquivos e testes de limite.

**Onde estudar/alterar:** simulador/arquivos.py: ArquivoAberto e _abertura; simulador/carga.py; simulador/nucleo.py: _executar_arquivo

**Treino adicional:** Abra duas vezes o mesmo arquivo, mova só um cursor e confirme que o outro não mudou.

#### Questão 086 — C

**Resposta:** Validar o novo valor, localizar o objeto, alterar fcb.permissoes e modificacao e registrar o evento; integrar a nova instrução ao parser da carga.

**Comentário:** Permissões são metadados do FCB, já conferidos também em ler e escrever. A extensão deve definir sua política de autorização, pois o modelo atual não tem dono nem autenticação.

**Onde estudar/alterar:** simulador/arquivos.py: FCB e _exigir_permissao; simulador/carga.py; simulador/nucleo.py

**Treino adicional:** Proponha a regra didática explicitamente e teste uma abertura rw cuja permissão de escrita seja retirada antes de escrever.

#### Questão 087 — A

**Resposta:** Manter um conjunto de índices visitados e recusar um índice repetido.

**Comentário:** Um ciclo não alcança None e causaria percurso infinito. O conjunto detecta repetição; a proteção também pode verificar se o índice existe em self.blocos.

**Onde estudar/alterar:** simulador/arquivos.py: _indices_blocos

#### Questão 088 — D

**Resposta:** 0 novamente, pois escolhe o menor inteiro não utilizado.

**Comentário:** O descritor local é buscado desde zero; IDs de abertura global, ao contrário, crescem com _proxima_abertura. Um registrador com número antigo pode passar a identificar outra abertura após reutilização.

**Onde estudar/alterar:** simulador/arquivos.py: abrir

#### Questão 089 — D

**Resposta:** Porque outra abertura pode ter alterado o tamanho e append deve continuar escrevendo no final atual.

**Comentário:** A escrita concatena a partir do fim observado no momento da chamada. Um cursor antigo poderia sobrescrever dados acrescidos por outra abertura.

**Onde estudar/alterar:** simulador/arquivos.py: escrever

#### Questão 090 — B

**Resposta:** len(self.blocos) / self.numero_blocos.

**Comentário:** Cada chave em self.blocos representa um bloco alocado. Aberturas contam descritores globais, e não capacidade de armazenamento usada.

**Onde estudar/alterar:** simulador/arquivos.py: SistemaArquivos.blocos

**Treino adicional:** Escreva 10 bytes com blocos de 4 e capacidade 5: ocupação esperada 3/5, ou 60%.

### 10. Cargas, validação e testes

#### Questão 091 — A

**Resposta:** Porque bool é subclasse de int em Python, mas true não deve ser aceito como uma duração inteira da carga.

**Comentário:** isinstance(True,int) é True. A verificação exata preserva o contrato da carga, enquanto bloqueante tem validação separada de booleano.

**Onde estudar/alterar:** simulador/carga.py: inteiro; simulador/configuracao.py: __post_init__

#### Questão 092 — A

**Resposta:** Recusa a instrução por conter um campo desconhecido.

**Comentário:** Campos permitidos são explícitos por operação. Detectar a grafia errada evita que uma demonstração use parâmetros diferentes dos pretendidos.

**Onde estudar/alterar:** simulador/carga.py: validar_instrucao

#### Questão 093 — D

**Resposta:** Inteiros de 0 a 127.

**Comentário:** A condição é 0 <= endereco < tamanho. Paginação traduz endereços válidos, mas não amplia o espaço lógico definido pela carga.

**Onde estudar/alterar:** simulador/carga.py: validar_instrucao; simulador/memoria.py: decompor_endereco

#### Questão 094 — E

**Resposta:** Sim; a unicidade do ID da thread é exigida dentro do processo, e a chave completa distingue os donos.

**Comentário:** ids_threads é reiniciado para cada processo. Repetir T1 dentro do mesmo processo é inválido, mas P1/T1 e P2/T1 são chaves diferentes.

**Onde estudar/alterar:** simulador/carga.py: construir_processos; simulador/modelo.py: Thread.chave

#### Questão 095 — C

**Resposta:** Usar --carga - e enviar o JSON pela entrada padrão.

**Comentário:** O terminal lê sys.stdin.read e chama carregar_texto. Os mesmos validadores são aplicados, sem persistir a entrada.

**Onde estudar/alterar:** simulador/terminal.py: main

#### Questão 096 — B

**Resposta:** O padrão em Configuracao e o padrão de quantum no mapa do parser, além da documentação e verificações afetadas.

**Comentário:** A CLI declara seu próprio padrão 2 e o passa ao construtor, portanto pode sobrepor o padrão da dataclass. Os dois pontos precisam ficar coerentes.

**Onde estudar/alterar:** simulador/configuracao.py: Configuracao.quantum; simulador/terminal.py: criar_parser

**Treino adicional:** Compare Configuracao().quantum com criar_parser().parse_args([]).quantum após a alteração.

#### Questão 097 — A

**Resposta:** Que as operações do sistema de arquivos simulado não dependem de abrir arquivos hospedeiros durante a simulação.

**Comentário:** A carga é lida antes de instalar os bloqueios. O teste cobre a execução do núcleo e das chamadas virtuais, não faz uma garantia global sobre processos externos.

**Onde estudar/alterar:** testes/test_simulador.py: test_nucleo_nao_abre_nem_grava_arquivos_reais

#### Questão 098 — E

**Resposta:** Criar threads prontas com prioridades conhecidas, conferir a ordem e incluir um empate para validar a estabilidade.

**Comentário:** O total de CPU não identifica a ordem de seleção. Uma fila com prioridades diferentes e um empate testa precisamente a alteração solicitada.

**Onde estudar/alterar:** testes/test_simulador.py: test_prioridades_e_desempate; simulador/escalonamento.py

#### Questão 099 — E

**Resposta:** Informa erro objetivo, incluindo localização do problema JSON, e retorna código 2.

**Comentário:** carregar_texto converte JSONDecodeError em ErroSimulacao com linha e coluna. main captura a falha e imprime em stderr, sem executar estado parcial.

**Onde estudar/alterar:** simulador/carga.py: carregar_texto; simulador/terminal.py: main

#### Questão 100 — E

**Resposta:** Aceitar e validar o campo em construir_processos, acrescentar seu armazenamento no modelo e repassá-lo ao construir o PCB.

**Comentário:** A lista de campos permitidos é fechada e o construtor do PCB não inventa atributos da carga. A extensão deve conectar formato, modelo e uso de forma explícita.

**Onde estudar/alterar:** simulador/carga.py: construir_processos; simulador/modelo.py: PCB

**Treino adicional:** Teste carga com etiqueta válida, carga sem etiqueta e valor de tipo inválido.

### 11. Pedidos práticos de alteração durante a apresentação

#### Questão 101 — A

**Resposta:** Contar somente os registros cujo tipo é PREEMPCAO.

**Comentário:** Há despachos por admissão, bloqueio e reeleição, então a contagem de trocas é outra métrica. O log já distingue os eventos PREEMPCAO.

**Onde estudar/alterar:** simulador/nucleo.py: metricas, _iniciar_cpu e _concluir_cpu

**Treino adicional:** Na carga verificacao em RR q=2, espere uma preempção e três despachos.

#### Questão 102 — C

**Resposta:** Selecionar os registros cujo objeto é igual a 'P1/T1'.

**Comentário:** Uma visão filtrada preserva a trilha completa. Ela não inclui automaticamente eventos atribuídos ao processo ou ao dispositivo, o que deve ser explicado na interface.

**Onde estudar/alterar:** simulador/eventos.py: RegistroEvento; simulador/terminal.py: main

#### Questão 103 — C

**Resposta:** Somar len(p.threads) dos processos e dividir por tempo_total, protegendo horizonte zero.

**Comentário:** A unidade muda de processos para threads, mas o horizonte permanece o mesmo. Uma nova chave evita substituir silenciosamente a métrica original.

**Onde estudar/alterar:** simulador/nucleo.py: metricas

#### Questão 104 — D

**Resposta:** Faltariam transições, eventos de suspensão/retorno, tratamento nas filas e regra de estado agregado do processo.

**Comentário:** O estado tem efeitos no escalonamento e no progresso. Sua implementação deve garantir que nenhuma thread suspensa permaneça selecionável sem o evento de retorno definido.

**Onde estudar/alterar:** simulador/modelo.py: Estado; simulador/nucleo.py: TRANSICOES, _mudar_estado e _atualizar_processo

**Treino adicional:** Antes de codificar, desenhe as transições permitidas e defina se suspensão durante CPU cancela o evento atual.

#### Questão 105 — E

**Resposta:** 4, pois cada despacho inicia uma nova rodada.

**Comentário:** _despachar atribui configuracao.quantum. CPU restante da instrução e quota da rodada são campos diferentes e têm regras de preservação distintas.

**Onde estudar/alterar:** simulador/nucleo.py: _despachar

#### Questão 106 — D

**Resposta:** Poderia executar além do quantum ou além do surto restante, violando o limite e gerando contadores incorretos.

**Comentário:** O intervalo precisa respeitar os dois limites simultaneamente. max escolhe o maior e pode deixar cpu_restante ou quantum_restante negativo.

**Onde estudar/alterar:** simulador/nucleo.py: _iniciar_cpu

#### Questão 107 — A

**Resposta:** Usar --tempo-falta-pagina 8.

**Comentário:** O paginador tem fila própria e usa tempo_falta_pagina. Alterar o dispositivo disco não modifica automaticamente esse atendimento.

**Onde estudar/alterar:** simulador/terminal.py: criar_parser; simulador/nucleo.py: _iniciar_paginador

#### Questão 108 — A

**Resposta:** (prioridade_do_processo, processo_id, identificador_da_thread).

**Comentário:** Tuplas são comparadas por componentes na ordem. A prioridade continua principal; só os empates chegam aos IDs. Essa seria uma regra nova, que deve ser documentada e testada.

**Onde estudar/alterar:** simulador/escalonamento.py: Prioridades.selecionar

#### Questão 109 — D

**Resposta:** Aceitar e validar mensagem em carga.py e acrescentar um ramo explícito em _executar_instrucoes que registre e avance o PC.

**Comentário:** Operações desconhecidas são rejeitadas. O else atual encaminha instruções restantes para arquivos; um ramo explícito deixa a semântica clara e evita uma operação silenciosamente sem efeito.

**Onde estudar/alterar:** simulador/carga.py: validar_instrucao; simulador/nucleo.py: _executar_instrucoes

**Treino adicional:** Teste um programa cpu(1), marcar('meio'), cpu(1): marcador em 1 e CPU útil total 2.

#### Questão 110 — A

**Resposta:** type(posicao) is not int or posicao < 0.

**Comentário:** O teste exato de tipo rejeita bool. A condição completa do seek ainda deve incluir o limite superior definido e a validação do descritor.

**Onde estudar/alterar:** simulador/carga.py: inteiro; extensão proposta em SistemaArquivos

### 12. Diagnóstico integrado e defesa das decisões

#### Questão 111 — B

**Resposta:** A redução ocorreu nessa sequência; não demonstra que FIFO sempre melhora ao adicionar molduras em qualquer carga.

**Comentário:** O conjunto de referências do experimento cabe em quatro molduras. Uma observação particular não prova monotonicidade geral de FIFO nem elimina faltas iniciais.

**Onde estudar/alterar:** cargas/memoria.json; docs/RELATORIO.md: experimento 3

#### Questão 112 — B

**Resposta:** Foram alteradas duas variáveis; é preciso manter o custo de contexto igual para isolar a política.

**Comentário:** O algoritmo pode mudar a quantidade de despachos, e o custo muda a penalidade de cada um. Configuração, carga e horizonte de observação devem ser controlados para interpretar causalidade.

**Onde estudar/alterar:** simulador/terminal.py: executar_experimentos; docs/RELATORIO.md

#### Questão 113 — A

**Resposta:** O parâmetro inválido encerra a CLI com código 2; a leitura inválida gera ERRO_ARQUIVO e a thread continua.

**Comentário:** A validação da configuração protege a execução antes de iniciar. Erros de chamadas do programa simulado fazem parte do comportamento observável e são tratados no núcleo.

**Onde estudar/alterar:** simulador/configuracao.py; simulador/terminal.py: main; simulador/nucleo.py: _executar_arquivo

#### Questão 114 — A

**Resposta:** Para evitar a gravação dos arquivos de cache .pyc durante os imports da aplicação.

**Comentário:** A flag controla a escrita do cache de bytecode, não a leitura dos fontes nem os objetos em RAM. Os testes também são executados com -B.

**Onde estudar/alterar:** main.py

#### Questão 115 — E

**Resposta:** Evita que os dois campos referenciem o mesmo dicionário externo, embora a cópia seja rasa.

**Comentário:** copy cria outro dicionário, mas valores mutáveis internos ainda podem ser compartilhados. O PCB é um retrato observado, enquanto o contexto usado para execução permanece no TCB.

**Onde estudar/alterar:** simulador/nucleo.py: _avancar_programa

#### Questão 116 — D

**Resposta:** Os PCBs e TCBs foram modificados; é preciso reconstruir os processos da carga para comparar execuções limpas.

**Comentário:** O construtor armazena referências aos processos recebidos. Recarregar a carga recria estados NOVO, PCs e recursos independentes, como fazem os experimentos.

**Onde estudar/alterar:** simulador/nucleo.py: __init__; simulador/terminal.py: executar_experimentos

#### Questão 117 — D

**Resposta:** Para evitar índices obsoletos e duplicados na ordem de substituição quando essas molduras forem reutilizadas.

**Comentário:** A fila deve representar apenas cargas residentes, uma vez por moldura ocupada. Manter índices liberados poderia selecionar uma vítima inválida ou violar a ordem correta.

**Onde estudar/alterar:** simulador/memoria.py: liberar

#### Questão 118 — C

**Resposta:** Há inconsistência na contabilização ou sobreposição indevida de CPU/contexto, pois ociosidade resultaria negativa.

**Comentário:** Com uma CPU lógica, os tempos útil e contexto são parcelas exclusivas do horizonte. O teste de integração verifica a identidade e a não negatividade da ociosidade.

**Onde estudar/alterar:** simulador/nucleo.py: metricas; testes/test_simulador.py: test_todas_cargas_nas_tres_politicas

#### Questão 119 — A

**Resposta:** Na conclusão do atendimento do paginador, quando _concluir_paginacao chama memoria.carregar.

**Comentário:** A requisição entra na fila na ocorrência da falta, mas a escolha acontece na conclusão. Isso evita reservar molduras antecipadamente e faz a decisão refletir o estado daquele instante.

**Onde estudar/alterar:** simulador/nucleo.py: _iniciar_paginador e _concluir_paginacao

#### Questão 120 — E

**Resposta:** Explicar a regra atual, localizar a política, alterar o menor trecho coerente e conferir um cenário pequeno com resultado esperado e os testes relevantes.

**Comentário:** A alteração deve ser demonstrável. Um cenário de duas ou três threads permite prever ordem, tempos e desempates; testes direcionados confirmam a intenção e os de integração detectam efeitos colaterais.

**Onde estudar/alterar:** docs/APRESENTACAO.md; testes/test_simulador.py; simulador/escalonamento.py

**Treino adicional:** Treine inverter prioridades e justificar por que FCFS e RR devem permanecer com a mesma seleção anterior.

## Conferência final antes da apresentação

- Consigo explicar quem possui os recursos e quem disputa a CPU?
- Consigo prever a ordem e os tempos de uma carga pequena?
- Sei quais alterações exigem invalidar um evento já agendado?
- Sei distinguir arquivo virtual em RAM de arquivo de entrada da aplicação?
- Consigo alterar uma regra sem contornar validação, log ou máquina de estados?
- Consigo indicar um teste que falha antes e passa depois da alteração solicitada?

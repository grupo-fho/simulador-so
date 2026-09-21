# Guia de estudo e apresentação

Este arquivo foi pensado para a apresentação do trabalho. Ele não substitui o relatório técnico nem o enunciado; serve para organizar o que cada integrante precisa saber explicar no código e na demonstração.

## 1. Resumo do projeto

O programa é um simulador didático de sistemas operacionais. Ele usa um clock lógico e uma fila de eventos para representar processos, threads, CPU, memória paginada, entrada e saída e sistema de arquivos.

Uma explicação curta para abrir a apresentação pode ser:

> O simulador recebe uma carga de trabalho externa e reproduz a evolução dos processos em tempo lógico. A cada execução podemos acompanhar os eventos e comparar o efeito das políticas de escalonamento, da memória e dos dispositivos nas métricas.

O projeto não é um kernel real e não substitui o Windows ou Linux. Os processos e threads mostrados pelo simulador são objetos Java do modelo.

## 2. O que é simulado e o que é real

| Item | No projeto |
|---|---|
| Processo | objeto `Processo`, usado como PCB |
| Thread | objeto `ThreadSimulada`, usado como TCB |
| CPU | estado do simulador e eventos de execução |
| Clock | contador lógico em unidades abstratas |
| Memória | páginas, molduras e tabelas mantidas em objetos |
| E/S | filas de dispositivos com tempo de serviço |
| Arquivos | árvore e blocos mantidos em memória |
| Logs e CSVs | arquivos reais gravados no computador |
| Interface Swing | aplicação real executada pela JVM |
| Chocolate Doom | processo real iniciado pelo sistema hospedeiro |

Essa diferença é importante porque o enunciado pede uma simulação dos mecanismos, não a criação de um sistema operacional inicializável.

## 3. Caminho de uma execução

O fluxo principal pode ser explicado assim:

```text
arquivo de carga
      |
      v
    Main
      |
      v
Configuracao + Carga
      |
      v
  Simulador
      |
      +--> Escalonador
      +--> Memoria
      +--> Dispositivos
      +--> Arquivos
      |
      v
log + metricas + resultados
```

`Main` valida os argumentos, lê a carga e chama o simulador. O `Simulador` agenda as chegadas, avança o clock pelo próximo evento e chama o mecanismo necessário em cada situação.

## 4. Classes que vale saber explicar

| Classe | Papel principal |
|---|---|
| `Main` | entrada da CLI e fluxo compartilhado com a GUI |
| `Configuracao` | parâmetros da execução |
| `Carga` | leitura e validação da carga textual |
| `Evento` | instante, tipo, sequência e ação agendada |
| `Simulador` | núcleo do clock e dos eventos |
| `Processo` | PCB do modelo |
| `ThreadSimulada` | TCB do modelo |
| `Escalonador` | fila de prontas e política de CPU |
| `Memoria` | tradução, falta e FIFO |
| `Dispositivo` | fila e conclusão de E/S |
| `Arquivos` | diretórios, arquivos, blocos e descritores |
| `Metricas` | cálculo e gravação dos resultados |
| `InterfaceGrafica` | configuração e visualização em Swing |
| `LinhaTempo` | representação gráfica dos eventos da CPU |
| `Doom` | lançador do Chocolate Doom |

## 5. Clock e fila de eventos

O clock não usa `System.currentTimeMillis()` para controlar a simulação. Quando não existe trabalho até o instante seguinte, o clock simplesmente avança até o próximo evento da fila.

No mesmo instante, a ordem usada é:

1. conclusão de E/S ou paginação;
2. chegada;
3. término de unidade da CPU;
4. fim de troca de contexto.

Essa regra evita resultados diferentes entre duas execuções iguais.

## 6. Estados

As threads usam cinco estados: NOVO, PRONTO, EXECUTANDO, BLOQUEADO e FINALIZADO.

Exemplos de transições:

- chegada: NOVO -> PRONTO;
- despacho: PRONTO -> EXECUTANDO;
- fim de quantum no RR: EXECUTANDO -> PRONTO;
- falta de página: EXECUTANDO -> BLOQUEADO;
- conclusão da paginação: BLOQUEADO -> PRONTO;
- fim do programa: EXECUTANDO -> FINALIZADO.

Cada mudança registra uma causa no log.

## 7. Escalonamento

### FCFS

A primeira thread que entra na fila é a primeira a executar. Ela só deixa a CPU quando bloqueia ou termina.

### Round Robin

Usa a mesma fila, mas limita o tempo contínuo de CPU pelo quantum. Se o quantum termina e a thread ainda possui CPU restante, ela volta ao fim da fila.

### Prioridade

A política é não preemptiva. O menor valor numérico representa a maior prioridade. Se uma thread de prioridade melhor chegar enquanto outra executa, ela aguarda o próximo ponto de escalonamento.

### Troca de contexto

Cada despacho pode consumir um custo configurável. Esse tempo entra no clock, mas é registrado como sobrecarga, não como CPU útil.

## 8. Memória

Cada processo possui sua tabela de páginas. O endereço lógico é convertido em página e deslocamento.

Se a página estiver residente, ocorre um acerto. Caso contrário:

1. a falta é registrada;
2. a thread bloqueia;
3. o pedido entra na fila do paginador;
4. é escolhida uma moldura livre ou uma vítima FIFO;
5. a página é carregada;
6. a referência é concluída;
7. a thread volta para PRONTO.

O experimento com duas e três molduras mostra de forma simples o efeito da quantidade de memória sobre a taxa de faltas.

## 9. Entrada e saída

O projeto possui um dispositivo de bloco e um de caractere.

Na operação bloqueante, a thread sai da CPU e só volta quando a interrupção de conclusão é processada. Na operação não bloqueante, a thread continua e o resultado chega depois pela caixa de entrada do TCB.

As filas são FCFS e o tempo de serviço de cada dispositivo é configurável.

## 10. Sistema de arquivos

O sistema de arquivos possui uma raiz, diretórios e arquivos. O conteúdo é dividido em blocos encadeados.

As operações principais são:

```text
CRIAR
MKDIR
ABRIR
LER
ESCREVER
FECHAR
REMOVER
LISTAR
```

Os descritores pertencem ao processo. Threads do mesmo processo compartilham essa tabela. O volume é apenas simulado em memória; ao iniciar uma nova execução ele volta ao estado inicial.

## 11. Formato da carga

Um exemplo pequeno está em `carga-apresentacao.txt`:

```text
PROCESSO P1 0 1 2
THREAD T1
CPU 2
MEM 17
IO disco B
CPU 1
FIM_THREAD
THREAD T2
CPU 4
FIM_THREAD
FIM_PROCESSO
```

Nesse caso o processo `P1` chega no instante 0, tem prioridade 1 e duas páginas lógicas. A primeira thread executa CPU, acessa memória, faz E/S bloqueante e executa novamente. A segunda possui apenas um surto de CPU.

## 12. Métricas

As principais métricas são:

- **tempo de retorno**: finalização menos chegada;
- **tempo de espera**: soma do tempo na fila de prontas;
- **tempo de resposta**: chegada até a primeira utilização da CPU;
- **utilização da CPU**: CPU útil dividida pelo tempo total;
- **sobrecarga**: tempo gasto com trocas de contexto;
- **utilização dos dispositivos**: tempo ocupado dividido pelo tempo total;
- **throughput**: processos concluídos por unidade de tempo;
- **taxa de faltas**: faltas divididas pelo total de referências;
- **trocas de contexto**: quantidade e custo acumulado.

## 13. Resultados usados na apresentação

A tabela `experimentos-apresentacao.csv` contém os resultados já usados para as comparações.

### Políticas de CPU

| Política | Tempo total | Trocas | Resposta média | Espera média | Retorno médio |
|---|---:|---:|---:|---:|---:|
| FCFS | 70 | 13 | 17,75 | 30,25 | 63,33 |
| RR, q=3 | 87 | 24 | 6,25 | 42,00 | 69,00 |
| Prioridade | 75 | 12 | 15,00 | 28,75 | 50,33 |

A leitura mais importante é que as políticas mudam o comportamento de formas diferentes. O RR melhora o primeiro atendimento das threads nesse cenário, mas aumenta bastante a quantidade de trocas. Por isso não existe uma política que seja automaticamente melhor em qualquer carga.

### Quantum do Round Robin

| Quantum | Tempo total | Trocas | Resposta média | Utilização útil da CPU |
|---|---:|---:|---:|---:|
| 1 | 122 | 54 | 3,25 | 44,26% |
| 3 | 87 | 24 | 6,25 | 62,07% |
| 6 | 76 | 15 | 10,00 | 71,05% |

Quantum pequeno melhora o tempo até a primeira resposta, mas aumenta a sobrecarga. No cenário q=1, foram 54 trocas para 54 unidades úteis de CPU.

### Quantidade de molduras

| Molduras | Faltas | Taxa de faltas | Tempo total |
|---|---:|---:|---:|
| 2 | 9 | 100,00% | 65 |
| 3 | 3 | 33,33% | 29 |

A carga repete três páginas. Com três molduras, depois do primeiro carregamento de cada página, as referências seguintes viram acertos. Com duas, a sequência provoca substituições sucessivas.

## 14. Demonstração sugerida

Uma sequência simples de apresentação é:

1. mostrar rapidamente o arquivo de carga;
2. executar FCFS e apontar o log de chegada e despacho;
3. executar RR e mostrar uma preempção por fim de quantum;
4. usar `carga-apresentacao.txt` para mostrar a falta de página e a E/S bloqueante;
5. abrir a linha do tempo e relacionar com o log;
6. apresentar as três tabelas de experimentos;
7. executar a suíte de testes;
8. mostrar a interface gráfica;
9. deixar o DOOM para o final, como recurso extra.

Com Java 21 disponível, a suíte pode ser executada por:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\testar.ps1
```

Exemplo da carga de apresentação:

```powershell
java -cp build\classes so.Main --carga docs\carga-apresentacao.txt --politica RR --quantum 2 --troca 1 --pagina 16 --molduras 1 --falta 3 --disco 2 --terminal 2 --saida resultados\demo-completa
```

## 15. Perguntas que podem aparecer

**Por que as threads do simulador não são threads Java reais?**  
Porque a ordem de execução precisa ser controlada pelo próprio modelo. Se cada TCB fosse uma thread real, o escalonador do sistema hospedeiro também passaria a influenciar a execução.

**Como existe concorrência sem paralelismo real?**  
Os eventos representam atividades que se sobrepõem no tempo lógico. Enquanto uma thread está bloqueada em E/S, outra pode usar a CPU.

**Uma falta de página é um erro?**  
Não. É um evento normal do modelo. A thread bloqueia, a página é carregada e a execução continua.

**Por que o número de faltas pode mudar quando muda apenas o escalonador?**  
Porque muda a ordem das referências à memória. Isso altera quais páginas permanecem nas molduras quando uma referência acontece.

**Qual política é melhor?**  
Depende da carga e da métrica observada. No experimento, RR melhora a resposta inicial, mas aumenta as trocas e o tempo total.

**O DOOM é executado pelo simulador?**  
Não. Ele é iniciado como processo real pelo sistema operacional do computador. O recurso demonstra integração da interface, não execução pelo kernel simulado.

**O executável elimina a necessidade de Java?**  
Ele elimina a necessidade de instalar Java separadamente quando o runtime já está incluído no pacote. Internamente a aplicação continua sendo Java.

## 16. Limitações que devem ser assumidas

O projeto não implementa multiprocessamento real, TLB, páginas sujas, semáforos, deadlocks, cache de blocos, journaling, persistência do volume simulado ou drivers reais. O paginador também não utiliza o mesmo dispositivo de disco usado pelas instruções de E/S.

Essas limitações devem ser apresentadas como simplificações do modelo, e não como recursos parcialmente prontos.

## 17. Antes da entrega

Confiram pelo menos:

- execução a partir de uma cópia limpa do projeto;
- Java 21 selecionado corretamente;
- suíte com 191 verificações aprovadas;
- geração do pacote Windows;
- abertura de `SimuladorSO.exe`;
- execução de uma carga pela CLI;
- geração do log e dos CSVs;
- diagrama compatível com as classes atuais;
- acesso ao repositório GitHub;
- histórico de commits e participação real do grupo;
- declaração das ferramentas externas usadas, conforme as regras da disciplina.

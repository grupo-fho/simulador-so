# Arquitetura do simulador

## Visão geral

O projeto foi organizado em torno de um núcleo orientado a eventos. A classe `Main` recebe os parâmetros da execução, carrega a carga de trabalho e cria o `Simulador`. A partir daí, o tempo é controlado por um clock lógico e por uma fila de eventos. Não existe dependência do relógio real do computador para decidir o resultado da simulação.

As responsabilidades principais ficaram separadas da seguinte forma:

- `Simulador`: coordena o clock, os eventos e o estado geral da execução;
- `Escalonador`: mantém a fila de prontas e escolhe a próxima thread;
- `Memoria`: faz a tradução de endereços e trata faltas de página;
- `Dispositivo`: representa as filas de E/S;
- `Arquivos`: mantém a árvore de diretórios, descritores e blocos;
- `Processo`: concentra as informações equivalentes ao PCB;
- `ThreadSimulada`: concentra as informações equivalentes ao TCB;
- `Metricas`: calcula e grava os resultados da execução.

O diagrama completo está em `diagrama-classes.mmd`.

## Fluxo da execução

1. `Main` lê a configuração e a carga externa.
2. Os processos são criados com suas threads e instruções.
3. O `Simulador` agenda os eventos de chegada.
4. A fila de eventos avança o clock até o próximo acontecimento.
5. Threads prontas entram no `Escalonador` e disputam a CPU conforme a política escolhida.
6. Faltas de página e operações de E/S bloqueantes retiram a thread da CPU.
7. O término da operação gera um novo evento e pode devolver a thread ao estado PRONTO.
8. Quando todas as threads terminam e não existem operações pendentes, o processo é finalizado.
9. Ao fim da simulação são gravados o log e os arquivos de métricas.

## Ordem de eventos no mesmo instante

A fila usa três valores para ordenar os eventos: instante, tipo e sequência de inserção. A precedência adotada é:

1. conclusões de E/S e paginação;
2. chegadas;
3. término de uma unidade de CPU;
4. fim de troca de contexto.

Quando dois eventos têm o mesmo instante e o mesmo tipo, vale a ordem de inserção. A regra é determinística, o que permite reproduzir uma execução com a mesma carga e os mesmos parâmetros.

## CPU e troca de contexto

A CPU é simulada em unidades lógicas. Um surto `CPU 4`, por exemplo, consome quatro unidades de CPU útil. O Round Robin pode interromper esse surto quando o quantum termina, preservando o restante para o próximo despacho.

O custo de troca de contexto é configurável. Durante esse período a CPU está ocupada com a troca, mas nenhuma instrução da carga é executada. O custo é contabilizado separadamente da CPU útil.

As políticas implementadas são FCFS, Round Robin e Prioridade. A prioridade adotada é não preemptiva: uma nova thread com prioridade melhor não interrompe imediatamente a thread que já está executando. Entre prioridades iguais, a ordem de entrada na fila é usada como desempate.

## Processos, threads e estados

`Processo` representa o PCB do modelo. Ele mantém, entre outras informações, identificador, prioridade, instante de chegada, threads, espaço de endereçamento e descritores de arquivos.

`ThreadSimulada` representa o TCB. Cada thread mantém seu estado, contador de programa, acumulador, pilha lógica, instruções e dados usados no cálculo das métricas.

As transições válidas de uma thread são:

```text
NOVO -> PRONTO -> EXECUTANDO
                    |-> PRONTO
                    |-> BLOQUEADO -> PRONTO
                    |-> FINALIZADO
```

O estado do processo é obtido a partir da situação das suas threads. Por isso ele não precisa seguir exatamente a mesma sequência de transições do TCB.

## Memória paginada

Cada processo possui uma tabela de páginas própria. O endereço lógico é dividido em página e deslocamento. Se a página estiver residente, o endereço físico é calculado por:

```text
endereco_fisico = moldura * tamanho_pagina + deslocamento
```

Quando a página não está presente, ocorre uma falta de página. A thread fica bloqueada enquanto o paginador atende a solicitação. Se não houver moldura livre, a substituição usa FIFO. Acertos não alteram a ordem FIFO.

A referência que gerou a falta é concluída no evento de término da paginação. Dessa forma ela não é contada novamente quando a thread volta à CPU.

## Entrada e saída

O modelo possui um dispositivo de bloco e um dispositivo de caractere, cada um com sua própria fila FCFS e tempo de serviço configurável.

A operação bloqueante (`B`) tira a thread da CPU até a interrupção de conclusão. A operação não bloqueante (`NB`) permite que a thread continue, e o resultado é entregue posteriormente pela caixa de entrada do TCB. Não é usada espera ativa.

## Sistema de arquivos

O sistema de arquivos é mantido em memória durante a simulação. A raiz pode conter arquivos e diretórios, e cada arquivo possui metadados simplificados, permissões e indicação do primeiro bloco de dados.

A alocação é encadeada: cada bloco aponta para o próximo. Essa escolha simplifica a alocação, mas torna o acesso a posições mais distantes dependente do percurso da cadeia.

Cada processo possui sua própria tabela de descritores. A abertura cria uma associação com uma entrada da tabela global. São suportadas as operações de criar, abrir, ler, escrever, fechar, remover e listar. Arquivos abertos não podem ser removidos, e diretórios precisam estar vazios antes da remoção.

O volume é recriado a cada execução; ele não representa arquivos reais do sistema hospedeiro.

## Interface gráfica

A interface Swing usa o mesmo fluxo de execução da CLI por meio de `Main.executar`. Ela apenas coleta parâmetros e apresenta os resultados; as regras de escalonamento, memória, E/S e arquivos continuam no núcleo.

A execução é feita em um `SwingWorker` para evitar travar a janela. Isso não significa que os processos simulados sejam executados em paralelo. O modelo continua sequencial e controlado pelo clock lógico.

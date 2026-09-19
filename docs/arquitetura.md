# Arquitetura e convenções do modelo

## Fluxo principal

`Main` lê opções, carrega programas e valida endereços. `Simulador` agenda chegadas, retira eventos em ordem temporal e inicia despachos quando a CPU está livre. Cada evento é uma ação sobre objetos do modelo. A simulação termina depois de todas as threads e requisições pendentes; somente então `Main` grava os resultados.

## Ordem dos eventos simultâneos

A chave da fila é `(instante, tipo, sequência de inserção)`. Tipos: 0 para conclusões de E/S/paginação; 1 para chegadas; 2 para término de unidade de CPU; 3 para fim de troca. Todos os eventos do mesmo instante são processados antes de iniciar outra troca. Empates do mesmo tipo seguem inserção. Processos empatados chegam na ordem do arquivo; threads, na ordem de declaração.

O escalonador usa a sequência de entrada em PRONTO; prioridade acrescenta antes dela o valor numérico da prioridade. O nome completo é o último desempate. Assim, no limite do quantum, uma chegada simultânea entra na fila antes da thread preemptada. Não há aleatoriedade; a semente é aceita e registrada para tornar a configuração explícita, mas não altera resultados.

## CPU e contexto

A CPU executa uma unidade por evento. Essa granularidade permite preempção em qualquer unidade do surto sem depender de relógio real. Durante intervalos ociosos, o clock salta diretamente ao próximo evento. Uma troca também é um intervalo agendado; eventos externos podem ocorrer durante ela. A thread é selecionada ao fim da troca, considerando as chegadas nesse intervalo.

Todo despacho cobra `--troca`, inclusive o primeiro e o redispatch da única thread pronta. Conta-se essa operação como uma troca mesmo com custo zero. FCFS/prioridades cedem a CPU apenas ao bloquear ou finalizar. RR também cede quando o quantum se esgota. Se término/bloqueio coincidir com fim do quantum, término/bloqueio prevalece.

`ThreadSimulada` é o TCB. O contador de programa seleciona a instrução, `restanteSurto` preserva uma CPU parcialmente executada e o acumulador recebe resultados. `CPU` incrementa o acumulador; `MEM` recebe endereço físico; `ABRIR`, descritor; `LER`, comprimento; `DESEMPILHAR`, o topo da pilha. `EMPILHAR`/`DESEMPILHAR` demonstram a pilha lógica. A caixa de entrada recebe resultados assíncronos sem polling.

`Processo` é o PCB: mantém prioridade, chegada, espaço de endereçamento, threads, tabela local de arquivos e cópia do último contexto atualizado. `ultimaThread` identifica o dono desse retrato; a execução sempre usa o TCB correto. As cópias de PC/registrador são para inspeção do PCB, não um segundo contexto executável. Em falta de página, a conclusão do paginador atualiza esse retrato com o resultado da referência.

## Estados

As transições de thread aceitas são: NOVO → PRONTO; PRONTO → EXECUTANDO; EXECUTANDO → PRONTO/BLOQUEADO/FINALIZADO; BLOQUEADO → PRONTO. `mudarEstado` valida a aresta e uma causa não vazia, atualiza métricas e registra a mudança.

O estado do processo é agregado: EXECUTANDO se uma thread executa; senão PRONTO se existe uma pronta; senão BLOQUEADO enquanto houver thread não finalizada ou E/S pendente; FINALIZADO quando todas terminaram e não há E/S pendente. Portanto a matriz de estados agregados difere da de uma thread: por exemplo, um processo pode ir de BLOQUEADO a FINALIZADO quando sua última requisição assíncrona termina, se todas as threads já finalizaram. Não se aplica ao PCB a matriz do TCB. Toda alteração agregada também registra causa.

Se a última instrução bloquear, a conclusão retorna a thread a PRONTO e um último despacho realiza o encerramento, sem CPU útil adicional. O despacho cobra o custo configurado. Isso mantém uma única regra de encerramento no núcleo, visível no log.

## Paginação

Cada processo possui número de páginas e tabela esparsa: entrada ausente equivale a página não presente. Uma entrada instanciada contém presença e moldura; página expulsa fica com presença falsa e moldura −1. O deslocamento é o resto da divisão pelo tamanho de página; o endereço físico é `moldura * tamanhoPagina + deslocamento`.

A falta bloqueia a thread e entra na fila FCFS do paginador. O serviço possui duração fixa e é serial. Ao concluir, escolhe a primeira moldura livre ou expulsa a mais antiga da fila FIFO global. Acertos não reordenam FIFO. A página só ocupa moldura ao concluir, evitando reservas que pudessem ser expulsas durante atendimento. Se duas threads já solicitaram a mesma página, a segunda conserva seu serviço agendado, mas reutiliza a página caso ainda presente; não duplica a moldura.

A referência faltosa é resolvida pelo próprio evento de conclusão; não é reemitida nem contada duas vezes ao retomar a CPU. O PC já aponta à próxima instrução e o endereço físico vai ao acumulador. Logo, uma expulsão posterior antes do despacho não desfaz uma referência já concluída. Referências = acertos + faltas. O processo libera molduras ao encerrar, removendo-as também da fila FIFO.

## E/S

Há duas instâncias de `Dispositivo`, uma de bloco e uma de caractere, com filas independentes. A cabeça da fila está em serviço; fila vazia significa LIVRE. O tempo ocupado é a soma dos serviços concluídos. A simulação esvazia todas as filas, então não restam serviços parcialmente contabilizados.

`B` remove a thread da CPU; a interrupção a devolve à fila. `NB` permite continuar; a interrupção entrega `dispositivo:id:OK` à caixa de entrada do TCB e registra a entrega. Não há espera ativa nem instrução de consulta repetida. Um processo cujas threads já terminaram aguarda suas requisições assíncronas antes da liberação final. Essa escolha torna a entrega e a contabilização completas; o tempo de retorno do processo pode superar o das threads.

## Arquivos

`No` representa arquivo ou diretório. O diretório contém filhos ordenados por nome. Cada nó guarda nome, tipo, permissões, criação/modificação, tamanho e primeiro bloco. O tamanho de diretório é zero: somente conteúdo de arquivo consome blocos neste modelo.

Os blocos contêm texto e índice do próximo bloco; −1 termina a cadeia. O volume tem 128 blocos de 16 unidades UTF-16. Acesso sequencial exige percorrer a cadeia; essa é uma limitação da alocação encadeada. As escritas recompõem a cadeia de modo didático, verificando capacidade antes da alteração para que falhas não destruam conteúdo anterior.

Cada `ABRIR` cria uma entrada global com nó, modo e cursor, e um descritor local, crescente a partir de 3, que aponta à entrada. Threads do mesmo processo compartilham descritores; processos diferentes têm espaços independentes. Fechar remove ambas as associações. Abrir novamente começa no deslocamento zero e **não trunca**. Escrever sobrescreve a partir do cursor, preservando eventual sufixo, e avança; não há `seek`.

Para remover um arquivo, ele deve estar fechado em todos os processos; diretórios precisam estar vazios; raiz não é removível. Criar/remover exige `w` no pai. Atravessar diretórios exige `r`; listar exige diretório legível; abrir verifica os modos contra permissões do arquivo. Não há usuários ou bits de execução. O encerramento do processo fecha automaticamente descritores remanescentes, com log.

## Clareza e encapsulamento

Somente `Main` é API pública de execução. As classes do modelo são internas ao pacote, com identidade/referências estáveis `final`. Estado de processo e thread, filas, blocos e tabelas internas de arquivos são privados. Campos de contexto mutáveis têm visibilidade de pacote para permitir colaboração direta entre núcleo e mecanismos sem dezenas de getters triviais. Não se permite acesso externo pelo pacote público.

A política de CPU está concentrada em `Escalonador`, cuja instância é configurável. Uma interface com uma única implementação não foi adicionada. FIFO fica em `Memoria`; FCFS de E/S em `Dispositivo`. Não há herança artificial, frameworks, Lombok, DTOs duplicados ou camadas de serviço/repositório.

## Apresentação gráfica

`InterfaceGrafica` chama o fluxo compartilhado `Main.executar` e apresenta resultados. `LinhaTempo` interpreta eventos concluídos, sem alterar o clock. SwingWorker isola o trabalho da thread de apresentação. Consulte `interface-grafica.md`.

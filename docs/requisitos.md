# Rastreabilidade dos requisitos

Esta tabela relaciona os pontos principais do enunciado com as partes do projeto que os atendem. Ela serve como checklist técnico; a validação final deve ser feita executando o projeto em um ambiente limpo.

| Requisito | Implementação / evidência | Situação |
|---|---|---|
| Clock lógico e eventos discretos | `Simulador` e `Evento`; o clock avança pelo próximo evento | Implementado |
| Separação por módulos | Escalonador, memória, E/S e arquivos em classes próprias | Implementado |
| Processo e PCB | `Processo` mantém estado, prioridade, contexto, threads, páginas e descritores | Implementado |
| Thread e TCB | `ThreadSimulada` mantém estado, PC, registradores simulados, pilha e métricas | Implementado |
| Estados e transições | NOVO, PRONTO, EXECUTANDO, BLOQUEADO e FINALIZADO com registro no log | Implementado |
| FCFS | Política disponível no `Escalonador` | Implementado |
| Round Robin | Política com quantum configurável | Implementado |
| Prioridade | Política não preemptiva; menor valor numérico tem maior prioridade | Implementado |
| Custo de troca de contexto | Parâmetro de execução, com tempo separado da CPU útil | Implementado |
| Paginação | Tabela de páginas por processo e molduras de tamanho fixo | Implementado |
| Substituição FIFO | Fila FIFO global para escolha de vítima | Implementado |
| Falta de página | Bloqueio da thread, atendimento e retorno a PRONTO | Implementado |
| Dispositivo de bloco e caractere | Duas instâncias de `Dispositivo` com filas independentes | Implementado |
| E/S bloqueante | Thread sai da CPU e retorna após interrupção simulada | Implementado |
| E/S não bloqueante | Resultado entregue posteriormente à caixa de entrada | Implementado |
| Sistema de arquivos hierárquico | Raiz, diretórios, arquivos e blocos encadeados | Implementado |
| Operações de arquivo | Criar, abrir, ler, escrever, fechar, remover e listar | Implementado |
| Descritores por processo | Tabela local associada à tabela global de arquivos abertos | Implementado |
| Carga externa | Arquivos de carga lidos sem recompilar o programa | Implementado |
| Cargas CPU, E/S e mista | Arquivos na pasta `cargas` | Implementado |
| Log de eventos | `eventos.log` com clock, tipo, objeto e descrição | Implementado |
| Métricas | Retorno, espera, resposta, CPU, dispositivos, throughput, faltas e trocas | Implementado |
| Três experimentos | Comparação de políticas, quantum e quantidade de molduras | Implementado |
| Testes automatizados | `Testes.java`, `TestesInterface.java` e `TestesDoom.java` | Implementado |
| Execução reproduzível | Ordem determinística; semente registrada na configuração | Implementado |
| Interface por linha de comando | `so.Main` e scripts de execução | Implementado |
| Interface gráfica opcional | Swing, sem substituir CLI, cargas e logs | Implementado |
| Repositório GitHub | Deve permanecer acessível ao professor e com histórico real do grupo | Conferir antes da entrega |
| Execução em ambiente limpo | Repetir geração do pacote, testes e uma carga completa | Conferir antes da entrega |

## Decisões que precisam ser explicadas na apresentação

Alguns detalhes são escolhas do projeto e não regras universais de sistemas operacionais. Vale deixá-los claros durante a avaliação:

- prioridade é não preemptiva;
- o menor número representa maior prioridade;
- cada despacho contabiliza o custo configurado de contexto;
- o paginador atende faltas de forma serial;
- o algoritmo de substituição é FIFO;
- o sistema de arquivos fica apenas em memória;
- operações de arquivo não são convertidas automaticamente em requisições ao dispositivo de disco;
- a interface gráfica é apenas uma camada de apresentação;
- o DOOM é iniciado pelo sistema hospedeiro e não pela CPU simulada.

## Conferência final

Antes de entregar, o grupo deve verificar principalmente os itens da seção 16 do enunciado: execução a partir do README, carga externa, clock e fila de eventos, três políticas, paginação FIFO, dispositivos, arquivos, logs, métricas, testes e coerência entre código, diagrama e relatório.

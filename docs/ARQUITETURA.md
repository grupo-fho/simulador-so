# Arquitetura e classes

```mermaid
classDiagram
    class Simulador {
        +clock: int
        +executar()
        +metricas()
        -mudar_estado()
        -despachar()
        -executar_instrucoes()
    }
    class Configuracao
    class AgendaEventos {
        +agendar()
        +proximo()
    }
    class Evento
    class RegistroEventos
    class Processo
    class PCB
    class Thread
    class TCB
    class EspacoEnderecamento
    class EntradaPagina
    class Escalonador
    class PoliticaEscalonamento {
        <<abstract>>
        +selecionar()
    }
    class FCFS
    class RoundRobin
    class Prioridades
    class GerenciadorMemoria
    class Dispositivo
    class Requisicao
    class SistemaArquivos
    class FCB
    class Arquivo
    class Diretorio
    class Bloco
    class ArquivoAberto
    Simulador *-- Configuracao
    Simulador *-- AgendaEventos
    AgendaEventos *-- Evento
    Simulador *-- RegistroEventos
    Simulador *-- Processo
    Processo *-- PCB
    Processo *-- Thread
    Thread *-- TCB
    TCB --> PCB : processo_id
    PCB *-- EspacoEnderecamento
    EspacoEnderecamento *-- EntradaPagina
    Simulador *-- Escalonador
    Escalonador o-- Thread : fila_prontos
    Escalonador *-- PoliticaEscalonamento
    PoliticaEscalonamento <|-- FCFS
    FCFS <|-- RoundRobin
    PoliticaEscalonamento <|-- Prioridades
    Simulador *-- GerenciadorMemoria
    GerenciadorMemoria --> EspacoEnderecamento
    Simulador *-- Dispositivo
    Dispositivo *-- Requisicao
    Requisicao --> Thread
    Dispositivo --> AgendaEventos
    Simulador *-- SistemaArquivos
    SistemaArquivos *-- Diretorio : raiz
    Diretorio o-- Diretorio : filhos
    Diretorio o-- Arquivo : filhos
    Diretorio *-- FCB
    Arquivo *-- FCB
    SistemaArquivos *-- Bloco
    Bloco --> Bloco : proximo
    SistemaArquivos *-- ArquivoAberto : tabela_global
    ArquivoAberto --> Arquivo
    PCB --> ArquivoAberto : descritor_local para id_global
```

O núcleo compõe os mecanismos e fornece o tempo comum. O gerenciador de memória decide presença/tradução/vítima; o núcleo agenda a latência e muda estados. Dispositivos agendam as próprias conclusões e notificam o núcleo por callback. O sistema de arquivos recebe explicitamente o clock em cada chamada e não depende da interface.

O escalonador mantém uma única fila; a política seleciona um índice. Round Robin herda a seleção FCFS porque usa a mesma ordem, enquanto o núcleo aplica seu limite temporal. Prioridades substitui apenas o critério de seleção. A herança fica limitada às políticas; as entidades do SO usam composição.

TCB guarda contexto privado; PCB guarda recursos compartilhados. O processo deriva seu estado dos TCBs: quando uma thread bloqueia, ele pode continuar pronto se outra thread estiver na fila. A máquina de transições explicitamente validada é a da unidade escalonável, a thread.

```mermaid
stateDiagram-v2
    [*] --> Novo
    Novo --> Pronto: admissão
    Pronto --> Executando: despacho
    Executando --> Pronto: fim do quantum
    Executando --> Bloqueado: E/S ou falta de página
    Bloqueado --> Pronto: interrupção ou página carregada
    Executando --> Finalizado: fim das instruções
    Finalizado --> [*]
```

Não há relógio real ou concorrência hospedeira. Cada intervalo de CPU agenda sua conclusão; chegadas e interrupções no meio desse intervalo são processadas sem alterar a propriedade da CPU. O simulador só despacha uma nova thread quando a anterior libera a CPU.

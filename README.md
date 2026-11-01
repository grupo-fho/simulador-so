# Simulador didático de sistemas operacionais

Python orientado a objetos, executado pelo terminal, com relógio lógico e eventos discretos. Implementa processos, threads, PCB/TCB, FCFS, Round Robin, prioridades, paginação FIFO, dispositivos e sistema de arquivos hierárquico.

**Os dados simulados ficam somente na memória da aplicação.** O disco virtual é um dicionário de blocos; `/aula/notas` é um caminho virtual, sem relação com `C:`. Logs e métricas ficam em objetos e são exibidos no terminal. Ao encerrar, o estado é descartado. O programa não gera `.txt`, bancos de dados nem arquivos de log. `main.py` desativa a geração de bytecode `__pycache__`.

As cargas JSON incluídas são entradas estáticas da aplicação, atendendo ao requisito de carga externa do PDF. São apenas lidas. Também é possível fornecer JSON pela entrada padrão, sem criar um arquivo de carga. O PDF do relatório e os documentos deste repositório são materiais da entrega, não dados gravados pelo simulador.

## Executar

Requisito: **Python 3.10 ou superior**. Usa somente a biblioteca padrão; não precisa instalar pacotes. Validado com Python 3.14 no Windows.

Na pasta do projeto:

```powershell
python main.py
python main.py --ajuda
python main.py --cenario arquivos
python main.py --cenario verificacao --algoritmo rr --quantum 2
python main.py --carga cargas/mista.json --algoritmo prioridades --sem-log
python main.py --cenario memoria --numero-molduras 2 --tempo-falta-pagina 3
python main.py --cenario es --tempo-disco 6 --tempo-terminal 2
python main.py --cenario cpu --quantum 4 --custo-contexto 1
python main.py --experimentos
```

Cada execução termina automaticamente. `--sem-log` exibe configuração e métricas; `--json` apresenta a saída estruturada **no terminal**, sem salvar nada. Sem `--sem-log`, cada linha informa clock, evento, objeto e descrição. A configuração aparece no início.

Entrada padrão, no PowerShell:

```powershell
'{"processos":[{"id":"P1","chegada":0,"prioridade":1,"threads":[{"id":"T1","instrucoes":[{"op":"cpu","duracao":3}]}]}]}' | python main.py --carga -
```

## Parâmetros

| Parâmetro | Padrão | Significado |
|---|---:|---|
| `--cenario` | mista | cpu, es, mista, verificacao, memoria ou arquivos |
| `--carga` | — | Caminho de JSON externo, ou `-` para entrada padrão; exclusivo com cenario |
| `--algoritmo` | rr | fcfs, rr ou prioridades |
| `--quantum` | 2 | Unidades de CPU por rodada do RR |
| `--custo-contexto` | 0 | Custo por despacho, incluindo o primeiro |
| `--tamanho-pagina` | 16 | Bytes por página/moldura |
| `--numero-molduras` | 3 | Quantidade de molduras físicas |
| `--tempo-falta-pagina` | 3 | Serviço do paginador por carregamento |
| `--tempo-disco` | 4 | Serviço padrão de E/S do dispositivo de bloco |
| `--tempo-terminal` | 2 | Serviço padrão do dispositivo de caractere |
| `--tamanho-bloco` | 16 | Bytes por bloco do disco virtual |
| `--numero-blocos` | 64 | Capacidade do disco virtual |
| `--semente` | 42 | Registrada; não há geração aleatória nas cargas fornecidas |
| `--sem-log` | desligado | Exibe somente configuração e métricas |
| `--json` | desligado | Saída JSON no terminal |
| `--experimentos` | desligado | Executa as sete rodadas das três comparações |

Tempos e capacidades devem ser inteiros positivos; custo de contexto pode ser zero. Configuração ou carga inválida produz uma mensagem em stderr e código de saída 2. Execução concluída retorna 0. Uma chamada inválida ao sistema de arquivos é um erro do programa **simulado**: gera `ERRO_ARQUIVO`, preenche o registrador `erro_arquivo` e permite à thread continuar; uma chamada bem-sucedida limpa esse registrador.

Nos experimentos, a comparação de quantum fixa custo de contexto em 1 e valores de quantum em 1 e 4; a comparação de memória fixa as molduras em 2 e 4. A comparação de políticas usa a carga mista, a de quantum usa a carga de CPU e a de molduras usa a carga de memória. Os demais parâmetros seguem a configuração de execução. `--experimentos` usa esses cenários predefinidos, independentemente de `--carga` ou `--cenario`.

## Formato da carga

A raiz deve conter somente `processos`, uma lista não vazia. IDs de processos são únicos; IDs de threads são únicos dentro do processo. IDs não podem conter `/`. Chegada e prioridade são inteiros não negativos; **menor prioridade numérica significa atendimento preferencial**. `memoria` é o tamanho do espaço lógico em bytes, com padrão 256. As threads chegam junto com o processo.

```json
{
  "processos": [
    {
      "id": "P1",
      "chegada": 0,
      "prioridade": 1,
      "memoria": 128,
      "threads": [
        {
          "id": "T1",
          "instrucoes": [
            {"op": "memoria", "endereco": 0},
            {"op": "cpu", "duracao": 3},
            {"op": "es", "dispositivo": "disco", "bloqueante": true},
            {"op": "cpu", "duracao": 1}
          ]
        }
      ]
    }
  ]
}
```

Campos desconhecidos são rejeitados para detectar erros de digitação. Instruções são executadas em ordem, até o fim da lista; não é necessário um comando de encerramento.

| `op` | Campos | Efeito |
|---|---|---|
| `cpu` | `duracao` | Consome CPU útil; pode sofrer preempção RR |
| `memoria` | `endereco` | Traduz endereço; bloqueia se a página não estiver residente |
| `es` | `dispositivo`, `bloqueante` opcional, `duracao` opcional | Dispositivo disco/terminal; bloqueante padrão true; duração substitui o padrão do dispositivo |
| `criar_diretorio` | `caminho`, `permissoes` opcional | Cria diretório em pai existente |
| `criar_arquivo` | `caminho`, `permissoes` opcional | Cria arquivo vazio |
| `abrir` | `caminho`, `modo` opcional, `salvar_em` opcional | Modo padrão r; guarda o descritor no registrador indicado, padrão fd |
| `escrever` | `fd`, `texto` | Escreve texto codificado em UTF-8 |
| `ler` | `fd`, `quantidade` opcional | Lê bytes; omitir quantidade lê até o fim; resultado em ultima_leitura |
| `fechar` | `fd` | Remove a associação local/global da abertura |
| `listar` | `caminho` | Retorna metadados em ultima_listagem e registra a listagem |
| `remover` | `caminho` | Remove arquivo fechado ou diretório vazio |

`fd` pode ser um inteiro ou o nome do registrador que recebeu um descritor. Exemplo: abrir com `"salvar_em":"notas"` e depois escrever com `"fd":"notas"`. Registradores são locais à thread; descritores pertencem ao processo e podem ser compartilhados usando o mesmo número. Depois de fechar, o número pode ser reutilizado por uma abertura posterior.

Permissões: `r`, `w`, `rw` ou string vazia; padrão `rw`. Em diretórios, r permite percorrer/listar e w permite alterar entradas. Caminhos são absolutos; `.` e `..`, barras repetidas e barra final são rejeitados (exceto `/`). Não há usuários ou grupos.

Modos: r lê; w escreve e trunca na abertura; rw lê/escreve preservando o conteúdo; a escreve sempre ao final. Cada abertura tem cursor independente em **bytes**. A leitura pode dividir um caractere UTF-8: os bytes originais continuam no modelo, enquanto a exibição do registrador usa substituição para sequências parciais. Arquivos abertos não podem ser removidos. Falta de espaço cancela a escrita sem alterar conteúdo ou cursor.

## Convenções do modelo

- Uma CPU lógica; processos e threads são objetos, sem threads reais, `sleep` ou relógio físico.
- Eventos em heap por instante e sequência de inserção. Todas as ações agendadas para o instante atual são processadas antes de selecionar uma nova thread.
- Admissões ordenadas por chegada e ID de processo; threads por ID. Empates de FCFS/RR seguem a entrada na fila. Prioridades usa o menor número e, no empate, a ordem da fila.
- Prioridades é **não preemptiva**. Uma chegada de maior prioridade não interrompe a thread em execução.
- O quantum mede somente CPU útil e acumula entre instruções CPU adjacentes. Bloqueio ou novo despacho reinicia a rodada. Ao acabar um surto exatamente no quantum, instruções instantâneas de controle podem concluir/bloquear; haverá preempção se houver mais CPU a executar.
- Cada despacho conta como uma troca de contexto, inclusive o inicial, a retomada após bloqueio e a reeleição da mesma thread. Durante o custo, a thread já foi retirada da fila de prontos; esse tempo é sobrecarga, não espera de fila nem CPU útil. O TCB preserva PC, registradores e CPU restante. A pilha lógica marca execução e chamadas de arquivo; o PCB guarda o último PC e os registradores observados ao avançar uma instrução, além dos recursos compartilhados.
- Apenas `cpu` consome CPU útil. Referências de memória, chamadas de arquivos e submissão de E/S são operações instantâneas; os tempos de atendimento e bloqueio são explícitos. Arquivos não submetem automaticamente E/S ao disco; use `es` na carga para modelar essa latência.
- O paginador tem uma fila FCFS própria e serviço configurável, independente do dispositivo disco. FIFO é global entre processos. A moldura/vítima é escolhida **na conclusão** do carregamento. Faltas simultâneas da mesma página compartilham atendimento. Cada acesso não residente conta uma falta; carregamentos podem ser menos numerosos que faltas. A referência pendente se completa no carregamento, sem uma nova contagem ou tentativa artificial no despacho seguinte.
- E/S não bloqueante retorna de imediato e entrega a conclusão por interrupção, lista `notificacoes` e registrador `es_N` do TCB, inclusive se a thread já terminou. Não há consulta repetitiva. O simulador drena as solicitações pendentes antes de terminar.
- O estado do processo é agregado: executando se alguma thread executa, pronto se alguma está pronta, bloqueado se só restam bloqueadas/finalizadas, finalizado quando todas terminam. Todos os estados e causas aparecem no log. No fim do processo, fecha descritores e libera molduras; o arquivo virtual permanece até remoção explícita ou encerramento da aplicação.
- Blocos de tamanho fixo são ligados por `proximo`; o FCB aponta para o primeiro. Diretórios guardam entradas em memória e não consomem os blocos destinados ao conteúdo dos arquivos.

## Métricas

Retorno = finalização − chegada. Espera da thread = soma dos intervalos na fila de prontos. Resposta = primeira utilização de CPU útil − chegada; n/a quando não há instrução CPU. No processo, resposta considera a primeira CPU de qualquer thread; `espera_threads` é a soma das esperas das threads, podendo superar o tempo de vida do processo.

O horizonte global vai do clock 0 até o último evento, incluindo chegada tardia e E/S assíncrona pendente. Utilização da CPU = CPU útil/horizonte; sobrecarga = custo acumulado/horizonte; ociosidade = horizonte − CPU útil − sobrecarga. Utilização por dispositivo = tempo de atendimento/horizonte (fila não conta como atendimento). Throughput = processos concluídos/horizonte. Taxa de faltas = referências não residentes/referências totais. Para horizonte zero, as razões são apresentadas como zero.

## Testes e conferência manual

```powershell
python -B -m unittest discover -s testes -v
```

Resultado esperado: **32 testes, OK**. Cobrem estados, filas, quantum, métricas, tradução, FIFO, faltas compartilhadas, E/S bloqueante e assíncrona, arquivos, validação, determinismo e integração. Um teste bloqueia `open` e `io.open` durante as operações virtuais para comprovar que o núcleo não usa arquivos hospedeiros.

`verificacao.json` contém P1/T1 com CPU 3 e P2/T1 com CPU 2, chegada 0. Sem custo de contexto:

| Política | Ordem dos intervalos | Retorno P1/P2 | Espera P1/P2 | Resposta P1/P2 |
|---|---|---|---|---|
| FCFS | P1 [0,3), P2 [3,5) | 3 / 5 | 0 / 3 | 0 / 3 |
| RR q=2 | P1 [0,2), P2 [2,4), P1 [4,5) | 5 / 4 | 2 / 2 | 0 / 2 |
| Prioridades | P2 [0,2), P1 [2,5) | 5 / 2 | 2 / 0 | 2 / 0 |

As três têm CPU útil 5, horizonte 5, utilização 100% e throughput 0,4. A carga `arquivos` provoca intencionalmente **três erros**: leitura de descritor fechado, escrita sem permissão e remoção de caminho inexistente. Eles demonstram a validação e aparecem no log.

## Organização e apresentação

| Local | Responsabilidade |
|---|---|
| `main.py` | Entrada e proteção contra bytecode em disco |
| `simulador/modelo.py` | Entidades, PCB, TCB, estados, espaço lógico |
| `simulador/eventos.py` | Clock agendado por eventos e registros em memória |
| `simulador/escalonamento.py` | Políticas substituíveis e fila de prontos |
| `simulador/memoria.py` | Tabelas de páginas, tradução e FIFO |
| `simulador/entrada_saida.py` | Requisições, filas e interrupções |
| `simulador/arquivos.py` | FCB, diretórios, blocos e tabelas de aberturas |
| `simulador/nucleo.py` | Coordenação, transições e métricas |
| `simulador/carga.py` | Leitura e validação de cenários |
| `simulador/configuracao.py` | Parâmetros e validação |
| `simulador/terminal.py` | CLI, apresentação e experimentos |
| `cargas/` | Seis cenários JSON editáveis sem mudar classes |
| `testes/` | Testes unitários e de integração |
| `docs/` | Diagrama, guia e relatório técnico em Markdown e PDF |

Veja [o guia de apresentação](docs/APRESENTACAO.md), [o diagrama](docs/ARQUITETURA.md) e [o relatório técnico](docs/RELATORIO.md). O PDF está em `docs/RELATORIO.pdf`.


Limites deliberados: sem multiprocessamento, TLB, LRU, envelhecimento, SSTF, cache, journaling, persistência física ou interface gráfica. Estes recursos são opcionais no enunciado. Filas e blocos priorizam clareza didática; cargas muito grandes manterão muitos eventos de log em RAM.


# Simulador didático de sistemas operacionais

Projeto Java 21, com CLI e interface gráfica, baseado nos requisitos do **Trabalho SO.pdf**. Implementa clock lógico, eventos discretos, processos/threads, FCFS, Round Robin, prioridades não preemptivas, paginação FIFO, E/S e arquivos hierárquicos.

## Interface gráfica

Desktop Frutiger Aero: céu azul, colinas verdes, bolhas, ícones brilhantes,

janelas claras, barra de tarefas e menu de aplicações.

Configura CPU/memória/E/S, executa cargas e mostra métricas, processos, threads,

linha do tempo e eventos. Usa Swing, sem bibliotecas externas.

Para abrir no Windows com JDK 21 selecionado:

```powershell

powershell -ExecutionPolicy Bypass -File scripts/abrir-interface.ps1

```

Consulte `docs/interface-grafica.md`. Regere o pacote portátil para obter a GUI;

o executável antigo continua sendo a versão anterior.

## DOOM clássico

O atalho **DOOM clássico** inicia Chocolate Doom em tela cheia no SO

hospedeiro. Prepare o motor e seu IWAD uma vez, usando `scripts/preparar-doom.ps1`;

o gerador inclui esses arquivos no pacote portátil. Veja **[docs/doom.md](docs/doom.md)**.

O ZIP de fontes contém o lançador, não o motor nem o WAD. A partida não utiliza

CPU/memória simuladas e não altera métricas acadêmicas.

## Requisitos e instalação

### Entrega portátil ao professor (Windows)

O professor não precisa instalar Java **quando receber o ZIP portátil gerado**.

Ele extrai a pasta inteira e abre `SimuladorSO.exe` ou `INICIAR.bat`: a interface

gráfica configura e executa as cargas usando o runtime incluído.

A CLI está em `SimuladorCLI.exe`, e o menu textual em `MENU-CLI.bat`. A CLI continua

aceitando arquivos externos e todos os parâmetros originais.

Para gerar esse ZIP no seu Windows, com OpenJDK 21 instalado, execute na raiz:

```powershell

powershell -ExecutionPolicy Bypass -File scripts/gerar-executavel.ps1 -Jdk "C:\Java\jdk-21"

```

Ajuste `-Jdk` para a pasta real. O script compila, testa, cria os executáveis com

`jpackage`, testa novamente usando o Java embutido e gera

`dist/<identificador>/SimuladorSO-Windows.zip`. Envie **esse ZIP completo**, não

somente o `.exe` nem o ZIP de fontes. Não é necessário instalar WiX para este

formato `app-image`; não se está criando um instalador MSI.

**Estado atual (19/09/2026):** o ZIP Windows/JDK 21 foi gerado neste ambiente.

Passaram 191 verificações do núcleo, o teste offscreen da interface e 10

verificações do lançador DOOM. O executável empacotado concluiu a carga mista

nas três políticas. O Chocolate Doom com `doom2.wad` permaneceu em execução

por cinco segundos no teste de inicialização. Vídeo, teclado e áudio ainda

precisam de conferência manual antes da entrega.

Consulte `docs/entrega-portatil.md`. As instruções abaixo são para desenvolvimento

e compilação do código-fonte, não para o professor que recebe o pacote pronto.

- JDK 21 ou superior com módulo `jdk.compiler`; não basta uma distribuição reduzida contendo apenas o runtime.

- Nenhuma biblioteca Java externa, Maven, Gradle, rede ou instalação de dependências é necessária.

- Python 3 é opcional, usado apenas para automatizar os experimentos com a biblioteca padrão. Cada cenário também pode ser executado diretamente em Java.

- Extraia o ZIP e abra um terminal na pasta `simulador-so`.

- Confira se `java -version` mostra 21 ou superior. O executável `java` selecionado pelo `PATH` deve pertencer ao JDK desejado; apenas instalar outro JDK não altera necessariamente essa seleção.

- Versão de compilação: `--release 21`, sem recursos preview. Classes compiladas para 21 não executam no Java 17.

**Validação da migração:** a suíte e o pacote Windows foram executados com

OpenJDK 21. Os sete experimentos também foram reproduzidos com JDK 21 em

19/09/2026; os resultados e sua interpretação estão no

[guia de apresentação](docs/guia-apresentacao.md) e em

[experimentos-apresentacao.csv](docs/experimentos-apresentacao.csv).

O relatório PDF preserva o registro histórico anterior.

### Windows / PowerShell

```powershell

java -version

powershell -ExecutionPolicy Bypass -File scripts/compilar.ps1

java -cp build/classes so.Main --carga cargas/mista.txt --politica RR --quantum 3 --saida resultados/minha-execucao

powershell -ExecutionPolicy Bypass -File scripts/testar.ps1

```

O `Bypass` vale somente para o processo iniciado. Não altera a política permanente do Windows. Alternativamente compile diretamente, sem scripts PowerShell:

```powershell

New-Item -ItemType Directory -Force build/classes

$fontes = @((Get-ChildItem src/so/*.java).FullName) + @((Get-ChildItem test/so/*.java).FullName)

java -m jdk.compiler/com.sun.tools.javac.Main --release 21 -encoding UTF-8 -Xlint:all,-output-file-clash -d build/classes $fontes

java -cp build/classes so.Testes

```

### Linux / macOS

```sh

java -version

sh scripts/compilar.sh

java -cp build/classes so.Main --carga cargas/mista.txt --politica RR --quantum 3 --saida resultados/minha-execucao

sh scripts/testar.sh

```

Os scripts chamam o compilador pelo módulo padrão do JDK, equivalente a `javac`. O resultado esperado do teste é **`OK: 191 verificações aprovadas.`** e código de saída zero. Em seguida, `TestesInterface` confere a execução gráfica offscreen e a equivalência de métricas com a CLI. As verificações lançam `AssertionError` diretamente; não dependem de `-ea`. Os scripts devem ser executados a partir de uma cópia com as cargas originais.

## Parâmetros

```sh

java -cp build/classes so.Main --ajuda

```

| Opção | Padrão | Significado |

|---|---|---|

| `--carga` | obrigatório | Arquivo textual UTF-8 |

| `--politica` | `FCFS` | `FCFS`, `RR` ou `PRIORIDADE` |

| `--quantum` | 3 | Unidades úteis por despacho no RR |

| `--troca` | 1 | Custo de cada despacho, inclusive inicial e redispatch da mesma thread |

| `--pagina` | 16 | Unidades de endereço por página/moldura |

| `--molduras` | 4 | Quantidade de molduras físicas |

| `--falta` | 5 | Serviço do paginador, serial, por falta |

| `--disco` | 4 | Serviço de cada requisição do dispositivo de bloco |

| `--terminal` | 2 | Serviço de cada requisição do dispositivo de caractere |

| `--semente` | 42 | Inteiro de 64 bits registrado; a implementação não faz sorteios |

| `--saida` | `resultados/execucao` | Diretório novo ou vazio para os resultados |

Parâmetros numéricos, salvo semente, devem estar entre 1 e 1.000.000; troca aceita zero. Prioridades e chegadas da carga aceitam zero. Identificadores de processos são únicos; identificadores de threads são únicos dentro de seu processo. Menor número de prioridade vence.

A carga e os parâmetros são validados antes de simular e antes de gravar resultados. Erros retornam código 2 com mensagem objetiva. Diretórios não vazios são recusados para evitar sobrescrever experimentos. Não há interação durante a execução. Um erro do sistema hospedeiro durante a gravação pode deixar saída parcial; o erro é informado e a pasta deve ser revisada antes de nova execução.

## Formato da carga

```text

# processo: identificador, chegada, prioridade, quantidade de páginas lógicas

PROCESSO P1 0 2 4

THREAD T1

CPU 3

MEM 17

IO disco B

CPU 2

FIM_THREAD

THREAD T2

IO terminal NB

CPU 4

FIM_THREAD

FIM_PROCESSO

```

O arquivo aceita linhas vazias e comentários de linha inteira iniciados por `#`. Comandos e opções distinguem maiúsculas/minúsculas. Texto entre aspas pode conter espaços, mas não há escapes nem comentários ao fim da linha. Todas as threads chegam com seu processo, na ordem declarada. Um processo deve ter pelo menos uma thread e cada thread ao menos uma instrução.

| Instrução | Exemplo | Efeito |

|---|---|---|

| `CPU duração` | `CPU 5` | Executa 5 unidades úteis; preserva restante do surto nas preempções |

| `MEM endereço` | `MEM 17` | Referência lógica; registra tradução ou bloqueia por falta |

| `IO dispositivo modo` | `IO disco B` | `disco` ou `terminal`; `B` bloqueante, `NB` assíncrona |

| `MKDIR caminho permissões` | `MKDIR /dados rw` | Cria diretório |

| `CRIAR caminho permissões` | `CRIAR /dados/a.txt rw` | Cria arquivo vazio |

| `ABRIR caminho modo` | `ABRIR /dados/a.txt rw` | Retorna descritor no acumulador e no log |

| `ESCREVER descritor texto` | `ESCREVER 3 "Ola mundo"` | Escreve na posição atual e avança o cursor |

| `LER descritor quantidade` | `LER 3 10` | Lê até a quantidade; texto no log; comprimento no acumulador |

| `FECHAR descritor` | `FECHAR 3` | Remove associação local/global |

| `REMOVER caminho` | `REMOVER /dados/a.txt` | Remove arquivo fechado ou diretório vazio |

| `LISTAR caminho` | `LISTAR /dados` | Lista conteúdo e metadados, em ordem alfabética |

| `EMPILHAR inteiro` | `EMPILHAR 7` | Empilha inteiro positivo no TCB |

| `DESEMPILHAR` | `DESEMPILHAR` | Retira topo para o acumulador; valida pilha vazia |

Cada instrução, exceto `CPU N`, custa uma unidade útil da CPU para emitir a operação. `CPU N` custa N. Serviços de E/S e paginação ocorrem depois da emissão, em paralelo lógico com a CPU. O quantum conta todas essas unidades úteis.

Endereços devem pertencer a `[0, paginas * tamanhoPagina)`. Endereços e números da carga são inteiros até 1.000.000. Os caminhos são absolutos, sem `.` ou `..`, sem barras duplicadas; componentes usam letras ASCII, números, ponto, hífen ou sublinhado. Permissões são `r`, `w`, `rw` ou `-`; abertura usa `r`, `w` ou `rw`. O formato deliberadamente pequeno não aceita JSON, referências a variáveis ou ramificações.

## Cargas incluídas

| Arquivo | Objetivo |

|---|---|

| `cargas/cpu.txt` | Predomínio de CPU |

| `cargas/io.txt` | Predomínio de E/S com os dois dispositivos |

| `cargas/mista.txt` | CPU, memória, E/S e múltiplas threads |

| `cargas/memoria.txt` | Pressão de memória: páginas 0,1,2 repetidas |

| `cargas/verificacao.txt` | Duas threads; cálculo manual de métricas |

| `cargas/threads-io.txt` | Outra thread progride durante bloqueio |

| `cargas/arquivos.txt` | Todas as operações de arquivos e pilha |

| `cargas/erros-arquivos.txt` | Quatro falhas operacionais esperadas, registradas no log |

## Resultados e métricas

Cada execução escreve:

- `eventos.log`: clock, tipo, objeto e descrição; inicia com toda a configuração.

- `resumo.csv`: tempo total, CPU útil, sobrecarga, ociosidade, utilizações, throughput, trocas, referências/acertos/faltas e erros de operações.

- `threads.csv`: chegada, fim, retorno, espera, resposta e CPU por thread.

- `processos.csv`: chegada, fim, retorno, **soma das esperas das threads** e primeira resposta do processo.

Retorno = fim − chegada; espera = soma de intervalos PRONTO, incluindo troca de contexto; resposta = início da primeira instrução − chegada. Utilizações e taxa de faltas são proporções entre 0 e 1, não porcentagens. Throughput = processos concluídos / clock final. O intervalo observado começa em zero, incluindo ociosidade antes da primeira chegada. A utilização dos dispositivos usa o mesmo intervalo. A espera agregada de um processo pode exceder seu retorno, pois threads podem esperar simultaneamente.

### Conferência manual

```sh

java -cp build/classes so.Main --carga cargas/verificacao.txt --politica FCFS --troca 0 --saida resultados/manual-fcfs

java -cp build/classes so.Main --carga cargas/verificacao.txt --politica RR --quantum 2 --troca 0 --saida resultados/manual-rr

```

| Política | Thread | Fim | Retorno | Espera | Resposta |

|---|---|---:|---:|---:|---:|

| FCFS | P1/T1 | 3 | 3 | 0 | 0 |

| FCFS | P2/T1 | 5 | 4 | 2 | 2 |

| RR, q=2 | P1/T1 | 5 | 5 | 2 | 0 |

| RR, q=2 | P2/T1 | 4 | 3 | 1 | 1 |

Ambas usam 5 unidades úteis, utilização 1 e throughput 0,4. FCFS tem dois despachos; RR tem três e uma preempção. Com troca zero, esses despachos não consomem tempo.

## Experimentos reproduzíveis

```sh

python3 scripts/experimentos.py resultados/nova-comparacao

```

No Windows, use `python` ou `py -3` em vez de `python3`. Escolha uma pasta inexistente. O script executa sete cenários: três políticas na carga mista, RR com quantum 1 e 6, e memória com 2 e 3 molduras. Todos usam troca 1, página 16, falta 5, disco 4, terminal 2 e semente 42. Os cenários de políticas usam quantum 3 e quatro molduras. Os cenários de quantum usam quatro molduras. Os cenários de memória usam FCFS e quantum 3 (sem efeito no FCFS).

Os logs/CSVs da execução de referência no JDK 17, quando disponíveis, ficam em `resultados/experimentos`. Resultados são ignorados pelo Git; o relatório registra os números necessários à comparação. A saída `comparacoes.csv` agrega as métricas e médias de cada cenário. Consulte `docs/relatorio-tecnico.pdf` para interpretação. O PDF registra uma migração antiga para JDK 27; o alvo desta entrega é JDK 21.

Sem Python, execute os comandos Java com a mesma matriz de parâmetros; por exemplo:

```sh

java -cp build/classes so.Main --carga cargas/memoria.txt --politica FCFS --troca 1 --pagina 16 --molduras 2 --falta 5 --disco 4 --terminal 2 --semente 42 --saida resultados/memoria-duas

```

### Regenerar o relatório (opcional)

O PDF pronto acompanha o projeto. Para regenerá-lo após reproduzir os experimentos no diretório padrão, instale `reportlab` no ambiente Python e execute `python3 scripts/gerar_relatorio.py`. Essa biblioteca serve somente à documentação. O gerador incorpora DejaVu Sans se disponível em `/usr/share/fonts/truetype/dejavu` ou na pasta indicada pela variável `SO_FONT_DIR`; sem essas fontes usa Helvetica padrão.

## Arquitetura e manutenção

Código em `src/so`, testes em `test/so`. Consulte `docs/arquitetura.md`, `docs/diagrama-classes.mmd`, `docs/requisitos.md` e `docs/relatorio-tecnico.pdf`.

- `InterfaceGrafica`, `LinhaTempo`: desktop Swing e projeção visual dos eventos.

- `Main`, `Configuracao`, `Carga`: CLI, validação e entrada.

- `Simulador`, `Evento`: clock, fila de eventos, execução e registro.

- `Processo`, `ThreadSimulada`, `Estado`, `Instrucao`: PCB, TCB e programa.

- `Escalonador`: seleção de threads; altere aqui uma política de CPU.

- `Memoria`: tradução e FIFO; altere aqui substituição e atendimento.

- `Dispositivo`: fila FCFS e interrupções de cada dispositivo.

- `Arquivos`: nós, blocos encadeados e descritores.

- `Metricas`: CSV e cálculos uniformes.

Não existem threads reais, `sleep`, banco de dados, drivers, rede nem comunicação externa no núcleo. A GUI usa SwingWorker somente para separar apresentação e execução; isso não muda os processos simulados. As únicas leituras/escritas reais são carga e resultados em `Main`/`Carga`.

## Decisões e limitações

Prioridades são não preemptivas, sem envelhecimento. FIFO é global. O paginador tem fila e serviço próprios, separados do disco genérico. Arquivos ficam em memória e suas operações são síncronas de uma unidade: não geram requisições no dispositivo `disco`. A integração com processos se dá pelas tabelas e descritores; o disco é exercitado por `IO disco`.

O volume tem 128 blocos de 16 unidades UTF-16, encadeados; o tamanho lógico não representa bytes UTF-8. Não há persistência entre execuções, permissões por usuário, links simbólicos, cache, TLB ou journaling. Essas extensões não são exigidas. Erros de operações simuladas são registrados e a thread prossegue, semelhante ao retorno de erro de uma chamada; erros de formato/CLI impedem a execução.

## Fontes, autoria e entrega acadêmica

Fonte de requisitos: `Trabalho SO.pdf`, Prof. Maurício Acconcia Dias. Os algoritmos foram implementados a partir das definições do enunciado; não há biblioteca de núcleo de SO.

A criação/publicação do repositório GitHub não foi realizada. O pacote está pronto para ser colocado em um repositório do grupo. `docs/progresso.md` é um registro técnico desta implementação. Antes da entrega, registre a participação real, confirme o acesso do professor e repita os comandos de compilação, teste e execução em seu ambiente.
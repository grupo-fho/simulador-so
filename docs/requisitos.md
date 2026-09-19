# Rastreabilidade do enunciado

| Seção do PDF | Implementação / evidência |
|---|---|
| 2: clock e eventos discretos | `Simulador`, `Evento`; sem relógio real ou threads do hospedeiro |
| 3: módulos e orientação a objetos | `docs/arquitetura.md`, diagrama de classes e classes do pacote `so` |
| 4.1: PCB e estados | `Processo`; estado agregado, contexto, páginas, threads e descritores |
| 4.2: TCB e múltiplas threads | `ThreadSimulada`; `cargas/threads-io.txt`, teste `testarIo` |
| 4.3: políticas e contexto | `Escalonador`, núcleo; testes de filas, quantum, prioridades e troca |
| 5: paginação e FIFO | `Memoria`; `testarMemoria`; experimento molduras 2/3 |
| 6: bloco/carácter, B/NB, interrupção | Duas instâncias de `Dispositivo`; caixas de entrada e testes de E/S |
| 7: hierarquia e FCB | `Arquivos.No`, blocos encadeados, permissões, tabelas local/global; `testarArquivos` |
| 8: CLI e carga externa | `Main`, `Configuracao`, `Carga`; cargas CPU, E/S e mista |
| 9: log e métricas | `eventos.log`, CSVs de `Metricas`; script de sete cenários |
| 9: três experimentos | `docs/relatorio-tecnico.pdf`: políticas, quantum, memória |
| 10: testes automáticos | `test/so/Testes.java`; 191 verificações unitárias e de integração |
| 10: verificação manual | `cargas/verificacao.txt`, tabela no README |
| 11: documentação e relatório | README, arquitetura, diagrama e PDF |
| 11: GitHub e histórico | Pendente de publicação pelo grupo; não foi criado histórico artificial |
| 11: entrega intermediária | Registro técnico em `docs/progresso.md`; não representa submissão passada |
| 14: bibliotecas | Java padrão; Python padrão opcional para experimentos; sem núcleo externo |
| 15: fontes e apoio | Declaração de assistência no README e no relatório |
| 16: execução limpa | ZIP gerado e suíte executada com OpenJDK 21 no Windows em 19/09/2026; conferir interação manual no destino |

## Ajustes em relação às regras de código do Markdown

Não havia código anterior para refatorar: esta é uma implementação nova. Os nomes foram escolhidos em português e pelo domínio, com loops explícitos, estruturas pequenas e responsabilidades concentradas. `record` é usado apenas para dados/configuração/eventos. Nenhuma classe ou abstração antiga foi removida. Não houve API, integração ou regra preexistente a preservar.

Pontos de atenção são as convenções do modelo, documentadas na arquitetura: cobrança inicial de contexto, prioridade não preemptiva, atendimento serial de faltas, arquivos síncronos e drenagem de E/S pendente. Essas decisões são explícitas porque o PDF não fixa uma única alternativa para todos esses detalhes.

## Interface gráfica adicional

`InterfaceGrafica` e `LinhaTempo` acrescentam desktop Swing, configuração e visualização de resultados. A CLI e as cargas externas permanecem disponíveis; consulte `interface-grafica.md` para alcance e validação.

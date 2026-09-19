# Registro técnico de progresso

Nota de 19/09/2026: esta entrega usa OpenJDK 21. O ZIP portátil com Chocolate
Doom e DOOM II foi gerado no Windows e passou na suíte automática. A seção
histórica sobre JDK 27 abaixo não descreve o alvo atual.

Implementação produzida nesta sessão, em 16/09/2026. Este documento não simula uma entrega intermediária realizada em data anterior.

- Núcleo, processos/TCBs e três políticas: implementados.
- Memória, E/S e arquivos: implementados e integrados.
- Testes, cargas, logs, métricas, documentação e três experimentos: concluídos.
- Estimativa do escopo funcional obrigatório implementado: 100%, considerando as convenções documentadas e verificações incluídas. Isso não equivale a certificação de ausência de bugs ou de aprovação acadêmica.
- Etapas administrativas: publicação no GitHub, acesso do professor, identificação dos integrantes e registro de participação real permanecem sob responsabilidade do grupo.
- Limitações conhecidas: simulação de uma CPU; FIFO global; prioridades sem envelhecimento; volume volátil; ausência de integração das operações de arquivos com a fila do disco; nenhuma extensão opcional reivindicada.
- Plano para a entrega: revisar cada módulo, repetir execução limpa no computador do grupo, discutir as decisões do modelo, publicar o repositório e conferir a reprodução dos experimentos.

Não foi fabricado histórico de commits ou percentual de participação dos integrantes.

## Migração para JDK 27

A compilação agora usa `--release 27`. Ajuda CLI, README e relatório foram atualizados. A lógica de simulação foi preservada. As verificações e resultados acima são evidência da execução anterior em JDK 17. Compilar, executar a suíte e repetir os experimentos com JDK 27 permanece pendente de um ambiente com essa versão; consulte `migracao-jdk27.md`.

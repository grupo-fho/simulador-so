# Migração para JDK 27

## Alterações

- Scripts de compilação Linux/macOS e Windows usam `--release 27` em fontes e testes.
- Exemplos de compilação manual, requisito do JDK e ajuda da CLI foram atualizados.
- Relatório técnico e seu gerador identificam Java 27 como alvo de compilação.
- Nenhum recurso preview foi introduzido. A lógica de eventos, as políticas e os cálculos permanecem iguais.

O OpenJDK informa disponibilidade geral do JDK 27 em 15/09/2026:
https://openjdk.org/projects/jdk/27/
Downloads oficiais: https://jdk.java.net/27/

## O que foi e não foi verificado

As 191 verificações e os sete experimentos presentes no pacote foram executados originalmente com JDK 17. A mudança de alvo não torna essa evidência uma validação de Java 27. Neste ambiente, somente JDK 17 está disponível; a tentativa de acesso ao download do JDK 27 terminou em timeout do proxy. Não foram alegados testes ou compilação bem-sucedidos com JDK 27.

O pacote não contém classes compiladas anteriormente. Após selecionar o JDK 27 no PATH, compile novamente, execute a suíte e reproduza os experimentos. Os resultados anteriores servem como referência de comportamento.

## Verificação no Windows

Abra o PowerShell na raiz do projeto:

```powershell
java -version
powershell -ExecutionPolicy Bypass -File scripts/testar.ps1
java -cp build/classes so.Main --carga cargas/mista.txt --politica RR --quantum 3 --saida resultados/jdk27
py -3 scripts/experimentos.py resultados/experimentos-jdk27
```

`java -version` deve mostrar 27 ou superior. Resultado esperado da suíte: `OK: 191 verificações aprovadas.`. Compare `resultados/experimentos-jdk27/comparacoes.csv` com `resultados/experimentos/comparacoes.csv`. Use outro nome de saída se a pasta já existir.

## Verificação no Linux/macOS

```sh
java -version
sh scripts/testar.sh
java -cp build/classes so.Main --carga cargas/mista.txt --politica RR --quantum 3 --saida resultados/jdk27
python3 scripts/experimentos.py resultados/experimentos-jdk27
```

Não altere `--release 27` para contornar um compilador antigo: selecione o JDK correto. `--release` define o alvo da compilação, mas não instala nem seleciona automaticamente outra distribuição de Java.

# Interface gráfica

A interface foi feita em Swing e funciona como uma camada sobre o mesmo núcleo usado pela CLI. Não existe uma segunda implementação da simulação: tanto a interface quanto a linha de comando chamam `Main.executar`.

## Objetivo

A GUI foi incluída para facilitar a demonstração do trabalho. Ela permite configurar a simulação sem digitar todos os argumentos e apresenta os resultados de forma mais visual. A entrada por arquivo, o log textual e os CSVs continuam disponíveis, como exigido pelo projeto.

## Execução durante o desenvolvimento

No Windows, com JDK 21 configurado:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\abrir-interface.ps1
```

## Uso

Na tela de configuração é possível:

1. escolher uma carga de trabalho;
2. selecionar FCFS, RR ou PRIORIDADE;
3. informar quantum, custo de troca de contexto, tamanho de página e quantidade de molduras;
4. configurar os tempos dos dispositivos;
5. informar a semente e a pasta de resultados;
6. iniciar a simulação.

Depois da execução, o monitor apresenta o resumo das métricas, os processos, as threads, a linha do tempo da CPU e o log de eventos.

![Tela de configuração](interface-configuracao.png)

![Tela de resultados](interface-resultados.png)

## Pacote para Windows

O gerador de distribuição cria uma pasta pronta para execução. O pacote pode conter:

- `SimuladorSO.exe`: abre a interface gráfica;
- `SimuladorCLI.exe`: executa a versão por argumentos;
- `Testar.exe`: executa a suíte compilada;
- `INICIAR.bat`: atalho para a interface;
- `MENU-CLI.bat`: menu textual alternativo.

Para gerar novamente o pacote com o JDK 21 instalado em `C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot`:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\gerar-executavel.ps1 -Jdk "C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot"
```

É importante usar uma pasta de saída nova ou substituir conscientemente uma distribuição antiga. Um pacote já gerado não recebe automaticamente alterações posteriores feitas no código-fonte.

## Linha do tempo

`LinhaTempo` transforma os eventos do log em uma representação gráfica da CPU e das trocas de contexto. Ela é uma visualização do resultado final, não uma animação em tempo real da simulação.

Em cargas maiores, vários eventos ficam comprimidos na escala. Quando for necessário conferir o instante exato de uma operação, o log continua sendo a fonte principal.

## Validação

A versão atual foi executada com Java 21 e a suíte registrou 191 verificações aprovadas. Os testes da interface conferem a abertura dos componentes principais, a execução pelo mesmo fluxo da CLI e a geração dos arquivos de resultado.

A interação visual final deve ser conferida no Windows antes da entrega, principalmente depois de regenerar o executável.

## Central de jogos

O atalho de DOOM abre `PainelDoom`. A classe `Doom` valida os arquivos e usa `ProcessBuilder` para iniciar o Chocolate Doom. O jogo roda como processo real do sistema hospedeiro e não participa das métricas da simulação. Os detalhes estão em `doom.md`.

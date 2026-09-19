# DOOM clássico no desktop Aero

A interface inicia o **Chocolate Doom**, um motor real compatível com os dados
originais do DOOM. Não é uma imitação do jogo. O motor roda em tela cheia no
Windows/Linux, fora da JVM; não está embutido na janela interna Swing.
O simulador acadêmico não é um sistema inicializável nem um emulador x86.
O DOOM não é executado pelo escalonador didático e não altera suas métricas.

## Preparação única no seu Windows

1. Baixe Chocolate Doom para Windows na página oficial:
   https://www.chocolate-doom.org/wiki/index.php/Downloads
2. Extraia o ZIP inteiro. Localize a pasta com `chocolate-doom.exe`, as DLLs
   e os arquivos de licença. Não copie apenas o executável.
3. Localize o IWAD de uma cópia sua do DOOM: `DOOM.WAD` ou `DOOM2.WAD`.
   `DOOM1.WAD`, da edição shareware original, também é aceito.
   Um mod `PWAD` não substitui os dados base. Os dados do jogo não estão neste ZIP.
4. Na raiz deste projeto, prepare os arquivos (ajuste ambos os caminhos):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/preparar-doom.ps1 -PastaMotor "C:\Jogos\ChocolateDoom" -Wad "C:\Jogos\DOOM\DOOM.WAD"
```

O script copia a distribuição completa do motor para `jogos/doom` e preserva
o nome do IWAD como `doom.wad`, `doom1.wad` ou `doom2.wad` em minúsculas.
Os arquivos existentes do motor não são substituídos
silenciosamente. Ele valida o cabeçalho e os limites do diretório do IWAD;
a compatibilidade do conteúdo é verificada pelo próprio Chocolate Doom.

5. Abra a interface, clique em **DOOM clássico** e em **Jogar DOOM**.
   Os caminhos preparados são preenchidos automaticamente. Para uma execução
   avulsa, os botões **Procurar** permitem escolher arquivos em outras pastas;
   essa escolha é válida durante a sessão e não copia dependências para a entrega.
6. Gere novamente o executável:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/gerar-executavel.ps1 -Jdk "C:\Program Files\Java\jdk-21"
```

O gerador inclui `jogos` inteira, com DLLs e licenças. Sem motor/WAD, ele avisa
que o pacote tem somente o lançador. O professor não precisa repetir a configuração
quando você entrega o pacote completo já preparado. Inclua apenas dados cuja
licença permita a distribuição ao destinatário; ter o motor livre não torna o
IWAD comercial livre. Para dados comerciais, o destinatário deve usar sua cópia.

## Jogar e conferir

- Abra o `SimuladorSO.exe` da pasta **nova** dentro de `dist`.
- Clique em **DOOM clássico → Jogar DOOM**. Comece uma partida e confira vídeo,
  teclado e áudio. O jogo abre em tela cheia. Em monitores largos, o motor pode
  manter barras laterais para preservar a proporção clássica da imagem.
- Controles padrão: setas para mover/girar, Ctrl para atirar, Espaço para usar,
  Esc para o menu. Opções podem ser ajustadas pelo utilitário do Chocolate Doom.
- Encerre pelo menu do jogo. O botão Jogar é reativado quando o processo termina.
- Fechar a janela interna do lançador não encerra o jogo; ele continua em sua
  própria janela. Sair do simulador também não mata a partida externa.
- Saves, configurações e logs ficam em `%USERPROFILE%\.simulador-so\doom`.
  O botão **Abrir log do jogo** ajuda a identificar DLLs ausentes e WAD incompatível.
- Os campos são argumentos separados de `ProcessBuilder`; caminhos com espaços
  não passam por shell e não precisam de aspas digitadas nos campos.

## Validação desta entrega

Em 19/09/2026, OpenJDK 21 no Windows aprovou 191 verificações do núcleo,
a comparação GUI/CLI e 10 verificações do lançador. Chocolate Doom 3.1.1
iniciou com `doom2.wad` e permaneceu em execução por cinco segundos. O teste
não confirma renderização, áudio ou jogabilidade; confira uma partida na
interface antes de entregar.

## Fontes e dependências

- Chocolate Doom (dependência opcional externa, GPL v2):
  https://www.chocolate-doom.org/wiki/index.php/Downloads
- Argumentos `-iwad`, `-fullscreen`, `-savedir`, `-config`,
  `-extraconfig`: https://www.chocolate-doom.org/wiki/index.php/Command_line_arguments
- Preserve os avisos/licenças do motor e cumpra seus termos de redistribuição,
  incluindo a disponibilização do código-fonte correspondente quando aplicável.
- O tema é desenhado com Java2D/Nimbus. Não usa imagens externas.

## Configuracao local de 16/09/2026

Chocolate Doom 3.1.1 e suas DLLs foram extraidos em `jogos/doom`.
O pacote `24timebom.zip` foi extraido em `jogos/doom/mods`, preservando
`24TIMEBOM.TXT`. Ele e um PWAD com 24 mapas, nao um jogo base.
O autor exige o `DOOM.WAD` completo; o shareware nao serve para esses mapas.

A central possui um terceiro campo opcional para o PWAD, enviado ao motor
com `-file`. O campo começa vazio. IWAD e PWAD são validados separadamente.

O IWAD `doom2.wad` foi preparado localmente em 19/09/2026. Para trocar o IWAD,
execute:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/preparar-doom.ps1 -Wad "C:\Jogos\DOOM\DOOM.WAD"
```

Ou selecione seu IWAD no segundo campo da central. Para inclui-lo em um
novo pacote portatil, prepare o arquivo e execute o gerador novamente.
O 24TIMEBOM não é selecionado automaticamente, pois exige DOOM registrado e
não é compatível com o DOOM II preparado. Deixe o terceiro campo vazio para
jogar DOOM II. Para usar o mod, escolha um `DOOM.WAD` completo e selecione
`jogos/doom/mods/24TIMEBOM.WAD` manualmente.

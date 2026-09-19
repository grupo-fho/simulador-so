# Correção da interface — JDK 21

O pacote anterior inspecionado no Windows continha so/Main.class e não continha
so/InterfaceGrafica.class. Alterar o caminho do Java não acrescenta classes ao JAR.
Esta distribuição de correção reúne os fontes completos da interface Frutiger Aero,
o núcleo e um gerador para JDK 21. Extraia em uma PASTA NOVA; não reutilize dist antiga.

## Gerar no Windows

Na pasta deste arquivo:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\gerar-executavel.ps1 -Jdk "C:\Program Files\Eclipse Adoptium\jdk-21.0.11.10-hotspot"
```

Ajuste somente a pasta do JDK se ela for diferente. O script confere os fontes,
compila com --release 21, executa testes, verifica as classes no JAR, testa a GUI
diretamente do JAR e testa a interface sem janela com o runtime empacotado.
Também confere que SimuladorSO.cfg aponta para so.InterfaceGrafica.

A pasta NOVA de saída abre no Explorador ao final. Abra SimuladorSO.exe nela.
DIAGNOSTICO.bat abre a mesma interface com console e mantém erros visíveis.
Envie ao professor o ZIP completo gerado dentro de dist, não este ZIP de fontes.

## Abrir sem gerar EXE

Com o JDK 21 no PATH:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\abrir-interface.ps1
```

## Escopo e validação

Tema Aero e lançador DOOM incluídos. Nesta cópia local, Chocolate Doom 3.1.1
e `doom2.wad` estão preparados em `jogos/doom`; veja `docs/doom.md`.
O ZIP portátil gerado inclui esses arquivos. Confirme que pode distribuir o
IWAD ao destinatário antes de compartilhar o pacote.

A validação local de 19/09/2026 usou OpenJDK 21 no Windows: 191 verificações
do núcleo, 10 do lançador e comparação GUI/CLI, inclusive no executável
portátil. A inicialização do motor com DOOM II foi confirmada por cinco
segundos; vídeo e áudio devem ser conferidos manualmente. Documentos históricos
e o relatório anterior podem mencionar JDK 27. Esta entrega usa JDK 21.

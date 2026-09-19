# Entrega portátil para Windows

## Objetivo

Eliminar a necessidade de o professor instalar JDK, selecionar versões no PATH,
compilar ou instalar bibliotecas. O ZIP gerado contém três executáveis nativos de
entrada (GUI, CLI e testes), o JAR, um runtime Java reduzido, cargas, documentação
e um menu de console. Não é uma compilação para código de máquina independente
da JVM: a JVM necessária viaja junto, isolada do Java instalado no computador.

## Gerar uma vez, na máquina do grupo

Requisitos do responsável pela geração: Windows e OpenJDK 21 completo, na mesma
arquitetura do computador do professor. Nenhum download é realizado pelo script.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/gerar-executavel.ps1 -Jdk "C:\Java\jdk-21"
```

O argumento é a pasta que contém `bin`, não a pasta `bin` em si. A seleção usa
caminhos explícitos para todas as ferramentas, sem alterar o PATH do computador.
Sem `-Jdk`, usa JAVA_HOME; se ausente, tenta o caminho de java.exe no PATH.

Cada geração usa diretórios novos em build e dist; não apaga resultados antigos.
O script compila fontes e testes em uma pasta limpa, executa a suíte, cria o JAR
e chama `jpackage --type app-image --add-modules java.base,java.desktop`.
A imagem contém apenas o runtime necessário; o destinatário não precisa do JDK.
O segundo launcher, `Testar.exe`, inicia a suíte já compilada.

Antes de compactar, o script executa Testar.exe e a carga mista nas três políticas
com o runtime embarcado. Falhas interrompem a geração. O registro VALIDACAO.txt
e as saídas de validação acompanham o ZIP. A integridade estrutural do ZIP é
conferida após a compactação. Uma falha nessa última verificação pode deixar um
ZIP incompleto: só distribua quando o script informar sucesso.

## O que enviar

Envie `dist/<identificador>/SimuladorSO-Windows.zip` ao professor. Mantenha o
código-fonte e histórico real no GitHub, como pede o enunciado. O executável é
uma comodidade adicional e não substitui a entrega das fontes e documentação.

O professor extrai tudo em uma pasta gravável e abre SimuladorSO.exe ou INICIAR.bat. O desktop gráfico está descrito em interface-grafica.md. MENU-CLI.bat oferece o menu textual anterior. O menu permite
demonstrar FCFS/RR/prioridades, operações de arquivos, executar a suíte, abrir
resultados ou consultar a ajuda. Cada demonstração cria uma pasta diferente.
O menu é opcional: SimuladorCLI.exe aceita os mesmos argumentos da CLI original.

Não envie o .exe isolado: ele depende das pastas app e runtime. Não execute
diretamente da visualização interna do ZIP. Não precisa de administrador para
executar em uma pasta do usuário. Políticas institucionais podem restringir
execução; não desative proteções para contorná-las.

## Verificação antes da entrega

1. Gere o ZIP no Windows com OpenJDK 21 e aguarde o sucesso de todas as etapas.
2. Extraia em outra pasta, de preferência com espaços no nome.
3. Abra SimuladorSO.exe e confira seleção de carga, execução, tabelas, eventos e linha do tempo. Confira também o MENU-CLI.bat.
4. Repita a demonstração e confirme que os resultados anteriores não mudaram.
5. Confirme que a suíte imprime `OK: 191 verificações aprovadas.`.
6. Execute em uma conta/máquina sem Java no PATH, para verificar a independência.
7. Entregue o ZIP completo e o link do repositório.

## Limites da validação nesta sessão

Em 19/09/2026, o gerador foi executado no Windows com OpenJDK 21. O ZIP passou
na conferência estrutural, a suíte passou antes e depois do empacotamento, e
a CLI empacotada concluiu a carga mista em FCFS, RR e PRIORIDADE. A GUI foi
testada sem janela; confira a interação nativa e uma partida de DOOM II no
computador de destino. O PDF mantém o registro histórico dos experimentos
com JDK 17.

Referência da ferramenta: https://openjdk.org/jeps/392
Manual: https://docs.oracle.com/en/java/javase/21/docs/specs/man/jpackage.html

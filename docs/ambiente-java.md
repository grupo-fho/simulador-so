# Ambiente Java do projeto

## Versão adotada

A versão atual do projeto usa **Java 21** como alvo de compilação. Os scripts foram ajustados para `--release 21`, sem uso de recursos preview.

A distribuição utilizada nos testes recentes foi o Eclipse Temurin 21.0.12.101.

Para conferir o Java ativo no Windows:

```powershell
java -version; javac -version; where.exe java; where.exe javac
```

## Testes

Na raiz do projeto:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\testar.ps1
```

O resultado esperado da versão validada é:

```text
OK: 191 verificações aprovadas.
```

## Executar uma carga pela CLI

Exemplo com Round Robin:

```powershell
java -cp build\classes so.Main --carga cargas\mista.txt --politica RR --quantum 3 --saida resultados\teste-rr
```

## Gerar o pacote portátil

No ambiente em que o JDK 21 está instalado em `C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot`:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\gerar-executavel.ps1 -Jdk "C:\Program Files\Eclipse Adoptium\jdk-21.0.12.101-hotspot"
```

O pacote gerado leva um runtime próprio. Assim, a máquina que recebe a distribuição não precisa ter outro Java configurado no `PATH` para abrir os executáveis empacotados.

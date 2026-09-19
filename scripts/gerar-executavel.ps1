param([string]$Jdk = $env:JAVA_HOME)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$raiz = Split-Path $PSScriptRoot -Parent
$pastaAnterior = Get-Location

function Confirmar-JarGrafico([string]$ArquivoJar) {
    $conteudoJar = & "$Jdk\bin\jar.exe" --list --file $ArquivoJar
    if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel inspecionar o JAR: $ArquivoJar" }
    foreach ($classe in @('so/InterfaceGrafica.class', 'so/TemaAero.class', 'so/Main.class', 'so/TestesInterface.class', 'so/Doom.class', 'so/PainelDoom.class')) {
        if ($conteudoJar -notcontains $classe) {
            throw "Pacote incompleto: falta $classe em $ArquivoJar. Nenhum ZIP deve ser entregue."
        }
    }
}

try {
    if ($env:OS -ne 'Windows_NT') {
        throw 'Gere o executavel de Windows no Windows, usando um OpenJDK 21 completo.'
    }
    if ([string]::IsNullOrWhiteSpace($Jdk)) {
        $javaNoPath = (Get-Command java.exe -ErrorAction Stop).Source
        # java.home resolve o JDK real mesmo quando java.exe e um atalho no PATH.
        $preferenciaAnterior = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            $configuracaoJava = & $javaNoPath -XshowSettings:properties -version 2>&1
            $codigoJava = $LASTEXITCODE
        } finally { $ErrorActionPreference = $preferenciaAnterior }
        if ($codigoJava -ne 0) { throw 'Nao foi possivel consultar o Java no PATH. Informe -Jdk com a pasta do JDK 21.' }
        foreach ($linha in $configuracaoJava) {
            if ("$linha" -match '^\s*java\.home\s*=\s*(.+)$') {
                $Jdk = $Matches[1].Trim()
                break
            }
        }
        if ([string]::IsNullOrWhiteSpace($Jdk)) { throw 'JDK nao localizado. Informe -Jdk com a pasta do JDK 21.' }
    }
    $Jdk = (Resolve-Path -LiteralPath $Jdk).Path
    foreach ($ferramenta in @('java.exe', 'javac.exe', 'jar.exe', 'jpackage.exe', 'jlink.exe')) {
        if (-not (Test-Path -LiteralPath (Join-Path $Jdk "bin\$ferramenta"))) {
            throw "JDK incompleto ou caminho incorreto: falta bin\$ferramenta em $Jdk. Use -Jdk com a pasta do OpenJDK 21."
        }
    }
    $versao = & "$Jdk\bin\javac.exe" --version
    if ($LASTEXITCODE -ne 0 -or "$versao" -notmatch '^javac 21(?:[. +\-]|$)') {
        throw "Este pacote exige OpenJDK 21. Compilador selecionado: $versao"
    }
    Set-Location -LiteralPath $raiz
    if (-not (Test-Path -LiteralPath 'src/so/InterfaceGrafica.java')) {
        throw 'Esta pasta nao contem a interface grafica. Use este script dentro de scripts da versao grafica do projeto.'
    }
    $identificador = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
    $trabalho = Join-Path $raiz "build\pacote-$identificador"
    $classes = Join-Path $trabalho 'classes'
    $entrada = Join-Path $trabalho 'entrada'
    $destino = Join-Path $raiz "dist\$identificador"
    New-Item -ItemType Directory -Path $classes, $entrada, $destino | Out-Null

    Write-Host '1/5 Compilando fontes e testes com OpenJDK 21...'
    $fontes = @((Get-ChildItem src/so/*.java).FullName) + @((Get-ChildItem test/so/*.java).FullName)
    & "$Jdk\bin\javac.exe" --release 21 -encoding UTF-8 -Xlint:all,-output-file-clash -d $classes $fontes
    if ($LASTEXITCODE -ne 0) { throw 'A compilacao falhou; nenhum ZIP de entrega foi criado.' }
    & "$Jdk\bin\java.exe" -cp $classes so.Testes
    if ($LASTEXITCODE -ne 0) { throw 'Os testes falharam; nenhum ZIP de entrega foi criado.' }
    & "$Jdk\bin\java.exe" '-Djava.awt.headless=true' -cp $classes so.TestesInterface
    if ($LASTEXITCODE -ne 0) { throw 'Os testes da interface falharam.' }

    if (Test-Path -LiteralPath 'test/so/TestesDoom.java') {
        & "$Jdk\bin\java.exe" -cp $classes so.TestesDoom
        if ($LASTEXITCODE -ne 0) { throw 'Os testes do lancador DOOM falharam.' }
    }

    Write-Host '2/5 Criando JAR e imagem com Java embutido...'
    & "$Jdk\bin\jar.exe" --create --file "$entrada\simulador-so.jar" --main-class so.Main -C $classes .
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar o JAR.' }
    Confirmar-JarGrafico (Join-Path $entrada 'simulador-so.jar')
    & "$Jdk\bin\java.exe" '-Djava.awt.headless=true' -cp "$entrada\simulador-so.jar" so.TestesInterface
    if ($LASTEXITCODE -ne 0) { throw 'A interface falhou ao executar diretamente do JAR.' }
    $lancadorTestes = Join-Path $trabalho 'testes.properties'
    @('main-jar=simulador-so.jar', 'main-class=so.Testes', 'win-console=true') |
        Set-Content -LiteralPath $lancadorTestes -Encoding ASCII
    $lancadorCli = Join-Path $trabalho 'cli.properties'
    @('main-jar=simulador-so.jar', 'main-class=so.Main', 'win-console=true') |
        Set-Content -LiteralPath $lancadorCli -Encoding ASCII
    $lancadorDiagnostico = Join-Path $trabalho 'diagnostico.properties'
    @('main-jar=simulador-so.jar', 'main-class=so.InterfaceGrafica', 'win-console=true') |
        Set-Content -LiteralPath $lancadorDiagnostico -Encoding ASCII
    $lancadorInterface = Join-Path $trabalho 'verificar-interface.properties'
    @('main-jar=simulador-so.jar', 'main-class=so.TestesInterface', 'win-console=true', 'java-options=-Djava.awt.headless=true') |
        Set-Content -LiteralPath $lancadorInterface -Encoding ASCII
    & "$Jdk\bin\jpackage.exe" --type app-image --name SimuladorSO --app-version 1.1.0 `
        --input $entrada --main-jar simulador-so.jar --main-class so.InterfaceGrafica `
        --add-modules 'java.base,java.desktop' --add-launcher "Testar=$lancadorTestes" `
        --add-launcher "SimuladorCLI=$lancadorCli" --add-launcher "Diagnostico=$lancadorDiagnostico" `
        --add-launcher "VerificarInterface=$lancadorInterface" --dest $destino
    if ($LASTEXITCODE -ne 0) { throw 'Falha no jpackage; nenhum ZIP de entrega foi criado.' }

    $imagem = Join-Path $destino 'SimuladorSO'
    Confirmar-JarGrafico (Join-Path $imagem 'app\simulador-so.jar')
    $configuracaoGrafica = Get-Content -LiteralPath (Join-Path $imagem 'app\SimuladorSO.cfg') -Raw
    if ($configuracaoGrafica -notmatch '(?m)^app.mainclass=so\.InterfaceGrafica\s*$') {
        throw 'O executavel SimuladorSO nao aponta para a interface grafica.'
    }
    Copy-Item -LiteralPath (Join-Path $raiz 'cargas') -Destination $imagem -Recurse
    Copy-Item -LiteralPath (Join-Path $raiz 'docs') -Destination $imagem -Recurse
    if (Test-Path -LiteralPath (Join-Path $raiz 'jogos')) {
        Copy-Item -LiteralPath (Join-Path $raiz 'jogos') -Destination $imagem -Recurse
    }
    $motorDoom = Join-Path $imagem 'jogos\doom\chocolate-doom.exe'
    $iwads = @(@('doom2.wad', 'doom.wad', 'doom1.wad') | Where-Object {
        Test-Path -LiteralPath (Join-Path $imagem "jogos\doom\$_") -PathType Leaf
    })
    if ((Test-Path -LiteralPath $motorDoom) -and $iwads.Count -gt 0) {
        Write-Host 'DOOM incluido. Confira a abertura e uma partida no pacote final antes de entregar.'
    } else {
        Write-Warning 'DOOM incompleto: falta o motor ou IWAD base. Os arquivos locais foram incluidos. Leia docs/doom.md.'
    }
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'windows\INICIAR.bat') -Destination $imagem
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'windows\MENU-CLI.bat') -Destination $imagem
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'windows\LEIA-ME.txt') -Destination $imagem

    Write-Host '3/5 Testando os executaveis com o Java embutido...'
    Set-Location -LiteralPath $imagem
    & '.\VerificarInterface.exe'
    if ($LASTEXITCODE -ne 0) { throw 'A interface falhou com o Java embutido. Nenhum ZIP de entrega foi criado.' }
    & '.\Testar.exe'
    if ($LASTEXITCODE -ne 0) { throw 'A suite falhou no executavel empacotado.' }
    foreach ($politica in @('FCFS', 'RR', 'PRIORIDADE')) {
        & '.\SimuladorCLI.exe' --carga cargas/mista.txt --politica $politica --quantum 3 --saida "validacao/$politica"
        if ($LASTEXITCODE -ne 0) { throw "A validacao do executavel falhou na politica $politica." }
    }
    @("Compilador: $versao", "JDK: $Jdk", "Data: $(Get-Date -Format o)",
        'Suite de testes: aprovada antes e depois do empacotamento.',
        'Carga mista: FCFS, RR e PRIORIDADE concluidas pelo executavel.',
        'O runtime embarcado foi gerado pelo jpackage; nao requer Java no PATH do destinatario.',
        'Teste offscreen da GUI: aprovado; a janela nativa ainda deve ser conferida no Windows de destino.') |
        Set-Content -LiteralPath (Join-Path $imagem 'VALIDACAO.txt') -Encoding UTF8

    @('@echo off', 'cd /d "%~dp0"', 'Diagnostico.exe', 'pause') |
        Set-Content -LiteralPath (Join-Path $imagem 'DIAGNOSTICO.bat') -Encoding ASCII
    Write-Host '4/5 Compactando a pasta completa...'
    Set-Location -LiteralPath $destino
    $zip = Join-Path $destino 'SimuladorSO-Windows.zip'
    Compress-Archive -LiteralPath $imagem -DestinationPath $zip -CompressionLevel Optimal

    Write-Host '5/5 Conferindo a integridade do ZIP...'
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $arquivo = [IO.Compression.ZipFile]::OpenRead($zip)
    try {
        foreach ($sufixo in @('/SimuladorSO.exe', '/SimuladorCLI.exe', '/Testar.exe', '/INICIAR.bat', '/runtime/lib/modules')) {
            $encontrado = @($arquivo.Entries | Where-Object { $_.FullName.Replace('\', '/').EndsWith($sufixo) })
            if ($encontrado.Count -ne 1) { throw "ZIP incompleto: $sufixo" }
        }
    } finally { $arquivo.Dispose() }
    Write-Host "Pronto. Envie ao professor: $zip"
    Write-Host 'Ele deve extrair TUDO e abrir INICIAR.bat. Nao envie somente o .exe.'
    Write-Host "Abra a NOVA interface: $(Join-Path $imagem 'SimuladorSO.exe')"
    # O caminho da entrega e informado acima; nao abre janelas durante a geracao.
} catch {
    [Console]::Error.WriteLine("Erro ao gerar executavel: $($_.Exception.Message)")
    exit 1
} finally {
    Set-Location $pastaAnterior
}

$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    [Console]::Error.WriteLine('Erro: Java nao encontrado. Instale um JDK 21 ou superior e adicione sua pasta bin ao PATH.')
    exit 1
}

# Consulta o compilador pelo mesmo executavel usado na compilacao.
$preferenciaAnterior = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    $versao = & java -m jdk.compiler/com.sun.tools.javac.Main --version 2>&1
    $codigo = $LASTEXITCODE
} finally { $ErrorActionPreference = $preferenciaAnterior }
if ($codigo -ne 0 -or "$versao" -notmatch '(?m)^javac (\d+)(?:[. +\-]|$)' -or [int]$Matches[1] -lt 21) {
    [Console]::Error.WriteLine('Erro: e necessario um JDK 21 ou superior com o modulo jdk.compiler. Confira java -version e ajuste JAVA_HOME e PATH para o JDK desejado; um JRE nao e suficiente.')
    exit 1
}

New-Item -ItemType Directory -Force build/classes, build/test | Out-Null
$fontes = @((Get-ChildItem src/so/*.java).FullName) + @((Get-ChildItem test/so/*.java).FullName)
& java -m jdk.compiler/com.sun.tools.javac.Main --release 21 -encoding UTF-8 -Xlint:all,-output-file-clash -d build/classes $fontes
exit $LASTEXITCODE

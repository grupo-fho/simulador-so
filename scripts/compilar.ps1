$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
New-Item -ItemType Directory -Force build/classes, build/test | Out-Null
$fontes = @((Get-ChildItem src/so/*.java).FullName) + @((Get-ChildItem test/so/*.java).FullName)
& java -m jdk.compiler/com.sun.tools.javac.Main --release 21 -encoding UTF-8 -Xlint:all,-output-file-clash -d build/classes $fontes
exit $LASTEXITCODE

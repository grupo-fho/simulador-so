$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'compilar.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java -cp 'build/classes;build/test' so.Testes
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java '-Djava.awt.headless=true' -cp 'build/classes;build/test' so.TestesInterface
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java -cp 'build/classes;build/test' so.TestesDoom
exit $LASTEXITCODE

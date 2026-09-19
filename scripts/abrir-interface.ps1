$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
& (Join-Path $PSScriptRoot 'compilar.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& java -cp build/classes so.InterfaceGrafica
exit $LASTEXITCODE

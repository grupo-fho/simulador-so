param(
    [string]$PastaMotor,
    [Parameter(Mandatory=$true)][string]$Wad
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
try {
    $destino = Join-Path (Split-Path $PSScriptRoot -Parent) 'jogos\doom'
    $origem = $destino
    if ($PastaMotor) { $origem = (Resolve-Path -LiteralPath $PastaMotor).Path }
    $arquivoWad = (Resolve-Path -LiteralPath $Wad).Path
    if (-not (Test-Path -LiteralPath (Join-Path $origem 'chocolate-doom.exe') -PathType Leaf)) {
        throw 'Selecione a pasta extraida que contem chocolate-doom.exe e suas DLLs.'
    }
    $arquivo = [IO.File]::OpenRead($arquivoWad)
    try {
        $leitor = New-Object IO.BinaryReader($arquivo)
        if ($arquivo.Length -lt 12) { throw 'WAD incompleto.' }
        if ([Text.Encoding]::ASCII.GetString($leitor.ReadBytes(4)) -ne 'IWAD') { throw 'Selecione um IWAD base, nao um mod PWAD.' }
        $entradas = $leitor.ReadInt32()
        $diretorio = $leitor.ReadInt32()
        if ($entradas -le 0 -or $diretorio -lt 12 -or ([long]$diretorio + [long]$entradas * 16) -gt $arquivo.Length) {
            throw 'Diretorio do WAD invalido ou arquivo incompleto.'
        }
    } finally { $arquivo.Dispose() }
    $destino = Join-Path (Split-Path $PSScriptRoot -Parent) 'jogos\doom'
    if ($PastaMotor -and (Test-Path -LiteralPath (Join-Path $destino 'chocolate-doom.exe'))) {
        throw "Motor ja preparado em $destino. Para trocar a instalacao, mova a pasta anterior primeiro."
    }
    New-Item -ItemType Directory -Force -Path $destino | Out-Null
    if ($PastaMotor) { Get-ChildItem -LiteralPath $origem | Copy-Item -Destination $destino -Recurse -Force }
    $nomeWad = [IO.Path]::GetFileName($arquivoWad).ToLowerInvariant()
    if ($nomeWad -notin @('doom.wad', 'doom1.wad', 'doom2.wad')) {
        throw 'O IWAD deve se chamar DOOM.WAD, DOOM1.WAD ou DOOM2.WAD.'
    }
    Copy-Item -LiteralPath $arquivoWad -Destination (Join-Path $destino $nomeWad) -Force
    Write-Host "DOOM preparado com $nomeWad. Abra a interface e teste o jogo; depois gere o pacote portatil."
    Write-Host 'Os arquivos do motor, DLLs e licencas serao incluidos automaticamente no pacote.'
} catch {
    [Console]::Error.WriteLine("Erro ao preparar DOOM: $($_.Exception.Message)")
    exit 1
}

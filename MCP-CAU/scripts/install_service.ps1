# Script para instalar o servidor GLPI Agent como serviço do Windows
# Requer privilégios de administrador

param(
    [string]$ServiceName = "GLPIAgent",
    [string]$DisplayName = "GLPI Agent API Server",
    [string]$Description = "Servidor API para integração Copilot Studio com GLPI"
)

# Verifica se está rodando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "Este script deve ser executado como Administrador!"
    exit 1
}

$currentPath = Get-Location
$pythonPath = (Get-Command python).Source
$scriptPath = Join-Path $currentPath "run_server.py"

Write-Host "Configurando serviço do Windows..."
Write-Host "Nome do Serviço: $ServiceName"
Write-Host "Caminho do Python: $pythonPath"
Write-Host "Caminho do Script: $scriptPath"

# Remove serviço existente se houver
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "Removendo serviço existente..."
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    sc.exe delete $ServiceName
    Start-Sleep -Seconds 2
}

# Cria o serviço
Write-Host "Criando novo serviço..."
$binaryPath = "`"$pythonPath`" `"$scriptPath`""

sc.exe create $ServiceName binPath= $binaryPath DisplayName= $DisplayName start= auto
sc.exe description $ServiceName $Description

# Configura recuperação automática
sc.exe failure $ServiceName reset= 86400 actions= restart/5000/restart/10000/restart/30000

Write-Host "Serviço '$ServiceName' criado com sucesso!"
Write-Host ""
Write-Host "Para gerenciar o serviço:"
Write-Host "  Iniciar: Start-Service -Name $ServiceName"
Write-Host "  Parar:   Stop-Service -Name $ServiceName"
Write-Host "  Status:  Get-Service -Name $ServiceName"
Write-Host ""
Write-Host "Iniciando serviço..."
Start-Service -Name $ServiceName

Start-Sleep -Seconds 3
$serviceStatus = Get-Service -Name $ServiceName
Write-Host "Status do serviço: $($serviceStatus.Status)"
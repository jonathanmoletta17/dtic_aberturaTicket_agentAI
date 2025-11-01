# Script PowerShell para iniciar e monitorar o servidor GLPI Agent
# Inclui restart automático e logging

param(
    [switch]$NoRestart,
    [int]$RestartDelay = 5
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path "server_monitor.log" -Value $logMessage
}

function Test-ServerHealth {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -TimeoutSec 5
        return $response.glpi_connection -eq "ok"
    }
    catch {
        return $false
    }
}

function Start-Server {
    Write-Log "Iniciando servidor GLPI Agent..."
    
    # Verifica se a porta 5000 está em uso
    $portInUse = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Log "Porta 5000 já está em uso. Tentando finalizar processo..." "WARNING"
        $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
            $_.MainWindowTitle -like "*python*" -or $_.ProcessName -eq "python"
        }
        foreach ($proc in $processes) {
            try {
                $proc.Kill()
                Write-Log "Processo Python finalizado: $($proc.Id)" "INFO"
            }
            catch {
                Write-Log "Erro ao finalizar processo: $($_.Exception.Message)" "ERROR"
            }
        }
        Start-Sleep -Seconds 2
    }
    
    # Inicia o servidor
    $process = Start-Process -FilePath "python" -ArgumentList "run_server.py" -PassThru -NoNewWindow
    Start-Sleep -Seconds 3
    
    # Verifica se o servidor iniciou corretamente
    $healthCheck = Test-ServerHealth
    if ($healthCheck) {
        Write-Log "Servidor iniciado com sucesso! PID: $($process.Id)"
        return $process
    }
    else {
        Write-Log "Falha ao iniciar servidor ou health check falhou" "ERROR"
        return $null
    }
}

function Monitor-Server {
    param($Process)
    
    while ($true) {
        Start-Sleep -Seconds 30
        
        # Verifica se o processo ainda está rodando
        if ($Process.HasExited) {
            Write-Log "Processo do servidor finalizou inesperadamente" "ERROR"
            return $false
        }
        
        # Verifica health do servidor
        $isHealthy = Test-ServerHealth
        if (-not $isHealthy) {
            Write-Log "Health check falhou - servidor pode estar com problemas" "WARNING"
            return $false
        }
        
        Write-Log "Servidor funcionando normalmente"
    }
}

# Script principal
Write-Log "=== Iniciando Monitor do Servidor GLPI Agent ==="
Write-Log "Diretório: $(Get-Location)"
Write-Log "NoRestart: $NoRestart, RestartDelay: $RestartDelay segundos"

do {
    $serverProcess = Start-Server
    
    if ($serverProcess) {
        Write-Log "Monitorando servidor..."
        $serverOk = Monitor-Server -Process $serverProcess
        
        if (-not $serverOk) {
            Write-Log "Servidor apresentou problemas" "WARNING"
            
            # Finaliza o processo se ainda estiver rodando
            if (-not $serverProcess.HasExited) {
                $serverProcess.Kill()
                Write-Log "Processo do servidor finalizado"
            }
        }
    }
    
    if (-not $NoRestart) {
        Write-Log "Reiniciando servidor em $RestartDelay segundos..." "INFO"
        Start-Sleep -Seconds $RestartDelay
    }
    
} while (-not $NoRestart)

Write-Log "Monitor finalizado"
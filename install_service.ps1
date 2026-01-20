# Script para instalar el bot como servicio de Windows usando NSSM
# Requiere NSSM (Non-Sucking Service Manager)

Write-Host "📦 Instalador de Servicio de Windows para Bot de Telegram" -ForegroundColor Green
Write-Host ""

# Verificar si está ejecutando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host "Por favor, cierra esta ventana y ejecuta PowerShell como Administrador" -ForegroundColor Yellow
    pause
    exit
}

# Descargar NSSM si no existe
$nssmPath = "$PSScriptRoot\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "📥 Descargando NSSM..." -ForegroundColor Cyan
    
    # URL de NSSM (versión 2.24)
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $zipPath = "$PSScriptRoot\nssm.zip"
    
    try {
        Invoke-WebRequest -Uri $nssmUrl -OutFile $zipPath
        
        # Extraer
        Expand-Archive -Path $zipPath -DestinationPath $PSScriptRoot -Force
        
        # Copiar ejecutable correcto (32 o 64 bits)
        if ([Environment]::Is64BitOperatingSystem) {
            Copy-Item "$PSScriptRoot\nssm-2.24\win64\nssm.exe" $nssmPath
        } else {
            Copy-Item "$PSScriptRoot\nssm-2.24\win32\nssm.exe" $nssmPath
        }
        
        # Limpiar
        Remove-Item $zipPath
        Remove-Item "$PSScriptRoot\nssm-2.24" -Recurse -Force
        
        Write-Host "✅ NSSM descargado" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error al descargar NSSM: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Descarga NSSM manualmente desde: https://nssm.cc/download" -ForegroundColor Yellow
        Write-Host "Y coloca nssm.exe en: $PSScriptRoot" -ForegroundColor Yellow
        pause
        exit
    }
}

# Configuración del servicio
$serviceName = "TelegramEmailBot"
$pythonPath = (Get-Command python).Source
$botScript = "$PSScriptRoot\bot.py"
$workingDir = $PSScriptRoot

Write-Host ""
Write-Host "⚙️ Configuración:" -ForegroundColor Cyan
Write-Host "  Nombre del servicio: $serviceName"
Write-Host "  Python: $pythonPath"
Write-Host "  Script: $botScript"
Write-Host "  Directorio: $workingDir"
Write-Host ""

# Detener y eliminar servicio si existe
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "🛑 Deteniendo servicio existente..." -ForegroundColor Yellow
    & $nssmPath stop $serviceName
    Start-Sleep -Seconds 2
    
    Write-Host "🗑️ Eliminando servicio existente..." -ForegroundColor Yellow
    & $nssmPath remove $serviceName confirm
}

# Instalar servicio
Write-Host "➕ Instalando servicio..." -ForegroundColor Cyan
& $nssmPath install $serviceName $pythonPath $botScript

# Configurar parámetros
& $nssmPath set $serviceName AppDirectory $workingDir
& $nssmPath set $serviceName DisplayName "Telegram Email Bot"
& $nssmPath set $serviceName Description "Bot de Telegram para envío de emails masivos"
& $nssmPath set $serviceName Start SERVICE_AUTO_START

# Configurar reinicio automático en caso de fallo
& $nssmPath set $serviceName AppThrottle 1500
& $nssmName set $serviceName AppRestartDelay 5000

# Iniciar servicio
Write-Host "🚀 Iniciando servicio..." -ForegroundColor Green
& $nssmPath start $serviceName

Write-Host ""
Write-Host "✅ ¡Servicio instalado correctamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Comandos útiles:" -ForegroundColor Cyan
Write-Host "  Ver estado:  .\nssm.exe status $serviceName"
Write-Host "  Iniciar:     .\nssm.exe start $serviceName"
Write-Host "  Detener:     .\nssm.exe stop $serviceName"
Write-Host "  Reiniciar:   .\nssm.exe restart $serviceName"
Write-Host "  Ver logs:    Get-EventLog -LogName Application -Source $serviceName -Newest 50"
Write-Host ""
Write-Host "Para desinstalar:"
Write-Host "  .\nssm.exe stop $serviceName"
Write-Host "  .\nssm.exe remove $serviceName confirm"
Write-Host ""

pause

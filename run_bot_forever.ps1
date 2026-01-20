# Script para mantener el bot ejecutándose con auto-reinicio
# Si el bot se cae, se reinicia automáticamente

Write-Host "🤖 Iniciando Bot con Auto-Reinicio..." -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener completamente" -ForegroundColor Yellow
Write-Host ""

while ($true) {
    try {
        Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Iniciando bot..." -ForegroundColor Cyan
        
        # Ejecutar el bot
        python bot.py
        
        # Si el bot termina normalmente, esperar 5 segundos antes de reiniciar
        Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Bot detenido. Reiniciando en 5 segundos..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
    } catch {
        Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Reiniciando en 10 segundos..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

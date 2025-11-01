@echo off
echo ========================================
echo  Iniciando Servidor GLPI Agent
echo ========================================

cd /d "%~dp0"

:RESTART
echo [%date% %time%] Iniciando servidor...
python run_server.py

echo [%date% %time%] Servidor parou. Reiniciando em 5 segundos...
timeout /t 5 /nobreak >nul

goto RESTART
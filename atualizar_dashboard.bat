@echo off
title Tron — Atualizando Dashboard Meta Ads
cd /d "C:\Users\Marketing\Desktop"
python update_dashboard.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERRO ao atualizar o dashboard. Verifique o Python e as credenciais.
    pause
    exit /b 1
)
echo.
echo Copiando para pasta tron-dashboard...
copy /y "dashboard.html" "tron-dashboard\index.html" >nul
echo.
echo Pronto! Arraste a pasta tron-dashboard para netlify.com/drop para publicar.
echo.
pause

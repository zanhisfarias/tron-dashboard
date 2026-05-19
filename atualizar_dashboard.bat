@echo off
cd /d "C:\Users\Marketing\Desktop\Dashboard"
set LOG=C:\Users\Marketing\Desktop\Dashboard\update_log.txt
echo. >> "%LOG%"
echo ============================================================ >> "%LOG%"
echo Execucao: %DATE% %TIME% >> "%LOG%"
echo ============================================================ >> "%LOG%"
python update_dashboard.py >> "%LOG%" 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERRO na atualizacao - veja update_log.txt
) else (
    echo OK - Dashboard atualizado em %DATE% %TIME%
)

@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao encontrado. Execute setup.bat primeiro.
    pause
    exit /b 1
)

:: Criar .env se nao existir
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo.
    echo ================================================
    echo   ATENCAO: Configure sua chave da API!
    echo ================================================
    echo.
    echo Abra o arquivo .env nesta pasta e substitua
    echo a chave de exemplo pela sua chave real.
    echo Obtenha em: https://console.anthropic.com/
    echo.
    echo Apos configurar, execute run.bat novamente.
    echo ================================================
    echo.
    start notepad ".env"
    pause
    exit /b 0
)

echo.
echo ================================================
echo   Novus Auditiva - Painel Financeiro
echo   AMZ Consultoria Empresarial
echo ================================================
echo.
echo   Acesse: http://localhost:5000
echo   Ctrl+C para encerrar
echo.

set PYTHONUTF8=1
python app.py
pause

@echo off
chcp 65001 >nul
echo.
echo ================================================
echo   Novus Auditiva - Dashboard Setup
echo   AMZ Consultoria Empresarial
echo ================================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/3] Instalando Python via winget...
    winget install --id Python.Python.3.12 --source winget --silent --accept-source-agreements --accept-package-agreements
    if %errorlevel% neq 0 (
        echo.
        echo ERRO: Nao foi possivel instalar Python automaticamente.
        echo Por favor, instale manualmente em: https://python.org/downloads
        echo Marque a opcao "Add Python to PATH" durante a instalacao.
        pause
        exit /b 1
    )
    echo     Python instalado com sucesso.
) else (
    echo [1/3] Python ja esta instalado. OK
)

echo.
echo [2/3] Atualizando pip...
python -m pip install --upgrade pip --quiet

echo.
echo [3/3] Instalando dependencias do projeto...
python -m pip install flask openpyxl anthropic --quiet

echo.
echo ================================================
echo   Setup concluido com sucesso!
echo ================================================
echo.
echo PROXIMO PASSO:
echo.
echo 1. Copie o arquivo ".env.example" e renomeie para ".env"
echo 2. Abra o arquivo ".env" e substitua a chave de exemplo
echo    pela sua chave real da API Claude (Anthropic).
echo    Obtenha em: https://console.anthropic.com/
echo.
echo 3. Execute: run.bat
echo.
pause

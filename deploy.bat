@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PATH=%PATH%;%APPDATA%\npm

echo.
echo ================================================
echo   Novus Auditiva - Deploy na Railway
echo ================================================
echo.

:: Passo 1: Login
echo [1/4] Fazendo login na Railway (abre o navegador)...
railway login
if %errorlevel% neq 0 (echo ERRO no login. & pause & exit /b 1)

:: Passo 2: Criar projeto
echo.
echo [2/4] Criando projeto na Railway...
railway init --name "novus-auditiva-dashboard"
if %errorlevel% neq 0 (echo ERRO ao criar projeto. & pause & exit /b 1)

:: Passo 3: Configurar chave da API
echo.
echo [3/4] Configurando chave da API Claude...
set /p API_KEY="Cole aqui sua chave ANTHROPIC_API_KEY: "
railway variables set ANTHROPIC_API_KEY=%API_KEY%

:: Passo 4: Deploy
echo.
echo [4/4] Fazendo deploy (aguarde 2-3 minutos)...
railway up --detach

echo.
echo ================================================
echo   Deploy concluido!
echo ================================================
echo.
echo Acesse o painel em: railway open
echo Adicione um dominio personalizado no dashboard da Railway.
echo.
echo IMPORTANTE: Para dados persistirem entre reinicializacoes,
echo adicione um Volume no dashboard da Railway apontando para /app/data
echo e configure DATA_DIR=/app/data nas variaveis de ambiente.
echo.
pause

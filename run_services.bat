@echo off
echo ================================================================
echo           SISTEMA FLASK MICROSERVICES - INICIANDO
echo ================================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

REM Verificar se as dependências estão instaladas
echo Verificando dependencias...
python -c "import flask, requests, flask_cors, flask_sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo AVISO: Algumas dependencias podem estar faltando.
    echo Instalando dependencias...
    pip install -r requirements.txt
)

echo.
echo Criando diretorios de logs...
if not exist "user_service\logs" mkdir "user_service\logs"
if not exist "transaction_service\logs" mkdir "transaction_service\logs"
if not exist "api_gateway\logs" mkdir "api_gateway\logs"

echo.
echo ================================================================
echo INICIANDO SERVICOS (aguarde alguns segundos entre cada um)
echo ================================================================
echo.

REM Iniciar User Service
echo [1/3] Iniciando User Service na porta 5001...
start "User Service" cmd /k "cd user_service && python app.py"
timeout /t 3 /nobreak >nul

REM Iniciar Transaction Service
echo [2/3] Iniciando Transaction Service na porta 5002...
start "Transaction Service" cmd /k "cd transaction_service && python app.py"
timeout /t 3 /nobreak >nul

REM Iniciar API Gateway
echo [3/3] Iniciando API Gateway na porta 5000...
start "API Gateway" cmd /k "cd api_gateway && python gateway.py"
timeout /t 3 /nobreak >nul

echo.
echo ================================================================
echo                    SERVICOS INICIADOS
echo ================================================================
echo.
echo URLs dos servicos:
echo - API Gateway:        http://localhost:5000
echo - User Service:       http://localhost:5001
echo - Transaction Service: http://localhost:5002
echo.
echo Health Check:         http://localhost:5000/health
echo.
echo IMPORTANTE: 
echo - Aguarde alguns segundos para todos os servicos iniciarem
echo - Use CTRL+C em cada janela para parar os servicos
echo - Sempre pare os servicos na ordem: Gateway -> Transaction -> User
echo.

REM Aguardar um pouco e fazer health check
echo Aguardando servicos iniciarem...
timeout /t 5 /nobreak >nul

echo Testando conectividade...
curl -s http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    echo AVISO: Nem todos os servicos estao respondendo ainda.
    echo Aguarde mais alguns segundos e teste manualmente.
) else (
    echo SUCESSO: Servicos estao respondendo!
)

echo.
echo Para testar o sistema, execute:
echo curl http://localhost:5000/health
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
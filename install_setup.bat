@echo off
echo ================================================================
echo     INSTALACAO DO SISTEMA FLASK MICROSERVICES - WINDOWS
echo ================================================================
echo.

REM Verificar se Python está instalado
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.8 ou superior:
    echo https://www.python.org/downloads/
    echo.
    echo Certifique-se de marcar "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)

python --version
echo Python encontrado com sucesso!
echo.

REM Verificar se pip está disponível
echo Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: pip nao encontrado!
    echo Por favor, reinstale Python com pip incluso.
    pause
    exit /b 1
)
echo pip encontrado com sucesso!
echo.

REM Verificar se requirements.txt existe
if not exist "requirements.txt" (
    echo ERRO: Arquivo requirements.txt nao encontrado!
    echo Certifique-se de estar no diretorio correto do projeto.
    pause
    exit /b 1
)

REM Criar ambiente virtual (opcional mas recomendado)
echo ================================================================
echo CRIANDO AMBIENTE VIRTUAL
echo ================================================================
echo.
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERRO: Falha ao criar ambiente virtual.
        echo Continuando sem ambiente virtual...
        goto :install_deps
    )
    echo Ambiente virtual criado com sucesso!
) else (
    echo Ambiente virtual ja existe.
)

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo AVISO: Falha ao ativar ambiente virtual.
    echo Continuando sem ambiente virtual...
    goto :install_deps
)
echo Ambiente virtual ativado!

:install_deps
echo.
echo ================================================================
echo INSTALANDO DEPENDENCIAS
echo ================================================================
echo.
echo Instalando pacotes Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha na instalacao das dependencias.
    echo Verifique sua conexao com a internet e tente novamente.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo CRIANDO ESTRUTURA DE DIRETORIOS
echo ================================================================
echo.
if not exist "user_service\logs" mkdir "user_service\logs"
if not exist "transaction_service\logs" mkdir "transaction_service\logs"
if not exist "api_gateway\logs" mkdir "api_gateway\logs"
echo Diretorios de logs criados.

echo.
echo ================================================================
echo VERIFICANDO INSTALACAO
echo ================================================================
echo.
echo Testando importacao dos modulos...
python -c "import flask; print('✓ Flask instalado')"
python -c "import requests; print('✓ Requests instalado')"
python -c "import flask_cors; print('✓ Flask-CORS instalado')"
python -c "import flask_sqlalchemy; print('✓ Flask-SQLAlchemy instalado')"

if errorlevel 1 (
    echo ERRO: Alguns modulos nao foram instalados corretamente.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo              INSTALACAO CONCLUIDA COM SUCESSO!
echo ================================================================
echo.
echo Proximos passos:
echo.
echo 1. Para iniciar todos os servicos automaticamente:
echo    run_services.bat
echo.
echo 2. Para iniciar servicos manualmente:
echo    - User Service:       cd user_service && python app.py
echo    - Transaction Service: cd transaction_service && python app.py
echo    - API Gateway:        cd api_gateway && python gateway.py
echo.
echo 3. Para testar o sistema:
echo    curl http://localhost:5000/health
echo.
echo 4. Consulte o README.md para documentacao completa.
echo.

REM Perguntar se quer iniciar os serviços
set /p start_services="Deseja iniciar os servicos agora? (s/n): "
if /i "%start_services%"=="s" (
    echo.
    echo Iniciando servicos...
    call run_services.bat
) else (
    echo.
    echo Para iniciar os servicos depois, execute: run_services.bat
)

echo.
echo Pressione qualquer tecla para finalizar...
pause >nul
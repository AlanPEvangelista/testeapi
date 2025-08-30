#!/bin/bash

echo "================================================================"
echo "           SISTEMA FLASK MICROSERVICES - INICIANDO"
echo "================================================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 não encontrado! Instale Python 3.8+ primeiro."
    exit 1
fi

# Verificar se as dependências estão instaladas
echo "Verificando dependências..."
python3 -c "import flask, requests, flask_cors, flask_sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "AVISO: Algumas dependências podem estar faltando."
    echo "Instalando dependências..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Criando diretórios de logs..."
mkdir -p user_service/logs
mkdir -p transaction_service/logs
mkdir -p api_gateway/logs

echo ""
echo "================================================================"
echo "INICIANDO SERVIÇOS (aguarde alguns segundos entre cada um)"
echo "================================================================"
echo ""

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "Parando serviços..."
    kill $USER_PID $TRANSACTION_PID $GATEWAY_PID 2>/dev/null
    exit 0
}

# Configurar trap para cleanup
trap cleanup SIGINT SIGTERM

# Iniciar User Service
echo "[1/3] Iniciando User Service na porta 5001..."
cd user_service
python3 app.py &
USER_PID=$!
cd ..
sleep 3

# Iniciar Transaction Service
echo "[2/3] Iniciando Transaction Service na porta 5002..."
cd transaction_service
python3 app.py &
TRANSACTION_PID=$!
cd ..
sleep 3

# Iniciar API Gateway
echo "[3/3] Iniciando API Gateway na porta 5000..."
cd api_gateway
python3 gateway.py &
GATEWAY_PID=$!
cd ..
sleep 3

echo ""
echo "================================================================"
echo "                    SERVIÇOS INICIADOS"
echo "================================================================"
echo ""
echo "URLs dos serviços:"
echo "- API Gateway:         http://localhost:5000"
echo "- User Service:        http://localhost:5001"
echo "- Transaction Service: http://localhost:5002"
echo ""
echo "Health Check:          http://localhost:5000/health"
echo ""
echo "PIDs dos processos:"
echo "- User Service:        $USER_PID"
echo "- Transaction Service: $TRANSACTION_PID"
echo "- API Gateway:         $GATEWAY_PID"
echo ""

# Aguardar um pouco e fazer health check
echo "Aguardando serviços iniciarem..."
sleep 5

echo "Testando conectividade..."
if curl -s http://localhost:5000/health >/dev/null 2>&1; then
    echo "SUCESSO: Serviços estão respondendo!"
else
    echo "AVISO: Nem todos os serviços estão respondendo ainda."
    echo "Aguarde mais alguns segundos e teste manualmente."
fi

echo ""
echo "Para testar o sistema, execute:"
echo "curl http://localhost:5000/health"
echo ""
echo "Para parar todos os serviços, pressione Ctrl+C"
echo ""

# Manter o script rodando
while true; do
    sleep 1
    # Verificar se todos os processos ainda estão rodando
    if ! kill -0 $USER_PID 2>/dev/null || ! kill -0 $TRANSACTION_PID 2>/dev/null || ! kill -0 $GATEWAY_PID 2>/dev/null; then
        echo "Um ou mais serviços pararam inesperadamente."
        cleanup
    fi
done
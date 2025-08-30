# -*- coding: utf-8 -*-
"""
Gateway API Principal
====================

Este é o arquivo principal do API Gateway que funciona como ponto
de entrada único para o sistema de microservices. Redireciona
requisições para os serviços apropriados e fornece funcionalidades
de agregação de dados.

O gateway roda na porta 5000 e roteia requisições para:
- User Service (porta 5001)
- Transaction Service (porta 5002)

Autor: Sistema Flask Microservices
Data: 2024
"""

import logging
import os
import requests
import time
import concurrent.futures
import threading
from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from flask_cors import CORS
from config import Config
import json

def criar_app():
    """
    Factory function para criar e configurar a aplicação Flask do Gateway.
    
    Esta função configura todos os componentes necessários para o
    funcionamento do API Gateway, incluindo roteamento, CORS e logging.
    
    Returns:
        Flask: Instância configurada da aplicação Flask
    """
    # Criação da instância Flask
    app = Flask(__name__, template_folder='templates')
    
    # Carregamento das configurações
    app.config.from_object(Config)
    
    # Configuração do CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configuração do sistema de logs
    configurar_logging(app)
    
    return app

def configurar_logging(app):
    """
    Configura o sistema de logging para a aplicação.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    # Configuração do nível de log
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    # Configuração do formato das mensagens de log
    formatter = logging.Formatter(app.config.get('LOG_FORMAT'))
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Handler para arquivo (opcional)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = logging.FileHandler('logs/api_gateway.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Configuração do logger da aplicação
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    # Configuração do logger do requests (menos verboso)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

def determinar_servico_destino(path):
    """
    Determina qual serviço deve processar a requisição baseado no path.
    
    Args:
        path (str): Caminho da URL da requisição
        
    Returns:
        str: Nome do serviço destino ou None se não encontrado
    """
    # Remove parâmetros de query e normaliza o path
    path_limpo = path.split('?')[0].rstrip('/')
    
    # Verifica mapeamentos exatos primeiro
    if path_limpo in app.config['ROUTE_MAPPING']:
        return app.config['ROUTE_MAPPING'][path_limpo]
    
    # Verifica mapeamentos por prefixo
    for rota_prefixo, servico in app.config['ROUTE_MAPPING'].items():
        if path_limpo.startswith(rota_prefixo.rstrip('/')):
            return servico
    
    return None

def obter_url_servico(servico):
    """
    Obtém a URL base do serviço especificado.
    
    Args:
        servico (str): Nome do serviço
        
    Returns:
        str: URL base do serviço ou None se não encontrado
    """
    mapping = {
        'USER_SERVICE': app.config['USER_SERVICE_URL'],
        'TRANSACTION_SERVICE': app.config['TRANSACTION_SERVICE_URL']
    }
    
    return mapping.get(servico)

def preparar_headers_requisicao(headers_originais):
    """
    Prepara os headers para envio ao microservice.
    
    Remove headers específicos do gateway e mantém os necessários.
    
    Args:
        headers_originais: Headers da requisição original
        
    Returns:
        dict: Headers limpos para envio
    """
    headers_limpos = {}
    
    for nome, valor in headers_originais.items():
        # Remove headers que não devem ser encaminhados
        if nome.lower() not in app.config['HEADERS_TO_REMOVE']:
            headers_limpos[nome] = valor
    
    return headers_limpos

def fazer_requisicao_com_retry(url, method, headers=None, data=None, params=None):
    """
    Faz requisição HTTP com retry automático em caso de falha.
    
    Args:
        url (str): URL de destino
        method (str): Método HTTP
        headers (dict): Headers da requisição
        data: Dados do corpo da requisição
        params (dict): Parâmetros de query
        
    Returns:
        Response: Objeto response do requests
    """
    max_tentativas = app.config['MAX_RETRY_ATTEMPTS']
    delay = app.config['RETRY_DELAY']
    
    for tentativa in range(max_tentativas):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params,
                timeout=app.config['REQUEST_TIMEOUT']
            )
            return response
            
        except requests.exceptions.Timeout:
            app.logger.warning(f"Timeout na tentativa {tentativa + 1} para {url}")
            if tentativa < max_tentativas - 1:
                time.sleep(delay)
            else:
                raise
                
        except requests.exceptions.ConnectionError:
            app.logger.warning(f"Erro de conexão na tentativa {tentativa + 1} para {url}")
            if tentativa < max_tentativas - 1:
                time.sleep(delay)
            else:
                raise
                
        except Exception as e:
            app.logger.error(f"Erro inesperado na tentativa {tentativa + 1}: {str(e)}")
            if tentativa < max_tentativas - 1:
                time.sleep(delay)
            else:
                raise

# Criação da instância da aplicação
app = criar_app()

@app.route('/')
def pagina_principal():
    """
    Serve a página web principal do sistema.
    
    Returns:
        HTML: Interface web para gerenciamento do sistema
    """
    return render_template('index.html')

@app.route('/api')
def info_gateway():
    """
    Endpoint que retorna informações sobre o API Gateway.
    
    Returns:
        JSON: Informações básicas do Gateway
    """
    return jsonify({
        'servico': 'API Gateway',
        'versao': '1.0.0',
        'descricao': 'Gateway para sistema de microservices',
        'servicos_disponiveis': [
            'User Service (porta 5001)',
            'Transaction Service (porta 5002)'
        ],
        'rotas_disponiveis': [
            'GET /api/users - Gerenciamento de usuários',
            'GET /api/transactions - Gerenciamento de transações',
            'GET /api/reports/user/<id> - Relatórios agregados',
            'GET /health - Status de todos os serviços'
        ],
        'porta': app.config['PORT'],
        'documentacao': 'Consulte o README.md para documentação completa',
        'interface_web': 'Acesse http://localhost:5000 para a interface web'
    })

@app.route('/health')
def health_check():
    """
    Verifica o status de saúde de todos os microservices.
    
    Returns:
        JSON: Status de todos os serviços
    """
    app.logger.info("Verificando saúde de todos os serviços")
    
    status_servicos = {}
    status_geral = True
    
    # Verifica User Service
    try:
        user_url = f"{app.config['USER_SERVICE_URL']}/users/health"
        response = requests.get(user_url, timeout=5)  # Aumentado para 5 segundos para startup
        status_servicos['user_service'] = {
            'status': 'ativo' if response.status_code == 200 else 'erro',
            'codigo': response.status_code,
            'url': user_url
        }
    except Exception as e:
        status_servicos['user_service'] = {
            'status': 'indisponível',
            'erro': str(e),
            'url': f"{app.config['USER_SERVICE_URL']}/users/health"
        }
        status_geral = False
    
    # Verifica Transaction Service
    try:
        transaction_url = f"{app.config['TRANSACTION_SERVICE_URL']}/transactions/health"
        response = requests.get(transaction_url, timeout=5)  # Aumentado para 5 segundos para startup
        status_servicos['transaction_service'] = {
            'status': 'ativo' if response.status_code == 200 else 'erro',
            'codigo': response.status_code,
            'url': transaction_url
        }
    except Exception as e:
        status_servicos['transaction_service'] = {
            'status': 'indisponível',
            'erro': str(e),
            'url': f"{app.config['TRANSACTION_SERVICE_URL']}/transactions/health"
        }
        status_geral = False
    
    return jsonify({
        'gateway_status': 'ativo',
        'status_geral': 'ativo' if status_geral else 'degradado',
        'servicos': status_servicos,
        'timestamp': time.time()
    }), 200 if status_geral else 503

@app.route('/api/reports/user/<int:user_id>')
def relatorio_usuario(user_id):
    """
    Gera relatório agregado de um usuário, combinando dados de múltiplos serviços.
    Utiliza requisições paralelas para melhor performance.
    
    Args:
        user_id (int): ID do usuário
        
    Returns:
        JSON: Relatório completo do usuário
    """
    app.logger.info(f"Gerando relatório agregado para usuário {user_id}")
    
    def buscar_dados_usuario():
        """Busca dados do usuário no User Service."""
        try:
            user_url = f"{app.config['USER_SERVICE_URL']}/users/{user_id}"
            response = fazer_requisicao_com_retry(
                url=user_url,
                method='GET',
                headers={'Content-Type': 'application/json'}
            )
            return ('user', response)
        except Exception as e:
            return ('user', e)
    
    def buscar_transacoes_usuario():
        """Busca transações do usuário no Transaction Service."""
        try:
            transaction_url = f"{app.config['TRANSACTION_SERVICE_URL']}/transactions/user/{user_id}"
            response = fazer_requisicao_com_retry(
                url=transaction_url,
                method='GET',
                headers={'Content-Type': 'application/json'}
            )
            return ('transactions', response)
        except Exception as e:
            return ('transactions', e)
    
    def buscar_estatisticas_usuario():
        """Busca estatísticas do usuário no Transaction Service."""
        try:
            stats_url = f"{app.config['TRANSACTION_SERVICE_URL']}/transactions/stats/user/{user_id}"
            response = fazer_requisicao_com_retry(
                url=stats_url,
                method='GET',
                headers={'Content-Type': 'application/json'}
            )
            return ('stats', response)
        except Exception as e:
            return ('stats', e)
    
    try:
        # Executa todas as requisições em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submete todas as tarefas simultaneamente
            future_user = executor.submit(buscar_dados_usuario)
            future_transactions = executor.submit(buscar_transacoes_usuario)
            future_stats = executor.submit(buscar_estatisticas_usuario)
            
            # Coleta os resultados
            results = {}
            for future in concurrent.futures.as_completed([future_user, future_transactions, future_stats], timeout=10):
                try:
                    tipo, response = future.result()
                    results[tipo] = response
                except Exception as e:
                    app.logger.error(f"Erro em requisição paralela: {str(e)}")
        
        # Processa resultado dos dados do usuário
        if 'user' not in results or isinstance(results['user'], Exception):
            return jsonify({
                'erro': 'Erro ao buscar dados do usuário',
                'mensagem': 'Não foi possível recuperar informações do usuário'
            }), 500
        
        user_response = results['user']
        if user_response.status_code == 404:
            return jsonify({
                'erro': 'Usuário não encontrado',
                'mensagem': f'Não existe usuário com ID {user_id}'
            }), 404
        
        if user_response.status_code != 200:
            return jsonify({
                'erro': 'Erro ao buscar dados do usuário',
                'mensagem': 'Não foi possível recuperar informações do usuário'
            }), 500
        
        usuario_dados = user_response.json()
        
        # Processa resultado das transações
        transacoes_dados = {'transacoes': [], 'resumo': {}}
        if 'transactions' in results and not isinstance(results['transactions'], Exception):
            transaction_response = results['transactions']
            if transaction_response.status_code == 200:
                transacoes_dados = transaction_response.json()
        
        # Processa resultado das estatísticas
        estatisticas = {}
        if 'stats' in results and not isinstance(results['stats'], Exception):
            stats_response = results['stats']
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                estatisticas = stats_data.get('resumo_geral', {})
        
        # Monta o relatório agregado
        relatorio = {
            'usuario': usuario_dados,
            'transacoes': transacoes_dados.get('transacoes', []),
            'resumo_financeiro': transacoes_dados.get('resumo', {}),
            'estatisticas_detalhadas': estatisticas,
            'metadados': {
                'gerado_em': time.time(),
                'total_registros': len(transacoes_dados.get('transacoes', [])),
                'fonte_dados': {
                    'usuario': 'User Service',
                    'transacoes': 'Transaction Service'
                },
                'performance': {
                    'requisicoes_paralelas': True,
                    'tempo_otimizado': True
                }
            }
        }
        
        app.logger.info(f"Relatório gerado com sucesso para usuário {user_id} (requisições paralelas)")
        return jsonify(relatorio), 200
        
    except concurrent.futures.TimeoutError:
        app.logger.error(f"Timeout ao gerar relatório para usuário {user_id}")
        return jsonify({
            'erro': 'Timeout na consulta',
            'mensagem': 'Tempo limite excedido ao consultar os serviços'
        }), 504
        
    except requests.exceptions.ConnectionError:
        app.logger.error(f"Erro de conexão ao gerar relatório para usuário {user_id}")
        return jsonify({
            'erro': 'Serviços indisponíveis',
            'mensagem': 'Não foi possível conectar aos microservices'
        }), 503
        
    except Exception as e:
        app.logger.error(f"Erro interno ao gerar relatório: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do gateway',
            'mensagem': 'Não foi possível gerar o relatório'
        }), 500

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy_requisicao(path):
    """
    Proxy para redirecionar requisições aos microservices apropriados.
    
    Args:
        path (str): Caminho da URL após /api/
        
    Returns:
        Response: Resposta do microservice de destino
    """
    path_completo = f"/api/{path}"
    app.logger.info(f"Recebida requisição: {request.method} {path_completo}")
    
    # Determina qual serviço deve processar a requisição
    servico_destino = determinar_servico_destino(path_completo)
    
    if not servico_destino:
        app.logger.warning(f"Nenhum serviço encontrado para {path_completo}")
        return jsonify({
            'erro': 'Rota não encontrada',
            'mensagem': f'Não existe serviço configurado para {path_completo}',
            'rotas_disponiveis': list(app.config['ROUTE_MAPPING'].keys())
        }), 404
    
    # Obtém URL do serviço de destino
    url_servico = obter_url_servico(servico_destino)
    
    if not url_servico:
        app.logger.error(f"URL não configurada para serviço {servico_destino}")
        return jsonify({
            'erro': 'Configuração inválida',
            'mensagem': 'URL do serviço não está configurada'
        }), 500
    
    # Monta a URL final
    # Remove /api do path para enviar ao microservice
    path_servico = path_completo.replace('/api', '')
    url_final = f"{url_servico}{path_servico}"
    
    # Prepara headers e dados
    headers_limpos = preparar_headers_requisicao(request.headers)
    dados_requisicao = request.get_data()
    params_query = dict(request.args)
    
    app.logger.info(f"Encaminhando para: {request.method} {url_final}")
    
    try:
        # Faz a requisição para o microservice
        response = fazer_requisicao_com_retry(
            url=url_final,
            method=request.method,
            headers=headers_limpos,
            data=dados_requisicao,
            params=params_query
        )
        
        # Prepara a resposta para retornar ao cliente
        response_headers = {}
        for nome, valor in response.headers.items():
            # Remove headers específicos do servidor
            if nome.lower() not in ['server', 'date', 'content-encoding']:
                response_headers[nome] = valor
        
        app.logger.info(f"Resposta recebida: {response.status_code}")
        
        return Response(
            response.content,
            status=response.status_code,
            headers=response_headers,
            mimetype=response.headers.get('content-type', 'application/json')
        )
        
    except requests.exceptions.Timeout:
        app.logger.error(f"Timeout na requisição para {url_final}")
        return jsonify({
            'erro': 'Timeout na requisição',
            'mensagem': 'O serviço não respondeu dentro do tempo limite'
        }), 504
        
    except requests.exceptions.ConnectionError:
        app.logger.error(f"Erro de conexão com {url_final}")
        return jsonify({
            'erro': 'Serviço indisponível',
            'mensagem': f'Não foi possível conectar ao {servico_destino}'
        }), 503
        
    except Exception as e:
        app.logger.error(f"Erro inesperado: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do gateway',
            'mensagem': 'Ocorreu um erro inesperado no gateway'
        }), 500

@app.errorhandler(404)
def nao_encontrado(error):
    """Handler para erros 404 (não encontrado)."""
    return jsonify({
        'erro': 'Endpoint não encontrado',
        'mensagem': 'A URL solicitada não existe neste gateway',
        'servico': 'API Gateway'
    }), 404

@app.errorhandler(500)
def erro_interno(error):
    """Handler para erros 500 (erro interno do servidor)."""
    return jsonify({
        'erro': 'Erro interno do gateway',
        'mensagem': 'Ocorreu um erro inesperado no gateway',
        'servico': 'API Gateway'
    }), 500

if __name__ == '__main__':
    """
    Ponto de entrada principal do API Gateway.
    
    Inicia o servidor Flask na porta configurada.
    """
    # Log de inicialização
    app.logger.info("=" * 50)
    app.logger.info("INICIANDO API GATEWAY")
    app.logger.info("=" * 50)
    app.logger.info(f"Servidor rodando na porta: {app.config['PORT']}")
    app.logger.info(f"Debug mode: {app.config['DEBUG']}")
    app.logger.info(f"User Service: {app.config['USER_SERVICE_URL']}")
    app.logger.info(f"Transaction Service: {app.config['TRANSACTION_SERVICE_URL']}")
    app.logger.info("=" * 50)
    
    # Inicia o servidor Flask
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
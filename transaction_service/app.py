# -*- coding: utf-8 -*-
"""
Aplicação Principal do Serviço de Transações
===========================================

Este é o arquivo principal do microservice de transações. Configura
a aplicação Flask, inicializa o banco de dados, registra as rotas
e fornece funcionalidades para executar o serviço.

O serviço roda na porta 5002 e fornece APIs REST para gerenciamento
de transações/lançamentos no sistema de microservices.

Autor: Sistema Flask Microservices
Data: 2024
"""

import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db, Lancamento
from routes import transaction_routes
from decimal import Decimal

def criar_app():
    """
    Factory function para criar e configurar a aplicação Flask.
    
    Esta função configura todos os componentes necessários para o
    funcionamento do microservice de transações, incluindo banco de dados,
    rotas, CORS e logging.
    
    Returns:
        Flask: Instância configurada da aplicação Flask
    """
    # Criação da instância Flask
    app = Flask(__name__)
    
    # Carregamento das configurações
    app.config.from_object(Config)
    
    # Configuração do CORS para permitir comunicação entre microservices
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5000", "http://localhost:5001"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicialização do banco de dados
    db.init_app(app)
    
    # Registro das rotas
    app.register_blueprint(transaction_routes)
    
    # Configuração do sistema de logs
    configurar_logging(app)
    
    # Criação das tabelas do banco de dados
    with app.app_context():
        db.create_all()
        app.logger.info("Banco de dados inicializado para Transaction Service")
    
    return app

def configurar_logging(app):
    """
    Configura o sistema de logging para a aplicação.
    
    Define o nível de log, formato das mensagens e handlers
    para arquivo e console, facilitando o debugging e monitoramento.
    
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
    
    file_handler = logging.FileHandler('logs/transaction_service.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Configuração do logger da aplicação
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    # Configuração do logger do SQLAlchemy (menos verboso)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Configuração do logger do requests (menos verboso)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)

def inicializar_dados_exemplo(app):
    """
    Inicializa o banco de dados com algumas transações de exemplo.
    
    Útil para desenvolvimento e testes. Cria transações de exemplo
    se o banco estiver vazio.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    with app.app_context():
        # Verifica se já existem transações cadastradas
        if Lancamento.query.count() == 0:
            app.logger.info("Criando dados de exemplo...")
            
            try:
                # Transações de exemplo (assumindo que existem usuários com IDs 1-4)
                transacoes_exemplo = [
                    Lancamento(
                        usuario_id=1,
                        descricao="Compra Amazon - Livros",
                        valor=Decimal("89.90"),
                        cartao_tipo="Crédito",
                        cartao_final="1234"
                    ),
                    Lancamento(
                        usuario_id=1,
                        descricao="Supermercado Extra",
                        valor=Decimal("156.75"),
                        cartao_tipo="Débito",
                        cartao_final="5678"
                    ),
                    Lancamento(
                        usuario_id=2,
                        descricao="Posto de Gasolina Shell",
                        valor=Decimal("120.00"),
                        cartao_tipo="Crédito",
                        cartao_final="9012"
                    ),
                    Lancamento(
                        usuario_id=2,
                        descricao="Farmácia Droga Raia",
                        valor=Decimal("45.30"),
                        cartao_tipo="Pré-pago",
                        cartao_final="3456"
                    ),
                    Lancamento(
                        usuario_id=3,
                        descricao="Netflix - Assinatura Mensal",
                        valor=Decimal("32.90"),
                        cartao_tipo="Crédito",
                        cartao_final="7890"
                    ),
                    Lancamento(
                        usuario_id=3,
                        descricao="Uber - Corrida Centro",
                        valor=Decimal("18.50"),
                        cartao_tipo="Débito",
                        cartao_final="2345"
                    ),
                    Lancamento(
                        usuario_id=4,
                        descricao="Restaurante Outback",
                        valor=Decimal("78.90"),
                        cartao_tipo="Crédito",
                        cartao_final="6789"
                    )
                ]
                
                # Adiciona as transações ao banco
                for transacao in transacoes_exemplo:
                    db.session.add(transacao)
                
                db.session.commit()
                app.logger.info(f"Criadas {len(transacoes_exemplo)} transações de exemplo")
                
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Erro ao criar dados de exemplo: {str(e)}")

# Criação da instância da aplicação
app = criar_app()

@app.errorhandler(404)
def nao_encontrado(error):
    """
    Handler para erros 404 (não encontrado).
    
    Args:
        error: Objeto do erro
        
    Returns:
        JSON: Mensagem de erro padronizada
    """
    return jsonify({
        'erro': 'Endpoint não encontrado',
        'mensagem': 'A URL solicitada não existe neste serviço',
        'servico': 'Transaction Service'
    }), 404

@app.errorhandler(500)
def erro_interno(error):
    """
    Handler para erros 500 (erro interno do servidor).
    
    Args:
        error: Objeto do erro
        
    Returns:
        JSON: Mensagem de erro padronizada
    """
    return jsonify({
        'erro': 'Erro interno do servidor',
        'mensagem': 'Ocorreu um erro inesperado no servidor',
        'servico': 'Transaction Service'
    }), 500

# Rota raiz para informações do serviço
@app.route('/')
def info_servico():
    """
    Endpoint raiz que retorna informações sobre o serviço.
    
    Returns:
        JSON: Informações básicas do Transaction Service
    """
    return jsonify({
        'servico': 'Transaction Service',
        'versao': '1.0.0',
        'descricao': 'Microservice para gerenciamento de transações financeiras',
        'endpoints': [
            'GET /transactions - Lista todas as transações',
            'GET /transactions/<id> - Busca transação por ID',
            'GET /transactions/user/<user_id> - Lista transações de um usuário',
            'POST /transactions - Cria nova transação',
            'PUT /transactions/<id> - Atualiza transação',
            'DELETE /transactions/<id> - Remove transação',
            'GET /transactions/stats/user/<user_id> - Estatísticas do usuário',
            'GET /transactions/health - Status do serviço'
        ],
        'porta': app.config['PORT'],
        'documentacao': 'Consulte o README.md para documentação completa',
        'tipos_cartao_aceitos': app.config['TIPOS_CARTAO_VALIDOS'],
        'limites_valor': {
            'minimo': float(app.config['VALOR_MINIMO_TRANSACAO']),
            'maximo': float(app.config['VALOR_MAXIMO_TRANSACAO'])
        }
    })

if __name__ == '__main__':
    """
    Ponto de entrada principal do Transaction Service.
    
    Inicializa dados de exemplo (se necessário) e inicia o servidor Flask
    na porta configurada com debug habilitado para desenvolvimento.
    """
    # Inicializa dados de exemplo para desenvolvimento
    if app.config['DEBUG']:
        # Aguarda um pouco para garantir que o User Service esteja rodando
        import time
        time.sleep(2)
        inicializar_dados_exemplo(app)
    
    # Log de inicialização
    app.logger.info("=" * 50)
    app.logger.info("INICIANDO TRANSACTION SERVICE")
    app.logger.info("=" * 50)
    app.logger.info(f"Servidor rodando na porta: {app.config['PORT']}")
    app.logger.info(f"Debug mode: {app.config['DEBUG']}")
    app.logger.info(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.logger.info(f"User Service URL: {app.config['USER_SERVICE_URL']}")
    app.logger.info("=" * 50)
    
    # Inicia o servidor Flask
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
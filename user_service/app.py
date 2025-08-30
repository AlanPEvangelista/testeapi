# -*- coding: utf-8 -*-
"""
Aplicação Principal do Serviço de Usuários
=========================================

Este é o arquivo principal do microservice de usuários. Configura
a aplicação Flask, inicializa o banco de dados, registra as rotas
e fornece funcionalidades para executar o serviço.

O serviço roda na porta 5001 e fornece APIs REST para gerenciamento
de usuários no sistema de microservices.

Autor: Sistema Flask Microservices
Data: 2024
"""

import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db, Usuario
from routes import user_routes

def criar_app():
    """
    Factory function para criar e configurar a aplicação Flask.
    
    Esta função configura todos os componentes necessários para o
    funcionamento do microservice de usuários, incluindo banco de dados,
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
            "origins": ["http://localhost:5000", "http://localhost:5002"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Inicialização do banco de dados
    db.init_app(app)
    
    # Registro das rotas
    app.register_blueprint(user_routes)
    
    # Configuração do sistema de logs
    configurar_logging(app)
    
    # Criação das tabelas do banco de dados
    with app.app_context():
        db.create_all()
        app.logger.info("Banco de dados inicializado para User Service")
    
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
    
    file_handler = logging.FileHandler('logs/user_service.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Configuração do logger da aplicação
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    # Configuração do logger do SQLAlchemy (menos verboso)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

def inicializar_dados_exemplo(app):
    """
    Inicializa o banco de dados com alguns dados de exemplo.
    
    Útil para desenvolvimento e testes. Cria usuários de exemplo
    se o banco estiver vazio.
    
    Args:
        app (Flask): Instância da aplicação Flask
    """
    with app.app_context():
        # Verifica se já existem usuários cadastrados
        if Usuario.query.count() == 0:
            app.logger.info("Criando dados de exemplo...")
            
            try:
                # Usuários de exemplo
                usuarios_exemplo = [
                    Usuario(nome="João Silva", email="joao.silva@email.com"),
                    Usuario(nome="Maria Santos", email="maria.santos@email.com"),
                    Usuario(nome="Pedro Oliveira", email="pedro.oliveira@email.com"),
                    Usuario(nome="Ana Costa", email="ana.costa@email.com")
                ]
                
                # Adiciona os usuários ao banco
                for usuario in usuarios_exemplo:
                    db.session.add(usuario)
                
                db.session.commit()
                app.logger.info(f"Criados {len(usuarios_exemplo)} usuários de exemplo")
                
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
        'servico': 'User Service'
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
        'servico': 'User Service'
    }), 500

# Rota raiz para informações do serviço
@app.route('/')
def info_servico():
    """
    Endpoint raiz que retorna informações sobre o serviço.
    
    Returns:
        JSON: Informações básicas do User Service
    """
    return jsonify({
        'servico': 'User Service',
        'versao': '1.0.0',
        'descricao': 'Microservice para gerenciamento de usuários',
        'endpoints': [
            'GET /users - Lista todos os usuários',
            'GET /users/<id> - Busca usuário por ID',
            'POST /users - Cria novo usuário',
            'PUT /users/<id> - Atualiza usuário',
            'DELETE /users/<id> - Remove usuário',
            'GET /users/health - Status do serviço'
        ],
        'porta': app.config['PORT'],
        'documentacao': 'Consulte o README.md para documentação completa'
    })

if __name__ == '__main__':
    """
    Ponto de entrada principal do User Service.
    
    Inicializa dados de exemplo (se necessário) e inicia o servidor Flask
    na porta configurada com debug habilitado para desenvolvimento.
    """
    # Inicializa dados de exemplo para desenvolvimento
    if app.config['DEBUG']:
        inicializar_dados_exemplo(app)
    
    # Log de inicialização
    app.logger.info("=" * 50)
    app.logger.info("INICIANDO USER SERVICE")
    app.logger.info("=" * 50)
    app.logger.info(f"Servidor rodando na porta: {app.config['PORT']}")
    app.logger.info(f"Debug mode: {app.config['DEBUG']}")
    app.logger.info(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.logger.info("=" * 50)
    
    # Inicia o servidor Flask
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
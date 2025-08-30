# -*- coding: utf-8 -*-
"""
Configuração do Serviço de Usuários
===================================

Este módulo contém as configurações necessárias para o funcionamento
do microservice de usuários, incluindo configurações de banco de dados,
URLs de comunicação entre serviços e configurações da aplicação Flask.

Autor: Sistema Flask Microservices
Data: 2024
"""

import os
from datetime import timedelta

class Config:
    """
    Classe de configuração principal para o serviço de usuários.
    
    Contém todas as configurações necessárias para o funcionamento
    adequado do microservice, incluindo banco de dados, segurança
    e comunicação entre serviços.
    """
    
    # Configuração do banco de dados SQLite
    # Caminho relativo para o arquivo de banco de dados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///user_database.db'
    
    # Desabilita tracking de modificações para melhor performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Chave secreta para segurança da aplicação Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-usuarios-2024'
    
    # Configurações de debug
    DEBUG = True
    
    # Configuração da porta do serviço
    PORT = 5001
    
    # Host de execução
    HOST = '0.0.0.0'
    
    # URLs de outros microservices para comunicação inter-service
    TRANSACTION_SERVICE_URL = 'http://localhost:5002'
    API_GATEWAY_URL = 'http://localhost:5000'
    
    # Configurações de timeout para requisições HTTP
    REQUEST_TIMEOUT = 30  # segundos
    
    # Configurações de logs
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
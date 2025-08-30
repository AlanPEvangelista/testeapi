# -*- coding: utf-8 -*-
"""
Configuração do Serviço de Transações/Lançamentos
================================================

Este módulo contém as configurações necessárias para o funcionamento
do microservice de transações (lançamentos), incluindo configurações
de banco de dados, URLs de comunicação entre serviços e configurações
da aplicação Flask.

Autor: Sistema Flask Microservices
Data: 2024
"""

import os
from datetime import timedelta

class Config:
    """
    Classe de configuração principal para o serviço de transações.
    
    Contém todas as configurações necessárias para o funcionamento
    adequado do microservice, incluindo banco de dados, segurança
    e comunicação entre serviços.
    """
    
    # Configuração do banco de dados SQLite
    # Caminho relativo para o arquivo de banco de dados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///transaction_database.db'
    
    # Desabilita tracking de modificações para melhor performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Chave secreta para segurança da aplicação Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-transacoes-2024'
    
    # Configurações de debug
    DEBUG = True
    
    # Configuração da porta do serviço
    PORT = 5002
    
    # Host de execução
    HOST = '0.0.0.0'
    
    # URLs de outros microservices para comunicação inter-service
    USER_SERVICE_URL = 'http://localhost:5001'
    API_GATEWAY_URL = 'http://localhost:5000'
    
    # Configurações de timeout para requisições HTTP (otimizado para performance local)
    REQUEST_TIMEOUT = 3  # segundos
    
    # Configurações de logs
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurações específicas do serviço de transações
    TIPOS_CARTAO_VALIDOS = ['Crédito', 'Débito', 'Pré-pago']
    
    # Limites de valores para transações
    VALOR_MINIMO_TRANSACAO = 0.01  # R$ 0,01
    VALOR_MAXIMO_TRANSACAO = 99999.99  # R$ 99.999,99
    
    # Configurações de retry para comunicação entre serviços (otimizado para performance)
    MAX_RETRY_ATTEMPTS = 2
    RETRY_DELAY = 0.3  # segundos
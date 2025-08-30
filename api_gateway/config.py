# -*- coding: utf-8 -*-
"""
Configuração do Gateway API
==========================

Este módulo contém as configurações necessárias para o funcionamento
do API Gateway, incluindo roteamento de requisições, URLs dos
microservices e configurações de timeout e retry.

Autor: Sistema Flask Microservices
Data: 2024
"""

import os

class Config:
    """
    Classe de configuração principal para o API Gateway.
    
    Contém todas as configurações necessárias para o funcionamento
    adequado do gateway, incluindo roteamento, timeouts e URLs
    dos microservices.
    """
    
    # Chave secreta para segurança da aplicação Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-gateway-2024'
    
    # Configurações de debug
    DEBUG = True
    
    # Configuração da porta do gateway
    PORT = 5000
    
    # Host de execução
    HOST = '0.0.0.0'
    
    # URLs dos microservices
    USER_SERVICE_URL = 'http://localhost:5001'
    TRANSACTION_SERVICE_URL = 'http://localhost:5002'
    
    # Configurações de timeout para requisições HTTP (otimizado para microservices locais)
    REQUEST_TIMEOUT = 5  # segundos
    
    # Configurações de logs
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurações de retry para comunicação entre serviços (otimizado para performance)
    MAX_RETRY_ATTEMPTS = 2
    RETRY_DELAY = 0.5  # segundos
    
    # Mapeamento de rotas para serviços
    ROUTE_MAPPING = {
        # Rotas do User Service
        '/api/users': 'USER_SERVICE',
        '/api/users/': 'USER_SERVICE',
        
        # Rotas do Transaction Service
        '/api/transactions': 'TRANSACTION_SERVICE',
        '/api/transactions/': 'TRANSACTION_SERVICE',
        
        # Rotas especiais (agregação de dados)
        '/api/reports': 'GATEWAY_INTERNAL'
    }
    
    # Headers a serem removidos das requisições
    HEADERS_TO_REMOVE = [
        'host',
        'content-length',
        'transfer-encoding',
        'connection'
    ]
    
    # Health check endpoints dos serviços
    HEALTH_CHECK_ENDPOINTS = {
        'user_service': '/users/health',
        'transaction_service': '/transactions/health'
    }
    
    # Configurações de cache (futuro)
    CACHE_ENABLED = False
    CACHE_TIMEOUT = 300  # 5 minutos
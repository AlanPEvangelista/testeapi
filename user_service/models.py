# -*- coding: utf-8 -*-
"""
Modelos de Dados do Serviço de Usuários
======================================

Este módulo define os modelos de dados para o microservice de usuários,
incluindo a tabela 'usuarios' com todos os campos necessários para
gerenciamento de usuários no sistema.

Tabela: usuarios
- id: Identificador único do usuário
- nome: Nome completo do usuário
- email: Email único do usuário
- data_criacao: Data e hora de criação da conta

Autor: Sistema Flask Microservices
Data: 2024
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

# Instância do SQLAlchemy para este serviço
db = SQLAlchemy()

class Usuario(db.Model):
    """
    Modelo de dados para a tabela de usuários.
    
    Esta classe representa um usuário no sistema e define
    todos os campos necessários para o gerenciamento de contas
    de usuário, incluindo validações básicas.
    
    Attributes:
        id (int): Chave primária única do usuário
        nome (str): Nome completo do usuário (até 100 caracteres)
        email (str): Email único do usuário (até 150 caracteres)
        data_criacao (datetime): Timestamp de criação da conta
    """
    
    # Nome da tabela no banco de dados
    __tablename__ = 'usuarios'
    
    # Campos da tabela
    id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True,
        comment='Identificador único do usuário'
    )
    
    nome = db.Column(
        db.String(100), 
        nullable=False,
        comment='Nome completo do usuário'
    )
    
    email = db.Column(
        db.String(150), 
        unique=True, 
        nullable=False,
        comment='Email único do usuário'
    )
    
    data_criacao = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        comment='Data e hora de criação da conta'
    )
    
    def __init__(self, nome, email):
        """
        Construtor da classe Usuario.
        
        Args:
            nome (str): Nome completo do usuário
            email (str): Email do usuário
            
        Raises:
            ValueError: Se os dados fornecidos forem inválidos
        """
        self.nome = nome
        self.email = email
        self._validar_dados()
    
    def _validar_dados(self):
        """
        Valida os dados do usuário antes de salvá-los no banco.
        
        Verifica se o nome não está vazio, se o email tem formato válido
        e se todos os campos obrigatórios foram preenchidos.
        
        Raises:
            ValueError: Se algum dado for inválido
        """
        # Validação do nome
        if not self.nome or len(self.nome.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres")
        
        # Validação do email
        if not self.email or not self._validar_email(self.email):
            raise ValueError("Email deve ter formato válido")
        
        # Normalização dos dados
        self.nome = self.nome.strip()
        self.email = self.email.lower().strip()
    
    def _validar_email(self, email):
        """
        Valida o formato do email usando regex.
        
        Args:
            email (str): Email a ser validado
            
        Returns:
            bool: True se o email for válido, False caso contrário
        """
        padrao_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao_email, email) is not None
    
    def to_dict(self):
        """
        Converte o objeto Usuario para um dicionário.
        
        Útil para serialização JSON e retorno de dados via API.
        
        Returns:
            dict: Dicionário com os dados do usuário
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
    
    def atualizar_dados(self, nome=None, email=None):
        """
        Atualiza os dados do usuário.
        
        Args:
            nome (str, optional): Novo nome do usuário
            email (str, optional): Novo email do usuário
            
        Raises:
            ValueError: Se os novos dados forem inválidos
        """
        if nome is not None:
            self.nome = nome
        
        if email is not None:
            self.email = email
        
        # Revalida os dados após atualização
        self._validar_dados()
    
    def __repr__(self):
        """
        Representação string do objeto Usuario.
        
        Returns:
            str: Representação legível do usuário
        """
        return f'<Usuario {self.id}: {self.nome} ({self.email})>'
    
    @staticmethod
    def buscar_por_email(email):
        """
        Busca um usuário pelo email.
        
        Args:
            email (str): Email do usuário a ser buscado
            
        Returns:
            Usuario or None: Usuário encontrado ou None se não existir
        """
        return Usuario.query.filter_by(email=email.lower().strip()).first()
    
    @staticmethod
    def email_ja_existe(email, excluir_id=None):
        """
        Verifica se um email já está cadastrado no sistema.
        
        Args:
            email (str): Email a ser verificado
            excluir_id (int, optional): ID do usuário a ser excluído da verificação
                                      (útil para atualizações)
        
        Returns:
            bool: True se o email já existe, False caso contrário
        """
        query = Usuario.query.filter_by(email=email.lower().strip())
        
        if excluir_id:
            query = query.filter(Usuario.id != excluir_id)
        
        return query.first() is not None
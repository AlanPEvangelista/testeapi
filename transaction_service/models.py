# -*- coding: utf-8 -*-
"""
Modelos de Dados do Serviço de Transações
========================================

Este módulo define os modelos de dados para o microservice de transações,
incluindo a tabela 'lancamentos' com todos os campos necessários para
gerenciamento de transações financeiras no sistema.

Tabela: lancamentos
- id: Identificador único da transação
- usuario_id: ID do usuário (referência ao User Service)
- descricao: Descrição da transação
- valor: Valor da transação
- cartao_tipo: Tipo do cartão (Crédito, Débito, Pré-pago)
- cartao_final: Últimos 4 dígitos do cartão
- data_lancamento: Data e hora da transação

Autor: Sistema Flask Microservices
Data: 2024
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from decimal import Decimal, InvalidOperation

# Instância do SQLAlchemy para este serviço
db = SQLAlchemy()

class Lancamento(db.Model):
    """
    Modelo de dados para a tabela de lançamentos (transações).
    
    Esta classe representa uma transação financeira no sistema e define
    todos os campos necessários para o gerenciamento de lançamentos,
    incluindo validações específicas para dados financeiros.
    
    Attributes:
        id (int): Chave primária única da transação
        usuario_id (int): ID do usuário que fez a transação
        descricao (str): Descrição da transação (até 255 caracteres)
        valor (Decimal): Valor da transação (precision 10, scale 2)
        cartao_tipo (str): Tipo do cartão (Crédito, Débito, Pré-pago)
        cartao_final (str): Últimos 4 dígitos do cartão
        data_lancamento (datetime): Timestamp da transação
    """
    
    # Nome da tabela no banco de dados
    __tablename__ = 'lancamentos'
    
    # Campos da tabela
    id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True,
        comment='Identificador único da transação'
    )
    
    usuario_id = db.Column(
        db.Integer, 
        nullable=False,
        comment='ID do usuário que fez a transação'
    )
    
    descricao = db.Column(
        db.String(255), 
        nullable=False,
        comment='Descrição da transação'
    )
    
    valor = db.Column(
        db.Numeric(10, 2), 
        nullable=False,
        comment='Valor da transação'
    )
    
    cartao_tipo = db.Column(
        db.String(20), 
        nullable=False,
        comment='Tipo do cartão (Crédito, Débito, Pré-pago)'
    )
    
    cartao_final = db.Column(
        db.String(4), 
        nullable=False,
        comment='Últimos 4 dígitos do cartão'
    )
    
    data_lancamento = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        comment='Data e hora da transação'
    )
    
    def __init__(self, usuario_id, descricao, valor, cartao_tipo, cartao_final):
        """
        Construtor da classe Lancamento.
        
        Args:
            usuario_id (int): ID do usuário que fez a transação
            descricao (str): Descrição da transação
            valor (float/Decimal): Valor da transação
            cartao_tipo (str): Tipo do cartão
            cartao_final (str): Últimos 4 dígitos do cartão
            
        Raises:
            ValueError: Se os dados fornecidos forem inválidos
        """
        self.usuario_id = usuario_id
        self.descricao = descricao
        self.valor = valor
        self.cartao_tipo = cartao_tipo
        self.cartao_final = cartao_final
        self._validar_dados()
    
    def _validar_dados(self):
        """
        Valida os dados da transação antes de salvá-los no banco.
        
        Verifica se todos os campos obrigatórios foram preenchidos,
        se o valor é válido, se o tipo de cartão é aceito e se
        os últimos dígitos do cartão são válidos.
        
        Raises:
            ValueError: Se algum dado for inválido
        """
        # Validação do usuario_id
        if not isinstance(self.usuario_id, int) or self.usuario_id <= 0:
            raise ValueError("ID do usuário deve ser um número inteiro positivo")
        
        # Validação da descrição
        if not self.descricao or len(self.descricao.strip()) < 3:
            raise ValueError("Descrição deve ter pelo menos 3 caracteres")
        
        if len(self.descricao.strip()) > 255:
            raise ValueError("Descrição não pode exceder 255 caracteres")
        
        # Validação do valor
        self._validar_valor()
        
        # Validação do tipo de cartão
        self._validar_tipo_cartao()
        
        # Validação dos últimos dígitos do cartão
        self._validar_cartao_final()
        
        # Normalização dos dados
        self.descricao = self.descricao.strip()
        self.cartao_tipo = self.cartao_tipo.strip()
        self.cartao_final = self.cartao_final.strip()
    
    def _validar_valor(self):
        """
        Valida o valor da transação.
        
        Verifica se o valor é numérico, positivo e está dentro dos
        limites estabelecidos para transações.
        
        Raises:
            ValueError: Se o valor for inválido
        """
        try:
            # Converte para Decimal para precisão monetária
            if isinstance(self.valor, str):
                # Remove espaços e troca vírgula por ponto se necessário
                valor_limpo = self.valor.strip().replace(',', '.')
                self.valor = Decimal(valor_limpo)
            elif isinstance(self.valor, (int, float)):
                self.valor = Decimal(str(self.valor))
            elif not isinstance(self.valor, Decimal):
                raise ValueError("Valor deve ser numérico")
            
            # Verifica se o valor é positivo
            if self.valor <= 0:
                raise ValueError("Valor da transação deve ser positivo")
            
            # Verifica limites (importados da configuração se disponível)
            valor_minimo = Decimal('0.01')  # R$ 0,01
            valor_maximo = Decimal('99999.99')  # R$ 99.999,99
            
            if self.valor < valor_minimo:
                raise ValueError(f"Valor mínimo para transação é R$ {valor_minimo}")
            
            if self.valor > valor_maximo:
                raise ValueError(f"Valor máximo para transação é R$ {valor_maximo}")
            
            # Verifica se tem no máximo 2 casas decimais
            if self.valor.as_tuple().exponent < -2:
                raise ValueError("Valor deve ter no máximo 2 casas decimais")
                
        except (InvalidOperation, ValueError) as e:
            if "Valor deve ser numérico" in str(e):
                raise e
            raise ValueError("Formato de valor inválido")
    
    def _validar_tipo_cartao(self):
        """
        Valida o tipo de cartão.
        
        Verifica se o tipo de cartão está na lista de tipos aceitos.
        
        Raises:
            ValueError: Se o tipo de cartão for inválido
        """
        tipos_validos = ['Crédito', 'Débito', 'Pré-pago']
        
        if not self.cartao_tipo or self.cartao_tipo.strip() not in tipos_validos:
            raise ValueError(f"Tipo de cartão deve ser um dos seguintes: {', '.join(tipos_validos)}")
    
    def _validar_cartao_final(self):
        """
        Valida os últimos dígitos do cartão.
        
        Verifica se contém exatamente 4 dígitos numéricos.
        
        Raises:
            ValueError: Se os dígitos do cartão forem inválidos
        """
        if not self.cartao_final:
            raise ValueError("Últimos 4 dígitos do cartão são obrigatórios")
        
        # Remove espaços e verifica se são 4 dígitos
        cartao_limpo = self.cartao_final.strip()
        
        if len(cartao_limpo) != 4:
            raise ValueError("Devem ser fornecidos exatamente 4 dígitos do cartão")
        
        if not cartao_limpo.isdigit():
            raise ValueError("Últimos dígitos do cartão devem ser numéricos")
        
        self.cartao_final = cartao_limpo
    
    def to_dict(self):
        """
        Converte o objeto Lancamento para um dicionário.
        
        Útil para serialização JSON e retorno de dados via API.
        
        Returns:
            dict: Dicionário com os dados da transação
        """
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'descricao': self.descricao,
            'valor': float(self.valor),
            'cartao_tipo': self.cartao_tipo,
            'cartao_final': self.cartao_final,
            'data_lancamento': self.data_lancamento.isoformat() if self.data_lancamento else None
        }
    
    def atualizar_dados(self, descricao=None, valor=None, cartao_tipo=None, cartao_final=None):
        """
        Atualiza os dados da transação.
        
        Note: O usuario_id não pode ser alterado após criação por questões de auditoria.
        
        Args:
            descricao (str, optional): Nova descrição da transação
            valor (float/Decimal, optional): Novo valor da transação
            cartao_tipo (str, optional): Novo tipo de cartão
            cartao_final (str, optional): Novos últimos dígitos do cartão
            
        Raises:
            ValueError: Se os novos dados forem inválidos
        """
        # Valida cada campo individualmente antes de atualizar
        if descricao is not None:
            # Validação da descrição
            if not descricao or len(descricao.strip()) < 3:
                raise ValueError("Descrição deve ter pelo menos 3 caracteres")
            if len(descricao.strip()) > 255:
                raise ValueError("Descrição não pode exceder 255 caracteres")
            self.descricao = descricao.strip()
        
        if valor is not None:
            # Validação do valor
            old_valor = self.valor
            self.valor = valor
            try:
                self._validar_valor()
            except ValueError:
                self.valor = old_valor  # Reverte se inválido
                raise
        
        if cartao_tipo is not None:
            # Validação do tipo de cartão
            tipos_validos = ['Crédito', 'Débito', 'Pré-pago']
            if not cartao_tipo or cartao_tipo.strip() not in tipos_validos:
                raise ValueError(f"Tipo de cartão deve ser um dos seguintes: {', '.join(tipos_validos)}")
            self.cartao_tipo = cartao_tipo.strip()
        
        if cartao_final is not None:
            # Validação dos últimos dígitos do cartão
            if not cartao_final:
                raise ValueError("Últimos 4 dígitos do cartão são obrigatórios")
            cartao_limpo = cartao_final.strip()
            if len(cartao_limpo) != 4:
                raise ValueError("Devem ser fornecidos exatamente 4 dígitos do cartão")
            if not cartao_limpo.isdigit():
                raise ValueError("Últimos dígitos do cartão devem ser numéricos")
            self.cartao_final = cartao_limpo
    
    def __repr__(self):
        """
        Representação string do objeto Lancamento.
        
        Returns:
            str: Representação legível da transação
        """
        return f'<Lancamento {self.id}: R$ {self.valor} - {self.descricao[:30]}>'
    
    @staticmethod
    def buscar_por_usuario(usuario_id):
        """
        Busca todas as transações de um usuário específico.
        
        Args:
            usuario_id (int): ID do usuário
            
        Returns:
            List[Lancamento]: Lista de transações do usuário
        """
        return Lancamento.query.filter_by(usuario_id=usuario_id).order_by(
            Lancamento.data_lancamento.desc()
        ).all()
    
    @staticmethod
    def calcular_total_usuario(usuario_id):
        """
        Calcula o total gasto por um usuário.
        
        Args:
            usuario_id (int): ID do usuário
            
        Returns:
            Decimal: Total gasto pelo usuário
        """
        resultado = db.session.query(
            db.func.sum(Lancamento.valor)
        ).filter_by(usuario_id=usuario_id).scalar()
        
        return resultado or Decimal('0.00')
    
    @staticmethod
    def estatisticas_por_tipo_cartao(usuario_id=None):
        """
        Retorna estatísticas de uso por tipo de cartão.
        
        Args:
            usuario_id (int, optional): ID do usuário (se None, considera todos)
            
        Returns:
            dict: Estatísticas de uso por tipo de cartão
        """
        query = db.session.query(
            Lancamento.cartao_tipo,
            db.func.count(Lancamento.id).label('quantidade'),
            db.func.sum(Lancamento.valor).label('total')
        )
        
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        resultado = query.group_by(Lancamento.cartao_tipo).all()
        
        estatisticas = {}
        for tipo, quantidade, total in resultado:
            estatisticas[tipo] = {
                'quantidade': quantidade,
                'total': float(total or 0)
            }
        
        return estatisticas
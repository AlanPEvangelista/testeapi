# -*- coding: utf-8 -*-
"""
Rotas do Serviço de Usuários
============================

Este módulo define todas as rotas/endpoints da API REST para o
microservice de usuários. Inclui operações CRUD completas para
gerenciamento de usuários no sistema.

Endpoints disponíveis:
- GET /users - Lista todos os usuários
- GET /users/<id> - Busca usuário por ID
- POST /users - Cria novo usuário
- PUT /users/<id> - Atualiza usuário existente
- DELETE /users/<id> - Remove usuário do sistema

Autor: Sistema Flask Microservices
Data: 2024
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from models import db, Usuario
import logging

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)

# Criação do Blueprint para as rotas de usuários
user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/users', methods=['GET'])
def listar_usuarios():
    """
    Lista todos os usuários cadastrados no sistema.
    
    Returns:
        JSON: Lista de todos os usuários com seus dados
        Status: 200 (sucesso) ou 500 (erro interno)
    
    Exemplo de retorno:
    [
        {
            "id": 1,
            "nome": "João Silva",
            "email": "joao@email.com",
            "data_criacao": "2024-01-15T10:30:00"
        }
    ]
    """
    try:
        logger.info("Solicitação para listar todos os usuários")
        
        # Busca todos os usuários no banco de dados
        usuarios = Usuario.query.all()
        
        # Converte os objetos Usuario para dicionários
        usuarios_dict = [usuario.to_dict() for usuario in usuarios]
        
        logger.info(f"Encontrados {len(usuarios_dict)} usuários")
        
        return jsonify(usuarios_dict), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível recuperar a lista de usuários'
        }), 500

@user_routes.route('/users/<int:user_id>', methods=['GET'])
def buscar_usuario_por_id(user_id):
    """
    Busca um usuário específico pelo ID.
    
    Args:
        user_id (int): ID do usuário a ser buscado
        
    Returns:
        JSON: Dados do usuário encontrado ou mensagem de erro
        Status: 200 (encontrado), 404 (não encontrado) ou 500 (erro)
    """
    try:
        logger.info(f"Buscando usuário com ID: {user_id}")
        
        # Busca o usuário pelo ID
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            logger.warning(f"Usuário com ID {user_id} não encontrado")
            return jsonify({
                'erro': 'Usuário não encontrado',
                'mensagem': f'Não existe usuário com ID {user_id}'
            }), 404
        
        logger.info(f"Usuário encontrado: {usuario.nome}")
        return jsonify(usuario.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar usuário {user_id}: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível buscar o usuário'
        }), 500

@user_routes.route('/users', methods=['POST'])
def criar_usuario():
    """
    Cria um novo usuário no sistema.
    
    Espera receber JSON com:
    {
        "nome": "Nome do usuário",
        "email": "email@exemplo.com"
    }
    
    Returns:
        JSON: Dados do usuário criado ou mensagem de erro
        Status: 201 (criado), 400 (dados inválidos) ou 500 (erro)
    """
    try:
        # Verifica se os dados foram enviados em formato JSON
        if not request.is_json:
            return jsonify({
                'erro': 'Formato inválido',
                'mensagem': 'Os dados devem ser enviados em formato JSON'
            }), 400
        
        dados = request.get_json()
        logger.info(f"Solicitação para criar usuário: {dados.get('email', 'N/A')}")
        
        # Validação dos campos obrigatórios
        if not dados.get('nome'):
            return jsonify({
                'erro': 'Campo obrigatório',
                'mensagem': 'O campo "nome" é obrigatório'
            }), 400
        
        if not dados.get('email'):
            return jsonify({
                'erro': 'Campo obrigatório',
                'mensagem': 'O campo "email" é obrigatório'
            }), 400
        
        # Verifica se o email já está cadastrado
        if Usuario.email_ja_existe(dados['email']):
            logger.warning(f"Tentativa de cadastro com email já existente: {dados['email']}")
            return jsonify({
                'erro': 'Email já cadastrado',
                'mensagem': 'Este email já está sendo usado por outro usuário'
            }), 400
        
        # Cria o novo usuário
        novo_usuario = Usuario(
            nome=dados['nome'],
            email=dados['email']
        )
        
        # Salva no banco de dados
        db.session.add(novo_usuario)
        db.session.commit()
        
        logger.info(f"Usuário criado com sucesso: ID {novo_usuario.id}")
        
        return jsonify(novo_usuario.to_dict()), 201
        
    except ValueError as e:
        # Erro de validação dos dados
        logger.warning(f"Dados inválidos para criação de usuário: {str(e)}")
        return jsonify({
            'erro': 'Dados inválidos',
            'mensagem': str(e)
        }), 400
        
    except IntegrityError as e:
        # Erro de integridade do banco (email duplicado, etc.)
        db.session.rollback()
        logger.error(f"Erro de integridade ao criar usuário: {str(e)}")
        return jsonify({
            'erro': 'Violação de integridade',
            'mensagem': 'Email já está cadastrado no sistema'
        }), 400
        
    except Exception as e:
        # Erro interno do servidor
        db.session.rollback()
        logger.error(f"Erro interno ao criar usuário: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível criar o usuário'
        }), 500

@user_routes.route('/users/<int:user_id>', methods=['PUT'])
def atualizar_usuario(user_id):
    """
    Atualiza os dados de um usuário existente.
    
    Args:
        user_id (int): ID do usuário a ser atualizado
        
    Espera receber JSON com campos a serem atualizados:
    {
        "nome": "Novo nome",
        "email": "novo@email.com"
    }
    
    Returns:
        JSON: Dados do usuário atualizado ou mensagem de erro
        Status: 200 (atualizado), 400/404 (erro) ou 500 (erro interno)
    """
    try:
        # Verifica se os dados foram enviados em formato JSON
        if not request.is_json:
            return jsonify({
                'erro': 'Formato inválido',
                'mensagem': 'Os dados devem ser enviados em formato JSON'
            }), 400
        
        dados = request.get_json()
        logger.info(f"Solicitação para atualizar usuário ID: {user_id}")
        
        # Busca o usuário a ser atualizado
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            logger.warning(f"Tentativa de atualizar usuário inexistente: ID {user_id}")
            return jsonify({
                'erro': 'Usuário não encontrado',
                'mensagem': f'Não existe usuário com ID {user_id}'
            }), 404
        
        # Verifica se há algo para atualizar
        if not dados.get('nome') and not dados.get('email'):
            return jsonify({
                'erro': 'Nenhum dado fornecido',
                'mensagem': 'Pelo menos um campo (nome ou email) deve ser fornecido'
            }), 400
        
        # Verifica se o novo email já está sendo usado por outro usuário
        if dados.get('email') and Usuario.email_ja_existe(dados['email'], excluir_id=user_id):
            logger.warning(f"Tentativa de atualizar com email já existente: {dados['email']}")
            return jsonify({
                'erro': 'Email já cadastrado',
                'mensagem': 'Este email já está sendo usado por outro usuário'
            }), 400
        
        # Atualiza os dados do usuário
        usuario.atualizar_dados(
            nome=dados.get('nome'),
            email=dados.get('email')
        )
        
        # Salva as alterações no banco
        db.session.commit()
        
        logger.info(f"Usuário {user_id} atualizado com sucesso")
        
        return jsonify(usuario.to_dict()), 200
        
    except ValueError as e:
        # Erro de validação dos dados
        logger.warning(f"Dados inválidos para atualização: {str(e)}")
        return jsonify({
            'erro': 'Dados inválidos',
            'mensagem': str(e)
        }), 400
        
    except IntegrityError as e:
        # Erro de integridade do banco
        db.session.rollback()
        logger.error(f"Erro de integridade ao atualizar usuário: {str(e)}")
        return jsonify({
            'erro': 'Violação de integridade',
            'mensagem': 'Email já está cadastrado no sistema'
        }), 400
        
    except Exception as e:
        # Erro interno do servidor
        db.session.rollback()
        logger.error(f"Erro interno ao atualizar usuário {user_id}: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível atualizar o usuário'
        }), 500

@user_routes.route('/users/<int:user_id>', methods=['DELETE'])
def deletar_usuario(user_id):
    """
    Remove um usuário do sistema.
    
    Args:
        user_id (int): ID do usuário a ser removido
        
    Returns:
        JSON: Mensagem de confirmação ou erro
        Status: 204 (removido), 404 (não encontrado) ou 500 (erro)
    """
    try:
        logger.info(f"Solicitação para deletar usuário ID: {user_id}")
        
        # Busca o usuário a ser removido
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            logger.warning(f"Tentativa de deletar usuário inexistente: ID {user_id}")
            return jsonify({
                'erro': 'Usuário não encontrado',
                'mensagem': f'Não existe usuário com ID {user_id}'
            }), 404
        
        # Armazena informações para log antes de deletar
        nome_usuario = usuario.nome
        email_usuario = usuario.email
        
        # Remove o usuário do banco de dados
        db.session.delete(usuario)
        db.session.commit()
        
        logger.info(f"Usuário removido: {nome_usuario} ({email_usuario})")
        
        return jsonify({
            'mensagem': 'Usuário removido com sucesso',
            'usuario_removido': {
                'id': user_id,
                'nome': nome_usuario,
                'email': email_usuario
            }
        }), 200
        
    except Exception as e:
        # Erro interno do servidor
        db.session.rollback()
        logger.error(f"Erro interno ao deletar usuário {user_id}: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível remover o usuário'
        }), 500

@user_routes.route('/users/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificação de saúde do serviço.
    
    Útil para monitoramento e verificação se o serviço está funcionando.
    
    Returns:
        JSON: Status do serviço
        Status: 200 (sempre)
    """
    return jsonify({
        'servico': 'User Service',
        'status': 'ativo',
        'versao': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Importação necessária para o health check
from datetime import datetime
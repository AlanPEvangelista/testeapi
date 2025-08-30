# -*- coding: utf-8 -*-
"""
Rotas do Serviço de Transações/Lançamentos
=========================================

Este módulo define todas as rotas/endpoints da API REST para o
microservice de transações. Inclui operações CRUD para gerenciamento
de lançamentos e comunicação com o User Service para validação.

Endpoints disponíveis:
- GET /transactions - Lista todas as transações
- GET /transactions/<id> - Busca transação por ID
- GET /transactions/user/<user_id> - Lista transações de um usuário
- POST /transactions - Cria nova transação
- PUT /transactions/<id> - Atualiza transação existente
- DELETE /transactions/<id> - Remove transação
- GET /transactions/stats/user/<user_id> - Estatísticas do usuário

Autor: Sistema Flask Microservices
Data: 2024
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from models import db, Lancamento
import logging
import requests
from datetime import datetime

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)

# Criação do Blueprint para as rotas de transações
transaction_routes = Blueprint('transaction_routes', __name__)

def verificar_usuario_existe(usuario_id):
    """
    Verifica se um usuário existe através do User Service.
    
    Esta função faz uma requisição HTTP para o User Service
    para validar se o usuário existe antes de criar/atualizar transações.
    
    Args:
        usuario_id (int): ID do usuário a ser verificado
        
    Returns:
        tuple: (bool, dict) - (existe, dados_usuario ou erro)
    """
    try:
        user_service_url = current_app.config['USER_SERVICE_URL']
        timeout = current_app.config['REQUEST_TIMEOUT']
        
        # Faz requisição para o User Service
        url = f"{user_service_url}/users/{usuario_id}"
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 404:
            return False, {'erro': 'Usuário não encontrado'}
        else:
            logger.error(f"Erro inesperado do User Service: {response.status_code}")
            return False, {'erro': 'Erro na validação do usuário'}
            
    except requests.exceptions.Timeout:
        logger.error("Timeout na comunicação com User Service")
        return False, {'erro': 'Timeout na validação do usuário'}
    except requests.exceptions.ConnectionError:
        logger.error("Erro de conexão com User Service")
        return False, {'erro': 'Serviço de usuários indisponível'}
    except Exception as e:
        logger.error(f"Erro inesperado na validação do usuário: {str(e)}")
        return False, {'erro': 'Erro interno na validação do usuário'}

@transaction_routes.route('/transactions', methods=['GET'])
def listar_transacoes():
    """
    Lista todas as transações cadastradas no sistema.
    
    Suporta parâmetros de query para filtros opcionais:
    - limit: número máximo de registros (padrão: 100)
    - offset: número de registros para pular (padrão: 0)
    
    Returns:
        JSON: Lista de todas as transações com seus dados
        Status: 200 (sucesso) ou 500 (erro interno)
    """
    try:
        logger.info("Solicitação para listar todas as transações")
        
        # Parâmetros de paginação opcionais
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Busca as transações com paginação
        transacoes = Lancamento.query.order_by(
            Lancamento.data_lancamento.desc()
        ).limit(limit).offset(offset).all()
        
        # Converte os objetos para dicionários
        transacoes_dict = [transacao.to_dict() for transacao in transacoes]
        
        # Informações adicionais sobre a consulta
        total_transacoes = Lancamento.query.count()
        
        logger.info(f"Retornadas {len(transacoes_dict)} de {total_transacoes} transações")
        
        return jsonify({
            'transacoes': transacoes_dict,
            'total': total_transacoes,
            'limit': limit,
            'offset': offset,
            'count': len(transacoes_dict)
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar transações: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível recuperar a lista de transações'
        }), 500

@transaction_routes.route('/transactions/<int:transaction_id>', methods=['GET'])
def buscar_transacao_por_id(transaction_id):
    """
    Busca uma transação específica pelo ID.
    
    Args:
        transaction_id (int): ID da transação a ser buscada
        
    Returns:
        JSON: Dados da transação encontrada ou mensagem de erro
        Status: 200 (encontrado), 404 (não encontrado) ou 500 (erro)
    """
    try:
        logger.info(f"Buscando transação com ID: {transaction_id}")
        
        # Busca a transação pelo ID
        transacao = Lancamento.query.get(transaction_id)
        
        if not transacao:
            logger.warning(f"Transação com ID {transaction_id} não encontrada")
            return jsonify({
                'erro': 'Transação não encontrada',
                'mensagem': f'Não existe transação com ID {transaction_id}'
            }), 404
        
        logger.info(f"Transação encontrada: {transacao.descricao}")
        return jsonify(transacao.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar transação {transaction_id}: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível buscar a transação'
        }), 500

@transaction_routes.route('/transactions/user/<int:user_id>', methods=['GET'])
def buscar_transacoes_por_usuario(user_id):
    """
    Busca todas as transações de um usuário específico.
    
    Args:
        user_id (int): ID do usuário
        
    Returns:
        JSON: Lista das transações do usuário ou mensagem de erro
        Status: 200 (sucesso), 404 (usuário não encontrado) ou 500 (erro)
    """
    try:
        logger.info(f"Buscando transações do usuário ID: {user_id}")
        
        # Verifica se o usuário existe
        usuario_existe, usuario_dados = verificar_usuario_existe(user_id)
        
        if not usuario_existe:
            logger.warning(f"Usuário {user_id} não encontrado")
            return jsonify({
                'erro': 'Usuário não encontrado',
                'mensagem': f'Não existe usuário com ID {user_id}'
            }), 404
        
        # Busca as transações do usuário
        transacoes = Lancamento.buscar_por_usuario(user_id)
        transacoes_dict = [transacao.to_dict() for transacao in transacoes]
        
        # Calcula estatísticas do usuário
        total_gasto = float(Lancamento.calcular_total_usuario(user_id))
        estatisticas_cartao = Lancamento.estatisticas_por_tipo_cartao(user_id)
        
        logger.info(f"Encontradas {len(transacoes_dict)} transações para usuário {user_id}")
        
        return jsonify({
            'usuario': usuario_dados,
            'transacoes': transacoes_dict,
            'resumo': {
                'total_transacoes': len(transacoes_dict),
                'total_gasto': total_gasto,
                'estatisticas_por_cartao': estatisticas_cartao
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar transações do usuário {user_id}: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível buscar as transações do usuário'
        }), 500

@transaction_routes.route('/transactions', methods=['POST'])
def criar_transacao():
    """
    Cria uma nova transação no sistema.
    
    Espera receber JSON com:
    {
        "usuario_id": 1,
        "descricao": "Compra Amazon",
        "valor": 150.99,
        "cartao_tipo": "Crédito",
        "cartao_final": "1234"
    }
    
    Returns:
        JSON: Dados da transação criada ou mensagem de erro
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
        logger.info(f"Solicitação para criar transação para usuário: {dados.get('usuario_id', 'N/A')}")
        
        # Validação dos campos obrigatórios
        campos_obrigatorios = ['usuario_id', 'descricao', 'valor', 'cartao_tipo', 'cartao_final']
        for campo in campos_obrigatorios:
            if campo not in dados or dados[campo] is None:
                return jsonify({
                    'erro': 'Campo obrigatório',
                    'mensagem': f'O campo "{campo}" é obrigatório'
                }), 400
        
        # Verifica se o usuário existe
        usuario_existe, usuario_dados = verificar_usuario_existe(dados['usuario_id'])
        
        if not usuario_existe:
            logger.warning(f"Tentativa de criar transação para usuário inexistente: {dados['usuario_id']}")
            return jsonify({
                'erro': 'Usuário não encontrado',
                'mensagem': 'O usuário especificado não existe no sistema'
            }), 400
        
        # Cria a nova transação
        nova_transacao = Lancamento(
            usuario_id=dados['usuario_id'],
            descricao=dados['descricao'],
            valor=dados['valor'],
            cartao_tipo=dados['cartao_tipo'],
            cartao_final=dados['cartao_final']
        )
        
        # Salva no banco de dados
        db.session.add(nova_transacao)
        db.session.commit()
        
        logger.info(f"Transação criada com sucesso: ID {nova_transacao.id}")
        
        return jsonify(nova_transacao.to_dict()), 201
        
    except ValueError as e:
        # Erro de validação dos dados
        logger.warning(f"Dados inválidos para criação de transação: {str(e)}")
        return jsonify({
            'erro': 'Dados inválidos',
            'mensagem': str(e)
        }), 400
        
    except Exception as e:
        # Erro interno do servidor
        db.session.rollback()
        logger.error(f"Erro interno ao criar transação: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível criar a transação'
        }), 500

@transaction_routes.route('/transactions/<int:transaction_id>', methods=['PUT'])
def atualizar_transacao(transaction_id):
    """
    Atualiza os dados de uma transação existente.
    
    Note: O usuario_id não pode ser alterado por questões de auditoria.
    
    Args:
        transaction_id (int): ID da transação a ser atualizada
        
    Returns:
        JSON: Dados da transação atualizada ou mensagem de erro
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
        logger.info(f"Solicitação para atualizar transação ID: {transaction_id}")
        
        # Busca a transação a ser atualizada
        transacao = Lancamento.query.get(transaction_id)
        
        if not transacao:
            logger.warning(f"Tentativa de atualizar transação inexistente: ID {transaction_id}")
            return jsonify({
                'erro': 'Transação não encontrada',
                'mensagem': f'Não existe transação com ID {transaction_id}'
            }), 404
        
        # Verifica se há algo para atualizar
        campos_atualizaveis = ['descricao', 'valor', 'cartao_tipo', 'cartao_final']
        tem_atualizacao = any(campo in dados for campo in campos_atualizaveis)
        
        if not tem_atualizacao:
            return jsonify({
                'erro': 'Nenhum dado fornecido',
                'mensagem': 'Pelo menos um campo deve ser fornecido para atualização'
            }), 400
        
        # Alerta sobre tentativa de alterar usuario_id
        if 'usuario_id' in dados:
            logger.warning(f"Tentativa de alterar usuario_id na transação {transaction_id}")
            return jsonify({
                'erro': 'Campo não alterável',
                'mensagem': 'O ID do usuário não pode ser alterado por questões de auditoria'
            }), 400
        
        # Atualiza os dados da transação
        transacao.atualizar_dados(
            descricao=dados.get('descricao'),
            valor=dados.get('valor'),
            cartao_tipo=dados.get('cartao_tipo'),
            cartao_final=dados.get('cartao_final')
        )
        
        # Salva as alterações no banco
        db.session.commit()
        
        logger.info(f"Transação {transaction_id} atualizada com sucesso")
        
        return jsonify(transacao.to_dict()), 200
        
    except ValueError as e:
        # Erro de validação dos dados
        logger.warning(f"Dados inválidos para atualização: {str(e)}")
        return jsonify({
            'erro': 'Dados inválidos',
            'mensagem': str(e)
        }), 400
        
    except Exception as e:
        # Erro interno do servidor
        db.session.rollback()
        logger.error(f"Erro interno ao atualizar transação {transaction_id}: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível atualizar a transação'
        }), 500

@transaction_routes.route('/transactions/<int:transaction_id>', methods=['DELETE'])
def deletar_transacao(transaction_id):
    """
    Remove uma transação do sistema.
    
    Args:
        transaction_id (int): ID da transação a ser removida
        
    Returns:
        JSON: Mensagem de confirmação ou erro
        Status: 200 (removido), 404 (não encontrado) ou 500 (erro)
    """
    try:
        logger.info(f"Solicitação para deletar transação ID: {transaction_id}")
        
        # Busca a transação a ser removida
        transacao = Lancamento.query.get(transaction_id)
        
        if not transacao:
            logger.warning(f"Tentativa de deletar transação inexistente: ID {transaction_id}")
            return jsonify({
                'erro': 'Transação não encontrada',
                'mensagem': f'Não existe transação com ID {transaction_id}'
            }), 404
        
        # Armazena informações para log antes de deletar
        descricao_transacao = transacao.descricao
        valor_transacao = float(transacao.valor)
        usuario_id = transacao.usuario_id
        
        # Remove a transação do banco de dados
        db.session.delete(transacao)
        db.session.commit()
        
        logger.info(f"Transação removida: {descricao_transacao} - R$ {valor_transacao}")
        
        return jsonify({
            'mensagem': 'Transação removida com sucesso',
            'transacao_removida': {
                'id': transaction_id,
                'descricao': descricao_transacao,
                'valor': valor_transacao,
                'usuario_id': usuario_id
            }
        }), 200
        
    except Exception as e:
        # Erro interno do servidor
        db.session.rollback()
        logger.error(f"Erro interno ao deletar transação {transaction_id}: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível remover a transação'
        }), 500

@transaction_routes.route('/transactions/stats/user/<int:user_id>', methods=['GET'])
def estatisticas_usuario(user_id):
    """
    Retorna estatísticas detalhadas das transações de um usuário.
    
    Args:
        user_id (int): ID do usuário
        
    Returns:
        JSON: Estatísticas completas do usuário
        Status: 200 (sucesso), 404 (usuário não encontrado) ou 500 (erro)
    """
    try:
        logger.info(f"Solicitação de estatísticas para usuário ID: {user_id}")
        
        # Verifica se o usuário existe
        usuario_existe, usuario_dados = verificar_usuario_existe(user_id)
        
        if not usuario_existe:
            logger.warning(f"Usuário {user_id} não encontrado para estatísticas")
            return jsonify({
                'erro': 'Usuário não encontrado',
                'mensagem': f'Não existe usuário com ID {user_id}'
            }), 404
        
        # Calcula estatísticas
        total_transacoes = Lancamento.query.filter_by(usuario_id=user_id).count()
        total_gasto = float(Lancamento.calcular_total_usuario(user_id))
        estatisticas_cartao = Lancamento.estatisticas_por_tipo_cartao(user_id)
        
        # Busca a transação mais recente e mais antiga
        transacao_recente = Lancamento.query.filter_by(usuario_id=user_id).order_by(
            Lancamento.data_lancamento.desc()
        ).first()
        
        transacao_antiga = Lancamento.query.filter_by(usuario_id=user_id).order_by(
            Lancamento.data_lancamento.asc()
        ).first()
        
        # Calcula valores médios
        valor_medio = total_gasto / total_transacoes if total_transacoes > 0 else 0
        
        estatisticas = {
            'usuario': usuario_dados,
            'resumo_geral': {
                'total_transacoes': total_transacoes,
                'total_gasto': total_gasto,
                'valor_medio_transacao': round(valor_medio, 2)
            },
            'por_tipo_cartao': estatisticas_cartao,
            'periodo': {
                'primeira_transacao': transacao_antiga.data_lancamento.isoformat() if transacao_antiga else None,
                'ultima_transacao': transacao_recente.data_lancamento.isoformat() if transacao_recente else None
            }
        }
        
        logger.info(f"Estatísticas calculadas para usuário {user_id}")
        
        return jsonify(estatisticas), 200
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas do usuário {user_id}: {str(e)}")
        return jsonify({
            'erro': 'Erro interno do servidor',
            'mensagem': 'Não foi possível calcular as estatísticas'
        }), 500

@transaction_routes.route('/transactions/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificação de saúde do serviço.
    
    Inclui verificação da conectividade com o User Service.
    
    Returns:
        JSON: Status do serviço e suas dependências
        Status: 200 (sempre)
    """
    # Testa conectividade com User Service
    user_service_status = 'indisponível'
    try:
        user_service_url = current_app.config['USER_SERVICE_URL']
        response = requests.get(f"{user_service_url}/users/health", timeout=5)
        if response.status_code == 200:
            user_service_status = 'ativo'
    except:
        pass
    
    return jsonify({
        'servico': 'Transaction Service',
        'status': 'ativo',
        'versao': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'dependencias': {
            'user_service': user_service_status,
            'database': 'ativo'
        }
    }), 200
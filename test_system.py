# -*- coding: utf-8 -*-
"""
Script de Testes do Sistema Flask Microservices
==============================================

Este script executa uma bateria completa de testes para validar
o funcionamento do sistema de microservices, incluindo:

- Conectividade dos serviços
- CRUD de usuários
- CRUD de transações
- Comunicação entre serviços
- Relatórios agregados
- Validações e tratamento de erros

Autor: Sistema Flask Microservices
Data: 2024
"""

import requests
import json
import time
import sys
from datetime import datetime

class TesteMicroservices:
    """
    Classe para executar testes completos do sistema de microservices.
    """
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.user_service_url = "http://localhost:5001"
        self.transaction_service_url = "http://localhost:5002"
        
        self.testes_executados = 0
        self.testes_passaram = 0
        self.testes_falharam = 0
        
        # IDs criados durante os testes para limpeza
        self.usuarios_criados = []
        self.transacoes_criadas = []
    
    def log(self, mensagem, tipo="INFO"):
        """Log colorido para melhor visualização."""
        cores = {
            "INFO": "\033[94m",  # Azul
            "SUCCESS": "\033[92m",  # Verde
            "ERROR": "\033[91m",  # Vermelho
            "WARNING": "\033[93m",  # Amarelo
            "RESET": "\033[0m"  # Reset
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{cores.get(tipo, '')}{timestamp} [{tipo}] {mensagem}{cores['RESET']}")
    
    def executar_teste(self, nome_teste, funcao_teste):
        """
        Executa um teste individual e registra o resultado.
        
        Args:
            nome_teste (str): Nome descritivo do teste
            funcao_teste (function): Função que executa o teste
        """
        self.log(f"Executando: {nome_teste}")
        self.testes_executados += 1
        
        try:
            resultado = funcao_teste()
            if resultado:
                self.log(f"✓ PASSOU: {nome_teste}", "SUCCESS")
                self.testes_passaram += 1
            else:
                self.log(f"✗ FALHOU: {nome_teste}", "ERROR")
                self.testes_falharam += 1
            return resultado
        except Exception as e:
            self.log(f"✗ ERRO: {nome_teste} - {str(e)}", "ERROR")
            self.testes_falharam += 1
            return False
    
    def fazer_requisicao(self, method, url, data=None, timeout=10):
        """
        Faz requisição HTTP com tratamento de erro padrão.
        
        Args:
            method (str): Método HTTP
            url (str): URL da requisição
            data (dict): Dados para envio (opcional)
            timeout (int): Timeout em segundos
            
        Returns:
            tuple: (sucesso, response ou erro)
        """
        try:
            if method.upper() == 'GET':
                response = requests.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, timeout=timeout)
            else:
                return False, f"Método {method} não suportado"
            
            return True, response
        
        except requests.exceptions.ConnectionError:
            return False, "Erro de conexão - serviço pode estar offline"
        except requests.exceptions.Timeout:
            return False, f"Timeout após {timeout} segundos"
        except Exception as e:
            return False, str(e)
    
    def teste_conectividade_gateway(self):
        """Testa se o API Gateway está respondendo."""
        sucesso, response = self.fazer_requisicao('GET', f"{self.base_url}/")
        if not sucesso:
            return False
        
        return response.status_code == 200
    
    def teste_health_check(self):
        """Testa o health check de todos os serviços."""
        sucesso, response = self.fazer_requisicao('GET', f"{self.base_url}/health")
        if not sucesso:
            return False
        
        if response.status_code != 200:
            return False
        
        dados = response.json()
        return dados.get('gateway_status') == 'ativo'
    
    def teste_conectividade_servicos_diretos(self):
        """Testa conectividade direta com cada microservice."""
        # User Service
        sucesso, response = self.fazer_requisicao('GET', f"{self.user_service_url}/")
        if not sucesso or response.status_code != 200:
            return False
        
        # Transaction Service
        sucesso, response = self.fazer_requisicao('GET', f"{self.transaction_service_url}/")
        if not sucesso or response.status_code != 200:
            return False
        
        return True
    
    def teste_criar_usuario_valido(self):
        """Testa criação de usuário com dados válidos."""
        dados_usuario = {
            "nome": "Teste Usuario",
            "email": f"teste{int(time.time())}@email.com"
        }
        
        sucesso, response = self.fazer_requisicao('POST', f"{self.base_url}/api/users", dados_usuario)
        if not sucesso:
            return False
        
        if response.status_code != 201:
            self.log(f"Status esperado: 201, recebido: {response.status_code}", "ERROR")
            return False
        
        dados_resposta = response.json()
        if 'id' not in dados_resposta:
            return False
        
        # Armazena ID para limpeza posterior
        self.usuarios_criados.append(dados_resposta['id'])
        return True
    
    def teste_criar_usuario_email_duplicado(self):
        """Testa validação de email duplicado."""
        # Primeiro usuário
        dados_usuario = {
            "nome": "Usuario 1",
            "email": "duplicado@email.com"
        }
        
        sucesso, response = self.fazer_requisicao('POST', f"{self.base_url}/api/users", dados_usuario)
        if not sucesso or response.status_code != 201:
            return False
        
        user_id = response.json()['id']
        self.usuarios_criados.append(user_id)
        
        # Segundo usuário com mesmo email
        dados_usuario2 = {
            "nome": "Usuario 2",
            "email": "duplicado@email.com"
        }
        
        sucesso, response = self.fazer_requisicao('POST', f"{self.base_url}/api/users", dados_usuario2)
        if not sucesso:
            return False
        
        # Deve retornar erro 400
        return response.status_code == 400
    
    def teste_listar_usuarios(self):
        """Testa listagem de usuários."""
        sucesso, response = self.fazer_requisicao('GET', f"{self.base_url}/api/users")
        if not sucesso:
            return False
        
        if response.status_code != 200:
            return False
        
        dados = response.json()
        return isinstance(dados, list)
    
    def teste_buscar_usuario_existente(self):
        """Testa busca de usuário existente."""
        if not self.usuarios_criados:
            return False
        
        user_id = self.usuarios_criados[0]
        sucesso, response = self.fazer_requisicao('GET', f"{self.base_url}/api/users/{user_id}")
        if not sucesso:
            return False
        
        return response.status_code == 200
    
    def teste_buscar_usuario_inexistente(self):
        """Testa busca de usuário inexistente."""
        sucesso, response = self.fazer_requisicao('GET', f"{self.base_url}/api/users/99999")
        if not sucesso:
            return False
        
        return response.status_code == 404
    
    def teste_criar_transacao_valida(self):
        """Testa criação de transação com dados válidos."""
        if not self.usuarios_criados:
            return False
        
        dados_transacao = {
            "usuario_id": self.usuarios_criados[0],
            "descricao": "Teste Compra Supermercado",
            "valor": 125.50,
            "cartao_tipo": "Crédito",
            "cartao_final": "1234"
        }
        
        sucesso, response = self.fazer_requisicao('POST', f"{self.base_url}/api/transactions", dados_transacao)
        if not sucesso:
            return False
        
        if response.status_code != 201:
            self.log(f"Status esperado: 201, recebido: {response.status_code}", "ERROR")
            return False
        
        dados_resposta = response.json()
        if 'id' not in dados_resposta:
            return False
        
        self.transacoes_criadas.append(dados_resposta['id'])
        return True
    
    def teste_criar_transacao_usuario_inexistente(self):
        """Testa criação de transação para usuário inexistente."""
        dados_transacao = {
            "usuario_id": 99999,
            "descricao": "Teste Erro",
            "valor": 50.00,
            "cartao_tipo": "Débito",
            "cartao_final": "5678"
        }
        
        sucesso, response = self.fazer_requisicao('POST', f"{self.base_url}/api/transactions", dados_transacao)
        if not sucesso:
            return False
        
        # Deve retornar erro 400 (usuário não encontrado)
        return response.status_code == 400
    
    def teste_criar_transacao_dados_invalidos(self):
        """Testa validações de dados da transação."""
        if not self.usuarios_criados:
            return False
        
        # Teste com valor negativo
        dados_invalidos = {
            "usuario_id": self.usuarios_criados[0],
            "descricao": "Teste Valor Negativo",
            "valor": -50.00,
            "cartao_tipo": "Crédito",
            "cartao_final": "1234"
        }
        
        sucesso, response = self.fazer_requisicao('POST', f"{self.base_url}/api/transactions", dados_invalidos)
        if not sucesso:
            return False
        
        return response.status_code == 400
    
    def teste_listar_transacoes_usuario(self):
        """Testa listagem de transações por usuário."""
        if not self.usuarios_criados:
            return False
        
        user_id = self.usuarios_criados[0]
        sucesso, response = self.fazer_requisicao('GET', f"{self.base_url}/api/transactions/user/{user_id}")
        if not sucesso:
            return False
        
        if response.status_code != 200:
            return False
        
        dados = response.json()
        return 'transacoes' in dados and isinstance(dados['transacoes'], list)
    
    def teste_relatorio_agregado(self):
        """Testa geração de relatório agregado."""
        if not self.usuarios_criados:
            return False
        
        user_id = self.usuarios_criados[0]
        sucesso, response = self.fazer_requisicao('GET', f"{self.base_url}/api/reports/user/{user_id}")
        if not sucesso:
            return False
        
        if response.status_code != 200:
            return False
        
        dados = response.json()
        return all(key in dados for key in ['usuario', 'transacoes', 'metadados'])
    
    def teste_atualizar_usuario(self):
        """Testa atualização de dados do usuário."""
        if not self.usuarios_criados:
            return False
        
        user_id = self.usuarios_criados[0]
        dados_atualizacao = {
            "nome": "Nome Atualizado"
        }
        
        sucesso, response = self.fazer_requisicao('PUT', f"{self.base_url}/api/users/{user_id}", dados_atualizacao)
        if not sucesso:
            return False
        
        return response.status_code == 200
    
    def limpar_dados_teste(self):
        """Remove dados criados durante os testes."""
        self.log("Limpando dados de teste...")
        
        # Remove transações
        for transaction_id in self.transacoes_criadas:
            sucesso, response = self.fazer_requisicao('DELETE', f"{self.base_url}/api/transactions/{transaction_id}")
            if sucesso and response.status_code == 200:
                self.log(f"Transação {transaction_id} removida")
        
        # Remove usuários
        for user_id in self.usuarios_criados:
            sucesso, response = self.fazer_requisicao('DELETE', f"{self.base_url}/api/users/{user_id}")
            if sucesso and response.status_code == 200:
                self.log(f"Usuário {user_id} removido")
    
    def executar_todos_os_testes(self):
        """Executa todos os testes do sistema."""
        self.log("=" * 60)
        self.log("INICIANDO TESTES DO SISTEMA FLASK MICROSERVICES")
        self.log("=" * 60)
        
        # Testes de conectividade
        self.log("\n1. TESTES DE CONECTIVIDADE", "WARNING")
        self.executar_teste("Gateway respondendo", self.teste_conectividade_gateway)
        self.executar_teste("Health check completo", self.teste_health_check)
        self.executar_teste("Serviços diretos", self.teste_conectividade_servicos_diretos)
        
        # Testes de usuários
        self.log("\n2. TESTES DE USUÁRIOS", "WARNING")
        self.executar_teste("Criar usuário válido", self.teste_criar_usuario_valido)
        self.executar_teste("Email duplicado (validação)", self.teste_criar_usuario_email_duplicado)
        self.executar_teste("Listar usuários", self.teste_listar_usuarios)
        self.executar_teste("Buscar usuário existente", self.teste_buscar_usuario_existente)
        self.executar_teste("Buscar usuário inexistente", self.teste_buscar_usuario_inexistente)
        self.executar_teste("Atualizar usuário", self.teste_atualizar_usuario)
        
        # Testes de transações
        self.log("\n3. TESTES DE TRANSAÇÕES", "WARNING")
        self.executar_teste("Criar transação válida", self.teste_criar_transacao_valida)
        self.executar_teste("Usuário inexistente (validação)", self.teste_criar_transacao_usuario_inexistente)
        self.executar_teste("Dados inválidos (validação)", self.teste_criar_transacao_dados_invalidos)
        self.executar_teste("Listar transações do usuário", self.teste_listar_transacoes_usuario)
        
        # Testes de integração
        self.log("\n4. TESTES DE INTEGRAÇÃO", "WARNING")
        self.executar_teste("Relatório agregado", self.teste_relatorio_agregado)
        
        # Limpeza
        self.log("\n5. LIMPEZA", "WARNING")
        self.limpar_dados_teste()
        
        # Resultados finais
        self.log("\n" + "=" * 60)
        self.log("RESULTADOS FINAIS")
        self.log("=" * 60)
        self.log(f"Total de testes: {self.testes_executados}")
        self.log(f"Passou: {self.testes_passaram}", "SUCCESS")
        self.log(f"Falhou: {self.testes_falharam}", "ERROR")
        
        taxa_sucesso = (self.testes_passaram / self.testes_executados) * 100 if self.testes_executados > 0 else 0
        self.log(f"Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        if self.testes_falharam == 0:
            self.log("\n🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.", "SUCCESS")
            return True
        else:
            self.log(f"\n⚠️  {self.testes_falharam} teste(s) falharam. Verifique os logs acima.", "ERROR")
            return False

def main():
    """Função principal para executar os testes."""
    print("Sistema de Testes Flask Microservices")
    print("====================================")
    
    # Verificar se os serviços estão rodando
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code != 200:
            print("❌ API Gateway não está respondendo na porta 5000")
            print("Certifique-se de que todos os serviços estão rodando:")
            print("- run_services.bat (Windows)")
            print("- ./run_services.sh (Linux/Mac)")
            return False
    except:
        print("❌ Não foi possível conectar ao API Gateway (localhost:5000)")
        print("Certifique-se de que todos os serviços estão rodando antes de executar os testes.")
        return False
    
    # Executar testes
    teste = TesteMicroservices()
    sucesso = teste.executar_todos_os_testes()
    
    return sucesso

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
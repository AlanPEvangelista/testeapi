# -*- coding: utf-8 -*-
"""
Script de Teste Simples do Sistema
=================================

Este script testa se os serviços podem ser importados e inicializados
corretamente sem erros de sintaxe ou dependências.
"""

import sys
import os
import importlib

def limpar_modulos(prefixos):
    """Remove módulos específicos do cache para evitar conflitos."""
    modulos_para_remover = []
    for nome_modulo in sys.modules.keys():
        for prefixo in prefixos:
            if nome_modulo.startswith(prefixo) or nome_modulo == prefixo:
                modulos_para_remover.append(nome_modulo)
                break
    
    for modulo in modulos_para_remover:
        del sys.modules[modulo]

def testar_user_service():
    """Testa se o User Service pode ser importado e inicializado."""
    try:
        # Adiciona o diretório do user_service ao path
        user_path = os.path.join(os.getcwd(), 'user_service')
        sys.path.insert(0, user_path)
        
        # Importa e testa os módulos
        import config
        print("✓ User Service - Config carregado")
        
        from models import db, Usuario
        print("✓ User Service - Models carregados")
        
        from routes import user_routes
        print("✓ User Service - Routes carregadas")
        
        # Testa criação da app
        from app import criar_app
        app = criar_app()
        print("✓ User Service - App criada com sucesso")
        print(f"  Porta configurada: {app.config['PORT']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no User Service: {str(e)}")
        return False
    finally:
        # Remove do path
        if user_path in sys.path:
            sys.path.remove(user_path)

def testar_transaction_service():
    """Testa se o Transaction Service pode ser importado e inicializado."""
    try:
        # Limpa módulos de outros serviços
        limpar_modulos(['config', 'models', 'routes', 'app'])
        
        # Remove qualquer path anterior
        paths_to_remove = [p for p in sys.path if 'user_service' in p]
        for path in paths_to_remove:
            sys.path.remove(path)
        
        # Adiciona o diretório do transaction_service ao path
        transaction_path = os.path.join(os.getcwd(), 'transaction_service')
        sys.path.insert(0, transaction_path)
        
        # Importa e testa os módulos
        import config
        print("✓ Transaction Service - Config carregado")
        
        from models import db, Lancamento
        print("✓ Transaction Service - Models carregados")
        
        from routes import transaction_routes
        print("✓ Transaction Service - Routes carregadas")
        
        # Testa criação da app
        from app import criar_app
        app = criar_app()
        print("✓ Transaction Service - App criada com sucesso")
        print(f"  Porta configurada: {app.config['PORT']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no Transaction Service: {str(e)}")
        return False
    finally:
        # Remove do path
        if transaction_path in sys.path:
            sys.path.remove(transaction_path)

def testar_api_gateway():
    """Testa se o API Gateway pode ser importado e inicializado."""
    try:
        # Limpa módulos de outros serviços
        limpar_modulos(['config', 'models', 'routes', 'app', 'gateway'])
        
        # Remove qualquer path anterior
        paths_to_remove = [p for p in sys.path if ('user_service' in p or 'transaction_service' in p)]
        for path in paths_to_remove:
            sys.path.remove(path)
        
        # Adiciona o diretório do api_gateway ao path
        gateway_path = os.path.join(os.getcwd(), 'api_gateway')
        sys.path.insert(0, gateway_path)
        
        # Importa e testa os módulos
        import config
        print("✓ API Gateway - Config carregado")
        
        from gateway import criar_app
        app = criar_app()
        print("✓ API Gateway - App criada com sucesso")
        print(f"  Porta configurada: {app.config['PORT']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no API Gateway: {str(e)}")
        return False
    finally:
        # Remove do path
        if gateway_path in sys.path:
            sys.path.remove(gateway_path)

def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("TESTE DE INICIALIZAÇÃO DOS MICROSERVICES")
    print("=" * 60)
    print()
    
    testes = [
        ("User Service", testar_user_service),
        ("Transaction Service", testar_transaction_service),
        ("API Gateway", testar_api_gateway)
    ]
    
    sucesso_total = True
    
    for nome, funcao_teste in testes:
        print(f"Testando {nome}...")
        sucesso = funcao_teste()
        print()
        
        if not sucesso:
            sucesso_total = False
    
    print("=" * 60)
    if sucesso_total:
        print("🎉 TODOS OS SERVIÇOS PODEM SER INICIALIZADOS!")
        print("\nPara executar o sistema completo:")
        print("- Windows: run_services.bat")
        print("- Linux/Mac: ./run_services.sh")
    else:
        print("❌ ALGUNS SERVIÇOS TÊM PROBLEMAS")
        print("\nVerifique os erros acima e corrija antes de prosseguir.")
    print("=" * 60)
    
    return sucesso_total

if __name__ == "__main__":
    main()
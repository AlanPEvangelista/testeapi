# Sistema Flask com Microservices

Um sistema completo demonstrando arquitetura de microservices usando Flask, SQLite e comunicação HTTP entre serviços. Este projeto implementa um sistema de gerenciamento de usuários e transações financeiras dividido em múltiplos serviços independentes.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Instalação e Configuração](#instalação-e-configuração)
- [Executando o Sistema](#executando-o-sistema)
- [Documentação da API](#documentação-da-api)
- [Exemplos de Uso](#exemplos-de-uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Banco de Dados](#banco-de-dados)
- [Testes](#testes)
- [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

Este sistema demonstra conceitos fundamentais de microservices:

- **Separação de Responsabilidades**: Cada serviço tem uma responsabilidade específica
- **Comunicação HTTP**: Serviços se comunicam via APIs REST
- **Banco de Dados por Serviço**: Cada microservice tem seu próprio banco SQLite
- **API Gateway**: Ponto único de entrada para o sistema
- **Tolerância a Falhas**: Tratamento de erros e timeouts entre serviços

### Funcionalidades Principais

- ✅ **Interface Web Completa**: Página web para gerenciamento visual do sistema
- ✅ **Gerenciamento de Usuários**: CRUD completo de usuários
- ✅ **Gerenciamento de Transações**: Registro e consulta de lançamentos financeiros
- ✅ **Validação de Cartões**: Suporte a diferentes tipos de cartão (Crédito, Débito, Pré-pago)
- ✅ **Relatórios Agregados**: Combinação de dados de múltiplos serviços
- ✅ **Health Checks**: Monitoramento da saúde dos serviços
- ✅ **Logs Estruturados**: Sistema de logging para debugging e monitoramento

## 🏗️ Arquitetura

```
┌─────────────────┐
│     Cliente     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   API Gateway   │  ← Porta 5000
│   (gateway.py)  │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌─────────┐ ┌─────────────┐
│  User   │ │Transaction  │
│Service  │ │  Service    │
│:5001    │ │   :5002     │
└────┬────┘ └──────┬──────┘
     │             │
     ▼             ▼
┌─────────┐ ┌─────────────┐
│Users DB │ │Transactions │
│(SQLite) │ │DB (SQLite)  │
└─────────┘ └─────────────┘
```

### Componentes do Sistema

1. **API Gateway (Porta 5000)**
   - Ponto único de entrada
   - Roteamento de requisições
   - Agregação de dados
   - Health checks

2. **User Service (Porta 5001)**
   - Gerenciamento de usuários
   - Validação de emails
   - CRUD completo

3. **Transaction Service (Porta 5002)**
   - Gerenciamento de transações
   - Validação de cartões
   - Comunicação com User Service

## ⚙️ Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional)

### 1. Clone do Repositório

```bash
git clone <url-do-repositorio>
cd testeapi
```

### 2. Criação do Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 4. Verificação da Instalação

```bash
# Verificar se todas as dependências foram instaladas
pip list
```

## 🚀 Executando o Sistema

O sistema deve ser executado em uma ordem específica para garantir a comunicação entre serviços.

### Método Recomendado: Scripts Automatizados

```bash
# Windows
.\run_services.bat

# Linux/Mac
./run_services.sh
```

### Método Manual: Execução Individual

#### 1. User Service (Terminal 1)
```bash
cd user_service
python app.py
```

#### 2. Transaction Service (Terminal 2)
```bash
cd transaction_service
python app.py
```

#### 3. API Gateway (Terminal 3)
```bash
cd api_gateway
python gateway.py
```

### Verificação dos Serviços

Após iniciar todos os serviços, verifique se estão funcionando:

**🌐 Interface Web (Recomendado):**
```
http://localhost:5000
```

**📋 Verificação via API:**
```bash
# Health check do gateway
curl http://localhost:5000/health

# Informações dos serviços
curl http://localhost:5001/
curl http://localhost:5002/
curl http://localhost:5000/api
```

## 📚 Documentação da API

### 🌐 Interface Web

**URL Principal**: http://localhost:5000

O sistema inclui uma interface web completa que permite:

- **📊 Dashboard**: Visão geral do sistema e status dos microservices
- **👥 Gestão de Usuários**: Criar, listar e visualizar usuários
- **💳 Gestão de Transações**: Visualizar histórico de transações
- **➕ Nova Transação**: Formulário para criar novas transações
- **📈 Relatórios**: Relatórios detalhados por usuário

### Base URLs

- **API Gateway**: `http://localhost:5000`
- **User Service**: `http://localhost:5001`
- **Transaction Service**: `http://localhost:5002`

> **Recomendação**: Use sempre o API Gateway (`localhost:5000`) em produção.

### Endpoints do User Service

#### 📝 Criar Usuário
```http
POST /api/users
Content-Type: application/json

{
    "nome": "João Silva",
    "email": "joao@email.com"
}
```

**Resposta (201 Created):**
```json
{
    "id": 1,
    "nome": "João Silva",
    "email": "joao@email.com",
    "data_criacao": "2024-01-15T10:30:00"
}
```

#### 📋 Listar Usuários
```http
GET /api/users
```

#### 🔍 Buscar Usuário
```http
GET /api/users/{id}
```

#### ✏️ Atualizar Usuário
```http
PUT /api/users/{id}
Content-Type: application/json

{
    "nome": "João Santos",
    "email": "joao.santos@email.com"
}
```

#### 🗑️ Deletar Usuário
```http
DELETE /api/users/{id}
```

### Endpoints do Transaction Service

#### 💳 Criar Transação
```http
POST /api/transactions
Content-Type: application/json

{
    "usuario_id": 1,
    "descricao": "Compra Amazon",
    "valor": 150.99,
    "cartao_tipo": "Crédito",
    "cartao_final": "1234"
}
```

**Resposta (201 Created):**
```json
{
    "id": 1,
    "usuario_id": 1,
    "descricao": "Compra Amazon",
    "valor": 150.99,
    "cartao_tipo": "Crédito",
    "cartao_final": "1234",
    "data_lancamento": "2024-01-15T14:30:00"
}
```

#### 📋 Listar Transações
```http
GET /api/transactions
```

#### 🔍 Buscar Transações por Usuário
```http
GET /api/transactions/user/{user_id}
```

#### 📊 Estatísticas do Usuário
```http
GET /api/transactions/stats/user/{user_id}
```

### Endpoints do Gateway

#### 📈 Relatório Agregado
```http
GET /api/reports/user/{user_id}
```

**Resposta:**
```json
{
    "usuario": {
        "id": 1,
        "nome": "João Silva",
        "email": "joao@email.com"
    },
    "transacoes": [...],
    "resumo_financeiro": {
        "total_transacoes": 5,
        "total_gasto": 580.45
    },
    "estatisticas_detalhadas": {...}
}
```

#### 🏥 Health Check
```http
GET /health
```

## 💡 Exemplos de Uso

### 🌐 Usando a Interface Web (Recomendado)

1. **Acesse a interface principal**: http://localhost:5000
2. **Dashboard**: Visualize o status de todos os microservices e estatísticas gerais
3. **Criar Usuário**: 
   - Vá para a seção "Usuários"
   - Preencha nome e email
   - Clique em "Criar Usuário"
4. **Criar Transação**:
   - Vá para "Nova Transação"
   - Selecione o usuário
   - Preencha valor, descrição, tipo de cartão e últimos 4 dígitos
   - Clique em "Salvar Transação"
5. **Visualizar Relatórios**:
   - Vá para "Relatórios"
   - Selecione um usuário
   - Clique em "Gerar Relatório"

### 📋 Exemplo Completo via API: Criando Usuário e Transações

```bash
# 1. Criar usuário
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Silva",
    "email": "maria@email.com"
  }'

# 2. Criar transação para o usuário (ID retornado: 1)
curl -X POST http://localhost:5000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 1,
    "descricao": "Supermercado Extra",
    "valor": 125.80,
    "cartao_tipo": "Débito",
    "cartao_final": "5678"
  }'

# 3. Consultar transações do usuário
curl http://localhost:5000/api/transactions/user/1

# 4. Gerar relatório completo
curl http://localhost:5000/api/reports/user/1
```

### Exemplo com Python requests

```python
import requests
import json

base_url = "http://localhost:5000/api"

# Criar usuário
usuario_data = {
    "nome": "Pedro Santos",
    "email": "pedro@email.com"
}

response = requests.post(f"{base_url}/users", json=usuario_data)
usuario = response.json()
user_id = usuario['id']

print(f"Usuário criado: {usuario}")

# Criar transação
transacao_data = {
    "usuario_id": user_id,
    "descricao": "Netflix - Assinatura",
    "valor": 32.90,
    "cartao_tipo": "Crédito",
    "cartao_final": "9876"
}

response = requests.post(f"{base_url}/transactions", json=transacao_data)
transacao = response.json()

print(f"Transação criada: {transacao}")

# Consultar relatório
response = requests.get(f"{base_url}/reports/user/{user_id}")
relatorio = response.json()

print(f"Relatório: {json.dumps(relatorio, indent=2)}")
```

## 📁 Estrutura do Projeto

```
testeapi/
├── user_service/
│   ├── app.py              # Aplicação principal do User Service
│   ├── models.py           # Modelos de dados (usuários)
│   ├── routes.py           # Rotas/endpoints da API
│   ├── config.py           # Configurações do serviço
│   ├── user_database.db    # Banco SQLite (criado automaticamente)
│   └── logs/               # Logs do serviço
│
├── transaction_service/
│   ├── app.py              # Aplicação principal do Transaction Service
│   ├── models.py           # Modelos de dados (transações)
│   ├── routes.py           # Rotas/endpoints da API
│   ├── config.py           # Configurações do serviço
│   ├── transaction_database.db  # Banco SQLite (criado automaticamente)
│   └── logs/               # Logs do serviço
│
├── api_gateway/
│   ├── gateway.py          # Aplicação principal do Gateway
│   ├── config.py           # Configurações do gateway
│   └── logs/               # Logs do gateway
│
├── scripts/
│   ├── run_services.bat    # Script Windows para iniciar serviços
│   ├── run_services.sh     # Script Linux/Mac para iniciar serviços
│   ├── install_deps.bat    # Script Windows para instalação
│   └── install_deps.sh     # Script Linux/Mac para instalação
│
├── requirements.txt        # Dependências Python
├── README.md              # Documentação (este arquivo)
└── .gitignore             # Arquivos ignorados pelo Git
```

## 🗄️ Banco de Dados

### Schema do User Service

**Tabela: usuarios**
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Schema do Transaction Service

**Tabela: lancamentos**
```sql
CREATE TABLE lancamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    cartao_tipo VARCHAR(20) NOT NULL,
    cartao_final VARCHAR(4) NOT NULL,
    data_lancamento DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Dados de Exemplo

O sistema cria automaticamente dados de exemplo quando executado em modo debug:

**Usuários:**
- João Silva (joao.silva@email.com)
- Maria Santos (maria.santos@email.com)
- Pedro Oliveira (pedro.oliveira@email.com)
- Ana Costa (ana.costa@email.com)

**Transações:**
- Diversas transações associadas aos usuários
- Diferentes tipos de cartão (Crédito, Débito, Pré-pago)
- Valores variados para demonstração

## 🧪 Testes

### Testes Manuais

#### Teste 1: Conectividade dos Serviços
```bash
curl http://localhost:5000/health
```

#### Teste 2: CRUD de Usuários
```bash
# Criar
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste User","email":"teste@email.com"}'

# Listar
curl http://localhost:5000/api/users

# Atualizar (substitua {id} pelo ID retornado)
curl -X PUT http://localhost:5000/api/users/{id} \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste User Updated"}'

# Deletar
curl -X DELETE http://localhost:5000/api/users/{id}
```

#### Teste 3: Transações e Validações
```bash
# Transação válida
curl -X POST http://localhost:5000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 1,
    "descricao": "Teste Compra",
    "valor": 50.00,
    "cartao_tipo": "Crédito",
    "cartao_final": "1234"
  }'

# Transação inválida (usuário inexistente)
curl -X POST http://localhost:5000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 999,
    "descricao": "Teste Erro",
    "valor": 50.00,
    "cartao_tipo": "Crédito",
    "cartao_final": "1234"
  }'
```

### Validações Implementadas

#### User Service:
- ✅ Email único
- ✅ Formato de email válido
- ✅ Nome mínimo de 2 caracteres
- ✅ Campos obrigatórios

#### Transaction Service:
- ✅ Usuário existe (comunicação com User Service)
- ✅ Valor positivo e com máximo 2 casas decimais
- ✅ Tipo de cartão válido (Crédito, Débito, Pré-pago)
- ✅ Últimos 4 dígitos do cartão (numéricos)
- ✅ Descrição mínima de 3 caracteres

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro "Address already in use"
```bash
# Verificar portas ocupadas
netstat -ano | findstr :5000
netstat -ano | findstr :5001
netstat -ano | findstr :5002

# Matar processos se necessário
taskkill /PID {PID} /F
```

#### 2. Módulo não encontrado
```bash
# Verificar se o ambiente virtual está ativo
where python
pip list

# Reinstalar dependências se necessário
pip install -r requirements.txt
```

#### 3. Erro de comunicação entre serviços
```bash
# Verificar se todos os serviços estão rodando
curl http://localhost:5001/users/health
curl http://localhost:5002/transactions/health

# Verificar logs
tail -f user_service/logs/user_service.log
tail -f transaction_service/logs/transaction_service.log
tail -f api_gateway/logs/api_gateway.log
```

#### 4. Banco de dados corrompido
```bash
# Deletar bancos e reiniciar serviços
rm user_service/user_database.db
rm transaction_service/transaction_database.db
# Reiniciar os serviços
```

### Logs e Debugging

Cada serviço gera logs em sua respectiva pasta `logs/`:
- `user_service/logs/user_service.log`
- `transaction_service/logs/transaction_service.log`
- `api_gateway/logs/api_gateway.log`

Os logs incluem:
- Requisições recebidas
- Comunicação entre serviços
- Erros e exceções
- Operações de banco de dados

### Configurações de Debug

Para habilitar logs mais detalhados, edite os arquivos `config.py`:

```python
# Alterar nível de log
LOG_LEVEL = 'DEBUG'

# Habilitar logs do SQLAlchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## 🚀 Melhorias Futuras

### Funcionalidades Planejadas
- [ ] Autenticação e autorização (JWT)
- [ ] Cache Redis para performance
- [ ] Documentação Swagger/OpenAPI
- [ ] Containerização com Docker
- [ ] Monitoramento com Prometheus
- [ ] Circuit breaker pattern
- [ ] Rate limiting
- [ ] Versionamento de APIs

### Otimizações
- [ ] Conexão pool para banco de dados
- [ ] Compressão de respostas HTTP
- [ ] Paginação automática
- [ ] Validação com schemas JSON
- [ ] Testes automatizados (pytest)

## 📄 Licença

Este projeto é para fins educacionais e demonstração de conceitos de microservices.

## 👥 Contribuições

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Consulte a seção [Troubleshooting](#troubleshooting)
- Verifique os logs dos serviços
- Abra uma issue no repositório

---

**Desenvolvido com ❤️ usando Flask e Python**
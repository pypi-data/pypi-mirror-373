# Neofin Toolbox

O **neofin-toolbox** é um repositório privado do Bitbucket que centraliza artefatos e componentes de uso comum no ecossistema **Neofin**. Seu objetivo é padronizar e acelerar o desenvolvimento, fornecendo módulos reutilizáveis para diferentes serviços da plataforma.

Ótimo. Com base na sua solicitação, aqui está a seção de **Versionamento** completa, contendo a explicação do padrão de tags, a tabela de tipos de mudança e o detalhamento de uso do `Makefile` que você forneceu.

-----

## 📦 Instalação

### Via Git (Desenvolvimento)

```bash
# Clone do repositório
git clone https://bitbucket.org/neofin/neofin-toolbox.git
cd neofin-toolbox

# Instalação em modo desenvolvimento
poetry install
```

### Via Tag Específica

```bash
# Instalar versão específica
poetry add git+username:token@https://bitbucket.org/neofin/neofin-toolbox.git@v1.2.0
```

---

## 🏷️ Versionamento

A toolbox utiliza **versionamento semântico** baseado em **tags Git**.
Cada nova mudança deve ser publicada com uma nova tag incremental seguindo o padrão [SemVer](https://semver.org/):

| Tipo | Formato | Descrição | Exemplo |
|------|---------|-----------|---------|
| **PATCH** | `x.y.Z` | Correções de bugs e ajustes pequenos | `1.0.1` |
| **MINOR** | `x.Y.0` | Novas funcionalidades compatíveis | `1.1.0` |
| **MAJOR** | `X.0.0` | Mudanças que quebram compatibilidade | `2.0.0` |

#### **Como Usar**

Para que o script funcione corretamente, você deve seguir um padrão no título da sua pull request (PR).

Inclua a hashtag do tipo de bump no título da PR:

- #major: Para mudanças grandes e incompatíveis com versões anteriores.
- #minor: Para novas funcionalidades que são compatíveis com versões anteriores.
- #patch: Para correções de bugs.

```Exemplo de título de PR: Adiciona novo recurso de autenticação #minor```

##### Exemplo de Fluxo de Trabalho
Vamos supor que a última tag no seu repositório seja v1.2.3.

- Cenário 1: Correção de bug
    - Título da PR: Corrige falha na autenticação do usuário #patch
    - Resultado: O script irá criar e puxar a tag v1.2.4.
- Cenário 2: Nova funcionalidade
    - Título da PR: Implementa login com redes sociais #minor
    - Resultado: O script irá criar e puxar a tag v1.3.0.
- Cenário 3: Mudança drástica
    - Título da PR: Refatoração completa do motor de busca #major
    - Resultado: O script irá criar e puxar a tag v2.0.0.

## 🗂️ Estrutura de Módulos

-----

### 🔌 **Adapters**

Adapters para integração com serviços externos, centralizando instâncias e configurações para promover a reutilização e padronização.

#### 🔹 **SQSAdapter**

Adaptador para operações com o Amazon SQS, fornecendo métodos para envio de mensagens individuais e em lote com tratamento de erros. A classe `SQSAdapter` inicializa de forma segura o cliente SQS e utiliza o `boto3` para suas operações.

##### **Funcionalidades**

  - **Envio de Mensagem:** Envia uma única mensagem para uma fila SQS, permitindo a configuração de um atraso de até 900 segundos.
  - **Envio em Lote:** Permite o envio de até 10 mensagens simultaneamente em um único lote.
  - **Validação:** Realiza validações automáticas, garantindo que o nome da fila e o corpo da mensagem não estejam vazios, e que o `delay_seconds` esteja dentro do limite permitido (0 a 900).
  - **Tratamento de Erros:** Captura e trata exceções como `ClientError` (para filas inexistentes) e `BotoCoreError`, relançando-as como `SQSAdapterException` para um tratamento consistente.

#### 📋 **Exemplos de Uso**


```python
import json
from neofin_toolbox.adapters.sqs_adapter import SQSAdapter
from neofin_toolbox.exceptions.adapters.sqs_adapter_exception import SQSAdapterException

adapter = SQSAdapter()

# Envio simples de um evento de criação de usuário
message_body = json.dumps({
    "event_type": "user_created",
    "user_id": "user-12345",
    "timestamp": "2024-08-21T10:47:28Z"
})
try:
    response = adapter.send_message(
        queue_name="user-events-queue",
        message=message_body
    )
    print("Mensagem enviada com sucesso:", response)
except SQSAdapterException as e:
    print(f"Erro ao enviar mensagem: {e}")

# Envio com atraso de 5 minutos
delayed_message = json.dumps({"task": "send_welcome_email", "user_id": "user-12345"})
try:
    response = adapter.send_message(
        queue_name="delayed-tasks-queue",
        message=delayed_message,
        delay_seconds=300
    )
    print("Mensagem atrasada enviada com sucesso:", response)
except SQSAdapterException as e:
    print(f"Erro ao enviar mensagem atrasada: {e}")
```


```python
import json
from neofin_toolbox.adapters.sqs_adapter import SQSAdapter
from neofin_toolbox.exceptions.adapters.sqs_adapter_exception import SQSAdapterException

adapter = SQSAdapter()

# Envio em lote de eventos de processamento de pedidos
messages = [
    json.dumps({"event": "order_created", "order_id": "order-1001"}),
    json.dumps({"event": "order_created", "order_id": "order-1002"}),
    json.dumps({"event": "order_created", "order_id": "order-1003"})
]

try:
    response = adapter.send_batch_messages(
        queue_name="order-processing-queue",
        messages=messages
    )
    print(f"Lote enviado. Sucesso: {len(response.get('Successful', []))}, Falha: {len(response.get('Failed', []))}")
except SQSAdapterException as e:
    print(f"Erro ao enviar lote de mensagens: {e}")
```



```python
from neofin_toolbox.adapters.sqs_adapter import SQSAdapter
from neofin_toolbox.exceptions.adapters.sqs_adapter_exception import SQSAdapterException
import logging

logger = logging.getLogger(__name__)

adapter = SQSAdapter()

# Tentativa de enviar para uma fila inexistente
try:
    adapter.send_message("non-existent-queue", "Test message")
except SQSAdapterException as e:
    logger.error(f"Erro no SQS capturado: {e}")
    # Aqui você pode adicionar lógica de retry, fallback ou notificação de erro.
```


-----

#### 🔹 **SESAdapter**

Adaptador para envio de emails via Amazon SES, com suporte a templates dinâmicos usando Jinja2. A classe `SESAdapter` inicializa clientes para SES e Jinja2, buscando os templates em uma pasta configurável.

##### **Funcionalidades**

  - **Renderização de Templates:** Renderiza templates HTML e de texto simples (`.txt`) com variáveis de contexto fornecidas.
  - **Envio de Email:** Envia e-mails individuais, suportando destinatários (`to`), cópia (`cc`), cópia oculta (`bcc`) e endereços de resposta (`reply-to`).
  - **Envio em Lote:** Possui um método `send_bulk_emails` que itera sobre uma lista de dados de e-mail e envia cada um individualmente, registrando os resultados (sucesso ou falha).
  - **Verificação de Endereço:** Inclui a funcionalidade de verificar se um endereço de e-mail está verificado no SES.
  - **Estatísticas de Envio:** Fornece um método para obter estatísticas de envio de e-mail diretamente do SES.
  - **Tratamento de Erros:** O `SESAdapter` lida com erros como `FileNotFoundError` (para templates inexistentes), `NoCredentialsError` e `ClientError`, fornecendo mensagens de log detalhadas para cada falha.

#### 📋 **Exemplos de Uso**

```python
from neofin_toolbox.adapters.ses_adapter import SESAdapter
import os

# Supondo que você tenha um template 'welcome.html'
# na pasta 'templates' dentro do seu projeto.
# O SESAdapter busca automaticamente nesta pasta.
# Exemplo de conteúdo de 'welcome.html':
# <html><body>Olá, {{ user_name }}! <p>Bem-vindo à Neofin. Seu link é: <a href="{{ activation_link }}">Ativar</a></p></body></html>

ses_adapter = SESAdapter(default_source_email="noreply@neofin.com")

response = ses_adapter.send_email(
    to_addresses=["usuario@exemplo.com"],
    subject="Bem-vindo à Neofin!",
    template_name="welcome.html",
    context={
        "user_name": "João Silva",
        "activation_link": "https://app.neofin.com/activate/abc123"
    }
)
print("Email de boas-vindas enviado:", response)
```

```python
from neofin_toolbox.adapters.ses_adapter import SESAdapter

ses_adapter = SESAdapter(default_source_email="contato@neofin.com")

response = ses_adapter.send_email(
    to_addresses=["cliente@empresa.com", "outro_cliente@empresa.com"],
    cc_addresses=["gerente@empresa.com"],
    subject="Relatório Mensal de Janeiro",
    template_name="monthly_report.html",
    context={
        "month": "Janeiro",
        "year": 2024,
        "total_balance": 1000.00
    },
    reply_to="suporte@neofin.com"
)
print("Relatório mensal enviado:", response)
```

```python
from neofin_toolbox.adapters.ses_adapter import SESAdapter

ses_adapter = SESAdapter()

# Verificar se um email já está verificado no SES
is_verified = ses_adapter.verify_email_address("novo@cliente.com")

if not is_verified:
    # Se não estiver verificado, o SES enviará um email de verificação
    print("Email de verificação não encontrado. Por favor, verifique seu inbox.")
```

```python
from neofin_toolbox.adapters.ses_adapter import SESAdapter

ses_adapter = SESAdapter()
try:
    stats = ses_adapter.get_send_statistics()
    print("Estatísticas de envio:", stats)
except Exception as e:
    print(f"Erro ao obter estatísticas: {e}")
```

### ⚙️ **Configs**
Configurações e constantes reutilizáveis em todo o ecossistema.

**Inclui:**
- Enums de status e substatus
- Nomes de tabelas e índices
- Configurações de ambiente
- Constantes do sistema

---

### 🚨 **Exceptions**
Padronização de exceções personalizadas para o ecossistema.

**Hierarquia de exceções:**
```
exceptions
├── CommonException (genérica)
│   ├── adapters
│       └── SQSAdapterException
│   └── decorators
│       └── AuthException
│       └── PermissionException
│       └── AuthenticationException
│       └── MissingUserException
│       └── MissingRoleException
|   └── repositories
|       └── company_repository_exception
│           └── CompanyNotFoundException
|       └── roles_repository_exception
│           └── RolesRepositoryException
│           └── RolesNotFoundException
|       └── user_repository_exception
│           └── UserRepositoryException
│           └── UserNotFoundException
```

---

### 📦 **Models**
Modelos de dados compartilhados entre serviços.

**Exemplo:** Modelo de usuário, entidades comuns, DTOs

---

Aqui está uma versão aprimorada da seção **🗄️ Repositories** que reflete a estrutura e a funcionalidade dos arquivos Python fornecidos.

---

### 🗄️ **Repositories**
Repositórios para abstrair a lógica de acesso a dados, centralizando as operações de CRUD e consulta. Eles herdam da classe `DynamoDbRepository` para reutilizar a configuração do cliente AWS e métodos de paginação.

#### **Estrutura e Padrão de Uso**
- A classe base `DynamoDbRepository` gerencia a inicialização dos clientes `boto3` para o DynamoDB e fornece métodos utilitários, como a consulta paginada `_paginated_query`.
- Cada repositório (ex: `UserRepository`, `CompanyRepository`) herda de `DynamoDbRepository` e é responsável por interagir com uma tabela específica.
- As exceções customizadas (`UserNotFoundException`, `RolesRepositoryException`, etc.) são usadas para fornecer um tratamento de erro específico e semântico.
- Logging detalhado é incluído para cada operação, facilitando o rastreamento e a depuração.

#### **Repositórios Disponíveis**

##### `AuditRepository`
- **Tabela:** `TableConfigEnum.AUDIT`
- **Funcionalidade:** Responsável por inserir itens de auditoria. Possui um método `put_item` com tratamento de erros específico para `ClientError`, `Boto3Error` e erros genéricos.

##### `CompanyRepository`
- **Tabela:** `TableConfigEnum.COMPANY`
- **Funcionalidade:** Gerencia as operações de empresas.
- **Métodos principais:**
    - `get_company_by_id(company_id: str)`: Recupera uma empresa pelo seu ID.
    - `get_companies_by_document(document: str)`: Busca empresas por um documento (ex: CNPJ), utilizando um Índice Secundário Global.
    - `put_company(payload: Dict[str, Any])`: Cria ou atualiza um registro de empresa.

##### `CustomerRepository`
- **Tabela:** `TableConfigEnum.CUSTOMER`
- **Funcionalidade:** Responsável pelas operações de clientes.
- **Índices:** Usa os GSIs `company_id-document` e `document`.
- **Métodos principais:**
    - `get_by_customer_id_and_company_id(customer_id: str, company_id: str)`: Recupera um cliente usando a chave primária composta.
    - `get_customers_by_company_id(company_id: str)`: Busca todos os clientes de uma empresa, com paginação interna.

##### `InstallmentsRepository`
- **Tabela:** `TableConfigEnum.INSTALLMENTS`
- **Funcionalidade:** Gerencia as parcelas de pagamento.
- **Métodos principais:**
    - `get_overdue_installments_by_company_id(company_id: str)`: Busca parcelas vencidas para uma empresa específica, utilizando um GSI e um filtro de data.
    - `get_installments_by_ids(company_id: str, installment_ids: List[str])`: Recupera múltiplas parcelas por ID, otimizado para lidar com listas grandes.
    - `get_installments_by_billing_id(billing_id: str)`: Busca parcelas relacionadas a um ID de cobrança.

##### `RenegotiationCampaignRepository`
- **Tabela:** `TableConfigEnum.RENEGOTIATION_CAMPAIGNS`
- **Funcionalidade:** Repositório para campanhas de renegociação.
- **Índices:** Utiliza os GSIs `company_id` e `end_date`.
- **Métodos principais:**
    - `put_renegotiation_campaign(renegotiation_campaign: RenegotiationCampaign)`: Salva uma campanha.
    - `get_renegotiation_campaign_by_id_and_company_id(...)`: Recupera uma campanha usando a chave primária composta.
    - `_query_campaigns_by_company_id(...)` e `_query_campaigns_by_end_date(...)`: Métodos privados de auxílio para buscas paginadas.

##### `RolesRepository`
- **Tabela:** `TableConfigEnum.ROLES`
- **Funcionalidade:** Gerencia os papéis (roles) de usuário.
- **Índice:** Usa o GSI `company_id-role_name`.
- **Métodos principais:**
    - `get_role_by_id(role_id: str)`: Busca um papel pelo seu ID.
    - `get_roles_by_company_id_and_name(company_id: str, role_name: str)`: Busca papéis por empresa e nome.
    - `put_role(payload: Dict[str, Any])`: Salva um papel no banco de dados.

##### `UserRepository`
- **Tabela:** `TableConfigEnum.USERS`
- **Funcionalidade:** Gerencia as operações de usuário.
- **Métodos principais:**
    - `get_user_by_id(user_id: str)`: Recupera um usuário pelo ID com tratamento de erro detalhado, incluindo a exceção `UserNotFoundException`.

---

Aqui está uma versão aprimorada da seção **🛠️ Utils** que reflete a estrutura e a funcionalidade dos arquivos Python fornecidos.

-----

### 🛠️ **Utils**

Funções utilitárias, helpers e decorators reutilizáveis para diversas tarefas, incluindo segurança, tratamento de erros e manipulação de dados.

#### ✨ **Funcionalidades**

##### **`Audit Decorator`**

  - **Arquivo:** `decorators/audit.py`
  - **Descrição:** Decorator para auditar requisições de API. Captura o contexto da requisição (usuário, método, corpo) e a salva na tabela de auditoria (`AuditRepository`).
  - **Padrão de uso:** `from neofin_toolbox.utils.audit import save`
  - **Exemplo de uso:**
    ```python
    from neofin_toolbox.utils.audit import save

    @app.route('/my-resource', methods=['POST'])
    @save(app=app, entity='MyResource', entity_pk='id')
    def create_resource():
        # Lógica de negócio
        return {"message": "Resource created"}
    ```

##### **`Auth & Permission Decorator`**

  - **Arquivo:** `decorators/auth_permission.py`
  - **Descrição:** Decorator para controle de acesso baseado em permissões. Valida a identidade do usuário (`user_id`), recupera seu papel (`role_id`) e verifica se as permissões necessárias estão presentes na lista de permissões do papel.
  - **Exceções:** Lança exceções customizadas como `MissingUserException`, `MissingRoleException` e `PermissionException`.
  - **Padrão de uso:** `from neofin_toolbox.utils.auth_permission import check`
  - **Exemplo de uso:**
    ```python
    from neofin_toolbox.utils.auth_permission import check

    @app.route('/secure-endpoint', methods=['GET'])
    @check(app=app, perm_list=['reports/read'])
    def get_secure_data():
        # Lógica de negócio
        return {"data": "Secure data"}
    ```

##### **`Error Handler Decorator`**

  - **Arquivo:** `decorators/handler_error.py`
  - **Descrição:** Decorator para centralizar o tratamento de erros em endpoints de API (Chalice). Ele intercepta diferentes tipos de exceções (`NotFoundError`, `BadRequestError`, `ValidationError` do Pydantic, e exceções customizadas do tipo `CommonException`) e retorna respostas padronizadas com status codes apropriados.
  - **Padrão de uso:** `from neofin_toolbox.utils.handler_error import handle_error`
  - **Exemplo de uso:**
    ```python
    from neofin_toolbox.utils.handler_error import handle_error
    from neofin_toolbox.exceptions.common_exceptions import CommonException

    @app.route('/protected-action', methods=['POST'])
    @handle_error
    def do_action():
        if some_condition_is_invalid:
            raise CommonException(message="Invalid condition", status_code=400)
        return {"status": "success"}
    ```

##### **`Helpers`**

  - **Arquivo:** `helpers.py`
  - **Descrição:** Conjunto de funções para tarefas gerais de utilidade em APIs, como a criação de respostas HTTP padronizadas e a gestão de CORS.
  - **Inclui:**
      - `make_response`: Cria um objeto `chalice.Response` com headers de CORS predefinidos.
      - `get_default_origins`: Retorna uma lista de origens de domínio permitidas para CORS.
      - `handle_cors_options`: Lógica para validar a origem da requisição e retornar a resposta correta para requisições `OPTIONS`.

##### **`Encoders`**

  - **Arquivo:** `encoders.py`
  - **Descrição:** Classes e funções para manipular e serializar tipos de dados específicos, como `Decimal` do Python, para garantir a compatibilidade com JSON e DynamoDB.
  - **Inclui:**
      - `DecimalEncoder`: Uma classe `json.JSONEncoder` que converte objetos `Decimal` para `int` (se forem datas em timestamp) ou `str`, evitando erros de serialização.
      - `deserialize_item`: Função para desserializar itens do DynamoDB, convertendo-os de volta para tipos Python nativos.

---


<div align="center">

**Neofin Toolbox** - Acelerando o desenvolvimento do ecossistema Neofin 🚀

</div>
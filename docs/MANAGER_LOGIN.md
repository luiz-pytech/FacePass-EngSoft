# Sistema de Login de Gestor - FacePass

## Visão Geral

O FacePass implementa um sistema de autenticação simples para gestores, permitindo controle de acesso às funcionalidades administrativas do sistema.

## Credenciais Padrão

Ao executar o script de inicialização do banco de dados (`scripts_tables.py`), um gestor padrão é criado automaticamente:

```
Email: admin@facepass.com
Senha: admin123
```

**⚠️ IMPORTANTE:** Altere a senha padrão após o primeiro login por questões de segurança.

## Como Fazer Login

1. Execute a aplicação: `streamlit run facepass/ui/main.py`
2. No menu lateral, selecione **"👨‍💼 Login de Gestor"**
3. Digite as credenciais:
   - **Email:** `admin@facepass.com`
   - **Senha:** `admin123`
4. Clique em **"🔓 Entrar"**

## Funcionalidades Protegidas

Após o login, o gestor terá acesso a:

- **👤 Gestão de Cadastros** - Aprovar/rejeitar cadastros de usuários
- **📜 Relatórios de Acesso** - Visualizar e exportar logs de acesso
- **🔔 Notificações** - Gerenciar notificações de acessos negados

## Gerenciamento de Sessão

- A autenticação é armazenada no `st.session_state` do Streamlit
- Variáveis de sessão após login:
  - `manager_authenticated`: `True`
  - `manager_id`: ID do gestor
  - `manager_name`: Nome do gestor
  - `manager_email`: Email do gestor

## Logout

Para fazer logout:
1. Acesse a página **"👨‍💼 Login de Gestor"**
2. Clique em **"🚪 Fazer Logout"**

## Segurança

### Hash de Senha

As senhas são armazenadas usando hash **SHA-256**:

```python
import hashlib
password_hash = hashlib.sha256(password.encode()).hexdigest()
```

### Validação

O sistema valida:
- Formato de email (presença de `@` e `.`)
- Existência do gestor no banco de dados
- Correspondência do hash da senha

## Criando Novos Gestores

Atualmente, novos gestores devem ser criados diretamente no banco de dados ou via script Python:

```python
import hashlib
from facepass.database.setup_database.connection import DatabaseConnection
from facepass.database.repository.manager_repository import ManagerRepository

# Conectar ao banco
cnx = DatabaseConnection(host, user, password, database)
cnx.connect()
connection = cnx.get_connection()

# Criar repositório
manager_repo = ManagerRepository(connection)

# Hash da senha
password_hash = hashlib.sha256("nova_senha".encode()).hexdigest()

# Dados do novo gestor
new_manager = {
    'name': 'Nome do Gestor',
    'email': 'gestor@exemplo.com',
    'password_hash': password_hash
}

# Criar gestor
manager_id = manager_repo.create_manager(new_manager)
print(f"Gestor criado com ID: {manager_id}")
```

## Proteção de Rotas (Futuro)

**Planejado para próximas versões:**

Adicionar verificação de autenticação nas páginas protegidas:

```python
def app():
    # Verificar se o gestor está autenticado
    if not st.session_state.get('manager_authenticated', False):
        st.warning("⚠️ Acesso restrito! Faça login como gestor.")
        st.stop()

    # Continuar com a lógica da página
    st.title("Página Protegida")
    # ...
```

## Estrutura do Banco de Dados

### Tabela `manager`

```sql
CREATE TABLE manager (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
)
```

## Arquivos Relacionados

- **Página de Login:** [`facepass/ui/ui_pages/manager_login.py`](../facepass/ui/ui_pages/manager_login.py)
- **Repositório:** [`facepass/database/repository/manager_repository.py`](../facepass/database/repository/manager_repository.py)
- **Setup do Banco:** [`facepass/database/setup_database/scripts_tables.py`](../facepass/database/setup_database/scripts_tables.py)
- **Main App:** [`facepass/ui/main.py`](../facepass/ui/main.py)

## Melhorias Futuras

- [ ] Implementar troca de senha via interface
- [ ] Adicionar níveis de permissão (admin, gestor, etc.)
- [ ] Implementar recuperação de senha via email
- [ ] Adicionar autenticação de dois fatores (2FA)
- [ ] Logs de atividades de login/logout
- [ ] Sessão com timeout automático
- [ ] Proteção contra força bruta (rate limiting)
- [ ] Interface para criar/editar/remover gestores

## Troubleshooting

### "Serviço de autenticação indisponível"

- Verifique se o banco de dados está rodando
- Confirme que o arquivo `.env` está configurado corretamente
- Execute novamente `python -m facepass.database.setup_database.scripts_tables`

### "Email ou senha incorretos"

- Verifique se está usando as credenciais corretas
- Confirme que o gestor existe na tabela `manager`
- Use as credenciais padrão: `admin@facepass.com` / `admin123`

### Gestor padrão não foi criado

Execute manualmente:

```bash
python -m facepass.database.setup_database.scripts_tables
```

Isso recriará o gestor padrão se não existir.
# Refatoração: Separação UI e Lógica de Integração

## Problema Identificado

Atualmente, as páginas UI (ex: `user_registration.py`) estão **misturando responsabilidades**:

1. **Apresentação** - Formulários, layouts, componentes visuais (Streamlit)
2. **Validação** - Funções como `validar_email()`, `validar_cpf()`
3. **Integração** - Criação de objetos de domínio e chamadas aos services
4. **Estado** - Gerenciamento do `st.session_state`

### Exemplo do problema (user_registration.py:164-175)
```python
# UI fazendo integração direta com services
usuario = Usuario(
    id=0,
    nome=nome.strip(),
    email=email.strip().lower(),
    cpf=limpar_cpf(cpf),
    foto_reconhecimento=foto_bytes,
    cargo=cargo.strip(),
    aprovado=False
)

usuario_service.create_user(usuario)
```

**Problemas**:
- ❌ Difícil testar lógica sem UI
- ❌ Validações duplicadas em múltiplas páginas
- ❌ UI conhece detalhes do domínio (como criar `Usuario`)
- ❌ Dificulta reuso (API futura precisaria reescrever tudo)
- ❌ Viola Single Responsibility Principle

---

## Solução Proposta: Controller Layer

Criar uma **camada de Controllers** que faz a ponte entre UI e Services:

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (Streamlit)                   │
│  user_registration.py, approve_registration.py, etc.        │
│  - Apenas apresentação e coleta de inputs                   │
│  - Chama controllers                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Controller Layer (NOVO)                        │
│  user_controller.py, access_controller.py, etc.             │
│  - Validações de entrada                                    │
│  - Transformação de dados (UI → Domain)                     │
│  - Orquestração de múltiplos services                       │
│  - Tratamento de exceções                                   │
│  - Formatação de respostas (Domain → UI)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Service Layer                             │
│  user_service.py, access_service.py, etc.                   │
│  - Apenas lógica de negócio                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 Repository Layer                            │
│  user_repository.py, etc.                                   │
│  - Apenas persistência                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Estrutura Proposta

```
facepass/
├── ui/
│   ├── pages/
│   │   ├── user_registration.py      # Apenas UI (formulários, layout)
│   │   ├── approve_registration.py   # Apenas UI
│   │   ├── facial_recognition.py     # Apenas UI
│   │   └── ...
│   └── app.py
│
├── controllers/  # NOVA CAMADA
│   ├── __init__.py
│   ├── user_controller.py           # Integração para operações de usuário
│   ├── access_controller.py         # Integração para controle de acesso
│   ├── notification_controller.py   # Integração para notificações
│   └── report_controller.py         # Integração para relatórios
│
├── services/     # Lógica de negócio pura
│   ├── user_service.py
│   ├── access_service.py
│   └── ...
│
└── validators/   # NOVA CAMADA (refatorar validations)
    ├── __init__.py
    ├── input_validator.py           # Validações de entrada (email, CPF, etc)
    └── domain_validator.py          # Validações de domínio (regras de negócio)
```

---

## Exemplo: UserController

### Arquivo: `facepass/controllers/user_controller.py`

```python
from typing import Dict, List, Optional
from facepass.models.user import Usuario
from facepass.services.user_service import UsuarioService
from facepass.validators.input_validator import InputValidator
from datetime import datetime


class UserController:
    """
    Controller para operações relacionadas a usuários.

    Responsabilidades:
    - Validar inputs do usuário (UI)
    - Transformar dados de entrada em objetos de domínio
    - Orquestrar chamadas aos services
    - Tratar exceções e retornar respostas padronizadas
    - Formatar dados para apresentação na UI
    """

    def __init__(self, user_service: UsuarioService):
        self.user_service = user_service
        self.validator = InputValidator()

    def create_user(
        self,
        nome: str,
        email: str,
        cpf: str,
        cargo: str,
        foto_bytes: bytes,
        aceita_termos: bool
    ) -> Dict:
        """
        Processa o cadastro de um novo usuário.

        Args:
            nome: Nome completo
            email: Email
            cpf: CPF (formatado ou não)
            cargo: Cargo/função
            foto_bytes: Imagem facial em bytes
            aceita_termos: Se aceitou os termos

        Returns:
            Dict com formato:
            {
                'success': bool,
                'message': str,
                'data': Usuario | None,
                'errors': List[str]
            }
        """
        errors = []

        # Validações de entrada
        if not nome or len(nome.strip()) < 3:
            errors.append("Nome completo deve ter no mínimo 3 caracteres")

        if not self.validator.validar_email(email):
            errors.append("Email inválido")

        if not self.validator.validar_cpf(cpf):
            errors.append("CPF inválido")

        if not cargo or len(cargo.strip()) < 2:
            errors.append("Cargo/Função é obrigatório")

        if not foto_bytes or len(foto_bytes) == 0:
            errors.append("Foto para reconhecimento facial é obrigatória")

        if not aceita_termos:
            errors.append("Você deve aceitar os termos e condições")

        # Se houver erros, retorna imediatamente
        if errors:
            return {
                'success': False,
                'message': 'Erro de validação',
                'data': None,
                'errors': errors
            }

        try:
            # Transformar dados de entrada para objeto de domínio
            usuario = Usuario(
                id=0,  # Será gerado pelo banco
                nome=nome.strip(),
                email=email.strip().lower(),
                cpf=self.validator.limpar_cpf(cpf),
                foto_reconhecimento=foto_bytes,
                cargo=cargo.strip(),
                aprovado=False  # Sempre começa não aprovado
            )

            # Delegar lógica de negócio ao service
            usuario_salvo = self.user_service.create_user(usuario)

            # Retornar resposta de sucesso
            return {
                'success': True,
                'message': 'Usuário cadastrado com sucesso! Aguardando aprovação do gestor.',
                'data': usuario_salvo,
                'errors': []
            }

        except ValueError as e:
            # Erros de validação do service
            return {
                'success': False,
                'message': 'Erro de validação',
                'data': None,
                'errors': [str(e)]
            }

        except Exception as e:
            # Erros inesperados
            return {
                'success': False,
                'message': 'Erro ao processar cadastro',
                'data': None,
                'errors': [f'Erro interno: {str(e)}']
            }

    def approve_user(self, user_id: int, approved: bool, motivo: Optional[str] = None) -> Dict:
        """
        Aprova ou rejeita um usuário.

        Args:
            user_id: ID do usuário
            approved: True para aprovar, False para rejeitar
            motivo: Motivo da rejeição (se aplicável)

        Returns:
            Dict padronizado com success, message, data, errors
        """
        try:
            if approved:
                usuario = self.user_service.approve_user(user_id)
                return {
                    'success': True,
                    'message': f'Usuário {usuario.nome} aprovado com sucesso!',
                    'data': usuario,
                    'errors': []
                }
            else:
                # Aqui você pode adicionar lógica de rejeição
                # Por exemplo, marcar como rejeitado e enviar notificação
                usuario = self.user_service.get_user_by_id(user_id)
                # TODO: Implementar método reject_user no service
                return {
                    'success': True,
                    'message': f'Usuário {usuario.nome} rejeitado.',
                    'data': usuario,
                    'errors': []
                }

        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao processar aprovação',
                'data': None,
                'errors': [str(e)]
            }

    def list_pending_users(self) -> Dict:
        """
        Lista usuários pendentes de aprovação.

        Returns:
            Dict padronizado
        """
        try:
            usuarios = self.user_service.list_unapproved_users()
            return {
                'success': True,
                'message': f'{len(usuarios)} usuário(s) pendente(s)',
                'data': usuarios,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao listar usuários',
                'data': [],
                'errors': [str(e)]
            }

    def get_user_status(self, email: str) -> Dict:
        """
        Consulta o status de cadastro de um usuário pelo email.

        Args:
            email: Email do usuário

        Returns:
            Dict com informações do status
        """
        try:
            usuario = self.user_service.get_user_by_email(email)

            if not usuario:
                return {
                    'success': False,
                    'message': 'Usuário não encontrado',
                    'data': None,
                    'errors': ['Email não cadastrado no sistema']
                }

            status_texto = "Aprovado" if usuario.aprovado else "Aguardando Aprovação"

            return {
                'success': True,
                'message': f'Status: {status_texto}',
                'data': {
                    'nome': usuario.nome,
                    'email': usuario.email,
                    'cargo': usuario.cargo,
                    'aprovado': usuario.aprovado,
                    'status_texto': status_texto
                },
                'errors': []
            }

        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao consultar status',
                'data': None,
                'errors': [str(e)]
            }
```

---

## Exemplo: InputValidator (Refatorar validações)

### Arquivo: `facepass/validators/input_validator.py`

```python
import re
from typing import Optional


class InputValidator:
    """Validações de entrada de dados (formato, sintaxe)"""

    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email.strip()) is not None

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """
        Valida formato básico de CPF.
        TODO: Adicionar validação completa com dígitos verificadores
        """
        if not cpf:
            return False

        # Remove caracteres não numéricos
        cpf_limpo = re.sub(r'\D', '', cpf)

        # Verifica se tem 11 dígitos
        if len(cpf_limpo) != 11:
            return False

        # Verifica se não é sequência repetida (ex: 111.111.111-11)
        if cpf_limpo == cpf_limpo[0] * 11:
            return False

        return True

    @staticmethod
    def limpar_cpf(cpf: str) -> str:
        """Remove formatação do CPF"""
        return re.sub(r'\D', '', cpf)

    @staticmethod
    def validar_nome_completo(nome: str, min_length: int = 3) -> bool:
        """Valida nome completo"""
        if not nome:
            return False
        nome = nome.strip()
        return len(nome) >= min_length and ' ' in nome

    @staticmethod
    def validar_imagem(foto_bytes: Optional[bytes], max_size_mb: int = 5) -> bool:
        """Valida se a imagem está no formato e tamanho adequados"""
        if not foto_bytes:
            return False

        max_size_bytes = max_size_mb * 1024 * 1024
        return len(foto_bytes) <= max_size_bytes
```

---

## Como a UI ficaria refatorada

### ANTES (user_registration.py - linhas 130-210)

```python
# UI misturada com validação e integração
if submit_button:
    erros = []

    # Validações inline
    if not nome or len(nome.strip()) < 3:
        erros.append("❌ Nome inválido")

    if not email or not validar_email(email):
        erros.append("❌ Email inválido")

    # ... mais validações ...

    if erros:
        for erro in erros:
            st.error(erro)
    else:
        try:
            # Criação do objeto de domínio na UI
            usuario = Usuario(
                id=0,
                nome=nome.strip(),
                email=email.strip().lower(),
                cpf=limpar_cpf(cpf),
                foto_reconhecimento=foto_bytes,
                cargo=cargo.strip(),
                aprovado=False
            )

            # Chamada direta ao service
            usuario_service.create_user(usuario)

            st.success("✅ Cadastro enviado com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
```

### DEPOIS (user_registration.py - refatorado)

```python
# UI limpa, apenas apresentação
if submit_button:
    # Obter controller do session_state
    user_controller = st.session_state.get('user_controller')

    if not user_controller:
        st.error("Erro: Sistema não inicializado corretamente")
        return

    # Chamada única ao controller com dados do formulário
    result = user_controller.create_user(
        nome=nome,
        email=email,
        cpf=cpf,
        cargo=cargo,
        foto_bytes=foto_bytes,
        aceita_termos=aceita_termos
    )

    # Apenas exibir o resultado
    if result['success']:
        st.success(result['message'])
        st.balloons()

        # Exibir resumo
        if result['data']:
            with st.expander("📋 Resumo do Cadastro"):
                usuario = result['data']
                st.markdown(f"""
                    **Nome:** {usuario.nome}
                    **Email:** {usuario.email}
                    **Cargo:** {usuario.cargo}
                    **Status:** ⏳ Aguardando Aprovação
                """)
    else:
        st.error(result['message'])
        for error in result['errors']:
            st.error(f"❌ {error}")
```

---

## Benefícios da Refatoração

### 1. Testabilidade
```python
# Agora é fácil testar sem UI
def test_create_user_invalid_email():
    controller = UserController(mock_user_service)
    result = controller.create_user(
        nome="João Silva",
        email="email-invalido",
        cpf="12345678900",
        cargo="Dev",
        foto_bytes=b"fake_image",
        aceita_termos=True
    )

    assert result['success'] == False
    assert 'Email inválido' in result['errors']
```

### 2. Reuso (API futura)
```python
# API pode usar o mesmo controller!
@app.post("/api/users")
async def create_user_api(request: UserCreateRequest):
    controller = get_user_controller()
    result = controller.create_user(
        nome=request.nome,
        email=request.email,
        cpf=request.cpf,
        cargo=request.cargo,
        foto_bytes=request.foto_base64,
        aceita_termos=request.aceita_termos
    )

    if result['success']:
        return JSONResponse(result, status_code=201)
    else:
        return JSONResponse(result, status_code=400)
```

### 3. Separação de Responsabilidades
- **UI**: Apenas apresentação e coleta de inputs
- **Controller**: Validação, transformação e orquestração
- **Service**: Lógica de negócio pura
- **Repository**: Persistência

### 4. Manutenibilidade
- Mudanças no formato de entrada não afetam services
- Mudanças na lógica de negócio não afetam UI
- Fácil adicionar novos tipos de validação

---

## Plano de Migração

### Fase 1: Criar estrutura base
1. Criar diretório `facepass/controllers/`
2. Criar `facepass/validators/input_validator.py`
3. Mover validações de `user_registration.py` para `InputValidator`

### Fase 2: Implementar primeiro controller
1. Criar `UserController` com método `create_user()`
2. Inicializar controller em `main.py` (junto com services)
3. Refatorar `user_registration.py` para usar o controller

### Fase 3: Refatorar outras páginas
1. Criar `AccessController` para `facial_recognition.py`
2. Criar `ReportController` para `registers.py`
3. Criar `NotificationController` para `notifications.py`

### Fase 4: Limpeza
1. Remover funções de validação duplicadas das páginas UI
2. Atualizar documentação
3. Adicionar testes unitários para controllers

---

## Inicialização dos Controllers (main.py)

```python
def init_controllers():
    """Inicializa os controllers após os services"""

    if 'user_service' in st.session_state and 'user_controller' not in st.session_state:
        from facepass.controllers.user_controller import UserController

        user_controller = UserController(
            user_service=st.session_state['user_service']
        )
        st.session_state['user_controller'] = user_controller

    # Repetir para outros controllers...
```

---

## Roadmap Atualizado

Adicionar ao `docs/MVP_ROADMAP.md`:

```markdown
## Fase 3.5: Refatoração - Controller Layer (NOVO)

### 3.5.1 Criar estrutura de Controllers
- [ ] Criar diretório `facepass/controllers/`
- [ ] Criar `__init__.py`
- [ ] Definir padrão de resposta padronizada (Dict com success, message, data, errors)

### 3.5.2 Extrair validações para Validators
- [ ] Criar `facepass/validators/input_validator.py`
- [ ] Mover validações de email, CPF, nome de `user_registration.py`
- [ ] Adicionar validação de imagem

### 3.5.3 Implementar UserController
- [ ] Criar `facepass/controllers/user_controller.py`
- [ ] Implementar `create_user()`
- [ ] Implementar `approve_user()`
- [ ] Implementar `list_pending_users()`
- [ ] Implementar `get_user_status()`

### 3.5.4 Refatorar UI para usar Controllers
- [ ] Refatorar `user_registration.py`
- [ ] Refatorar `approve_registration.py`
- [ ] Inicializar controllers em `main.py`

### 3.5.5 Implementar outros Controllers
- [ ] Criar `AccessController` (para reconhecimento facial)
- [ ] Criar `ReportController` (para relatórios)
- [ ] Criar `NotificationController` (para notificações)
- [ ] Refatorar páginas UI correspondentes

### 3.5.6 Testes e Documentação
- [ ] Adicionar testes unitários para controllers
- [ ] Atualizar CLAUDE.md com nova arquitetura
- [ ] Documentar padrão de resposta padronizada
```

---

## Conclusão

A adição da **Controller Layer** traz os benefícios de:

✅ **Separação clara de responsabilidades**
✅ **Facilita testes automatizados**
✅ **Permite reuso de lógica (UI + API futura)**
✅ **Melhora manutenibilidade**
✅ **Segue padrões MVC/MVP**
✅ **UI mais limpa e focada em apresentação**

**Recomendação**: Implementar esta refatoração **ANTES** de adicionar mais funcionalidades, para evitar acúmulo de débito técnico.

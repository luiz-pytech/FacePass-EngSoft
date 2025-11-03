# Padrões de Projeto - MVP FacePass

## Índice

1. [Introdução](#introdução)
   - [Padrões Criacionais](#padrões-criacionais)
   - [Padrões Estruturais](#padrões-estruturais)
   - [Padrões Comportamentais](#padrões-comportamentais)
---

## Introdução

Este documento descreve os padrões de projeto (design patterns) utilizados no MVP do sistema FacePass, desenvolvido como parte da disciplina de Engenharia de Software da UFRN. 

### Padrões Criacionais

Padrões criacionais abstraem o processo de instanciação de objetos, tornando o sistema independente de como seus objetos são criados, compostos e representados.

#### Factory Method (Método Fábrica)

**Categoria**: Criacional (GoF)

**Intenção**: Definir uma interface para criar um objeto, mas deixar que as subclasses (ou métodos) decidam qual classe instanciar.

**Localização**: Métodos `from_dict()` nas classes de modelo (`facepass/models/`)

**Problema que resolve**: No FacePass, precisamos criar objetos de domínio (Usuario, Gestor, etc.) a partir de dados retornados do banco (dicionários). A lógica de criação é complexa, envolvendo conversões de tipos e tratamento de campos opcionais.

**Implementação**:
```python
class Usuario:
    @classmethod
    def from_dict(cls, data: dict):
        """Factory Method: cria Usuario a partir de dicionário"""
        usuario = cls(
            id=data.get("id"),
            name=data.get("name"),
            email=data.get("email"),
            cpf=data.get("cpf"),
            photo_recognition=data.get("photo_recognition"),
            position=data.get("position"),
        )

        # Lógica de conversão de tipos
        if "approved" in data:
            usuario.approved = bool(data.get("approved"))
        if "created_at" in data:
            created_at_value = data.get("created_at")
            if isinstance(created_at_value, str):
                usuario.created_at = datetime.datetime.fromisoformat(created_at_value)
            elif isinstance(created_at_value, datetime.datetime):
                usuario.created_at = created_at_value

        return usuario

class Gestor:
    @classmethod
    def from_dict(cls, data: dict):
        """Factory Method: cria Gestor a partir de dicionário"""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", "")
        )
```

**Uso no código**:
```python
# Em UsuarioRepository
def get_user_by_id(self, user_id: int) -> Usuario | None:
    query = """SELECT * FROM usuarios WHERE id = %s"""
    result = self.executor.execute_query_one(query, (user_id,))
    # Factory Method usado aqui
    return Usuario.from_dict(result) if result else None
```

**Benefícios**:
- ✅ Centraliza a lógica de criação de objetos
- ✅ Facilita a manutenção (mudanças na criação ficam em um só lugar)
- ✅ Permite tratamento consistente de conversões de tipos
- ✅ Repositories retornam objetos tipados em vez de dicionários

---

### Padrões Estruturais

Padrões estruturais se preocupam com a composição de classes e objetos, facilitando o design ao identificar formas simples de relacionar entidades.

#### Adapter (Adaptador)

**Categoria**: Estrutural

**Intenção**: Converter a interface de uma classe em outra interface esperada pelos clientes, permitindo que classes com interfaces incompatíveis trabalhem juntas.

**Localização**: `facepass/models/faceEncoding.py`

**Problema que resolve**: Arrays NumPy (tipo `numpy.ndarray`) não podem ser armazenados diretamente no MySQL. Precisamos converter entre NumPy arrays (usados pela biblioteca `face_recognition`) e bytes (tipo suportado pelo MySQL como BLOB).

**Implementação**:
```python
import numpy as np
import io

class FaceEncoding:
    """Adapta numpy arrays para o formato de bytes do banco de dados"""

    def __init__(self, user_id: int, encoding, id: Optional[int] = None):
        self.id: Optional[int] = id
        self.user_id: int = user_id
        self.encoding = encoding  # numpy.ndarray

    def to_bytes(self) -> bytes:
        """Adapta numpy array para bytes (interface esperada pelo banco)"""
        buffer = io.BytesIO()
        np.save(buffer, self.encoding, allow_pickle=False)
        return buffer.getvalue()

    @classmethod
    def from_bytes(cls, data: bytes) -> np.ndarray:
        """Adapta bytes de volta para numpy array"""
        buffer = io.BytesIO(data)
        return np.load(buffer, allow_pickle=False)
```

**Diagrama conceitual**:
```
┌─────────────────────┐         ┌──────────────────────┐
│ face_recognition    │         │ MySQL Database       │
│ (espera numpy       │  ◄───►  │ (espera bytes)       │
│  array)             │         │                      │
└─────────────────────┘         └──────────────────────┘
           ▲                              ▲
           │                              │
           │    ┌──────────────┐         │
           └────┤ FaceEncoding │─────────┘
                │  (Adapter)   │
                └──────────────┘
```

**Uso no repositório**:
```python
class FaceEncodingRepository:
    def save_encoding(self, face_encoding: FaceEncoding) -> FaceEncoding:
        query = """INSERT INTO face_encoding (user_id, encoding) VALUES (%s, %s)"""
        # Adapter converte numpy array → bytes
        params = (face_encoding.user_id, face_encoding.to_bytes())
        encoding_id = self.executor.execute_insert(query, params)
        face_encoding.id = encoding_id
        return face_encoding

    def get_encoding_by_user_id(self, user_id: int) -> Optional[FaceEncoding]:
        result = self.executor.execute_query_one(query, (user_id,))
        if result:
            # Adapter converte bytes → numpy array
            encoding_array = FaceEncoding.from_bytes(result['encoding'])
            return FaceEncoding(
                id=result['id'],
                user_id=result['user_id'],
                encoding=encoding_array
            )
        return None
```

**Benefícios**:
- ✅ Permite integração entre bibliotecas incompatíveis (NumPy ↔ MySQL)
- ✅ Conversão bidirecional transparente
- ✅ Encapsula a lógica de conversão em um único lugar
- ✅ Facilita mudanças futuras no formato de armazenamento

---

#### Facade (Fachada)

**Categoria**: Estrutural

**Intenção**: Fornecer uma interface unificada e simplificada para um conjunto de interfaces em um subsistema, tornando o subsistema mais fácil de usar.

**Localização**: `facepass/database/setup_database/connection.py`

**Problema que resolve**: A biblioteca `mysql.connector` possui uma API complexa com muitas configurações, tratamento de exceções e gerenciamento de cursores. O Facade simplifica essa interface para o resto do sistema.

**Implementação**:
```python
import mysql.connector

class DatabaseConnection:
    """Facade: simplifica a interface do mysql.connector"""

    def __init__(self, host, user, password, database=None, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        """Interface simplificada para conexão (esconde complexidade)"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=False,
                charset='utf8mb4',
                use_unicode=True
            )
            print("Conexão bem-sucedida!")
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao MySQL: {err}")
            self.connection = None

    def close(self):
        """Interface simplificada para fechar conexão"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexão fechada com sucesso!")

    def get_connection(self):
        """Retorna a conexão bruta se necessário"""
        return self.connection
```

**Antes do Facade (código complexo)**:
```python
# Sem Facade - código cliente precisa conhecer todos os detalhes
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="senha123",
    database="facepass_db",
    port=3306,
    autocommit=False,
    charset='utf8mb4',
    use_unicode=True,
    connection_timeout=30
)
```

**Com o Facade (código simplificado)**:
```python
# Com Facade - interface simples e clara
db_connection = DatabaseConnection("localhost", "root", "senha123", "facepass_db")
db_connection.connect()
```

**Benefícios**:
- ✅ Simplifica interface complexa do MySQL Connector
- ✅ Centraliza tratamento de erros de conexão
- ✅ Esconde configurações técnicas do resto do sistema
- ✅ Facilita mudanças futuras (trocar de SGBD, por exemplo

---

### Padrões Comportamentais

Padrões comportamentais se preocupam com algoritmos e a atribuição de responsabilidades entre objetos.

#### Strategy (Estratégia)

**Categoria**: Comportamental

**Intenção**: Definir uma família de algoritmos, encapsular cada um deles e torná-los intercambiáveis. Strategy permite que o algoritmo varie independentemente dos clientes que o utilizam.

**Localização**: `facepass/validators/input_validator.py`

**Problema que resolve**: Diferentes tipos de dados (nome, email, CPF, cargo, senha) requerem diferentes estratégias de validação. O padrão Strategy encapsula cada algoritmo de validação de forma independente.

**Implementação**:
```python
import re

class InputValidator:
    """Família de estratégias de validação"""

    @staticmethod
    def validar_name(name: str) -> bool:
        """Estratégia: validação de nome"""
        if not name or len(name.strip()) < 3 or len(name) > 100:
            return False
        return True

    @staticmethod
    def validar_email(email: str) -> bool:
        """Estratégia: validação de email com regex"""
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(regex, email))

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Estratégia: validação de CPF (formato brasileiro)"""
        regex = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$'
        return bool(re.match(regex, cpf))

    @staticmethod
    def validar_position(position: str) -> bool:
        """Estratégia: validação de cargo (lista permitida)"""
        positions_validas = {'Desenvolvedor', 'Analista de Dados', 'Gerente'}
        return position in positions_validas or \
               position.lower() in (p.lower() for p in positions_validas)

    @staticmethod
    def validar_password(password: str) -> bool:
        """Estratégia: validação de senha"""
        return password is not None and len(password.strip()) >= 6

    @staticmethod
    def validar_photo(photo: bytes) -> bool:
        """Estratégia: validação de foto"""
        return photo is not None and len(photo) > 0
```

**Uso no código**:
```python
class UserController:
    def __init__(self, user_service: UsuarioService):
        self.user_service = user_service
        self.validator = InputValidator()  # Contexto usa as estratégias

    def create_user(self, name: str, email: str, cpf: str, ...) -> Dict:
        errors = []

        # Aplicando diferentes estratégias de validação
        if not self.validator.validar_name(name):
            errors.append("Nome inválido (mínimo 3 caracteres).")
        if not self.validator.validar_email(email):
            errors.append("Email inválido.")
        if not self.validator.validar_cpf(cpf):
            errors.append("CPF inválido (formato: 000.000.000-00).")
        if not self.validator.validar_position(position):
            errors.append("Cargo inválido.")

        if errors:
            return {'success': False, 'errors': errors}
        # ... continua
```

**Benefícios**:
- ✅ Cada estratégia de validação é independente
- ✅ Novas estratégias podem ser adicionadas facilmente (OCP)
- ✅ Estratégias podem ser reutilizadas em diferentes contextos
- ✅ Código mais limpo e organizado


---

#### Template Method (Método Template)

**Categoria**: Comportamental

**Intenção**: Definir o esqueleto de um algoritmo em uma operação, postergando alguns passos para subclasses/métodos. Template Method permite que subclasses redefinam certos passos de um algoritmo sem mudar sua estrutura.

**Localização**: `facepass/services/face_recognition_service.py`

**Problema que resolve**: O processo de reconhecimento facial segue sempre os mesmos passos (gerar encoding → buscar conhecidos → comparar → retornar melhor match), mas alguns detalhes podem variar (threshold de confiança, tipo de comparação).

**Implementação**:
```python
import face_recognition
import numpy as np

class FaceRecognitionService:
    """Template Method: define o esqueleto do algoritmo de reconhecimento"""

    def __init__(self, face_encoding_repository: FaceEncodingRepository):
        self.repository = face_encoding_repository
        self.tolerance = 0.6  # Threshold configurável (hook)

    def identify_face(self, image_bytes: bytes) -> Optional[Tuple[int, float]]:
        """Template Method: define o esqueleto do algoritmo"""

        # Passo 1: Gerar encoding da imagem desconhecida
        unknown_encoding = self._generate_encoding(image_bytes)
        if unknown_encoding is None:
            return None

        # Passo 2: Buscar encodings conhecidos do banco
        known_encodings_data = self._fetch_known_encodings()
        if not known_encodings_data:
            return None

        # Passo 3: Comparar encodings
        best_match = self._compare_encodings(unknown_encoding, known_encodings_data)

        # Passo 4: Retornar resultado
        return best_match

    def _generate_encoding(self, image_bytes: bytes):
        """Passo customizável: gera encoding a partir da imagem"""
        if isinstance(image_bytes, (bytes, bytearray)):
            image_file = io.BytesIO(image_bytes)
            image = face_recognition.load_image_file(image_file)
        else:
            image = face_recognition.load_image_file(image_bytes)

        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            return None

        face_encodings = face_recognition.face_encodings(image, face_locations)
        return face_encodings[0] if face_encodings else None

    def _fetch_known_encodings(self):
        """Passo customizável: busca encodings do banco"""
        return self.repository.get_all_encodings()

    def _compare_encodings(self, unknown_encoding, known_encodings_data):
        """Passo customizável: compara encodings e retorna melhor match"""
        known_encodings = [enc.encoding for enc in known_encodings_data]
        known_user_ids = [enc.user_id for enc in known_encodings_data]

        # Calcula distâncias
        distances = face_recognition.face_distance(known_encodings, unknown_encoding)

        # Encontra melhor match
        best_match_index = np.argmin(distances)
        min_distance = distances[best_match_index]

        # Aplica threshold (hook point)
        if min_distance <= self.tolerance:
            confidence = 1 - min_distance
            return (known_user_ids[best_match_index], confidence)

        return None
```

**Estrutura do Template Method**:
```
identify_face() [TEMPLATE METHOD]
  ├── _generate_encoding()      [passo 1 - pode variar]
  ├── _fetch_known_encodings()  [passo 2 - pode variar]
  ├── _compare_encodings()      [passo 3 - pode variar]
  └── return best_match         [passo 4 - fixo]
```

**Benefícios**:
- ✅ Define a estrutura geral do algoritmo de reconhecimento
- ✅ Permite customização de passos individuais sem alterar a estrutura
- ✅ Facilita manutenção (mudanças no fluxo acontecem em um só lugar)
- ✅ Tolerance pode ser ajustado como "hook" do template

**Relação com o livro**: O padrão Template Method é apresentado no Capítulo 6 como forma de definir esqueletos de algoritmos.

---

#### Observer (Observador)

**Categoria**: Comportamental

**Intenção**: Definir uma dependência um-para-muitos entre objetos, de modo que quando um objeto muda de estado, todos os seus dependentes são notificados e atualizados automaticamente.

**Localização**: Sistema de notificações (`facepass/services/`)

**Problema que resolve**: Quando eventos importantes acontecem (novo usuário cadastrado, acesso negado), os gestores (observers) precisam ser notificados automaticamente, sem que o código que gera o evento precise conhecer os detalhes de quem será notificado.

**Implementação**:

**Subject (Observable)**:
```python
class UsuarioService:
    """Subject: gera eventos que serão observados"""

    def __init__(self, usuario_repository: UsuarioRepository,
                 notification_repository: NotificationRepository):
        self.usuario_repository = usuario_repository
        self.notification_service = NotificationService(notification_repository)

    def create_user(self, usuario: Usuario, manager_id: int) -> Usuario | None:
        # Validação e regras de negócio
        if usuario is None:
            raise ValueError("Usuário não pode ser None.")

        usuario.approved = False
        usuario.id = 0

        # Persistência
        usuario_salvo = self.usuario_repository.save_user(usuario)

        # Notifica observadores (gestores)
        self.notification_service.notify_new_user_pending_approval(
            usuario_salvo, manager_id)

        return usuario_salvo

class AccessService:
    """Subject: gera eventos de tentativa de acesso"""

    def register_access_attempt(self, registro: RegistroAcesso,
                                manager_id: int, user_name: Optional[str] = None):
        # Salva registro de acesso
        self.acesso_repository.save_register(registro)

        # Notifica observadores apenas se acesso negado
        if not registro.access_allowed:
            self.notification_service.notify_access_denied(
                registro_acesso=registro,
                manager_id=manager_id,
                user_name=user_name
            )
```

**Observer (Dispatcher de notificações)**:
```python
class NotificationService:
    """Observer: reage a eventos criando notificações para gestores"""

    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    def notify_new_user_pending_approval(self, usuario: Usuario, manager_id: int):
        """Reage ao evento: novo usuário cadastrado"""
        message = f"Novo usuário cadastrado: {usuario.name}. Aguardando aprovação."
        notificacao = Notificacao(
            id=0,
            manager_id=manager_id,
            type_notification="new_user_pending",
            message=message,
            is_read=False,
            created_at=datetime.datetime.now()
        )
        self.notification_repository.save_notification(notificacao)

    def notify_access_denied(self, registro_acesso: RegistroAcesso,
                            manager_id: int, user_name: Optional[str] = None):
        """Reage ao evento: acesso negado"""
        message = f"Acesso negado em {registro_acesso.date_time}."
        if user_name:
            message = f"Tentativa de acesso de {user_name} foi negada."

        notificacao = Notificacao(
            id=0,
            manager_id=manager_id,
            type_notification="access_denied",
            message=message,
            is_read=False,
            registro_acesso_id=registro_acesso.id,
            created_at=datetime.datetime.now()
        )
        self.notification_repository.save_notification(notificacao)
```

**Diagrama conceitual**:
```
┌──────────────────┐          ┌─────────────────────┐
│ UsuarioService   │          │ NotificationService │
│ (Subject)        │─notify──▶│ (Observer)          │
└──────────────────┘          └─────────────────────┘
                                        │
                                        ▼
                              ┌─────────────────────┐
                              │ Gestor recebe       │
                              │ notificação         │
                              └─────────────────────┘
```

**Benefícios**:
- ✅ Desacoplamento entre quem gera eventos e quem reage a eles
- ✅ Novos observadores podem ser adicionados facilmente
- ✅ Sistema orientado a eventos (event-driven)
- ✅ Gestores são notificados automaticamente sobre eventos importantes

---

### Padrões não usados

Alguns padrões de projetos não foram utilizados pois na arquitetura esquematizada monolitica para nosso projeto, não foi necessário. Mas mudanças de arquitetura influenciariam diretamente no nosso projeto, como implementação de API e etc. 

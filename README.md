# FacePass

Sistema de reconhecimento facial para controle de acesso desenvolvido como parte da disciplina de Engenharia de Software (UFRN).

## Índice

- [FacePass - Sistema de Reconhecimento Facial](#facepass---sistema-de-reconhecimento-facial)
- [Como Executar com Docker](#como-executar-com-docker)
- [Instalação Manual](#instalação-manual)
- [Histórias de Usuário](#histórias-de-usuário)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Licença](#licença)

## FacePass - Sistema de Reconhecimento Facial

O FacePass é um sistema de controle de acesso baseado em reconhecimento facial. Ele possibilita o cadastro de usuários, a autenticação por imagem e o gerenciamento de permissões de entrada em ambientes físicos ou virtuais. Além disso, o sistema mantém logs de acessos para auditoria.

### Objetivos

- Garantir segurança e praticidade no acesso
- Evitar fraudes comuns em sistemas de senha/cartão
- Servir como aplicação prática dos conceitos da disciplina de Engenharia de Software
- Manter registros de acesso para fins de auditoria e segurança

### Componentes

- Luiz Felipe de Souza Silva
- Carlos Eduardo Nascimento Morais
- Caio Mendonça de Andrade

## Como Executar com Docker

A forma mais simples de executar o projeto é utilizando Docker, que gerencia automaticamente o banco de dados e a aplicação.

### Pré-requisitos

- Docker instalado ([Instruções de instalação](https://docs.docker.com/get-docker/))
- Docker Compose instalado ([Instruções de instalação](https://docs.docker.com/compose/install/))

### Passos para Execução

**1. Clone o repositório:**

```bash
git clone https://github.com/luiz-pytech/FacePass-EngSoft.git
cd FacePass-EngSoft
```

**2. Configure as variáveis de ambiente:**

Renomeie o arquivo `.env.example` para `.env` e configure as credenciais do banco de dados:

```env
DB_HOST=mysql
DB_USER=facepass_user
DB_PASSWORD=sua_senha_segura
DB_NAME=facepass_db
DB_PORT=3306
```

**3. Inicie os containers:**

```bash
docker-compose up -d
```

Este comando irá:
- Baixar as imagens necessárias
- Criar o container do MySQL
- Criar o container da aplicação FacePass
- Inicializar o banco de dados automaticamente
- Iniciar a aplicação Streamlit

**4. Acesse a aplicação:**

Abra seu navegador e acesse: `http://localhost:8501`

### Comandos Úteis

```bash
# Ver logs da aplicação
docker-compose logs -f facepass

# Ver logs do banco de dados
docker-compose logs -f mysql

# Parar os containers
docker-compose down

# Parar e remover volumes (dados do banco)
docker-compose down -v

# Reconstruir as imagens
docker-compose up -d --build
```

## Instalação Manual

Se preferir executar sem Docker, siga os passos abaixo:

### Pré-requisitos

- Python 3.11+
- MySQL Server 8.0+

### Passos para Instalação

**1. Clone o repositório:**

Você pode clonar via HTTPS:
```bash
git clone https://github.com/luiz-pytech/FacePass-EngSoft.git
cd FacePass-EngSoft
```

Ou via SSH:
```bash
git clone git@github.com:luiz-pytech/FacePass-EngSoft.git
cd FacePass-EngSoft
```

**2. Crie e ative um ambiente virtual:**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**4. Configure o arquivo .env:**

Renomeie o arquivo `.env.example` para `.env` e adicione suas credenciais do banco de dados:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=facepass_db
DB_PORT=3306
```

**5. Crie as tabelas no banco de dados:**

```bash
python -m facepass.database.setup_database.scripts_tables
```

**6. Execute a aplicação:**

```bash
streamlit run facepass/ui/app.py
```

A aplicação estará disponível em: `http://localhost:8501`

## Histórias de Usuário

As histórias de usuário a seguir serviram como ponto de partida para o desenvolvimento do projeto. Para mais detalhes, consulte a [documentação completa](docs/historias_de_usuario.md).

<table>
<tr>
<td width="33%" valign="top">

### US1 - Gerenciar Usuários

**Como** gestor
**Gostaria de** gerenciar os usuários: cadastrando, removendo e atualizando dados
**Para** ter controle sobre os mesmos

**Critérios principais:**
- Cadastrar e remover usuários
- Atualizar dados dos usuários
- Feedback das ações realizadas

</td>
<td width="33%" valign="top">

### US2 - Monitorar Registros

**Como** gestor
**Quero** visualizar e filtrar relatórios de acesso
**Para** auditar a segurança e movimentação

**Critérios principais:**
- Exibir nome, data, hora e local
- Filtrar por usuário e período
- Exportar dados (CSV/PDF)

</td>
<td width="33%" valign="top">

### US3 - Notificações

**Como** gestor
**Quero** ser notificado sobre acessos negados
**Para** identificar falhas ou tentativas indevidas

**Critérios principais:**
- Notificar rostos não reconhecidos
- Notificar acessos negados
- Incluir data, hora e local

</td>
</tr>
</table>

## Estrutura do Projeto

```
FacePass-EngSoft/
├── LICENSE
├── README.md
├── .env.example
├── requirements.txt
├── user_test.py              # testes com pytest coverage
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── facepass/                  # Código-fonte principal
│   ├── controllers/           # Conexão com UI
│   ├── services/              # Lógica de negócio
│   ├── models/                # Modelos de dados
│   ├── database/              # Persistência e configuração do banco
│   │   ├── setup_database/    # Scripts de configuração
│   │   └── repository/        # Camada de acesso a dados
│   └── validators/            # funções de validações
│   └── ui/ 
|       ├── ui_pages/                
│       └── app.py             # Aplicação principal
└── docs/                      # Documentação
    ├── user_stories/
    └── principles/
    └── diagrams/
```

## Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo `LICENSE` para mais detalhes.

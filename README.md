# FacePass - Eng-de-Software-UFRN

Sistema de reconhecimento facial para controle de acesso desenvolvido como parte da disciplina de Engenharia de Software (UFRN).

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Como clonar ou baixar](#como-clonar-ou-baixar)  
- [Estrutura do Projeto](#estrutura-do-projeto)  
- [Licença](#licença)  
- [Histórias de Usuário](#histórias-de-usuário)

## Sobre o Projeto

### Título
FacePass - Reconhecimento Facial

### Descrição
O FacePass é um sistema de controle de acesso baseado em reconhecimento facial. Ele possibilita o cadastro de usuários, a autenticação por imagem e o gerenciamento de permissões de entrada em ambientes físicos ou virtuais. Além disso, o sistema mantém logs de acessos para auditoria.

### Objetivo

- Garantir segurança e praticidade no acesso.
- Evitar fraudes comuns em sistemas de senha/cartão.
- Servir como aplicação prática dos conceitos da disciplina de Engenharia de Software.

### Componentes
- Luiz Felipe de Souza Silva
- Carlos Eduardo Nascimento Morais
- Caio Mendonça de Andrade

### Histórias de usuário
**1. Gerenciar usuários**

Como gestor gostaria de gerenciar os usuários: Cadastrando, removendo e atualizando dados os dado para controle dos mesmos

**- Critérios de aceitação:**
- O gestor deve poder cadastrar novos usuários e remover usuários
- O gestor deve poder atualizar os dados dos usuários
- Ao final o gestor deve receber uma mensagem de feedback de sua ação.

**2. Monitorar registros de acesso**

Como um gestor, eu quero visualizar e filtrar um relatório de registros de acesso, para que eu possa auditar a segurança e a movimentação no ambiente.

**- Critérios de aceitação:**
- A tela de relatório deve exibir uma lista com, no mínimo: Nome do Usuário, Data, Hora e Local/Câmera do acesso.
- Deve ser possível filtrar os registros por nome de usuário.
- Deve ser possível filtrar os registros por um intervalo de data e hora.
- Deve haver uma opção para exportar os dados filtrados para um arquivo (ex: .CSV ou .PDF)

**3. Notificações de Tentativa de Acesso Negado**
Como um gestor, eu quero ser notificado em tempo real sobre tentativas de acesso negadas, para que eu possa identificar rapidamente possíveis falhas no sistema ou tentativas de entrada indevida

**- Critérios de aceitação:**
- Quando um rosto não reconhecido (não cadastrado) tenta o acesso, uma notificação deve ser gerada para o gestor.
- Quando um usuário cadastrado tem seu acesso negado por algum motivo (ex: foto de baixa qualidade, bloqueio temporário), uma notificação também deve ser gerada.
- A notificação deve conter, no mínimo, a data, a hora e o local/câmera da tentativa de acesso.

## Como clonar ou baixar

Você pode obter este repositório de três formas:

### Clonar via HTTPS

```bash
git clone https://github.com/mvapedrosa/Eng-de-Software-UFRN.git
```

Isso criará uma cópia local do repositório em sua máquina.

### Clonar via SSH

Se você já configurou sua chave SSH no GitHub, pode clonar usando:

```bash
git clone git@github.com:mvapedrosa/Eng-de-Software-UFRN.git
```

Isso criará uma cópia local do repositório em sua máquina.

### Baixar como ZIP

1. Acesse a página do repositório no GitHub:
   [https://github.com/luiz-pytech/FacePass-EngSoft.git](https://github.com/luiz-pytech/FacePass-EngSoft.git)
2. Clique no botão **Code** (verde).
3. Selecione **Download ZIP**.
4. Extraia o arquivo ZIP para o local desejado em seu computador.


## Estrutura do Projeto

> *Esta seção pode variar conforme a organização do repositório de cada grupo.*

```
FacePass-EngSoft/
├── LICENSE
├── README.md
├── requirements.txt
├── main.py
├── facepass/          # código-fonte principal
│   ├── core/          # lógica de reconhecimento
│   ├── database/      # persistência de dados
│   ├── api/           # rotas/serviços
│   └── ui/            # interface (streamlit/web)
└── docs/              # documentação e diagramas
```

- LICENSE: termos da licença do projeto (MIT).
- README.md: este arquivo de apresentação.
requirements.txt: lista das dependências necessárias para executar o projeto.
- main.py: ponto de entrada da aplicação (inicializa o sistema).
- facepass/core: lógica principal de reconhecimento facial (detecção e autenticação).
- facepass/database: gerenciamento da persistência de dados (usuários, imagens e logs).
- facepass/api: rotas e serviços de integração (ex.: cadastro, autenticação, logs).
- facepass/ui: interface gráfica/web (ex.: protótipo com Streamlit ou página em Flask).
- docs/: documentação e diagramas de apoio ao projeto.

## Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo `LICENSE` para mais detalhes.

# Histórias de Usuário - FacePass

Este documento descreve as histórias de usuário que guiaram o desenvolvimento do sistema FacePass. Essas histórias representam as necessidades dos principais atores do sistema e serviram como ponto de partida para a implementação das funcionalidades.

## US1 - Gerenciar Usuários

**Como** gestor
**Gostaria de** gerenciar os usuários: cadastrando, removendo e atualizando dados
**Para** ter controle sobre os mesmos

### Critérios de Aceitação
- O gestor deve poder cadastrar novos usuários e remover usuários
- O gestor deve poder atualizar os dados dos usuários
- Ao final o gestor deve receber uma mensagem de feedback de sua ação

---

## US2 - Monitorar Registros de Acesso

**Como** gestor
**Quero** visualizar e filtrar um relatório de registros de acesso
**Para que** eu possa auditar a segurança e a movimentação no ambiente

### Critérios de Aceitação
- A tela de relatório deve exibir uma lista com, no mínimo: Nome do Usuário, Data, Hora e Local/Câmera do acesso
- Deve ser possível filtrar os registros por nome de usuário
- Deve ser possível filtrar os registros por um intervalo de data e hora
- Deve haver uma opção para exportar os dados filtrados para um arquivo (ex: CSV ou PDF)

---

## US3 - Notificações de Tentativa de Acesso Negado

**Como** gestor
**Quero** ser notificado em tempo real sobre tentativas de acesso negadas
**Para que** eu possa identificar rapidamente possíveis falhas no sistema ou tentativas de entrada indevida

### Critérios de Aceitação
- Quando um rosto não reconhecido (não cadastrado) tenta o acesso, uma notificação deve ser gerada para o gestor
- Quando um usuário cadastrado tem seu acesso negado por algum motivo (ex: foto de baixa qualidade, bloqueio temporário), uma notificação também deve ser gerada
- A notificação deve conter, no mínimo, a data, a hora e o local/câmera da tentativa de acesso

# Principios de Projeto - FacePass

Este documento descreve os princípios de projeto de software aplicáveis ao sistema FacePass, evidenciando boas práticas utilizadas na modelagem e implementação inicial do projeto.

---

## Princípios aplicados ou aplicavéis no sistema

### Single responsability principle(SRP)

O Princípio da Responsabilidade Única afirma que cada classe deve ter apenas um motivo para mudar, ou seja, uma única responsabilidade.

Na etapa inicial do projeto, foram criadas as classes Usuario e RegistroAcesso, cuja função é apenas representar entidades.
A lógica de negócio e manipulação de dados é tratada por outras camadas, como usuario_service.py, responsável por gerenciar operações e regras relacionadas aos usuários.

Resumidamente:

| Classe | Responsabilidade | Justificativa |
|--------|------------------|---------------|
| Usuario| Representar dados do usuário| Apenas armazena dados, não faz validação ou persistência |
| RegistroAcesso| Representar logs de acesso| Apenas dados, sem lógica de filtro ou exportação |
| UsuarioService | Lógica de negócio de usuários | Orquestra operações, não faz persistência |

### Open/Close principle (OCP)

O Princípio Aberto/Fechado estabelece que as classes devem estar abertas para extensão, mas fechadas para modificação.
Isso significa que é possível adicionar novos comportamentos sem alterar o código existente, evitando que mudanças quebrem funcionalidades já implementadas.

Um exemplo de aplicação no FacePass seria a criação de uma classe de validação.
Inicialmente, ela pode validar apenas e-mail e CPF, mas futuramente poderá ser estendida para incluir novas validações, como senhas, formato de imagem facial ou padrões de segurança, sem a necessidade de modificar a implementação original.

### Conclusão
A aplicação desses princípios contribui para um código modular, escalável e de fácil manutenção, alinhado aos fundamentos da programação orientada a objetos (POO) e do Design Limpo (Clean Code).
O FacePass continuará a evoluir seguindo esses princípios, garantindo qualidade e robustez no desenvolvimento do sistema.

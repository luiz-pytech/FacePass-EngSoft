from typing import List, Optional
from facepass.models.usuario import Usuario

class UsuarioService:
    """
    SRP: responsável apenas pelo serviço de lógica de negócio para usuários
    
    """
    
    def __init__(self, usuario: Usuario):
        self._usuario = usuario
    
    def cadastrar_usuario(self, usuario: Usuario) -> tuple[bool, str, Optional[Usuario]]:
        """
        Cadastra novo usuário
        Retorna: (sucesso, mensagem, usuario_cadastrado)
        """
        
        usuario.aprovado = False
        usuario.ativo = False
        #usuario_salvo = self._repository.salvar(usuario) enviar para ser salvo no banco de dados
        usuario_salvo = usuario  # Simulação de salvamento

        #TODO: Gerar notificação para gestor (US3)

        return True, "Cadastro enviado para aprovação", usuario_salvo
    
    def aprovar_cadastro(self, usuario_id: int) -> tuple[bool, str]:
        """
        Gestor aprova cadastro (US1)
        """
        usuario = self._repository.buscar_por_id(usuario_id)
        
        if not usuario:
            return False, "Usuário não encontrado"
        
        if usuario.aprovado:
            return False, "Usuário já aprovado"
        
        usuario.aprovado = True
        usuario.ativo = True
        self._repository.atualizar(usuario)
        
        return True, f"Usuário {usuario.nome} aprovado com sucesso"
    
    def rejeitar_cadastro(self, usuario_id: int) -> tuple[bool, str]:
        """
        Gestor rejeita cadastro (US1)
        """
        usuario = self._repository.buscar_por_id(usuario_id)
        
        if not usuario:
            return False, "Usuário não encontrado"
        
        self._repository.remover(usuario_id)
        
        return True, "Cadastro rejeitado"
    
    def listar_pendentes_aprovacao(self) -> List[Usuario]:
        """
        Lista usuários aguardando aprovação do gestor (US1)
        """
        return self._repository.listar_pendentes()
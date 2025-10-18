from validator_service import ValidatorService
from facepass.models.user import Usuario
from facepass.database.repository.user_repository import UsuarioRepository
from facepass.services.notification_service import NotificationService
from facepass.database.repository.notification_repository import NotificationRepository


class UsuarioService:
    def __init__(self, usuario_repository: UsuarioRepository, notification_repository: NotificationRepository):
        self.usuario_repository = usuario_repository
        self.notification_service = NotificationService(
            notification_repository)

    def create_user(self, usuario: Usuario) -> Usuario | None:
        if usuario == None:
            raise ValueError("Usuário não pode ser None.")

        if not ValidatorService.validar_usuario(usuario):
            raise ValueError("Dados do usuário inválidos.")

        usuario.aprovado = False
        usuario.id = 0
        usuario_salvo = self.usuario_repository.save_user(usuario)

        if usuario_salvo is None:
            raise RuntimeError("Falha ao salvar usuário.")

        self.notification_service.send_approval_request(usuario_salvo)

        return usuario_salvo

    def update_user(self, usuario: Usuario) -> None:
        if not ValidatorService.validar_usuario(usuario):
            raise ValueError("Dados do usuário inválidos.")
        existing_user = self.usuario_repository.get_user_by_id(usuario.id)
        if not existing_user:
            raise ValueError("Usuário não encontrado.")
        self.usuario_repository.save_user(usuario)

    def remove_user(self, user_id: int) -> None:
        existing_user = self.usuario_repository.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("Usuário não encontrado.")
        self.usuario_repository.remove_user(user_id)

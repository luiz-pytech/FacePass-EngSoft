from facepass.models.user import Usuario
from facepass.database.repository.user_repository import UsuarioRepository
from facepass.services.notification_service import NotificationService
from facepass.database.repository.notification_repository import NotificationRepository


class UsuarioService:
    def __init__(self, usuario_repository: UsuarioRepository, notification_repository: NotificationRepository):
        self.usuario_repository = usuario_repository
        self.notification_service = NotificationService(
            notification_repository)

    def create_user(self, usuario: Usuario, manager_id: int) -> Usuario | None:
        if usuario is None:
            raise ValueError("Usuário não pode ser None.")

        usuario.approved = False
        usuario.id = 0

        usuario_salvo = self.usuario_repository.save_user(usuario)

        if usuario_salvo is None:
            raise RuntimeError("Falha ao salvar usuário.")

        # Notifica gestor sobre novo cadastro pendente (US1)
        self.notification_service.notify_new_user_pending_approval(
            usuario_salvo, manager_id)

        return usuario_salvo

    def approve_user(self, user_id: int) -> None:
        existing_user = self.usuario_repository.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("Usuário não encontrado.")

        self.usuario_repository.approve_user(user_id)

    def reject_user(self, user_id: int) -> None:
        self.usuario_repository.remove_user(user_id)
    
    def remove_user(self, user_id: int) -> None:
        existing_user = self.usuario_repository.get_user_by_id(user_id)
        if not existing_user:
                raise ValueError("Usuário não encontrado.")

        self.usuario_repository.remove_user(user_id)

    def list_pending_approvals(self):
        return self.usuario_repository.list_unapproved_users()

    def list_approved_users(self):
        return self.usuario_repository.list_approved_users()

    def update_user(self, usuario: Usuario) -> None:

        if usuario is None:
            raise ValueError("Usuário não pode ser None.")

        existing_user = self.usuario_repository.get_user_by_id(usuario.id)
        if not existing_user:
            raise ValueError("Usuário não encontrado.")

        self.usuario_repository.save_user(usuario)

    def list_all_users(self):
        return self.usuario_repository.list_all_users()

    def get_user_by_id(self, user_id: int):
        return self.usuario_repository.get_user_by_id(user_id)

    def get_user_by_email(self, email: str):
        return self.usuario_repository.get_user_by_email(email)

    def get_statistics(self) -> dict:
        total = self.usuario_repository.get_user_count()
        approved = self.usuario_repository.get_approved_user_count()
        pending = self.usuario_repository.get_pending_user_count()

        return {
            'total': total,
            'approved': approved,
            'pending': pending
        }

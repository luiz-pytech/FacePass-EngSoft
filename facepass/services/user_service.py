from facepass.services.validator_service import ValidatorService
from facepass.models.user import Usuario
from facepass.database.repository.user_repository import UsuarioRepository
from facepass.services.notification_service import NotificationService
from facepass.database.repository.notification_repository import NotificationRepository


class UsuarioService:
    """
    User management service.

    Responsible for business logic related to:
    - Registering new users
    - Approving/rejecting registrations (US1)
    - Updating and removing users
    """

    def __init__(self, usuario_repository: UsuarioRepository, notification_repository: NotificationRepository):
        self.usuario_repository = usuario_repository
        self.notification_service = NotificationService(
            notification_repository)

    def create_user(self, usuario: Usuario, manager_id: int) -> Usuario | None:
        """
        Registers a new user in the system.

        Args:
            usuario: The user data to register
            manager_id: ID of the manager who will receive an approval notification

        Returns:
            The registered user

        Raises:
            ValueError: If the user data is invalid
            RuntimeError: If saving to the database fails
        """
        if usuario is None:
            raise ValueError("Usuário não pode ser None.")

        if not ValidatorService.validar_usuario(usuario):
            raise ValueError("Dados do usuário inválidos.")

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
        """
        Approves a pending user registration (US1).

        Args:
            user_id: ID of the user to approve

        Raises:
            ValueError: If the user is not found
        """
        existing_user = self.usuario_repository.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("Usuário não encontrado.")

        self.usuario_repository.approve_user(user_id)

    def reject_user(self, user_id: int) -> None:
        """
        Rejects a pending user registration by removing it from the system (US1).

        Args:
            user_id: ID of the user to reject

        Raises:
            ValueError: If the user is not found
        """
        self.remove_user(user_id)

    def list_pending_approvals(self):
        """
        Lists all users awaiting approval (US1).

        Returns:
            List of unapproved users
        """
        return self.usuario_repository.list_unapproved_users()

    def update_user(self, usuario: Usuario) -> None:
        """
        Updates an existing user's data.

        Args:
            usuario: The updated user data

        Raises:
            ValueError: If the data is invalid or the user does not exist
        """
        if not ValidatorService.validar_usuario(usuario):
            raise ValueError("Dados do usuário inválidos.")

        existing_user = self.usuario_repository.get_user_by_id(usuario.id)
        if not existing_user:
            raise ValueError("Usuário não encontrado.")

        self.usuario_repository.save_user(usuario)

    def remove_user(self, user_id: int) -> None:
        """
        Removes a user from the system.

        Args:
            user_id: ID of the user to remove

        Raises:
            ValueError: If the user is not found
        """
        existing_user = self.usuario_repository.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("Usuário não encontrado.")

        self.usuario_repository.remove_user(user_id)

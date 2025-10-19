from typing import Optional
from facepass.database.repository.register_repository import RegistroRepository
from facepass.database.repository.user_repository import UsuarioRepository
from facepass.models.registerAccess import RegistroAcesso
from facepass.services.notification_service import NotificationService
from facepass.database.repository.notification_repository import NotificationRepository


class AccessService:
    """
    Access records management service.

    Responsible for:
    - Processing access attempts
    - Recording allowed and denied accesses
    - Notifying managers about denied accesses
    """

    def __init__(self, acesso_repository: RegistroRepository, notification_repository: NotificationRepository, usuario_repository: UsuarioRepository):
        self.acesso_repository = acesso_repository
        self.usuario_repository = usuario_repository
        self.notification_service = NotificationService(
            notification_repository)

    def register_access_attempt(self, registro: RegistroAcesso, manager_id: int, user_name: Optional[str] = None) -> None:
        """
        Registers an access attempt in the system.

        Args:
            registro: Access record data
            manager_id: ID of the manager who will receive a notification if access is denied
            user_name: User name (if recognized)

        Raises:
            ValueError: If registro is invalid
        """
        if not registro:
            raise ValueError("Registro de acesso inválido.")

        self.acesso_repository.save_register(registro)

        if not registro.access_allowed:
            self.notification_service.notify_access_denied(
                registro_acesso=registro,
                manager_id=manager_id,
                user_name=user_name
            )

    def get_access_logs_by_period(self, start_date: str, end_date: str):
        """
        Fetches access logs by period.

        Args:
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)

        Returns:
            List of access logs in the period
        """
        return self.acesso_repository.get_register_by_period(start_date, end_date)

    def get_access_logs_by_user(self, user_id: int):
        """
        Fetches access logs by user.

        Args:
            user_id: ID of the user

        Returns:
            List of access logs for the user
        """
        return self.acesso_repository.get_registers_by_user(user_id)

    def list_denied_accesses(self):
        """
        Fetches all denied accesses (US2, US3).

        Returns:
            List of denied access logs
        """
        return self.acesso_repository.list_acess_denied()

    def export_access_logs(self):
        """
        Exports all access logs (US2).

        Returns:
            List of all access logs
        """
        return self.acesso_repository.export_registers()

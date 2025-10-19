from datetime import datetime
from typing import Optional
from facepass.models.user import Usuario
from facepass.models.notification import Notificacao
from facepass.models.registerAccess import RegistroAcesso
from facepass.database.repository.notification_repository import NotificationRepository


class NotificationService:
    """
    Notification service for managers.

    Responsible for creating and managing notifications that alert managers about:
    - New users pending approval (US1)
    - Denied access attempts (US3)
    """

    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    def notify_new_user_pending_approval(self, usuario: Usuario, manager_id: int) -> None:
        """
        Creates a notification for the manager when a new user registers and is pending approval.

        Args:
            usuario: The user who registered.
            manager_id: ID of the manager who will receive the notification.

        Raises:
            ValueError: If the provided user is invalid.
        """
        if not usuario:
            raise ValueError("Usuário inválido para notificação.")

        message = (
            f"Novo usuário cadastrado: {usuario.name} ({usuario.email}). "
            f"Aguardando aprovação do cadastro."
        )

        notificacao = Notificacao(
            id=0,
            manager_id=manager_id,
            access_register_id=0,
            created_at=datetime.now(),
            type_notification="new_user_pending",
            message=message,
            is_read=False
        )

        self.notification_repository.save_notification(notificacao)

    def notify_access_denied(self, registro_acesso: RegistroAcesso, manager_id: int, user_name: Optional[str] = None) -> None:
        """
        Creates a notification for a manager when an access attempt is denied.

        Args:
            registro_acesso: The denied access record.
            manager_id: ID of the manager who will receive the notification.
            user_name: Name of the user if recognized, or None if unrecognized.

        Raises:
            ValueError: If the access record is invalid.
        """
        if not registro_acesso:
            raise ValueError("Registro de acesso inválido para notificação.")

        if not registro_acesso.access_allowed:
            if user_name:
                message = (
                    f"Acesso negado para usuário {user_name}. "
                    f"Motivo: {registro_acesso.reason_denied or 'Não especificado'}. "
                    f"Data/Hora: {registro_acesso.created_at.strftime('%d/%m/%Y %H:%M:%S')}"
                )
            else:
                message = (
                    f"Tentativa de acesso por pessoa não reconhecida. "
                    f"Motivo: {registro_acesso.reason_denied or 'Rosto não cadastrado'}. "
                    f"Data/Hora: {registro_acesso.created_at.strftime('%d/%m/%Y %H:%M:%S')}"
                )

            notificacao = Notificacao(
                id=0,
                manager_id=manager_id,
                access_register_id=registro_acesso.id,
                created_at=datetime.now(),
                type_notification="access_denied",
                message=message,
                is_read=False
            )

            self.notification_repository.save_notification(notificacao)

    def list_unread_notifications(self, manager_id: Optional[int] = None):
        """
        List unread notifications.

        Args:
            manager_id: If provided, filters by specific manager

        Returns:
            List of unread notifications
        """
        if manager_id:
            all_notifications = self.notification_repository.get_notifications_by_manager(
                manager_id)

            return [n for n in all_notifications if not n[6]]
        return self.notification_repository.list_unread_notifications()

    def mark_as_read(self, notification_id: int) -> None:
        """
        Marks a notification as read.

        Args:
            notification_id: ID of the notification
        """
        self.notification_repository.mark_notification_as_read(notification_id)

    def delete_notification(self, notification_id: int) -> None:
        """
        Deletes a notification.

        Args:
            notification_id: ID of the notification
        """
        self.notification_repository.delete_notification(notification_id)

    def list_all_notifications(self, manager_id: Optional[int] = None):
        """
        Lists all notifications (read and unread).

        Args:
            manager_id: If provided, filters by specific manager

        Returns:
            List of all notifications
        """
        if manager_id:
            return self.notification_repository.get_notifications_by_manager(manager_id)
        return self.notification_repository.list_all_notifications()

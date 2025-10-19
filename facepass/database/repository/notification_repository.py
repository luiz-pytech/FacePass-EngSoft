from typing import Any
from facepass.database.setup_database.executor_query import QueryExecutor
from facepass.models.notification import Notificacao
from dotenv import load_dotenv

load_dotenv()


class NotificationRepository:
    def __init__(self, connection: Any):
        self.connection = connection
        self.executor = QueryExecutor(self.connection)

    def save_notification(self, notification: Notificacao) -> Notificacao:
        query = """
            INSERT into notifications (manager_id, access_register_id, created_at, type_notification, message, is_read)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        params = (notification.manager_id, notification.access_register_id,
                  notification.created_at, notification.type_notification, notification.message, notification.is_read)
        notification_id = self.executor.execute_insert(query, params)

        # Atualizar o ID da notificação com o ID gerado pelo banco
        notification.id = notification_id
        return notification

    def get_notifications_by_manager(self, manager_id: int):
        query = """
            SELECT id, manager_id, access_register_id, created_at, type_notification, message, is_read FROM notifications WHERE manager_id = %s
        """
        params = (manager_id,)
        results = self.executor.execute_query(query, params)
        return results

    def delete_notification(self, notification_id: int) -> None:
        query = """
            DELETE FROM notifications WHERE id = %s
        """
        params = (notification_id,)
        self.executor.execute_update(query, params)

    def mark_notification_as_read(self, notification_id: int) -> None:
        query = """
            UPDATE notifications SET is_read = TRUE WHERE id = %s
        """
        params = (notification_id,)
        self.executor.execute_update(query, params)

    def list_all_notifications(self):
        query = """
            SELECT id, manager_id, access_register_id, created_at, type_notification, message, is_read FROM notifications
        """
        results = self.executor.execute_query(query)
        return results

    def list_unread_notifications(self):
        query = """
            SELECT id, manager_id, access_register_id, created_at, type_notification, message, is_read FROM notifications WHERE is_read = FALSE
        """
        results = self.executor.execute_query(query)
        return results

    def get_unread_count_by_manager(self, manager_id: int) -> int:
        """Conta notificações não lidas de um gestor específico"""
        query = """
            SELECT COUNT(*) as total
            FROM notifications
            WHERE manager_id = %s AND read = FALSE
        """
        params = (manager_id,)
        result = self.executor.execute_query_one(query, params)
        return result['total'] if result else 0

    def get_notifications_with_details(self, manager_id: int):
        """Retorna notificações com JOIN para pegar detalhes do registro/usuário"""
        query = """
            SELECT n.id, n.manager_id, n.access_register_id, n.created_at,
                   n.type_notification, n.message, n.is_read,
                   ar.type_access, ar.access_allowed, ar.reason_denied,
                   u.name as user_name, u.email as user_email
            FROM notifications n
            LEFT JOIN accessRegisters ar ON n.access_register_id = ar.id
            LEFT JOIN users u ON ar.user_id = u.id
            WHERE n.manager_id = %s
            ORDER BY n.created_at DESC
        """
        params = (manager_id,)
        results = self.executor.execute_query(query, params)
        return results

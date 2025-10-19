import mysql.connector
from facepass.database.setup_database.executor_query import QueryExecutor
from facepass.models.notification import Notificacao
from dotenv import load_dotenv

load_dotenv()


class NotificationRepository:
    def __init__(self, connection: mysql.connector.MySQLConnection):
        self.connection = connection
        self.executor = QueryExecutor(self.connection)

    def save_notification(self, notification: Notificacao) -> None:
        query = """
            INSERT into notifications (id, manager_id, access_register_id, created_at, type_notification, message, read) VALUES
            (%s, %s, %s, %s, %s, %s, %s);
        """
        params = (notification.id, notification.manager_id,
                  notification.access_register_id, notification.created_at, notification.type_notification, notification.message, notification.read)
        self.executor.execute_insert(query, params)

    def get_notifications_by_manager(self, manager_id: int):
        query = """
            SELECT id, manager_id, access_register_id, created_at, type_notification, message, read FROM notifications WHERE manager_id = %s
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
            UPDATE notifications SET read = TRUE WHERE id = %s
        """
        params = (notification_id,)
        self.executor.execute_update(query, params)

    def list_all_notifications(self):
        query = """
            SELECT id, manager_id, access_register_id, created_at, type_notification, message, read FROM notifications
        """
        results = self.executor.execute_query(query)
        return results

    def list_unread_notifications(self):
        query = """
            SELECT id, manager_id, access_register_id, created_at, type_notification, message, read FROM notifications WHERE read = FALSE
        """
        results = self.executor.execute_query(query)
        return results

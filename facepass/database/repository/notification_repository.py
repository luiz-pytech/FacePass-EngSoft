import mysql.connector
from setup_database.executor_query import QueryExecutor
from facepass.models.notification import Notificacao
from dotenv import load_dotenv

load_dotenv()


class NotificationRepository:
    def __init__(self, connection: mysql.connector.MySQLConnection):
        self.connection = connection
        self.executor = QueryExecutor(self.connection)

    def save_notification(self, notification: Notificacao) -> None:
        query = """
            INSERT into notifications (id, gestor_id, registro_acesso_id, data_hora, tipo_notificacao, mensagem) VALUES
            (%s, %s, %s, %s, %s, %s);
        """
        params = (notification.id, notification.gestor_id,
                  notification.registro_acesso_id, notification.data_hora, notification.tipo_notificacao, notification.mensagem)
        self.executor.execute_insert(query, params)

    def get_notifications_by_gestor(self, gestor_id: int):
        query = """
            SELECT id, gestor_id, registro_acesso_id, data_hora, tipo_notificacao, mensagem FROM notifications WHERE gestor_id = %s
        """
        params = (gestor_id,)
        results = self.executor.execute_query(query, params)
        return results

    def delete_notification(self, notification_id: int) -> None:
        query = """
            DELETE FROM notifications WHERE id = %s
        """
        params = (notification_id,)
        self.executor.execute_update(query, params)

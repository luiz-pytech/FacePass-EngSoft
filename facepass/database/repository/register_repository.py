import mysql.connector
from facepass.database.setup_database.executor_query import QueryExecutor
from facepass.models.user import Usuario
from facepass.models.registerAccess import RegistroAcesso
from dotenv import load_dotenv
import os

load_dotenv()


class RegistroRepository:
    def __init__(self, connection: mysql.connector.MySQLConnection):
        self.connection = connection
        self.executor = QueryExecutor(self.connection)

    def save_register(self, registro: RegistroAcesso) -> None:
        query = """
            INSERT into accessRegisters (id, user_id, created_at, type_access, access_allowed, reason_denied, captured_image) VALUES
            (%s, %s, %s, %s, %s, %s, %s);
        """
        params = (registro.id, registro.user_id, registro.created_at,
                  registro.type_access, registro.access_allowed, registro.reason_denied, registro.captured_image)
        self.executor.execute_insert(query, params)

    def get_register_by_period(self, start_date: str, end_date: str):
        query = """
            SELECT id, user_id, created_at, type_access, access_allowed, reason_denied, captured_image
            FROM accessRegisters
            WHERE created_at BETWEEN %s AND %s
        """
        params = (start_date, end_date)
        results = self.executor.execute_query(query, params)
        return results

    def get_registers_by_user(self, user_id: int):
        query = """
            SELECT id, user_id, created_at, type_access, access_allowed, reason_denied, captured_image
            FROM accessRegisters
            WHERE user_id = %s
        """
        params = (user_id,)
        results = self.executor.execute_query(query, params)
        return results

    def list_acess_denied(self):
        query = """
            SELECT id, user_id, created_at, type_access, access_allowed, reason_denied, captured_image
            FROM accessRegisters
            WHERE access_allowed = false
        """
        results = self.executor.execute_query(query)
        return results

    def export_registers(self):
        query = """
            SELECT id, user_id, created_at, type_access, access_allowed, reason_denied, captured_image
            FROM accessRegisters
        """
        results = self.executor.execute_query(query)
        return results

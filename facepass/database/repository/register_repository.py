from typing import Any
from facepass.database.setup_database.executor_query import QueryExecutor
from facepass.models.user import Usuario
from facepass.models.registerAccess import RegistroAcesso
from dotenv import load_dotenv
import os

load_dotenv()


class RegistroRepository:
    def __init__(self, connection: Any):
        self.connection = connection
        self.executor = QueryExecutor(self.connection)

    def save_register(self, registro: RegistroAcesso) -> RegistroAcesso:
        query = """
            INSERT into accessRegisters (user_id, created_at, type_access, access_allowed, reason_denied, captured_image)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        params = (registro.user_id, registro.created_at,
                  registro.type_access, registro.access_allowed, registro.reason_denied, registro.captured_image)
        register_id = self.executor.execute_insert(query, params)

        # Atualizar o ID do registro com o ID gerado pelo banco
        registro.id = register_id
        return registro

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

    def list_all_registers(self):
        query = """
            SELECT id, user_id, created_at, type_access, access_allowed, reason_denied, captured_image
            FROM accessRegisters
        """
        results = self.executor.execute_query(query)
        return results

    def get_registers_with_user_info(self, start_date: str = "", end_date: str = ""):
        """Retorna registros com JOIN para pegar nome do usuário"""
        if start_date and end_date:
            query = """
                SELECT ar.id, ar.user_id, ar.created_at, ar.type_access,
                       ar.access_allowed, ar.reason_denied, ar.captured_image,
                       u.name as user_name, u.email as user_email
                FROM accessRegisters ar
                LEFT JOIN users u ON ar.user_id = u.id
                WHERE ar.created_at BETWEEN %s AND %s
                ORDER BY ar.created_at DESC
            """
            params = (start_date, end_date)
            results = self.executor.execute_query(query, params)
        else:
            query = """
                SELECT ar.id, ar.user_id, ar.created_at, ar.type_access,
                       ar.access_allowed, ar.reason_denied, ar.captured_image,
                       u.name as user_name, u.email as user_email
                FROM accessRegisters ar
                LEFT JOIN users u ON ar.user_id = u.id
                ORDER BY ar.created_at DESC
            """
            results = self.executor.execute_query(query)
        return results

    def get_today_access_count(self) -> int:
        """Retorna total de acessos hoje"""
        query = """
            SELECT COUNT(*) as total
            FROM accessRegisters
            WHERE DATE(created_at) = CURDATE()
        """
        result = self.executor.execute_query_one(query)
        return result['total'] if result else 0

    def get_registers_by_filters(self, user_name: str = "", status: str = "",
                                 location: str = "", start_date: str = "",
                                 end_date: str = ""):
        """Busca com múltiplos filtros"""
        query = """
            SELECT ar.id, ar.user_id, ar.created_at, ar.type_access,
                   ar.access_allowed, ar.reason_denied, ar.captured_image,
                   u.name as user_name, u.email as user_email
            FROM accessRegisters ar
            LEFT JOIN users u ON ar.user_id = u.id
            WHERE 1=1
        """
        params = []

        if user_name:
            query += " AND u.name LIKE %s"
            params.append(f"%{user_name}%")

        if status == "Permitido":
            query += " AND ar.access_allowed = true"
        elif status == "Negado":
            query += " AND ar.access_allowed = false"

        if start_date and end_date:
            query += " AND ar.created_at BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        # TODO: Adicionar filtro de location quando implementar campo na tabela

        query += " ORDER BY ar.created_at DESC"

        results = self.executor.execute_query(
            query, tuple(params) if params else ())
        return results

    def get_access_count_by_status(self) -> dict:
        """Retorna contagem de acessos por status"""
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN access_allowed = true THEN 1 ELSE 0 END) as permitidos,
                SUM(CASE WHEN access_allowed = false THEN 1 ELSE 0 END) as negados
            FROM accessRegisters
        """
        result = self.executor.execute_query_one(query)
        return {
            'total': result['total'] if result else 0,
            'permitidos': result['permitidos'] if result else 0,
            'negados': result['negados'] if result else 0
        }

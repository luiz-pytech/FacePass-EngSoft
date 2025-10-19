from typing import Any
from facepass.database.setup_database.executor_query import QueryExecutor


class ManagerRepository:
    def __init__(self, connection: Any):
        self.connection = connection
        self.executor = QueryExecutor(connection)

    def create_manager(self, manager_data: dict):
        """Cria um novo gestor"""
        query = """
            INSERT INTO manager (name, email, password_hash)
            VALUES (%s, %s, %s)
        """
        params = (manager_data['name'], manager_data['email'],
                  manager_data['password_hash'])
        manager_id = self.executor.execute_insert(query, params)
        return manager_id

    def get_manager_by_id(self, manager_id: int):
        """Busca gestor por ID"""
        query = """
            SELECT id, name, email, password_hash
            FROM manager
            WHERE id = %s
        """
        params = (manager_id,)
        result = self.executor.execute_query_one(query, params)
        return result

    def get_manager_by_email(self, email: str):
        """Busca gestor por email (útil para autenticação)"""
        query = """
            SELECT id, name, email, password_hash
            FROM manager
            WHERE email = %s
        """
        params = (email,)
        result = self.executor.execute_query_one(query, params)
        return result

    def list_all_managers(self):
        """Lista todos os gestores"""
        query = """
            SELECT id, name, email, password_hash
            FROM manager
        """
        results = self.executor.execute_query(query)
        return results

    def update_manager(self, manager_id: int, manager_data: dict):
        """Atualiza dados do gestor"""
        query = """
            UPDATE manager
            SET name = %s, email = %s, password_hash = %s
            WHERE id = %s
        """
        params = (manager_data['name'], manager_data['email'],
                  manager_data['password_hash'], manager_id)
        self.executor.execute_update(query, params)

    def delete_manager(self, manager_id: int):
        """Remove um gestor"""
        query = """
            DELETE FROM manager
            WHERE id = %s
        """
        params = (manager_id,)
        self.executor.execute_update(query, params)

    def get_manager_count(self) -> int:
        """Retorna total de gestores cadastrados"""
        query = "SELECT COUNT(*) as total FROM manager"
        result = self.executor.execute_query_one(query)
        return result['total'] if result else 0

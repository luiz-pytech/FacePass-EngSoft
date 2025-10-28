from typing import Any
from facepass.database.setup_database.executor_query import QueryExecutor
from facepass.models.user import Usuario
from dotenv import load_dotenv
import os

load_dotenv()


class UsuarioRepository:
    def __init__(self, connection: Any):
        self.connection = connection
        self.executor = QueryExecutor(self.connection)

    def save_user(self, usuario: Usuario) -> Usuario | None:
        query = """
            INSERT into users (name, email, cpf, created_at, photo_recognition, position, approved)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        params = (usuario.name, usuario.email, usuario.cpf,
                  usuario.created_at, usuario.photo_recognition, usuario.position, usuario.approved)
        user_id = self.executor.execute_insert(query, params)

        # Atualizar o ID do usuário com o ID gerado pelo banco
        usuario.id = user_id
        return usuario

    def get_user_by_id(self, user_id: int):
        query = """
            SELECT id, name, email, cpf, created_at, photo_recognition, position, approved FROM users WHERE id = %s
        """
        params = (user_id,)
        result = self.executor.execute_query_one(query, params)
        if not result:
            return None
        return result

    def get_user_by_email(self, user_email: str):
        query = """
            SELECT id, name, email, cpf, created_at, photo_recognition, position, approved FROM users WHERE email = %s
        """
        params = (user_email,)
        result = self.executor.execute_query_one(query, params)
        if not result:
            return None
        return result

    def get_user_by_cpf(self, user_cpf: str):
        query = """
            SELECT id, name, email, cpf, created_at, photo_recognition, position, approved FROM users WHERE cpf = %s
        """
        params = (user_cpf,)
        result = self.executor.execute_query_one(query, params)
        if not result:
            return None
        return result

    def approve_user(self, user_id: int):
        query = """
            UPDATE users SET approved = true WHERE id = %s
        """
        params = (user_id,)
        self.executor.execute_update(query, params)

    def reject_user(self, user_id: int):
        """Remove usuário rejeitado do sistema permanentemente"""
        query = """
            DELETE FROM users WHERE id = %s
        """
        params = (user_id,)
        self.executor.execute_update(query, params)

    def remove_user(self, user_id: int):
        query = """
            DELETE FROM users WHERE id = %s
        """
        params = (user_id,)
        self.executor.execute_update(query, params)

    def list_unapproved_users(self):
        query = """
            SELECT id, name, email, cpf, created_at, photo_recognition, position, approved FROM users WHERE approved = false
        """
        results = self.executor.execute_query(query)
        return results

    def list_approved_users(self):
        query = """
            SELECT id, name, email, cpf, created_at, photo_recognition, position, approved FROM users WHERE approved = true
        """
        results = self.executor.execute_query(query)
        return results

    def list_denied_users(self):
        query = """
            SELECT id, name, email, cpf, created_at, photo_recognition, position, approved FROM users WHERE approved = false
        """
        results = self.executor.execute_query(query)
        return results

    def list_all_users(self):
        query = """
            SELECT id, name, email, cpf, created_at, photo_recognition, position, approved FROM users
        """
        results = self.executor.execute_query(query)
        return results

    def update_user(self, usuario: Usuario) -> None:
        """Atualiza dados de um usuário existente"""
        query = """
            UPDATE users
            SET name = %s, email = %s, cpf = %s, photo_recognition = %s,
                position = %s, approved = %s
            WHERE id = %s
        """
        params = (usuario.name, usuario.email, usuario.cpf,
                  usuario.photo_recognition, usuario.position,
                  usuario.approved, usuario.id)
        self.executor.execute_update(query, params)

    def get_user_count(self) -> int:
        """Retorna total de usuários cadastrados"""
        query = "SELECT COUNT(*) as total FROM users"
        result = self.executor.execute_query_one(query)
        return result['total'] if result else 0

    def get_approved_user_count(self) -> int:
        """Retorna total de usuários aprovados"""
        query = "SELECT COUNT(*) as total FROM users WHERE approved = true"
        result = self.executor.execute_query_one(query)
        return result['total'] if result else 0

    def get_pending_user_count(self) -> int:
        """Retorna total de usuários pendentes de aprovação"""
        query = "SELECT COUNT(*) as total FROM users WHERE approved = false"
        result = self.executor.execute_query_one(query)
        return result['total'] if result else 0

import mysql.connector
from facepass.database.setup_database.executor_query import QueryExecutor
from facepass.models.user import Usuario
from dotenv import load_dotenv
import os

load_dotenv()


class UsuarioRepository:
    def __init__(self, connection: mysql.connector.MySQLConnection):
        self.connection = connection
        self.executor = QueryExecutor(self.connection)

    def save_user(self, usuario: Usuario) -> Usuario | None:
        query = """
            INSERT into users (id, name, email, cpf, created_at, photo_recognition, position, approved) VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (usuario.id, usuario.name, usuario.email, usuario.cpf,
                  usuario.created_at, usuario.photo_recognition, usuario.position, usuario.approved)
        self.executor.execute_insert(query, params)

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

    def list_unapproved_users(self):
        query = """
            SELECT id, name, email, cpf, created_at, photo_recognition, position, approved FROM users WHERE approved = false
        """
        results = self.executor.execute_query(query)
        return results

    def remove_user(self, user_id: int):
        query = """
            DELETE FROM users WHERE id = %s
        """
        params = (user_id,)
        self.executor.execute_update(query, params)

    def list_all_users(self):
        query = """
            SELECT id, name, email, cpf, created_at, photo_recognition, position, approved FROM users
        """
        results = self.executor.execute_query(query)
        return results

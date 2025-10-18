from setup_database.connection import DatabaseConnection
import mysql.connector
from setup_database.executor_query import QueryExecutor
from facepass.models.user import Usuario
from dotenv import load_dotenv
import os

load_dotenv()


class UsuarioRepository:
    def __init__(self, connection: mysql.connector.MySQLConnection):
        self.connection = connection
        self.executor = QueryExecutor(self.connection)

    def save_user(self, usuario: Usuario) -> None:
        query = """
            INSERT into usuarios (id, nome, email, cpf, data_cadastro, foto_reconhecimento, cargo, aprovado) VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (usuario.id, usuario.nome, usuario.email, usuario.cpf,
                  usuario.data_cadastro, usuario.foto_reconhecimento, usuario.cargo, usuario.aprovado)
        self.executor.execute_insert(query, params)

    def get_user_by_id(self, user_id: int):
        query = """
            SELECT id, nome, email, cpf, data_cadastro, foto_reconhecimento, cargo, aprovado FROM usuarios WHERE id = %s
        """
        params = (user_id,)
        result = self.executor.execute_query_one(query, params)
        if not result:
            return None
        return result

    def get_user_by_email(self, user_email: str):
        query = """
            SELECT id, nome, email, cpf, data_cadastro, foto_reconhecimento, cargo, aprovado FROM usuarios WHERE id = %s
        """
        params = (user_email,)
        result = self.executor.execute_query_one(query, params)
        if not result:
            return None
        return result

    def get_user_by_cpf(self, user_cpf: str):
        query = """
            SELECT id, nome, email, cpf, data_cadastro, foto_reconhecimento, cargo, aprovado FROM usuarios WHERE id = %s
        """
        params = (user_cpf,)
        result = self.executor.execute_query_one(query, params)
        if not result:
            return None
        return result

    def approve_user(self, user_id: int):
        query = """
            UPDATE usuarios SET aprovado = true WHERE id = %s
        """
        params = (user_id,)
        self.executor.execute_update(query, params)

    def list_unapproved_users(self):
        query = """
            SELECT id, nome, email, cpf, data_cadastro, foto_reconhecimento, cargo, aprovado FROM usuarios WHERE aprovado = false
        """
        results = self.executor.execute_query(query)
        return results

    def remove_user(self, user_id: int):
        query = """
            DELETE FROM usuarios WHERE id = %s
        """
        params = (user_id,)
        self.executor.execute_update(query, params)

    def list_all_users(self):
        query = """
            SELECT id, nome, email, cpf, data_cadastro, foto_reconhecimento, cargo, aprovado FROM usuarios
        """
        results = self.executor.execute_query(query)
        return results

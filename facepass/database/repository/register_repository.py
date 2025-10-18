import mysql.connector
from setup_database.executor_query import QueryExecutor
from facepass.models.user import Usuario
from facepass.models.registerAcess import RegistroAcesso
from dotenv import load_dotenv
import os

load_dotenv()


class RegistroRepository:
    def __init__(self, connection: mysql.connector.MySQLConnection):
        self.connection = connection
        self.executor = QueryExecutor(self.connection)

    def save_register(self, registro: RegistroAcesso) -> None:
        query = """
            INSERT into registros_acesso (id, usuario_id, data_hora, tipo_acesso, acesso_permitido, motivo_negacao, imagem_capturada) VALUES
            (%s, %s, %s, %s, %s, %s, %s);
        """
        params = (registro.id, registro.usuario_id, registro.data_hora,
                  registro.tipo_acesso, registro.acesso_permitido, registro.motivo_negacao, registro.imagem_capturada)
        self.executor.execute_insert(query, params)

    def get_register_by_period(self, start_date: str, end_date: str):
        query = """
            SELECT id, usuario_id, data_hora, tipo_acesso, acesso_permitido, motivo_negacao, imagem_capturada 
            FROM registros_acesso 
            WHERE data_hora BETWEEN %s AND %s
        """
        params = (start_date, end_date)
        results = self.executor.execute_query(query, params)
        return results

    def get_registers_by_user(self, user_id: int):
        query = """
            SELECT id, usuario_id, data_hora, tipo_acesso, acesso_permitido, motivo_negacao, imagem_capturada 
            FROM registros_acesso 
            WHERE usuario_id = %s
        """
        params = (user_id,)
        results = self.executor.execute_query(query, params)
        return results

    def list_acess_denied(self):
        query = """
            SELECT id, usuario_id, data_hora, tipo_acesso, acesso_permitido, motivo_negacao, imagem_capturada 
            FROM registros_acesso 
            WHERE acesso_permitido = false
        """
        results = self.executor.execute_query(query)
        return results

    def export_registers(self):
        query = """
            SELECT id, usuario_id, data_hora, tipo_acesso, acesso_permitido, motivo_negacao, imagem_capturada 
            FROM registros_acesso
        """
        results = self.executor.execute_query(query)
        return results

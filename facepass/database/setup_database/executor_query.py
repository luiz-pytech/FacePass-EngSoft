import mysql.connector
from typing import List, Dict, Any


class QueryExecutor:
    def __init__(self, connection: mysql.connector.MySQLConnection):
        self.connection = connection

    def execute_query(self, query: str, params: tuple = (None,)):
        """
        Executa SELECT e retorna LISTA de dicionários (fetchall)
        Ideal para: buscar múltiplos registros
        """
        if self.connection is None:
            raise RuntimeError(
                "No database connection. Call connect() before executing queries.")

        cursor = self.connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()

    def execute_query_one(self, query: str, params: tuple = (None,)):
        if self.connection is None:
            raise RuntimeError(
                "No database connection. Call connect() before executing queries.")

        cursor = self.connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result
        except mysql.connector.Error:
            raise
        finally:
            cursor.close()

    def execute_update(self, query: str, params: tuple = (None,)):
        """
        Executa INSERT, UPDATE, DELETE
        Retorna: número de linhas afetadas
        """
        if self.connection is None:
            raise RuntimeError(
                "No database connection. Call connect() before executing queries.")

        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.rowcount
        except mysql.connector.Error:
            try:
                self.connection.rollback()
            except Exception:
                pass
            raise
        finally:
            cursor.close()

    def execute_insert(self, query: str, params: tuple = (None,)):
        if self.connection is None:
            raise RuntimeError(
                "No database connection. Call connect() before executing queries.")

        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.lastrowid
        except mysql.connector.Error:
            try:
                self.connection.rollback()
            except Exception:
                pass
            raise
        finally:
            cursor.close()

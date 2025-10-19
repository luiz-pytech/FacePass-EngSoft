import mysql.connector
from setup_database.executor_query import QueryExecutor


class ManagerRepository:
    def __init__(self, connection: mysql.connector.MySQLConnection):
        self.connection = connection
        self.executor = QueryExecutor(connection)

    def create_manager(self, manager_data: dict):
        query = """
        INSERT INTO gestor (name, email, password_hash)
        VALUES (%s, %s, %s)
        """
        params = (manager_data['name'], manager_data['email'],
                  manager_data['password_hash'])
        manager_id = self.executor.execute_insert(query, params)
        return manager_id

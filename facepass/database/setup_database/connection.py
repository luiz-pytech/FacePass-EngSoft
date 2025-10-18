import mysql.connector


class DatabaseConnection:
    def __init__(self, host, user, password, database=None, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            print("Conexão bem-sucedida!")
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao MySQL: {err}")
            self.connection = None

    def close(self):
        if self.connection:
            self.connection.close()
            print("Conexão fechada.")

    def get_connection(self):
        return self.connection

    def execute_query(self, query, params=None):
        if self.connection is None:
            raise RuntimeError(
                "No database connection. Call connect() before executing queries.")

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
            else:
                result = cursor.rowcount
            self.connection.commit()
            return result
        except mysql.connector.Error:
            try:
                self.connection.rollback()
            except Exception:
                pass
            raise
        finally:
            cursor.close()

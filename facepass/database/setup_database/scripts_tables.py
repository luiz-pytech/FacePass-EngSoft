import os
import dotenv
from facepass.database.setup_database.connection import DatabaseConnection

dotenv.load_dotenv()


def create_database():
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'facepass_db')
    port = int(os.getenv('DB_PORT', '3306'))

    db_connection = DatabaseConnection(host, user, password, None, port)
    db_connection.connect()
    conn = db_connection.get_connection()

    if conn is None:
        print("Erro: Não foi possível estabelecer conexão com o banco de dados.")
        return

    cursor = conn.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    cursor.execute(f"USE {database}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            cpf VARCHAR(11) NOT NULL UNIQUE,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            foto_reconhecimento BLOB,
            cargo VARCHAR(50),
            cadastrado_aprovado BOOLEAN DEFAULT FALSE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gestor (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            senha_hash VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registroAcesso (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo_acesso ENUM('ENTRADA', 'SAIDA'),
            acesso_permitido BOOLEAN,
            motivo_rejeicao VARCHAR(255),
            imagem_capturada BLOB,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notificacoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            gestor_id INT,
            registro_acesso_id INT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo_notificacao VARCHAR(100),
            mensagem TEXT,
            lida BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (gestor_id) REFERENCES gestor(id),
            FOREIGN KEY (registro_acesso_id) REFERENCES registroAcesso(id
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Database '{database}' and tables created successfully.")


if __name__ == "__main__":
    create_database()

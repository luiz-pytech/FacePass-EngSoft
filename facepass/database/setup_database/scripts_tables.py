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
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            cpf VARCHAR(11) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            photo_recognition BLOB,
            position VARCHAR(50),
            approved BOOLEAN DEFAULT FALSE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manager (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accessRegisters (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            type_access VARCHAR(50),
            access_allowed BOOLEAN,
            rejection_reason VARCHAR(255),
            captured_image BLOB,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            manager_id INT,
            access_register_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            type_notification VARCHAR(100),
            message TEXT,
            read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (manager_id) REFERENCES manager(id),
            FOREIGN KEY (access_register_id) REFERENCES accessRegisters(id)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Database '{database}' and tables created successfully.")


if __name__ == "__main__":
    create_database()

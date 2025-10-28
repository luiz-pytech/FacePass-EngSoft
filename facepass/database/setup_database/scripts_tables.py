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

    print(f"🔗 Conectando ao MySQL em {host}:{port}...")
    print(f"📦 Criando database: {database}")

    db_connection = DatabaseConnection(host, user, password, None, port)
    db_connection.connect()
    conn = db_connection.get_connection()

    if conn is None:
        print("❌ Erro: Não foi possível estabelecer conexão com o banco de dados.")
        print("   Verifique suas credenciais no arquivo .env")
        return

    cursor = conn.cursor()
    print("✅ Conexão estabelecida com sucesso!")

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    print(f"✅ Database '{database}' criado/verificado com sucesso!")

    cursor.execute(f"USE {database}")
    print(f"📊 Criando tabelas...")

    # Tabela: users
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
    print("  ✓ Tabela 'users' criada")

    # Tabela: manager
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manager (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
    """)
    print("  ✓ Tabela 'manager' criada")

    # Tabela: accessRegisters
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accessRegisters (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            type_access VARCHAR(50),
            access_allowed BOOLEAN DEFAULT FALSE,
            reason_denied VARCHAR(255),
            captured_image BLOB,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)
    print("  ✓ Tabela 'accessRegisters' criada")

    # Tabela: notifications
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            manager_id INT NOT NULL,
            access_register_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            type_notification VARCHAR(100),
            message TEXT,
            is_read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (manager_id) REFERENCES manager(id) ON DELETE CASCADE,
            FOREIGN KEY (access_register_id) REFERENCES accessRegisters(id) ON DELETE SET NULL
        )
    """)
    print("  ✓ Tabela 'notifications' criada")
    
    # Tabela: face_encoding
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_encoding (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            encoding BLOB NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("  ✓ Tabela 'face_encoding' criada")

    # Criar um manager padrão se não existir (necessário para notificações)
    cursor.execute("SELECT COUNT(*) FROM manager")
    row = cursor.fetchone()
    if row is None:
        manager_count = 0
    elif isinstance(row, (list, tuple)):
        manager_count = row[0]
    elif isinstance(row, dict):
        manager_count = next(iter(row.values()))
    else:
        try:
            manager_count = row[0]
        except Exception:
            manager_count = 0

    if manager_count == 0:
        print("\n📝 Criando gestor padrão...")
        import hashlib
        default_password = hashlib.sha256("admin123".encode()).hexdigest()

        cursor.execute("""
            INSERT INTO manager (name, email, password_hash)
            VALUES (%s, %s, %s)
        """, ("Admin Padrão", "admin@facepass.com", default_password))

        print("  ✓ Gestor padrão criado:")
        print("     Email: admin@facepass.com")
        print("     Senha: admin123")
        print("     ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")

    conn.commit()
    cursor.close()
    conn.close()

    print("\n" + "="*50)
    print(f"✅ Setup completo! Database '{database}' criado com sucesso!")
    print("="*50)
    print("\n📋 Tabelas criadas:")
    print("  1. users")
    print("  2. manager")
    print("  3. accessRegisters")
    print("  4. notifications")
    print("  5. face_encoding")
    print("\n💡 Próximo passo: Execute 'streamlit run facepass/ui/main.py'\n")


if __name__ == "__main__":
    create_database()

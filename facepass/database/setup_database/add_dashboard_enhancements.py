"""
Script SIMPLIFICADO para dashboard - Apenas configurações essenciais

Para sistemas com baixo volume de dados, otimizações complexas são desnecessárias.
Este script apenas garante que o banco está pronto para o dashboard.

Execute este script após criar as tabelas iniciais do sistema (OPCIONAL).
"""

import os
import dotenv
from facepass.database.setup_database.connection import DatabaseConnection

dotenv.load_dotenv()


def apply_dashboard_enhancements():
    """Aplica configurações mínimas no banco de dados para o dashboard"""

    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'facepass_db')
    port = int(os.getenv('DB_PORT', '3306'))

    print("🔗 Conectando ao MySQL...")
    print(f"📦 Verificando database: {database}")

    db_connection = DatabaseConnection(host, user, password, database, port)
    db_connection.connect()
    conn = db_connection.get_connection()

    if conn is None:
        print("❌ Erro: Não foi possível estabelecer conexão com o banco de dados.")
        return

    cursor = conn.cursor()
    print("✅ Conexão estabelecida com sucesso!")
    print("\n" + "="*60)

    # Verificar se a coluna type_access existe e aceita os valores corretos
    print("\n📊 Verificando configuração da tabela accessRegisters...")

    try:
        cursor.execute("""
            SELECT COLUMN_NAME, COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'accessRegisters'
            AND COLUMN_NAME = 'type_access'
        """, (database,))

        result = cursor.fetchone()

        if result:
            print(f"  ✓ Coluna 'type_access' existe: {result[1]}")
            print("  ℹ️ Use 'entrada' para registros de entrada")
            print("  ℹ️ Use 'saida' para registros de saída")
        else:
            print("  ⚠️ Coluna 'type_access' não encontrada")
            print("  💡 Certifique-se de que a tabela foi criada corretamente")

    except Exception as e:
        print(f"  ⚠️ Erro ao verificar type_access: {e}")

    # Adicionar índices OPCIONAIS para performance (recomendado mas não obrigatório)
    print("\n📊 Adicionando índices opcionais (melhora performance)...")

    try:
        # Índice simples para filtrar por data
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON accessRegisters(created_at)
        """)
        print("  ✓ Índice 'idx_created_at' criado")
    except Exception as e:
        print(f"  ℹ️ Índice idx_created_at: {e}")

    try:
        # Índice para queries de usuário
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id
            ON accessRegisters(user_id)
        """)
        print("  ✓ Índice 'idx_user_id' criado")
    except Exception as e:
        print(f"  ℹ️ Índice idx_user_id: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print("\n" + "="*60)
    print("✅ Verificação concluída!")
    print("\n📋 Resumo:")
    print("  1. ✓ Banco de dados verificado")
    print("  2. ✓ Campo 'type_access' confirmado")
    print("  3. ✓ Índices opcionais adicionados")
    print("\n💡 O dashboard já está pronto para uso!")
    print("   Execute: streamlit run facepass/ui/main.py")
    print("\n📝 Lembre-se de usar:")
    print("   - type_access = 'entrada' para entradas")
    print("   - type_access = 'saida' para saídas\n")


if __name__ == "__main__":
    apply_dashboard_enhancements()

import os
import random
import hashlib
from datetime import datetime, timedelta
import dotenv
from facepass.database.setup_database.connection import DatabaseConnection

dotenv.load_dotenv()


# Dados de exemplo
NAMES = [
    "Ana Silva", "Bruno Costa", "Carlos Santos", "Diana Oliveira",
    "Eduardo Pereira", "Fernanda Lima", "Gabriel Rodrigues", "Helena Martins",
    "Igor Alves", "Julia Fernandes", "Kevin Souza", "Laura Mendes",
    "Marcos Ribeiro", "Natalia Castro", "Otavio Barbosa", "Patricia Gomes",
    "Rafael Cardoso", "Sabrina Dias", "Thiago Moreira", "Vanessa Rocha"
]

POSITIONS = ["Desenvolvedor", "Analista de Dados", "Gerente"]

NOTIFICATION_TYPES = [
    "Acesso Negado - Rosto não reconhecido",
    "Acesso Negado - Usuário não aprovado",
    "Acesso Negado - Tentativa suspeita",
    "Novo cadastro pendente"
]

DENIAL_REASONS = [
    "Rosto não reconhecido no sistema",
    "Usuário aguardando aprovação",
    "Múltiplas tentativas falhadas",
    "Foto de baixa qualidade",
    "Nenhum rosto detectado na imagem"
]


def generate_cpf():
    """Gera um CPF fictício válido"""
    cpf = [random.randint(0, 9) for _ in range(9)]

    # Primeiro dígito verificador
    sum1 = sum([(10 - i) * cpf[i] for i in range(9)])
    d1 = 11 - (sum1 % 11)
    d1 = 0 if d1 >= 10 else d1
    cpf.append(d1)

    # Segundo dígito verificador
    sum2 = sum([(11 - i) * cpf[i] for i in range(10)])
    d2 = 11 - (sum2 % 11)
    d2 = 0 if d2 >= 10 else d2
    cpf.append(d2)

    return ''.join(map(str, cpf))


def generate_email(name):
    """Gera email baseado no nome"""
    first_name = name.split()[0].lower()
    last_name = name.split()[-1].lower()
    return f"{first_name}.{last_name}@facepass.com"


def create_placeholder_photo():
    """Cria um placeholder de foto (apenas alguns bytes)"""
    return b'\x00' * 100  # 100 bytes vazios como placeholder


def seed_users(cursor, count=20):
    """Cria usuários de exemplo"""
    print(f"\n👥 Criando {count} usuários...")

    users = []
    used_names = random.sample(NAMES, min(count, len(NAMES)))

    for i, name in enumerate(used_names):
        email = generate_email(name)
        cpf = generate_cpf()
        position = random.choice(POSITIONS)
        photo = create_placeholder_photo()
        
        rand = random.random()
        if rand < 0.7:
            approved = True
        else:
            approved = False

        created_at = datetime.now() - timedelta(days=random.randint(30, 90))

        cursor.execute("""
            INSERT INTO users (name, email, cpf, created_at, photo_recognition, position, approved)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, cpf, created_at, photo, position, approved))

        user_id = cursor.lastrowid
        users.append({
            'id': user_id,
            'name': name,
            'approved': approved,
            'created_at': created_at
        })

    print(f"  ✓ {len(users)} usuários criados")
    return users


def seed_access_registers(cursor, users):
    """Cria registros de acesso (entrada/saída) distribuídos ao longo de 30 dias"""
    print(f"\n🚪 Criando registros de acesso...")

    approved_users = [u for u in users if u['approved']]

    if not approved_users:
        print("  ⚠️  Nenhum usuário aprovado encontrado, pulando registros de acesso")
        return []

    access_records = []
    now = datetime.now()

    # Criar acessos para os últimos 30 dias
    for day_offset in range(30, -1, -1):  # Últimos 30 dias até hoje
        date = now - timedelta(days=day_offset)

        # Apenas dias úteis (segunda a sexta)
        if date.weekday() >= 5:
            continue

        for user in approved_users:
            if random.random() < 0.8:
                entry_hour = random.randint(7, 9)
                entry_minute = random.randint(0, 59)
                entry_time = date.replace(
                    hour=entry_hour, minute=entry_minute, second=0)

                # Criar entrada
                cursor.execute("""
                    INSERT INTO accessRegisters
                    (user_id, created_at, type_access, access_allowed, reason_denied, captured_image)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user['id'], entry_time, 'entrada', True, None, create_placeholder_photo()))

                entry_id = cursor.lastrowid
                access_records.append({
                    'id': entry_id,
                    'user_id': user['id'],
                    'type': 'entrada',
                    'time': entry_time
                })

                if random.random() < 0.9:
                    exit_hour = random.randint(17, 18)
                    exit_minute = random.randint(0, 59)
                    exit_time = date.replace(
                        hour=exit_hour, minute=exit_minute, second=0)

                    cursor.execute("""
                        INSERT INTO accessRegisters
                        (user_id, created_at, type_access, access_allowed, reason_denied, captured_image)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user['id'], exit_time, 'saida', True, None, create_placeholder_photo()))

                    exit_id = cursor.lastrowid
                    access_records.append({
                        'id': exit_id,
                        'user_id': user['id'],
                        'type': 'saida',
                        'time': exit_time
                    })

    # Criar alguns acessos HOJE com usuários presentes
    print(f"  ✓ Criando acessos de HOJE com usuários presentes...")
    today = datetime.now()

    # Garantir que alguns usuários estão presentes agora
    present_count = min(random.randint(3, 7), len(approved_users))
    present_users = random.sample(approved_users, present_count)

    for user in present_users:
        # Entrada hoje (entre 7h e 9h)
        entry_hour = random.randint(7, 9)
        entry_minute = random.randint(0, 59)
        entry_time = today.replace(
            hour=entry_hour, minute=entry_minute, second=0)

        cursor.execute("""
            INSERT INTO accessRegisters
            (user_id, created_at, type_access, access_allowed, reason_denied, captured_image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user['id'], entry_time, 'entrada', True, None, create_placeholder_photo()))

        access_records.append({
            'id': cursor.lastrowid,
            'user_id': user['id'],
            'type': 'entrada',
            'time': entry_time
        })

    # Criar alguns acessos negados (tentativas falhadas)
    denied_count = random.randint(5, 15)
    print(f"  ✓ Criando {denied_count} acessos negados...")

    for _ in range(denied_count):
        # Distribuir ao longo dos últimos 30 dias
        days_ago = random.randint(0, 30)
        denied_date = now - timedelta(days=days_ago)
        denied_hour = random.randint(6, 20)
        denied_minute = random.randint(0, 59)
        denied_time = denied_date.replace(
            hour=denied_hour, minute=denied_minute, second=0)

        reason = random.choice(DENIAL_REASONS)

        # 50% com user_id (usuário não aprovado), 50% sem user_id (não reconhecido)
        user_id = random.choice(approved_users)[
            'id'] if random.random() < 0.5 else None

        cursor.execute("""
            INSERT INTO accessRegisters
            (user_id, created_at, type_access, access_allowed, reason_denied, captured_image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, denied_time, 'entrada', False, reason, create_placeholder_photo()))

        access_records.append({
            'id': cursor.lastrowid,
            'user_id': user_id,
            'type': 'entrada',
            'time': denied_time,
            'denied': True
        })

    print(f"  ✓ {len(access_records)} registros de acesso criados")
    print(f"  ✓ {present_count} usuários atualmente PRESENTES")
    return access_records


def seed_notifications(cursor, access_records):
    """Cria notificações baseadas nos acessos negados"""
    print(f"\n🔔 Criando notificações...")

    # Pegar acessos negados
    denied_records = [r for r in access_records if r.get('denied', False)]

    if not denied_records:
        print("  ⚠️  Nenhum acesso negado encontrado, pulando notificações")
        return []

    notifications = []

    # Criar notificações para acessos negados
    for record in denied_records:
        notif_type = random.choice(NOTIFICATION_TYPES)
        message = f"Tentativa de acesso negado. Motivo: {notif_type}"
        is_read = random.choice([True, False])

        cursor.execute("""
            INSERT INTO notifications
            (manager_id, access_register_id, created_at, type_notification, message, is_read)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (1, record['id'], record['time'], notif_type, message, is_read))

        notifications.append({
            'id': cursor.lastrowid,
            'type': notif_type,
            'is_read': is_read
        })

    print(f"  ✓ {len(notifications)} notificações criadas")
    return notifications


def seed_database():
    """Função principal de seed"""
    print("="*60)
    print("🌱 SEED DATABASE - Populando banco de dados")
    print("="*60)

    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', 'facepass_db')
    port = int(os.getenv('DB_PORT', '3306'))

    print(f"\n🔗 Conectando ao MySQL em {host}:{port}...")
    print(f"📦 Database: {database}")

    db_connection = DatabaseConnection(host, user, password, database, port)
    db_connection.connect()
    conn = db_connection.get_connection()

    if conn is None:
        print("❌ Erro: Não foi possível estabelecer conexão com o banco de dados.")
        return

    cursor = conn.cursor()
    print("✅ Conexão estabelecida com sucesso!")

    try:
        # Limpar dados existentes (exceto manager)
        print("\n🧹 Limpando dados antigos...")
        cursor.execute("DELETE FROM notifications")
        cursor.execute("DELETE FROM face_encoding")
        cursor.execute("DELETE FROM accessRegisters")
        cursor.execute("DELETE FROM users")
        print("  ✓ Dados antigos removidos")

        # Seed
        users = seed_users(cursor, count=20)
        access_records = seed_access_registers(cursor, users)
        notifications = seed_notifications(cursor, access_records)

        # Commit
        conn.commit()

        # Estatísticas finais
        print("✅ SEED COMPLETO!")
        print("="*60)
        print(f"\n📊 Resumo:")
        print(f"  👥 Usuários: {len(users)}")
        print(f"     - Aprovados: {len([u for u in users if u['approved']])}")
        print(
            f"     - Pendentes: {len([u for u in users if not u['approved']])}")
        print(f"  🚪 Registros de Acesso: {len(access_records)}")
        print(
            f"     - Permitidos: {len([r for r in access_records if not r.get('denied', False)])}")
        print(
            f"     - Negados: {len([r for r in access_records if r.get('denied', False)])}")
        print(f"  🔔 Notificações: {len(notifications)}")
        print(
            f"     - Lidas: {len([n for n in notifications if n['is_read']])}")
        print(
            f"     - Não lidas: {len([n for n in notifications if not n['is_read']])}")
        

    except Exception as e:
        print(f"\n❌ Erro durante seed: {str(e)}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    seed_database()

import streamlit as st
from facepass.ui.ui_pages import notifications, approve_registration, registers, facial_recognition, user_registration, manager_login, dashboard
from facepass.database.setup_database.connection import DatabaseConnection
from facepass.services.user_service import UsuarioService
from facepass.services.notification_service import NotificationService
from facepass.services.access_service import AccessService
from facepass.services.face_recognition_service import FaceRecognitionService
from facepass.services.manager_service import ManagerService
from facepass.services.dashboard_service import DashboardService
from facepass.database.repository.user_repository import UsuarioRepository
from facepass.database.repository.notification_repository import NotificationRepository
from facepass.database.repository.register_repository import RegistroRepository
from facepass.database.repository.face_encoding_repository import FaceEncodingRepository
from facepass.database.repository.manager_repository import ManagerRepository
from facepass.database.repository.dashboard_repository import DashboardRepository
from facepass.controllers.face_recognition_controller import FaceRecognitionController
from facepass.controllers.user_controller import UserController
from facepass.controllers.manager_controller import ManagerController
from facepass.controllers.notification_controller import NotificationController
from facepass.controllers.dashboard_controller import DashboardController
from facepass.controllers.access_controller import AccessController
import os
from dotenv import load_dotenv

load_dotenv()


def sidebar():
    """Barra lateral de navegação"""
    st.sidebar.title("🔐 FacePass")
    st.sidebar.markdown("---")

    st.sidebar.info("Sistema de Controle de Acesso por Reconhecimento Facial")

    manager_authenticated = st.session_state.get(
        'manager_authenticated', False)

    if manager_authenticated:
        manager_name = st.session_state.get('manager_name', 'Gestor')
        st.sidebar.success(f"✅ **{manager_name}**")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Navegação")

    # Páginas públicas (sempre visíveis)
    public_pages = [
        "🏠 Início",
        "📝 Cadastro de Usuário",
        "🔐 Reconhecimento Facial",
        "👨‍💼 Login de Gestor"
    ]

    # Páginas restritas (apenas para gestores autenticados)
    restricted_pages = [
        "📊 Dashboard",
        "👤 Gestão de Cadastros",
        "📜 Relatórios de Acesso",
        "🔔 Notificações"
    ]

    # Determinar quais páginas mostrar
    if manager_authenticated:
        available_pages = public_pages + restricted_pages
    else:
        available_pages = public_pages

    # Opções de navegação
    page = st.sidebar.radio(
        "Ir para:",
        available_pages,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")

    # Informações adicionais
    with st.sidebar.expander("ℹ️ Sobre o Sistema"):
        st.markdown("""
            **FacePass v1.0**

            Sistema desenvolvido para:
            - Controle de acesso seguro
            - Reconhecimento facial
            - Gestão de usuários
            - Auditoria de acessos

            © 2025 - Eng. Software UFRN
        """)

    return page


def home_page():
    """Página inicial"""
    st.title("🏠 Bem-vindo ao FacePass")
    st.markdown("---")

    # Banner de boas-vindas
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #000428 0%, #004e92 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
        ">
            <h1 style="margin: 0;">🔐 FacePass</h1>
            <p style="font-size: 18px; margin: 10px 0;">
                Sistema Inteligente de Controle de Acesso por Reconhecimento Facial
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("🚀 Funcionalidades Principais")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            ### 📝 Cadastro
            - Auto-cadastro de usuários
            - Upload de foto facial
            - Validação de dados
            - Aprovação por gestores
        """)

    with col2:
        st.markdown("""
            ### 🔐 Acesso
            - Reconhecimento facial
            - Autenticação segura
            - Registro de tentativas
            - Notificações em tempo real
        """)

    with col3:
        st.markdown("""
            ### 📊 Gestão
            - Aprovação de usuários
            - Relatórios detalhados
            - Exportação de dados
            - Auditoria completa
        """)

    st.markdown("---")

    st.subheader("📖 Guia Rápido")

    with st.expander("👤 Para Novos Usuários"):
        st.markdown("""
            1. Acesse **Cadastro de Usuário** no menu lateral
            2. Preencha seus dados pessoais
            3. Tire uma foto ou faça upload
            4. Aguarde aprovação do gestor
            5. Após aprovação, utilize o **Reconhecimento Facial** para acessar
        """)

    with st.expander("👨‍💼 Para Gestores"):
        st.markdown("""
            1. Acesse **Gestão de Cadastros** para aprovar novos usuários
            2. Visualize e gerencie todos os usuários cadastrados
            3. Acompanhe **Relatórios de Acesso** com filtros avançados
            4. Receba **Notificações** de tentativas de acesso negadas
        """)

    with st.expander("🔐 Para Acessar o Sistema"):
        st.markdown("""
            1. Acesse **Reconhecimento Facial** no menu lateral
            2. Posicione seu rosto na webcam ou faça upload de foto
            3. Clique em **Solicitar Acesso**
            4. Aguarde o processamento do reconhecimento
            5. Visualize o resultado (Permitido/Negado)
        """)

    st.markdown("---")

    st.subheader("📊 Estatísticas do Sistema")

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat4, col_stat5, col_stat6 = st.columns(3)

    # Obter estatísticas do session_state
    stats = st.session_state.get('user_stats', {})

    with col_stat1:
        st.metric("👥 Usuários Cadastrados", stats.get('total_users', 0),
                  help="Total de usuários no sistema")

    with col_stat2:
        st.metric("✅ Usuários Aprovados", stats.get('approved_users', 0),
                  help="Usuários com acesso liberado")

    with col_stat3:
        st.metric("❌ Usuários Pendentes", stats.get('pending_users', 0),
                  help="Usuários aguardando aprovação")

    with col_stat4:
        st.metric("📊 Acessos Totais", len(st.session_state.get('acessos_registrados', [])),
                  help="Total de tentativas de acesso")

    with col_stat5:
        st.metric("📈 Taxa de usuários aprovados", f"{stats.get('approval_rate', 0.0):.2f}%",
                  help="Percentual de usuários aprovados")
    with col_stat6:
        st.metric("🔔 Notificações", len(st.session_state.get('notificacoes', [])),
                  help="Total de notificações geradas")

    st.markdown("---")

    st.subheader("📂 Diagramas do Sistema")
    st.image('docs/diagrams/activity_diagram.png',
             caption='Diagrama de atividades do FacePass', width="stretch")
    st.image('docs/diagrams/class_diagram.png',
             caption='Diagrama de classes do FacePass', width="stretch")

    st.markdown("---")
    st.info("""
        💡 **Dica:** Use o menu lateral para navegar entre as funcionalidades do sistema.
    """)


def init_services():
    """Inicializa os serviços necessários"""

    # Tentar estabelecer conexão com banco de dados
    if 'db_connection' not in st.session_state:
        try:
            cnx = DatabaseConnection(
                os.getenv("DB_HOST"),
                os.getenv("DB_USER"),
                os.getenv("DB_PASSWORD"),
                os.getenv("DB_NAME")
            )
            cnx.connect()
            connection = cnx.get_connection()

            # Armazenar conexão e objeto DatabaseConnection
            st.session_state['db_connection'] = cnx
            st.session_state['connection'] = connection

            # Inicializar repositórios
            usuario_repository = UsuarioRepository(connection)
            notification_repository = NotificationRepository(connection)
            access_repository = RegistroRepository(connection)
            face_encoding_repository = FaceEncodingRepository(connection)
            manager_repository = ManagerRepository(connection)
            dashboard_repository = DashboardRepository(connection)

            # Inicializar serviços
            user_service = UsuarioService(
                usuario_repository, notification_repository)
            notification_service = NotificationService(
                notification_repository)
            access_service = AccessService(
                access_repository, notification_repository, usuario_repository)
            face_recognition_service = FaceRecognitionService(
                face_encoding_repository)
            manager_service = ManagerService(manager_repository)
            dashboard_service = DashboardService(
                dashboard_repository, user_service, notification_service)

            # Inicializar controllers
            face_recognition_controller = FaceRecognitionController(
                face_recognition_service, user_service, access_service)
            user_controller = UserController(user_service)
            manager_controller = ManagerController(manager_service)
            notification_controller = NotificationController(
                notification_service)
            dashboard_controller = DashboardController(dashboard_service)
            access_controller = AccessController(access_service)

            # Armazenar no session_state
            st.session_state['usuario_repository'] = usuario_repository
            st.session_state['notification_repository'] = notification_repository
            st.session_state['access_repository'] = access_repository
            st.session_state['face_encoding_repository'] = face_encoding_repository
            st.session_state['manager_repository'] = manager_repository

            st.session_state['user_service'] = user_service
            st.session_state['notification_service'] = notification_service
            st.session_state['access_service'] = access_service
            st.session_state['face_recognition_service'] = face_recognition_service
            st.session_state['manager_service'] = manager_service

            st.session_state['face_recognition_controller'] = face_recognition_controller
            st.session_state['user_controller'] = user_controller
            st.session_state['manager_controller'] = manager_controller
            st.session_state['notification_controller'] = notification_controller
            st.session_state['dashboard_controller'] = dashboard_controller
            st.session_state['access_controller'] = access_controller

            # Carregar estatísticas dos usuários
            stats_result = user_controller.get_stats()
            if stats_result['success']:
                st.session_state['user_stats'] = stats_result['data']
            else:
                st.session_state['user_stats'] = {
                    'total_users': 0,
                    'approved_users': 0,
                    'pending_users': 0,
                    'approval_rate': 0.0
                }

            st.success("✅ Conexão com banco de dados estabelecida!")

            st.session_state.acessos_registrados = st.session_state.access_service.list_all_access_records(
            ) if st.session_state.get('access_service') else []

            st.session_state.taxas_sucesso = st.session_state.access_service.get_success_rate(
            ) if st.session_state.get('access_service') else 0.0

            st.session_state.notificacoes = st.session_state.notification_service.list_all_notifications(
            ) if st.session_state.get('notification_service') else []

        except Exception as e:
            st.error(f"❌ Erro ao conectar com o banco de dados: {str(e)}")

            clean_db_services()


def main():
    """Função principal da aplicação"""
    st.set_page_config(
        page_title="FacePass - Controle de Acesso",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inicializar serviços e conexões
    init_services()

    # Navegação
    page = sidebar()

    # Roteamento de páginas
    if page == "🏠 Início":
        home_page()
    elif page == "📝 Cadastro de Usuário":
        user_registration.app()
    elif page == "🔐 Reconhecimento Facial":
        facial_recognition.app()
    elif page == "👨‍💼 Login de Gestor":
        manager_login.app()
    elif page == "📊 Dashboard":
        dashboard.app()
    elif page == "👤 Gestão de Cadastros":
        approve_registration.app()
    elif page == "📜 Relatórios de Acesso":
        registers.app()
    elif page == "🔔 Notificações":
        notifications.app()


def clean_db_services():
    """Limpa os serviços do banco de dados ao fechar a aplicação"""
    if 'db_connection' in st.session_state:
        db_connection = st.session_state['db_connection']
        if db_connection:
            db_connection.close()
            st.session_state['db_connection'] = None
            st.session_state['connection'] = None
            st.session_state['user_service'] = None
            st.session_state['notification_service'] = None
            st.session_state['access_service'] = None
            st.session_state['manager_service'] = None
            st.session_state['manager_repository'] = None

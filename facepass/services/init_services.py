import streamlit as st
import os
from typing import Dict, Any, Optional
from facepass.database.setup_database.connection import DatabaseConnection
from facepass.database.repository.user_repository import UsuarioRepository
from facepass.database.repository.notification_repository import NotificationRepository
from facepass.database.repository.register_repository import RegistroRepository
from facepass.database.repository.face_encoding_repository import FaceEncodingRepository
from facepass.database.repository.manager_repository import ManagerRepository
from facepass.database.repository.dashboard_repository import DashboardRepository
from facepass.services.access_service import AccessService
from facepass.services.user_service import UsuarioService
from facepass.services.notification_service import NotificationService
from facepass.services.face_recognition_service import FaceRecognitionService
from facepass.services.manager_service import ManagerService
from facepass.services.dashboard_service import DashboardService
from facepass.controllers.face_recognition_controller import FaceRecognitionController
from facepass.controllers.user_controller import UserController
from facepass.controllers.manager_controller import ManagerController
from facepass.controllers.notification_controller import NotificationController
from facepass.controllers.access_controller import AccessController


def initialize_database_connection() -> Optional[DatabaseConnection]:
    try:
        cnx = DatabaseConnection(
            os.getenv("DB_HOST"),
            os.getenv("DB_USER"),
            os.getenv("DB_PASSWORD"),
            os.getenv("DB_NAME")
        )
        cnx.connect()
        return cnx
    except Exception as e:
        st.error(f"❌ Erro ao conectar com o banco de dados: {str(e)}")
        return None


def initialize_repositories(connection) -> Dict[str, Any]:
    return {
        'usuario_repository': UsuarioRepository(connection),
        'notification_repository': NotificationRepository(connection),
        'access_repository': RegistroRepository(connection),
        'face_encoding_repository': FaceEncodingRepository(connection),
        'manager_repository': ManagerRepository(connection),
        'dashboard_repository': DashboardRepository(connection)
    }


def initialize_services(repositories: Dict[str, Any]) -> Dict[str, Any]:
    user_service = UsuarioService(
        repositories['usuario_repository'],
        repositories['notification_repository']
    )

    notification_service = NotificationService(
        repositories['notification_repository']
    )

    access_service = AccessService(
        repositories['access_repository'],
        repositories['notification_repository'],
        repositories['usuario_repository']
    )

    face_recognition_service = FaceRecognitionService(
        repositories['face_encoding_repository']
    )

    manager_service = ManagerService(
        repositories['manager_repository']
    )

    dashboard_service = DashboardService(
        repositories['dashboard_repository'],
        user_service,
        notification_service
    )

    return {
        'user_service': user_service,
        'notification_service': notification_service,
        'access_service': access_service,
        'face_recognition_service': face_recognition_service,
        'manager_service': manager_service,
        'dashboard_service': dashboard_service
    }


def initialize_controllers(services: Dict[str, Any]) -> Dict[str, Any]:
    face_recognition_controller = FaceRecognitionController(
        services['face_recognition_service'],
        services['user_service'],
        services['access_service']
    )

    user_controller = UserController(services['user_service'])

    manager_controller = ManagerController(services['manager_service'])

    notification_controller = NotificationController(
        services['notification_service']
    )

    access_controller = AccessController(services['access_service'])

    return {
        'face_recognition_controller': face_recognition_controller,
        'user_controller': user_controller,
        'manager_controller': manager_controller,
        'notification_controller': notification_controller,
        'access_controller': access_controller
    }


def load_initial_data(services: Dict[str, Any], controllers: Dict[str, Any]) -> Dict[str, Any]:
    initial_data = {}

    stats_result = controllers['user_controller'].get_stats()
    if stats_result['success']:
        initial_data['user_stats'] = stats_result['data']
    else:
        initial_data['user_stats'] = {
            'total_users': 0,
            'approved_users': 0,
            'pending_users': 0,
            'approval_rate': 0.0
        }

    initial_data['acessos_registrados'] = services['access_service'].list_all_access_records()

    initial_data['taxas_sucesso'] = services['access_service'].get_success_rate()

    initial_data['notificacoes'] = services['notification_service'].list_all_notifications()

    return initial_data


def store_in_session_state(
    db_connection: DatabaseConnection,
    connection,
    repositories: Dict[str, Any],
    services: Dict[str, Any],
    controllers: Dict[str, Any],
    initial_data: Dict[str, Any]
) -> None:
    st.session_state['db_connection'] = db_connection
    st.session_state['connection'] = connection

    for key, value in repositories.items():
        st.session_state[key] = value

    for key, value in services.items():
        st.session_state[key] = value

    for key, value in controllers.items():
        st.session_state[key] = value

    for key, value in initial_data.items():
        st.session_state[key] = value


def clean_db_services() -> None:
    if 'db_connection' in st.session_state:
        db_connection = st.session_state['db_connection']
        if db_connection:
            db_connection.close()

        keys_to_clear = [
            'db_connection', 'connection',
            'usuario_repository', 'notification_repository', 'access_repository',
            'face_encoding_repository', 'manager_repository', 'dashboard_repository',
            'user_service', 'notification_service', 'access_service',
            'face_recognition_service', 'manager_service', 'dashboard_service',
            'face_recognition_controller', 'user_controller', 'manager_controller',
            'notification_controller', 'access_controller'
        ]

        for key in keys_to_clear:
            if key in st.session_state:
                st.session_state[key] = None


def init_services() -> None:
    if 'db_connection' in st.session_state:
        return

    try:
        db_connection = initialize_database_connection()
        if not db_connection:
            clean_db_services()
            return

        connection = db_connection.get_connection()

        repositories = initialize_repositories(connection)

        services = initialize_services(repositories)

        controllers = initialize_controllers(services)

        initial_data = load_initial_data(services, controllers)

        store_in_session_state(
            db_connection,
            connection,
            repositories,
            services,
            controllers,
            initial_data
        )

        st.success("✅ Conexão com banco de dados estabelecida!")

    except Exception as e:
        st.error(f"❌ Erro ao inicializar serviços: {str(e)}")
        clean_db_services()

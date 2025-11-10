import streamlit as st
from facepass.ui.ui_pages import notifications, approve_registration, registers, facial_recognition, user_registration, manager_login, dashboard
from facepass.services.init_services import init_services, clean_db_services
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


if __name__ == "__main__":
    main()

import streamlit as st
import time


def app():
    """Página de login do gestor"""
    st.title("🔐 Login de Gestor")
    st.markdown("---")

    # Verificar se já está autenticado
    if st.session_state.get('manager_authenticated', False):
        manager_name = st.session_state.get('manager_name', 'Gestor')

        st.success(f"✅ Você já está autenticado como **{manager_name}**")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚪 Fazer Logout", use_container_width=True):
                st.session_state['manager_authenticated'] = False
                st.session_state['manager_id'] = None
                st.session_state['manager_name'] = None
                st.session_state['manager_email'] = None
                st.rerun()

        with col2:
            st.info("Use o menu lateral para acessar as funcionalidades de gestão")

        return

    # Container de login
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <h2 style="margin: 0;">👨‍💼 Acesso Restrito</h2>
            <p style="margin: 10px 0 0 0;">
                Área exclusiva para gestores do sistema FacePass
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Formulário de login
    with st.form("login_form"):
        st.subheader("📧 Credenciais de Acesso")

        email = st.text_input(
            "Email",
            placeholder="gestor@facepass.com",
            help="Digite o email cadastrado no sistema"
        )

        password = st.text_input(
            "Senha",
            type="password",
            placeholder="Digite sua senha",
            help="Senha de acesso ao sistema"
        )

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            submit_button = st.form_submit_button(
                "🔓 Entrar",
                use_container_width=True
            )

    # Processar login
    if submit_button:
        # Obter controller do session_state
        manager_controller = st.session_state.get('manager_controller')

        if not manager_controller:
            st.error(
                "❌ Serviço de autenticação indisponível. Verifique a conexão com o banco.")
            return

        with st.spinner("🔐 Autenticando..."):
            # Autenticar via controller
            result = manager_controller.authenticate(email, password)

            if result['success']:
                # Login bem-sucedido - armazenar dados na sessão
                manager_data = result['data']
                st.session_state['manager_authenticated'] = True
                st.session_state['manager_id'] = manager_data['id']
                st.session_state['manager_name'] = manager_data['name']
                st.session_state['manager_email'] = manager_data['email']

                st.success(f"✅ {result['message']}")
                st.balloons()

                st.info(
                    "👉 Use o menu lateral para acessar as funcionalidades de gestão")

                # Pequeno delay para mostrar a mensagem
                time.sleep(1)
                st.rerun()

            else:
                # Erro no login
                st.error(f"❌ {result['message']}")
                for error in result['errors']:
                    st.error(f"• {error}")

    # Informações adicionais
    st.markdown("---")

    with st.expander("ℹ️ Informações de Acesso"):
        st.markdown("""
            ### 🔐 Sobre o Login de Gestor

            Esta área é **exclusiva para gestores** autorizados do sistema FacePass.

            **Funcionalidades disponíveis após o login:**
            - ✅ Aprovar ou rejeitar cadastros de usuários
            - 📊 Visualizar relatórios de acesso completos
            - 🔔 Gerenciar notificações do sistema
            - 👥 Administrar usuários cadastrados

            **Primeiro acesso:**
            Um gestor padrão é criado automaticamente durante a inicialização do banco de dados.

            **Credenciais padrão:**
            - Email: `admin@facepass.com`
            - Senha: `admin123`

            ⚠️ **Importante:** Altere a senha padrão após o primeiro acesso.

            **Esqueceu sua senha?**
            Entre em contato com o administrador do sistema.
        """)

    with st.expander("🔒 Segurança"):
        st.markdown("""
            - As senhas são armazenadas usando hash SHA-256
            - Nunca compartilhe suas credenciais
            - Faça logout ao finalizar o uso
            - Utilize senhas fortes e únicas
        """)

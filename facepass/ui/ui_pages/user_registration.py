import streamlit as st
from datetime import datetime
from facepass.controllers.user_controller import UserController
import os
from dotenv import load_dotenv

load_dotenv()


def app():
    """Página de Cadastro de Usuário"""
    st.title("📝 Cadastro de Novo Usuário")
    st.markdown("---")

    # Informações iniciais
    st.info("""
        👋 **Bem-vindo ao FacePass!**

        Preencha o formulário abaixo para solicitar seu cadastro no sistema de controle de acesso.
        Após o envio, seu cadastro será analisado por um gestor antes da aprovação final.
    """)

    st.markdown("---")

    # ==================== FORMULÁRIO DE CADASTRO ====================
    with st.form("user_registration_form", clear_on_submit=True):
        st.subheader("📋 Informações Pessoais")

        # Dados pessoais
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Nome Completo *",
                placeholder="Ex: João Silva Santos",
                help="Digite seu nome completo"
            )

            email = st.text_input(
                "Email *",
                placeholder="Ex: joao.silva@empresa.com",
                help="Email corporativo ou pessoal"
            )

        with col2:
            cpf = st.text_input(
                "CPF *",
                placeholder="Ex: 123.456.789-00",
                help="CPF no formato 000.000.000-00 ou 00000000000",
                max_chars=14
            )

            position = st.selectbox(
                "Cargo/Função *",
                options=[
                    "Desenvolvedor",
                    "Analista de Dados",
                    "Gerente",
                ],
                help="Seu cargo ou função na organização"
            )

        st.markdown("---")

        # ==================== FOTO PARA RECONHECIMENTO ====================
        st.subheader("📸 Foto para Reconhecimento Facial")

        st.warning("""
            **⚠️ Importante:**
            - A foto deve conter apenas seu rosto
            - Boa iluminação
            - Sem óculos escuros, bonés ou chapéus
            - Olhe diretamente para a câmera
        """)

        # Tabs para escolher método de captura
        tab_cam, tab_file = st.tabs(
            ["📷 Capturar da Webcam", "📁 Upload de Arquivo"])

        foto_bytes = None

        with tab_cam:
            st.markdown("**Tire uma foto usando sua webcam:**")
            camera_photo = st.camera_input("Capturar foto")

            if camera_photo:
                foto_bytes = camera_photo.getvalue()
                st.success("✅ Foto capturada com sucesso!")

        with tab_file:
            st.markdown("**Ou faça upload de uma foto:**")
            uploaded_photo = st.file_uploader(
                "Escolha uma imagem",
                type=["jpg", "jpeg", "png"],
                help="Formatos aceitos: JPG, JPEG, PNG"
            )

            if uploaded_photo:
                foto_bytes = uploaded_photo.read()
                st.image(foto_bytes, caption="Foto Carregada", width=300)
                st.success("✅ Foto carregada com sucesso!")

        st.markdown("---")

        # ==================== TERMOS E CONDIÇÕES ====================
        st.subheader("📜 Termos e Condições")

        aceita_termos = st.checkbox(
            """
            Li e aceito os termos de uso do sistema FacePass, incluindo a coleta e
            armazenamento de dados biométricos (reconhecimento facial) para fins de
            controle de acesso e segurança.
            """,
            help="É necessário aceitar os termos para continuar"
        )

        st.markdown("---")

        # ==================== BOTÕES DE AÇÃO ====================
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

        with col_btn1:
            submit_button = st.form_submit_button(
                "✅ Enviar Cadastro",
                type="primary",
                use_container_width=True
            )

        with col_btn2:
            clear_button = st.form_submit_button(
                "🔄 Limpar Formulário",
                use_container_width=True
            )

        # ==================== VALIDAÇÃO E PROCESSAMENTO ====================
        if submit_button:
            user_controller = st.session_state.get("user_controller")

            if not user_controller:
                st.error("❌ Erro interno: controlador de usuário não encontrado.")
                return

            result = user_controller.create_user(
                name=name,
                email=email,
                cpf=cpf,
                position=position,
                photo=foto_bytes,
                terms_accepted=aceita_termos
            )
            with st.spinner("📤 Enviando seu cadastro..."):

                if result['success']:
                    st.success(result['message'])
                    st.success("""
                            Seus dados foram registrados e estão aguardando aprovação do gestor.
                            Você receberá uma notificação quando seu cadastro for aprovado.

                            **Próximos passos:**
                            1. Aguarde a análise do gestor
                            2. Você será notificado por email
                            3. Após aprovação, já poderá utilizar o sistema de acesso
                        """)
                    st.balloons()

                    with st.expander("📋 Resumo do Cadastro"):
                        usuario = result['data']
                        st.markdown(f"""
                            **Nome:** {usuario.name}
                            **Email:** {usuario.email}
                            **Cargo:** {usuario.position}
                            **Status:** ⏳ Aguardando Aprovação
                            **Data de Cadastro:** {usuario.created_at.strftime('%d/%m/%Y %H:%M:%S')}
                        """)
                else:
                    st.error(result['message'])
                    for error in result['errors']:
                        st.error(f"❌ {error}")

        if clear_button:
            st.info("🔄 Formulário limpo! Preencha novamente se necessário.")
            st.rerun()

        # ==================== DICAS E INFORMAÇÕES ====================
        st.markdown("---")
        st.subheader("💡 Dicas para um Cadastro Bem-Sucedido")

        col_dica1, col_dica2, col_dica3 = st.columns(3)

        with col_dica1:
            st.markdown("""
                **📸 Foto de Qualidade**
                - Fundo neutro
                - Boa iluminação
                - Rosto centralizado
                - Expressão neutra
            """)

        with col_dica2:
            st.markdown("""
                **📝 Dados Corretos**
                - Use seu nome completo
                - Email válido e ativo
                - CPF sem erros
                - Cargo real
            """)

        with col_dica3:
            st.markdown("""
                **⏱️ Tempo de Aprovação**
                - Análise em até 24h
                - Notificação por email
                - Acesso liberado após aprovação
            """)

    # ==================== STATUS DO CADASTRO (CONSULTA) ====================
    st.markdown("---")
    st.subheader("🔍 Já tem cadastro? Consulte o status")

    with st.expander("📧 Consultar Status do Cadastro"):
        email_consulta = st.text_input(
            "Digite seu email cadastrado:",
            placeholder="seu.email@empresa.com",
            key="email_consulta"
        )

    if st.button("🔍 Consultar", key="btn_consultar"):
        if email_consulta:
            # Mock - substituir por consulta real
            # status = usuario_service.get_user_status_by_email(email_consulta)

            st.info(f"""
                    **Status do Cadastro:**
                    - Email: {email_consulta}
                    - Status: ⏳ Aguardando Aprovação
                    - Data de Cadastro: {datetime.now().strftime('%d/%m/%Y')}

                    💡 Seu cadastro está em análise. Aguarde a aprovação do gestor.
                """)
        else:
            st.warning("⚠️ Por favor, digite um email válido.")

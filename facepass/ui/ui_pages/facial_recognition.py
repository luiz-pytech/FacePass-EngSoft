import streamlit as st
from datetime import datetime


def app():
    """Página de Reconhecimento Facial - Controle de Acesso"""
    st.title("🔐 Reconhecimento Facial")
    st.markdown("---")

    # Informações iniciais
    st.info("👋 Posicione seu rosto na câmera e clique em 'Solicitar Acesso' para autenticação.")

    # Estado da sessão
    if 'access_result' not in st.session_state:
        st.session_state['access_result'] = None
    if 'processing' not in st.session_state:
        st.session_state['processing'] = False

    # ==================== CAPTURA DE IMAGEM ====================
    st.subheader("📸 Captura de Imagem")

    # Tabs para escolher método de captura
    tab_webcam, tab_upload = st.tabs(["📷 Webcam", "📁 Upload de Arquivo"])

    captured_image = None

    with tab_webcam:
        st.markdown("**Capturar foto da webcam:**")
        camera_image = st.camera_input("Tire uma foto")

        if camera_image:
            captured_image = camera_image.getvalue()
            st.success("✅ Imagem capturada com sucesso!")

    with tab_upload:
        st.markdown("**Ou faça upload de uma imagem:**")
        uploaded_file = st.file_uploader(
            "Escolha uma imagem",
            type=["jpg", "jpeg", "png"],
            help="Formatos aceitos: JPG, JPEG, PNG"
        )

        if uploaded_file:
            captured_image = uploaded_file.read()
            st.image(captured_image, caption="Imagem Carregada", width=300)
            st.success("✅ Imagem carregada com sucesso!")

    st.markdown("---")

    # ==================== BOTÃO DE SOLICITAÇÃO DE ACESSO ====================
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])

    with col_btn2:
        btn_access = st.button(
            "🔓 Solicitar Acesso",
            type="primary",
            disabled=not captured_image,
            use_container_width=True
        )

    # ==================== PROCESSAMENTO ====================
    if btn_access and captured_image:
        st.session_state['processing'] = True

        # Obter controller e manager_id do session_state
        face_recognition_controller = st.session_state.get('face_recognition_controller')
        manager_id = st.session_state.get('manager_id', 1)  # Default: gestor padrão

        if not face_recognition_controller:
            st.error("❌ Erro: Serviço de reconhecimento facial indisponível.")
            st.session_state['processing'] = False
        else:
            # Processar reconhecimento facial através do controller
            with st.spinner("🔍 Processando reconhecimento facial..."):
                response = face_recognition_controller.process_access_attempt(
                    image_bytes=captured_image,
                    manager_id=manager_id,
                    location='Entrada Principal'
                )

                if response['success']:
                    st.session_state['access_result'] = response['data']
                else:
                    # Erro no processamento
                    st.error(f"❌ {response['message']}")
                    for error in response['errors']:
                        st.error(f"• {error}")
                    st.session_state['access_result'] = response['data']

                st.session_state['processing'] = False

    # ==================== EXIBIÇÃO DE RESULTADO ====================
    if st.session_state.get('access_result'):
        resultado = st.session_state['access_result']

        st.markdown("---")
        st.subheader("📊 Resultado da Autenticação")

        if resultado['acesso_permitido']:
            # ACESSO PERMITIDO
            st.success("✅ ACESSO PERMITIDO")

            # Card com informações do usuário
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 20px 0;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                ">
                    <h1 style="margin: 0; font-size: 48px;">✅</h1>
                    <h2 style="margin: 10px 0;">Bem-vindo(a)!</h2>
                    <h3 style="margin: 10px 0; font-weight: 300;">{resultado['usuario_nome']}</h3>
                    <p style="margin: 5px 0; font-size: 16px; opacity: 0.9;">{resultado['usuario_cargo']}</p>
                    <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 20px 0;">
                    <p style="margin: 5px 0; font-size: 14px;">
                        🎯 Confiança: {resultado['confianca']*100:.2f}%
                    </p>
                    <p style="margin: 5px 0; font-size: 14px;">
                        📅 {resultado['data_hora'].strftime('%d/%m/%Y %H:%M:%S')}
                    </p>
                    <p style="margin: 5px 0; font-size: 14px;">
                        📍 {resultado['local']}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Informações adicionais
            with st.expander("ℹ️ Detalhes da Autenticação"):
                col_det1, col_det2 = st.columns(2)

                with col_det1:
                    st.metric("Nível de Confiança", f"{resultado['confianca']*100:.2f}%")
                    st.markdown(f"**Nome:** {resultado['usuario_nome']}")

                with col_det2:
                    st.metric("Status", "Permitido ✅")
                    st.markdown(f"**Cargo:** {resultado['usuario_cargo']}")

        else:
            # ACESSO NEGADO
            st.error("❌ ACESSO NEGADO")

            # Card com motivo da negação
            motivo = resultado.get('motivo_negacao', 'Motivo não especificado')

            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    margin: 20px 0;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                ">
                    <h1 style="margin: 0; font-size: 48px;">❌</h1>
                    <h2 style="margin: 10px 0;">Acesso Negado</h2>
                    <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 20px 0;">
                    <p style="margin: 10px 0; font-size: 18px; font-weight: 500;">
                        ⚠️ {motivo}
                    </p>
                    <p style="margin: 5px 0; font-size: 14px; opacity: 0.9;">
                        📅 {resultado['data_hora'].strftime('%d/%m/%Y %H:%M:%S')}
                    </p>
                    <p style="margin: 5px 0; font-size: 14px; opacity: 0.9;">
                        📍 {resultado['local']}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Mensagem informativa
            st.warning("""
                **⚠️ Possíveis motivos para negação:**
                - Rosto não reconhecido no banco de dados
                - Usuário ainda não aprovado pelo gestor
                - Cadastro pendente de validação
                - Qualidade da imagem inadequada

                **💡 Sugestão:** Se você é um novo usuário, certifique-se de ter realizado o cadastro
                e aguarde a aprovação do gestor.
            """)

            # Informações adicionais
            with st.expander("ℹ️ Detalhes da Tentativa"):
                col_det1, col_det2 = st.columns(2)

                with col_det1:
                    if resultado.get('confianca'):
                        st.metric("Nível de Confiança", f"{resultado['confianca']*100:.2f}%")
                    st.markdown(f"**Motivo:** {motivo}")

                with col_det2:
                    st.metric("Status", "Negado ❌")
                    st.markdown(f"**Data/Hora:** {resultado['data_hora'].strftime('%d/%m/%Y %H:%M:%S')}")

        # Botão para tentar novamente
        st.markdown("<br>", unsafe_allow_html=True)

        col_retry1, col_retry2, col_retry3 = st.columns([2, 1, 2])

        with col_retry2:
            if st.button("🔄 Tentar Novamente", use_container_width=True):
                st.session_state['access_result'] = None
                st.rerun()

    # ==================== INSTRUÇÕES E DICAS ====================
    if not st.session_state.get('access_result'):
        st.markdown("---")
        st.subheader("📋 Instruções para Melhor Reconhecimento")

        col_tip1, col_tip2, col_tip3 = st.columns(3)

        with col_tip1:
            st.markdown("""
                **💡 Iluminação**
                - Use luz natural ou artificial adequada
                - Evite contra-luz
                - Ilumine o rosto uniformemente
            """)

        with col_tip2:
            st.markdown("""
                **📸 Posicionamento**
                - Centralize o rosto na câmera
                - Mantenha distância adequada
                - Olhe diretamente para a câmera
            """)

        with col_tip3:
            st.markdown("""
                **⚠️ Evite**
                - Óculos escuros
                - Bonés ou chapéus
                - Imagens tremidas ou borradas
            """)

    # ==================== HISTÓRICO (OPCIONAL) ====================
    if st.checkbox("📜 Exibir Histórico de Tentativas Recentes"):
        st.markdown("---")
        st.subheader("📊 Últimas Tentativas de Acesso")

        # Mock data - substituir por chamada ao serviço
        historico = []
        # historico = acesso_service.get_recent_attempts(limit=5)

        if not historico:
            st.info("📭 Nenhuma tentativa recente registrada.")
        else:
            for tentativa in historico:
                status_icon = "✅" if tentativa['acesso_permitido'] else "❌"
                st.markdown(f"{status_icon} {tentativa['data_hora']} - {tentativa.get('usuario_nome', 'Desconhecido')}")

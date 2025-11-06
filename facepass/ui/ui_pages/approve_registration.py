from PIL import Image
import streamlit as st
import io
from facepass.models.user import Usuario
import time


def app():
    """Página de Gestão de Cadastros - Aprovação de Usuários (US1)"""
    st.title("👤 Gestão de Cadastros")
    st.markdown("---")

    # Verificar autenticação
    if not st.session_state.get('manager_authenticated', False):
        st.warning("⚠️ **Acesso Restrito**")
        st.info(
            "Esta página é exclusiva para gestores. Por favor, faça login primeiro.")
        st.markdown("[👉 Ir para Login de Gestor](#)")
        return

    # Obter controller
    user_controller = st.session_state.get('user_controller')
    if not user_controller:
        st.error("❌ Erro: Serviço de usuários indisponível.")
        return

    # Tabs para organizar funcionalidades
    tab1, tab2 = st.tabs(["⏳ Pendentes de Aprovação", "👥 Todos os Usuários"])

    # ==================== TAB 1: PENDENTES DE APROVAÇÃO ====================
    with tab1:
        st.subheader("Usuários Aguardando Aprovação")

        # Buscar usuários pendentes via controller
        result = user_controller.list_pending_users()

        if not result['success']:
            st.error(f"❌ {result['message']}")
            for error in result['errors']:
                st.error(f"• {error}")
            return

        usuarios_pendentes = result['data']
        usuarios_pendentes = [Usuario.from_dict(
            user) for user in usuarios_pendentes]

        if not usuarios_pendentes:
            st.info("📭 Não há usuários pendentes de aprovação no momento.")
        else:
            st.success(
                f"📋 **{len(usuarios_pendentes)} usuário(s) aguardando aprovação**")

            for user in usuarios_pendentes:
                with st.expander(f"📋 {user.name} - {user.email}"):
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        # Exibir foto do usuário
                        if user.photo_recognition:
                            try:
                                image = Image.open(
                                    io.BytesIO(user.photo_recognition))
                                st.image(
                                    image, caption="Foto de Reconhecimento", width=200)
                            except Exception:
                                st.warning("⚠️ Erro ao carregar foto")
                        else:
                            st.warning("Sem foto cadastrada")

                    with col2:
                        # Informações do usuário
                        st.markdown(f"**Nome:** {user.name}")
                        st.markdown(f"**Email:** {user.email}")
                        st.markdown(f"**CPF:** {user.cpf}")
                        st.markdown(f"**Cargo:** {user.position}")
                        st.markdown(
                            f"**Data de Cadastro:** {user.created_at.strftime('%d/%m/%Y %H:%M:%S')}")

                    # Verificar se está em modo de confirmação de rejeição
                    if st.session_state.get(f'confirm_reject_{user.id}'):
                        st.warning(
                            "⚠️ **Confirmação necessária:** Clique novamente em 'Rejeitar' para confirmar a exclusão deste usuário.")

                    # Botões de ação
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])

                    with col_btn1:
                        if st.button("✅ Aprovar", key=f"aprovar_{user.id}", use_container_width=True):
                            with st.spinner("Processando aprovação..."):
                                # Aprovar via controller
                                approve_result = user_controller.approve_user(
                                    user.id, approved=True)

                                if approve_result['success']:
                                    # Obter face_recognition_controller e cadastrar encoding facial
                                    face_recognition_controller = st.session_state.get('face_recognition_controller')

                                    if face_recognition_controller:
                                        encoding_result = face_recognition_controller.save_user_face_encoding(
                                            user.id, user.photo_recognition
                                        )

                                        if not encoding_result['success']:
                                            st.warning(f"⚠️ Usuário aprovado, mas houve erro ao salvar o encoding facial: {encoding_result['message']}")
                                        else:
                                            st.success(f"✅ Usuário {user.name} aprovado com sucesso!")
                                            st.balloons()
                                    else:
                                        st.warning(f"⚠️ Usuário aprovado, mas serviço de reconhecimento facial indisponível")
                                        st.success(f"✅ Usuário {user.name} aprovado (sem reconhecimento facial)!")

                                    time.sleep(2)
                                    if f'confirm_reject_{user.id}' in st.session_state:
                                        del st.session_state[f'confirm_reject_{user.id}']
                                    st.rerun()
                                else:
                                    st.error(f"❌ {approve_result['message']}")

                    with col_btn2:
                        if st.button("❌ Rejeitar", key=f"rejeitar_{user.id}", use_container_width=True):
                            if st.session_state.get(f'confirm_reject_{user.id}'):
                                with st.spinner("Processando rejeição..."):
                                    reject_result = user_controller.approve_user(
                                        user.id, approved=False, motivo="Rejeitado pelo gestor")

                                    if reject_result['success']:
                                        st.success(
                                            f"✅ Usuário {user.name} rejeitado.")
                                        del st.session_state[f'confirm_reject_{user.id}']
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(
                                            f"❌ {reject_result['message']}")
                            else:
                                st.session_state[f'confirm_reject_{user.id}'] = True
                                st.rerun()

    # ==================== TODOS OS USUÁRIOS ====================
    with tab2:
        st.subheader("Gerenciar Todos os Usuários")

        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            filter_name = st.text_input(
                "🔍 Filtrar por Nome", key="filter_name")

        with col_filter2:
            filter_status = st.selectbox(
                "Status", ["Todos", "Aprovados", "Não Aprovados"], key="filter_status")

        with col_filter3:
            filter_cargo = st.text_input(
                "🔍 Filtrar por Cargo", key="filter_cargo")

        st.markdown("---")

        result = user_controller.list_all_users()

        if not result['success']:
            st.error(f"❌ {result['message']}")
            for error in result['errors']:
                st.error(f"• {error}")
            return

        todos_usuarios = result['data']

        todos_usuarios = [Usuario.from_dict(
            user) for user in todos_usuarios]

        # Aplicar filtros
        if filter_name:
            todos_usuarios = [
                u for u in todos_usuarios if filter_name.lower() in u.name.lower()]
        if filter_status != "Todos":
            aprovado = filter_status == "Aprovados"
            todos_usuarios = [
                u for u in todos_usuarios if u.approved == aprovado]
        if filter_cargo:
            todos_usuarios = [
                u for u in todos_usuarios if filter_cargo.lower() in u.position.lower()]

        if not todos_usuarios:
            st.info("📭 Nenhum usuário encontrado.")
        else:
            # Tabela de usuários
            st.markdown(
                f"**Total de usuários encontrados:** {len(todos_usuarios)}")

            for idx, user in enumerate(todos_usuarios):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                    with col1:
                        status_icon = "✅" if user.approved else "⏳"
                        st.markdown(f"{status_icon} **{user.name}**")
                        st.caption(f"{user.email}")

                    with col2:
                        st.markdown(f"**Cargo:** {user.position}")

                    with col3:
                        status_text = "Aprovado" if user.approved else "Pendente"
                        st.markdown(f"**Status:** {status_text}")

                    with col4:
                        col_edit, col_delete = st.columns(2)

                        with col_edit:
                            if st.button("✏️", key=f"edit_{idx}", help="Editar usuário"):
                                st.session_state[f'editing_{user.id}'] = True
                                st.rerun()

                        with col_delete:
                            if st.button("🗑️", key=f"delete_{idx}", help="Remover usuário"):
                                if st.session_state.get(f'confirm_delete_{user.id}'):
                                    # Confirmar e remover
                                    with st.spinner("Removendo usuário..."):
                                        delete_result = user_controller.remove_user(
                                            user.id)

                                        if delete_result['success']:
                                            st.success(
                                                f"✅ Usuário {user.name} removido.")
                                            st.session_state[f'confirm_delete_{user.id}'] = False
                                            st.rerun()
                                        else:
                                            st.error(
                                                f"❌ {delete_result['message']}")
                                else:
                                    st.session_state[f'confirm_delete_{user.id}'] = True
                                    st.warning(
                                        "⚠️ Clique novamente para confirmar exclusão")

                    if st.session_state.get(f'editing_{user.id}'):
                        with st.form(key=f"edit_form_{user.id}"):
                            st.markdown("### ✏️ Editar Usuário")

                            edit_nome = st.text_input("Nome", value=user.name)
                            edit_email = st.text_input(
                                "Email", value=user.email)
                            edit_cpf = st.text_input("CPF", value=user.cpf)
                            edit_cargo = st.selectbox(
                                "Cargo",
                                options=["Desenvolvedor",
                                         "Analista de Dados", "Gerente"],
                                index=["Desenvolvedor", "Analista de Dados", "Gerente"].index(
                                    user.position) if user.position in ["Desenvolvedor", "Analista de Dados", "Gerente"] else 0
                            )
                            edit_aprovado = st.checkbox(
                                "Aprovado", value=user.approved)

                            col_save, col_cancel = st.columns(2)

                            with col_save:
                                submitted = st.form_submit_button(
                                    "💾 Salvar", use_container_width=True)
                                if submitted:
                                    with st.spinner("Salvando alterações..."):
                                        update_result = user_controller.update_user(
                                            user_id=user.id,
                                            name=edit_nome,
                                            email=edit_email,
                                            cpf=edit_cpf,
                                            position=edit_cargo,
                                            approved=edit_aprovado
                                        )

                                        if update_result['success']:
                                            st.success(
                                                "✅ Usuário atualizado com sucesso!")
                                            st.session_state[f'editing_{user.id}'] = False
                                            st.rerun()
                                        else:
                                            st.error(
                                                f"❌ {update_result['message']}")
                                            for error in update_result['errors']:
                                                st.error(f"• {error}")

                            with col_cancel:
                                cancelled = st.form_submit_button(
                                    "❌ Cancelar", use_container_width=True)
                                if cancelled:
                                    st.session_state[f'editing_{user.id}'] = False
                                    st.rerun()

                    st.markdown("---")

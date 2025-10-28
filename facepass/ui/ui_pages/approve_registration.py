import streamlit as st
from datetime import datetime
from facepass.models.user import Usuario
from facepass.services.user_service import UsuarioService
from facepass.services.face_recognition_service import FaceRecognitionService


def app():
    """Página de Gestão de Cadastros - Aprovação de Usuários (US1)"""
    st.title("👤 Gestão de Cadastros")
    st.markdown("---")

    # Tabs para organizar funcionalidades
    tab1, tab2 = st.tabs(["⏳ Pendentes de Aprovação", "👥 Todos os Usuários"])

    # ==================== TAB 1: PENDENTES DE APROVAÇÃO ====================
    with tab1:
        st.subheader("Usuários Aguardando Aprovação")

        face_recognition_service: FaceRecognitionService = st.session_state["face_recognition_service"]
        usuario_service: UsuarioService = st.session_state["user_service"]
        usuarios_pendentes = usuario_service.list_pending_approvals()

        # Transformando uma lista de 'dicts' em uma lista de Objetos 'Usuario'
        usuarios_pendentes = [Usuario.from_dict(row) for row in usuarios_pendentes]
        
        if not usuarios_pendentes:
            st.info("📭 Não há usuários pendentes de aprovação no momento.")
        else:
            for user in usuarios_pendentes:
                with st.expander(f"📋 {user.name} - {user.email}"):
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        # Exibir foto do usuário
                        if user.photo_recognition:
                            st.image(user.photo_recognition, caption="Foto de Reconhecimento", width=200)
                        else:
                            st.warning("Sem foto cadastrada")

                    with col2:
                        # Informações do usuário
                        st.markdown(f"**Nome:** {user.name}")
                        st.markdown(f"**Email:** {user.email}")
                        st.markdown(f"**CPF:** {user.cpf}")
                        st.markdown(f"**Cargo:** {user.position}")
                        st.markdown(f"**Data de Cadastro:** {user.created_at}")

                    # Botões de ação
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])

                    with col_btn1:
                        if st.button("✅ Aprovar", key=f"aprovar_{user.id}"):
                            usuario_service.approve_user(user.id)

                            # Cadastra um encoding do usuário na tabela de encodings do BD
                            face_recognition_service.save_user_face(user.id, user.photo_recognition )

                            st.success(f"Usuário {user.name} aprovado com sucesso!")
                            st.rerun()

                    with col_btn2:
                        if st.button("❌ Rejeitar", key=f"rejeitar_{user.id}"):
                            usuario_service.reject_user(user.id)
                            st.warning(f"Usuário {user.name} rejeitado.")
                            st.rerun()

    # ==================== TAB 2: TODOS OS USUÁRIOS ====================
    with tab2:
        st.subheader("Gerenciar Todos os Usuários")

        # Filtros
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            filter_name = st.text_input("🔍 Filtrar por Nome", key="filter_name")

        with col_filter2:
            filter_status = st.selectbox("Status", ["Todos", "Aprovados", "Não Aprovados"], key="filter_status")

        with col_filter3:
            filter_cargo = st.text_input("🔍 Filtrar por Cargo", key="filter_cargo")

        st.markdown("---")

        # Mock data - substituir pela chamada ao serviço
        todos_usuarios = []
        todos_usuarios = usuario_service.list_all_users()

        # Aplicar filtros (quando integrado com banco)
        # if filter_name:
        #     todos_usuarios = [u for u in todos_usuarios if filter_name.lower() in u['nome'].lower()]
        # if filter_status != "Todos":
        #     aprovado = filter_status == "Aprovados"
        #     todos_usuarios = [u for u in todos_usuarios if u['aprovado'] == aprovado]
        # if filter_cargo:
        #     todos_usuarios = [u for u in todos_usuarios if filter_cargo.lower() in u['cargo'].lower()]

        if not todos_usuarios:
            st.info("📭 Nenhum usuário encontrado.")
        else:
            # Tabela de usuários
            st.markdown(f"**Total de usuários encontrados:** {len(todos_usuarios)}")

            for idx, user in enumerate(todos_usuarios):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                    with col1:
                        status_icon = "✅" if user.get('aprovado') else "⏳"
                        st.markdown(f"{status_icon} **{user.get('nome', 'N/A')}**")
                        st.caption(f"{user.get('email', 'N/A')}")

                    with col2:
                        st.markdown(f"**Cargo:** {user.get('cargo', 'N/A')}")

                    with col3:
                        status_text = "Aprovado" if user.get('aprovado') else "Pendente"
                        st.markdown(f"**Status:** {status_text}")

                    with col4:
                        col_edit, col_delete = st.columns(2)

                        with col_edit:
                            if st.button("✏️", key=f"edit_{idx}", help="Editar usuário"):
                                st.session_state[f'editing_{user.get("id")}'] = True

                        with col_delete:
                            if st.button("🗑️", key=f"delete_{idx}", help="Remover usuário"):
                                if st.session_state.get(f'confirm_delete_{user.get("id")}'):
                                    # Chamar usuario_service.remove_user(user['id'])
                                    st.success(f"Usuário {user.get('nome')} removido.")
                                    st.rerun()
                                else:
                                    st.session_state[f'confirm_delete_{user.get("id")}'] = True
                                    st.warning("⚠️ Clique novamente para confirmar exclusão")

                    # Modal de edição (se ativado)
                    if st.session_state.get(f'editing_{user.get("id")}'):
                        with st.form(key=f"edit_form_{user.get('id')}"):
                            st.markdown("### ✏️ Editar Usuário")

                            edit_nome = st.text_input("Nome", value=user.get('nome', ''))
                            edit_email = st.text_input("Email", value=user.get('email', ''))
                            edit_cargo = st.text_input("Cargo", value=user.get('cargo', ''))
                            edit_aprovado = st.checkbox("Aprovado", value=user.get('aprovado', False))

                            col_save, col_cancel = st.columns(2)

                            with col_save:
                                submitted = st.form_submit_button("💾 Salvar")
                                if submitted:
                                    # Atualizar usuário via usuario_service.update_user()
                                    st.success("Usuário atualizado com sucesso!")
                                    st.session_state[f'editing_{user.get("id")}'] = False
                                    st.rerun()

                            with col_cancel:
                                cancelled = st.form_submit_button("❌ Cancelar")
                                if cancelled:
                                    st.session_state[f'editing_{user.get("id")}'] = False
                                    st.rerun()

                    st.markdown("---")

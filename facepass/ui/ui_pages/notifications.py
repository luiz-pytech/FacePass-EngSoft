import streamlit as st
from datetime import datetime


def app():
    """Página de Notificações - Visualização de alertas para gestores (US3)"""
    st.title("🔔 Notificações")
    st.markdown("---")

    # Verificar autenticação
    if not st.session_state.get('manager_authenticated', False):
        st.warning("⚠️ **Acesso Restrito**")
        st.info(
            "Esta página é exclusiva para gestores. Por favor, faça login primeiro.")
        st.markdown("[👉 Ir para Login de Gestor](#)")
        return

    # Obter controller e manager_id
    notification_controller = st.session_state.get('notification_controller')
    manager_id = st.session_state.get('manager_id')

    if not notification_controller:
        st.error("❌ Erro: Serviço de notificações indisponível.")
        return

    # Obter estatísticas
    stats_result = notification_controller.get_statistics(manager_id)

    if stats_result['success']:
        stats = stats_result['data']
    else:
        stats = {'total': 0, 'unread': 0, 'read': 0}
        st.error(f"❌ {stats_result['message']}")

    # Mostrar estatísticas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📋 Total de Notificações", stats['total'])

    with col2:
        st.metric("✉️ Não Lidas", stats['unread'],
                  delta=None if stats['unread'] == 0 else f"{stats['unread']} novas")

    with col3:
        st.metric("✅ Lidas", stats['read'])

    st.markdown("---")

    # Filtros
    col_filter1, col_filter2 = st.columns([2, 1])

    with col_filter1:
        filter_type = st.selectbox(
            "Filtrar por:",
            ["Todas", "Não Lidas", "Lidas"],
            key="filter_notifications"
        )

    with col_filter2:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Buscar notificações baseado no filtro
    if filter_type == "Não Lidas":
        result = notification_controller.list_unread_notifications(manager_id)
    else:
        result = notification_controller.list_all_notifications(manager_id)

    if not result['success']:
        st.error(f"❌ {result['message']}")
        for error in result['errors']:
            st.error(f"• {error}")
        return

    notifications = result['data']

    # Aplicar filtro de "Lidas" se necessário
    if filter_type == "Lidas":
        notifications = [n for n in notifications if n[6]]  # n[6] = is_read

    if not notifications:
        st.info("📭 Nenhuma notificação no momento.")
    else:
        st.success(
            f"📬 **{len(notifications)} notificação(ões) encontrada(s)**")

        for notif in notifications:
            # Desempacotar tupla do banco
            # (id, manager_id, access_register_id, created_at, type_notification, message, is_read)
            notif_id = notif[0]
            # manager_id_notif = notif[1]
            # access_register_id = notif[2]
            created_at = notif[3]
            type_notification = notif[4]
            message = notif[5]
            is_read = notif[6]

            # Determinar ícone e cor baseado no tipo
            if type_notification == "access_denied":
                icone = "🚫"
                cor_fundo = "#fff3cd"  # Amarelo claro
                cor_borda = "#ffc107"
                titulo = "Acesso Negado"
            elif type_notification == "new_user_pending":
                icone = "👤"
                cor_fundo = "#d1ecf1"  # Azul claro
                cor_borda = "#0dcaf0"
                titulo = "Novo Cadastro Pendente"
            else:
                icone = "ℹ️"
                cor_fundo = "#f8f9fa"
                cor_borda = "#6c757d"
                titulo = "Notificação"

            # Status de leitura
            status_icon = "✅" if is_read else "✉️"
            status_text = "Lida" if is_read else "Não lida"
            status_color = "#28a745" if is_read else "#dc3545"

            # Formatar data
            try:
                if isinstance(created_at, str):
                    data_formatada = datetime.fromisoformat(
                        created_at).strftime('%d/%m/%Y %H:%M:%S')
                else:
                    data_formatada = created_at.strftime('%d/%m/%Y %H:%M:%S')
            except:
                data_formatada = str(created_at)

            with st.container():
                # Card da notificação
                st.markdown(f"""
                    <div style="
                        background-color: {cor_fundo};
                        border-left: 4px solid {cor_borda};
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 15px;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                                    <span style="font-size: 24px;">{icone}</span>
                                    <div>
                                        <div style="font-weight: 600; color: #333;">{titulo}</div>
                                        <div style="font-size: 12px; color: #666;">
                                            {data_formatada}
                                        </div>
                                    </div>
                                </div>
                                <div style="color: #444; font-size: 14px; line-height: 1.6; margin-left: 34px;">
                                    {message}
                                </div>
                                <div style="margin-top: 10px; margin-left: 34px; font-size: 12px;">
                                    <span style="color: {status_color}; font-weight: 600;">
                                        {status_icon} {status_text}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Botões de ação
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])

                with col_btn1:
                    if not is_read:
                        if st.button("✓ Marcar como lida", key=f"mark_read_{notif_id}", use_container_width=True):
                            with st.spinner("Marcando..."):
                                mark_result = notification_controller.mark_as_read(
                                    notif_id)

                                if mark_result['success']:
                                    st.success("✅ Marcada como lida!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {mark_result['message']}")

                with col_btn2:
                    # Verificar confirmação de exclusão
                    if st.session_state.get(f'confirm_delete_notif_{notif_id}'):
                        st.warning("⚠️ Confirme a exclusão")

                    if st.button("🗑️ Excluir", key=f"delete_{notif_id}", use_container_width=True):
                        if st.session_state.get(f'confirm_delete_notif_{notif_id}'):
                            with st.spinner("Removendo..."):
                                delete_result = notification_controller.delete_notification(
                                    notif_id)

                                if delete_result['success']:
                                    st.success("✅ Notificação removida!")
                                    del st.session_state[f'confirm_delete_notif_{notif_id}']
                                    st.rerun()
                                else:
                                    st.error(f"❌ {delete_result['message']}")
                        else:
                            st.session_state[f'confirm_delete_notif_{notif_id}'] = True
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    # Informações sobre notificações
    with st.expander("ℹ️ Sobre as Notificações"):
        st.markdown("""
            ### 🔔 Sistema de Notificações

            **Tipos de notificações:**
            - 🚫 **Acesso Negado:** Alerta quando há tentativa de acesso não autorizado
            - 👤 **Novo Cadastro:** Notifica quando há novo usuário aguardando aprovação

            **Como funcionam:**
            1. Notificações são criadas automaticamente pelo sistema
            2. Aparecem em tempo real para gestores autenticados
            3. Podem ser marcadas como lidas ou excluídas
            4. Ajudam na auditoria e segurança do sistema

            **Dica:** Mantenha suas notificações organizadas marcando como lidas após visualizar!
        """)

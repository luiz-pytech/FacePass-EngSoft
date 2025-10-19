import streamlit as st


def app():
    st.title("🔔 Notificações")
    st.markdown("---")

    # Estatísticas de notificações
    total_notif = len(st.session_state.notificacoes)
    nao_lidas = len(
        [n for n in st.session_state.notificacoes if not n['lida']])

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total de Notificações", total_notif)

    with col2:
        st.metric("Não Lidas", nao_lidas)

    st.markdown("---")

    # Listar notificações
    if not st.session_state.notificacoes:
        st.info("📭 Nenhuma notificação no momento.")
    else:
        for idx, notif in enumerate(st.session_state.notificacoes):
            classe = "notification"
            icone = "ℹ️"

            if notif['tipo'] == 'alerta':
                classe += " notification-alert"
                icone = "⚠️"
            elif notif['tipo'] == 'sucesso':
                classe += " notification-success"
                icone = "✅"

            status_leitura = "✉️ Não lida" if not notif['lida'] else "✅ Lida"

            with st.container():
                st.markdown(f"""
                    <div class="{classe}">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                                    <span style="font-size: 24px;">{icone}</span>
                                    <div>
                                        <div style="font-weight: 600; color: #333;">{notif['titulo']}</div>
                                        <div style="font-size: 12px; color: #999;">{notif['tempo']}</div>
                                    </div>
                                </div>
                                <div style="color: #666; font-size: 14px; line-height: 1.5;">
                                    {notif['mensagem']}
                                </div>
                                <div style="margin-top: 10px; font-size: 12px; color: #999;">
                                    {status_leitura}
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if not notif['lida']:
                    if st.button(f"✓ Marcar como lida", key=f"marcar_{idx}"):
                        st.session_state.notificacoes[idx]['lida'] = True
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

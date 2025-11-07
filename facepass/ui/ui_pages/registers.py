import streamlit as st
from datetime import datetime, timedelta
import io


def app():
    """Página de Relatórios de Acesso - US2"""
    st.title("📜 Relatórios de Acesso")
    st.markdown("---")

    # Verificar autenticação do gestor
    if not st.session_state.get('manager_authenticated', False):
        st.warning(
            "⚠️ Acesso restrito. Faça login como gestor para acessar os relatórios.")
        return

    # Obter controller do session_state
    access_controller = st.session_state.get('access_controller')

    if not access_controller:
        st.error("❌ Relatórios não disponíveis. Controller não inicializado.")
        return

    # ==================== FILTROS ====================
    st.subheader("🔍 Filtros de Busca")

    col1, col2, col3 = st.columns(3)

    with col1:
        filter_user = st.text_input(
            "👤 Nome do Usuário", placeholder="Digite o nome...")

    with col2:
        filter_date_start = st.date_input(
            "📅 Data Inicial",
            value=datetime.now() - timedelta(days=7)
        )

    with col3:
        filter_date_end = st.date_input(
            "📅 Data Final",
            value=datetime.now()
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        filter_status = st.selectbox(
            "Status de Acesso",
            ["Todos", "Permitido", "Negado"]
        )

    with col5:
        filter_location = st.text_input(
            "📍 Local/Câmera", placeholder="Ex: Entrada Principal")

    with col6:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_search = st.button("🔍 Buscar", type="primary", width='stretch')

    st.markdown("---")

    # ==================== ESTATÍSTICAS ====================
    st.subheader("📊 Estatísticas do Período")

    # Buscar registros com filtros
    result = access_controller.get_registers_with_filters(
        user_name=filter_user,
        status=filter_status,
        location=filter_location,
        start_date=filter_date_start.strftime('%Y-%m-%d'),
        end_date=filter_date_end.strftime('%Y-%m-%d')
    )

    if not result.get('success'):
        st.error(f"❌ {result.get('message', 'Erro ao carregar registros')}")
        return

    registros = result.get('data', [])

    # Buscar estatísticas
    stats_result = access_controller.get_statistics_by_period(
        start_date=filter_date_start.strftime('%Y-%m-%d'),
        end_date=filter_date_end.strftime('%Y-%m-%d')
    )

    stats = stats_result.get('data', {})
    total_acessos = stats.get('total', 0)
    acessos_permitidos = stats.get('permitidos', 0)
    acessos_negados = stats.get('negados', 0)
    taxa_sucesso = stats.get('taxa_sucesso', 0.0)

    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

    with col_stat1:
        st.metric("Total de Acessos", total_acessos)

    with col_stat2:
        st.metric("✅ Permitidos", acessos_permitidos)

    with col_stat3:
        st.metric("❌ Negados", acessos_negados)

    with col_stat4:
        st.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")

    st.markdown("---")

    # ==================== TABELA DE REGISTROS ====================
    st.subheader("📋 Registros de Acesso")

    # Botão de exportação
    col_export1, col_export2, col_export3 = st.columns([1, 1, 4])

    with col_export1:
        if registros and st.button("📥 Exportar CSV", width='stretch'):
            # Gerar CSV dos registros
            csv_content = access_controller.export_registers_csv(registros)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_content,
                file_name=f"relatorio_acessos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        elif not registros:
            st.button("📥 Exportar CSV", width='stretch', disabled=True)

    with col_export2:
        if st.button("📄 Exportar PDF", width='stretch'):
            st.info("🚧 Funcionalidade de exportação PDF em desenvolvimento")

    st.markdown("<br>", unsafe_allow_html=True)

    # Exibir registros
    if not registros:
        st.info("📭 Nenhum registro encontrado para os filtros selecionados.")
    else:
        # Ordenar por data (mais recente primeiro)
        registros_ordenados = sorted(
            registros,
            key=lambda x: x.get('created_at', datetime.min),
            reverse=True
        )

        # Exibir em cards
        for idx, registro in enumerate(registros_ordenados):
            status_icon = "✅" if registro.get('access_allowed') else "❌"
            status_text = "PERMITIDO" if registro.get(
                'access_allowed') else "NEGADO"
            status_color = "#28a745" if registro.get(
                'access_allowed') else "#dc3545"

            # Formatação da data
            created_at = registro.get('created_at', 'N/A')
            if isinstance(created_at, datetime):
                data_formatada = created_at.strftime('%d/%m/%Y %H:%M:%S')
            else:
                data_formatada = str(created_at)

            with st.container():
                st.markdown(f"""
                    <div style="
                        border: 2px solid {status_color};
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 15px;
                        background-color: #f8f9fa;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0; color: #333;">
                                    {status_icon} {registro.get('user_name', 'Desconhecido')}
                                </h4>
                                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                                    📅 {data_formatada}
                                </p>
                                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                                    🚪 Tipo: {registro.get('type_access', 'N/A').upper()}
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <span style="
                                    background-color: {status_color};
                                    color: white;
                                    padding: 8px 16px;
                                    border-radius: 20px;
                                    font-weight: bold;
                                    font-size: 14px;
                                ">{status_text}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                # Detalhes adicionais (expansível)
                with st.expander("📋 Ver Detalhes"):
                    col_det1, col_det2 = st.columns(2)

                    with col_det1:
                        st.markdown(
                            f"**ID do Registro:** {registro.get('id', 'N/A')}")
                        st.markdown(
                            f"**Tipo de Acesso:** {registro.get('type_access', 'N/A')}")
                        st.markdown(
                            f"**Email do Usuário:** {registro.get('user_email', 'N/A')}")

                        if not registro.get('access_allowed'):
                            st.markdown(
                                f"**⚠️ Motivo da Negação:** {registro.get('reason_denied', 'N/A')}")

                    with col_det2:
                        # Exibir imagem capturada (se disponível)
                        if registro.get('captured_image'):
                            st.info(
                                "📷 Imagem capturada disponível no banco de dados")
                        else:
                            st.info("Sem imagem disponível")

                st.markdown("</div>", unsafe_allow_html=True)

    # ==================== GRÁFICOS (OPCIONAL) ====================
    if registros and st.checkbox("📊 Exibir Gráficos Analíticos"):
        st.markdown("---")
        st.subheader("📈 Análise Visual")

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("**Acessos por Status**")
            chart_data = {
                "Status": ["Permitido", "Negado"],
                "Quantidade": [acessos_permitidos, acessos_negados]
            }
            st.bar_chart(chart_data, x="Status", y="Quantidade")

        with col_chart2:
            st.markdown("**Acessos por Dia**")
            # Agrupar registros por dia
            # (implementar quando integrado com dados reais)
            st.info("🚧 Gráfico de timeline em desenvolvimento")

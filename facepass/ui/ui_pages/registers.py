import streamlit as st
from datetime import datetime, timedelta
import io


def app():
    """Página de Relatórios de Acesso - US2"""
    st.title("📜 Relatórios de Acesso")
    st.markdown("---")

    # ==================== FILTROS ====================
    st.subheader("🔍 Filtros de Busca")

    col1, col2, col3 = st.columns(3)

    with col1:
        filter_user = st.text_input("👤 Nome do Usuário", placeholder="Digite o nome...")

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
        filter_location = st.text_input("📍 Local/Câmera", placeholder="Ex: Entrada Principal")

    with col6:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_search = st.button("🔍 Buscar", type="primary", use_container_width=True)

    st.markdown("---")

    # ==================== ESTATÍSTICAS ====================
    st.subheader("📊 Estatísticas do Período")

    # Mock data - substituir por chamada ao serviço
    registros = []
    # registros = registro_service.get_access_records(
    #     user_name=filter_user,
    #     date_start=filter_date_start,
    #     date_end=filter_date_end,
    #     status=filter_status,
    #     location=filter_location
    # )

    # Calcular estatísticas
    total_acessos = len(registros)
    acessos_permitidos = len([r for r in registros if r.get('acesso_permitido')])
    acessos_negados = total_acessos - acessos_permitidos
    taxa_sucesso = (acessos_permitidos / total_acessos * 100) if total_acessos > 0 else 0

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
        if st.button("📥 Exportar CSV", use_container_width=True):
            # Gerar CSV dos registros
            csv_content = generate_csv(registros)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_content,
                file_name=f"relatorio_acessos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with col_export2:
        if st.button("📄 Exportar PDF", use_container_width=True):
            st.info("🚧 Funcionalidade de exportação PDF em desenvolvimento")

    st.markdown("<br>", unsafe_allow_html=True)

    # Exibir registros
    if not registros:
        st.info("📭 Nenhum registro encontrado para os filtros selecionados.")
    else:
        # Ordenar por data (mais recente primeiro)
        registros_ordenados = sorted(
            registros,
            key=lambda x: x.get('data_hora', datetime.min),
            reverse=True
        )

        # Exibir em cards
        for idx, registro in enumerate(registros_ordenados):
            status_icon = "✅" if registro.get('acesso_permitido') else "❌"
            status_text = "PERMITIDO" if registro.get('acesso_permitido') else "NEGADO"
            status_color = "#28a745" if registro.get('acesso_permitido') else "#dc3545"

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
                                    {status_icon} {registro.get('usuario_nome', 'Desconhecido')}
                                </h4>
                                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                                    📅 {registro.get('data_hora', 'N/A').strftime('%d/%m/%Y %H:%M:%S') if isinstance(registro.get('data_hora'), datetime) else registro.get('data_hora', 'N/A')}
                                </p>
                                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                                    📍 {registro.get('local', 'Local não especificado')}
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
                        st.markdown(f"**Tipo de Acesso:** {registro.get('tipo_acesso', 'N/A')}")
                        st.markdown(f"**Confiança do Reconhecimento:** {registro.get('confianca_reconhecimento', 'N/A')}%")

                        if not registro.get('acesso_permitido'):
                            st.markdown(f"**⚠️ Motivo da Negação:** {registro.get('motivo_negacao', 'N/A')}")

                    with col_det2:
                        # Exibir imagem capturada (se disponível)
                        if registro.get('imagem_capturada'):
                            st.image(
                                registro['imagem_capturada'],
                                caption="Imagem Capturada",
                                width=200
                            )
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


def generate_csv(registros):
    """Gera conteúdo CSV dos registros"""
    if not registros:
        return "Nenhum registro disponível"

    # Cabeçalho
    csv_lines = ["ID,Usuario,Data/Hora,Local,Status,Tipo Acesso,Confianca,Motivo Negacao\n"]

    # Dados
    for reg in registros:
        linha = f"{reg.get('id', '')},{reg.get('usuario_nome', '')},"
        linha += f"{reg.get('data_hora', '')},"
        linha += f"{reg.get('local', '')},"
        linha += f"{'Permitido' if reg.get('acesso_permitido') else 'Negado'},"
        linha += f"{reg.get('tipo_acesso', '')},"
        linha += f"{reg.get('confianca_reconhecimento', '')},"
        linha += f"{reg.get('motivo_negacao', '')}\n"
        csv_lines.append(linha)

    return "".join(csv_lines)

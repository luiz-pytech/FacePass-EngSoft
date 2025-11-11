import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def app():
    """Dashboard principal para gestores - Apenas renderização"""

    # Verificar autenticação do gestor
    if not st.session_state.get('manager_authenticated', False):
        st.warning(
            "⚠️ Acesso restrito. Faça login como gestor para acessar o dashboard.")
        return

    # Obter service do session_state
    dashboard_service = st.session_state.get('dashboard_service')

    if not dashboard_service:
        st.error("❌ Dashboard não disponível. Service não inicializado.")
        return

    st.title("📊 Dashboard de Gestão")
    st.markdown("---")

    # Quick Cards - Estatísticas principais
    render_quick_cards(dashboard_service)

    st.markdown("---")

    # Controle de Presença
    render_presence_control(dashboard_service)

    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        render_access_timeline_chart(dashboard_service)

    with col2:
        render_access_by_hour_chart(dashboard_service)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        render_success_rate_chart(dashboard_service)

    with col4:
        render_top_users_chart(dashboard_service)

    st.markdown("---")

    # Gráfico de notificações
    render_notifications_chart(dashboard_service)

    st.markdown("---")

    # Seção de Horas Extras
    render_overtime_section(dashboard_service)


def render_quick_cards(dashboard_service):
    """Renderiza os cards com estatísticas rápidas"""
    st.subheader("📈 Visão Geral")

    # Obter dados do service
    result = dashboard_service.get_quick_stats()

    if not result.get('success'):
        st.error(f"❌ {result.get('message', 'Erro ao carregar estatísticas')}")
        return

    stats = result.get('data', {})

    # Primeira linha de cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="👥 Usuários Cadastrados",
            value=stats.get('total_users', 0),
            help="Total de usuários no sistema"
        )

    with col2:
        st.metric(
            label="✅ Usuários Aprovados",
            value=stats.get('approved_users', 0),
            help="Usuários com acesso liberado"
        )

    with col3:
        st.metric(
            label="⏳ Pendentes",
            value=stats.get('pending_users', 0),
            help="Aguardando aprovação"
        )

    with col4:
        st.metric(
            label="📊 Taxa de Aprovação",
            value=f"{stats.get('approval_rate', 0.0):.1f}%",
            help="Percentual de usuários aprovados"
        )

    # Segunda linha de cards
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric(
            label="🚪 Acessos Hoje",
            value=stats.get('today_total', 0),
            help="Total de tentativas de acesso hoje"
        )

    with col6:
        st.metric(
            label="✅ Permitidos Hoje",
            value=stats.get('today_allowed', 0),
            help="Acessos permitidos hoje"
        )

    with col7:
        today_denied = stats.get('today_denied', 0)
        st.metric(
            label="❌ Negados Hoje",
            value=today_denied,
            help="Acessos negados hoje",
            delta=f"-{today_denied}" if today_denied > 0 else "0",
            delta_color="inverse"
        )

    with col8:
        unread = stats.get('unread_notifications', 0)
        st.metric(
            label="🔔 Notificações",
            value=unread,
            help="Notificações não lidas",
            delta=f"+{unread}" if unread > 0 else "0"
        )


def render_presence_control(dashboard_service):
    """Renderiza o controle de presença (entrada/saída) para todos os usuários"""
    st.subheader("👥 Controle de Presença")

    # Filtro de data
    col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 1])

    with col_filter1:
        date_option = st.selectbox(
            "Selecionar Data",
            ["Hoje", "Ontem", "Escolher data"],
            key="date_selector"
        )

    selected_date = None
    with col_filter2:
        if date_option == "Hoje":
            from datetime import date
            selected_date = None  # None usa CURDATE() no SQL
            display_date = date.today().strftime("%d/%m/%Y")
        elif date_option == "Ontem":
            from datetime import date, timedelta
            yesterday = date.today() - timedelta(days=1)
            selected_date = yesterday.strftime("%Y-%m-%d")
            display_date = yesterday.strftime("%d/%m/%Y")
        else:  # Escolher data
            from datetime import date
            custom_date = st.date_input(
                "Data",
                value=date.today(),
                key="custom_date"
            )
            selected_date = custom_date.strftime("%Y-%m-%d")
            display_date = custom_date.strftime("%d/%m/%Y")

    with col_filter3:
        if st.button("🔄 Atualizar", key="refresh_presence"):
            st.rerun()

    # Obter dados do service
    result = dashboard_service.get_all_users_attendance(selected_date)

    if not result.get('success'):
        st.error(
            f"❌ {result.get('message', 'Erro ao carregar dados de presença')}")
        return

    all_users = result.get('data', [])
    total_count = result.get('total_count', 0)
    present_count = result.get('present_count', 0)
    absent_count = result.get('absent_count', 0)
    left_count = result.get('left_count', 0)

    # Exibir estatísticas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label=f"📅 {display_date}",
            value=f"{total_count} usuários",
            help="Total de usuários aprovados"
        )

    with col2:
        st.metric(
            label="🟢 Presentes",
            value=present_count,
            help="Usuários que entraram e não saíram"
        )

    with col3:
        st.metric(
            label="🟡 Saíram",
            value=left_count,
            help="Usuários que já saíram"
        )

    with col4:
        st.metric(
            label="🔴 Ausentes",
            value=absent_count,
            help="Usuários que não registraram entrada",
            delta=f"-{absent_count}" if absent_count > 0 else "0",
            delta_color="inverse"
        )

    if not all_users:
        st.info("Nenhum usuário cadastrado.")
        return

    # Preparar dados para exibição
    df_users = pd.DataFrame(all_users)

    # Formatar horários
    def format_time(time_value):
        if pd.isna(time_value) or time_value is None:
            return "-"
        if isinstance(time_value, str):
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(time_value)
                return dt.strftime("%H:%M:%S")
            except:
                return time_value
        return str(time_value)

    # Criar DataFrame de exibição
    df_display = pd.DataFrame({
        'Nome': df_users['name'],
        'Cargo': df_users['position'],
        'Entrada': df_users['last_entry_time'].apply(format_time),
        'Saída': df_users['last_exit_time'].apply(format_time),
        'Acessos': df_users['access_count'],
        'Status': df_users['status'].apply(lambda x:
            '🟢 Presente' if x == 'Presente' else
            '🟡 Saiu' if x == 'Saiu' else
            '🔴 Ausente'
        )
    })

    # Opções de filtro
    status_filter = st.multiselect(
        "Filtrar por Status",
        ['🟢 Presente', '🟡 Saiu', '🔴 Ausente'],
        default=['🟢 Presente', '🟡 Saiu', '🔴 Ausente'],
        key="status_filter"
    )

    # Aplicar filtro
    if status_filter:
        df_filtered = df_display[df_display['Status'].isin(status_filter)]
    else:
        df_filtered = df_display

    # Exibir tabela
    st.dataframe(
        df_filtered,
        width='stretch',
        hide_index=True
    )

    # Informações adicionais
    st.caption(f"Total exibido: {len(df_filtered)} de {len(df_display)} usuários")


def render_access_timeline_chart(dashboard_service):
    """Gráfico de linha: Acessos ao longo do tempo (últimos 30 dias)"""
    st.subheader("📅 Acessos nos Últimos 30 Dias")

    # Obter dados do service
    result = dashboard_service.get_access_timeline(days=30)

    if not result.get('success'):
        st.error(f"❌ {result.get('message', 'Erro ao carregar dados')}")
        return

    data = result.get('data', [])

    if not data:
        st.info("Nenhum dado disponível para o período.")
        return

    df = pd.DataFrame(data)

    # Criar gráfico
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total'],
        name='Total',
        mode='lines+markers',
        line=dict(color='blue', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['allowed'],
        name='Permitidos',
        mode='lines+markers',
        line=dict(color='green', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['denied'],
        name='Negados',
        mode='lines+markers',
        line=dict(color='red', width=2)
    ))

    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Quantidade",
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig, width='stretch')


def render_access_by_hour_chart(dashboard_service):
    """Gráfico de barras: Acessos por hora do dia (hoje)"""
    st.subheader("🕐 Acessos por Hora (Hoje)")

    # Obter dados do service
    result = dashboard_service.get_hourly_access_distribution()

    if not result.get('success'):
        st.error(f"❌ {result.get('message', 'Erro ao carregar dados')}")
        return

    data = result.get('data', [])

    if not data:
        st.info("Nenhum acesso registrado hoje.")
        return

    df = pd.DataFrame(data)

    # Criar gráfico
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['hour'],
        y=df['allowed'],
        name='Permitidos',
        marker_color='green'
    ))

    fig.add_trace(go.Bar(
        x=df['hour'],
        y=df['denied'],
        name='Negados',
        marker_color='red'
    ))

    fig.update_layout(
        xaxis_title="Hora",
        yaxis_title="Quantidade",
        barmode='stack',
        height=400
    )

    st.plotly_chart(fig, width='stretch')


def render_success_rate_chart(dashboard_service):
    """Gráfico de área: Taxa de sucesso ao longo do tempo"""
    st.subheader("📈 Taxa de Sucesso de Reconhecimento")

    # Obter dados do service
    result = dashboard_service.get_success_rate_trend(days=30)

    if not result.get('success'):
        st.error(f"❌ {result.get('message', 'Erro ao carregar dados')}")
        return

    data = result.get('data', [])

    if not data:
        st.info("Nenhum dado disponível.")
        return

    df = pd.DataFrame(data)

    # Criar gráfico
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['success_rate'],
        fill='tozeroy',
        name='Taxa de Sucesso',
        line=dict(color='lightblue', width=2)
    ))

    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Taxa de Sucesso (%)",
        yaxis=dict(range=[0, 100]),
        height=400
    )

    st.plotly_chart(fig, width='stretch')


def render_top_users_chart(dashboard_service):
    """Gráfico de barras horizontal: Top 10 usuários com mais acessos"""
    st.subheader("🏆 Top 10 Usuários")

    # Obter dados do service
    result = dashboard_service.get_top_active_users(limit=10)

    if not result.get('success'):
        st.error(f"❌ {result.get('message', 'Erro ao carregar dados')}")
        return

    data = result.get('data', [])

    if not data:
        st.info("Nenhum dado disponível.")
        return

    df = pd.DataFrame(data)

    # Criar gráfico
    fig = go.Figure(go.Bar(
        x=df['access_count'],
        y=df['name'],
        orientation='h',
        marker_color='lightgreen'
    ))

    fig.update_layout(
        xaxis_title="Número de Acessos",
        yaxis_title="Usuário",
        height=400
    )

    st.plotly_chart(fig, width='stretch')


def render_notifications_chart(dashboard_service):
    """Gráfico de pizza: Distribuição de notificações por tipo"""
    st.subheader("🔔 Notificações por Tipo")

    # Obter dados do service
    result = dashboard_service.get_notification_distribution(days=30)

    if not result.get('success'):
        st.error(f"❌ {result.get('message', 'Erro ao carregar dados')}")
        return

    data = result.get('data', [])

    if not data:
        st.info("Nenhuma notificação registrada.")
        return

    df = pd.DataFrame(data)

    # Criar gráfico
    fig = px.pie(
        df,
        values='count',
        names='type_notification',
        title='Distribuição de Notificações',
        hole=0.3
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)

    st.plotly_chart(fig, width='stretch')


def render_overtime_section(dashboard_service):
    """Renderiza a seção de Horas Extras"""
    st.subheader("⏰ Análise de Horas Extras")

    # Seletor de período
    col_period, col_refresh = st.columns([3, 1])

    with col_period:
        period_days = st.selectbox(
            "Período de Análise",
            [7, 15, 30, 60, 90],
            index=2,  # Padrão: 30 dias
            key="overtime_period",
            format_func=lambda x: f"Últimos {x} dias"
        )

    with col_refresh:
        if st.button("🔄 Atualizar", key="refresh_overtime"):
            st.rerun()

    # Obter dados do service
    result = dashboard_service.get_overtime_statistics(days=period_days)

    if not result.get('success'):
        st.error(f"❌ {result.get('message', 'Erro ao carregar dados de horas extras')}")
        return

    overtime_data = result.get('data', [])
    total_overtime_hours = result.get('total_overtime_hours', 0)
    overtime_rate = result.get('overtime_rate', 30.0)
    total_cost = result.get('total_cost', 0)

    # Cards de resumo
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Custo Total de Horas Extras",
            value=f"R$ {total_cost:,.2f}",
            help=f"Custo total com horas extras nos últimos {period_days} dias"
        )

    with col2:
        st.metric(
            label="⏱️ Total de Horas Extras",
            value=f"{total_overtime_hours:.2f}h",
            help="Soma de todas as horas extras trabalhadas"
        )

    with col3:
        st.metric(
            label="💵 Valor por Hora Extra",
            value=f"R$ {overtime_rate:.2f}",
            help="Valor pago por hora extra trabalhada"
        )

    with col4:
        employees_with_overtime = len(overtime_data)
        st.metric(
            label="👥 Funcionários com H.E.",
            value=employees_with_overtime,
            help="Número de funcionários que fizeram horas extras"
        )

    if not overtime_data:
        st.info(f"Nenhuma hora extra registrada nos últimos {period_days} dias.")
        return

    st.markdown("---")

    # Gráfico de Horas Extras por Funcionário
    col_chart, col_table = st.columns([2, 1])

    with col_chart:
        st.subheader("📊 Horas Extras por Funcionário")

        df_overtime = pd.DataFrame(overtime_data)

        # Criar gráfico de barras horizontal
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=df_overtime['name'],
            x=df_overtime['total_overtime_hours'],
            orientation='h',
            marker_color='orange',
            text=df_overtime['total_overtime_hours'].apply(lambda x: f"{float(x):.2f}h"),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>' +
                          'Horas Extras: %{x:.2f}h<br>' +
                          'Custo: R$ %{customdata:.2f}<extra></extra>',
            customdata=df_overtime['total_overtime_hours'].apply(lambda x: float(x) * overtime_rate)
        ))

        fig.update_layout(
            xaxis_title="Horas Extras (h)",
            yaxis_title="Funcionário",
            height=max(400, len(overtime_data) * 30),  # Altura dinâmica
            showlegend=False
        )

        st.plotly_chart(fig, width='stretch')

    with col_table:
        st.subheader("💰 Custo Individual")

        # Criar DataFrame para tabela
        df_cost = pd.DataFrame({
            'Funcionário': df_overtime['name'],
            'H. Extras': df_overtime['total_overtime_hours'].apply(lambda x: f"{float(x):.2f}h"),
            'Custo': df_overtime['total_overtime_hours'].apply(lambda x: f"R$ {float(x) * overtime_rate:,.2f}")
        })

        st.dataframe(
            df_cost,
            hide_index=True,
            width='stretch'
        )

        # Informação adicional
        st.caption(f"Total: {len(df_cost)} funcionário(s)")

    st.markdown("---")

    # Tabela detalhada
    with st.expander("📋 Detalhes Completos de Horas Extras"):
        df_detailed = pd.DataFrame({
            'Nome': df_overtime['name'],
            'Cargo': df_overtime['position'],
            'Dias Trab.': df_overtime['days_worked'],
            'H. Totais': df_overtime['total_hours_worked'].apply(lambda x: f"{float(x):.2f}h"),
            'H. Extras': df_overtime['total_overtime_hours'].apply(lambda x: f"{float(x):.2f}h"),
            'Custo H.E.': df_overtime['total_overtime_hours'].apply(lambda x: f"R$ {float(x) * overtime_rate:,.2f}")
        })

        st.dataframe(
            df_detailed,
            hide_index=True,
            width='stretch'
        )

        # Estatísticas adicionais
        st.markdown("#### 📈 Estatísticas do Período")

        col_stat1, col_stat2, col_stat3 = st.columns(3)

        with col_stat1:
            avg_overtime = total_overtime_hours / employees_with_overtime if employees_with_overtime > 0 else 0
            st.metric(
                "Média de H.E. por Funcionário",
                f"{avg_overtime:.2f}h"
            )

        with col_stat2:
            total_days_worked = df_overtime['days_worked'].sum()
            st.metric(
                "Total de Dias Trabalhados",
                total_days_worked
            )

        with col_stat3:
            max_overtime = float(df_overtime['total_overtime_hours'].max())
            st.metric(
                "Máximo de H.E. (Individual)",
                f"{max_overtime:.2f}h"
            )

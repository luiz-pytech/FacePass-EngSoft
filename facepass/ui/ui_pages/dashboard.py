"""
Dashboard UI - Página de visualização do dashboard (apenas renderização)
"""

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

    # Obter controller do session_state
    dashboard_controller = st.session_state.get('dashboard_controller')

    if not dashboard_controller:
        st.error("❌ Dashboard não disponível. Controller não inicializado.")
        return

    st.title("📊 Dashboard de Gestão")
    st.markdown("---")

    # Quick Cards - Estatísticas principais
    render_quick_cards(dashboard_controller)

    st.markdown("---")

    # Controle de Presença
    render_presence_control(dashboard_controller)

    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        render_access_timeline_chart(dashboard_controller)

    with col2:
        render_access_by_hour_chart(dashboard_controller)

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        render_success_rate_chart(dashboard_controller)

    with col4:
        render_top_users_chart(dashboard_controller)

    st.markdown("---")

    # Gráfico de notificações
    render_notifications_chart(dashboard_controller)


def render_quick_cards(dashboard_controller):
    """Renderiza os cards com estatísticas rápidas"""
    st.subheader("📈 Visão Geral")

    # Obter dados do controller
    result = dashboard_controller.get_quick_stats()

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


def render_presence_control(dashboard_controller):
    """Renderiza o controle de presença (entrada/saída)"""
    st.subheader("👥 Controle de Presença")

    # Obter dados do controller
    result = dashboard_controller.get_present_users()

    if not result.get('success'):
        st.error(
            f"❌ {result.get('message', 'Erro ao carregar usuários presentes')}")
        return

    present_users = result.get('data', [])
    count = result.get('count', 0)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.info(f"**{count} usuários presentes no momento**")

    with col2:
        if st.button("🔄 Atualizar", key="refresh_presence"):
            st.rerun()

    if not present_users:
        st.info("Nenhum usuário presente no momento.")
        return

    # Exibir tabela de usuários presentes
    df_present = pd.DataFrame(present_users)

    # Formatar a tabela
    df_display = df_present[['name', 'position',
                             'last_entry_time', 'status']].copy()
    df_display.columns = ['Nome', 'Cargo', 'Entrada', 'Status']

    # Adicionar ícone de status
    df_display['Status'] = df_display['Status'].apply(
        lambda x: "🟢 Presente" if x == "present" else "🔴 Ausente"
    )

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )


def render_access_timeline_chart(dashboard_controller):
    """Gráfico de linha: Acessos ao longo do tempo (últimos 30 dias)"""
    st.subheader("📅 Acessos nos Últimos 30 Dias")

    # Obter dados do controller
    result = dashboard_controller.get_access_timeline_data(days=30)

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

    st.plotly_chart(fig, use_container_width=True)


def render_access_by_hour_chart(dashboard_controller):
    """Gráfico de barras: Acessos por hora do dia (hoje)"""
    st.subheader("🕐 Acessos por Hora (Hoje)")

    # Obter dados do controller
    result = dashboard_controller.get_hourly_distribution_data()

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

    st.plotly_chart(fig, use_container_width=True)


def render_success_rate_chart(dashboard_controller):
    """Gráfico de área: Taxa de sucesso ao longo do tempo"""
    st.subheader("📈 Taxa de Sucesso de Reconhecimento")

    # Obter dados do controller
    result = dashboard_controller.get_success_rate_data(days=30)

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

    st.plotly_chart(fig, use_container_width=True)


def render_top_users_chart(dashboard_controller):
    """Gráfico de barras horizontal: Top 10 usuários com mais acessos"""
    st.subheader("🏆 Top 10 Usuários")

    # Obter dados do controller
    result = dashboard_controller.get_top_users_data(limit=10)

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

    st.plotly_chart(fig, use_container_width=True)


def render_notifications_chart(dashboard_controller):
    """Gráfico de pizza: Distribuição de notificações por tipo"""
    st.subheader("🔔 Notificações por Tipo")

    # Obter dados do controller
    result = dashboard_controller.get_notification_distribution_data(days=30)

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

    st.plotly_chart(fig, use_container_width=True)

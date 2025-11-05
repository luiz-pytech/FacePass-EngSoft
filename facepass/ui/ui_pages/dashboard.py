import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

def app():
    """Página de Dashboard para o gestor"""
    st.title("📝 Dashboard do Gestor")
    st.markdown("---")

    st.info("""
        👋 **Bem-vindo ao Dashboard!**
        Aqui você acompanha os principais indicadores do sistema.
    """)

    st.set_page_config(layout="wide")

    st.markdown("---")

    # ---- MOCK DE DADOS ----
    np.random.seed(42)
    usuarios = pd.DataFrame({
        "Nome": [f"Usuário {i}" for i in range(1, 11)],
        "Cargo": np.random.choice(["Gestor", "Analista", "Supervisor", "Estagiário"], 10),
        "Status": np.random.choice(["Aprovado", "Pendente", "Reprovado"], 10),
        "Acessos": np.random.randint(5, 100, 10),
        "Notificações": np.random.randint(1, 20, 10)
    })

    acessos = pd.DataFrame({
        "Tipo": ["Permitido", "Negado"],
        "Quantidade": [np.random.randint(50, 150), np.random.randint(10, 50)]
    })

    notificacoes = pd.DataFrame({
        "Tipo": ["Lidas", "Não lidas"],
        "Quantidade": [np.random.randint(30, 80), np.random.randint(10, 40)]
    })

    acessos_horario = pd.DataFrame({
        "Hora": list(range(0, 24)),
        "Acessos": np.random.randint(0, 50, 24)
    })

    notificacoes_horario = pd.DataFrame({
        "Hora": list(range(0, 24)),
        "Notificações": np.random.randint(0, 30, 24)
    })

    # ---- PRIMEIRO BLOCO ----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Usuários cadastrados", len(usuarios))
    with col2:
        st.metric("Usuários aprovados", sum(usuarios["Status"] == "Aprovado"))
    with col3:
        st.metric("Total de acessos", usuarios["Acessos"].sum())

    # ---- SEGUNDO BLOCO ----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Acessos permitidos", acessos.loc[0, "Quantidade"])
    with col2:
        st.metric("Acessos negados", acessos.loc[1, "Quantidade"])
    with col3:
        st.metric("Total de notificações", notificacoes["Quantidade"].sum())

    st.markdown("---")

    # ---- GRÁFICOS ----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Tipo de acesso")
        chart_acesso = alt.Chart(acessos).mark_arc().encode(
            theta="Quantidade",
            color="Tipo"
        )
        st.altair_chart(chart_acesso, width='stretch')

        st.subheader("Acesso por usuário")
        chart_user = alt.Chart(usuarios).mark_bar().encode(
            x="Nome",
            y="Acessos",
            color="Status"
        ).properties(height=200)
        st.altair_chart(chart_user, width='stretch')

    with col2:
        st.subheader("Tipo de notificação")
        chart_notif = alt.Chart(notificacoes).mark_arc().encode(
            theta="Quantidade",
            color="Tipo"
        )
        st.altair_chart(chart_notif, width='stretch')

        st.subheader("Notificações por horário")
        chart_notif_time = alt.Chart(notificacoes_horario).mark_line().encode(
            x="Hora",
            y="Notificações"
        )
        st.altair_chart(chart_notif_time, width='stretch')

    with col3:
        st.subheader("Cadastro de usuário")

        col_filter1, col_filter2, col_filter3 = st.columns(3)
        with col_filter1:
            filter_name = st.text_input("🔍 Filtrar por Nome", key="filter_name")
        with col_filter2:
            filter_status = st.selectbox("Status", ["Todos", "Aprovado", "Pendente", "Reprovado"], key="filter_status")
        with col_filter3:
            filter_cargo = st.text_input("🔍 Filtrar por Cargo", key="filter_cargo")

        df_filtered = usuarios.copy()
        if filter_name:
            df_filtered = df_filtered[df_filtered["Nome"].str.contains(filter_name, case=False)]
        if filter_status != "Todos":
            df_filtered = df_filtered[df_filtered["Status"] == filter_status]
        if filter_cargo:
            df_filtered = df_filtered[df_filtered["Cargo"].str.contains(filter_cargo, case=False)]

        st.dataframe(df_filtered, width='stretch')

# Executar diretamente (útil para testes locais)
if __name__ == "__main__":
    app()

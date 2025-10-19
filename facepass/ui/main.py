import streamlit as st
from facepass.ui.pages import notifications, approve_registration, registers
from facepass.models.user import Usuario
from facepass.services.user_service import UsuarioService
from facepass.database.repository.user_repository import UsuarioRepository


def sidebar():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Go to", ["🏠 Home", "👤 Approve Users", "📜 Access logs", "🔔 Notifications"])
    return page


def main():
    st.set_page_config(
        page_title="FacePass - Controle de Acesso",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title(" 🔐FacePass Application")
    st.write("Welcome to the FacePass application")

    page = sidebar()
    if page == "Home":
        st.subheader("Home")
        st.write("This is the home page of the FacePass application.")
    elif page == "Approve Users":
        approve_registration.app()
    elif page == "Registers":
        registers.app()
    elif page == "Notifications":
        notifications.app()
        st.rerun()

    with st.form("auto-cadastro-form", clear_on_submit=True, enter_to_submit=True):
        st.header("Auto Cadastro de Usuário")
        name = st.text_input("Nome Completo")
        email = st.text_input("Email")
        cpf = st.text_input("CPF")
        cargo = st.text_input("Cargo")
        photo_recognition = st.file_uploader(
            "Foto para Reconhecimento Facial", type=["jpg", "jpeg", "png"])

        submitted = st.form_submit_button("Enviar Cadastro")
        if submitted:
            user = Usuario(id=0, name=name, email=email, cpf=cpf,
                           photo_recognition=photo_recognition.read() if photo_recognition else b"")
            user.position = cargo
            user_service: UsuarioService = st.session_state['user_service']
            try:
                user_service.create_user(user, manager_id=1)
                st.success(
                    "Cadastro enviado com sucesso! Aguardando aprovação.")
            except Exception as e:
                st.error(f"Erro ao enviar cadastro: {str(e)}")

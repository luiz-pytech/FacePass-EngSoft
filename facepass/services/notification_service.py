from facepass.models.user import Usuario
from facepass.models.manager import Gestor
from facepass.models.notification import Notificacao
from facepass.database.repository.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository

    def create_notification_from_user(self, usuario: Usuario, tipo_notificacao: str, mensagem: str):
        if not usuario:
            raise ValueError("Usuário inválido para notificação.")

        if tipo_notificacao not in ["aprovação", "rejeição", "aguardando"]:
            raise ValueError("Tipo de notificação inválido.")

        if tipo_notificacao == "aprovação":
            mensagem = f"Olá {usuario.nome}, sua conta foi criada e está aguardando aprovação."

        if tipo_notificacao == "rejeição":
            mensagem = f"Olá {usuario.nome}, sua conta foi rejeitada. Por favor, entre em contato com o suporte."

        if tipo_notificacao == "aguardando":
            mensagem = f"Olá {usuario.nome}, sua conta está aguardando aprovação do administrador."

        notificacao = {
            "usuario_id": usuario.id,
            "tipo_notificacao": tipo_notificacao,
            "mensagem": mensagem
        }

        return notificacao

    def create_notification_from_manager(self, gestor: Gestor, usuario: Usuario, tipo_notificacao: str, mensagem: str):
        if not gestor:
            raise ValueError("Gestor inválido para notificação.")

        if tipo_notificacao not in ["alerta", "info", "erro", "cadastro_pendente"]:
            raise ValueError("Tipo de notificação inválido.")

        if tipo_notificacao == "alerta":
            mensagem = f"Alerta para gestor {gestor.nome}: {mensagem}"

        if tipo_notificacao == "info":
            mensagem = f"Informação para gestor {gestor.nome}: {mensagem}"

        if tipo_notificacao == "erro":
            mensagem = f"Erro para gestor {gestor.nome}: {mensagem}"

        if tipo_notificacao == "cadastro_pendente":
            mensagem = f"Olá {gestor.nome}, uma nova solicitação de cadastro está pendente."

        notificacao = {
            "gestor_id": gestor.id,
            "tipo_notificacao": tipo_notificacao,
            "usuario_id": usuario.id,
            "mensagem": mensagem
        }

        return notificacao

    def send_approval_request(self, usuario: Usuario):
        self.create_notification_from_user(
            usuario, "aprovação", "Solicitação de aprovação enviada. Aguarde a aprovação do administrador.")

    def create_access_denied_notification(self, notificacao):
        self.create_notification_from_manager(
            notificacao.gestor_id, notificacao.registro_acesso_id, notificacao.tipo_notificacao, notificacao.mensagem)

    def list_unread_notifications(self):
        return self.notification_repository.list_unread_notifications()

    def mark_as_read(self, notification_id: int):
        self.notification_repository.mark_notification_as_read(notification_id)

    def delete_notification(self, notification_id: int):
        self.notification_repository.delete_notification(notification_id)

    def list_all_notifications(self):
        return self.notification_repository.list_all_notifications()

from facepass.database.repository.register_repository import RegistroRepository
from facepass.models.registerAcess import RegistroAcesso
from facepass.models.notification import Notificacao
from facepass.services.notification_service import NotificationService
from facepass.database.repository.notification_repository import NotificationRepository
from datetime import datetime


class AccessService:
    def __init__(self, acesso_repository: RegistroRepository, notification_repository: NotificationRepository):
        self.acesso_repository = acesso_repository
        self.notification_repository = notification_repository

    def create_access(self, registro: RegistroAcesso) -> None:
        if registro.acesso_permitido == False:
            notificacao_service = NotificationService(
                self.notification_repository)
            notificacao = Notificacao(
                id=None,
                gestor_id=None,
                registro_acesso_id=registro.id,
                data_hora=registro.data_hora,
                tipo_notificacao="erro",
                mensagem="Acesso negado em {}".format(registro.data_hora),
                lida=False
            )
            notificacao_service.create_access_denied_notification(notificacao)
        self.acesso_repository.save_register(registro)

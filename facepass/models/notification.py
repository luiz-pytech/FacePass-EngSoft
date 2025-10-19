from datetime import datetime


class Notificacao:
    """Model class representing a notification in the FacePass system."""

    def __init__(self, id: int, manager_id: int, access_register_id: int, created_at: datetime, type_notification: str, message: str, read: bool = False):
        self.id: int = id
        self.manager_id: int = manager_id
        self.access_register_id: int = access_register_id
        self.created_at: datetime = created_at
        self.type_notification: str = type_notification
        self.message: str = message
        self.read: bool = read

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "gestor_id": self.manager_id,
            "registro_acesso_id": self.access_register_id,
            "data_hora": self.created_at,
            "tipo_notificacao": self.type_notification,
            "mensagem": self.message,
            "lida": self.read,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            manager_id=data.get("gestor_id"),
            access_register_id=data.get("registro_acesso_id"),
            created_at=data.get("data_hora"),
            type_notification=data.get("tipo_notificacao"),
            message=data.get("mensagem"),
            read=data.get("lida"),
        )
